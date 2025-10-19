#!/usr/bin/env python3
"""
完全修正版統合システム
- pending判定の柔軟化
- 役割マッピング完全対応
- デバッグログ強化
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
    """既存コードと統合されたTaskExecutor（修正版）"""
    
    def __init__(self, sheets_manager, browser_controller):
        self.sheets = sheets_manager
        self.browser = browser_controller
        self.output_dir = Path("agent_outputs/integrated")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 拡張された役割マッピング
        self.role_handlers = {
            'design': self.handle_design_task,
            'dev': self.handle_dev_task,
            'wp_dev': self.handle_wp_dev_task,        # WordPress開発
            'wp_cpt': self.handle_wp_cpt_task,        # カスタム投稿タイプ
            'wordpress': self.handle_wordpress_task,  # WordPress汎用
            'writer_en': self.handle_writer_en_task,  # 英語ライター
            'content': self.handle_content_task,
            'review': self.handle_review_task,
            'wp': self.handle_wp_task,
        }
        
        print(f"\n📋 登録されているエージェント:")
        for role in sorted(self.role_handlers.keys()):
            print(f"   ✅ {role}")
    
    async def execute_all_pending(self) -> Dict:
        """すべてのpendingタスクを実行"""
        
        print("\n" + "="*70)
        print("🚀 統合タスク実行システム起動")
        print("="*70)
        
        # [1/6] タスク読み込み
        print("\n[1/6] タスク読み込み...")
        tasks = await self.sheets.load_tasks_from_sheet(sheet_name="pm_tasks")
        
        if not tasks:
            print("⚠️  タスクが見つかりません")
            return {"total": 0, "success": 0, "failed": 0}
        
        print(f"✅ {len(tasks)}件のタスクを取得")
        
        # デバッグ: 最初の5件のステータスを確認
        print("\n🔍 デバッグ: 最初の5件のステータス確認")
        for i, t in enumerate(tasks[:5], 1):
            status_raw = t.get('status', '')
            status_clean = status_raw.strip() if status_raw else ''
            print(f"   {i}. ID={t.get('task_id')}: status='{status_raw}' → clean='{status_clean}'")
        
        # pending抽出（柔軟判定）
        pending = []
        for t in tasks:
            status = t.get('status', '').strip().lower()
            # pending または 空文字列 または 'pending'を含む
            if status == 'pending' or status == '' or 'pending' in status:
                pending.append(t)
        
        print(f"\n📊 pending判定結果:")
        print(f"   全タスク: {len(tasks)}")
        print(f"   pending: {len(pending)}")
        
        if not pending:
            print("\n⚠️  pendingタスクなし（詳細）")
            print("\nすべてのタスクのステータス:")
            status_count = {}
            for t in tasks:
                status = t.get('status', '(空)').strip() or '(空)'
                status_count[status] = status_count.get(status, 0) + 1
            
            for status, count in sorted(status_count.items()):
                print(f"   {status}: {count}件")
            
            return {"total": 0, "success": 0, "failed": 0}
        
        # pending タスクの詳細表示
        print(f"\n✅ {len(pending)}件のpendingタスクを発見:")
        for i, t in enumerate(pending[:5], 1):
            print(f"   {i}. ID={t.get('task_id')}: {t.get('description', '')[:60]}... (role: {t.get('required_role')})")
        
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
            role = task.get('required_role', 'design').strip().lower()
            
            print(f"\n{'='*70}")
            print(f"[{i}/{len(pending)}] タスクID: {task_id}")
            print(f"役割: {role}")
            print(f"概要: {task.get('description', '')[:80]}...")
            print(f"{'='*70}")
            
            # エージェント選択
            handler = self.role_handlers.get(role, self.handle_default_task)
            handler_name = handler.__name__.replace('handle_', '').replace('_task', '')
            print(f"🎯 使用エージェント: {handler_name}")
            
            try:
                # ステータス更新: in_progress
                await self.sheets.update_task_status(
                    task_id=task_id,
                    status="in_progress",
                    sheet_name="pm_tasks"
                )
                
                # タスク実行
                success = await handler(task)
                
                if success:
                    # completed
                    await self.sheets.update_task_status(
                        task_id=task_id,
                        status="completed",
                        sheet_name="pm_tasks"
                    )
                    results["success"] += 1
                    print(f"✅ タスク {task_id} 完了")
                else:
                    # failed
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
                    "agent": handler_name,
                    "success": success
                })
                
                # レート制限
                if i < len(pending):
                    print("\n⏳ レート制限: 20秒待機...")
                    await asyncio.sleep(20)
                    
            except Exception as e:
                print(f"❌ エラー: {e}")
                
                await self.sheets.update_task_status(
                    task_id=task_id,
                    status="failed",
                    sheet_name="pm_tasks"
                )
                
                results["failed"] += 1
                results["details"].append({
                    "task_id": task_id,
                    "role": role,
                    "agent": "error",
                    "success": False,
                    "error": str(e)
                })
        
        # 結果サマリー
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
            print(f"  {status} タスク{detail['task_id']} ({detail['role']}) → {detail['agent']}エージェント")
        
        print("="*70)
        
        return results
    
    # エージェントハンドラー
    async def handle_design_task(self, task: Dict) -> bool:
        print("🎨 Design Agent で処理中...")
        return await self._execute_with_gemini(task, "設計専門家")
    
    async def handle_dev_task(self, task: Dict) -> bool:
        print("💻 Dev Agent で処理中...")
        return await self._execute_with_gemini(task, "開発専門家")
    
    async def handle_wp_dev_task(self, task: Dict) -> bool:
        print("🌐 WordPress Dev Agent で処理中...")
        return await self._execute_with_gemini(task, "WordPress開発専門家")
    
    async def handle_wp_cpt_task(self, task: Dict) -> bool:
        print("📝 WordPress CPT Agent で処理中...")
        return await self._execute_with_gemini(task, "WordPressカスタム投稿タイプ専門家")
    
    async def handle_wordpress_task(self, task: Dict) -> bool:
        print("🌐 WordPress Agent で処理中...")
        return await self._execute_with_gemini(task, "WordPress専門家")
    
    async def handle_writer_en_task(self, task: Dict) -> bool:
        print("✍️ English Writer Agent で処理中...")
        return await self._execute_with_gemini(task, "英語ライティング専門家")
    
    async def handle_content_task(self, task: Dict) -> bool:
        print("📝 Content Writer Agent で処理中...")
        return await self._execute_with_gemini(task, "コンテンツ作成専門家")
    
    async def handle_review_task(self, task: Dict) -> bool:
        print("✅ Review Agent で処理中...")
        return await self._execute_with_gemini(task, "品質レビュー専門家")
    
    async def handle_wp_task(self, task: Dict) -> bool:
        print("🌐 WordPress Agent で処理中...")
        return await self._execute_with_gemini(task, "WordPress専門家")
    
    async def handle_default_task(self, task: Dict) -> bool:
        print("🤖 Default Agent で処理中...")
        return await self._execute_with_gemini(task, "汎用")
    
    async def _execute_with_gemini(self, task: Dict, agent_type: str) -> bool:
        """Geminiでタスク実行"""
        
        task_id = task.get('task_id')
        description = task.get('description', '')
        
        prompt = f"""あなたは{agent_type}です。

以下のタスクを実行してください：

タスクID: {task_id}
内容: {description}

具体的な成果物を日本語で作成してください。"""
        
        try:
            print(f"\n📤 プロンプト送信...")
            await self.browser.send_prompt(prompt)
            print("✅ 送信完了")
            
            print("⏳ レスポンス生成待機中...")
            await self.browser.wait_for_text_generation(max_wait=120)
            
            response = await self.browser.extract_latest_text_response()
            
            if response and len(response) > 100:
                print(f"✅ レスポンス取得: {len(response)} 文字")
                
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"task_{task_id}_{agent_type}_{timestamp}.md"
                filepath = self.output_dir / filename
                
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(f"# タスク {task_id}: {agent_type}\n\n")
                    f.write(f"**概要**: {description}\n\n")
                    f.write(f"**文字数**: {len(response)}\n\n")
                    f.write("---\n\n")
                    f.write(response)
                
                print(f"💾 保存: {filepath}")
                return True
            else:
                print(f"⚠️  レスポンス短い: {len(response) if response else 0} 文字")
                return False
                
        except Exception as e:
            print(f"❌ 実行エラー: {e}")
            return False


async def main():
    print("="*70)
    print("🎯 完全修正版統合システム")
    print("="*70)
    
    sheets = GoogleSheetsManager(
        spreadsheet_id=get_spreadsheet_id(),
        service_account_file=get_service_account_file()
    )
    
    print("✅ SheetsManager初期化完了")
    
    async with BrowserController(download_folder="./downloads") as browser:
        print("✅ BrowserController初期化完了")
        
        executor = IntegratedTaskExecutor(sheets, browser)
        results = await executor.execute_all_pending()
    
    print("\n" + "="*70)
    print("📋 最終レポート")
    print("="*70)
    print(f"\nGoogle Sheets:")
    print(f"  https://docs.google.com/spreadsheets/d/{get_spreadsheet_id()}")
    print(f"\n出力ファイル:")
    print(f"  agent_outputs/integrated/")
    print("="*70)


if __name__ == "__main__":
    asyncio.run(main())

