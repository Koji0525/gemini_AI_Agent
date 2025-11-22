import logging
import os
import datetime
from typing import List, Dict, Any

# ロギング設定のグローバル変数
LOG_FILE = "integration_test_log.log"

class TestResult:
    """単一のテストケースの結果を保持するデータ構造"""
    def __init__(self, name: str, success: bool, message: str = ""):
        self.name = name
        self.success = success
        self.message = message
        self.timestamp = datetime.datetime.now().isoformat()

    def __repr__(self):
        status = "PASS" if self.success else "FAIL"
        return f"[{status}] {self.name}: {self.message}"

def setup_logging(log_file: str = LOG_FILE) -> logging.Logger:
    """
    アプリケーションのロギングを設定します。
    コンソールとファイルの両方にログを出力します。
    """
    # 既存のロガーが存在すれば、ハンドラをクリアして再設定
    logger = logging.getLogger(__name__)
    if logger.handlers:
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
        logger.propagate = False # 重複ログを避ける

    logger.setLevel(logging.INFO)

    # フォーマット設定
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # コンソールハンドラ
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # ファイルハンドラ
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # ログが親ロガーに伝播しないようにする (これにより、二重出力の可能性を減らす)
    logger.propagate = False
    return logger

class TestReportGenerator:
    """
    テスト結果のリストからレポートを生成するクラス。
    マークダウン形式で整形されたレポートを出力します。
    """
    def __init__(self, results: List[TestResult]):
        self.results = results

    def get_total_count(self) -> int:
        """総テスト数を取得する"""
        return len(self.results)

    def get_success_count(self) -> int:
        """成功したテスト数を取得する"""
        return sum(1 for r in self.results if r.success)

    def get_failure_count(self) -> int:
        """失敗したテスト数を取得する"""
        return sum(1 for r in self.results if not r.success)

    def get_success_rate(self) -> float:
        """テストの成功率を計算する"""
        total = self.get_total_count()
        if total == 0:
            return 0.0
        return (self.get_success_count() / total) * 100

    def generate_markdown_report(self) -> str:
        """
        テスト結果をマークダウン形式のレポートとして生成する。
        """
        report_lines = []
        report_lines.append("# 統合テスト結果レポート")
        report_lines.append(f"生成日時: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append("\n---")

        # サマリー
        total_tests = self.get_total_count()
        successful_tests = self.get_success_count()
        failed_tests = self.get_failure_count()
        success_rate = self.get_success_rate()

        report_lines.append("## テストサマリー")
        report_lines.append(f"- **合計テスト数**: {total_tests}")
        report_lines.append(f"- **成功テスト数**: {successful_tests}")
        report_lines.append(f"- **失敗テスト数**: {failed_tests}")
        report_lines.append(f"- **成功率**: {success_rate:.2f}%")

        if success_rate >= 85.0:
            report_lines.append("\n**全体評価**: ✅ 成功基準 (85%以上の成功率) を達成しました。")
        else:
            report_lines.append(f"\n**全体評価**: ❌ 成功基準 (85%以上の成功率) を達成できませんでした。(現在の成功率: {success_rate:.2f}%)")

        report_lines.append("\n## テスト詳細")
        report_lines.append("| ステータス | テスト名 | メッセージ |")
        report_lines.append("|---|---|---|")

        for result in self.results:
            status_icon = "✅" if result.success else "❌"
            message_safe = result.message.replace('|', '\\|') # マークダウンテーブル内でパイプをエスケープ
            report_lines.append(f"| {status_icon} | `{result.name}` | {message_safe} |")

        # 失敗したテストのセクション
        failure_results = [r for r in self.results if not r.success]
        if failure_results:
            report_lines.append("\n## 失敗したテスト")
            for result in failure_results:
                report_lines.append(f"- `❌ {result.name}`: {result.message}")
        else:
            report_lines.append("\n## 失敗したテスト")
            report_lines.append("- 全てのテストが成功しました。")

        report_lines.append("\n## 成功基準の確認")
        # 成功基準1: 全テストで85%以上の成功率
        report_lines.append(f"- **全テストで85%以上の成功率を達成**: {'✅ 達成' if success_rate >= 85.0 else '❌ 未達成'}")
        
        # 成功基準2: F1-F10の全機能が正常に初期化される
        initialization_failures = [r for r in self.results if "Initialization" in r.name and not r.success]
        report_lines.append(f"- **F1-F10の全機能が正常に初期化される**: {'✅ 達成' if not initialization_failures else '❌ 未達成'}")
        if initialization_failures:
            report_lines.append("  - 失敗した初期化テスト:")
            for r in initialization_failures:
                report_lines.append(f"    - `{r.name}`: {r.message}")

        # 成功基準3: ナレッジシステムが正常に動作する
        knowledge_system_failures = [r for r in self.results if "F4_KnowledgeSystem" in r.name and not r.success]
        report_lines.append(f"- **ナレッジシステムが正常に動作する**: {'✅ 達成' if not knowledge_system_failures else '❌ 未達成'}")
        if knowledge_system_failures:
            report_lines.append("  - 失敗したナレッジシステムテスト:")
            for r in knowledge_system_failures:
                report_lines.append(f"    - `{r.name}`: {r.message}")

        # 成功基準4: テスト結果レポートが生成される
        # このレポート自体が生成されているので、これは常に達成済み
        report_lines.append("- **テスト結果レポートが生成される**: ✅ 達成")

        report_lines.append(f"\n詳細なログは `{LOG_FILE}` ファイルを参照してください。")

        return "\n".join(report_lines)