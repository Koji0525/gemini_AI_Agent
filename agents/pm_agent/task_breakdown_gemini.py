#!/usr/bin/env python3
"""
PM Agent - Gemini統合版タスク分解エージェント
簡潔なタスクをGemini AIを使って詳細な実行可能タスクに分解
"""
import asyncio
import json
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

# 詳細記述テンプレートをインポート
import sys
from agents.pm_agent.task_description_template import TaskDescriptionTemplate


class GeminiTaskBreakdownAgent:
    """Gemini AIを使用したタスク分解エージェント"""
    
    def __init__(self, sheets_manager, browser_controller):
        """
        初期化
        
        Args:
            sheets_manager: GoogleSheetsManager インスタンス
            browser_controller: BrowserController インスタンス（Gemini連携用）
        """
        self.sheets_manager = sheets_manager
        self.browser = browser_controller
        self.template = TaskDescriptionTemplate()
        
        print("🤖 Gemini統合版TaskBreakdownAgent初期化完了")
    
    async def generate_tasks_for_goal(
        self,
        goal_id: str,
        goal_title: str,
        goal_description: str,
        context: Dict[str, Any] = None,
        max_tasks: int = 5
    ) -> List[Dict[str, Any]]:
        """
        目標に対してGemini AIを使用してタスクを生成
        
        Args:
            goal_id: 目標ID
            goal_title: 目標タイトル
            goal_description: 目標の説明
            context: 追加のコンテキスト情報
            max_tasks: 生成する最大タスク数（デフォルト5）
        
        Returns:
            生成されたタスクのリスト
        """
        print(f"\n🎯 目標{goal_id}のタスク分解を開始（Gemini使用）...")
        print(f"   タイトル: {goal_title}")
        print(f"   最大タスク数: {max_tasks}")
        
        # ステップ1: 既存タスクを取得
        existing_tasks = await self._get_existing_tasks(goal_id)
        print(f"✅ 既存タスク: {len(existing_tasks)}件")
        
        # ステップ2: Geminiにタスク分解を依頼
        generated_tasks = await self._generate_tasks_with_gemini(
            goal_id=goal_id,
            goal_title=goal_title,
            goal_description=goal_description,
            existing_tasks=existing_tasks,
            context=context,
            max_tasks=max_tasks
        )
        
        print(f"✅ {len(generated_tasks)}個のタスクを生成しました")
        
        return generated_tasks
    
    async def _get_existing_tasks(self, goal_id: str) -> List[Dict[str, Any]]:
        """既存のタスクを取得"""
        try:
            # 直接 pm_tasks シートを指定
            all_tasks = self.sheets_manager.get_all_data("pm_tasks")
            
            # 該当目標のタスクのみ抽出
            existing = []
            for task in all_tasks:
                if len(task) > 0 and str(task[0]).startswith(str(goal_id)):
                    existing.append({
                        "task_id": task[0] if len(task) > 0 else "",
                        "title": task[1] if len(task) > 1 else "",
                        "status": task[4] if len(task) > 4 else "pending"
                    })
            
            return existing
        except Exception as e:
            print(f"⚠️ 既存タスク取得エラー: {e}")
            return []
    
    async def _generate_tasks_with_gemini(
        self,
        goal_id: str,
        goal_title: str,
        goal_description: str,
        existing_tasks: List[Dict],
        context: Dict[str, Any],
        max_tasks: int
    ) -> List[Dict[str, Any]]:
        """
        Gemini AIを使用してタスクを生成
        """
        print("\n🤖 Geminiにタスク分解を依頼中...")
        
        # タスク分解プロンプトを構築
        prompt = self._build_task_breakdown_prompt(
            goal_id=goal_id,
            goal_title=goal_title,
            goal_description=goal_description,
            existing_tasks=existing_tasks,
            context=context,
            max_tasks=max_tasks
        )
        
        try:
            # Geminiにプロンプトを送信
            print("📤 プロンプト送信中...")
            response = await self.browser.send_prompt(prompt)
            
            # レスポンスを待機（長文なので20秒待機）
            await asyncio.sleep(20)
            print("⏳ さらに10秒追加待機して完全なレスポンスを取得...")
            await asyncio.sleep(10)
            
            # 最新のレスポンスを取得
            print("📥 レスポンス取得中...")
            gemini_response = await self.browser.extract_latest_text_response()
            
            print(f"✅ Geminiからレスポンスを取得（{len(gemini_response)}文字）")
            
            # デバッグ: レスポンスの内容を確認
            separator = "=" * 70
            print(f"\n{separator}")
            print("📋 Geminiレスポンス（先頭500文字）:")
            print(separator)
            print(gemini_response[:500])
            print(separator)
            print("📋 Geminiレスポンス（末尾500文字）:")
            print(separator)
            print(gemini_response[-500:])
            print(f"{separator}\n")
            
            # レスポンスをパース
            tasks = self._parse_gemini_response(gemini_response, goal_id)
            
            return tasks
            
        except Exception as e:
            print(f"❌ Gemini生成エラー: {e}")
            print("💡 フォールバック: 基本的なタスクを生成します")
            return self._generate_fallback_tasks(goal_id, goal_title, max_tasks)
    
    def _build_task_breakdown_prompt(
        self,
        goal_id: str,
        goal_title: str,
        goal_description: str,
        existing_tasks: List[Dict],
        context: Dict[str, Any],
        max_tasks: int
    ) -> str:
        """タスク分解用のプロンプトを構築"""
        
        # 既存タスクの情報
        existing_info = ""
        if existing_tasks:
            existing_info = "\n【既存のタスク】\n"
            for task in existing_tasks[:10]:  # 最大10件
                existing_info += f"- {task['title']} (ステータス: {task['status']})\n"
        
        # コンテキスト情報
        context_info = ""
        if context:
            context_info = "\n【プロジェクトコンテキスト】\n"
            for key, value in context.items():
                context_info += f"- {key}: {value}\n"
        
        prompt = f"""
あなたは経験豊富なプロジェクトマネージャーです。
以下の目標を達成するために、実行可能な小タスクに分解してください。

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
【目標ID】
{goal_id}

【目標タイトル】
{goal_title}

【目標の説明】
{goal_description}
{context_info}
{existing_info}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【タスク分解の指示】

1. **タスク数**: {max_tasks}個のタスクに分解してください
2. **タスクの粒度**: 各タスクは1-2日で完了できる大きさにしてください
3. **詳細度**: 各タスクには以下を含めてください：
   - 【目的】なぜこのタスクが必要か
   - 【ゴール条件】何が達成されれば完了か
   - 【具体的要件】何を作成/設定するか
   - 【完了判定】どうやって確認するか（チェックリスト形式）
   - 【注意事項】気をつけるべきポイント

4. **依存関係**: 先行タスクがある場合は明記してください
5. **実行タイプ**: タスクの種類を明記してください
   - "gemini": Gemini AIでの設計・分析タスク
   - "wordpress": WordPressでの実装タスク

【出力形式】
以下のJSON配列形式で出力してください：
```json
[
  {{
    "title": "タスクのタイトル（簡潔に20-30文字）",
    "description": "【目的】\\n...\\n【ゴール条件】\\n...\\n【具体的要件】\\n...\\n【完了判定】\\n...\\n【注意事項】\\n...",
    "agent": "design/dev/wordpress/review",
    "priority": "high/medium/low",
    "dependencies": "依存するタスク番号（カンマ区切り、例: 1,2）",
    "execution_type": "gemini/wordpress",
    "estimated_hours": 8
  }}
]
```

**重要**: 
- descriptionには必ず5つのセクション（目的、ゴール条件、具体的要件、完了判定、注意事項）を含めてください
- WordPress関連タスクの場合、管理画面での確認方法を完了判定に明記してください
- JSON形式を厳守してください（正しいエスケープ、カンマ、括弧）
"""
        return prompt
    
    def _parse_gemini_response(self, response: str, goal_id: str) -> List[Dict[str, Any]]:
        """Geminiのレスポンスをパースしてタスクリストに変換"""
        
        print("\n📋 Geminiレスポンスをパース中...")
        
        try:
            # JSON抽出の改善版
            json_str = None
            
            # パターン1: ```json ... ``` で囲まれたJSON
            json_match = re.search(r'```json\s*([\s\S]*?)\s*```', response)
            if json_match:
                json_str = json_match.group(1)
                print("✅ パターン1でJSON抽出: ```json ブロック")
            
            # パターン2: JSON[ ... ] の形式（最後の ] まで取得）
            if not json_str:
                # "JSON[" の位置を探す
                json_start = response.find('JSON[')
                if json_start != -1:
                    # JSON[ 以降の最後の ] を見つける
                    json_str_candidate = response[json_start + 4:]  # "JSON" の4文字をスキップ
                    
                    # 括弧の対応を確認しながら終端を探す
                    bracket_count = 0
                    end_pos = -1
                    for i, char in enumerate(json_str_candidate):
                        if char == '[':
                            bracket_count += 1
                        elif char == ']':
                            bracket_count -= 1
                            if bracket_count == 0:
                                end_pos = i + 1
                                break
                    
                    if end_pos > 0:
                        json_str = json_str_candidate[:end_pos]
                        print(f"✅ パターン2でJSON抽出: JSON[ ... ] 形式 ({end_pos}文字)")
            
            # パターン3: [ ... ] の形式（配列のみ）
            if not json_str:
                array_match = re.search(r'(\[\s*\{[\s\S]*?\}\s*\])', response)
                if array_match:
                    json_str = array_match.group(1)
                    print("✅ パターン3でJSON抽出: [ ... ] 配列のみ")
            
            if json_str:
                print(f"✅ JSON抽出成功（{len(json_str)}文字）")
                
                # JSON完全性チェック
                open_brackets = json_str.count('[')
                close_brackets = json_str.count(']')
                open_braces = json_str.count('{')
                close_braces = json_str.count('}')
                
                print(f"📊 JSON構造チェック:")
                print(f"   [ : {open_brackets}, ] : {close_brackets}")
                print(f"   {{ : {open_braces}, }} : {close_braces}")
                
                if open_brackets != close_brackets or open_braces != close_braces:
                    print("⚠️ JSONが不完全です（括弧の数が一致しません）")
                    print("💡 レスポンスの待機時間が不足している可能性があります")
                
                # 制御文字のエスケープ処理（初心者向け説明付き）
                print("🔧 JSONをパース中...")
                # 実際の改行を \n に置き換え（JSONで正しく読めるようにする）
                print(f"✅ JSON準備完了（{len(json_str)}文字）")
                
                tasks_data = json.loads(json_str)
                
                # タスクデータを整形
                formatted_tasks = []
                for i, task in enumerate(tasks_data, 1):
                    formatted_task = {
                        "goal_id": goal_id,
                        "task_number": i,
                        "title": task.get("title", f"タスク{i}"),
                        "description": task.get("description", ""),
                        "agent": task.get("agent", "dev"),
                        "priority": task.get("priority", "medium"),
                        "dependencies": task.get("dependencies", ""),
                        "execution_type": task.get("execution_type", "gemini"),
                        "estimated_hours": task.get("estimated_hours", 8)
                    }
                    formatted_tasks.append(formatted_task)
                
                print(f"✅ {len(formatted_tasks)}個のタスクをパース成功")
                return formatted_tasks
                
            else:
                print("⚠️ JSONブロックが見つかりませんでした")
                # フォールバック: テキストから手動でパース
                return self._parse_text_response(response, goal_id)
                
        except json.JSONDecodeError as e:
            print(f"❌ JSONパースエラー: {e}")
            return self._parse_text_response(response, goal_id)
        except Exception as e:
            print(f"❌ パースエラー: {e}")
            return []
    
    def _parse_text_response(self, response: str, goal_id: str) -> List[Dict[str, Any]]:
        """
        JSONパースに失敗した場合のフォールバック
        テキストから手動でタスクを抽出
        """
        print("�� テキストベースのパースを試行中...")
        
        tasks = []
        # タスクのパターンを検出（タイトルベース）
        title_pattern = r'(?:タスク|Task)\s*(\d+)[：:]\s*(.+?)(?=\n|$)'
        matches = re.finditer(title_pattern, response)
        
        for match in matches:
            task_num = match.group(1)
            title = match.group(2).strip()
            
            # 簡易的なタスク構造を作成
            task = {
                "goal_id": goal_id,
                "task_number": int(task_num),
                "title": title,
                "description": f"【目的】\n{title}を実行する\n\n【完了判定】\n✅ タスクが完了していること",
                "agent": "dev",
                "priority": "medium",
                "dependencies": "",
                "execution_type": "gemini",
                "estimated_hours": 8
            }
            tasks.append(task)
        
        if tasks:
            print(f"✅ テキストから{len(tasks)}個のタスクを抽出")
        
        return tasks
    
    def _generate_fallback_tasks(
        self,
        goal_id: str,
        goal_title: str,
        max_tasks: int
    ) -> List[Dict[str, Any]]:
        """Gemini失敗時のフォールバックタスク生成"""
        
        print(f"🔄 フォールバックタスクを生成中（{max_tasks}件）...")
        
        fallback_tasks = []
        
        # 基本的なフェーズに分解
        phases = [
            ("要件定義", "design", "gemini"),
            ("設計書作成", "design", "gemini"),
            ("実装", "dev", "wordpress"),
            ("テスト", "review", "gemini"),
            ("ドキュメント作成", "design", "gemini")
        ]
        
        for i in range(min(max_tasks, len(phases))):
            phase_name, agent, exec_type = phases[i]
            
            task = {
                "goal_id": goal_id,
                "task_number": i + 1,
                "title": f"{goal_title} - {phase_name}",
                "description": self.template.enhance_task_description(
                    f"{goal_title}の{phase_name}を実行",
                    context={"フェーズ": phase_name}
                ),
                "agent": agent,
                "priority": "high" if i < 2 else "medium",
                "dependencies": str(i) if i > 0 else "",
                "execution_type": exec_type,
                "estimated_hours": 8
            }
            fallback_tasks.append(task)
        
        return fallback_tasks


# テスト実行
async def test_gemini_task_breakdown():
    """Gemini統合版のテスト"""
    print("=" * 70)
    print("🧪 Gemini統合版TaskBreakdownAgentのテスト")
    print("=" * 70)
    
    # モックオブジェクトでテスト
    class MockSheets:
        def get_sheet_name_from_cache(self, name):
            return "pm_tasks"
        def get_all_data(self, sheet):
            return []
    
    class MockBrowser:
        async def send_prompt(self, prompt):
            print(f"📤 プロンプト送信（{len(prompt)}文字）")
            return True
        
        async def extract_latest_text_response(self):
            # サンプルレスポンス
            return '''
```json
[
  {
    "title": "M&A案件CPT要件定義",
    "description": "【目的】\\nM&A案件管理のためのカスタム投稿タイプの要件を明確化\\n\\n【ゴール条件】\\n- 必要なフィールドが特定されている\\n- データ構造が設計されている\\n\\n【具体的要件】\\n1. 案件情報フィールドの洗い出し\\n2. 必須・任意の区分\\n\\n【完了判定】\\n✅ 要件定義書が作成されている\\n✅ レビュー済み\\n\\n【注意事項】\\n- ウズベキスタンの商習慣を考慮",
    "agent": "design",
    "priority": "high",
    "dependencies": "",
    "execution_type": "gemini",
    "estimated_hours": 4
  },
  {
    "title": "M&A案件CPT実装",
    "description": "【目的】\\nM&A案件を管理するカスタム投稿タイプを作成\\n\\n【ゴール条件】\\n- CPTがWordPressに登録されている\\n- 管理画面に表示される\\n\\n【具体的要件】\\n- 投稿タイプ名: ma_deal\\n- 基本フィールド設定\\n\\n【完了判定】\\n✅ 管理画面にメニュー表示\\n✅ 投稿作成可能\\n\\n【注意事項】\\n- スラッグは英数字のみ",
    "agent": "wordpress",
    "priority": "high",
    "dependencies": "1",
    "execution_type": "wordpress",
    "estimated_hours": 6
  }
]
```
'''
    
    agent = GeminiTaskBreakdownAgent(MockSheets(), MockBrowser())
    
    tasks = await agent.generate_tasks_for_goal(
        goal_id="4",
        goal_title="ウズベキスタンM&A案件管理システム構築",
        goal_description="WordPressでM&A案件を管理するシステムを作成",
        context={"技術": "WordPress + ACF", "期限": "2週間"},
        max_tasks=3
    )
    
    print("\n" + "=" * 70)
    print("📋 生成されたタスク:")
    print("=" * 70)
    for task in tasks:
        print(f"\nタスク{task['task_number']}: {task['title']}")
        print(f"  エージェント: {task['agent']}")
        print(f"  実行タイプ: {task['execution_type']}")
        print(f"  説明（先頭100文字）: {task['description'][:100]}...")


if __name__ == "__main__":
    asyncio.run(test_gemini_task_breakdown())
