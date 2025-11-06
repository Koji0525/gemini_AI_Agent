"""
ナレッジベース同期ツール
新規タブ起動時に自動的にナレッジを同期
"""
import json
import os
from pathlib import Path
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


class KnowledgeSync:
    """ナレッジベースの同期管理"""
    
    def __init__(self):
        self.knowledge_files = [
            'mvp_v4/knowledge/learned/conversation_knowledge_v3.json',
            'mvp_v4/knowledge/learned/conversation_knowledge_v4.json'
        ]
        self.sync_cache_file = '.knowledge_sync_cache.json'
    
    def sync_all(self) -> Dict[str, int]:
        """すべてのナレッジファイルを同期"""
        stats = {
            'total_knowledge': 0,
            'files_synced': 0,
            'errors': []
        }
        
        for file_path in self.knowledge_files:
            try:
                if os.path.exists(file_path):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        
                        if isinstance(data, list):
                            count = len(data)
                        elif isinstance(data, dict):
                            count = len(data.get('knowledge_base', []))
                        else:
                            count = 0
                        
                        stats['total_knowledge'] += count
                        stats['files_synced'] += 1
                        logger.info(f"✅ 同期完了: {file_path} ({count}件)")
            
            except Exception as e:
                error_msg = f"❌ {file_path}: {str(e)}"
                stats['errors'].append(error_msg)
                logger.error(error_msg)
        
        # キャッシュに保存
        self._save_cache(stats)
        
        return stats
    
    def get_cached_stats(self) -> Dict[str, int]:
        """キャッシュされた統計情報を取得"""
        try:
            if os.path.exists(self.sync_cache_file):
                with open(self.sync_cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"⚠️ キャッシュ読み込みエラー: {e}")
        
        return {'total_knowledge': 0, 'files_synced': 0}
    
    def _save_cache(self, stats: Dict[str, int]):
        """統計情報をキャッシュに保存"""
        try:
            with open(self.sync_cache_file, 'w', encoding='utf-8') as f:
                json.dump(stats, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.warning(f"⚠️ キャッシュ保存エラー: {e}")
    
    def auto_sync_on_startup(self):
        """起動時の自動同期"""
        logger.info("🔄 ナレッジベース自動同期開始...")
        stats = self.sync_all()
        
        logger.info("=" * 60)
        logger.info("📊 ナレッジベース同期完了")
        logger.info("=" * 60)
        logger.info(f"📚 総ナレッジ数: {stats['total_knowledge']}件")
        logger.info(f"📁 同期ファイル数: {stats['files_synced']}個")
        
        if stats['errors']:
            logger.warning(f"⚠️ エラー: {len(stats['errors'])}件")
            for error in stats['errors']:
                logger.warning(f"  {error}")
        
        logger.info("=" * 60)
        
        return stats


def sync_knowledge_on_startup():
    """起動時の自動同期（簡易版）"""
    sync = KnowledgeSync()
    return sync.auto_sync_on_startup()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    sync_knowledge_on_startup()
