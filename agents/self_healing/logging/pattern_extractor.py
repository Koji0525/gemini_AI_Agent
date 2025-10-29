#!/usr/bin/env python3
"""
PatternExtractor: パターン抽出エンジン

統合ログから成功パターン、失敗パターン、修正レシピを自動抽出。
機械学習の訓練データとして使用可能な形式で出力。
"""
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from collections import defaultdict
import json
from .knowledge_base_manager import KnowledgePattern
from .log_integrator import LogIntegrator, IntegratedLog


class PatternExtractor:
    """パターン抽出エンジン"""
    
    # 成功パターンの閾値
    SUCCESS_MIN_COUNT = 3        # 最低3回成功
    SUCCESS_MIN_QUALITY = 8.0    # 品質スコア8以上
    
    # 失敗パターンの閾値
    FAILURE_MIN_COUNT = 2        # 最低2回発生
    
    def __init__(self, log_integrator: LogIntegrator):
        """
        初期化
        
        Args:
            log_integrator: LogIntegratorインスタンス
        """
        self.log_integrator = log_integrator
        print("✅ PatternExtractor初期化完了")
    
    async def extract_all_patterns(self) -> List[KnowledgePattern]:
        """
        全てのパターンを抽出
        
        Returns:
            抽出されたパターンのリスト
        """
        print("\n" + "=" * 60)
        print("🔍 パターン抽出エンジン開始")
        print("=" * 60)
        
        # 統合ログを取得
        print("\n📚 統合ログ取得中...")
        integrated_logs = await self.log_integrator.integrate_by_task_id()
        cleaned_logs = self.log_integrator.clean_data(integrated_logs)
        
        print(f"✅ {len(cleaned_logs)}タスクを分析対象に")
        
        all_patterns = []
        
        # 1. 成功パターン抽出
        print("\n" + "-" * 60)
        print("1️⃣  成功パターン抽出")
        print("-" * 60)
        success_patterns = self._extract_success_patterns(cleaned_logs)
        all_patterns.extend(success_patterns)
        print(f"✅ 成功パターン: {len(success_patterns)}件")
        
        # 2. 失敗パターン抽出
        print("\n" + "-" * 60)
        print("2️⃣  失敗パターン抽出")
        print("-" * 60)
        failure_patterns = self._extract_failure_patterns(cleaned_logs)
        all_patterns.extend(failure_patterns)
        print(f"✅ 失敗パターン: {len(failure_patterns)}件")
        
        # 3. 修正レシピ抽出
        print("\n" + "-" * 60)
        print("3️⃣  修正レシピ抽出")
        print("-" * 60)
        fix_recipes = self._extract_fix_recipes(cleaned_logs)
        all_patterns.extend(fix_recipes)
        print(f"✅ 修正レシピ: {len(fix_recipes)}件")
        
        # 4. 高品質タスクパターン
        print("\n" + "-" * 60)
        print("4️⃣  高品質タスクパターン抽出")
        print("-" * 60)
        quality_patterns = self._extract_high_quality_patterns(cleaned_logs)
        all_patterns.extend(quality_patterns)
        print(f"✅ 高品質パターン: {len(quality_patterns)}件")
        
        print("\n" + "=" * 60)
        print(f"🎉 パターン抽出完了: 合計 {len(all_patterns)}件")
        print("=" * 60)
        
        return all_patterns
    
    def _extract_success_patterns(
        self, 
        integrated_logs: Dict[str, IntegratedLog]
    ) -> List[KnowledgePattern]:
        """成功パターンを抽出"""
        patterns = []
        
        # タスクタイプごとにグループ化
        type_groups = defaultdict(list)
        
        for task_id, log in integrated_logs.items():
            for exec_log in log.execution_logs:
                if exec_log.get('status') == 'completed':
                    quality = float(exec_log.get('quality_score', 0))
                    if quality >= self.SUCCESS_MIN_QUALITY:
                        task_type = exec_log.get('execution_type', 'unknown')
                        type_groups[task_type].append({
                            'task_id': task_id,
                            'quality': quality,
                            'log': exec_log
                        })
        
        # 各タスクタイプでパターン生成
        for task_type, successes in type_groups.items():
            if len(successes) >= self.SUCCESS_MIN_COUNT:
                avg_quality = sum(s['quality'] for s in successes) / len(successes)
                
                pattern = KnowledgePattern(
                    pattern_type='success_pattern',
                    description=f'{task_type}タスクの高品質実行パターン',
                    context={
                        'task_type': task_type,
                        'success_count': len(successes),
                        'avg_quality': round(avg_quality, 2)
                    },
                    source_logs=[s['task_id'] for s in successes[:10]]  # 最初の10件
                )
                
                pattern.success_rate = 100.0
                pattern.usage_count = len(successes)
                pattern.effectiveness_score = min(100, int(avg_quality * 10))
                pattern.learning_tags = [task_type, 'success', 'high_quality']
                
                patterns.append(pattern)
                
                print(f"   ✓ {task_type}: {len(successes)}回成功, 平均品質{avg_quality:.1f}")
        
        return patterns
    
    def _extract_failure_patterns(
        self,
        integrated_logs: Dict[str, IntegratedLog]
    ) -> List[KnowledgePattern]:
        """失敗パターンを抽出"""
        patterns = []
        
        # エラータイプごとにグループ化
        error_groups = defaultdict(list)
        
        for task_id, log in integrated_logs.items():
            # 実行ログから失敗を検出
            for exec_log in log.execution_logs:
                if exec_log.get('status') in ['failed', 'error']:
                    error_msg = exec_log.get('error', 'Unknown error')
                    error_type = self._classify_error_type(error_msg)
                    error_groups[error_type].append({
                        'task_id': task_id,
                        'error_msg': error_msg,
                        'log': exec_log
                    })
            
            # リトライログから失敗を検出
            for retry_log in log.retry_logs:
                if not retry_log.get('success'):
                    error_type = retry_log.get('error_type', 'UnknownError')
                    error_groups[error_type].append({
                        'task_id': task_id,
                        'error_msg': retry_log.get('error_message', ''),
                        'log': retry_log
                    })
        
        # 各エラータイプでパターン生成
        for error_type, failures in error_groups.items():
            if len(failures) >= self.FAILURE_MIN_COUNT:
                pattern = KnowledgePattern(
                    pattern_type='failure_pattern',
                    description=f'{error_type}の発生パターン（{len(failures)}回発生）',
                    context={
                        'error_type': error_type,
                        'occurrence_count': len(failures),
                        'sample_message': failures[0]['error_msg'][:100]
                    },
                    source_logs=[f['task_id'] for f in failures[:10]]
                )
                
                pattern.related_errors = [error_type]
                pattern.effectiveness_score = min(100, len(failures) * 5)  # 発生頻度に応じたスコア
                pattern.learning_tags = [error_type, 'failure', 'attention_required']
                
                patterns.append(pattern)
                
                print(f"   ✓ {error_type}: {len(failures)}回発生")
        
        return patterns
    
    def _extract_fix_recipes(
        self,
        integrated_logs: Dict[str, IntegratedLog]
    ) -> List[KnowledgePattern]:
        """修正レシピを抽出（コンテキストログから）"""
        patterns = []
        
        # パターン名ごとにグループ化
        recipe_groups = defaultdict(list)
        
        for task_id, log in integrated_logs.items():
            for context_log in log.context_logs:
                pattern_name = context_log.get('pattern_name', '')
                if pattern_name:
                    recipe_groups[pattern_name].append({
                        'task_id': task_id,
                        'context': context_log
                    })
        
        # 各レシピでパターン生成
        for pattern_name, recipes in recipe_groups.items():
            context = recipes[0]['context']  # 最初のコンテキストを代表として使用
            
            pattern = KnowledgePattern(
                pattern_type='fix_recipe',
                description=context.get('modification_purpose', f'{pattern_name}の修正レシピ'),
                context={
                    'pattern_name': pattern_name,
                    'usage_count': len(recipes),
                    'error_type': context.get('error_type', 'Unknown'),
                    'decision_process': context.get('decision_process', '')
                },
                source_logs=[r['task_id'] for r in recipes]
            )
            
            pattern.code_snippet = pattern_name
            pattern.usage_count = len(recipes)
            pattern.effectiveness_score = min(100, len(recipes) * 20)
            
            # システム状態を適用条件として設定
            try:
                pattern.applicable_conditions = json.loads(
                    context.get('system_state', '{}')
                )
            except:
                pattern.applicable_conditions = {}
            
            # 学習タグを設定
            tags = context.get('learning_tags', '')
            pattern.learning_tags = tags.split(',') if tags else [pattern_name]
            
            patterns.append(pattern)
            
            print(f"   ✓ {pattern_name}: {len(recipes)}回使用")
        
        return patterns
    
    def _extract_high_quality_patterns(
        self,
        integrated_logs: Dict[str, IntegratedLog]
    ) -> List[KnowledgePattern]:
        """高品質タスクの特徴を抽出"""
        patterns = []
        
        # 品質スコア9以上のタスクを抽出
        high_quality_tasks = []
        
        for task_id, log in integrated_logs.items():
            for exec_log in log.execution_logs:
                try:
                    quality = float(exec_log.get('quality_score', 0))
                    if quality >= 9.0:
                        high_quality_tasks.append({
                            'task_id': task_id,
                            'quality': quality,
                            'type': exec_log.get('execution_type', 'unknown'),
                            'log': exec_log
                        })
                except (ValueError, TypeError):
                    pass
        
        if len(high_quality_tasks) >= 5:
            avg_quality = sum(t['quality'] for t in high_quality_tasks) / len(high_quality_tasks)
            
            pattern = KnowledgePattern(
                pattern_type='success_pattern',
                description=f'超高品質タスク実行パターン（品質9.0以上）',
                context={
                    'min_quality': 9.0,
                    'count': len(high_quality_tasks),
                    'avg_quality': round(avg_quality, 2),
                    'task_types': list(set(t['type'] for t in high_quality_tasks))
                },
                source_logs=[t['task_id'] for t in high_quality_tasks[:10]]
            )
            
            pattern.success_rate = 100.0
            pattern.usage_count = len(high_quality_tasks)
            pattern.effectiveness_score = 95
            pattern.learning_tags = ['excellence', 'high_quality', 'best_practice']
            
            patterns.append(pattern)
            
            print(f"   ✓ 超高品質タスク: {len(high_quality_tasks)}件, 平均{avg_quality:.2f}")
        
        return patterns
    
    def _classify_error_type(self, error_message: str) -> str:
        """エラーメッセージからエラータイプを分類"""
        error_msg_lower = error_message.lower()
        
        # キーワードベースの分類
        if 'timeout' in error_msg_lower or 'timed out' in error_msg_lower:
            return 'TimeoutError'
        elif 'network' in error_msg_lower or 'connection' in error_msg_lower:
            return 'NetworkError'
        elif 'authentication' in error_msg_lower or 'auth' in error_msg_lower:
            return 'AuthenticationError'
        elif 'permission' in error_msg_lower or 'forbidden' in error_msg_lower:
            return 'PermissionError'
        elif 'not found' in error_msg_lower or '404' in error_msg_lower:
            return 'NotFoundError'
        elif 'rate limit' in error_msg_lower or 'quota' in error_msg_lower:
            return 'RateLimitError'
        else:
            return 'GeneralError'
