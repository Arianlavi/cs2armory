import sys
import os
import ctypes
import subprocess
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import Qt, QTimer


def is_admin() -> bool:
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


def relaunch_as_admin():
    script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    params = subprocess.list2cmdline(sys.argv)

    ret = ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, params, script_dir, 1
    )

    if int(ret) <= 32:
        app = QApplication(sys.argv)
        QMessageBox.critical(
            None,
            "Administrator Rights Required",
            "CS2 Armory needs Administrator rights to manage Windows Firewall rules.\n\n"
            "Please run it again and click \"Yes\" on the UAC prompt.",
        )
    sys.exit()


if not is_admin():
    relaunch_as_admin()

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.main_window import MainWindow
from ui.splash_screen import SplashScreen
from ui.styles import apply_style


def main():
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    apply_style(app)

    splash = SplashScreen()
    splash.show()
    app.processEvents()

    window = MainWindow()
    splash.set_status("Fetching server list from Steam...")

    state = {"revealed": False}

    def reveal():
        if state["revealed"]:
            return
        state["revealed"] = True
        splash.finish(window)

    QTimer.singleShot(20000, reveal)

    window.start(on_ready=reveal)

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
