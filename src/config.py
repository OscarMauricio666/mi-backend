"""
Configuración de la aplicación.

Carga las variables de entorno y provee la configuración global.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Configuración de la aplicación cargada desde variables de entorno."""

    app_name: str = "Mi Backend API"
    app_version: str = "1.0.0"
    debug: bool = False

    # MongoDB Atlas
    mongodb_url: str = ""
    database_name: str = "mi_backend"

    # Anthropic API
    anthropic_api_key: str = ""

    # External APIs
    newsapi_key: str = ""
    football_api_key: str = ""

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    """Obtiene la configuración cacheada de la aplicación."""
    return Settings()
