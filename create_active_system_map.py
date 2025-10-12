#!/usr/bin/env python3
"""
今動いているアクティブなシステムの構成図を作成
"""
from pathlib import Path
import json

def analyze_active_system():
    """アクティブなシステムを分析"""
    
    # 依存関係レポートを読み込み
    if Path('dependency_report.json').exists():
        with open('dependency_report.json', 'r') as f:
            dep_report = json.load(f)
        used_files = set(dep_report.get('used_files', []))
    else:
        used_files = set()
    
    # メインエントリーポイント
    main_scripts = {
        'integrated_system_with_review.py': {
            'status': '⚠️ エラーあり',
            'description': 'メインの統合システム（WordPressとレビュー連携）',
            'priority': 'HIGH'
        },
        'run_multi_agent.py': {
            'status': '✅ 動作中',
            'description': 'マルチエージェント実行システム',
            'priority': 'HIGH'
        },
        'test_tasks.py': {
            'status': '✅ テスト完了',
            'description': '基本システムテスト',
            'priority': 'MEDIUM'
        },
        'test_tasks_practical.py': {
            'status': '✅ 実践テスト完了',
            'description': 'WordPress/Sheets実践テスト',
            'priority': 'MEDIUM'
        }
    }
    
    # コアモジュール
    core_modules = {
        'Browser': [
            'browser_controller.py',
            'browser_lifecycle.py',
            'browser_ai_chat_agent.py',
            'browser_wp_session_manager.py',
            'brower_cookie_and_session.py'
        ],
        'WordPress': [
            'wordpress/wp_post_creator.py',
            'wordpress/wp_post_editor.py',
            'wordpress/wp_auth.py',
            'wordpress/wp_agent.py'
        ],
        'Sheets': [
            'sheets_manager.py'
        ],
        'Review': [
            'review_agent.py',
            'review_agent_prompts.py'
        ],
        'Agents': [
            'pm_agent.py',
            'dev_agent.py',
            'design_agent.py',
            'content_writer_agent.py'
        ],
        'Config': [
            'config_utils.py',
            'config_hybrid.py'
        ]
    }
    
    # Markdown形式で出力
    output = []
    output.append("# 🎯 アクティブシステム構成図")
    output.append(f"\n📅 生成日時: {Path('backup_analysis.json').stat().st_mtime if Path('backup_analysis.json').exists() else 'N/A'}\n")
    
    output.append("## 🚀 メインエントリーポイント\n")
    for script, info in main_scripts.items():
        status = info['status']
        desc = info['description']
        priority = info['priority']
        in_use = '✓ 使用中' if script in used_files else '⚠️ 未使用'
        
        output.append(f"### {script}")
        output.append(f"- **ステータス**: {status}")
        output.append(f"- **説明**: {desc}")
        output.append(f"- **優先度**: {priority}")
        output.append(f"- **使用状況**: {in_use}\n")
    
    output.append("\n## 🔧 コアモジュール構成\n")
    for category, modules in core_modules.items():
        output.append(f"### {category}\n")
        for module in modules:
            exists = '✓' if Path(module).exists() else '✗'
            in_use = '(使用中)' if module in used_files else ''
            output.append(f"- {exists} `{module}` {in_use}")
        output.append("")
    
    output.append("\n## ⚠️ 既知の問題\n")
    output.append("### 1. ブラウザ初期化エラー")
    output.append("- **エラー**: `'NoneType' object has no attribute 'goto'`")
    output.append("- **場所**: WordPressエグゼキューター")
    output.append("- **原因**: ブラウザコントローラーが未初期化\n")
    
    output.append("### 2. レビューAIエラー")
    output.append("- **エラー**: `'NoneType' object has no attribute 'send_prompt'`")
    output.append("- **場所**: レビューエージェント")
    output.append("- **原因**: ブラウザコントローラーとの連携不備\n")
    
    output.append("\n## 📝 次のアクション\n")
    output.append("1. ✅ バックアップファイルの整理（安全な削除）")
    output.append("2. 🔧 ブラウザ初期化の統一")
    output.append("3. 🐛 エラーハンドリングの強化")
    output.append("4. 🧪 integrated_system_with_review.py の修正\n")
    
    # ファイルに保存
    content = '\n'.join(output)
    with open('ACTIVE_SYSTEM_MAP.md', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ ACTIVE_SYSTEM_MAP.md を作成しました")
    print("\n" + "=" * 80)
    print(content)
    print("=" * 80)

if __name__ == "__main__":
    analyze_active_system()
