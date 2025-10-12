#!/usr/bin/env python3
"""
ハイブリッド修正システムのメインエントリーポイント
"""
import sys
import asyncio
from pathlib import Path
import uuid

# プロジェクトルートをパスに追加
sys.path.insert(0, str(Path(__file__).parent))

from fix_agents.cloud_fix_agent import CloudFixAgent
from fix_agents.local_fix_agent import LocalFixAgent
from fix_agents.hybrid_fix_orchestrator import HybridFixOrchestrator
from configuration.config_hybrid import HybridFixConfig
from data_models.data_models import BugFixTask, ErrorContextModel

async def main():
    """メイン実行関数"""
    # コマンドライン引数から修正対象を取得
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', type=str, help='修正対象ファイル')
    parser.add_argument('--error', type=str, default='', help='エラーメッセージ')
    parser.add_argument('--strategy', type=str, default='CLOUD_ONLY', help='修正戦略')
    args = parser.parse_args()
    
    config = HybridFixConfig()
    
    # エージェントを初期化
    cloud_agent = CloudFixAgent(config)
    local_agent = LocalFixAgent(config)
    
    # オーケストレーターを初期化
    orchestrator = HybridFixOrchestrator(
        local_agent=local_agent,
        cloud_agent=cloud_agent
    )
    
    # 修正タスクを作成
    if args.file:
        # エラーコンテキストを作成
        error_context = ErrorContextModel(
            error_type="ModuleNotFoundError",
            error_message=args.error or "モジュールインポートエラー",
            file_path=args.file,
            line_number=0,
            code_snippet=""
        )
        
        task = BugFixTask(
            task_id=str(uuid.uuid4()),
            original_task_id=str(uuid.uuid4()),
            file_path=args.file,
            error_message=args.error or "エラーが発生しました",
            error_type="ModuleNotFoundError",
            error_context=error_context,
            priority="high"
        )
        
        # 修正を実行
        result = await orchestrator.execute_fix_task(task)
        
        if result.success:
            print(f"✅ 修正成功: {args.file}")
        else:
            print(f"❌ 修正失敗: {args.file}")
            if hasattr(result, 'error_message'):
                print(f"エラー: {result.error_message}")
        
        return result
    else:
        print("⚠️  --file オプションで修正対象ファイルを指定してください")
        return None

if __name__ == "__main__":
    asyncio.run(main())
