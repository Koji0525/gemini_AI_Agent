#!/usr/bin/env python3
"""
インターフェース契約テスト v1.0
全コンポーネントが契約を満たすか検証
"""
import sys
sys.path.insert(0, '/workspaces/gemini_AI_Agent')

from tools.interfaces import (
    SheetsManagerProtocol,
    verify_contract,
    get_missing_attributes
)


def test_sheets_manager_contract():
    """GoogleSheetsManagerの契約テスト"""
    print("\n🧪 GoogleSheetsManager契約テスト")
    print("-" * 50)
    
    try:
        from tools.sheets_manager import GoogleSheetsManager
        
        manager = GoogleSheetsManager()
        
        # 契約検証
        is_valid = verify_contract(manager, SheetsManagerProtocol)
        
        if is_valid:
            print("✅ 契約を満たしています")
        else:
            print("❌ 契約を満たしていません")
            missing = get_missing_attributes(manager, SheetsManagerProtocol)
            print(f"   欠落属性: {missing}")
            return False
        
        # 個別属性チェック
        required_attrs = {
            'spreadsheet_id': manager.spreadsheet_id,
            'authenticated': manager.authenticated,
            'client': manager.client,
            'sheet': manager.sheet
        }
        
        print("\n📊 属性状態:")
        for attr, value in required_attrs.items():
            print(f"  ✅ {attr}: {type(value).__name__} = {value}")
        
        # メソッドチェック
        print("\n🔧 メソッドチェック:")
        methods = ['read_sheet', 'get_sheet_data', 'write_sheet', 'authenticate']
        for method in methods:
            has_method = hasattr(manager, method) and callable(getattr(manager, method))
            symbol = "✅" if has_method else "❌"
            print(f"  {symbol} {method}()")
        
        return True
        
    except Exception as e:
        print(f"❌ テスト失敗: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_all_components():
    """全コンポーネントの契約テスト"""
    print("🧪 全コンポーネント契約テスト")
    print("=" * 50)
    
    tests = [
        ("GoogleSheetsManager", test_sheets_manager_contract),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"✅ {name}: PASSED")
            else:
                failed += 1
                print(f"❌ {name}: FAILED")
        except Exception as e:
            failed += 1
            print(f"❌ {name}: ERROR - {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 結果: {passed}件成功 / {failed}件失敗")
    
    if failed == 0:
        print("🎉 全テストパス！インターフェース契約準拠")
        return True
    else:
        print("⚠️  一部テスト失敗 - 修正が必要です")
        return False


if __name__ == "__main__":
    success = test_all_components()
    sys.exit(0 if success else 1)
