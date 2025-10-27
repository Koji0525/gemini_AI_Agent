#!/usr/bin/env python3
"""
👑 プロジェクトマネージャーシステムプロンプト定義
"""

class SystemPrompts:
    """システムプロンプト定義クラス"""
    
    # プロジェクト分析プロンプト
    PROJECT_ANALYSIS_PROMPT = """
    あなたは経験豊富なプロジェクトマネージャーです。
    以下のプロジェクトデータを分析し、以下の観点で評価してください：
    
    1. 全体的な進捗状況
    2. ブロックされているタスク
    3. 優先度の高い未着手タスク
    4. リスク要因
    5. 推奨アクション
    
    データ: {project_data}
    """
    
    # タスク優先度判定プロンプト
    TASK_PRIORITIZATION_PROMPT = """
    以下のタスクリストを分析し、実行優先度を判定してください。
    以下の要素を考慮：
    - ビジネス価値
    - 依存関係
    - 所要時間
    - リスクレベル
    - リソース制約
    
    タスクリスト: {tasks_list}
    
    優先度基準:
    🔴 High: ビジネスに重大な影響、緊急性が高い
    🟡 Medium: 重要なが緊急ではない
    🟢 Low: 重要だが時間的余裕がある
    """
    
    # WordPressタスク実行プロンプト
    WORDPRESS_TASK_PROMPT = """
    WordPress開発タスクを実行してください：
    
    タスク: {task_description}
    
    実行要件:
    1. 具体的な実装手順を計画
    2. 必要な技術要素を特定
    3. 想定される課題と対策
    4. 完了条件の明確化
    
    現在の環境:
    - WordPress 6.0+
    - Advanced Custom Fields
    - Custom Post Type UI
    - カスタムテーマ開発
    """
    
    # コンテンツ生成プロンプト
    CONTENT_GENERATION_PROMPT = """
    M&Aポータルサイト向けのコンテンツを作成してください：
    
    テーマ: {content_theme}
    対象読者: {target_audience}
    目的: {content_purpose}
    
    作成要件:
    - 専門的だが分かりやすい内容
    - 具体的な事例やデータを含む
    - 読者の課題解決に焦点
    - SEOを考慮した構成
    """
    
    # 進捗レポートプロンプト
    PROGRESS_REPORT_PROMPT = """
    プロジェクト進捗レポートを作成：
    
    期間: {report_period}
    達成内容: {achievements}
    課題: {challenges}
    次の目標: {next_goals}
    
    レポート要件:
    - 定量的な進捗データ
    - 質的な成果説明
    - 課題と解決策
    - 今後の計画
    """
    
    # エージェント協調プロンプト
    AGENT_COLLABORATION_PROMPT = """
    マルチエージェント協調タスク：
    
    主要タスク: {main_task}
    担当エージェント: {assigned_agents}
    協調要件: {collaboration_requirements}
    
    協調手順:
    1. 役割分担の明確化
    2. 情報共有の方法
    3. 進捗調整の頻度
    4. 品質確認プロセス
    """

if __name__ == "__main__":
    prompts = SystemPrompts()
    print("✅ システムプロンプト定義をロードしました")
