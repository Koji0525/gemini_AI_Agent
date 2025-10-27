#!/bin/bash
set -e

echo "=========================================="
echo "🔧 SheetsManager メソッド統合"
echo "=========================================="

# バックアップ
cp tools/sheets_manager.py tools/sheets_manager.py.backup_before_writeback

# メソッドを追加
python3 << 'PYTHON_ADD'
# 既存のファイルを読み込む
with open("tools/sheets_manager.py", "r", encoding="utf-8") as f:
    content = f.read()

# 新しいメソッドを追加（クラスの最後に）
new_methods = '''
    def update_task_status(
        self,
        task_id: str,
        status: str,
        result: dict = None,
        error_message: str = None,
        output_file: str = None
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
            
            sheet = self.gc.open_by_key(self.spreadsheet_id)
            task_sheet = sheet.worksheet("tasks")
            
            # タスクIDで行を検索
            cell = task_sheet.find(str(task_id))
            
            if not cell:
                print(f"⚠️  タスクID {task_id} が見つかりません")
                return False
            
            row = cell.row
            
            # ステータス列に書き込み（D列 = 4）
            task_sheet.update_cell(row, 4, status)
            
            # 完了日時を記録（E列 = 5）
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            task_sheet.update_cell(row, 5, timestamp)
            
            # 結果の詳細を記録（F列 = 6）
            if result:
                result_text = str(result.get('summary', ''))[:500]
                task_sheet.update_cell(row, 6, result_text)
            
            # エラーメッセージを記録（G列 = 7）
            if error_message:
                task_sheet.update_cell(row, 7, error_message[:500])
            
            # 出力ファイルパスを記録（H列 = 8）
            if output_file:
                task_sheet.update_cell(row, 8, output_file)
            
            print(f"✅ タスクID {task_id} の結果を書き込みました")
            return True
            
        except Exception as e:
            print(f"❌ Sheets書き込みエラー: {e}")
            return False
'''

# クラスの最後（最後のメソッドの後）に追加
# GoogleSheetsManager クラスの最後を見つける
import re

# クラスの終わりを探す（次のクラスまたはファイル末尾）
# 最後のメソッドの後に追加
if "class GoogleSheetsManager" in content:
    # 既に update_task_status がないか確認
    if "def update_task_status" not in content:
        # クラスの最後に追加（ファイルの最後）
        content = content.rstrip() + new_methods + "\n"
        print("✅ update_task_status メソッドを追加しました")
    else:
        print("⚠️  update_task_status は既に存在します")
else:
    print("❌ GoogleSheetsManager クラスが見つかりません")
    exit(1)

# 保存
with open("tools/sheets_manager.py", "w", encoding="utf-8") as f:
    f.write(content)

print("✅ ファイル保存完了")

PYTHON_ADD

# 構文チェック
python3 -m py_compile tools/sheets_manager.py

if [ $? -eq 0 ]; then
    echo "✅ 構文チェック成功"
else
    echo "❌ 構文エラー - バックアップから復元してください"
    exit 1
fi

echo ""
echo "=========================================="
echo "✅ SheetsManager 統合完了"
echo "=========================================="

