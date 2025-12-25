"""Ollama helper utilities.

This module centralizes Ollama installation detection, service management, and
model verification.

The goal is to avoid opaque provider failures like HTTP 404 by:
- Detecting whether Ollama is installed
- Starting the Ollama service when needed
- Ensuring at least one model is available (optionally auto-pulling)
- Producing actionable error messages
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import httpx

from src.utils.logger import get_logger

logger = get_logger(__name__)


class OllamaHelper:
    """Helper class for managing Ollama installation and service."""

    DEFAULT_HOST = "http://localhost:11434"

    RECOMMENDED_MODELS = [
        "llama3.2:1b",
        "llama3.2:3b",
        "phi3:mini",
        "gemma2:2b",
        "qwen2:1.5b",
    ]

    def __init__(self, host: str | None = None):
        self.host = (host or self.DEFAULT_HOST).rstrip("/")
        self.api_base = f"{self.host}/api"

    def is_installed(self) -> bool:
        ollama_path = shutil.which("ollama")
        if ollama_path:
            logger.debug(f"Ollama found at: {ollama_path}")
            return True

        # Windows common locations (when PATH isn't updated yet)
        common_paths = [
            Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "Ollama" / "ollama.exe",
            Path(os.environ.get("PROGRAMFILES", "")) / "Ollama" / "ollama.exe",
            Path(os.environ.get("USERPROFILE", "")) / "AppData" / "Local" / "Programs" / "Ollama" / "ollama.exe",
        ]

        for p in common_paths:
            try:
                if p.exists():
                    logger.debug(f"Ollama found at: {p}")
                    return True
            except Exception:
                continue

        logger.warning("Ollama is not installed")
        return False

    def is_running(self) -> bool:
        try:
            with httpx.Client(timeout=5) as client:
                r = client.get(f"{self.api_base}/tags")
            return r.status_code == 200
        except (httpx.ConnectError, httpx.ConnectTimeout):
            logger.debug("Ollama service is not running")
            return False
        except Exception as e:
            logger.debug(f"Ollama running check failed: {e}")
            return False

    def start_service(self) -> Tuple[bool, str]:
        if self.is_running():
            return True, "Ollama is already running"

        logger.info("Attempting to start Ollama service...")

        try:
            if sys.platform == "win32":
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE

                subprocess.Popen(
                    ["ollama", "serve"],
                    startupinfo=startupinfo,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    creationflags=subprocess.CREATE_NO_WINDOW,
                )
            else:
                subprocess.Popen(
                    ["ollama", "serve"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )

            for i in range(30):
                time.sleep(1)
                if self.is_running():
                    logger.info("Ollama service started successfully")
                    return True, "Ollama service started successfully"
                logger.debug(f"Waiting for Ollama to start... ({i + 1}/30)")

            return False, "Ollama service failed to start within 30 seconds"

        except FileNotFoundError:
            return False, "Ollama executable not found. Please install Ollama first."
        except Exception as e:
            return False, f"Failed to start Ollama: {e}"

    def get_installed_models(self) -> List[Dict[str, Any]]:
        if not self.is_running():
            return []

        try:
            with httpx.Client(timeout=10) as client:
                r = client.get(f"{self.api_base}/tags")
            if r.status_code != 200:
                return []
            data = r.json()
            if not isinstance(data, dict):
                return []
            models = data.get("models", [])
            if not isinstance(models, list):
                return []
            return [m for m in models if isinstance(m, dict)]
        except Exception as e:
            logger.warning(f"Failed to get models: {e}")
            return []

    def is_model_installed(self, model_name: str) -> bool:
        models = self.get_installed_models()
        full_names = [str(m.get("name", "")) for m in models]

        # If the caller specified a tag (e.g. llama3.2:3b), require an exact match.
        if ":" in model_name:
            return model_name in full_names

        # Otherwise accept any tag for that base model (e.g. "llama3.2").
        base_name = model_name.split(":")[0]
        return any(n.split(":")[0] == base_name for n in full_names)

    def pull_model(self, model_name: str) -> Tuple[bool, str]:
        if not self.is_running():
            ok, msg = self.start_service()
            if not ok:
                return False, f"Cannot pull model: {msg}"

        logger.info(f"Pulling Ollama model: {model_name}")

        # Prefer CLI because it gives better progress and works across versions.
        # Fall back to API if CLI isn't available.
        try:
            proc = subprocess.run(
                ["ollama", "pull", model_name],
                capture_output=True,
                text=True,
                timeout=60 * 20,
            )
            if proc.returncode == 0:
                return True, f"Model {model_name} installed successfully"
            err = (proc.stderr or proc.stdout or "").strip()
            return False, err or "Model pull failed"
        except FileNotFoundError:
            pass
        except subprocess.TimeoutExpired:
            return False, "Model pull timed out. The model may be too large."
        except Exception as e:
            logger.debug(f"ollama pull via CLI failed: {e}")

        try:
            with httpx.Client(timeout=60 * 20) as client:
                r = client.post(f"{self.api_base}/pull", json={"name": model_name})
            if r.status_code != 200:
                return False, f"Failed to pull model: HTTP {r.status_code}"

            if self.is_model_installed(model_name):
                return True, f"Model {model_name} installed successfully"
            return False, "Model pull completed but model not found"
        except httpx.TimeoutException:
            return False, "Model pull timed out. The model may be too large."
        except Exception as e:
            return False, f"Failed to pull model: {e}"

    def get_first_available_model(self) -> Optional[str]:
        models = self.get_installed_models()
        if models:
            name = models[0].get("name")
            return str(name) if name else None
        return None

    def ensure_ready(self, preferred_model: str = "llama3.2:3b") -> Tuple[bool, str, Optional[str]]:
        if not self.is_installed():
            return (
                False,
                "Ollama is not installed. Install it from https://ollama.com/download and restart the application.",
                None,
            )

        if not self.is_running():
            ok, msg = self.start_service()
            if not ok:
                return False, msg, None

        if self.is_model_installed(preferred_model):
            return True, f"Using model: {preferred_model}", preferred_model

        existing = self.get_first_available_model()
        if existing:
            logger.info(f"Preferred model '{preferred_model}' not found, using available model '{existing}'")
            return True, f"Using available model: {existing}", existing

        # No models installed: try to pull a small one automatically.
        small_model = "llama3.2:1b"
        ok, msg = self.pull_model(small_model)
        if ok:
            return True, f"Downloaded and using model: {small_model}", small_model

        return (
            False,
            f"No Ollama models available. Please run: ollama pull {small_model}. Error: {msg}",
            None,
        )

    def test_generation(self, model: str) -> Tuple[bool, str]:
        try:
            with httpx.Client(timeout=30) as client:
                r = client.post(
                    f"{self.api_base}/generate",
                    json={
                        "model": model,
                        "prompt": "Say 'OK' and nothing else.",
                        "stream": False,
                        "options": {"num_predict": 10},
                    },
                )
            if r.status_code == 200:
                return True, "Model is working correctly"
            if r.status_code == 404:
                return False, f"Model '{model}' not found"
            return False, f"Model test failed: HTTP {r.status_code}"
        except Exception as e:
            return False, f"Model test failed: {e}"

    def get_installation_instructions(self) -> str:
        return (
            "\n"
            "\n╔══════════════════════════════════════════════════════════════╗"
            "\n║                    OLLAMA INSTALLATION                        ║"
            "\n╠══════════════════════════════════════════════════════════════╣"
            "\n║  Ollama provides FREE local AI - no API keys needed!         ║"
            "\n║                                                              ║"
            "\n║  1. Go to: https://ollama.com/download                       ║"
            "\n║  2. Install Ollama                                            ║"
            "\n║  3. Run: ollama pull llama3.2:1b                              ║"
            "\n║  4. Restart this application                                  ║"
            "\n╚══════════════════════════════════════════════════════════════╝\n"
        )


_ollama_helper: OllamaHelper | None = None


def get_ollama_helper(host: str | None = None) -> OllamaHelper:
    global _ollama_helper
    if _ollama_helper is None or host:
        _ollama_helper = OllamaHelper(host)
    return _ollama_helper
