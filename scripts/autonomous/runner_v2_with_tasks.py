#!/usr/bin/env python3
"""
24時間自律稼働ランナー v2.0 - シンプル版
VERSION_STATUS.jsonから本番環境版を直接実行
"""

import asyncio
import sys
import json
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

print("=" * 70)
print("🚀 24時間自律稼働システム起動（v2.0 - シンプル版）")
print("=" * 70)

# VERSION_STATUS.jsonを読み込み
status_file = project_root / "scripts/VERSION_STATUS.json"

if not status_file.exists():
    print(f"❌ {status_file} が見つかりません")
    sys.exit(1)

with open(status_file) as f:
    status = json.load(f)

prod_info = status.get("production", {})
prod_file = prod_info.get("file")

if not prod_file:
    print("❌ 本番環境版が指定されていません")
    sys.exit(1)

prod_path = project_root / "scripts" / prod_file

print(f"\n📦 本番環境版: {prod_file}")
print(f"   パス: {prod_path}")
print(f"   ステータス: {prod_info.get('status', 'unknown')}")

if not prod_path.exists():
    print(f"\n❌ ファイルが存在しません: {prod_path}")
    sys.exit(1)

print(f"\n✅ ファイル確認OK")

# Pythonスクリプトとして直接実行
print("\n" + "=" * 70)
print("実行開始...")
print("=" * 70 + "\n")

# sys.argvを調整（オプション引数を渡せるように）
sys.argv = [str(prod_path)]

# 直接実行
try:
    with open(prod_path) as f:
        code = compile(f.read(), str(prod_path), "exec")
        exec(code, {"__name__": "__main__", "__file__": str(prod_path)})
except KeyboardInterrupt:
    print("\n⚠️  停止シグナル受信 - 正常終了")
except Exception as e:
    print(f"\n❌ 実行エラー: {e}")
    import traceback

    traceback.print_exc()
