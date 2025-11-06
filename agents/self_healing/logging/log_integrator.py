#!/usr/bin/env python3
"""
LogIntegrator: 複数のログソースを統合

全てのログシートからデータを取得し、タスクIDをキーに統合する。
AIが学習するための包括的なデータセットを構築。
"""
from datetime import datetime
from typing import Any, Dict, List, Optional


class IntegratedLog:
    """統合されたログデータ"""

    def __init__(self, task_id: str):
        self.task_id = task_id
        self.execution_logs: List[Dict] = []
        self.retry_logs: List[Dict] = []
        self.context_logs: List[Dict] = []
        self.feedback_logs: List[Dict] = []
        self.agent_info: Optional[Dict] = None

    def add_execution_log(self, log: Dict):
        """実行ログを追加"""
        self.execution_logs.append(log)

    def add_retry_log(self, log: Dict):
        """リトライログを追加"""
        self.retry_logs.append(log)

    def add_context_log(self, log: Dict):
        """コンテキストログを追加"""
        self.context_logs.append(log)

    def add_feedback_log(self, log: Dict):
        """フィードバックログを追加"""
        self.feedback_logs.append(log)

    def set_agent_info(self, info: Dict):
        """エージェント情報を設定"""
        self.agent_info = info

    def to_dict(self) -> Dict[str, Any]:
        """辞書形式に変換"""
        return {
            "task_id": self.task_id,
            "execution_logs": self.execution_logs,
            "retry_logs": self.retry_logs,
            "context_logs": self.context_logs,
            "feedback_logs": self.feedback_logs,
            "agent_info": self.agent_info,
            "summary": self._generate_summary(),
        }

    def _generate_summary(self) -> Dict[str, Any]:
        """サマリーを生成"""
        return {
            "total_executions": len(self.execution_logs),
            "total_retries": len(self.retry_logs),
            "total_contexts": len(self.context_logs),
            "total_feedbacks": len(self.feedback_logs),
            "has_agent_info": self.agent_info is not None,
            "success_rate": self._calculate_success_rate(),
            "avg_quality_score": self._calculate_avg_quality(),
        }

    def _calculate_success_rate(self) -> float:
        """成功率を計算"""
        if not self.execution_logs:
            return 0.0

        successes = sum(1 for log in self.execution_logs if log.get("status") == "completed")
        return (successes / len(self.execution_logs)) * 100

    def _calculate_avg_quality(self) -> float:
        """平均品質スコアを計算"""
        quality_scores = []
        for log in self.execution_logs:
            try:
                score = float(log.get("quality_score", 0))
                if score > 0:
                    quality_scores.append(score)
            except (ValueError, TypeError):
                pass

        return sum(quality_scores) / len(quality_scores) if quality_scores else 0.0


class LogIntegrator:
    """ログ統合システム"""

    # 統合するシート名
    SHEETS = {
        "execution": "task_execution_log",
        "retry": "retry_log",
        "context": "context_log",
        "feedback": "feedback_queue",
        "agent": "agent_registry",
    }

    def __init__(self, sheets_manager):
        """
        初期化

        Args:
            sheets_manager: GoogleSheetsManagerインスタンス
        """
        self.sheets_manager = sheets_manager
        #        # ✅ gc属性は使用しない（sheets_manager経由でアクセス）        # スプレッドシートIDを取得（環境変数から読み込み）
        import os

        self.spreadsheet_id = os.getenv("SPREADSHEET_ID", "")
        print("✅ LogIntegrator初期化完了")

    def _get_sheet(self, sheet_name: str):
        """
        シートを取得（sheets_manager経由）

        Args:
            sheet_name: シート名

        Returns:
            シートデータ（DataFrame形式） または None
        """
        try:
            # ✅ sheets_manager の標準メソッドを使用
            df = self.sheets_manager.read_sheet(sheet_name)
            return df
        except Exception as e:
            print(f"⚠️ シート取得エラー ({sheet_name}): {e}")
            return None

    async def load_all_logs(self) -> Dict[str, List[Dict]]:
        """
        全てのログシートからデータを読み込み

        Returns:
            シート名をキーとしたログデータの辞書
        """
        all_logs = {}

        print("📚 全ログシート読み込み中...")

        for log_type, sheet_name in self.SHEETS.items():
            sheet = self._get_sheet(sheet_name)

            if sheet:
                try:
                    records = sheet.get_all_records()
                    all_logs[log_type] = records
                    print(f"  ✅ {sheet_name}: {len(records)}件")
                except Exception as e:
                    print(f"  ⚠️ {sheet_name}: 読み込みエラー - {e}")
                    all_logs[log_type] = []
            else:
                print(f"  ⚠️ {sheet_name}: シートが見つかりません")
                all_logs[log_type] = []

        return all_logs

    async def integrate_by_task_id(self) -> Dict[str, IntegratedLog]:
        """
        タスクIDごとにログを統合

        Returns:
            タスクIDをキーとした統合ログの辞書
        """
        print("\n🔗 ログ統合処理開始...")

        # 全ログを読み込み
        all_logs = await self.load_all_logs()

        # タスクIDごとに統合
        integrated_logs = {}

        # 1. 実行ログから開始（メインソース）
        print("\n1️⃣  実行ログから統合開始...")
        for log in all_logs.get("execution", []):
            task_id = str(log.get("task_id", ""))
            if task_id and task_id != "":
                if task_id not in integrated_logs:
                    integrated_logs[task_id] = IntegratedLog(task_id)
                integrated_logs[task_id].add_execution_log(log)

        print(f"   ✅ {len(integrated_logs)}タスク検出")

        # 2. リトライログを追加
        print("\n2️⃣  リトライログを統合...")
        retry_count = 0
        for log in all_logs.get("retry", []):
            task_id = str(log.get("task_id", ""))
            if task_id in integrated_logs:
                integrated_logs[task_id].add_retry_log(log)
                retry_count += 1
        print(f"   ✅ {retry_count}件のリトライログを統合")

        # 3. コンテキストログを追加
        print("\n3️⃣  コンテキストログを統合...")
        context_count = 0
        for log in all_logs.get("context", []):
            task_id = str(log.get("task_id", ""))
            if task_id in integrated_logs:
                integrated_logs[task_id].add_context_log(log)
                context_count += 1
        print(f"   ✅ {context_count}件のコンテキストログを統合")

        # 4. フィードバックログを追加
        print("\n4️⃣  フィードバックログを統合...")
        feedback_count = 0
        for log in all_logs.get("feedback", []):
            task_id = str(log.get("task_id", ""))
            if task_id in integrated_logs:
                integrated_logs[task_id].add_feedback_log(log)
                feedback_count += 1
        print(f"   ✅ {feedback_count}件のフィードバックログを統合")

        # 5. エージェント情報を追加
        print("\n5️⃣  エージェント情報を統合...")
        agent_count = 0
        for log in all_logs.get("agent", []):
            log.get("agent_name", "")
            # エージェント名からタスクIDを推測（あれば）
            # 実際の紐付けロジックは要調整
            agent_count += 1
        print(f"   ✅ {agent_count}件のエージェント情報")

        print(f"\n✅ 統合完了: {len(integrated_logs)}タスク")
        return integrated_logs

    def clean_data(self, integrated_logs: Dict[str, IntegratedLog]) -> Dict[str, IntegratedLog]:
        """
        データクリーニング

        Args:
            integrated_logs: 統合ログ

        Returns:
            クリーニング済みログ
        """
        print("\n🧹 データクリーニング開始...")

        cleaned = {}
        removed_count = 0

        for task_id, log in integrated_logs.items():
            # 最低1つの実行ログがあるか確認
            if log.execution_logs:
                # 重複除去
                log.execution_logs = self._remove_duplicates(log.execution_logs)
                log.retry_logs = self._remove_duplicates(log.retry_logs)
                log.context_logs = self._remove_duplicates(log.context_logs)

                cleaned[task_id] = log
            else:
                removed_count += 1

        print(f"   ✅ クリーニング完了")
        print(f"   📊 有効データ: {len(cleaned)}タスク")
        print(f"   🗑️  削除データ: {removed_count}タスク")

        return cleaned

    def _remove_duplicates(self, logs: List[Dict]) -> List[Dict]:
        """重複を除去"""
        if not logs:
            return []

        seen = set()
        unique_logs = []

        for log in logs:
            # タイムスタンプとログIDで重複判定
            key = (log.get("timestamp", ""), log.get("log_id", ""))
            if key not in seen:
                seen.add(key)
                unique_logs.append(log)

        return unique_logs

    def get_statistics(self, integrated_logs: Dict[str, IntegratedLog]) -> Dict[str, Any]:
        """統計情報を取得"""
        total_executions = sum(len(log.execution_logs) for log in integrated_logs.values())
        total_retries = sum(len(log.retry_logs) for log in integrated_logs.values())
        total_contexts = sum(len(log.context_logs) for log in integrated_logs.values())

        # 成功率計算

        # 標準環境変数ローダー（自動追加）import sysfrom pathlib import Pathsys.path.insert(0, str(Path(__file__).parent.parent))from tools.env_loader import StandardEnvLoaderif not StandardEnvLoader.load_and_verify():    print("環境変数の読み込みに失敗しました")    sys.exit(1)
        success_count = 0
        total_count = 0
        for log in integrated_logs.values():
            for exec_log in log.execution_logs:
                total_count += 1
                if exec_log.get("status") == "completed":
                    success_count += 1

        success_rate = (success_count / total_count * 100) if total_count > 0 else 0

        return {
            "total_tasks": len(integrated_logs),
            "total_executions": total_executions,
            "total_retries": total_retries,
            "total_contexts": total_contexts,
            "overall_success_rate": round(success_rate, 2),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
