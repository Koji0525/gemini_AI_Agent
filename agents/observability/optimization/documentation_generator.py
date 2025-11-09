"""
DocumentationGenerator - Phase 5.3 ドキュメント自動生成

【機能】
- APIドキュメントの自動生成
- ユーザーマニュアルのテンプレート作成
- トラブルシューティングガイド生成
"""

import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))


class DocumentationGenerator:
    """ドキュメント自動生成エンジン"""

    def __init__(self):
        self.docs_dir = project_root / "docs" / "observability"
        self.docs_dir.mkdir(parents=True, exist_ok=True)

        print("✅ DocumentationGenerator初期化完了")

    def generate_api_documentation(self) -> Dict[str, Any]:
        """APIドキュメントの生成"""

        api_docs = {
            "title": "Observability System API Documentation",
            "version": "1.0.0",
            "generated_at": datetime.now().isoformat(),
            "endpoints": [
                {
                    "path": "/api/traces/search",
                    "method": "GET",
                    "description": "トレースの検索",
                    "parameters": [
                        {
                            "name": "limit",
                            "type": "integer",
                            "default": 100,
                            "description": "取得件数",
                        }
                    ],
                    "response": {"type": "array", "items": "Trace object"},
                },
                {
                    "path": "/api/metrics/aggregate",
                    "method": "GET",
                    "description": "メトリクスの集計",
                    "parameters": [{"name": "metric_name", "type": "string", "required": True}],
                    "response": {"type": "object", "fields": ["metric_name", "value", "timestamp"]},
                },
                {
                    "path": "/api/intelligence/dashboard",
                    "method": "GET",
                    "description": "インテリジェンスダッシュボードデータの取得",
                    "response": {
                        "type": "object",
                        "fields": ["system_health", "pattern_insights", "recommendations"],
                    },
                },
            ],
            "examples": [
                {
                    "title": "トレース検索の例",
                    "code": "GET /api/traces/search?limit=50",
                    "response": "[{trace_id: ..., operation_name: ..., status: ...}, ...]",
                }
            ],
        }

        # ファイルに保存
        api_doc_file = self.docs_dir / "API_DOCUMENTATION.md"
        self._save_markdown_doc(api_doc_file, api_docs)

        return {
            "doc_type": "api_documentation",
            "file_path": str(api_doc_file),
            "endpoints_documented": len(api_docs["endpoints"]),
            "generated_at": api_docs["generated_at"],
        }

    def generate_user_manual(self) -> Dict[str, Any]:
        """ユーザーマニュアルの生成"""

        user_manual = {
            "title": "Observability System User Manual",
            "version": "1.0.0",
            "generated_at": datetime.now().isoformat(),
            "sections": [
                {
                    "title": "1. はじめに",
                    "content": "本システムは自律型AIエージェントシステムの可観測性を提供します。",
                },
                {
                    "title": "2. 基本的な使い方",
                    "subsections": [
                        {
                            "title": "2.1 ダッシュボードの起動",
                            "content": "python3 agents/autonomous/autonomous_orchestrator_v1.31.0_complete.py",
                        },
                        {
                            "title": "2.2 トレースの確認",
                            "content": "python3 agents/observability/cli/observability_cli.py traces",
                        },
                        {
                            "title": "2.3 統計の表示",
                            "content": "python3 agents/observability/cli/observability_cli.py stats",
                        },
                    ],
                },
                {
                    "title": "3. 高度な機能",
                    "subsections": [
                        {
                            "title": "3.1 故障分析",
                            "content": "Phase 4.1の機能を使用した自動故障検出",
                        },
                        {
                            "title": "3.2 予測分析",
                            "content": "Phase 4.2のリソース予測とコスト最適化",
                        },
                        {"title": "3.3 学習可視化", "content": "Phase 4.3のナレッジ成長追跡"},
                    ],
                },
                {
                    "title": "4. トラブルシューティング",
                    "content": "よくある問題と解決方法については別ドキュメント参照",
                },
            ],
        }

        # ファイルに保存
        manual_file = self.docs_dir / "USER_MANUAL.md"
        self._save_markdown_doc(manual_file, user_manual)

        return {
            "doc_type": "user_manual",
            "file_path": str(manual_file),
            "sections_count": len(user_manual["sections"]),
            "generated_at": user_manual["generated_at"],
        }

    def generate_troubleshooting_guide(self) -> Dict[str, Any]:
        """トラブルシューティングガイドの生成"""

        troubleshooting = {
            "title": "Observability System Troubleshooting Guide",
            "version": "1.0.0",
            "generated_at": datetime.now().isoformat(),
            "common_issues": [
                {
                    "issue": "データが表示されない",
                    "symptoms": ["ダッシュボードが空", "トレース数が0"],
                    "causes": ["ObservabilityManager未初期化", "トレース記録の失敗"],
                    "solutions": [
                        "initialize()が正しく呼ばれているか確認",
                        "record_trace()の呼び出しを確認",
                        "エラーログを確認",
                    ],
                },
                {
                    "issue": "Phase 4.3でデータ不足エラー",
                    "symptoms": ["insufficient_dataエラー", "0件のデータ"],
                    "causes": ["KnowledgeBase未統合", "トレースキーワード不一致"],
                    "solutions": [
                        "IntegratedLearningVisualizerを使用",
                        "KnowledgeBaseAdapterで統合",
                        "既存ナレッジのインポート実行",
                    ],
                },
                {
                    "issue": "性能が遅い",
                    "symptoms": ["クエリ時間>1秒", "UI応答遅延"],
                    "causes": ["大量データ", "インデックス未最適化"],
                    "solutions": [
                        "PerformanceOptimizerで最適化",
                        "サンプリング率の調整",
                        "古いデータのアーカイブ",
                    ],
                },
            ],
        }

        # ファイルに保存
        troubleshooting_file = self.docs_dir / "TROUBLESHOOTING.md"
        self._save_markdown_doc(troubleshooting_file, troubleshooting)

        return {
            "doc_type": "troubleshooting_guide",
            "file_path": str(troubleshooting_file),
            "issues_documented": len(troubleshooting["common_issues"]),
            "generated_at": troubleshooting["generated_at"],
        }

    def _save_markdown_doc(self, file_path: Path, content: Dict[str, Any]):
        """Markdown形式でドキュメントを保存"""

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(f"# {content.get('title', 'Document')}\n\n")
            f.write(f"**Version**: {content.get('version', '1.0.0')}\n")
            f.write(f"**Generated**: {content.get('generated_at', 'unknown')}\n\n")
            f.write("---\n\n")

            # セクションごとに出力
            if "sections" in content:
                for section in content["sections"]:
                    f.write(f"## {section.get('title', 'Section')}\n\n")
                    f.write(f"{section.get('content', '')}\n\n")

                    if "subsections" in section:
                        for sub in section["subsections"]:
                            f.write(f"### {sub.get('title', 'Subsection')}\n\n")
                            f.write(f"```\n{sub.get('content', '')}\n```\n\n")

            # エンドポイント情報
            if "endpoints" in content:
                f.write("## API Endpoints\n\n")
                for endpoint in content["endpoints"]:
                    f.write(f"### {endpoint.get('method', 'GET')} {endpoint.get('path', '/')}\n\n")
                    f.write(f"{endpoint.get('description', '')}\n\n")

            # 問題一覧
            if "common_issues" in content:
                f.write("## Common Issues\n\n")
                for issue in content["common_issues"]:
                    f.write(f"### {issue.get('issue', 'Issue')}\n\n")
                    f.write(f"**Symptoms**: {', '.join(issue.get('symptoms', []))}\n\n")
                    f.write(f"**Solutions**:\n")
                    for sol in issue.get("solutions", []):
                        f.write(f"- {sol}\n")
                    f.write("\n")

        print(f"✅ ドキュメント生成: {file_path}")


if __name__ == "__main__":
    print("🧪 DocumentationGenerator テスト")

    generator = DocumentationGenerator()

    print("\n【APIドキュメント生成】")
    api_doc = generator.generate_api_documentation()
    print(f"  生成ファイル: {api_doc.get('file_path')}")
    print(f"  エンドポイント数: {api_doc.get('endpoints_documented')}個")

    print("\n【ユーザーマニュアル生成】")
    manual = generator.generate_user_manual()
    print(f"  生成ファイル: {manual.get('file_path')}")
    print(f"  セクション数: {manual.get('sections_count')}個")

    print("\n【トラブルシューティングガイド生成】")
    troubleshooting = generator.generate_troubleshooting_guide()
    print(f"  生成ファイル: {troubleshooting.get('file_path')}")
    print(f"  問題数: {troubleshooting.get('issues_documented')}個")
