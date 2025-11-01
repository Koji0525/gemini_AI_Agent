#!/usr/bin/env python3
"""
最重要コンストラクタ修正 - 即時対応版
"""

import os
import sys
from pathlib import Path


def fix_critical_constructors():
    """最重要クラスの引数不一致を修正"""

    fixes = [
        {
            "file": "task_executor.py",
            "class": "TaskExecutor",
            "old_pattern": "TaskExecutor()",
            "new_pattern": "TaskExecutor(sheets_manager=sheets_manager, browser_controller=browser_controller)",
        },
        {
            "file": "core_agents/design_agent.py",
            "class": "DesignAgent",
            "old_pattern": "DesignAgent()",
            "new_pattern": "DesignAgent(sheets_manager=sheets_manager, browser_controller=browser_controller)",
        },
        {
            "file": "scripts/run_multi_agent.py",
            "class": "DesignAgent",
            "old_pattern": "DesignAgent(config)",
            "new_pattern": "DesignAgent(sheets_manager=sheets_manager, browser_controller=browser_controller, config=config)",
        },
        {
            "file": "scripts/run_multi_agent.py",
            "class": "DevAgent",
            "old_pattern": "DevAgent(config)",
            "new_pattern": "DevAgent(sheets_manager=sheets_manager, browser_controller=browser_controller, config=config)",
        },
    ]

    print("🔧 最重要コンストラクタ修正を開始...")

    for fix in fixes:
        file_path = Path(fix["file"])
        if file_path.exists():
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                if fix["old_pattern"] in content:
                    new_content = content.replace(fix["old_pattern"], fix["new_pattern"])
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(new_content)
                    print(f"✅ {fix['file']}: {fix['class']} を修正")
                else:
                    print(f"⚠️  {fix['file']}: パターンが見つかりません")

            except Exception as e:
                print(f"❌ {fix['file']}: 修正失敗 - {e}")
        else:
            print(f"⏭️  {fix['file']}: ファイルが存在しません")

    print("🎯 最重要修正完了")


if __name__ == "__main__":
    fix_critical_constructors()
