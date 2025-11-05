#!/usr/bin/env python3
"""
正確な開発フェーズ診断システム
"""
import sys
import os

def check_phase_accurate():
    print("🔍 正確な開発フェーズ診断中...")
    
    phase_components = {
        "Phase 1 - 基本構造": [
            ("tools.sheets_manager", "GoogleSheetsManager"),
            ("browser_control.browser_controller", "BrowserController")
        ],
        "Phase 2 - 知識管理基盤": [
            ("agents.self_healing.knowledge_base_manager", "KnowledgeBaseManager"),
            ("agents.self_healing.log_integrator", "LogIntegrator")
        ],
        "Phase 3 - 学習コンポーネント": [
            ("agents.self_healing.pattern_extractor", "PatternExtractor"),
            ("agents.self_healing.decision_support_system", "DecisionSupportSystem"),
            ("agents.self_healing.context_logger", "ContextLogger")
        ],
        "Phase 4 - 自己学習統合": [
            ("agents.self_healing.self_learning_pipeline", "SelfLearningPipeline")
        ],
        "Phase 4.4 - タスク実行統合": [
            ("task_executor", "TaskExecutor"),
            ("autonomous_development_orchestrator", "AutonomousDevelopmentOrchestrator")
        ]
    }
    
    current_phase = "Phase 0"
    successful_phases = []
    
    for phase, components in phase_components.items():
        all_ok = True
        
        for module_path, class_name in components:
            try:
                # モジュールの動的インポート
                module = __import__(module_path, fromlist=[class_name])
                # クラスの取得（インスタンス化はしない）
                cls = getattr(module, class_name)
                print(f"  ✅ {phase}: {class_name}")
            except Exception as e:
                print(f"  ❌ {phase}: {class_name} - {e}")
                all_ok = False
                break
        
        if all_ok:
            successful_phases.append(phase)
            current_phase = phase
    
    print(f"🎯 現在の開発フェーズ: {current_phase}")
    print(f"📈 達成フェーズ: {', '.join(successful_phases)}")
    
    # 次の目標
    next_steps = {
        "Phase 0": "Phase 1 - 基本コンポーネントの構築",
        "Phase 1 - 基本構造": "Phase 2 - 知識管理基盤の構築",
        "Phase 2 - 知識管理基盤": "Phase 3 - 学習コンポーネントの統合", 
        "Phase 3 - 学習コンポーネント": "Phase 4 - 自己学習パイプライン",
        "Phase 4 - 自己学習統合": "Phase 4.4 - タスク実行統合",
        "Phase 4.4 - タスク実行統合": "Phase 5 - 24時間完全自律稼働"
    }
    
    if current_phase in next_steps:
        print(f"🚀 次の目標: {next_steps[current_phase]}")
    
    return current_phase

if __name__ == "__main__":
    check_phase_accurate()
