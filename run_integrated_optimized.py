#!/usr/bin/env python3
"""
最適化版統合システム
- 動的レート制限
- WordPress統合
- タブ管理
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

class OptimizedTaskExecutor:
    """最適化版TaskExecutor"""
    
    def __init__(self, sheets_manager, browser_controller, rate_limit_mode='balanced'):
        self.sheets = sheets_manager
        self.browser = browser_controller
        self.output_dir = Path("agent_outputs/integrated")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # レート制限モード設定
        self.rate_limits = {
            'aggressive': 10,   # 攻めモード
            'balanced': 15,     # バランス（推奨）
            'safe': 20,         # 安全
            'test': 5           # テスト用
        }
        self.current_rate_limit = self.rate_limits.get(rate_limit_mode, 15)
        
        print(f"\n⏱️  レート制限モード: {rate_limit_mode}")
        print(f"   間隔: {self.current_rate_limit}秒")
        print(f"   1時間あたり: 約{3600 // self.current_rate_limit}タスク")
        
        # 役割マッピング
        self.role_handlers = {
            'design': self.handle_design_task,
            'dev': self.handle_dev_task,
            'wp_dev': self.handle_wp_dev_task,
            'wp_cpt': self.handle_wp_cpt_task,
            'wordpress': self.handle_wordpress_task,
            'writer_en': self.handle_writer_en_task,
            'content': self.handle_content_task,
            'review': self.handle_review_task,
            'wp': self.handle_wp_task,
        }
        
        # WordPressログイン状態
        self.wp_logged_in = False
        
        print(f"\n📋 登録エージェント: {len(self.role_handlers)}種類")
    
    async def ensure_wordpress_login(self):
        """WordPressログインを確保（別タブ）"""
        
        if self.wp_logged_in:
            return True
        
        try:
            print("\n🌐 WordPress接続確認...")
            
            # 新しいタブでWordPressを開く
            # browser_controller に既存のタブ管理機能があるか確認
            if hasattr(self.browser, 'open_new_tab'):
                wp_page = await self.browser.open_new_tab()
                await wp_page.goto('http://localhost/wp-admin')
                
                # ログイン確認
                # 既にログイン済みの場合はダッシュボードにリダイレクトされる
                await asyncio.sleep(2)
                
                current_url = wp_page.url
                if 'wp-admin' in current_url and 'wp-login' not in current_url:
                    print("✅ WordPress既にログイン済み")
                    self.wp_logged_in = True
                else:
                    print("⚠️  WordPressログインが必要")
                    # TODO: 自動ログイン実装
                    
            else:
                print("⚠️  タブ管理機能が見つかりません（Geminiのみ使用）")
            
            return self.wp_logged_in
            
        except Exception as e:
            print(f"⚠️  WordPress接続エラー: {e}")
            return False
    
    async def execute_all_pending(self, max_tasks: int = None) -> Dict:
        """すべてのpendingタスクを実行"""
        
        print("\n" + "="*70)
        print("🚀 最適化版統合システム起動")
        print("="*70)
        
        # タスク読み込み
        print("\n[1/7] タスク読み込み...")
        tasks = await self.sheets.load_tasks_from_sheet(sheet_name="pm_tasks")
        
        if not tasks:
            return {"total": 0, "success": 0, "failed": 0}
        
        print(f"✅ {len(tasks)}件のタスクを取得")
        
        # pending抽出
        pending = []
        for t in tasks:
            status = t.get('status', '').strip().lower()
            if status == 'pending' or status == '' or 'pending' in status:
                pending.append(t)
        
        if not pending:
            print("\n⚠️  pendingタスクなし")
            return {"total": 0, "success": 0, "failed": 0}
        
        # 最大タスク数の制限
        if max_tasks and len(pending) > max_tasks:
            print(f"\n⚠️  {len(pending)}件中、最初の{max_tasks}件のみ実行")
            pending = pending[:max_tasks]
        
        print(f"\n✅ {len(pending)}件のpendingタスクを実行")
        
        # レート制限の自動調整
        if len(pending) <= 5:
            self.current_rate_limit = self.rate_limits['test']
            print(f"   少数タスク → {self.current_rate_limit}秒間隔に変更")
        elif len(pending) <= 20:
            self.current_rate_limit = self.rate_limits['aggressive']
            print(f"   中規模 → {self.current_rate_limit}秒間隔に変更")
        
        # Gemini準備
        print("\n[2/7] Gemini接続...")
        if not await self.browser.navigate_to_gemini():
            print("❌ Gemini接続失敗")
            return {"total": 0, "success": 0, "failed": 0}
        
        print("✅ Gemini準備完了")
        
        # WordPress準備（wp系タスクがある場合）
        has_wp_task = any(
            'wp' in t.get('required_role', '').lower() 
            for t in pending
        )
        
        if has_wp_task:
            print("\n[3/7] WordPress接続...")
            await self.ensure_wordpress_login()
        else:
            print("\n[3/7] WordPress接続スキップ（wp系タスクなし）")
        
        # タスク実行
        print("\n[4/7] タスク実行開始...")
        
        results = {
            "total": len(pending),
            "success": 0,
            "failed": 0,
            "details": [],
            "start_time": datetime.now(),
        }
        
        for i, task in enumerate(pending, 1):
            task_id = task.get('task_id')
            role = task.get('required_role', 'design').strip().lower()
            
            print(f"\n{'='*70}")
            print(f"[{i}/{len(pending)}] タスクID: {task_id}")
            print(f"役割: {role}")
            print(f"{'='*70}")
            
            handler = self.role_handlers.get(role, self.handle_default_task)
            handler_name = handler.__name__.replace('handle_', '').replace('_task', '')
            print(f"🎯 エージェント: {handler_name}")
            
            try:
                await self.sheets.update_task_status(
                    task_id=task_id,
                    status="in_progress",
                    sheet_name="pm_tasks"
                )
                
                success = await handler(task)
                
                if success:
                    await self.sheets.update_task_status(
                        task_id=task_id,
                        status="completed",
                        sheet_name="pm_tasks"
                    )
                    results["success"] += 1
                    print(f"✅ 完了")
                else:
                    await self.sheets.update_task_status(
                        task_id=task_id,
                        status="failed",
                        sheet_name="pm_tasks"
                    )
                    results["failed"] += 1
                    print(f"❌ 失敗")
                
                results["details"].append({
                    "task_id": task_id,
                    "role": role,
                    "agent": handler_name,
                    "success": success
                })
                
                # 動的レート制限
                if i < len(pending):
                    print(f"\n⏳ レート制限: {self.current_rate_limit}秒待機...")
                    await asyncio.sleep(self.current_rate_limit)
                    
            except Exception as e:
                print(f"❌ エラー: {e}")
                results["failed"] += 1
        
        results["end_time"] = datetime.now()
        results["duration"] = (results["end_time"] - results["start_time"]).total_seconds()
        
        # サマリー
        print("\n" + "="*70)
        print("📊 実行結果サマリー")
        print("="*70)
        print(f"実行タスク数: {results['total']}")
        print(f"✅ 成功: {results['success']}")
        print(f"❌ 失敗: {results['failed']}")
        print(f"⏱️  実行時間: {results['duration']:.1f}秒")
        print(f"   平均: {results['duration']/results['total']:.1f}秒/タスク")
        
        if results['total'] > 0:
            success_rate = results['success'] / results['total'] * 100
            print(f"成功率: {success_rate:.1f}%")
        
        print("="*70)
        
        return results
    
    # エージェントハンドラー（既存と同じ）
    async def handle_design_task(self, task: Dict) -> bool:
        print("🎨 Design Agent")
        return await self._execute_with_gemini(task, "設計専門家")
    
    async def handle_dev_task(self, task: Dict) -> bool:
        print("💻 Dev Agent")
        return await self._execute_with_gemini(task, "開発専門家")
    
    async def handle_wp_dev_task(self, task: Dict) -> bool:
        print("🌐 WordPress Dev Agent")
        result = await self._execute_with_gemini(task, "WordPress開発専門家")
        
        # WordPress統合が有効な場合、投稿も試みる
        if result and self.wp_logged_in:
            print("   📝 WordPress投稿を試行中...")
            # TODO: WordPress REST API統合
        
        return result
    
    async def handle_wp_cpt_task(self, task: Dict) -> bool:
        print("📝 WordPress CPT Agent")
        return await self._execute_with_gemini(task, "WordPressカスタム投稿タイプ専門家")
    
    async def handle_wordpress_task(self, task: Dict) -> bool:
        print("🌐 WordPress Agent")
        return await self._execute_with_gemini(task, "WordPress専門家")
    
    async def handle_writer_en_task(self, task: Dict) -> bool:
        print("✍️ English Writer Agent")
        return await self._execute_with_gemini(task, "英語ライティング専門家")
    
    async def handle_content_task(self, task: Dict) -> bool:
        print("📝 Content Writer Agent")
        return await self._execute_with_gemini(task, "コンテンツ作成専門家")
    
    async def handle_review_task(self, task: Dict) -> bool:
        print("✅ Review Agent")
        return await self._execute_with_gemini(task, "品質レビュー専門家")
    
    async def handle_wp_task(self, task: Dict) -> bool:
        print("🌐 WP Agent")
        return await self._execute_with_gemini(task, "WordPress専門家")
    
    async def handle_default_task(self, task: Dict) -> bool:
        print("🤖 Default Agent")
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
            await self.browser.send_prompt(prompt)
            await self.browser.wait_for_text_generation(max_wait=120)
            response = await self.browser.extract_latest_text_response()
            
            if response and len(response) > 100:
                print(f"   ✅ {len(response)} 文字")
                
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"task_{task_id}_{agent_type}_{timestamp}.md"
                filepath = self.output_dir / filename
                
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(f"# タスク {task_id}: {agent_type}\n\n")
                    f.write(f"**概要**: {description}\n\n")
                    f.write("---\n\n")
                    f.write(response)
                
                return True
            else:
                return False
                
        except Exception as e:
            print(f"   ❌ {e}")
            return False


async def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='最適化版統合システム')
    parser.add_argument('--mode', choices=['test', 'aggressive', 'balanced', 'safe'], 
                       default='balanced', help='レート制限モード')
    parser.add_argument('--max-tasks', type=int, help='最大タスク数')
    
    args = parser.parse_args()
    
    print("="*70)
    print("🎯 最適化版統合システム")
    print("="*70)
    print(f"\nモード: {args.mode}")
    if args.max_tasks:
        print(f"最大タスク数: {args.max_tasks}")
    
    sheets = GoogleSheetsManager(
        spreadsheet_id=get_spreadsheet_id(),
        service_account_file=get_service_account_file()
    )
    
    async with BrowserController(download_folder="./downloads") as browser:
        executor = OptimizedTaskExecutor(sheets, browser, rate_limit_mode=args.mode)
        results = await executor.execute_all_pending(max_tasks=args.max_tasks)
    
    print("\n" + "="*70)
    print("📋 完了")
    print("="*70)


if __name__ == "__main__":
    asyncio.run(main())

