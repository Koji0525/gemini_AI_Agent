#!/usr/bin/env python3
"""
🎯 Smart File Creator v1.0
新規ファイル作成時に自動でバージョンチェック＆命名

【使い方】
  # 対話式（推奨）
  touch_smart script.py
  
  # ワンライナー
  touch_smart task_executor.py "新機能追加"

【自動実行内容】
✅ 1. 既存ファイルの重複チェック
✅ 2. 最新バージョン番号を自動検出
✅ 3. 適切なバージョン番号を提案
✅ 4. ファイルを作成（テンプレート付き）
✅ 5. バージョン管理に自動登録
"""

import sys
import re
from pathlib import Path
from datetime import datetime

class SmartFileCreator:
    """スマートファイル作成ツール"""
    
    EXCLUDE_DIRS = {'_WIP', '_ARCHIVE', '_BACKUP', '__pycache__', '.git'}
    
    def __init__(self):
        self.project_root = Path.cwd()
    
    def create_file_interactive(self, filename: str = None, reason: str = None):
        """対話式ファイル作成"""
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("🎯 Smart File Creator - 対話式モード")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        
        # ファイル名入力
        if not filename:
            filename = input("\n📝 ファイル名を入力（例: task_executor.py）: ").strip()
        
        if not filename:
            print("❌ ファイル名が必要です")
            return False
        
        # 拡張子チェック
        if not filename.endswith('.py'):
            filename += '.py'
        
        # ベース名を取得
        base_name = self._get_base_name(filename)
        
        print(f"\n🔍 既存ファイルチェック中...")
        
        # 既存ファイルを検索
        existing_files = self._find_existing_files(base_name)
        
        if not existing_files:
            print(f"✅ '{base_name}' の既存ファイルなし")
            suggested_name = filename
            next_version = 1
        else:
            print(f"⚠️  '{base_name}' の既存ファイル発見: {len(existing_files)}件")
            
            # 既存ファイルを表示
            for f in existing_files[:5]:
                rel_path = f.relative_to(self.project_root)
                version = self._extract_version(f.name)
                v_str = f"v{version:02d}" if version else "本番版"
                print(f"   - {rel_path} ({v_str})")
            
            if len(existing_files) > 5:
                print(f"   ... 他 {len(existing_files) - 5} 件")
            
            # 最新バージョンを検出
            max_version = max(
                (self._extract_version(f.name) for f in existing_files 
                 if self._extract_version(f.name) is not None),
                default=0
            )
            
            next_version = max_version + 1
            
            print(f"\n💡 最新バージョン: v{max_version:02d}")
            print(f"💡 推奨: v{next_version:02d}")
        
        # 機能名入力
        if not reason:
            reason = input(f"\n📋 機能名を入力（例: feature, bugfix, refactor）: ").strip()
        
        if not reason:
            reason = "update"
        
        # ファイル名を生成
        suggested_name = f"{base_name}_v{next_version:02d}_{reason}.py"
        
        print(f"\n📂 作成するファイル: {suggested_name}")
        
        # 確認
        confirm = input("この名前で作成しますか？ (Y/n): ").strip().lower()
        
        if confirm and confirm != 'y':
            custom_name = input("カスタムファイル名を入力: ").strip()
            if custom_name:
                suggested_name = custom_name if custom_name.endswith('.py') else f"{custom_name}.py"
        
        # ファイル作成
        return self._create_file_with_template(suggested_name, reason)
    
    def _find_existing_files(self, base_name: str) -> list:
        """既存ファイルを検索"""
        existing = []
        
        for py_file in self.project_root.rglob('*.py'):
            # 除外ディレクトリをスキップ
            if any(excluded in py_file.parts for excluded in self.EXCLUDE_DIRS):
                continue
            
            if py_file.name == '__init__.py':
                continue
            
            # ベース名が一致するファイルを収集
            file_base = self._get_base_name(py_file.name)
            if file_base == base_name:
                existing.append(py_file)
        
        return sorted(existing)
    
    def _create_file_with_template(self, filename: str, reason: str) -> bool:
        """テンプレート付きでファイル作成"""
        filepath = self.project_root / filename
        
        if filepath.exists():
            print(f"❌ ファイルが既に存在します: {filename}")
            return False
        
        # テンプレート生成
        template = self._generate_template(filename, reason)
        
        # ファイル書き込み
        filepath.write_text(template, encoding='utf-8')
        filepath.chmod(0o755)
        
        print(f"\n✅ ファイル作成完了: {filename}")
        print(f"📂 パス: {filepath}")
        
        # エディタで開くか確認
        open_editor = input("\nVS Codeで開きますか？ (Y/n): ").strip().lower()
        
        if not open_editor or open_editor == 'y':
            import subprocess
            try:
                subprocess.run(['code', str(filepath)], check=False)
                print("📝 VS Codeで開きました")
            except:
                print("⚠️ VS Codeを開けませんでした")
        
        return True
    
    def _generate_template(self, filename: str, reason: str) -> str:
        """Pythonファイルテンプレート生成"""
        base_name = self._get_base_name(filename)
        version = self._extract_version(filename)
        version_str = f"v{version}.0" if version else "v1.0"
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
        
        return f'''#!/usr/bin/env python3
"""
{base_name.replace('_', ' ').title()} {version_str}

【{version_str} 変更の理由】
何が起きた:
- {reason}

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
project_root = Path(__file__).parent.parent
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
        description='🎯 Smart File Creator - 自動バージョンチェック付きファイル作成',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  # 対話式（推奨）
  python3 tools/smart_file_creator.py
  
  # ファイル名指定
  python3 tools/smart_file_creator.py task_executor.py
  
  # ファイル名＋理由指定
  python3 tools/smart_file_creator.py task_executor.py "新機能追加"

エイリアス設定後:
  touch_smart
  touch_smart script.py
  touch_smart script.py "機能追加"
        """
    )
    
    parser.add_argument('filename', nargs='?', help='ファイル名')
    parser.add_argument('reason', nargs='?', help='機能名/理由')
    
    args = parser.parse_args()
    
    creator = SmartFileCreator()
    creator.create_file_interactive(args.filename, args.reason)


if __name__ == "__main__":
    main()
