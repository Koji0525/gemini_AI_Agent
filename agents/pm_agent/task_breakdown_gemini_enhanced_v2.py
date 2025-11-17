#!/usr/bin/env python3
"""
GeminiTaskBreakdownAgent 強化版v2
詳細なタスク分解と依存関係の自動生成
"""

# 標準環境変数ローダー（必須）
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from tools.env_loader import StandardEnvLoader
if not StandardEnvLoader.load_and_verify():
    print("❌ 環境変数の読み込みに失敗しました")
    sys.exit(1)

import os
import json
import traceback
from typing import Dict, List, Any, Optional
import google.generativeai as genai
from datetime import datetime


class GeminiTaskBreakdownAgentV2:
    """Gemini APIでタスク分解（強化版v2）"""

    def __init__(self, knowledge_manager=None):
        """
        初期化
        
        Args:
            knowledge_manager: KnowledgeBaseManager（オプション）
        """
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY環境変数が必要です")

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-2.0-flash-exp")
        self.knowledge_manager = knowledge_manager
        print(f"✅ GeminiTaskBreakdownAgentV2 初期化完了")

    def _build_enhanced_prompt(
        self, goal_id: str, goal_description: str, knowledge_context: str = ""
    ) -> str:
        """強化版プロンプトの構築"""
        
        prompt = f"""あなたは経験豊富なプロジェクトマネージャーとして、以下の目標を実行可能な具体的タスクに分解してください。

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
【目標】
Goal ID: {goal_id}
Description: {goal_description}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【過去の成功パターン】
{knowledge_context if knowledge_context else "なし"}

【タスク分解の指針】
1. **ゴールの具体化**: 抽象的な目標は具体的な作業に落とし込む
2. **段階的アプローチ**: 調査→設計→実装→テスト→品質改善→ドキュメントの流れ
3. **依存関係の明確化**: 前提となるタスクを明記
4. **成功基準の設定**: 各タスクの完了条件を明確にする

【タスク種別】
- research: 調査・情報収集
- design: 設計・計画立案
- implementation: 実装・開発
- testing: テスト・検証
- quality_improvement: 品質改善・リファクタリング
- documentation: ドキュメント作成

【出力形式】以下のJSON配列で返してください（5〜10個のタスク）:
```json
[
  {{
    "task_type": "research",
    "title": "タスクの簡潔なタイトル",
    "description": "具体的な作業内容（何を、どのように実施するか）",
    "purpose": "このタスクの目的（なぜ必要か）",
    "success_criteria": "完了と判断する基準（何ができたら完了か）",
    "context_info": "実施時に必要な前提知識やコンテキスト",
    "required_role": "developer/designer/tester/pm",
    "priority": "high/medium/low",
    "estimated_time": "2h/4h/8h/16h",
    "dependencies": "前提となるタスク番号（1,2,3など。なければ空文字）"
  }},
  ...
]
```

【重要な注意事項】
- 各タスクは単独で実行可能な粒度にする
- descriptionは具体的な手順を含める
- success_criteriaは測定可能な基準にする
- 依存関係は実行順序を考慮して、タスク番号（1,2,3など）で設定する
- タスクは論理的な順序で並べる（調査→設計→実装→テスト）

それでは、タスク分解を開始してください。"""

        return prompt

    async def generate_tasks_for_goal(
        self,
        goal_id: str,
        goal_description: str,
        use_knowledge: bool = True
    ) -> List[Dict[str, Any]]:
        """
        目標からタスクを生成
        
        Args:
            goal_id: 目標ID
            goal_description: 目標の説明
            use_knowledge: ナレッジベース参照の有無
            
        Returns:
            タスクのリスト
        """
        print(f"\n🤖 Gemini APIでタスク分解開始")
        print(f"   Goal ID: {goal_id}")
        print(f"   Description: {goal_description[:100]}...")

        # ナレッジベースから過去の成功パターンを検索
        knowledge_context = ""
        if use_knowledge and self.knowledge_manager:
            try:
                print("📚 ナレッジベースから関連情報を検索中...")
                # キーワード抽出（簡易版）
                keywords = goal_description[:100]
                # TODO: 実際のナレッジ検索実装
                # knowledge_results = self.knowledge_manager.search_knowledge(keywords)
                knowledge_context = "（ナレッジ検索機能は今後実装）"
            except Exception as e:
                print(f"⚠️ ナレッジ検索エラー: {e}")

        # プロンプト構築
        prompt = self._build_enhanced_prompt(goal_id, goal_description, knowledge_context)
        
        try:
            print("📤 Gemini APIにリクエスト送信中...")
            response = self.model.generate_content(prompt)
            print(f"✅ レスポンス受信: {len(response.text)}文字")

            # JSON抽出
            text = response.text
            print(f"📄 レスポンス内容（最初の200文字）:\n{text[:200]}...")
            
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]

            print(f"🔍 JSON抽出結果:\n{text[:300]}...")

            # JSONパース
            tasks_raw = json.loads(text.strip())

            if not isinstance(tasks_raw, list):
                print(f"❌ タスク形式が不正: {type(tasks_raw)}")
                return []

            print(f"✅ {len(tasks_raw)}個のタスクをパースしました")

            # タスクIDの生成と整形
            formatted_tasks = []
            for i, task in enumerate(tasks_raw, 1):
                task_id = f"{goal_id}_TASK_{i:03d}"
                
                # 依存関係の変換（タスク番号からタスクIDへ）
                dependencies = task.get("dependencies", "")
                if dependencies:
                    # カンマ区切りの番号をタスクIDに変換
                    dep_ids = []
                    for dep in str(dependencies).split(","):
                        dep = dep.strip()
                        if dep.isdigit():
                            dep_num = int(dep)
                            if 1 <= dep_num < i:  # 自分より前のタスクのみ
                                dep_ids.append(f"{goal_id}_TASK_{dep_num:03d}")
                    dependencies = ",".join(dep_ids)
                
                formatted_task = {
                    "task_id": task_id,
                    "parent_goal_id": goal_id,
                    "task_type": task.get("task_type", "implementation"),
                    "title": task.get("title", f"タスク{i}"),
                    "description": task.get("description", ""),
                    "purpose": task.get("purpose", ""),
                    "success_criteria": task.get("success_criteria", ""),
                    "context_info": task.get("context_info", ""),
                    "required_role": task.get("required_role", "developer"),
                    "priority": task.get("priority", "medium"),
                    "estimated_time": task.get("estimated_time", "4h"),
                    "dependencies": dependencies,
                    "status": "pending",
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "execution_type": "gemini"
                }
                formatted_tasks.append(formatted_task)

            print(f"✅ {len(formatted_tasks)}個のタスクを生成しました")
            
            # タスク一覧を表示
            for task in formatted_tasks:
                deps_str = f" [依存: {task['dependencies']}]" if task['dependencies'] else ""
                print(f"   📌 {task['task_id']}: {task['title']} ({task['task_type']}){deps_str}")
            
            return formatted_tasks

        except json.JSONDecodeError as e:
            print(f"❌ JSON解析エラー: {e}")
            print(f"📄 解析対象テキスト:\n{text[:500]}...")
            return []
        except Exception as e:
            print(f"❌ タスク生成エラー: {type(e).__name__}: {e}")
            traceback.print_exc()
            return []

    def convert_to_pm_tasks_format(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        タスクをpm_tasksスキーマ形式に変換
        
        Args:
            tasks: 生成されたタスクリスト
            
        Returns:
            pm_tasksスキーマに準拠したタスクリスト
        """
        pm_tasks = []
        
        for task in tasks:
            # descriptionフィールドを詳細情報で構築
            full_description = f"{task.get('title', '')}\n"
            full_description += f"【目的】{task.get('purpose', '')}\n"
            full_description += f"【作業内容】{task.get('description', '')}\n"
            full_description += f"【成功基準】{task.get('success_criteria', '')}\n"
            if task.get('context_info'):
                full_description += f"【コンテキスト】{task.get('context_info', '')}"
            
            pm_task = {
                "task_id": task.get("task_id", ""),
                "parent_goal_id": task.get("parent_goal_id", ""),
                "description": full_description.strip(),
                "required_role": task.get("required_role", "developer"),
                "status": task.get("status", "pending"),
                "priority": task.get("priority", "medium"),
                "estimated_time": task.get("estimated_time", "4h"),
                "dependencies": task.get("dependencies", ""),
                "created_at": task.get("created_at", ""),
                "batch_id": "",
                "detail_file_path": "",
                "blank": "",
                "execution_type": task.get("execution_type", "gemini"),
            }
            pm_tasks.append(pm_task)
        
        return pm_tasks


# テスト用のメイン関数
async def test_breakdown():
    """テスト実行"""
    print("=" * 60)
    print("GeminiTaskBreakdownAgentV2 テスト実行")
    print("=" * 60)
    
    agent = GeminiTaskBreakdownAgentV2()
    
    test_goal = {
        "goal_id": "GOAL_TEST_001",
        "goal_description": "ユーザー認証システムの実装（JWT認証、ログイン/ログアウト機能、セキュリティ対策を含む）"
    }
    
    tasks = await agent.generate_tasks_for_goal(
        test_goal["goal_id"],
        test_goal["goal_description"]
    )
    
    print(f"\n{'='*60}")
    print(f"📊 生成結果サマリー: {len(tasks)}個のタスク")
    print(f"{'='*60}")
    
    for task in tasks:
        print(f"\n【{task['task_id']}】{task['title']}")
        print(f"   種別: {task['task_type']}")
        print(f"   優先度: {task['priority']}")
        print(f"   見積: {task['estimated_time']}")
        print(f"   役割: {task['required_role']}")
        if task['dependencies']:
            print(f"   依存: {task['dependencies']}")
        print(f"   目的: {task['purpose'][:60]}...")
    
    # pm_tasks形式に変換
    print(f"\n{'='*60}")
    print("pm_tasks形式への変換テスト")
    print(f"{'='*60}")
    
    pm_tasks = agent.convert_to_pm_tasks_format(tasks)
    print(f"✅ pm_tasks形式への変換完了: {len(pm_tasks)}個")
    
    # 最初のタスクの詳細を表示
    if pm_tasks:
        print(f"\n【サンプル】最初のタスクの詳細:")
        first_task = pm_tasks[0]
        for key, value in first_task.items():
            if value:  # 空でない値のみ表示
                print(f"   {key}: {str(value)[:100]}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_breakdown())
