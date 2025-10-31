#!/usr/bin/env python3
"""
安全なPHPコード生成ツール
構文チェックと環境検出を組み合わせ
"""

import subprocess
import tempfile
import os


class PHPCodeGenerator:
    """AI開発加速のための安全なPHPコード生成"""

    def __init__(self):
        self.detector = WordPressPathDetector() if "WordPressPathDetector" in globals() else None

    def generate_require_statement(self):
        """環境検出付きrequire文を生成"""
        if self.detector:
            wp_path = self.detector.detect_wp_path()
            if wp_path:
                return f"require_once('{wp_path}/wp-load.php');"

        # フォールバック: 相対パスまたは環境変数
        return "<?php\n// WordPressパス自動検出\n$wp_path = getenv('WP_PATH') ?: dirname(__FILE__);\nif (file_exists($wp_path . '/wp-load.php')) {\n    require_once($wp_path . '/wp-load.php');\n} else {\n    die('WordPress not found');\n}\n?>"

    def validate_php_syntax(self, php_code):
        """PHP構文チェック"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".php", delete=False) as f:
            f.write(php_code)
            temp_file = f.name

        try:
            result = subprocess.run(["php", "-l", temp_file], capture_output=True, text=True)
            os.unlink(temp_file)
            return result.returncode == 0, result.stdout
        except Exception as e:
            return False, str(e)


# 使用例
if __name__ == "__main__":
    generator = PHPCodeGenerator()
    require_code = generator.generate_require_statement()
    print("生成されたrequire文:")
    print(require_code)
