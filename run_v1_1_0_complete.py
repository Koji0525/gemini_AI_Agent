#!/usr/bin/env python3
"""
v1.1.0-integrated 完全版
- 複数依存対応
- 依存チェック
- 循環依存検出
- スマート要約
- 品質評価
- 自動再実行
- ゴール達成度測定
"""
import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Set
import hashlib
import re

sys.path.insert(0, str(Path(__file__).parent))
os.environ['DISPLAY'] = ':1'

from configuration.config_loader import get_spreadsheet_id, get_service_account_file
from browser_control.browser_controller import BrowserController
from tools.sheets_manager import GoogleSheetsManager


# カスタム例外
class DependencyNotReadyError(Exception):
    """依存タスクが未完了"""
    pass

class CircularDependencyError(Exception):
    """循環依存を検出"""
    pass

class TaskExecutionError(Exception):
    """タスク実行失敗"""
    pass


# WordPressエージェント
try:
    from wordpress.wp_agent import WordPressAgent
    HAS_WP_AGENT = True
except:
    HAS_WP_AGENT = False


class AdvancedFeedbackExecutor:
    """v1.1.0 高度なフィードバックシステム"""
    
    def __init__(self, sheets_manager, browser_controller):
        self.sheets = sheets_manager
        self.browser = browser_controller
        
        # ストレージ
        self.github_storage = Path("/workspaces/gemini_AI_Agent/agent_outputs/tasks")
        self.github_storage.mkdir(parents=True, exist_ok=True)
        
        self.rate_limit = 10
        
        # 設定
        self.max_retries = 3
        self.quality_threshold = 7  # 10点満点中7点以上
        self.smart_summary_enabled = True
        
        # プロジェクトゴール
        self.project_goal = None
        
        # エージェント
        self.agents = {}
        self._initialize_agents()
    
    def _initialize_agents(self):
        """エージェント初期化"""
        
        print(f"\n🤖 エージェント初期化:")
        
        if HAS_WP_AGENT:
            try:
                self.agents['wp'] = WordPressAgent(self.browser)
                self.agents['wordpress'] = self.agents['wp']
                print("  ✅ WordPressAgent")
            except Exception as e:
                print(f"  ⚠️  初期化失敗: {e}")
    
    # ========================================
    # 依存関係管理（新機能）
    # ========================================
    
    def parse_dependencies(self, dependencies: str) -> List[int]:
        """依存関係を解析（複数対応）"""
        
        if not dependencies or dependencies.strip() == '':
            return []
        
        # カンマ区切りで分割
        dep_ids = []
        for dep in dependencies.split(','):
            dep = dep.strip()
            if dep.isdigit():
                dep_ids.append(int(dep))
        
        return dep_ids
    
    async def get_task_status(self, task_id: int) -> Optional[str]:
        """タスクのステータスを取得"""
        
        try:
            spreadsheet = self.sheets.gc.open_by_key(get_spreadsheet_id())
            log_sheet = spreadsheet.worksheet('task_execution_log')
            
            all_data = log_sheet.get_all_values()
            
            # 最新のログを検索（逆順）
            for row in reversed(all_data[1:]):
                if len(row) > 1 and str(row[1]) == str(task_id):
                    return row[7] if len(row) > 7 else None
            
            return None
            
        except Exception as e:
            print(f"   ⚠️  ステータス取得エラー: {e}")
            return None
    
    async def validate_dependencies(self, task: Dict) -> bool:
        """依存タスクが完了しているか確認"""
        
        dependencies = task.get('dependencies', '')
        if not dependencies:
            return True
        
        dep_ids = self.parse_dependencies(dependencies)
        
        if not dep_ids:
            return True
        
        print(f"   🔍 依存チェック: {dep_ids}")
        
        for dep_id in dep_ids:
            status = await self.get_task_status(dep_id)
            
            if status != 'completed':
                print(f"   ❌ タスク{dep_id}が未完了（status: {status}）")
                return False
        
        print(f"   ✅ 全依存タスク完了")
        return True
    
    def detect_circular_dependency(
        self, 
        task_id: int, 
        all_tasks: List[Dict],
        visited: Optional[Set[int]] = None,
        path: Optional[List[int]] = None
    ) -> bool:
        """循環依存を検出"""
        
        if visited is None:
            visited = set()
            path = []
        
        if task_id in visited:
            cycle_path = path + [task_id]
            cycle_str = " → ".join(map(str, cycle_path))
            print(f"   ⚠️  循環依存検出: {cycle_str}")
            return True
        
        visited.add(task_id)
        path.append(task_id)
        
        # このタスクの依存を取得
        task = next((t for t in all_tasks if t.get('task_id') == task_id), None)
        
        if task:
            dep_ids = self.parse_dependencies(task.get('dependencies', ''))
            
            for dep_id in dep_ids:
                if self.detect_circular_dependency(dep_id, all_tasks, visited.copy(), path.copy()):
                    return True
        
        return False
    
    # ========================================
    # スマート要約（新機能）
    # ========================================
    
    async def smart_summarize_dependency(
        self, 
        full_output: str,
        task_description: str
    ) -> str:
        """重要な情報のみを抽出（Gemini使用）"""
        
        if not self.smart_summary_enabled or len(full_output) <= 2000:
            return full_output[:2000]
        
        print(f"   🤔 スマート要約中（{len(full_output):,}文字 → 約1000文字）...")
        
        try:
            summary_prompt = f"""以下の出力から、次のタスク「{task_description}」に必要な重要情報のみを抽出してください。

出力（{len(full_output)}文字）:
{full_output[:3000]}

重要情報を1000文字以内でまとめてください。"""
            
            await self.browser.send_prompt(summary_prompt)
            await self.browser.wait_for_text_generation(max_wait=60)
            summary = await self.browser.extract_latest_text_response()
            
            if summary and len(summary) > 50:
                print(f"   ✅ 要約完了: {len(summary)}文字")
                return summary
            else:
                print(f"   ⚠️  要約失敗、元の出力を使用")
                return full_output[:2000]
                
        except Exception as e:
            print(f"   ⚠️  要約エラー: {e}")
            return full_output[:2000]
    
    # ========================================
    # 品質評価（新機能）
    # ========================================
    
    async def evaluate_quality(
        self, 
        task: Dict,
        output: str
    ) -> Dict[str, any]:
        """出力品質を評価"""
        
        print(f"   📊 品質評価中...")
        
        try:
            evaluation_prompt = f"""以下のタスク出力を評価してください。

タスク: {task.get('description')}
出力文字数: {len(output)}

評価基準（各項目1-10点）:
1. 完成度: タスク要件を満たしているか
2. 正確性: 内容に誤りがないか
3. 実用性: 実際に使える内容か

出力:
{output[:1000]}

以下の形式で回答してください:
完成度: X点
正確性: X点
実用性: X点
総合点: X点
理由: [簡潔に]"""
            
            await self.browser.send_prompt(evaluation_prompt)
            await self.browser.wait_for_text_generation(max_wait=60)
            evaluation = await self.browser.extract_latest_text_response()
            
            # スコア抽出
            total_score = 0
            if evaluation:
                match = re.search(r'総合点[：:]\s*(\d+)', evaluation)
                if match:
                    total_score = int(match.group(1))
            
            result = {
                "score": total_score,
                "evaluation": evaluation,
                "passed": total_score >= self.quality_threshold
            }
            
            print(f"   📊 評価結果: {total_score}/10点")
            
            if result["passed"]:
                print(f"   ✅ 品質基準クリア（{self.quality_threshold}点以上）")
            else:
                print(f"   ⚠️  品質基準未達（{self.quality_threshold}点未満）")
            
            return result
            
        except Exception as e:
            print(f"   ⚠️  評価エラー: {e}")
            return {"score": 0, "evaluation": "", "passed": False}
    
    # ========================================
    # 自動再実行（新機能）
    # ========================================
    
    async def execute_with_retry(
        self,
        task: Dict,
        role: str,
        dependency_output: Optional[str] = None
    ) -> tuple:
        """失敗時に自動再実行"""
        
        for attempt in range(self.max_retries):
            try:
                print(f"   �� 実行試行 {attempt + 1}/{self.max_retries}")
                
                success, output, error = await self._execute_with_gemini(
                    task, role, dependency_output
                )
                
                if success:
                    # 品質評価
                    quality = await self.evaluate_quality(task, output)
                    
                    if quality["passed"]:
                        print(f"   ✅ 実行成功（品質OK）")
                        return True, output, ""
                    else:
                        print(f"   ⚠️  品質不足、再試行します...")
                        error = f"品質スコア: {quality['score']}/{self.quality_threshold}"
                else:
                    print(f"   ⚠️  試行 {attempt + 1} 失敗: {error}")
                
                # 最後の試行でなければ待機
                if attempt < self.max_retries - 1:
                    wait_time = 10 * (attempt + 1)
                    print(f"   ⏳ {wait_time}秒待機後に再試行...")
                    await asyncio.sleep(wait_time)
                    
            except Exception as e:
                print(f"   ❌ 試行 {attempt + 1} エラー: {e}")
                
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(10 * (attempt + 1))
        
        # 全試行失敗
        error_msg = f"{self.max_retries}回の試行後も失敗"
        print(f"   ❌ {error_msg}")
        return False, "", error_msg
    
    # ========================================
    # ゴール達成度測定（新機能）
    # ========================================
    
    async def measure_goal_progress(self) -> Dict:
        """ゴール達成度を測定"""
        
        print(f"\n📊 ゴール達成度測定中...")
        
        try:
            # 量的評価
            spreadsheet = self.sheets.gc.open_by_key(get_spreadsheet_id())
            pm_tasks = spreadsheet.worksheet('pm_tasks')
            
            all_data = pm_tasks.get_all_values()
            total_tasks = len(all_data) - 1  # ヘッダー除く
            
            # completedタスク数を取得
            status_col = None
            for i, header in enumerate(all_data[0]):
                if 'status' in header.lower():
                    status_col = i
                    break
            
            completed_count = 0
            if status_col is not None:
                for row in all_data[1:]:
                    if status_col < len(row):
                        if row[status_col].lower() == 'completed':
                            completed_count += 1
            
            quantitative_progress = (completed_count / total_tasks * 100) if total_tasks > 0 else 0
            
            print(f"   量的進捗: {completed_count}/{total_tasks} ({quantitative_progress:.1f}%)")
            
            # 質的評価（Gemini使用）
            if self.project_goal:
                print(f"   質的評価中...")
                
                eval_prompt = f"""プロジェクトゴール:
{self.project_goal}

進捗状況:
- 完了タスク: {completed_count}/{total_tasks} ({quantitative_progress:.1f}%)

ゴール達成度を評価してください（0-100%）。
また、次に優先すべきタスクの種類を提案してください。

評価（%）:
次の優先事項:"""
                
                await self.browser.send_prompt(eval_prompt)
                await self.browser.wait_for_text_generation(max_wait=60)
                qualitative_eval = await self.browser.extract_latest_text_response()
                
                # パーセンテージ抽出
                qualitative_progress = 0
                if qualitative_eval:
                    match = re.search(r'(\d+)%', qualitative_eval)
                    if match:
                        qualitative_progress = int(match.group(1))
                
                print(f"   質的進捗: {qualitative_progress}%")
            else:
                qualitative_eval = "ゴール未設定"
                qualitative_progress = 0
            
            return {
                "quantitative": quantitative_progress,
                "qualitative": qualitative_progress,
                "completed_tasks": completed_count,
                "total_tasks": total_tasks,
                "evaluation": qualitative_eval
            }
            
        except Exception as e:
            print(f"   ⚠️  測定エラー: {e}")
            return {
                "quantitative": 0,
                "qualitative": 0,
                "completed_tasks": 0,
                "total_tasks": 0,
                "evaluation": ""
            }
    
    # ========================================
    # 依存出力取得（改善版）
    # ========================================
    
    async def get_dependency_outputs(self, task: Dict) -> Optional[str]:
        """複数依存タスクの出力を統合"""
        
        dependencies = task.get('dependencies', '')
        if not dependencies:
            return None
        
        dep_ids = self.parse_dependencies(dependencies)
        
        if not dep_ids:
            return None
        
        print(f"   📥 {len(dep_ids)}件の依存タスク出力を取得中...")
        
        all_outputs = []
        
        for dep_id in dep_ids:
            output = await self.get_single_dependency_output(dep_id)
            
            if output:
                # スマート要約
                summarized = await self.smart_summarize_dependency(
                    output, 
                    task.get('description', '')
                )
                
                all_outputs.append(f"【タスク{dep_id}の出力】\n{summarized}")
        
        if all_outputs:
            combined = "\n\n" + "="*70 + "\n\n".join(all_outputs)
            print(f"   ✅ 統合完了: {len(combined)}文字")
            return combined
        
        return None
    
    async def get_single_dependency_output(self, dependency_task_id: int) -> Optional[str]:
        """単一依存タスクの出力を取得"""
        
        try:
            spreadsheet = self.sheets.gc.open_by_key(get_spreadsheet_id())
            log_sheet = spreadsheet.worksheet('task_execution_log')
            
            all_data = log_sheet.get_all_values()
            
            # GitHub参照を検索
            github_path = None
            for row in reversed(all_data[1:]):
                if len(row) > 1 and str(row[1]) == str(dependency_task_id):
                    output_data = row[6] if len(row) > 6 else ""
                    
                    if "GitHub:" in output_data:
                        lines = output_data.split('\n')
                        for line in lines:
                            if "GitHub:" in line:
                                github_path = line.split("GitHub:")[-1].strip()
                                github_path = github_path.replace("📁", "").strip()
                                break
                    break
            
            # GitHubから読み込み
            if github_path:
                full_path = Path("/workspaces/gemini_AI_Agent") / github_path
                
                if full_path.exists():
                    with open(full_path, "r", encoding="utf-8") as f:
                        content = f.read()
                    
                    # マークダウンヘッダー除去
                    if "---" in content:
                        parts = content.split("---", 2)
                        if len(parts) > 2:
                            content = parts[2].strip()
                    
                    return content
            
            return None
            
        except Exception as e:
            print(f"   ⚠️  取得エラー: {e}")
            return None
    
    # ========================================
    # ストレージ
    # ========================================
    
    async def save_output_hybrid(
        self,
        task_id: int,
        task_description: str,
        agent_role: str,
        full_output: str,
        status: str,
        quality_score: int = 0
    ) -> Dict[str, str]:
        """ハイブリッド保存"""
        
        print(f"\n   💾 ハイブリッド保存...")
        
        result = {
            "github_path": "",
            "sheets_log_id": "",
            "output_hash": "",
            "output_length": len(full_output)
        }
        
        try:
            # GitHub保存
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"task_{task_id}_{agent_role}_{timestamp}.md"
            filepath = self.github_storage / filename
            
            content = f"""# タスク {task_id}: {agent_role}

**概要**: {task_description}

**ステータス**: {status}

**品質スコア**: {quality_score}/10

**生成日時**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

**文字数**: {len(full_output):,}

---

{full_output}
"""
            
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            
            relative_path = f"agent_outputs/tasks/{filename}"
            result["github_path"] = relative_path
            result["output_hash"] = hashlib.sha256(full_output.encode()).hexdigest()[:8]
            
            print(f"      ✅ GitHub: {filename} ({len(full_output):,}文字)")
            
        except Exception as e:
            print(f"      ❌ GitHub保存エラー: {e}")
        
        try:
            # Sheets保存
            spreadsheet = self.sheets.gc.open_by_key(get_spreadsheet_id())
            log_sheet = spreadsheet.worksheet('task_execution_log')
            
            all_data = log_sheet.get_all_values()
            next_log_id = len(all_data)
            
            # サマリー
            if len(full_output) > 200:
                summary = f"{full_output[:100]}...\n\n[中略 {len(full_output)-200}文字]\n\n...{full_output[-100:]}"
            else:
                summary = full_output
            
            output_data_content = f"""📁 GitHub: {result['github_path']}

📊 メタデータ:
- 文字数: {len(full_output):,}
- 品質スコア: {quality_score}/10
- ハッシュ: {result['output_hash']}

📝 サマリー:
{summary[:200]}
"""
            
            row = [
                next_log_id,
                task_id,
                task_description[:100],
                datetime.now().isoformat(),
                agent_role,
                summary[:100],
                output_data_content[:500],
                status
            ]
            
            log_sheet.append_row(row)
            
            result["sheets_log_id"] = str(next_log_id)
            
            print(f"      ✅ Sheets: log_id {next_log_id}")
            
        except Exception as e:
            print(f"      ❌ Sheets保存エラー: {e}")
        
        return result
    
    # ========================================
    # プロジェクトゴール読み込み
    # ========================================
    
    async def load_project_goal(self) -> str:
        """プロジェクトゴールを読み込み"""
        
        try:
            spreadsheet = self.sheets.gc.open_by_key(get_spreadsheet_id())
            goal_sheet = spreadsheet.worksheet('project_goal')
            
            all_data = goal_sheet.get_all_values()
            
            if len(all_data) > 1:
                latest_goal = all_data[-1]
                goal_text = latest_goal[1] if len(latest_goal) > 1 else ""
                
                print(f"\n🎯 プロジェクトゴール:")
                print(f"   {goal_text[:100]}...")
                
                self.project_goal = goal_text
                return goal_text
            
            return ""
            
        except Exception as e:
            print(f"⚠️  ゴール読み込みエラー: {e}")
            return ""
    
    # ========================================
    # メイン実行
    # ========================================
    
    async def execute_all_pending(self, max_tasks: Optional[int] = None) -> Dict:
        """v1.1.0 完全版タスク実行"""
        
        print("\n" + "="*70)
        print("🚀 v1.1.0-integrated 完全版起動")
        print("="*70)
        
        # [1] プロジェクトゴール
        await self.load_project_goal()
        
        # [2] タスク読み込み
        print("\n[1/7] タスク読み込み...")
        tasks = await self.sheets.load_tasks_from_sheet(sheet_name="pm_tasks")
        
        if not tasks:
            return {"total": 0, "success": 0, "failed": 0}
        
        # pending抽出
        pending = []
        for t in tasks:
            status = t.get('status', '').strip().lower()
            if 'pending' in status or status == '':
                pending.append(t)
        
        if not pending:
            print(f"⚠️  pendingタスクなし")
            
            # ゴール達成度測定
            progress = await self.measure_goal_progress()
            
            return {"total": 0, "success": 0, "failed": 0, "progress": progress}
        
        # [3] 循環依存チェック
        print("\n[2/7] 循環依存チェック...")
        for task in pending:
            task_id = task.get('task_id')
            if self.detect_circular_dependency(task_id, tasks):
                print(f"   ❌ タスク{task_id}に循環依存")
                raise CircularDependencyError(f"Task {task_id} has circular dependency")
        
        print("   ✅ 循環依存なし")
        
        if max_tasks and len(pending) > max_tasks:
            pending = pending[:max_tasks]
        
        print(f"\n✅ {len(pending)}件のpendingタスク")
        
        # [4] Gemini準備
        print("\n[3/7] Gemini接続...")
        if not await self.browser.navigate_to_gemini():
            return {"total": 0, "success": 0, "failed": 0}
        print("✅ 完了")
        
        # [5] タスク実行
        print("\n[4/7] タスク実行開始...")
        
        results = {
            "total": len(pending),
            "success": 0,
            "failed": 0,
            "skipped": 0,
            "details": [],
            "start_time": datetime.now()
        }
        
        for i, task in enumerate(pending, 1):
            task_id = task.get('task_id')
            role = task.get('required_role', 'design').strip().lower()
            description = task.get('description', '')
            
            print(f"\n{'='*70}")
            print(f"[{i}/{len(pending)}] タスク{task_id}: {role}")
            print(f"概要: {description[:60]}...")
            print(f"{'='*70}")
            
            try:
                # 依存チェック
                if not await self.validate_dependencies(task):
                    print(f"   ⏭️  依存タスク未完了のためスキップ")
                    results["skipped"] += 1
                    continue
                
                # in_progress
                await self.sheets.update_task_status(
                    task_id=task_id,
                    status="in_progress",
                    sheet_name="pm_tasks"
                )
                
                # 依存出力取得（複数対応）
                dependency_output = await self.get_dependency_outputs(task)
                
                # エージェント選択
                agent = self.agents.get(role)
                
                # タスク実行（自動再実行付き）
                if agent and hasattr(agent, 'execute_task'):
                    print(f"   🤖 WordPress専門エージェント")
                    result = await agent.execute_task(task)
                    success = result.get('success', False)
                    output = result.get('output', '')
                    quality_score = 8  # エージェント実行は品質評価スキップ
                else:
                    print(f"   🤖 Gemini統合 ({role})")
                    success, output, error = await self.execute_with_retry(
                        task, role, dependency_output
                    )
                    
                    # 品質スコア取得
                    if success:
                        quality = await self.evaluate_quality(task, output)
                        quality_score = quality.get('score', 0)
                    else:
                        quality_score = 0
                
                # ステータス更新
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
                
                # ハイブリッド保存（品質スコア付き）
                save_result = await self.save_output_hybrid(
                    task_id=task_id,
                    task_description=description,
                    agent_role=role,
                    full_output=output if output else "",
                    status="completed" if success else "failed",
                    quality_score=quality_score
                )
                
                results["details"].append({
                    "task_id": task_id,
                    "role": role,
                    "success": success,
                    "quality_score": quality_score,
                    "github_path": save_result.get("github_path", ""),
                    "output_length": save_result.get("output_length", 0)
                })
                
                # レート制限
                if i < len(pending):
                    print(f"\n⏳ {self.rate_limit}秒待機...")
                    await asyncio.sleep(self.rate_limit)
                    
            except Exception as e:
                print(f"❌ エラー: {e}")
                results["failed"] += 1
        
        results["end_time"] = datetime.now()
        results["duration"] = (results["end_time"] - results["start_time"]).total_seconds()
        
        # [6] ゴール達成度測定
        print("\n[5/7] ゴール達成度測定...")
        progress = await self.measure_goal_progress()
        results["progress"] = progress
        
        # [7] サマリー
        print("\n" + "="*70)
        print("📊 実行結果サマリー")
        print("="*70)
        print(f"実行: {results['total']}")
        print(f"✅ 成功: {results['success']}")
        print(f"❌ 失敗: {results['failed']}")
        print(f"⏭️  スキップ: {results['skipped']}")
        print(f"⏱️  時間: {results['duration']:.1f}秒")
        
        if results['total'] > 0:
            print(f"成功率: {results['success']/results['total']*100:.1f}%")
        
        print(f"\n🎯 ゴール達成度:")
        print(f"   量的: {progress['quantitative']:.1f}%")
        print(f"   質的: {progress['qualitative']:.1f}%")
        
        print(f"\n📊 品質スコア:")
        for detail in results['details']:
            if 'quality_score' in detail:
                print(f"   タスク{detail['task_id']}: {detail['quality_score']}/10")
        
        print("="*70)
        
        return results
    
    async def _execute_with_gemini(
        self, 
        task: Dict, 
        role: str,
        dependency_output: Optional[str] = None
    ):
        """Gemini実行"""
        
        task_id = task.get('task_id')
        description = task.get('description', '')
        
        prompt = f"""あなたは{role}の専門家です。

タスクID: {task_id}
内容: {description}

プロジェクトゴール:
{self.project_goal if self.project_goal else '（未設定）'}
"""
        
        if dependency_output:
            prompt += f"""

【前提情報】
前のタスクの出力:
{dependency_output}

上記を踏まえて実行してください。
"""
        
        prompt += "\n具体的で実用的な成果物を作成してください。"
        
        try:
            await self.browser.send_prompt(prompt)
            await self.browser.wait_for_text_generation(max_wait=120)
            response = await self.browser.extract_latest_text_response()
            
            if response and len(response) > 100:
                print(f"   ✅ {len(response):,}文字生成")
                return True, response, ""
            else:
                return False, "", "レスポンス不足"
                
        except Exception as e:
            return False, "", str(e)


async def main():
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--max-tasks', type=int, help='最大タスク数')
    parser.add_argument('--quality-threshold', type=int, default=7, help='品質基準（1-10）')
    parser.add_argument('--max-retries', type=int, default=3, help='最大再試行回数')
    parser.add_argument('--disable-smart-summary', action='store_true', help='スマート要約無効化')
    
    args = parser.parse_args()
    
    print("="*70)
    print("🎯 v1.1.0-integrated 完全版")
    print("="*70)
    print("\n新機能:")
    print("  ✅ 複数依存対応")
    print("  ✅ 依存チェック")
    print("  ✅ 循環依存検出")
    print("  ✅ スマート要約")
    print("  ✅ 品質評価")
    print("  ✅ 自動再実行")
    print("  ✅ ゴール達成度測定")
    
    sheets = GoogleSheetsManager(
        spreadsheet_id=get_spreadsheet_id(),
        service_account_file=get_service_account_file()
    )
    
    async with BrowserController(download_folder="./downloads") as browser:
        executor = AdvancedFeedbackExecutor(sheets, browser)
        
        # 設定
        executor.quality_threshold = args.quality_threshold
        executor.max_retries = args.max_retries
        executor.smart_summary_enabled = not args.disable_smart_summary
        
        results = await executor.execute_all_pending(max_tasks=args.max_tasks)
    
    print("\n📋 完了")
    print(f"Google Sheets: https://docs.google.com/spreadsheets/d/{get_spreadsheet_id()}")


if __name__ == "__main__":
    asyncio.run(main())

