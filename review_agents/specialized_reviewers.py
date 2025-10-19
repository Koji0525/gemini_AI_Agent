"""
専門レビューエージェント集
"""
import re
import asyncio
from typing import Dict, List, Optional

class ContentReviewAgent:
    """コンテンツ品質レビューエージェント"""
    
    def __init__(self, browser):
        self.browser = browser
    
    async def review_content_quality(self, task_description: str, output: str) -> Dict:
        """コンテンツの品質をレビュー"""
        try:
            review_prompt = f"""以下のタスク出力を専門家の視点で詳細にレビューしてください。

【レビュー対象タスク】
{task_description}

【レビュー対象出力】
{output[:1500]}

【レビュー観点】
1. 内容の正確性 - 技術的に正しい情報か
2. 実用性 - 実際に実装可能な内容か
3. 完全性 - 要件をすべて満たしているか
4. 具体性 - 具体例やコード例が含まれているか
5. 構成 - 論理的で読みやすい構成か

【レビュー形式】
以下の項目ごとに詳細に評価してください:

## 総合評価: X/10

## 詳細評価:

### ✅ 優れている点:
- [具体的な優れている点を列挙]

### ❌ 改善が必要な点:
- [具体的な問題点を列挙]

### 💡 具体的な改善提案:
- [具体的な改善方法を提案]

## 評価根拠:
[なぜその評価点なのかの具体的な根拠]

必ず1-10の整数で評価し、具体的な根拠を示してください。"""
            
            await self.browser.send_prompt(review_prompt)
            await self.browser.wait_for_text_generation(max_wait=60)
            review_text = await self.browser.extract_latest_text_response()
            
            return self._parse_content_review(review_text, output)
            
        except Exception as e:
            return self._create_error_review(f"コンテンツレビューエラー: {e}")
    
    def _parse_content_review(self, review_text: str, original_output: str) -> Dict:
        """レビューテキストを解析"""
        if not review_text:
            return self._create_error_review("レビュー結果が空です")
        
        # スコア抽出
        score = 0
        score_patterns = [
            r'総合評価[：:]\s*(\d+)/10',
            r'評価[：:]\s*(\d+)/10',
            r'(\d+)/10'
        ]
        
        for pattern in score_patterns:
            match = re.search(pattern, review_text)
            if match:
                score = int(match.group(1))
                if 1 <= score <= 10:
                    break
        
        # セクション抽出
        strengths = self._extract_section(review_text, '優れている点')
        improvements = self._extract_section(review_text, '改善が必要な点')
        suggestions = self._extract_section(review_text, '具体的な改善提案')
        rationale = self._extract_section(review_text, '評価根拠')
        
        # 異常値チェック
        if score <= 0 or score > 10:
            score = 5
            rationale = ["スコア抽出に問題があったため保守的評価"]
        
        return {
            "reviewer_type": "content_quality",
            "score": score,
            "strengths": strengths,
            "improvements_needed": improvements,
            "suggestions": suggestions,
            "rationale": rationale,
            "full_review": review_text[:1000],
            "output_length": len(original_output)
        }
    
    def _extract_section(self, text: str, section_name: str) -> List[str]:
        """特定のセクションを抽出"""
        items = []
        patterns = [
            f'{section_name}[：:](.*?)(?=###|##|$)',
            f'{section_name}.*?\\n(.*?)(?=###|##|$)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.DOTALL)
            if match:
                content = match.group(1).strip()
                # 箇条書きを分割
                lines = [line.strip(' -•*') for line in content.split('\n') if line.strip()]
                items.extend(lines)
                break
        
        return items if items else [f"{section_name}の詳細情報なし"]
    
    def _create_error_review(self, error_msg: str) -> Dict:
        """エラーレビューを作成"""
        return {
            "reviewer_type": "content_quality",
            "score": 5,
            "strengths": [],
            "improvements_needed": [error_msg],
            "suggestions": ["レビュープロセスの再実行を推奨"],
            "rationale": ["レビュー処理中にエラーが発生"],
            "full_review": error_msg,
            "output_length": 0
        }

class TechnicalFeasibilityReviewer:
    """技術的実現性レビューエージェント"""
    
    def __init__(self, browser):
        self.browser = browser
    
    async def review_technical_feasibility(self, task_description: str, output: str) -> Dict:
        """技術的実現性をレビュー"""
        try:
            review_prompt = f"""以下の技術提案の実現可能性を専門家の視点でレビューしてください。

【提案内容】
{task_description}

【技術的詳細】
{output[:1200]}

【レビュー観点】
1. 技術的正確性 - 提案されている技術が正しいか
2. 実装可能性 - 実際のプロジェクトで実装可能か
3. ベストプラクティス - 業界標準に沿っているか
4. パフォーマンス - 効率的な実装方法か
5. 保守性 - 長期運用が可能な設計か

【評価項目】
- 技術的精度 (1-10点)
- 実装容易性 (1-10点)
- 拡張性 (1-10点)

具体的な技術的問題点や改善案があれば詳細に記述してください。"""
            
            await self.browser.send_prompt(review_prompt)
            await self.browser.wait_for_text_generation(max_wait=60)
            review_text = await self.browser.extract_latest_text_response()
            
            return self._parse_technical_review(review_text)
            
        except Exception as e:
            return self._create_tech_error_review(f"技術レビューエラー: {e}")
    
    def _parse_technical_review(self, review_text: str) -> Dict:
        """技術レビューを解析"""
        if not review_text:
            return self._create_tech_error_review("技術レビュー結果が空です")
        
        # 技術スコアの抽出（複数スコアの平均）
        tech_scores = []
        score_patterns = [
            r'技術的精度.*?(\d+)[点/]',
            r'実装容易性.*?(\d+)[点/]',
            r'拡張性.*?(\d+)[点/]',
            r'(\d+)/10'
        ]
        
        for pattern in score_patterns:
            matches = re.findall(pattern, review_text)
            for match in matches:
                score = int(match)
                if 1 <= score <= 10:
                    tech_scores.append(score)
        
        avg_score = sum(tech_scores) / len(tech_scores) if tech_scores else 5
        
        # 技術的問題点の抽出
        issues = self._extract_technical_issues(review_text)
        
        return {
            "reviewer_type": "technical_feasibility",
            "score": round(avg_score, 1),
            "technical_issues": issues,
            "component_scores": {
                "accuracy": tech_scores[0] if len(tech_scores) > 0 else 5,
                "implementability": tech_scores[1] if len(tech_scores) > 1 else 5,
                "scalability": tech_scores[2] if len(tech_scores) > 2 else 5
            },
            "full_review": review_text[:800]
        }
    
    def _extract_technical_issues(self, text: str) -> List[str]:
        """技術的問題点を抽出"""
        issues = []
        # 問題点を示すキーワードパターン
        issue_indicators = [
            r'問題点[：:](.*?)(?=改善案|解決策|$)',
            r'改善が必要[：:](.*?)(?=推奨|$)',
            r'注意点[：:](.*?)(?=アドバイス|$)'
        ]
        
        for pattern in issue_indicators:
            match = re.search(pattern, text, re.DOTALL)
            if match:
                issues_text = match.group(1)
                # 箇条書きを分割
                lines = [line.strip(' -•*') for line in issues_text.split('\n') if line.strip()]
                issues.extend(lines)
        
        return issues if issues else ["特筆すべき技術的問題は見つかりませんでした"]
    
    def _create_tech_error_review(self, error_msg: str) -> Dict:
        """技術レビューエラーを作成"""
        return {
            "reviewer_type": "technical_feasibility",
            "score": 5,
            "technical_issues": [error_msg],
            "component_scores": {"accuracy": 5, "implementability": 5, "scalability": 5},
            "full_review": error_msg
        }

class WordPressImplementationReviewer:
    """WordPress実装レビューエージェント"""
    
    def __init__(self, browser):
        self.browser = browser
    
    async def review_wordpress_implementation(self, task_description: str, output: str) -> Dict:
        """WordPress実装の適切さをレビュー"""
        try:
            review_prompt = f"""以下のWordPress実装提案を専門家の視点でレビューしてください。

【実装要件】
{task_description}

【提案実装】
{output[:1200]}

【レビュー観点】
1. WordPress標準への準拠 - WordPressのコーディング標準に沿っているか
2. セキュリティ - 安全な実装方法か
3. パフォーマンス - 効率的な実装か
4. メンテナンス性 - 保守しやすいコードか
5. プラグイン/テーマの互換性 - 他のコンポーネントと競合しないか

【評価項目】
- WordPress適合性 (1-10点)
- セキュリティ対策 (1-10点)
- パフォーマンス最適化 (1-10点)

WordPress開発のベストプラクティスに照らして詳細な評価をお願いします。"""
            
            await self.browser.send_prompt(review_prompt)
            await self.browser.wait_for_text_generation(max_wait=60)
            review_text = await self.browser.extract_latest_text_response()
            
            return self._parse_wp_review(review_text)
            
        except Exception as e:
            return self._create_wp_error_review(f"WordPressレビューエラー: {e}")
    
    def _parse_wp_review(self, review_text: str) -> Dict:
        """WordPressレビューを解析"""
        if not review_text:
            return self._create_wp_error_review("WordPressレビュー結果が空です")
        
        # WordPress関連スコアの抽出
        wp_scores = []
        score_patterns = [
            r'適合性.*?(\d+)[点/]',
            r'セキュリティ.*?(\d+)[点/]',
            r'パフォーマンス.*?(\d+)[点/]',
            r'(\d+)/10'
        ]
        
        for pattern in score_patterns:
            matches = re.findall(pattern, review_text)
            for match in matches:
                score = int(match)
                if 1 <= score <= 10:
                    wp_scores.append(score)
        
        avg_score = sum(wp_scores) / len(wp_scores) if wp_scores else 5
        
        # WordPress固有の問題点抽出
        wp_issues = self._extract_wp_issues(review_text)
        
        return {
            "reviewer_type": "wordpress_implementation",
            "score": round(avg_score, 1),
            "wordpress_issues": wp_issues,
            "component_scores": {
                "compatibility": wp_scores[0] if len(wp_scores) > 0 else 5,
                "security": wp_scores[1] if len(wp_scores) > 1 else 5,
                "performance": wp_scores[2] if len(wp_scores) > 2 else 5
            },
            "full_review": review_text[:800]
        }
    
    def _extract_wp_issues(self, text: str) -> List[str]:
        """WordPress固有の問題点を抽出"""
        issues = []
        wp_keywords = ['セキュリティ', 'パフォーマンス', '互換性', '標準', 'ベストプラクティス']
        
        # WordPress関連の問題点を検索
        for keyword in wp_keywords:
            pattern = f'{keyword}.*?[問題|懸念|改善][：:](.*?)(?=\.|\n|$)'
            matches = re.findall(pattern, text)
            for match in matches:
                if match.strip():
                    issues.append(f"{keyword}: {match.strip()}")
        
        return issues if issues else ["WordPress実装上の特筆すべき問題は見つかりませんでした"]
    
    def _create_wp_error_review(self, error_msg: str) -> Dict:
        """WordPressレビューエラーを作成"""
        return {
            "reviewer_type": "wordpress_implementation",
            "score": 5,
            "wordpress_issues": [error_msg],
            "component_scores": {"compatibility": 5, "security": 5, "performance": 5},
            "full_review": error_msg
        }

