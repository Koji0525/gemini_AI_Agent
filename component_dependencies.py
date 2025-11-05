#!/usr/bin/env python3
"""
24時間自律開発システム - コンポーネント依存関係マップ
"""
import sys
sys.path.insert(0, '/workspaces/gemini_AI_Agent')

def analyze_dependencies():
    """コンポーネント依存関係を分析"""
    
    dependencies = {
        "GoogleSheetsManager": {
            "dependencies": [],
            "dependents": ["KnowledgeBaseManager", "LogIntegrator"],
            "purpose": "データ永続化 - Google Sheets連携"
        },
        "KnowledgeBaseManager": {
            "dependencies": ["GoogleSheetsManager"],
            "dependents": ["SelfLearningPipeline"],
            "purpose": "ナレッジ管理 - 成功/失敗パターン保存"
        },
        "LogIntegrator": {
            "dependencies": ["GoogleSheetsManager"],
            "dependents": ["PatternExtractor", "SelfLearningPipeline"],
            "purpose": "ログ統合 - 複数ソースからのログ収集"
        },
        "PatternExtractor": {
            "dependencies": ["LogIntegrator"],
            "dependents": ["SelfLearningPipeline"],
            "purpose": "パターン抽出 - 成功/失敗パターン分析"
        },
        "DecisionSupportSystem": {
            "dependencies": [],
            "dependents": ["SelfLearningPipeline"],
            "purpose": "意思決定 - 修正戦略生成"
        },
        "ContextLogger": {
            "dependencies": [],
            "dependents": ["SelfLearningPipeline"],
            "purpose": "コンテキスト記録 - 実行状況の追跡"
        },
        "SelfLearningPipeline": {
            "dependencies": ["KnowledgeBaseManager", "LogIntegrator", "PatternExtractor", "DecisionSupportSystem", "ContextLogger"],
            "dependents": ["AutonomousDevelopmentOrchestrator"],
            "purpose": "自己学習 - 継続的改善サイクル"
        },
        "TaskExecutor": {
            "dependencies": ["RAG Engine"],
            "dependents": ["AutonomousDevelopmentOrchestrator"],
            "purpose": "タスク実行 - ナレッジを活用したタスク処理"
        },
        "RAG Engine": {
            "dependencies": [],
            "dependents": ["TaskExecutor"],
            "purpose": "検索 - ナレッジベースからの関連情報取得"
        },
        "AutonomousDevelopmentOrchestrator": {
            "dependencies": ["SelfLearningPipeline", "TaskExecutor"],
            "dependents": [],
            "purpose": "全体統合 - 24時間自律稼働の調整"
        }
    }
    
    print("🔗 24時間自律開発システム - コンポーネント依存関係マップ")
    print("=" * 70)
    
    for component, info in dependencies.items():
        print(f"\n🎯 {component}")
        print(f"   📋 目的: {info['purpose']}")
        print(f"   📥 依存: {', '.join(info['dependencies']) if info['dependencies'] else 'なし'}")
        print(f"   📤 依存先: {', '.join(info['dependents']) if info['dependents'] else 'なし'}")
    
    print("\n💡 初期化順序:")
    initialized = set()
    order = 1
    
    while len(initialized) < len(dependencies):
        for component, info in dependencies.items():
            if component in initialized:
                continue
                
            # すべての依存関係が初期化済みかチェック
            deps_initialized = all(dep in initialized for dep in info['dependencies'])
            
            if deps_initialized:
                print(f"   {order}. {component}")
                initialized.add(component)
                order += 1

if __name__ == "__main__":
    analyze_dependencies()
