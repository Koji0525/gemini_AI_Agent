#!/bin/bash
echo "🔧 ワークフローファイルを適切な形式に修正します"

# complete_24h_system_plan.py を適切な形式に修正
if [ -f "complete_24h_system_plan.py" ]; then
    echo "📦 complete_24h_system_plan.py を修正..."
    # ファイルを適切なPythonスクリプトに変換
    cat > complete_24h_system_plan.py << 'PYEOF'
#!/usr/bin/env python3
"""
24時間システム計画 - ワークフロー定義
このファイルはGitHub Actionsワークフローの計画を定義します
"""

WORKFLOW_PLAN = {
    "name": "24時間AI開発システム",
    "on": {
        "workflow_dispatch": {
            "inputs": {
                "development_goal": {
                    "description": "開発目標",
                    "required": True,
                    "type": "string"
                },
                "priority": {
                    "description": "優先度",
                    "required": True,
                    "type": "choice",
                    "options": ["high", "medium", "low"]
                },
                "max_duration": {
                    "description": "最大実行時間（時間）",
                    "required": False,
                    "type": "number",
                    "default": 24
                }
            }
        },
        "schedule": [
            {"cron": "0 */6 * * *"}  # 6時間ごと
        ]
    },
    "jobs": {
        "ai_development": {
            "runs-on": "ubuntu-latest",
            "steps": [
                {
                    "name": "🎯 目標受信と設定",
                    "run": "echo '開発目標: ${{ github.event.inputs.development_goal }}'"
                }
            ]
        }
    }
}

if __name__ == "__main__":
    print("24時間システム計画ワークフロー")
    print("この計画はGitHub Actionsで使用されます")
PYEOF
    echo "✅ complete_24h_system_plan.py 修正完了"
fi

# create_integration_plan.py を適切な形式に修正
if [ -f "create_integration_plan.py" ]; then
    echo "📦 create_integration_plan.py を修正..."
    # ファイルを適切なPythonスクリプトに変換
    cat > create_integration_plan.py << 'PYEOF'
#!/usr/bin/env python3
"""
統合計画作成 - ワークフロー定義
このファイルは統合テストのワークフロー計画を定義します
"""

INTEGRATION_WORKFLOW = {
    "name": "AIエージェント統合テスト",
    "on": {
        "workflow_dispatch": {
            "inputs": {
                "development_goal": {
                    "description": "開発目標",
                    "required": True,
                    "type": "string"
                },
                "priority": {
                    "description": "優先度", 
                    "required": True,
                    "type": "choice",
                    "options": ["high", "medium", "low"]
                }
            }
        }
    },
    "jobs": {
        "goal_processing": {
            "runs-on": "ubuntu-latest", 
            "if": "github.event_name == 'workflow_dispatch'",
            "steps": [
                {
                    "name": "🎯 目標受信とスプレッドシート登録",
                    "run": "echo '目標: ${{ github.event.inputs.development_goal }}'"
                }
            ]
        }
    }
}

if __name__ == "__main__":
    print("統合計画ワークフロー")
    print("この計画は統合テストで使用されます")
PYEOF
    echo "✅ create_integration_plan.py 修正完了"
fi

echo "✅ ワークフローファイル修正完了"
