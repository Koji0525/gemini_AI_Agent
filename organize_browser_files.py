#!/usr/bin/env python3
"""
ブラウザ関連ファイルの整理
フォルダ構成ルールに準拠
"""

import shutil
from pathlib import Path
from datetime import datetime

def organize_browser_files():
    print("📁 ブラウザファイル整理開始")
    print("=" * 70)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # ディレクトリ作成
    dirs_to_create = [
        "_BACKUP/browser_control",
        "_ARCHIVE/browser_control",
        "_WIP/browser_control"
    ]
    
    for dir_path in dirs_to_create:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"✅ ディレクトリ作成: {dir_path}")
    
    # ファイル移動ルール
    moves = [
        # 旧browser_controller.py → ARCHIVE
        {
            "source": "browser_control/browser_controller.py",
            "dest": f"_ARCHIVE/browser_control/browser_controller_{timestamp}.py",
            "reason": "旧版（EnhancedBrowserControllerに置き換え）"
        },
        # browser_ai_chat_agent.py → ARCHIVE（機能が重複）
        {
            "source": "browser_control/browser_ai_chat_agent.py",
            "dest": f"_ARCHIVE/browser_control/browser_ai_chat_agent_{timestamp}.py",
            "reason": "機能重複（EnhancedBrowserControllerに統合）"
        },
        # browser_lifecycle.py → ARCHIVE（未使用）
        {
            "source": "browser_control/browser_lifecycle.py",
            "dest": f"_ARCHIVE/browser_control/browser_lifecycle_{timestamp}.py",
            "reason": "未使用（必要なら後で復元）"
        },
        # テストファイル群 → _WIP
        {
            "source": "test_browser_setup.py",
            "dest": "_WIP/test_browser_setup.py",
            "reason": "テストファイル"
        },
        {
            "source": "test_browser_agent_integration.py",
            "dest": "_WIP/test_browser_agent_integration.py",
            "reason": "テストファイル"
        },
        {
            "source": "test_design_agent_browser.py",
            "dest": "_WIP/test_design_agent_browser.py",
            "reason": "テストファイル"
        },
        {
            "source": "test_dev_agent_browser.py",
            "dest": "_WIP/test_dev_agent_browser.py",
            "reason": "テストファイル"
        },
        {
            "source": "test_review_agent_fixed.py",
            "dest": "_WIP/test_review_agent_fixed.py",
            "reason": "テストファイル"
        },
        {
            "source": "test_all_agents_browser.py",
            "dest": "_WIP/test_all_agents_browser.py",
            "reason": "テストファイル"
        },
        {
            "source": "test_task_executor_integration.py",
            "dest": "_WIP/test_task_executor_integration.py",
            "reason": "テストファイル"
        },
        {
            "source": "test_task_executor_debug.py",
            "dest": "_WIP/test_task_executor_debug.py",
            "reason": "テストファイル"
        }
    ]
    
    # 実行
    for move in moves:
        source = Path(move["source"])
        dest = Path(move["dest"])
        
        if source.exists():
            # バックアップは上書きしない
            if dest.exists():
                print(f"⚠️ スキップ（既存）: {move['source']}")
                continue
            
            shutil.move(str(source), str(dest))
            print(f"✅ 移動: {move['source']}")
            print(f"   → {move['dest']}")
            print(f"   理由: {move['reason']}")
        else:
            print(f"⚠️ 存在しない: {move['source']}")
    
    # EnhancedBrowserControllerをbrowser_controller.pyにリネーム（標準名に）
    print("\n📝 EnhancedBrowserController → BrowserController リネーム")
    enhanced_path = Path("browser_control/enhanced_browser_controller.py")
    standard_path = Path("browser_control/browser_controller.py")
    
    if enhanced_path.exists():
        with open(enhanced_path, 'r') as f:
            content = f.read()
        
        # クラス名は残す（EnhancedBrowserController）
        # ファイル名だけ標準化
        with open(standard_path, 'w') as f:
            f.write(content)
        
        # 元ファイルを削除
        enhanced_path.unlink()
        print(f"✅ リネーム完了")
        print(f"   browser_control/browser_controller.py")
        print(f"   （クラス名: EnhancedBrowserController）")
    
    print("\n" + "=" * 70)
    print("✅ ファイル整理完了！")
    print()
    print("📂 構造:")
    print("  browser_control/")
    print("    ├── browser_controller.py  ← 本番（EnhancedBrowserController）")
    print("    ├── __init__.py")
    print("    └── その他")
    print()
    print("  _ARCHIVE/browser_control/")
    print("    ├── browser_controller_*.py  ← 旧版")
    print("    ├── browser_ai_chat_agent_*.py  ← 旧版")
    print("    └── browser_lifecycle_*.py  ← 旧版")
    print()
    print("  _WIP/")
    print("    └── test_*.py  ← テストファイル群")

if __name__ == "__main__":
    organize_browser_files()
