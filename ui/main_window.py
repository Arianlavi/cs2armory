import os
import re
import threading
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QHeaderView, QPushButton, QProgressBar,
    QMessageBox, QLabel, QDialog, QStatusBar
)
from PyQt5.QtCore import Qt, QUrl, pyqtSignal
from PyQt5.QtGui import QPixmap, QIcon, QColor, QDesktopServices

from core.server_manager import ServerManager
from core.firewall_manager import FirewallManager
from core.ping_manager import PingManager
from core.preset_manager import PresetManager
from core.version_checker import VersionChecker

from ui.preset_dialog import PresetDialog
from ui.settings_dialog import SettingsDialog

APP_VERSION = "1.0"


class MainWindow(QMainWindow):
    # Background work (fetching, pinging, firewall ops) runs on plain
    servers_loaded_sig = pyqtSignal(dict, dict, str, bool)
    servers_load_failed_sig = pyqtSignal(str, bool)
    ping_round_complete_sig = pyqtSignal(int)
    latency_update_sig = pyqtSignal(str, int, int)
    firewall_op_done_sig = pyqtSignal(int, object)
    version_available_sig = pyqtSignal(str, str)

    def __init__(self):
        super().__init__()
        self.servers_loaded_sig.connect(self._on_servers_loaded)
        self.servers_load_failed_sig.connect(self._on_servers_load_failed)
        self.ping_round_complete_sig.connect(self._on_ping_round_complete)
        self.latency_update_sig.connect(self._update_latency_ui)
        self.firewall_op_done_sig.connect(self._on_firewall_operation_done)
        self.version_available_sig.connect(self._prompt_update)
        self.setWindowTitle("CS2 Armory")
        self.setMinimumSize(960, 700)
        try:
            self.setWindowIcon(QIcon("resources/icons/app.ico"))
        except Exception:
            pass

        self.server_mgr = ServerManager()
        self.firewall = FirewallManager()
        self.ping_mgr = PingManager()
        self.preset_mgr = PresetManager()
        self.clustered_data = {}
        self.unclustered_data = {}
        self.current_data = {}
        self.is_clustered = True
        self.revision = ""
        self.pending_operation = False
        self._generation = 0
        self._on_ready = None

        self.setup_ui()
        self.setup_status_bar()

    def start(self, on_ready=None):

        self._on_ready = on_ready
        self.load_servers(initial=True)
        self.check_version()

    # ------------------------------------------------------------------ UI

    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(16, 16, 16, 16)

        header = QHBoxLayout()
        title = QLabel("☣️ CS2 Armory")
        title.setObjectName("titleLabel")
        header.addWidget(title)
        subtitle = QLabel("CS2 Server Manager")
        subtitle.setObjectName("subtitleLabel")
        header.addWidget(subtitle)
        header.addStretch()
        ver_label = QLabel(f"v{APP_VERSION}")
        ver_label.setObjectName("subtitleLabel")
        header.addWidget(ver_label)
        main_layout.addLayout(header)

        toolbar = QHBoxLayout()
        toolbar.setSpacing(8)

        self.info_btn = QPushButton("ℹ️ Info")
        self.info_btn.setObjectName("accentBtn")
        self.info_btn.clicked.connect(self.show_info)
        toolbar.addWidget(self.info_btn)

        self.preset_btn = QPushButton("📋 Presets")
        self.preset_btn.clicked.connect(self.open_presets)
        toolbar.addWidget(self.preset_btn)

        self.refresh_btn = QPushButton("🔄 Refresh")
        self.refresh_btn.clicked.connect(self.refresh_servers)
        toolbar.addWidget(self.refresh_btn)

        self.cluster_btn = QPushButton("📦 Uncluster")
        self.cluster_btn.clicked.connect(self.toggle_cluster)
        toolbar.addWidget(self.cluster_btn)

        self.progress = QProgressBar()
        self.progress.setVisible(False)
        self.progress.setRange(0, 0)
        self.progress.setMaximumHeight(24)
        toolbar.addWidget(self.progress)

        toolbar.addStretch()

        icon_layout = QHBoxLayout()
        for icon_file, callback in [
            ("settings.png", self.open_settings),
            ("github.png", self.open_github),
            ("paypal.png", self.open_paypal),
        ]:
            lbl = QLabel()
            pix = QPixmap(f"resources/icons/{icon_file}")
            if not pix.isNull():
                lbl.setPixmap(pix.scaled(24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            else:
                lbl.setText("⚙️" if icon_file == "settings.png" else "🐙" if "github" in icon_file else "💲")
            lbl.setCursor(Qt.PointingHandCursor)
            lbl.mousePressEvent = callback
            icon_layout.addWidget(lbl)

        toolbar.addLayout(icon_layout)
        main_layout.addLayout(toolbar)

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["", "Server", "Latency"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.ExtendedSelection)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        self.table.verticalHeader().setVisible(False)
        self.table.itemDoubleClicked.connect(self.on_item_double_click)
        main_layout.addWidget(self.table)

        action_bar = QHBoxLayout()
        action_bar.setSpacing(10)

        self.block_all_btn = QPushButton("🚫 Block All")
        self.block_all_btn.setObjectName("blockBtn")
        self.block_all_btn.clicked.connect(self.block_all)
        action_bar.addWidget(self.block_all_btn)

        self.block_selected_btn = QPushButton("🚫 Block Selected")
        self.block_selected_btn.setObjectName("blockBtn")
        self.block_selected_btn.clicked.connect(self.block_selected)
        action_bar.addWidget(self.block_selected_btn)

        self.unblock_selected_btn = QPushButton("✅ Unblock Selected")
        self.unblock_selected_btn.setObjectName("unblockBtn")
        self.unblock_selected_btn.clicked.connect(self.unblock_selected)
        action_bar.addWidget(self.unblock_selected_btn)

        self.unblock_all_btn = QPushButton("✅ Unblock All")
        self.unblock_all_btn.setObjectName("unblockBtn")
        self.unblock_all_btn.clicked.connect(self.unblock_all)
        action_bar.addWidget(self.unblock_all_btn)

        action_bar.addStretch()
        self.selection_info = QLabel("Select servers to manage")
        self.selection_info.setObjectName("subtitleLabel")
        action_bar.addWidget(self.selection_info)

        main_layout.addLayout(action_bar)

        self.table.itemSelectionChanged.connect(self._update_selection_label)

    def setup_status_bar(self):
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

    def _update_selection_label(self):
        count = len(self.get_selected_servers())
        self.selection_info.setText(f"{count} server(s) selected" if count else "Select servers to manage")

    # ------------------------------------------------------------ loading

    def load_servers(self, initial=False):
        if self.pending_operation:
            return
        self.set_operation_in_progress(True)
        self.status_bar.showMessage("Fetching server list...")
        self._show_placeholder_row("Loading server list from Steam...")

        def task():
            try:
                clustered, unclustered, revision = self.server_mgr.fetch_servers()
                self.servers_loaded_sig.emit(clustered, unclustered, revision, initial)
            except Exception as e:
                self.servers_load_failed_sig.emit(str(e), initial)

        threading.Thread(target=task, daemon=True).start()

    def _on_servers_loaded(self, clustered, unclustered, revision, initial):
        self.clustered_data = clustered
        self.unclustered_data = unclustered
        self.revision = revision
        self.current_data = self.clustered_data if self.is_clustered else self.unclustered_data
        self.status_bar.showMessage(f"Loaded {len(self.current_data)} server(s) - revision {revision}")
        try:
            self.populate_table()
            self.ping_all_servers()
        finally:
            self._finish_initial_load(initial)

    def _on_servers_load_failed(self, message, initial):
        self.set_operation_in_progress(False)
        self.status_bar.showMessage("Failed to load server list")
        self._show_placeholder_row("Failed to load - click Refresh to try again")
        self._finish_initial_load(initial)
        QMessageBox.critical(
            self, "Error",
            f"Failed to load server data:\n{message}\n\n"
            "If this keeps happening, api.steampowered.com may be blocked "
            "or filtered on your network - try again with a VPN, or make "
            "sure your VPN/proxy tool is actually running first."
        )

    def _finish_initial_load(self, initial):
        if initial and self._on_ready:
            self._on_ready()
            self._on_ready = None

    # -------------------------------------------------------------- table

    def _show_placeholder_row(self, text):

        self.table.setRowCount(1)
        self.table.setItem(0, 0, QTableWidgetItem())
        msg_item = QTableWidgetItem(text)
        msg_item.setTextAlignment(Qt.AlignCenter)
        self.table.setItem(0, 1, msg_item)
        self.table.setItem(0, 2, QTableWidgetItem())

    def populate_table(self):
        self._generation += 1
        if not self.current_data:
            self._show_placeholder_row("No servers found - click Refresh to try again")
            return
        self.table.setRowCount(len(self.current_data))
        row = 0
        for name in self.current_data.keys():
            flag_item = QTableWidgetItem()
            flag_pixmap = self.get_flag_pixmap(name)
            if flag_pixmap and not flag_pixmap.isNull():
                flag_item.setIcon(QIcon(flag_pixmap))
            self.table.setItem(row, 0, flag_item)
            self.table.setItem(row, 1, QTableWidgetItem(name))
            lat_item = QTableWidgetItem("")
            lat_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 2, lat_item)
            row += 1
        self._refresh_blocked_status_display()

    def _refresh_blocked_status_display(self):
        for row in range(self.table.rowCount()):
            name_item = self.table.item(row, 1)
            lat_item = self.table.item(row, 2)
            if name_item is None or lat_item is None:
                continue
            try:
                blocked = self.firewall.is_blocked(name_item.text())
            except Exception:
                blocked = False
            if blocked:
                name_item.setBackground(QColor(100, 40, 40))
                lat_item.setText("🚫 Blocked")
                lat_item.setBackground(QColor(100, 40, 40))

    def get_flag_pixmap(self, server_name):
        flag_dir = "resources/flags/"
        if not os.path.exists(flag_dir):
            return QPixmap()
        name_lower = server_name.lower()
        best_match, best_len = None, 0
        for f in os.listdir(flag_dir):
            if not f.endswith(".png"):
                continue
            base = os.path.splitext(f)[0].lower()
            if re.search(rf"(^|[\s(]){re.escape(base)}($|[\s)])", name_lower) and len(base) > best_len:
                best_match, best_len = f, len(base)
        return QPixmap(os.path.join(flag_dir, best_match)) if best_match else QPixmap()

    # --------------------------------------------------------------- ping

    def ping_all_servers(self):
        gen = self._generation
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 2)
            if item is not None:
                item.setText("Pinging...")
                item.setBackground(QColor(50, 50, 50))

        def callback(name, latency):
            self.update_latency(name, latency, gen)

        def on_complete():
            self.ping_round_complete_sig.emit(gen)

        threading.Thread(
            target=self.ping_mgr.ping_servers,
            args=(self.current_data, callback),
            kwargs={"on_complete": on_complete},
            daemon=True,
        ).start()

    def _on_ping_round_complete(self, gen):
        if gen == self._generation:
            self.set_operation_in_progress(False)
            self.status_bar.showMessage("Ready")

    def update_latency(self, server_name, latency, gen):
        self.latency_update_sig.emit(server_name, latency, gen)

    def _update_latency_ui(self, server_name, latency, gen):
        if gen != self._generation:
            return
        for row in range(self.table.rowCount()):
            name_item = self.table.item(row, 1)
            if name_item is None or name_item.text() != server_name:
                continue
            lat_item = self.table.item(row, 2)
            if lat_item is None:
                return
            if latency == -1:
                lat_item.setText("⏱ Timeout")
                lat_item.setBackground(QColor(100, 80, 20))
            else:
                lat_item.setText(f"{latency} ms")
                lat_item.setBackground(QColor(40, 100, 40))
            break

    # --------------------------------------------------------- operations

    def set_operation_in_progress(self, in_progress):
        self.pending_operation = in_progress
        self.progress.setVisible(in_progress)
        self.refresh_btn.setEnabled(not in_progress)
        self.cluster_btn.setEnabled(not in_progress)
        self.block_all_btn.setEnabled(not in_progress)
        self.block_selected_btn.setEnabled(not in_progress)
        self.unblock_all_btn.setEnabled(not in_progress)
        self.unblock_selected_btn.setEnabled(not in_progress)

    def get_selected_servers(self):
        selected = []
        for item in self.table.selectedItems():
            name_item = self.table.item(item.row(), 1)
            if name_item is not None and name_item.text() not in selected:
                selected.append(name_item.text())
        return selected

    def block_all(self):
        if self.pending_operation:
            return
        if QMessageBox.question(self, "Confirm", "Block all servers?",
                                 QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            self.run_firewall_operation(self.firewall.block_all, self.current_data)

    def unblock_all(self):
        if self.pending_operation:
            return
        if QMessageBox.question(self, "Confirm", "Unblock all servers?",
                                 QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            self.run_firewall_operation(self.firewall.unblock_all, self.current_data)

    def block_selected(self):
        if self.pending_operation:
            return
        selected = self.get_selected_servers()
        if not selected:
            QMessageBox.information(self, "Info", "No servers selected.")
            return
        data = {name: self.current_data[name] for name in selected if name in self.current_data}
        self.run_firewall_operation(self.firewall.block_all, data)

    def unblock_selected(self):
        if self.pending_operation:
            return
        selected = self.get_selected_servers()
        if not selected:
            QMessageBox.information(self, "Info", "No servers selected.")
            return
        data = {name: self.current_data[name] for name in selected if name in self.current_data}
        self.run_firewall_operation(self.firewall.unblock_all, data)

    def run_firewall_operation(self, operation, data):
        if self.pending_operation:
            return
        self.set_operation_in_progress(True)
        gen = self._generation

        def task():
            error_msg = None
            try:
                operation(data)
            except Exception as e:
                error_msg = f"Operation failed:\n{e}"
            finally:
                self.firewall_op_done_sig.emit(gen, error_msg)

        threading.Thread(target=task, daemon=True).start()

    def _on_firewall_operation_done(self, gen, error_msg):
        if gen == self._generation:
            self.set_operation_in_progress(False)
            self._refresh_blocked_status_display()
        if error_msg:
            self.show_error(error_msg)

    def toggle_cluster(self):
        if self.pending_operation:
            return
        self.is_clustered = not self.is_clustered
        self.current_data = self.clustered_data if self.is_clustered else self.unclustered_data
        self.cluster_btn.setText("Uncluster" if self.is_clustered else "Cluster")
        self.set_operation_in_progress(True)
        self.populate_table()
        self.ping_all_servers()

    def refresh_servers(self):
        if self.pending_operation:
            return
        self.load_servers(initial=False)

    def on_item_double_click(self, item):
        name_item = self.table.item(item.row(), 1)
        if name_item is None:
            return
        name = name_item.text()
        if name not in self.current_data:
            return
        gen = self._generation

        def callback(n, lat):
            self.update_latency(n, lat, gen)

        threading.Thread(
            target=self.ping_mgr.ping_servers,
            args=({name: self.current_data[name]}, callback),
            daemon=True,
        ).start()

    # ----------------------------------------------------------- dialogs

    def open_presets(self):
        dialog = PresetDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.load_servers()

    def open_settings(self, event):
        SettingsDialog(self).exec_()

    def open_github(self, event):
        QDesktopServices.openUrl(QUrl("https://github.com/arianlavi/cs2armory"))

    def open_paypal(self, event):
        QDesktopServices.openUrl(QUrl("https://plisio.net/donate/uTXSR0Q1"))

    def show_info(self):
        info = f"""
        <h3>CS2 Armory</h3>
        <p><b>Version:</b> {APP_VERSION}</p>
        <p>Manage CS2 servers via CS2 Armory</p>
        <ul>
            <li><b>Select:</b> CTRL+click or drag</li>
            <li><b>Ping:</b> Double-click a row</li>
            <li><b>Clustering:</b> Groups China, India, Japan, Stockholm</li>
        </ul>
        <p><b>Author:</b> arianlavi</p>
        """
        QMessageBox.information(self, "About", info)

    def check_version(self):
        def check():
            try:
                result = VersionChecker.check(APP_VERSION)
                if result:
                    tag, url = result
                    self.version_available_sig.emit(tag, url)
            except Exception:
                pass
        threading.Thread(target=check, daemon=True).start()

    def _prompt_update(self, tag, url):
        if QMessageBox.question(self, "Update Available", f"Version {tag} is available. Download now?",
                                 QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            QDesktopServices.openUrl(QUrl(url))

    def show_error(self, msg):
        QMessageBox.critical(self, "Error", msg)
