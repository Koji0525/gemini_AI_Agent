#!/usr/bin/env python3
"""
WordPress健康状態チェック - AI開発加速のための予防的メンテナンス
"""

import os
import sys
from pathlib import Path


class WordPressHealthChecker:
    """WordPressの健康状態をチェック"""

    def __init__(self, wp_path=None):
        self.wp_path = wp_path or os.getenv("WP_PATH", "/workspaces/gemini_AI_Agent")
        self.required_files = ["wp-load.php", "wp-settings.php", "wp-config.php", "index.php"]
        self.required_dirs = ["wp-admin", "wp-includes", "wp-content"]

    def check_installation(self):
        """インストール状態をチェック"""
        print(f"🔍 WordPress健康チェック: {self.wp_path}")

        issues = []

        # ファイルのチェック
        for file in self.required_files:
            file_path = os.path.join(self.wp_path, file)
            if not os.path.exists(file_path):
                issues.append(f"❌ ファイル不足: {file}")
            else:
                print(f"✅ {file}")

        # ディレクトリのチェック
        for directory in self.required_dirs:
            dir_path = os.path.join(self.wp_path, directory)
            if not os.path.exists(dir_path):
                issues.append(f"❌ ディレクトリ不足: {directory}")
            else:
                print(f"✅ {directory}")

        # 結果報告
        if issues:
            print("\n🚨 問題が見つかりました:")
            for issue in issues:
                print(f"   {issue}")
            return False
        else:
            print("\n✅ WordPressインストールは正常です")
            return True

    def auto_repair(self):
        """自動修復を試みる"""
        if not self.check_installation():
            print("\n🔧 自動修復を試みます...")

            # 最小限のWordPressファイルを作成
            self.create_minimal_wp()

            # 再チェック
            return self.check_installation()
        return True

    def create_minimal_wp(self):
        """最小限のWordPressファイルを作成"""
        print("📁 最小限のWordPressファイルを作成...")

        # ディレクトリ作成
        for directory in self.required_dirs:
            dir_path = os.path.join(self.wp_path, directory)
            os.makedirs(dir_path, exist_ok=True)
            print(f"✅ ディレクトリ作成: {directory}")

        # wp-load.phpの作成
        wp_load_content = """<?php
if ( ! defined( 'ABSPATH' ) ) {
    define( 'ABSPATH', __DIR__ . '/' );
}
if ( file_exists( ABSPATH . 'wp-config.php' ) ) {
    require_once ABSPATH . 'wp-config.php';
} else {
    die( 'wp-config.php not found' );
}
?>
"""
        with open(os.path.join(self.wp_path, "wp-load.php"), "w") as f:
            f.write(wp_load_content)

        print("✅ 最小限のWordPressファイルを作成完了")


if __name__ == "__main__":
    checker = WordPressHealthChecker()

    if not checker.auto_repair():
        print("\n❌ 自動修復に失敗しました。手動での対応が必要です。")
        sys.exit(1)
    else:
        print("\n✅ WordPressの準備が完了しました")
