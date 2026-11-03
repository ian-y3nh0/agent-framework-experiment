"""改編自 Deep Agents 官方研究助理範例。"""

import asyncio

from deepagents import create_deep_agent
from langchain.agents.middleware import TodoListMiddleware
from langchain_core.messages import HumanMessage, ToolMessage
from langchain_core.tools import tool

from model import create_model
from settings import Settings

FRAMEWORK = "langgraph-deep-agent"
REFERENCES = {
    "langgraph": "LangGraph 以節點與邊控制工作流程。狀態會傳遞至下一個節點。",
    "deepagents": "Deep Agents 建立在 LangGraph 上。它提供規劃、虛擬檔案與子代理工具。",
    "codex": "Codex Python SDK 透過本機 app-server 執行程式碼相關任務。",
}


@tool
def lookup_reference(topic: str) -> str:
    """讀取本地教學摘要。topic 可為 langgraph、deepagents 或 codex。"""
    return REFERENCES.get(
        topic.strip().lower(), "找不到資料。請使用 langgraph、deepagents 或 codex。"
    )


def build_agent(model):
    return create_deep_agent(
        model=model,
        tools=[lookup_reference],
        middleware=[TodoListMiddleware()],
        system_prompt=(
            "你是技術研究助理。以繁體中文回答。使用短句。"
            "研究任務先使用 write_todos 規劃，再用 lookup_reference 讀取摘要。"
            "使用 write_file 將結論寫入 /report.md。最後回覆結論。"
            "摘要是本地教學資料，並非即時網路搜尋結果。"
        ),
    )


async def run_agent(prompt: str) -> dict:
    settings = Settings.load()
    agent = build_agent(create_model(settings))
    async with asyncio.timeout(settings.timeout):
        state = await agent.ainvoke(
            {"messages": [HumanMessage(content=prompt)]}, {"recursion_limit": 60}
        )
    return {
        "framework": FRAMEWORK,
        "output": state["messages"][-1].text,
        "todos": state.get("todos", []),
        "files": {path: data["content"] for path, data in state.get("files", {}).items()},
        "tool_results": [m.content for m in state["messages"] if isinstance(m, ToolMessage)],
    }
