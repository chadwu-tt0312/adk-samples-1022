# MLE-STAR 使用說明

## 1. 簡介

本文件為「MLE-STAR (Machine Learning Engineering Agent)」專案的技術使用手冊。

MLE-STAR 是一個創新的機器學習工程自動化代理程式，旨在自動化實現機器學習模型的完整流程。其核心架構是一個基於 Python 的代理程式，利用大型語言模型（LLM）來理解任務、生成程式碼、進行測試與優化，最終提交一個完整的解決方案。

此架構目前主要整合 Google 的 Gemini 系列模型（透過 Vertex AI 或 Google AI Platform 執行），並設計為可擴充以支援其他模型服務。

本文件的目標讀者為負責部署、設定與維護此專案的 DevOps 工程師、系統管理員或後端開發人員。

## 2. 環境變數詳解 (Environment Variables)

專案的執行高度依賴環境變數。請將 `.env.example` 檔案複製為 `.env`，並填寫以下必要資訊。

| 變數名稱                          | 預設值                    | 必填 | 說明                                                                                                                                                            |
| --------------------------------- | ------------------------- | ---- | --------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `GOOGLE_GENAI_USE_VERTEXAI`       | `true`                    | 是   | 設定為 `true` 或 `1` 以使用 Google Cloud Vertex AI 後端。設定為 `false` 或 `0` 則使用 Google AI Platform Studio (ML Dev) 後端。                                    |
| `GOOGLE_API_KEY`                  | `YOUR_VALUE_HERE`         | 條件 | 當 `GOOGLE_GENAI_USE_VERTEXAI` 設為 `false` 或 `0` 時，此為必要的 Google AI Platform Studio API 金鑰。                                                                 |
| `GOOGLE_CLOUD_PROJECT`            | `gen-lang-client-0331781710` | 條件 | 當 `GOOGLE_GENAI_USE_VERTEXAI` 設為 `true` 或 `1` 時，此為必要的 Google Cloud 專案 ID。                                                                              |
| `GOOGLE_CLOUD_LOCATION`           | `us-central1`             | 條件 | 當 `GOOGLE_GENAI_USE_VERTEXAI` 設為 `true` 或 `1` 時，此為必要的 Google Cloud 資源地區。                                                                             |
| `ROOT_AGENT_MODEL`                | `gemini-1.5-flash`        | 否   | 指定代理程式所使用的核心 LLM 模型名稱。                                                                                                                         |
| `GOOGLE_CLOUD_STORAGE_BUCKET`     | (無)                      | 否   | 用於部署或儲存產出檔案的 Google Cloud Storage 儲存桶名稱。主要由 `deployment/deploy.py` 等部署腳本使用。                                                    |
| `ADK_DISABLE_LOGGING`             | `true`                    | 否   | 設定為 `true` 可禁用 ADK 的日誌記錄功能，以避免在特定環境下（如無寫入權限）產生 symlink 相關錯誤。                                                           |

### Azure OpenAI 整合變數 (參考)

雖然當前版本主要支援 Google AI 平台，但若要擴充支援 Azure OpenAI，通常需要設定以下標準環境變數。請注意，程式碼需要對應修改才能實際啟用。

| 變數名稱                  | 必填 | 說明                                           |
| ------------------------- | ---- | ---------------------------------------------- |
| `AZURE_OPENAI_API_KEY`    | 是   | 您的 Azure OpenAI 服務 API 金鑰。                |
| `AZURE_OPENAI_ENDPOINT`   | 是   | 您的 Azure OpenAI 服務端點 URL。                 |
| `OPENAI_API_VERSION`      | 是   | 您要使用的 Azure OpenAI API 版本，例如 `2024-02-01`。 |
| `AZURE_OPENAI_DEPLOYMENT_NAME` | 是 | 您在 Azure OpenAI 中建立的部署 (Deployment) 名稱。 |


## 3. 安裝與部署

此專案使用 Poetry 進行套件管理。經分析，專案未包含 `Dockerfile` 或 `docker-compose.yml`，因此目前僅提供本機開發環境的安裝指引。

### 本機安裝 (Poetry)

1.  **安裝 Poetry**:
    若您的系統尚未安裝 Poetry，請參考其[官方文件](https://python-poetry.org/docs/#installation)進行安裝。

2.  **建立虛擬環境與安裝相依套件**:
    在專案根目錄下執行以下指令，Poetry 會自動偵測 `pyproject.toml` 檔案，建立虛擬環境並安裝所有必要的 Python 套件。

    ```bash
    # 建議先設定 poetry 將虛擬環境建立在專案目錄下
    poetry config virtualenvs.in-project true

    # 安裝相依套件
    poetry install
    ```
    > [圖片說明：此處應顯示 `poetry install` 指令成功執行的終端機畫面。]

3.  **啟用虛擬環境**:
    執行以下指令以啟用由 Poetry 管理的 Shell 環境。

    ```bash
    poetry shell
    ```

4.  **設定環境變數**:
    將 `.env.example` 複製為 `.env`，並根據「環境變數詳解」章節的說明填入您的設定值。

## 4. 操作指南

### 基本操作

專案的核心執行腳本是 `run_task.py`，它允許您以非互動模式執行一個完整的機器學習任務。

您可以透過指令列參數傳遞任務描述。若未提供，則預設執行 `Please solve the titanic task`。

**執行範例：**

```bash
# 啟用虛擬環境
poetry shell

# 執行預設的鐵達尼號生存預測任務
python run_task.py

# 執行自訂任務（例如：加州房價預測）
python run_task.py "Please solve the california-housing-prices task"
```
> [圖片說明：此處應顯示 `run_task.py` 腳本執行過程中的 Log 輸出，包含最終的 Agent 回應。]


### 進階設定 (LLM Integration)

#### Google AI Platform (Vertex AI / AI Studio)

模型的選擇由 `GOOGLE_GENAI_USE_VERTEXAI` 環境變數控制：
*   **使用 Vertex AI (推薦)**:
    1.  設定 `GOOGLE_GENAI_USE_VERTEXAI=true`。
    2.  確保 `GOOGLE_CLOUD_PROJECT` 和 `GOOGLE_CLOUD_LOCATION` 已正確設定。
    3.  確保您的執行環境（例如本機 gcloud CLI 或服務帳號）已通過 `gcloud auth application-default login` 認證。

*   **使用 Google AI Platform Studio (舊稱 ML Dev)**:
    1.  設定 `GOOGLE_GENAI_USE_VERTEXAI=false`。
    2.  在 `.env` 檔案中提供您的 `GOOGLE_API_KEY`。

#### Azure OpenAI 整合 (擴充指引)

如需將模型更換為 Azure OpenAI，您需要：
1.  在 `.env` 中設定 `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_ENDPOINT`, `OPENAI_API_VERSION`, 和 `AZURE_OPENAI_DEPLOYMENT_NAME` 等變數。
2.  修改程式碼中初始化 LLM Client 的部分（例如 `machine_learning_engineering/agent.py`），使其能根據環境變數讀取 Azure 憑證並建立對應的 Client 實例。

### 故障排除 (Troubleshooting)

*   **Python 相依性問題**:
    - **問題**: `poetry install` 失敗或出現版本衝突。
    - **解決方案**: 嘗試刪除 `poetry.lock` 檔案並重新執行 `poetry install`。若問題持續，請檢查 `pyproject.toml` 中是否有不相容的版本釘選。

*   **Google AI 連線錯誤 (401/403 Unauthorized, 404 Not Found)**:
    - **問題**: 執行時出現認證失敗或找不到資源的錯誤。
    - **解決方案**:
        1.  **檢查 Vertex AI 設定**：確認 `GOOGLE_CLOUD_PROJECT` 和 `GOOGLE_CLOUD_LOCATION` 是否正確。
        2.  **執行 gcloud 認證**：在本機執行 `gcloud auth application-default login` 並使用具有權限的帳號登入。
        3.  **檢查 API Key**：若使用 AI Studio，請確認 `GOOGLE_API_KEY` 是否正確且未過期。
        4.  **檢查 API 是否啟用**：確保您的 Google Cloud 專案已啟用 "Vertex AI API"。

*   **NFS 掛載失敗 (針對潛在的容器化部署)**:
    - **問題**: 在 Kubernetes 環境中，Pod 因無法掛載 NFS Persistent Volume 而啟動失敗。
    - **解決方案**:
        1.  **檢查 PV/PVC 狀態**: 使用 `kubectl describe pv <pv-name>` 和 `kubectl describe pvc <pvc-name>` 檢查詳細錯誤訊息。
        2.  **檢查 NFS Server 與路徑**: 確認 `PersistentVolume` 定義中的 `server` IP 和 `path` 是否正確且可從 K8s Worker 節點存取。
        3.  **檢查權限**: 確保 NFS Server 上的匯出目錄具有正確的讀寫權限（`uid`/`gid` 可能需要與容器內的使用者匹配）。

## 5. 範例與截圖

本節提供具體操作的範例。

### 程式碼執行範例

以下指令展示如何啟動一個分析 "california-housing-prices" 資料集的任務。

```bash
python run_task.py "Please perform exploratory data analysis and build a regression model for the california-housing-prices dataset. The goal is to predict the median house value."
```

### 產出結果示意

代理程式執行完畢後，會在 `machine_learning_engineering/workspace/<task-name>/` 目錄下生成相關的程式碼、模型與報告檔案。

> [圖片說明：此處應顯示 `workspace/california-housing-prices/` 目錄結構的檔案總管或 `ls` 指令截圖，展示其中生成的 `.py` 和 `.csv` 檔案。]
