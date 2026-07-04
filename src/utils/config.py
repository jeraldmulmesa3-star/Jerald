"""Configuration Management

Handles system configuration and settings.
"""

import json
import os
from typing import Any, Dict


class Config:
    """System configuration management."""

    # Default configuration
    DEFAULTS = {
        'collection_interval': 5,
        'max_history': 1000,
        'api_port': 8000,
        'api_host': '0.0.0.0',
        'debug': False,
        'log_level': 'INFO',
        'database': {
            'type': 'sqlite',
            'path': 'performance_tracking.db',
        },
        'alerts': {
            'enabled': True,
            'check_interval': 10,
        },
    }

    def __init__(self, config_file: str | None = None):
        """
        Initialize configuration.

        Args:
            config_file: Path to configuration file (optional)
        """
        self.config = self.DEFAULTS.copy()
        
        if config_file and os.path.exists(config_file):
            self.load_from_file(config_file)

    def load_from_file(self, filepath: str) -> None:
        """Load configuration from file.

        Args:
            filepath: Path to configuration file
        """
        try:
            with open(filepath, 'r') as f:
                if filepath.endswith('.json'):
                    user_config = json.load(f)
                elif filepath.endswith('.yaml') or filepath.endswith('.yml'):
                    import yaml
                    user_config = yaml.safe_load(f)
                else:
                    raise ValueError(f"Unsupported config format: {filepath}")
            
            # Deep merge with defaults
            self._deep_merge(self.config, user_config)
        except Exception as e:
            print(f"Warning: Could not load config file {filepath}: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value.

        Args:
            key: Configuration key (supports dot notation)
            default: Default value if key not found

        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        
        return value if value is not None else default

    def set(self, key: str, value: Any) -> None:
        """Set configuration value.

        Args:
            key: Configuration key (supports dot notation)
            value: Value to set
        """
        keys = key.split('.')
        current = self.config
        
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
        
        current[keys[-1]] = value

    def save_to_file(self, filepath: str) -> None:
        """Save configuration to file.

        Args:
            filepath: Path to save configuration file
        """
        try:
            if filepath.endswith('.json'):
                with open(filepath, 'w') as f:
                    json.dump(self.config, f, indent=2)
            elif filepath.endswith('.yaml') or filepath.endswith('.yml'):
                import yaml
                with open(filepath, 'w') as f:
                    yaml.dump(self.config, f)
        except Exception as e:
            print(f"Error saving config file: {e}")

    def _deep_merge(self, base: Dict, update: Dict) -> None:
        """Deep merge update into base dictionary.

        Args:
            base: Base dictionary to merge into
            update: Dictionary with updates
        """
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value
