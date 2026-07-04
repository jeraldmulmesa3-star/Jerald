"""Logging Configuration

Sets up logging for the performance tracking system.
"""

import logging
import sys
from datetime import datetime
from typing import Optional


class Logger:
    """Centralized logging configuration."""

    _loggers = {}

    @staticmethod
    def get_logger(name: str, level: str = "INFO", 
                  log_file: Optional[str] = None) -> logging.Logger:
        """Get or create a logger.

        Args:
            name: Logger name
            level: Logging level
            log_file: Optional log file path

        Returns:
            Configured logger instance
        """
        if name in Logger._loggers:
            return Logger._loggers[name]
        
        logger = logging.getLogger(name)
        logger.setLevel(getattr(logging, level.upper()))
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, level.upper()))
        
        # Format
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # File handler if specified
        if log_file:
            try:
                file_handler = logging.FileHandler(log_file)
                file_handler.setLevel(getattr(logging, level.upper()))
                file_handler.setFormatter(formatter)
                logger.addHandler(file_handler)
            except Exception as e:
                logger.warning(f"Could not create file handler: {e}")
        
        Logger._loggers[name] = logger
        return logger

    @staticmethod
    def log_event(logger: logging.Logger, event_type: str, message: str, 
                 data: dict = None) -> None:
        """Log a structured event.

        Args:
            logger: Logger instance
            event_type: Type of event
            message: Event message
            data: Additional event data
        """
        log_message = f"[{event_type}] {message}"
        if data:
            log_message += f" | {data}"
        logger.info(log_message)
