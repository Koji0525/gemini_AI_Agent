#!/usr/bin/env python3
"""
IntelligentFeedbackGenerator: 知的フィードバック生成器

ナレッジベースとDecisionSupportSystemを活用して、
AIによる高度な改善提案を自動生成。
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
import google.generativeai as genai
from configuration.config_loader import get_config


class FeedbackProposal:
    """フィードバック提案"""
    
    def __init__(
        self,
        feedback_id: str,
        title: str,
        description: str,
        priority: int,  # 1(最高) ~ 5(最低)
        category: str,  # bug_fix / enhancement / optimization / learning
        confidence: float,  # 0.0 ~ 1.0
        actionable_steps: List[str],
        estimated_impact: str,  # high / medium / low
        supporting_evidence: List[Dict[str, Any]]
    ):
        self.feedback_id = feedback_id
        self.title = title
        self.description = description
        self.priority = priority
        self.category = category
        self.confidence = confidence
        self.actionable_steps = actionable_steps
        self.estimated_impact = estimated_impact
        self.supporting_evidence = supporting_evidence
        self.created_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """辞書形式に変換"""
        return {
            'feedback_id': self.feedback_id,
            'title': self.title,
            'description': self.description,
            'priority': self.priority,
            'category': self.category,
            'confidence': self.confidence,
            'actionable_steps': self.actionable_steps,
            'estimated_impact': self.estimated_impact,
            'evidence_count': len(self.supporting_evidence),
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }


class IntelligentFeedbackGenerator:
    """知的フィードバック生成器"""
    
    def __init__(
        self,
        kb_manager=None,
        decision_system=None,
        use_gemini: bool = True
    ):
        """
        初期化
        
        Args:
            kb_manager: KnowledgeBaseManager
            decision_system: DecisionSupportSystem
            use_gemini: Gemini APIを使用するか
        """
        self.kb_manager = kb_manager
        self.decision_system = decision_system
        self.use_gemini = use_gemini
        
        # Gemini API初期化
        if use_gemini:
            try:
                api_key = get_config('GEMINI_API_KEY')
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel('gemini-pro')
                print("✅ Gemini API初期化完了")
            except Exception as e:
                print(f"⚠️ Gemini API初期化失敗: {e}")
                self.use_gemini = False
                self.model = None
        else:
            self.model = None
        
        print("✅ IntelligentFeedbackGenerator初期化完了")
    
    def analyze_system_health(self) -> Dict[str, Any]:
        """
        システムの健全性を分析
        
        Returns:
            分析結果
        """
        print("\n" + "=" * 70)
        print("🏥 システム健全性分析")
        print("=" * 70)
        
        if not self.kb_manager:
            print("⚠️ KnowledgeBaseManager未設定")
            return {}
        
        # ナレッジベース統計取得
        stats = self.kb_manager.get_statistics()
        
        total = stats.get('total_knowledge', 0)
        success_patterns = stats.get('success_patterns', 0)
        failure_patterns = stats.get('failure_patterns', 0)
        fix_recipes = stats.get('fix_recipes', 0)
        
        # 健全性スコア計算
        health_score = 100.0
        issues = []
        
        # 1. ナレッジ量チェック
        if total < 10:
            health_score -= 30
            issues.append("ナレッジが不足（最低10件推奨）")
        
        # 2. バランスチェック
        if success_patterns == 0:
            health_score -= 20
            issues.append("成功パターンがない")
        
        if failure_patterns > fix_recipes * 2:
            health_score -= 15
            issues.append("失敗に対する修正レシピが不足")
        
        # 3. 活用度チェック
        if fix_recipes == 0:
            health_score -= 20
            issues.append("修正レシピがない")
        
        result = {
            'health_score': max(0, health_score),
            'total_knowledge': total,
            'success_patterns': success_patterns,
            'failure_patterns': failure_patterns,
            'fix_recipes': fix_recipes,
            'issues': issues,
            'status': self._get_health_status(health_score)
        }
        
        print(f"\n📊 健全性スコア: {result['health_score']:.1f}/100")
        print(f"ステータス: {result['status']}")
        if issues:
            print(f"\n⚠️ 検出された問題:")
            for i, issue in enumerate(issues, 1):
                print(f"   {i}. {issue}")
        
        return result
    
    def _get_health_status(self, score: float) -> str:
        """健全性スコアからステータスを判定"""
        if score >= 80:
            return "優良"
        elif score >= 60:
            return "良好"
        elif score >= 40:
            return "注意"
        else:
            return "要改善"
    
    def generate_feedback_from_knowledge(
        self,
        limit: int = 5
    ) -> List[FeedbackProposal]:
        """
        ナレッジベースから改善提案を生成
        
        Args:
            limit: 最大提案数
            
        Returns:
            フィードバック提案のリスト
        """
        print("\n" + "=" * 70)
        print("💡 ナレッジベースから改善提案生成")
        print("=" * 70)
        
        proposals = []
        
        # 1. システム健全性から提案生成
        health = self.analyze_system_health()
        proposals.extend(self._generate_health_based_feedback(health))
        
        # 2. 失敗パターンから提案生成
        if self.kb_manager:
            failure_patterns = self.kb_manager.search_similar_knowledge(
                {'knowledge_type': 'failure_pattern'},
                limit=5
            )
            proposals.extend(self._generate_failure_based_feedback(failure_patterns))
        
        # 3. 成功パターンから提案生成
        if self.kb_manager:
            success_patterns = self.kb_manager.search_similar_knowledge(
                {'knowledge_type': 'success_pattern'},
                limit=5
            )
            proposals.extend(self._generate_success_based_feedback(success_patterns))
        
        # 優先度順にソート
        proposals.sort(key=lambda p: (p.priority, -p.confidence))
        
        print(f"\n✅ {len(proposals)}件の提案を生成")
        
        return proposals[:limit]
    
    def _generate_health_based_feedback(
        self,
        health: Dict[str, Any]
    ) -> List[FeedbackProposal]:
        """健全性分析から提案生成"""
        proposals = []
        
        for issue in health.get('issues', []):
            if 'ナレッジが不足' in issue:
                proposal = FeedbackProposal(
                    feedback_id=f"HEALTH_{datetime.now().strftime('%Y%m%d%H%M%S')}_1",
                    title="ナレッジベースの拡充が必要",
                    description="現在のナレッジ量では効果的な学習ができません。より多くのタスクを実行してデータを蓄積してください。",
                    priority=2,
                    category='learning',
                    confidence=0.9,
                    actionable_steps=[
                        "様々な種類のタスクを実行",
                        "成功・失敗の両方を記録",
                        "判断プロセスを詳細に記録"
                    ],
                    estimated_impact='high',
                    supporting_evidence=[health]
                )
                proposals.append(proposal)
            
            elif '成功パターンがない' in issue:
                proposal = FeedbackProposal(
                    feedback_id=f"HEALTH_{datetime.now().strftime('%Y%m%d%H%M%S')}_2",
                    title="成功例の蓄積が必要",
                    description="成功パターンがないため、ベストプラクティスを学習できません。品質の高いタスクを実行してください。",
                    priority=2,
                    category='learning',
                    confidence=0.85,
                    actionable_steps=[
                        "品質スコア8以上のタスクを3件以上実行",
                        "成功した設定やパラメータを記録",
                        "再現可能な手順を文書化"
                    ],
                    estimated_impact='high',
                    supporting_evidence=[health]
                )
                proposals.append(proposal)
            
            elif '修正レシピが不足' in issue:
                proposal = FeedbackProposal(
                    feedback_id=f"HEALTH_{datetime.now().strftime('%Y%m%d%H%M%S')}_3",
                    title="エラー修正レシピの記録が必要",
                    description="失敗に対する修正方法が記録されていません。エラー発生時に判断プロセスを記録してください。",
                    priority=1,
                    category='bug_fix',
                    confidence=0.8,
                    actionable_steps=[
                        "エラー発生時にContextLoggerで判断記録",
                        "修正内容と結果を詳細に記録",
                        "成功した修正をパターン化"
                    ],
                    estimated_impact='high',
                    supporting_evidence=[health]
                )
                proposals.append(proposal)
        
        return proposals
    
    def _generate_failure_based_feedback(
        self,
        failure_patterns: List[Dict[str, Any]]
    ) -> List[FeedbackProposal]:
        """失敗パターンから提案生成"""
        proposals = []
        
        # 頻度の高い失敗パターンに注目
        for pattern in failure_patterns[:3]:
            try:
                import json
                context = json.loads(pattern.get('context', '{}'))
                occurrence = context.get('occurrence_count', 0)
                
                if occurrence >= 3:  # 3回以上発生
                    proposal = FeedbackProposal(
                        feedback_id=f"FAILURE_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                        title=f"頻発エラーの対策が必要: {pattern.get('pattern_description', 'N/A')}",
                        description=f"このエラーは過去に{occurrence}回発生しています。根本的な対策が必要です。",
                        priority=1,
                        category='bug_fix',
                        confidence=0.75,
                        actionable_steps=[
                            "エラーの根本原因を分析",
                            "恒久的な修正を実装",
                            "修正レシピとしてナレッジベースに登録"
                        ],
                        estimated_impact='high',
                        supporting_evidence=[pattern]
                    )
                    proposals.append(proposal)
            except:
                pass
        
        return proposals
    
    def _generate_success_based_feedback(
        self,
        success_patterns: List[Dict[str, Any]]
    ) -> List[FeedbackProposal]:
        """成功パターンから提案生成"""
        proposals = []
        
        # 成功パターンを他のタスクにも適用できるか提案
        for pattern in success_patterns[:2]:
            try:
                import json
                context = json.loads(pattern.get('context', '{}'))
                success_count = context.get('success_count', 0)
                
                if success_count >= 5:  # 5回以上成功
                    proposal = FeedbackProposal(
                        feedback_id=f"SUCCESS_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                        title=f"成功パターンの水平展開: {pattern.get('pattern_description', 'N/A')}",
                        description=f"このパターンは{success_count}回成功しています。他のタスクにも適用を検討してください。",
                        priority=3,
                        category='enhancement',
                        confidence=0.7,
                        actionable_steps=[
                            "類似タスクを特定",
                            "成功パターンを適用",
                            "効果を測定"
                        ],
                        estimated_impact='medium',
                        supporting_evidence=[pattern]
                    )
                    proposals.append(proposal)
            except:
                pass
        
        return proposals
    
    async def generate_gemini_feedback(
        self,
        context: str,
        knowledge_summary: str
    ) -> Optional[str]:
        """
        Gemini APIで改善提案を生成
        
        Args:
            context: コンテキスト情報
            knowledge_summary: ナレッジの要約
            
        Returns:
            生成された提案
        """
        if not self.use_gemini or not self.model:
            return None
        
        print("\n🤖 Gemini APIで改善提案生成中...")
        
        prompt = f"""
あなたはAIシステムの改善を支援するアシスタントです。

以下の情報を基に、システムの改善提案を3つ生成してください：

【現在の状況】
{context}

【ナレッジベースの要約】
{knowledge_summary}

【要件】
1. 具体的で実行可能な提案
2. 優先度と期待される効果を明記
3. 実装の難易度を考慮

簡潔に箇条書きで回答してください。
"""
        
        try:
            response = self.model.generate_content(prompt)
            print("✅ Gemini API応答取得完了")
            return response.text
        except Exception as e:
            print(f"⚠️ Gemini API呼び出しエラー: {e}")
            return None
    
    def format_feedback_report(
        self,
        proposals: List[FeedbackProposal]
    ) -> str:
        """
        フィードバックレポートをフォーマット
        
        Args:
            proposals: フィードバック提案のリスト
            
        Returns:
            フォーマットされたレポート
        """
        report = []
        report.append("=" * 70)
        report.append("📊 システム改善提案レポート")
        report.append("=" * 70)
        report.append(f"生成日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"提案数: {len(proposals)}件")
        report.append("")
        
        # 優先度別に分類
        by_priority = {}
        for p in proposals:
            if p.priority not in by_priority:
                by_priority[p.priority] = []
            by_priority[p.priority].append(p)
        
        priority_names = {
            1: "🔴 最優先",
            2: "🟡 高優先度",
            3: "🟢 中優先度",
            4: "🔵 低優先度",
            5: "⚪ 補足"
        }
        
        for priority in sorted(by_priority.keys()):
            report.append(f"\n{priority_names.get(priority, f'優先度{priority}')}")
            report.append("-" * 70)
            
            for i, proposal in enumerate(by_priority[priority], 1):
                report.append(f"\n{i}. {proposal.title}")
                report.append(f"   カテゴリ: {proposal.category}")
                report.append(f"   信頼度: {proposal.confidence:.0%}")
                report.append(f"   期待効果: {proposal.estimated_impact}")
                report.append(f"\n   {proposal.description}")
                report.append(f"\n   アクション:")
                for step in proposal.actionable_steps:
                    report.append(f"      • {step}")
        
        report.append("\n" + "=" * 70)
        
        return "\n".join(report)


if __name__ == "__main__":
    # 簡易テスト
    generator = IntelligentFeedbackGenerator(use_gemini=False)
    print("IntelligentFeedbackGenerator初期化成功")
