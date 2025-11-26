#!/usr/bin/env python3
"""
テスト成功率監視スクリプト

目的: 既存テストの成功率を監視し、84.3%を下回らないようにする
実行頻度: 開発時に随時
所要時間: 約5分
"""
import subprocess
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List

# 定数
PROJECT_ROOT = Path(__file__).parent.parent.parent
HISTORY_FILE = PROJECT_ROOT / "shared_states/diagnostics/test_history.json"
THRESHOLD = 84.3  # 成功率基準

def run_tests() -> Dict:
    """
    既存テストを実行して結果を取得
    
    Returns:
        {
            'timestamp': '2025-11-26T10:00:00',
            'passed': 84,
            'failed': 16,
            'total': 100,
            'success_rate': 84.0
        }
    """
    print("🧪 テスト実行中...")
    
    # 既存テストのみ実行（統合テストは除外）
    result = subprocess.run(
        [
            "pytest", 
            "tests/", 
            "--ignore=tests/integration/",
            "--tb=no", 
            "-q"
        ],
        capture_output=True,
        text=True,
        cwd=PROJECT_ROOT
    )
    
    output = result.stdout + result.stderr
    
    # 結果をパース
    passed = 0
    failed = 0
    
    # "84 passed" のようなパターンを検索
    passed_match = re.search(r'(\d+) passed', output)
    if passed_match:
        passed = int(passed_match.group(1))
    
    # "16 failed" のようなパターンを検索
    failed_match = re.search(r'(\d+) failed', output)
    if failed_match:
        failed = int(failed_match.group(1))
    
    total = passed + failed
    success_rate = (passed / total * 100) if total > 0 else 0
    
    return {
        'timestamp': datetime.now().isoformat(),
        'passed': passed,
        'failed': failed,
        'total': total,
        'success_rate': round(success_rate, 1)
    }

def load_history() -> List[Dict]:
    """履歴を読み込み"""
    if not HISTORY_FILE.exists():
        return []
    
    with open(HISTORY_FILE, 'r') as f:
        return json.load(f)

def save_history(history: List[Dict]):
    """履歴を保存（直近100件のみ）"""
    # 直近100件のみ保持
    history = history[-100:]
    
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=2)

def check_degradation(current: Dict, history: List[Dict]) -> bool:
    """
    品質劣化を検出
    
    Returns:
        True: 劣化検出、False: 正常
    """
    has_issue = False
    
    # 基準値チェック
    if current['success_rate'] < THRESHOLD:
        print(f"\n❌ アラート: テスト成功率が基準値を下回りました")
        print(f"   現在: {current['success_rate']}%")
        print(f"   基準: {THRESHOLD}%")
        print(f"   失敗テスト: {current['failed']}件")
        has_issue = True
    
    # トレンドチェック（履歴がある場合）
    if len(history) >= 2:
        prev = history[-1]
        diff = current['success_rate'] - prev['success_rate']
        
        if diff < -5:  # 5%以上の急激な低下
            print(f"\n⚠️  警告: テスト成功率が急激に低下しました")
            print(f"   変化: {diff:+.1f}%")
            print(f"   前回: {prev['success_rate']}%")
            print(f"   今回: {current['success_rate']}%")
            has_issue = True
    
    return has_issue

def analyze_trend(history: List[Dict]):
    """トレンド分析"""
    if len(history) < 5:
        print("\n📈 トレンド分析: データ不足（5件以上必要）")
        return
    
    recent = history[-5:]
    rates = [h['success_rate'] for h in recent]
    
    avg = sum(rates) / len(rates)
    max_rate = max(rates)
    min_rate = min(rates)
    
    print(f"\n📈 トレンド分析（直近5回）:")
    print(f"   平均: {avg:.1f}%")
    print(f"   最高: {max_rate:.1f}%")
    print(f"   最低: {min_rate:.1f}%")
    print(f"   変動: {max_rate - min_rate:.1f}%")
    
    # 傾向判定
    if rates[-1] > rates[0]:
        print(f"   傾向: ✅ 改善傾向")
    elif rates[-1] < rates[0]:
        print(f"   傾向: ⚠️  悪化傾向")
    else:
        print(f"   傾向: → 横ばい")

def main():
    """メイン処理"""
    print("="*60)
    print("📊 テスト成功率監視")
    print("="*60)
    
    # テスト実行
    current = run_tests()
    
    # 履歴読み込み
    history = load_history()
    
    # 結果表示
    print(f"\n📝 実行結果:")
    print(f"   成功: {current['passed']}/{current['total']}")
    print(f"   失敗: {current['failed']}/{current['total']}")
    print(f"   成功率: {current['success_rate']}%")
    print(f"   基準値: {THRESHOLD}%")
    
    if current['success_rate'] >= THRESHOLD:
        print(f"   判定: ✅ 基準値クリア")
    else:
        print(f"   判定: ❌ 基準値未達")
    
    # 品質劣化チェック
    has_degradation = check_degradation(current, history)
    
    # トレンド分析
    if history:
        analyze_trend(history)
    
    # 履歴に追加して保存
    history.append(current)
    save_history(history)
    
    print(f"\n📄 履歴保存: {HISTORY_FILE}")
    print(f"   履歴件数: {len(history)}")
    
    print(f"\n{'='*60}")
    if has_degradation:
        print("❌ 品質劣化が検出されました")
        print("="*60)
        return 1
    else:
        print("✅ 監視完了")
        print("="*60)
        return 0

if __name__ == "__main__":
    exit(main())
