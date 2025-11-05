#!/usr/bin/env python3
"""
システム健康診断 - 非同期エラー修正版
"""
import asyncio
import sys
import os
sys.path.insert(0, '/workspaces/gemini_AI_Agent')

async def check_system_health():
    """システムの健康状態をチェック"""
    components = {
        "GoogleSheetsManager": ("tools.sheets_manager", "GoogleSheetsManager"),
        "KnowledgeBaseManager": ("agents.self_healing.knowledge_base_manager", "KnowledgeBaseManager"),
        "LogIntegrator": ("agents.self_healing.logging.log_integrator", "LogIntegrator"),
        "PatternExtractor": ("agents.self_healing.pattern_extractor", "PatternExtractor"),
        "DecisionSupportSystem": ("agents.self_healing.decision_support_system", "DecisionSupportSystem"),
        "ContextLogger": ("agents.self_healing.logging.context_logger", "ContextLogger"),
        "SelfLearningPipeline": ("agents.self_healing.self_learning_pipeline_fixed", "SelfLearningPipelineFixed"),
        "TaskExecutor": ("task_executor", "TaskExecutor"),
        "RAG Engine": ("mvp_v4.scripts.rag_engine_persistent_v2", "get_rag_engine_v2")
    }

    print("🔧 システムコンポーネント健康診断...")
    all_healthy = True
    
    for name, (module, item) in components.items():
        try:
            mod = __import__(module, fromlist=[item])
            cls = getattr(mod, item)
            
            # コンポーネントごとの初期化
            if name == "GoogleSheetsManager":
                instance = cls()
            elif name == "KnowledgeBaseManager":
                from tools.sheets_manager import GoogleSheetsManager
                sheets = GoogleSheetsManager()
                instance = cls(sheets)
            elif name == "LogIntegrator":
                from tools.sheets_manager import GoogleSheetsManager
                sheets = GoogleSheetsManager()
                instance = cls(sheets)
            elif name == "PatternExtractor":
                from tools.sheets_manager import GoogleSheetsManager
                from agents.self_healing.logging.log_integrator import LogIntegrator
                sheets = GoogleSheetsManager()
                log_integrator = LogIntegrator(sheets)
                instance = cls(log_integrator)
            elif name == "DecisionSupportSystem":
                instance = cls()
            elif name == "ContextLogger":
                from tools.sheets_manager import GoogleSheetsManager
                sheets = GoogleSheetsManager()
                instance = cls(sheets)
            elif name == "SelfLearningPipeline":
                from tools.sheets_manager import GoogleSheetsManager
                from agents.self_healing.knowledge_base_manager import KnowledgeBaseManager
                sheets = GoogleSheetsManager()
                kb = KnowledgeBaseManager(sheets)
                instance = cls(sheets, kb)
            elif name == "TaskExecutor":
                instance = cls()
                await instance.initialize()
            elif name == "RAG Engine":
                instance = cls(['mvp_v4/knowledge/learned/conversation_knowledge_v3.json'])
            
            print(f"  ✅ {name}: 健康")
            
        except Exception as e:
            print(f"  ❌ {name}: 異常 - {e}")
            all_healthy = False
    
    return all_healthy

async def main():
    all_healthy = await check_system_health()
    
    if all_healthy:
        print("\n🎉 システム健康状態: 良好")
        print("🚀 24時間自律開発システム: 本格稼働準備完了")
    else:
        print("\n⚠️  システム健康状態: 要改善")
        print("🔧 異常コンポーネントの修正が必要です")

if __name__ == "__main__":
    asyncio.run(main())
