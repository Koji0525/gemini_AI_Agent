#!/usr/bin/env python3
"""
ConfigLoader修正スクリプト
get()メソッドを追加
"""
import sys
import os

sys.path.insert(0, ".")


def check_and_fix_config_loader():
    """ConfigLoaderを確認して修正"""

    config_file = "configuration/config_loader.py"

    print("=" * 60)
    print("🔧 ConfigLoader修正")
    print("=" * 60)
    print()

    # 現在のファイルを読み込み
    if not os.path.exists(config_file):
        print(f"❌ {config_file} が見つかりません")
        return False

    with open(config_file, "r", encoding="utf-8") as f:
        content = f.read()

    # get()メソッドが存在するか確認
    if "def get(self" in content:
        print("✅ get()メソッドは既に存在します")
        return True

    print("⚠️  get()メソッドが見つかりません")
    print("💡 get()メソッドを追加します...")

    # get()メソッドを追加
    get_method = '''
    def get(self, key, default=None):
        """設定値を取得（辞書風アクセス）"""
        return getattr(self, key, default)
'''

    # クラス定義の最後に追加
    # 簡易的な追加（クラスの__init__の後に挿入）
    if "class ConfigLoader" in content:
        # ファイルの最後に追加
        modified_content = content + "\n" + get_method

        # バックアップ作成
        backup_file = config_file + ".backup"
        with open(backup_file, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"📝 バックアップ作成: {backup_file}")

        # 修正版を保存
        with open(config_file, "w", encoding="utf-8") as f:
            f.write(modified_content)

        print("✅ get()メソッドを追加しました")
        print()
        print("🔍 確認:")

        # 動作確認
        try:
            from configuration.config_loader import ConfigLoader

            config = ConfigLoader()
            test_value = config.get("WP_URL")
            print(f"   ✅ config.get('WP_URL'): {test_value}")
            return True
        except Exception as e:
            print(f"   ❌ エラー: {e}")
            return False

    return False


if __name__ == "__main__":
    success = check_and_fix_config_loader()

    if success:
        print("\n🎉 ConfigLoader修正完了")
    else:
        print("\n❌ 修正失敗")
