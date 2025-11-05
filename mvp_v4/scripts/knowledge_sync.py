"""
ナレッジベース自動同期システム

機能:
1. 複数アカウント/ブランチからナレッジを収集
2. 重複排除とマージ
3. 品質スコア順にソート
4. 自動Git同期
"""

import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
import subprocess


class KnowledgeSync:
    def __init__(
        self, main_kb_path: str = "mvp_v4/knowledge/learned/conversation_knowledge_v3.json"
    ):
        self.main_kb_path = Path(main_kb_path)
        self.main_kb_path.parent.mkdir(parents=True, exist_ok=True)

    def load_knowledge(self, path: str) -> List[Dict[str, Any]]:
        """ナレッジファイルを読み込み"""
        kb_path = Path(path)
        if not kb_path.exists():
            return []

        with open(kb_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        return data.get("knowledge_base", [])

    def calculate_hash(self, kb: Dict[str, Any]) -> str:
        """ナレッジのハッシュ値を計算（重複判定用）"""
        # シナリオと解決策からハッシュ生成
        content = f"{kb.get('scenario', '')}{kb.get('best_practice', '')}"
        return hashlib.md5(content.encode()).hexdigest()

    def merge_knowledge_bases(self, sources: List[str]) -> List[Dict[str, Any]]:
        """複数のナレッジベースをマージ"""
        all_knowledge = []
        seen_hashes = set()

        print(f"📥 {len(sources)}個のソースからナレッジ収集中...")

        for source in sources:
            kb_list = self.load_knowledge(source)
            print(f"  📂 {source}: {len(kb_list)}件")

            for kb in kb_list:
                kb_hash = self.calculate_hash(kb)

                if kb_hash not in seen_hashes:
                    seen_hashes.add(kb_hash)
                    all_knowledge.append(kb)

        print(f"✅ 重複排除後: {len(all_knowledge)}件")
        return all_knowledge

    def sort_by_quality(self, knowledge_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """品質スコア順にソート"""

        def get_quality_score(kb):
            # 成功率 × 信頼度 × 詳細度
            success_rate = kb.get("success_rate", 0.5)
            confidence = kb.get("confidence_score", 0.5)
            detail_score = len(kb.get("best_practice", "")) / 100  # 詳細度

            return success_rate * confidence * min(detail_score, 1.0)

        return sorted(knowledge_list, key=get_quality_score, reverse=True)

    def save_merged_knowledge(self, knowledge_list: List[Dict[str, Any]]):
        """マージしたナレッジを保存"""
        # 品質順にソート
        sorted_kb = self.sort_by_quality(knowledge_list)

        data = {
            "version": "3.0",
            "last_updated": datetime.now().isoformat(),
            "total_count": len(sorted_kb),
            "knowledge_base": sorted_kb,
        }

        with open(self.main_kb_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"💾 保存完了: {self.main_kb_path}")

    def auto_git_sync(self, commit_message: str = "Sync: ナレッジベース自動同期"):
        """Git自動同期"""
        try:
            # ステージング
            subprocess.run(["git", "add", str(self.main_kb_path)], check=True)

            # コミット
            subprocess.run(["git", "commit", "-m", commit_message], check=True)

            # プッシュ
            subprocess.run(["git", "push", "origin", "main"], check=True)

            print("✅ Git同期完了")
        except subprocess.CalledProcessError as e:
            print(f"⚠️  Git同期失敗: {e}")

    def sync_from_remote(self, remote_paths: List[str]):
        """リモートからナレッジを同期"""
        # まず最新をpull
        try:
            subprocess.run(["git", "pull", "origin", "main"], check=True)
            print("✅ 最新版をpull完了")
        except subprocess.CalledProcessError:
            print("⚠️  pull失敗（競合の可能性）")

        # ローカルのナレッジを含める
        all_sources = [str(self.main_kb_path)] + remote_paths

        # マージ
        merged_kb = self.merge_knowledge_bases(all_sources)

        # 保存
        self.save_merged_knowledge(merged_kb)

        # Git同期
        self.auto_git_sync(f"Sync: {len(merged_kb)}件のナレッジを統合")


if __name__ == "__main__":
    syncer = KnowledgeSync()

    # リモートパス例（実際のパスに変更）
    remote_sources = [
        # 他のブランチやアカウントのパスをここに追加
        # 'path/to/other/account/knowledge.json',
    ]

    syncer.sync_from_remote(remote_sources)
