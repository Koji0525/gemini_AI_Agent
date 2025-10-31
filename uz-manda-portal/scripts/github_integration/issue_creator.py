"""
GitHub Issues自動生成
品質スコアが低い場合に改善提案Issueを自動作成
"""

import os
import json
from typing import Dict
from datetime import datetime

class GitHubIssueCreator:
    """GitHub Issue自動作成"""
    
    def __init__(self, repo: str = None, token: str = None):
        self.repo = repo or os.getenv('GITHUB_REPOSITORY', 'your-repo')
        self.token = token or os.getenv('GITHUB_TOKEN')
        
        if not self.token:
            print("⚠️ GITHUB_TOKENが設定されていません")
    
    def create_improvement_issue(self, result: Dict):
        """改善提案Issueを作成"""
        
        quality_score = result['results'].get('quality_score', 0)
        
        # 品質スコアが8未満の場合にIssue作成
        if quality_score >= 8.0:
            print("✅ 品質スコアが高いため、Issue作成不要")
            return None
        
        if not self.token:
            print("⚠️ GitHub Issue作成スキップ（Token未設定）")
            return None
        
        title = f"🔧 WordPress自動投稿の品質改善 - スコア {quality_score:.1f}/10"
        
        body = f"""## 📊 実行結果

- **実行日時**: {result.get('timestamp', 'N/A')}
- **品質スコア**: {quality_score:.1f}/10 ⚠️
- **成功**: {result['results']['successful_posts']}社
- **失敗**: {result['results']['failed_posts']}社

## 💡 改善提案

品質スコアが8.0未満です。以下の点を確認してください：

1. ❌ 失敗した投稿の原因分析
2. 🔄 リトライ戦略の見直し
3. 🔍 WordPress接続の安定性確認
4. 📝 DD項目の完全性チェック

## 🔗 関連ログ

- タスクID: `{result.get('task_id', 'N/A')}`
- 実行時間: {result.get('execution_time', 'N/A')}

---

*このIssueは自動生成されました*
"""
        
        # 実際のIssue作成はGitHub APIを使用（ここでは構造のみ）
        issue_data = {
            'title': title,
            'body': body,
            'labels': ['auto-generated', 'improvement', 'wordpress'],
            'assignees': []
        }
        
        print(f"📝 Issue作成予定: {title}")
        
        # TODO: GitHub API呼び出しを実装
        # requests.post(f'https://api.github.com/repos/{self.repo}/issues', ...)
        
        return issue_data

