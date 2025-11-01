#!/usr/bin/env python3
"""役割マッピング拡張"""

# run_integrated_system.py を読み込み
with open("run_integrated_system.py", "r", encoding="utf-8") as f:
    content = f.read()

# role_handlersを拡張
old_mapping = """        self.role_handlers = {
            'design': self.handle_design_task,
            'dev': self.handle_dev_task,
            'content': self.handle_content_task,
            'review': self.handle_review_task,
            'wp': self.handle_wp_task,
        }"""

new_mapping = """        self.role_handlers = {
            'design': self.handle_design_task,
            'dev': self.handle_dev_task,
            'wp_dev': self.handle_wp_dev_task,      # WordPress開発
            'wp_cpt': self.handle_wp_cpt_task,      # カスタム投稿タイプ
            'content': self.handle_content_task,
            'review': self.handle_review_task,
            'wp': self.handle_wp_task,
        }"""

content = content.replace(old_mapping, new_mapping)

# 新しいハンドラーを追加
new_handlers = """
    async def handle_wp_dev_task(self, task: Dict) -> bool:
        \"\"\"WordPress開発タスク処理\"\"\"
        print("🌐 WordPress Dev Agent で処理中...")
        return await self._execute_with_gemini(task, "WordPress開発")
    
    async def handle_wp_cpt_task(self, task: Dict) -> bool:
        \"\"\"WordPressカスタム投稿タイプタスク処理\"\"\"
        print("📝 WordPress CPT Agent で処理中...")
        return await self._execute_with_gemini(task, "WordPressカスタム投稿タイプ")
"""

# handle_wp_taskの前に挿入
content = content.replace(
    "    async def handle_wp_task(self, task: Dict) -> bool:",
    new_handlers + "\n    async def handle_wp_task(self, task: Dict) -> bool:",
)

# 保存
with open("run_integrated_system.py", "w", encoding="utf-8") as f:
    f.write(content)

print("✅ 役割マッピング拡張完了")
print("\n追加された役割:")
print("  - wp_dev: WordPress開発")
print("  - wp_cpt: カスタム投稿タイプ")
