#!/usr/bin/env python3
"""
🏷️ bot-controlラベル作成＆Issue #4に追加
"""
import os
import sys

try:
    from github import Github, Auth, GithubException
except ImportError:
    print("❌ PyGithubがインストールされていません")
    sys.exit(1)

# GITHUB_TOKEN確認
token = os.getenv('GITHUB_TOKEN')
if not token:
    print("❌ GITHUB_TOKEN環境変数が設定されていません")
    sys.exit(1)

print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print("🏷️ bot-controlラベル作成＆追加")
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

try:
    # 新しいAPI使用方法（DeprecationWarning対策）
    auth = Auth.Token(token)
    g = Github(auth=auth)
    repo = g.get_repo("Koji0525/gemini_AI_Agent")
    
    print(f"✅ GitHub API接続成功")
    print(f"📋 リポジトリ: {repo.full_name}")
    
    # ラベル作成（存在しない場合）
    print("\n🔍 bot-controlラベルを確認中...")
    
    try:
        label = repo.get_label("bot-control")
        print(f"✅ bot-controlラベルは既に存在します")
    except GithubException:
        print(f"📝 bot-controlラベルを作成します...")
        label = repo.create_label(
            name="bot-control",
            color="7057ff",
            description="Bot制御用Issue"
        )
        print(f"✅ bot-controlラベルを作成しました")
    
    # Issue #4にラベルを追加
    print("\n📨 Issue #4にラベルを追加中...")
    issue = repo.get_issue(4)
    
    current_labels = [l.name for l in issue.labels]
    print(f"   現在のラベル: {current_labels}")
    
    if "bot-control" not in current_labels:
        issue.add_to_labels("bot-control")
        print(f"✅ bot-controlラベルを追加しました")
    else:
        print(f"✅ bot-controlラベルは既に付いています")
    
    # 確認
    issue = repo.get_issue(4)
    updated_labels = [l.name for l in issue.labels]
    print(f"   更新後のラベル: {updated_labels}")
    
    # コメントがない場合は追加
    comments = list(issue.get_comments())
    if len(comments) == 0:
        print("\n💬 テストコメントを追加します...")
        issue.create_comment("@bot help")
        print("✅ テストコメント追加完了")
    
    print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🎉 すべて完了！")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("\n次のアクション:")
    print("  bash scripts/test_human_interaction.sh")

except Exception as e:
    print(f"❌ エラー: {e}")
    sys.exit(1)
