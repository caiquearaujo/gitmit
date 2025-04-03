"""Service for the configuration of the application."""

import configparser

from typing import Optional

from pathlib import Path

from pydantic import BaseModel

from src.services.database import ConnectionModel, LLMUsageDatabaseService
from src.llms.ollamallm import OllamaLLMService
from src.llms.googlellm import GoogleLLMService
from src.llms import LLMService


class Services(BaseModel):
    """Services for the application."""

    commit: LLMService
    resume: Optional[LLMService]
    database: LLMUsageDatabaseService

    class Config:
        arbitrary_types_allowed = True


def __required_param(config: configparser.ConfigParser, section: str, param: str):
    """Check if the parameter is required.

    Args:
        config (configparser.ConfigParser): The config to check.
    """
    value = config.get(section, param, fallback="").strip()

    if not value:
        raise ValueError(f"Missing required parameter '{param}' in section '{section}'")


def __parse_model(model: str, allow_none=False) -> Optional[dict[str, str]]:
    """Parse the model from the config.

    Args:
        model (str): The model to parse.
    """
    model = model.strip()

    if allow_none and not model:
        return None

    parts = model.split("/", 1)

    if len(parts) != 2 or not parts[0] or not parts[1]:
        raise ValueError(
            f"Unexpected model format: {model}. Expected format: service/model"
        )

    return {"service": parts[0], "model": parts[1]}


def __evaluate(config: configparser.ConfigParser):
    """Evaluate the config.

    Args:
        config (configparser.ConfigParser): The config to evaluate.
    """
    connection = ConnectionModel(
        host=config.get("mysql", "host"),
        port=config.get("mysql", "port"),
        user=config.get("mysql", "user"),
        password=config.get("mysql", "password"),
        database=config.get("mysql", "database"),
    )

    database = LLMUsageDatabaseService(connection)
    database.start()

    services = {
        "google": lambda c, m: GoogleLLMService(
            api_key=c.get("google", "api_key"), database=database, model=m
        ),
        "ollama": lambda c, m: OllamaLLMService(host=c.get("ollama", "host"), model=m),
    }

    commit_validators = {
        "google": lambda c: __required_param(c, "google", "api_key"),
        "ollama": lambda c: __required_param(c, "ollama", "host"),
    }

    resume_validators = {
        "ollama": lambda c: __required_param(c, "ollama", "host"),
    }

    commit_value = config.get("models", "commit", fallback="").strip()
    resume_value = config.get("models", "resume", fallback="").strip()

    if not commit_value:
        raise ValueError("Missing required parameter 'commit' in section 'models'")

    commit_model = __parse_model(commit_value)
    resume_model = __parse_model(resume_value) if resume_value else None

    try:
        commit_validators[commit_model["service"]](config)
    except KeyError as e:
        raise ValueError(
            f"Invalid commit service: '{commit_model['service']}'. "
            f"Allowed services: {list(commit_validators.keys())}"
        ) from e

    if resume_model is not None:
        try:
            resume_validators[resume_model["service"]](config)
        except KeyError as e:
            raise ValueError(
                f"Invalid resume service: '{resume_model['service']}'. "
                f"Allowed services: {list(resume_validators.keys())}"
            ) from e

    return Services(
        commit=services[commit_model["service"]](config, commit_model["model"]),
        resume=(
            services[resume_model["service"]](config, resume_model["model"])
            if resume_model
            else None
        ),
        database=database,
    )


def init():
    """Initialize the config.

    Returns:
        Services: The services for the application.
    """
    path = Path.home() / ".config" / "gitmit"
    path.mkdir(parents=True, exist_ok=True)
    file = path.joinpath("config.ini").as_posix()

    config = configparser.ConfigParser()

    if not Path(file).exists():
        __create(config, file)
    else:
        __read(config, file)

    return __evaluate(config)


def __read(config: configparser.ConfigParser, file: str):
    """Read the config from the file.

    Args:
        file (str): The file to read the config from.
    """
    config.read(file)


def __write(config: configparser.ConfigParser, file: str):
    """Write the config to the file.

    Args:
        file (str): The file to write the config to.
    """
    with open(file, "w", encoding="utf-8") as f:
        config.write(f)


def __create(config: configparser.ConfigParser, file: str):
    """Create a new config file with the default values.

    Args:
        file (str): The file to write the config to.
    """
    config["models"] = {
        "commit": "google/gemini-2.0-flash",
        "resume": "",
    }

    config["google"] = {
        "api_key": "",
    }

    config["ollama"] = {
        "host": "http://localhost:11434",
    }

    config["mysql"] = {
        "host": "localhost",
        "port": 3306,
        "user": "root",
        "password": "",
        "database": "gitmit",
    }

    __write(config, file)
