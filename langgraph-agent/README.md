# LangGraph 計算代理

以 Graph API 建立工具迴圈。模型節點決定是否呼叫工具。工具節點回傳結果。條件邊決定下一個節點。

## 必要條件

- uv。
- Python 3.13。uv 可安裝此版本。
- Docker Engine 與 Docker Compose 2.24.4 以上版本。
- 可用的 LiteLLM 端點、金鑰與模型別名。
- 模型必須支援工具呼叫。

## 設定

1. 切換至本資料夾。
2. 在根目錄 `.env` 設定連線。也可建立本資料夾的 `.env`。
3. 依 `.env.example` 填入 `LITELLM_ENDPOINT`、`LITELLM_API_KEY` 與 `LITELLM_MODEL`。

請保留已有的 `.env`。不要用範例檔覆蓋有效金鑰。
網址必須是 API 基底網址，例如 `http://localhost:4000/v1`。
程式會保留自訂網址路徑，不會自動補上 `/v1`。

本機設定優先順序：環境變數、本資料夾 `.env`、根目錄 `.env`。
Compose 依序載入根目錄與本資料夾的 `.env`。後者覆寫前者。
Shell 環境變數不會自動覆寫 Compose 的 `env_file`。

## 執行命令列範例

```bash
uv sync --locked
uv run main.py '請使用工具計算 (12 + 8) × 3，再除以 5。'
```

預期結果是 JSON。`output` 欄位包含回答。

## 原生 API 教學

開啟 [tutorial_native.ipynb](tutorial_native.ipynb)，可查看直接使用官方 module 的範例。
此教學展示原生輸入、回傳型別、完整欄位與串流事件。
教學另含 HTML／SVG 類別關係圖、控制流程圖與循序圖。
執行標示為圖形的區塊即可顯示。圖形不需外部 JavaScript，也不會呼叫 LLM。
所有呼叫都寫在 Notebook 中，不使用專案的 `run_agent`、`build_agent` 或設定封裝。
LangGraph 範例只保留框架需要的節點與工具函式。

```bash
uv sync --locked --group notebook
uv run --group notebook jupyter lab tutorial_native.ipynb
```

原生版的推論區塊會直接呼叫模型，並使用模型額度。
依序執行全部區塊。讀取已保存的輸出不會呼叫模型。

## 開啟教學

```bash
uv sync --locked --group notebook
uv run --group notebook jupyter lab tutorial.ipynb
```

Notebook 預設執行離線步驟。將 `RUN_LIVE` 改為 `True`，再執行模型步驟。
Notebook 使用頂層 `await`，不需呼叫 `asyncio.run()`。

## 啟動 Docker 服務

```bash
docker compose up --build -d --wait
curl --fail http://localhost:8001/health
curl --fail-with-body http://localhost:8001/invoke \
  -H 'Content-Type: application/json' \
  -d '{"prompt":"請使用工具計算 (12 + 8) × 3，再除以 5。"}'
```

開啟 `http://localhost:8001/docs`，可使用 API 測試頁面。
`/health` 只檢查服務程序。`/invoke` 才會測試 LLM 連線。

Compose 會設定 `AGENT_IN_DOCKER=1`。程式會將本機端點的 `localhost`、`127.0.0.1` 或 `::1` 轉為 `host.docker.internal`。
連接埠與路徑保持不變。遠端網址保持不變。LiteLLM 必須接受來自 Docker 主機閘道的連線。

停止服務：

```bash
docker compose down
```

## 連線至只監聽 localhost 的 LiteLLM

Linux 主機可使用主機網路設定。這適用於 LiteLLM 只監聽 `127.0.0.1` 的情況。
此模式直接使用 `.env` 的端點，不轉換主機名稱。
API 仍只監聽 `127.0.0.1`。

```bash
docker compose -f compose.yaml -f docker/compose.host.yaml up --build -d --wait
```

停止此模式的服務：

```bash
docker compose -f compose.yaml -f docker/compose.host.yaml down
```

## 啟動本機 HTTP 服務

```bash
uv run main.py --serve --port 8001
```

## 測試

```bash
uv sync --locked --group notebook
uv run pytest -q
uv run ruff check .
```

測試使用離線資料。它們不會呼叫付費模型。
`AGENT_TIMEOUT_SECONDS` 限制一次任務的時間。預設是 120 秒。

| HTTP 狀態 | 原因 | 處理方式 |
|---|---|---|
| 422 | 提示詞是空白或格式錯誤 | 提供非空白的 `prompt` |
| 503 | 設定缺漏 | 補齊 `.env` |
| 502 | 上游或代理執行失敗 | 檢查端點、模型別名與 API 相容性 |
| 504 | 執行逾時 | 縮短任務，或增加時間限制 |

## 檔案用途

| 檔案 | 用途 |
|---|---|
| `tutorial.ipynb` | 分步教學 |
| `main.py` | 命令列與 HTTP 入口 |
| `agent.py` | 框架範例 |
| `settings.py` | 設定載入與驗證 |
| `pyproject.toml`、`uv.lock` | Python 依賴與鎖定版本 |
| `compose.yaml` | 容器服務設定 |
| `docker/Dockerfile` | 映像建置步驟 |
| `tests/` | 離線行為測試 |

## 官方依據

官方範例使用 Anthropic。本實驗改用 ChatOpenAI，透過 LiteLLM 呼叫標準 Chat Completions API。保留計算工具與明確的節點流程。

- [LangGraph 官方 Quickstart](https://docs.langchain.com/oss/python/langgraph/quickstart)
- [ChatOpenAI 官方整合文件](https://docs.langchain.com/oss/python/integrations/chat/openai)
- [uv 官方 Docker 指引](https://docs.astral.sh/uv/guides/integration/docker/)

文件核對日期：2026-11-03。實際安裝版本以 `uv.lock` 為準。

## 文字規則

說明以繁體中文撰寫。每句表達一個重點。每個步驟只要求一個動作。
ASD-STE100 是受控英文規範。本文件採用其寫作原則，不宣稱中文內容符合英文詞彙規範。
