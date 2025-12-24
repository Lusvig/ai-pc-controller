"""
Custom Exceptions for AI PC Controller

This module defines all custom exceptions used throughout the application.
Each exception is designed to provide clear, actionable error information.
"""

from typing import Any, Dict, Optional


class AIControllerError(Exception):
    """Base exception for all AI PC Controller errors."""

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        """Initialize the exception."""
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}

    def __str__(self) -> str:
        if self.error_code:
            return f"[{self.error_code}] {self.message}"
        return self.message

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for logging/serialization."""
        return {
            "error_type": self.__class__.__name__,
            "message": self.message,
            "error_code": self.error_code,
            "details": self.details,
        }


# ============================================
# AI Provider Exceptions
# ============================================


class AIProviderError(AIControllerError):
    """Base exception for AI provider errors."""


class AIConnectionError(AIProviderError):
    """Raised when connection to AI provider fails."""

    def __init__(self, provider: str, message: str | None = None):
        super().__init__(
            message or f"Failed to connect to AI provider: {provider}",
            error_code="AI_CONNECTION_ERROR",
            details={"provider": provider},
        )


class AIResponseError(AIProviderError):
    """Raised when AI provider returns an invalid response."""

    def __init__(self, provider: str, response: Any = None, message: str | None = None):
        super().__init__(
            message or f"Invalid response from AI provider: {provider}",
            error_code="AI_RESPONSE_ERROR",
            details={"provider": provider, "response": str(response)[:500]},
        )


class AIModelNotFoundError(AIProviderError):
    """Raised when the specified AI model is not available."""

    def __init__(self, model: str, provider: str):
        super().__init__(
            f"Model '{model}' not found for provider '{provider}'",
            error_code="AI_MODEL_NOT_FOUND",
            details={"model": model, "provider": provider},
        )


class AIRateLimitError(AIProviderError):
    """Raised when AI provider rate limit is exceeded."""

    def __init__(self, provider: str, retry_after: Optional[int] = None):
        super().__init__(
            f"Rate limit exceeded for provider: {provider}",
            error_code="AI_RATE_LIMIT",
            details={"provider": provider, "retry_after": retry_after},
        )


class AIAPIKeyError(AIProviderError):
    """Raised when API key is missing or invalid."""

    def __init__(self, provider: str):
        super().__init__(
            f"Invalid or missing API key for provider: {provider}",
            error_code="AI_API_KEY_ERROR",
            details={"provider": provider},
        )


# ============================================
# Command Execution Exceptions
# ============================================


class CommandError(AIControllerError):
    """Base exception for command execution errors."""


class CommandParseError(CommandError):
    """Raised when a command cannot be parsed."""

    def __init__(self, command: str, reason: str | None = None):
        super().__init__(
            f"Failed to parse command: {reason or 'Unknown error'}",
            error_code="COMMAND_PARSE_ERROR",
            details={"command": command, "reason": reason},
        )


class CommandExecutionError(CommandError):
    """Raised when a command fails to execute."""

    def __init__(self, command: str, action: str, reason: str):
        super().__init__(
            f"Failed to execute '{action}': {reason}",
            error_code="COMMAND_EXECUTION_ERROR",
            details={"command": command, "action": action, "reason": reason},
        )


class CommandNotFoundError(CommandError):
    """Raised when a command action is not recognized."""

    def __init__(self, action: str):
        super().__init__(
            f"Unknown command action: {action}",
            error_code="COMMAND_NOT_FOUND",
            details={"action": action},
        )


class CommandBlockedError(CommandError):
    """Raised when a command is blocked by safety settings."""

    def __init__(self, command: str, reason: str = "Security policy"):
        super().__init__(
            f"Command blocked: {reason}",
            error_code="COMMAND_BLOCKED",
            details={"command": command, "reason": reason},
        )


class CommandTimeoutError(CommandError):
    """Raised when a command times out."""

    def __init__(self, command: str, timeout: float):
        super().__init__(
            f"Command timed out after {timeout} seconds",
            error_code="COMMAND_TIMEOUT",
            details={"command": command, "timeout": timeout},
        )


# ============================================
# Controller Exceptions
# ============================================


class ControllerError(AIControllerError):
    """Base exception for controller errors."""


class ApplicationNotFoundError(ControllerError):
    """Raised when an application cannot be found."""

    def __init__(self, app_name: str, searched_paths: list | None = None):
        super().__init__(
            f"Application not found: {app_name}",
            error_code="APP_NOT_FOUND",
            details={"app_name": app_name, "searched_paths": searched_paths},
        )


class FileOperationError(ControllerError):
    """Raised when a file operation fails."""

    def __init__(self, operation: str, path: str, reason: str):
        super().__init__(
            f"File {operation} failed for '{path}': {reason}",
            error_code="FILE_OPERATION_ERROR",
            details={"operation": operation, "path": path, "reason": reason},
        )


class SystemOperationError(ControllerError):
    """Raised when a system operation fails."""

    def __init__(self, operation: str, reason: str):
        super().__init__(
            f"System operation '{operation}' failed: {reason}",
            error_code="SYSTEM_OPERATION_ERROR",
            details={"operation": operation, "reason": reason},
        )


class PermissionDeniedError(ControllerError):
    """Raised when operation requires elevated permissions."""

    def __init__(self, operation: str):
        super().__init__(
            f"Permission denied for operation: {operation}. Try running as administrator.",
            error_code="PERMISSION_DENIED",
            details={"operation": operation},
        )


class DeviceNotFoundError(ControllerError):
    """Raised when a hardware device is not found."""

    def __init__(self, device_type: str, device_name: str | None = None):
        super().__init__(
            f"{device_type} device not found" + (f": {device_name}" if device_name else ""),
            error_code="DEVICE_NOT_FOUND",
            details={"device_type": device_type, "device_name": device_name},
        )


# ============================================
# Voice Exceptions
# ============================================


class VoiceError(AIControllerError):
    """Base exception for voice-related errors."""


class SpeechRecognitionError(VoiceError):
    """Raised when speech recognition fails."""

    def __init__(self, reason: str):
        super().__init__(
            f"Speech recognition failed: {reason}",
            error_code="SPEECH_RECOGNITION_ERROR",
            details={"reason": reason},
        )


class TextToSpeechError(VoiceError):
    """Raised when text-to-speech fails."""

    def __init__(self, reason: str):
        super().__init__(
            f"Text-to-speech failed: {reason}",
            error_code="TTS_ERROR",
            details={"reason": reason},
        )


class MicrophoneError(VoiceError):
    """Raised when microphone is not available or fails."""

    def __init__(self, reason: str = "Microphone not available"):
        super().__init__(
            reason,
            error_code="MICROPHONE_ERROR",
            details={"reason": reason},
        )


class WakeWordError(VoiceError):
    """Raised when wake word detection fails."""

    def __init__(self, reason: str):
        super().__init__(
            f"Wake word detection failed: {reason}",
            error_code="WAKE_WORD_ERROR",
            details={"reason": reason},
        )


# ============================================
# Configuration Exceptions
# ============================================


class ConfigurationError(AIControllerError):
    """Base exception for configuration errors."""


class ConfigFileNotFoundError(ConfigurationError):
    """Raised when configuration file is not found."""

    def __init__(self, config_path: str):
        super().__init__(
            f"Configuration file not found: {config_path}",
            error_code="CONFIG_NOT_FOUND",
            details={"config_path": config_path},
        )


class ConfigValidationError(ConfigurationError):
    """Raised when configuration validation fails."""

    def __init__(self, field: str, reason: str):
        super().__init__(
            f"Invalid configuration for '{field}': {reason}",
            error_code="CONFIG_VALIDATION_ERROR",
            details={"field": field, "reason": reason},
        )


# ============================================
# Plugin Exceptions
# ============================================


class PluginError(AIControllerError):
    """Base exception for plugin errors."""


class PluginLoadError(PluginError):
    """Raised when a plugin fails to load."""

    def __init__(self, plugin_name: str, reason: str):
        super().__init__(
            f"Failed to load plugin '{plugin_name}': {reason}",
            error_code="PLUGIN_LOAD_ERROR",
            details={"plugin_name": plugin_name, "reason": reason},
        )


class PluginExecutionError(PluginError):
    """Raised when a plugin command fails."""

    def __init__(self, plugin_name: str, command: str, reason: str):
        super().__init__(
            f"Plugin '{plugin_name}' failed executing '{command}': {reason}",
            error_code="PLUGIN_EXECUTION_ERROR",
            details={"plugin_name": plugin_name, "command": command, "reason": reason},
        )


# ============================================
# Database Exceptions
# ============================================


class DatabaseError(AIControllerError):
    """Base exception for database errors."""


class DatabaseConnectionError(DatabaseError):
    """Raised when database connection fails."""

    def __init__(self, db_path: str, reason: str):
        super().__init__(
            f"Failed to connect to database: {reason}",
            error_code="DB_CONNECTION_ERROR",
            details={"db_path": db_path, "reason": reason},
        )


class DatabaseQueryError(DatabaseError):
    """Raised when a database query fails."""

    def __init__(self, query: str, reason: str):
        super().__init__(
            f"Database query failed: {reason}",
            error_code="DB_QUERY_ERROR",
            details={"query": query[:100], "reason": reason},
        )
