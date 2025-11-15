#!/usr/bin/env python3
"""プロジェクト構造を整理してsetuptools問題を解決"""

import os
import shutil
from pathlib import Path

def organize_project():
    """プロジェクト構造を整理"""
    project_root = Path(".")
    
    # Pythonパッケージとして認識すべきディレクトリ
    python_packages = [
        "agents", "core_agents", "task_executor", "browser_control",
        "configuration", "tools", "knowledge_system"
    ]
    
    # 非Pythonディレクトリ（別場所に移動）
    non_python_dirs = [
        "md", "sh", "MD", "log", "backups", "configs", "templates",
        "temp_texts", "text_files", "poc_output", "test_reports",
        "backup_files", "conversations", "agent_outputs",
        "markdown_files", "content_writers", "notebookLM_move",
        "wordpress_projects", "final_backup_20251104_195511",
        "git_cleanup_backup_20251104_200146"
    ]
    
    # _PROMPTディレクトリ作成（非Pythonファイル用）
    prompt_dir = project_root / "_PROMPT"
    prompt_dir.mkdir(exist_ok=True)
    
    # 非Pythonディレクトリを_PROMPTに移動
    moved_dirs = []
    for dir_name in non_python_dirs:
        dir_path = project_root / dir_name
        if dir_path.exists() and dir_path.is_dir():
            # _PROMPT内にサブディレクトリ作成
            target_dir = prompt_dir / dir_name
            if not target_dir.exists():
                shutil.move(str(dir_path), str(target_dir))
                moved_dirs.append(dir_name)
                print(f"✅ 移動: {dir_name} → _PROMPT/{dir_name}")
    
    print(f"📁 移動完了: {len(moved_dirs)}個のディレクトリ")
    
    # .gitignoreを更新
    gitignore_content = """
# 非Pythonリソース
_PROMPT/
*.log
*.backup
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.venv/
"""
    with open(".gitignore", "a", encoding="utf-8") as f:
        f.write(gitignore_content)
    
    print("✅ .gitignoreを更新")
    
    # 整理後の構造を表示
    print("\n📁 整理後のプロジェクト構造:")
    for item in project_root.iterdir():
        if item.is_dir() and not item.name.startswith('.'):
            print(f"  📂 {item.name}/")
        elif item.is_file() and item.suffix in ['.py', '.md', '.txt']:
            print(f"  📄 {item.name}")

if __name__ == "__main__":
    organize_project()
