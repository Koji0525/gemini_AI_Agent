#!/usr/bin/env python3
"""
XServer専用 WordPress詳細検出ツール
"""

from ftplib import FTP
import json


def detailed_ftp_check(host, user, password):
    """詳細なFTPディレクトリ検査"""
    print("🔍 XServer WordPressディレクトリ詳細検査")
    print("=" * 70)
    print()

    try:
        ftp = FTP()
        ftp.connect(host, 21, timeout=30)
        ftp.login(user, password)

        print("✅ FTP接続成功")
        print()

        # ルートディレクトリを確認
        root = ftp.pwd()
        print(f"📁 ログイン直後のディレクトリ: {root}")
        print()

        # 詳細なファイルリストを取得
        print("📂 ルートディレクトリの内容（詳細）:")
        all_items = []

        def parse_line(line):
            all_items.append(line)
            print(f"   {line}")

        ftp.retrlines("LIST -a", parse_line)
        print()

        # WordPressファイルを探す
        wp_indicators = ["wp-content", "wp-admin", "wp-includes", "wp-config.php", "index.php", "wp-load.php"]

        found_wp_files = []

        for item in all_items:
            item_lower = item.lower()
            for indicator in wp_indicators:
                if indicator in item_lower:
                    found_wp_files.append(indicator)

        print("🔎 WordPress関連ファイル検出結果:")
        if found_wp_files:
            print("✅ WordPressファイルが見つかりました！")
            for file in found_wp_files:
                print(f"   ✓ {file}")
            print()
            print("=" * 70)
            print("✅ WordPressパスの結論:")
            print(f"   パス: {root if root != '/' else ''}")
            print("   （空の場合はルートディレクトリ = WordPressディレクトリ）")
            print("=" * 70)

            # 設定ファイルを更新
            config_path = "tools/wp_config.json"
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)

            # ルートが / の場合は空文字列に設定
            config["ftp_wp_path"] = root if root != "/" else ""

            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2, ensure_ascii=False)

            print()
            print("✅ 設定ファイルを自動更新しました！")

            # wp-contentディレクトリへのアクセステスト
            print()
            print("📝 wp-contentへのアクセステスト...")

            try:
                ftp.cwd("wp-content")
                print("✅ wp-contentにアクセス成功")

                # pluginsディレクトリの確認
                try:
                    ftp.cwd("plugins")
                    print("✅ pluginsディレクトリにアクセス成功")
                    print()
                    print("🎉 完璧！すべて正常です")

                    ftp.quit()
                    return True

                except Exception as e:
                    print(f"❌ pluginsディレクトリエラー: {str(e)}")
                    ftp.quit()
                    return False

            except Exception as e:
                print(f"❌ wp-contentアクセスエラー: {str(e)}")
                ftp.quit()
                return False

        else:
            print("❌ WordPressファイルが見つかりません")
            print()
            print("📋 可能性のある原因:")
            print("1. FTPユーザーが間違っている")
            print("2. WordPressが別の場所にインストールされている")
            print("3. サブディレクトリにWordPressがある")
            print()

            # サブディレクトリを探す
            print("🔍 サブディレクトリを探索中...")
            directories = []

            for item in all_items:
                parts = item.split()
                if len(parts) >= 9 and parts[0].startswith("d"):
                    dir_name = " ".join(parts[8:])
                    if dir_name not in [".", ".."]:
                        directories.append(dir_name)

            if directories:
                print(f"📁 見つかったサブディレクトリ: {len(directories)}個")

                for dir_name in directories:
                    print(f"   🔍 {dir_name} を調査中...")
                    try:
                        ftp.cwd(f"/{dir_name}")
                        sub_items = []
                        ftp.retrlines("LIST -a", sub_items.append)

                        # WordPressファイルをチェック
                        has_wp = False
                        for sub_item in sub_items:
                            if "wp-content" in sub_item.lower():
                                has_wp = True
                                break

                        if has_wp:
                            print(f"   ✅ {dir_name} にWordPress発見！")
                            wp_path = f"/{dir_name}"

                            # 設定更新
                            config_path = "tools/wp_config.json"
                            with open(config_path, "r", encoding="utf-8") as f:
                                config = json.load(f)

                            config["ftp_wp_path"] = wp_path

                            with open(config_path, "w", encoding="utf-8") as f:
                                json.dump(config, f, indent=2, ensure_ascii=False)

                            print()
                            print("=" * 70)
                            print(f"✅ WordPressパス: {wp_path}")
                            print("✅ 設定ファイルを更新しました")
                            print("=" * 70)

                            ftp.quit()
                            return True

                        ftp.cwd("/")  # ルートに戻る

                    except Exception as e:
                        continue

            ftp.quit()
            return False

    except Exception as e:
        print(f"❌ FTPエラー: {str(e)}")
        return False


if __name__ == "__main__":
    host = "sv10502.xserver.jp"
    user = "uzbek-ma@uzbek-ma.com"
    password = "mo05WkMqd"

    success = detailed_ftp_check(host, user, password)

    if success:
        print()
        print("=" * 70)
        print("🎉 検出完了！次のステップ:")
        print("   ./wp-setup")
        print("=" * 70)
    else:
        print()
        print("=" * 70)
        print("❌ 自動検出に失敗しました")
        print()
        print("📋 手動確認が必要です:")
        print("1. https://www.xserver.ne.jp/login/file/ftp/ にアクセス")
        print("2. ログイン")
        print("3. wp-content フォルダを探す")
        print("4. そのパスをメモ")
        print("=" * 70)
