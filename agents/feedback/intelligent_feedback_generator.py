"""
Intelligent Feedback Generator v1.0
AIが具体的で実行可能な改善提案を生成
"""
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import json

project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

from tools.sheets_manager import GoogleSheetsManager
from configuration.config_loader import ConfigLoader
from agents.advanced_analytics.execution_analyzer import ExecutionAnalyzer
from agents.advanced_analytics.pattern_learner import PatternLearner
from browser_control.gemini_api_client import GeminiAPIClient


class IntelligentFeedbackGenerator:
    """AI駆動の改善提案生成エンジン"""
    
    def __init__(self, sheets_manager: GoogleSheetsManager, gemini_client: GeminiAPIClient):
        self.sheets = sheets_manager
        self.gemini = gemini_client
        self.analyzer = ExecutionAnalyzer(sheets_manager)
        self.learner = PatternLearner(sheets_manager)
    
    async def generate_improvement_suggestions(self) -> List[Dict[str, Any]]:
        """改善提案を生成"""
        
        print("🤖 AI駆動改善提案を生成中...\n")
        
        # 1. データ分析
        print("📊 ステップ1: データ分析")
        analysis = await self.analyzer.analyze_execution_patterns()
        patterns = {
            "success_patterns": await self.learner.learn_success_patterns(),
            "failure_patterns": await self.learner.learn_failure_patterns()
        }
        
        # 2. 改善領域の特定
        print("🔍 ステップ2: 改善領域の特定")
        improvement_areas = self._identify_improvement_areas(analysis, patterns)
        
        print(f"   特定された改善領域: {len(improvement_areas)}件")
        
        # 3. Gemini APIで改善提案生成
        print("🤖 ステップ3: AI改善提案生成")
        suggestions = []
        
        for i, area in enumerate(improvement_areas[:5], 1):  # 最大5件
            print(f"   {i}/{min(len(improvement_areas), 5)}: {area['title']}")
            suggestion = await self._generate_suggestion_with_ai(area, analysis, patterns)
            if suggestion:
                suggestions.append(suggestion)
        
        # 4. 優先度付け
        print("📊 ステップ4: 優先度付けとROI計算")
        prioritized_suggestions = self._prioritize_suggestions(suggestions)
        
        print(f"\n✅ {len(prioritized_suggestions)}件の改善提案を生成しました\n")
        
        return prioritized_suggestions
    
    def _identify_improvement_areas(
        self, analysis: Dict[str, Any], patterns: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """改善領域を特定"""
        
        areas = []
        
        # エラー率が高い場合
        success_rate = analysis.get("success_rate", 100)
        if success_rate < 95:
            areas.append({
                "category": "reliability",
                "title": "システム成功率の向上",
                "current_value": success_rate,
                "target_value": 95,
                "context": f"現在の成功率は{success_rate:.1f}%です"
            })
        
        # タイムアウトエラーがある場合
        errors = analysis.get("common_errors", [])
        timeout_errors = [e for e in errors if "timeout" in e.get("error_type", "").lower()]
        if timeout_errors:
            areas.append({
                "category": "performance",
                "title": "APIタイムアウトの削減",
                "current_value": timeout_errors[0].get("count", 0),
                "target_value": 0,
                "context": f"タイムアウトエラーが{timeout_errors[0].get('count', 0)}件発生"
            })
        
        # 成功率が低いエージェントがある場合
        agent_perf = analysis.get("agent_performance", [])
        low_performers = [a for a in agent_perf if a.get("success_rate", 100) < 80]
        if low_performers:
            for agent in low_performers[:2]:  # 上位2つ
                areas.append({
                    "category": "reliability",
                    "title": f"{agent['agent']}エージェントの改善",
                    "current_value": agent.get("success_rate", 0),
                    "target_value": 90,
                    "context": f"{agent['agent']}の成功率は{agent.get('success_rate', 0):.1f}%"
                })
        
        # パフォーマンス改善の機会
        if analysis.get("total_executions", 0) > 100:
            areas.append({
                "category": "performance",
                "title": "実行速度の最適化",
                "current_value": analysis.get("average_execution_time", 0),
                "target_value": 0,
                "context": "大量タスク処理のパフォーマンス最適化"
            })
        
        # ユーザビリティ改善
        areas.append({
            "category": "usability",
            "title": "ログとレポートの改善",
            "current_value": 0,
            "target_value": 100,
            "context": "より詳細で分かりやすいログとレポート"
        })
        
        return areas
    
    async def _generate_suggestion_with_ai(
        self, area: Dict[str, Any], analysis: Dict[str, Any], patterns: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """AIで改善提案を生成"""
        
        # Gemini APIへのプロンプト
        prompt = f"""
あなたはWordPress自動構築システムの改善提案エキスパートです。

【改善領域】
- カテゴリ: {area['category']}
- タイトル: {area['title']}
- 現状: {area['context']}
- 現在値: {area['current_value']}
- 目標値: {area['target_value']}

【システム分析データ】
- 総実行数: {analysis.get('total_executions', 0)}件
- 成功率: {analysis.get('success_rate', 0):.1f}%

以下の形式で具体的な改善提案を生成してください（JSON形式）：

{{
  "description": "改善提案の説明（2-3文で簡潔に）",
  "expected_benefit": "期待される効果（具体的な数値目標を含む）",
  "difficulty": "易/中/難のいずれか",
  "implementation_steps": ["ステップ1", "ステップ2", "ステップ3"],
  "risks": ["リスク1", "リスク2"]
}}
"""
        
        try:
            # Gemini APIで生成（awaitを追加！）
            response = await self.gemini.send_prompt(prompt)
            
            # JSONを抽出
            response_text = response.strip()
            
            # ```json ブロックを削除
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            suggestion_data = json.loads(response_text)
            
            # ROIスコアを計算
            roi_score = self._calculate_roi(
                area['category'],
                suggestion_data.get('difficulty', '中'),
                area.get('current_value', 0),
                area.get('target_value', 100)
            )
            
            # 優先度を決定
            priority = self._determine_priority(area['category'], roi_score)
            
            print(f"      ✅ AI提案生成成功")
            
            return {
                "suggestion_id": f"sug_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "timestamp": datetime.now().isoformat(),
                "priority": priority,
                "category": area['category'],
                "title": area['title'],
                "description": suggestion_data.get('description', ''),
                "expected_benefit": suggestion_data.get('expected_benefit', ''),
                "implementation_difficulty": suggestion_data.get('difficulty', '中'),
                "roi_score": roi_score,
                "implementation_steps": suggestion_data.get('implementation_steps', []),
                "risks": suggestion_data.get('risks', []),
                "status": "pending",
                "generated_by": "AI"
            }
            
        except Exception as e:
            print(f"   ⚠️ AI生成エラー: {e}")
            
            # フォールバック: 基本的な提案を返す
            return {
                "suggestion_id": f"sug_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "timestamp": datetime.now().isoformat(),
                "priority": "中",
                "category": area['category'],
                "title": area['title'],
                "description": f"{area['title']}の改善を推奨します。{area['context']}",
                "expected_benefit": f"目標値{area['target_value']}の達成",
                "implementation_difficulty": "中",
                "roi_score": 20.0,
                "implementation_steps": ["詳細分析", "実装計画作成", "テスト実施"],
                "risks": ["実装時間の確保が必要"],
                "status": "pending",
                "generated_by": "System"
            }
    
    def _calculate_roi(
        self, category: str, difficulty: str, current_value: float, target_value: float
    ) -> float:
        """ROI（投資対効果）スコアを計算"""
        
        # カテゴリ別の重要度
        category_weight = {
            "reliability": 1.0,
            "performance": 0.8,
            "usability": 0.6
        }
        
        # 難易度別のコスト
        difficulty_cost = {
            "易": 1.0,
            "中": 2.0,
            "難": 3.0
        }
        
        # 期待される改善幅
        improvement = abs(target_value - current_value) if target_value > 0 else 50
        
        # ROI = (重要度 × 改善幅) / コスト
        roi = (category_weight.get(category, 0.7) * improvement) / difficulty_cost.get(difficulty, 2.0)
        
        return round(roi, 2)
    
    def _determine_priority(self, category: str, roi_score: float) -> str:
        """優先度を決定"""
        
        # reliabilityは常に優先度を上げる
        if category == "reliability":
            roi_score *= 1.2
        
        if roi_score >= 30:
            return "高"
        elif roi_score >= 15:
            return "中"
        else:
            return "低"
    
    def _prioritize_suggestions(self, suggestions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """提案を優先度順にソート"""
        
        # ROIスコアと優先度でソート
        priority_order = {"高": 3, "中": 2, "低": 1}
        
        sorted_suggestions = sorted(
            suggestions,
            key=lambda x: (
                priority_order.get(x.get("priority", "低"), 1),
                x.get("roi_score", 0)
            ),
            reverse=True
        )
        
        return sorted_suggestions
    
    async def save_suggestions_to_sheet(self, suggestions: List[Dict[str, Any]]) -> bool:
        """改善提案をGoogle Sheetsに保存"""
        
        print("💾 改善提案をGoogle Sheetsに保存中...")
        
        try:
            spreadsheet = self.sheets.gc.open_by_key(self.sheets.spreadsheet_id)
            worksheet = spreadsheet.worksheet("improvement_suggestions")
            
            for suggestion in suggestions:
                row = [
                    suggestion.get("suggestion_id", ""),
                    suggestion.get("timestamp", ""),
                    suggestion.get("priority", ""),
                    suggestion.get("category", ""),
                    suggestion.get("title", ""),
                    suggestion.get("description", "")[:500],
                    suggestion.get("expected_benefit", "")[:300],
                    suggestion.get("implementation_difficulty", ""),
                    suggestion.get("roi_score", 0),
                    suggestion.get("status", "pending"),
                    suggestion.get("generated_by", "AI"),
                    "",  # approved_by
                    "",  # approved_at
                    json.dumps(suggestion.get("implementation_steps", []), ensure_ascii=False)[:500],
                    ""   # result
                ]
                
                worksheet.append_row(row)
            
            print(f"✅ {len(suggestions)}件の提案を保存しました")
            return True
            
        except Exception as e:
            print(f"❌ 保存エラー: {e}")
            return False
    
    def print_suggestions(self, suggestions: List[Dict[str, Any]]):
        """改善提案を表示"""
        
        print("\n" + "="*70)
        print("🤖 AI生成改善提案")
        print("="*70 + "\n")
        
        for i, sug in enumerate(suggestions, 1):
            priority_icon = "🔴" if sug['priority'] == "高" else "🟡" if sug['priority'] == "中" else "🟢"
            
            print(f"{i}. {priority_icon} {sug['title']}")
            print(f"   優先度: {sug['priority']} | カテゴリ: {sug['category']} | ROI: {sug['roi_score']}")
            print(f"   難易度: {sug['implementation_difficulty']}")
            print(f"\n   📝 説明:")
            print(f"   {sug['description']}")
            print(f"\n   ✨ 期待される効果:")
            print(f"   {sug['expected_benefit']}")
            print(f"\n   �� 実装ステップ:")
            for step_idx, step in enumerate(sug.get('implementation_steps', [])[:3], 1):
                print(f"   {step_idx}. {step}")
            if len(sug.get('implementation_steps', [])) > 3:
                print(f"   ... 他 {len(sug['implementation_steps']) - 3} ステップ")
            
            if sug.get('risks'):
                print(f"\n   ⚠️ リスク:")
                for risk in sug.get('risks', [])[:2]:
                    print(f"   • {risk}")
            
            print("\n" + "-"*70 + "\n")


async def main():
    """メイン実行"""
    print("🚀 Intelligent Feedback Generator を起動\n")
    
    # 設定読み込み
    config = ConfigLoader()
    sheets = GoogleSheetsManager(
        spreadsheet_id=config.get("SPREADSHEET_ID"),
        service_account_file=config.get("GOOGLE_SERVICE_ACCOUNT_FILE")
    )
    
    # Gemini API クライアント
    gemini = GeminiAPIClient()
    
    # フィードバックジェネレーター
    generator = IntelligentFeedbackGenerator(sheets, gemini)
    
    # 改善提案を生成
    suggestions = await generator.generate_improvement_suggestions()
    
    # 表示
    generator.print_suggestions(suggestions)
    
    # Google Sheetsに保存
    await generator.save_suggestions_to_sheet(suggestions)
    
    # JSONで保存
    output_file = Path("agent_outputs/improvement_suggestions.json")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(suggestions, f, indent=2, ensure_ascii=False)
    
    print(f"💾 改善提案を保存: {output_file}")
    
    print("\n" + "="*70)
    print("✅ Phase 4-1: IntelligentFeedbackGenerator 完成！")
    print("="*70)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
