"""使用官方 Codex Python SDK 與 LiteLLM Responses API。"""

import asyncio
import json
import os
from pathlib import Path

from openai_codex import ApprovalMode, AsyncCodex, CodexConfig, Sandbox

from settings import Settings

FRAMEWORK = "codex-sdk"
WORKSPACE = Path(__file__).resolve().parent / "workspace"


def runtime_config(settings: Settings) -> CodexConfig:
    # JSON 字串也是合法的 TOML 基本字串。金鑰只透過環境變數傳入。
    return CodexConfig(
        cwd=str(WORKSPACE),
        env={**os.environ, "LITELLM_API_KEY": settings.api_key},
        config_overrides=(
            'model_provider="litellm"',
            'model_providers.litellm.name="LiteLLM"',
            f"model_providers.litellm.base_url={json.dumps(settings.endpoint)}",
            'model_providers.litellm.env_key="LITELLM_API_KEY"',
            'model_providers.litellm.wire_api="responses"',
            "model_providers.litellm.requires_openai_auth=false",
            "model_providers.litellm.request_max_retries=0",
            "model_providers.litellm.stream_max_retries=0",
            'web_search="disabled"',
        ),
    )


async def run_agent(prompt: str) -> dict:
    settings = Settings.load(codex=True)
    async with asyncio.timeout(settings.timeout):
        async with AsyncCodex(runtime_config(settings)) as codex:
            thread = await codex.thread_start(
                model=settings.model,
                model_provider="litellm",
                cwd=str(WORKSPACE),
                sandbox=Sandbox.read_only,
                approval_mode=ApprovalMode.deny_all,
                ephemeral=True,
                developer_instructions="以繁體中文回答。使用短句。分析程式碼並提出修正建議。",
            )
            result = await thread.run(prompt)
    return {"framework": FRAMEWORK, "output": result.final_response}
