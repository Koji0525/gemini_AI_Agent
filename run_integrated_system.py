#!/usr/bin/env python3
"""
既存コード完全対応の統合システム
- 既存のupdate_task_status（async）を使用
- 既存のload_tasks_from_sheetを使用
- pm_tasksシート構造に対応
- BrowserControllerを統合
"""
import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List

sys.path.insert(0, str(Path(__file__).parent))
os.environ['DISPLAY'] = ':1'

from configuration.config_loader import get_spreadsheet_id, get_service_account_file
from browser_control.browser_controller import BrowserController
from tools.sheets_manager import GoogleSheetsManager

class IntegratedTaskExecutor:
    """既存コードと統合されたTaskExecutor"""
    
    def __init__(self, sheets_manager, browser_controller):
        self.sheets = sheets_manager
        self.browser = browser_controller
        self.output_dir = Path("agent_outputs/integrated")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # エージェントマッピング（required_role → 処理）
        self.role_handlers = {
            'design': self.handle_design_task,
            'dev': self.handle_dev_task,
            'wp_dev': self.handle_wp_dev_task,      # WordPress開発
            'wp_cpt': self.handle_wp_cpt_task,      # カスタム投稿タイプ
            'content': self.handle_content_task,
            'review': self.handle_review_task,
            'wp': self.handle_wp_task,
        }
    
    async def execute_all_pending(self) -> Dict:
        """すべてのpendingタスクを実行"""
        
        print("\n" + "="*70)
        print("🚀 統合タスク実行システム起動")
        print("="*70)
        
        # [1/6] タスク読み込み（既存メソッド使用）
        print("\n[1/6] タスク読み込み...")
        tasks = await self.sheets.load_tasks_from_sheet(sheet_name="pm_tasks")
        
        if not tasks:
            print("⚠️  タスクが見つかりません")
            return {"total": 0, "success": 0, "failed": 0}
        
        print(f"✅ {len(tasks)}件のタスクを取得")
        
        # pending抽出
        pending = [t for t in tasks if t.get('status', '').lower() == 'pending']
        
        if not pending:
            print("⚠️  pendingタスクなし")
            print("\nタスク一覧（最初の5件）:")
            for i, t in enumerate(tasks[:5], 1):
                print(f"  {i}. ID={t.get('task_id')}: {t.get('description', '')[:60]}... (status: {t.get('status')})")
            return {"total": 0, "success": 0, "failed": 0}
        
        print(f"   うち pending: {len(pending)}件")
        
        # [2/6] Gemini準備
        print("\n[2/6] Gemini接続...")
        if not await self.browser.navigate_to_gemini():
            print("❌ Gemini接続失敗")
            return {"total": 0, "success": 0, "failed": 0}
        
        print("✅ Gemini準備完了")
        
        # [3/6] タスク実行
        results = {
            "total": len(pending),
            "success": 0,
            "failed": 0,
            "details": []
        }
        
        for i, task in enumerate(pending, 1):
            task_id = task.get('task_id')
            role = task.get('required_role', 'design')
            
            print(f"\n{'='*70}")
            print(f"[{i}/{len(pending)}] タスクID: {task_id}")
            print(f"役割: {role}")
            print(f"概要: {task.get('description', '')[:80]}...")
            print(f"{'='*70}")
            
            try:
                # ステータス更新: in_progress（既存メソッド）
                await self.sheets.update_task_status(
                    task_id=task_id,
                    status="in_progress",
                    sheet_name="pm_tasks"
                )
                
                # 役割に応じた処理
                handler = self.role_handlers.get(role, self.handle_default_task)
                success = await handler(task)
                
                if success:
                    # ステータス更新: completed
                    await self.sheets.update_task_status(
                        task_id=task_id,
                        status="completed",
                        sheet_name="pm_tasks"
                    )
                    results["success"] += 1
                    print(f"✅ タスク {task_id} 完了")
                else:
                    # ステータス更新: failed
                    await self.sheets.update_task_status(
                        task_id=task_id,
                        status="failed",
                        sheet_name="pm_tasks"
                    )
                    results["failed"] += 1
                    print(f"❌ タスク {task_id} 失敗")
                
                results["details"].append({
                    "task_id": task_id,
                    "role": role,
                    "success": success
                })
                
                # レート制限（最後のタスク以外）
                if i < len(pending):
                    print("\n⏳ レート制限: 20秒待機...")
                    await asyncio.sleep(20)
                    
            except Exception as e:
                print(f"❌ エラー: {e}")
                
                # ステータス更新: failed
                await self.sheets.update_task_status(
                    task_id=task_id,
                    status="failed",
                    sheet_name="pm_tasks"
                )
                
                results["failed"] += 1
                results["details"].append({
                    "task_id": task_id,
                    "role": role,
                    "success": False,
                    "error": str(e)
                })
        
        # [4/6] 結果サマリー
        print("\n" + "="*70)
        print("📊 実行結果サマリー")
        print("="*70)
        print(f"実行タスク数: {results['total']}")
        print(f"✅ 成功: {results['success']}")
        print(f"❌ 失敗: {results['failed']}")
        
        if results['total'] > 0:
            success_rate = results['success'] / results['total'] * 100
            print(f"成功率: {success_rate:.1f}%")
        
        print("\n詳細:")
        for detail in results['details']:
            status = "✅" if detail.get('success') else "❌"
            print(f"  {status} タスク{detail['task_id']} ({detail['role']})")
        
        print("="*70)
        
        return results
    
    async def handle_design_task(self, task: Dict) -> bool:
        """設計タスク処理"""
        print("🎨 Design Agent で処理中...")
        return await self._execute_with_gemini(task, "設計")
    
    async def handle_dev_task(self, task: Dict) -> bool:
        """開発タスク処理"""
        print("💻 Dev Agent で処理中...")
        return await self._execute_with_gemini(task, "開発")
    
    async def handle_content_task(self, task: Dict) -> bool:
        """コンテンツ作成タスク処理"""
        print("📝 Content Writer Agent で処理中...")
        return await self._execute_with_gemini(task, "コンテンツ作成")
    
    async def handle_review_task(self, task: Dict) -> bool:
        """レビュータスク処理"""
        print("✅ Review Agent で処理中...")
        return await self._execute_with_gemini(task, "レビュー")
    

    async def handle_wp_dev_task(self, task: Dict) -> bool:
        """WordPress開発タスク処理"""
        print("🌐 WordPress Dev Agent で処理中...")
        return await self._execute_with_gemini(task, "WordPress開発")
    
    async def handle_wp_cpt_task(self, task: Dict) -> bool:
        """WordPressカスタム投稿タイプタスク処理"""
        print("📝 WordPress CPT Agent で処理中...")
        return await self._execute_with_gemini(task, "WordPressカスタム投稿タイプ")


    async def handle_wp_dev_task(self, task: Dict) -> bool:
        """WordPress開発タスク処理"""
        print("🌐 WordPress Dev Agent で処理中...")
        return await self._execute_with_gemini(task, "WordPress開発")
    
    async def handle_wp_cpt_task(self, task: Dict) -> bool:
        """WordPressカスタム投稿タイプタスク処理"""
        print("📝 WordPress CPT Agent で処理中...")
        return await self._execute_with_gemini(task, "WordPressカスタム投稿タイプ")

    async def handle_wp_task(self, task: Dict) -> bool:
        """WordPressタスク処理"""
        print("🌐 WordPress Agent で処理中...")
        return await self._execute_with_gemini(task, "WordPress")
    
    async def handle_default_task(self, task: Dict) -> bool:
        """デフォルトタスク処理"""
        print("🤖 Default Agent で処理中...")
        return await self._execute_with_gemini(task, "汎用")
    
    async def _execute_with_gemini(self, task: Dict, task_type: str) -> bool:
        """Geminiでタスク実行（共通処理）"""
        
        task_id = task.get('task_id')
        description = task.get('description', '')
        
        # プロンプト生成
        prompt = f"""あなたは{task_type}の専門家です。

以下のタスクを実行してください：

タスクID: {task_id}
内容: {description}

具体的な成果物を日本語で作成してください。"""
        
        try:
            # プロンプト送信
            print(f"\n📤 プロンプト送信（{len(prompt)}文字）...")
            await self.browser.send_prompt(prompt)
            print("✅ 送信完了")
            
            # レスポンス待機
            print("⏳ レスポンス生成待機中...")
            await self.browser.wait_for_text_generation(max_wait=120)
            
            # レスポンス取得
            response = await self.browser.extract_latest_text_response()
            
            if response and len(response) > 100:
                print(f"✅ レスポンス取得: {len(response)} 文字")
                
                # ファイル保存
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"task_{task_id}_{task_type}_{timestamp}.md"
                filepath = self.output_dir / filename
                
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(f"# タスク {task_id}: {task_type}\n\n")
                    f.write(f"**概要**: {description}\n\n")
                    f.write(f"**文字数**: {len(response)}\n")
                    f.write(f"**生成日時**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                    f.write("---\n\n")
                    f.write(response)
                
                print(f"💾 保存: {filepath}")
                
                # プレビュー
                print(f"\n📄 レスポンスプレビュー:")
                print("-"*70)
                print(response[:300])
                if len(response) > 300:
                    print("...")
                print("-"*70)
                
                return True
            else:
                print(f"⚠️  レスポンスが短すぎます: {len(response) if response else 0} 文字")
                return False
                
        except Exception as e:
            print(f"❌ 実行エラー: {e}")
            import traceback
            traceback.print_exc()
            return False


async def main():
    """メイン実行"""
    
    print("="*70)
    print("🎯 既存コード完全統合システム")
    print("="*70)
    
    # 初期化
    print("\n初期化中...")
    
    sheets = GoogleSheetsManager(
        spreadsheet_id=get_spreadsheet_id(),
        service_account_file=get_service_account_file()
    )
    
    print("✅ SheetsManager初期化完了")
    
    async with BrowserController(download_folder="./downloads") as browser:
        print("✅ BrowserController初期化完了")
        
        # 統合実行
        executor = IntegratedTaskExecutor(sheets, browser)
        results = await executor.execute_all_pending()
    
    # 最終レポート
    print("\n" + "="*70)
    print("📋 最終レポート")
    print("="*70)
    print(f"\nGoogle Sheetsを確認:")
    print(f"  https://docs.google.com/spreadsheets/d/{get_spreadsheet_id()}")
    print(f"\n出力ファイル:")
    print(f"  agent_outputs/integrated/")
    print("="*70)


if __name__ == "__main__":
    asyncio.run(main())

