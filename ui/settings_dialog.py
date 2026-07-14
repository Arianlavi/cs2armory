from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QCheckBox, QPushButton,
    QMessageBox, QLabel, QGroupBox
)
from PyQt5.QtCore import Qt, QSettings
from core.firewall_manager import FirewallManager

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setMinimumWidth(400)
        self.firewall = FirewallManager()
        self.settings = QSettings("CS2Armory", "Settings")
        self.setup_ui()
        self.load_settings()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        self.version_check = QCheckBox("Check for updates on startup")
        layout.addWidget(self.version_check)

        fw_group = QGroupBox("Firewall")
        fw_layout = QVBoxLayout()
        self.reset_fw_btn = QPushButton("Reset Firewall to Default")
        self.reset_fw_btn.clicked.connect(self.reset_firewall)
        fw_layout.addWidget(self.reset_fw_btn)
        self.check_fw_btn = QPushButton("Check Firewall Status")
        self.check_fw_btn.clicked.connect(self.check_firewall)
        fw_layout.addWidget(self.check_fw_btn)
        fw_group.setLayout(fw_layout)
        layout.addWidget(fw_group)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

    def load_settings(self):
        self.version_check.setChecked(self.settings.value("versionCheck", True, type=bool))

    def save_settings(self):
        self.settings.setValue("versionCheck", self.version_check.isChecked())

    def accept(self):
        self.save_settings()
        super().accept()

    def reset_firewall(self):
        reply = QMessageBox.question(self, "Confirm", "Reset Windows Firewall to default settings?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                self.firewall._run_netsh("advfirewall reset")
                QMessageBox.information(self, "Success", "Firewall reset successfully.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to reset firewall: {str(e)}")

    def check_firewall(self):
        try:
            stdout, stderr, code = self.firewall._run_netsh("advfirewall show allprofiles state")
            if "ON" in stdout.upper():
                QMessageBox.information(self, "Firewall Status", "All profiles are ON.")
            else:
                reply = QMessageBox.question(self, "Firewall Status",
                                             "Firewall is OFF. Enable now?",
                                             QMessageBox.Yes | QMessageBox.No)
                if reply == QMessageBox.Yes:
                    self.firewall._run_netsh("advfirewall set allprofiles state on")
                    QMessageBox.information(self, "Success", "Firewall enabled.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to check firewall: {str(e)}")