from src.ai.ai_engine import AIEngine
from src.ai.response_parser import ResponseParser
from src.utils.config_manager import get_config


def test_response_parser_json():
    parsed = ResponseParser.parse('{"action":"chat","params":{},"message":"hi"}')
    assert parsed.action == "chat"
    assert parsed.message == "hi"


def test_response_parser_fallback_to_chat():
    parsed = ResponseParser.parse("not json")
    assert parsed.action == "chat"
    assert parsed.message == "not json"


def test_ai_engine_process_monkeypatched_provider(monkeypatch):
    cfg = get_config()
    engine = AIEngine(config=cfg)

    def fake_generate(prompt, system_prompt=None):
        return '{"action":"get_system_info","params":{},"message":"ok"}'

    monkeypatch.setattr(engine.provider, "generate", fake_generate)
    parsed = engine.process("hi")
    assert parsed.action == "get_system_info"
    assert parsed.message == "ok"
