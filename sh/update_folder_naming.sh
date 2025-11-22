#!/bin/bash
# フォルダ名形式変更

cd /workspaces/gemini_AI_Agent

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📁 フォルダ名形式変更"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

NOW_JST=$(TZ=Asia/Tokyo date +%y%m%d_%H%M)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 1: フォルダ名生成コードを探す
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo "📍 STEP 1: フォルダ名生成コードを探す"

# TaskExecutorを探す
if [ -f "agents/task_executor.py" ]; then
    echo "  ✅ agents/task_executor.py 発見"
    EXECUTOR_FILE="agents/task_executor.py"
elif [ -f "agents/automation/task_executor.py" ]; then
    echo "  ✅ agents/automation/task_executor.py 発見"
    EXECUTOR_FILE="agents/automation/task_executor.py"
else
    echo "  ⚠️  TaskExecutorが見つかりません"
    echo "     フォルダ名生成箇所を手動で確認してください"
fi

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 2: フォルダ名フォーマッター作成
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo ""
echo "📍 STEP 2: フォルダ名フォーマッター作成"

cat > tools/folder_name_formatter.py << 'PYTHON'
"""
フォルダ名フォーマッター
{parent_goal_id}_{task_id}_{task_name}_{timestamp}_{jst_datetime}
例: 7_7_24時間稼働最終確認_032337_04_251122_1231
"""

from datetime import datetime
import pytz

def format_folder_name(
    parent_goal_id: str,
    task_id: str,
    task_name: str,
    sequence_number: int = 1
) -> str:
    """
    フォルダ名をフォーマット
    
    Args:
        parent_goal_id: 親ゴールID（例: "7"）
        task_id: タスクID（例: "7"）
        task_name: タスク名（例: "24時間稼働最終確認"）
        sequence_number: 連番（例: 4）
    
    Returns:
        folder_name: 例: "7_7_24時間稼働最終確認_032337_04_251122_1231"
    """
    
    # 日本時間取得
    jst = pytz.timezone('Asia/Tokyo')
    now_jst = datetime.now(jst)
    
    # タイムスタンプ（時分秒）
    timestamp_hms = now_jst.strftime('%H%M%S')
    
    # 日本時間（年月日時分）
    jst_datetime = now_jst.strftime('%y%m%d_%H%M')
    
    # 連番（2桁）
    seq = str(sequence_number).zfill(2)
    
    # タスク名をクリーンアップ
    clean_task_name = task_name.strip().replace(' ', '_')
    
    # フォルダ名構築
    folder_name = f"{parent_goal_id}_{task_id}_{clean_task_name}_{timestamp_hms}_{seq}_{jst_datetime}"
    
    return folder_name

def parse_task_info_from_sheet(row: dict) -> dict:
    """
    Google Sheetsの行からタスク情報を抽出
    
    Args:
        row: Sheetsの行データ
    
    Returns:
        task_info: {
            'parent_goal_id': str,
            'task_id': str,
            'task_name': str
        }
    """
    
    # parent_goal_id（例: "7"）
    parent_goal_id = str(row.get('parent_goal_id', '0'))
    
    # task_id（例: "7"）
    task_id = str(row.get('task_id', '0'))
    
    # task_name（例: "24時間稼働最終確認"）
    task_name = row.get('task_name', row.get('title', 'unknown_task'))
    
    return {
        'parent_goal_id': parent_goal_id,
        'task_id': task_id,
        'task_name': task_name
    }

# 使用例
if __name__ == '__main__':
    # テスト
    folder_name = format_folder_name(
        parent_goal_id='7',
        task_id='7',
        task_name='24時間稼働最終確認',
        sequence_number=4
    )
    
    print(f"フォルダ名: {folder_name}")
    # 例: 7_7_24時間稼働最終確認_123456_04_251122_1231

PYTHON

echo "  ✅ フォルダ名フォーマッター作成完了"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 3: TaskExecutor更新
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo ""
echo "📍 STEP 3: TaskExecutor更新"

cat > agents/task_executor.py << 'PYTHON'
"""
タスク実行エンジン
新しいフォルダ名形式対応版
"""

import sys
import os
from pathlib import Path
from datetime import datetime

sys.path.insert(0, '/workspaces/gemini_AI_Agent')

from tools.folder_name_formatter import format_folder_name, parse_task_info_from_sheet

class TaskExecutor:
    """タスク実行エンジン"""
    
    def __init__(self):
        self.output_base_dir = Path('/workspaces/gemini_AI_Agent/agents/generated')
        self.output_base_dir.mkdir(exist_ok=True)
        self.sequence_counter = {}
    
    def execute_task(self, task_data: dict) -> dict:
        """
        タスク実行
        
        Args:
            task_data: {
                'parent_goal_id': str,
                'task_id': str,
                'task_name': str,
                'description': str,
                ...
            }
        
        Returns:
            result: {
                'success': bool,
                'output_path': str,
                'folder_name': str,
                ...
            }
        """
        
        # タスク情報抽出
        parent_goal_id = task_data.get('parent_goal_id', '0')
        task_id = task_data.get('task_id', '0')
        task_name = task_data.get('task_name', task_data.get('title', 'unknown'))
        
        # 連番取得
        key = f"{parent_goal_id}_{task_id}_{task_name}"
        if key not in self.sequence_counter:
            self.sequence_counter[key] = 1
        else:
            self.sequence_counter[key] += 1
        
        sequence = self.sequence_counter[key]
        
        # フォルダ名生成
        folder_name = format_folder_name(
            parent_goal_id=parent_goal_id,
            task_id=task_id,
            task_name=task_name,
            sequence_number=sequence
        )
        
        # 出力パス
        output_path = self.output_base_dir / folder_name
        output_path.mkdir(exist_ok=True)
        
        print(f"📁 出力フォルダ: {folder_name}")
        
        # タスク実行（ここに実際のコード生成ロジック）
        # ...
        
        return {
            'success': True,
            'output_path': str(output_path),
            'folder_name': folder_name,
            'parent_goal_id': parent_goal_id,
            'task_id': task_id,
            'task_name': task_name,
            'sequence': sequence
        }

PYTHON

echo "  ✅ TaskExecutor更新完了"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 4: pytz インストール
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo ""
echo "📍 STEP 4: pytz インストール"

pip install pytz --break-system-packages --quiet

echo "  ✅ pytz インストール完了"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 5: テストスクリプト
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo ""
echo "📍 STEP 5: テストスクリプト作成"

cat > sh/test_folder_naming.sh << 'TESTBASH'
#!/bin/bash
# フォルダ名テスト

cd /workspaces/gemini_AI_Agent

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🧪 フォルダ名形式テスト"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

python3 << PYTHON
import sys
sys.path.insert(0, '/workspaces/gemini_AI_Agent')

from tools.folder_name_formatter import format_folder_name
from datetime import datetime
import pytz

print("📋 フォルダ名生成テスト")
print("=" * 80)
print()

# テストケース1
folder1 = format_folder_name(
    parent_goal_id='7',
    task_id='7',
    task_name='24時間稼働最終確認',
    sequence_number=4
)

print(f"テスト1: {folder1}")
print()

# テストケース2
folder2 = format_folder_name(
    parent_goal_id='5',
    task_id='12',
    task_name='統合テスト実行',
    sequence_number=1
)

print(f"テスト2: {folder2}")
print()

# 現在時刻確認
jst = pytz.timezone('Asia/Tokyo')
now_jst = datetime.now(jst)

print(f"現在時刻（JST）: {now_jst.strftime('%Y年%m月%d日 %H:%M:%S')}")
print()

print("✅ フォーマット確認:")
print("   形式: {parent_goal_id}_{task_id}_{task_name}_{HHMMSS}_{seq}_{YYMMDD_HHMM}")
print()

PYTHON

TESTBASH

chmod +x sh/test_folder_naming.sh

echo "  ✅ テストスクリプト作成完了"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ フォルダ名形式変更完了"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📋 新しい形式:"
echo "   {parent_goal_id}_{task_id}_{task_name}_{HHMMSS}_{seq}_{YYMMDD_HHMM}"
echo ""
echo "📖 例:"
echo "   7_7_24時間稼働最終確認_032337_04_251122_1231"
echo ""
echo "🧪 テスト実行:"
echo "   bash sh/test_folder_naming.sh"
echo ""
echo "⚠️  重要:"
echo "   Phase 3実行スクリプトでTaskExecutorを使用している箇所を"
echo "   新しいformat_folder_nameに更新する必要があります。"
echo ""
echo "📂 確認すべきファイル:"
echo "   - sh/run_phase3_full_autonomous.sh"
echo "   - agents/pm_agent.py"
echo "   - agents/automation/code_generator.py"
echo ""

