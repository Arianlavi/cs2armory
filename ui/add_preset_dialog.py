from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QListWidget, QMessageBox, QDialogButtonBox
)
from core.preset_manager import PresetManager

class AddPresetDialog(QDialog):
    def __init__(self, parent_app, parent=None, preset_name=None):
        super().__init__(parent)
        self.parent_app = parent_app
        self.preset_mgr = PresetManager()
        self.preset_name = preset_name
        self.setWindowTitle("Add Preset" if not preset_name else "Update Preset")
        self.setMinimumSize(400, 500)
        self.setup_ui()
        self.load_servers()
        if preset_name:
            self.load_preset_data()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Preset Name:"))
        self.name_edit = QLineEdit()
        layout.addWidget(self.name_edit)
        layout.addWidget(QLabel("Select Servers:"))
        self.server_list = QListWidget()
        self.server_list.setSelectionMode(QListWidget.MultiSelection)
        layout.addWidget(self.server_list)

        btn_layout = QHBoxLayout()
        self.reset_btn = QPushButton("Reset Selection")
        self.reset_btn.clicked.connect(self.reset_selection)
        btn_layout.addWidget(self.reset_btn)
        btn_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btn_box.accepted.connect(self.accept)
        btn_box.rejected.connect(self.reject)
        btn_layout.addWidget(btn_box)
        layout.addLayout(btn_layout)

    def load_servers(self):
        data = self.parent_app.current_data if self.parent_app else {}
        for name in data.keys():
            self.server_list.addItem(name)

    def load_preset_data(self):
        preset = self.preset_mgr.get_preset(self.preset_name)
        if preset:
            self.name_edit.setText(preset.get("presetName", ""))
            selected = set(preset.get("servers", []))
            for i in range(self.server_list.count()):
                item = self.server_list.item(i)
                if item.text() in selected:
                    item.setSelected(True)

    def reset_selection(self):
        for i in range(self.server_list.count()):
            self.server_list.item(i).setSelected(False)

    def get_selected_servers(self):
        return [item.text() for item in self.server_list.selectedItems()]

    def accept(self):
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.information(self, "Info", "Enter a preset name.")
            return
        servers = self.get_selected_servers()
        if not servers:
            QMessageBox.information(self, "Info", "Select at least one server.")
            return
        is_clustered = self.parent_app.is_clustered if self.parent_app else True
        if self.preset_name:
            success = self.preset_mgr.update_preset(self.preset_name, name, servers, is_clustered)
        else:
            success = self.preset_mgr.add_preset(name, servers, is_clustered)
        if not success:
            QMessageBox.warning(self, "Error", "Preset name might already exist.")
            return
        super().accept()