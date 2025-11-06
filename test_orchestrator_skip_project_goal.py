#!/usr/bin/env python3
"""
🧪 Orchestrator 5分間テスト（project_goal スキップ版）
目的: project_goalエラーを回避して他の機能をテスト
"""

import asyncio
import sys
sys.path.insert(0, '/workspaces/gemini_AI_Agent')

from autonomous_development_orchestrator import AutonomousDevelopmentOrchestrator

async def main():
    print("=" * 60)
    print("🧪 24時間稼働システム テスト（5分間）")
    print("   ⚠️  project_goal は手動修正が必要")
    print("=" * 60)
    
    try:
        orchestrator = AutonomousDevelopmentOrchestrator()
        
        # 5分間だけ実行
        await asyncio.wait_for(orchestrator.run_forever(), timeout=300)
    except asyncio.TimeoutError:
        print("\n⏱️  5分経過 - テスト終了")
        orchestrator.running = False
        await orchestrator._shutdown()
    except Exception as e:
        print(f"\n❌ エラー: {e}")
        print("\n📝 対処方法:")
        print("  1. manual_header_cleanup_guide.txt を確認")
        print("  2. project_goal のヘッダーをクリーンアップ")
        print("  3. 再度テスト実行")

if __name__ == '__main__':
    asyncio.run(main())
