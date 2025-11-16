#!/usr/bin/env python3
"""
AIコード生成器 - バージョン1 (最小限実装)
フェーズ2の核となるコンポーネント
"""
import os
import re
from pathlib import Path


class AICodeGenerator:
    def __init__(self, template_dir=None):
        self.template_dir = template_dir or Path(__file__).parent / "templates"
        self.generated_count = 0

    def detect_code_type(self, description):
        """説明文からコードタイプを検出"""
        patterns = {
            "api": r"(API|REST|エンドポイント|FastAPI|Flask)",
            "data": r"(データ|分析|pandas|CSV|Excel)",
            "web": r"(Web|画面|HTML|Flask|Django)",
            "ml": r"(機械学習|AI|モデル|scikit|tensorflow)",
            "cli": r"(CLI|コマンド|コンソール)",
            "test": r"(テスト|単体テスト|pytest)",
        }

        for code_type, pattern in patterns.items():
            if re.search(pattern, description, re.IGNORECASE):
                return code_type
        return "general"

    def generate_simple_code(self, description, code_type=None):
        """シンプルなコード生成"""
        if not code_type:
            code_type = self.detect_code_type(description)

        base_code = f'''#!/usr/bin/env python3
"""
生成されたコード: {description}
タイプ: {code_type}
"""

def main():
    """メイン関数"""
    print("🚀 生成コード実行開始")
    print(f"目的: {description}")
    # TODO: 実際のロジックを実装
    print("✅ 処理完了")

if __name__ == "__main__":
    main()
'''
        self.generated_count += 1
        return base_code

    def save_generated_code(self, code, task_id, output_dir="agent_outputs/ai_generated"):
        """生成コードを保存"""
        output_path = Path(output_dir) / f"{task_id}_ai.py"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(code)

        return output_path


def main():
    """テスト実行"""
    generator = AICodeGenerator()

    # テストケース
    test_cases = [
        "REST APIのユーザー管理エンドポイントを作成",
        "データ分析のためのパンダスパイプライン",
        "機械学習モデルの訓練スクリプト",
    ]

    for i, description in enumerate(test_cases, 1):
        code_type = generator.detect_code_type(description)
        code = generator.generate_simple_code(description, code_type)
        file_path = generator.save_generated_code(code, f"test_ai_{i}")
        print(f"✅ 生成完了: {file_path} (タイプ: {code_type})")


if __name__ == "__main__":
    main()
