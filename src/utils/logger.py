"""
Logging Configuration for AI PC Controller

This module sets up comprehensive logging using loguru.
Provides file logging, console output, and log rotation.
"""

import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

from loguru import logger

from src import LOGS_DIR


def _strip_loguru_colors(format_string: str) -> str:
    return (
        format_string.replace("<green>", "")
        .replace("</green>", "")
        .replace("<level>", "")
        .replace("</level>", "")
        .replace("<cyan>", "")
        .replace("</cyan>", "")
    )


def setup_logger(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    max_size_mb: int = 50,
    backup_count: int = 5,
    console_output: bool = True,
    format_string: Optional[str] = None,
) -> None:
    """Configure the application logger."""

    logger.remove()

    if format_string is None:
        format_string = (
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level>"
        )

    if console_output:
        logger.add(
            sys.stdout,
            format=format_string,
            level=log_level,
            colorize=True,
            backtrace=True,
            diagnose=True,
        )

    resolved_log_file: Path
    if log_file is None:
        resolved_log_file = LOGS_DIR / "app.log"
    else:
        resolved_log_file = Path(log_file)

    resolved_log_file.parent.mkdir(parents=True, exist_ok=True)

    plain_format = _strip_loguru_colors(format_string)

    logger.add(
        resolved_log_file,
        format=plain_format,
        level=log_level,
        rotation=f"{max_size_mb} MB",
        retention=backup_count,
        compression="zip",
        backtrace=True,
        diagnose=True,
        encoding="utf-8",
    )

    error_log = resolved_log_file.parent / "errors.log"
    logger.add(
        error_log,
        format=plain_format,
        level="ERROR",
        rotation=f"{max_size_mb // 2} MB",
        retention=backup_count,
        compression="zip",
        backtrace=True,
        diagnose=True,
        encoding="utf-8",
    )

    logger.info(f"Logger initialized - Level: {log_level}, File: {resolved_log_file}")


def get_logger(name: str | None = None):
    """Get a logger instance."""

    if name:
        return logger.bind(name=name)
    return logger


class CommandLogger:
    """Specialized logger for command history."""

    def __init__(self, log_dir: Path | None = None):
        self.log_dir = log_dir or LOGS_DIR / "commands"
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.current_file: Path | None = None
        self.current_date: str | None = None

    def _get_log_file(self) -> Path:
        today = datetime.now().strftime("%Y-%m-%d")

        if self.current_date != today:
            self.current_date = today
            self.current_file = self.log_dir / f"commands_{today}.log"

        assert self.current_file is not None
        return self.current_file

    def log_command(
        self,
        user_input: str,
        ai_response: str,
        action: str,
        success: bool,
        execution_time: float | None = None,
        error: str | None = None,
    ) -> None:
        log_file = self._get_log_file()

        timestamp = datetime.now().isoformat()
        status = "SUCCESS" if success else "FAILED"

        log_entry = f"[{timestamp}] [{status}]\n  Input: {user_input}\n  Action: {action}\n"

        if ai_response:
            log_entry += f"  AI Response: {ai_response[:200]}...\n"

        if execution_time is not None:
            log_entry += f"  Execution Time: {execution_time:.3f}s\n"

        if error:
            log_entry += f"  Error: {error}\n"

        log_entry += "\n"

        with open(log_file, "a", encoding="utf-8") as f:
            f.write(log_entry)

        if success:
            logger.info(f"Command executed: {action}")
        else:
            logger.error(f"Command failed: {action} - {error}")


command_logger = CommandLogger()
