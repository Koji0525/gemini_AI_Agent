"""
F9指示処理スクリプト
human_instructionsシートの指示を処理してpm_tasksに追加
"""

import sys
sys.path.insert(0, '/workspaces/gemini_AI_Agent')

from agents.f9_human_interface import F9HumanInterface
from tools.sheets_manager import GoogleSheetsManager

def main():
    """F9指示を処理"""
    print("\n" + "=" * 80)
    print("🔄 F9指示処理開始")
    print("=" * 80)
    
    # 初期化
    sheets = GoogleSheetsManager()
    f9 = F9HumanInterface(sheets)
    
    # 未処理の指示をチェック
    instructions = f9.check_human_instructions()
    
    if not instructions:
        print("\n✅ 処理すべき指示はありません")
        return
    
    print(f"\n�� {len(instructions)}件の指示を処理します")
    
    # 指示を処理
    results = f9.process_instructions(instructions)
    
    print("\n" + "=" * 80)
    print("✅ F9指示処理完了")
    print("=" * 80)
    print(f"  処理成功: {results['processed']}件")
    print(f"  処理失敗: {results['failed']}件")
    print("=" * 80)
    print()

if __name__ == "__main__":
    main()

