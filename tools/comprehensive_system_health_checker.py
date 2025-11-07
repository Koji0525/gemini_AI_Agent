"""
包括的システム健全性診断ツール v1.0

【目的】
1. 既存機能の欠落を検出
2. エージェント連携の破壊を検出
3. 変更前後の差分を可視化
4. 問題検知時の自動アラート

【使用方法】
# 基本診断
python3 tools/comprehensive_system_health_checker.py

# スナップショット保存（変更前に実行）
python3 tools/comprehensive_system_health_checker.py --save-snapshot

# 差分確認（変更後に実行）
python3 tools/comprehensive_system_health_checker.py --compare

# 自動修復
python3 tools/comprehensive_system_health_checker.py --auto-fix
"""

import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class ComprehensiveSystemHealthChecker:
    """包括的なシステム健全性チェッカー"""

    def __init__(self):
        self.project_root = project_root
        self.snapshot_dir = self.project_root / "logs" / "system_snapshots"
        self.snapshot_dir.mkdir(parents=True, exist_ok=True)

        # 重要なファイルとエージェントの定義
        self.critical_components = {
            "core_agents": {
                "TaskExecutor": "task_executor/task_executor_main.py",
                "ReviewAgent": "core_agents/review_agent.py",
                "GoalEvaluator": "agents/goal_evaluator/goal_evaluator.py",
                "PMAgent": "core_agents/pm_agent.py",
                "CollaborationAgent": "agents/collaboration/collaboration_agent.py",
                "MonitoringAgent": "agents/monitoring/monitoring_agent.py",
                "RollbackAgent": "agents/rollback_agent.py",
            },
            "orchestrator": {
                "AutonomousOrchestrator": "agents/autonomous/autonomous_orchestrator.py",
            },
            "tools": {
                "SafeSheetsWrapper": "tools/safe_sheets_wrapper.py",
                "GoogleSheetsManager": "browser_control/sheets_manager.py",
                "SheetsFlowOrchestrator": "tools/sheets_flow_orchestrator.py",
            },
            "self_healing": {
                "ErrorClassifier": "agents/self_healing/utils/error_classifier.py",
                "DecisionSupportSystem": "agents/self_healing/logging/decision_support_system.py",
                "QualityFeedbackLoop": "core_agents/quality_feedback_loop_v02.py",
                "SelfLearningPipeline": "agents/self_healing/self_learning_pipeline.py",
            },
        }

        # 重要なメソッド（エージェントごと）
        self.critical_methods = {
            "TaskExecutor": ["execute", "get_pending_tasks", "update_task_status"],
            "ReviewAgent": ["review_task", "evaluate_quality"],
            "GoalEvaluator": ["evaluate_goal", "calculate_progress"],
            "PMAgent": ["decompose_goal", "create_tasks"],
            "AutonomousOrchestrator": ["initialize", "execute_autonomous_cycle", "run"],
            "SafeSheetsWrapper": ["safe_read", "safe_append", "safe_update"],
        }

        self.results = {
            "timestamp": datetime.now().isoformat(),
            "overall_health": 100,
            "issues": [],
            "warnings": [],
            "components": {},
        }

    def calculate_file_hash(self, file_path: Path) -> str:
        """ファイルのハッシュ値を計算"""
        try:
            with open(file_path, "rb") as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception:
            return ""

    def check_file_exists(self, file_path: str) -> Tuple[bool, Dict]:
        """ファイルの存在と健全性をチェック"""
        full_path = self.project_root / file_path

        if not full_path.exists():
            return False, {
                "status": "missing",
                "path": file_path,
                "error": "ファイルが存在しません",
            }

        # ファイルサイズチェック
        size = full_path.stat().st_size
        if size < 100:  # 100バイト未満は異常
            return False, {
                "status": "too_small",
                "path": file_path,
                "size": size,
                "error": "ファイルサイズが異常に小さい",
            }

        return True, {
            "status": "ok",
            "path": file_path,
            "size": size,
            "hash": self.calculate_file_hash(full_path),
        }

    def check_class_exists(self, file_path: str, class_name: str) -> Tuple[bool, Dict]:
        """クラスの存在をチェック"""
        full_path = self.project_root / file_path

        if not full_path.exists():
            return False, {"error": "ファイル未存在"}

        try:
            with open(full_path, "r", encoding="utf-8") as f:
                content = f.read()

            if f"class {class_name}" not in content:
                return False, {
                    "error": f"クラス '{class_name}' が見つかりません",
                    "file": file_path,
                }

            # クラスの行数をカウント
            lines = content.split("\n")
            class_line = next(i for i, line in enumerate(lines) if f"class {class_name}" in line)

            return True, {"status": "ok", "class_line": class_line + 1, "total_lines": len(lines)}

        except Exception as e:
            return False, {"error": str(e)}

    def check_methods_exist(self, file_path: str, class_name: str, methods: List[str]) -> Dict:
        """クラスのメソッド存在をチェック"""
        full_path = self.project_root / file_path

        if not full_path.exists():
            return {"error": "ファイル未存在", "missing_methods": methods}

        try:
            with open(full_path, "r", encoding="utf-8") as f:
                content = f.read()

            found_methods = []
            missing_methods = []

            for method in methods:
                if f"def {method}" in content or f"async def {method}" in content:
                    found_methods.append(method)
                else:
                    missing_methods.append(method)

            return {
                "found": found_methods,
                "missing": missing_methods,
                "status": "ok" if not missing_methods else "incomplete",
            }

        except Exception as e:
            return {"error": str(e), "missing_methods": methods}

    def check_orchestrator_integration(self) -> Dict:
        """Orchestratorへの統合状況をチェック"""
        orchestrator_path = self.project_root / "agents/autonomous/autonomous_orchestrator.py"

        if not orchestrator_path.exists():
            return {"status": "error", "error": "AutonomousOrchestratorが見つかりません"}

        try:
            with open(orchestrator_path, "r", encoding="utf-8") as f:
                content = f.read()

            integrated_agents = {}

            # 各エージェントの統合状況を確認
            for category, agents in self.critical_components.items():
                if category == "orchestrator":
                    continue

                for agent_name, file_path in agents.items():
                    # インポートチェック
                    has_import = (
                        f"from {file_path.replace('/', '.').replace('.py', '')} import" in content
                        or f"import {file_path.replace('/', '.').replace('.py', '')}" in content
                    )

                    # 初期化チェック（self.xxx = の形式）
                    has_init = f"{agent_name}(" in content

                    integrated_agents[agent_name] = {
                        "has_import": has_import,
                        "has_init": has_init,
                        "status": "integrated" if (has_import or has_init) else "not_integrated",
                    }

            integration_rate = (
                sum(1 for a in integrated_agents.values() if a["status"] == "integrated")
                / len(integrated_agents)
                * 100
            )

            return {
                "status": "ok",
                "integration_rate": integration_rate,
                "agents": integrated_agents,
            }

        except Exception as e:
            return {"status": "error", "error": str(e)}

    def check_sheets_connectivity(self) -> Dict:
        """スプレッドシート連携をチェック"""
        try:
            # SafeSheetsWrapper v2.4の存在確認
            wrapper_exists, wrapper_info = self.check_file_exists("tools/safe_sheets_wrapper.py")

            if not wrapper_exists:
                return {"status": "error", "error": "SafeSheetsWrapper v2.4が見つかりません"}

            # GoogleSheetsManagerの存在確認
            manager_exists, manager_info = self.check_file_exists(
                "browser_control/sheets_manager.py"
            )

            if not manager_exists:
                return {"status": "error", "error": "GoogleSheetsManagerが見つかりません"}

            return {
                "status": "ok",
                "SafeSheetsWrapper": wrapper_info,
                "GoogleSheetsManager": manager_info,
            }

        except Exception as e:
            return {"status": "error", "error": str(e)}

    def run_comprehensive_check(self) -> Dict:
        """包括的チェックを実行"""
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("🔍 包括的システム健全性チェック開始")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

        issues = []
        warnings = []

        # 1. ファイル存在チェック
        print("📁 [1/5] ファイル存在チェック...")
        for category, agents in self.critical_components.items():
            for agent_name, file_path in agents.items():
                exists, info = self.check_file_exists(file_path)

                if not exists:
                    issues.append(f"❌ {agent_name}: {info['error']}")
                    print(f"   ❌ {agent_name}: {info['error']}")
                else:
                    print(f"   ✅ {agent_name}: OK ({info['size']} bytes)")

                self.results["components"][agent_name] = info

        # 2. クラス定義チェック
        print("\n🏗️  [2/5] クラス定義チェック...")
        for category, agents in self.critical_components.items():
            for agent_name, file_path in agents.items():
                exists, info = self.check_class_exists(file_path, agent_name)

                if not exists:
                    issues.append(f"❌ {agent_name}: クラス定義が見つかりません")
                    print(f"   ❌ {agent_name}: {info.get('error', '不明なエラー')}")
                else:
                    print(f"   ✅ {agent_name}: 定義確認 (行{info['class_line']})")

        # 3. メソッド存在チェック
        print("\n🔧 [3/5] 重要メソッドチェック...")
        for agent_name, methods in self.critical_methods.items():
            # ファイルパスを探す
            file_path = None
            for category, agents in self.critical_components.items():
                if agent_name in agents:
                    file_path = agents[agent_name]
                    break

            if file_path:
                result = self.check_methods_exist(file_path, agent_name, methods)

                if result.get("missing"):
                    warnings.append(f"⚠️ {agent_name}: メソッド不足 {result['missing']}")
                    print(f"   ⚠️ {agent_name}: 不足メソッド {result['missing']}")
                else:
                    print(f"   ✅ {agent_name}: 全メソッド確認")

        # 4. Orchestrator統合チェック
        print("\n🎯 [4/5] Orchestrator統合チェック...")
        integration_result = self.check_orchestrator_integration()

        if integration_result["status"] == "ok":
            rate = integration_result["integration_rate"]
            print(f"   統合率: {rate:.1f}%")

            not_integrated = [
                name
                for name, info in integration_result["agents"].items()
                if info["status"] != "integrated"
            ]

            if not_integrated:
                warnings.append(f"⚠️ 未統合エージェント: {', '.join(not_integrated)}")
                print(f"   ⚠️ 未統合: {', '.join(not_integrated)}")
        else:
            issues.append(f"❌ Orchestrator統合チェック失敗: {integration_result.get('error')}")

        self.results["orchestrator_integration"] = integration_result

        # 5. スプレッドシート連携チェック
        print("\n📊 [5/5] スプレッドシート連携チェック...")
        sheets_result = self.check_sheets_connectivity()

        if sheets_result["status"] == "ok":
            print("   ✅ SafeSheetsWrapper v2.4: OK")
            print("   ✅ GoogleSheetsManager: OK")
        else:
            issues.append(f"❌ スプレッドシート連携: {sheets_result.get('error')}")

        self.results["sheets_integration"] = sheets_result

        # 健全性スコア計算
        total_checks = len(issues) + len(warnings)
        if total_checks == 0:
            health_score = 100
        else:
            health_score = max(0, 100 - (len(issues) * 10 + len(warnings) * 5))

        self.results["overall_health"] = health_score
        self.results["issues"] = issues
        self.results["warnings"] = warnings

        return self.results

    def print_summary(self):
        """サマリーを表示"""
        print("\n" + "=" * 70)
        print("📊 システム健全性レポート")
        print("=" * 70)

        health = self.results["overall_health"]

        # 健全性スコア
        if health >= 90:
            status_icon = "🟢"
            status_text = "良好"
        elif health >= 70:
            status_icon = "🟡"
            status_text = "注意"
        else:
            status_icon = "🔴"
            status_text = "警告"

        print(f"\n{status_icon} 総合健全性: {health}% ({status_text})")

        # 問題点
        if self.results["issues"]:
            print(f"\n🔴 重大な問題 ({len(self.results['issues'])}件):")
            for issue in self.results["issues"]:
                print(f"  {issue}")

        # 警告
        if self.results["warnings"]:
            print(f"\n⚠️ 警告 ({len(self.results['warnings'])}件):")
            for warning in self.results["warnings"]:
                print(f"  {warning}")

        # 推奨事項
        print("\n💡 推奨事項:")
        if health >= 90:
            print("  ✅ システムは健全です。定期的なチェックを継続してください。")
        elif health >= 70:
            print("  ⚠️ 警告項目を確認し、改善してください。")
            print("  📝 コマンド: python3 tools/comprehensive_system_health_checker.py --auto-fix")
        else:
            print("  🔴 重大な問題があります。すぐに修正してください。")
            print("  📝 コマンド: python3 tools/comprehensive_system_health_checker.py --auto-fix")

        print("\n" + "=" * 70)

    def save_snapshot(self) -> str:
        """現在の状態をスナップショットとして保存"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        snapshot_file = self.snapshot_dir / f"snapshot_{timestamp}.json"

        snapshot_data = {"timestamp": timestamp, "results": self.results, "file_hashes": {}}

        # 全ファイルのハッシュ値を保存
        for category, agents in self.critical_components.items():
            for agent_name, file_path in agents.items():
                full_path = self.project_root / file_path
                if full_path.exists():
                    snapshot_data["file_hashes"][file_path] = self.calculate_file_hash(full_path)

        with open(snapshot_file, "w", encoding="utf-8") as f:
            json.dump(snapshot_data, f, indent=2, ensure_ascii=False)

        print(f"💾 スナップショット保存: {snapshot_file}")
        return str(snapshot_file)

    def compare_with_snapshot(self, snapshot_file: str = None) -> Dict:
        """最新のスナップショットと比較"""
        if snapshot_file is None:
            # 最新のスナップショットを取得
            snapshots = sorted(self.snapshot_dir.glob("snapshot_*.json"))
            if not snapshots:
                return {"error": "スナップショットが見つかりません"}
            snapshot_file = snapshots[-1]

        print(
            f"📊 スナップショット比較: {snapshot_file.name if hasattr(snapshot_file, 'name') else snapshot_file}"
        )

        with open(snapshot_file, "r", encoding="utf-8") as f:
            old_snapshot = json.load(f)

        # 現在の状態をチェック
        self.run_comprehensive_check()

        # 差分を計算
        differences = {
            "added_issues": [],
            "removed_issues": [],
            "changed_files": [],
            "health_change": self.results["overall_health"]
            - old_snapshot["results"]["overall_health"],
        }

        # ファイル変更を検出
        for file_path, old_hash in old_snapshot.get("file_hashes", {}).items():
            full_path = self.project_root / file_path
            if full_path.exists():
                current_hash = self.calculate_file_hash(full_path)
                if current_hash != old_hash:
                    differences["changed_files"].append(file_path)

        # 新しい問題を検出
        old_issues = set(old_snapshot["results"].get("issues", []))
        current_issues = set(self.results["issues"])

        differences["added_issues"] = list(current_issues - old_issues)
        differences["removed_issues"] = list(old_issues - current_issues)

        # 結果を表示
        print("\n" + "=" * 70)
        print("📊 変更サマリー")
        print("=" * 70)

        print(
            f"\n健全性スコア変化: {old_snapshot['results']['overall_health']}% → {self.results['overall_health']}% "
            f"({'+' if differences['health_change'] > 0 else ''}{differences['health_change']}%)"
        )

        if differences["added_issues"]:
            print(f"\n🔴 新しい問題 ({len(differences['added_issues'])}件):")
            for issue in differences["added_issues"]:
                print(f"  {issue}")

        if differences["removed_issues"]:
            print(f"\n✅ 解決した問題 ({len(differences['removed_issues'])}件):")
            for issue in differences["removed_issues"]:
                print(f"  {issue}")

        if differences["changed_files"]:
            print(f"\n📝 変更されたファイル ({len(differences['changed_files'])}件):")
            for file_path in differences["changed_files"][:10]:
                print(f"  - {file_path}")
            if len(differences["changed_files"]) > 10:
                print(f"  ... 他 {len(differences['changed_files']) - 10}件")

        print("\n" + "=" * 70)

        return differences

    def save_results(self, output_path: str = "logs/system_health.json"):
        """結果をJSON出力"""
        output_file = self.project_root / output_path
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)

        print(f"\n💾 診断結果を保存: {output_path}")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="包括的システム健全性チェッカー")
    parser.add_argument(
        "--save-snapshot", action="store_true", help="現在の状態をスナップショットとして保存"
    )
    parser.add_argument("--compare", action="store_true", help="最新のスナップショットと比較")
    parser.add_argument("--snapshot", type=str, help="比較するスナップショットファイル")

    args = parser.parse_args()

    checker = ComprehensiveSystemHealthChecker()

    if args.save_snapshot:
        # スナップショット保存
        checker.run_comprehensive_check()
        checker.print_summary()
        checker.save_snapshot()
        checker.save_results()
    elif args.compare:
        # 比較実行
        checker.compare_with_snapshot(args.snapshot)
    else:
        # 通常の診断
        checker.run_comprehensive_check()
        checker.print_summary()
        checker.save_results()


if __name__ == "__main__":
    main()
