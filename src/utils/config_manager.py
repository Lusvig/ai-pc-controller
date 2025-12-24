"""
Configuration Manager for AI PC Controller

Handles loading, validation, and saving of configuration settings.
Supports YAML config files and environment variables.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any, Optional

import yaml
from dotenv import load_dotenv
from pydantic import BaseModel, Field, validator
from pydantic_settings import BaseSettings

from src import CONFIG_DIR, PROJECT_ROOT
from src.utils.logger import get_logger

logger = get_logger(__name__)


# ============================================
# Pydantic Models for Configuration
# ============================================


class OllamaConfig(BaseModel):
    """Ollama AI provider configuration."""

    host: str = "http://localhost:11434"
    model: str = "llama3.2:3b"
    timeout: int = 60
    context_length: int = 4096


class GeminiConfig(BaseModel):
    """Google Gemini configuration."""

    model: str = "gemini-1.5-flash"
    temperature: float = 0.7
    max_tokens: int = 2048


class GroqConfig(BaseModel):
    """Groq configuration."""

    model: str = "llama-3.1-70b-versatile"
    temperature: float = 0.7
    max_tokens: int = 2048


class AIConfig(BaseModel):
    """AI configuration."""

    provider: str = "ollama"
    ollama: OllamaConfig = Field(default_factory=OllamaConfig)
    gemini: GeminiConfig = Field(default_factory=GeminiConfig)
    groq: GroqConfig = Field(default_factory=GroqConfig)

    @validator("provider")
    def validate_provider(cls, v: str) -> str:
        valid_providers = ["ollama", "gemini", "groq", "openai"]
        if v not in valid_providers:
            raise ValueError(f"Invalid AI provider: {v}. Must be one of {valid_providers}")
        return v


class RecognitionConfig(BaseModel):
    """Speech recognition configuration."""

    engine: str = "google"
    language: str = "en-US"
    timeout: int = 5
    phrase_timeout: int = 3
    energy_threshold: int = 300
    dynamic_energy: bool = True


class TTSConfig(BaseModel):
    """Text-to-speech configuration."""

    engine: str = "pyttsx3"
    voice: Optional[str] = None
    rate: int = 175
    volume: float = 1.0


class WakeWordConfig(BaseModel):
    """Wake word configuration."""

    enabled: bool = False
    phrase: str = "hey computer"
    sensitivity: float = 0.5


class VoiceConfig(BaseModel):
    """Voice configuration."""

    enabled: bool = True
    recognition: RecognitionConfig = Field(default_factory=RecognitionConfig)
    tts: TTSConfig = Field(default_factory=TTSConfig)
    wake_word: WakeWordConfig = Field(default_factory=WakeWordConfig)


class WindowConfig(BaseModel):
    """Window configuration."""

    width: int = 900
    height: int = 700
    min_width: int = 600
    min_height: int = 400
    start_maximized: bool = False
    start_minimized: bool = False
    always_on_top: bool = False


class SystemTrayConfig(BaseModel):
    """System tray configuration."""

    enabled: bool = True
    minimize_to_tray: bool = True
    start_in_tray: bool = False


class ChatConfig(BaseModel):
    """Chat display configuration."""

    font_family: str = "Segoe UI"
    font_size: int = 12
    max_history: int = 1000
    show_timestamps: bool = True


class ColorScheme(BaseModel):
    """Color scheme configuration."""

    background: str = "#1a1a2e"
    secondary: str = "#16213e"
    accent: str = "#0f3460"
    text: str = "#e8e8e8"
    user_message: str = "#4a90d9"
    ai_message: str = "#2ecc71"
    error: str = "#e74c3c"
    warning: str = "#f39c12"


class ColorsConfig(BaseModel):
    """Colors configuration."""

    dark: ColorScheme = Field(default_factory=ColorScheme)
    light: ColorScheme = Field(
        default_factory=lambda: ColorScheme(
            background="#ffffff",
            secondary="#f5f5f5",
            accent="#e0e0e0",
            text="#333333",
            user_message="#1976d2",
            ai_message="#388e3c",
            error="#d32f2f",
            warning="#f57c00",
        )
    )


class GUIConfig(BaseModel):
    """GUI configuration."""

    theme: str = "dark"
    window: WindowConfig = Field(default_factory=WindowConfig)
    system_tray: SystemTrayConfig = Field(default_factory=SystemTrayConfig)
    chat: ChatConfig = Field(default_factory=ChatConfig)
    colors: ColorsConfig = Field(default_factory=ColorsConfig)

    @validator("theme")
    def validate_theme(cls, v: str) -> str:
        valid_themes = ["dark", "light", "system"]
        if v not in valid_themes:
            raise ValueError(f"Invalid theme: {v}. Must be one of {valid_themes}")
        return v


class SafetyConfig(BaseModel):
    """Safety configuration."""

    enabled: bool = True
    confirm_commands: list[str] = Field(
        default_factory=lambda: [
            "shutdown",
            "restart",
            "sleep",
            "hibernate",
            "lock",
            "delete",
            "format",
            "empty_recycle_bin",
        ]
    )
    blocked_commands: list[str] = Field(default_factory=list)
    rate_limit_enabled: bool = True
    max_commands_per_minute: int = 30


class HotkeysConfig(BaseModel):
    """Hotkeys configuration."""

    toggle_listening: str = "ctrl+shift+space"
    emergency_stop: str = "ctrl+shift+escape"
    show_window: str = "ctrl+shift+a"
    take_screenshot: str = "ctrl+shift+s"


class LoggingConfig(BaseModel):
    """Logging configuration."""

    level: str = "INFO"
    file: str = "logs/app.log"
    max_size_mb: int = 50
    backup_count: int = 5
    console_output: bool = True


class DatabaseConfig(BaseModel):
    """Database configuration."""

    path: str = "data/history.db"
    backup_enabled: bool = True
    backup_interval: int = 86400
    max_backups: int = 7


class AppConfig(BaseModel):
    """Complete application configuration."""

    ai: AIConfig = Field(default_factory=AIConfig)
    voice: VoiceConfig = Field(default_factory=VoiceConfig)
    gui: GUIConfig = Field(default_factory=GUIConfig)
    safety: SafetyConfig = Field(default_factory=SafetyConfig)
    hotkeys: HotkeysConfig = Field(default_factory=HotkeysConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)


# ============================================
# Environment Variables Configuration
# ============================================


class EnvConfig(BaseSettings):
    """Environment variables configuration."""

    ai_provider: str = "ollama"

    ollama_host: str = "http://localhost:11434"
    ollama_model: str = "llama3.2:3b"

    gemini_api_key: str = ""
    groq_api_key: str = ""

    openai_api_key: str = ""
    openai_base_url: str = ""

    voice_enabled: bool = True
    wake_word_enabled: bool = False
    wake_word: str = "hey computer"

    log_level: str = "INFO"
    log_file: str = "logs/app.log"

    theme: str = "dark"
    window_width: int = 900
    window_height: int = 700
    start_minimized: bool = False
    minimize_to_tray: bool = True

    database_path: str = "data/history.db"

    global_hotkey: str = "ctrl+shift+space"
    emergency_stop: str = "ctrl+shift+escape"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# ============================================
# Configuration Manager
# ============================================


class ConfigManager:
    """Manages application configuration."""

    _instance: Optional["ConfigManager"] = None
    _config: Optional[AppConfig] = None
    _env: Optional[EnvConfig] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._config is None:
            self._load_configuration()

    def _load_configuration(self) -> None:
        env_path = PROJECT_ROOT / ".env"
        if env_path.exists():
            load_dotenv(env_path)
            logger.debug(f"Loaded environment from {env_path}")

        self._env = EnvConfig()

        config_path = CONFIG_DIR / "default_config.yaml"

        if config_path.exists():
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    yaml_config = yaml.safe_load(f) or {}

                yaml_config.pop("app", None)

                self._config = AppConfig(**yaml_config)
                logger.info(f"Loaded configuration from {config_path}")

            except Exception as e:
                logger.warning(f"Failed to load config file: {e}. Using defaults.")
                self._config = AppConfig()
        else:
            logger.info("No config file found. Using default configuration.")
            self._config = AppConfig()

        self._apply_env_overrides()

    def _apply_env_overrides(self) -> None:
        assert self._config is not None
        assert self._env is not None

        if self._env.ai_provider:
            self._config.ai.provider = self._env.ai_provider
        if self._env.ollama_host:
            self._config.ai.ollama.host = self._env.ollama_host
        if self._env.ollama_model:
            self._config.ai.ollama.model = self._env.ollama_model

        self._config.voice.enabled = self._env.voice_enabled
        self._config.voice.wake_word.enabled = self._env.wake_word_enabled
        self._config.voice.wake_word.phrase = self._env.wake_word

        self._config.gui.theme = self._env.theme
        self._config.gui.window.width = self._env.window_width
        self._config.gui.window.height = self._env.window_height
        self._config.gui.window.start_minimized = self._env.start_minimized
        self._config.gui.system_tray.minimize_to_tray = self._env.minimize_to_tray

        self._config.logging.level = self._env.log_level
        self._config.logging.file = self._env.log_file

        self._config.database.path = self._env.database_path

        self._config.hotkeys.toggle_listening = self._env.global_hotkey
        self._config.hotkeys.emergency_stop = self._env.emergency_stop

    @property
    def config(self) -> AppConfig:
        assert self._config is not None
        return self._config

    @property
    def env(self) -> EnvConfig:
        assert self._env is not None
        return self._env

    def get(self, key: str, default: Any = None) -> Any:
        try:
            value: Any = self.config
            for part in key.split("."):
                if hasattr(value, part):
                    value = getattr(value, part)
                elif isinstance(value, dict):
                    value = value.get(part)
                else:
                    return default
            return value
        except Exception:
            return default

    def set(self, key: str, value: Any) -> None:
        parts = key.split(".")
        obj: Any = self.config

        for part in parts[:-1]:
            obj = getattr(obj, part)

        setattr(obj, parts[-1], value)
        logger.debug(f"Configuration updated: {key} = {value}")

    def save(self, path: Path | None = None) -> None:
        if path is None:
            path = CONFIG_DIR / "user_config.yaml"

        config_dict = self.config.model_dump()

        with open(path, "w", encoding="utf-8") as f:
            yaml.dump(config_dict, f, default_flow_style=False, indent=2)

        logger.info(f"Configuration saved to {path}")

    def reload(self) -> None:
        self._config = None
        self._env = None
        self._load_configuration()
        logger.info("Configuration reloaded")

    def get_api_key(self, provider: str) -> Optional[str]:
        env = self.env
        key_map = {
            "gemini": env.gemini_api_key,
            "groq": env.groq_api_key,
            "openai": env.openai_api_key,
        }

        return key_map.get(provider)


@lru_cache(maxsize=1)
def get_config_manager() -> ConfigManager:
    """Get the global configuration manager instance."""

    return ConfigManager()


def get_config() -> AppConfig:
    """Shortcut to get the application configuration."""

    return get_config_manager().config
