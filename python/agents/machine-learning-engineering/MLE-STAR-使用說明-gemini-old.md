# MLE-STAR 使用說明

## 1. 簡介
MLE-STAR 是一個創新的機器學習工程 (MLE) 代理程式，旨在自動化機器學習模型的實作過程。它透過一系列的子代理程式協同工作，從任務初始化、模型精煉到最終提交，以簡化和加速 ML 開發流程。

## 2. 安裝與部署

### 2.1 生產環境部署 (Kubernetes Helm)

由於專案中沒有提供現成的 Kubernetes Helm Chart 或 Docker Compose 設定，以下將說明如何為 MLE-STAR 專案準備容器映像檔，並建立基本的 Helm Chart 進行 Kubernetes 部署，同時涵蓋 NFS 儲存的配置。

#### 2.1.1 建立 Docker 映像檔

首先，需要為 MLE-STAR 應用程式建立一個 Docker 映像檔。以下是一個基本的 `Dockerfile` 範例，假設應用程式的啟動腳本為 `run_task.py`：

```dockerfile
# 使用官方 Python 基礎映像檔
FROM python:3.12-slim-bookworm

# 設定工作目錄
WORKDIR /app

# 將 poetry 相關設定複製到容器中
COPY pyproject.toml poetry.lock ./

# 安裝 Poetry
RUN pip install poetry

# 安裝專案依賴
RUN poetry install --no-root --no-dev

# 複製應用程式程式碼
COPY . .

# 設定環境變數 (請根據實際需求調整)
ENV GOOGLE_GENAI_USE_VERTEXAI=1
ENV GOOGLE_CLOUD_PROJECT=YOUR_GOOGLE_CLOUD_PROJECT_ID
ENV GOOGLE_CLOUD_LOCATION=YOUR_GOOGLE_CLOUD_LOCATION
ENV ROOT_AGENT_MODEL='gemini-2.5-flash'

# 如果使用 GOOGLE_API_KEY，請務必安全地注入，例如透過 Kubernetes Secrets
# ENV GOOGLE_API_KEY=YOUR_API_KEY

# 定義應用程式啟動指令
# 請根據您的實際應用程式入口點調整
CMD ["poetry", "run", "python", "run_task.py"]
```

**建置 Docker 映像檔：**

```bash
docker build -t mle-star-app:latest .
docker push your-registry/mle-star-app:latest
```
請將 `your-registry` 替換為您的容器註冊表地址。

#### 2.1.2 建立 Helm Chart

一個基本的 Helm Chart 結構如下：

```
mle-star-chart/
├── Chart.yaml
├── values.yaml
├── templates/
│   ├── deployment.yaml
│   ├── service.yaml
│   └── _helpers.tpl
└── requirements.yaml (如果需要管理子 Chart)
```

**Chart.yaml 範例:**
```yaml
apiVersion: v2
name: mle-star-app
description: A Helm chart for the MLE-STAR application
version: 0.1.0
appVersion: "1.0.0"
```

**values.yaml 範例 (配置映像檔、環境變數、資源請求等):**
```yaml
replicaCount: 1

image:
  repository: your-registry/mle-star-app
  pullPolicy: IfNotPresent
  # Overrides the image tag whose default is the chart appVersion.
  tag: "latest"

env:
  GOOGLE_GENAI_USE_VERTEXAI: "1"
  GOOGLE_CLOUD_PROJECT: "your-gcp-project-id"
  GOOGLE_CLOUD_LOCATION: "your-gcp-region"
  ROOT_AGENT_MODEL: "gemini-2.5-flash"
  # GOOGLE_API_KEY: "" # 請透過 Secret 注入

nfs:
  enabled: true
  server: nfs-server.example.com # 您的 NFS 伺服器地址
  path: /exports/mle-star # 您的 NFS 匯出路徑

service:
  type: ClusterIP
  port: 80 # 如果應用程式有暴露服務，請指定埠號

resources:
  limits:
    cpu: 500m
    memory: 1Gi
  requests:
    cpu: 200m
    memory: 512Mi
```

**templates/deployment.yaml 範例 (包含 NFS PV/PVC 配置):**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "mle-star-app.fullname" . }}
  labels:
    {{- include "mle-star-app.labels" . | nindent 4 }}
spec:
  replicas: {{ .Values.replicaCount }}
  selector:
    matchLabels:
      {{- include "mle-star-app.selectorLabels" . | nindent 6 }}
  template:
    metadata:
      labels:
        {{- include "mle-star-app.selectorLabels" . | nindent 8 }}
    spec:
      containers:
        - name: {{ .Chart.Name }}
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag | default .Chart.AppVersion }}"
          imagePullPolicy: {{ .Values.image.pullPolicy }}
          env:
            {{- range $key, $value := .Values.env }}
            - name: {{ $key }}
              value: {{ $value | quote }}
            {{- end }}
            # 範例：從 Secret 載入 API 金鑰
            # - name: GOOGLE_API_KEY
            #   valueFrom:
            #     secretKeyRef:
            #       name: mle-star-secrets
            #       key: google_api_key
          resources:
            {{- toYaml .Values.resources | nindent 12 }}
          volumeMounts:
            - name: nfs-storage
              mountPath: /app/data # 應用程式內部使用 NFS 的路徑
      volumes:
        - name: nfs-storage
          persistentVolumeClaim:
            claimName: {{ include "mle-star-app.fullname" . }}-pvc
      {{- with .Values.nodeSelector }}
      nodeSelector:
        {{- toYaml . | nindent 8 }}
      {{- end }}
      {{- with .Values.affinity }}
      affinity:
        {{- toYaml . | nindent 8 }}
      {{- end }}
      {{- with .Values.tolerations }}
      tolerations:
        {{- toYaml . | nindent 8 }}
      {{- end }}
---
{{- if .Values.nfs.enabled }}
apiVersion: v1
kind: PersistentVolume
metadata:
  name: {{ include "mle-star-app.fullname" . }}-pv
  labels:
    {{- include "mle-star-app.labels" . | nindent 4 }}
spec:
  capacity:
    storage: 10Gi # 請根據需求調整儲存容量
  accessModes:
    - ReadWriteMany
  nfs:
    server: {{ .Values.nfs.server }}
    path: {{ .Values.nfs.path }}
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: {{ include "mle-star-app.fullname" . }}-pvc
  labels:
    {{- include "mle-star-app.labels" . | nindent 4 }}
spec:
  accessModes:
    - ReadWriteMany
  resources:
    requests:
      storage: 10Gi # 需與 PersistentVolume 的容量匹配
{{- end }}
```

**templates/service.yaml 範例 (如果應用程式有暴露服務):**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: {{ include "mle-star-app.fullname" . }}
  labels:
    {{- include "mle-star-app.labels" . | nindent 4 }}
spec:
  type: {{ .Values.service.type }}
  ports:
    - port: {{ .Values.service.port }}
      targetPort: http
      protocol: TCP
      name: http
  selector:
    {{- include "mle-star-app.selectorLabels" . | nindent 4 }}
```

**部署 Helm Chart：**

```bash
helm upgrade --install mle-star-release ./mle-star-chart -f values.yaml --namespace mle-star --create-namespace
```

**NFS 儲存配置：**
上述 `deployment.yaml` 範例中包含了 `PersistentVolume` 和 `PersistentVolumeClaim` 的定義，用於配置 NFS 儲存。
*   `nfs.server`: 替換為您的 NFS 伺服器的 IP 地址或 hostname。
*   `nfs.path`: 替換為 NFS 伺服器上共享的目錄路徑。
*   `mountPath: /app/data`: 這是應用程式容器內部掛載 NFS 儲存的路徑。請確保您的應用程式會將需要持久化的資料寫入此路徑。

**重要提示：**
*   **安全性：** 環境變數中的敏感資訊（如 `GOOGLE_API_KEY`）應使用 Kubernetes Secrets 安全地管理，而非直接寫入 `values.yaml` 或 `Dockerfile`。
*   **路徑調整：** `mountPath` 應與應用程式中實際使用資料的路徑匹配。例如，如果 `config.py` 中的 `data_dir` 或 `workspace_dir` 指向 `/app/data`，則此處配置是合理的。
*   **NFS 服務：** 確保您的 Kubernetes 集群可以訪問 NFS 伺服器。
*   **完善 Helm Chart：** 上述僅為基本範例，實際生產環境的 Helm Chart 可能需要更完善的健康檢查、HPA (Horizontal Pod Autoscaler)、Ingress 配置等。


### 2.2 開發環境部署
本專案使用 Poetry 進行依賴管理。請按照以下步驟設定開發環境：

1.  **安裝 Poetry (如果尚未安裝):**
    ```bash
    pip install poetry
    ```

2.  **安裝專案依賴:**
    導航至專案根目錄，然後執行：
    ```bash
    poetry install
    ```
    這將會建立一個虛擬環境並安裝所有必要的依賴套件。

3.  **啟用虛擬環境:**
    ```bash
    poetry shell
    ```

4.  **Python 版本要求:**
    專案要求 Python 版本為 `3.12` 或更高。



## 3. 基本操作

MLE-STAR 代理程式主要透過 `run_task.py` 腳本執行。此腳本接收一個任務提示作為輸入，並協調代理程式來解決機器學習任務。

1.  **確保環境變數已設定**：在執行代理程式之前，請確保您的 `.env` 檔案已正確配置，如「環境變數設定」章節所述。

2.  **執行代理程式**：
    在專案的根目錄下，您可以使用 `poetry run` 來執行 `run_task.py`，並傳遞您希望代理程式解決的任務提示。

    **範例：解決 Titanic 任務**
    ```bash
    poetry run python run_task.py "Please solve the titanic task"
    ```

    **範例：解決 California Housing Prices 任務**
    ```bash
    poetry run python run_task.py "Solve the california-housing-prices task"
    ```

    代理程式將會開始執行，並在控制台輸出其進度。最終結果和中間產物將儲存在 `machine_learning_engineering/workspace/` 目錄下對應的任務資料夾中。

## 4. 進階設定

除了 LLM 整合的配置外，MLE-STAR 代理程式還提供了多種參數來控制其行為和性能。這些設定可以在 `machine_learning_engineering/shared_libraries/config.py` 中找到，並可透過修改該檔案來調整。

### 4.1 LLM 整合 (已在上方說明)

### 4.2 其他進階設定

以下是一些重要的進階配置參數：

*   `data_dir` (預設值: `./machine_learning_engineering/tasks/`)：儲存機器學習任務及其資料的目錄路徑。
*   `task_name` (預設值: `"california-housing-prices"`)：要載入和處理的特定任務名稱。
*   `task_type` (預設值: `"Tabular Regression"`)：機器學習問題的類型。
*   `workspace_dir` (預設值: `./machine_learning_engineering/workspace/`)：用於儲存中間輸出、結果和日誌的目錄。
*   `exec_timeout` (預設值: `600`)：允許完成任務的最長秒數。
*   `num_solutions` (預設值: `2`)：為給定任務生成或嘗試的不同解決方案數量。
*   `num_model_candidates` (預設值: `2`)：要考慮作為候選模型的不同模型架構或超參數集的數量。
*   `max_debug_round` (預設值: `5`)：調試步驟允許的最大迭代或回合數。
*   `max_rollback_round` (預設值: `2`)：在發生錯誤或性能不佳時，系統可以回滾到先前狀態的最大次數。
*   `use_data_leakage_checker` (預設值: `False`)：啟用 (`True`) 或禁用 (`False`) 機器學習流程中資料洩漏的檢查。

**修改這些設定：**
您可以直接修改 `machine_learning_engineering/shared_libraries/config.py` 檔案中的 `DefaultConfig` 類別來調整這些參數。例如：

```python
# machine_learning_engineering/shared_libraries/config.py
@dataclasses.dataclass
class DefaultConfig:
    # ... 其他設定 ...
    exec_timeout: int = 1200 # 將執行超時時間增加到 1200 秒
    num_solutions: int = 3   # 嘗試生成 3 個不同的解決方案
    # ... 其他設定 ...
```

透過調整這些參數，您可以微調代理程式的行為，以適應不同的任務複雜度和資源限制。

## 5. 環境變數設定

本專案依賴於以下環境變數進行配置。請將 `.env.example` 檔案複製為 `.env` 並填寫您的值：

```bash
# 選擇模型後端: 0 -> ML Dev (Google Gemini API), 1 -> Vertex AI
GOOGLE_GENAI_USE_VERTEXAI=1

# ML Dev 後端配置。如果使用 ML Dev 後端，請填寫此項。
GOOGLE_API_KEY=您的_API_金鑰

# Vertex AI 後端配置
GOOGLE_CLOUD_PROJECT=您的_Google_Cloud_專案_ID
GOOGLE_CLOUD_LOCATION=您的_Google_Cloud_區域

# 以下值為 MLE-STAR 專案特有

# 代理程式中使用的模型
ROOT_AGENT_MODEL='gemini-2.5-flash'
```

**說明:**

*   `GOOGLE_GENAI_USE_VERTEXAI`:
    *   `1`: 使用 Google Cloud Vertex AI 作為大型語言模型 (LLM) 的後端。
    *   `0`: 使用 Google Gemini API (ML Dev) 作為 LLM 的後端。
*   `GOOGLE_API_KEY`: 當 `GOOGLE_GENAI_USE_VERTEXAI` 設定為 `0` 時，需要提供 Google Gemini API 金鑰。
*   `GOOGLE_CLOUD_PROJECT`: 當 `GOOGLE_GENAI_USE_VERTEXAI` 設定為 `1` 時，需要提供您的 Google Cloud 專案 ID。
*   `GOOGLE_CLOUD_LOCATION`: 當 `GOOGLE_GENAI_USE_VERTEXAI` 設定為 `1` 時，需要提供您的 Google Cloud 區域（例如 `us-central1`）。
*   `ROOT_AGENT_MODEL`: 指定主要代理程式所使用的 LLM 模型名稱，例如 `'gemini-2.5-flash'`。

## 6. 故障排除

在使用 MLE-STAR 代理程式時，您可能會遇到一些問題。以下是一些常見問題及其解決方案：

*   **ImportError 或依賴問題：**
    *   **錯誤訊息範例：** `ImportError: cannot import name 'Agent' from 'google.adk.agents` 或其他關於模組找不到的錯誤。
    *   **解決方案：** 確保您已正確安裝所有專案依賴。請按照「開發環境部署」章節的說明，使用 `poetry install` 安裝依賴，並在虛擬環境中執行。

*   **環境變數未設定或設定錯誤：**
    *   **錯誤訊息範例：** 代理程式報告無法初始化模型，或使用錯誤的模型後端。
    *   **解決方案：** 檢查您的 `.env` 檔案是否已正確配置所有必要的環境變數，特別是 `GOOGLE_GENAI_USE_VERTEXAI`、`GOOGLE_API_KEY`（或 GCP 相關變數）和 `ROOT_AGENT_MODEL`。請參考「環境變數設定」章節。

*   **LLM 訪問權限不足：**
    *   **錯誤訊息範例：** 代理程式在呼叫 LLM 時遇到權限錯誤 (e.g., `403 Permission Denied`)。
    *   **解決方案：**
        *   如果您使用 Google Gemini API，請確認您的 `GOOGLE_API_KEY` 是有效的。
        *   如果您使用 Vertex AI，請確認您的 GCP 專案已啟用相關 API，並且您的服務帳戶或用戶帳戶具有足夠的權限來訪問 Vertex AI 模型。

*   **代理程式執行超時：**
    *   **錯誤訊息範例：** 代理程式在執行過程中停止，並顯示超時相關的錯誤訊息。
    *   **解決方案：** 代理程式的 `exec_timeout` 參數可能過短。您可以考慮增加 `machine_learning_engineering/shared_libraries/config.py` 中的 `exec_timeout` 值，以給予代理程式更多的時間來完成任務。

*   **無效的任務提示：**
    *   **錯誤訊息範例：** 代理程式無法理解或處理提供的任務提示。
    *   **解決方案：** 嘗試使用更明確、具體的任務提示。例如，指定資料集名稱 (`titanic` 或 `california-housing-prices`)。

## 7. 範例與截圖

*   **範例使用情境：**
    *   **Titanic 任務：** 您可以透過執行 `poetry run python run_task.py "Please solve the titanic task"` 來啟動代理程式，讓它嘗試解決 Kaggle Titanic 生存預測任務。代理程式會自動下載資料、建立模型、訓練並產生提交檔案。
    *   **California Housing Prices 任務：** 類似地，執行 `poetry run python run_task.py "Solve the california-housing-prices task"` 將會啟動代理程式來處理加州房屋價格預測任務。

*   **圖片與截圖：**
    由於本說明文件無法直接生成動態圖片，所有範例結果和代理程式執行流程的視覺化（例如，代理程式的思維鏈、生成的程式碼截圖、最終提交結果的圖表等）目前以文字描述替代。未來，這些部分將會補充具體的截圖或示意圖，以提升閱讀體驗和理解度。

*   **代理程式輸出：**
    代理程式的執行結果和中間步驟日誌將會輸出到終端機，並在 `machine_learning_engineering/workspace/<task_name>/` 目錄下生成 `final_state.json` 及其他相關檔案。建議查閱這些檔案以理解代理程式的決策過程和結果。

