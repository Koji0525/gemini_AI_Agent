#!/usr/bin/env python3
"""
WordPress Plugin Manager - 完全自動デプロイ対応版
"""

import os
import sys
import json
import base64
import requests
import zipfile
from pathlib import Path
from datetime import datetime
from ftplib import FTP
import io


class WordPressPluginManager:
    """WordPress プラグインマネージャー"""

    def __init__(self):
        self.config_file = "tools/wp_config.json"
        self.config = self.load_config()

    def load_config(self):
        """設定を読み込み"""
        if os.path.exists(self.config_file):
            with open(self.config_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def save_config(self, config):
        """設定を保存"""
        os.makedirs("tools", exist_ok=True)
        with open(self.config_file, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

    def setup_initial_config(self):
        """初期設定"""
        print("=" * 70)
        print("🔧 WordPress接続設定（初回のみ）")
        print("=" * 70)
        print()

        config = {}

        print("【基本情報】")
        config["wp_url"] = input("WordPressのURL（例: https://example.com）: ").strip()
        config["wp_admin_user"] = input("管理者ユーザー名: ").strip()

        print()
        print("【FTP情報】")
        config["ftp_host"] = input("FTPホスト: ").strip()
        config["ftp_user"] = input("FTPユーザー名: ").strip()
        config["ftp_pass"] = input("FTPパスワード: ").strip()
        config["ftp_wp_path"] = input("WordPressパス（例: /public_html）: ").strip()

        self.save_config(config)
        print()
        print("✅ 設定保存完了！")
        print()

        return config

    def create_plugin_zip(self):
        """プラグインをZIPファイルに圧縮"""
        print("📦 プラグインファイルをZIP圧縮中...")

        plugin_dir = "deploy_system/wp_auto_deploy_plugin"
        zip_path = "deploy_system/auto-deploy-receiver.zip"

        if not os.path.exists(plugin_dir):
            print(f"❌ エラー: プラグインディレクトリが見つかりません: {plugin_dir}")
            return None

        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(plugin_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.join("auto-deploy-receiver", os.path.relpath(file_path, plugin_dir))
                    zipf.write(file_path, arcname)

        print(f"✅ ZIP作成完了: {zip_path}")
        return zip_path

    def upload_plugin_via_ftp(self, zip_path):
        """FTP経由でプラグインをアップロード"""
        print("📤 FTP経由でアップロード中...")

        try:
            ftp = FTP()
            ftp.connect(self.config["ftp_host"], 21, timeout=30)
            ftp.login(self.config["ftp_user"], self.config["ftp_pass"])

            plugins_path = f"{self.config['ftp_wp_path']}/wp-content/plugins"

            try:
                ftp.cwd(plugins_path)
            except:
                print(f"❌ エラー: {plugins_path} に移動できません")
                ftp.quit()
                return False

            try:
                ftp.mkd("auto-deploy-receiver")
            except:
                pass

            ftp.cwd("auto-deploy-receiver")

            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                for file_info in zip_ref.filelist:
                    if file_info.is_dir():
                        continue

                    filename = file_info.filename.replace("auto-deploy-receiver/", "")
                    file_content = zip_ref.read(file_info.filename)
                    ftp.storbinary(f"STOR {filename}", io.BytesIO(file_content))
                    print(f"   ✓ {filename}")

            ftp.quit()
            print("✅ アップロード完了！")
            return True

        except Exception as e:
            print(f"❌ FTPエラー: {str(e)}")
            return False

    def guide_app_password_creation(self):
        """アプリケーションパスワード作成ガイド"""
        print()
        print("=" * 70)
        print("🔑 アプリケーションパスワード取得ガイド")
        print("=" * 70)
        print()
        print("【手順】")
        print(f"1. {self.config['wp_url']}/wp-admin/ にログイン")
        print("2. 左メニュー → ユーザー → プロフィール")
        print("3. 下にスクロール → 「アプリケーションパスワード」セクション")
        print("4. 「新しいアプリケーションパスワード名」に「AutoDeploy」と入力")
        print("5. 「新しいアプリケーションパスワードを追加」をクリック")
        print("6. 表示されたパスワードをコピー（スペースは除く）")
        print()
        print("例: abcd efgh ijkl mnop → abcdefghijklmnop")
        print()

        app_password = input("取得したアプリケーションパスワードを貼り付け: ").strip()
        app_password = app_password.replace(" ", "")

        return app_password

    def activate_plugin_manual_guide(self):
        """プラグイン手動有効化ガイド"""
        print()
        print("=" * 70)
        print("🔌 プラグイン有効化")
        print("=" * 70)
        print()
        print("【手順】")
        print(f"1. {self.config['wp_url']}/wp-admin/plugins.php にアクセス")
        print("2. 「Auto Deploy Receiver」を探す")
        print("3. 「有効化」をクリック")
        print()
        input("有効化したらEnterキーを押してください...")
        print()

    def setup_auto_deploy_config(self, app_password):
        """自動デプロイシステムの設定ファイルを作成"""
        print("⚙️ 自動デプロイ設定を作成中...")

        deploy_config = {
            "wp_url": self.config["wp_url"],
            "wp_user": self.config["wp_admin_user"],
            "wp_password": app_password,
            "deploy_method": "rest_api",
            "ftp_host": self.config.get("ftp_host", ""),
            "ftp_user": self.config.get("ftp_user", ""),
            "ftp_pass": self.config.get("ftp_pass", ""),
            "ftp_path": self.config.get("ftp_wp_path", ""),
            "setup_completed": True,
            "setup_date": datetime.now().isoformat(),
        }

        os.makedirs("deploy_system", exist_ok=True)
        with open("deploy_system/config.json", "w", encoding="utf-8") as f:
            json.dump(deploy_config, f, indent=2, ensure_ascii=False)

        print("✅ 自動デプロイ設定完了！")
        return True

    def run_auto_deploy(self):
        """自動デプロイを実行"""
        print()
        print("=" * 70)
        print("🚀 自動デプロイ実行")
        print("=" * 70)
        print()

        import subprocess

        if not os.path.exists("deploy_system/AUTO_DEPLOY_MASTER.py"):
            print("❌ エラー: AUTO_DEPLOY_MASTER.py が見つかりません")
            return False

        try:
            result = subprocess.run(
                ["python3", "deploy_system/AUTO_DEPLOY_MASTER.py"], capture_output=True, text=True, timeout=300
            )

            print(result.stdout)

            if result.returncode == 0:
                print("✅ 自動デプロイ成功！")
                return True
            else:
                print(f"❌ 自動デプロイ失敗: {result.stderr}")
                return False

        except Exception as e:
            print(f"❌ エラー: {str(e)}")
            return False

    def full_setup_and_deploy(self):
        """完全自動セットアップ＆デプロイ"""
        print()
        print("=" * 70)
        print("🎯 WordPress完全自動セットアップ開始")
        print("=" * 70)
        print()

        if not self.config:
            self.config = self.setup_initial_config()

        print("【STEP 1】プラグインのZIP作成")
        zip_path = self.create_plugin_zip()
        if not zip_path:
            return False
        print()

        print("【STEP 2】プラグインをWordPressにアップロード")
        if not self.upload_plugin_via_ftp(zip_path):
            return False
        print()

        print("【STEP 3】プラグインを有効化")
        self.activate_plugin_manual_guide()

        print("【STEP 4】アプリケーションパスワード取得")
        app_password = self.guide_app_password_creation()
        print()

        print("【STEP 5】自動デプロイ設定")
        self.setup_auto_deploy_config(app_password)
        print()

        print("【STEP 6】自動デプロイ実行")
        self.run_auto_deploy()
        print()

        print("=" * 70)
        print("🎉 完全自動セットアップ完了！")
        print("=" * 70)
        print()

        return True

    def deploy_only(self):
        """デプロイのみ実行"""
        if not os.path.exists("deploy_system/config.json"):
            print("❌ エラー: 初期設定が必要です")
            print("   python3 tools/wp_plugin_manager.py --setup")
            return False

        return self.run_auto_deploy()


def main():
    import argparse

    parser = argparse.ArgumentParser(description="WordPress Plugin Manager")
    parser.add_argument("--setup", action="store_true", help="初期セットアップ実行")
    parser.add_argument("--deploy", action="store_true", help="デプロイのみ実行")

    args = parser.parse_args()

    manager = WordPressPluginManager()

    if args.deploy:
        manager.deploy_only()
    elif args.setup:
        manager.full_setup_and_deploy()
    else:
        manager.full_setup_and_deploy()


if __name__ == "__main__":
    main()
