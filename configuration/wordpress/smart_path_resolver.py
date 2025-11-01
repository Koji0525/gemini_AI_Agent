#!/usr/bin/env python3
"""
スマートなWordPressパス解決 - AI開発加速のための先進的検出
"""

import os
import sys
import subprocess
from pathlib import Path


class SmartWordPressResolver:
    """複数方法でWordPressパスを解決"""

    def __init__(self):
        self.detection_methods = [
            self.detect_via_wp_load,
            self.detect_via_wp_config,
            self.detect_via_directory_structure,
            self.detect_via_composer,
            self.detect_via_environment,
        ]

    def detect_via_wp_load(self):
        """wp-load.phpから検出"""
        try:
            result = subprocess.run(
                ["find", "/workspaces", "/home", "/var", "/opt", ".", "-name", "wp-load.php", "-type", "f"],
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode == 0:
                for path in result.stdout.strip().split("\n"):
                    if path and self.validate_wp_directory(os.path.dirname(path)):
                        return os.path.dirname(path)
        except Exception:
            pass
        return None

    def detect_via_wp_config(self):
        """wp-config.phpから検出"""
        try:
            result = subprocess.run(
                ["find", "/workspaces", "/home", "/var", "/opt", ".", "-name", "wp-config.php", "-type", "f"],
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode == 0:
                for path in result.stdout.strip().split("\n"):
                    if path:
                        config_dir = os.path.dirname(path)
                        # 設定ディレクトリの親をチェック
                        parent_dir = os.path.dirname(config_dir)
                        if self.validate_wp_directory(parent_dir):
                            return parent_dir
                        elif self.validate_wp_directory(config_dir):
                            return config_dir
        except Exception:
            pass
        return None

    def detect_via_directory_structure(self):
        """ディレクトリ構造から検出（修正版）"""
        common_roots = ["/workspaces/gemini_AI_Agent", ".", "/var/www", "/var/www/html"]

        for root in common_roots:
            if os.path.exists(root):
                # os.walkの代わりに再帰的な検索（深さ制限付き）
                for current_dir in self.walk_with_depth(root, max_depth=3):
                    dirnames = []
                    filenames = []
                    try:
                        with os.scandir(current_dir) as entries:
                            for entry in entries:
                                if entry.is_dir():
                                    dirnames.append(entry.name)
                                else:
                                    filenames.append(entry.name)
                    except OSError:
                        continue

                    if "wp-admin" in dirnames and "wp-includes" in dirnames:
                        if any(f.endswith(".php") for f in filenames):
                            return current_dir
        return None

    def walk_with_depth(self, root_path, max_depth=3):
        """深さ制限付きのディレクトリ走査"""
        from collections import deque

        queue = deque([(root_path, 0)])
        while queue:
            current_path, depth = queue.popleft()
            yield current_path

            if depth < max_depth:
                try:
                    with os.scandir(current_path) as entries:
                        for entry in entries:
                            if entry.is_dir() and not entry.name.startswith("."):
                                queue.append((entry.path, depth + 1))
                except OSError:
                    continue

    def detect_via_composer(self):
        """Composerから検出"""
        try:
            # composer.jsonからWordPressのパスを検出
            result = subprocess.run(
                ["find", ".", "-name", "composer.json", "-type", "f"], capture_output=True, text=True
            )
            if result.returncode == 0:
                for composer_path in result.stdout.strip().split("\n"):
                    if composer_path:
                        composer_dir = os.path.dirname(composer_path)
                        # WordPressインストール先をチェック
                        possible_paths = [
                            os.path.join(composer_dir, "web", "wp"),
                            os.path.join(composer_dir, "wordpress"),
                            os.path.join(composer_dir, "wp"),
                        ]
                        for path in possible_paths:
                            if self.validate_wp_directory(path):
                                return path
        except Exception:
            pass
        return None

    def detect_via_environment(self):
        """環境変数から検出"""
        env_path = os.getenv("WP_PATH")
        if env_path and self.validate_wp_directory(env_path):
            return env_path
        return None

    def validate_wp_directory(self, path):
        """WordPressディレクトリの検証"""
        if not path or not os.path.exists(path):
            return False

        required_items = ["wp-load.php", "wp-admin", "wp-includes"]

        # wp-config.phpは同じ階層か1つ上の階層にある可能性
        config_paths = [os.path.join(path, "wp-config.php"), os.path.join(os.path.dirname(path), "wp-config.php")]

        has_config = any(os.path.exists(p) for p in config_paths)

        for item in required_items:
            if not os.path.exists(os.path.join(path, item)):
                return False

        if not has_config:
            print(f"⚠️  wp-config.phpが見つかりません: {path}")
            return False

        return True

    def resolve(self):
        """すべての方法で解決を試みる"""
        print("🔧 スマートWordPressパス解決を開始...")

        for method in self.detection_methods:
            result = method()
            if result:
                print(f"✅ {method.__name__} で検出: {result}")
                return result

        print("❌ すべての検出方法が失敗しました")
        return None


# 使用例
if __name__ == "__main__":
    resolver = SmartWordPressResolver()
    wp_root = resolver.resolve()

    if wp_root:
        print(f"WP_ROOT={wp_root}")
        # 環境変数に設定
        with open(".env", "a") as f:
            f.write(f"\nWP_PATH={wp_root}\n")
        print("✅ .envを更新しました")
    else:
        print("WP_ROOT=NOT_FOUND")
        sys.exit(1)
