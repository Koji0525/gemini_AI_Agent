"""
ナレッジベース統合（実践版）
動作確認済みコードをナレッジとして蓄積
"""

import sys
import os
from pathlib import Path
from datetime import datetime

sys.path.insert(0, '/workspaces/gemini_AI_Agent')

from tools.knowledge_manager import KnowledgeManager
from agents.automation.working_code_extractor import WorkingCodeExtractor

class KnowledgeBaseIntegrator:
    """ナレッジベース統合（実践版）"""
    
    def __init__(self):
        self.km = KnowledgeManager()
        self.extractor = WorkingCodeExtractor()
    
    def register_to_knowledge_base(
        self,
        task_id: str,
        output_path: str,
        quality_score: float,
        test_results: dict
    ) -> dict:
        """
        動作確認済みコードをナレッジベースに登録
        
        Args:
            task_id: タスクID
            output_path: 出力パス
            quality_score: 品質スコア
            test_results: テスト結果
        
        Returns:
            result: 登録結果
        """
        
        print()
        print("=" * 80)
        print("�� ナレッジベース登録（動作確認済みコード）")
        print("=" * 80)
        print(f"タスクID: {task_id}")
        print(f"品質スコア: {quality_score}/10")
        print()
        
        # 品質閾値チェック
        if quality_score < 7.0:
            print(f"⚠️  品質スコアが低いため登録をスキップ (<7.0)")
            return {'success': False, 'reason': 'low_quality'}
        
        # 動作確認済みコードを抽出
        print("🔍 動作確認済みコードを抽出中...")
        knowledge = self.extractor.extract_working_knowledge(
            task_id, output_path, quality_score, test_results
        )
        
        # ナレッジフォーマット化
        formatted_knowledge = self._format_knowledge(knowledge)
        
        print(f"✅ ナレッジ抽出完了")
        print(f"   タイトル: {knowledge['title']}")
        print(f"   コード行数: {len(knowledge['working_code'].split(chr(10)))}行")
        print()
        
        # ナレッジベースに登録
        try:
            entry_id = self.km.add_knowledge(
                content=formatted_knowledge,
                source=f'verified_code:{task_id}',
                metadata={
                    'task_id': task_id,
                    'output_path': output_path,
                    'quality_score': quality_score,
                    'test_status': knowledge['test_status'],
                    'category': 'working_code',
                    'tags': ['verified', 'phase3', 'phase4a', f'quality_{int(quality_score)}'],
                    'timestamp': datetime.now().isoformat()
                }
            )
            
            print(f"✅ ナレッジベース登録完了 ({entry_id})")
            
            return {
                'success': True,
                'entry_id': entry_id,
                'quality_score': quality_score
            }
        
        except Exception as e:
            print(f"❌ ナレッジベース登録エラー: {e}")
            import traceback
            traceback.print_exc()
            
            return {
                'success': False,
                'error': str(e)
            }
    
    def _format_knowledge(self, knowledge: dict) -> str:
        """ナレッジをMarkdown形式にフォーマット"""
        
        formatted = f"""# {knowledge['title']}

## 📋 概要
**動作確認済みコード（品質: {knowledge['quality_score']}/10 | テスト: {knowledge['test_status']}）**

{knowledge['problem'][:200]}

## ❓ 解決した問題
{knowledge['problem']}

## ✅ 実装方法
{knowledge['solution']}

## 💻 動作確認済みコード
```python
{knowledge['working_code']}
```

## 🎯 使い方
{knowledge['usage']}

## 🎓 学んだこと
{knowledge['lessons']}

## 🔖 タグ
verified, working_code, phase3, phase4a, quality_{int(knowledge['quality_score'])}

---
*このナレッジは実際に動作確認されたコードです*
"""
        
        return formatted

