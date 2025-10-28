#!/usr/bin/env python3
"""
既存のBrowserControllerの使用法を分析
"""
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

try:
    from browser_control.browser_controller import BrowserController

    print("✅ BrowserController インポート成功")

    # メソッド一覧を確認
    import inspect

    methods = [m for m in dir(BrowserController) if not m.startswith("_")]
    print("📋 BrowserController の公開メソッド:")
    for method in methods[:10]:  # 最初の10個だけ表示
        print(f"  - {method}")

except Exception as e:
    print(f"❌ インポートエラー: {e}")
    import traceback

    traceback.print_exc()
