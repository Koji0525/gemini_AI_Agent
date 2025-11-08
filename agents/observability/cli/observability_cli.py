"""
ObservabilityCLI - コマンドラインインターフェース

【Phase 2.3: CLIツール拡張】
ターミナルから観測データにアクセス
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from agents.observability.observability_manager import \
    get_observability_manager
from agents.observability.visualization.timeline_view import TimelineView


class ObservabilityCLI:
    """観測基盤CLIツール"""

    def __init__(self):
        self.obs_manager = get_observability_manager()
        self.timeline_view = TimelineView()
        print("✅ ObservabilityCLI初期化完了")

    def cmd_stats(self, args):
        """統計表示コマンド"""
        print("━━━━━━━━━━━━━━━━━━━━━━━━")
        print("📊 観測基盤統計")
        print("━━━━━━━━━━━━━━━━━━━━━━━━")

        stats = self.obs_manager.get_comprehensive_stats()

        # トレース統計
        traces = stats.get("traces", {})
        print(f"\n【トレース】")
        print(f"  総数: {traces.get('total_traces', 0)}")
        print(f"  成功: {traces.get('success_count', 0)}")
        print(f"  エラー: {traces.get('error_count', 0)}")
        print(f"  成功率: {traces.get('success_rate', 0):.1%}")

        # オペレーション別統計
        op_stats = traces.get("operation_stats", {})
        if op_stats:
            print(f"\n【オペレーション別】")
            for op_name, op_data in op_stats.items():
                print(f"  {op_name}:")
                print(f"    実行数: {op_data['count']}")
                print(f"    成功: {op_data['success']}")
                print(f"    エラー: {op_data['error']}")

        # OpenTelemetry情報
        otel = stats.get("opentelemetry", {})
        print(f"\n【OpenTelemetry】")
        print(f"  利用可能: {otel.get('available', False)}")
        print(f"  サービス名: {otel.get('service_name', 'N/A')}")

        print("\n━━━━━━━━━━━━━━━━━━━━━━━━")

    def cmd_traces(self, args):
        """トレース検索コマンド"""
        print("━━━━━━━━━━━━━━━━━━━━━━━━")
        print("🔍 トレース検索")
        print("━━━━━━━━━━━━━━━━━━━━━━━━")

        kwargs = {}

        if args.operation:
            kwargs["operation_name"] = args.operation

        if args.status:
            kwargs["status"] = args.status

        if args.limit:
            kwargs["limit"] = args.limit

        traces = self.obs_manager.search_traces(**kwargs)

        print(f"\n検索結果: {len(traces)}件")

        if not traces:
            print("  （トレースデータがありません）")
        else:
            for i, trace in enumerate(traces[:10], 1):
                status_icon = "✅" if trace.get("status") == "success" else "❌"
                print(f"\n{i}. {status_icon} {trace.get('operation_name', 'unknown')}")
                print(f"   ID: {trace.get('trace_id', 'N/A')}")
                print(f"   時間: {trace.get('duration_ms', 0)}ms")
                print(f"   タイムスタンプ: {trace.get('timestamp', 'N/A')}")

        print("\n━━━━━━━━━━━━━━━━━━━━━━━━")

    def cmd_export(self, args):
        """データエクスポートコマンド"""
        print("━━━━━━━━━━━━━━━━━━━━━━━━")
        print("💾 データエクスポート")
        print("━━━━━━━━━━━━━━━━━━━━━━━━")

        stats = self.obs_manager.get_comprehensive_stats()

        output_path = (
            args.output or f"observability_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)

        print(f"\n✅ エクスポート完了: {output_path}")
        print(f"   ファイルサイズ: {Path(output_path).stat().st_size} bytes")
        print("\n━━━━━━━━━━━━━━━━━━━━━━━━")

    def cmd_metrics(self, args):
        """Prometheusメトリクスコマンド"""
        print("━━━━━━━━━━━━━━━━━━━━━━━━")
        print("📈 Prometheusメトリクス")
        print("━━━━━━━━━━━━━━━━━━━━━━━━")

        metrics_text = self.obs_manager.export_metrics_prometheus()

        if not metrics_text.strip():
            print("\n（メトリクスデータがありません）")
        else:
            print(f"\n{metrics_text}")

        print("\n━━━━━━━━━━━━━━━━━━━━━━━━")


def main():
    """CLIメイン関数"""
    parser = argparse.ArgumentParser(
        description="観測基盤CLIツール - Phase 2.3",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  # 統計表示
  python3 agents/observability/cli/observability_cli.py stats
  
  # トレース検索
  python3 agents/observability/cli/observability_cli.py traces --limit 5
  
  # データエクスポート
  python3 agents/observability/cli/observability_cli.py export --output data.json
  
  # Prometheusメトリクス
  python3 agents/observability/cli/observability_cli.py metrics
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="コマンド")

    # statsコマンド
    parser_stats = subparsers.add_parser("stats", help="統計表示")

    # tracesコマンド
    parser_traces = subparsers.add_parser("traces", help="トレース検索")
    parser_traces.add_argument("--operation", help="オペレーション名でフィルタ")
    parser_traces.add_argument(
        "--status", choices=["success", "error"], help="ステータスでフィルタ"
    )
    parser_traces.add_argument("--limit", type=int, default=100, help="最大取得件数")

    # exportコマンド
    parser_export = subparsers.add_parser("export", help="データエクスポート")
    parser_export.add_argument("--output", help="出力ファイルパス")

    # metricsコマンド
    parser_metrics = subparsers.add_parser("metrics", help="Prometheusメトリクス表示")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    cli = ObservabilityCLI()

    if args.command == "stats":
        cli.cmd_stats(args)
    elif args.command == "traces":
        cli.cmd_traces(args)
    elif args.command == "export":
        cli.cmd_export(args)
    elif args.command == "metrics":
        cli.cmd_metrics(args)


if __name__ == "__main__":
    main()
