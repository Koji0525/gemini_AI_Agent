"""
ツール自動統合システム
目的: 生成されたツールを即座にメインシステムに統合
"""
import shutil
from pathlib import Path
from typing import List
import os


class ToolIntegrator:
    """生成されたツールをシステムに統合"""
    
    def __init__(self):
        self.project_root = Path("/workspaces/gemini_AI_Agent")
        self.tools_dir = self.project_root / "tools"
        self.scripts_dir = self.project_root / "scripts"
    
    def integrate_cli_tool(self, task_id: str) -> bool:
        """
        CLIツールをメインシステムに統合
        
        生成された task_cli.py を scripts/ にコピーし、
        すぐに使えるようにする
        """
        source_dir = self.project_root / "agent_outputs/tasks" / f"task_{task_id}"
        cli_file = source_dir / "task_cli.py"
        
        if not cli_file.exists():
            print(f"❌ CLIファイルが見つかりません: {cli_file}")
            return False
        
        # scripts/ディレクトリにコピー
        target_file = self.scripts_dir / f"task_manager_cli.py"
        shutil.copy(cli_file, target_file)
        
        # 実行権限付与
        os.chmod(target_file, 0o755)
        
        print(f"✅ CLIツールを統合しました: {target_file}")
        print(f"\n🚀 すぐに使えます:")
        print(f"   python3 scripts/task_manager_cli.py list-tasks")
        print(f"   python3 scripts/task_manager_cli.py stats")
        
        return True
    
    def create_shortcuts(self):
        """
        よく使うコマンドのショートカットを作成
        
        例: 
        - tm list  → python3 scripts/task_manager_cli.py list-tasks
        - tm run 469 → python3 scripts/task_manager_cli.py run-task 469
        """
        shortcuts_file = self.project_root / "scripts/tm"
        
        content = '''#!/bin/bash
# タスクマネージャーショートカット
# 使用例: ./scripts/tm list, ./scripts/tm run 469

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
CLI_TOOL="$SCRIPT_DIR/task_manager_cli.py"

case "$1" in
    list|ls)
        python3 "$CLI_TOOL" list-tasks "${@:2}"
        ;;
    run|exec)
        python3 "$CLI_TOOL" run-task "${@:2}"
        ;;
    status|st)
        python3 "$CLI_TOOL" update-status "${@:2}"
        ;;
    stats)
        python3 "$CLI_TOOL" stats
        ;;
    logs)
        python3 "$CLI_TOOL" show-logs "${@:2}"
        ;;
    *)
        echo "タスクマネージャー (tm) - ショートカット"
        echo ""
        echo "使用法:"
        echo "  tm list [OPTIONS]     - タスク一覧"
        echo "  tm run TASK_ID        - タスク実行"
        echo "  tm status TASK_ID ST  - ステータス変更"
        echo "  tm stats              - 統計表示"
        echo "  tm logs               - ログ表示"
        echo ""
        echo "例:"
        echo "  tm list"
        echo "  tm run 469"
        echo "  tm stats"
        ;;
esac
'''
        
        with open(shortcuts_file, 'w') as f:
            f.write(content)
        
        os.chmod(shortcuts_file, 0o755)
        
        print(f"\n✅ ショートカット作成: {shortcuts_file}")
        print(f"\n�� さらに簡単に:")
        print(f"   ./scripts/tm list")
        print(f"   ./scripts/tm run 469")
        print(f"   ./scripts/tm stats")
