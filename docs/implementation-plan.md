# Agent framework 實作計畫

## 目標

建立三個獨立實驗。每個實驗使用 uv 與 Python 3.13。每個實驗包含 Notebook、命令列入口與 Docker Compose HTTP 服務。

## 實作選擇

- 每個資料夾使用獨立的 pyproject.toml 與 uv.lock。這可避免不同框架的依賴互相影響。
- LangGraph 使用 Graph API。範例包含加法、乘法與除法工具。
- Deep Agents 使用 create_deep_agent。範例使用本地參考資料工具，避免要求額外的搜尋服務金鑰。
- Codex 使用官方 openai-codex Python SDK。自訂供應者連線至 LiteLLM Responses API。
- 三個 HTTP 服務提供 GET /health 與 POST /invoke。每次請求建立獨立執行狀態。
- 環境變數優先於專案 .env。專案 .env 優先於根目錄 .env。
- 模型別名由 LITELLM_MODEL 設定。Codex 可用 CODEX_MODEL 覆寫。
- 說明使用繁體中文。採用 ASD-STE100 的短句、主動語態與單一步驟原則。ASD-STE100 本身是受控英文規範，因此不宣稱中文文件通過該標準認證。

## 執行順序

1. 寫入設定與 HTTP 行為測試。確認尚未實作時會失敗。
2. 建立設定載入、模型介面及各框架範例。
3. 產生 uv.lock。執行測試。
4. 建立教學 Notebook、README 與 Docker 設定。
5. 建置三個映像。以 Compose 啟動服務。驗證健康檢查及請求處理。
6. 在模型名稱與服務可用時，執行真實推論。

## 驗證重點

- 缺少設定時，應提供明確訊息。
- 環境變數與 .env 的優先順序應一致。
- 空白提示詞應回傳 422。
- 服務不得把上游例外內的金鑰送回呼叫端。
- LangGraph 應完成工具呼叫迴圈。
- Deep Agents 應能讀取參考資料及寫入虛擬檔案。
- Codex 應能啟動隨套件提供的 runtime。
- Notebook 的離線步驟應可重複執行。

## 進度

- 已核對官方 quickstart 與 SDK 文件。
- 初始工作目錄不是 Git repository。依使用者後續要求，已初始化為 main 分支。

- 已建立三個獨立專案與鎖定依賴。
- 已完成 35 個離線測試與三份 Notebook 的執行驗證。
- 已修正 Deep Agents 0.7.32 的字串檔案格式。
- 已明確加入 TodoListMiddleware，確保規劃工具可用。
- 已補上現有端點的 HTTP 協定。保留原有 API 金鑰。
- 預設模型由實作者選定：LangGraph 使用 gpt-4.1-mini，Codex 使用 gpt-5.4-mini。使用者可在 .env 更換。
- 現有 LiteLLM 只監聽 localhost。已新增 Linux 主機網路模式。
- 已完成獨立程式碼審查。文件連結問題已在交付時補齊。
- Codex 容器可分析內嵌程式碼。主機沙箱阻擋的檔案工具列為環境限制。
