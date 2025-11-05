"""
修正版LogIntegrator - メソッド互換性確保
"""

import sys

sys.path.insert(0, "/workspaces/gemini_AI_Agent")


class LogIntegratorFixed:
    """ログ統合システム - 修正版"""

    # 統合するシート名
    SHEETS = {
        "execution": "task_execution_log",
        "retry": "retry_log",
        "context": "context_log",
        "feedback": "feedback_queue",
        "agents": "agent_registry",
    }

    def __init__(self, sheets_manager):
        self.sheets_manager = sheets_manager
        print("✅ LogIntegratorFixed 初期化完了")

    async def load_all_logs(self):
        """すべてのログを読み込み - 修正版"""
        print("�� 全ログシート読み込み中...")
        all_logs = []

        for log_type, sheet_name in self.SHEETS.items():
            try:
                logs = self.sheets_manager.read_sheet(sheet_name)
                if logs:
                    print(f"  ✅ {sheet_name}: {len(logs)}件のログを読み込み")
                    # ログタイプを追加
                    for log in logs:
                        log["log_type"] = log_type
                    all_logs.extend(logs)
                else:
                    print(f"  ⚠️ {sheet_name}: シートが見つかりません")
            except Exception as e:
                print(f"  ❌ {sheet_name}: 読み込みエラー - {e}")

        print(f"📊 合計 {len(all_logs)}件のログを統合")
        return all_logs

    async def integrate_logs(self, logs):
        """ログを統合 - 互換性確保"""
        try:
            # 簡易的なログ統合処理
            integrated = {
                "total_logs": len(logs),
                "log_types": set(log.get("log_type", "unknown") for log in logs),
                "logs": logs,
            }
            return integrated
        except Exception as e:
            print(f"❌ ログ統合エラー: {e}")
            return {"total_logs": 0, "log_types": set(), "logs": []}
