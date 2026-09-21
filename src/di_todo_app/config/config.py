from pathlib import Path
import tomllib
from typing import Literal

from pydantic import BaseModel, ConfigDict

from di_todo_app.exception.exception import InvalidConfiguration

class AppConfig(BaseModel):
    """
    Class to store all application config.
    """
    storage_type: Literal['memory', 'json', 'db']
    json_path: Path
    db_path: Path
    model_config = ConfigDict(from_attributes=True) 

def load_config(config_path: Path) -> AppConfig:
    """
    Load configuration from the TOML config.
    """
    try:
        project_root = config_path.parent
        with config_path.open("rb") as f:
            config = tomllib.load(f)
        
        return AppConfig(
            storage_type=config["storage_type"],
            json_path=(project_root / config["json_path"]).resolve(),
            db_path=(project_root / config["db_path"]).resolve()
        )
    except Exception as e:
        raise InvalidConfiguration(e)

        