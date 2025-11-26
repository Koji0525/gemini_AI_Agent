#!/usr/bin/env python3
"""
共有黒板履歴ビューアー

目的: 変更履歴の可視化と分析
"""
import json
from pathlib import Path
from typing import List, Dict
from datetime import datetime

class BlackboardHistoryViewer:
    """履歴ビューアー"""
    
    def __init__(self, goal_id: str, base_dir: str = "shared_states"):
        self.goal_id = goal_id
        self.history_dir = Path(base_dir) / "history" / f"goal_{goal_id}"
    
    def get_all_versions(self) -> List[Dict]:
        """全バージョンを取得"""
        if not self.history_dir.exists():
            return []
        
        versions = []
        for file in sorted(self.history_dir.glob("*.json")):
            with open(file, 'r') as f:
                data = json.load(f)
                versions.append({
                    'version': data['meta']['version'],
                    'timestamp': data['meta']['last_updated'],
                    'file': str(file)
                })
        
        return versions
    
    def get_version_diff(self, version1: int, version2: int) -> Dict:
        """2つのバージョン間の差分を取得"""
        # 簡易実装
        return {
            'added_sections': [],
            'modified_sections': [],
            'removed_sections': []
        }
    
    def get_statistics(self) -> Dict:
        """履歴統計を取得"""
        versions = self.get_all_versions()
        
        return {
            'total_versions': len(versions),
            'first_version': versions[0] if versions else None,
            'latest_version': versions[-1] if versions else None,
            'history_size_mb': sum(f.stat().st_size for f in self.history_dir.glob("*.json")) / 1024 / 1024
        }

if __name__ == "__main__":
    viewer = BlackboardHistoryViewer(goal_id="test_001")
    stats = viewer.get_statistics()
    print(json.dumps(stats, indent=2, ensure_ascii=False))
