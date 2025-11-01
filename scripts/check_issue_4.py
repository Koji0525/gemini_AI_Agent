#!/usr/bin/env python3
"""
🔍 Issue #4 情報確認スクリプト
"""
import os
import sys

# PyGithubのインポート確認
try:
    from github import Github
except ImportError:
    print("❌ PyGithubがインストールされていません")
    print("   pip install PyGithub --break-system-packages")
    sys.exit(1)

# GITHUB_TOKENの確認
token = os.getenv('GITHUB_TOKEN')
if not token:
    print("❌ GITHUB_TOKEN環境変数が設定されていません")
    print("\n設定方法:")
    print("  export GITHUB_TOKEN=ghp_your_token_here")
    sys.exit(1)

print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print("🔍 Issue #4 情報確認")
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

try:
    # GitHub API接続
    g = Github(token)
    repo = g.get_repo("Koji0525/gemini_AI_Agent")
    
    print(f"✅ GitHub API接続成功")
    print(f"📋 リポジトリ: {repo.full_name}")
    
    # Issue #4を取得
    issue = repo.get_issue(4)
    
    print(f"\n{'='*60}")
    print(f"📨 Issue #{issue.number}")
    print(f"{'='*60}")
    print(f"タイトル: {issue.title}")
    print(f"状態: {issue.state}")
    print(f"作成者: {issue.user.login}")
    print(f"ラベル: {[label.name for label in issue.labels]}")
    
    # コメントを取得
    comments = list(issue.get_comments())
    print(f"\n💬 コメント数: {len(comments)}")
    
    for idx, comment in enumerate(comments, 1):
        print(f"\n--- コメント {idx} ---")
        print(f"投稿者: {comment.user.login}")
        print(f"内容: {comment.body[:100]}...")
    
    print(f"\n{'='*60}")
    print("✅ Issue #4の情報取得成功")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

except Exception as e:
    print(f"❌ エラー: {e}")
    sys.exit(1)
