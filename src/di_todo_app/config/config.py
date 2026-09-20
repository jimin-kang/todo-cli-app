import tomllib
from typing import Literal

from pydantic import BaseModel, ConfigDict

from di_todo_app.exception.exception import InvalidConfiguration

class AppConfig(BaseModel):
    """
    Class to store all application config.
    """
    storage_type: Literal['memory', 'json', 'db']
    model_config = ConfigDict(from_attributes=True) 

def load_config() -> AppConfig:
    """
    Load configuration from the TOML config (placed in the project root).
    """
    try:
        with open("config.toml", "rb") as f:
            config = tomllib.load(f)
        return AppConfig(storage_type=config["storage_type"])
    except Exception as e:
        raise InvalidConfiguration(e)

        