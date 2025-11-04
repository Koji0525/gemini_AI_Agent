#!/usr/bin/env python3
"""
学習サイクル実行スクリプト
ナレッジベースを活用した継続的な学習と改善提案を生成
"""
import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agents.self_healing.logging.similarity_search_engine import SimilaritySearchEngine
from agents.self_healing.self_learning.intelligent_feedback import IntelligentFeedbackGenerator
from agents.self_healing.logging.knowledge_base_manager import KnowledgeBaseManager
from configuration.config_loader import get_config
from tools.sheets_manager import GoogleSheetsManager


async def run_learning_cycle():
    """学習サイクルを実行"""
    print("=" * 60)
    print("🧠 学習サイクル開始")
    print(f"⏰ 実行時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    try:
        # 1. 設定読み込み
        config = get_config()

        # 2. GoogleSheetsManager初期化
        # 重要: 引数名は他のスクリプト（monitor.py, task_breakdown.py）と統一
        sheets_manager = GoogleSheetsManager(
            spreadsheet_id=config.get("SPREADSHEET_ID"),
            service_account_file=config.get("SERVICE_ACCOUNT_FILE"),  # ← 修正: credentials_file → service_account_file
        )

        # 3. 各コンポーネント初期化
        kb_manager = KnowledgeBaseManager(sheets_manager=sheets_manager)
        search_engine = SimilaritySearchEngine(kb_manager)
        feedback_gen = IntelligentFeedbackGenerator(kb_manager, search_engine)

        # 4. システム健全性分析
        print("\n📊 システム健全性分析中...")
        health_data = feedback_gen.analyze_system_health()

        print(f"📊 健全性スコア: {health_data['health_score']}/100")
        print(f"ステータス: {health_data['status']}")

        if health_data["issues"]:
            print("⚠️ 検出された問題:")
            for i, issue in enumerate(health_data["issues"], 1):
                print(f"   {i}. {issue}")

        # 5. フィードバック生成（ナレッジベース活用）
        print("\n💡 改善提案生成中...")
        feedback_proposals = feedback_gen.generate_feedback_from_knowledge(limit=5)

        if feedback_proposals:
            print(f"\n✅ {len(feedback_proposals)}件の改善提案を生成しました:")
            for i, proposal in enumerate(feedback_proposals, 1):
                print(f"\n--- 提案 {i} ---")
                print(f"タイトル: {proposal.title}")
                print(f"優先度: {proposal.priority} (1=最高)")
                print(f"カテゴリ: {proposal.category}")
                print(f"影響度: {proposal.estimated_impact}")
                print(f"信頼度: {proposal.confidence:.2f}")
                print(f"説明: {proposal.description}")
                if proposal.actionable_steps:
                    print("実行ステップ:")
                    for step in proposal.actionable_steps:
                        print(f"  • {step}")
        else:
            print("ℹ️ 現時点で新しい改善提案はありません。")

        # 6. 完了レポート
        print("\n" + "=" * 60)
        print("✅ 学習サイクル完了")
        print(f"📊 システム健全性スコア: {health_data['health_score']}/100")
        print(f"ステータス: {health_data['status']}")
        print("=" * 60)

        return True

    except Exception as e:
        print(f"\n❌ エラー発生: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(run_learning_cycle())
    sys.exit(0 if success else 1)
