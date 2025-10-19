#!/usr/bin/env python3
"""
TaskExecutor - シンプル版（動作確認済み）
"""
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional

class TaskExecutor:
    """シンプルなタスク実行"""
    
    def __init__(self, sheets_manager, browser_controller):
        self.sheets = sheets_manager
        self.browser = browser_controller
        self.output_dir = Path("agent_outputs/executor")
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    async def execute_all_pending(self) -> Dict:
        """すべてのpendingタスクを実行"""
        
        print("\n🚀 TaskExecutor起動")
        
        # タスク取得
        tasks = self.sheets.get_tasks()
        pending = [t for t in tasks if t.get('status', '').lower() in ['pending', '']]
        
        if not pending:
            print("⚠️  pendingタスクなし")
            return {"total": 0, "success": 0, "failed": 0}
        
        print(f"📋 {len(pending)}件のタスクを実行")
        
        # Gemini準備
        if not await self.browser.navigate_to_gemini():
            print("❌ Gemini接続失敗")
            return {"total": 0, "success": 0, "failed": 0}
        
        # 実行
        results = {"total": len(pending), "success": 0, "failed": 0}
        
        for i, task in enumerate(pending, 1):
            print(f"\n[{i}/{len(pending)}] {task.get('title')}")
            
            success = await self.execute_single(task)
            
            if success:
                results["success"] += 1
            else:
                results["failed"] += 1
            
            # レート制限（30秒待機）
            if i < len(pending):
                print("⏳ 30秒待機...")
                await asyncio.sleep(30)
        
        print("\n" + "="*70)
        print(f"📊 結果: {results['success']}/{results['total']} 成功")
        print("="*70)
        
        return results
    
    async def execute_single(self, task: Dict) -> bool:
        """単一タスク実行"""
        
        task_id = task.get('id')
        
        try:
            # in_progress
            self.sheets.update_task_status(task_id=task_id, status="in_progress")
            
            # プロンプト送信
            await self.browser.send_prompt(task.get('prompt', ''))
            
            # レスポンス待機
            await self.browser.wait_for_text_generation(max_wait=120)
            response = await self.browser.extract_latest_text_response()
            
            if response and len(response) > 50:
                # ファイル保存
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filepath = self.output_dir / f"{task_id}_{timestamp}.md"
                
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(f"# {task.get('title')}\n\n")
                    f.write(response)
                
                # completed
                self.sheets.update_task_status(
                    task_id=task_id,
                    status="completed",
                    result={"summary": f"{len(response)}文字"},
                    output_file=str(filepath)
                )
                
                print(f"✅ 成功: {len(response)} 文字")
                return True
            else:
                raise Exception("レスポンス不足")
                
        except Exception as e:
            print(f"❌ 失敗: {e}")
            
            self.sheets.update_task_status(
                task_id=task_id,
                status="failed",
                error=str(e)
            )
            
            return False

