"""
F9コマンドツール
いつでも簡単に指示を追加できるCLIツール
"""

import sys
import argparse
from datetime import datetime

sys.path.insert(0, '/workspaces/gemini_AI_Agent')

from tools.sheets_manager import GoogleSheetsManager

class F9Command:
    """F9コマンドツール"""
    
    INSTRUCTION_TYPES = [
        'add_task',
        'pause_system',
        'resume_system',
        'change_priority',
        'stop_task',
        'restart_task',
        'message',
        'emergency_stop'
    ]
    
    PRIORITIES = ['high', 'medium', 'low']
    
    def __init__(self):
        self.sheets = GoogleSheetsManager()
        self.instructions_sheet = "human_instructions"
        
    def add_instruction(
        self,
        instruction_type: str,
        content: str,
        priority: str = 'medium',
        target_task: str = ''
    ) -> bool:
        """指示を追加"""
        print("\n" + "=" * 80)
        print("📝 F9: 指示を追加")
        print("=" * 80)
        
        # バリデーション
        if instruction_type not in self.INSTRUCTION_TYPES:
            print(f"❌ 無効な指示タイプ: {instruction_type}")
            print(f"   利用可能: {', '.join(self.INSTRUCTION_TYPES)}")
            return False
        
        if priority not in self.PRIORITIES:
            print(f"❌ 無効な優先度: {priority}")
            print(f"   利用可能: {', '.join(self.PRIORITIES)}")
            return False
        
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
        
        try:
            # Google Sheetsに追加
            self.sheets.service.spreadsheets().values().append(
                spreadsheetId=self.sheets.spreadsheet_id,
                range=f"{self.instructions_sheet}!A:G",
                valueInputOption="RAW",
                body={"values": [row_data]}
            ).execute()
            
            print(f"\n✅ 指示を追加しました")
            print(f"   タイプ: {instruction_type}")
            print(f"   内容: {content}")
            print(f"   優先度: {priority}")
            
            if target_task:
                print(f"   対象タスク: {target_task}")
            
            print(f"\n📋 システムが次のサイクルで自動処理します")
            return True
            
        except Exception as e:
            print(f"❌ 指示追加エラー: {e}")
            return False
    
    def list_instructions(self, status: str = None):
        """指示一覧を表示"""
        print("\n" + "=" * 80)
        print("📋 F9: 指示一覧")
        print("=" * 80)
        
        try:
            result = self.sheets.service.spreadsheets().values().get(
                spreadsheetId=self.sheets.spreadsheet_id,
                range=f"{self.instructions_sheet}!A2:G100"
            ).execute()
            
            values = result.get('values', [])
            
            if not values:
                print("\n📭 指示がありません")
                return
            
            # フィルタリング
            filtered = []
            for row in values:
                if len(row) < 3:
                    continue
                
                inst_status = row[2] if len(row) > 2 else ''
                
                if status is None or inst_status == status:
                    filtered.append(row)
            
            if not filtered:
                print(f"\n📭 {status}の指示がありません")
                return
            
            # 表示
            print(f"\n【{status or '全て'}の指示】{len(filtered)}件")
            print()
            
            for i, row in enumerate(filtered, 1):
                timestamp = row[0] if len(row) > 0 else ''
                inst_type = row[1] if len(row) > 1 else ''
                inst_status = row[2] if len(row) > 2 else ''
                content = row[3] if len(row) > 3 else ''
                priority = row[4] if len(row) > 4 else ''
                
                status_icon = {
                    'pending': '⏳',
                    'completed': '✅',
                    'failed': '❌'
                }.get(inst_status, '❓')
                
                priority_icon = {
                    'high': '🔴',
                    'medium': '🟡',
                    'low': '🟢'
                }.get(priority, '')
                
                print(f"{i}. {status_icon} [{inst_type}] {priority_icon} {priority}")
                print(f"   {timestamp}")
                print(f"   {content[:80]}{'...' if len(content) > 80 else ''}")
                print()
            
        except Exception as e:
            print(f"❌ 一覧取得エラー: {e}")
    
    def interactive_mode(self):
        """対話モード"""
        print("\n" + "=" * 80)
        print("💬 F9: 対話モード")
        print("=" * 80)
        print("\nいつでも指示を追加できます。終了するには 'quit' と入力してください。")
        
        while True:
            print("\n" + "-" * 80)
            print("【指示タイプ】")
            for i, itype in enumerate(self.INSTRUCTION_TYPES, 1):
                print(f"  {i}. {itype}")
            
            print("\n  0. 一覧表示")
            print("  q. 終了")
            
            choice = input("\n選択してください: ").strip()
            
            if choice in ['q', 'quit', 'exit']:
                print("\n👋 終了します")
                break
            
            if choice == '0':
                self.list_instructions(status='pending')
                continue
            
            try:
                choice_num = int(choice)
                if 1 <= choice_num <= len(self.INSTRUCTION_TYPES):
                    instruction_type = self.INSTRUCTION_TYPES[choice_num - 1]
                else:
                    print("❌ 無効な選択です")
                    continue
            except ValueError:
                print("❌ 数字を入力してください")
                continue
            
            # 内容入力
            content = input("\n📝 指示内容を入力してください: ").strip()
            if not content:
                print("❌ 内容は必須です")
                continue
            
            # 優先度選択
            print("\n【優先度】")
            print("  1. high   (🔴 高)")
            print("  2. medium (🟡 中)")
            print("  3. low    (🟢 低)")
            
            priority_choice = input("\n優先度を選択 [1-3] (デフォルト: 2): ").strip() or '2'
            priority = {
                '1': 'high',
                '2': 'medium',
                '3': 'low'
            }.get(priority_choice, 'medium')
            
            # 対象タスク（オプション）
            target_task = input("\n対象タスクID (オプション、Enterでスキップ): ").strip()
            
            # 確認
            print("\n" + "-" * 80)
            print("【確認】")
            print(f"  タイプ: {instruction_type}")
            print(f"  内容: {content}")
            print(f"  優先度: {priority}")
            if target_task:
                print(f"  対象タスク: {target_task}")
            
            confirm = input("\nこの指示を追加しますか？ [y/N] ").strip().lower()
            
            if confirm == 'y':
                self.add_instruction(instruction_type, content, priority, target_task)
            else:
                print("❌ キャンセルしました")

def main():
    """メイン実行"""
    parser = argparse.ArgumentParser(
        description='F9: 人間指示ツール - いつでも指示を追加できます',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  # 対話モード
  python3 tools/f9_command.py

  # タスク追加
  python3 tools/f9_command.py add --type add_task --content "データベース最適化を実装" --priority high

  # システム一時停止
  python3 tools/f9_command.py add --type pause_system --content "メンテナンスのため一時停止"

  # 指示一覧
  python3 tools/f9_command.py list
  python3 tools/f9_command.py list --status pending
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='コマンド')
    
    # addコマンド
    add_parser = subparsers.add_parser('add', help='指示を追加')
    add_parser.add_argument('--type', '-t', required=True, 
                           choices=F9Command.INSTRUCTION_TYPES,
                           help='指示タイプ')
    add_parser.add_argument('--content', '-c', required=True,
                           help='指示内容')
    add_parser.add_argument('--priority', '-p', default='medium',
                           choices=F9Command.PRIORITIES,
                           help='優先度 (デフォルト: medium)')
    add_parser.add_argument('--target', default='',
                           help='対象タスクID (オプション)')
    
    # listコマンド
    list_parser = subparsers.add_parser('list', help='指示一覧を表示')
    list_parser.add_argument('--status', '-s',
                            choices=['pending', 'completed', 'failed'],
                            help='ステータスでフィルタ')
    
    args = parser.parse_args()
    
    f9 = F9Command()
    
    if args.command == 'add':
        f9.add_instruction(
            instruction_type=args.type,
            content=args.content,
            priority=args.priority,
            target_task=args.target
        )
    elif args.command == 'list':
        f9.list_instructions(status=args.status)
    else:
        # デフォルトは対話モード
        f9.interactive_mode()

if __name__ == "__main__":
    main()

