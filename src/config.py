from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict

# NOTE: starting from pydantic v2.0, type hints are mandatory


# configuration .env
class BaseConfig(BaseSettings):
    ENV_STATE: Optional[str] = None  # which env will be used (dev, test, prod)

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


#  configurazione per ogni env
class GlobalConfig(BaseConfig):
    DATABASE_URL: Optional[str] = None
    DB_FORCE_ROLL_BACK: bool = False  # delete database after test
    OPENAI_API_KEY: Optional[str] = None
    # DEEPAI_API_KEY: Optional[str] = None

    MAILGUN_API_KEY: Optional[str] = None
    MAILGUN_DOMAIN: Optional[str] = None


class DevConfig(GlobalConfig):
    model_config = SettingsConfigDict(env_prefix="DEV_")


class ProdConfig(GlobalConfig):
    model_config = SettingsConfigDict(env_prefix="PROD_")


class TestConfig(GlobalConfig):
    # not needed in .env, hardcoded here
    DATABASE_URL: str = "sqlite:///test.db"
    DB_FORCE_ROLL_BACK: bool = True

    model_config = SettingsConfigDict(env_prefix="TEST_")


@lru_cache()
def get_config(env_state: str):
    configs = {"dev": DevConfig, "test": TestConfig, "prod": ProdConfig}
    return configs[env_state]()


config = get_config(BaseConfig().ENV_STATE)
