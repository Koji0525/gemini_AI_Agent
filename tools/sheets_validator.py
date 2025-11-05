"""
スプレッドシート書き込みデータの検証ツール
書き込み前に列定義との整合性をチェック
"""
import sys
sys.path.insert(0, '/workspaces/gemini_AI_Agent')

from configuration.spreadsheet_schema import (
    get_schema, get_column_names, validate_row_data
)

class SheetsValidator:
    """スプレッドシートデータの検証クラス"""
    
    def __init__(self):
        self.validation_log = []
    
    def validate_before_write(self, sheet_name, row_data):
        """書き込み前の検証"""
        is_valid, message = validate_row_data(sheet_name, row_data)
        
        self.validation_log.append({
            "sheet": sheet_name,
            "valid": is_valid,
            "message": message,
            "row_data_length": len(row_data)
        })
        
        if not is_valid:
            print(f"⚠️ 検証エラー [{sheet_name}]: {message}")
            print(f"   データ長: {len(row_data)}")
            schema = get_schema(sheet_name)
            if schema:
                print(f"   期待列数: {schema['total_columns']}")
        
        return is_valid, message
    
    def create_valid_row(self, sheet_name, data_dict):
        """辞書から正しい順序の行データを生成"""
        schema = get_schema(sheet_name)
        if not schema:
            raise ValueError(f"Unknown sheet: {sheet_name}")
        
        row = []
        for col in schema["columns"]:
            col_name = col["name"]
            value = data_dict.get(col_name, "")
            
            # 型変換
            if col["type"] == "int":
                value = int(value) if value else 0
            elif col["type"] == "float":
                value = float(value) if value else 0.0
            elif col["type"] == "bool":
                value = bool(value) if value else False
            else:
                value = str(value) if value else ""
            
            row.append(value)
        
        return row
    
    def get_validation_summary(self):
        """検証サマリーを取得"""
        total = len(self.validation_log)
        valid = sum(1 for log in self.validation_log if log["valid"])
        invalid = total - valid
        
        return {
            "total": total,
            "valid": valid,
            "invalid": invalid,
            "success_rate": (valid / total * 100) if total > 0 else 0
        }

# テスト用の関数
if __name__ == "__main__":
    validator = SheetsValidator()
    
    # pm_tasksのテスト
    print("📊 pm_tasksシートのテスト:")
    test_data = {
        "task_id": "TEST-001",
        "parent_goal_id": "GOAL-001",
        "description": "テストタスク",
        "required_role": "developer",
        "status": "pending",
        "priority": "high",
        "estimated_time": 30,
        "dependencies": "",
        "created_at": "2025-11-05",
        "batch_id": "BATCH-001"
    }
    
    row = validator.create_valid_row("pm_tasks", test_data)
    is_valid, message = validator.validate_before_write("pm_tasks", row)
    print(f"  結果: {'✅ 成功' if is_valid else '❌ 失敗'} - {message}")
    
    # task_execution_logのテスト
    print("\n📊 task_execution_logシートのテスト:")
    test_log = {
        "log_id": "LOG-001",
        "task_id": "TEST-001",
        "task_description": "テストタスク",
        "timestamp": "2025-11-05 10:00:00",
        "agent_role": "developer",
        "output_summary": "完了",
        "output_data": "",
        "status": "completed",
        "Quality_Score": 9,
        "Quality_description": "良好",
        "elapsed_time": 15.5,
        "retry_count": 0,
        "error_type": "",
        "fix_applied": False
    }
    
    row = validator.create_valid_row("task_execution_log", test_log)
    is_valid, message = validator.validate_before_write("task_execution_log", row)
    print(f"  結果: {'✅ 成功' if is_valid else '❌ 失敗'} - {message}")
    
    # サマリー表示
    summary = validator.get_validation_summary()
    print(f"\n📈 検証サマリー:")
    print(f"  総数: {summary['total']}")
    print(f"  成功: {summary['valid']}")
    print(f"  失敗: {summary['invalid']}")
    print(f"  成功率: {summary['success_rate']:.1f}%")

