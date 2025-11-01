#!/bin/bash
set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "=========================================="
echo "🔧 SheetsManager 完全修正"
echo "=========================================="

# ====================================================================
# STEP 1: 現在のメソッド確認
# ====================================================================
echo ""
echo -e "${BLUE}[STEP 1/3] 現在のメソッド確認${NC}"
echo "=========================================="

echo "既存のメソッド:"
grep "^    def " tools/sheets_manager.py | grep -v "__" || true

echo ""
echo "get_tasks メソッドの有無:"
if grep -q "def get_tasks" tools/sheets_manager.py; then
    echo "  ✅ 存在します"
else
    echo "  ❌ 存在しません - 追加が必要"
fi

# ====================================================================
# STEP 2: 必要なメソッドを追加
# ====================================================================
echo ""
echo -e "${BLUE}[STEP 2/3] メソッド追加${NC}"
echo "=========================================="

# バックアップ
cp tools/sheets_manager.py tools/sheets_manager.py.backup_get_tasks

python3 << 'PYTHON_ADD'
with open("tools/sheets_manager.py", "r", encoding="utf-8") as f:
    content = f.read()

# get_tasks メソッドが存在しない場合のみ追加
if "def get_tasks" not in content:
    print("📝 get_tasks メソッドを追加中...")
    
    get_tasks_method = '''
    def get_tasks(self) -> list:
        """
        Sheetsからタスク一覧を取得
        
        Returns:
            list: タスクのリスト（辞書形式）
        """
        try:
            self._ensure_client()
            
            # スプレッドシートを開く
            sheet = self.gc.open_by_key(self.spreadsheet_id)
            
            # 'tasks' シートを取得
            try:
                task_sheet = sheet.worksheet("tasks")
            except gspread.WorksheetNotFound:
                print("⚠️  'tasks' シートが見つかりません")
                print("   シート名を 'tasks' にしてください")
                return []
            
            # 全データを取得
            all_values = task_sheet.get_all_values()
            
            if not all_values or len(all_values) < 2:
                print("⚠️  データが見つかりません")
                return []
            
            # ヘッダー行（1行目）
            headers = all_values[0]
            
            # データ行（2行目以降）
            tasks = []
            for row in all_values[1:]:
                if not row or not row[0]:  # 空行をスキップ
                    continue
                
                task = {}
                for i, header in enumerate(headers):
                    if i < len(row):
                        task[header.lower()] = row[i]
                
                tasks.append(task)
            
            print(f"✅ {len(tasks)}件のタスクを取得しました")
            return tasks
            
        except Exception as e:
            print(f"❌ タスク取得エラー: {e}")
            import traceback
            traceback.print_exc()
            return []
'''
    
    # クラスの最後に追加
    # update_task_status の前に追加（もし存在すれば）
    if "def update_task_status" in content:
        content = content.replace(
            "    def update_task_status",
            get_tasks_method + "\n    def update_task_status"
        )
    else:
        # クラスの最後に追加
        content = content.rstrip() + get_tasks_method + "\n"
    
    print("✅ get_tasks メソッド追加完了")
else:
    print("⚠️  get_tasks メソッドは既に存在します")

# 保存
with open("tools/sheets_manager.py", "w", encoding="utf-8") as f:
    f.write(content)

print("✅ ファイル保存完了")

PYTHON_ADD

# ====================================================================
# STEP 3: 構文チェック
# ====================================================================
echo ""
echo -e "${BLUE}[STEP 3/3] 構文チェック${NC}"
echo "=========================================="

python3 -m py_compile tools/sheets_manager.py

if [ $? -eq 0 ]; then
    echo "✅ 構文チェック成功"
else
    echo "❌ 構文エラー"
    echo "   バックアップから復元:"
    echo "   cp tools/sheets_manager.py.backup_get_tasks tools/sheets_manager.py"
    exit 1
fi

echo ""
echo "=========================================="
echo -e "${GREEN}✅ SheetsManager修正完了${NC}"
echo "=========================================="
echo ""
echo "追加されたメソッド:"
echo "  ✅ get_tasks() - タスク一覧取得"
echo ""

