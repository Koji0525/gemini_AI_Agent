#!/usr/bin/env python3
"""
🎯 Smart File Creator v1.1

【v1.1 変更の理由】
何が起きた:
- 日本語の機能名がファイル名に入る
- ファイルがプロジェクトルートに作成される

原因:
- 機能名をそのままファイル名に使用
- 配置ディレクトリを指定していない

狙い:
- 英数字のみのファイル名生成
- 適切なディレクトリに配置
- ファイル名の可読性向上

【使い方】
  touch_smart                          # 対話式
  touch_smart task_executor.py         # ファイル名指定
  touch_smart scripts/agent.py feature # ディレクトリ＋機能指定
"""

import sys
import re
import unicodedata
from pathlib import Path
from datetime import datetime

class SmartFileCreator:
    """スマートファイル作成ツール v1.1"""
    
    EXCLUDE_DIRS = {'_WIP', '_ARCHIVE', '_BACKUP', '__pycache__', '.git'}
    
    # ディレクトリ別のデフォルト配置
    DEFAULT_LOCATIONS = {
        'agent': 'core_agents',
        'script': 'scripts',
        'tool': 'tools',
        'test': 'tests',
        'module': 'automation/modules',
    }
    
    def __init__(self):
        self.project_root = Path.cwd()
    
    def create_file_interactive(self, filename: str = None, reason: str = None):
        """対話式ファイル作成"""
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("🎯 Smart File Creator v1.1")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        
        # ファイル名入力
        if not filename:
            print("\n📝 ファイル名を入力:")
            print("   例1: task_executor.py")
            print("   例2: scripts/agent.py")
            print("   例3: core_agents/pm_agent.py")
            filename = input("\n→ ").strip()
        
        if not filename:
            print("❌ ファイル名が必要です")
            return False
        
        # パスを分解
        filepath = Path(filename)
        
        # ディレクトリ指定がない場合、自動判定
        if len(filepath.parts) == 1:
            base_name = filepath.stem
            suggested_dir = self._suggest_directory(base_name)
            
            if suggested_dir:
                print(f"\n💡 推奨配置: {suggested_dir}/")
                use_suggested = input(f"この場所に作成しますか？ (Y/n): ").strip().lower()
                
                if not use_suggested or use_suggested == 'y':
                    filepath = Path(suggested_dir) / filepath.name
        
        # 拡張子チェック
        if not filepath.suffix:
            filepath = filepath.with_suffix('.py')
        
        # ベース名を取得
        base_name = self._get_base_name(filepath.name)
        
        print(f"\n🔍 既存ファイルチェック中...")
        
        # 既存ファイルを検索
        existing_files = self._find_existing_files(base_name)
        
        if not existing_files:
            print(f"✅ '{base_name}' の既存ファイルなし")
            next_version = 1
        else:
            print(f"⚠️  '{base_name}' の既存ファイル発見: {len(existing_files)}件")
            
            for f in existing_files[:5]:
                rel_path = f.relative_to(self.project_root)
                version = self._extract_version(f.name)
                v_str = f"v{version:02d}" if version else "本番版"
                print(f"   - {rel_path} ({v_str})")
            
            if len(existing_files) > 5:
                print(f"   ... 他 {len(existing_files) - 5} 件")
            
            max_version = max(
                (self._extract_version(f.name) for f in existing_files 
                 if self._extract_version(f.name) is not None),
                default=0
            )
            
            next_version = max_version + 1
            print(f"\n💡 最新バージョン: v{max_version:02d}")
            print(f"�� 次のバージョン: v{next_version:02d}")
        
        # 機能名入力
        if not reason:
            print("\n📋 機能名を入力（英数字推奨）:")
            print("   例: feature, bugfix, refactor, optimization")
            reason = input("\n→ ").strip()
        
        if not reason:
            reason = "update"
        
        # 機能名を英数字に変換
        safe_reason = self._sanitize_filename(reason)
        
        # 新しいファイル名を生成
        new_filename = f"{base_name}_v{next_version:02d}_{safe_reason}.py"
        new_filepath = filepath.parent / new_filename
        
        print(f"\n📂 作成するファイル:")
        print(f"   {new_filepath}")
        
        # 確認
        confirm = input("\nこの名前で作成しますか？ (Y/n): ").strip().lower()
        
        if confirm and confirm != 'y':
            custom_name = input("カスタムファイル名を入力: ").strip()
            if custom_name:
                new_filepath = filepath.parent / (custom_name if custom_name.endswith('.py') else f"{custom_name}.py")
        
        # ファイル作成
        return self._create_file_with_template(new_filepath, safe_reason, next_version)
    
    def _suggest_directory(self, base_name: str) -> str:
        """ファイル名から推奨ディレクトリを提案"""
        base_lower = base_name.lower()
        
        if 'agent' in base_lower:
            return 'core_agents'
        elif 'test' in base_lower:
            return 'tests'
        elif 'tool' in base_lower or 'util' in base_lower:
            return 'tools'
        elif 'wp_' in base_lower or 'wordpress' in base_lower:
            return 'automation/modules'
        else:
            return 'scripts'
    
    def _sanitize_filename(self, text: str) -> str:
        """ファイル名に使える安全な文字列に変換"""
        # 日本語をローマ字に変換（簡易版）
        translation_table = {
            '新機能': 'feature',
            '機能追加': 'feature',
            'バグ修正': 'bugfix',
            '修正': 'fix',
            '最適化': 'optimize',
            'リファクタ': 'refactor',
            '改善': 'improve',
            '更新': 'update',
        }
        
        for jp, en in translation_table.items():
            if jp in text:
                return en
        
        # 英数字とアンダースコアのみ残す
        safe = re.sub(r'[^a-zA-Z0-9_]', '', text)
        
        # 空の場合はデフォルト
        return safe if safe else 'update'
    
    def _find_existing_files(self, base_name: str) -> list:
        """既存ファイルを検索"""
        existing = []
        
        for py_file in self.project_root.rglob('*.py'):
            if any(excluded in py_file.parts for excluded in self.EXCLUDE_DIRS):
                continue
            
            if py_file.name == '__init__.py':
                continue
            
            file_base = self._get_base_name(py_file.name)
            if file_base == base_name:
                existing.append(py_file)
        
        return sorted(existing)
    
    def _create_file_with_template(self, filepath: Path, reason: str, version: int) -> bool:
        """テンプレート付きでファイル作成"""
        if filepath.exists():
            print(f"❌ ファイルが既に存在します: {filepath}")
            return False
        
        # ディレクトリ作成
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        # テンプレート生成
        template = self._generate_template(filepath.name, reason, version)
        
        # ファイル書き込み
        filepath.write_text(template, encoding='utf-8')
        filepath.chmod(0o755)
        
        rel_path = filepath.relative_to(self.project_root)
        print(f"\n✅ ファイル作成完了: {rel_path}")
        
        # エディタで開く
        open_editor = input("\nVS Codeで開きますか？ (Y/n): ").strip().lower()
        
        if not open_editor or open_editor == 'y':
            import subprocess
            try:
                subprocess.run(['code', str(filepath)], check=False)
                print("📝 VS Codeで開きました")
            except:
                print("⚠️ VS Codeを開けませんでした")
        
        return True
    
    def _generate_template(self, filename: str, reason: str, version: int) -> str:
        """Pythonファイルテンプレート生成"""
        base_name = self._get_base_name(filename)
        version_str = f"v{version}.0"
        
        return f'''#!/usr/bin/env python3
"""
{base_name.replace('_', ' ').title()} {version_str}

【{version_str} 変更の理由】
何が起きた:
- {reason} 機能の追加

原因:
- （原因を記載）

狙い:
- （目的を記載）

【使用例】
    python3 {filename}
"""

import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).resolve()
while not (project_root / '.git').exists() and project_root != project_root.parent:
    project_root = project_root.parent
sys.path.insert(0, str(project_root))


def main():
    """メイン処理"""
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"🚀 {base_name.replace('_', ' ').title()} {version_str}")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    # TODO: 実装
    pass


if __name__ == "__main__":
    main()
'''
    
    def _get_base_name(self, filename: str) -> str:
        """バージョン番号を除いたベース名を取得"""
        base = re.sub(r'_v\d+.*\.py$', '', filename)
        base = re.sub(r'\.py$', '', base)
        return base
    
    def _extract_version(self, filename: str) -> int:
        """ファイル名からバージョン番号を抽出"""
        match = re.search(r'_v(\d+)', filename)
        return int(match.group(1)) if match else None


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='🎯 Smart File Creator v1.1',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  # 対話式（推奨）
  touch_smart
  
  # ファイル名指定
  touch_smart task_executor.py
  
  # ディレクトリ＋ファイル名
  touch_smart scripts/agent.py
  
  # ファイル名＋機能名
  touch_smart task_executor.py feature
  
  # フルパス＋機能名
  touch_smart core_agents/pm_agent.py refactor
        """
    )
    
    parser.add_argument('filename', nargs='?', help='ファイル名（ディレクトリ指定可）')
    parser.add_argument('reason', nargs='?', help='機能名/理由（日本語可）')
    
    args = parser.parse_args()
    
    creator = SmartFileCreator()
    creator.create_file_interactive(args.filename, args.reason)


if __name__ == "__main__":
    main()
