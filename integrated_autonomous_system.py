#!/usr/bin/env python3
"""
完全統合：自律型エージェントシステム
test_tasks → run_multi_agent → エラー検出 → main_hybrid_fix
"""
import asyncio
import sys
import subprocess
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IntegratedAutonomousSystem:
    """統合自律システム"""
    
    def __init__(self):
        self.max_retries = 3
        self.error_log_path = Path("error_logs")
        self.error_log_path.mkdir(exist_ok=True)
    
    async def run_test_tasks(self):
        """test_tasks.py を実行"""
        logger.info("📝 test_tasks.py 実行中...")
        result = subprocess.run(
            ['python', 'test_tasks.py'],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            # エラーログを保存
            error_file = self.error_log_path / "test_tasks_error.log"
            error_file.write_text(result.stderr)
            return False, error_file
        
        return True, None
    
    async def run_multi_agent(self):
        """run_multi_agent.py を実行"""
        logger.info("🤖 run_multi_agent.py 実行中...")
        result = subprocess.run(
            ['python', 'run_multi_agent.py'],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            error_file = self.error_log_path / "multi_agent_error.log"
            error_file.write_text(result.stderr)
            return False, error_file
        
        return True, None
    
    async def call_hybrid_fix(self, error_file):
        """main_hybrid_fix.py を呼び出し"""
        logger.info(f"🔧 main_hybrid_fix.py 呼び出し: {error_file}")
        
        result = subprocess.run(
            ['python', 'main_hybrid_fix.py', '--error-log', str(error_file)],
            capture_output=True,
            text=True
        )
        
        logger.info("✅ 修正完了")
        return result.returncode == 0
    
    async def run_cycle(self):
        """完全サイクル実行"""
        print("\n" + "="*80)
        print("🤖 統合自律型エージェントシステム")
        print("="*80)
        
        for attempt in range(1, self.max_retries + 1):
            print(f"\n🔄 試行 {attempt}/{self.max_retries}")
            
            # ステップ1: test_tasks
            success, error_file = await self.run_test_tasks()
            if not success:
                logger.error("❌ test_tasks.py 失敗")
                if error_file:
                    await self.call_hybrid_fix(error_file)
                continue
            
            logger.info("✅ test_tasks.py 成功")
            
            # ステップ2: run_multi_agent
            success, error_file = await self.run_multi_agent()
            if not success:
                logger.error("❌ run_multi_agent.py 失敗")
                if error_file:
                    await self.call_hybrid_fix(error_file)
                continue
            
            logger.info("✅ run_multi_agent.py 成功")
            
            # 両方成功
            print("\n" + "="*80)
            print("🎉 全サイクル成功！")
            print("="*80)
            return True
        
        print("\n" + "="*80)
        print(f"⚠️ {self.max_retries}回試行しましたが失敗しました")
        print("="*80)
        return False

async def main():
    system = IntegratedAutonomousSystem()
    success = await system.run_cycle()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
