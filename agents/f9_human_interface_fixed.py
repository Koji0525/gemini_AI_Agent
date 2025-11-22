"""
F9: 人間指示インターフェース（修正版）
エラーハンドリングを強化
"""

import sys
import traceback
from datetime import datetime
from typing import List, Dict, Any

sys.path.insert(0, '/workspaces/gemini_AI_Agent')

class F9HumanInterface:
    """F9: 人間指示インターフェース（修正版）"""
    
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
        """指示を追加（エラーハンドリング強化版）"""
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
        """人間からの指示をチェック（既存コードを維持）"""
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

