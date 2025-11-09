#!/usr/bin/env python3
"""
テスト環境セットアップツール - 改良版
"""
import os
import sys
from pathlib import Path

def setup_test_environment():
    """テスト環境をセットアップ - エラーハンドリング強化"""
    
    print("🔧 テスト環境セットアップ開始...")
    
    # プロジェクトルートをパスに追加
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))
    
    # テスト用環境変数を設定（既存の値を上書きしない）
    test_env_vars = {
        'GEMINI_API_KEY': 'test-api-key-for-testing',
        'SPREADSHEET_ID': 'test-spreadsheet-id',
        'WP_URL': 'https://test.example.com',
        'WP_USER': 'testuser',
        'WP_PASS': 'testpass',
        'PYTHONPATH': str(project_root)
    }
    
    for key, value in test_env_vars.items():
        if key not in os.environ:  # 既に設定されている場合は上書きしない
            os.environ[key] = value
            print(f"✅ 環境変数設定: {key}=***")
        else:
            print(f"ℹ️  環境変数既存: {key}=***")
    
    # .envファイルが存在する場合は読み込み（上書きしない）
    env_file = project_root / '.env'
    if env_file.exists():
        print(f"✅ .envファイルを発見: {env_file}")
        try:
            from dotenv import load_dotenv
            # override=Falseで既存の環境変数を上書きしない
            load_dotenv(env_file, override=False)
            print("✅ .envファイルを読み込み完了（既存設定を保持）")
        except ImportError:
            print("⚠️  dotenvパッケージがありません")
        except Exception as e:
            print(f"⚠️  .env読み込みエラー: {e}")
    else:
        print("ℹ️  .envファイルは存在しません")
    
    # 環境変数の検証
    required_vars = ['GEMINI_API_KEY', 'SPREADSHEET_ID']
    missing_vars = [var for var in required_vars if var not in os.environ]
    
    if missing_vars:
        print(f"❌ 必須環境変数が不足: {missing_vars}")
        # テスト用のダミー値を設定
        for var in missing_vars:
            os.environ[var] = f"test-dummy-{var}"
            print(f"⚠️  ダミー値を設定: {var}=***")
    else:
        print("✅ 必須環境変数がすべて設定されています")
    
    print("🎉 テスト環境セットアップ完了")

if __name__ == "__main__":
    setup_test_environment()
