#!/usr/bin/env python3
"""完了判定の改善"""
from pathlib import Path

file = Path('claude_agent_intelligent.py')
content = file.read_text()

# 完了判定を強化
old_check = '''    def check_completion(self, response: str) -> bool:
        """完了判定"""
        completion_keywords = [
            'タスク完了', 'すべて完了', '作業完了', '実装完了',
            'テスト成功', 'すべて成功', '問題なし', '全て正常'
        ]

        return any(keyword in response for keyword in completion_keywords)'''

new_check = '''    def check_completion(self, response: str) -> bool:
        """完了判定（厳格化）"""
        # 明確な完了表明
        explicit_completion = [
            'タスク完了', 'すべて完了', '作業完了',
            'これで完了です', '以上で完了'
        ]

        # コマンドがない + 成功メッセージ
        has_no_commands = not self.extract_commands(response)
        has_success_msg = any(word in response for word in ['成功', '正常', '問題なし'])

        # 明示的完了 OR (コマンドなし + 全コマンド成功)
        explicit = any(keyword in response for keyword in explicit_completion)
        implicit = has_no_commands and self.failed_commands == 0 and self.total_commands > 0

        return explicit or implicit'''

if old_check in content:
    content = content.replace(old_check, new_check)
    file.write_text(content)
    print("✅ 完了判定を改善しました")
else:
    print("⚠️ 該当箇所が見つかりません")
