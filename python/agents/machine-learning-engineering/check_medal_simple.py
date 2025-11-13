"""
簡化版獎牌檢查工具 - 不需要 Kaggle API

適用於：
1. 手動輸入 leaderboard 數據
2. 從 CSV 檔案讀取 leaderboard
3. 快速計算排名和獎牌
"""

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import List, Tuple


def load_csv_leaderboard(csv_path: str) -> List[float]:
    """從 CSV 檔案讀取分數列表"""
    scores = []
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # 嘗試不同的欄位名稱
                for col in ['Score', 'score', 'Public Score', 'Private Score']:
                    if col in row and row[col]:
                        try:
                            scores.append(float(row[col]))
                            break
                        except ValueError:
                            continue
        return scores
    except Exception as e:
        print(f"❌ 讀取 CSV 時發生錯誤：{e}")
        return []


def calculate_medal_simple(score: float, scores: List[float], higher_is_better: bool = True) -> Tuple[str, float, int]:
    """
    計算獎牌等級（簡化版）
    
    Args:
        score: 要檢查的分數
        scores: 所有參賽者的分數列表
        higher_is_better: True 表示分數越高越好
    
    Returns:
        (medal_type, percentile, rank)
    """
    if not scores:
        return 'Unknown', 0, 0
    
    # 排序
    sorted_scores = sorted(scores, reverse=higher_is_better)
    
    # 計算排名
    if higher_is_better:
        rank = sum(1 for s in sorted_scores if s >= score)
    else:
        rank = sum(1 for s in sorted_scores if s <= score)
    
    total = len(sorted_scores)
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


def load_score_from_final_state(final_state_path: str) -> float:
    """從 final_state.json 讀取分數"""
    try:
        with open(final_state_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 嘗試從不同位置取得分數
        if 'submission_code_exec_result' in data:
            return data['submission_code_exec_result'].get('score')
        elif 'ensemble_code_exec_result_1' in data:
            return data['ensemble_code_exec_result_1'].get('score')
        elif 'best_score_2' in data:
            return data['best_score_2']
        
        return None
    except Exception as e:
        print(f"❌ 讀取 final_state.json 時發生錯誤：{e}")
        return None


def main():
    parser = argparse.ArgumentParser(
        description="簡化版獎牌檢查工具（不需要 Kaggle API）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
範例：
  # 從 CSV 檔案讀取 leaderboard
  python check_medal_simple.py --score 0.8156 --csv leaderboard.csv
  
  # 從 final_state.json 讀取分數
  python check_medal_simple.py --final-state final_state.json --csv leaderboard.csv
  
  # 手動輸入分數列表（用逗號分隔）
  python check_medal_simple.py --score 0.8156 --scores "0.82,0.81,0.80,0.79,0.78"
        """
    )
    
    parser.add_argument('--score', type=float, help='要檢查的分數')
    parser.add_argument('--final-state', type=str, help='final_state.json 檔案路徑')
    parser.add_argument('--csv', type=str, help='Leaderboard CSV 檔案路徑')
    parser.add_argument('--scores', type=str, help='分數列表（用逗號分隔）')
    parser.add_argument('--higher-is-better', action='store_true', default=True, help='分數越高越好')
    parser.add_argument('--lower-is-better', action='store_true', help='分數越低越好')
    
    args = parser.parse_args()
    
    # 處理分數方向
    higher_is_better = not args.lower_is_better if args.lower_is_better else args.higher_is_better
    
    # 取得要檢查的分數
    score = args.score
    if not score and args.final_state:
        score = load_score_from_final_state(args.final_state)
    
    if score is None:
        print("❌ 請提供 --score 或 --final-state 參數")
        parser.print_help()
        sys.exit(1)
    
    # 取得 leaderboard 分數
    scores = []
    
    if args.csv:
        print(f"📂 從 CSV 檔案讀取：{args.csv}")
        scores = load_csv_leaderboard(args.csv)
    elif args.scores:
        print("📝 從命令列讀取分數列表")
        try:
            scores = [float(s.strip()) for s in args.scores.split(',')]
        except ValueError:
            print("❌ 分數格式錯誤，請使用逗號分隔的數字")
            sys.exit(1)
    else:
        print("❌ 請提供 --csv 或 --scores 參數")
        parser.print_help()
        sys.exit(1)
    
    if not scores:
        print("❌ 無法讀取分數數據")
        sys.exit(1)
    
    print(f"✅ 讀取到 {len(scores)} 筆分數數據")
    
    # 計算獎牌
    print(f"\n📊 分析分數：{score}")
    print(f"分數方向：{'越高越好' if higher_is_better else '越低越好'}")
    
    medal, percentile, rank = calculate_medal_simple(score, scores, higher_is_better)
    
    # 顯示結果
    print("\n" + "="*60)
    print("🏆 獎牌檢查結果")
    print("="*60)
    print(f"分數：{score}")
    print(f"排名：第 {rank} 名（共 {len(scores)} 名參賽者）")
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
    
    # 顯示統計資訊
    sorted_scores = sorted(scores, reverse=higher_is_better)
    print(f"\n📈 Leaderboard 統計：")
    print(f"   最高分：{sorted_scores[0]:.4f}")
    print(f"   最低分：{sorted_scores[-1]:.4f}")
    print(f"   中位數：{sorted_scores[len(sorted_scores)//2]:.4f}")
    print(f"   平均分：{sum(scores)/len(scores):.4f}")


if __name__ == "__main__":
    main()

