#!/usr/bin/env python3
"""
ReviewAgentをDesignAgent/DevAgentと同じ形式に修正
browser_controllerを受け取れるようにする
"""

import re
from pathlib import Path

def fix_review_agent():
    """ReviewAgent.__init__を修正"""
    
    print("🔧 ReviewAgent修正開始")
    print("=" * 60)
    
    review_agent_path = Path("core_agents/review_agent.py")
    
    if not review_agent_path.exists():
        print("❌ review_agent.py が見つかりません")
        return False
    
    # 元のファイルを読み込み
    with open(review_agent_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # バックアップ
    backup_path = Path("core_agents/review_agent.py.backup_browser_fix")
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ バックアップ作成: {backup_path}")
    
    # __init__メソッドを探す
    init_pattern = r'def __init__\(self\):'
    
    if re.search(init_pattern, content):
        print("✅ 引数なし__init__を発見")
        
        # 新しい__init__
        new_init = '''def __init__(self, browser_controller=None, browser=None, output_folder: Path = None):
        """
        ReviewAgent初期化
        
        Args:
            browser_controller: BrowserController インスタンス
            browser: BrowserController インスタンス（互換性用）
            output_folder: 出力フォルダパス
        """
        # ブラウザ設定（browser_controller優先）
        if browser_controller is not None:
            self.browser = browser_controller
        elif browser is not None:
            self.browser = browser
        else:
            self.browser = None
        
        # 出力フォルダ設定
        if output_folder:
            self.output_folder = Path(output_folder)
        else:
            self.output_folder = Path("agent_outputs/review")
        
        self.output_folder.mkdir(parents=True, exist_ok=True)'''
        
        # 置換
        content = re.sub(
            r'def __init__\(self\):',
            new_init,
            content,
            count=1
        )
        
        # 保存
        with open(review_agent_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ ReviewAgent.__init__を修正しました")
        print()
        print("修正内容:")
        print("  - browser_controller引数を追加")
        print("  - browser引数を追加（互換性）")
        print("  - output_folder引数を追加")
        print()
        return True
    else:
        print("⚠️ __init__の形式が想定と異なります")
        print("手動確認が必要です")
        return False

if __name__ == "__main__":
    success = fix_review_agent()
    if success:
        print("=" * 60)
        print("✅ 修正完了！次のテストを実行してください:")
        print("  DISPLAY=:1 python3 test_all_agents_browser.py")
    else:
        print("=" * 60)
        print("❌ 修正失敗。手動確認が必要です")
