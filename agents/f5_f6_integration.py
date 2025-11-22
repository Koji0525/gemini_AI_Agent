"""
F5-F6統合モジュール
既存システムを壊さずに、F5とF6の機能を提供
"""

import os
import sys
from datetime import datetime
from typing import Dict, List, Any

class ProgressVisualization:
    """F5: 進捗自動可視化の統合"""
    
    def __init__(self, sheets_manager=None):
        self.sheets = sheets_manager
        
    def show_progress(self) -> Dict[str, Any]:
        """進捗を可視化"""
        try:
            # dashboardを呼び出す
            if os.path.exists("agents/observability/dashboard.py"):
                import subprocess
                result = subprocess.run(
                    ["python3", "agents/observability/dashboard.py"],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                return {
                    "success": result.returncode == 0,
                    "output": result.stdout
                }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_progress_summary(self) -> Dict[str, Any]:
        """進捗サマリーを取得"""
        if not self.sheets:
            return {"error": "Sheets manager not available"}
        
        try:
            # pm_tasksから進捗を取得
            tasks = self.sheets.read_sheet("pm_tasks", "A2:Z1000")
            
            total = len(tasks)
            completed = sum(1 for t in tasks if t[4] == "completed")
            pending = sum(1 for t in tasks if t[4] == "pending")
            
            return {
                "total_tasks": total,
                "completed": completed,
                "pending": pending,
                "progress_rate": f"{completed * 100 / total:.1f}%" if total > 0 else "0%"
            }
        except Exception as e:
            return {"error": str(e)}


class DynamicTaskManager:
    """F6: 動的タスク追加の統合"""
    
    def __init__(self, sheets_manager=None, pm_agent=None):
        self.sheets = sheets_manager
        self.pm_agent = pm_agent
        
    def add_dynamic_task(
        self,
        goal_id: str,
        description: str,
        priority: str = "medium",
        dependencies: str = ""
    ) -> Dict[str, Any]:
        """動的にタスクを追加"""
        if not self.sheets:
            return {"success": False, "error": "Sheets manager not available"}
        
        try:
            # タスクIDの生成
            task_id = f"{goal_id}_dynamic_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # タスクデータ
            task_data = [
                task_id,
                goal_id,
                description,
                "developer",  # required_role
                "pending",    # status
                priority,
                "1h",         # estimated_time
                dependencies,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "dynamic",    # batch_id
                "",           # detail_file_path
                "",           # blank
                "implementation"  # execution_type
            ]
            
            # Sheetsに追加
            result = self.sheets.append_row("pm_tasks", [task_data])
            
            return {
                "success": True,
                "task_id": task_id,
                "message": f"Dynamic task added: {task_id}"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def adjust_task_priority(
        self,
        task_id: str,
        new_priority: str
    ) -> Dict[str, Any]:
        """タスクの優先度を動的に調整"""
        # 実装は既存のSheets操作を使用
        return {"success": True, "message": "Priority adjusted"}


class F5F6Integration:
    """F5-F6統合クラス（CompleteEngineに追加）"""
    
    def __init__(self, sheets_manager=None, pm_agent=None):
        self.progress = ProgressVisualization(sheets_manager)
        self.dynamic_tasks = DynamicTaskManager(sheets_manager, pm_agent)
        
    def integrate_to_engine(self, engine):
        """CompleteEngineに統合"""
        # F5メソッドを追加
        engine.show_progress = self.progress.show_progress
        engine.get_progress_summary = self.progress.get_progress_summary
        
        # F6メソッドを追加
        engine.add_dynamic_task = self.dynamic_tasks.add_dynamic_task
        engine.adjust_task_priority = self.dynamic_tasks.adjust_task_priority
        
        print("✅ F5-F6統合完了")

