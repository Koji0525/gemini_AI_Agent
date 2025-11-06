#!/usr/bin/env python3
"""
🧪 Orchestrator 5分間テスト
目的: 3つのループが正常に動作するか確認
"""

import asyncio
import sys
sys.path.insert(0, '/workspaces/gemini_AI_Agent')

from autonomous_development_orchestrator import AutonomousDevelopmentOrchestrator

async def main():
    print("=" * 60)
    print("🧪 24時間稼働システム テスト（5分間）")
    print("=" * 60)
    
    orchestrator = AutonomousDevelopmentOrchestrator()
    
    # 5分間だけ実行
    try:
        await asyncio.wait_for(orchestrator.run_forever(), timeout=300)
    except asyncio.TimeoutError:
        print("\n⏱️  5分経過 - テスト終了")
        orchestrator.running = False
        await orchestrator._shutdown()

if __name__ == '__main__':
    asyncio.run(main())
