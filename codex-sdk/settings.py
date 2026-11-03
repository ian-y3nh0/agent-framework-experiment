"""載入實驗設定。環境變數具有最高優先權。"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import urlsplit

from dotenv import dotenv_values


class ConfigurationError(ValueError):
    """設定缺漏或格式錯誤。"""


@dataclass(frozen=True)
class Settings:
    endpoint: str
    api_key: str = field(repr=False)
    model: str
    timeout: float = 120.0

    @classmethod
    def load(cls, project_dir: Path | None = None, *, codex: bool = False) -> "Settings":
        project_dir = project_dir or Path(__file__).resolve().parent
        values = {
            **dotenv_values(project_dir.parent / ".env"),
            **dotenv_values(project_dir / ".env"),
            **os.environ,
        }
        model = (values.get("CODEX_MODEL") if codex else None) or values.get("LITELLM_MODEL")
        required = {
            "LITELLM_ENDPOINT": values.get("LITELLM_ENDPOINT"),
            "LITELLM_API_KEY": values.get("LITELLM_API_KEY"),
            "LITELLM_MODEL（Codex 可用 CODEX_MODEL）": model,
        }
        missing = [name for name, value in required.items() if not value or not value.strip()]
        if missing:
            raise ConfigurationError("請在 .env 設定：" + "、".join(missing))
        endpoint = values["LITELLM_ENDPOINT"].strip().rstrip("/")
        try:
            parsed = urlsplit(endpoint)
            valid = parsed.scheme in {"http", "https"} and parsed.hostname and parsed.port != 0
        except ValueError:
            valid = False
        if not valid or parsed.username or parsed.password or parsed.query or parsed.fragment:
            raise ConfigurationError("LITELLM_ENDPOINT 必須是 HTTP 或 HTTPS 基底網址。")
        if values.get("AGENT_IN_DOCKER") == "1" and parsed.hostname in {
            "localhost",
            "127.0.0.1",
            "::1",
        }:
            host = "host.docker.internal"
            if parsed.port is not None:
                host += f":{parsed.port}"
            endpoint = parsed._replace(netloc=host).geturl()
        try:
            timeout = float(values.get("AGENT_TIMEOUT_SECONDS", "120"))
        except (TypeError, ValueError):
            raise ConfigurationError("AGENT_TIMEOUT_SECONDS 必須是 1 至 600 的數值。") from None
        if not 1 <= timeout <= 600:
            raise ConfigurationError("AGENT_TIMEOUT_SECONDS 必須是 1 至 600 的數值。")
        return cls(endpoint, values["LITELLM_API_KEY"].strip(), model.strip(), timeout)
