"""
Kaggle Leaderboard 獎牌檢查工具

此腳本用於：
1. 從 Kaggle 下載競賽的 leaderboard 數據
2. 根據 final_state.json 中的分數計算排名百分比
3. 判斷是否獲得獎牌（金牌/銀牌/銅牌）

使用方法：
    python check_medal.py --competition titanic --score 0.8156
    或
    python check_medal.py --competition titanic --final-state path/to/final_state.json
"""

import argparse
import json
import os
import sys
import zipfile
from pathlib import Path
from typing import Optional, Tuple

try:
    import kaggle
    import pandas as pd
except ImportError:
    print("錯誤：請先安裝 kaggle 和 pandas")
    print("pip install kaggle pandas")
    sys.exit(1)


def setup_kaggle_api():
    """設定 Kaggle API 認證"""
    kaggle_dir = Path.home() / ".kaggle"
    kaggle_json = kaggle_dir / "kaggle.json"
    
    if not kaggle_json.exists():
        print("\n⚠️  未找到 Kaggle API 認證文件")
        print("請按照以下步驟設定：")
        print("1. 前往 https://www.kaggle.com/settings 建立 API token")
        print("2. 下載 kaggle.json 檔案")
        print(f"3. 將檔案放置於：{kaggle_json}")
        print("4. 設定權限：chmod 600 ~/.kaggle/kaggle.json")
        return False
    
    # 設定環境變數（如果尚未設定）
    if "KAGGLE_CONFIG_DIR" not in os.environ:
        os.environ["KAGGLE_CONFIG_DIR"] = str(kaggle_dir)
    
    return True


def find_csv_file(output_path: Path, competition: str) -> Optional[Path]:
    """
    尋找符合格式的 CSV 檔案
    
    Args:
        output_path: 搜尋目錄
        competition: 競賽名稱
    
    Returns:
        找到的 CSV 檔案路徑，如果沒找到則返回 None
    """
    # 優先匹配帶時間戳記的格式（例如：titanic-publicleaderboard-2025-11-13T03_49_49.csv）
    patterns = [
        f"{competition}-publicleaderboard-*.csv",  # 帶時間戳記的格式
        f"{competition}-publicleaderboard.csv",   # 不帶時間戳記的格式
        f"{competition}-leaderboard-*.csv",
        f"{competition}-leaderboard.csv",
    ]
    
    for pattern in patterns:
        matches = list(output_path.glob(pattern))
        if matches:
            # 如果有多個匹配，選擇最新的（時間戳記最大的）
            csv_file = max(matches, key=lambda p: p.stat().st_mtime)
            return csv_file
    
    # 如果還是沒找到，搜尋所有 CSV 檔案
    csv_files = list(output_path.glob("*.csv"))
    if csv_files:
        # 選擇最新的 CSV 檔案
        return max(csv_files, key=lambda p: p.stat().st_mtime)
    
    return None


def validate_csv_file(csv_file: Path) -> bool:
    """
    驗證 CSV 檔案格式是否正確（包含必要的欄位）
    
    Args:
        csv_file: CSV 檔案路徑
    
    Returns:
        True 如果格式正確，False 否則
    """
    try:
        df = pd.read_csv(csv_file, nrows=1)  # 只讀取第一行來檢查欄位
        # 檢查是否包含分數相關的欄位
        score_columns = ['Score', 'score', 'Public Score', 'Private Score']
        has_score_column = any(col in df.columns for col in score_columns)
        return has_score_column
    except Exception:
        return False


def download_leaderboard(competition: str, output_dir: str = "./leaderboards") -> Optional[pd.DataFrame]:
    """
    從 Kaggle 下載競賽的 leaderboard 數據
    
    流程：
    1. 檢查是否已有符合格式的 CSV 檔案，如果有且格式正確則直接使用
    2. 檢查是否已有 zip 檔案，如果有則解壓縮
    3. 如果都沒有，才進行下載
    
    Args:
        competition: 競賽名稱（例如 'titanic'）
        output_dir: 輸出目錄
    
    Returns:
        DataFrame 包含 leaderboard 數據，如果失敗則返回 None
    """
    try:
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # 步驟 1：檢查是否已有符合格式的 CSV 檔案
        print(f"\n🔍 檢查是否已有 {competition} 競賽的 leaderboard CSV 檔案...")
        csv_file = find_csv_file(output_path, competition)
        
        if csv_file and csv_file.exists():
            print(f"📄 找到現有的 CSV 檔案：{csv_file.name}")
            if validate_csv_file(csv_file):
                print("✅ CSV 檔案格式正確，直接使用")
                df = pd.read_csv(csv_file)
                print(f"✅ 成功讀取 leaderboard，共 {len(df)} 筆記錄")
                print(f"📋 CSV 欄位：{', '.join(df.columns.tolist())}")
                return df
            else:
                print("⚠️  CSV 檔案格式不正確，將重新下載")
        
        # 步驟 2：檢查是否已有 zip 檔案
        zip_files = list(output_path.glob("*.zip"))
        if zip_files:
            zip_file = zip_files[0]  # 使用第一個找到的 zip 檔案
            print(f"📦 找到現有的壓縮檔：{zip_file.name}")
            print("📂 正在解壓縮...")
            
            try:
                with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                    zip_ref.extractall(output_path)
                
                # 再次檢查解壓縮後的 CSV 檔案
                csv_file = find_csv_file(output_path, competition)
                if csv_file and csv_file.exists():
                    if validate_csv_file(csv_file):
                        print(f"✅ 找到 CSV 檔案：{csv_file.name}")
                        df = pd.read_csv(csv_file)
                        print(f"✅ 成功讀取 leaderboard，共 {len(df)} 筆記錄")
                        print(f"📋 CSV 欄位：{', '.join(df.columns.tolist())}")
                        return df
            except zipfile.BadZipFile:
                print(f"⚠️  zip 檔案損壞，將重新下載")
            except Exception as e:
                print(f"⚠️  解壓縮時發生錯誤：{e}，將重新下載")
        
        # 步驟 3：如果都沒有，才進行下載
        print(f"\n📥 正在從 Kaggle 下載 {competition} 競賽的 leaderboard...")
        
        # 使用 Kaggle API 下載 leaderboard（會下載為 .zip 檔案）
        kaggle.api.competition_leaderboard_download(
            competition=competition,
            path=str(output_path),
            quiet=False
        )
        
        # 尋找下載的 .zip 檔案
        zip_files = list(output_path.glob("*.zip"))
        if not zip_files:
            print("⚠️  找不到下載的 .zip 檔案")
            return None
        
        zip_file = zip_files[0]  # 使用第一個找到的 zip 檔案
        print(f"📦 找到壓縮檔：{zip_file.name}")
        
        # 解壓縮 zip 檔案
        print("📂 正在解壓縮...")
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            zip_ref.extractall(output_path)
        
        # 尋找解壓縮後的 CSV 檔案
        csv_file = find_csv_file(output_path, competition)
        
        if csv_file and csv_file.exists():
            if validate_csv_file(csv_file):
                df = pd.read_csv(csv_file)
                print(f"✅ 成功讀取 leaderboard，共 {len(df)} 筆記錄")
                print(f"📋 CSV 欄位：{', '.join(df.columns.tolist())}")
                return df
            else:
                print("⚠️  CSV 檔案格式不正確")
        else:
            print("⚠️  找不到解壓縮後的 CSV 檔案")
            print(f"   在 {output_path} 中找到的檔案：")
            for f in output_path.iterdir():
                if f.is_file():
                    print(f"     - {f.name}")
            return None
            
    except zipfile.BadZipFile:
        print(f"❌ 無法讀取 zip 檔案：{zip_file}")
        return None
    except Exception as e:
        print(f"❌ 下載 leaderboard 時發生錯誤：{e}")
        import traceback
        traceback.print_exc()
        print("\n提示：")
        print("1. 確認競賽名稱正確（例如 'titanic' 或 'titanic-machine-learning-from-disaster'）")
        print("2. 確認已正確設定 Kaggle API 認證")
        print("3. 某些競賽可能不提供公開 leaderboard")
        return None


def get_leaderboard_from_web(competition: str) -> Optional[pd.DataFrame]:
    """
    從 Kaggle 網頁手動取得 leaderboard（備用方法）
    
    注意：此方法需要手動操作或使用網頁爬蟲
    """
    print("\n📋 手動取得 leaderboard 的方法：")
    print(f"1. 前往 https://www.kaggle.com/competitions/{competition}/leaderboard")
    print("2. 在網頁上查看或複製 leaderboard 數據")
    print("3. 將數據儲存為 CSV 檔案")
    print("\n或者使用以下 Python 腳本（需要安裝 requests 和 BeautifulSoup）：")
    print("""
import requests
from bs4 import BeautifulSoup
import pandas as pd

url = f"https://www.kaggle.com/competitions/{competition}/leaderboard"
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')
# 解析 HTML 並提取 leaderboard 數據
# ...（需要根據實際網頁結構調整）
    """)
    return None


def calculate_medal(score: float, df: pd.DataFrame, higher_is_better: bool = True) -> Tuple[str, float, int]:
    """
    計算分數對應的獎牌等級
    
    Args:
        score: 要檢查的分數
        df: leaderboard DataFrame，應包含 'Score' 欄位
        higher_is_better: True 表示分數越高越好（如 accuracy），False 表示越低越好（如 RMSE）
    
    Returns:
        (medal_type, percentile, rank) 元組
        medal_type: 'Gold', 'Silver', 'Bronze', 或 'No Medal'
        percentile: 排名百分比（0-100）
        rank: 排名（從 1 開始）
    """
    if 'Score' not in df.columns:
        # 嘗試其他可能的欄位名稱
        possible_cols = ['score', 'Public Score', 'Private Score', 'Score']
        score_col = None
        for col in possible_cols:
            if col in df.columns:
                score_col = col
                break
        
        if score_col is None:
            print("❌ 找不到分數欄位，可用的欄位：", df.columns.tolist())
            return 'Unknown', 0, 0
    else:
        score_col = 'Score'
    
    # 排序
    df_sorted = df.sort_values(score_col, ascending=not higher_is_better)
    
    # 計算排名
    if higher_is_better:
        better_scores = (df_sorted[score_col] >= score).sum()
    else:
        better_scores = (df_sorted[score_col] <= score).sum()
    
    rank = better_scores
    total = len(df_sorted)
    percentile = (1 - rank / total) * 100 if total > 0 else 0
    
    # 判斷獎牌
    if percentile >= 95:
        medal = 'Gold'
    elif percentile >= 90:
        medal = 'Silver'
    elif percentile >= 75:
        medal = 'Bronze'
    else:
        medal = 'No Medal'
    
    return medal, percentile, rank


def load_score_from_final_state(final_state_path: str) -> Optional[float]:
    """從 final_state.json 讀取分數"""
    try:
        with open(final_state_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 嘗試從不同位置取得分數
        score = None
        if 'submission_code_exec_result' in data:
            score = data['submission_code_exec_result'].get('score')
        elif 'ensemble_code_exec_result_1' in data:
            score = data['ensemble_code_exec_result_1'].get('score')
        elif 'best_score_2' in data:
            score = data['best_score_2']
        
        if score is not None:
            print(f"✅ 從 final_state.json 讀取分數：{score}")
            return score
        else:
            print("⚠️  無法從 final_state.json 找到分數")
            return None
            
    except Exception as e:
        print(f"❌ 讀取 final_state.json 時發生錯誤：{e}")
        return None


def main():
    parser = argparse.ArgumentParser(
        description="檢查 Kaggle 競賽的獎牌等級",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
範例：
  # 使用分數直接檢查
  python check_medal.py --competition titanic --score 0.8156
  
  # 從 final_state.json 讀取分數
  python check_medal.py --competition titanic --final-state workspace/Titanic/final_state.json
  
  # 指定分數越高越好（預設）
  python check_medal.py --competition titanic --score 0.8156 --higher-is-better
  
  # 指定分數越低越好（如 RMSE）
  python check_medal.py --competition california-housing-prices --score 50000 --lower-is-better
        """
    )
    
    parser.add_argument(
        '--competition',
        type=str,
        required=True,
        help='Kaggle 競賽名稱（例如：titanic）'
    )
    
    parser.add_argument(
        '--score',
        type=float,
        help='要檢查的分數'
    )
    
    parser.add_argument(
        '--final-state',
        type=str,
        help='final_state.json 檔案路徑'
    )
    
    parser.add_argument(
        '--higher-is-better',
        action='store_true',
        default=True,
        help='分數越高越好（如 accuracy），預設為 True'
    )
    
    parser.add_argument(
        '--lower-is-better',
        action='store_true',
        help='分數越低越好（如 RMSE），會覆蓋 --higher-is-better'
    )
    
    parser.add_argument(
        '--leaderboard-file',
        type=str,
        help='本地 leaderboard CSV 檔案路徑（跳過下載）'
    )
    
    args = parser.parse_args()
    
    # 處理分數方向
    higher_is_better = not args.lower_is_better if args.lower_is_better else args.higher_is_better
    
    # 取得分數
    score = args.score
    if not score and args.final_state:
        score = load_score_from_final_state(args.final_state)
    
    if score is None:
        print("❌ 請提供 --score 或 --final-state 參數")
        parser.print_help()
        sys.exit(1)
    
    # 取得 leaderboard
    df = None
    if args.leaderboard_file:
        print(f"\n📂 從本地檔案讀取 leaderboard：{args.leaderboard_file}")
        try:
            df = pd.read_csv(args.leaderboard_file)
            print(f"✅ 成功讀取，共 {len(df)} 筆記錄")
        except Exception as e:
            print(f"❌ 讀取檔案時發生錯誤：{e}")
            sys.exit(1)
    else:
        if not setup_kaggle_api():
            print("\n💡 提示：您也可以手動下載 leaderboard CSV 檔案，然後使用 --leaderboard-file 參數")
            sys.exit(1)
        
        df = download_leaderboard(args.competition)
        
        if df is None:
            print("\n💡 備用方案：")
            get_leaderboard_from_web(args.competition)
            print("\n或者手動下載 leaderboard CSV 後，使用 --leaderboard-file 參數")
            sys.exit(1)
    
    # 計算獎牌
    print(f"\n📊 分析分數：{score}")
    print(f"分數方向：{'越高越好' if higher_is_better else '越低越好'}")
    
    medal, percentile, rank = calculate_medal(score, df, higher_is_better)
    
    # 顯示結果
    print("\n" + "="*60)
    print("🏆 獎牌檢查結果")
    print("="*60)
    print(f"分數：{score}")
    print(f"排名：第 {rank} 名（共 {len(df)} 名參賽者）")
    print(f"百分位數：{percentile:.2f}%")
    print(f"獎牌等級：{medal}")
    
    if medal == 'Gold':
        print("🎉 恭喜！您獲得了金牌！")
    elif medal == 'Silver':
        print("🥈 恭喜！您獲得了銀牌！")
    elif medal == 'Bronze':
        print("🥉 恭喜！您獲得了銅牌！")
    else:
        print("💪 繼續努力！")
        if percentile >= 50:
            print(f"   您已經超越了 {percentile:.1f}% 的參賽者！")
    
    print("="*60)
    
    # 顯示獎牌門檻
    print("\n📋 獎牌門檻：")
    print("  金牌：前 5%")
    print("  銀牌：前 10%（不含金牌）")
    print("  銅牌：前 25%（不含金牌和銀牌）")


if __name__ == "__main__":
    main()

