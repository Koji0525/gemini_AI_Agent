#!/bin/bash
set -e

echo "=========================================="
echo "🎯 TaskExecutor 完全実装"
echo "=========================================="

mkdir -p scripts

cat > scripts/task_executor.py << 'EXECUTOR_CODE'
#!/usr/bin/env python3
"""
TaskExecutor - タスク実行のオーケストレーター

Google Sheets → Gemini → 結果保存 → Sheets更新
の全フローを管理
"""
import asyncio
import sys
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

# パス設定
sys.path.insert(0, str(Path(__file__).parent.parent))

from browser_control.browser_controller import BrowserController
from browser_control.rate_limiter import RateLimiter
from browser_control.error_recovery import ErrorRecovery
from tools.sheets_manager import GoogleSheetsManager


class TaskExecutor:
    """
    タスク実行を統括するクラス
    """
    
    def __init__(
        self,
        sheets_manager: GoogleSheetsManager,
        output_dir: str = "agent_outputs"
    ):
        self.sheets_manager = sheets_manager
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # レート制限
        self.rate_limiter = RateLimiter(
            max_requests_per_hour=50,
            min_interval_seconds=30
        )
        
        # エラーリカバリー
        self.error_recovery = ErrorRecovery(max_retries=3)
    
    async def execute_all_pending_tasks(self) -> Dict:
        """
        未実行のタスクをすべて実行
        
        Returns:
            実行結果のサマリー
        """
        print("\n" + "="*70)
        print("🚀 タスク一括実行開始")
        print("="*70)
        
        # タスク取得
        print("\n📊 タスク取得中...")
        all_tasks = self.sheets_manager.get_tasks()
        
        # 未実行タスクを抽出
        pending_tasks = [
            task for task in all_tasks
            if task.get('status', '').lower() in ['pending', '']
        ]
        
        print(f"   全タスク: {len(all_tasks)}")
        print(f"   未実行: {len(pending_tasks)}")
        
        if not pending_tasks:
            print("\n✅ 実行すべきタスクはありません")
            return {"total": 0, "success": 0, "failed": 0}
        
        # 実行
        results = {
            "total": len(pending_tasks),
            "success": 0,
            "failed": 0,
            "details": []
        }
        
        async with BrowserController(download_folder="./downloads") as browser:
            print("\n✅ ブラウザ初期化完了")
            
            # Geminiにアクセス
            logged_in = await browser.navigate_to_gemini()
            if not logged_in:
                print("❌ Geminiへのアクセスに失敗しました")
                return results
            
            print("✅ Gemini準備完了")
            
            # 各タスクを実行
            for i, task in enumerate(pending_tasks, 1):
                print("\n" + "-"*70)
                print(f"�� タスク {i}/{len(pending_tasks)}")
                print("-"*70)
                
                # レート制限チェック
                await self.rate_limiter.wait_if_needed()
                
                # タスク実行
                success = await self.execute_single_task(browser, task)
                
                if success:
                    results["success"] += 1
                else:
                    results["failed"] += 1
                
                results["details"].append({
                    "task_id": task.get('id'),
                    "success": success
                })
                
                # 統計表示
                stats = self.rate_limiter.get_stats()
                print(f"\n📊 進捗: {i}/{len(pending_tasks)} "
                      f"(成功: {results['success']}, 失敗: {results['failed']})")
                print(f"   残り実行可能回数: {stats['remaining']}/{stats['max_per_hour']}")
        
        # 最終結果
        print("\n" + "="*70)
        print("📊 実行結果サマリー")
        print("="*70)
        print(f"実行タスク数: {results['total']}")
        print(f"✅ 成功: {results['success']}")
        print(f"❌ 失敗: {results['failed']}")
        print(f"成功率: {results['success']/results['total']*100:.1f}%")
        print("="*70)
        
        return results
    
    async def execute_single_task(
        self,
        browser: BrowserController,
        task: Dict
    ) -> bool:
        """
        単一タスクを実行
        
        Args:
            browser: BrowserController インスタンス
            task: タスク情報
            
        Returns:
            bool: 成功したかどうか
        """
        task_id = task.get('id', 'unknown')
        title = task.get('title', 'No Title')
        prompt = task.get('prompt', '')
        
        print(f"\n🎯 タスク: {title}")
        print(f"   ID: {task_id}")
        print(f"   プロンプト: {prompt[:100]}...")
        
        try:
            # ステータスを「実行中」に更新
            self.sheets_manager.update_task_status(
                task_id=task_id,
                status="in_progress"
            )
            
            # プロンプト送信
            print("\n📤 プロンプト送信中...")
            await browser.send_prompt(prompt)
            
            # レスポンス待機
            print("⏳ レスポンス生成待機中...")
            await browser.wait_for_text_generation(max_wait=120)
            
            # レスポンス取得
            print("📥 レスポンス取得中...")
            response = await browser.extract_latest_text_response()
            
            if not response or len(response) < 50:
                raise Exception(f"レスポンスが短すぎます: {len(response) if response else 0} 文字")
            
            print(f"✅ レスポンス取得成功: {len(response)} 文字")
            
            # ファイル保存
            output_file = self.save_result(task_id, title, response)
            print(f"💾 保存: {output_file}")
            
            # 成功ステータスに更新
            self.sheets_manager.update_task_status(
                task_id=task_id,
                status="completed",
                result={
                    "summary": f"{len(response)}文字のレスポンスを取得",
                    "length": len(response)
                },
                output_file=str(output_file)
            )
            
            print(f"✅ タスク完了: {title}")
            return True
            
        except Exception as e:
            print(f"❌ タスク失敗: {e}")
            
            # 失敗ステータスに更新
            self.sheets_manager.update_task_status(
                task_id=task_id,
                status="failed",
                error_message=str(e)
            )
            
            return False
    
    def save_result(self, task_id: str, title: str, content: str) -> Path:
        """
        結果をファイルに保存
        
        Args:
            task_id: タスクID
            title: タイトル
            content: 内容
            
        Returns:
            保存先のPath
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{task_id}_{timestamp}.md"
        filepath = self.output_dir / filename
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"# {title}\n\n")
            f.write(f"**タスクID**: {task_id}\n")
            f.write(f"**生成日時**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**文字数**: {len(content)}\n\n")
            f.write("---\n\n")
            f.write(content)
        
        return filepath


async def main():
    """
    メイン実行関数
    """
    print("\n🚀 TaskExecutor 起動")
    
    # SheetsManager初期化
    sheets_manager = GoogleSheetsManager(
        service_account_file="configuration/service_account.json",
        spreadsheet_id="YOUR_SPREADSHEET_ID"  # 環境変数または設定ファイルから読み込む
    )
    
    # TaskExecutor初期化
    executor = TaskExecutor(
        sheets_manager=sheets_manager,
        output_dir="agent_outputs"
    )
    
    # すべての未実行タスクを実行
    results = await executor.execute_all_pending_tasks()
    
    print("\n✅ すべての処理が完了しました")


if __name__ == "__main__":
    asyncio.run(main())

EXECUTOR_CODE

chmod +x scripts/task_executor.py

echo "✅ TaskExecutor作成完了"

