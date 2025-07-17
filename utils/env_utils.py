from dotenv import load_dotenv, dotenv_values
from typing import Optional, Dict
import os

MUST_HAVE_ENV_VARS = [
    "ELEVENLABS_API_KEY",
    "GEMINI_API_KEY",
]


def assert_env_variable(var_name: str) -> None:
    variable = get_environment_variable(var_name)
    if variable is None:
        raise ValueError(f"Environment variable '{var_name}' is not set.")

    assert variable, f"Environment variable '{var_name}' cannot be empty."


def load_environment_variables() -> Optional[Dict[str, str | None]]:
    """
    Load and validate all required environment variables.
    Returns env dict if successful, None if failed.
    """
    try:
        is_env_loaded = load_dotenv()
        if not is_env_loaded:
            raise Exception("Failed to load .env file")

        env = dotenv_values()

        for var in MUST_HAVE_ENV_VARS:
            assert_env_variable(var)
        print("Environment variables loaded and validated")
        return env
    except FileNotFoundError:
        print(".env file not found. Please create one with your API keys.")
        return None
    except AssertionError as e:
        print(f"Environment validation failed: {e}")
        return None
    except Exception as e:
        print(f"Failed to load environment variables: {e}")
        return None


def get_environment_variable(var_name: str) -> Optional[str]:
    """
    Retrieve a specific environment variable.
    """
    value = os.getenv(var_name)
    if value:
        return value

    env = dotenv_values()
    return env.get(var_name, None)


def is_development() -> bool:
    """Check if we're running in development mode."""
    return get_environment_variable("ENVIRONMENT") == "development"
