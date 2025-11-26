# MLE-STAR 使用說明

**文件版本**：v1.0.0  
**最後更新**：2025年11月

---

## 1. 簡介

### 專案概述

MLE-STAR（Machine Learning Engineering Agent via Search and Targeted Refinement）是一個自動化機器學習工程代理系統，能夠自動完成從資料清理、特徵工程、模型選擇、超參數調整到 Ensemble 整合的完整 ML 流程。

### 核心功能

- **初始解決方案生成**：透過搜尋引擎檢索最新的模型與範例程式碼，整合最佳候選方案
- **程式碼區塊精煉**：透過 Ablation Study 識別影響效能最大的程式碼區塊，進行迭代優化
- **Ensemble 策略**：提出並優化多模型整合策略，提升整體表現
- **穩健性模組**：包含除錯代理、資料洩漏檢查器與資料使用檢查器

### 系統架構

MLE-STAR 採用多代理（Multi-Agent）架構，包含以下子代理：

1. **Initialization Agent**：初始化代理，負責生成初始解決方案
2. **Refinement Agent**：精煉代理，負責迭代優化模型
3. **Ensemble Agent**：整合代理，負責生成 Ensemble 策略
4. **Submission Agent**：提交代理，負責產出最終解決方案

### 技術規格

- **Python 版本**：3.12+
- **依賴管理**：Poetry
- **授權協議**：Apache License 2.0
- **LLM 支援**：Google Gemini（透過 Vertex AI 或 Google AI Studio API Key）

---

## 2. 環境變數詳解

### 環境變數總覽

MLE-STAR 使用以下環境變數進行配置。建議將這些變數設定在 `.env` 檔案中，或透過 `export` 指令在 shell 中設定。

### Google Cloud / Vertex AI 相關變數

| 變數名稱 | 預設值 | 必填 | 說明 |
|---------|--------|------|------|
| `GOOGLE_GENAI_USE_VERTEXAI` | `false` | 否 | 是否使用 Vertex AI。設為 `true` 時使用 Vertex AI，設為 `false` 時使用 Google AI Studio API Key 模式 |
| `GOOGLE_CLOUD_PROJECT` | - | 條件必填 | GCP 專案 ID。僅在使用 Vertex AI 模式時必填 |
| `GOOGLE_CLOUD_LOCATION` | - | 條件必填 | GCP 專案位置（如 `us-central1`）。僅在使用 Vertex AI 模式時必填 |
| `GOOGLE_CLOUD_STORAGE_BUCKET` | - | 條件必填 | GCS 儲存桶名稱。僅在部署至 Vertex AI Agent Engine 時必填 |
| `GOOGLE_API_KEY` | - | 條件必填 | Google AI Studio API Key。僅在使用 API Key 模式時必填 |

### LLM 模型相關變數

| 變數名稱 | 預設值 | 必填 | 說明 |
|---------|--------|------|------|
| `ROOT_AGENT_MODEL` | `gemini-2.0-flash-001` | 否 | 使用的 LLM 模型名稱。建議值：`gemini-2.5-pro`（最佳表現）、`gemini-2.5-flash`（平衡成本與表現）、`gemini-2.0-flash-001` |

### 其他環境變數

| 變數名稱 | 預設值 | 必填 | 說明 |
|---------|--------|------|------|
| `ADK_DISABLE_LOGGING` | - | 否 | 設為 `true` 時停用 ADK 日誌記錄 |
| `ADK_LOG_LEVEL` | - | 否 | ADK 日誌層級（如 `ERROR`、`INFO`、`DEBUG`） |

### Azure OpenAI 整合說明

**注意**：MLE-STAR 目前主要支援 Google Cloud Platform（Vertex AI）與 Google AI Studio API Key。若需要整合 Azure OpenAI，可能需要進行以下客製化：

| 變數名稱 | 說明 | 備註 |
|---------|------|------|
| `AZURE_OPENAI_API_KEY` | Azure OpenAI API 金鑰 | 需要修改程式碼以支援 Azure OpenAI SDK |
| `AZURE_OPENAI_ENDPOINT` | Azure OpenAI 端點 URL | 格式：`https://{your-resource-name}.openai.azure.com/` |
| `OPENAI_API_VERSION` | API 版本 | 建議使用 `2024-02-15-preview` 或更新版本 |
| `AZURE_OPENAI_DEPLOYMENT_NAME` | Deployment 名稱 | 在 Azure Portal 中建立的模型部署名稱 |

**重要提示**：整合 Azure OpenAI 需要修改 `machine_learning_engineering/agent.py` 與相關的 LLM 呼叫程式碼，將 Google GenAI SDK 替換為 Azure OpenAI SDK。此為進階客製化需求，不在本文件標準部署範圍內。

### 環境變數設定範例

#### 方式一：使用 Google AI Studio API Key（推薦，無需 gcloud）

建立 `.env` 檔案：

```bash
# API Key 模式（推薦）
GOOGLE_API_KEY=your-google-ai-studio-api-key-here
ROOT_AGENT_MODEL=gemini-2.5-flash
GOOGLE_GENAI_USE_VERTEXAI=false
```

#### 方式二：使用 Vertex AI（需要 gcloud 認證）

建立 `.env` 檔案：

```bash
# Vertex AI 模式
GOOGLE_GENAI_USE_VERTEXAI=true
GOOGLE_CLOUD_PROJECT=your-gcp-project-id
GOOGLE_CLOUD_LOCATION=us-central1
ROOT_AGENT_MODEL=gemini-2.5-pro
GOOGLE_CLOUD_STORAGE_BUCKET=your-storage-bucket  # 僅部署時需要
```

---

## 3. 安裝與部署

### 3.1 前置需求

- **Python 3.12+**
- **Poetry**：用於依賴管理與套件安裝
- **Git**：用於 clone 專案
- **Google Cloud Account**（僅在使用 Vertex AI 模式時需要）
- **Google Cloud CLI**（僅在使用 Vertex AI 模式時需要）

### 3.2 本機安裝步驟

#### 步驟 1：Clone 專案

```bash
git clone https://github.com/google/adk-samples.git
cd adk-samples/python/agents/machine-learning-engineering
```

#### 步驟 2：安裝 Poetry

```bash
pip install poetry
```

**注意**：Linux 使用者若遇到 `keyring` 相關錯誤，可執行以下指令停用：

```bash
poetry config keyring.enabled false
```

#### 步驟 3：安裝專案依賴

```bash
poetry install
```

此指令會讀取 `pyproject.toml` 並安裝所有必要的依賴套件至 Poetry 管理的虛擬環境中。

若遇到 `command not found` 錯誤，可使用：

```bash
python -m poetry install
```

#### 步驟 4：啟動虛擬環境

```bash
poetry shell
```

或使用：

```bash
source $(poetry env info --path)/bin/activate
```

驗證環境已啟動：

```bash
poetry env list
```

預期輸出範例：

```
machine-learning-engineering-Gb54hHID-py3.12 (Activated)
```

#### 步驟 5：設定環境變數

根據選擇的模式（API Key 或 Vertex AI），設定對應的環境變數（詳見「環境變數詳解」章節）。

**使用 API Key 模式**：

```bash
export GOOGLE_API_KEY=your-api-key-here
export ROOT_AGENT_MODEL=gemini-2.5-flash
export GOOGLE_GENAI_USE_VERTEXAI=false
```

**使用 Vertex AI 模式**：

```bash
export GOOGLE_GENAI_USE_VERTEXAI=true
export GOOGLE_CLOUD_PROJECT=your-project-id
export GOOGLE_CLOUD_LOCATION=us-central1
export ROOT_AGENT_MODEL=gemini-2.5-pro
```

然後執行 gcloud 認證：

```bash
gcloud auth application-default login
gcloud auth application-default set-quota-project $GOOGLE_CLOUD_PROJECT
```

### 3.3 驗證安裝

執行以下指令驗證安裝是否成功：

```bash
poetry run adk run machine_learning_engineering
```

若看到 Agent 啟動訊息，表示安裝成功。

---

## 4. 操作指南

### 4.1 基本操作

#### 啟動服務

**方式一：使用 CLI**

```bash
adk run machine_learning_engineering
```

或透過 Poetry：

```bash
poetry run adk run machine_learning_engineering
```

**方式二：使用 Web 介面**

```bash
adk web
```

此指令會啟動 Web 伺服器並顯示 URL（通常為 `http://localhost:8000`）。開啟 URL 後，在左上角下拉選單選擇 `machine_learning_engineering`，即可使用聊天介面與 Agent 互動。

#### 準備任務

1. 在 `machine_learning_engineering/tasks/` 目錄下建立任務資料夾（例如 `titanic`）
2. 在該資料夾中建立任務描述檔案
3. 將資料檔案（如 CSV）放置於該資料夾中

範例結構：

```
machine_learning_engineering/tasks/
└── titanic/
    ├── task_description.txt
    ├── train.csv
    └── test.csv
```

#### 執行任務

透過 CLI 或 Web 介面與 Agent 互動，例如：

```
[user]: execute the titanic task
```

Agent 會自動：
1. 識別任務名稱
2. 載入資料
3. 執行完整的 ML 流程（初始化、精煉、整合、提交）
4. 產出最終解決方案（`final_solution.py`）

### 4.2 進階設定

#### LLM 整合設定

**Google AI Studio API Key 模式（推薦）**

1. 取得 API Key：
   - 訪問 https://aistudio.google.com/apikey
   - 登入並建立 API Key

2. 設定環境變數：
   ```bash
   export GOOGLE_API_KEY=your-api-key-here
   export ROOT_AGENT_MODEL=gemini-2.5-flash
   export GOOGLE_GENAI_USE_VERTEXAI=false
   ```

**Vertex AI 模式**

1. 設定環境變數：
   ```bash
   export GOOGLE_GENAI_USE_VERTEXAI=true
   export GOOGLE_CLOUD_PROJECT=your-project-id
   export GOOGLE_CLOUD_LOCATION=us-central1
   export ROOT_AGENT_MODEL=gemini-2.5-pro
   ```

2. 執行 gcloud 認證：
   ```bash
   gcloud auth application-default login
   gcloud auth application-default set-quota-project $GOOGLE_CLOUD_PROJECT
   ```

**模型選擇建議**

| 模型 | 獎牌率 | 成本 | 適用場景 |
|------|--------|------|---------|
| `gemini-2.5-pro` | 63.6% | 高 | 追求最佳表現 |
| `gemini-2.5-flash` | 43.9% | 中 | 平衡成本與表現 |
| `gemini-2.0-flash-001` | - | 低 | 開發測試 |

#### 配置參數調整

主要配置參數定義於 `machine_learning_engineering/shared_libraries/config.py` 的 `DefaultConfig` 類別。可調整的參數包括：

- `num_solutions`：生成的解決方案數量（預設：2）
- `num_model_candidates`：模型候選數量（預設：2）
- `max_retry`：最大重試次數（預設：10）
- `max_debug_round`：最大除錯輪數（預設：5）
- `inner_loop_round`：內層迴圈輪數（預設：1）
- `outer_loop_round`：外層迴圈輪數（預設：1）
- `ensemble_loop_round`：Ensemble 迴圈輪數（預設：1）

### 4.3 故障排除

#### Google Cloud 連線錯誤

**錯誤：401 Unauthorized**

- **原因**：認證失敗或 API Key 無效
- **解決方案**：
  - 檢查 `GOOGLE_API_KEY` 是否正確設定
  - 若使用 Vertex AI，確認已執行 `gcloud auth application-default login`
  - 確認 API Key 或服務帳號具有適當權限

**錯誤：404 Not Found**

- **原因**：專案 ID 或位置設定錯誤
- **解決方案**：
  - 檢查 `GOOGLE_CLOUD_PROJECT` 是否正確
  - 檢查 `GOOGLE_CLOUD_LOCATION` 是否為有效位置（如 `us-central1`）
  - 確認專案已啟用 Vertex AI API

**錯誤：Permission Denied**

- **原因**：服務帳號權限不足
- **解決方案**：
  - 確認服務帳號具有 `Vertex AI User` 角色
  - 若使用 GCS，確認具有 `Storage Object Admin` 角色

#### Python 套件相依性問題

**錯誤：ModuleNotFoundError**

- **原因**：套件未正確安裝或虛擬環境未啟動
- **解決方案**：
  ```bash
  poetry install
  poetry shell
  ```

**錯誤：版本衝突**

- **原因**：套件版本不相容
- **解決方案**：
  ```bash
  poetry update
  ```

#### 資料載入錯誤

**錯誤：FileNotFoundError**

- **原因**：任務資料夾或檔案不存在
- **解決方案**：
  - 確認任務資料夾位於 `machine_learning_engineering/tasks/` 目錄下
  - 確認資料檔案名稱與路徑正確

#### NFS 掛載失敗（部署環境）

**注意**：本專案目前不包含容器化部署配置，此問題僅在自行建立 Kubernetes 部署時可能遇到。

若在 Kubernetes 環境中部署，NFS Persistent Volume 掛載失敗的常見原因：

- **原因**：NFS 伺服器連線失敗或權限設定錯誤
- **解決方案**：
  - 確認 NFS 伺服器可從 Kubernetes 節點存取
  - 檢查 PersistentVolume 與 PersistentVolumeClaim 設定
  - 確認 Pod 具有適當的 SecurityContext 權限

#### 其他常見問題

**Agent 無回應**

- 檢查環境變數是否正確設定
- 確認 LLM API 配額未用盡
- 查看日誌檔案（位於 `machine_learning_engineering/logs/`）

**執行時間過長**

- 調整 `exec_timeout` 參數（預設：600 秒）
- 考慮使用較快的模型（如 `gemini-2.5-flash`）
- 減少 `num_solutions` 或 `num_model_candidates` 參數

---

## 5. 範例與截圖

### 5.1 基本互動範例

以下為透過 Web 介面與 Agent 互動的範例對話：

> **[user]:** who are you?

> **[mle_frontdoor_agent]:** I am a machine learning engineer agent.

> **[user]:** what can you do?

> **[mle_frontdoor_agent]:** I am a machine learning engineer. My primary role is to engineer solutions for machine learning tasks, such as the California Housing Task. I can also describe the task if you'd like. I work by executing a sequence of sub-agents to solve the machine learning engineering task.

> **[user]:** describe the task that you have

> **[mle_frontdoor_agent]:** The task I have is the California Housing Task. This task involves predicting the median house value in California districts, given various features about those districts. It's a regression problem where the goal is to build a model that can accurately estimate house prices based on factors like population, median income, and housing age within a district.

> **[user]:** execute the task

> **[mle_frontdoor_agent]:** *\<執行過程輸出\>*  
> Submission file saved successfully to {submission_file_path}

> [圖片說明：此處應顯示 Web 介面截圖，包含 Agent 回應與執行過程]

### 5.2 任務執行流程

執行任務時，Agent 會依序執行以下步驟：

1. **初始化階段**：生成初始解決方案
2. **精煉階段**：迭代優化模型效能
3. **整合階段**：生成 Ensemble 策略
4. **提交階段**：產出最終解決方案

> [圖片說明：此處應顯示執行流程的視覺化圖表或日誌輸出]

### 5.3 產出檔案

任務執行完成後，會在 `machine_learning_engineering/workspace/{task_name}/` 目錄下產生以下檔案：

- `final_solution.py`：最終解決方案程式碼
- `final_state.json`：最終狀態記錄
- 其他中間產出檔案（視任務而定）

> [圖片說明：此處應顯示 workspace 目錄結構與檔案內容範例]

### 5.4 部署至 Vertex AI Agent Engine

若使用 Vertex AI 模式，可將 Agent 部署至 Vertex AI Agent Engine：

```bash
# 安裝部署依賴
poetry install --with deployment

# 部署 Agent
python3 deployment/deploy.py --create
```

部署完成後會顯示：

```
Created remote agent: projects/<PROJECT_NUMBER>/locations/<PROJECT_LOCATION>/reasoningEngines/<AGENT_ENGINE_ID>
```

列出已部署的 Agent：

```bash
python3 deployment/deploy.py --list
```

測試部署的 Agent：

```bash
export USER_ID=test-user
python3 deployment/test_deployment.py --resource_id=${AGENT_ENGINE_ID} --user_id=${USER_ID}
```

> [圖片說明：此處應顯示部署成功訊息與測試互動範例]

---

## 附錄

### A. 專案結構

```
machine-learning-engineering/
├── machine_learning_engineering/
│   ├── agent.py                    # 主 Agent 定義
│   ├── prompt.py                   # Prompt 定義
│   ├── shared_libraries/           # 共用函式庫
│   │   └── config.py              # 配置定義
│   ├── sub_agents/                 # 子代理
│   │   ├── initialization/        # 初始化代理
│   │   ├── refinement/           # 精煉代理
│   │   ├── ensemble/             # 整合代理
│   │   └── submission/           # 提交代理
│   ├── tasks/                     # 任務資料夾
│   └── workspace/                 # 工作區（產出檔案）
├── deployment/                     # 部署腳本
├── tests/                          # 測試檔案
├── pyproject.toml                  # Poetry 配置
└── README.md                       # 專案說明
```

### B. 相關資源

- **專案 GitHub**：https://github.com/google/adk-samples
- **研究論文**：https://www.arxiv.org/abs/2506.15692
- **MLE-Bench**：https://github.com/openai/mle-bench
- **Google AI Studio**：https://aistudio.google.com/
- **Vertex AI 文件**：https://cloud.google.com/vertex-ai/docs

### C. 版本資訊

- **專案版本**：0.1
- **Python 需求**：>= 3.12, < 4.0
- **主要依賴**：
  - `google-adk` (>=1.5.0,<2.0.0)
  - `google-genai` (>=1.9.0,<2.0.0)
  - `google-cloud-aiplatform` (>=1.93,<2.0)
  - `scikit-learn` (>=1.7.1,<2.0.0)
  - `torch` (>=2.7.1,<3.0.0)
  - `xgboost` (>=3.1.1)

---

**文件結束**

