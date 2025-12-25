"""Main entry point for AI PC Controller.

This startup sequence:
1) Checks for Ollama availability (if configured)
2) Attempts to start Ollama if not running
3) Verifies at least one model is available
4) Initializes the AI engine
5) Launches the GUI or CLI
"""

from __future__ import annotations

from src.ai.ai_engine import AIEngine
from src.controllers.controller_manager import ControllerManager
from src.utils.config_manager import get_config_manager
from src.utils.logger import get_logger, setup_logger
from src.utils.ollama_helper import get_ollama_helper

logger = get_logger(__name__)


def check_ollama_readiness() -> tuple[bool, str]:
    """Check if Ollama is ready (installed, running, has models)."""

    print("\n" + "=" * 60)
    print("   AI PC CONTROLLER - Checking AI Availability")
    print("=" * 60 + "\n")

    cfg = get_config_manager().config

    # Only do this if Ollama is the configured provider
    if cfg.ai.provider.lower() != "ollama":
        print(f"  Configured provider: {cfg.ai.provider}")
        print("  (Skipping Ollama checks)\n")
        return True, f"Using {cfg.ai.provider}"

    helper = get_ollama_helper(cfg.ai.ollama.host)

    print("[1/4] Checking Ollama installation...")
    if not helper.is_installed():
        print("  ✗ Ollama is not installed")
        print(helper.get_installation_instructions())
        return False, "Ollama not installed"
    print("  ✓ Ollama is installed")

    print("\n[2/4] Checking Ollama service...")
    if not helper.is_running():
        print("  → Ollama is not running, attempting to start...")
        ok, msg = helper.start_service()
        if ok:
            print(f"  ✓ {msg}")
        else:
            print(f"  ✗ {msg}")
            return False, msg
    else:
        print("  ✓ Ollama service is running")

    print("\n[3/4] Checking for AI models...")
    models = helper.get_installed_models()
    if not models:
        print("  ✗ No models installed")
        print("  → Attempting to download a small AI model (llama3.2:1b)...")
        print("     This may take a few minutes...")

        ok, msg = helper.pull_model("llama3.2:1b")
        if ok:
            print(f"  ✓ {msg}")
        else:
            print(f"  ✗ {msg}")
            print("\n  Please manually run: ollama pull llama3.2:1b")
            return False, msg
    else:
        model_names = [str(m.get("name", "unknown")) for m in models]
        print(f"  ✓ Found models: {', '.join(model_names[:3])}")

    print("\n[4/4] Initializing AI Engine...")
    return True, "Ollama ready"


def run_cli() -> None:
    cfg = get_config_manager().config
    engine = AIEngine(config=cfg)
    controllers = ControllerManager()

    ok, msg = engine.initialize()
    if not ok:
        print(f"AI initialization failed: {msg}")
        print("Continuing in limited mode...\n")

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

    logger.info("Starting AI PC Controller")

    # Pre-check Ollama readiness if it's the configured provider
    ready, msg = check_ollama_readiness()
    if ready:
        print(f"  ✓ {msg}\n")
        print("=" * 60)
        print("   Starting Application")
        print("=" * 60 + "\n")
    else:
        print("\n" + "!" * 60)
        print("   AI SETUP INCOMPLETE")
        print("!" * 60)
        print(f"\nError: {msg}")
        print("\nYou can still start the application, but AI features may not work.")
        print("Press Enter to continue, or Ctrl+C to exit...\n")
        try:
            input()
        except KeyboardInterrupt:
            print("\nExiting.")
            return

    try:
        from src.gui.main_window import run_app

        # Initialize engine once
        engine = AIEngine(config=cfg)
        ok, msg = engine.initialize()

        if ok:
            logger.info(f"AI initialized: {msg}")
        else:
            logger.warning(f"AI initialization failed: {msg}")

        run_app(ai_engine=engine)
    except Exception as e:
        logger.warning(f"Failed to start GUI, falling back to CLI: {e}")
        run_cli()


if __name__ == "__main__":
    main()
