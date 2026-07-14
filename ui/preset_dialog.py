from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QMessageBox
)
from PyQt5.QtCore import Qt
from core.preset_manager import PresetManager
from ui.add_preset_dialog import AddPresetDialog

class PresetDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.preset_mgr = PresetManager()
        self.parent_app = parent
        self.setWindowTitle("Preset Manager")
        self.setMinimumSize(700, 500)
        self.setup_ui()
        self.load_presets()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        self.table = QTableWidget()
        self.table.setColumnCount(1)
        self.table.setHorizontalHeaderLabels(["Preset Name"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.table)

        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("Add")
        self.add_btn.clicked.connect(self.add_preset)
        btn_layout.addWidget(self.add_btn)

        self.update_btn = QPushButton("Update")
        self.update_btn.clicked.connect(self.update_preset)
        btn_layout.addWidget(self.update_btn)

        self.delete_btn = QPushButton("Delete")
        self.delete_btn.clicked.connect(self.delete_preset)
        btn_layout.addWidget(self.delete_btn)

        self.block_btn = QPushButton("Block Preset")
        self.block_btn.clicked.connect(self.block_preset)
        btn_layout.addWidget(self.block_btn)

        self.block_except_btn = QPushButton("Block Except Preset")
        self.block_except_btn.clicked.connect(self.block_except_preset)
        btn_layout.addWidget(self.block_except_btn)

        btn_layout.addStretch()
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(close_btn)

        layout.addLayout(btn_layout)

    def load_presets(self):
        self.table.setRowCount(0)
        is_clustered = self.parent_app.is_clustered if self.parent_app else True
        presets = self.preset_mgr.get_presets_for_cluster(is_clustered)
        for key, data in presets.items():
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(data.get("presetName", key)))

    def get_selected_preset_name(self):
        selected = self.table.selectedItems()
        if not selected:
            return None
        return selected[0].text()

    def add_preset(self):
        dialog = AddPresetDialog(self.parent_app, self)
        if dialog.exec_() == QDialog.Accepted:
            self.load_presets()

    def update_preset(self):
        name = self.get_selected_preset_name()
        if not name:
            QMessageBox.information(self, "Info", "Select a preset first.")
            return
        dialog = AddPresetDialog(self.parent_app, self, name)
        if dialog.exec_() == QDialog.Accepted:
            self.load_presets()

    def delete_preset(self):
        name = self.get_selected_preset_name()
        if not name:
            QMessageBox.information(self, "Info", "Select a preset first.")
            return
        reply = QMessageBox.question(self, "Confirm", f"Delete preset '{name}'?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.preset_mgr.delete_preset(name)
            self.load_presets()

    def block_preset(self):
        name = self.get_selected_preset_name()
        if not name:
            QMessageBox.information(self, "Info", "Select a preset first.")
            return
        preset = self.preset_mgr.get_preset(name)
        if not preset:
            return
        servers = preset.get("servers", [])
        if not servers:
            QMessageBox.information(self, "Info", "Preset has no servers.")
            return
        data = {s: self.parent_app.current_data.get(s, "") for s in servers if s in self.parent_app.current_data}
        if data:
            self.parent_app.run_firewall_operation(self.parent_app.firewall.block_all, data)
            self.accept()

    def block_except_preset(self):
        name = self.get_selected_preset_name()
        if not name:
            QMessageBox.information(self, "Info", "Select a preset first.")
            return
        preset = self.preset_mgr.get_preset(name)
        if not preset:
            return
        servers = set(preset.get("servers", []))
        data = {s: ips for s, ips in self.parent_app.current_data.items() if s not in servers}
        if data:
            self.parent_app.run_firewall_operation(self.parent_app.firewall.block_all, data)
            self.accept()