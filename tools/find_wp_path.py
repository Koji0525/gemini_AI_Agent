#!/usr/bin/env python3
"""
XServer WordPressパス自動検出ツール
"""

from ftplib import FTP
import sys


def find_wordpress_path(host, user, password):
    """WordPressのパスを自動検出"""
    print("🔍 WordPressディレクトリを探しています...")
    print()

    try:
        ftp = FTP()
        ftp.connect(host, 21, timeout=30)
        ftp.login(user, password)

        print("✅ FTP接続成功！")
        print()

        # 現在のディレクトリを確認
        current_dir = ftp.pwd()
        print(f"📁 現在のディレクトリ: {current_dir}")
        print()

        # ディレクトリ一覧を取得
        print("�� 利用可能なディレクトリ:")
        files = []
        ftp.retrlines("LIST", files.append)

        directories = []
        for line in files:
            parts = line.split()
            if len(parts) >= 9 and (parts[0].startswith("d") or parts[0].startswith("l")):
                dir_name = " ".join(parts[8:])
                directories.append(dir_name)
                print(f"   📁 {dir_name}")

        print()

        # 一般的なWordPressパスをチェック
        possible_paths = [
            "/uzbek-ma.com/public_html",
            "/public_html",
            "/www",
            "/httpdocs",
            "/domains/uzbek-ma.com/public_html",
            "/home/uzbek-ma/public_html",
            "/home/uzbek-ma/uzbek-ma.com/public_html",
        ]

        # ドメイン名のディレクトリを確認
        for dir_name in directories:
            if "uzbek" in dir_name.lower() or "ma" in dir_name.lower():
                possible_paths.insert(0, f"/{dir_name}/public_html")
                possible_paths.insert(0, f"/{dir_name}")

        print("🔎 WordPress検出を試行中...")
        print()

        found_paths = []

        for path in possible_paths:
            try:
                # ディレクトリに移動してみる
                ftp.cwd("/")  # ルートに戻る
                ftp.cwd(path)

                # wp-contentディレクトリの存在を確認
                files_in_dir = []
                ftp.retrlines("LIST", files_in_dir.append)

                has_wp_content = False
                for line in files_in_dir:
                    if "wp-content" in line:
                        has_wp_content = True
                        break

                if has_wp_content:
                    found_paths.append(path)
                    print(f"✅ WordPress発見: {path}")

            except Exception as e:
                continue

        ftp.quit()

        print()
        print("=" * 70)

        if found_paths:
            print("🎉 WordPressパスを発見しました！")
            print()
            print("【検出されたパス】")
            for i, path in enumerate(found_paths, 1):
                print(f"{i}. {path}")
            print()

            if len(found_paths) == 1:
                return found_paths[0]
            else:
                print("複数のパスが見つかりました。")
                print("通常は最初のパスが正解です。")
                return found_paths[0]
        else:
            print("❌ WordPressパスが見つかりませんでした")
            print()
            print("📋 手動確認方法:")
            print("1. FileZillaなどのFTPクライアントで接続")
            print("2. wp-content, wp-admin, wp-includes フォルダを探す")
            print("3. そのフォルダがあるディレクトリのパスをメモ")
            print()
            print(f"現在のルートディレクトリ: {current_dir}")
            print("利用可能なディレクトリ:")
            for dir_name in directories:
                print(f"  - {dir_name}")

            return None

    except Exception as e:
        print(f"❌ エラー: {str(e)}")
        return None


if __name__ == "__main__":
    host = "sv10502.xserver.jp"
    user = "uzbek-ma@uzbek-ma.com"
    password = "mo05WkMqd"

    wp_path = find_wordpress_path(host, user, password)

    if wp_path:
        print()
        print("=" * 70)
        print("✅ 使用するパス:")
        print(f"   {wp_path}")
        print("=" * 70)
        print()

        # 設定ファイルを自動更新
        import json
        import os

        config_file = "tools/wp_config.json"
        if os.path.exists(config_file):
            with open(config_file, "r", encoding="utf-8") as f:
                config = json.load(f)

            config["ftp_wp_path"] = wp_path

            with open(config_file, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2, ensure_ascii=False)

            print("✅ 設定ファイルを自動更新しました！")
            print()
            print("📋 次のステップ:")
            print("   ./wp-setup")
            print()

        sys.exit(0)
    else:
        sys.exit(1)
