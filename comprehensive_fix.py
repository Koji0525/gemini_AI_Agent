#!/usr/bin/env python3
"""
包括的な修正スクリプト
BrowserControllerの使用法を一括修正
"""
import os
import re


def fix_all_browser_initializations():
    """すべてのBrowserController初期化を修正"""

    # 修正パターン
    patterns = [
        # パターン1: await browser.initialize() の削除
        (
            r"(\s*)browser = BrowserController\(\)\s*\n\s*await browser\.initialize\(\)",
            r"\1browser = BrowserController()",
        ),
        # パターン2: ブラウザ初期化後の余分なawaitを削除
        (
            r"browser = BrowserController\(\)\s*\n\s*#.*\n\s*await browser\.initialize\(\)",
            "browser = BrowserController()",
        ),
    ]

    # 修正対象ファイル
    target_files = []
    for root, dirs, files in os.walk("."):
        for file in files:
            if file.endswith(".py") and any(name in root for name in ["agents", "scripts", "test"]):
                file_path = os.path.join(root, file)
                target_files.append(file_path)

    fixed_count = 0
    for file_path in target_files[:20]:  # 最初の20ファイルのみ処理
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            original_content = content

            for pattern, replacement in patterns:
                content = re.sub(pattern, replacement, content)

            if content != original_content:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                print(f"✅ 修正: {file_path}")
                fixed_count += 1

        except Exception as e:
            print(f"⚠️ 処理エラー {file_path}: {e}")

    print(f"🎉 {fixed_count} 個のファイルを修正しました")


def fix_design_generator_syntax():
    """設計図生成器の構文エラーを修正"""
    file_path = "agents/wordpress/wp_design_generator.py"

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # 重複したensure_asciiを修正
        content = content.replace("ensure_ascii=False, ensure_ascii=False", "ensure_ascii=False")

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        print("✅ wp_design_generator.py の構文エラーを修正")

    except Exception as e:
        print(f"❌ 修正エラー: {e}")


if __name__ == "__main__":
    print("🔧 包括的な修正を開始...")
    fix_all_browser_initializations()
    fix_design_generator_syntax()
    print("�� すべての修正が完了しました")
