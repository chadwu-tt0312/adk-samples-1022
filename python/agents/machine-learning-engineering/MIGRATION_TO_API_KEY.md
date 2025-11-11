# 遷移到 API Key 模式（無需 gcloud 權限）

## 修改摘要

本次修改將 machine-learning-engineering agent 預設改為使用 Google AI Studio API Key 模式，避免需要 gcloud 認證。

## 已完成的修改

### 1. `adk_runner.py`
- ✅ 移除強制設定 `GOOGLE_GENAI_USE_VERTEXAI=true`
- ✅ 預設改為 `false`（使用 API Key 模式）
- ✅ 新增 API Key 檢查與提示訊息
- ✅ 保留 Vertex AI 模式的支援

### 2. `adk_fix.py`
- ✅ 與 `adk_runner.py` 相同的修改
- ✅ 確保兩種執行方式都支援 API Key 模式

### 3. `README.md`
- ✅ 更新 Configuration 章節
- ✅ 新增兩種模式的詳細說明
- ✅ 明確標示推薦方式（API Key 模式）

## 使用方法

### 方式一：使用 API Key（推薦，無需 gcloud）

1. **取得 API Key**
   - 訪問 https://aistudio.google.com/apikey
   - 登入並建立 API Key

2. **設定環境變數**
   ```bash
   export GOOGLE_API_KEY=your-api-key-here
   export ROOT_AGENT_MODEL=gemini-2.5-flash
   # 或使用 .env 檔案
   ```

3. **執行 Agent**
   ```bash
   adk web
   # 或
   adk run machine_learning_engineering
   ```

### 方式二：使用 Vertex AI（需要 gcloud）

如果需要使用 Vertex AI，設定以下環境變數：

```bash
export GOOGLE_GENAI_USE_VERTEXAI=true
export GOOGLE_CLOUD_PROJECT=your-project-id
export GOOGLE_CLOUD_LOCATION=us-central1
```

然後執行 gcloud 認證：
```bash
gcloud auth application-default login
gcloud auth application-default set-quota-project $GOOGLE_CLOUD_PROJECT
```

## .env 檔案範例

建立 `.env` 檔案（複製以下內容並填入你的 API Key）：

```bash
# API Key 模式（推薦）
GOOGLE_API_KEY=your-google-ai-studio-api-key-here
ROOT_AGENT_MODEL=gemini-2.5-flash
GOOGLE_GENAI_USE_VERTEXAI=false

# 如果需要使用 Vertex AI，取消註解並設定以下變數：
# GOOGLE_GENAI_USE_VERTEXAI=true
# GOOGLE_CLOUD_PROJECT=your-gcp-project-id
# GOOGLE_CLOUD_LOCATION=us-central1
```

## 注意事項

1. **API Key 模式限制**
   - 不需要 Google Cloud Project
   - 不需要 gcloud CLI
   - 適合本地開發和測試
   - 無法使用部署到 Vertex AI Agent Engine 的功能

2. **Vertex AI 模式**
   - 需要 Google Cloud Project
   - 需要 gcloud 認證
   - 可用於部署到 Vertex AI Agent Engine
   - 可能有更多進階功能

3. **Google Search Tool**
   - `google_search_tool` 可能仍需要某些 Google 服務認證
   - 如遇到問題，可能需要額外設定

## 測試建議

1. 測試 API Key 模式：
   ```bash
   export GOOGLE_API_KEY=your-key
   export GOOGLE_GENAI_USE_VERTEXAI=false
   adk run machine_learning_engineering
   ```

2. 如果遇到錯誤，檢查：
   - API Key 是否正確設定
   - 環境變數是否正確載入
   - `google-genai` 套件版本是否支援 API Key 模式

## 回報問題

如果遇到任何問題，請檢查：
1. API Key 是否有效
2. 環境變數設定是否正確
3. `google-genai` 和 `google-adk` 版本是否相容

