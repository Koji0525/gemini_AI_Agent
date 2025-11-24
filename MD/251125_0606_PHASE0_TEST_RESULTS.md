# Phase 0 テスト結果

**実行日時**: 2025-11-24 18:27:36
**テスト成功率**: 50.0%
**基準値**: 84.3%以上
**判定**: FAILED

## 詳細

```
============================= test session starts ==============================
platform linux -- Python 3.12.1, pytest-9.0.1, pluggy-1.6.0 -- /usr/local/python/3.12.1/bin/python3
cachedir: .pytest_cache
rootdir: /workspaces/gemini_AI_Agent
configfile: pyproject.toml
plugins: anyio-4.11.0, asyncio-1.3.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collecting ... collected 178 items

tests/e2e/test_autonomous_cycle.py::TestAutonomousCycle::test_autonomous_orchestrator_exists SKIPPED [  0%]
tests/e2e/test_autonomous_cycle.py::TestAutonomousCycle::test_orchestrator_initialization SKIPPED [  1%]
tests/e2e/test_autonomous_cycle.py::TestAutonomousCycle::test_full_autonomous_cycle SKIPPED [  1%]
tests/integration/test_extended_features.py::TestHiddenDependencyDetector::test_detect_file PASSED [  2%]
tests/integration/test_extended_features.py::TestHiddenDependencyDetector::test_detector_import PASSED [  2%]
tests/integration/test_extended_features.py::TestHiddenDependencyDetector::test_scan_project PASSED [  3%]
tests/integration/test_extended_features.py::TestChangeImpactAnalyzer::test_analyzer_import PASSED [  3%]
tests/integration/test_extended_features.py::TestChangeImpactAnalyzer::test_get_git_changes PASSED [  4%]
tests/integration/test_extended_features.py::TestGraphDB::test_add_component PASSED [  5%]
tests/integration/test_extended_features.py::TestGraphDB::test_graph_db_import PASSED [  5%]
tests/integration/test_extended_features.py::TestImpactAnalyzer::test_impact_analyzer_import PASSED [  6%]
tests/integration/test_extended_features.py::TestCompleteDashboard::test_dashboard_html_exists PASSED [  6%]
tests/integration/test_extended_features.py::TestCompleteDashboard::test_dashboard_html_size PASSED [  7%]
tests/integration/test_extended_features.py::TestCompleteDashboard::test_dashboard_load_time PASSED [  7%]
tests/integration/test_extended_features.py::TestAPIExtensions::test_api_extensions_file_exists PASSED [  8%]
tests/integration/test_extended_features.py::TestIntegration::test_core_components_exist PASSED [  8%]
tests/integration/test_extended_features.py::TestIntegration::test_existing_observer_components PASSED [  9%]
tests/integration/test_integrated_v31_core.py::TestIntegratedOrchestratorV31Core::test_import PASSED [ 10%]
tests/integration/test_integrated_v31_core.py::TestIntegratedOrchestratorV31Core::test_initialization SKIPPED [ 10%]
tests/integration/test_integrated_v31_core.py::TestIntegratedOrchestratorV31Core::test_has_required_attributes PASSED [ 11%]
tests/integration/test_integrated_v31_core.py::TestIntegratedOrchestratorV31Core::test_single_cycle_dry_run PASSED [ 11%]
tests/integration/test_integrated_v31_core.py::TestIntegratedOrchestratorV31Core::test_version_info PASSED [ 12%]
tests/integration/test_knowledge_integration.py::TestKnowledgeIntegration::test_search_with_mocked_data PASSED [ 12%]
tests/integration/test_knowledge_integration.py::TestKnowledgeIntegration::test_load_entries_mocked PASSED [ 13%]
tests/integration/test_knowledge_integration.py::TestKnowledgeIntegration::test_observability_integration_mocked PASSED [ 14%]
tests/integration/test_knowledge_integration.py::TestKnowledgeIntegration::test_multiple_searches PASSED [ 14%]
tests/integration/test_knowledge_integration.py::TestKnowledgeIntegration::test_error_resilience PASSED [ 15%]
tests/integration/test_phase4_integration.py::TestPhase4Integration::test_intelligence_coordinator PASSED [ 15%]
tests/integration/test_phase4_integration.py::TestPhase4Integration::test_resource_forecaster PASSED [ 16%]
tests/integration/test_phase4_integration.py::TestPhase4Integration::test_learning_visualizer PASSED [ 16%]
tests/integration/test_phase4_integration.py::TestPhase4Integration::test_performance_optimizer PASSED [ 17%]
tests/integration/test_phase4_integration.py::TestPhase4Integration::test_full_phase4_flow PASSED [ 17%]
tests/observer_enhanced/graph/test_graph_db.py::TestSystemGraphDB::test_add_component PASSED [ 18%]
tests/observer_enhanced/graph/test_graph_db.py::TestSystemGraphDB::test_get_component FAILED [ 19%]
tests/observer_enhanced/graph/test_graph_db.py::TestSystemGraphDB::test_update_component FAILED [ 19%]
tests/observer_enhanced/graph/test_graph_db.py::TestSystemGraphDB::test_remove_component FAILED [ 20%]
tests/observer_enhanced/graph/test_graph_db.py::TestSystemGraphDB::test_list_components FAILED [ 20%]
tests/observer_enhanced/graph/test_graph_db.py::TestSystemGraphDB::test_add_dependency PASSED [ 21%]
tests/observer_enhanced/graph/test_graph_db.py::TestSystemGraphDB::test_get_dependency FAILED [ 21%]
tests/observer_enhanced/graph/test_graph_db.py::TestSystemGraphDB::test_remove_dependency FAILED [ 22%]
tests/observer_enhanced/graph/test_graph_db.py::TestSystemGraphDB::test_get_dependencies PASSED [ 23%]
tests/observer_enhanced/graph/test_graph_db.py::TestSystemGraphDB::test_get_impact_range_depth1 FAILED [ 23%]
tests/observer_enhanced/graph/test_graph_db.py::TestSystemGraphDB::test_get_impact_range_depth2 FAILED [ 24%]
tests/observer_enhanced/graph/test_graph_db.py::TestSystemGraphDB::test_get_shortest_path FAILED [ 24%]
tests/observer_enhanced/graph/test_graph_db.py::TestSystemGraphDB::test_find_cycles FAILED [ 25%]
tests/observer_enhanced/graph/test_graph_db.py::TestSystemGraphDB::test_get_statistics FAILED [ 25%]
tests/observer_enhanced/graph/test_graph_db.py::TestSystemGraphDB::test_get_most_dependent FAILED [ 26%]
tests/observer_enhanced/graph/test_graph_db.py::TestSystemGraphDB::test_get_most_depending FAILED [ 26%]
tests/observer_enhanced/graph/test_graph_db.py::TestSystemGraphDB::test_export_to_json FAILED [ 27%]
tests/observer_enhanced/graph/test_graph_db.py::TestSystemGraphDB::test_import_from_json FAILED [ 28%]
tests/observer_enhanced/graph/test_graph_db.py::TestSystemGraphDB::test_performance_add_node PASSED [ 28%]
tests/observer_enhanced/graph/test_graph_db.py::TestSystemGraphDB::test_performance_add_edge PASSED [ 29%]
tests/observer_enhanced/graph/test_graph_db.py::TestSystemGraphDB::test_performance_impact_range FAILED [ 29%]
tests/observer_enhanced/graph/test_impact_analyzer.py::TestImpactAnalyzer::test_analyze_impact_basic FAILED [ 30%]
tests/observer_enhanced/graph/test_impact_analyzer.py::TestImpactAnalyzer::test_analyze_impact_depth FAILED [ 30%]
tests/observer_enhanced/graph/test_impact_analyzer.py::TestImpactAnalyzer::test_analyze_impact_direction_in FAILED [ 31%]
tests/observer_enhanced/graph/test_impact_analyzer.py::TestImpactAnalyzer::test_analyze_impact_direction_out FAILED [ 32%]
tests/observer_enhanced/graph/test_impact_analyzer.py::TestImpactAnalyzer::test_analyze_impact_nonexistent PASSED [ 32%]
tests/observer_enhanced/graph/test_impact_analyzer.py::TestImpactAnalyzer::test_find_path FAILED [ 33%]
tests/observer_enhanced/graph/test_impact_analyzer.py::TestImpactAnalyzer::test_find_path_no_path FAILED [ 33%]
tests/observer_enhanced/graph/test_impact_analyzer.py::TestImpactAnalyzer::test_detect_cycles_no_cycle FAILED [ 34%]
tests/observer_enhanced/graph/test_impact_analyzer.py::TestImpactAnalyzer::test_detect_cycles_with_cycle FAILED [ 34%]
tests/observer_enhanced/graph/test_impact_analyzer.py::TestImpactAnalyzer::test_scoring_low_risk PASSED [ 35%]
tests/observer_enhanced/graph/test_impact_analyzer.py::TestImpactAnalyzer::test_scoring_high_risk PASSED [ 35%]
tests/observer_enhanced/graph/test_impact_analyzer.py::TestImpactAnalyzer::test_generate_test_recommendations FAILED [ 36%]
tests/observer_enhanced/graph/test_impact_analyzer.py::TestImpactAnalyzer::test_recommendations_for_large_change FAILED [ 37%]
tests/observer_enhanced/graph/test_impact_analyzer.py::TestImpactAnalyzer::test_performance_analyze_impact FAILED [ 37%]
tests/observer_enhanced/graph/test_impact_analyzer.py::TestImpactAnalyzer::test_performance_generate_recommendations FAILED [ 38%]
tests/observer_enhanced/test_api.py::test_health_api_status_code PASSED  [ 38%]
tests/observer_enhanced/test_api.py::test_health_api_response_structure PASSED [ 39%]
tests/observer_enhanced/test_api.py::test_health_api_health_score PASSED [ 39%]
tests/observer_enhanced/test_api.py::test_health_api_component_scores PASSED [ 40%]
tests/observer_enhanced/test_api.py::test_graph_api_status_code PASSED   [ 41%]
tests/observer_enhanced/test_api.py::test_graph_api_with_limit PASSED    [ 41%]
tests/observer_enhanced/test_api.py::test_graph_api_structure PASSED     [ 42%]
tests/observer_enhanced/test_api.py::test_traces_api_status_code PASSED  [ 42%]
tests/observer_enhanced/test_api.py::test_traces_api_parameters PASSED   [ 43%]
tests/observer_enhanced/test_api.py::test_traces_api_statistics PASSED   [ 43%]
tests/observer_enhanced/test_api.py::test_alerts_api_status_code FAILED  [ 44%]
tests/observer_enhanced/test_api.py::test_alerts_api_parameters FAILED   [ 44%]
tests/observer_enhanced/test_api.py::test_alerts_api_level_filter FAILED [ 45%]
tests/observer_enhanced/test_api.py::test_cors_headers PASSED            [ 46%]
tests/observer_enhanced/test_api.py::test_cors_methods FAILED            [ 46%]
tests/observer_enhanced/test_api.py::test_analyze_api_status_code PASSED [ 47%]
tests/observer_enhanced/test_api.py::test_full_workflow FAILED           [ 47%]
tests/observer_enhanced/test_api.py::test_health_api_performance PASSED  [ 48%]
tests/observer_enhanced/test_api.py::test_graph_api_performance PASSED   [ 48%]
tests/observer_enhanced/test_api_server.py::TestAPIServer::test_health_check FAILED [ 49%]
tests/observer_enhanced/test_api_server.py::TestAPIServer::test_get_dependencies PASSED [ 50%]
tests/observer_enhanced/test_api_server.py::TestAPIServer::test_get_duplicates FAILED [ 50%]
tests/observer_enhanced/test_api_server.py::TestAPIServer::test_get_impact_analysis PASSED [ 51%]
tests/observer_enhanced/test_api_server.py::TestAPIServer::test_cors_headers FAILED [ 51%]
tests/observer_enhanced/test_api_server_fixed.py::TestAPIServerFixed::test_health_check FAILED [ 52%]
tests/observer_enhanced/test_api_server_fixed.py::TestAPIServerFixed::test_get_dependencies PASSED [ 52%]
tests/observer_enhanced/test_api_server_fixed.py::TestAPIServerFixed::test_get_duplicates FAILED [ 53%]
tests/observer_enhanced/test_api_server_fixed.py::TestAPIServerFixed::test_get_impact_analysis PASSED [ 53%]
tests/observer_enhanced/test_api_server_fixed.py::TestAPIServerFixed::test_cors_settings PASSED [ 54%]
tests/observer_enhanced/test_import_extractor.py::TestImportExtractor::test_extract_simple_imports FAILED [ 55%]
tests/observer_enhanced/test_import_extractor.py::TestImportExtractor::test_extract_complex_imports FAILED [ 55%]
tests/observer_enhanced/test_import_extractor.py::TestImportExtractor::test_extract_from_real_file SKIPPED [ 56%]
tests/observer_enhanced/test_import_extractor.py::TestImportExtractor::test_filter_internal_external FAILED [ 56%]
tests/observer_enhanced/test_import_extractor.py::TestImportExtractor::test_performance PASSED [ 57%]
tests/observer_enhanced/test_import_extractor.py::TestImportExtractorIntegration::test_full_workflow PASSED [ 57%]
tests/system_protection/test_core_functions.py::test_f1_goal_concrete PASSED [ 58%]
tests/system_protection/test_core_functions.py::test_f2_task_execution PASSED [ 58%]
tests/system_protection/test_core_functions.py::test_f3_quality_evaluator PASSED [ 59%]
tests/system_protection/test_core_functions.py::test_f4_knowledge_system PASSED [ 60%]
tests/system_protection/test_core_functions.py::test_f7_self_healing PASSED [ 60%]
tests/system_protection/test_core_functions.py::test_f8_self_evolution PASSED [ 61%]
tests/system_protection/test_core_functions.py::test_f9_human_collaboration PASSED [ 61%]
tests/test_data_integration_v2.py::TestDataIntegrationPipeline::test_pipeline_basic_mock PASSED [ 62%]
tests/test_data_integration_v2.py::TestDataIntegrationPipeline::test_sheets_manager_mock PASSED [ 62%]
tests/test_data_integration_v2.py::TestDataIntegrationPipeline::test_empty_data_handling PASSED [ 63%]
tests/test_data_integration_v2.py::TestDataIntegrationPipeline::test_error_handling PASSED [ 64%]
tests/test_data_integration_v2.py::TestDataIntegrationPipeline::test_multiple_sources PASSED [ 64%]
tests/test_data_integration_v2.py::TestDataIntegrationReal::test_real_pipeline SKIPPED [ 65%]
tests/test_phase1_agents_final.py::TestCodeGenerationAgentFinalFixed::test_agent_initialization_success_complete PASSED [ 65%]
tests/test_phase1_agents_final.py::TestCodeGenerationAgentFinalFixed::test_agent_initialization_no_models PASSED [ 66%]
tests/test_phase1_agents_final.py::TestCodeGenerationAgentFinalFixed::test_code_generation_success_complete_fixed PASSED [ 66%]
tests/test_phase1_agents_final.py::TestCodeGenerationAgentFinalFixed::test_code_generation_api_error_complete_fixed PASSED [ 67%]
tests/test_phase1_agents_final.py::TestGeminiAPIClientFinalFixed::test_client_initialization_complete PASSED [ 67%]
tests/test_phase1_agents_final.py::TestGeminiAPIClientFinalFixed::test_send_prompt_success_complete PASSED [ 68%]
tests/test_phase1_agents_final.py::TestGeminiAPIClientFinalFixed::test_send_prompt_sync_context_complete PASSED [ 69%]
tests/test_phase1_agents_final.py::TestGeminiAPIClientFinalFixed::test_send_prompt_error_complete PASSED [ 69%]
tests/test_phase1_agents_final.py::TestIntegrationFinalFixed::test_environment_consistency_complete PASSED [ 70%]
tests/test_phase1_agents_final.py::TestIntegrationFinalFixed::test_module_imports_complete PASSED [ 70%]
tests/test_phase1_agents_final.py::TestIntegrationFinalFixed::test_async_method_detection PASSED [ 71%]
tests/test_phase1_agents_final.py::TestIntegrationFinalFixed::test_actual_implementation_structure PASSED [ 71%]
tests/test_phase1_agents_refactored.py::TestCodeGenerationAgentRefactored::test_agent_initialization_success PASSED [ 72%]
tests/test_phase1_agents_refactored.py::TestCodeGenerationAgentRefactored::test_code_generation_success PASSED [ 73%]
tests/test_phase1_agents_refactored.py::TestCodeGenerationAgentRefactored::test_code_generation_api_error PASSED [ 73%]
tests/test_phase1_agents_refactored.py::TestCodeGenerationAgentRefactored::test_initialization_error PASSED [ 74%]
tests/test_phase1_agents_refactored.py::TestGeminiAPIClientRefactored::test_client_initialization PASSED [ 74%]
tests/test_phase1_agents_refactored.py::TestGeminiAPIClientRefactored::test_send_prompt_success PASSED [ 75%]
tests/test_phase1_agents_refactored.py::TestGeminiAPIClientRefactored::test_send_prompt_sync_context PASSED [ 75%]
tests/test_phase1_agents_refactored.py::TestGeminiAPIClientRefactored::test_send_prompt_error PASSED [ 76%]
tests/test_phase1_agents_refactored.py::TestIntegrationRefactored::test_cross_module_imports PASSED [ 76%]
tests/test_phase1_agents_refactored.py::TestIntegrationRefactored::test_environment_consistency PASSED [ 77%]
tests/test_phase1_agents_refactored.py::TestIntegrationRefactored::test_async_sync_boundaries PASSED [ 78%]
tests/test_phase1_agents_with_knowledge.py::TestPhase1WithKnowledge::test_knowledge_integration_placeholder PASSED [ 78%]
tests/test_phase1_agents_with_knowledge.py::TestPhase1WithKnowledge::test_agent_with_knowledge_lookup SKIPPED [ 79%]
tests/test_phase2_agents.py::test_documentation_agent PASSED             [ 79%]
tests/test_phase2_agents.py::test_monitoring_agent PASSED                [ 80%]
tests/test_phase2_agents.py::test_optimization_agent PASSED              [ 80%]
tests/test_phase3_agents.py::test_collaboration_agent PASSED             [ 81%]
tests/test_phase3_agents.py::test_learning_optimizer FAILED              [ 82%]
tests/unit/test_error_cases.py::TestErrorHandling::test_observability_connection_error PASSED [ 82%]
tests/unit/test_error_cases.py::TestErrorHandling::test_knowledge_search_timeout PASSED [ 83%]
tests/unit/test_error_cases.py::TestErrorHandling::test_api_rate_limit PASSED [ 83%]
tests/unit/test_error_cases.py::TestErrorHandling::test_database_recovery PASSED [ 84%]
tests/unit/test_error_cases.py::TestErrorHandling::test_empty_data_handling PASSED [ 84%]
tests/unit/test_knowledge_base_adapter.py::TestKnowledgeBaseAdapter::test_initialization_without_import PASSED [ 85%]
tests/unit/test_knowledge_base_adapter.py::TestKnowledgeBaseAdapter::test_search_knowledge PASSED [ 85%]
tests/unit/test_knowledge_base_adapter.py::TestKnowledgeBaseAdapter::test_load_knowledge_entries PASSED [ 86%]
tests/unit/test_knowledge_base_adapter.py::TestKnowledgeBaseAdapter::test_error_handling_returns_empty PASSED [ 87%]
tests/unit/test_knowledge_base_adapter.py::TestKnowledgeBaseAdapter::test_basic_functionality PASSED [ 87%]
tests/unit/test_knowledge_base_adapter.py::TestKnowledgeBaseAdapter::test_concurrent_searches PASSED [ 88%]
tests/unit/test_knowledge_manager.py::TestKnowledgeManagerCore::test_search_knowledge_with_limit PASSED [ 88%]
tests/unit/test_knowledge_manager.py::TestKnowledgeManagerCore::test_get_sample_entries PASSED [ 89%]
tests/unit/test_knowledge_manager.py::TestKnowledgeManagerCore::test_load_knowledge_entries_limited PASSED [ 89%]
tests/unit/test_knowledge_manager.py::TestKnowledgeManagerCore::test_error_handling_db_connection PASSED [ 90%]
tests/unit/test_knowledge_manager.py::TestKnowledgeManagerCore::test_vector_search_functionality PASSED [ 91%]
tests/unit/test_observability_core.py::TestObservabilityCore::test_trace_recording_basic PASSED [ 91%]
tests/unit/test_observability_core.py::TestObservabilityCore::test_trace_search PASSED [ 92%]
tests/unit/test_observability_core.py::TestObservabilityCore::test_stats_retrieval PASSED [ 92%]
tests/unit/test_observability_core.py::TestKnowledgeCore::test_knowledge_search_with_limit PASSED [ 93%]
tests/unit/test_observability_core.py::TestKnowledgeCore::test_sample_entries_retrieval PASSED [ 93%]
tests/unit/test_observability_core.py::TestKnowledgeCore::test_knowledge_search_empty_query PASSED [ 94%]
tests/unit/test_observability_manager.py::TestObservabilityManagerCore::test_singleton_pattern PASSED [ 94%]
tests/unit/test_observability_manager.py::TestObservabilityManagerCore::test_record_trace_basic PASSED [ 95%]
tests/unit/test_observability_manager.py::TestObservabilityManagerCore::test_record_trace_with_metadata PASSED [ 96%]
tests/unit/test_observability_manager.py::TestObservabilityManagerSearch::test_search_traces_by_operation PASSED [ 96%]
tests/unit/test_observability_manager.py::TestObservabilityManagerSearch::test_search_traces_by_status PASSED [ 97%]
tests/unit/test_observability_manager.py::TestObservabilityManagerSearch::test_search_traces_by_date_range PASSED [ 97%]
tests/unit/test_observability_manager.py::TestObservabilityManagerStats::test_get_stats_empty PASSED [ 98%]
tests/unit/test_observability_manager.py::TestObservabilityManagerStats::test_get_stats_with_data PASSED [ 98%]
tests/unit/test_observability_manager.py::TestObservabilityManagerErrorHandling::test_error_handling_invalid_trace PASSED [ 99%]
tests/unit/test_observability_manager.py::TestObservabilityManagerErrorHandling::test_concurrent_trace_recording PASSED [100%]

=================================== FAILURES ===================================
_____________________ TestSystemGraphDB.test_get_component _____________________
tests/observer_enhanced/graph/test_graph_db.py:72: in test_get_component
    comp = populated_db.get_component('PMAgent')
           ^^^^^^^^^^^^^^^^^^^^^^^^^^
E   AttributeError: 'SystemGraphDB' object has no attribute 'get_component'. Did you mean: 'add_component'?
---------------------------- Captured stdout setup -----------------------------
⚠️  グラフDB読み込みエラー: 'links'
___________________ TestSystemGraphDB.test_update_component ____________________
tests/observer_enhanced/graph/test_graph_db.py:80: in test_update_component
    success = populated_db.update_component('PMAgent', {'lines': 900})
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   AttributeError: 'SystemGraphDB' object has no attribute 'update_component'. Did you mean: 'add_component'?
---------------------------- Captured stdout setup -----------------------------
⚠️  グラフDB読み込みエラー: 'links'
___________________ TestSystemGraphDB.test_remove_component ____________________
tests/observer_enhanced/graph/test_graph_db.py:91: in test_remove_component
    success = populated_db.remove_component('Dashboard')
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   AttributeError: 'SystemGraphDB' object has no attribute 'remove_component'
---------------------------- Captured stdout setup -----------------------------
⚠️  グラフDB読み込みエラー: 'links'
____________________ TestSystemGraphDB.test_list_components ____________________
tests/observer_enhanced/graph/test_graph_db.py:100: in test_list_components
    all_comps = populated_db.list_components()
                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   AttributeError: 'SystemGraphDB' object has no attribute 'list_components'. Did you mean: 'add_component'?
---------------------------- Captured stdout setup -----------------------------
⚠️  グラフDB読み込みエラー: 'links'
____________________ TestSystemGraphDB.test_get_dependency _____________________
tests/observer_enhanced/graph/test_graph_db.py:126: in test_get_dependency
    dep = populated_db.get_dependency('PMAgent', 'SheetsManager')
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   AttributeError: 'SystemGraphDB' object has no attribute 'get_dependency'. Did you mean: 'add_dependency'?
---------------------------- Captured stdout setup -----------------------------
⚠️  グラフDB読み込みエラー: 'links'
___________________ TestSystemGraphDB.test_remove_dependency ___________________
tests/observer_enhanced/graph/test_graph_db.py:136: in test_remove_dependency
    success = populated_db.remove_dependency('PMAgent', 'SheetsManager')
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   AttributeError: 'SystemGraphDB' object has no attribute 'remove_dependency'
---------------------------- Captured stdout setup -----------------------------
⚠️  グラフDB読み込みエラー: 'links'
________________ TestSystemGraphDB.test_get_impact_range_depth1 ________________
tests/observer_enhanced/graph/test_graph_db.py:161: in test_get_impact_range_depth1
    affected = populated_db.get_impact_range('SheetsManager', depth=1, direction='in')
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   AttributeError: 'SystemGraphDB' object has no attribute 'get_impact_range'. Did you mean: 'get_impact_scope'?
---------------------------- Captured stdout setup -----------------------------
⚠️  グラフDB読み込みエラー: 'links'
________________ TestSystemGraphDB.test_get_impact_range_depth2 ________________
tests/observer_enhanced/graph/test_graph_db.py:170: in test_get_impact_range_depth2
    affected = populated_db.get_impact_range('SheetsManager', depth=2, direction='in')
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   AttributeError: 'SystemGraphDB' object has no attribute 'get_impact_range'. Did you mean: 'get_impact_scope'?
---------------------------- Captured stdout setup -----------------------------
⚠️  グラフDB読み込みエラー: 'links'
___________________ TestSystemGraphDB.test_get_shortest_path ___________________
tests/observer_enhanced/graph/test_graph_db.py:178: in test_get_shortest_path
    path = populated_db.get_shortest_path('Dashboard', 'SheetsManager')
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   AttributeError: 'SystemGraphDB' object has no attribute 'get_shortest_path'
---------------------------- Captured stdout setup -----------------------------
⚠️  グラフDB読み込みエラー: 'links'
______________________ TestSystemGraphDB.test_find_cycles ______________________
tests/observer_enhanced/graph/test_graph_db.py:196: in test_find_cycles
    cycles = db.find_cycles()
             ^^^^^^^^^^^^^^
E   AttributeError: 'SystemGraphDB' object has no attribute 'find_cycles'
---------------------------- Captured stdout setup -----------------------------
⚠️  グラフDB読み込みエラー: 'links'
____________________ TestSystemGraphDB.test_get_statistics _____________________
tests/observer_enhanced/graph/test_graph_db.py:207: in test_get_statistics
    stats = populated_db.get_statistics()
            ^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   AttributeError: 'SystemGraphDB' object has no attribute 'get_statistics'
---------------------------- Captured stdout setup -----------------------------
⚠️  グラフDB読み込みエラー: 'links'
__________________ TestSystemGraphDB.test_get_most_dependent ___________________
tests/observer_enhanced/graph/test_graph_db.py:216: in test_get_most_dependent
    most_dep = populated_db.get_most_dependent(limit=3)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   AttributeError: 'SystemGraphDB' object has no attribute 'get_most_dependent'
---------------------------- Captured stdout setup -----------------------------
⚠️  グラフDB読み込みエラー: 'links'
__________________ TestSystemGraphDB.test_get_most_depending ___________________
tests/observer_enhanced/graph/test_graph_db.py:225: in test_get_most_depending
    most_dep = populated_db.get_most_depending(limit=3)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   AttributeError: 'SystemGraphDB' object has no attribute 'get_most_depending'
---------------------------- Captured stdout setup -----------------------------
⚠️  グラフDB読み込みエラー: 'links'
____________________ TestSystemGraphDB.test_export_to_json _____________________
tests/observer_enhanced/graph/test_graph_db.py:237: in test_export_to_json
    json_str = populated_db.export_to_json()
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   AttributeError: 'SystemGraphDB' object has no attribute 'export_to_json'
---------------------------- Captured stdout setup -----------------------------
⚠️  グラフDB読み込みエラー: 'links'
___________________ TestSystemGraphDB.test_import_from_json ____________________
tests/observer_enhanced/graph/test_graph_db.py:248: in test_import_from_json
    populated_db.export_to_json(filepath=json_file)
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   AttributeError: 'SystemGraphDB' object has no attribute 'export_to_json'
---------------------------- Captured stdout setup -----------------------------
⚠️  グラフDB読み込みエラー: 'links'
_______________ TestSystemGraphDB.test_performance_impact_range ________________
tests/observer_enhanced/graph/test_graph_db.py:294: in test_performance_impact_range
    affected = populated_db.get_impact_range('SheetsManager', depth=3)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   AttributeError: 'SystemGraphDB' object has no attribute 'get_impact_range'. Did you mean: 'get_impact_scope'?
---------------------------- Captured stdout setup -----------------------------
⚠️  グラフDB読み込みエラー: 'links'
_________________ TestImpactAnalyzer.test_analyze_impact_basic _________________
tests/observer_enhanced/graph/test_impact_analyzer.py:63: in test_analyze_impact_basic
    result = analyzer_with_data.analyze_impact('SheetsManager')
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
agents/observer_enhanced/graph/impact_analyzer.py:75: in analyze_impact
    affected = self.graph_db.get_impact_range(
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   AttributeError: 'SystemGraphDB' object has no attribute 'get_impact_range'. Did you mean: 'get_impact_scope'?
---------------------------- Captured stdout setup -----------------------------
⚠️  グラフDB読み込みエラー: 'links'
_________________ TestImpactAnalyzer.test_analyze_impact_depth _________________
tests/observer_enhanced/graph/test_impact_analyzer.py:73: in test_analyze_impact_depth
    result_d1 = analyzer_with_data.analyze_impact('SheetsManager', depth=1)
                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
agents/observer_enhanced/graph/impact_analyzer.py:75: in analyze_impact
    affected = self.graph_db.get_impact_range(
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   AttributeError: 'SystemGraphDB' object has no attribute 'get_impact_range'. Did you mean: 'get_impact_scope'?
---------------------------- Captured stdout setup -----------------------------
⚠️  グラフDB読み込みエラー: 'links'
_____________ TestImpactAnalyzer.test_analyze_impact_direction_in ______________
tests/observer_enhanced/graph/test_impact_analyzer.py:85: in test_analyze_impact_direction_in
    result = analyzer_with_data.analyze_impact('SheetsManager', direction='in')
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
agents/observer_enhanced/graph/impact_analyzer.py:75: in analyze_impact
    affected = self.graph_db.get_impact_range(
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   AttributeError: 'SystemGraphDB' object has no attribute 'get_impact_range'. Did you mean: 'get_impact_scope'?
---------------------------- Captured stdout setup -----------------------------
⚠️  グラフDB読み込みエラー: 'links'
_____________ TestImpactAnalyzer.test_analyze_impact_direction_out _____________
tests/observer_enhanced/graph/test_impact_analyzer.py:94: in test_analyze_impact_direction_out
    result = analyzer_with_data.analyze_impact('PMAgent', direction='out')
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
agents/observer_enhanced/graph/impact_analyzer.py:75: in analyze_impact
    affected = self.graph_db.get_impact_range(
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   AttributeError: 'SystemGraphDB' object has no attribute 'get_impact_range'. Did you mean: 'get_impact_scope'?
---------------------------- Captured stdout setup -----------------------------
⚠️  グラフDB読み込みエラー: 'links'
______________________ TestImpactAnalyzer.test_find_path _______________________
tests/observer_enhanced/graph/test_impact_analyzer.py:114: in test_find_path
    path = analyzer_with_data.find_path('Dashboard', 'SheetsManager')
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
agents/observer_enhanced/graph/impact_analyzer.py:108: in find_path
    return self.graph_db.get_shortest_path(source, target)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   AttributeError: 'SystemGraphDB' object has no attribute 'get_shortest_path'
---------------------------- Captured stdout setup -----------------------------
⚠️  グラフDB読み込みエラー: 'links'
__________________ TestImpactAnalyzer.test_find_path_no_path ___________________
tests/observer_enhanced/graph/test_impact_analyzer.py:124: in test_find_path_no_path
    path = analyzer_with_data.find_path('SheetsManager', 'Dashboard')
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
agents/observer_enhanced/graph/impact_analyzer.py:108: in find_path
    return self.graph_db.get_shortest_path(source, target)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   AttributeError: 'SystemGraphDB' object has no attribute 'get_shortest_path'
---------------------------- Captured stdout setup -----------------------------
⚠️  グラフDB読み込みエラー: 'links'
________________ TestImpactAnalyzer.test_detect_cycles_no_cycle ________________
tests/observer_enhanced/graph/test_impact_analyzer.py:135: in test_detect_cycles_no_cycle
    cycles = analyzer_with_data.detect_cycles()
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
agents/observer_enhanced/graph/impact_analyzer.py:117: in detect_cycles
    return self.graph_db.find_cycles()
           ^^^^^^^^^^^^^^^^^^^^^^^^^
E   AttributeError: 'SystemGraphDB' object has no attribute 'find_cycles'
---------------------------- Captured stdout setup -----------------------------
⚠️  グラフDB読み込みエラー: 'links'
_______________ TestImpactAnalyzer.test_detect_cycles_with_cycle _______________
tests/observer_enhanced/graph/test_impact_analyzer.py:151: in test_detect_cycles_with_cycle
    cycles = analyzer.detect_cycles()
             ^^^^^^^^^^^^^^^^^^^^^^^^
agents/observer_enhanced/graph/impact_analyzer.py:117: in detect_cycles
    return self.graph_db.find_cycles()
           ^^^^^^^^^^^^^^^^^^^^^^^^^
E   AttributeError: 'SystemGraphDB' object has no attribute 'find_cycles'
---------------------------- Captured stdout setup -----------------------------
⚠️  グラフDB読み込みエラー: 'links'
____________ TestImpactAnalyzer.test_generate_test_recommendations _____________
tests/observer_enhanced/graph/test_impact_analyzer.py:213: in test_generate_test_recommendations
    result = analyzer_with_data.generate_test_recommendations(
agents/observer_enhanced/graph/impact_analyzer.py:141: in generate_test_recommendations
    impact = self.analyze_impact(component_id, depth=3, direction='in')
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
agents/observer_enhanced/graph/impact_analyzer.py:75: in analyze_impact
    affected = self.graph_db.get_impact_range(
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   AttributeError: 'SystemGraphDB' object has no attribute 'get_impact_range'. Did you mean: 'get_impact_scope'?
---------------------------- Captured stdout setup -----------------------------
⚠️  グラフDB読み込みエラー: 'links'
___________ TestImpactAnalyzer.test_recommendations_for_large_change ___________
tests/observer_enhanced/graph/test_impact_analyzer.py:236: in test_recommendations_for_large_change
    result = analyzer_with_data.generate_test_recommendations(
agents/observer_enhanced/graph/impact_analyzer.py:141: in generate_test_recommendations
    impact = self.analyze_impact(component_id, depth=3, direction='in')
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
agents/observer_enhanced/graph/impact_analyzer.py:75: in analyze_impact
    affected = self.graph_db.get_impact_range(
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   AttributeError: 'SystemGraphDB' object has no attribute 'get_impact_range'. Did you mean: 'get_impact_scope'?
---------------------------- Captured stdout setup -----------------------------
⚠️  グラフDB読み込みエラー: 'links'
______________ TestImpactAnalyzer.test_performance_analyze_impact ______________
tests/observer_enhanced/graph/test_impact_analyzer.py:258: in test_performance_analyze_impact
    result = analyzer_with_data.analyze_impact('SheetsManager', depth=3)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
agents/observer_enhanced/graph/impact_analyzer.py:75: in analyze_impact
    affected = self.graph_db.get_impact_range(
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   AttributeError: 'SystemGraphDB' object has no attribute 'get_impact_range'. Did you mean: 'get_impact_scope'?
---------------------------- Captured stdout setup -----------------------------
⚠️  グラフDB読み込みエラー: 'links'
_________ TestImpactAnalyzer.test_performance_generate_recommendations _________
tests/observer_enhanced/graph/test_impact_analyzer.py:269: in test_performance_generate_recommendations
    result = analyzer_with_data.generate_test_recommendations('SheetsManager', 100)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
agents/observer_enhanced/graph/impact_analyzer.py:141: in generate_test_recommendations
    impact = self.analyze_impact(component_id, depth=3, direction='in')
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
agents/observer_enhanced/graph/impact_analyzer.py:75: in analyze_impact
    affected = self.graph_db.get_impact_range(
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   AttributeError: 'SystemGraphDB' object has no attribute 'get_impact_range'. Did you mean: 'get_impact_scope'?
---------------------------- Captured stdout setup -----------------------------
⚠️  グラフDB読み込みエラー: 'links'
_________________________ test_alerts_api_status_code __________________________
tests/observer_enhanced/test_api.py:200: in test_alerts_api_status_code
    assert response.status_code == 200
E   assert 500 == 200
E    +  where 500 = <Response [500 Internal Server Error]>.status_code
------------------------------ Captured log call -------------------------------
ERROR    agents.observer_enhanced.web.api_endpoints:api_endpoints.py:338 Error in get_alerts: 'AlertManager' object has no attribute 'get_alerts'
__________________________ test_alerts_api_parameters __________________________
tests/observer_enhanced/test_api.py:208: in test_alerts_api_parameters
    assert "alerts" in data
E   assert 'alerts' in {'detail': "'AlertManager' object has no attribute 'get_alerts'"}
------------------------------ Captured log call -------------------------------
ERROR    agents.observer_enhanced.web.api_endpoints:api_endpoints.py:338 Error in get_alerts: 'AlertManager' object has no attribute 'get_alerts'
_________________________ test_alerts_api_level_filter _________________________
tests/observer_enhanced/test_api.py:217: in test_alerts_api_level_filter
    assert response.status_code == 200
E   assert 500 == 200
E    +  where 500 = <Response [500 Internal Server Error]>.status_code
------------------------------ Captured log call -------------------------------
ERROR    agents.observer_enhanced.web.api_endpoints:api_endpoints.py:338 Error in get_alerts: 'AlertManager' object has no attribute 'get_alerts'
______________________________ test_cors_methods _______________________________
tests/observer_enhanced/test_api.py:259: in test_cors_methods
    assert response.status_code == expected_status,                f"{endpoint} returned {response.status_code}, expected {expected_status}"
E   AssertionError: /api/alerts?limit=3 returned 500, expected 200
E   assert 500 == 200
E    +  where 500 = <Response [500 Internal Server Error]>.status_code
------------------------------ Captured log call -------------------------------
ERROR    agents.observer_enhanced.web.api_endpoints:api_endpoints.py:338 Error in get_alerts: 'AlertManager' object has no attribute 'get_alerts'
______________________________ test_full_workflow ______________________________
tests/observer_enhanced/test_api.py:298: in test_full_workflow
    assert response.status_code == 200
E   assert 500 == 200
E    +  where 500 = <Response [500 Internal Server Error]>.status_code
------------------------------ Captured log call -------------------------------
ERROR    agents.observer_enhanced.web.api_endpoints:api_endpoints.py:338 Error in get_alerts: 'AlertManager' object has no attribute 'get_alerts'
_______________________ TestAPIServer.test_health_check ________________________
tests/observer_enhanced/test_api_server.py:27: in test_health_check
    assert "status" in response.json()
                       ^^^^^^^^^^^^^^^
/home/codespace/.local/lib/python3.12/site-packages/httpx/_models.py:832: in json
    return jsonlib.loads(self.content, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/python/3.12.1/lib/python3.12/json/__init__.py:346: in loads
    return _default_decoder.decode(s)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/python/3.12.1/lib/python3.12/json/decoder.py:337: in decode
    obj, end = self.raw_decode(s, idx=_w(s, 0).end())
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/python/3.12.1/lib/python3.12/json/decoder.py:355: in raw_decode
    raise JSONDecodeError("Expecting value", s, err.value) from None
E   json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)
______________________ TestAPIServer.test_get_duplicates _______________________
tests/observer_enhanced/test_api_server.py:42: in test_get_duplicates
    assert response.status_code == 200
E   assert 404 == 200
E    +  where 404 = <Response [404 Not Found]>.status_code
_______________________ TestAPIServer.test_cors_headers ________________________
tests/observer_enhanced/test_api_server.py:64: in test_cors_headers
    assert "access-control-allow-origin" in response.headers or response.status_code == 200
E   AssertionError: assert ('access-control-allow-origin' in Headers({'allow': 'GET', 'content-length': '31', 'content-type': 'application/json'}) or 405 == 200)
E    +  where Headers({'allow': 'GET', 'content-length': '31', 'content-type': 'application/json'}) = <Response [405 Method Not Allowed]>.headers
E    +  and   405 = <Response [405 Method Not Allowed]>.status_code
_____________________ TestAPIServerFixed.test_health_check _____________________
tests/observer_enhanced/test_api_server_fixed.py:26: in test_health_check
    data = response.json()
           ^^^^^^^^^^^^^^^
/home/codespace/.local/lib/python3.12/site-packages/httpx/_models.py:832: in json
    return jsonlib.loads(self.content, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/python/3.12.1/lib/python3.12/json/__init__.py:346: in loads
    return _default_decoder.decode(s)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/python/3.12.1/lib/python3.12/json/decoder.py:337: in decode
    obj, end = self.raw_decode(s, idx=_w(s, 0).end())
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/python/3.12.1/lib/python3.12/json/decoder.py:355: in raw_decode
    raise JSONDecodeError("Expecting value", s, err.value) from None
E   json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)
____________________ TestAPIServerFixed.test_get_duplicates ____________________
tests/observer_enhanced/test_api_server_fixed.py:51: in test_get_duplicates
    assert response.status_code == 200
E   assert 404 == 200
E    +  where 404 = <Response [404 Not Found]>.status_code
_______________ TestImportExtractor.test_extract_simple_imports ________________
tests/observer_enhanced/test_import_extractor.py:64: in test_extract_simple_imports
    assert any(
tests/observer_enhanced/test_import_extractor.py:65: in <genexpr>
    imp.module == 'os' and imp.import_type == 'import'
    ^^^^^^^^^^
E   AttributeError: 'dict' object has no attribute 'module'
_______________ TestImportExtractor.test_extract_complex_imports _______________
tests/observer_enhanced/test_import_extractor.py:94: in test_extract_complex_imports
    typing_import = next(
tests/observer_enhanced/test_import_extractor.py:95: in <genexpr>
    (imp for imp in imports if imp.module == 'typing'),
                               ^^^^^^^^^^
E   AttributeError: 'dict' object has no attribute 'module'
______________ TestImportExtractor.test_filter_internal_external _______________
tests/observer_enhanced/test_import_extractor.py:141: in test_filter_internal_external
    assert any('agents' in imp.module for imp in internal)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
tests/observer_enhanced/test_import_extractor.py:141: in <genexpr>
    assert any('agents' in imp.module for imp in internal)
                           ^^^^^^^^^^
E   AttributeError: 'dict' object has no attribute 'module'
___________________________ test_learning_optimizer ____________________________
tests/test_phase3_agents.py:60: in test_learning_optimizer
    result = await optimizer.execute({"type": "analyze"})
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
agents/learning/learning_optimizer.py:373: in execute
    result = await self.analyze_knowledge_base()
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
agents/learning/learning_optimizer.py:56: in analyze_knowledge_base
    data = json.load(f)
           ^^^^^^^^^^^^
/usr/local/python/3.12.1/lib/python3.12/json/__init__.py:293: in load
    return loads(fp.read(),
/usr/local/python/3.12.1/lib/python3.12/json/__init__.py:346: in loads
    return _default_decoder.decode(s)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/python/3.12.1/lib/python3.12/json/decoder.py:337: in decode
    obj, end = self.raw_decode(s, idx=_w(s, 0).end())
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/local/python/3.12.1/lib/python3.12/json/decoder.py:353: in raw_decode
    obj, end = self.scan_once(s, idx)
               ^^^^^^^^^^^^^^^^^^^^^^
E   json.decoder.JSONDecodeError: Expecting property name enclosed in double quotes: line 17 column 29 (char 609)
----------------------------- Captured stdout call -----------------------------

============================================================
🧠 LearningOptimizer テスト開始
============================================================
=============================== warnings summary ===============================
tests/e2e/test_autonomous_cycle.py:20
  /workspaces/gemini_AI_Agent/tests/e2e/test_autonomous_cycle.py:20: PytestUnknownMarkWarning: Unknown pytest.mark.timeout - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.timeout(300)

<frozen importlib._bootstrap>:488
  <frozen importlib._bootstrap>:488: DeprecationWarning: builtin type SwigPyPacked has no __module__ attribute

<frozen importlib._bootstrap>:488
  <frozen importlib._bootstrap>:488: DeprecationWarning: builtin type SwigPyObject has no __module__ attribute

<frozen importlib._bootstrap>:488
  <frozen importlib._bootstrap>:488: DeprecationWarning: builtin type swigvarlink has no __module__ attribute

tests/integration/test_integrated_v31_core.py:54
  /workspaces/gemini_AI_Agent/tests/integration/test_integrated_v31_core.py:54: PytestUnknownMarkWarning: Unknown pytest.mark.timeout - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.timeout(60)

tests/integration/test_knowledge_integration.py:6
  /workspaces/gemini_AI_Agent/tests/integration/test_knowledge_integration.py:6: PytestUnknownMarkWarning: Unknown pytest.mark.timeout - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.timeout(60)

tests/integration/test_phase4_integration.py:6
  /workspaces/gemini_AI_Agent/tests/integration/test_phase4_integration.py:6: PytestUnknownMarkWarning: Unknown pytest.mark.timeout - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.timeout(60)

agents/observer_enhanced/web/api_server.py:139
  /workspaces/gemini_AI_Agent/agents/observer_enhanced/web/api_server.py:139: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

../../usr/local/python/3.12.1/lib/python3.12/site-packages/fastapi/applications.py:4575
../../usr/local/python/3.12.1/lib/python3.12/site-packages/fastapi/applications.py:4575
  /usr/local/python/3.12.1/lib/python3.12/site-packages/fastapi/applications.py:4575: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    return self.router.on_event(event_type)

agents/observer_enhanced/web/api_server.py:150
  /workspaces/gemini_AI_Agent/agents/observer_enhanced/web/api_server.py:150: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("shutdown")

tests/test_result_reporter.py:15
  /workspaces/gemini_AI_Agent/tests/test_result_reporter.py:15: PytestCollectionWarning: cannot collect test class 'TestResultReporter' because it has a __init__ constructor (from: tests/test_result_reporter.py)
    class TestResultReporter:

tests/unit/test_knowledge_base_adapter.py:6
  /workspaces/gemini_AI_Agent/tests/unit/test_knowledge_base_adapter.py:6: PytestUnknownMarkWarning: Unknown pytest.mark.timeout - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.timeout(30)

tests/unit/test_knowledge_manager.py:6
  /workspaces/gemini_AI_Agent/tests/unit/test_knowledge_manager.py:6: PytestUnknownMarkWarning: Unknown pytest.mark.timeout - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.timeout(1)

tests/unit/test_observability_core.py:6
  /workspaces/gemini_AI_Agent/tests/unit/test_observability_core.py:6: PytestUnknownMarkWarning: Unknown pytest.mark.timeout - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.timeout(1)

tests/unit/test_observability_core.py:36
  /workspaces/gemini_AI_Agent/tests/unit/test_observability_core.py:36: PytestUnknownMarkWarning: Unknown pytest.mark.timeout - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.timeout(1)

tests/unit/test_observability_manager.py:30
  /workspaces/gemini_AI_Agent/tests/unit/test_observability_manager.py:30: PytestUnknownMarkWarning: Unknown pytest.mark.timeout - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.timeout(1)

tests/unit/test_observability_manager.py:68
  /workspaces/gemini_AI_Agent/tests/unit/test_observability_manager.py:68: PytestUnknownMarkWarning: Unknown pytest.mark.timeout - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.timeout(1)

tests/unit/test_observability_manager.py:104
  /workspaces/gemini_AI_Agent/tests/unit/test_observability_manager.py:104: PytestUnknownMarkWarning: Unknown pytest.mark.timeout - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.timeout(1)

tests/unit/test_observability_manager.py:132
  /workspaces/gemini_AI_Agent/tests/unit/test_observability_manager.py:132: PytestUnknownMarkWarning: Unknown pytest.mark.timeout - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.timeout(1)

tests/integration/test_extended_features.py::TestHiddenDependencyDetector::test_scan_project
  <unknown>:11: SyntaxWarning: invalid escape sequence '\s'

tests/integration/test_extended_features.py::TestHiddenDependencyDetector::test_scan_project
  <unknown>:253: SyntaxWarning: invalid escape sequence '\`'

tests/integration/test_extended_features.py: 3 warnings
tests/observer_enhanced/graph/test_graph_db.py: 21 warnings
tests/observer_enhanced/graph/test_impact_analyzer.py: 15 warnings
  /home/codespace/.local/lib/python3.12/site-packages/networkx/readwrite/json_graph/node_link.py:290: FutureWarning: 
  The default value will be changed to `edges="edges" in NetworkX 3.6.
  
  To make this warning go away, explicitly set the edges kwarg, e.g.:
  
    nx.node_link_graph(data, edges="links") to preserve current behavior, or
    nx.node_link_graph(data, edges="edges") for forward compatibility.
    warnings.warn(

tests/system_protection/test_core_functions.py::test_f1_goal_concrete
  /usr/local/python/3.12.1/lib/python3.12/site-packages/_pytest/python.py:170: PytestReturnNotNoneWarning: Test functions should return None, but tests/system_protection/test_core_functions.py::test_f1_goal_concrete returned <class 'bool'>.
  Did you mean to use `assert` instead of `return`?
  See https://docs.pytest.org/en/stable/how-to/assert.html#return-not-none for more information.
    warnings.warn(

tests/system_protection/test_core_functions.py::test_f2_task_execution
  /usr/local/python/3.12.1/lib/python3.12/site-packages/_pytest/python.py:170: PytestReturnNotNoneWarning: Test functions should return None, but tests/system_protection/test_core_functions.py::test_f2_task_execution returned <class 'bool'>.
  Did you mean to use `assert` instead of `return`?
  See https://docs.pytest.org/en/stable/how-to/assert.html#return-not-none for more information.
    warnings.warn(

tests/system_protection/test_core_functions.py::test_f3_quality_evaluator
  /usr/local/python/3.12.1/lib/python3.12/site-packages/_pytest/python.py:170: PytestReturnNotNoneWarning: Test functions should return None, but tests/system_protection/test_core_functions.py::test_f3_quality_evaluator returned <class 'bool'>.
  Did you mean to use `assert` instead of `return`?
  See https://docs.pytest.org/en/stable/how-to/assert.html#return-not-none for more information.
    warnings.warn(

tests/system_protection/test_core_functions.py::test_f4_knowledge_system
  /usr/local/python/3.12.1/lib/python3.12/site-packages/_pytest/python.py:170: PytestReturnNotNoneWarning: Test functions should return None, but tests/system_protection/test_core_functions.py::test_f4_knowledge_system returned <class 'bool'>.
  Did you mean to use `assert` instead of `return`?
  See https://docs.pytest.org/en/stable/how-to/assert.html#return-not-none for more information.
    warnings.warn(

tests/system_protection/test_core_functions.py::test_f7_self_healing
  /usr/local/python/3.12.1/lib/python3.12/site-packages/_pytest/python.py:170: PytestReturnNotNoneWarning: Test functions should return None, but tests/system_protection/test_core_functions.py::test_f7_self_healing returned <class 'bool'>.
  Did you mean to use `assert` instead of `return`?
  See https://docs.pytest.org/en/stable/how-to/assert.html#return-not-none for more information.
    warnings.warn(

tests/system_protection/test_core_functions.py::test_f8_self_evolution
  /usr/local/python/3.12.1/lib/python3.12/site-packages/_pytest/python.py:170: PytestReturnNotNoneWarning: Test functions should return None, but tests/system_protection/test_core_functions.py::test_f8_self_evolution returned <class 'bool'>.
  Did you mean to use `assert` instead of `return`?
  See https://docs.pytest.org/en/stable/how-to/assert.html#return-not-none for more information.
    warnings.warn(

tests/system_protection/test_core_functions.py::test_f9_human_collaboration
  /usr/local/python/3.12.1/lib/python3.12/site-packages/_pytest/python.py:170: PytestReturnNotNoneWarning: Test functions should return None, but tests/system_protection/test_core_functions.py::test_f9_human_collaboration returned <class 'bool'>.
  Did you mean to use `assert` instead of `return`?
  See https://docs.pytest.org/en/stable/how-to/assert.html#return-not-none for more information.
    warnings.warn(

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ============================
FAILED tests/observer_enhanced/graph/test_graph_db.py::TestSystemGraphDB::test_get_component
FAILED tests/observer_enhanced/graph/test_graph_db.py::TestSystemGraphDB::test_update_component
FAILED tests/observer_enhanced/graph/test_graph_db.py::TestSystemGraphDB::test_remove_component
FAILED tests/observer_enhanced/graph/test_graph_db.py::TestSystemGraphDB::test_list_components
FAILED tests/observer_enhanced/graph/test_graph_db.py::TestSystemGraphDB::test_get_dependency
FAILED tests/observer_enhanced/graph/test_graph_db.py::TestSystemGraphDB::test_remove_dependency
FAILED tests/observer_enhanced/graph/test_graph_db.py::TestSystemGraphDB::test_get_impact_range_depth1
FAILED tests/observer_enhanced/graph/test_graph_db.py::TestSystemGraphDB::test_get_impact_range_depth2
FAILED tests/observer_enhanced/graph/test_graph_db.py::TestSystemGraphDB::test_get_shortest_path
FAILED tests/observer_enhanced/graph/test_graph_db.py::TestSystemGraphDB::test_find_cycles
FAILED tests/observer_enhanced/graph/test_graph_db.py::TestSystemGraphDB::test_get_statistics
FAILED tests/observer_enhanced/graph/test_graph_db.py::TestSystemGraphDB::test_get_most_dependent
FAILED tests/observer_enhanced/graph/test_graph_db.py::TestSystemGraphDB::test_get_most_depending
FAILED tests/observer_enhanced/graph/test_graph_db.py::TestSystemGraphDB::test_export_to_json
FAILED tests/observer_enhanced/graph/test_graph_db.py::TestSystemGraphDB::test_import_from_json
FAILED tests/observer_enhanced/graph/test_graph_db.py::TestSystemGraphDB::test_performance_impact_range
FAILED tests/observer_enhanced/graph/test_impact_analyzer.py::TestImpactAnalyzer::test_analyze_impact_basic
FAILED tests/observer_enhanced/graph/test_impact_analyzer.py::TestImpactAnalyzer::test_analyze_impact_depth
FAILED tests/observer_enhanced/graph/test_impact_analyzer.py::TestImpactAnalyzer::test_analyze_impact_direction_in
FAILED tests/observer_enhanced/graph/test_impact_analyzer.py::TestImpactAnalyzer::test_analyze_impact_direction_out
FAILED tests/observer_enhanced/graph/test_impact_analyzer.py::TestImpactAnalyzer::test_find_path
FAILED tests/observer_enhanced/graph/test_impact_analyzer.py::TestImpactAnalyzer::test_find_path_no_path
FAILED tests/observer_enhanced/graph/test_impact_analyzer.py::TestImpactAnalyzer::test_detect_cycles_no_cycle
FAILED tests/observer_enhanced/graph/test_impact_analyzer.py::TestImpactAnalyzer::test_detect_cycles_with_cycle
FAILED tests/observer_enhanced/graph/test_impact_analyzer.py::TestImpactAnalyzer::test_generate_test_recommendations
FAILED tests/observer_enhanced/graph/test_impact_analyzer.py::TestImpactAnalyzer::test_recommendations_for_large_change
FAILED tests/observer_enhanced/graph/test_impact_analyzer.py::TestImpactAnalyzer::test_performance_analyze_impact
FAILED tests/observer_enhanced/graph/test_impact_analyzer.py::TestImpactAnalyzer::test_performance_generate_recommendations
FAILED tests/observer_enhanced/test_api.py::test_alerts_api_status_code - ass...
FAILED tests/observer_enhanced/test_api.py::test_alerts_api_parameters - asse...
FAILED tests/observer_enhanced/test_api.py::test_alerts_api_level_filter - as...
FAILED tests/observer_enhanced/test_api.py::test_cors_methods - AssertionErro...
FAILED tests/observer_enhanced/test_api.py::test_full_workflow - assert 500 =...
FAILED tests/observer_enhanced/test_api_server.py::TestAPIServer::test_health_check
FAILED tests/observer_enhanced/test_api_server.py::TestAPIServer::test_get_duplicates
FAILED tests/observer_enhanced/test_api_server.py::TestAPIServer::test_cors_headers
FAILED tests/observer_enhanced/test_api_server_fixed.py::TestAPIServerFixed::test_health_check
FAILED tests/observer_enhanced/test_api_server_fixed.py::TestAPIServerFixed::test_get_duplicates
FAILED tests/observer_enhanced/test_import_extractor.py::TestImportExtractor::test_extract_simple_imports
FAILED tests/observer_enhanced/test_import_extractor.py::TestImportExtractor::test_extract_complex_imports
FAILED tests/observer_enhanced/test_import_extractor.py::TestImportExtractor::test_filter_internal_external
FAILED tests/test_phase3_agents.py::test_learning_optimizer - json.decoder.JS...
=========== 42 failed, 129 passed, 7 skipped, 68 warnings in 47.01s ============
```
