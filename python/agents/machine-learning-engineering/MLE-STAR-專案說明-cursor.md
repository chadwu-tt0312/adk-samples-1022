# MLE-STAR 專案說明文件

> **重要說明**：本文檔中，**「LLM」**（Large Language Model，大型語言模型）指的是用於生成程式碼和決策的人工智慧模型（如 Gemini、GPT 等），而**「機器學習模型」**（或簡稱「模型」）指的是用於預測的統計模型（如 LightGBM、XGBoost 等）。兩者是完全不同的概念。

## 1. 專案用途

MLE-STAR（Machine Learning Engineering STAR）是一個**自動化機器學習工程代理系統**，用於自動建立和優化機器學習模型。

### 核心功能

這個專案的主要目的是**自動化完成機器學習競賽的完整流程**，從資料處理到模型訓練，再到最終提交。即使你不懂機器學習，系統也能自動：

1. **搜尋最佳機器學習模型**：透過網路搜尋找到適合當前任務的機器學習模型（如 LightGBM、XGBoost 等）
2. **自動生成程式碼**：LLM 根據找到的模型範例，自動產生完整的 Python 訓練程式
3. **找出關鍵改進點**：透過 Ablation Study（消融研究）找出對機器學習模型 Performance（效能）影響最大的程式碼區塊
4. **迭代優化**：LLM 針對關鍵區塊進行多輪改進，逐步提升機器學習模型的預測 Accuracy（準確度）
5. **整合多個機器學習模型**：將多個機器學習模型組合 Ensemble（整合）以獲得更好的預測結果

### 實際應用場景

以本專案的範例「加州房價預測」為例：
- **任務**：根據地區的人口、收入、房屋年齡等 Feature（特徵），預測該地區的房價中位數
- **系統自動完成**：Data Cleaning（資料清理）、Feature Engineering（特徵工程）、Model Selection（模型選擇）、Hyperparameter Tuning（參數調整）、Ensemble（模型整合）等所有步驟
- **最終產出**：一個可以直接提交到 Kaggle 競賽的預測結果檔案

---

## 2. 專案的 Input/Output

### 輸入（Input）

#### 2.1 任務描述檔案（`task_description.txt`）
- **位置**：`tasks/california-housing-prices/task_description.txt`
- **內容**：
  - 任務目標 `Task`（例如：預測房屋中位數`median_house_value`）
  - Evaluation Metric（評估指標）`Metric`（例如：Root Mean Squared Error（RMSE，均方根誤差）`root_mean_squared_error`）
  - 提交格式要求 `Submission Format`
- **用途**：告訴系統要解決什麼問題、如何評估好壞、輸出格式是什麼

#### 2.2 Training Data（訓練資料）（`train.csv`）
- **位置**：`tasks/california-housing-prices/train.csv`
- **內容**：包含 Feature（特徵）欄位（如經緯度、人口、收入等）和 Target Value（目標值）（房價中位數）
  - 經度、緯度、房屋中位數年齡、房間總數、臥室總數、人口、家庭戶數、收入中位數、房價中位數
- **用途**：用於訓練模型和驗證模型 Performance（效能）

#### 2.3 Test Data（測試資料）（`test.csv`）
- **位置**：`tasks/california-housing-prices/test.csv`
- **內容**：只包含 Feature（特徵）欄位，沒有 Target Value（目標值）
- **用途**：用於產生最終的預測結果

#### 2.4 配置參數
- **位置**：程式碼中的配置設定（`shared_libraries/config.py`）
- **內容**：
  - 使用的 LLM 模型（如 `gemini-2.5-flash`）
  - 要嘗試的機器學習模型候選數量（如 2 個）
  - 優化輪數（outer loop、inner loop）
- **用途**：控制系統的行為和資源使用
- **注意**：這裡的「模型候選」指的是**機器學習模型**（如 LightGBM、XGBoost），不是 LLM

### 輸出（Output）

#### 2.5 初始解決方案程式碼
- **位置**：`workspace/california-housing-prices/{solution_id}/init_code_*.py`
- **內容**：根據網路搜尋結果產生的初始 Python 訓練程式
- **用途**：作為後續優化的起點

#### 2.6 優化後的訓練程式碼
- **位置**：`workspace/california-housing-prices/{solution_id}/train*.py`
- **內容**：經過多輪優化改進的完整訓練程式
- **用途**：實際用於產生預測的程式碼

#### 2.7 消融研究程式碼
- **位置**：`workspace/california-housing-prices/{solution_id}/ablation_*.py`
- **內容**：用於測試不同組件影響的實驗程式碼
- **用途**：找出對效能影響最大的程式碼區塊

#### 2.8 整合模型程式碼
- **位置**：`workspace/california-housing-prices/ensemble/ensemble*.py`
- **內容**：將多個模型組合的程式碼
- **用途**：透過模型整合提升預測準確度

#### 2.9 最終提交檔案（`submission.csv`）
- **位置**：`workspace/california-housing-prices/ensemble/final/submission.csv`
- **內容**：對測試資料的預測結果，格式符合競賽要求
- **用途**：可以直接提交到 Kaggle 競賽的結果檔案

#### 2.10 狀態記錄檔案（`final_state.json`）
- **位置**：`workspace/california-housing-prices/final_state.json`
- **內容**：記錄整個執行過程的所有狀態、中間結果、評估分數等
- **用途**：用於追蹤執行歷程和除錯

### 最終產出成果及其作用

1. **完整的訓練程式碼**：可以獨立執行的 Python 程式，包含資料處理、機器學習模型訓練、預測產生等完整流程
2. **優化的機器學習模型**：經過多輪改進的機器學習模型，通常比初始版本有更好的預測準確度
3. **提交檔案**：符合競賽格式的預測結果，可直接用於提交
4. **執行記錄**：詳細記錄了系統如何從初始方案逐步優化到最終方案

---

## 3. 專案使用的 LLM（大型語言模型）

> **重要區分**：本節說明的是**LLM**（用於生成程式碼和決策），不是機器學習模型（用於預測）。

### 3.1 使用的 LLM 模型

專案使用 **Google Gemini 系列模型**，主要有兩種選擇：

1. **Gemini-2.5-Flash**（預設）
   - 速度較快，成本較低
   - 適合快速迭代和測試
   - 在本專案中，使用此模型可達到 43.9% 的獎牌率

2. **Gemini-2.5-Pro**
   - 效能更強，準確度更高
   - 適合追求最佳結果
   - 可達到 63.6% 的獎牌率

### 3.2 LLM 在各階段的使用

#### 階段 (a)：初始化（Initialization）
- **使用的 Agent**：`A_retriever`（檢索代理）
- **LLM 的作用**：
  1. 根據任務描述，生成搜尋查詢（如「What models are effective for tabular regression?」）
  2. 解析網路搜尋結果，提取模型名稱和範例程式碼
  3. 整合多個候選模型，生成初始解決方案
- **產生的結果**：
  - 機器學習模型候選清單（如 LightGBM、XGBoost）
  - 每個機器學習模型的範例程式碼
  - 整合後的初始 Python 訓練程式

#### 階段 (b)：程式碼區塊提取（Code Block Extraction）
- **使用的 Agent**：`A_abl`（消融研究代理）、`A_extractor`（提取代理）
- **LLM 的作用**：
  1. `A_abl`：生成消融研究程式碼，測試移除不同組件對效能的影響
  2. `A_extractor`：分析消融研究結果，判斷哪個程式碼區塊影響最大
- **產生的結果**：
  - 消融研究程式碼（`ablation_*.py`）
  - 消融研究執行結果（各組件的效能影響）
  - 被識別出的關鍵程式碼區塊

#### 階段 (c)：程式碼區塊優化（Code Block Refinement）
- **使用的 Agent**：`A_planner`（規劃代理）
- **LLM 的作用**：
  1. 根據前次實驗的反饋，提出多個改進計劃
  2. 評估每個計劃的預期效果
  3. 選擇較佳計劃並實作
  4. 根據執行結果更新策略，進行下一輪優化
- **產生的結果**：
  - 多個改進計劃（Plan 1, Plan 2, ..., Plan k）
  - 每個計劃的實作程式碼
  - 優化後的程式碼區塊

#### 整合階段（Ensemble）
- **使用的 Agent**：Ensemble Agent
- **LLM 的作用**：
  1. 提出整合策略（如簡單平均、加權平均等）
  2. 根據各模型的效能計算權重
  3. 生成整合程式碼
- **產生的結果**：
  - 整合策略計劃
  - 整合程式碼（`ensemble*.py`）
  - 最終的整合預測結果

### 3.3 LLM 產生的具體結果範例

從 `final_state.json` 可以看到：

1. **機器學習模型檢索結果**：
   ```json
   "init_2_model_1": {
     "model_name": "LightGBM Regressor",
     "example_code": "...完整的 Python 程式碼...",
     "model_description": "...模型說明..."
   }
   ```
   > 注意：這裡的 "model" 指的是**機器學習模型**（LightGBM），不是 LLM。

2. **消融研究結果**：
   ```
   Baseline: RMSE = 61439.0947
   No Feature Engineering: RMSE = 62724.5419
   → 結論：特徵工程對效能影響最大
   ```

3. **優化計劃**：
   - Plan 1：改進特徵工程策略
   - Plan 2：調整資料預處理方法
   - 系統選擇效果較好的計劃實作

---

## 4. 與 Kaggle 的關係

### 4.1 California Housing Prices 資料集

Kaggle 上的 "California Housing Prices" 是一個**經典的機器學習競賽資料集**，來源於 1990 年美國人口普查資料。

### 4.2 與本專案的關係

1. **資料集來源**：
   - 本專案使用的 `train.csv` 和 `test.csv` 就是來自這個 Kaggle 資料集
   - 任務格式也遵循 Kaggle 競賽的標準格式

2. **任務類型**：
   - **問題類型**：Regression（迴歸問題）
   - **目標**：預測加州地區的房價中位數
   - **評估指標**：RMSE（Root Mean Squared Error，均方根誤差）

3. **專案定位**：
   - 本專案是為了**自動化完成類似 Kaggle 競賽的完整流程**
   - 系統設計目標是在 MLE-Bench-Lite 基準測試中達到競賽水準的表現
   - 根據論文，使用 Gemini-2.5-Pro 可達到 63.6% 的獎牌率

4. **實際應用**：
   - 如果你有一個新的 Kaggle 競賽任務，可以：
     1. 將任務描述和資料放入 `tasks/` 目錄
     2. 執行 MLE-STAR 系統
     3. 系統會自動產生可提交的結果檔案

### 4.3 資料集特徵

根據 `task_description.txt`，資料包含以下特徵：
- `longitude`、`latitude`：地理位置
- `housing_median_age`：房屋年齡中位數
- `total_rooms`、`total_bedrooms`：房間數
- `population`、`households`：人口和家庭數
- `median_income`：收入中位數
- **目標**：`median_house_value`（房價中位數）

---

## 5. 基礎概念說明

### 5.1 什麼是「機器學習模型」？

**機器學習模型**（Machine Learning Model）是一個數學函數或演算法，用於從資料中學習規律，並對新資料進行預測。

#### 簡單比喻
想像機器學習模型是一個「學生」：
- **訓練階段**：給學生看很多「題目」（特徵）和「答案」（目標值），讓學生學習規律
- **預測階段**：給學生新的「題目」（只有特徵），讓學生根據學到的規律「答題」（預測）

#### 實際例子
在加州房價預測任務中：
- **輸入**：地區的人口、收入、房屋年齡等特徵
- **機器學習模型**：學習這些特徵與房價的關係
- **輸出**：預測該地區的房價

#### 常見的機器學習模型類型
1. **Regression Model（迴歸模型）**：預測連續數值（如房價、溫度）
2. **Classification Model（分類模型）**：預測類別（如是否為垃圾郵件、圖片中的物體）
3. **Clustering Model（聚類模型）**：將資料分組（Unsupervised Learning，無監督學習）

### 5.2 什麼是「LightGBM」、「XGBoost」、「RandomForest」？

這三種都是**機器學習模型**（不是 LLM），屬於 Gradient Boosting（梯度提升）或 Random Forest（隨機森林）類型的演算法。

#### LightGBM（Light Gradient Boosting Machine）
- **類型**：Gradient Boosting Decision Tree（GBDT，梯度提升決策樹）
- **特點**：
  - 訓練速度快
  - 記憶體使用效率高
  - 適合處理大型資料集
  - 在表格資料（Tabular Data）上表現優異
- **適用場景**：Kaggle 競賽、結構化資料預測
- **官方網站**：<https://lightgbm.readthedocs.io/>

#### XGBoost（eXtreme Gradient Boosting）
- **類型**：Gradient Boosting Decision Tree（GBDT，梯度提升決策樹）
- **特點**：
  - 準確度高
  - 支援多種 Objective Function（目標函數）
  - 有 Regularization（正則化）機制，不易 Overfitting（過擬合）
  - 在競賽中受歡迎
- **適用場景**：競賽、需要高準確度的場景
- **官方網站**：<https://xgboost.readthedocs.io/>

#### RandomForest（隨機森林）
- **類型**：Ensemble Learning（集成學習）
- **特點**：
  - 由多棵 Decision Tree（決策樹）組成
  - 訓練速度快
  - 對 Overfitting（過擬合）有較好的抗性
  - 容易理解和解釋
- **適用場景**：需要穩定性和可解釋性的場景
- **官方網站**：<https://scikit-learn.org/stable/modules/ensemble.html#random-forests>

#### 三者比較

| 特性 | LightGBM | XGBoost | RandomForest |
|------|----------|---------|--------------|
| 速度 | 最快 | 中等 | 較快 |
| 準確度 | 高 | 很高 | 高 |
| 記憶體使用 | 低 | 中等 | 中等 |
| 參數調優難度 | 中等 | 較難 | 較易 |
| 競賽表現 | 良好 | 良好 | 良好 |

### 5.3 從哪裡可以找到「機器學習模型」與「模型範例」？

#### 機器學習模型資源

1. **官方文件與範例**
   - **LightGBM**：<https://lightgbm.readthedocs.io/en/latest/>
   - **XGBoost**：<https://xgboost.readthedocs.io/>
   - **scikit-learn**（包含 RandomForest）：<https://scikit-learn.org/stable/>
   - **CatBoost**：<https://catboost.ai/>

2. **Kaggle 競賽範例**
   - **Kaggle Learn**：<https://www.kaggle.com/learn>
   - **Kaggle Notebooks**：<https://www.kaggle.com/code>
   - 搜尋關鍵字：「tabular regression tutorial」、「lightgbm example」

3. **GitHub 資源**
   - **Awesome Machine Learning**：<https://github.com/josephmisiti/awesome-machine-learning>
   - 搜尋關鍵字：「machine learning tutorial」、「regression example」

4. **教學網站**
   - **Towards Data Science**：<https://towardsdatascience.com/>
   - **Analytics Vidhya**：<https://www.analyticsvidhya.com/>
   - **Machine Learning Mastery**：<https://machinelearningmastery.com/>

5. **Python 套件文件**
   - **scikit-learn 範例**：<https://scikit-learn.org/stable/auto_examples/>
   - **LightGBM 範例**：<https://github.com/microsoft/LightGBM/tree/master/examples>

#### 模型範例搜尋建議

在網路受限環境中，可以：
1. **使用代理搜尋**：透過 proxy 訪問上述網站
2. **離線文件**：下載官方文件（PDF 或 HTML）到本地
3. **GitHub 離線**：使用 `git clone` 下載範例程式碼（需先透過 proxy 下載）

### 5.4 初始解決方案的數量如何影響專案結果？

**初始解決方案數量**由配置參數 `num_solutions` 控制（預設為 2）。

#### 影響分析

1. **數量越多**：
   - **優點**：
     - 探索更多不同的機器學習模型組合
     - 增加找到較佳解決方案的機會
     - 在整合階段有更多選擇
   - **缺點**：
     - 執行時間明顯增加（每個解決方案都需要完整流程）
     - LLM API 呼叫次數增加（成本上升）
     - 計算資源需求增加

2. **數量越少**：
   - **優點**：
     - 執行時間短
     - 成本低
     - 資源需求少
   - **缺點**：
     - 可能錯過更好的解決方案
     - 整合效果可能較差

#### 建議設定

- **快速測試**：`num_solutions = 1`
- **一般使用**：`num_solutions = 2`（預設，平衡效果與成本）
- **追求較佳結果**：`num_solutions = 3-5`（需要更多時間和資源）

#### 實際範例

在本專案的 `final_state.json` 中，`num_solutions = 2`，產生了兩個解決方案：
- **Solution 1**：使用 LightGBM，最終 RMSE = 54243.64
- **Solution 2**：使用 RandomForest，最終 RMSE = 61439.09

整合後的最終結果 RMSE = 54243.64（選擇了較好的 Solution 1）。

### 5.5 什麼是「消融研究」（Ablation Study）？

**消融研究**（Ablation Study）是一種科學研究方法，用於了解系統中每個組件對整體效能的貢獻。

#### 簡單比喻

想像你在做一道菜，想知道哪個調料最重要：
- **完整版本**：所有調料都加，評分 8 分
- **移除鹽**：評分降到 3 分 → 鹽很重要
- **移除胡椒**：評分降到 7 分 → 胡椒影響較小
- **結論**：鹽是最關鍵的調料

#### 在機器學習中的應用

在 MLE-STAR 中，消融研究用於找出程式中哪個部分對預測準確度影響最大：

1. **完整版本**：包含所有組件（特徵工程、資料預處理、模型訓練等）
2. **移除特徵工程**：測試沒有特徵工程時的效能
3. **移除資料預處理**：測試沒有預處理時的效能
4. **比較結果**：找出移除後效能下降最多的組件

#### 實際範例

從 `final_state.json` 的消融研究結果：

```
Baseline（完整版本）: RMSE = 61439.09
移除特徵工程: RMSE = 62724.54（變差 1285.45）
移除資料預處理: RMSE = 61439.09（無影響）
```

**結論**：特徵工程對效能影響最大，應該優先優化特徵工程部分。

#### 消融研究的步驟

1. **建立基準**：執行完整版本的程式，記錄效能
2. **逐一移除組件**：每次移除一個組件，重新執行
3. **比較結果**：計算移除組件後的效能變化
4. **識別關鍵組件**：找出移除後效能下降最多的組件

### 5.6 將「多個模型組合（ensemble）以獲得更好的預測結果」。組合了哪些模型？

在本專案的範例中，整合了以下**機器學習模型**：

#### 組合的模型

根據 `final_state.json` 和 `ensemble/ensemble1.py`：

1. **LightGBM Regressor**
   - 使用 K-Fold Cross Validation（K 折交叉驗證）
   - 最終 OOF（Out-Of-Fold）RMSE：54243.64
   - 權重：0.5311（約 53%）

2. **RandomForest Regressor**
   - 使用簡單的 Train/Validation Split（訓練/驗證分割）
   - Validation RMSE（驗證 RMSE）：61439.09
   - 權重：0.4689（約 47%）

#### 整合策略

系統嘗試了兩種整合策略：

1. **策略 0（簡單平均）**：
   ```python
   ensemble_predictions = (lgbm_predictions + rf_predictions) / 2
   ```
   - 每個模型的權重相等（50% / 50%）
   - 最終 RMSE：57841.37

2. **策略 1（加權平均，根據 RMSE 反比加權）**：
   ```python
   weight_lgbm = 1 / rmse_lgbm  # 效能越好，權重越大
   weight_rf = 1 / rmse_rf
   # 正規化權重使其總和為 1
   ensemble_predictions = weight_lgbm * lgbm_predictions + weight_rf * rf_predictions
   ```
   - LightGBM 權重：53.11%（因為 RMSE 較低，效能較好）
   - RandomForest 權重：46.89%
   - 最終 RMSE：54243.64（選擇了較好的策略）

#### 為什麼整合能提升效能？

1. **互補性**：不同模型可能在不同資料上表現更好，整合可以互補
2. **降低風險**：單一模型可能過擬合，整合可以降低風險
3. **穩定性**：整合後的預測通常更穩定

### 5.7 什麼是「資料清理」、「特徵工程」、「模型選擇」、「參數調整」、「模型整合」？

這些是機器學習流程中的關鍵步驟：

#### 資料清理（Data Cleaning）

**目的**：處理資料中的問題，使其適合機器學習模型使用。

**常見問題與處理方法**：
- **Missing Value（缺失值）**：
  - 問題：某些資料欄位為空（如 `total_bedrooms` 可能為 NaN）
  - 處理：使用中位數、平均值或刪除該筆資料
  - 範例：`SimpleImputer(strategy="median")`
- **Outlier（異常值）**：
  - 問題：某些資料值明顯不合理（如房價為負數）
  - 處理：移除或修正異常值
- **資料格式不一致**：
  - 問題：日期格式不統一、文字大小寫不一致等
  - 處理：標準化格式

#### 特徵工程（Feature Engineering）

**目的**：從原始資料中創造新的、更有用的特徵，提升模型預測能力。

**常見方法**：
- **組合特徵**：
  - 原始：`total_rooms`、`households`
  - 新特徵：`rooms_per_household = total_rooms / households`
- **Mathematical Transformation（數學變換）**：
  - 對數變換：`log(income)`（處理 Skewed Distribution（偏態分佈））
  - 平方：`age^2`（捕捉 Non-linear Relationship（非線性關係））
- **Categorical Encoding（類別編碼）**：
  - One-Hot Encoding：將 Categorical Variable（類別變數）轉換為數值
- **時間特徵**：
  - 從日期中提取：年、月、星期幾等

**範例**（來自本專案）：
```python
# 創造新特徵
df['rooms_per_household'] = df['total_rooms'] / df['households']
df['bedrooms_per_room'] = df['total_bedrooms'] / df['total_rooms']
df['population_per_household'] = df['population'] / df['households']
```

#### 模型選擇（Model Selection）

**目的**：選擇適合當前任務的機器學習模型。

**考慮因素**：
- **任務類型**：
  - 迴歸問題 → LightGBM、XGBoost、RandomForest
  - 分類問題 → Logistic Regression（邏輯迴歸）、SVM（Support Vector Machine，支援向量機）、Neural Network（NN，神經網路）
- **資料特性**：
  - 表格資料 → 樹模型（LightGBM、XGBoost）
  - 圖像資料 → CNN（Convolutional Neural Network，卷積神經網路）
  - 文字資料 → Transformer、LSTM（Long Short-Term Memory，長短期記憶）
- **效能要求**：
  - 需要高準確度 → XGBoost、LightGBM
  - 需要可解釋性 → Linear Model（線性模型）、Decision Tree（決策樹）

**在本專案中**：系統透過網路搜尋找到 LightGBM 和 XGBoost，因為它們在表格迴歸任務上表現優異。

#### 參數調整（Hyperparameter Tuning）

**目的**：調整模型的參數，以獲得最佳效能。

**常見參數**（以 LightGBM 為例）：
- `n_estimators`：樹的數量（越多越準確，但可能 Overfitting（過擬合））
- `learning_rate`：Learning Rate（學習率）（越小越穩定，但需要更多樹）
- `num_leaves`：每棵樹的葉子數（控制模型複雜度）
- `max_depth`：樹的最大深度

**調整方法**：
- **Grid Search（網格搜尋）**：嘗試所有參數組合
- **Random Search（隨機搜尋）**：隨機嘗試參數組合
- **Bayesian Optimization（貝葉斯優化）**：智能選擇參數組合

**在本專案中**：系統使用預設參數或 LLM 建議的參數，沒有進行大規模參數搜尋。

#### 模型整合（Ensemble / Model Integration）

**目的**：將多個模型的預測結果組合，獲得比單一模型更好的效能。

**常見方法**：
1. **Simple Averaging（簡單平均）**：`prediction = (model1_pred + model2_pred) / 2`
2. **Weighted Averaging（加權平均）**：`prediction = w1 * model1_pred + w2 * model2_pred`（權重根據 Performance（效能）決定）
3. **Voting（投票法）**（分類問題）：多數決
4. **Stacking（堆疊法）**：用另一個模型學習如何組合預測

**在本專案中**：使用加權平均，權重根據各模型的 RMSE 反比計算。

---

## 6. 執行流程

### 6.1 執行流程範例

以實際執行過程為例（參考 `final_state.json`）：

1. **初始化階段**：
   - 搜尋找到 LightGBM 和 XGBoost 兩個機器學習模型
   - 產生兩個初始解決方案（`init_code_1.py`、`init_code_2.py`）
   - 評估兩個方案，選擇較好的作為起點

2. **第一次優化**：
   - 執行消融研究（`ablation_0.py`）
   - 發現「特徵工程」影響最大
   - 生成多個改進計劃
   - 實作較佳計劃，產生 `train0_improve0.py`、`train0_improve1.py`
   - 更新為 `train1.py`

3. **第二次優化**：
   - 再次執行消融研究
   - 識別新的關鍵區塊
   - 重複優化流程

4. **整合階段**：
   - 將多個解決方案組合
   - 嘗試不同的整合策略（簡單平均、加權平均等）
   - 產生最終的 `final_solution.py` 和 `submission.csv`

### 6.2 完整執行過程步驟

以下是 MLE-STAR 系統的完整執行流程：

#### 階段 0：準備階段（Preparation）

1. **載入配置**
   - 讀取 `DefaultConfig` 中的配置參數
   - 設定隨機種子（seed）確保可重現性
   - 初始化工作目錄

2. **讀取任務描述**
   - 從 `tasks/{task_name}/task_description.txt` 讀取任務描述
   - 解析任務類型、評估指標、提交格式等

3. **建立工作空間**
   - 在 `workspace/{task_name}/` 下建立目錄結構
   - 複製資料檔案到 `workspace/{task_name}/{solution_id}/input/`

#### 階段 1：初始化階段（Initialization）

**目標**：產生多個初始解決方案

對於每個解決方案（`num_solutions` 次，預設 2 次）：

1. **任務摘要生成**（Task Summarization）
   - **LLM 呼叫**：1 次
   - **Agent**：`task_summarization_agent`
   - **作用**：將任務描述濃縮為簡潔摘要

2. **機器學習模型檢索**（Model Retrieval）
   - **LLM 呼叫**：1 次（可能重試，最多 `max_retry` 次）
   - **Agent**：`model_retriever_agent`（A_retriever）
   - **工具**：使用 `google_search` 工具搜尋網路
   - **作用**：
     - 生成搜尋查詢（如「effective models for tabular regression」）
     - 解析搜尋結果
     - 提取機器學習模型名稱和範例程式碼
   - **產出**：`num_model_candidates` 個模型候選（預設 2 個）

3. **模型評估與程式碼生成**（Model Evaluation）
   - 對於每個模型候選（`num_model_candidates` 次）：
     - **LLM 呼叫**：1 次（可能重試，最多 `max_retry` 次）
     - **Agent**：`model_eval_and_debug_loop_agent`
     - **作用**：
       - 根據模型範例和任務描述，生成完整的訓練程式碼
       - 執行程式碼並評估效能
       - 如果出錯，進行除錯（最多 `max_debug_round` 次）
   - **產出**：`init_code_{solution_id}_{model_id}.py` 和執行結果

4. **方案排序**（Ranking）
   - 根據評估分數（RMSE）對模型候選進行排序
   - 選擇較佳模型作為基礎方案

5. **方案整合**（Integration）
   - 對於其他模型候選（`num_model_candidates - 1` 次）：
     - **LLM 呼叫**：1 次（可能重試）
     - **Agent**：`merge_and_debug_loop_agent`
     - **作用**：將其他模型的優點整合到基礎方案中
   - **產出**：`train0.py`（初始解決方案）

#### 階段 2：優化階段（Refinement）

**目標**：迭代優化每個解決方案

對於每個解決方案，執行外迴圈（`outer_loop_round` 次，預設 1 次）：

**外迴圈每次迭代**：

1. **消融研究**（Ablation Study）
   - **LLM 呼叫**：1 次（可能重試，最多 `max_rollback_round` 次）
   - **Agent**：`ablation_agent`（A_abl）
   - **作用**：
     - 分析當前程式碼
     - 生成消融研究程式碼（測試移除不同組件的影響）
     - 執行消融研究
   - **產出**：`ablation_{step}.py` 和執行結果

2. **消融結果摘要**（Ablation Summary）
   - **LLM 呼叫**：1 次
   - **Agent**：`ablation_summary_agent`
   - **作用**：分析消融研究結果，總結各組件的影響

3. **程式碼區塊提取與計劃生成**（Code Block Extraction & Planning）
   - **LLM 呼叫**：1 次（可能重試，最多 `max_retry` 次）
   - **Agent**：`init_plan_agent`（A_extractor + A_planner）
   - **作用**：
     - 根據消融研究結果，識別關鍵程式碼區塊
     - 生成初始改進計劃
   - **產出**：關鍵程式碼區塊和改進計劃

4. **初始計劃實作**（Initial Plan Implementation）
   - **LLM 呼叫**：1 次（可能重試）
   - **Agent**：`init_plan_implement_agent`
   - **作用**：實作初始改進計劃
   - **產出**：改進後的程式碼和執行結果

5. **內迴圈優化**（Inner Loop Refinement）
   - 執行內迴圈（`inner_loop_round` 次，預設 1 次）：
     - **計劃精煉**（Plan Refinement）
       - **LLM 呼叫**：1 次
       - **Agent**：`plan_refine_agent`（A_planner）
       - **作用**：根據前次執行結果，精煉改進計劃
     - **計劃實作**（Plan Implementation）
       - **LLM 呼叫**：1 次（可能重試）
       - **Agent**：`plan_implement_agent`
       - **作用**：實作精煉後的計劃
   - **產出**：`train{step+1}.py`（優化後的解決方案）

#### 階段 3：整合階段（Ensemble）

**目標**：將多個解決方案組合

1. **初始整合計劃生成**（Initial Ensemble Plan）
   - **LLM 呼叫**：1 次
   - **Agent**：`init_ensemble_plan_agent`（A_ensemble）
   - **作用**：生成整合策略（如簡單平均、加權平均等）
   - **產出**：整合計劃

2. **初始整合計劃實作**（Initial Ensemble Plan Implementation）
   - **LLM 呼叫**：1 次（可能重試）
   - **Agent**：`init_ensemble_plan_implement_agent`
   - **作用**：實作整合計劃，生成整合程式碼
   - **產出**：`ensemble0.py` 和執行結果

3. **整合計劃精煉迴圈**（Ensemble Plan Refinement Loop）
   - 執行整合迴圈（`ensemble_loop_round` 次，預設 1 次）：
     - **計劃精煉**（Plan Refinement）
       - **LLM 呼叫**：1 次
       - **Agent**：`ensemble_plan_refine_agent`（A_ensemble）
       - **作用**：根據前次執行結果，精煉整合策略
     - **計劃實作**（Plan Implementation）
       - **LLM 呼叫**：1 次（可能重試）
       - **Agent**：`ensemble_plan_implement_agent`
       - **作用**：實作精煉後的整合策略
   - **產出**：`ensemble{iter}.py` 和執行結果

#### 階段 4：提交階段（Submission）

**目標**：產生最終提交檔案

1. **選擇較佳解決方案**
   - 根據評估分數，選擇較佳的解決方案或整合結果

2. **生成最終程式碼**
   - **LLM 呼叫**：1 次（可能重試）
   - **Agent**：`submission_agent`
   - **作用**：生成符合提交格式的最終程式碼
   - **產出**：`final_solution.py`

3. **執行並產生提交檔案**
   - 執行最終程式碼
   - 產生 `final/submission.csv`

4. **儲存狀態**
   - 將所有狀態儲存到 `final_state.json`

---

## 7. 需要補充說明的部分

### 7.1 系統架構細節

#### 多代理系統結構
- **主代理**（`mle_frontdoor_agent`）：負責接收使用者請求並協調子代理
- **管道代理**（`mle_pipeline_agent`）：依序執行四個子代理
- **子代理**：
  1. `initialization_agent`：初始化階段
  2. `refinement_agent`：優化階段
  3. `ensemble_agent`：整合階段
  4. `submission_agent`：提交階段

#### 雙迴圈優化機制
- **外迴圈（Outer Loop）**：
  - 每次迭代進行一次消融研究
  - 識別新的關鍵程式碼區塊
  - 更新優化目標
- **內迴圈（Inner Loop）**：
  - 針對同一個程式碼區塊，嘗試多個改進計劃
  - 選擇效果較好的計劃
  - 更新程式碼區塊

### 7.2 關鍵技術細節

#### 消融研究（Ablation Study）
- **目的**：找出對模型效能影響最大的組件
- **方法**：逐一移除或修改不同組件（如特徵工程、資料預處理、模型參數等），比較效能變化
- **範例**：
  - 完整模型：RMSE = 61439
  - 移除特徵工程：RMSE = 62724（變差 1285）
  - 結論：特徵工程影響最大，應優先優化

#### 程式碼區塊提取
- **方法**：分析消融研究結果，找出移除後效能下降最多的組件
- **實作**：使用 AST（抽象語法樹）解析 Python 程式碼，精確定位程式碼區塊

#### 計劃生成與選擇
- **計劃生成**：LLM 根據前次實驗結果和當前程式碼，提出多個改進方向
- **計劃評估**：每個計劃都會實作並執行，比較實際效果
- **計劃選擇**：選擇效果最好的計劃，更新到主程式碼中

### 7.3 配置與參數說明

#### 重要配置參數
- `num_solutions`：要產生幾個初始解決方案（預設 2）
- `num_model_candidates`：每個解決方案要嘗試幾個模型候選（預設 2）
- `outer_loop_round`：外迴圈優化輪數（預設 1）
- `inner_loop_round`：內迴圈優化輪數（預設 1）
- `num_top_plans`：每次考慮幾個改進計劃（預設 2）

以下是 `DefaultConfig` 的**全部配置參數**說明：

#### 完整配置參數列表

##### 1. `data_dir`
- **類型**：`str`
- **預設值**：`"./machine_learning_engineering/tasks/"`
- **說明**：機器學習任務和資料的儲存目錄路徑
- **影響**：決定系統從哪裡讀取任務描述和資料檔案

##### 2. `task_name`
- **類型**：`str`
- **預設值**：`"california-housing-prices"`
- **說明**：要載入和處理的特定任務名稱
- **影響**：決定使用哪個任務的資料和描述

##### 3. `task_type`
- **類型**：`str`
- **預設值**：`"Tabular Regression"`
- **說明**：機器學習問題的類型
- **影響**：影響 LLM 選擇適合的機器學習模型和策略
- **常見值**：`"Tabular Regression"`、`"Tabular Classification"`、`"Image Classification"` 等

##### 4. `lower`
- **類型**：`bool`
- **預設值**：`True`
- **說明**：評估指標是否越小越好
- **影響**：
  - `True`：RMSE（Root Mean Squared Error，均方根誤差）、MAE（Mean Absolute Error，平均絕對誤差）等（越小越好）
  - `False`：Accuracy（準確率）、F1-Score 等（越大越好）
- **影響**：影響方案排序和選擇邏輯

##### 5. `workspace_dir`
- **類型**：`str`
- **預設值**：`"./machine_learning_engineering/workspace/"`
- **說明**：用於儲存中間輸出、結果、日誌的工作目錄
- **影響**：決定所有輸出檔案的位置

##### 6. `agent_model`
- **類型**：`str`
- **預設值**：`os.environ.get("ROOT_AGENT_MODEL", "gemini-2.0-flash-001")`
- **說明**：Agent 使用的 LLM 模型識別碼
- **影響**：決定使用哪個 LLM（影響成本和效能）
- **常見值**：`"gemini-2.5-flash"`、`"gemini-2.5-pro"` 等

##### 7. `task_description`
- **類型**：`str`
- **預設值**：`""`
- **說明**：任務的詳細描述（通常從檔案讀取）
- **影響**：提供給 LLM 的任務資訊

##### 8. `task_summary`
- **類型**：`str`
- **預設值**：`""`
- **說明**：任務的簡潔摘要（由 LLM 生成）
- **影響**：用於模型檢索等階段

##### 9. `start_time`
- **類型**：`float`
- **預設值**：`0.0`
- **說明**：任務開始時間的時間戳記（秒）
- **影響**：用於追蹤執行時間

##### 10. `seed`
- **類型**：`int`
- **預設值**：`42`
- **說明**：隨機種子值，用於確保實驗的可重現性
- **影響**：影響資料分割、模型初始化的隨機性

##### 11. `exec_timeout`
- **類型**：`int`
- **預設值**：`600`
- **說明**：完成任務的最大允許時間（秒）
- **影響**：防止程式執行時間過長

##### 12. `num_solutions`
- **類型**：`int`
- **預設值**：`2`
- **說明**：要產生或嘗試的不同解決方案數量
- **影響**：
  - 越多：探索更多可能性，但時間和成本增加
  - 越少：執行快速，但可能錯過較佳方案

##### 13. `num_model_candidates`
- **類型**：`int`
- **預設值**：`2`
- **說明**：要考慮的不同機器學習模型架構或超參數組合數量
- **影響**：
  - 越多：嘗試更多模型，但時間增加
  - 越少：執行快速，但可能錯過更好的模型
- **注意**：這裡的「模型」指的是**機器學習模型**，不是 LLM

##### 14. `max_retry`
- **類型**：`int`
- **預設值**：`10`
- **說明**：失敗操作的最大重試次數
- **影響**：
  - 越多：更可能成功，但可能浪費時間
  - 越少：快速失敗，但可能錯過可修復的錯誤

##### 15. `max_debug_round`
- **類型**：`int`
- **預設值**：`5`
- **說明**：除錯步驟允許的最大迭代或輪數
- **影響**：限制除錯嘗試次數，防止無限迴圈

##### 16. `max_rollback_round`
- **類型**：`int`
- **預設值**：`2`
- **說明**：系統可以回滾到先前狀態的最大次數（發生錯誤或效能不佳時）
- **影響**：限制回滾次數，防止無限回滾

##### 17. `inner_loop_round`
- **類型**：`int`
- **預設值**：`1`
- **說明**：內迴圈中要執行的迭代或輪數
- **影響**：
  - 越多：對同一程式碼區塊進行更多改進嘗試
  - 越少：快速進入下一階段

##### 18. `outer_loop_round`
- **類型**：`int`
- **預設值**：`1`
- **說明**：外迴圈中要執行的迭代或輪數（可能包含多個內迴圈）
- **影響**：
  - 越多：進行更多輪的消融研究和優化
  - 越少：快速完成優化階段

##### 19. `ensemble_loop_round`
- **類型**：`int`
- **預設值**：`1`
- **說明**：專用於整合的輪數或迭代次數（組合多個模型或解決方案）
- **影響**：
  - 越多：嘗試更多整合策略
  - 越少：快速完成整合

##### 20. `num_top_plans`
- **類型**：`int`
- **預設值**：`2`
- **說明**：要選擇或保留的最高分計劃或策略數量
- **影響**：
  - 越多：考慮更多計劃，但時間增加
  - 越少：快速選擇，但可能錯過更好的計劃

##### 21. `use_data_leakage_checker`
- **類型**：`bool`
- **預設值**：`False`
- **說明**：啟用（`True`）或停用（`False`）機器學習管道中的資料洩漏檢查
- **影響**：
  - `True`：檢查並防止資料洩漏（如使用未來資訊預測過去），但增加執行時間
  - `False`：不檢查，執行快速，但可能有資料洩漏風險

##### 22. `use_data_usage_checker`
- **類型**：`bool`
- **預設值**：`False`
- **說明**：啟用（`True`）或停用（`False`）資料使用檢查（用於合規或最佳實踐）
- **影響**：
  - `True`：確保所有提供的資料來源都被使用，但增加執行時間
  - `False`：不檢查，執行快速

### 7.4 調整配置參數（如任務類型、評估指標等）會有哪些影響，請針對每個配置參數詳細說明

以下是每個配置參數調整的**詳細影響說明**：

#### 資料與任務相關參數

##### `data_dir`
- **調整影響**：
  - 改變任務資料的讀取位置
  - 如果路徑錯誤，系統無法找到任務資料
- **建議**：保持預設值，除非任務資料儲存在其他位置

##### `task_name`
- **調整影響**：
  - 切換到不同的任務
  - 必須確保對應的目錄和檔案存在
- **建議**：根據實際任務修改

##### `task_type`
- **調整影響**：
  - **`"Tabular Regression"`**：LLM 會搜尋迴歸模型（LightGBM、XGBoost 等）
  - **`"Tabular Classification"`**：LLM 會搜尋分類模型（Logistic Regression 邏輯迴歸、SVM 支援向量機等）
  - **`"Image Classification"`**：LLM 會搜尋 CNN 模型
- **建議**：必須與實際任務類型匹配

##### `lower`
- **調整影響**：
  - **`True`**（RMSE（Root Mean Squared Error，均方根誤差）、MAE（Mean Absolute Error，平均絕對誤差））：系統會選擇分數**最低**的方案
  - **`False`**（Accuracy（準確率）、F1-Score）：系統會選擇分數**最高**的方案
- **建議**：必須與評估指標的特性匹配

#### 工作空間參數

##### `workspace_dir`
- **調整影響**：
  - 改變所有輸出檔案的位置
  - 如果路徑不存在，系統會自動建立
- **建議**：保持預設值，除非需要指定特定位置

#### LLM 相關參數

##### `agent_model`
- **調整影響**：
  - **`"gemini-2.5-flash"`**：
    - 成本低、速度快
    - 獎牌率約 43.9%
    - 適合快速迭代
  - **`"gemini-2.5-pro"`**：
    - 成本高、速度慢
    - 獎牌率約 63.6%
    - 適合追求較佳結果
- **建議**：根據預算和需求選擇

#### 執行控制參數

##### `seed`
- **調整影響**：
  - 影響資料分割、模型初始化的隨機性
  - 相同 seed 可以重現結果
  - 不同 seed 可能產生不同結果
- **建議**：用於實驗可重現性，一般保持 42

##### `exec_timeout`
- **調整影響**：
  - 限制單次執行的最大時間
  - 過小可能導致正常執行被中斷
  - 過大可能讓錯誤執行運行太久
- **建議**：根據資料大小調整，一般 600 秒足夠

#### 解決方案數量參數

##### `num_solutions`
- **調整影響**：
  - **增加**：
    - 探索更多可能性
    - 整合階段有更多選擇
    - 執行時間和成本線性增加
  - **減少**：
    - 執行快速
    - 可能錯過最佳方案
- **建議**：
  - 快速測試：1
  - 一般使用：2（預設）
  - 追求較佳：3-5

##### `num_model_candidates`
- **調整影響**：
  - **增加**：
    - 嘗試更多機器學習模型
    - 增加找到較佳模型的機會
    - 每個解決方案的時間增加
  - **減少**：
    - 執行快速
    - 可能錯過更好的模型
- **建議**：
  - 快速測試：1
  - 一般使用：2（預設）
  - 追求較佳：3-4

#### 迴圈控制參數

##### `outer_loop_round`
- **調整影響**：
  - **增加**：
    - 進行更多輪的消融研究和優化
    - 可能找到更多改進點
    - 執行時間明顯增加
  - **減少**：
    - 快速完成優化
    - 可能錯過改進機會
- **建議**：
  - 快速測試：0（跳過優化）
  - 一般使用：1（預設）
  - 追求較佳：2-3

##### `inner_loop_round`
- **調整影響**：
  - **增加**：
    - 對同一程式碼區塊進行更多改進嘗試
    - 可能找到更好的改進計劃
    - 執行時間增加
  - **減少**：
    - 快速進入下一階段
    - 可能錯過更好的計劃
- **建議**：
  - 快速測試：0
  - 一般使用：1（預設）
  - 追求較佳：2-3

##### `ensemble_loop_round`
- **調整影響**：
  - **增加**：
    - 嘗試更多整合策略
    - 可能找到更好的整合方法
    - 執行時間增加
  - **減少**：
    - 快速完成整合
    - 可能錯過更好的整合策略
- **建議**：
  - 快速測試：0（跳過整合）
  - 一般使用：1（預設）
  - 追求較佳：2

#### 計劃選擇參數

##### `num_top_plans`
- **調整影響**：
  - **增加**：
    - 考慮更多改進計劃
    - 可能找到更好的計劃
    - 執行時間增加
  - **減少**：
    - 快速選擇計劃
    - 可能錯過更好的計劃
- **建議**：
  - 快速測試：1
  - 一般使用：2（預設）
  - 追求較佳：3-5

#### 重試與除錯參數

##### `max_retry`
- **調整影響**：
  - **增加**：
    - 更可能從暫時性錯誤中恢復
    - 但可能浪費時間在無法修復的錯誤上
  - **減少**：
    - 快速失敗，節省時間
    - 但可能錯過可修復的錯誤
- **建議**：
  - 快速測試：3
  - 一般使用：10（預設）
  - 穩定環境：5

##### `max_debug_round`
- **調整影響**：
  - **增加**：
    - 允許更多除錯嘗試
    - 可能修復更多錯誤
    - 但可能陷入無限除錯
  - **減少**：
    - 快速失敗
    - 但可能錯過可修復的錯誤
- **建議**：保持預設值 5

##### `max_rollback_round`
- **調整影響**：
  - **增加**：
    - 允許更多回滾嘗試
    - 可能從錯誤中恢復
    - 但可能浪費時間
  - **減少**：
    - 快速失敗
    - 但可能錯過可恢復的情況
- **建議**：保持預設值 2

#### 檢查器參數

##### `use_data_leakage_checker`
- **調整影響**：
  - **`True`**：
    - 檢查並防止資料洩漏
    - 增加執行時間（每次檢查都需要 LLM 呼叫）
    - 提高結果的可信度
  - **`False`**：
    - 不檢查，執行快速
    - 但可能有資料洩漏風險（如使用測試資料特徵預測訓練資料）
- **建議**：
  - 正式競賽：`True`
  - 快速測試：`False`（預設）

##### `use_data_usage_checker`
- **調整影響**：
  - **`True`**：
    - 確保所有提供的資料都被使用
    - 增加執行時間
    - 可能有助於發現遺漏的資料來源
  - **`False`**：
    - 不檢查，執行快速
    - 但可能遺漏某些資料來源
- **建議**：一般保持 `False`（預設）

#### 配置參數調整建議總結

**快速測試配置**：
```python
num_solutions = 1
num_model_candidates = 1
outer_loop_round = 0
inner_loop_round = 0
ensemble_loop_round = 0
max_retry = 3
```

**一般使用配置**（預設）：
```python
# 保持所有預設值
```

**追求較佳結果配置**：
```python
num_solutions = 3
num_model_candidates = 3
outer_loop_round = 2
inner_loop_round = 2
ensemble_loop_round = 2
num_top_plans = 3
agent_model = "gemini-2.5-pro"
use_data_leakage_checker = True
```

### 7.5 限制與注意事項

1. **執行時間**：
   - 完整流程可能需要數小時，取決於資料大小和配置
   - 每次模型訓練和消融研究都需要實際執行 Python 程式

2. **成本考量**：
   - 使用 LLM API 會產生費用
   - Gemini-2.5-Pro 比 Flash 版本更貴但效果更好

3. **資料品質**：
   - 系統假設輸入資料格式正確
   - 如果資料有嚴重問題，可能需要人工介入

4. **除錯機制**：
   - 系統包含除錯代理（debug agent），會自動修正程式錯誤
   - 但如果錯誤過於複雜，可能需要人工協助

### 7.6 「要嘗試的模型候選數量」這裡的模型是「模型」還是「LLM」？模型候選有哪些？數量多少如何決定？

**這裡的「模型」指的是「機器學習模型」**（如 LightGBM、XGBoost），**不是 LLM**。

#### 模型候選

**模型候選**由配置參數 `num_model_candidates` 控制（預設為 2），指的是系統會嘗試的**機器學習模型**數量。

#### 常見的模型候選

根據任務類型，系統可能搜尋到的模型候選包括：

**表格迴歸任務**（如本專案）：
- LightGBM Regressor
- XGBoost Regressor
- RandomForest Regressor
- CatBoost Regressor
- Gradient Boosting Regressor
- Linear Regression（線性迴歸）
- SVR（Support Vector Regression，支援向量迴歸）

**表格分類任務**：
- LightGBM Classifier
- XGBoost Classifier
- RandomForest Classifier
- Logistic Regression（邏輯迴歸）
- SVM（Support Vector Machine，支援向量機）

#### 數量如何決定？

**由配置參數 `num_model_candidates` 控制**：

1. **預設值**：2
   - 平衡探索與效率
   - 每個解決方案嘗試 2 個不同的機器學習模型

2. **如何修改**：
   - 在 `shared_libraries/config.py` 中修改 `num_model_candidates`
   - 或在執行時透過環境變數設定

3. **建議值**：
   - **快速測試**：1（只嘗試一個模型）
   - **一般使用**：2（預設，平衡效果與時間）
   - **追求較佳結果**：3-5（需要更多時間和 LLM API 呼叫）

#### 實際範例

在本專案中，`num_model_candidates = 2`，對於每個解決方案：
- **Solution 1**：嘗試了 XGBoost 和 LightGBM
- **Solution 2**：嘗試了 LightGBM 和 XGBoost

最終選擇了效能較好的模型作為基礎方案。

### 7.7 所謂「多輪優化改進的完整訓練程式」請詳細說明程式邏輯，改進了哪些內容用來達成更好的預測準確度？

**多輪優化**指的是系統透過外迴圈和內迴圈，迭代改進訓練程式，逐步提升機器學習模型的預測準確度。

#### 優化流程邏輯

```
初始程式碼 (train0.py)
    ↓
[外迴圈開始]
    ↓
消融研究 → 識別關鍵組件（如：特徵工程）
    ↓
[內迴圈開始]
    ↓
生成改進計劃 1 → 實作 → 評估（RMSE = 62000）
生成改進計劃 2 → 實作 → 評估（RMSE = 61500）
    ↓
選擇較佳計劃（計劃 2）
    ↓
[內迴圈結束]
    ↓
更新程式碼 (train1.py, RMSE = 61500)
    ↓
[外迴圈結束]
```

#### 具體改進內容

根據本專案的實際執行記錄，系統改進了以下內容：

1. **特徵工程優化**：
   - **初始版本**：簡單的特徵組合
   - **改進後**：
     - 處理除零錯誤（`households_safe = households.replace(0, 1)`）
     - 處理無限值（`replace([np.inf, -np.inf], np.nan)`）
     - 更完整的缺失值處理

2. **資料預處理改進**：
   - **初始版本**：簡單的中位數填補
   - **改進後**：
     - 分階段填補（先填補特定欄位，再填補其他欄位）
     - 確保訓練和測試資料的一致性處理

3. **模型參數調整**：
   - **初始版本**：使用預設參數
   - **改進後**：
     - 根據任務特性調整參數
     - 使用 K-Fold Cross Validation（K 折交叉驗證）提升穩定性

4. **驗證策略改進**：
   - **初始版本**：簡單的 Train/Validation Split（訓練/驗證分割）
   - **改進後**：
     - 使用 K-Fold Cross Validation（K 折交叉驗證）
     - 更準確的 Performance Evaluation（效能評估）

#### 實際改進範例

從 `final_state.json` 可以看到：

**初始方案（train0.py）**：
- RMSE = 61439.09
- 使用 RandomForest，簡單的特徵工程

**第一次優化後（train1.py）**：
- 改進了特徵工程（處理除零和無限值）
- RMSE = 61439.09（維持相同，但程式更穩定）

**整合後（ensemble）**：
- 結合 LightGBM 和 RandomForest
- 最終 RMSE = 54243.64（明顯提升）

#### 改進策略

系統使用以下策略進行改進：

1. **目標導向**：根據消融研究結果，優先改進影響最大的組件
2. **實驗驗證**：每個改進都會實際執行並評估
3. **迭代精煉**：根據執行結果，進一步精煉改進計劃
4. **選擇較佳**：比較多個改進計劃，選擇效果較好的

### 7.8 A_retriever、A_abl、A_extractor、A_planner、A_ensemble 在這個 task 範例中各自呼叫 LLM 幾次？呼叫次數如何決定？如何修改「呼叫次數」？

根據程式碼分析和執行流程，以下是各 Agent 的 LLM 呼叫次數：

#### LLM 呼叫次數統計

**假設配置**：`num_solutions = 2`，`num_model_candidates = 2`，`outer_loop_round = 1`，`inner_loop_round = 1`，`ensemble_loop_round = 1`

##### A_retriever（模型檢索代理）

- **呼叫次數**：`num_solutions` 次（每個解決方案 1 次）
- **本範例**：2 次
- **可能重試**：最多 `max_retry` 次（預設 10 次）
- **實際可能**：2-20 次（如果每次都成功，只需 2 次）

##### A_abl（消融研究代理）

- **呼叫次數**：`num_solutions × outer_loop_round` 次
- **本範例**：2 × 1 = 2 次
- **可能重試**：最多 `max_rollback_round` 次（預設 2 次）
- **實際可能**：2-4 次

##### A_extractor（程式碼區塊提取代理）

- **與 A_planner 合併**：在 `init_plan_agent` 中一起執行
- **呼叫次數**：`num_solutions × outer_loop_round` 次
- **本範例**：2 × 1 = 2 次
- **可能重試**：最多 `max_retry` 次（預設 10 次）
- **實際可能**：2-20 次

##### A_planner（計劃生成代理）

- **初始計劃**：`num_solutions × outer_loop_round` 次（與 A_extractor 一起）
- **計劃精煉**：`num_solutions × outer_loop_round × inner_loop_round` 次
- **本範例**：2 × 1 + 2 × 1 × 1 = 4 次
- **可能重試**：每次最多 `max_retry` 次
- **實際可能**：4-40 次

##### A_ensemble（整合代理）

- **初始計劃**：1 次
- **計劃精煉**：`ensemble_loop_round` 次
- **本範例**：1 + 1 = 2 次
- **可能重試**：每次最多 `max_retry` 次
- **實際可能**：2-20 次

#### 總計（本範例）

| Agent | 最少呼叫 | 最多呼叫（含重試） |
|-------|----------|-------------------|
| A_retriever | 2 | 20 |
| A_abl | 2 | 4 |
| A_extractor | 2 | 20 |
| A_planner | 4 | 40 |
| A_ensemble | 2 | 20 |
| **總計** | **12** | **104** |

#### 呼叫次數如何決定？

**由以下配置參數決定**：

1. **`num_solutions`**：影響 A_retriever、A_abl、A_extractor、A_planner
2. **`num_model_candidates`**：影響模型評估的 LLM 呼叫（不在上述 Agent 中）
3. **`outer_loop_round`**：影響 A_abl、A_extractor、A_planner
4. **`inner_loop_round`**：影響 A_planner
5. **`ensemble_loop_round`**：影響 A_ensemble
6. **`max_retry`**：影響所有 Agent 的重試次數
7. **`max_rollback_round`**：影響 A_abl 的重試次數

#### 如何修改「呼叫次數」？

**方法 1：修改配置參數**

在 `shared_libraries/config.py` 中修改：

```python
@dataclasses.dataclass
class DefaultConfig:
    num_solutions: int = 1  # 減少解決方案數量
    outer_loop_round: int = 0  # 減少外迴圈次數
    inner_loop_round: int = 0  # 減少內迴圈次數
    ensemble_loop_round: int = 0  # 減少整合迴圈次數
    max_retry: int = 3  # 減少重試次數
```

**方法 2：透過環境變數**

在執行前設定環境變數（如果系統支援）。

**方法 3：修改程式碼**

直接修改各 Agent 的 `max_iterations` 參數。

### 7.9 A_retriever、A_abl、A_extractor、A_planner、A_ensemble 如果需要設定為不同 LLM，請根據需求能力給予不同等級（等級簡單分區為1-5，5級最高）

根據各 Agent 的任務複雜度和對 LLM 能力的需求，建議的 LLM 等級如下：

#### LLM 需求等級評估

| Agent | 任務描述 | 需求等級 | 建議 LLM | 理由 |
|-------|----------|----------|----------|------|
| **A_retriever** | 生成搜尋查詢、解析搜尋結果、提取模型資訊 | **4級** | Gemini-2.5-Pro / GPT-4 | 需要理解任務、生成有效查詢、解析複雜結果 |
| **A_abl** | 生成消融研究程式碼、分析程式結構 | **3級** | Gemini-2.5-Flash / GPT-3.5-Turbo | 需要程式碼生成能力，但邏輯相對直接 |
| **A_extractor** | 分析消融結果、識別關鍵程式碼區塊 | **4級** | Gemini-2.5-Pro / GPT-4 | 需要深度分析和推理能力 |
| **A_planner** | 生成改進計劃、根據結果精煉計劃 | **5級** | Gemini-2.5-Pro / GPT-4 | 需要較強的推理和策略規劃能力 |
| **A_ensemble** | 設計整合策略、計算權重 | **3級** | Gemini-2.5-Flash / GPT-3.5-Turbo | 邏輯相對簡單，主要是數學計算 |

#### 等級說明

- **5級（最高）**：需要較強的推理、規劃和策略能力
- **4級**：需要深度分析和理解能力
- **3級**：需要基本的程式碼生成和理解能力
- **2級**：需要簡單的文字處理能力
- **1級（最低）**：只需要基本的文字生成

#### 實際配置建議

**方案 1：平衡成本與效果**
```python
A_retriever: Gemini-2.5-Flash (3級)
A_abl: Gemini-2.5-Flash (3級)
A_extractor: Gemini-2.5-Pro (4級)
A_planner: Gemini-2.5-Pro (5級)
A_ensemble: Gemini-2.5-Flash (3級)
```

**方案 2：追求較佳效果**
```python
全部使用: Gemini-2.5-Pro (4-5級)
```

**方案 3：節省成本**
```python
全部使用: Gemini-2.5-Flash (3級)
```

#### 如何實作不同 LLM 配置？

**需要修改程式碼**，在各 Agent 定義中指定不同的 `model` 參數：

```python
# 在 initialization/agent.py 中
model_retriever_agent = agents.Agent(
    model="gemini-2.5-pro",  # 使用 Pro 版本
    ...
)

# 在 refinement/agent.py 中
ablation_agent = agents.Agent(
    model="gemini-2.5-flash",  # 使用 Flash 版本
    ...
)

init_plan_agent = agents.Agent(
    model="gemini-2.5-pro",  # 使用 Pro 版本（需要更強能力）
    ...
)
```

### 7.10 什麼是「獎牌率」？「43.9%」與「63.6%」數字的大小分別代表什麼意義？

**獎牌率**（Medal Rate）是指在 MLE-Bench-Lite 基準測試中，系統能夠獲得獎牌的任務比例。

#### 獎牌定義

在 Kaggle 競賽中，獎牌分為三種：
- **Gold Medal（金牌）**：前 5% 的參賽者
- **Silver Medal（銀牌）**：前 10% 的參賽者（但不包括金牌）
- **Bronze Medal（銅牌）**：前 25% 的參賽者（但不包括金牌和銀牌）

#### 數字意義

**43.9%**（使用 Gemini-2.5-Flash）：
- 在 100 個任務中，有 43.9 個任務能獲得獎牌（金牌、銀牌或銅牌）
- 意味著系統在約 44% 的任務上達到競賽前 25% 的水準
- **意義**：系統能夠自動產生不錯的解決方案

**63.6%**（使用 Gemini-2.5-Pro）：
- 在 100 個任務中，有 63.6 個任務能獲得獎牌
- 意味著系統在約 64% 的任務上達到競賽前 25% 的水準
- **意義**：系統能夠自動產生競賽水準的解決方案，表現良好

#### 比較分析

| LLM 模型 | 獎牌率 | 金牌率 | 銀牌率 | 銅牌率 | 意義 |
|----------|--------|--------|--------|--------|------|
| Gemini-2.5-Flash | 43.9% | 30.3% | 4.5% | 9.1% | 良好，適合快速迭代 |
| Gemini-2.5-Pro | 63.6% | 36.4% | 21.2% | 6.1% | 良好，適合追求較佳結果 |

#### 實際意義

- **43.9%**：對於快速測試和開發，已經足夠好
- **63.6%**：對於正式競賽或生產環境，表現良好
- **差異原因**：Gemini-2.5-Pro 的推理能力較強，能產生較好的程式碼和決策

### 7.11 擴展應用

這個系統不僅限於加州房價預測，可以應用到：
- 其他 Kaggle 競賽任務
- 企業內部的機器學習專案
- 任何結構化資料的預測問題（分類或迴歸）

只需要：
1. 準備任務描述檔案
2. 準備訓練和測試資料
3. 調整配置參數（如任務類型、評估指標等）
4. 執行系統

---

## 8. 網路受限環境注意事項

### 8.1 Proxy 設定

如果環境需要透過 proxy 才能連接外網，需要設定以下環境變數：

```bash
export HTTP_PROXY=http://proxy-server:port
export HTTPS_PROXY=http://proxy-server:port
export NO_PROXY=localhost,127.0.0.1
```

### 8.2 無法訪問的網站

部分外網可能無法訪問，影響：
- **Google Search**：A_retriever 需要網路搜尋，如果無法訪問，可能影響模型檢索
- **LLM API**：需要能夠訪問 Google AI Studio 或 Vertex AI

### 8.3 解決方案

1. **使用 Proxy**：設定系統 proxy，讓所有網路請求透過 proxy
2. **離線模式**：如果可能，預先下載模型範例到本地，修改程式碼跳過網路搜尋
3. **本地 LLM**：如果無法訪問 Google API，考慮使用本地部署的 LLM（需要大量修改程式碼）

---

## 總結

MLE-STAR 是一個**全自動化的機器學習工程系統**，透過 LLM 的協助，自動完成從資料處理到模型優化的完整流程。即使不具備機器學習專業知識，也能透過這個系統產生競賽水準的模型和預測結果。

系統的核心優勢在於：
1. **自動化程度高**：減少人工介入
2. **迭代優化**：透過消融研究和計劃生成，持續改進模型
3. **多模型整合**：結合多個模型的優勢
4. **可擴展性**：適用於多種機器學習任務

對於大學生或初學者來說，這個系統不僅可以幫助完成專案，更重要的是可以**觀察和學習**系統如何自動完成機器學習的完整流程，是一個不錯的學習工具。
