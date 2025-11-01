#!/usr/bin/env python3
"""
FTPディレクトリ構造の詳細調査
"""

from ftplib import FTP
import json


def find_functions_php_path():
    """functions.phpの正確なパスを発見"""

    print("=" * 70)
    print("🔍 FTPディレクトリ構造を詳細調査")
    print("=" * 70)
    print()

    with open("tools/wp_config.json", "r", encoding="utf-8") as f:
        config = json.load(f)

    try:
        ftp = FTP()
        ftp.connect(config["ftp_host"], 21, timeout=30)
        ftp.login(config["ftp_user"], config["ftp_pass"])

        print("✅ FTP接続成功")
        print()

        # 現在のディレクトリ
        current = ftp.pwd()
        print(f"📁 ログイン直後のディレクトリ: {current}")
        print()

        # ディレクトリ一覧（隠しファイル含む）
        print("📂 ルートディレクトリの内容（詳細）:")
        items = []
        ftp.retrlines("LIST -la", items.append)

        for item in items:
            print(f"   {item}")

        print()

        # 可能性のあるパスを順に試す
        possible_paths = [
            "uzbek-ma.com/public_html/wp-content/themes/cocoon-child-master",
            "/uzbek-ma.com/public_html/wp-content/themes/cocoon-child-master",
            "public_html/wp-content/themes/cocoon-child-master",
            "/public_html/wp-content/themes/cocoon-child-master",
            "../uzbek-ma.com/public_html/wp-content/themes/cocoon-child-master",
            "/home/xs395696/uzbek-ma/uzbek-ma.com/public_html/wp-content/themes/cocoon-child-master",
        ]

        print("🔎 functions.phpを探索中...")
        print()

        found_path = None

        for path in possible_paths:
            try:
                print(f"試行: {path}")
                ftp.cwd("/")  # ルートに戻る
                ftp.cwd(path)

                # functions.phpの存在確認
                files = []
                ftp.retrlines("NLST", files.append)

                if "functions.php" in files:
                    found_path = path
                    print(f"   ✅ 発見！ {path}")
                    print()
                    break
                else:
                    print(f"   ❌ functions.phpなし")

            except Exception as e:
                print(f"   ❌ アクセス不可: {str(e)}")

        if not found_path:
            # ディレクトリを段階的に探索
            print()
            print("�� 段階的探索を開始...")
            print()

            def explore_directory(path, depth=0):
                if depth > 3:
                    return None

                try:
                    ftp.cwd(path)
                    print("  " * depth + f"📁 {path}")

                    items = []
                    ftp.retrlines("LIST", items.append)

                    dirs = []
                    for item in items:
                        parts = item.split()
                        if len(parts) >= 9 and parts[0].startswith("d"):
                            dir_name = " ".join(parts[8:])
                            if dir_name not in [".", ".."]:
                                dirs.append(dir_name)
                                print("  " * (depth + 1) + f"└─ {dir_name}")

                    # wp-content を探す
                    if "wp-content" in dirs:
                        print()
                        print(f"✅ wp-content 発見: {path}/wp-content")

                        ftp.cwd(f"{path}/wp-content/themes")
                        theme_dirs = []
                        ftp.retrlines("NLST", theme_dirs.append)

                        print(f"📂 テーマディレクトリ:")
                        for theme_dir in theme_dirs:
                            print(f"   - {theme_dir}")
                            if "cocoon" in theme_dir.lower():
                                full_path = f"{path}/wp-content/themes/{theme_dir}"
                                print(f"   ✅ Cocoon発見: {full_path}")
                                return full_path

                    # サブディレクトリを探索
                    for dir_name in dirs:
                        if dir_name in ["uzbek-ma.com", "public_html", "httpdocs", "www"]:
                            result = explore_directory(f"{path}/{dir_name}", depth + 1)
                            if result:
                                return result

                except Exception as e:
                    pass

                return None

            # ルートから探索開始
            ftp.cwd("/")
            found_path = explore_directory("/", 0)

        ftp.quit()

        if found_path:
            print()
            print("=" * 70)
            print("🎉 functions.phpのパスを発見！")
            print("=" * 70)
            print()
            print(f"📁 パス: {found_path}")
            print()

            # 設定を更新
            config["ftp_wp_path"] = found_path.replace("/wp-content/themes/cocoon-child-master", "")

            with open("tools/wp_config.json", "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2, ensure_ascii=False)

            print("✅ 設定ファイルを更新しました")
            print()

            return found_path

        else:
            print()
            print("=" * 70)
            print("❌ functions.phpが見つかりませんでした")
            print("=" * 70)
            print()
            return None

    except Exception as e:
        print(f"❌ エラー: {str(e)}")
        return None


if __name__ == "__main__":
    path = find_functions_php_path()

    if path:
        print("=" * 70)
        print("🚀 次のステップ:")
        print("   python3 tools/ftp_emergency_fix.py")
        print("=" * 70)
