#!/usr/bin/env python3
"""
タスク詳細エクスポートエージェント
生成されたタスクの詳細をMarkdownファイルとして保存
"""
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List


class TaskExportAgent:
    """タスク詳細をMarkdownファイルにエクスポート"""
    
    def __init__(self, output_folder: str = "agent_outputs/task_details"):
        self.output_folder = Path(output_folder)
        self.output_folder.mkdir(parents=True, exist_ok=True)
        print(f"📁 TaskExportAgent初期化: {self.output_folder}")
    
    def export_tasks(
        self,
        goal_id: str,
        goal_title: str,
        tasks: List[Dict[str, Any]]
    ) -> str:
        """
        タスクリストをMarkdownファイルにエクスポート
        
        Args:
            goal_id: 目標ID
            goal_title: 目標タイトル
            tasks: タスクリスト
        
        Returns:
            エクスポートしたファイルのパス
        """
        if not tasks:
            print("⚠️ エクスポートするタスクがありません")
            return ""
        
        print(f"\n📤 タスク詳細をエクスポート中（目標{goal_id}）...")
        
        # ファイル名を生成
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"goal_{goal_id}_tasks_{timestamp}.md"
        filepath = self.output_folder / filename
        
        # Markdownコンテンツを生成
        content = self._generate_markdown(goal_id, goal_title, tasks)
        
        # ファイルに保存
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ エクスポート完了: {filepath}")
        print(f"   タスク数: {len(tasks)}個")
        
        return str(filepath)
    
    def _generate_markdown(
        self,
        goal_id: str,
        goal_title: str,
        tasks: List[Dict[str, Any]]
    ) -> str:
        """Markdownコンテンツを生成"""
        
        content = f"""# 📋 目標{goal_id}のタスク詳細

## 目標情報
- **目標ID**: {goal_id}
- **目標名**: {goal_title}
- **タスク数**: {len(tasks)}個
- **生成日時**: {datetime.now().strftime("%Y年%m月%d日 %H:%M:%S")}

---

"""
        
        # 各タスクの詳細を追加
        for i, task in enumerate(tasks, 1):
            task_title = task.get('title', 'タイトル未設定')
            description = task.get('description', '説明なし')
            agent = task.get('agent', 'unknown')
            execution_type = task.get('execution_type', 'gemini')
            priority = task.get('priority', 'medium')
            estimated_hours = task.get('estimated_hours', 0)
            dependencies = task.get('dependencies', '')
            
            content += f"""## タスク{i}: {task_title}

**基本情報**
- **実行エージェント**: {agent}
- **実行タイプ**: {execution_type}
- **優先度**: {priority}
- **見積時間**: {estimated_hours}時間
- **依存関係**: {dependencies if dependencies else 'なし'}

**詳細説明**

{description}

---

"""
        
        # フッター
        content += f"""
## 📊 サマリー

| 項目 | 値 |
|------|-----|
| 目標ID | {goal_id} |
| タスク総数 | {len(tasks)}個 |
| 合計見積時間 | {sum(t.get('estimated_hours', 0) for t in tasks)}時間 |
| WordPress専用 | {sum(1 for t in tasks if t.get('execution_type') == 'wordpress')}個 |
| Gemini実行 | {sum(1 for t in tasks if t.get('execution_type') == 'gemini')}個 |
| 高優先度 | {sum(1 for t in tasks if t.get('priority') == 'high')}個 |

---

**生成元**: Gemini AI統合版PM Agent  
**エクスポート日時**: {datetime.now().strftime("%Y年%m月%d日 %H:%M:%S")}
"""
        
        return content


# テスト実行
def test_task_exporter():
    """TaskExportAgentのテスト"""
    print("=" * 70)
    print("🧪 TaskExportAgentのテスト")
    print("=" * 70)
    
    exporter = TaskExportAgent()
    
    # テストデータ
    test_tasks = [
        {
            "title": "M&A案件CPT要件定義",
            "description": """【目的】
M&A案件管理のためのカスタム投稿タイプの要件を明確化

【ゴール条件】
- 必要なフィールドが特定されている
- データ構造が設計されている

【具体的要件】
1. 案件情報フィールドの洗い出し
2. データ構造の設計
3. カスタムタクソノミーの検討

【完了判定】
- [ ] 要件定義書が作成されている
- [ ] フィールドリストが完成している

【注意事項】
WordPressのベストプラクティスに従う""",
            "agent": "design",
            "execution_type": "gemini",
            "priority": "high",
            "estimated_hours": 4,
            "dependencies": ""
        },
        {
            "title": "M&A案件CPT実装",
            "description": """【目的】
M&A案件を管理するカスタム投稿タイプを作成

【ゴール条件】
- CPTがWordPressに登録されている
- 管理画面に表示される

【具体的要件】
- 投稿タイプ名: ma_deal
- functions.phpに登録コードを追加

【完了判定】
- [ ] CPTが管理画面に表示される

【注意事項】
テスト環境で動作確認すること""",
            "agent": "wordpress",
            "execution_type": "wordpress",
            "priority": "medium",
            "estimated_hours": 8,
            "dependencies": "1"
        }
    ]
    
    # エクスポート
    filepath = exporter.export_tasks(
        goal_id="4",
        goal_title="ウズベキスタンM&A案件管理システム構築",
        tasks=test_tasks
    )
    
    print("\n" + "=" * 70)
    print(f"✅ テスト完了")
    print(f"📄 生成されたファイル: {filepath}")
    print("=" * 70)


if __name__ == "__main__":
    test_task_exporter()
