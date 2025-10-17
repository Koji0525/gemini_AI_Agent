#!/usr/bin/env python3
"""
TaskExecutorにDesignAgent/DevAgentの自動初期化を追加
ReviewAgentと同じ方式で初期化
"""

from pathlib import Path

def add_core_agents():
    print("🔧 TaskExecutorにコアエージェント初期化を追加")
    print("=" * 70)
    
    file_path = Path("scripts/task_executor.py")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # バックアップ
    backup_path = Path("scripts/task_executor.py.backup_add_agents")
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print(f"✅ バックアップ: {backup_path}")
    
    # ReviewAgent初期化の場所を探す（169-184行目付近）
    review_agent_start = None
    for i, line in enumerate(lines):
        if 'self.review_agent_instance = None' in line:
            review_agent_start = i
            break
    
    if review_agent_start is None:
        print("❌ ReviewAgent初期化コードが見つかりません")
        return False
    
    # 挿入するコード（ReviewAgentの直前に追加）
    new_code = '''
        # DesignAgent の初期化
        self.design_agent = None
        try:
            from core_agents.design_agent import DesignAgent
            if self.browser:
                self.design_agent = DesignAgent(
                    browser_controller=self.browser,
                    output_folder=Path("agent_outputs/design")
                )
                self.agents['design'] = self.design_agent
                logger.info("✅ DesignAgent 初期化完了")
            else:
                logger.warning("⚠️ ブラウザ未設定のためDesignAgentを初期化できません")
        except Exception as e:
            logger.warning(f"⚠️ DesignAgent 初期化失敗: {e}")
            self.design_agent = None

        # DevAgent の初期化
        self.dev_agent = None
        try:
            from core_agents.dev_agent import DevAgent
            if self.browser:
                self.dev_agent = DevAgent(
                    browser_controller=self.browser,
                    output_folder=Path("agent_outputs/dev")
                )
                self.agents['dev'] = self.dev_agent
                logger.info("✅ DevAgent 初期化完了")
            else:
                logger.warning("⚠️ ブラウザ未設定のためDevAgentを初期化できません")
        except Exception as e:
            logger.warning(f"⚠️ DevAgent 初期化失敗: {e}")
            self.dev_agent = None

'''
    
    # 挿入
    lines.insert(review_agent_start, new_code)
    
    # 保存
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print("✅ DesignAgent/DevAgentの初期化コードを追加しました")
    print()
    print("追加位置: ReviewAgent初期化の直前")
    print("  - DesignAgent: browser_controller付きで初期化")
    print("  - DevAgent: browser_controller付きで初期化")
    print()
    print("=" * 70)
    
    return True

if __name__ == "__main__":
    success = add_core_agents()
    if success:
        print("\n✅ 修正完了！")
        print("\n次のコマンドで確認:")
        print("  python3 -m py_compile scripts/task_executor.py")
        print("\nテスト実行:")
        print("  DISPLAY=:1 python3 test_task_executor_integration.py")
    else:
        print("\n❌ 修正失敗")
