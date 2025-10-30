#!/usr/bin/env python3
"""
パターン抽出エンジン

UnifiedLogEntry からナレッジパターンを抽出
"""

from typing import List, Dict, Any
from collections import Counter
import re

from tools.data_integration.models import UnifiedLogEntry, ContentType

class PatternExtractor:
    """パターン抽出エンジン"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.pattern_config = config.get('pattern_extraction', {})
    
    def extract_all_patterns(self, entries: List[UnifiedLogEntry]) -> Dict[str, List[Dict]]:
        """全パターンを抽出"""
        
        return {
            'failure_patterns': self.extract_failure_patterns(entries),
            'fix_recipes': self.extract_fix_recipes(entries),
            'success_patterns': self.extract_success_patterns(entries)
        }
    
    def extract_failure_patterns(self, entries: List[UnifiedLogEntry]) -> List[Dict]:
        """失敗パターン抽出"""
        
        if not self.pattern_config.get('failure_pattern', {}).get('enabled', True):
            return []
        
        # エラータイプのエントリのみ
        error_entries = [e for e in entries if e.content_type == ContentType.ERROR]
        
        # カテゴリ別に集計
        error_categories = []
        categories_config = self.pattern_config.get('failure_pattern', {}).get('categories', [])
        
        for entry in error_entries:
            error_text = str(entry.content)
            
            # カテゴリ判定
            category = 'unknown'
            for cat in categories_config:
                keywords = self._get_keywords_for_category(cat)
                if any(kw in error_text.lower() for kw in keywords):
                    category = cat
                    break
            
            error_categories.append({
                'category': category,
                'error': error_text[:500],
                'source': entry.source_id,
                'timestamp': entry.timestamp.isoformat()
            })
        
        # 頻出パターンを抽出
        min_freq = self.pattern_config.get('failure_pattern', {}).get('min_frequency', 2)
        category_counts = Counter([e['category'] for e in error_categories])
        
        patterns = []
        for category, count in category_counts.items():
            if count >= min_freq:
                # 代表例を3つ
                examples = [e for e in error_categories if e['category'] == category][:3]
                
                patterns.append({
                    'knowledge_type': 'failure_pattern',
                    'category': category,
                    'frequency': count,
                    'description': f"{category}エラーが{count}回発生",
                    'examples': [e['error'] for e in examples],
                    'confidence': min(0.9, 0.5 + (count * 0.1))
                })
        
        return patterns
    
    def extract_fix_recipes(self, entries: List[UnifiedLogEntry]) -> List[Dict]:
        """修正レシピ抽出"""
        
        if not self.pattern_config.get('fix_recipe', {}).get('enabled', True):
            return []
        
        recipes = []
        
        # エラーエントリから成功した解決方法を抽出
        for entry in entries:
            if entry.content_type != ContentType.ERROR:
                continue
            
            content = entry.content
            
            # 解決方法があるか
            solution = content.get('solution', '') or content.get('strategy', '')
            success = content.get('success', False)
            
            # 成功のみフィルター
            if self.pattern_config.get('fix_recipe', {}).get('success_only', True):
                if not success or solution == '未解決':
                    continue
            
            # 最小信頼度チェック
            min_conf = self.pattern_config.get('fix_recipe', {}).get('min_confidence', 0.8)
            if entry.confidence < min_conf:
                continue
            
            error_desc = content.get('error_description', '') or content.get('error', '')
            
            recipes.append({
                'knowledge_type': 'fix_recipe',
                'error': error_desc[:500],
                'solution': solution[:500],
                'success_rate': '100%',
                'confidence': entry.confidence,
                'source': entry.source_id,
                'context': content.get('context', '')[:200]
            })
        
        return recipes
    
    def extract_success_patterns(self, entries: List[UnifiedLogEntry]) -> List[Dict]:
        """成功パターン抽出"""
        
        if not self.pattern_config.get('success_pattern', {}).get('enabled', True):
            return []
        
        patterns = []
        
        min_quality = self.pattern_config.get('success_pattern', {}).get('min_quality_score', 8.0)
        
        for entry in entries:
            if entry.content_type != ContentType.TASK:
                continue
            
            # 品質スコアチェック
            if entry.quality_score is None or entry.quality_score < min_quality:
                continue
            
            content = entry.content
            status = content.get('status', '')
            
            if status != 'completed':
                continue
            
            task_desc = content.get('task_description', '') or content.get('description', '')
            
            patterns.append({
                'knowledge_type': 'success_pattern',
                'task': task_desc[:500],
                'quality_score': entry.quality_score,
                'status': status,
                'confidence': entry.confidence,
                'source': entry.source_id,
                'agent': content.get('agent_role', 'unknown')
            })
        
        return patterns
    
    def _get_keywords_for_category(self, category: str) -> List[str]:
        """カテゴリのキーワードを取得"""
        keywords_map = {
            'timeout': ['timeout', 'タイムアウト', '時間切れ', 'timed out'],
            'auth': ['401', 'unauthorized', '認証', '権限', 'forbidden', '403'],
            'api_limit': ['429', 'quota', 'rate limit', '制限', 'exceeded'],
            'import': ['import', 'module', 'インポート', 'modulenotfounderror', 'importerror'],
            'syntax': ['syntax', 'invalid', '構文', 'syntaxerror'],
            'network': ['network', 'connection', 'ネットワーク', '接続'],
        }
        
        return keywords_map.get(category, [])
