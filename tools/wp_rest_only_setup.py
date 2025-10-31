#!/usr/bin/env python3
"""
WordPress REST API専用セットアップ
FTP不要！プラグイン手動インストール版
"""

import json
import os


def create_rest_api_config():
    """REST APIのみの設定を作成"""
    print()
    print("=" * 70)
    print("🔧 WordPress REST API設定（FTP不要・最も簡単な方法）")
    print("=" * 70)
    print()

    config = {
        "wp_url": "https://uzbek-ma.com",
        "wp_user": "uzbek",
        "wp_password": "",
        "deploy_method": "rest_api",
        "setup_completed": False,
    }

    print("【このセットアップでやること】")
    print("1. プラグインを手動でWordPressにアップロード（1分）")
    print("2. アプリケーションパスワードを取得（1分）")
    print("3. 設定完了 → 以降は完全自動デプロイ！")
    print()

    input("準備OK？ Enterキーを押して続行...")

    print()
    print("=" * 70)
    print("【STEP 1】プラグインを手動インストール")
    print("=" * 70)
    print()

    # プラグインZIPのパスを確認
    plugin_zip = "deploy_system/auto-deploy-receiver.zip"
    if not os.path.exists(plugin_zip):
        print(f"❌ エラー: {plugin_zip} が見つかりません")
        print("   先に ./wp-setup を実行してください")
        return False

    print(f"✅ プラグインファイル確認: {plugin_zip}")
    print()
    print("以下の手順でインストールしてください：")
    print()
    print("1️⃣ WordPressにログイン")
    print("   👉 https://uzbek-ma.com/wp-admin/")
    print()
    print("2️⃣ プラグイン → 新規追加")
    print()
    print("3️⃣ 「プラグインのアップロード」をクリック")
    print()
    print("4️⃣ 「ファイルを選択」をクリック")
    print()
    print("5️⃣ 以下のファイルを選択:")
    print(f"   📁 {os.path.abspath(plugin_zip)}")
    print()
    print("   💡 ヒント: このパスをコピーしてファイル選択ダイアログに貼り付け")
    print()
    print("6️⃣ 「今すぐインストール」をクリック")
    print()
    print("7️⃣ 「プラグインを有効化」をクリック")
    print()

    input("✅ プラグインを有効化したらEnterキーを押してください...")

    print()
    print("=" * 70)
    print("【STEP 2】アプリケーションパスワード取得")
    print("=" * 70)
    print()
    print("1️⃣ WordPress管理画面で:")
    print("   左メニュー → ユーザー → プロフィール")
    print()
    print("2️⃣ 下にスクロールして「アプリケーションパスワード」セクションを探す")
    print()
    print("3️⃣ 「新しいアプリケーションパスワード名」欄に入力:")
    print("   👉 AutoDeploy")
    print()
    print("4️⃣ 「新しいアプリケーションパスワードを追加」をクリック")
    print()
    print("5️⃣ 表示されたパスワードをコピー")
    print("   ⚠️ スペースは除いてください")
    print("   例: abcd efgh ijkl → abcdefghijkl")
    print()

    app_password = input("📋 アプリケーションパスワードを貼り付け: ").strip().replace(" ", "")

    if not app_password:
        print("❌ パスワードが入力されていません")
        return False

    config["wp_password"] = app_password
    config["setup_completed"] = True

    # 設定を保存
    os.makedirs("deploy_system", exist_ok=True)
    with open("deploy_system/config.json", "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

    print()
    print("=" * 70)
    print("🎉 セットアップ完了！")
    print("=" * 70)
    print()
    print("✅ 設定ファイル保存: deploy_system/config.json")
    print()
    print("🚀 今すぐデプロイを実行:")
    print("   python3 deploy_system/AUTO_DEPLOY_MASTER.py")
    print()
    print("または:")
    print("   ./wp-deploy")
    print()

    # 自動デプロイ実行するか確認
    run_now = input("今すぐデプロイを実行しますか？ (y/n): ").strip().lower()

    if run_now == "y":
        print()
        print("🚀 デプロイ実行中...")
        import subprocess

        subprocess.run(["python3", "deploy_system/AUTO_DEPLOY_MASTER.py"])

    return True


if __name__ == "__main__":
    try:
        create_rest_api_config()
    except KeyboardInterrupt:
        print()
        print("⚠️ セットアップを中断しました")
    except Exception as e:
        print(f"❌ エラー: {str(e)}")
