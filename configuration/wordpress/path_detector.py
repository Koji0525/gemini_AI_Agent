#!/usr/bin/env python3
"""
WordPressパス自動検出モジュール
AI開発加速のための環境検出ツール
"""

import os
import subprocess
from pathlib import Path


class WordPressPathDetector:
    """WordPressインストールパスの自動検出"""

    def __init__(self):
        self.common_paths = [
            "/home",
            "/var/www",
            "/var/www/html",
            "/opt",
            "/usr/share",
            str(Path.cwd()),
            "/home/codespace",
            "/workspace",
        ]

    def detect_wp_path(self):
        """WordPressのルートパスを検出"""
        for base_path in self.common_paths:
            if os.path.exists(base_path):
                try:
                    result = subprocess.run(
                        ["find", base_path, "-name", "wp-load.php", "-type", "f"],
                        capture_output=True,
                        text=True,
                        timeout=30,
                    )
                    if result.returncode == 0 and result.stdout.strip():
                        wp_path = os.path.dirname(result.stdout.strip().split("\n")[0])
                        print(f"✅ WordPress detected: {wp_path}")
                        return wp_path
                except (subprocess.TimeoutExpired, Exception) as e:
                    continue

        # 代替方法: wp-config.phpを検索
        for base_path in self.common_paths:
            if os.path.exists(base_path):
                try:
                    result = subprocess.run(
                        ["find", base_path, "-name", "wp-config.php", "-type", "f"],
                        capture_output=True,
                        text=True,
                        timeout=30,
                    )
                    if result.returncode == 0 and result.stdout.strip():
                        wp_path = os.path.dirname(result.stdout.strip().split("\n")[0])
                        print(f"✅ WordPress detected via wp-config: {wp_path}")
                        return wp_path
                except (subprocess.TimeoutExpired, Exception) as e:
                    continue

        print("❌ WordPress not found in common locations")
        return None


if __name__ == "__main__":
    detector = WordPressPathDetector()
    path = detector.detect_wp_path()
    if path:
        print(f"WP_PATH={path}")
