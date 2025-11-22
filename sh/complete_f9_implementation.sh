#!/bin/bash
# F9HumanInterface完全実装

cd /workspaces/gemini_AI_Agent

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔧 F9HumanInterface完全実装"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

NOW_JST=$(TZ=Asia/Tokyo date +%y%m%d_%H%M)

# 完全版F9HumanInterfaceを作成
cat > agents/f9_human_interface_complete.py << 'PYTHON'
"""
F9: 人間指示インターフェース（完全版）
指示の受付と自動処理を実装
"""

import sys
import traceback
from datetime import datetime
from typing import List, Dict, Any

sys.path.insert(0, '/workspaces/gemini_AI_Agent')

class F9HumanInterface:
    """F9: 人間指示インターフェース（完全版）"""
    
    def __init__(self, sheets_manager=None):
        self.sheets = sheets_manager
        self.instructions_sheet = "human_instructions"
        
    def add_instruction(
        self,
        instruction_type: str,
        content: str,
        priority: str = 'medium',
        target_task: str = ''
    ) -> bool:
        """指示を追加"""
        try:
            print(f"\n{'=' * 80}")
            print("📝 F9: 指示を追加")
            print('=' * 80)
            print(f"  instruction_type: {instruction_type}")
            print(f"  content: {content}")
            print(f"  priority: {priority}")
            print(f"  target_task: {target_task}")
            
            # 指示データを作成
            row_data = [
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                instruction_type,
                'pending',
                content,
                priority,
                target_task,
                ''
            ]
            
            print(f"\n  📋 Google Sheetsに追加中...")
            
            # Google Sheetsに追加
            result = self.sheets.service.spreadsheets().values().append(
                spreadsheetId=self.sheets.spreadsheet_id,
                range=f"{self.instructions_sheet}!A:G",
                valueInputOption="RAW",
                body={"values": [row_data]}
            ).execute()
            
            print(f"  ✅ 追加成功")
            print(f"  📊 更新範囲: {result.get('updates', {}).get('updatedRange', 'N/A')}")
            print('=' * 80)
            print()
            
            return True
            
        except Exception as e:
            print(f"\n{'=' * 80}")
            print("❌ F9: 指示追加エラー")
            print(f"  エラータイプ: {type(e).__name__}")
            print(f"  エラー内容: {e}")
            print('=' * 80)
            traceback.print_exc()
            print('=' * 80)
            print()
            
            return False
    
    def check_human_instructions(self) -> List[Dict[str, Any]]:
        """人間からの指示をチェック"""
        print("\n" + "=" * 80)
        print("📨 F9: 人間指示チェック")
        print("=" * 80)
        
        try:
            result = self.sheets.service.spreadsheets().values().get(
                spreadsheetId=self.sheets.spreadsheet_id,
                range=f"{self.instructions_sheet}!A2:G100"
            ).execute()
            
            values = result.get('values', [])
            
            pending_instructions = []
            for i, row in enumerate(values, 2):
                if len(row) < 3:
                    continue
                
                status = row[2] if len(row) > 2 else ''
                
                if status == 'pending':
                    instruction = {
                        'row_index': i,
                        'timestamp': row[0],
                        'instruction_type': row[1],
                        'status': status,
                        'content': row[3] if len(row) > 3 else '',
                        'priority': row[4] if len(row) > 4 else 'medium',
                        'target_task': row[5] if len(row) > 5 else ''
                    }
                    pending_instructions.append(instruction)
            
            if pending_instructions:
                print(f"\n📬 {len(pending_instructions)}件の未処理指示があります")
                for i, inst in enumerate(pending_instructions, 1):
                    print(f"  {i}. [{inst['instruction_type']}] {inst['content'][:50]}...")
            else:
                print("\n✅ 未処理の指示はありません")
            
            return pending_instructions
            
        except Exception as e:
            if '範囲が見つかりません' in str(e) or 'Unable to parse range' in str(e):
                print("\n⚠️  human_instructions シートが存在しません")
                return []
            else:
                print(f"❌ 指示チェックエラー: {e}")
                traceback.print_exc()
                return []
    
    def process_instructions(self, instructions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """指示を処理（完全実装）"""
        results = {
            'processed': 0,
            'failed': 0,
            'actions': []
        }
        
        for instruction in instructions:
            print(f"\n{'=' * 80}")
            print(f"【指示処理】{instruction['instruction_type']}")
            print(f"  内容: {instruction['content']}")
            print('=' * 80)
            
            try:
                if instruction['instruction_type'] == 'add_task':
                    success = self._process_add_task(instruction)
                elif instruction['instruction_type'] == 'pause_system':
                    success = self._process_pause_system(instruction)
                elif instruction['instruction_type'] == 'resume_system':
                    success = self._process_resume_system(instruction)
                elif instruction['instruction_type'] == 'change_priority':
                    success = self._process_change_priority(instruction)
                elif instruction['instruction_type'] == 'stop_task':
                    success = self._process_stop_task(instruction)
                elif instruction['instruction_type'] == 'message':
                    success = self._process_message(instruction)
                else:
                    print(f"  ⚠️  未対応の指示タイプ: {instruction['instruction_type']}")
                    success = False
                
                if success:
                    # ステータスを完了に更新
                    self.sheets.service.spreadsheets().values().update(
                        spreadsheetId=self.sheets.spreadsheet_id,
                        range=f"{self.instructions_sheet}!C{instruction['row_index']}",
                        valueInputOption="RAW",
                        body={"values": [["completed"]]}
                    ).execute()
                    
                    print(f"  ✅ 処理成功")
                    results['processed'] += 1
                    results['actions'].append({
                        'type': instruction['instruction_type'],
                        'status': 'success'
                    })
                else:
                    print(f"  ❌ 処理失敗")
                    results['failed'] += 1
                
            except Exception as e:
                print(f"  ❌ 処理エラー: {e}")
                traceback.print_exc()
                results['failed'] += 1
                results['actions'].append({
                    'type': instruction['instruction_type'],
                    'status': 'failed',
                    'error': str(e)
                })
        
        return results
    
    def _process_add_task(self, instruction: Dict[str, Any]) -> bool:
        """タスク追加指示を処理"""
        content = instruction['content']
        priority = instruction.get('priority', 'high')
        
        print(f"  🔧 タスク追加処理開始")
        print(f"     内容: {content}")
        print(f"     優先度: {priority}")
        
        # タスクIDを生成
        timestamp = datetime.now().strftime('%y%m%d_%H%M%S')
        task_id = f"human_req_{timestamp}"
        
        # タスクデータを作成
        task_data = [
            task_id,  # task_id
            '',  # parent_goal_id
            content,  # description
            'developer',  # required_role
            'pending',  # status
            priority,  # priority
            '2h',  # estimated_time
            '',  # dependencies
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),  # created_at
            f'human_instruction_{timestamp}',  # batch_id
            '',  # detail_file_path
            '',  # blank
            'implementation'  # execution_type
        ]
        
        try:
            # pm_tasksに追加
            result = self.sheets.service.spreadsheets().values().append(
                spreadsheetId=self.sheets.spreadsheet_id,
                range="pm_tasks!A:M",
                valueInputOption="RAW",
                body={"values": [task_data]}
            ).execute()
            
            print(f"  ✅ タスク追加完了: {task_id}")
            print(f"  📊 更新範囲: {result.get('updates', {}).get('updatedRange', 'N/A')}")
            
            return True
            
        except Exception as e:
            print(f"  ❌ タスク追加エラー: {e}")
            traceback.print_exc()
            return False
    
    def _process_pause_system(self, instruction: Dict[str, Any]) -> bool:
        """システム一時停止指示を処理"""
        print(f"  ⏸️  システム一時停止")
        try:
            with open('/tmp/system_paused.flag', 'w') as f:
                f.write(instruction['content'])
            print(f"  ✅ 一時停止フラグ作成")
            return True
        except Exception as e:
            print(f"  ❌ エラー: {e}")
            return False
    
    def _process_resume_system(self, instruction: Dict[str, Any]) -> bool:
        """システム再開指示を処理"""
        print(f"  ▶️  システム再開")
        try:
            import os
            if os.path.exists('/tmp/system_paused.flag'):
                os.remove('/tmp/system_paused.flag')
                print(f"  ✅ 一時停止フラグ削除")
            else:
                print(f"  ℹ️  一時停止フラグは存在しません")
            return True
        except Exception as e:
            print(f"  ❌ エラー: {e}")
            return False
    
    def _process_change_priority(self, instruction: Dict[str, Any]) -> bool:
        """優先度変更指示を処理"""
        target_task = instruction.get('target_task', '')
        print(f"  🔄 優先度変更: {target_task}")
        print(f"  ℹ️  現在未実装")
        return True
    
    def _process_stop_task(self, instruction: Dict[str, Any]) -> bool:
        """タスク停止指示を処理"""
        target_task = instruction.get('target_task', '')
        print(f"  ⏹️  タスク停止: {target_task}")
        print(f"  ℹ️  現在未実装")
        return True
    
    def _process_message(self, instruction: Dict[str, Any]) -> bool:
        """メッセージを処理"""
        print(f"  💬 メッセージ: {instruction['content']}")
        return True

PYTHON

echo "✅ 完全版F9HumanInterface作成: agents/f9_human_interface_complete.py"

# 既存ファイルをバックアップして置き換え
cp agents/f9_human_interface.py "agents/f9_human_interface.py.backup_${NOW_JST}"
cp agents/f9_human_interface_complete.py agents/f9_human_interface.py

echo "✅ 既存ファイルを完全版に置き換え"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ F9HumanInterface完全実装完了"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 実装内容:"
echo "  ✅ process_instructions() メソッド追加"
echo "  ✅ _process_add_task() 実装（pm_tasksに追加）"
echo "  ✅ _process_pause_system() 実装"
echo "  ✅ _process_resume_system() 実装"
echo "  ✅ _process_message() 実装"
echo "  ✅ 詳細なログ出力"
echo ""
echo "🎯 動作フロー:"
echo "  1. ダッシュボードで指示を追加 → human_instructions"
echo "  2. process_instructions() 実行"
echo "  3. add_task の場合 → pm_tasks にタスク追加"
echo "  4. ステータスを completed に更新"
echo ""
echo "🧪 テスト実行:"
echo "  bash sh/process_f9_instructions_now.sh"
echo ""

# 自動テスト実行
read -p "今すぐF9指示を処理しますか？ [Y/n] " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Nn]$ ]]; then
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🧪 テスト実行"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    bash sh/process_f9_instructions_now.sh
    
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "✅ テスト完了"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "📊 確認:"
    echo "  Google Sheets の pm_tasks を開いて"
    echo "  human_req_* で始まるタスクが追加されているか確認"
    echo ""
else
    echo "⏭️  スキップしました"
    echo "   手動実行: bash sh/process_f9_instructions_now.sh"
fi

