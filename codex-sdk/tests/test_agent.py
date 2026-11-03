import asyncio
import tomllib

from openai_codex import ApprovalMode, AsyncCodex, Sandbox

from agent import WORKSPACE, runtime_config
from settings import Settings


def test_runtime_receives_valid_toml_without_secret_in_arguments():
    config = runtime_config(Settings("http://localhost:4000/v1", "private-key", "example"))
    combined = "\n".join(config.config_overrides)
    parsed = tomllib.loads(combined)
    provider = parsed["model_providers"]["litellm"]
    assert provider["base_url"] == "http://localhost:4000/v1"
    assert provider["wire_api"] == "responses"
    assert config.env[provider["env_key"]] == "private-key"
    assert "private-key" not in combined


def test_bundled_runtime_can_start_offline_thread():
    async def start():
        config = runtime_config(Settings("http://127.0.0.1:9/v1", "unused", "offline-test"))
        async with AsyncCodex(config) as codex:
            thread = await codex.thread_start(
                model="offline-test",
                model_provider="litellm",
                cwd=str(WORKSPACE),
                sandbox=Sandbox.read_only,
                approval_mode=ApprovalMode.deny_all,
                ephemeral=True,
            )
            assert thread.id

    asyncio.run(asyncio.wait_for(start(), timeout=30))
