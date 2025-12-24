from src.utils.config_manager import get_config_manager
from src.utils.exceptions import AIControllerError
from src.utils.validators import validate_percentage


def test_exceptions_to_dict():
    e = AIControllerError("boom", error_code="X", details={"a": 1})
    d = e.to_dict()
    assert d["error_type"] == "AIControllerError"
    assert d["error_code"] == "X"
    assert d["details"]["a"] == 1


def test_config_manager_get():
    cfg = get_config_manager().config
    assert cfg.ai.provider
    assert get_config_manager().get("ai.provider") == cfg.ai.provider


def test_validate_percentage():
    assert validate_percentage(0) == 0
    assert validate_percentage(50) == 50
    assert validate_percentage(999) == 100
