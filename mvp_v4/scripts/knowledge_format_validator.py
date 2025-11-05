#!/usr/bin/env python3
"""
ナレッジフォーマット検証＆自動修正ツール
- 複数行形式を1行形式に自動変換
- フォーマットエラーを事前検出
"""
from typing import Dict


class KnowledgeFormatValidator:
    """ナレッジフォーマットの検証と修正"""

    @staticmethod
    def detect_format(text: str) -> str:
        """
        フォーマットを自動検出
        Returns: 'single_line', 'multi_line', 'unknown'
        """
        lines = [l.strip() for l in text.strip().split("\n") if l.strip()]

        # 1行形式の検出
        if any(":" in line and line.split(":", 1)[1].strip() for line in lines):
            return "single_line"

        # 複数行形式の検出
        if any(line.endswith(":") for line in lines):
            return "multi_line"

        return "unknown"

    @staticmethod
    def convert_to_single_line(text: str) -> str:
        """
        複数行形式を1行形式に変換

        変換例:
        何が起きた:          →  何が起きた: 内容が入る
        内容が入る
        """
        lines = text.strip().split("\n")
        result = []
        current_key = None
        current_value = []

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # キー行（コロンで終わる、または「何が起きた:」などのパターン）
            if line.endswith(":") or any(
                key in line for key in ["何が起きた", "原因", "狙い", "成功率", "教訓"]
            ):
                # 前のキーがあれば保存
                if current_key and current_value:
                    result.append(f"{current_key}: {' '.join(current_value)}")

                # 新しいキーを設定
                if ":" in line:
                    parts = line.split(":", 1)
                    current_key = parts[0].strip()
                    # コロンの後に内容がある場合
                    if len(parts) > 1 and parts[1].strip():
                        current_value = [parts[1].strip()]
                    else:
                        current_value = []
                else:
                    current_key = line
                    current_value = []
            else:
                # 値行
                if current_key:
                    # コード例や箇条書きの処理
                    if line.startswith("-") or line.startswith("```"):
                        current_value.append(line)
                    else:
                        current_value.append(line)

        # 最後のキーを保存
        if current_key and current_value:
            result.append(f"{current_key}: {' '.join(current_value)}")

        return "\n".join(result)

    @staticmethod
    def validate_required_fields(text: str) -> Dict[str, bool]:
        """必須フィールドのチェック"""
        required = {"何が起きた": False, "原因": False, "狙い": False}

        for key in required.keys():
            if key in text:
                required[key] = True

        return required

    @staticmethod
    def auto_fix(text: str) -> tuple[str, list[str]]:
        """
        自動修正
        Returns: (修正後テキスト, 修正ログ)
        """
        logs = []

        # フォーマット検出
        format_type = KnowledgeFormatValidator.detect_format(text)
        logs.append(f"📋 検出フォーマット: {format_type}")

        # 複数行形式の場合は変換
        if format_type == "multi_line":
            text = KnowledgeFormatValidator.convert_to_single_line(text)
            logs.append("✅ 1行形式に自動変換")

        # 必須フィールドチェック
        validation = KnowledgeFormatValidator.validate_required_fields(text)
        missing = [k for k, v in validation.items() if not v]
        if missing:
            logs.append(f"⚠️  不足フィールド: {', '.join(missing)}")
        else:
            logs.append("✅ 必須フィールド完備")

        return text, logs


# コマンドラインツールとしても使用可能
if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        # ファイルから読み込み
        with open(sys.argv[1], "r", encoding="utf-8") as f:
            text = f.read()
    else:
        # 標準入力から読み込み
        text = sys.stdin.read()

    validator = KnowledgeFormatValidator()
    fixed_text, logs = validator.auto_fix(text)

    print("=" * 70)
    print("🔍 ナレッジフォーマット検証結果")
    print("=" * 70)
    for log in logs:
        print(log)
    print("\n" + "=" * 70)
    print("📝 修正後のテキスト")
    print("=" * 70)
    print(fixed_text)
