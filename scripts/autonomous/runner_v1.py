#!/usr/bin/env python3
"""24時間自律稼働ランナー v1.0"""

import asyncio
import time
from datetime import datetime

class SimpleRunner:
    """シンプルな24時間ランナー"""
    
    def __init__(self):
        self.cycle_count = 0
        self.running = True
    
    async def run_forever(self):
        """無限ループ"""
        print(f"🚀 起動: {datetime.now()}")
        
        while self.running:
            try:
                print(f"サイクル {self.cycle_count}: {datetime.now()}")
                self.cycle_count += 1
                
                # 3分待機
                await asyncio.sleep(180)
                
            except KeyboardInterrupt:
                print("\n停止")
                self.running = False

async def main():
    runner = SimpleRunner()
    await runner.run_forever()

if __name__ == '__main__':
    asyncio.run(main())
