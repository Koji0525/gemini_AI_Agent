import asyncio
from typing import Dict, List
from tools.sheets_manager import GoogleSheetsManager

class ExecutionDataAnalyzer:
    """実行データ分析専門クラス"""
    
    def __init__(self, sheets_manager):
        self.sheets_manager = sheets_manager
    
    async def get_recent_executions(self, days=7):
        """最近の実行データを取得"""
        try:
            spreadsheet = self.sheets_manager.gc.open_by_key(self.sheets_manager.spreadsheet_id)
            log_sheet = spreadsheet.worksheet('task_execution_log')
            logs = log_sheet.get_all_records()
            
            # 日付でフィルタリング（簡易版）
            recent_logs = logs[-50:] if len(logs) > 50 else logs  # 最新50件
            return recent_logs
            
        except Exception as e:
            print(f"実行データ取得エラー: {e}")
            return []
    
    def analyze_task_success_patterns(self, logs):
        """タスク成功のパターンを分析"""
        analysis = {
            "by_agent": {},
            "by_time": {},
            "common_success_factors": []
        }
        
        successful_tasks = [log for log in logs if log.get('result_status') == 'success']
        
        # エージェント別の成功率
        agents = {}
        for log in logs:
            agent = log.get('assigned_agent', 'unknown')
            if agent not in agents:
                agents[agent] = {'total': 0, 'success': 0}
            agents[agent]['total'] += 1
            if log.get('result_status') == 'success':
                agents[agent]['success'] += 1
        
        for agent, stats in agents.items():
            if stats['total'] > 0:
                analysis['by_agent'][agent] = {
                    'success_rate': stats['success'] / stats['total'],
                    'total_tasks': stats['total']
                }
        
        return analysis

async def test_analyzer():
    """アナライザーのテスト"""
    sheets = GoogleSheetsManager()
    analyzer = ExecutionDataAnalyzer(sheets)
    
    logs = await analyzer.get_recent_executions()
    print(f"取得したログ数: {len(logs)}")
    
    analysis = analyzer.analyze_task_success_patterns(logs)
    print("分析結果:")
    print(json.dumps(analysis, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    asyncio.run(test_analyzer())
