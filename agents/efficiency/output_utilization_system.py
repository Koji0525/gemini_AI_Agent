"""
成果物活用システム
タスク実行結果を活用して開発効率を向上
"""

import sys
import os
from pathlib import Path
from datetime import datetime

sys.path.insert(0, '/workspaces/gemini_AI_Agent')

class OutputUtilizationSystem:
    """成果物活用システム"""
    
    def __init__(self):
        self.output_base = Path("agent_outputs/implementation")
        
    def analyze_all_outputs(self) -> dict:
        """全成果物を分析"""
        print("\n" + "=" * 80)
        print("📊 成果物分析システム")
        print("=" * 80)
        
        all_outputs = list(self.output_base.glob("*/"))
        
        print(f"\n📂 総成果物数: {len(all_outputs)}個")
        
        analysis = {
            'total_outputs': len(all_outputs),
            'high_quality': [],  # 7点以上
            'reusable_components': [],  # 再利用可能
            'patterns': [],  # パターン
            'best_practices': []  # ベストプラクティス
        }
        
        for output_dir in all_outputs:
            files = list(output_dir.glob("*.py"))
            
            if len(files) >= 2:  # 高品質の可能性
                analysis['high_quality'].append({
                    'path': str(output_dir),
                    'files': [f.name for f in files],
                    'lines': sum(len(f.read_text().split('\n')) for f in files)
                })
        
        print(f"  ✅ 高品質成果物: {len(analysis['high_quality'])}個")
        
        return analysis
    
    def extract_reusable_code(self, output_path: str) -> list:
        """再利用可能なコードを抽出"""
        output_dir = Path(output_path)
        reusable = []
        
        for py_file in output_dir.glob("*.py"):
            content = py_file.read_text()
            
            # クラス定義を抽出
            import re
            classes = re.findall(r'class (\w+).*?:', content)
            
            for class_name in classes:
                reusable.append({
                    'type': 'class',
                    'name': class_name,
                    'file': py_file.name,
                    'source': output_path
                })
        
        return reusable
    
    def create_reusable_library(self):
        """再利用可能ライブラリの作成"""
        print("\n" + "=" * 80)
        print("📚 再利用可能ライブラリの作成")
        print("=" * 80)
        
        library_dir = Path("agents/efficiency/reusable_library")
        library_dir.mkdir(exist_ok=True, parents=True)
        
        # 全成果物を分析
        analysis = self.analyze_all_outputs()
        
        # 高品質な成果物からコードを抽出
        all_classes = []
        all_functions = []
        
        for output in analysis['high_quality']:
            components = self.extract_reusable_code(output['path'])
            
            for comp in components:
                if comp['type'] == 'class':
                    all_classes.append(comp)
        
        print(f"\n📦 再利用可能コンポーネント:")
        print(f"  クラス: {len(all_classes)}個")
        
        # インデックスを作成
        index_content = f"""# 再利用可能ライブラリ

## 生成日時
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 統計
- 総成果物数: {analysis['total_outputs']}個
- 高品質成果物: {len(analysis['high_quality'])}個
- 再利用可能クラス: {len(all_classes)}個

## クラス一覧

"""
        
        for cls in all_classes:
            index_content += f"### {cls['name']}\n"
            index_content += f"- ファイル: {cls['file']}\n"
            index_content += f"- ソース: {cls['source']}\n\n"
        
        with open(library_dir / "INDEX.md", 'w') as f:
            f.write(index_content)
        
        print(f"\n✅ ライブラリインデックス作成完了")
        print(f"   {library_dir / 'INDEX.md'}")
        
        return str(library_dir)

