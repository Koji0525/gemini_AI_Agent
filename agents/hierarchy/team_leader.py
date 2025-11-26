#!/usr/bin/env python3
"""
Team Leader - 階層型組織の中間管理職

役割: 担当領域のタスク管理、ワーカー割り当て、進捗監視
"""

import sys
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from agents.integration.shared_blackboard_manager import SharedBlackboardManager
from agents.planning.task_splitter import TaskSplitter

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class TeamLeader:
    """Team Leader - チームリーダー"""
    
    def __init__(self, team_name: str, goal_id: str):
        self.team_name = team_name
        self.goal_id = goal_id
        self.blackboard = SharedBlackboardManager(goal_id)
        self.workers = {}
        self.task_splitter = TaskSplitter()
        logger.info(f"TeamLeader初期化: team={team_name}, goal={goal_id}")
    
    def receive_mission(self) -> Optional[Dict]:
        """Executive Managerからミッションを受領"""
        logger.info(f"ミッション受領: {self.team_name}")
        try:
            org_structure = self.blackboard.read_section('organization')
            if not org_structure:
                logger.warning("組織構造が未定義です")
                return None
            
            teams = org_structure.get('teams', {})
            mission = teams.get(self.team_name)
            
            if mission:
                logger.info(f"ミッション受領成功: {mission['mission']}")
            else:
                logger.warning(f"チーム{self.team_name}のミッションが見つかりません")
            
            return mission
        except Exception as e:
            logger.error(f"ミッション受領エラー: {e}")
            return None
    
    def break_down_mission(self, mission: Dict) -> List[Dict]:
        """ミッションを具体的なタスクに分解"""
        logger.info(f"ミッション分解: {mission['mission']}")
        mission_text = mission['mission']
        tasks = []
        keywords = ['収集', '整形', '検証', '分析', '評価', 'レポート']
        
        for i, keyword in enumerate(keywords):
            if keyword in mission_text:
                task = {
                    'task_id': f"{self.team_name}_task_{i+1:03d}",
                    'title': f"{keyword}タスク",
                    'description': f"{mission_text}の一環として{keyword}を実行",
                    'estimated_hours': 2,
                    'priority': mission.get('priority', 'medium'),
                    'status': 'pending',
                    'assigned_to': None,
                    'created_at': datetime.now().isoformat()
                }
                tasks.append(task)
        
        if not tasks:
            tasks.append({
                'task_id': f"{self.team_name}_task_001",
                'title': "ミッション実行",
                'description': mission_text,
                'estimated_hours': 3,
                'priority': mission.get('priority', 'medium'),
                'status': 'pending',
                'assigned_to': None,
                'created_at': datetime.now().isoformat()
            })
        
        logger.info(f"ミッション分解完了: {len(tasks)}タスク")
        return tasks
    
    def assign_tasks_to_workers(self, tasks: List[Dict], workers: List[str]) -> Dict[str, List[Dict]]:
        """タスクをワーカーに割り当て"""
        logger.info(f"タスク割り当て: {len(tasks)}タスク → {len(workers)}ワーカー")
        assignments = {worker: [] for worker in workers}
        sorted_tasks = sorted(tasks, key=lambda t: {'high': 3, 'medium': 2, 'low': 1}.get(t['priority'], 0), reverse=True)
        
        for i, task in enumerate(sorted_tasks):
            worker = workers[i % len(workers)]
            task['assigned_to'] = worker
            assignments[worker].append(task)
        
        for worker, assigned_tasks in assignments.items():
            total_hours = sum(t['estimated_hours'] for t in assigned_tasks)
            logger.info(f"   {worker}: {len(assigned_tasks)}タスク（{total_hours}時間）")
        
        self.workers = assignments
        return assignments
    
    def monitor_team_progress(self) -> Dict:
        """チーム内の進捗を監視"""
        logger.info(f"チーム進捗監視: {self.team_name}")
        try:
            team_section = self.blackboard.read_section(self.team_name)
            if not team_section:
                logger.warning(f"チームセクション未作成: {self.team_name}")
                return self._empty_team_progress()
            
            worker_statuses = {}
            blockers = []
            quality_issues = []
            
            for worker_id, tasks in self.workers.items():
                completed = sum(1 for t in tasks if t['status'] == 'completed')
                total = len(tasks)
                worker_status = {
                    'progress': (completed / total * 100) if total > 0 else 0,
                    'tasks_total': total,
                    'tasks_completed': completed,
                    'status': 'active'
                }
                worker_statuses[worker_id] = worker_status
                
                blocked = [t for t in tasks if t['status'] == 'blocked']
                if blocked:
                    blockers.extend(blocked)
                
                low_quality = [t for t in tasks if t.get('quality_score', 100) < 60]
                if low_quality:
                    quality_issues.extend(low_quality)
            
            all_tasks = [t for tasks in self.workers.values() for t in tasks]
            overall_progress = (
                sum(1 for t in all_tasks if t['status'] == 'completed') / len(all_tasks) * 100
                if all_tasks else 0
            )
            
            result = {
                'team_name': self.team_name,
                'overall_progress': round(overall_progress, 1),
                'worker_statuses': worker_statuses,
                'blockers': blockers,
                'quality_issues': quality_issues,
                'monitored_at': datetime.now().isoformat()
            }
            logger.info(f"チーム進捗: {result['overall_progress']}%")
            return result
        except Exception as e:
            logger.error(f"チーム進捗監視エラー: {e}")
            return self._empty_team_progress()
    
    def report_to_executive(self, progress: Dict) -> Dict:
        """Executive Managerに進捗報告"""
        logger.info(f"進捗報告: {self.team_name} → Executive Manager")
        report = {
            'from': self.team_name,
            'to': 'executive_manager',
            'type': 'progress_report',
            'timestamp': datetime.now().isoformat(),
            'content': {
                'progress': progress['overall_progress'],
                'blockers_count': len(progress['blockers']),
                'quality_issues_count': len(progress['quality_issues']),
                'workers': len(progress['worker_statuses'])
            }
        }
        
        try:
            reports_section = self.blackboard.read_section('reports') or {}
            reports_section[self.team_name] = report
            success = self.blackboard.write_section('reports', reports_section)
            if success:
                logger.info("進捗報告成功")
            else:
                logger.warning("進捗報告失敗")
        except Exception as e:
            logger.error(f"進捗報告エラー: {e}")
        
        return report
    
    def escalate_issue(self, issue: Dict) -> Dict:
        """Executive Managerに問題をエスカレーション"""
        logger.info(f"エスカレーション: {issue.get('type')}")
        escalation = {
            'from': self.team_name,
            'to': 'executive_manager',
            'type': 'escalation',
            'priority': 'high',
            'timestamp': datetime.now().isoformat(),
            'issue': issue
        }
        
        try:
            escalations = self.blackboard.read_section('escalations') or []
            escalations.append(escalation)
            self.blackboard.write_section('escalations', escalations)
            logger.info("エスカレーション成功")
        except Exception as e:
            logger.error(f"エスカレーションエラー: {e}")
        
        return escalation
    
    def _empty_team_progress(self) -> Dict:
        return {
            'team_name': self.team_name,
            'overall_progress': 0,
            'worker_statuses': {},
            'blockers': [],
            'quality_issues': [],
            'monitored_at': datetime.now().isoformat()
        }


def main():
    print("=" * 60)
    print("👨‍💼 TeamLeader テスト")
    print("=" * 60)
    
    test_team = "team_data"
    test_goal = "test_goal_team"
    
    try:
        print("\n[1/5] TeamLeader初期化...")
        leader = TeamLeader(test_team, test_goal)
        print(f"   ✅ 初期化成功: {test_team}")
        
        print("\n[2/5] ミッション受領...")
        mock_mission = {
            'mission': 'データ収集・整形・検証',
            'priority': 'high',
            'members_count': 3
        }
        print(f"   ミッション: {mock_mission['mission']}")
        
        print("\n[3/5] ミッション分解...")
        tasks = leader.break_down_mission(mock_mission)
        print(f"   生成タスク数: {len(tasks)}")
        for task in tasks[:3]:
            print(f"   - {task['task_id']}: {task['title']}")
        
        print("\n[4/5] ワーカー割り当て...")
        mock_workers = ['worker_a1', 'worker_a2', 'worker_a3']
        assignments = leader.assign_tasks_to_workers(tasks, mock_workers)
        print(f"   割り当て完了: {len(mock_workers)}ワーカー")
        for worker, assigned_tasks in assignments.items():
            print(f"   - {worker}: {len(assigned_tasks)}タスク")
        
        print("\n[5/5] チーム進捗監視...")
        progress = leader.monitor_team_progress()
        print(f"   チーム進捗: {progress['overall_progress']}%")
        print(f"   ワーカー数: {len(progress['worker_statuses'])}")
        print(f"   ブロッカー: {len(progress['blockers'])}件")
        
        print("\n" + "=" * 60)
        print("✅ テスト完了")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ エラー: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
