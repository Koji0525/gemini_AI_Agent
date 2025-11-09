#!/usr/bin/env python3
"""
運用ルールv1.2.4をナレッジシステムに登録するスクリプト
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core_agents.knowledge_manager_v2 import KnowledgeManagerV2


def register_development_rules():
    """開発運用ルールをナレッジシステムに登録"""

    km = KnowledgeManagerV2(
        db_path="knowledge_system/database/knowledge.db",
        index_path="knowledge_system/database/faiss_index/knowledge.index",
    )

    # ナレッジデータの定義 - 運用ルールv1.2.4
    knowledge_items = [
        # 1. 開発基本原則
        {
            "scenario": "AIコード生成時の品質確保とインデント破壊防止",
            "cause": "局所的な修正パッチによる構文エラーとインデント不整合",
            "solution": "全文修正の原則を徹底。3行以上の修正はファイル全体を確認し、必ず全文書き換えを行う。1000行を超えるファイルは即時分割。",
            "success_rate": 0.95,
            "confidence": 0.9,
            "category": "開発基本原則",
            "task_type": "code_quality",
        },
        {
            "scenario": "ファイルサイズによるAI出力精度低下",
            "cause": "1200行を超えるファイルでのAI処理能力限界",
            "solution": "1000行を超えた時点でファイル分割を検討。機能カテゴリごとに専用ディレクトリにパッケージ化。",
            "success_rate": 0.98,
            "confidence": 0.85,
            "category": "開発基本原則",
            "task_type": "code_organization",
        },
        # 2. バージョン管理
        {
            "scenario": "ファイルバージョン管理と重複防止",
            "cause": "手動コピーによるファイル散乱とバージョン混乱",
            "solution": "tools/file_version_manager.pyを使用した3ステップ標準化: 1.自動バックアップ作成 2.v06修正 3.本番昇格オプション",
            "success_rate": 0.98,
            "confidence": 0.95,
            "category": "バージョン管理",
            "task_type": "version_control",
        },
        {
            "scenario": "ブランチ管理と機能開発",
            "cause": "mainブランチでの直接開発によるコード汚染",
            "solution": "v1.0.0-feature形式のブランチ名を使用。動作確認後mainマージ。",
            "success_rate": 0.96,
            "confidence": 0.9,
            "category": "バージョン管理",
            "task_type": "git_workflow",
        },
        # 3. API連携問題
        {
            "scenario": "Google Sheets連携時のメソッド名不一致エラー",
            "cause": "推測によるメソッド名使用とAPI仕様確認不足",
            "solution": "SafeSheetsWrapper v2.4の必須使用。初期化時に自動API検証実行。safe_read/safe_append/safe_updateメソッドのみ使用。",
            "success_rate": 0.99,
            "confidence": 0.9,
            "category": "API連携",
            "task_type": "api_integration",
        },
        {
            "scenario": "新しいクラス/モジュール使用時のAPI不一致",
            "cause": "ドキュメント依存による実装仕様の誤認識",
            "solution": "使用前に必ず実行: python3 tools/api_validator.py <ClassName>。実装を直接確認。",
            "success_rate": 0.97,
            "confidence": 0.88,
            "category": "API連携",
            "task_type": "api_validation",
        },
        # 4. 環境設定保護
        {
            "scenario": ".envファイルの誤上書きによる設定破壊",
            "cause": "cat > .envによる全体上書きと保護設定不足",
            "solution": "EnvProtectorの使用必須。修正前のcat .env確認。chmod 444 .envでの読み取り専用化。sed/追記による部分修正のみ許可。",
            "success_rate": 0.97,
            "confidence": 0.85,
            "category": "環境設定",
            "task_type": "security",
        },
        {
            "scenario": "環境変数読み込み失敗による実行エラー",
            "cause": "load_dotenv()の直接使用とoverride設定不足",
            "solution": "StandardEnvLoader.load_and_verify()の必須使用。スクリプト先頭での実行確認。",
            "success_rate": 0.98,
            "confidence": 0.9,
            "category": "環境設定",
            "task_type": "environment_management",
        },
        # 5. エラー早期解決
        {
            "scenario": "同じエラーの繰り返し発生による開発遅延",
            "cause": "根本原因の切り分け不足と場当たり的対応",
            "solution": "なぜなぜ分析の実施（10個以上の原因列挙）。tools/integrated_diagnostics.py --auto-fixの活用。キャッシュクリアの徹底。",
            "success_rate": 0.9,
            "confidence": 0.8,
            "category": "問題解決",
            "task_type": "troubleshooting",
        },
        {
            "scenario": "ターミナルプロセス終了エラー",
            "cause": "exit 1によるターミナル全体終了",
            "solution": "exit 1禁止。関数内はreturn 1、それ以外はechoエラーのみ。全コマンドに || true 追加。Pythonではsys.exit()禁止。",
            "success_rate": 0.99,
            "confidence": 0.95,
            "category": "問題解決",
            "task_type": "error_handling",
        },
        # 6. セキュリティ対策
        {
            "scenario": "APIキー漏洩リスクと機密情報管理",
            "cause": ".envのGitコミット、ハードコード、不適切なバックアップ",
            "solution": "secure_backup.shの必須使用。.gitignore徹底。StandardEnvLoader強制。APIキー無効化フローの確立。",
            "success_rate": 0.99,
            "confidence": 0.95,
            "category": "セキュリティ",
            "task_type": "security",
        },
        # 7. 自動保護パターン
        {
            "scenario": "AI自律修正時のコード破壊リスク",
            "cause": "バックアップなしでの直接修正、影響分析の未実施",
            "solution": "修正前自動バックアップ + CodeImpactAnalyzer + リスクレベル判定。criticalリスク時は修正中止して人間報告。",
            "success_rate": 0.96,
            "confidence": 0.88,
            "category": "自動保護",
            "task_type": "ai_safety",
        },
        # 8. 設計原則
        {
            "scenario": "中核クラスの依存性管理問題",
            "cause": "クラス内でのリソース自己初期化",
            "solution": "依存性注入の原則徹底。TaskExecutor, PMAgentなどはリソースを引数で受け取るのみ。外部での初期化統一。",
            "success_rate": 0.94,
            "confidence": 0.85,
            "category": "設計原則",
            "task_type": "architecture",
        },
        {
            "scenario": "機能の単一責任原則違反",
            "cause": "複数機能の混在による検索性低下",
            "solution": "1ファイル1機能原則。依頼エージェントは依頼のみ、実行エージェントは実行のみ。結合度低下を常に意識。",
            "success_rate": 0.96,
            "confidence": 0.9,
            "category": "設計原則",
            "task_type": "software_design",
        },
        # 9. 横展開パターン
        {
            "scenario": "Wrapper設計によるAPI変更耐性",
            "cause": "直接API呼び出しによる変更影響の広範囲化",
            "solution": "SafeWrapperパターン + METHOD_ALIASESによる抽象化。API変更時はWrapperのみ修正で全コード対応可能。",
            "success_rate": 0.97,
            "confidence": 0.92,
            "category": "設計パターン",
            "task_type": "api_design",
        },
        {
            "scenario": "モード管理の標準化",
            "cause": "状態管理の分散による制御困難",
            "solution": "ConfigManager（設定一元化） + ModeController（実行モード制御） + StateManager（状態管理）の分離実装。",
            "success_rate": 0.95,
            "confidence": 0.88,
            "category": "設計パターン",
            "task_type": "system_design",
        },
        # 10. 出力形式とコピペ効率化
        {
            "scenario": "出力形式の不統一によるコピペ効率低下",
            "cause": "複数回のコピペが必要な出力形式",
            "solution": "1回のコピペで完了する形式で出力。作業番号と内容を明確に記載。複数タスクを同時実行可能な形式で提供。",
            "success_rate": 0.98,
            "confidence": 0.9,
            "category": "開発効率",
            "task_type": "workflow_optimization",
        },
        # 11. キャッシュ管理
        {
            "scenario": "キャッシュ残存による問題特定の長期化",
            "cause": "古いキャッシュが結果に影響し、問題特定が困難",
            "solution": "毎回のプログラム実行前に./scripts/clean_cache.shを実行。GitHub Actionsに自動キャッシュクリアを設定。",
            "success_rate": 0.97,
            "confidence": 0.85,
            "category": "開発環境",
            "task_type": "cache_management",
        },
        # 12. ファイル配置ルール
        {
            "scenario": "プロジェクト直下のファイル散乱",
            "cause": "便利ツールの直下配置による視認性悪化",
            "solution": ".shファイルはsh/フォルダ、.mdファイルはMD/フォルダに厳格に配置。プロジェクト直下のファイル数を最小化。",
            "success_rate": 0.96,
            "confidence": 0.88,
            "category": "プロジェクト管理",
            "task_type": "file_organization",
        },
    ]

    # ナレッジ登録実行
    registered_count = 0
    for knowledge in knowledge_items:
        try:
            result = km.register_knowledge(knowledge)
            if result:
                registered_count += 1
                print(f"✅ 登録完了: {knowledge['scenario'][:50]}...")
            else:
                print(f"❌ 登録失敗: {knowledge['scenario'][:50]}...")
        except Exception as e:
            print(f"❌ エラー: {knowledge['scenario'][:50]}... - {str(e)}")

    # ベクトルインデックス保存
    km.save_vector_index()

    print(f"\n🎯 ナレッジ登録完了: {registered_count}/{len(knowledge_items)}件")

    # 統計情報の表示
    stats = km.get_stats()
    print(f"\n📊 現在のナレッジ状況:")
    print(f"   総ナレッジ数: {stats['total_knowledge']}件")
    print(f"   平均信頼度: {stats.get('avg_confidence', 'N/A')}")
    print(f"   ベクトルモデル: {stats.get('vector_model', 'N/A')}")
    print(f"   インデックスサイズ: {stats.get('vector_index_size', 'N/A')}")


if __name__ == "__main__":
    register_development_rules()
