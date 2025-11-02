#!/usr/bin/env python3
"""
システム診断ツール
24時間自律開発システムの問題を包括的に診断
"""
import sys

sys.path.insert(0, ".")

from tools.sheets_manager_v02_mapped import GoogleSheetsManager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SystemDiagnostics:
    """システム診断"""

    def __init__(self):
        self.sheets = GoogleSheetsManager()
        self.issues = []

    def check_task_execution_log(self):
        """task_execution_logシートの確認"""
        logger.info("\n【診断1: task_execution_logシート】")

        try:
            data = self.sheets.read_range("task_execution_log")

            if not data or len(data) <= 1:
                self.issues.append(
                    {
                        "category": "ログ記録",
                        "severity": "HIGH",
                        "issue": "task_execution_logにデータが記録されていない",
                        "cause": "TaskCoordinatorからのログ書き込みが動作していない",
                        "solution": "TaskCoordinatorのlog_execution()呼び出しを確認",
                    }
                )
                logger.warning("❌ ログが記録されていません")
            else:
                logger.info(f"✅ ログレコード: {len(data)-1}件")

                # 最新のログを確認
                latest = data[-1] if len(data) > 1 else []
                if latest:
                    logger.info(f"   最新ログ: {latest[:3]}")

        except Exception as e:
            self.issues.append(
                {
                    "category": "ログ記録",
                    "severity": "CRITICAL",
                    "issue": f"task_execution_logシートへのアクセスエラー: {e}",
                    "cause": "シートが存在しないか、権限がない",
                    "solution": "シートを作成するか、権限を確認",
                }
            )
            logger.error(f"❌ エラー: {e}")

    def check_pm_tasks_status(self):
        """pm_tasksシートのステータス更新確認"""
        logger.info("\n【診断2: pm_tasksシート】")

        try:
            data = self.sheets.read_range("pm_tasks")

            if not data or len(data) <= 1:
                self.issues.append(
                    {
                        "category": "タスク管理",
                        "severity": "HIGH",
                        "issue": "pm_tasksにタスクが存在しない",
                        "cause": "PM Agentがタスクを生成していない",
                        "solution": "PM Agentの実行を確認",
                    }
                )
                logger.warning("❌ タスクが存在しません")
            else:
                logger.info(f"✅ タスク数: {len(data)-1}件")

                # ステータス別の集計
                statuses = {}
                for row in data[1:]:
                    if len(row) > 3:
                        status = row[3] if len(row) > 3 else "unknown"
                        statuses[status] = statuses.get(status, 0) + 1

                logger.info(f"   ステータス: {statuses}")

                # completedがない場合は問題
                if "completed" not in statuses:
                    self.issues.append(
                        {
                            "category": "タスク実行",
                            "severity": "MEDIUM",
                            "issue": "completedステータスのタスクがない",
                            "cause": "タスクが実行されていない、またはステータス更新が動作していない",
                            "solution": "TaskCoordinatorのupdate_task_status()を確認",
                        }
                    )

        except Exception as e:
            self.issues.append(
                {
                    "category": "タスク管理",
                    "severity": "CRITICAL",
                    "issue": f"pm_tasksシートへのアクセスエラー: {e}",
                    "solution": "シートを作成するか、権限を確認",
                }
            )
            logger.error(f"❌ エラー: {e}")

    def check_project_goal_integration(self):
        """project_goalシートの統合確認"""
        logger.info("\n【診断3: project_goal統合】")

        try:
            data = self.sheets.read_range("project_goal")

            if not data or len(data) <= 1:
                self.issues.append(
                    {
                        "category": "目標管理",
                        "severity": "MEDIUM",
                        "issue": "project_goalにゴールが設定されていない",
                        "cause": "ゴールの初期設定が未実施",
                        "solution": "ゴール設定スクリプトを実行",
                    }
                )
                logger.warning("❌ ゴールが設定されていません")
            else:
                logger.info(f"✅ ゴール数: {len(data)-1}件")

                # 最新のゴールを確認
                latest = data[-1] if len(data) > 1 else []
                if latest and len(latest) > 0:
                    logger.info(f"   最新ゴール: {latest[0][:50]}...")

                # PM Agentとの連携を確認
                # TODO: PM Agentがproject_goalを読み取っているか確認
                self.issues.append(
                    {
                        "category": "目標管理",
                        "severity": "HIGH",
                        "issue": "project_goal→タスク分解の自動化が未実装",
                        "cause": "PM Agentがproject_goalを監視していない",
                        "solution": "GoalMonitorとPM Agentの連携を実装",
                    }
                )

        except Exception as e:
            logger.error(f"❌ エラー: {e}")

    def check_decision_support_integration(self):
        """DecisionSupportSystemの統合確認"""
        logger.info("\n【診断4: 自動修正提案の統合】")

        try:
            from agents.self_healing.logging.decision_support_system import DecisionSupportSystem
            from agents.self_healing.logging.knowledge_base_manager import KnowledgeBaseManager

            kb = KnowledgeBaseManager(self.sheets)
            DecisionSupportSystem(self.sheets, kb)

            logger.info("✅ DecisionSupportSystem初期化成功")

            # TaskCoordinatorとの統合確認
            # TODO: TaskCoordinator v02でDSSが使われているか確認
            self.issues.append(
                {
                    "category": "自己修復",
                    "severity": "MEDIUM",
                    "issue": "DecisionSupportSystemがメインフローに統合されていない可能性",
                    "cause": "TaskCoordinator v02の初期化でdecision_supportが渡されていない",
                    "solution": "IntegratedOrchestratorとTaskCoordinatorの連携を確認",
                }
            )

        except Exception as e:
            self.issues.append(
                {
                    "category": "自己修復",
                    "severity": "CRITICAL",
                    "issue": f"DecisionSupportSystem初期化エラー: {e}",
                    "solution": "インポートと依存関係を確認",
                }
            )
            logger.error(f"❌ エラー: {e}")

    def check_learning_integration(self):
        """学習データ活用の確認"""
        logger.info("\n【診断5: 学習データ活用】")

        try:
            kb_data = self.sheets.read_range("knowledge_base")

            if not kb_data or len(kb_data) <= 1:
                self.issues.append(
                    {
                        "category": "学習",
                        "severity": "MEDIUM",
                        "issue": "knowledge_baseにデータが蓄積されていない",
                        "cause": "SelfLearningPipelineが実行されていない",
                        "solution": "6時間ごとの自動学習が動作しているか確認",
                    }
                )
                logger.warning("❌ 学習データなし")
            else:
                logger.info(f"✅ ナレッジ数: {len(kb_data)-1}件")

                # 最近の学習を確認
                recent = kb_data[-5:] if len(kb_data) > 5 else kb_data[1:]
                logger.info(f"   最近の学習: {len(recent)}件")

        except Exception as e:
            logger.error(f"❌ エラー: {e}")

    def generate_report(self):
        """診断レポート生成"""
        logger.info("\n" + "=" * 60)
        logger.info("📊 診断レポート")
        logger.info("=" * 60)

        if not self.issues:
            logger.info("✅ 問題は検出されませんでした")
            return

        # 重要度別に分類
        critical = [i for i in self.issues if i["severity"] == "CRITICAL"]
        high = [i for i in self.issues if i["severity"] == "HIGH"]
        medium = [i for i in self.issues if i["severity"] == "MEDIUM"]

        logger.info(f"\n🚨 CRITICAL: {len(critical)}件")
        for issue in critical:
            logger.info(f"  [{issue['category']}] {issue['issue']}")
            logger.info(f"    原因: {issue.get('cause', 'N/A')}")
            logger.info(f"    対策: {issue['solution']}")

        logger.info(f"\n⚠️  HIGH: {len(high)}件")
        for issue in high:
            logger.info(f"  [{issue['category']}] {issue['issue']}")
            logger.info(f"    対策: {issue['solution']}")

        logger.info(f"\n💡 MEDIUM: {len(medium)}件")
        for issue in medium:
            logger.info(f"  [{issue['category']}] {issue['issue']}")

        logger.info("\n" + "=" * 60)
        logger.info(f"�� 合計: {len(self.issues)}件の問題を検出")
        logger.info("=" * 60)

        return self.issues


def main():
    """メイン実行"""
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🔍 24時間自律開発システム 診断開始")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    diag = SystemDiagnostics()

    # 各診断を実行
    diag.check_task_execution_log()
    diag.check_pm_tasks_status()
    diag.check_project_goal_integration()
    diag.check_decision_support_integration()
    diag.check_learning_integration()

    # レポート生成
    issues = diag.generate_report()

    # JSONで保存
    import json

    with open("logs/system_diagnosis.json", "w", encoding="utf-8") as f:
        json.dump(issues, f, indent=2, ensure_ascii=False)

    print("\n✅ 診断レポートを logs/system_diagnosis.json に保存")


if __name__ == "__main__":
    main()
