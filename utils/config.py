"""Load environment settings from configs/ and secrets from environment variables."""

import json
import os
from dataclasses import dataclass
from pathlib import Path

CONFIG_PATH = Path(__file__).resolve().parent.parent / "configs" / "config.json"
USER_ID_ENV_VAR = "SG_USER_ID"
BASE_URL_ENV_VAR = "SG_BASE_URL"
HEADLESS_ENV_VAR = "SG_HEADLESS"


@dataclass(frozen=True)
class Settings:
    base_url: str
    user_id: str
    ui_timeout_seconds: float
    api_timeout_seconds: float
    is_headless: bool


def load_settings() -> Settings:
    """Build Settings from configs/config.json, overridable by environment variables.

    The user id is a session token, so it is never stored in the repository and
    must come from the SG_USER_ID environment variable.

    Raises:
        RuntimeError: If SG_USER_ID is not set.
    """
    raw_config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    user_id = os.environ.get(USER_ID_ENV_VAR, "").strip()
    if not user_id:
        raise RuntimeError(
            f"Set the {USER_ID_ENV_VAR} environment variable to a valid x-user-id.",
        )

    headless_value = os.environ.get(HEADLESS_ENV_VAR, str(raw_config["headless"]))
    return Settings(
        base_url=os.environ.get(BASE_URL_ENV_VAR, raw_config["base_url"]).rstrip("/"),
        user_id=user_id,
        ui_timeout_seconds=float(raw_config["ui_timeout_seconds"]),
        api_timeout_seconds=float(raw_config["api_timeout_seconds"]),
        is_headless=headless_value.lower() == "true",
    )
