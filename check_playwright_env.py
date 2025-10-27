#!/usr/bin/env python3
"""
Playwright環境チェックスクリプト
"""

import subprocess
import sys
import os


def run_command(cmd):
    """コマンド実行"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)


def check_system_deps():
    """システム依存関係チェック"""
    print("🔍 システム依存関係チェック...")

    deps = [
        "libatk1.0-0",
        "libatk-bridge2.0-0",
        "libcups2",
        "libdrm2",
        "libxkbcommon0",
        "libatspi2.0-0",
        "libxcomposite1",
        "libxdamage1",
        "libxfixes3",
        "libxrandr2",
        "libgbm1",
        "libasound2",
        "libnss3",
    ]

    missing = []
    for dep in deps:
        success, stdout, stderr = run_command(f"dpkg -l | grep {dep}")
        if not success:
            missing.append(dep)

    if missing:
        print(f"❌ 不足している依存関係: {missing}")
        return False
    else:
        print("✅ システム依存関係 OK")
        return True


def check_playwright():
    """Playwrightチェック"""
    print("🔍 Playwrightチェック...")

    # Pythonパッケージ
    success, stdout, stderr = run_command("python -c 'import playwright; print(playwright.__version__)'")
    if success:
        print(f"✅ Playwrightバージョン: {stdout.strip()}")
    else:
        print("❌ Playwrightがインストールされていません")
        return False

    # ブラウザチェック
    success, stdout, stderr = run_command("python -m playwright --version")
    if success:
        print(f"✅ Playwright CLI: {stdout.strip()}")
    else:
        print("❌ Playwright CLIが利用できません")
        return False

    return True


def check_browsers():
    """ブラウザチェック"""
    print("🔍 ブラウザチェック...")

    browsers = ["chromium", "firefox", "webkit"]
    installed = []

    for browser in browsers:
        success, stdout, stderr = run_command(f"python -m playwright install {browser} --dry-run")
        if "Already installed" in stdout or "Installing" in stdout:
            installed.append(browser)

    if installed:
        print(f"✅ インストール済みブラウザ: {installed}")
        return True
    else:
        print("❌ ブラウザがインストールされていません")
        return False


def main():
    print("🚀 Playwright環境チェック開始")
    print("=" * 50)

    checks = [check_system_deps(), check_playwright(), check_browsers()]

    print("=" * 50)
    if all(checks):
        print("🎉 すべてのチェックが成功しました！")
        print("✅ ブラウザ自動化を実行できます")
    else:
        print("❌ 環境設定に問題があります")
        print("\n💡 解決策:")
        print("   以下のコマンドを実行してください:")
        print(
            "   sudo apt-get update && sudo apt-get install -y libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 libxrandr2 libgbm1 libasound2 libnss3"
        )
        print("   python -m playwright install")


if __name__ == "__main__":
    main()
