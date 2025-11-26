# MLE-STAR 使用說明

## 1. 簡介
MLE-STAR (Machine Learning Engineering Agent via Search and Targeted Refinement) 是一個自動化機器學習工程師代理人。它利用大型語言模型 (LLM) 來模擬人類專家的思考過程，自動執行從數據清理、特徵工程、模型選擇到程式碼撰寫與優化的完整機器學習流程。
本文件旨在協助技術人員進行 MLE-STAR 的部署、配置與維護。

## 2. 環境變數詳解 (Environment Variables)
請在專案根目錄建立 `.env` 檔案，或於系統環境變數中設定以下數值：

| 變數名稱 | 預設值 | 必填 | 說明 |
| :--- | :--- | :--- | :--- |
| `ROOT_AGENT_MODEL` | `gemini-1.5-pro` | 是 | 指定 Agent 使用的 LLM 模型名稱。 |
| `GOOGLE_CLOUD_PROJECT` | - | 是 | Google Cloud Project ID。 |
| `GOOGLE_CLOUD_LOCATION` | - | 是 | Google Cloud 資源所在的區域 (Region)，例如 `us-central1`。 |
| `GOOGLE_CLOUD_STORAGE_BUCKET` | - | 是 | 用於儲存暫存檔案與 Artifacts 的 GCS Bucket 名稱。 |
| `AZURE_OPENAI_API_KEY` | - | 否* | 若使用 Azure OpenAI 服務，請填入 API Key。 |
| `AZURE_OPENAI_ENDPOINT` | - | 否* | Azure OpenAI 的 Endpoint URL。 |
| `OPENAI_API_VERSION` | - | 否* | Azure OpenAI 的 API 版本，例如 `2023-05-15`。 |

*\*註：Azure 相關變數僅在整合 Azure OpenAI 作為後端模型時需要設定。*

## 3. 安裝與部署 (Installation & Deployment)

### 套件安裝
本專案使用 `pyproject.toml` 進行相依性管理。

**方法一：使用 Poetry (推薦)**
```bash
# 安裝相依套件
poetry install

# 進入虛擬環境
poetry shell
```

**方法二：使用 Pip**
```bash
# 直接安裝當前目錄套件
pip install .
```

*注意：本專案目前未提供 Dockerfile，建議直接於 Python 環境中運行。*

## 4. 操作指南 (Operations)

### 基本操作
**部署 Agent 至 Vertex AI Agent Engine**
使用 `deploy.py` 腳本將 Agent 部署為遠端服務：
```bash
python -m machine_learning_engineering.deployment.deploy --create
```

**列出已部署的 Agents**
```bash
python -m machine_learning_engineering.deployment.deploy --list
```

### 進階設定 (LLM Integration)
**Azure OpenAI 整合**
若需將後端模型切換為 Azure OpenAI，請確保已設定上述 Azure 相關環境變數。系統會優先讀取 `AZURE_OPENAI_ENDPOINT` 與 `AZURE_OPENAI_API_KEY` 來建立連線。
建議在 `.env` 中明確指定 Deployment Name 與 API Version 以避免版本相容性問題。

### 故障排除 (Troubleshooting)
1.  **Azure 連線錯誤 (401/404)**：
    *   檢查 `AZURE_OPENAI_API_KEY` 是否正確。
    *   確認 `AZURE_OPENAI_ENDPOINT` 是否包含完整的資源路徑。
    *   確認 Deployment Name 是否與 Azure Portal 上的設定一致。
2.  **Python 套件相依性問題**：
    *   若遇到版本衝突，建議刪除 `.venv` 資料夾並重新執行 `poetry install`。
    *   確認 Python 版本是否為 3.10 以上。
3.  **GCP 權限錯誤**：
    *   確認執行環境已透過 `gcloud auth login` 或 Service Account 取得足夠權限 (Vertex AI User, Storage Object Admin)。

## 5. 範例與截圖 (Examples)

> [圖片說明：此處應顯示 `python -m machine_learning_engineering.deployment.deploy --list` 指令執行後的終端機輸出截圖，顯示已部署的 Agent 列表。]

**部署成功範例輸出**：
```text
PROJECT: my-gcp-project
LOCATION: us-central1
BUCKET: my-staging-bucket
Created remote agent: projects/my-gcp-project/locations/us-central1/agents/mle-frontdoor-agent
```
