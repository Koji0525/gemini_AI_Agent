#!/bin/bash
# F9いつでも指示ツールの実装

cd /workspaces/gemini_AI_Agent

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔧 F9いつでも指示ツールの実装"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

NOW_JST=$(TZ=Asia/Tokyo date +%y%m%d_%H%M)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 1: CLIコマンドツールの作成
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 1: CLIコマンドツールの作成"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

cat > tools/f9_command.py << 'PYTHON'
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

PYTHON

echo "✅ F9コマンドツール作成: tools/f9_command.py"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 2: シェルラッパースクリプトの作成
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 2: シェルラッパースクリプトの作成"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

cat > f9 << 'WRAPPER'
#!/bin/bash
# F9コマンドの簡易ラッパー

cd /workspaces/gemini_AI_Agent
python3 tools/f9_command.py "$@"

WRAPPER

chmod +x f9
echo "✅ シェルラッパー作成: ./f9"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 3: 24時間稼働へのF9統合
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 3: 24時間稼働へのF9統合"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

cat > sh/run_autonomous_24h_v5_final.sh << 'AUTO'
#!/bin/bash
# 24時間自律稼働システム v5（完全版）
# F6/F9完全統合

cd /workspaces/gemini_AI_Agent

echo "🚀 24時間自律稼働開始 v5（完全版）"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "【新機能】"
echo "  ✅ F6: 動的タスク追加（品質不合格時）"
echo "  ✅ F9: 人間指示の定期チェック（毎サイクル）"
echo "  ✅ 厳格な品質評価（7点以上で合格）"
echo "  ✅ スマートタスク選択"
echo ""
echo "【F9使用方法】"
echo "  別ターミナルで以下を実行:"
echo "    ./f9                    # 対話モード"
echo "    ./f9 add -t add_task -c '新タスク' -p high"
echo "    ./f9 list --status pending"
echo ""

START_TIME=$(date +%s)
CYCLE_COUNT=0
ERROR_COUNT=0
SUCCESS_COUNT=0
MAX_CYCLES=96  # 24時間（15分間隔）

LOG_FILE="logs/autonomous_v5_$(TZ=Asia/Tokyo date +%y%m%d_%H%M).log"
mkdir -p logs

while [ $CYCLE_COUNT -lt $MAX_CYCLES ]; do
    CYCLE_COUNT=$((CYCLE_COUNT + 1))
    CURRENT_TIME=$(TZ=Asia/Tokyo date +"%Y-%m-%d %H:%M:%S")
    
    echo "" | tee -a "$LOG_FILE"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" | tee -a "$LOG_FILE"
    echo "サイクル ${CYCLE_COUNT}/${MAX_CYCLES} @ ${CURRENT_TIME}" | tee -a "$LOG_FILE"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" | tee -a "$LOG_FILE"
    
    # F9: 人間指示チェック（最優先）
    echo "  📨 F9: 人間指示チェック..." | tee -a "$LOG_FILE"
    python3 agents/f9_human_interface.py 2>&1 | tee -a "$LOG_FILE"
    
    # 一時停止フラグのチェック
    if [ -f "/tmp/system_paused.flag" ]; then
        echo "  ⏸️  システム一時停止中..." | tee -a "$LOG_FILE"
        echo "  💤 1時間待機します" | tee -a "$LOG_FILE"
        sleep 3600
        continue
    fi
    
    # F1: タスク可用性チェック
    echo "  🔄 F1: タスク可用性チェック..." | tee -a "$LOG_FILE"
    python3 agents/f1_loop_integration.py 2>&1 | tee -a "$LOG_FILE"
    
    # F2: タスク自律実行（スマート選択）
    echo "  🔄 F2: タスク実行中..." | tee -a "$LOG_FILE"
    
    if bash start_pending_tasks_fixed.sh 2 2>&1 | tee -a "$LOG_FILE"; then
        echo "  ✅ タスク実行成功" | tee -a "$LOG_FILE"
        SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
        ERROR_COUNT=0
        
    else
        echo "  ⚠️  タスク実行でエラー" | tee -a "$LOG_FILE"
        ERROR_COUNT=$((ERROR_COUNT + 1))
        
        # F7: 自己修復
        if [ $ERROR_COUNT -le 3 ]; then
            echo "  🔧 F7: 自己修復（${ERROR_COUNT}/3）" | tee -a "$LOG_FILE"
            sleep 30
        else
            echo "  ❌ F7: 修復失敗" | tee -a "$LOG_FILE"
            echo "  🚨 F9: 人間への通知が必要" | tee -a "$LOG_FILE"
            
            # F9経由で通知
            ./f9 add -t message -c "自己修復失敗: 人間の介入が必要です" -p high 2>&1 | tee -a "$LOG_FILE"
            
            sleep 3600
            ERROR_COUNT=0
        fi
    fi
    
    # F9: 進捗報告（1時間ごと）
    if [ $((CYCLE_COUNT % 4)) -eq 0 ]; then
        echo "  📊 F9: 進捗報告" | tee -a "$LOG_FILE"
        echo "     成功: ${SUCCESS_COUNT}サイクル" | tee -a "$LOG_FILE"
    fi
    
    # F10: 健全性チェック（1時間ごと）
    if [ $((CYCLE_COUNT % 4)) -eq 0 ]; then
        echo "  🔬 F10: 健全性チェック" | tee -a "$LOG_FILE"
        bash sh/health_check_periodic.sh 2>&1 | tee -a "$LOG_FILE"
    fi
    
    echo "  ⏳ 次のサイクルまで15分待機..." | tee -a "$LOG_FILE"
    sleep 900
done

END_TIME=$(date +%s)
ELAPSED=$((END_TIME - START_TIME))
ELAPSED_HOURS=$((ELAPSED / 3600))

echo "" | tee -a "$LOG_FILE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" | tee -a "$LOG_FILE"
echo "✅ 24時間自律稼働完了" | tee -a "$LOG_FILE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" | tee -a "$LOG_FILE"
echo "  実行時間: ${ELAPSED_HOURS}時間" | tee -a "$LOG_FILE"
echo "  実行サイクル: ${CYCLE_COUNT}" | tee -a "$LOG_FILE"
echo "  成功: ${SUCCESS_COUNT}サイクル" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

AUTO

chmod +x sh/run_autonomous_24h_v5_final.sh
echo "✅ 24時間稼働v5作成: sh/run_autonomous_24h_v5_final.sh"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ F9いつでも指示ツール完成"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 使用方法:"
echo ""
echo "【方法1: 対話モード（おすすめ）】"
echo "  ./f9"
echo "  → メニューから指示タイプを選択"
echo "  → 内容を入力"
echo "  → システムが自動処理"
echo ""
echo "【方法2: コマンドライン】"
echo "  # タスク追加"
echo "  ./f9 add --type add_task --content 'データベース最適化' --priority high"
echo ""
echo "  # システム一時停止"
echo "  ./f9 add --type pause_system --content 'メンテナンス' --priority high"
echo ""
echo "  # システム再開"
echo "  rm /tmp/system_paused.flag"
echo ""
echo "  # 指示一覧"
echo "  ./f9 list"
echo "  ./f9 list --status pending"
echo ""
echo "【方法3: Google Sheets直接編集】"
echo "  human_instructions シートに直接入力"
echo ""
echo "📝 指示タイプ:"
echo "  1. add_task        - タスク追加"
echo "  2. pause_system    - システム一時停止"
echo "  3. resume_system   - システム再開"
echo "  4. change_priority - 優先度変更"
echo "  5. stop_task       - タスク停止"
echo "  6. restart_task    - タスク再開"
echo "  7. message         - メッセージ"
echo "  8. emergency_stop  - 緊急停止"
echo ""
echo "🎯 テスト実行:"
echo "  ./f9"
echo ""

