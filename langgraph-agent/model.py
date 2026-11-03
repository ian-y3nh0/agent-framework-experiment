"""透過 LiteLLM 的標準 Chat Completions API 建立模型。"""

from langchain_openai import ChatOpenAI

from settings import Settings


def create_model(settings: Settings) -> ChatOpenAI:
    return ChatOpenAI(
        model=settings.model,
        base_url=settings.endpoint,
        api_key=settings.api_key,
        timeout=settings.timeout,
        max_retries=0,
        use_responses_api=False,
        stream_usage=False,
    )
