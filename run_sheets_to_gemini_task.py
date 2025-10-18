#!/usr/bin/env python3
"""
スプレッドシートからタスクを読み取り、Gemini統合でタスクを実行
"""
import asyncio
import sys
import os
from pathlib import Path
from typing import Dict, List

# パスを追加
sys.path.insert(0, str(Path(__file__).parent))

from scripts.task_executor import TaskExecutor
from tools.sheets_manager import GoogleSheetsManager
from browser_control.browser_controller import BrowserController
from core_agents.design_agent import DesignAgent
from core_agents.dev_agent import DevAgent
from core_agents.review_agent import ReviewAgent


async def run_sheets_integration():
    """
    スプレッドシート統合の完全なフロー
    """
    print("\n" + "="*70)
    print("🎯 スプレッドシート → Gemini タスク実行システム")
    print("="*70)
    
    # ====================================================================
    # STEP 1: Google Sheets Manager 初期化
    # ====================================================================
    print("\n[STEP 1/6] Google Sheetsに接続中...")
    print("="*70)
    
    try:
        # サービスアカウントファイルの確認
        service_account_paths = [
            "service_account.json",
            "credentials.json",
            r"C:\Users\color\Documents\gemini_auto_generate\service_account.json",
        ]
        
        service_account_path = None
        for path in service_account_paths:
            if os.path.exists(path):
                service_account_path = path
                print(f"✅ 認証ファイル発見: {path}")
                break
        
        if not service_account_path:
            print("\n❌ 認証ファイルが見つかりません")
            print("\n必要なファイル:")
            print("  - service_account.json")
            print("  - credentials.json")
            print("\n配置場所:")
            print("  プロジェクトルート (/workspaces/gemini_AI_Agent/)")
            print("\n取得方法:")
            print("  1. Google Cloud Console にアクセス")
            print("  2. サービスアカウントを作成")
            print("  3. JSONキーをダウンロード")
            print("  4. プロジェクトルートに配置")
            return False
        
        # スプレッドシートID（実際のIDに置き換えてください）
        spreadsheet_id = os.environ.get(
            "SPREADSHEET_ID",
            "YOUR_SPREADSHEET_ID_HERE"  # ← 実際のIDに変更
        )
        
        if spreadsheet_id == "YOUR_SPREADSHEET_ID_HERE":
            print("\n⚠️  スプレッドシートIDが設定されていません")
            print("\n設定方法:")
            print("  1. Google Sheetsで対象のスプレッドシートを開く")
            print("  2. URLから ID をコピー:")
            print("     https://docs.google.com/spreadsheets/d/【ここがID】/edit")
            print("  3. 環境変数に設定:")
            print("     export SPREADSHEET_ID='あなたのID'")
            print("\nまたは、このスクリプト内の spreadsheet_id を直接編集してください")
            return False
        
        sheets_manager = GoogleSheetsManager(
            service_account_file=service_account_path,
            spreadsheet_id=spreadsheet_id
        )
        
        print(f"✅ Google Sheets接続成功")
        print(f"   スプレッドシートID: {spreadsheet_id[:20]}...")
        
    except Exception as e:
        print(f"\n❌ Google Sheets接続エラー: {e}")
        print("\n考えられる原因:")
        print("  1. 認証ファイルが不正")
        print("  2. スプレッドシートIDが間違っている")
        print("  3. サービスアカウントに権限がない")
        return False
    
    # ====================================================================
    # STEP 2: ブラウザコントローラー初期化
    # ====================================================================
    print("\n[STEP 2/6] ブラウザコントローラー初期化中...")
    print("="*70)
    
    os.environ["DISPLAY"] = ":1"
    
    browser = BrowserController(download_folder="./downloads")
    await browser.__aenter__()
    
    print("✅ ブラウザ初期化完了")
    
    # ====================================================================
    # STEP 3: エージェント初期化
    # ====================================================================
    print("\n[STEP 3/6] エージェント初期化中...")
    print("="*70)
    
    design_agent = DesignAgent(browser_controller=browser)
    dev_agent = DevAgent(browser_controller=browser)
    review_agent = ReviewAgent(browser_controller=browser)
    
    print("✅ エージェント初期化完了")
    print("   - DesignAgent")
    print("   - DevAgent")
    print("   - ReviewAgent")
    
    # ====================================================================
    # STEP 4: TaskExecutor 初期化
    # ====================================================================
    print("\n[STEP 4/6] TaskExecutor初期化中...")
    print("="*70)
    
    task_executor = TaskExecutor(
        sheets_manager=sheets_manager,
        browser_controller=browser
    )
    
    # エージェント登録
    task_executor.register_agent("design", design_agent)
    task_executor.register_agent("dev", dev_agent)
    task_executor.register_review_agent(review_agent)
    
    print("✅ TaskExecutor初期化完了")
    
    # ====================================================================
    # STEP 5: タスク読み込み
    # ====================================================================
    print("\n[STEP 5/6] スプレッドシートからタスクを読み込み中...")
    print("="*70)
    
    try:
        pending_tasks = await task_executor.load_pending_tasks()
        
        if not pending_tasks:
            print("\n⚠️  実行待ちのタスクが見つかりません")
            print("\nスプレッドシートを確認してください:")
            print("  - ステータスが 'pending' のタスクがあるか")
            print("  - タスクシートの構造が正しいか")
            return False
        
        print(f"\n✅ {len(pending_tasks)} 件のタスクを読み込みました")
        print("\n📋 タスク一覧:")
        for i, task in enumerate(pending_tasks[:5], 1):  # 最初の5件
            task_type = task.get('type', 'unknown')
            task_desc = task.get('description', 'No description')[:50]
            print(f"   {i}. [{task_type}] {task_desc}...")
        
        if len(pending_tasks) > 5:
            print(f"   ... 他 {len(pending_tasks) - 5} 件")
        
    except Exception as e:
        print(f"\n❌ タスク読み込みエラー: {e}")
        return False
    
    # ====================================================================
    # STEP 6: タスク実行
    # ====================================================================
    print("\n[STEP 6/6] タスク実行開始...")
    print("="*70)
    
    try:
        # 最初のタスクのみ実行（テスト）
        first_task = pending_tasks[0]
        
        print(f"\n🎯 タスク実行:")
        print(f"   タイプ: {first_task.get('type', 'unknown')}")
        print(f"   内容: {first_task.get('description', 'No description')}")
        
        success = await task_executor.execute_task(first_task)
        
        if success:
            print("\n✅✅✅ タスク実行成功！")
            print("\n次のステップ:")
            print("  1. スプレッドシートで結果を確認")
            print("  2. agent_outputs/ で生成物を確認")
            print("  3. 必要に応じて次のタスクを実行")
        else:
            print("\n⚠️  タスク実行が完了しませんでした")
            print("詳細はログを確認してください")
        
    except Exception as e:
        print(f"\n❌ タスク実行エラー: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # クリーンアップ
        await browser.__aexit__(None, None, None)
        print("\n🧹 ブラウザをクリーンアップしました")
    
    return True


async def main():
    """メイン関数"""
    print("\n🚀 スプレッドシート統合システム起動")
    
    # DISPLAY環境変数設定
    if not os.environ.get("DISPLAY"):
        os.environ["DISPLAY"] = ":1"
        print("⚠️  DISPLAYを:1に設定しました")
    
    result = await run_sheets_integration()
    
    if result:
        print("\n" + "="*70)
        print("🎊 統合テスト完了！")
        print("="*70)
    else:
        print("\n" + "="*70)
        print("⚠️  統合テストが完了しませんでした")
        print("="*70)
        print("\n上記のエラーメッセージを確認して、必要な設定を行ってください")


if __name__ == "__main__":
    asyncio.run(main())

