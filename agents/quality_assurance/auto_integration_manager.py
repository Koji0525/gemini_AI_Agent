"""
自動統合マネージャー
生成された成果物を既存システムに自動統合
"""

import sys
import os
import shutil
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List

sys.path.insert(0, '/workspaces/gemini_AI_Agent')

class AutoIntegrationManager:
    """自動統合マネージャー"""
    
    def __init__(self):
        self.project_root = Path("/workspaces/gemini_AI_Agent")
        self.generated_dir = self.project_root / "agents" / "generated"
        self.generated_dir.mkdir(exist_ok=True, parents=True)
        
    def integrate_output(self, output_path: str, task_id: str, quality_score: float) -> Dict:
        """成果物を統合"""
        print(f"\n{'=' * 80}")
        print(f"🔄 自動統合: {task_id}")
        print('=' * 80)
        print(f"品質スコア: {quality_score:.1f}/10")
        print()
        
        results = {
            'success': False,
            'integration_path': None,
            'actions': []
        }
        
        # 品質チェック
        if quality_score < 7.0:
            print(f"⚠️  品質スコアが低いため統合をスキップ")
            return results
        
        output_dir = Path(output_path)
        
        # 統合先ディレクトリを作成
        target_dir = self.generated_dir / task_id
        target_dir.mkdir(exist_ok=True, parents=True)
        
        # ファイルをコピー
        copied_files = []
        for file in output_dir.glob("*.py"):
            target_file = target_dir / file.name
            shutil.copy2(file, target_file)
            copied_files.append(file.name)
            print(f"  ✅ {file.name} → agents/generated/{task_id}/")
        
        results['actions'].append(f"コピー: {len(copied_files)}個")
        
        # README.mdもコピー
        readme = output_dir / "README.md"
        if readme.exists():
            shutil.copy2(readme, target_dir / "README.md")
            print(f"  ✅ README.md → agents/generated/{task_id}/")
            results['actions'].append("README.md コピー")
        
        # __init__.pyを作成
        init_content = f'''"""
Generated Module: {task_id}
Quality Score: {quality_score:.1f}/10
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

このモジュールは自動生成されました。
"""

'''
        
        # main.pyからクラスをインポート
        main_py = target_dir / "main.py"
        if main_py.exists():
            content = main_py.read_text()
            classes = re.findall(r'class (\w+)', content)
            
            if classes:
                init_content += "# 自動インポート\n"
                for cls in classes:
                    init_content += f"from .main import {cls}\n"
        
        init_file = target_dir / "__init__.py"
        init_file.write_text(init_content)
        print(f"  ✅ __init__.py 作成")
        results['actions'].append("__init__.py 作成")
        
        # 使用例を作成
        self._create_usage_doc(task_id, target_dir)
        
        results['success'] = True
        results['integration_path'] = str(target_dir)
        
        print()
        print(f"✅ 統合完了: agents/generated/{task_id}/")
        
        return results
    
    def _create_usage_doc(self, task_id: str, target_dir: Path):
        """使用例ドキュメントを作成"""
        usage_content = f"""# {task_id} 使用ガイド

## インポート方法
```python
# 方法1: モジュール全体をインポート
from agents.generated.{task_id} import *

# 方法2: 特定のクラスをインポート
# from agents.generated.{task_id}.main import ClassName
```

## 基本的な使用方法
```python
# TODO: 実際の使用例を追加
```

## 詳細情報

- ソースコード: `agents/generated/{task_id}/`
- README: `agents/generated/{task_id}/README.md`
- テスト: `agents/generated/{task_id}/test_*.py`

## 統合日時

{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        usage_file = target_dir / "USAGE.md"
        usage_file.write_text(usage_content)
        print(f"  ✅ USAGE.md 作成")

