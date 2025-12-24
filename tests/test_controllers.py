from src.controllers.controller_manager import ControllerManager


def test_controller_manager_unknown_action():
    mgr = ControllerManager()
    res = mgr.execute("does_not_exist")
    assert res.success is False


def test_controller_manager_routes_action(monkeypatch):
    mgr = ControllerManager()

    # Prevent opening a browser.
    import webbrowser

    monkeypatch.setattr(webbrowser, "open", lambda *_a, **_k: True)

    res = mgr.execute("web_search", {"query": "python"})
    assert res.success is True
