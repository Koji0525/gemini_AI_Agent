#!/bin/bash

echo "============================================================"
echo "🚀 Day 1: ConfigLoader修正 & WP自動ログイン"
echo "============================================================"
echo ""

# Task 1.1: ConfigLoaderの確認
echo "【Task 1.1】ConfigLoader確認"
echo "----------------------------"
python3 << 'PYEOF'
import sys
import os
sys.path.insert(0, '.')

try:
    from configuration.config_loader import ConfigLoader
    
    config = ConfigLoader()
    print("✅ ConfigLoader読み込み成功")
    
    # 利用可能なメソッド確認
    methods = [m for m in dir(config) if not m.startswith('_')]
    print(f"\n📋 利用可能なメソッド:")
    for method in methods:
        print(f"   - {method}")
    
    # 実際に.envから値を取得してみる
    print("\n🔍 設定値の取得テスト:")
    
    # 直接属性でアクセスしてみる
    if hasattr(config, 'WP_URL'):
        print(f"   ✅ WP_URL: {config.WP_URL}")
    
    if hasattr(config, 'WP_USER'):
        print(f"   ✅ WP_USER: {config.WP_USER}")
    
    # get()メソッドの確認
    if hasattr(config, 'get'):
        try:
            wp_url = config.get('WP_URL')
            print(f"   ✅ config.get('WP_URL'): {wp_url}")
        except Exception as e:
            print(f"   ❌ config.get()エラー: {e}")
            print("   💡 修正が必要です")
    else:
        print("   ⚠️  get()メソッドが存在しません")
        print("   💡 get()メソッドを追加する必要があります")
    
except Exception as e:
    print(f"❌ エラー: {e}")
    import traceback
    traceback.print_exc()

PYEOF

echo ""
echo "============================================================"
echo "次のステップ:"
echo "  1. ConfigLoader.get()メソッドの追加（必要な場合）"
echo "  2. WP自動ログインモジュールの作成"
echo "============================================================"
