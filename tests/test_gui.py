def test_gui_imports():
    # Importing GUI modules should not require a display.
    from src.gui.main_window import MainWindow

    assert MainWindow
