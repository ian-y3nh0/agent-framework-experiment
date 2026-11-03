import asyncio

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from pydantic import Field

from agent import build_agent


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


def test_graph_executes_tool_and_returns_result():
    model = ScriptedModel(
        replies=[
            AIMessage(
                content="",
                tool_calls=[
                    {"name": "multiply", "args": {"a": 6, "b": 7}, "id": "m1", "type": "tool_call"}
                ],
            ),
            AIMessage(content="答案是 42。"),
        ]
    )
    state = asyncio.run(build_agent(model).ainvoke({"messages": [HumanMessage(content="6 乘 7")]}))
    assert state["messages"][-1].text == "答案是 42。"
    assert any(m.content == "42.0" for m in model.observed)


def test_division_by_zero_returns_tool_feedback():
    model = ScriptedModel(
        replies=[
            AIMessage(
                content="",
                tool_calls=[
                    {"name": "divide", "args": {"a": 1, "b": 0}, "id": "d1", "type": "tool_call"}
                ],
            ),
            AIMessage(content="除數不可為零。"),
        ]
    )
    state = asyncio.run(
        build_agent(model).ainvoke({"messages": [HumanMessage(content="1 除以 0")]})
    )
    assert "除數不可為零" in state["messages"][-2].content
