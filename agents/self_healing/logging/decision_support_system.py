#!/usr/bin/env python3
"""
DecisionSupportSystem: 判断支援システム

過去の成功例とナレッジベースを活用して、
AIによる自動判断と修正提案を生成する。
"""
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import json
from .similarity_search_engine import SimilaritySearchEngine
from .knowledge_base_manager import KnowledgeBaseManager


class DecisionProposal:
    """判断提案"""

    def __init__(
        self,
        proposal_id: str,
        proposal_type: str,  # fix / retry / escalate / ignore
        description: str,
        confidence_score: float,
        reasoning: str,
        action_steps: List[str],
        supporting_knowledge: List[Dict[str, Any]],
    ):
        self.proposal_id = proposal_id
        self.proposal_type = proposal_type
        self.description = description
        self.confidence_score = confidence_score  # 0.0 ~ 1.0
        self.reasoning = reasoning
        self.action_steps = action_steps
        self.supporting_knowledge = supporting_knowledge
        self.created_at = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """辞書形式に変換"""
        return {
            "proposal_id": self.proposal_id,
            "proposal_type": self.proposal_type,
            "description": self.description,
            "confidence_score": self.confidence_score,
            "reasoning": self.reasoning,
            "action_steps": self.action_steps,
            "supporting_knowledge_count": len(self.supporting_knowledge),
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        }

    def is_high_confidence(self) -> bool:
        """高信頼度か判定"""
        return self.confidence_score >= 0.75

    def is_actionable(self) -> bool:
        """実行可能か判定"""
        return self.confidence_score >= 0.5 and len(self.action_steps) > 0


class DecisionSupportSystem:
    """判断支援システム"""

    def __init__(self, kb_manager: KnowledgeBaseManager, search_engine: SimilaritySearchEngine):
        """
        初期化

        Args:
            kb_manager: KnowledgeBaseManager
            search_engine: SimilaritySearchEngine
        """
        self.kb_manager = kb_manager
        self.search_engine = search_engine

        print("✅ DecisionSupportSystem初期化完了")

    def analyze_situation(self, error_type: str, error_message: str, task_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        状況を分析

        Args:
            error_type: エラータイプ
            error_message: エラーメッセージ
            task_context: タスクコンテキスト

        Returns:
            分析結果
        """
        print("\n" + "=" * 70)
        print("🔍 状況分析開始")
        print("=" * 70)
        print(f"エラータイプ: {error_type}")
        print(f"エラーメッセージ: {error_message[:100]}...")
        print(f"タスクコンテキスト: {task_context}")

        # 類似ケースを検索
        query = {
            "text": f"{error_type} {error_message}",
            "error_type": error_type,
            "task_type": task_context.get("task_type"),
            "tags": task_context.get("tags", []),
        }

        similar_cases = self.search_engine.search(query=query, limit=5, min_score=0.2)

        # 成功例と失敗例を分類
        success_cases = []
        failure_cases = []
        fix_recipes = []

        for doc, score in similar_cases:
            knowledge_type = doc.get("knowledge_type")
            if knowledge_type == "success_pattern":
                success_cases.append((doc, score))
            elif knowledge_type == "failure_pattern":
                failure_cases.append((doc, score))
            elif knowledge_type == "fix_recipe":
                fix_recipes.append((doc, score))

        analysis = {
            "error_type": error_type,
            "error_message": error_message,
            "similar_cases_count": len(similar_cases),
            "success_cases_count": len(success_cases),
            "failure_cases_count": len(failure_cases),
            "fix_recipes_count": len(fix_recipes),
            "similar_cases": similar_cases,
            "success_cases": success_cases,
            "failure_cases": failure_cases,
            "fix_recipes": fix_recipes,
        }

        print(f"\n✅ 分析完了:")
        print(f"   類似ケース: {len(similar_cases)}件")
        print(f"   - 成功例: {len(success_cases)}件")
        print(f"   - 失敗例: {len(failure_cases)}件")
        print(f"   - 修正レシピ: {len(fix_recipes)}件")

        return analysis

    def generate_proposals(self, analysis: Dict[str, Any], max_proposals: int = 3) -> List[DecisionProposal]:
        """
        判断提案を生成

        Args:
            analysis: 状況分析結果
            max_proposals: 最大提案数

        Returns:
            判断提案のリスト
        """
        print("\n" + "=" * 70)
        print("💡 判断提案生成")
        print("=" * 70)

        proposals = []

        # 1. 修正レシピがある場合
        if analysis["fix_recipes"]:
            proposals.extend(self._generate_fix_proposals(analysis))

        # 2. 成功例がある場合
        if analysis["success_cases"]:
            proposals.extend(self._generate_success_based_proposals(analysis))

        # 3. 失敗例がある場合
        if analysis["failure_cases"]:
            proposals.extend(self._generate_avoidance_proposals(analysis))

        # 4. ナレッジがない場合
        if not proposals:
            proposals.append(self._generate_fallback_proposal(analysis))

        # 信頼度順にソート
        proposals.sort(key=lambda p: p.confidence_score, reverse=True)

        # 上位N件
        top_proposals = proposals[:max_proposals]

        print(f"\n✅ {len(top_proposals)}件の提案を生成")
        for i, proposal in enumerate(top_proposals, 1):
            print(f"\n{i}. {proposal.description}")
            print(f"   タイプ: {proposal.proposal_type}")
            print(f"   信頼度: {proposal.confidence_score:.2%}")
            print(f"   アクションステップ: {len(proposal.action_steps)}個")

        return top_proposals

    def _generate_fix_proposals(self, analysis: Dict[str, Any]) -> List[DecisionProposal]:
        """修正レシピベースの提案を生成"""
        proposals = []

        for doc, similarity_score in analysis["fix_recipes"]:
            # 信頼度計算
            effectiveness = float(doc.get("effectiveness_score", 0)) / 100
            usage_count = int(doc.get("usage_count", 0))

            # 使用回数が多いほど信頼度が高い
            usage_factor = min(usage_count / 10, 1.0)

            confidence = similarity_score * 0.4 + effectiveness * 0.4 + usage_factor * 0.2

            # アクションステップを生成
            code_snippet = doc.get("code_snippet", "")
            action_steps = [
                f"過去の成功例（{usage_count}回使用）を適用",
                f"修正内容: {doc.get('pattern_description', 'N/A')}",
            ]

            if code_snippet:
                action_steps.append(f"コード適用: {code_snippet}")

            action_steps.append("実行して結果を確認")
            action_steps.append("成功した場合、ナレッジベースを更新")

            # 推論の説明
            reasoning = (
                f"このエラーに対して過去に{usage_count}回使用され、"
                f"{effectiveness:.0%}の有効性を示した修正レシピがあります。"
                f"類似度は{similarity_score:.2%}です。"
            )

            proposal = DecisionProposal(
                proposal_id=f"FIX_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                proposal_type="fix",
                description=doc.get("pattern_description", "修正を適用"),
                confidence_score=confidence,
                reasoning=reasoning,
                action_steps=action_steps,
                supporting_knowledge=[doc],
            )

            proposals.append(proposal)

        return proposals

    def _generate_success_based_proposals(self, analysis: Dict[str, Any]) -> List[DecisionProposal]:
        """成功例ベースの提案を生成"""
        proposals = []

        for doc, similarity_score in analysis["success_cases"][:2]:  # 上位2件
            success_rate = float(doc.get("success_rate", 0)) / 100

            confidence = similarity_score * 0.6 + success_rate * 0.4

            try:
                context = json.loads(doc.get("context", "{}"))
                success_count = context.get("success_count", 0)
            except:
                success_count = 0

            action_steps = [
                "成功パターンを参考にタスクを再構成",
                f"成功例の共通要素を適用（{success_count}回成功）",
                "設定を成功例に合わせて調整",
                "再実行",
            ]

            reasoning = (
                f"類似のタスクで{success_count}回成功した例があります。"
                f"成功率{success_rate:.0%}、類似度{similarity_score:.2%}です。"
            )

            proposal = DecisionProposal(
                proposal_id=f"SUCCESS_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                proposal_type="retry",
                description=f"成功パターンを適用して再試行",
                confidence_score=confidence,
                reasoning=reasoning,
                action_steps=action_steps,
                supporting_knowledge=[doc],
            )

            proposals.append(proposal)

        return proposals

    def _generate_avoidance_proposals(self, analysis: Dict[str, Any]) -> List[DecisionProposal]:
        """失敗回避の提案を生成"""
        if not analysis["failure_cases"]:
            return []

        # 最も類似度の高い失敗例
        doc, similarity_score = analysis["failure_cases"][0]

        try:
            context = json.loads(doc.get("context", "{}"))
            occurrence = context.get("occurrence_count", 0)
        except:
            occurrence = 0

        # 失敗が頻繁なほど慎重に
        confidence = 0.4 - (min(occurrence, 10) / 10) * 0.2

        action_steps = [
            f"⚠️ 注意: このエラーは過去に{occurrence}回発生しています",
            "失敗パターンと異なるアプローチを検討",
            "代替手段を探す",
            "必要に応じて人間にエスカレーション",
        ]

        reasoning = f"このエラーは過去に{occurrence}回発生しており、" f"自動解決が困難な可能性があります。"

        proposal = DecisionProposal(
            proposal_id=f"AVOID_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            proposal_type="escalate",
            description="失敗パターンを回避・エスカレーション",
            confidence_score=confidence,
            reasoning=reasoning,
            action_steps=action_steps,
            supporting_knowledge=[doc],
        )

        return [proposal]

    def _generate_fallback_proposal(self, analysis: Dict[str, Any]) -> DecisionProposal:
        """フォールバック提案（ナレッジがない場合）"""
        action_steps = [
            "基本的なリトライを実行",
            "エラーログを記録",
            "新しいナレッジとして蓄積",
            "必要に応じて人間に報告",
        ]

        reasoning = "類似するナレッジが見つからないため、" "基本的な対応を行い、将来の学習データとして記録します。"

        return DecisionProposal(
            proposal_id=f"FALLBACK_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            proposal_type="retry",
            description="基本的なリトライと学習",
            confidence_score=0.3,
            reasoning=reasoning,
            action_steps=action_steps,
            supporting_knowledge=[],
        )

    def make_decision(
        self, error_type: str, error_message: str, task_context: Dict[str, Any], auto_execute_threshold: float = 0.75
    ) -> Tuple[DecisionProposal, bool]:
        """
        判断を下す

        Args:
            error_type: エラータイプ
            error_message: エラーメッセージ
            task_context: タスクコンテキスト
            auto_execute_threshold: 自動実行の閾値

        Returns:
            (判断提案, 自動実行可能か) のタプル
        """
        print("\n" + "=" * 70)
        print("🤔 判断プロセス開始")
        print("=" * 70)

        # 1. 状況分析
        analysis = self.analyze_situation(error_type, error_message, task_context)

        # 2. 提案生成
        proposals = self.generate_proposals(analysis)

        if not proposals:
            print("\n⚠️ 提案が生成できませんでした")
            return None, False

        # 3. 最良の提案を選択
        best_proposal = proposals[0]

        # 4. 自動実行可能か判定
        can_auto_execute = best_proposal.confidence_score >= auto_execute_threshold

        print("\n" + "=" * 70)
        print("✅ 判断完了")
        print("=" * 70)
        print(f"選択された提案: {best_proposal.description}")
        print(f"信頼度: {best_proposal.confidence_score:.2%}")
        print(f"自動実行: {'可能' if can_auto_execute else '不可（要人間確認）'}")
        print(f"\n推論:\n{best_proposal.reasoning}")
        print(f"\nアクションステップ:")
        for i, step in enumerate(best_proposal.action_steps, 1):
            print(f"  {i}. {step}")

        return best_proposal, can_auto_execute
