#!/usr/bin/env python3
"""ReviewAgent.__init__を完全に書き直し（インデント完璧版）"""

from pathlib import Path
import re

def rebuild_review_agent_init():
    print("🔧 ReviewAgent.__init__ 完全書き直し")
    print("=" * 70)
    
    file_path = Path("core_agents/review_agent.py")
    
    # 読み込み
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # バックアップ
    backup_path = Path("core_agents/review_agent.py.backup_rebuild")
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ バックアップ: {backup_path}")
    
    # 新しい__init__メソッド（完璧なインデント）
    new_init = '''    def __init__(self, browser_controller=None, browser=None, output_folder: Path = None):
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
        
        self.output_folder.mkdir(parents=True, exist_ok=True)
        
        # その他の初期化
        self.sheets_manager = None
        self.system_prompt = REVIEW_SYSTEM_PROMPT
'''
    
    # __init__メソッド全体を置換（次のdefまで）
    # パターン: def __init__ から次の def または class まで
    pattern = r'(    def __init__\(self.*?\n)(.*?)(\n    def |\n    async def |\nclass )'
    
    # 置換実行
    def replace_init(match):
        # 新しい__init__ + 次のメソッド/クラスの開始部分
        return new_init + match.group(3)
    
    new_content = re.sub(pattern, replace_init, content, flags=re.DOTALL)
    
    # 保存
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ ReviewAgent.__init__を完全に書き直しました")
    print()
    print("=" * 70)
    
    return True

if __name__ == "__main__":
    rebuild_review_agent_init()
