#!/usr/bin/env python3
"""
開発フェーズ自動判定システム
"""
import sys
import os

def check_phase():
    phases = {
        "Phase 1": ["基本的なファイル構造", "設定ファイル"],
        "Phase 2": ["GoogleSheetsManager", "BrowserController"], 
        "Phase 3": ["KnowledgeBaseManager", "LogIntegrator"],
        "Phase 4": ["SelfLearningPipeline", "PatternExtractor"],
        "Phase 4.4": ["TaskExecutor", "自律学習統合"],
        "Phase 5": ["24時間自律稼働", "自動修復"]
    }
    
    components = {
        "Phase 1": [
            "tools.sheets_manager.GoogleSheetsManager",
            "browser_control.browser_controller.BrowserController"
        ],
        "Phase 2": [
            "agents.self_healing.knowledge_base_manager.KnowledgeBaseManager",
            "agents.self_healing.log_integrator.LogIntegrator"
        ],
        "Phase 3": [
            "agents.self_healing.pattern_extractor.PatternExtractor",
            "agents.self_healing.decision_support_system.DecisionSupportSystem"
        ],
        "Phase 4": [
            "agents.self_healing.self_learning_pipeline.SelfLearningPipeline",
            "agents.self_healing.context_logger.ContextLogger"
        ],
        "Phase 4.4": [
            "task_executor.task_executor_main.TaskExecutor",
            "autonomous_development_orchestrator.AutonomousDevelopmentOrchestrator"
        ]
    }
    
    print("🔍 開発フェーズ診断中...")
    current_phase = "Phase 1"
    
    for phase, comp_list in components.items():
        all_ok = True
        for comp in comp_list:
            try:
                module_path, class_name = comp.rsplit('.', 1)
                module = __import__(module_path, fromlist=[class_name])
                getattr(module, class_name)
            except Exception as e:
                all_ok = False
                break
        
        if all_ok:
            current_phase = phase
        else:
            break
    
    print(f"🎯 現在の開発フェーズ: {current_phase}")
    print(f"📋 包含コンポーネント: {', '.join(phases[current_phase])}")
    
    # 次のフェーズへの道筋
    next_phases = {
        "Phase 1": "Phase 2 - コアマネージャーの実装",
        "Phase 2": "Phase 3 - 知識管理システムの構築", 
        "Phase 3": "Phase 4 - 自己学習パイプライン",
        "Phase 4": "Phase 4.4 - タスク実行統合",
        "Phase 4.4": "Phase 5 - 完全自律稼働"
    }
    
    if current_phase in next_phases:
        print(f"🚀 次の目標: {next_phases[current_phase]}")
    
    return current_phase

if __name__ == "__main__":
    check_phase()
