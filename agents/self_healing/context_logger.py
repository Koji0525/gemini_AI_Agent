"""
簡易版ContextLogger
"""


class ContextLogger:
    def __init__(self):
        print("✅ ContextLogger 初期化完了")

    async def log(self, data):
        """データをログに記録"""
        print(f"📝 ログ記録: {type(data).__name__}")
        return True

    async def get_context(self, context_id):
        """コンテキストを取得"""
        return {}
