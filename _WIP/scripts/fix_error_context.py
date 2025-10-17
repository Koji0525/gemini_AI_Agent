#!/usr/bin/env python3
"""ErrorContextModel の必須フィールドを追加"""
import uuid
from pathlib import Path

file_path = Path('main_hybrid_fix.py')
content = file_path.read_text()

# 古いErrorContextModel作成部分を探して置換
old_code = '''        error_context = ErrorContextModel(
            error_type="ModuleNotFoundError",
            error_message=args.error or "モジュールインポートエラー",
            file_path=args.file,
            line_number=0,
            code_snippet=""
        )'''

new_code = '''        error_context = ErrorContextModel(
            error_id=str(uuid.uuid4()),
            task_id=str(uuid.uuid4()),
            error_type="ModuleNotFoundError",
            error_message=args.error or "モジュールインポートエラー",
            file_path=args.file,
            line_number=0,
            code_snippet="",
            full_traceback=args.error or "トレースバック情報なし"
        )'''

if old_code in content:
    content = content.replace(old_code, new_code)
    file_path.write_text(content)
    print("✅ main_hybrid_fix.py を修正しました")
else:
    print("⚠️ 該当箇所が見つかりません。手動確認が必要です")
    print("\n修正が必要な箇所:")
    print(new_code)
