# 最小限の修正のみ
with open('autonomous_development_orchestrator.py', 'r') as f:
    content = f.read()

# 1行だけ修正
content = content.replace(
    "self.components['pm_agent'] = PMAgent()",
    "self.components['pm_agent'] = PMAgent(sheets_manager=self.components['sheets_manager'], browser_controller=None)"
)

with open('autonomous_development_orchestrator.py', 'w') as f:
    f.write(content)

print("✅ 1行修正完了")
