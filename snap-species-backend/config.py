import os

_config_dir = os.path.dirname(os.path.abspath(__file__))
_env_path = os.path.join(_config_dir, ".env")

try:
    from dotenv import load_dotenv
    load_dotenv(_env_path, override=True)
except ImportError:
    pass


def _read_key_from_file(filepath: str, key_prefix: str) -> str | None:
    if not filepath or not os.path.isfile(filepath):
        return None
    try:
        with open(filepath, "r", encoding="utf-8-sig") as f:  # utf-8-sig strips BOM
            for line in f:
                line = line.strip().strip("\r")
                if not line or line.startswith("#"):
                    continue
                if "=" not in line:
                    continue
                key, _, value = line.partition("=")
                if key.strip() == key_prefix and value:
                    return value.strip().strip('"').strip("'")
    except Exception:
        pass
    return None


def _read_from_env_file(key_prefix: str) -> str | None:
    out = _read_key_from_file(_env_path, key_prefix)
    if out is not None:
        return out
    cwd = os.getcwd()
    for extra in (os.path.join(cwd, ".env"), os.path.join(cwd, "snap-species-backend", ".env")):
        if extra != _env_path:
            out = _read_key_from_file(extra, key_prefix)
            if out is not None:
                return out
    return None


def _read_db_url_from_file() -> str | None:
    return _read_from_env_file("DB_URL")


def get_env(key: str, default: str = "") -> str:
    return os.environ.get(key, default).strip()


_DEFAULT_DB_URL = "postgresql://postgres:postgres@localhost:5432/snapspecies"


class Settings:
    def __init__(self) -> None:
        self.iucn_api_key = get_env("IUCN_API_KEY")
        self.animal_detect_api_key = get_env("ANIMAL_DETECT_API_KEY")
        _openai = get_env("OPENAI_API_KEY") or get_env("OPENAI_KEY")
        if not _openai:
            _openai = _read_from_env_file("OPENAI_API_KEY") or _read_from_env_file("OPENAI_KEY") or ""
        self.openai_api_key = _openai
        self.jwt_secret = get_env("JWT_SECRET", "change-me-in-production")
        self.jwt_algorithm = "HS256"
        self.jwt_expire_minutes = 60 * 24 * 7
        db_url = get_env("DB_URL", _DEFAULT_DB_URL)
        if db_url == _DEFAULT_DB_URL or not db_url:
            from_file = _read_db_url_from_file()
            if from_file:
                db_url = from_file
        self.db_url = db_url or _DEFAULT_DB_URL
        self.force_push_schema = get_env("FORCE_PUSH_SCHEMA", "false").lower() in ("1", "true", "yes")


def get_settings() -> Settings:
    return Settings()


def get_openai_key() -> str:
    """Return OPENAI_KEY from env or .env file (multiple paths). Use this for OpenAI API calls."""
    v = (os.environ.get("OPENAI_API_KEY") or os.environ.get("OPENAI_KEY") or "").strip()
    if v:
        return v
    v = _read_from_env_file("OPENAI_API_KEY") or _read_from_env_file("OPENAI_KEY")
    return (v or "").strip()
