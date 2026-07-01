import os
import time
import tomllib
from pathlib import Path

import requests
from requests.adapters import HTTPAdapter


API_FOOTBALL_BASE = "https://v3.football.api-sports.io"
DEFAULT_TIMEOUT = 12
RETRY_BACKOFF_SECONDS = (1, 2, 4)

_SESSION = None


class ApiFootballError(RuntimeError):
    pass


class ApiFootballTemporaryError(ApiFootballError):
    pass


def load_api_key():
    env_key = os.getenv("API_FOOTBALL_KEY")
    if env_key:
        return env_key.strip()

    secrets_path = Path(__file__).resolve().parents[1] / ".streamlit" / "secrets.toml"
    if secrets_path.exists():
        with secrets_path.open("rb") as file:
            secrets = tomllib.load(file)
        for key in ["API_FOOTBALL_KEY", "api_football_key"]:
            if secrets.get(key):
                return str(secrets[key]).strip()

    return None


def session():
    global _SESSION
    if _SESSION is None:
        _SESSION = requests.Session()
        adapter = HTTPAdapter(pool_connections=8, pool_maxsize=16)
        _SESSION.mount("https://", adapter)
        _SESSION.mount("http://", adapter)
    return _SESSION


def should_retry(error):
    return isinstance(error, (
        requests.exceptions.SSLError,
        requests.exceptions.Timeout,
        requests.exceptions.ConnectionError,
    ))


def api_errors_text(errors):
    if isinstance(errors, dict) and errors:
        return "; ".join(str(value) for value in errors.values())
    if isinstance(errors, list) and errors:
        return "; ".join(str(value) for value in errors)
    return None


def request(path, params=None, timeout=DEFAULT_TIMEOUT):
    api_key = load_api_key()
    if not api_key:
        raise ApiFootballError(
            "缺少 API-Football Key。请在 .streamlit/secrets.toml 中保存 API_FOOTBALL_KEY。"
        )

    last_error = None
    for attempt, delay in enumerate((0, *RETRY_BACKOFF_SECONDS), start=1):
        if delay:
            time.sleep(delay)
        try:
            response = session().get(
                f"{API_FOOTBALL_BASE}{path}",
                params=params or {},
                timeout=timeout,
                headers={
                    "x-apisports-key": api_key,
                    "Accept": "application/json",
                },
            )
            response.raise_for_status()
            data = response.json()
            error_text = api_errors_text(data.get("errors"))
            if error_text:
                raise ApiFootballError(error_text)
            return data.get("response", [])
        except ApiFootballError:
            raise
        except ValueError as error:
            last_error = error
            if attempt >= len(RETRY_BACKOFF_SECONDS) + 1:
                break
        except requests.exceptions.RequestException as error:
            last_error = error
            if attempt >= len(RETRY_BACKOFF_SECONDS) + 1 or not should_retry(error):
                break

    raise ApiFootballTemporaryError("API temporarily unavailable")


def request_json(path, params=None, timeout=DEFAULT_TIMEOUT):
    return request(path, params=params, timeout=timeout)
