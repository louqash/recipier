"""
Singleton config loader for the backend.
Loads configuration once at startup and caches it.
"""

import logging
import os
from typing import Optional

from recipier.config import TaskConfig

logger = logging.getLogger(__name__)


class ConfigLoader:
    """Singleton config loader."""

    _instance: Optional["ConfigLoader"] = None
    _config: Optional[TaskConfig] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def load(self) -> TaskConfig:
        """Load config from file (or return cached instance)."""
        if self._config is None:
            config_path = os.path.join(os.getcwd(), "my_config.json")
            if os.path.exists(config_path):
                logger.info(f"✅ Loading config from {config_path}")
                self._config = TaskConfig.from_file(config_path)
            else:
                logger.warning(f"⚠️  Config file not found at {config_path}, using defaults")
                self._config = TaskConfig()

        return self._config

    @property
    def config(self) -> TaskConfig:
        """Get the cached config (loads if not yet loaded)."""
        return self.load()


# Global singleton instance
_config_loader = ConfigLoader()


def get_config() -> TaskConfig:
    """Get the application config (singleton)."""
    return _config_loader.config
