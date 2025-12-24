"""Main entry point for AI PC Controller."""

from __future__ import annotations

from src.ai.ai_engine import AIEngine
from src.controllers.controller_manager import ControllerManager
from src.utils.config_manager import get_config_manager
from src.utils.logger import get_logger, setup_logger

logger = get_logger(__name__)


def run_cli() -> None:
    cfg = get_config_manager().config
    engine = AIEngine(config=cfg)
    controllers = ControllerManager()

    print("AI PC Controller (CLI mode). Type 'exit' to quit.")
    while True:
        text = input("> ").strip()
        if text.lower() in {"exit", "quit"}:
            break

        parsed = engine.safe_process(text)
        if parsed.action == "chat":
            print(parsed.message)
            continue

        result = controllers.execute(parsed.action, parsed.params)
        print(result.message)


def main() -> None:
    cfg = get_config_manager().config
    setup_logger(
        log_level=cfg.logging.level,
        log_file=cfg.logging.file,
        max_size_mb=cfg.logging.max_size_mb,
        backup_count=cfg.logging.backup_count,
        console_output=cfg.logging.console_output,
    )

    try:
        from src.gui.main_window import run_app

        run_app()
    except Exception as e:
        logger.warning(f"Failed to start GUI, falling back to CLI: {e}")
        run_cli()


if __name__ == "__main__":
    main()
