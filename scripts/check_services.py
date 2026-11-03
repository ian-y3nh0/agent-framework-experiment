import asyncio

import httpx


async def check(port, prompt):
    async with httpx.AsyncClient(timeout=150) as client:
        health = await client.get(f"http://127.0.0.1:{port}/health")
        print(port, "health", health.status_code, flush=True)
        response = await client.post(f"http://127.0.0.1:{port}/invoke", json={"prompt": prompt})
        print(port, "invoke", response.status_code, response.json(), flush=True)
        response.raise_for_status()
        return response.json()


async def main():
    results = await asyncio.gather(
        check(8001, "請使用工具計算 (12 + 8) 乘 3，再除以 5。"),
        check(
            8002,
            "請用 write_todos 規劃，查詢 langgraph 與 deepagents 本地摘要，將一句比較結論寫入 /report.md。",
        ),
        check(
            8003,
            "分析 def average(values): return sum(values) / len(values) 的空清單問題。請指出例外名稱，並用兩句話回答。",
        ),
        return_exceptions=True,
    )
    assert all(isinstance(item, dict) for item in results), [
        type(item).__name__ for item in results
    ]
    assert results[0]["tool_results"]
    assert "/report.md" in results[1]["files"]
    assert results[1]["todos"]
    assert "ZeroDivisionError" in results[2]["output"]
    print("三個 Compose 服務的真實推論測試通過。")


asyncio.run(main())
