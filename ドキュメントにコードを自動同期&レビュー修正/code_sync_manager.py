# code_sync_manager.py
import os
import json
from pathlib import Path
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class CodeSyncManager:
    """コード同期マネージャー - プログラムコードをGoogleドライブに保存"""
    
    def __init__(self, sheets_manager):
        self.sheets_manager = sheets_manager
        self.code_files = {
            'main': 'run_multi_agent.py',
            'task_executor': 'task_executor.py', 
            'pm_agent': 'pm_agent.py',
            'design_agent': 'design_agent.py',
            'review_agent': 'review_agent.py',
            'browser_controller': 'browser_controller.py',
            'sheets_manager': 'sheets_manager.py',
            'config': 'config_utils.py'
        }
    
    def read_current_code(self):
        """現在のコードを読み込む"""
        code_data = {}
        
        for agent_name, filename in self.code_files.items():
            try:
                file_path = Path(filename)
                if file_path.exists():
                    with open(file_path, 'r', encoding='utf-8') as f:
                        code_data[agent_name] = {
                            'content': f.read(),
                            'filename': filename,
                            'last_modified': datetime.now().isoformat(),
                            'size': len(f.read())
                        }
                    logger.info(f"✅ {agent_name} のコードを読み込み")
                else:
                    logger.warning(f"⚠️ {filename} が見つかりません")
            except Exception as e:
                logger.error(f"❌ {filename} 読み込みエラー: {e}")
        
        return code_data
    
    def save_code_to_drive(self, code_data):
        """コードをGoogleドライブに保存"""
        try:
            # コードをJSON形式でまとめる
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            drive_filename = f"agent_code_snapshot_{timestamp}.json"
            
            # 一時ファイルに保存
            temp_file = f"temp_{drive_filename}"
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(code_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"📁 コードスナップショットを作成: {drive_filename}")
            return True
            
        except Exception as e:
            logger.error(f"❌ コード保存エラー: {e}")
            return False
    
    def create_code_report(self, code_data):
        """コードの簡単な分析レポート作成"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_agents': len(code_data),
            'total_size': sum(data['size'] for data in code_data.values()),
            'agents': {}
        }
        
        for agent_name, data in code_data.items():
            report['agents'][agent_name] = {
                'filename': data['filename'],
                'size': data['size'],
                'lines': data['content'].count('\n') + 1
            }
        
        return report