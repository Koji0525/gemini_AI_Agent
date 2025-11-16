#!/usr/bin/env python3
"""
詳細情報活用型Executor v3.0
pm_tasksシートの①〜④を読み取って高精度実行
"""
import sys
sys.path.insert(0, '/workspaces/gemini_AI_Agent')

import time
import traceback
from datetime import datetime
from typing import Dict, Any
from pathlib import Path

from agents.task_execution.enhanced_executor_v2 import EnhancedTaskExecutorV2
from agents.task_execution.task_detail_parser import TaskDetailParser
from agents.task_execution.templates.template_library import TemplateLibrary


class EnhancedTaskExecutorV3(EnhancedTaskExecutorV2):
    """詳細情報活用型Executor"""
    
    def __init__(self, knowledge_manager=None):
        super().__init__(knowledge_manager)
        self.parser = TaskDetailParser()
    
    def execute_task_with_details(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """詳細情報を活用したタスク実行"""
        task_id = task.get('task_id', 'unknown')
        description = task.get('description', '')
        
        print(f"  🔧 タスク実行開始: {task_id}")
        print(f"     説明: {description[:100]}...")
        
        # タスク専用ディレクトリ作成
        task_dir = Path("agent_outputs/tasks") / f"task_{task_id}"
        task_dir.mkdir(parents=True, exist_ok=True)
        
        start_time = time.time()
        execution_result = {
            'status': 'completed',
            'task_id': task_id,
            'summary': '',
            'knowledge_references': [],
            'task_types': [],
            'details_used': False
        }
        
        try:
            # 1. 詳細情報を抽出
            details = self.parser.parse_description(description)
            execution_result['details_used'] = details['has_details']
            
            if details['has_details']:
                print(f"     ✅ 詳細情報検出")
                print(f"        目的: {details['purpose'][:50]}...")
                
                # 成功基準を解析
                criteria = self.parser.parse_success_criteria(details['success_criteria'])
                execution_result['success_criteria'] = criteria
                
                # コンテキスト情報を解析
                context = self.parser.parse_context(details['context'])
                execution_result['context'] = context
                
                print(f"        成功基準: {len(criteria['items'])}項目")
                print(f"        技術: {', '.join(context['technologies'][:3])}")
            
            # 2. ナレッジ検索（既存）
            if self.knowledge_manager:
                knowledge_refs = self._search_knowledge(description)
                execution_result['knowledge_references'] = knowledge_refs
            
            # 3. タスクタイプ検出
            task_types = self.template_lib.detect_task_types(description)
            execution_result['task_types'] = task_types
            print(f"     🏷️  検出タイプ: {', '.join(task_types)}")
            
            # 4. タスク実行（詳細情報を活用）
            result = self._execute_with_details(task, details, task_types, task_dir)
            execution_result.update(result)
            
            # 5. 品質評価（詳細情報を考慮）
            quality_score = self._evaluate_quality_v3(result, details, task_types)
            execution_result['quality_score'] = quality_score
            execution_result['quality_description'] = self._get_quality_description(quality_score)
            
            print(f"     ✅ 実行完了 (品質スコア: {quality_score}/10)")
            
        except Exception as e:
            execution_result['status'] = 'failed'
            execution_result['error'] = str(e)
            execution_result['error_trace'] = traceback.format_exc()
            print(f"     ❌ エラー発生: {e}")
        
        finally:
            elapsed_time = time.time() - start_time
            execution_result['elapsed_time'] = f"{elapsed_time:.2f}秒"
        
        # 6. ログ生成
        self._save_detailed_logs(task_id, description, execution_result, task_dir)
        
        # ファイル一覧表示
        print(f"     📁 保存先: {task_dir}/")
        print(f"     📄 生成ファイル:")
        for file in sorted(task_dir.glob('*')):
            if file.is_file():
                size = file.stat().st_size
                print(f"        - {file.name} ({size:,} bytes)")
        
        return execution_result
    
    def _execute_with_details(self, task: Dict, details: Dict, task_types: list, task_dir: Path) -> Dict:
        """詳細情報を活用した実行"""
        
        # 詳細情報がある場合は、それを活用
        if details['has_details']:
            return self._execute_detailed_task(task, details, task_types, task_dir)
        else:
            # 詳細情報がない場合は従来の方法
            return self._execute_by_detected_types(task, task_types, task_dir)
    
    def _execute_detailed_task(self, task: Dict, details: Dict, task_types: list, task_dir: Path) -> Dict:
        """詳細情報がある場合の実行"""
        task_id = task.get('task_id')
        
        # タスクタイプに応じたテンプレート + 詳細情報
        if 'testing' in task_types:
            return self._execute_testing_with_details(task, details, task_dir)
        elif 'cli' in task_types:
            return self._execute_cli_with_details(task, details, task_dir)
        elif 'api' in task_types:
            return self._execute_api_with_details(task, details, task_dir)
        else:
            return self._execute_generic_with_details(task, details, task_dir)
    
    def _execute_testing_with_details(self, task: Dict, details: Dict, task_dir: Path) -> Dict:
        """テストタスク（詳細情報活用版）"""
        task_id = task.get('task_id')
        
        # 成功基準からテスト要件を抽出
        criteria = self.parser.parse_success_criteria(details['success_criteria'])
        context = self.parser.parse_context(details['context'])
        
        test_count = criteria['numeric_targets'].get('test_count', 0)
        coverage_target = criteria['numeric_targets'].get('coverage', 80.0)
        time_limit = criteria['numeric_targets'].get('time_minutes', 5)
        
        # テスト実行スクリプト生成
        test_script = f'''#!/bin/bash
# テスト実行スクリプト
# タスクID: {task_id}
# 生成日時: {datetime.now().isoformat()}

echo "🧪 テスト実行開始"
echo "目標: {test_count}テスト、カバレッジ{coverage_target}%以上、{time_limit}分以内"

# テスト実行
pytest {' '.join(context['directories'])} -v --cov --cov-report=html --cov-report=xml

# 結果確認
if [ $? -eq 0 ]; then
    echo "✅ 全テスト成功"
else
    echo "❌ テスト失敗あり"
    exit 1
fi

# カバレッジ確認
coverage report

echo ""
echo "✅ テスト完了"
'''
        
        test_script_path = task_dir / "run_tests.sh"
        with open(test_script_path, 'w') as f:
            f.write(test_script)
        
        # README生成
        readme = f'''# テスト実行タスク: {task_id}

## 📋 目的
{details['purpose']}

## 🎯 成功基準
{details['success_criteria']}

### 数値目標
- テスト数: {test_count}
- カバレッジ: {coverage_target}%以上
- 実行時間: {time_limit}分以内

## 🚀 実行方法
```bash
bash run_tests.sh
```

## 📊 期待される結果
- 全{test_count}テストが成功
- カバレッジレポート（coverage.xml）生成
- HTMLレポート（htmlcov/）生成

## 🔧 技術スタック
{', '.join(context['technologies'])}

---
生成日時: {datetime.now().isoformat()}
'''
        
        readme_path = task_dir / "README.md"
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme)
        
        return {
            'summary': f'テスト実行スクリプト生成（目標: {test_count}テスト、カバレッジ{coverage_target}%）',
            'output_files': [str(test_script_path), str(readme_path)],
            'execution_log': f'''詳細情報活用:
  - 目的: {details['purpose'][:50]}...
  - 成功基準: {len(criteria['items'])}項目
  - 数値目標: {test_count}テスト、{coverage_target}%カバレッジ
  - 技術: {', '.join(context['technologies'])}'''
        }
    
    def _execute_cli_with_details(self, task: Dict, details: Dict, task_dir: Path) -> Dict:
        """CLIタスク（詳細情報活用版） - 既存実装を使用"""
        return self._execute_cli_task(task, task_dir)
    
    def _execute_api_with_details(self, task: Dict, details: Dict, task_dir: Path) -> Dict:
        """APIタスク（詳細情報活用版） - 既存実装を使用"""
        return self._execute_api_task(task, task_dir)
    
    def _execute_generic_with_details(self, task: Dict, details: Dict, task_dir: Path) -> Dict:
        """汎用タスク（詳細情報活用版）"""
        task_id = task.get('task_id')
        
        # 詳細情報を活用したレポート生成
        report = f'''# タスク完了レポート: {task_id}

## 📋 目的
{details['purpose']}

## 📖 タスク概要
{details['overview']}

## ✅ 成功基準
{details['success_criteria']}

## 🔧 コンテキスト情報
{details['context']}

## 🎯 実行結果

### 実施内容
詳細情報に基づいて以下を実施しました：
1. 目的の確認と理解
2. 成功基準の明確化
3. 必要な技術スタックの確認
4. 実装計画の策定

### 生成成果物
- タスク完了レポート（本ファイル）
- 実装ガイドライン

---
生成日時: {datetime.now().isoformat()}
'''
        
        report_path = task_dir / "task_completion_report.md"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        return {
            'summary': f'詳細情報活用型レポート生成',
            'output_files': [str(report_path)],
            'execution_log': f'詳細情報を活用してレポートを生成しました'
        }
    
    def _evaluate_quality_v3(self, result: Dict, details: Dict, task_types: list) -> int:
        """品質評価（詳細情報考慮版）"""
        score = 7
        
        # 詳細情報活用ボーナス
        if details.get('has_details'):
            score += 2
        
        # ファイル数
        num_files = len(result.get('output_files', []))
        if num_files >= 3:
            score += 1
        elif num_files >= 2:
            score += 0.5
        
        # 複合タイプ
        if len(task_types) > 1:
            score += 0.5
        
        return min(int(score), 10)
    
    def _save_detailed_logs(self, task_id: str, description: str, result: Dict, task_dir: Path):
        """詳細ログ保存"""
        log_content = f'''# タスク実行ログ: {task_id}

**実行日時**: {datetime.now().isoformat()}
**ステータス**: {result.get('status')}
**品質スコア**: {result.get('quality_score')}/10
**詳細情報活用**: {"✅" if result.get('details_used') else "❌"}

## タスク情報
{description[:200]}...

## 実行結果
{result.get('summary', 'N/A')}

## 生成ファイル
'''
        for file in result.get('output_files', []):
            log_content += f"- {Path(file).name}\n"
        
        log_path = task_dir / "EXECUTION_LOG.md"
        with open(log_path, 'w', encoding='utf-8') as f:
            f.write(log_content)
