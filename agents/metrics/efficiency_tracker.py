"""
開発効率測定システム
目的: 実際に効率が上がっているかを定量的に測定
"""
import time
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any


class EfficiencyTracker:
    """効率測定トラッカー"""
    
    def __init__(self):
        self.metrics_file = Path("agent_outputs/metrics/efficiency_metrics.json")
        self.metrics_file.parent.mkdir(parents=True, exist_ok=True)
        self.metrics = self._load_metrics()
    
    def _load_metrics(self) -> Dict:
        """既存メトリクスを読み込み"""
        if self.metrics_file.exists():
            with open(self.metrics_file, 'r') as f:
                return json.load(f)
        return {
            'operations': [],
            'total_time_saved': 0.0,
            'efficiency_multiplier': 1.0
        }
    
    def track_operation(
        self,
        operation_name: str,
        manual_time: float,
        automated_time: float,
        description: str = ""
    ):
        """
        操作を記録して効率化を測定
        
        Args:
            operation_name: 操作名
            manual_time: 手動で行った場合の時間（秒）
            automated_time: 自動化後の時間（秒）
            description: 詳細説明
        """
        time_saved = manual_time - automated_time
        efficiency = manual_time / automated_time if automated_time > 0 else 1.0
        
        operation = {
            'name': operation_name,
            'timestamp': datetime.now().isoformat(),
            'manual_time': manual_time,
            'automated_time': automated_time,
            'time_saved': time_saved,
            'efficiency_multiplier': efficiency,
            'description': description
        }
        
        self.metrics['operations'].append(operation)
        self.metrics['total_time_saved'] += time_saved
        
        # 平均効率倍率を計算
        if self.metrics['operations']:
            avg_efficiency = sum(
                op['efficiency_multiplier'] 
                for op in self.metrics['operations']
            ) / len(self.metrics['operations'])
            self.metrics['efficiency_multiplier'] = avg_efficiency
        
        self._save_metrics()
        
        print(f"\n📊 効率測定:")
        print(f"  操作: {operation_name}")
        print(f"  手動: {manual_time:.1f}秒")
        print(f"  自動: {automated_time:.1f}秒")
        print(f"  短縮: {time_saved:.1f}秒")
        print(f"  効率: {efficiency:.1f}倍")
        print(f"\n累計:")
        print(f"  総短縮時間: {self.metrics['total_time_saved']:.1f}秒 ({self.metrics['total_time_saved']/3600:.2f}時間)")
        print(f"  平均効率: {self.metrics['efficiency_multiplier']:.1f}倍")
    
    def _save_metrics(self):
        """メトリクスを保存"""
        with open(self.metrics_file, 'w') as f:
            json.dump(self.metrics, f, indent=2, ensure_ascii=False)
    
    def get_report(self) -> str:
        """効率化レポートを生成"""
        if not self.metrics['operations']:
            return "まだ測定データがありません"
        
        lines = []
        lines.append("=" * 60)
        lines.append("開発効率測定レポート")
        lines.append("=" * 60)
        lines.append(f"\n総操作数: {len(self.metrics['operations'])}回")
        lines.append(f"総短縮時間: {self.metrics['total_time_saved']:.1f}秒 ({self.metrics['total_time_saved']/3600:.2f}時間)")
        lines.append(f"平均効率倍率: {self.metrics['efficiency_multiplier']:.1f}倍")
        
        if self.metrics['efficiency_multiplier'] >= 10:
            lines.append("\n🎉 目標達成！10倍効率化を達成しました！")
        else:
            remaining = 10 - self.metrics['efficiency_multiplier']
            lines.append(f"\n⏳ 目標まであと {remaining:.1f}倍")
        
        lines.append("\n直近の操作:")
        for op in self.metrics['operations'][-5:]:
            lines.append(f"\n  {op['name']}")
            lines.append(f"    効率: {op['efficiency_multiplier']:.1f}倍")
            lines.append(f"    短縮: {op['time_saved']:.1f}秒")
        
        return "\n".join(lines)
