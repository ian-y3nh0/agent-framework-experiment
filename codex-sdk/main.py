"""提供命令列入口與 HTTP 測試服務。"""

import argparse
import asyncio
import json
import logging

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict, Field

from agent import FRAMEWORK, run_agent
from settings import ConfigurationError

app = FastAPI(title=f"{FRAMEWORK} 實驗", description="每次請求執行一個獨立任務。")
logger = logging.getLogger(__name__)


class InvokeRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    prompt: str = Field(min_length=1, max_length=16000, description="代理要執行的任務。")


@app.get("/health", summary="檢查服務程序")
async def health() -> dict:
    return {"status": "ok", "framework": FRAMEWORK}


@app.post("/invoke", summary="執行代理任務")
async def invoke(request: InvokeRequest) -> dict:
    try:
        return await run_agent(request.prompt)
    except ConfigurationError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from None
    except TimeoutError:
        raise HTTPException(
            status_code=504, detail="代理執行逾時。請縮短任務或調整時間限制。"
        ) from None
    except Exception as exc:  # noqa: BLE001 -- 邊界統一處理，避免洩漏上游敏感資料。
        logger.warning("代理執行失敗：%s", type(exc).__name__)
        raise HTTPException(
            status_code=502,
            detail="代理執行失敗。請檢查模型名稱、端點、金鑰與 API 相容性。",
        ) from None


def cli() -> None:
    parser = argparse.ArgumentParser(description="執行代理，或啟動 HTTP 服務。")
    parser.add_argument("prompt", nargs="?", help="代理任務。")
    parser.add_argument("--serve", action="store_true", help="啟動 HTTP 服務。")
    parser.add_argument("--host", default="127.0.0.1", help="服務綁定位址。")
    parser.add_argument("--port", type=int, default=8000, help="服務連接埠。")
    args = parser.parse_args()
    if args.serve:
        import uvicorn

        uvicorn.run(app, host=args.host, port=args.port)
        return
    if not args.prompt or not args.prompt.strip():
        parser.error("請提供任務，或使用 --serve。")
    try:
        result = asyncio.run(run_agent(args.prompt))
    except ConfigurationError as exc:
        parser.exit(2, f"設定錯誤：{exc}\n")
    except TimeoutError:
        parser.exit(1, "代理執行逾時。\n")
    except Exception as exc:  # noqa: BLE001 -- 邊界統一處理，避免洩漏上游敏感資料。
        parser.exit(1, f"代理執行失敗（{type(exc).__name__}）。請檢查端點與模型設定。\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    cli()
