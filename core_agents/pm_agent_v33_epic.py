"""
PMAgentV33Epic - Epic分解機能を備えたプロジェクトマネージャーエージェント
既存の pm_agent_v3_fixed.py を拡張し、Epic → Story 分解機能を追加
"""

import asyncio
import logging
import os
import sys
from typing import Any, Dict, List

# 既存システムとの互換性を維持
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from knowledge_system.core_agents.knowledge_manager import KnowledgeManager
from tools.base_data_accessor import BaseDataAccessor
from tools.safe_sheets_wrapper import SafeSheetsWrapper


class EpicTaskGenerator:
    """EpicをStoryに分解するジェネレータ"""
    
    def __init__(self, knowledge_manager: KnowledgeManager):
        self.knowledge_manager = knowledge_manager
        self.logger = logging.getLogger(__name__)
    
    async def decompose_epic_to_stories(self, epic_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Epicを8-12個のStoryに分解
        
        Args:
            epic_data: Epicデータ（project_goalシートから取得）
            
        Returns:
            List[Dict]: Storyのリスト
        """
        try:
            self.logger.info(f"Epic分解開始: {epic_data.get('goal', 'Unknown')}")
            
            # ナレッジベースから関連する成功パターンを検索
            similar_patterns = await self._find_similar_epic_patterns(epic_data)
            
            # Epicの規模と複雑さに基づいてStory数を決定
            story_count = self._calculate_optimal_story_count(epic_data)
            
            # Story生成
            stories = await self._generate_stories(epic_data, story_count, similar_patterns)
            
            self.logger.info(f"Epic分解完了: {len(stories)}個のStoryを生成")
            return stories
            
        except Exception as e:
            self.logger.error(f"Epic分解中にエラー: {e}")
            return []
    
    async def _find_similar_epic_patterns(self, epic_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """ナレッジベースから類似Epicパターンを検索"""
        try:
            query = f"{epic_data.get('goal', '')} {epic_data.get('description', '')}"
            results = self.knowledge_manager.search_knowledge(
                query=query,
                category="epic_pattern",
                limit=5
            )
            return results
        except Exception as e:
            self.logger.warning(f"類似パターン検索エラー: {e}")
            return []
    
    def _calculate_optimal_story_count(self, epic_data: Dict[str, Any]) -> int:
        """Epicの規模に基づいて最適なStory数を計算"""
        # 簡易的なヒューリスティック: 説明文の長さと複雑さから判断
        description = epic_data.get('description', '')
        goal_complexity = len(description.split())
        
        if goal_complexity < 500:
            return 8  # 小規模
        elif goal_complexity < 1000:
            return 10  # 中規模
        else:
            return 12  # 大規模
    
    async def _generate_stories(self, epic_data: Dict[str, Any], story_count: int, 
                              patterns: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """実際のStoryを生成"""
        stories = []
        
        # ここではモック実装。実際にはGemini APIを使用して生成
        for i in range(story_count):
            story = {
                'epic_id': epic_data.get('id'),
                'title': f"{epic_data.get('goal', 'Epic')} - Story {i+1}",
                'description': self._generate_story_description(epic_data, i, story_count),
                'estimated_lines': self._estimate_story_lines(epic_data, story_count, i),
                'priority': self._calculate_story_priority(i, story_count),
                'dependencies': self._identify_dependencies(i, story_count),
                'acceptance_criteria': self._generate_acceptance_criteria(),
                'category': 'development'
            }
            stories.append(story)
        
        return stories
    
    def _generate_story_description(self, epic_data: Dict[str, Any], story_index: int, 
                                  total_stories: int) -> str:
        """2,500-3,000文字の詳細なStory説明を生成"""
        base_description = epic_data.get('description', '')
        goal = epic_data.get('goal', '')
        
        # モック実装 - 実際にはGemini APIを使用
        description = f"""
{goal}の実装に向けたStory {story_index + 1}/{total_stories}

## 目的
このStoryでは、{goal}の一部として特定の機能コンポーネントを実装します。
全体の{((story_index + 1) / total_stories) * 100:.1f}%に相当する機能を担当します。

## 技術的要件
- コード規模: {self._estimate_story_lines(epic_data, total_stories, story_index)}行程度
- 技術スタック: Python, 非同期処理, 既存フレームワーク連携
- 品質目標: テストカバレッジ90%以上, ドキュメント完備

## 実装内容
{base_description}の一部を具体化し、実装可能な単位に分解します。
既存の{', '.join(['BaseDataAccessor', 'SafeSheetsWrapper', 'KnowledgeManager'])}と連携し、
システム全体の整合性を保ちながら開発を進めます。

## 完了条件
- 機能実装完了
- 単体テストの作成と実行
- 統合テストの通過
- ドキュメントの作成
- コードレビュー合格

## 注意点
既存システムの保護を最優先とし、破壊的変更を避けること。
運用ルールv1.2.4に従い、安全な実装を心がける。
        """
        
        # 文字数調整（2,500-3,000文字）
        return description.strip()[:3000]
    
    def _estimate_story_lines(self, epic_data: Dict[str, Any], total_stories: int, 
                            story_index: int) -> int:
        """Storyの推定コード行数を計算"""
        base_estimate = 1000  # 基本1,000行
        complexity_factor = len(epic_data.get('description', '')) / 1000
        index_factor = 1.0 + (story_index * 0.1)  # 後半のStoryほど複雑
        
        return int(base_estimate * complexity_factor * index_factor)
    
    def _calculate_story_priority(self, story_index: int, total_stories: int) -> str:
        """Storyの優先度を計算"""
        if story_index == 0:
            return "high"  # 最初のStoryは高優先度
        elif story_index < total_stories * 0.7:
            return "medium"
        else:
            return "low"
    
    def _identify_dependencies(self, story_index: int, total_stories: int) -> List[str]:
        """依存関係を特定"""
        dependencies = []
        if story_index > 0:
            dependencies.append(f"Story_{story_index}")  # 前のStoryに依存
        return dependencies
    
    def _generate_acceptance_criteria(self) -> List[str]:
        """受け入れ基準を生成"""
        return [
            "コードが正常にコンパイルされること",
            "単体テストが90%以上のカバレッジで通過すること",
            "既存機能に影響がないこと",
            "ドキュメントが作成されていること",
            "コードレビューで指摘事項がないこと"
        ]


class PMAgentV33Epic(BaseDataAccessor):
    """Epic管理機能を備えたPMAgent v33"""
    
    def __init__(self, sheets_manager=None, knowledge_manager=None):
        super().__init__(sheets_manager)
        self.knowledge_manager = knowledge_manager or KnowledgeManager()
        self.epic_generator = EpicTaskGenerator(self.knowledge_manager)
        self.logger = logging.getLogger(__name__)
    
    async process_epics(self) -> bool:
        """
        project_goalシートからEpicを読み込み、Storyに分解
        
        Returns:
            bool: 処理の成功可否
        """
        try:
            self.logger.info("Epic処理開始")
            
            # project_goalシートからactive/pendingのEpicを取得
            epics = self.read_sheet_as_dicts('project_goal')
            active_epics = [e for e in epics if e.get('status') in ['active', 'pending']]
            
            if not active_epics:
                self.logger.info("処理対象のEpicが見つかりません")
                return True
            
            processed_count = 0
            for epic in active_epics:
                success = await self._process_single_epic(epic)
                if success:
                    processed_count += 1
            
            self.logger.info(f"Epic処理完了: {processed_count}/{len(active_epics)}件成功")
            return processed_count > 0
            
        except Exception as e:
            self.logger.error(f"Epic処理中にエラー: {e}")
            return False
    
    async def _process_single_epic(self, epic: Dict[str, Any]) -> bool:
        """単一Epicの処理"""
        try:
            epic_id = epic.get('id')
            self.logger.info(f"Epic処理開始: {epic_id} - {epic.get('goal')}")
            
            # EpicをStoryに分解
            stories = await self.epic_generator.decompose_epic_to_stories(epic)
            
            if not stories:
                self.logger.warning(f"Epic {epic_id} の分解に失敗")
                return False
            
            # pm_tasksシートにStoryを書き込み
            success = await self._write_stories_to_sheets(stories, epic)
            
            if success:
                # Epicのステータスを更新（処理中）
                await self._update_epic_status(epic_id, 'in_progress')
                self.logger.info(f"Epic {epic_id} の処理完了: {len(stories)}個のStoryを生成")
            else:
                self.logger.error(f"Epic {epic_id} のStory書き込みに失敗")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Epic {epic.get('id')} 処理中にエラー: {e}")
            return False
    
    async def _write_stories_to_sheets(self, stories: List[Dict[str, Any]], 
                                     epic: Dict[str, Any]) -> bool:
        """生成したStoryをpm_tasksシートに書き込み"""
        try:
            # 既存のタスクを取得して重複チェック
            existing_tasks = self.read_sheet_as_dicts('pm_tasks')
            existing_titles = {t.get('title') for t in existing_tasks if t.get('title')}
            
            new_tasks = []
            for story in stories:
                # 重複チェック
                if story['title'] in existing_titles:
                    self.logger.info(f"重複Storyをスキップ: {story['title']}")
                    continue
                
                # pm_tasks形式に変換
                task = {
                    'title': story['title'],
                    'description': story['description'],
                    'status': 'pending',
                    'priority': story['priority'],
                    'category': story['category'],
                    'epic_id': epic.get('id'),
                    'goal_id': epic.get('id'),  # 既存システム互換性のため
                    'estimated_lines': story['estimated_lines'],
                    'dependencies': ','.join(story['dependencies']),
                    'acceptance_criteria': '; '.join(story['acceptance_criteria'])
                }
                new_tasks.append(task)
            
            if not new_tasks:
                self.logger.info("新しいStoryがありません")
                return True
            
            # SafeSheetsWrapperを使用して書き込み
            task_data = []
            for task in new_tasks:
                task_row = [
                    task.get('title', ''),
                    task.get('description', ''),
                    task.get('status', 'pending'),
                    task.get('priority', 'medium'),
                    task.get('category', 'development'),
                    task.get('epic_id', ''),
                    task.get('goal_id', ''),
                    task.get('estimated_lines', 0),
                    task.get('dependencies', ''),
                    task.get('acceptance_criteria', '')
                ]
                task_data.append(task_row)
            
            # pm_tasksシートに追加
            success = self.sheets.safe_append('pm_tasks', task_data)
            
            if success:
                self.logger.info(f"{len(new_tasks)}個のStoryをpm_tasksに追加")
                
                # ナレッジベースに登録
                for story in stories:
                    self._register_story_to_knowledge(story, epic)
                    
            return success
            
        except Exception as e:
            self.logger.error(f"Story書き込み中にエラー: {e}")
            return False
    
    async def _update_epic_status(self, epic_id: str, status: str) -> bool:
        """Epicのステータスを更新"""
        try:
            # project_goalシートの更新ロジック
            # 実際の実装ではGoogle Sheets APIを使用
            self.logger.info(f"Epic {epic_id} のステータスを {status} に更新")
            return True
        except Exception as e:
            self.logger.error(f"Epicステータス更新エラー: {e}")
            return False
    
    def _register_story_to_knowledge(self, story: Dict[str, Any], epic: Dict[str, Any]) -> bool:
        """Story情報をナレッジベースに登録"""
        try:
            title = f"Epic分解: {story['title']}"
            content = f"""
Epic: {epic.get('goal')}
Story: {story['title']}

説明:
{story['description']}

見積もり行数: {story['estimated_lines']}
優先度: {story['priority']}
依存関係: {', '.join(story['dependencies'])}

受け入れ基準:
{chr(10).join(story['acceptance_criteria'])}
            """
            
            self.knowledge_manager.add_knowledge(
                title=title,
                content=content,
                category="epic_decomposition",
                tags=f"epic,story,planning,{epic.get('id')}"
            )
            return True
        except Exception as e:
            self.logger.warning(f"ナレッジ登録エラー: {e}")
            return False

# テスト用の実行コード
async def main():
    """テスト実行"""
    logging.basicConfig(level=logging.INFO)
    
    # PMAgentV33Epicのインスタンス化
    pm_agent = PMAgentV33Epic()
    
    # Epic処理の実行
    success = await pm_agent.process_epics()
    
    if success:
        print("✅ Epic処理が正常に完了しました")
    else:
        print("❌ Epic処理中にエラーが発生しました")

if __name__ == "__main__":
    asyncio.run(main())
