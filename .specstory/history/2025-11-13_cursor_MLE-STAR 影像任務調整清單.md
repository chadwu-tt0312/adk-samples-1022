# MLE-STAR 影像任務調整清單
_Exported on 2025/11/13 at 13:45:46 [GMT+8] from Cursor (2.0.75)_

---

**User**

MLE-STAR 如果要處理影像型的任務。需要做哪些變更?

請列出所有需要調整的TODO list。並記錄下來。但不要實作。

---

**Cursor**


檢視 MLE-STAR 的結構與實作，以列出處理影像任務所需的調整項目。



檢視關鍵程式碼檔案，了解系統架構：



檢視核心程式碼結構，了解系統如何運作：



檢視主要程式碼結構，確認所有需要調整的部分：



建立處理影像任務所需的調整項目 TODO list：



建立文件記錄這些變更項目：


```markdown
# MLE-STAR 影像任務支援變更清單

本文檔列出 MLE-STAR 系統要支援影像型任務所需的所有變更項目。

## 概述

MLE-STAR 目前主要專注於表格數據（Tabular Data）任務，使用樹模型（XGBoost, LightGBM）進行分類和迴歸。要支援影像任務，需要進行以下類別的調整：

1. **資料處理層面**：從 CSV 表格改為影像檔案
2. **模型層面**：從樹模型改為深度學習模型（CNN）
3. **訓練流程層面**：從簡單 fit() 改為深度學習訓練迴圈
4. **Agent 層面**：調整 prompts 和搜尋策略
5. **基礎設施層面**：依賴套件、硬體支援等

---

## 變更項目清單

### 1. 資料載入與結構

#### 1.1 資料載入模組
- **目前狀態**：使用 `pd.read_csv()` 讀取 CSV 檔案
- **需要變更**：
  - 改為使用 PIL/Pillow 或 OpenCV 載入影像檔案
  - 支援常見影像格式（JPG, PNG, JPEG）
  - 建立影像載入函數，處理批次載入
- **影響範圍**：所有讀取資料的程式碼（`final_solution.py`, `train*.py`）

#### 1.2 資料結構
- **目前狀態**：使用 pandas DataFrame 儲存表格資料
- **需要變更**：
  - 改為使用 numpy array 或 PyTorch/TensorFlow tensor 儲存影像資料
  - 支援批次處理（batch processing）
  - 建立資料生成器（DataLoader/ImageDataGenerator）用於訓練
- **影響範圍**：資料處理流程、模型輸入格式

#### 1.3 目錄結構
- **目前狀態**：`input/train.csv`, `input/test.csv`
- **需要變更**：
  - 改為影像目錄結構（如 `input/train/`, `input/test/`）
  - 支援按類別分類的目錄結構（如 `input/train/class1/`, `input/train/class2/`）
  - 或使用標籤檔案（如 CSV 檔案對應影像路徑和標籤）
- **影響範圍**：資料載入邏輯、驗證腳本

---

### 2. 模型與訓練

#### 2.1 模型檢索 Agent (A_retriever)
- **目前狀態**：搜尋表格模型（LightGBM, XGBoost, RandomForest）
- **需要變更**：
  - 調整搜尋關鍵字生成邏輯
  - 搜尋影像分類模型（ResNet, EfficientNet, Vision Transformer, MobileNet）
  - 解析搜尋結果時提取 CNN 架構和預訓練模型資訊
- **影響範圍**：`sub_agents/initialization/agent.py`

#### 2.2 模型選擇
- **目前狀態**：使用樹模型（XGBoost, LightGBM, CatBoost, RandomForest）
- **需要變更**：
  - 改為深度學習模型（CNN, ResNet, EfficientNet, Vision Transformer）
  - 支援 PyTorch 或 TensorFlow/Keras 框架
  - 支援預訓練模型（pretrained models）的使用
- **影響範圍**：模型初始化、模型定義程式碼生成

#### 2.3 訓練迴圈
- **目前狀態**：簡單的 `model.fit(X, y)` 呼叫
- **需要變更**：
  - 實作完整的深度學習訓練迴圈
  - 包含 epochs、batch size、learning rate scheduling
  - 加入 early stopping、checkpoint saving
  - 支援驗證集評估和指標計算
- **影響範圍**：所有訓練程式碼（`train*.py`, `final_solution.py`）

#### 2.4 遷移學習（Transfer Learning）
- **目前狀態**：不適用
- **需要變更**：
  - 支援使用 ImageNet 預訓練的模型（ResNet, EfficientNet 等）
  - 實作 fine-tuning 策略（凍結部分層、調整學習率等）
- **影響範圍**：模型定義、訓練策略

---

### 3. 資料預處理與特徵工程

#### 3.1 預處理流程
- **目前狀態**：處理缺失值、類別編碼、數值標準化
- **需要變更**：
  - 影像 resize（統一尺寸）
  - 影像正規化（normalization，如除以 255 或使用 ImageNet 統計值）
  - 通道轉換（RGB/BGR）
  - Tensor 轉換（numpy array → PyTorch tensor 或 TensorFlow tensor）
- **影響範圍**：資料預處理程式碼

#### 3.2 特徵工程 → 資料擴增（Data Augmentation）
- **目前狀態**：表格特徵工程（組合特徵、數學變換）
- **需要變更**：
  - 改為影像資料擴增（data augmentation）
  - 支援旋轉、翻轉、縮放、亮度調整、對比度調整等
  - 在訓練時動態應用（而非預處理階段）
  - 建立可配置的擴增策略
- **影響範圍**：特徵工程程式碼、訓練流程

---

### 4. Agent 與 Prompts

#### 4.1 Agent Prompts 調整
- **需要調整的 Agents**：
  - `A_retriever`：搜尋策略和關鍵字生成
  - `A_abl`：消融研究的區塊識別
  - `A_extractor`：關鍵區塊提取邏輯
  - `A_planner`：優化計劃生成
  - `A_ensemble`：整合策略
- **變更內容**：
  - 加入影像任務相關的指引和範例
  - 調整程式碼生成模板，從表格處理改為影像處理
  - 更新最佳實踐範例
- **影響範圍**：`sub_agents/*/agent.py`, `prompt.py`

#### 4.2 消融研究（Ablation Study）
- **目前狀態**：測試表格特徵工程區塊的影響
- **需要變更**：
  - 改為測試影像增強策略、模型架構組件、訓練策略等
  - 識別關鍵的資料擴增方法、模型層級、超參數等
- **影響範圍**：`sub_agents/refinement/agent.py` (A_abl)

#### 4.3 模型整合（Ensemble）
- **目前狀態**：表格模型的預測平均（簡單平均、加權平均）
- **需要變更**：
  - 改為深度學習模型的整合策略
  - 支援模型平均、stacking、blending
  - 處理不同架構模型的整合
- **影響範圍**：`sub_agents/ensemble/agent.py`

---

### 5. 驗證與評估

#### 5.1 驗證腳本
- **檔案**：`validate_final_solution.py`
- **目前狀態**：檢查 CSV 檔案存在、格式驗證
- **需要變更**：
  - 檢查影像目錄結構
  - 驗證影像檔案格式和完整性
  - 確認資料載入邏輯正確
- **影響範圍**：驗證腳本

#### 5.2 評估指標
- **目前狀態**：表格任務的指標（accuracy, RMSE）
- **需要變更**：
  - 確認影像任務的評估指標（accuracy, F1-score, top-k accuracy 等）
  - 調整驗證流程中的指標計算
  - 確保輸出格式符合要求
- **影響範圍**：評估邏輯、驗證流程

#### 5.3 輸出格式
- **目前狀態**：CSV 格式的 submission（如 `PassengerId,Survived`）
- **需要變更**：
  - 確認影像任務的 submission 格式（可能仍為 CSV，但欄位可能不同）
  - 驗證輸出格式是否符合 Kaggle 影像競賽要求
- **影響範圍**：submission 生成邏輯

---

### 6. 基礎設施

#### 6.1 依賴套件
- **檔案**：`pyproject.toml`
- **目前狀態**：pandas, numpy, scikit-learn, xgboost, lightgbm 等
- **需要變更**：
  - 加入 PyTorch 或 TensorFlow
  - 加入 torchvision 或 tensorflow.keras
  - 加入 PIL/Pillow
  - 加入 opencv-python（可選）
- **影響範圍**：專案依賴配置

#### 6.2 硬體需求
- **目前狀態**：CPU 即可執行
- **需要變更**：
  - 加入 GPU 支援檢查和配置
  - 支援 CUDA、cuDNN（如使用 PyTorch/TensorFlow GPU 版本）
  - 在程式碼中檢查 GPU 可用性並自動選擇設備
- **影響範圍**：訓練程式碼、環境配置

---

### 7. 其他

#### 7.1 影像元資料處理
- **目前狀態**：不適用
- **需要變更**：
  - 如果需要處理影像的額外資訊（檔案名稱、標籤檔案、bounding box 等）
  - 建立對應的處理邏輯和資料結構
- **影響範圍**：資料載入模組（視任務需求而定）

#### 7.2 任務描述格式
- **檔案**：`task_description.txt`
- **目前狀態**：描述表格任務
- **需要變更**：
  - 確認任務描述格式是否需要調整以支援影像任務
  - 可能需要加入影像相關的元資訊（影像尺寸、類別數量等）
- **影響範圍**：任務描述範本、解析邏輯

---

## 變更優先級建議

### 高優先級（核心功能）
1. 資料載入模組（1.1, 1.2, 1.3）
2. 模型選擇與訓練迴圈（2.1, 2.2, 2.3）
3. 預處理流程（3.1）
4. Agent Prompts 調整（4.1）
5. 依賴套件（6.1）

### 中優先級（功能增強）
6. 資料擴增（3.2）
7. 遷移學習（2.4）
8. 消融研究調整（4.2）
9. 驗證腳本（5.1）
10. 硬體支援（6.2）

### 低優先級（優化與擴展）
11. 模型整合策略（4.3）
12. 評估指標調整（5.2, 5.3）
13. 影像元資料處理（7.1, 7.2）

---

## 注意事項

1. **向後相容性**：建議保留對表格任務的支援，透過任務類型自動選擇對應的處理流程
2. **測試**：每個變更項目都需要對應的測試案例
3. **文件**：更新相關文件，說明影像任務的使用方式
4. **效能**：影像任務通常需要更多計算資源，需要考慮訓練時間和資源限制

---

## 參考資源

- PyTorch 影像分類範例
- TensorFlow/Keras 影像分類範例
- Kaggle 影像競賽最佳實踐
- 常見的影像資料擴增方法
- 預訓練模型使用指南（ResNet, EfficientNet 等）

```


已建立 MLE-STAR 支援影像任務的變更清單。

## 已完成的工作

1. **建立 TODO list**：20 個變更項目，涵蓋：
   - 資料載入與結構（3 項）
   - 模型與訓練（4 項）
   - 資料預處理（2 項）
   - Agent 與 Prompts（3 項）
   - 驗證與評估（3 項）
   - 基礎設施（2 項）
   - 其他（3 項）

2. **建立文件**：`IMAGE_TASK_MIGRATION_TODO.md`，包含：
   - 各變更項目的說明
   - 目前狀態與需要變更的內容
   - 影響範圍
   - 優先級建議
   - 注意事項

## 主要變更類別

1. **資料層面**：從 CSV 表格改為影像檔案載入
2. **模型層面**：從樹模型（XGBoost, LightGBM）改為深度學習模型（CNN, ResNet, EfficientNet）
3. **訓練層面**：從簡單 `fit()` 改為完整訓練迴圈
4. **Agent 層面**：調整所有 Agent 的 prompts 和搜尋策略
5. **基礎設施**：加入深度學習相關套件和 GPU 支援

所有項目已記錄在 TODO list 中，並已建立文件。目前尚未實作任何變更，僅列出需要調整的項目。

