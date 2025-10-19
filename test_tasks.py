#!/usr/bin/env python3
"""
シンプルなタスク実行テスト（動作確認済みコードベース）
"""
import asyncio
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from configuration.config_loader import get_spreadsheet_id, get_service_account_file
from browser_control.browser_controller import BrowserController
from tools.sheets_manager import GoogleSheetsManager

async def test_simple_task():
    """シンプルなタスクテスト"""
    
    print("\n" + "="*70)
    print("🚀 シンプルタスクテスト")
    print("="*70)
    
    # SheetsManager初期化
    print("\n[1/5] SheetsManager初期化...")
    sheets = GoogleSheetsManager(
        spreadsheet_id=get_spreadsheet_id(),
        service_account_file=get_service_account_file()
    )
    print("✅ 完了")
    
    # タスク取得
    print("\n[2/5] タスク取得...")
    tasks = sheets.get_tasks()
    
    if not tasks:
        print("❌ タスクなし")
        return
    
    # pending抽出
    pending = [t for t in tasks if t.get('status', '').lower() in ['pending', '']]
    
    if not pending:
        print("❌ pendingタスクなし")
        return
    
    task = pending[0]
    task_id = task.get('id')
    
    print(f"✅ タスク: {task.get('title')}")
    print(f"   ID: {task_id}")
    
    # BrowserController初期化
    print("\n[3/5] ブラウザ起動...")
    async with BrowserController(download_folder="./downloads") as browser:
        print("✅ 完了")
        
        # Gemini接続
        if not await browser.navigate_to_gemini():
            print("❌ Gemini接続失敗")
            return
        
        print("✅ Gemini準備完了")
        
        # ステータス更新
        sheets.update_task_status(task_id=task_id, status="in_progress")
        
        # プロンプト送信（以前成功したコード）
        print(f"\n[4/5] プロンプト送信...")
        prompt = task.get('prompt', 'Please write a brief summary about AI.')
        
        await browser.send_prompt(prompt)
        print("✅ 送信完了")
        
        # レスポンス待機（以前成功した設定）
        print("\n[5/5] レスポンス待機...")
        await browser.wait_for_text_generation(max_wait=120)
        
        # レスポンス取得
        response = await browser.extract_latest_text_response()
        
        if response and len(response) > 50:
            print(f"✅ 成功: {len(response)} 文字")
            
            # ファイル保存
            output_dir = Path("agent_outputs/simple_test")
            output_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = output_dir / f"{task_id}_{timestamp}.md"
            
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(f"# {task.get('title')}\n\n")
                f.write(response)
            
            print(f"💾 保存: {filepath}")
            
            # 成功ステータス
            sheets.update_task_status(
                task_id=task_id,
                status="completed",
                result={"summary": f"{len(response)}文字"},
                output_file=str(filepath)
            )
            
            print("\n" + "="*70)
            print("🎊 テスト成功！")
            print("="*70)
            print(f"\nGoogle Sheets確認:")
            print(f"  https://docs.google.com/spreadsheets/d/{get_spreadsheet_id()}")
            print("="*70)
        else:
            print(f"❌ 失敗: {len(response) if response else 0} 文字")
            sheets.update_task_status(
                task_id=task_id,
                status="failed",
                error="レスポンス取得失敗"
            )

if __name__ == "__main__":
    import os
    os.environ['DISPLAY'] = ':1'
    asyncio.run(test_simple_task())

