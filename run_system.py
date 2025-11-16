#!/usr/bin/env python3
"""
メインシステム実行スクリプト - 起動検証付き
"""
import sys
from pathlib import Path


def main():
    """メイン実行"""
    print("🚀 マルチエージェント開発システム起動")

    # 起動検証を実行
    try:
        from tools.startup_validator import run_startup_validation

        if not run_startup_validation():
            print("❌ 起動検証失敗 - システムを終了します")
            sys.exit(1)
    except Exception as e:
        print(f"❌ 起動検証エラー: {e}")
        sys.exit(1)

    # メインシステムの実行
    print("\n🎯 メインシステムを実行します...")
    # ここに実際のシステム実行コードを追加

    print("✅ システム正常終了")


if __name__ == "__main__":
    main()
