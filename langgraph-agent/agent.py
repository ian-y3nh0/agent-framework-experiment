"""改編自 LangGraph 官方 Graph API 計算器範例。"""

import asyncio

from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool
from langgraph.graph import END, START, MessagesState, StateGraph

from model import create_model
from settings import Settings

FRAMEWORK = "langgraph-agent"


@tool
def add(a: float, b: float) -> float:
    """計算 a 加 b。"""
    return a + b


@tool
def multiply(a: float, b: float) -> float:
    """計算 a 乘 b。"""
    return a * b


@tool
def divide(a: float, b: float) -> float:
    """計算 a 除以 b。b 不可為零。"""
    if b == 0:
        raise ValueError("除數不可為零。")
    return a / b


TOOLS = [add, multiply, divide]


def build_agent(model):
    model_with_tools = model.bind_tools(TOOLS)
    tools_by_name = {item.name: item for item in TOOLS}

    async def call_model(state: MessagesState):
        response = await model_with_tools.ainvoke(
            [
                SystemMessage(content="你是計算助理。計算時使用工具。以繁體中文回答。使用短句。"),
                *state["messages"],
            ]
        )
        return {"messages": [response]}

    async def call_tools(state: MessagesState):
        results = []
        for call in state["messages"][-1].tool_calls:
            try:
                observation = await tools_by_name[call["name"]].ainvoke(call["args"])
            except (ValueError, KeyError) as exc:
                observation = f"工具輸入錯誤：{exc}"
            results.append(ToolMessage(content=str(observation), tool_call_id=call["id"]))
        return {"messages": results}

    def next_step(state: MessagesState):
        return "tools" if state["messages"][-1].tool_calls else END

    graph = StateGraph(MessagesState)
    graph.add_node("model", call_model)
    graph.add_node("tools", call_tools)
    graph.add_edge(START, "model")
    graph.add_conditional_edges("model", next_step, ["tools", END])
    graph.add_edge("tools", "model")
    return graph.compile()


async def run_agent(prompt: str) -> dict:
    settings = Settings.load()
    agent = build_agent(create_model(settings))
    async with asyncio.timeout(settings.timeout):
        state = await agent.ainvoke(
            {"messages": [HumanMessage(content=prompt)]}, {"recursion_limit": 30}
        )
    return {
        "framework": FRAMEWORK,
        "output": state["messages"][-1].text,
        "tool_results": [m.content for m in state["messages"] if isinstance(m, ToolMessage)],
    }
