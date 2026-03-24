try:
    from mars_app.gui import run_gui
except ModuleNotFoundError as error:
    missing_name = getattr(error, "name", "")
    if missing_name == "PyQt6":
        raise SystemExit(
            "PyQt6 не установлен. Установите пакет командой: python -m pip install PyQt6"
        ) from error
    raise


if __name__ == "__main__":
    run_gui()
