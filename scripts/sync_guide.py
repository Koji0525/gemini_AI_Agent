#!/usr/bin/env python3
"""
同期システム使い方ガイド
"""

import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from configuration.sync_settings import *
except ImportError:
    print("❌ 設定ファイルがありません。先に設定ファイルを作成してください")
    exit(1)

print("🎯 同期システム使い方ガイド")
print("=" * 60)

print("\n📋 現在の設定:")
print(f"   自動同期: {'✅ 有効' if AUTO_SYNC_ENABLED else '❌ 無効'}")
print(f"   同期間隔: {SYNC_INTERVAL_MINUTES}分")
print(f"   最大行数: {MAX_SYNC_ROWS}行")

print("\n🔧 設定変更方法:")
print("   1. configuration/sync_settings.py を編集")
print("   2. 以下の設定を変更:")
print("      • AUTO_SYNC_ENABLED = True   # 自動同期を有効化")
print("      • SYNC_INTERVAL_MINUTES = 30 # 30分間隔に変更")
print("      • MAX_SYNC_ROWS = 50         # 最大50行に制限")

print("\n🚀 実行方法:")
print("   手動実行: python3 scripts/configurable_sync_manager.py")
print("   自動実行: AUTO_SYNC_ENABLED = True にしてから実行")

print("\n⏰ 定期実行の設定方法:")

print("\n1. 🌐 GitHub Actionsを使う場合 (推奨)")
print("   .github/workflows/sync-progress.yml を作成:")
print("""
name: Sync Progress
on:
  schedule:
    - cron: '0 */6 * * *'  # 6時間ごと
  workflow_dispatch:        # 手動実行も可能
jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run sync
        run: python3 scripts/configurable_sync_manager.py
        env:
          GOOGLE_CREDENTIALS: ${{ secrets.GOOGLE_CREDENTIALS }}
""")

print("\n2. 🐧 Linux cronを使う場合")
print("   crontab -e で以下を追加:")
print("   */30 * * * * cd /workspaces/gemini_AI_Agent && python3 scripts/configurable_sync_manager.py")

print("\n3. 🪟 Windows Task Schedulerを使う場合")
print("   30分ごとに python scripts/configurable_sync_manager.py を実行")

print("\n🎯 推奨設定:")
print("   • 開発中: 手動モード (AUTO_SYNC_ENABLED = False)")
print("   • 本番環境: 自動モード + GitHub Actions")
print("   • テスト中: 短い間隔 (5-15分)")

print(f"\n💡 現在の設定では:")
if AUTO_SYNC_ENABLED:
    print("   ✅ 自動同期が有効です")
    print(f"   ⏰ {SYNC_INTERVAL_MINUTES}分間隔で実行されます")
else:
    print("   🔧 手動モードです")
    print("   python3 scripts/configurable_sync_manager.py で実行")

print("\n🔧 即時変更テスト:")
print("   設定を変更したい場合は、今すぐ configuration/sync_settings.py を編集してください")
