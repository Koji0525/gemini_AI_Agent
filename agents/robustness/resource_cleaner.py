"""
リソースクリーンアップシステム
ログ、古い成果物などを自動削除
"""

import sys
import os
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict

sys.path.insert(0, '/workspaces/gemini_AI_Agent')

class ResourceCleaner:
    """リソースクリーンアップ"""
    
    def __init__(self):
        self.project_root = Path("/workspaces/gemini_AI_Agent")
        
    def cleanup_all(self) -> Dict:
        """すべてのクリーンアップを実行"""
        print(f"\n{'=' * 80}")
        print(f"🧹 リソースクリーンアップ")
        print('=' * 80)
        print()
        
        results = {
            'logs_deleted': 0,
            'outputs_deleted': 0,
            'space_freed_mb': 0
        }
        
        # ログのクリーンアップ
        logs_result = self.cleanup_logs(days=3)
        results['logs_deleted'] = logs_result['deleted']
        
        # 古い成果物のクリーンアップ
        outputs_result = self.cleanup_old_outputs(days=7)
        results['outputs_deleted'] = outputs_result['deleted']
        
        # ディスク使用量を取得
        disk_usage = self.get_disk_usage()
        
        print()
        print("=" * 80)
        print(f"✅ クリーンアップ完了")
        print("=" * 80)
        print(f"  ログ削除: {results['logs_deleted']}個")
        print(f"  成果物削除: {results['outputs_deleted']}個")
        print(f"  ディスク使用率: {disk_usage['percent']:.1f}%")
        print("=" * 80)
        
        return results
    
    def cleanup_logs(self, days: int = 3) -> Dict:
        """古いログを削除"""
        print(f"  🗑️  ログクリーンアップ（{days}日以上前）")
        
        cutoff = datetime.now() - timedelta(days=days)
        deleted = 0
        
        logs_dir = self.project_root / "logs"
        
        if logs_dir.exists():
            for log_file in logs_dir.glob("*.log"):
                if log_file.stat().st_mtime < cutoff.timestamp():
                    size_mb = log_file.stat().st_size / (1024 * 1024)
                    log_file.unlink()
                    print(f"     - {log_file.name} ({size_mb:.1f}MB)")
                    deleted += 1
        
        print(f"     ✅ {deleted}個のログを削除")
        
        return {'deleted': deleted}
    
    def cleanup_old_outputs(self, days: int = 7) -> Dict:
        """古い成果物を削除"""
        print(f"  🗑️  成果物クリーンアップ（{days}日以上前）")
        
        cutoff = datetime.now() - timedelta(days=days)
        deleted = 0
        
        outputs_dir = self.project_root / "agent_outputs" / "implementation"
        
        if outputs_dir.exists():
            for output_dir in outputs_dir.glob("*/"):
                # ディレクトリの更新日時をチェック
                if output_dir.stat().st_mtime < cutoff.timestamp():
                    # サイズを計算
                    size_mb = sum(
                        f.stat().st_size 
                        for f in output_dir.rglob("*") 
                        if f.is_file()
                    ) / (1024 * 1024)
                    
                    shutil.rmtree(output_dir)
                    print(f"     - {output_dir.name} ({size_mb:.1f}MB)")
                    deleted += 1
        
        print(f"     ✅ {deleted}個の成果物を削除")
        
        return {'deleted': deleted}
    
    def get_disk_usage(self) -> Dict:
        """ディスク使用量を取得"""
        import psutil
        
        disk = psutil.disk_usage(str(self.project_root))
        
        return {
            'total_gb': disk.total / (1024**3),
            'used_gb': disk.used / (1024**3),
            'free_gb': disk.free / (1024**3),
            'percent': disk.percent
        }
    
    def get_memory_usage(self) -> Dict:
        """メモリ使用量を取得"""
        import psutil
        
        memory = psutil.virtual_memory()
        
        return {
            'total_gb': memory.total / (1024**3),
            'used_gb': memory.used / (1024**3),
            'available_gb': memory.available / (1024**3),
            'percent': memory.percent
        }

