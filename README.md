# Agent Framework 實驗

每個資料夾是一個獨立實驗。所有 Python 專案使用 uv 與 Python 3.13。

| 資料夾 | 學習重點 | HTTP 連接埠 |
|---|---|---|
| [langgraph-agent](langgraph-agent/README.md) | 節點、條件邊與計算工具 | 8001 |
| [langgraph-deep-agent](langgraph-deep-agent/README.md) | 規劃、本地資料工具與虛擬檔案 | 8002 |
| [codex-sdk](codex-sdk/README.md) | 官方 Python SDK 與程式碼分析 | 8003 |

每個資料夾包含 `tutorial.ipynb`、`main.py`、`README.md` 與 `docker/`。
每個專案有自己的 `pyproject.toml`、`uv.lock`、測試與 Compose 設定。

## 1. 設定連線

編輯根目錄的 `.env`。保留已有的端點與金鑰。
依 `.env.example` 補上 `LITELLM_MODEL`。
模型名稱必須是你的 LiteLLM model alias。
Codex 可另設 `CODEX_MODEL`。留白時使用 `LITELLM_MODEL`。

```dotenv
LITELLM_ENDPOINT=http://localhost:4000/v1
LITELLM_API_KEY=replace-with-your-key
LITELLM_MODEL=replace-with-your-model-alias
CODEX_MODEL=
AGENT_TIMEOUT_SECONDS=120
```

兩個 LangGraph 實驗使用標準 Chat Completions API。
Codex 使用 Responses API。請選擇支援對應 API 與工具呼叫的模型。

## 2. 執行一個實驗

```bash
cd langgraph-agent
uv sync --locked
uv run main.py '請使用工具計算 6 乘 7。'
```

## 3. 開啟 Notebook

在選定的專案資料夾執行：

```bash
uv sync --locked --group notebook
uv run --group notebook jupyter lab tutorial.ipynb
```

`tutorial.ipynb` 預設使用離線步驟。將 `RUN_LIVE` 改為 `True` 可呼叫模型。

另外提供三份原生 API 教學：

- [LangGraph 原生 I/O](langgraph-agent/tutorial_native.ipynb)：訊息、工具、圖形狀態與節點更新。
- [Deep Agents 原生 I/O](langgraph-deep-agent/tutorial_native.ipynb)：訊息、待辦事項、虛擬檔案與狀態更新。
- [Codex SDK 原生 I/O](codex-sdk/tutorial_native.ipynb)：字串、TextInput、TurnResult 與 Notification。

原生版直接匯入官方 module。完整呼叫與回傳資料都顯示在 Notebook 中。
每份原生版另含三個 HTML／SVG 圖形區塊：類別關係圖、控制流程圖與循序圖。
圖形使用內嵌 SVG，不需外部 JavaScript 或網路服務。執行圖形區塊不會呼叫模型。
在選定資料夾執行 `uv run --group notebook jupyter lab tutorial_native.ipynb`。
原生版沒有 `RUN_LIVE` 開關。執行推論區塊會直接使用模型額度。

## 4. 啟動全部 Docker 服務

回到根目錄，再執行：

```bash
docker compose up --build -d --wait
curl --fail http://localhost:8001/health
curl --fail http://localhost:8002/health
curl --fail http://localhost:8003/health
```

服務只綁定本機位址。可開啟各連接埠的 `/docs` 測試 API。
健康檢查不會呼叫模型。使用 `/invoke` 驗證真實推論。

```bash
curl --fail-with-body http://localhost:8001/invoke \
  -H 'Content-Type: application/json' \
  -d '{"prompt":"請使用工具計算 6 乘 7。"}'
```

Compose 會啟用容器設定。程式會將本機端點的 `localhost`、`127.0.0.1` 或 `::1` 轉為 `host.docker.internal`。
連接埠與路徑保持不變。遠端網址保持不變。
LiteLLM 必須接受來自 Docker 主機閘道的連線。

停止全部服務：

```bash
docker compose down
```

只啟動一個實驗時，可切換至該資料夾，再執行相同 Compose 命令。
不要同時啟動根目錄與個別專案的服務，否則連接埠會衝突。

## 5. 使用 Linux 主機網路

若 LiteLLM 只監聽 `127.0.0.1`，一般容器網路無法連入。
本次提供的本機端點屬於此情況。請使用下列命令啟動全部服務：

```bash
docker compose -f compose.yaml -f compose.host.yaml up --build -d --wait
```

此模式直接使用 `.env` 的端點。三個 API 仍只監聽 `127.0.0.1`。
此設定適用於 Linux Docker Engine。請使用 Docker Compose 2.24.4 以上版本。

停止服務：

```bash
docker compose -f compose.yaml -f compose.host.yaml down
```

## 6. 執行離線驗證

從根目錄執行：

```bash
uv run --directory langgraph-agent pytest -q
uv run --directory langgraph-deep-agent pytest -q
uv run --directory codex-sdk pytest -q
```

驗證 Notebook 的全部離線步驟：

```bash
uv run --directory langgraph-agent --group notebook python ../scripts/check_notebook.py
uv run --directory langgraph-deep-agent --group notebook python ../scripts/check_notebook.py
uv run --directory codex-sdk --group notebook python ../scripts/check_notebook.py
```

啟動三個服務後，可驗證真實推論。此命令會使用模型額度：

```bash
uv run --directory langgraph-agent python ../scripts/check_services.py
```

使用 `--directory` 可切換測試工作目錄。`--project` 不會切換工作目錄。

## 寫作規則

說明使用繁體中文、短句與主動語態。每個步驟只描述一個動作。
同一概念使用同一術語。
ASD-STE100 是受控英文規範。本專案採用其寫作原則，不宣稱中文符合英文詞彙要求。

各專案 README 列出官方教學來源與改編方式。
驗證結果請參閱 [驗證紀錄](docs/verification.md)。
