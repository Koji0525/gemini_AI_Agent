"""
AI開発加速ツール - 効率的な開発を支援
"""

import subprocess
import sys
from pathlib import Path


class DevelopmentAccelerator:
    """開発プロセスを加速するツール群"""

    @staticmethod
    def run_safe_php_script(php_script_path, backup=True):
        """安全なPHPスクリプト実行"""

        # バックアップ作成
        if backup:
            backup_path = f"{php_script_path}.backup"
            subprocess.run(["cp", php_script_path, backup_path])
            print(f"✅ バックアップ作成: {backup_path}")

        # 構文チェック
        result = subprocess.run(["php", "-l", php_script_path], capture_output=True, text=True)

        if result.returncode != 0:
            print(f"❌ 構文エラー: {result.stderr}")
            return False

        print("✅ 構文チェック合格")

        # 実行
        try:
            print("🚀 PHPスクリプトを実行...")
            subprocess.run(["php", php_script_path], check=True)
            print("✅ スクリプト実行完了")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ 実行エラー: {e}")
            return False

    @staticmethod
    def generate_php_template(template_name, variables=None):
        """安全なPHPテンプレート生成"""

        if variables is None:
            variables = {}

        template = """<?php
/**
 * 自動生成PHPスクリプト
 * 生成日: {generation_date}
 */

{require_statement}

// 設定
{config_section}

// メイン処理
function main() {
    {main_logic}
}

// 実行
if (isset($argv[0]) && basename($argv[0]) == basename(__FILE__)) {
    main();
}
?>
"""
        from datetime import datetime
        from configuration.config_loader import config

        filled_template = template.format(
            generation_date=datetime.now().isoformat(),
            require_statement=f"require_once('{config.wp_load_path}');",
            config_section="\n".join([f"${k} = {repr(v)};" for k, v in variables.items()]),
            main_logic="# ここにメイン処理を実装",
        )

        output_path = f"scripts/generated/{template_name}.php"
        Path(output_path).parent.mkdir(exist_ok=True)

        with open(output_path, "w") as f:
            f.write(filled_template)

        print(f"✅ PHPテンプレート生成: {output_path}")
        return output_path


# 使用例
if __name__ == "__main__":
    accelerator = DevelopmentAccelerator()

    # 現在のスクリプトをテスト実行
    success = accelerator.run_safe_php_script("/tmp/register_companies_dd.php")

    if success:
        print("🎉 開発加速セットアップ完了！")
    else:
        print("❌ 実行に問題があります")
