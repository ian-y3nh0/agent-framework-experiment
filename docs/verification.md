# 驗證紀錄

驗證日期：2026-11-03。

## 環境

- 本機 Python：3.13.15，由 uv 管理。
- uv：0.12.17。
- Docker Engine：29.8.1。
- Docker Compose：5.5.1。
- LangGraph：1.2.19。
- Deep Agents：0.7.32。
- Codex Python SDK 與隨附 runtime：0.163.0。

## 離線驗證

| 專案 | pytest | Notebook |
|---|---|---|
| langgraph-agent | 12 個測試通過 | 16 個區塊執行通過 |
| langgraph-deep-agent | 11 個測試通過 | 16 個區塊執行通過 |
| codex-sdk | 12 個測試通過 | 16 個區塊執行通過 |

三個專案的 Ruff 檢查均通過。
測試涵蓋設定優先順序、空白提示詞、錯誤資訊保護、逾時回應與容器端點轉換。
LangGraph 測試執行實際圖形與計算工具。
Deep Agents 測試執行實際規劃、摘要查詢與虛擬檔案工具。
Codex 測試啟動隨套件提供的 runtime，並建立離線 thread。

`tutorial.ipynb` 使用各專案的 Python 3.13 核心。未保存模型輸出或金鑰。
Jupyter 核心在驗證時顯示本機 TCP 傳輸提示。此提示不影響區塊執行。

## Docker 驗證

- 三個映像均建置成功。
- 一般 Compose 與各專案的主機網路設定均通過設定解析。
- 三個容器均以非 root 使用者執行。
- 三個 `/health` 均回傳 HTTP 200。
- 三個 `/invoke` 的預設教學任務均回傳 HTTP 200，並通過結果檢查。

目前使用 Linux 主機網路設定。原因是既有 LiteLLM 只監聽 `127.0.0.1`。
一般容器網路的主機閘道無法連入此端點。主機網路模式已驗證可用。
服務只監聽本機位址，並保持啟動。

| 專案 | 模型別名 | 真實任務結果 |
|---|---|---|
| langgraph-agent | gpt-4.1-mini | 依序得到 20、60、12 |
| langgraph-deep-agent | gpt-4.1-mini | 完成四個待辦事項，並產生 `/report.md` |
| codex-sdk | gpt-5.4-mini | 分析內嵌程式碼，指出 `ZeroDivisionError` |

## 已知限制

Codex 容器內的檔案讀取工具未通過本次測試。
代理回報主機沙箱阻擋檔案存取。此時 HTTP 仍可能回傳 200，因為代理已完成回答。
因此，HTTP 200 不代表代理要求的檔案操作成功。

預設教學使用內嵌程式碼。此路徑已通過真實推論。
本專案維持 `Sandbox.read_only` 與 `ApprovalMode.deny_all`。
需測試檔案或 shell 工具時，執行環境必須支援 Codex 的 Linux 沙箱。
官方文件說明容器的 namespace、bubblewrap 或 seccomp 限制可能阻擋沙箱。
參閱 [Codex 官方沙箱文件](https://learn.chatgpt.com/docs/agent-approvals-security)。

## 本機設定變更

- 為既有 `LITELLM_ENDPOINT` 補上 `http://`。
- 保留原有 API 金鑰。
- 新增 `LITELLM_MODEL=gpt-4.1-mini`。
- 新增 `CODEX_MODEL=gpt-5.4-mini`。
- `.env` 已列入 `.gitignore`，也不會進入 Docker 建置內容。

## 重現驗證

離線測試與 Notebook 指令見根目錄 README。
重新驗證三個服務的真實推論：

```bash
docker compose -f compose.yaml -f compose.host.yaml up --build -d --wait
uv run --directory langgraph-agent python ../scripts/check_services.py
```

此命令會使用模型額度。模型輸出可能不同。


## 原生 I/O 教學初版驗證

三份 `tutorial_native.ipynb` 已使用真實 LiteLLM 連線執行全部區塊。
LangGraph 有 20 個區塊。Deep Agents 與 Codex 各有 16 個區塊。
Ruff 檢查均通過。

- LangGraph：已觀察 `AIMessage`、工具參數 schema、`ToolMessage`、完整狀態與 `updates` 串流。計算工具回傳 42。
- Deep Agents：已觀察 `messages`、完成的 `todos`、包含時間與 encoding 的原生檔案資料，以及狀態更新串流。
- Codex：已觀察字串輸入、`TextInput`、完成的 `TurnResult`、原生項目、用量與 `Notification`。串流結束狀態是 `completed`。

原生版直接使用官方 module。它們沒有匯入專案的 agent、main、settings 或 model 模組。
LangGraph 只宣告工具函式與模型節點 callback。其他兩份沒有自訂函式。
原生版已保存真實輸出，並檢查輸出不含 LiteLLM API 金鑰。
重新執行推論區塊會使用模型額度。


## 原生教學圖解與 Git 初始化

三份原生教學各新增三個圖形區塊：類別關係圖、控制流程圖與循序圖。
圖形使用 `IPython.display.HTML` 與內嵌 SVG。它們不載入外部 JavaScript，也不呼叫模型。

九個圖形區塊均已單獨執行。HTML 輸出與 SVG XML 結構均通過檢查。
圖形已轉成預覽圖，檢查節點、箭頭、文字與排版。
既有原生推論輸出與使用者加入的區塊均保留。

首次 Git 提交前，三個專案的 35 個 pytest 測試與 Ruff 檢查均通過。
Git 作者資訊參考 `~/codex-virtuoso` 的本機設定。
`.env`、`.venv`、`.codex`、`.vscode` 與快取目錄均排除於版本控制之外。
