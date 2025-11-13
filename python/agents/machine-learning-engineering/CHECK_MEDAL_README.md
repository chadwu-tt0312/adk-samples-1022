# Kaggle Leaderboard 獎牌檢查指南

本指南說明如何取得 Kaggle 競賽的 leaderboard 數據，並判斷您的分數是否獲得獎牌。

## 方法一：使用自動化腳本（推薦）

### 前置準備

1. **安裝 Kaggle API**
   ```bash
   pip install kaggle pandas
   ```

2. **設定 Kaggle API 認證**
   - 前往 <https://www.kaggle.com/settings>
   - 點擊 "Create New Token" 下載 `kaggle.json`
   - 將檔案放置於 `~/.kaggle/kaggle.json`
   - 設定權限：`chmod 600 ~/.kaggle/kaggle.json`

### 使用方法

#### 方式 1：直接指定分數
```bash
python check_medal.py --competition titanic --score 0.8156
```

#### 方式 2：從 final_state.json 讀取分數
```bash
python check_medal.py --competition titanic --final-state machine_learning_engineering/workspace/Titanic/final_state.json
```

#### 方式 3：使用本地 leaderboard 檔案
```bash
# 先手動下載 leaderboard CSV（或解壓縮 zip 檔案）
python check_medal.py --competition titanic --score 0.8156 --leaderboard-file leaderboards/titanic-publicleaderboard.csv
```

**注意**：Kaggle API 下載的是 `.zip` 壓縮檔，腳本會自動：
1. 尋找下載的 `.zip` 檔案
2. 自動解壓縮
3. 尋找 CSV 檔案（支援多種命名格式，如 `titanic-publicleaderboard.csv`）

#### 參數說明

- `--competition`: Kaggle 競賽名稱（例如：`titanic`）
- `--score`: 要檢查的分數
- `--final-state`: final_state.json 檔案路徑
- `--higher-is-better`: 分數越高越好（如 accuracy），預設為 True
- `--lower-is-better`: 分數越低越好（如 RMSE）
- `--leaderboard-file`: 本地 leaderboard CSV 檔案路徑

### 範例輸出

```
📥 正在下載 titanic 競賽的 leaderboard...
📦 找到壓縮檔：titanic.zip
📂 正在解壓縮...
✅ 找到 CSV 檔案：titanic-publicleaderboard.csv
✅ 成功讀取 leaderboard，共 15987 筆記錄
📋 CSV 欄位：TeamId, TeamName, SubmissionDate, Score

📊 分析分數：0.8156
分數方向：越高越好

============================================================
🏆 獎牌檢查結果
============================================================
分數：0.8156
排名：第 1234 名（共 15987 名參賽者）
百分位數：92.28%
獎牌等級：Silver
🥈 恭喜！您獲得了銀牌！
============================================================

📋 獎牌門檻：
  金牌：前 5%
  銀牌：前 10%（不含金牌）
  銅牌：前 25%（不含金牌和銀牌）
```

## 方法二：手動從 Kaggle 網站取得

### 步驟

1. **訪問競賽頁面**
   - 前往 <https://www.kaggle.com/competitions/titanic/leaderboard>

2. **查看 Leaderboard**
   - 點擊 "Leaderboard" 標籤
   - 查看公開排行榜（Public Leaderboard）或私有排行榜（Private Leaderboard）

3. **手動記錄數據**
   - 複製排行榜數據到 Excel 或 CSV
   - 或使用瀏覽器開發者工具提取數據

### 使用網頁爬蟲（進階）

```python
import requests
from bs4 import BeautifulSoup
import pandas as pd

def scrape_kaggle_leaderboard(competition_name):
    """從 Kaggle 網頁爬取 leaderboard"""
    url = f"https://www.kaggle.com/competitions/{competition_name}/leaderboard"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # 解析 HTML 表格（需要根據實際網頁結構調整）
    # ...
    
    return df

# 注意：使用爬蟲需遵守 Kaggle 的服務條款
```

## 方法三：使用 Kaggle API 直接查詢

### Python 程式碼範例

```python
import kaggle
import pandas as pd

# 設定 API（需要先設定 kaggle.json）
kaggle.api.authenticate()

# 下載 leaderboard
kaggle.api.competition_leaderboard_download(
    competition='titanic',
    path='./leaderboards',
    quiet=False
)

# 讀取數據
df = pd.read_csv('./leaderboards/titanic_public_leaderboard.csv')

# 分析分數
your_score = 0.8156
df_sorted = df.sort_values('Score', ascending=False)
rank = (df_sorted['Score'] >= your_score).sum()
percentile = (1 - rank / len(df_sorted)) * 100

print(f"排名：第 {rank} 名")
print(f"百分位數：{percentile:.2f}%")
```

## 方法四：使用 MLE-Bench-Lite 的歷史數據

如果您要評估的是 MLE-Bench-Lite 中的任務，可以：

1. **查看 MLE-Bench-Lite 專案**
   - GitHub: <https://github.com/openai/mle-bench>
   - 可能包含歷史 leaderboard 數據

2. **參考論文數據**
   - 論文：<https://www.arxiv.org/abs/2506.15692>
   - 可能包含評估方法和基準數據

## 常見問題

### Q1: 找不到競賽名稱？

A: Kaggle 競賽名稱可能與顯示名稱不同，例如：
- 顯示名稱：Titanic - Machine Learning from Disaster
- 競賽名稱：`titanic` 或 `titanic-machine-learning-from-disaster`

可以在競賽 URL 中找到正確名稱：
`https://www.kaggle.com/competitions/[競賽名稱]/leaderboard`

### Q2: API 下載失敗？

A: 可能原因：
1. 競賽已結束且不提供公開 leaderboard
2. API 認證設定錯誤
3. 競賽名稱錯誤

解決方案：使用 `--leaderboard-file` 參數手動提供 CSV 檔案

### Q3: 如何判斷分數方向？

A:
- **越高越好**：accuracy, F1-score, AUC 等（使用 `--higher-is-better`）
- **越低越好**：RMSE, MAE, log loss 等（使用 `--lower-is-better`）

### Q4: Public vs Private Leaderboard？

A:
- **Public Leaderboard**：基於測試集的一部分（通常 50%）
- **Private Leaderboard**：基於完整測試集（競賽結束後公布）

通常使用 Public Leaderboard 進行評估，但最終排名以 Private Leaderboard 為準。

## Titanic 任務特定資訊

### 競賽資訊
- **競賽名稱**：`titanic` 或 `titanic-machine-learning-from-disaster`
- **評估指標**：Accuracy（準確率）
- **分數方向**：越高越好
- **典型分數範圍**：0.70 - 0.85+

### 獎牌門檻（估算）
根據歷史數據，Titanic 競賽的獎牌門檻大約是：
- **金牌**：Accuracy > 0.82（前 5%）
- **銀牌**：Accuracy > 0.80（前 10%）
- **銅牌**：Accuracy > 0.78（前 25%）

*注意：實際門檻會隨參賽者數量變化*

## 參考資源

- [Kaggle API 文檔](https://github.com/Kaggle/kaggle-api)
- [MLE-Bench-Lite GitHub](https://github.com/openai/mle-bench)
- [MLE-STAR 論文](https://www.arxiv.org/abs/2506.15692)
