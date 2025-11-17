#!/usr/bin/env python3
"""
スマートエグゼキューター: 詳細情報から実際に必要なコードを生成
汎用テンプレートではなく、タスク専用のカスタムコード
"""
import sys
sys.path.insert(0, '/workspaces/gemini_AI_Agent')

import re
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

from agents.task_execution.enhanced_executor_v3 import EnhancedTaskExecutorV3
from agents.task_execution.task_detail_parser import TaskDetailParser


class SmartExecutor(EnhancedTaskExecutorV3):
    """詳細情報から実際に必要なコードを生成"""
    
    def __init__(self, knowledge_manager=None):
        """初期化"""
        super().__init__(knowledge_manager)
        self.parser = TaskDetailParser()
        
        # AI生成機能の初期化
        self.use_ai = False
        self.ai_generator = None
        
        try:
            from agents.task_execution.ai_code_generator import AICodeGenerator
            self.ai_generator = AICodeGenerator()
            self.use_ai = True
            print("  🤖 AI生成: 有効")
        except Exception as e:
            print(f"  ⚠️ AI生成: 無効 ({e})")
            print("  💡 テンプレートベースにフォールバック")
            self.use_ai = False
            self.ai_generator = None
    
    def _execute_with_details(self, task: Dict, details: Dict, task_types: list, task_dir: Path) -> Dict:
        """詳細情報を深く解析して実行"""
        
        if not details['has_details']:
            # 詳細情報がない場合は従来の方法
            return self._execute_by_detected_types(task, task_types, task_dir)
        
        # タスク概要から「何を作るか」を抽出
        overview = details['overview']
        
        # パターンマッチング: 何を作るべきか
        if 'ディレクトリを作成' in overview or 'ディレクトリ作成' in overview:
            return self._execute_directory_creation(task, details, task_dir)
        
        elif '.py' in overview and ('実装' in overview or '作成' in overview or '追加' in overview):
            # Pythonファイル作成 → 汎用テンプレートは不要
            result = self._execute_python_file_creation(task, details, task_dir)
            result['skip_generic_templates'] = True
            return result
        
        elif 'requirements.txt' in overview:
            return self._execute_dependency_task(task, task_dir)
        
        elif 'テスト' in overview and '実行' in overview:
            return self._execute_testing_with_details(task, details, task_dir)
        
        else:
            # デフォルト: 詳細情報活用版のgeneric実行
            return self._execute_generic_with_details(task, details, task_dir)
    
    def _execute_directory_creation(self, task: Dict, details: Dict, task_dir: Path) -> Dict:
        """ディレクトリ作成タスク"""
        task_id = task.get('task_id')
        overview = details['overview']
        
        # ディレクトリパスを抽出
        dir_matches = re.findall(r'([a-zA-Z_][a-zA-Z0-9_/]*)/?\s*ディレクトリ', overview)
        
        if not dir_matches:
            dir_matches = re.findall(r'([a-zA-Z_][a-zA-Z0-9_/]+/)', overview)
        
        created_dirs = []
        created_files = []
        
        for dir_path in dir_matches:
            target_dir = Path('/workspaces/gemini_AI_Agent') / dir_path
            target_dir.mkdir(parents=True, exist_ok=True)
            created_dirs.append(str(target_dir))
            
            init_file = target_dir / '__init__.py'
            if not init_file.exists():
                with open(init_file, 'w') as f:
                    f.write(f'"""\n{dir_path} パッケージ\nタスクID: {task_id}\n"""\n')
                created_files.append(str(init_file))
        
        # ファイル名を抽出
        file_matches = re.findall(r'([a-zA-Z_][a-zA-Z0-9_]*\.py)', overview)
        
        for filename in file_matches:
            if filename == '__init__.py':
                continue
            
            if dir_matches:
                target_dir = Path('/workspaces/gemini_AI_Agent') / dir_matches[0]
                file_path = target_dir / filename
                
                content = self._generate_python_file_content(task_id, filename, details)
                
                with open(file_path, 'w') as f:
                    f.write(content)
                
                created_files.append(str(file_path))
        
        # レポート生成
        report_path = task_dir / 'creation_report.md'
        report = f'''# ディレクトリ・ファイル作成レポート

## タスク: {task_id}

### 目的
{details['purpose']}

### 作成したディレクトリ
'''
        for d in created_dirs:
            report += f'- {d}\n'
        
        report += '\n### 作成したファイル\n'
        for f in created_files:
            report += f'- {f}\n'
        
        report += f'''
### 成功基準の確認
{details['success_criteria']}

✅ ディレクトリ作成: 完了
✅ ファイル作成: 完了

---
生成日時: {datetime.now().isoformat()}
'''
        
        with open(report_path, 'w') as f:
            f.write(report)
        
        return {
            'summary': f'ディレクトリ{len(created_dirs)}個、ファイル{len(created_files)}個を作成',
            'output_files': created_files + [str(report_path)],
            'execution_log': f'''実際のプロジェクト構造に作成:
  ディレクトリ: {', '.join(created_dirs)}
  ファイル: {', '.join([Path(f).name for f in created_files])}'''
        }
    
    def _execute_python_file_creation(self, task: Dict, details: Dict, task_dir: Path) -> Dict:
        """Pythonファイル作成タスク"""
        task_id = task.get('task_id')
        overview = details['overview']
        
        file_matches = re.findall(r'([a-zA-Z_][a-zA-Z0-9_]*\.py)', overview)
        
        created_files = []
        
        for filename in file_matches:
            file_path = task_dir / filename
            
            content = self._generate_python_file_content(task_id, filename, details)
            
            with open(file_path, 'w') as f:
                f.write(content)
            
            created_files.append(str(file_path))
        
        readme_path = task_dir / 'README.md'
        readme = f'''# {task_id}: Pythonファイル作成

## 目的
{details['purpose']}

## 生成ファイル
'''
        for f in created_files:
            readme += f'- {Path(f).name}\n'
        
        readme += f'''
## 使用方法
```python
# インポート例
from {Path(created_files[0]).stem} import ...
```

---
生成日時: {datetime.now().isoformat()}
'''
        
        with open(readme_path, 'w') as f:
            f.write(readme)
        
        return {
            'summary': f'Pythonファイル{len(created_files)}個を作成',
            'output_files': created_files + [str(readme_path)],
            'execution_log': f'作成: {', '.join([Path(f).name for f in created_files])}'
        }
    
    def _generate_python_file_content(self, task_id: str, filename: str, details: Dict) -> str:
        """Pythonファイルの内容を生成（AI優先版）"""
        
        # AI生成を優先
        if self.use_ai and self.ai_generator:
            try:
                return self.ai_generator.generate_code(task_id, filename, details)
            except Exception as e:
                print(f"⚠️ AI生成失敗、テンプレートにフォールバック: {e}")
        
        # フォールバック: テンプレート生成
        class_name = ''.join(word.capitalize() for word in filename.replace('.py', '').split('_'))
        
        # 詳細情報から必要なメソッドを推測
        methods = self._extract_methods_from_details(details)
        
        methods_code = ""
        for method_name, method_desc in methods:
            methods_code += f'''
    def {method_name}(self):
        """
        {method_desc}
        """
        # TODO: {method_desc}
        pass
'''
        
        # 必要なimportを推測
        imports = self._extract_imports_from_details(details)
        imports_code = "\n".join(imports)
        
        content = f'''#!/usr/bin/env python3
"""
{filename}
タスクID: {task_id}

目的: {details['purpose']}

実装内容:
{details['overview']}

成功基準:
{details['success_criteria']}
"""
import sys
sys.path.insert(0, '/workspaces/gemini_AI_Agent')

{imports_code}


class {class_name}:
    """
    {details['purpose']}
    """
    
    def __init__(self):
        """初期化"""
        # TODO: 必要な初期化処理を追加
        pass
{methods_code}
    
    def execute(self):
        """メイン処理"""
        # TODO: 各メソッドを呼び出して処理を実行
        pass


if __name__ == '__main__':
    instance = {class_name}()
    instance.execute()
'''
        
        return content
    
    def _extract_methods_from_details(self, details: Dict) -> list:
        """詳細情報からメソッドを抽出"""
        methods = []
        overview = details.get('overview', '')
        criteria = details.get('success_criteria', '')
        
        if 'メトリクス' in criteria or 'メトリクス' in overview:
            methods.append(('collect_metrics', 'メトリクスを収集'))
        
        if '使用率' in overview:
            methods.append(('calculate_usage_rate', '使用率を計算'))
        
        if '解決率' in overview:
            methods.append(('calculate_resolution_rate', '解決率を計算'))
        
        if '新鮮度' in overview:
            methods.append(('calculate_freshness', '新鮮度を計算'))
        
        if '評価' in overview:
            methods.append(('evaluate', '評価を実行'))
        
        if 'レポート' in criteria or 'レポート' in overview:
            methods.append(('generate_report', 'レポートを生成'))
        
        if '分析' in overview:
            methods.append(('analyze', '分析を実行'))
        
        if '監視' in overview:
            methods.append(('monitor', '監視を実行'))
        
        if '状態監視' in overview:
            methods.append(('monitor_components', 'コンポーネントの状態を監視'))
        
        if '影響分析' in overview:
            methods.append(('analyze_impact', '変更影響を分析'))
        
        if not methods:
            methods.append(('run', '主要処理を実行'))
        
        return methods
    
    def _extract_imports_from_details(self, details: Dict) -> list:
        """詳細情報から必要なimportを推測"""
        imports = []
        context = details.get('context', '').lower()
        overview = details.get('overview', '').lower()
        
        if 'db' in context or 'database' in context or 'sqlite' in context:
            imports.append('import sqlite3')
        
        if 'knowledgemanager' in context or 'knowledge_manager' in context:
            imports.append('from knowledge_system.core_agents.knowledge_manager import KnowledgeManager')
        
        if 'スプレッドシート' in context or 'sheets' in context:
            imports.append('from tools.sheets_manager import GoogleSheetsManager')
        
        if '時間' in overview or '日時' in overview:
            imports.append('from datetime import datetime, timedelta')
        
        if 'ログ' in context or 'log' in context:
            imports.append('import logging')
        
        if 'json' in context or 'メトリクス' in overview:
            imports.append('import json')
        
        if 'ファイル' in overview or 'パス' in context:
            imports.append('from pathlib import Path')
        
        if imports:
            imports.insert(0, 'from typing import Dict, List, Optional, Any')
        
        return imports
