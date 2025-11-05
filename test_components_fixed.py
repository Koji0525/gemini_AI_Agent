#!/usr/bin/env python3
"""
コンポーネントテスト - 非同期エラー修正版
"""
import asyncio
import sys
sys.path.insert(0, '/workspaces/gemini_AI_Agent')

async def test_components():
    """個別コンポーネントテスト"""
    print("🔧 個別コンポーネントテスト...")
    
    try:
        # GoogleSheetsManagerテスト
        from tools.sheets_manager import GoogleSheetsManager
        sheets = GoogleSheetsManager()
        
        # read_sheetメソッドテスト
        test_data = sheets.read_sheet("task_execution_log")
        print(f"✅ GoogleSheetsManager.read_sheet: {len(test_data)}件のデータ")
        print(f"✅ GoogleSheetsManager.authenticated: {sheets.authenticated}")
        
        # LogIntegratorテスト
        from agents.self_healing.logging.log_integrator_fixed import LogIntegratorFixed
        log_integrator = LogIntegratorFixed(sheets)
        logs = await log_integrator.load_all_logs()
        print(f"✅ LogIntegratorFixed.load_all_logs: {len(logs)}件のログ")
        
        # PatternExtractorテスト
        from agents.self_healing.pattern_extractor import PatternExtractor
        pattern_extractor = PatternExtractor(log_integrator)
        patterns = await pattern_extractor.extract(logs)
        print(f"✅ PatternExtractor.extract: {len(patterns)}個のパターン")
        
        # KnowledgeBaseManagerテスト
        from agents.self_healing.knowledge_base_manager import KnowledgeBaseManager
        kb_manager = KnowledgeBaseManager(sheets)
        update_result = await kb_manager.update(patterns)
        print(f"✅ KnowledgeBaseManager.update: {update_result}")
        
        print("🎉 個別コンポーネントテスト: 成功")
        return True
        
    except Exception as e:
        print(f"❌ 個別コンポーネントテスト: {e}")
        import traceback
        traceback.print_exc()
        return False

async def integration_test():
    """統合テスト"""
    try:
        from tools.sheets_manager import GoogleSheetsManager
        from agents.self_healing.knowledge_base_manager import KnowledgeBaseManager
        from agents.self_healing.self_learning_pipeline_fixed_v2 import SelfLearningPipelineFixedV2
        
        sheets = GoogleSheetsManager()
        kb = KnowledgeBaseManager(sheets)
        pipeline = SelfLearningPipelineFixedV2(sheets, kb)
        
        # 学習サイクル実行テスト
        strategies = await pipeline.run_learning_cycle()
        
        print(f"✅ 統合テスト: 成功 - {len(strategies)}個の戦略を生成")
        return True
        
    except Exception as e:
        print(f"❌ 統合テスト: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """メイン関数"""
    # 個別コンポーネントテスト
    components_ok = await test_components()
    
    if components_ok:
        # 統合テスト
        integration_ok = await integration_test()
        
        if integration_ok:
            print("🎉 すべてのテストが成功しました！")
            return True
        else:
            print("❌ 統合テストが失敗しました")
            return False
    else:
        print("❌ コンポーネントテストが失敗しました")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
