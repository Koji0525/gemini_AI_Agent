#!/usr/bin/env python3
"""
main_hybrid_fix.py を修正
"""

content = '''#!/usr/bin/env python3
"""
ハイブリッド修正システムのメインエントリーポイント
"""
import sys
import asyncio
from pathlib import Path

# プロジェクトルートをパスに追加
sys.path.insert(0, str(Path(__file__).parent))

from fix_agents.cloud_fix_agent import CloudFixAgent
from fix_agents.local_fix_agent import LocalFixAgent
from fix_agents.hybrid_fix_orchestrator import HybridFixOrchestrator
from configuration.config_hybrid import HybridFixConfig

async def main():
    """メイン実行関数"""
    config = HybridFixConfig()
    
    # エージェントを初期化
    cloud_agent = CloudFixAgent(config)
    local_agent = LocalFixAgent(config)
    
    # オーケストレーターを初期化
    orchestrator = HybridFixOrchestrator(
        config=config,
        cloud_agent=cloud_agent,
        local_agent=local_agent
    )
    
    # 修正プロセスを実行
    result = await orchestrator.run()
    
    return result

if __name__ == "__main__":
    asyncio.run(main())
'''

with open('main_hybrid_fix.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ main_hybrid_fix.py を修正しました")
