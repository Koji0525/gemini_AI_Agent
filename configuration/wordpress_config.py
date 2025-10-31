"""
WordPress設定管理 - AI開発加速のための統一設定
"""

import os
from pathlib import Path


class WordPressConfig:
    """WordPress設定の一元管理"""

    def __init__(self):
        self.wp_path = os.getenv("WP_PATH")
        self.validate_config()

    def validate_config(self):
        """設定の検証"""
        if not self.wp_path:
            raise ValueError("WP_PATH環境変数が設定されていません")

        if not os.path.exists(os.path.join(self.wp_path, "wp-load.php")):
            raise FileNotFoundError(f"wp-load.phpが見つかりません: {self.wp_path}")

    def get_wp_load_path(self):
        """wp-load.phpの完全パスを取得"""
        return os.path.join(self.wp_path, "wp-load.php")

    def generate_php_require(self):
        """安全なrequire文を生成"""
        return f"require_once('{self.get_wp_load_path()}');"

    @classmethod
    def auto_detect(cls):
        """自動検出で設定を作成"""
        from wordpress.path_detector import WordPressPathDetector

        detector = WordPressPathDetector()
        wp_path = detector.detect_wp_path()

        if wp_path:
            os.environ["WP_PATH"] = wp_path
            return cls()
        else:
            raise RuntimeError("WordPressの自動検出に失敗しました")


# グローバル設定インスタンス
try:
    wp_config = WordPressConfig.auto_detect()
    print(f"✅ WordPress設定完了: {wp_config.wp_path}")
except Exception as e:
    print(f"❌ WordPress設定エラー: {e}")
    wp_config = None
