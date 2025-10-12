#!/usr/bin/env python3
"""
ハイブリッド修正システムのメインエントリーポイント
"""

from fix_agents.hybrid_fix_orchestrator import HybridFixOrchestrator
from configuration.config_hybrid import HybridFixConfig

def main():
    """メイン実行関数"""
    config = HybridFixConfig()
    orchestrator = HybridFixOrchestrator(config)
    
    # 修正プロセスを実行
    result = orchestrator.run()
    
    return result

if __name__ == "__main__":
    main()
