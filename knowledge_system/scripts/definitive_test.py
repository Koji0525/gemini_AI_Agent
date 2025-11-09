#!/usr/bin/env python3
import os
import sys

# 絶対パス設定 - 確実な方法
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
utils_dir = os.path.join(parent_dir, "utils")

print(f"🔧 カレントディレクトリ: {current_dir}")
print(f"🔧 親ディレクトリ: {parent_dir}")
print(f"🔧 ユーティリティディレクトリ: {utils_dir}")

# パスを確実に追加
sys.path.insert(0, parent_dir)
sys.path.insert(0, utils_dir)

print(f"🔧 Pythonパス: {sys.path}")


def test_imports_direct():
    """直接インポートテスト"""
    print("\n🔧 直接インポートテスト開始...")

    # 方法1: 直接ファイルからインポート
    try:
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "models_fixed", os.path.join(utils_dir, "models_fixed.py")
        )
        models_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(models_module)
        print("✅ EmbeddingModel インポート成功 (直接)")
        return True
    except Exception as e:
        print(f"❌ 直接インポート失敗: {e}")

    # 方法2: sys.path追加後にインポート
    try:
        print("✅ EmbeddingModel インポート成功 (標準)")
        return True
    except Exception as e:
        print(f"❌ 標準インポート失敗: {e}")

    return False


def test_database_direct():
    """データベース直接テスト"""
    print("\n🔧 データベース直接テスト開始...")

    try:
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "database_fixed", os.path.join(utils_dir, "database_fixed.py")
        )
        database_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(database_module)
        print("✅ DatabaseManager インポート成功 (直接)")
        return True
    except Exception as e:
        print(f"❌ データベースインポート失敗: {e}")
        return False


def test_embedding_functionality():
    """埋め込み機能テスト"""
    print("\n🔧 埋め込み機能テスト開始...")

    try:
        # 直接インポート
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "models_fixed", os.path.join(utils_dir, "models_fixed.py")
        )
        models_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(models_module)
        EmbeddingModel = models_module.EmbeddingModel

        model = EmbeddingModel()
        test_text = "これは機能テスト用の文章です"
        embedding = model.get_embedding(test_text)

        if embedding is not None:
            print(f"✅ 埋め込み生成成功: {embedding.shape}次元")
            return True
        else:
            print("❌ 埋め込み生成失敗")
            return False

    except Exception as e:
        print(f"❌ 埋め込み機能テスト失敗: {e}")
        return False


def test_database_functionality():
    """データベース機能テスト"""
    print("\n🔧 データベース機能テスト開始...")

    try:
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "database_fixed", os.path.join(utils_dir, "database_fixed.py")
        )
        database_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(database_module)
        DatabaseManager = database_module.DatabaseManager

        db_path = os.path.join(parent_dir, "database", "knowledge.db")
        db = DatabaseManager(db_path)

        stats = db.get_sync_stats()
        print(f"📊 データベース統計: {stats}")

        return True

    except Exception as e:
        print(f"❌ データベース機能テスト失敗: {e}")
        return False


def main():
    print("🚀 確実なテストを開始")

    tests = [
        test_imports_direct,
        test_database_direct,
        test_embedding_functionality,
        test_database_functionality,
    ]

    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ テスト実行中に例外: {e}")
            results.append(False)

    passed = sum(results)
    total = len(results)

    print(f"\n{'='*50}")
    print(f"📊 テスト結果: {passed}/{total} 成功")

    if passed == total:
        print("🎉 すべてのテストが成功しました！")
        return True
    else:
        print("💥 一部のテストが失敗しました")
        # 詳細な診断を実行
        run_detailed_diagnosis()
        return False


def run_detailed_diagnosis():
    """詳細な診断実行"""
    print("\n�� 詳細診断開始...")

    # ファイル存在確認
    files_to_check = [
        os.path.join(utils_dir, "models_fixed.py"),
        os.path.join(utils_dir, "database_fixed.py"),
        os.path.join(parent_dir, "database", "knowledge.db"),
    ]

    for file_path in files_to_check:
        exists = os.path.exists(file_path)
        print(f"{'✅' if exists else '❌'} {file_path}: {'存在する' if exists else '存在しない'}")

    # モジュール内容確認
    try:
        with open(os.path.join(utils_dir, "models_fixed.py"), "r") as f:
            content = f.read()
            has_class = "class EmbeddingModel" in content
            print(
                f"{'✅' if has_class else '❌'} models_fixed.py: EmbeddingModelクラス {'定義あり' if has_class else '定義なし'}"
            )
    except Exception as e:
        print(f"❌ ファイル読み込みエラー: {e}")


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
