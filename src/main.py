"""AI PC Controller - Main Entry Point

Handles startup, dependency checking, and initialization.
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def check_dependencies() -> dict:
    """
    Check which dependencies are available.
    
    Returns:
        Dictionary with dependency status
    """
    status = {
        "core": True,
        "voice": True,
        "optional": {},
        "warnings": []
    }
    
    # Check core dependencies
    core_packages = [
        "customtkinter",
        "requests",
        "loguru",
        "yaml",
        "pydantic"
    ]
    
    for package in core_packages:
        try:
            __import__(package)
        except ImportError:
            status["core"] = False
            status["warnings"].append(f"Missing core package: {package}")
    
    # Check voice dependencies
    try:
        import speech_recognition
        status["optional"]["speech_recognition"] = True
    except ImportError:
        status["optional"]["speech_recognition"] = False
        status["warnings"].append("SpeechRecognition not installed - voice input disabled")
    
    try:
        import pyttsx3
        status["optional"]["pyttsx3"] = True
    except ImportError:
        status["optional"]["pyttsx3"] = False
        status["warnings"].append("pyttsx3 not installed - voice output disabled")
    
    try:
        import pyaudio
        status["optional"]["pyaudio"] = True
    except ImportError:
        status["optional"]["pyaudio"] = False
        # Not critical - speech_recognition can work with other backends
    
    # Check AI dependencies
    try:
        import ollama
        status["optional"]["ollama"] = True
    except ImportError:
        status["optional"]["ollama"] = False
        status["warnings"].append("Ollama package not installed")
    
    return status


def print_startup_banner():
    """Print startup banner."""
    print()
    print("=" * 60)
    print("     AI PC CONTROLLER")
    print("=" * 60)
    print()


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
    """Main entry point."""
    print_startup_banner()
    
    # Check dependencies
    print("[1/4] Checking dependencies...")
    dep_status = check_dependencies()
    
    if not dep_status["core"]:
        print("\n[ERROR] Missing core dependencies!")
        for warning in dep_status["warnings"]:
            print(f"  - {warning}")
        print("\nPlease run: pip install -r requirements.txt")
        sys.exit(1)
    
    print("  [OK] Core dependencies available")
    
    # Print warnings for optional packages
    if dep_status["warnings"]:
        print("\n  [WARNINGS]")
        for warning in dep_status["warnings"]:
            print(f"    - {warning}")
    print()
    
    # Continue with normal startup
    print("[2/4] Loading configuration...")
    from src.utils.logger import setup_logger
    from src.utils.config_manager import get_config
    
    config = get_config()
    setup_logger(
        log_level=config.logging.level,
        log_file=config.logging.file,
        console_output=True
    )
    print("  [OK] Configuration loaded")
    print()
    
    print("[3/4] Initializing AI Engine...")
    from src.ai.ai_engine import AIEngine
    
    engine = AIEngine()
    success, message = engine.initialize()
    
    if success:
        print(f"  [OK] {message}")
    else:
        print(f"  [WARNING] {message}")
        print("  The application will start but AI features may be limited.")
    print()
    
    print("[4/4] Starting GUI...")
    print()
    
    try:
        from src.gui.main_window import MainWindow
        
        app = MainWindow(ai_engine=engine)
        app.run()
        
    except Exception as e:
        print(f"\n[ERROR] Failed to start: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
