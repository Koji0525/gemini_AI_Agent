"""
ImportExtractor テスト

実装ファイル: tests/observer_enhanced/test_import_extractor.py
行数目標: 300行
テスト件数: 5件
成功率目標: 100%
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, '/workspaces/gemini_AI_Agent')

from agents.observer_enhanced.import_extractor import ImportExtractor, ImportRelation


class TestImportExtractor:
    """ImportExtractorのテストクラス"""
    
    @pytest.fixture
    def extractor(self):
        """テスト用ImportExtractorインスタンス"""
        return ImportExtractor()
    
    @pytest.fixture
    def sample_code_simple(self, tmp_path):
        """シンプルなimport文のサンプルコード"""
        file_path = tmp_path / "simple.py"
        file_path.write_text("""
import os
import sys
from pathlib import Path
""")
        return file_path
    
    @pytest.fixture
    def sample_code_complex(self, tmp_path):
        """複雑なimport文のサンプルコード"""
        file_path = tmp_path / "complex.py"
        file_path.write_text("""
import os
import sys
from pathlib import Path
from typing import List, Dict, Optional
from agents.pm_agent import PMAgent
from tools.sheets_manager import GoogleSheetsManager
import google.auth as auth
""")
        return file_path
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Test 1: 基本的なimport抽出
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    def test_extract_simple_imports(self, extractor, sample_code_simple):
        """シンプルなimport文の抽出テスト"""
        imports = extractor.extract_from_file(sample_code_simple)
        
        # 検証
        assert len(imports) == 3  # os, sys, pathlib.Path
        
        # import os
        assert any(
            imp.module == 'os' and imp.import_type == 'import'
            for imp in imports
        )
        
        # import sys
        assert any(
            imp.module == 'sys' and imp.import_type == 'import'
            for imp in imports
        )
        
        # from pathlib import Path
        assert any(
            imp.module == 'pathlib' and 
            imp.import_type == 'from' and
            'Path' in imp.names
            for imp in imports
        )
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Test 2: 複雑なimport抽出
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    def test_extract_complex_imports(self, extractor, sample_code_complex):
        """複雑なimport文の抽出テスト"""
        imports = extractor.extract_from_file(sample_code_complex)
        
        # 検証
        assert len(imports) >= 6
        
        # from typing import List, Dict, Optional
        typing_import = next(
            (imp for imp in imports if imp.module == 'typing'),
            None
        )
        assert typing_import is not None
        assert 'List' in typing_import.names
        assert 'Dict' in typing_import.names
        assert 'Optional' in typing_import.names
        
        # from agents.pm_agent import PMAgent
        pm_import = next(
            (imp for imp in imports if 'pm_agent' in imp.module),
            None
        )
        assert pm_import is not None
        assert 'PMAgent' in pm_import.names
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Test 3: 実ファイルでのテスト
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    def test_extract_from_real_file(self, extractor):
        """実際の既存ファイル（pm_agent.py）でのテスト"""
        pm_agent_path = Path('/workspaces/gemini_AI_Agent/agents/pm_agent.py')
        
        if not pm_agent_path.exists():
            pytest.skip("pm_agent.py not found")
        
        imports = extractor.extract_from_file(pm_agent_path)
        
        # 検証
        assert len(imports) > 0  # 何らかのimportがある
        
        # sheets_managerへの依存があるはず
        assert any(
            'sheets_manager' in imp.module or 'SheetsManager' in imp.names
            for imp in imports
        ), "pm_agent.py should import sheets_manager"
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Test 4: 内部/外部import分類
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    def test_filter_internal_external(self, extractor, sample_code_complex):
        """内部/外部importのフィルタリングテスト"""
        imports = extractor.extract_from_file(sample_code_complex)
        
        # 内部import
        internal = extractor.filter_internal_imports(imports)
        assert any('agents' in imp.module for imp in internal)
        assert any('tools' in imp.module for imp in internal)
        
        # 外部import
        external = extractor.filter_external_imports(imports)
        assert any(imp.module == 'os' for imp in external)
        assert any(imp.module == 'sys' for imp in external)
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Test 5: パフォーマンステスト
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    def test_performance(self, extractor, sample_code_complex):
        """パフォーマンステスト（50ms以内）"""
        import time
        
        start = time.time()
        imports = extractor.extract_from_file(sample_code_complex)
        duration = (time.time() - start) * 1000  # ミリ秒
        
        # 検証
        assert duration < 50, f"処理時間 {duration:.2f}ms > 50ms"
        assert len(imports) > 0


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 統合テスト
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class TestImportExtractorIntegration:
    """統合テスト"""
    
    def test_full_workflow(self, tmp_path):
        """完全なワークフローテスト"""
        # 1. サンプルファイル作成
        file1 = tmp_path / "module1.py"
        file1.write_text("""
import os
from pathlib import Path
from module2 import helper
""")
        
        file2 = tmp_path / "module2.py"
        file2.write_text("""
import sys
from module1 import main
""")
        
        # 2. 抽出
        extractor = ImportExtractor()
        imports = extractor.extract_from_directory(tmp_path)
        
        # 3. 検証
        assert len(imports) >= 4  # 両ファイルのimport
        
        # 4. グループ化
        by_file = extractor.get_imports_by_file(imports)
        assert len(by_file) == 2  # 2ファイル
        
        # 5. モジュール集合
        modules = extractor.get_imported_modules(imports)
        assert 'os' in modules
        assert 'sys' in modules

