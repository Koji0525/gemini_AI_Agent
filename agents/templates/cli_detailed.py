"""
詳細CLIアプリケーションテンプレート
"""

import argparse
import sys
from typing import Optional, List


class DetailedCLI:
    """詳細なCLIアプリケーションのテンプレートクラス"""

    def __init__(self):
        self.parser = argparse.ArgumentParser(description="詳細CLIアプリケーション")
        self.setup_arguments()

    def setup_arguments(self):
        """引数の設定"""
        self.parser.add_argument("--config", type=str, help="設定ファイルのパス")
        self.parser.add_argument("--verbose", action="store_true", help="詳細出力")
        self.parser.add_argument("--output", type=str, help="出力ファイルのパス")

    def parse_arguments(self, args: Optional[List[str]] = None) -> argparse.Namespace:
        """引数を解析"""
        return self.parser.parse_args(args)

    def run(self, args: argparse.Namespace) -> int:
        """メイン実行処理"""
        try:
            if args.verbose:
                print("詳細モードで実行中...")

            # ここにメインの処理を実装
            result = self.main_logic(args)

            if args.verbose:
                print("処理が完了しました")

            return result

        except Exception as e:
            print(f"エラーが発生しました: {e}", file=sys.stderr)
            return 1

    def main_logic(self, args: argparse.Namespace) -> int:
        """メインロジック"""
        # メインのビジネスロジックをここに実装
        print("メインロジックを実行中...")

        # サンプル実装
        if args.config:
            print(f"設定ファイル: {args.config}")

        if args.output:
            print(f"出力先: {args.output}")

        return 0


def main():
    """メイン関数"""
    cli = DetailedCLI()
    args = cli.parse_arguments()
    sys.exit(cli.run(args))


if __name__ == "__main__":
    main()
