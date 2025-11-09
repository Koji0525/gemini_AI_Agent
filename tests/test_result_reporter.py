"""
テスト結果をObservabilityManagerに記録
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agents.observability.observability_manager import get_observability_manager


class TestResultReporter:
    """テスト結果レポーター"""
    
    def __init__(self):
        self.obs_manager = get_observability_manager()
    
    def report_test_results(self, test_results: Dict[str, Any]):
        """
        テスト結果をObservabilityに記録
        
        Args:
            test_results: pytestの実行結果
        """
        
        trace_data = {
            'trace_id': f"test-result-{datetime.now().timestamp()}",
            'operation_name': 'test_execution',
            'timestamp': datetime.now().isoformat(),
            'status': 'success' if test_results['failed'] == 0 else 'error',
            
            'test_stats': {
                'total': test_results['total'],
                'passed': test_results['passed'],
                'failed': test_results['failed'],
                'skipped': test_results['skipped'],
                'duration': test_results.get('duration', 0)
            },
            
            'test_type': test_results.get('test_type', 'unknown'),
            'test_coverage': test_results.get('coverage', 0)
        }
        
        self.obs_manager.record_trace(trace_data)
        print(f"✅ テスト結果をObservabilityに記録: {trace_data['trace_id']}")


if __name__ == "__main__":
    # テスト用
    reporter = TestResultReporter()
    
    sample_results = {
        'total': 10,
        'passed': 8,
        'failed': 2,
        'skipped': 0,
        'duration': 15.5,
        'test_type': 'unit'
    }
    
    reporter.report_test_results(sample_results)
