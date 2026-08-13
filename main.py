"""Punto de entrada del Analizador FTIR - Industrial Inspection Service."""
import sys
import traceback

from app.config import get_base_path


def main():
    from app.ui.main_window import MainWindow
    app = MainWindow()
    app.mainloop()


if __name__ == "__main__":
    try:
        main()
    except Exception:
        crash_log = get_base_path() / "crash.log"
        with open(crash_log, "w", encoding="utf-8") as f:
            f.write(traceback.format_exc())
        raise
