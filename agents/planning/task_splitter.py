#!/usr/bin/env python3
"""
タスク分割ロジック

目的: 大きすぎるタスクを適切なサイズに自動分割

分割基準:
1. 所要時間 > 4時間 → 分割
2. 説明文 > 1000文字 → 分割
3. 受け入れ基準 > 10個 → 分割

分割方法:
- 時系列分割: "データ収集→前処理→分析→報告"
- 機能分割: "API開発→UI開発→テスト"
- 並列分割: "データソースA, B, C を並列収集"
"""

from typing import Dict, List, Tuple
import re

class TaskSplitter:
    """
    タスク分割ロジック
    
    責務:
    - タスクサイズの評価
    - 分割必要性の判定
    - 適切な分割方法の選択
    - サブタスク生成
    
    使用例:
        splitter = TaskSplitter()
        
        should_split, reason = splitter.should_split(task_data)
        
        if should_split:
            subtasks = splitter.split_task(task_data, method='sequential')
    """
    
    # 分割基準
    MAX_DURATION_HOURS = 4  # 4時間以上は分割
    MAX_DESCRIPTION_LENGTH = 1000  # 1000文字以上は分割
    MAX_ACCEPTANCE_CRITERIA = 10  # 10個以上は分割
    
    def __init__(self):
        """初期化"""
        pass
    
    def should_split(self, task_data: Dict) -> Tuple[bool, str]:
        """
        タスクを分割すべきか判定
        
        Args:
            task_data: タスクデータ
        
        Returns:
            (分割すべきか, 理由)
        """
        reasons = []
        
        # 1. 所要時間チェック
        duration = task_data.get('estimated_duration_hours', 0)
        if duration > self.MAX_DURATION_HOURS:
            reasons.append(f"所要時間が長すぎる: {duration}時間 > {self.MAX_DURATION_HOURS}時間")
        
        # 2. 説明文長さチェック
        description = task_data.get('description', '')
        if len(description) > self.MAX_DESCRIPTION_LENGTH:
            reasons.append(f"説明が長すぎる: {len(description)}文字 > {self.MAX_DESCRIPTION_LENGTH}文字")
        
        # 3. 受け入れ基準数チェック
        acceptance_criteria = task_data.get('acceptance_criteria', [])
        if len(acceptance_criteria) > self.MAX_ACCEPTANCE_CRITERIA:
            reasons.append(f"受け入れ基準が多すぎる: {len(acceptance_criteria)}個 > {self.MAX_ACCEPTANCE_CRITERIA}個")
        
        should_split = len(reasons) > 0
        reason = '; '.join(reasons) if reasons else "分割不要"
        
        return should_split, reason
    
    def split_task(
        self,
        task_data: Dict,
        method: str = 'auto'
    ) -> List[Dict]:
        """
        タスクを分割
        
        Args:
            task_data: タスクデータ
            method: 分割方法
                - 'auto': 自動判定
                - 'sequential': 時系列分割
                - 'functional': 機能分割
                - 'parallel': 並列分割
        
        Returns:
            サブタスクのリスト
        """
        task_id = task_data.get('task_id', 'unknown')
        
        if method == 'auto':
            # 自動判定
            method = self._determine_split_method(task_data)
        
        print(f"📋 タスク分割: {task_id} ({method}方式)")
        
        if method == 'sequential':
            return self._split_sequential(task_data)
        elif method == 'functional':
            return self._split_functional(task_data)
        elif method == 'parallel':
            return self._split_parallel(task_data)
        else:
            # デフォルトは時系列分割
            return self._split_sequential(task_data)
    
    def _determine_split_method(self, task_data: Dict) -> str:
        """分割方法を自動判定"""
        description = task_data.get('description', '').lower()
        
        # キーワードで判定
        if any(word in description for word in ['api', 'ui', 'テスト', 'test']):
            return 'functional'
        elif any(word in description for word in ['複数', '各', 'それぞれ', 'multiple']):
            return 'parallel'
        else:
            return 'sequential'
    
    def _split_sequential(self, task_data: Dict) -> List[Dict]:
        """時系列分割"""
        task_id = task_data.get('task_id', 'unknown')
        description = task_data.get('description', '')
        
        # 一般的なフェーズに分割
        phases = [
            {
                'id': f"{task_id}_phase1",
                'name': '準備・調査',
                'description': f"{description}の準備と調査を実施",
                'phase': 'preparation'
            },
            {
                'id': f"{task_id}_phase2",
                'name': '実装・実行',
                'description': f"{description}の実装または実行",
                'phase': 'execution'
            },
            {
                'id': f"{task_id}_phase3",
                'name': '検証・報告',
                'description': f"{description}の検証と報告書作成",
                'phase': 'verification'
            }
        ]
        
        subtasks = []
        for phase in phases:
            subtask = {
                'task_id': phase['id'],
                'description': phase['description'],
                'type': 'sequential',
                'parent_task': task_id,
                'estimated_duration_hours': task_data.get('estimated_duration_hours', 4) / 3
            }
            subtasks.append(subtask)
        
        return subtasks
    
    def _split_functional(self, task_data: Dict) -> List[Dict]:
        """機能分割"""
        task_id = task_data.get('task_id', 'unknown')
        description = task_data.get('description', '')
        
        # 機能別に分割
        functions = [
            {
                'id': f"{task_id}_backend",
                'name': 'バックエンド開発',
                'description': f"{description}のバックエンド機能を実装"
            },
            {
                'id': f"{task_id}_frontend",
                'name': 'フロントエンド開発',
                'description': f"{description}のフロントエンド機能を実装"
            },
            {
                'id': f"{task_id}_test",
                'name': 'テスト',
                'description': f"{description}の統合テストを実施"
            }
        ]
        
        subtasks = []
        for func in functions:
            subtask = {
                'task_id': func['id'],
                'description': func['description'],
                'type': 'functional',
                'parent_task': task_id,
                'estimated_duration_hours': task_data.get('estimated_duration_hours', 6) / 3
            }
            subtasks.append(subtask)
        
        return subtasks
    
    def _split_parallel(self, task_data: Dict) -> List[Dict]:
        """並列分割"""
        task_id = task_data.get('task_id', 'unknown')
        description = task_data.get('description', '')
        
        # 並列実行可能な単位に分割
        parallel_units = [
            {
                'id': f"{task_id}_unit1",
                'name': 'ユニット1',
                'description': f"{description}のユニット1を処理"
            },
            {
                'id': f"{task_id}_unit2",
                'name': 'ユニット2',
                'description': f"{description}のユニット2を処理"
            },
            {
                'id': f"{task_id}_unit3",
                'name': 'ユニット3',
                'description': f"{description}のユニット3を処理"
            }
        ]
        
        subtasks = []
        for unit in parallel_units:
            subtask = {
                'task_id': unit['id'],
                'description': unit['description'],
                'type': 'parallel',
                'parent_task': task_id,
                'estimated_duration_hours': task_data.get('estimated_duration_hours', 6) / 3,
                'can_run_parallel': True
            }
            subtasks.append(subtask)
        
        return subtasks

# ========================================
# テスト
# ========================================
if __name__ == "__main__":
    print("="*60)
    print("✂️ TaskSplitter テスト")
    print("="*60)
    
    splitter = TaskSplitter()
    
    # テストタスク（分割が必要）
    large_task = {
        'task_id': 'task_large_001',
        'description': '金融市場の包括的分析レポートを作成する。' * 50,  # 長い説明
        'estimated_duration_hours': 8,  # 8時間
        'acceptance_criteria': [f'基準{i}' for i in range(15)]  # 15個の基準
    }
    
    print("\n[1/3] 分割判定...")
    should_split, reason = splitter.should_split(large_task)
    print(f"   分割必要: {should_split}")
    print(f"   理由: {reason}")
    
    if should_split:
        print("\n[2/3] タスク分割（時系列）...")
        subtasks_seq = splitter.split_task(large_task, method='sequential')
        print(f"   サブタスク数: {len(subtasks_seq)}")
        for st in subtasks_seq:
            print(f"   - {st['task_id']}: {st['description'][:50]}...")
        
        print("\n[3/3] タスク分割（機能別）...")
        subtasks_func = splitter.split_task(large_task, method='functional')
        print(f"   サブタスク数: {len(subtasks_func)}")
        for st in subtasks_func:
            print(f"   - {st['task_id']}: {st['description'][:50]}...")
    
    print("\n" + "="*60)
    print("✅ テスト完了")
    print("="*60)
