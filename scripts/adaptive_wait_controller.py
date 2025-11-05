"""
適応的待機時間コントローラー
タスク密度に応じて1-5分で可変調整
要件定義書v3.0 Section 4.2.1準拠
"""

class AdaptiveWaitController:
    """待機時間の動的調整"""
    
    def __init__(self):
        """初期化"""
        self.target_cycle_time = 180  # 目標3分（180秒）
        self.min_wait = 60            # 最小1分
        self.max_wait = 300           # 最大5分
    
    def calculate_wait_time(self, pending_count, last_cycle_time):
        """
        待機時間を計算
        
        Args:
            pending_count: pending状態のタスク数
            last_cycle_time: 前回のサイクル実行時間（秒）
        
        Returns:
            int: 待機時間（秒）
        """
        # タスク密度による基本待機時間
        if pending_count >= 10:
            base_wait = 60   # 1分（大量タスク）
        elif pending_count >= 5:
            base_wait = 120  # 2分（中程度）
        elif pending_count >= 1:
            base_wait = 180  # 3分（標準）
        else:
            base_wait = 300  # 5分（タスクなし）
        
        # サイクル実行時間による調整
        # 前回が遅かった場合は待機時間を延ばす
        if last_cycle_time > 10:  # 10秒以上かかった
            adjustment = min(60, last_cycle_time * 2)  # 最大60秒延長
            adjusted_wait = base_wait + adjustment
        else:
            adjusted_wait = base_wait
        
        # 範囲制限
        final_wait = max(self.min_wait, min(self.max_wait, adjusted_wait))
        
        print(f"⏱️  待機時間計算: pending={pending_count}, cycle={last_cycle_time:.1f}s → {final_wait}s")
        return final_wait
    
    def get_daily_cycle_estimate(self, avg_wait_time):
        """
        1日のサイクル数を推定
        
        Args:
            avg_wait_time: 平均待機時間（秒）
        
        Returns:
            int: 1日のサイクル数
        """
        minutes_per_day = 1440
        avg_wait_minutes = avg_wait_time / 60
        cycles_per_day = int(minutes_per_day / avg_wait_minutes)
        return cycles_per_day

# テスト用コード
if __name__ == "__main__":
    controller = AdaptiveWaitController()
    
    print("🧪 AdaptiveWaitControllerテスト")
    print("=" * 60)
    
    # テストケース
    test_cases = [
        {"pending": 15, "cycle_time": 5.0, "expected_range": (60, 120)},
        {"pending": 7, "cycle_time": 8.0, "expected_range": (120, 180)},
        {"pending": 2, "cycle_time": 6.0, "expected_range": (180, 240)},
        {"pending": 0, "cycle_time": 3.0, "expected_range": (300, 300)},
        {"pending": 5, "cycle_time": 15.0, "expected_range": (150, 180)},  # 遅いサイクル
    ]
    
    for i, case in enumerate(test_cases, 1):
        wait_time = controller.calculate_wait_time(case["pending"], case["cycle_time"])
        expected_min, expected_max = case["expected_range"]
        
        if expected_min <= wait_time <= expected_max:
            status = "✅"
        else:
            status = "❌"
        
        print(f"{status} テスト{i}: pending={case['pending']}, cycle={case['cycle_time']}s")
        print(f"   結果: {wait_time}s (期待: {expected_min}-{expected_max}s)")
    
    # 1日のサイクル数推定
    print("\n📊 1日のサイクル数推定:")
    for avg_wait in [60, 120, 180, 240, 300]:
        cycles = controller.get_daily_cycle_estimate(avg_wait)
        print(f"  平均待機{avg_wait}s（{avg_wait/60:.0f}分）→ {cycles}サイクル/日")
    
    print("\n✅ テスト完了")

