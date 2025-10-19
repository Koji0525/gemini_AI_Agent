#!/bin/bash
set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "=========================================="
echo "�� Google Sheets結果書き戻し機能実装"
echo "=========================================="

# ====================================================================
# STEP 1: SheetsManagerの拡張確認
# ====================================================================
echo ""
echo -e "${BLUE}[STEP 1/4] SheetsManager現状確認${NC}"
echo "=========================================="

echo "既存メソッドの確認:"
grep -n "def update_task_status\|def save_result" tools/sheets_manager.py || echo "  未実装"

# ====================================================================
# STEP 2: update_task_status メソッドの実装
# ====================================================================
echo ""
echo -e "${BLUE}[STEP 2/4] update_task_status 実装${NC}"
echo "=========================================="

cat > _WIP/sheets_manager_writeback_methods.py << 'WRITEBACK_METHODS'
"""
SheetsManager に追加するメソッド
tools/sheets_manager.py に追加してください
"""

def update_task_status(
    self,
    task_id: str,
    status: str,
    result: Optional[Dict] = None,
    error_message: Optional[str] = None,
    output_file: Optional[str] = None
) -> bool:
    """
    タスクの実行結果をスプレッドシートに書き戻す
    
    Args:
        task_id: タスクID
        status: ステータス ('completed', 'failed', 'in_progress')
        result: 実行結果（Dict）
        error_message: エラーメッセージ（失敗時）
        output_file: 出力ファイルパス
        
    Returns:
        bool: 書き込み成功したかどうか
    """
    try:
        self._ensure_client()
        
        # スプレッドシートを開く
        sheet = self.gc.open_by_key(self.spreadsheet_id)
        task_sheet = sheet.worksheet("tasks")  # タスクシート名
        
        # タスクIDの列を探す（通常は1列目）
        task_id_col = 1
        
        # タスクIDで行を検索
        cell = task_sheet.find(str(task_id))
        
        if not cell:
            print(f"⚠️  タスクID {task_id} が見つかりません")
            return False
        
        row = cell.row
        
        # ステータス列に書き込み（例：D列 = 4）
        status_col = 4
        task_sheet.update_cell(row, status_col, status)
        
        # 完了日時を記録（例：E列 = 5）
        timestamp_col = 5
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        task_sheet.update_cell(row, timestamp_col, timestamp)
        
        # 結果の詳細を記録（例：F列 = 6）
        if result:
            result_col = 6
            result_text = str(result.get('summary', ''))[:500]  # 500文字まで
            task_sheet.update_cell(row, result_col, result_text)
        
        # エラーメッセージを記録（例：G列 = 7）
        if error_message:
            error_col = 7
            task_sheet.update_cell(row, error_col, error_message[:500])
        
        # 出力ファイルパスを記録（例：H列 = 8）
        if output_file:
            output_col = 8
            task_sheet.update_cell(row, output_col, output_file)
        
        print(f"✅ タスクID {task_id} の結果を書き込みました")
        return True
        
    except Exception as e:
        print(f"❌ Sheets書き込みエラー: {e}")
        import traceback
        traceback.print_exc()
        return False


def batch_update_task_statuses(
    self,
    updates: List[Dict]
) -> bool:
    """
    複数のタスクステータスを一括更新（効率化）
    
    Args:
        updates: 更新内容のリスト
            [
                {"task_id": "1", "status": "completed", "result": {...}},
                {"task_id": "2", "status": "failed", "error": "..."},
            ]
    
    Returns:
        bool: 成功したかどうか
    """
    try:
        self._ensure_client()
        sheet = self.gc.open_by_key(self.spreadsheet_id)
        task_sheet = sheet.worksheet("tasks")
        
        # バッチ更新用のリスト
        batch_data = []
        
        for update in updates:
            task_id = update.get("task_id")
            
            # タスクIDで行を検索
            cell = task_sheet.find(str(task_id))
            if not cell:
                continue
            
            row = cell.row
            
            # 更新データを準備
            batch_data.append({
                "range": f"D{row}",  # ステータス列
                "values": [[update.get("status", "unknown")]]
            })
            
            # タイムスタンプ
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            batch_data.append({
                "range": f"E{row}",
                "values": [[timestamp]]
            })
        
        # バッチ更新実行
        if batch_data:
            task_sheet.batch_update(batch_data)
            print(f"✅ {len(updates)}件のタスクを一括更新しました")
        
        return True
        
    except Exception as e:
        print(f"❌ バッチ更新エラー: {e}")
        return False

WRITEBACK_METHODS

echo "✅ メソッド実装コード作成完了"
echo "   _WIP/sheets_manager_writeback_methods.py"

# ====================================================================
# STEP 3: TaskExecutorへの統合
# ====================================================================
echo ""
echo -e "${BLUE}[STEP 3/4] TaskExecutor統合コード${NC}"
echo "=========================================="

cat > _WIP/task_executor_sheets_integration.py << 'EXECUTOR_INTEGRATION'
"""
TaskExecutor への統合例
scripts/task_executor.py の execute_task メソッドに追加
"""

async def execute_task(self, task: Dict) -> bool:
    """
    タスクを実行（Sheets書き戻し統合版）
    """
    task_id = task.get('id', 'unknown')
    
    try:
        # 実行中ステータスに更新
        if self.sheets_manager:
            self.sheets_manager.update_task_status(
                task_id=task_id,
                status="in_progress"
            )
        
        # タスク実行（既存のロジック）
        result = await self._execute_task_logic(task)
        
        # 成功時の書き戻し
        if result.get('success'):
            if self.sheets_manager:
                self.sheets_manager.update_task_status(
                    task_id=task_id,
                    status="completed",
                    result=result,
                    output_file=result.get('output_file')
                )
            return True
        else:
            # 失敗時の書き戻し
            if self.sheets_manager:
                self.sheets_manager.update_task_status(
                    task_id=task_id,
                    status="failed",
                    error_message=result.get('error', 'Unknown error')
                )
            return False
            
    except Exception as e:
        # エラー時の書き戻し
        if self.sheets_manager:
            self.sheets_manager.update_task_status(
                task_id=task_id,
                status="failed",
                error_message=str(e)
            )
        raise

EXECUTOR_INTEGRATION

echo "✅ TaskExecutor統合コード作成完了"
echo "   _WIP/task_executor_sheets_integration.py"

# ====================================================================
# STEP 4: テストスクリプト作成
# ====================================================================
echo ""
echo -e "${BLUE}[STEP 4/4] テストスクリプト作成${NC}"
echo "=========================================="

cat > test_sheets_writeback.py << 'TEST_WRITEBACK'
#!/usr/bin/env python3
"""
Google Sheets 結果書き戻しテスト
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from tools.sheets_manager import GoogleSheetsManager

def test_writeback():
    print("\n🧪 Sheets書き戻しテスト")
    print("="*70)
    
    # SheetsManager初期化
    sheets_manager = GoogleSheetsManager(
        service_account_file="configuration/service_account.json",
        spreadsheet_id="YOUR_SPREADSHEET_ID"  # 実際のIDに変更
    )
    
    # テストデータ
    test_task_id = "TEST_001"
    
    print(f"\n📝 テストタスクID: {test_task_id}")
    
    # 1. 実行中に更新
    print("\n[1/3] 実行中ステータス更新...")
    success = sheets_manager.update_task_status(
        task_id=test_task_id,
        status="in_progress"
    )
    print(f"   結果: {'✅ 成功' if success else '❌ 失敗'}")
    
    # 2. 完了に更新
    print("\n[2/3] 完了ステータス更新...")
    success = sheets_manager.update_task_status(
        task_id=test_task_id,
        status="completed",
        result={
            "summary": "テスト実行が完了しました",
            "details": "5,532文字のレスポンスを取得"
        },
        output_file="agent_outputs/test/test_result.md"
    )
    print(f"   結果: {'✅ 成功' if success else '❌ 失敗'}")
    
    # 3. エラー時の更新
    print("\n[3/3] エラーステータス更新...")
    success = sheets_manager.update_task_status(
        task_id=test_task_id,
        status="failed",
        error_message="テスト用のエラーメッセージ"
    )
    print(f"   結果: {'✅ 成功' if success else '❌ 失敗'}")
    
    print("\n" + "="*70)
    print("✅ テスト完了")
    print("="*70)
    print("\nスプレッドシートを確認してください：")
    print(f"  https://docs.google.com/spreadsheets/d/{sheets_manager.spreadsheet_id}")

if __name__ == "__main__":
    test_writeback()

TEST_WRITEBACK

chmod +x test_sheets_writeback.py

echo "✅ テストスクリプト作成完了"
echo "   test_sheets_writeback.py"

echo ""
echo "=========================================="
echo -e "${GREEN}✅ Sheets書き戻し機能実装完了${NC}"
echo "=========================================="
echo ""
echo "📁 作成されたファイル:"
echo "   - _WIP/sheets_manager_writeback_methods.py"
echo "   - _WIP/task_executor_sheets_integration.py"
echo "   - test_sheets_writeback.py"
echo ""
echo "次のステップ:"
echo "  1. _WIP/sheets_manager_writeback_methods.py の内容を"
echo "     tools/sheets_manager.py に追加"
echo "  2. test_sheets_writeback.py でテスト実行"
echo "  3. TaskExecutor に統合"
echo ""

