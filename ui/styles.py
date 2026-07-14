def apply_style(app):
    style = """
    QWidget {
        background-color: #0f0f11;
        color: #d4d4d8;
        font-family: 'Segoe UI', 'Inter', 'Arial', sans-serif;
        font-size: 9pt;
    }
    QMainWindow {
        background-color: #0f0f11;
    }
    QPushButton {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 #28282d, stop:1 #1e1e22);
        border: 1px solid #3a3a44;
        border-radius: 6px;
        padding: 8px 16px;
        color: #e8e8ec;
        font-weight: 600;
        font-size: 8.5pt;
    }
    QPushButton:hover {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 #3a3a44, stop:1 #2a2a32);
        border-color: #d4a030;
    }
    QPushButton:pressed {
        background: #1a1a1e;
        border-color: #b08828;
    }
    QPushButton:disabled {
        opacity: 0.5;
    }
    QPushButton#blockBtn {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 #8a2a2a, stop:1 #6a1e1e);
        border-color: #aa3a3a;
        color: #ffd4d4;
    }
    QPushButton#blockBtn:hover {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 #aa3a3a, stop:1 #7a2828);
        border-color: #cc4a4a;
    }
    QPushButton#unblockBtn {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 #2a7a2a, stop:1 #1e5a1e);
        border-color: #3aaa3a;
        color: #d4ffd4;
    }
    QPushButton#unblockBtn:hover {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 #3aaa3a, stop:1 #287a28);
        border-color: #4acc4a;
    }
    QPushButton#accentBtn {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 #d4a030, stop:1 #b08820);
        border-color: #e8b840;
        color: #0f0f11;
        font-weight: 700;
    }
    QPushButton#accentBtn:hover {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 #e8b040, stop:1 #c89830);
        border-color: #f0c850;
    }
    QTableWidget {
        background-color: #141416;
        alternate-background-color: #1a1a1e;
        gridline-color: #28282d;
        selection-background-color: #2a3a5a;
        border: 1px solid #28282d;
        border-radius: 8px;
        outline: none;
    }
    QTableWidget::item {
        padding: 6px 8px;
        border: none;
    }
    QTableWidget::item:selected {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 #2a4a7a, stop:1 #1e3a5e);
        color: #ffffff;
    }
    QTableWidget::item:hover:!selected {
        background: #22222a;
    }
    QHeaderView::section {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 #1e1e22, stop:1 #16161a);
        padding: 8px 12px;
        border: none;
        border-bottom: 2px solid #d4a030;
        font-weight: 700;
        font-size: 8.5pt;
        color: #d4d4d8;
    }
    QHeaderView::section:hover {
        background: #28282d;
    }
    QTableCornerButton::section {
        background: #16161a;
        border: none;
    }
    QProgressBar {
        border: 1px solid #28282d;
        border-radius: 6px;
        background: #1a1a1e;
        text-align: center;
        color: #d4d4d8;
        font-weight: 600;
        height: 22px;
    }
    QProgressBar::chunk {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 #d4a030, stop:1 #e8b840);
        border-radius: 6px;
    }
    QDialog {
        background-color: #141416;
    }
    QDialog QPushButton {
        min-width: 80px;
    }
    QLabel {
        color: #d4d4d8;
    }
    QLabel#titleLabel {
        font-size: 14pt;
        font-weight: 700;
        color: #e8e8ec;
    }
    QLabel#subtitleLabel {
        font-size: 8.5pt;
        color: #8888aa;
    }
    QLineEdit {
        background-color: #1a1a1e;
        border: 1px solid #3a3a44;
        border-radius: 6px;
        padding: 6px 10px;
        color: #d4d4d8;
        selection-background-color: #d4a030;
    }
    QLineEdit:focus {
        border-color: #d4a030;
        background-color: #22222a;
    }
    QCheckBox {
        color: #d4d4d8;
        spacing: 8px;
    }
    QCheckBox::indicator {
        width: 16px;
        height: 16px;
        border-radius: 4px;
        border: 2px solid #4a4a55;
        background: #1a1a1e;
    }
    QCheckBox::indicator:checked {
        background: #d4a030;
        border-color: #d4a030;
    }
    QCheckBox::indicator:hover {
        border-color: #d4a030;
    }
    QComboBox {
        background: #1a1a1e;
        border: 1px solid #3a3a44;
        border-radius: 6px;
        padding: 6px 10px;
        color: #d4d4d8;
    }
    QComboBox::drop-down {
        border: none;
        width: 20px;
    }
    QComboBox::down-arrow {
        image: none;
        border-left: 5px solid transparent;
        border-right: 5px solid transparent;
        border-top: 5px solid #d4a030;
        margin-right: 6px;
    }
    QComboBox QAbstractItemView {
        background: #1a1a1e;
        border: 1px solid #3a3a44;
        selection-background-color: #2a3a5a;
    }
    QScrollBar:vertical {
        background: #141416;
        width: 10px;
        border-radius: 5px;
        margin: 2px;
    }
    QScrollBar::handle:vertical {
        background: #3a3a44;
        border-radius: 5px;
        min-height: 30px;
    }
    QScrollBar::handle:vertical:hover {
        background: #d4a030;
    }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        height: 0;
    }
    QScrollBar:horizontal {
        background: #141416;
        height: 10px;
        border-radius: 5px;
        margin: 2px;
    }
    QScrollBar::handle:horizontal {
        background: #3a3a44;
        border-radius: 5px;
        min-width: 30px;
    }
    QScrollBar::handle:horizontal:hover {
        background: #d4a030;
    }
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
        width: 0;
    }
    QStatusBar {
        background: #0f0f11;
        color: #8888aa;
        border-top: 1px solid #1e1e22;
        padding: 4px 8px;
        font-size: 8pt;
    }
    QStatusBar::item {
        border: none;
    }
    QToolTip {
        background: #1a1a1e;
        color: #d4d4d8;
        border: 1px solid #d4a030;
        border-radius: 4px;
        padding: 4px 8px;
        font-size: 8pt;
    }
    QMenu {
        background: #1a1a1e;
        border: 1px solid #3a3a44;
        border-radius: 6px;
        padding: 4px;
    }
    QMenu::item {
        padding: 6px 20px;
        border-radius: 4px;
    }
    QMenu::item:selected {
        background: #2a3a5a;
    }
    QMenu::separator {
        height: 1px;
        background: #3a3a44;
        margin: 4px 8px;
    }
    QGroupBox {
        border: 1px solid #28282d;
        border-radius: 8px;
        margin-top: 12px;
        padding-top: 8px;
        font-weight: 600;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 12px;
        padding: 0 8px;
        color: #d4d4d8;
    }
    """
    app.setStyleSheet(style)
