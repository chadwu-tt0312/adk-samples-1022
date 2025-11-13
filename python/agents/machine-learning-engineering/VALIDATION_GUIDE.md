# final_solution.py 驗證指南

## 問題 1：如何驗證 final_solution.py 是否能輸入 test.csv 得到模型及預測結果？

### 方法一：使用驗證腳本（推薦）

已建立自動化驗證腳本 `validate_final_solution.py`，可以自動檢查並執行驗證：

```bash
# 驗證 Titanic 任務的 final_solution.py
python validate_final_solution.py \
  --solution-path machine_learning_engineering/workspace/Titanic/ensemble/final_solution.py

# 驗證 California Housing 任務的 final_solution.py
python validate_final_solution.py \
  --solution-path machine_learning_engineering/workspace/california-housing-prices/ensemble/final_solution.py

# 只檢查結構，不執行程式碼
python validate_final_solution.py \
  --solution-path workspace/Titanic/ensemble/final_solution.py \
  --check-only
```

### 驗證腳本功能

驗證腳本會執行以下檢查：

1. **結構檢查**：
   - ✅ 確認 `final_solution.py` 存在
   - ✅ 確認 `input/` 目錄存在
   - ✅ 確認 `input/test.csv` 存在
   - ✅ 確認 `input/train.csv` 存在
   - ✅ 檢查程式碼是否包含讀取 `test.csv` 的邏輯
   - ✅ 檢查程式碼是否包含預測相關程式碼
   - ✅ 檢查程式碼是否包含輸出 submission 的邏輯

2. **執行驗證**：
   - ✅ 執行 `final_solution.py`
   - ✅ 確認執行成功（無錯誤）
   - ✅ 確認模型已訓練
   - ✅ 確認已產生預測結果
   - ✅ 確認 `final/submission.csv` 已產生
   - ✅ 驗證 `submission.csv` 格式正確

### 方法二：手動驗證

如果不想使用驗證腳本，可以手動執行以下步驟：

#### 步驟 1：檢查檔案結構

```bash
cd machine_learning_engineering/workspace/Titanic/ensemble

# 確認必要檔案存在
ls -la final_solution.py
ls -la input/train.csv
ls -la input/test.csv
```

#### 步驟 2：執行 final_solution.py

```bash
python final_solution.py
```

#### 步驟 3：檢查輸出

```bash
# 確認 submission.csv 已產生
ls -la final/submission.csv

# 檢查 submission.csv 內容
head final/submission.csv
```

#### 步驟 4：驗證預測結果格式

```python
import pandas as pd

# 讀取 submission.csv
submission = pd.read_csv('final/submission.csv')

# 檢查格式
print(f"行數：{len(submission)}")
print(f"欄位：{submission.columns.tolist()}")
print(f"\n前 5 筆預測：")
print(submission.head())
```

### 預期輸出

成功執行後，應該會看到：

1. **執行過程輸出**：
   ```
   Final Validation Performance: 0.8156
   ```

2. **產生的檔案**：
   - `final/submission.csv`：包含預測結果的 CSV 檔案

3. **submission.csv 格式**：
   - 應包含 `PassengerId` 和預測欄位（如 `Survived`）
   - 行數應與 `test.csv` 相同

### 常見問題

#### 問題 1：找不到 test.csv
**解決方案**：確認 `input/test.csv` 存在於 `final_solution.py` 的同一層目錄下

#### 問題 2：執行時出現 ImportError
**解決方案**：安裝必要的套件
```bash
pip install pandas numpy xgboost scikit-learn
```

#### 問題 3：預測結果為空
**解決方案**：檢查程式碼中的預測邏輯是否正確執行

---

## 問題 1.5：final_solution.py 只輸入 test.csv，不輸入 train.csv，能得到模型及預測結果嗎？

### 簡短答案

**❌ 不行。`train.csv` 是絕對必要的，無法只使用 `test.csv` 來訓練模型和產生預測結果。**

### 詳細說明

從 `final_solution.py` 的程式碼分析可以看出，`train.csv` 在整個流程中扮演多個關鍵角色：

#### 1. **訓練模型（最關鍵）**

```10:40:machine_learning_engineering/workspace/Titanic/ensemble/final_solution.py
train_df = pd.read_csv('./input/train.csv')
# ... 資料預處理 ...
X = train_df.drop('Survived', axis=1)
y = train_df['Survived']
```

- **第 10 行**：必須讀取 `train.csv`
- **第 38-40 行**：從 `train.csv` 提取特徵（X）和目標值（y）
- **第 72 行**：使用 X 和 y 訓練模型 `final_xgb_clf.fit(X, y)`

**沒有 `train.csv`，就沒有標記數據（labeled data），無法訓練模型。**

#### 2. **計算預處理統計值**

```12:18:machine_learning_engineering/workspace/Titanic/ensemble/final_solution.py
# --- Store imputation values from the training data for consistent preprocessing of test data ---
# Calculate median age from training data
median_age = train_df['Age'].median()
# Calculate mode embarked from training data
mode_embarked = train_df['Embarked'].mode()[0]
# Calculate median fare from training data (test data is known to have missing Fares)
median_fare = train_df['Fare'].median()
```

這些統計值用於處理 `test.csv` 的缺失值：

```84:91:machine_learning_engineering/workspace/Titanic/ensemble/final_solution.py
# Fill missing Age values with the median from the training data
test_df['Age'].fillna(median_age, inplace=True)

# Fill missing Embarked values with the mode from the training data
test_df['Embarked'].fillna(mode_embarked, inplace=True)

# Fill missing Fare values with the median from the training data (as test data has missing Fares)
test_df['Fare'].fillna(median_fare, inplace=True)
```

**為什麼要用訓練數據的統計值？**
- 避免資料洩漏（Data Leakage）：如果使用測試數據的統計值，會讓模型「看到」測試數據的資訊
- 確保一致性：訓練和測試使用相同的預處理參數

#### 3. **確定特徵欄位和順序**

```99:110:machine_learning_engineering/workspace/Titanic/ensemble/final_solution.py
# Align columns between training and test sets to ensure consistency
# This handles potential discrepancies in one-hot encoded columns if
# not all categories are present in both train and test.
missing_cols_in_test = set(X.columns) - set(test_df.columns)
for c in missing_cols_in_test:
    test_df[c] = 0 # Add missing columns to test_df and fill with 0

extra_cols_in_test = set(test_df.columns) - set(X.columns)
if len(extra_cols_in_test) > 0:
    test_df.drop(columns=list(extra_cols_in_test), inplace=True) # Drop extra columns from test_df

test_df = test_df[X.columns] # Ensure the order of columns is the same as in training data
```

**第 110 行**：使用訓練數據的欄位順序 `X.columns` 來對齊測試數據。

### 如果沒有 train.csv 會發生什麼？

如果嘗試只使用 `test.csv` 執行 `final_solution.py`，會在**第 10 行**就失敗：

```python
train_df = pd.read_csv('./input/train.csv')
# FileNotFoundError: [Errno 2] No such file or directory: './input/train.csv'
```

### 機器學習的基本原理

這反映了機器學習的基本原理：

1. **監督式學習（Supervised Learning）**需要：
   - **訓練數據（Training Data）**：包含特徵和正確答案（標籤）
   - **測試數據（Test Data）**：只包含特徵，需要預測答案

2. **訓練階段**：
   - 模型從訓練數據中學習「特徵 → 答案」的對應關係
   - 沒有訓練數據，模型無法學習

3. **預測階段**：
   - 使用訓練好的模型對測試數據進行預測
   - 沒有訓練好的模型，無法進行預測

### 總結

| 檔案 | 用途 | 是否必要 |
|------|------|----------|
| `train.csv` | 訓練模型、計算預處理參數、確定特徵結構 | ✅ **絕對必要** |
| `test.csv` | 進行預測、產生 submission | ✅ **必要** |

**結論**：`train.csv` 和 `test.csv` 都是必要的，缺一不可。

---

## 問題 2：MLE-STAR 可以處理影像型的任務嗎？

### 簡短答案

**目前版本主要專注於表格數據（Tabular Data）任務，未明確支援影像型任務。**

### 詳細說明

#### 1. 目前支援的任務類型

根據文件與程式碼，MLE-STAR 目前主要支援：

- ✅ **表格數據分類任務**（Tabular Classification）
  - 範例：Titanic 生存預測
  - 使用的模型：XGBoost、LightGBM、RandomForest 等

- ✅ **表格數據迴歸任務**（Tabular Regression）
  - 範例：California Housing Prices 房價預測
  - 使用的模型：CatBoost、LightGBM、XGBoost 等

#### 2. 技術限制

從程式碼範例可以看出，MLE-STAR 目前使用的模型都是針對表格數據設計的：

- **LightGBM**：梯度提升決策樹，主要用於表格數據
- **XGBoost**：梯度提升框架，主要用於表格數據
- **CatBoost**：梯度提升框架，主要用於表格數據
- **RandomForest**：隨機森林，主要用於表格數據

這些模型**不適合直接處理影像數據**，因為：
- 影像數據是 2D/3D 陣列（像素值）
- 需要卷積神經網路（CNN）等深度學習模型
- 需要不同的資料預處理流程（影像增強、正規化等）

#### 3. 理論上的可能性

雖然目前版本未明確支援，但從架構來看，MLE-STAR **理論上可能可以擴展**到影像任務，因為：

1. **架構彈性**：
   - MLE-STAR 使用 LLM 搜尋最佳實踐並生成程式碼
   - 如果 LLM 能找到影像分類的範例程式碼（如使用 ResNet、EfficientNet 等 CNN 模型），理論上可以生成對應的程式碼

2. **自動化流程**：
   - 資料清理、特徵工程、模型選擇、超參數調整等流程在影像任務中同樣適用
   - 只是具體的實作方式不同

3. **需要調整的部分**：
   - 資料載入方式（從 CSV 改為影像檔案或影像資料集）
   - 模型選擇（從樹模型改為 CNN 模型）
   - 特徵工程（從表格特徵改為影像增強、資料擴增等）

#### 4. 實際建議

如果您需要處理影像型任務，建議：

1. **檢查最新版本**：
   - 查看 MLE-STAR 的最新文件或 GitHub Issues，確認是否有影像任務的支援

2. **嘗試自訂任務**：
   - 可以嘗試在 `tasks/` 目錄下建立影像任務的資料夾
   - 提供 `task_description.txt` 描述影像分類任務
   - 但需要確保資料格式符合系統預期

3. **使用其他工具**：
   - 對於影像任務，可以考慮使用專門的 AutoML 工具，如：
     - AutoKeras
     - Google Cloud AutoML Vision
     - H2O.ai

### 總結

| 項目 | 狀態 |
|------|------|
| 表格數據分類 | ✅ 支援 |
| 表格數據迴歸 | ✅ 支援 |
| 影像分類 | ❓ 未明確支援，可能需要自訂 |
| 影像物件偵測 | ❌ 不支援 |
| 自然語言處理 | ❓ 未明確支援 |

**建議**：如果您的任務是影像相關，建議先查看 MLE-STAR 的最新文件或聯絡專案維護者確認支援情況。

