import asyncio

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, ToolMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from pydantic import Field


class ScriptedModel(BaseChatModel):
    replies: list[AIMessage]
    observed: list = Field(default_factory=list)

    @property
    def _llm_type(self):
        return "scripted-test"

    def bind_tools(self, tools, **kwargs):
        return self

    def _generate(self, messages, stop=None, run_manager=None, **kwargs):
        self.observed.extend(m for m in messages if isinstance(m, ToolMessage))
        return ChatResult(generations=[ChatGeneration(message=self.replies.pop(0))])


def test_deep_agent_uses_reference_and_virtual_file(monkeypatch):
    model = ScriptedModel(
        replies=[
            AIMessage(
                content="",
                tool_calls=[
                    {
                        "name": "write_todos",
                        "args": {
                            "todos": [{"content": "查詢摘要並寫入報告", "status": "in_progress"}]
                        },
                        "id": "plan1",
                        "type": "tool_call",
                    }
                ],
            ),
            AIMessage(
                content="",
                tool_calls=[
                    {
                        "name": "lookup_reference",
                        "args": {"topic": "langgraph"},
                        "id": "r1",
                        "type": "tool_call",
                    }
                ],
            ),
            AIMessage(
                content="",
                tool_calls=[
                    {
                        "name": "write_file",
                        "args": {
                            "file_path": "/report.md",
                            "content": "研究結論：LangGraph 使用節點與邊。",
                        },
                        "id": "w1",
                        "type": "tool_call",
                    }
                ],
            ),
            AIMessage(content="報告已完成。"),
        ]
    )
    import agent

    monkeypatch.setenv("LITELLM_MODEL", "offline-test")
    monkeypatch.setenv("LITELLM_ENDPOINT", "http://localhost:9/v1")
    monkeypatch.setenv("LITELLM_API_KEY", "unused")
    monkeypatch.setattr(agent, "create_model", lambda settings: model)
    result = asyncio.run(agent.run_agent("研究 LangGraph"))
    assert result["todos"] == [{"content": "查詢摘要並寫入報告", "status": "in_progress"}]
    assert result["output"] == "報告已完成。"
    assert result["files"]["/report.md"] == "研究結論：LangGraph 使用節點與邊。"
    assert any("節點與邊" in str(m.content) for m in model.observed)
