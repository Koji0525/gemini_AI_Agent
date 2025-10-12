#!/usr/bin/env python3
"""
プロジェクト構造を分析して、何があるのかを整理するツール
"""
import os
from pathlib import Path
from collections import defaultdict
import json

class ProjectAnalyzer:
    """プロジェクトの構造を分析"""
    
    def __init__(self):
        self.root = Path(".")
        self.files_by_category = defaultdict(list)
        self.duplicate_files = []
        
    def analyze(self):
        """全ファイルを分析"""
        print("🔍 プロジェクト分析中...\n")
        
        # 1. ファイルをカテゴリ別に分類
        self.categorize_files()
        
        # 2. 重複や類似ファイルを検出
        self.find_duplicates()
        
        # 3. エージェントファイルを整理
        self.list_agents()
        
        # 4. 設定ファイルを整理
        self.list_configs()
        
        # 5. 実行可能なメインファイルをリスト
        self.list_main_scripts()
        
        # 6. レポート生成
        self.generate_report()
    
    def categorize_files(self):
        """ファイルをカテゴリ別に分類"""
        categories = {
            'agents': ['agent.py', 'agent_'],
            'executors': ['executor.py', '_executor'],
            'managers': ['manager.py', '_manager'],
            'configs': ['config.py', 'config_'],
            'tests': ['test_', '_test.py'],
            'wordpress': ['wp_', 'wordpress'],
            'fixes': ['fix_', '_fix.py'],
            'utils': ['utils.py', 'helper'],
            'main': ['main_', 'run_'],
        }
        
        for file in self.root.rglob("*.py"):
            if '__pycache__' in str(file):
                continue
                
            file_str = str(file)
            categorized = False
            
            for category, patterns in categories.items():
                if any(pattern in file.name for pattern in patterns):
                    self.files_by_category[category].append(file)
                    categorized = True
                    break
            
            if not categorized:
                self.files_by_category['other'].append(file)
    
    def find_duplicates(self):
        """重複や類似ファイルを検出"""
        # 名前が似ているファイルをグループ化
        name_groups = defaultdict(list)
        
        for category, files in self.files_by_category.items():
            for file in files:
                # ベース名から数字や日付を除去
                base_name = file.stem.replace('_old', '').replace('_new', '')
                base_name = ''.join(c for c in base_name if not c.isdigit())
                name_groups[base_name].append(file)
        
        # 複数あるものを重複候補として記録
        self.duplicate_files = [
            (name, files) for name, files in name_groups.items() 
            if len(files) > 1
        ]
    
    def list_agents(self):
        """エージェント一覧"""
        print("=" * 80)
        print("🤖 エージェント一覧")
        print("=" * 80)
        
        agents = sorted(self.files_by_category['agents'])
        for i, agent in enumerate(agents, 1):
            print(f"{i:2d}. {agent}")
        print(f"\n合計: {len(agents)} ファイル\n")
    
    def list_configs(self):
        """設定ファイル一覧"""
        print("=" * 80)
        print("⚙️ 設定ファイル一覧")
        print("=" * 80)
        
        configs = sorted(self.files_by_category['configs'])
        for i, config in enumerate(configs, 1):
            print(f"{i:2d}. {config}")
        print(f"\n合計: {len(configs)} ファイル\n")
    
    def list_main_scripts(self):
        """メイン実行スクリプト一覧"""
        print("=" * 80)
        print("🚀 実行可能なメインスクリプト")
        print("=" * 80)
        
        mains = sorted(self.files_by_category['main'])
        for i, main in enumerate(mains, 1):
            # ファイルの最初の数行からdocstringを取得
            try:
                with open(main, 'r', encoding='utf-8') as f:
                    lines = f.readlines()[:10]
                    docstring = ""
                    for line in lines:
                        if '"""' in line or "'''" in line:
                            docstring = line.strip().strip('"""').strip("'''")
                            break
                    
                    print(f"{i:2d}. {main}")
                    if docstring:
                        print(f"    📝 {docstring}")
            except:
                print(f"{i:2d}. {main}")
        
        print(f"\n合計: {len(mains)} ファイル\n")
    
    def generate_report(self):
        """レポート生成"""
        print("=" * 80)
        print("📊 プロジェクト統計")
        print("=" * 80)
        
        total_files = sum(len(files) for files in self.files_by_category.values())
        
        print(f"📁 総ファイル数: {total_files}")
        print("\nカテゴリ別:")
        for category, files in sorted(self.files_by_category.items()):
            print(f"  {category:15s}: {len(files):3d} ファイル")
        
        print("\n" + "=" * 80)
        print("⚠️ 重複・類似ファイルの可能性")
        print("=" * 80)
        
        if self.duplicate_files:
            for base_name, files in self.duplicate_files[:10]:  # 最初の10個
                print(f"\n📦 '{base_name}' 系統:")
                for file in sorted(files):
                    print(f"  - {file}")
        else:
            print("✅ 重複ファイルは検出されませんでした")
        
        # レポートをJSONで保存
        report = {
            'total_files': total_files,
            'categories': {cat: len(files) for cat, files in self.files_by_category.items()},
            'duplicates': [(name, [str(f) for f in files]) for name, files in self.duplicate_files]
        }
        
        with open('project_analysis.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print("\n💾 詳細レポートを project_analysis.json に保存しました")

if __name__ == "__main__":
    analyzer = ProjectAnalyzer()
    analyzer.analyze()
