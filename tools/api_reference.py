"""
全コンポーネントAPIリファレンス
メソッド名、引数、戻り値を一元管理
"""

from typing import Any, Dict, List


class APIReference:
    """全コンポーネントの正しいAPIを管理"""

    # 各コンポーネントのメソッド定義
    COMPONENTS = {
        "GoogleSheetsManager": {
            "class_path": "tools.sheets_manager.GoogleSheetsManager",
            "methods": {
                "read_range": {
                    "signature": "read_range(range_name: str) -> List[List[Any]]",
                    "description": "指定範囲のデータ読み取り",
                    "example": 'sheets.read_range("pm_tasks!A1:K10")',
                },
                "append_rows": {  # ← 正解！
                    "signature": "append_rows(range_name: str, values: List[List[Any]]) -> bool",
                    "description": "データ行の追加（複数形！）",
                    "example": 'sheets.append_rows("pm_tasks", [[task_data]])',
                },
                "update_range": {
                    "signature": "update_range(range_name: str, values: List[List[Any]]) -> bool",
                    "description": "指定範囲のデータ更新",
                    "example": 'sheets.update_range("pm_tasks!A2:K2", [[updated_data]])',
                },
            },
            "common_errors": {
                "append_row": "append_rows（複数形が正解）",
                "read": "read_range（_rangeが必要）",
                "update": "update_range（_rangeが必要）",
            },
        },
        "SafeSheetsWrapper": {
            "class_path": "tools.safe_sheets_wrapper.SafeSheetsWrapper",
            "methods": {
                "safe_read": {
                    "signature": "safe_read(range_name: str, default: List[List[Any]] = None) -> List[List[Any]]",
                    "description": "安全なデータ読み取り（エラー時にdefault返却）",
                    "example": 'wrapper.safe_read("project_goal!A2:C100", default=[])',
                },
                "safe_append": {
                    "signature": "safe_append(range_name: str, values: List[List[Any]]) -> bool",
                    "description": "安全なデータ追加",
                    "example": 'wrapper.safe_append("pm_tasks", [[task_data]])',
                },
                "safe_update": {
                    "signature": "safe_update(range_name: str, values: List[List[Any]]) -> bool",
                    "description": "安全なデータ更新",
                    "example": 'wrapper.safe_update("pm_tasks!A2:K2", [[updated_data]])',
                },
            },
        },
        "KnowledgeManager": {
            "class_path": "knowledge_system.core_agents.knowledge_manager.KnowledgeManager",
            "methods": {
                "add_knowledge": {  # ← 正解！
                    "signature": 'add_knowledge(title: str, content: str, category: str = "general", tags: str = "")',
                    "description": "ナレッジ追加",
                    "example": 'km.add_knowledge(title="テスト", content="内容", category="test", tags="tag1")',
                },
                "search_knowledge": {
                    "signature": "search_knowledge(query: str, top_k: int = 5) -> List[Dict]",
                    "description": "ナレッジ検索",
                    "example": 'km.search_knowledge("エラー", top_k=5)',
                },
            },
            "common_errors": {
                "add_knowledge_entry": "add_knowledge（_entryは不要）",
                "insert_knowledge": "add_knowledge（insertではなくadd）",
            },
        },
        "ObservabilityManager": {
            "class_path": "agents.observability.observability_manager.ObservabilityManager",
            "methods": {
                "record_trace": {  # ← 正解！
                    "signature": "record_trace(trace_data: Dict[str, Any])",
                    "description": "トレース記録",
                    "example": 'obs.record_trace({"event": "task_start", "data": {}})',
                },
                "search_traces": {
                    "signature": "search_traces(**kwargs) -> List[Dict[str, Any]]",
                    "description": "トレース検索",
                    "example": 'obs.search_traces(event_type="error")',
                },
                "get_comprehensive_stats": {
                    "signature": "get_comprehensive_stats() -> Dict[str, Any]",
                    "description": "統計情報取得",
                    "example": "obs.get_comprehensive_stats()",
                },
            },
            "common_errors": {
                "log_metric": "record_trace（log_metricは存在しない）",
                "record_event": "record_trace（record_eventではなくrecord_trace）",
            },
        },
    }

    @classmethod
    def get_correct_method(cls, component: str, wrong_method: str) -> str:
        """
        間違ったメソッド名から正しいメソッド名を取得

        Args:
            component: コンポーネント名
            wrong_method: 間違ったメソッド名

        Returns:
            正しいメソッド名（見つからない場合は元のまま）
        """
        if component not in cls.COMPONENTS:
            return wrong_method

        common_errors = cls.COMPONENTS[component].get("common_errors", {})
        if wrong_method in common_errors:
            return common_errors[wrong_method]

        return wrong_method

    @classmethod
    def get_method_info(cls, component: str, method: str) -> Dict[str, Any]:
        """メソッドの詳細情報を取得"""
        if component not in cls.COMPONENTS:
            return {}

        methods = cls.COMPONENTS[component].get("methods", {})
        return methods.get(method, {})

    @classmethod
    def search_method(cls, search_term: str) -> List[Dict[str, Any]]:
        """メソッド名の部分一致検索"""
        results = []

        for component, info in cls.COMPONENTS.items():
            methods = info.get("methods", {})
            for method_name, method_info in methods.items():
                if search_term.lower() in method_name.lower():
                    results.append(
                        {
                            "component": component,
                            "method": method_name,
                            "signature": method_info.get("signature", ""),
                            "description": method_info.get("description", ""),
                            "example": method_info.get("example", ""),
                        }
                    )

        return results

    @classmethod
    def print_reference(cls, component: str = None):
        """リファレンスを表示"""
        if component:
            components = {component: cls.COMPONENTS.get(component, {})}
        else:
            components = cls.COMPONENTS

        for comp_name, comp_info in components.items():
            print(f"\n{'='*80}")
            print(f"📚 {comp_name}")
            print("=" * 80)

            methods = comp_info.get("methods", {})
            for method_name, method_info in methods.items():
                print(f"\n  {method_name}")
                print(f"    {method_info.get('signature', '')}")
                print(f"    説明: {method_info.get('description', '')}")
                print(f"    例: {method_info.get('example', '')}")

            common_errors = comp_info.get("common_errors", {})
            if common_errors:
                print(f"\n  ⚠️ よくある間違い:")
                for wrong, correct in common_errors.items():
                    print(f"    ❌ {wrong} → ✅ {correct}")


# テスト・使用例
if __name__ == "__main__":
    ref = APIReference()

    print("🧪 テスト1: 間違ったメソッド名を修正")
    print(f"append_row → {ref.get_correct_method('GoogleSheetsManager', 'append_row')}")
    print(f"log_metric → {ref.get_correct_method('ObservabilityManager', 'log_metric')}")

    print("\n🧪 テスト2: メソッド検索")
    results = ref.search_method("append")
    for r in results:
        print(f"  {r['component']}.{r['method']}: {r['description']}")

    print("\n🧪 テスト3: 全リファレンス表示")
    ref.print_reference("GoogleSheetsManager")
