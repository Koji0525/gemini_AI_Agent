#!/usr/bin/env python3
"""
ConfigLoaderの詳細確認スクリプト
"""
import sys
import os

sys.path.insert(0, ".")

print("=" * 60)
print("🔍 ConfigLoader詳細確認")
print("=" * 60)
print()

# ConfigLoaderのソースコードを確認
print("【1】ConfigLoaderのソースコード確認")
print("-" * 40)

config_file = "configuration/config_loader.py"
if os.path.exists(config_file):
    with open(config_file, "r", encoding="utf-8") as f:
        content = f.read()

    print(f"ファイルサイズ: {len(content)} bytes")
    print()
    print("--- ソースコード（最初の100行）---")
    lines = content.split("\n")
    for i, line in enumerate(lines[:100], 1):
        print(f"{i:3d}: {line}")
    print("--- ソースコード終わり ---")
else:
    print(f"❌ {config_file} が見つかりません")

print()
print("=" * 60)
print("【2】ConfigLoaderインスタンスの確認")
print("=" * 60)
print()

try:
    from configuration.config_loader import ConfigLoader

    config = ConfigLoader()

    # すべての属性を確認
    print("📋 すべての属性:")
    all_attrs = dir(config)
    for attr in all_attrs:
        if not attr.startswith("_"):
            value = getattr(config, attr, None)
            attr_type = type(value).__name__
            print(f"   - {attr}: {attr_type}")
            if not callable(value):
                print(f"     値: {value}")

    print()
    print("【3】.envファイルの確認")
    print("-" * 40)

    if os.path.exists(".env"):
        with open(".env", "r") as f:
            env_content = f.read()

        print("📄 .envファイルの内容:")
        for line in env_content.split("\n"):
            if line.strip() and not line.startswith("#"):
                # パスワードをマスク
                if "PASS" in line:
                    key = line.split("=")[0]
                    print(f"   {key}=***")
                else:
                    print(f"   {line}")
    else:
        print("❌ .envファイルが見つかりません")

    print()
    print("【4】環境変数の確認")
    print("-" * 40)

    wp_vars = ["WP_URL", "WP_USER", "WP_PASS"]
    for var in wp_vars:
        value = os.getenv(var, "NOT SET")
        if "PASS" in var and value != "NOT SET":
            print(f"   {var}: ***")
        else:
            print(f"   {var}: {value}")

except Exception as e:
    print(f"❌ エラー: {e}")
    import traceback

    traceback.print_exc()

print()
print("=" * 60)
print("💡 次のアクション")
print("=" * 60)
print()
print("1. ConfigLoaderがどのように.envを読み込んでいるか確認")
print("2. 正しいアクセス方法を特定")
print("3. WPAutoLoginを修正")
