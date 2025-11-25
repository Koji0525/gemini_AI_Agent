# Phase 4インポートエラー修正ナレッジ

## 問題の概要

**発生日時**: {NOW}
**エラー内容**: `cannot import name 'DependencyResolverV2' from 'agents.integration.dependency_resolver_v2'`

## 根本原因

1. **クラス名の不一致**
   - コードが `DependencyResolverV2` をimportしようとしている
   - しかし、実際のファイルには該当クラスが存在しない

2. **可能性のある原因**
   - ファイルが削除または移動された
   - クラス名が変更された（V2 → V1など）
   - リファクタリング後の未完了状態

## 解決策

### 解決策1: 既存クラスにエイリアスを付ける（推奨）

```python
# 修正前
from agents.integration.dependency_resolver_v2 import DependencyResolverV2

# 修正後
from agents.integration.dependency_resolver import DependencyResolver as DependencyResolverV2
```

**メリット**:
- 既存コードの変更が最小限
- 既存の実装を活用
- テスト済みコードを再利用

### 解決策2: 互換性スタブを作成

```python
# agents/integration/dependency_resolver_v2.py (新規作成)
from agents.integration.dependency_resolver import DependencyResolver

class DependencyResolverV2(DependencyResolver):
    """後方互換性維持用ラッパー"""
    pass
```

**メリット**:
- 将来的に独自実装に置き換え可能
- 既存コードの変更不要

### 解決策3: 未使用importの削除

- epic_orchestrator.py内で実際にDependencyResolverV2が使われていない場合
- import文を削除するだけで解決

## 予防策

1. **import整理の自動化**
   ```bash
   # 未使用importを検出
   pylint --disable=all --enable=unused-import agents/
   
   # 自動整理
   autoflake --remove-all-unused-imports --in-place agents/*.py
   ```

2. **依存関係の文書化**
   - DEPENDENCIES.md を作成
   - 各モジュールの依存関係を明記

3. **リファクタリング時のチェックリスト**
   - [ ] すべてのimport文を更新
   - [ ] テストを実行
   - [ ] ナレッジベースに記録

## テストコマンド

```bash
# インポートテスト
python3 -c "from agents.epic_orchestrator import *"

# 統合テスト
pytest tests/ -k "epic" -v

# 完全テスト
pytest tests/ -v --tb=short
```

## 関連ドキュメント

- Phase 4実装ロードマップ
- 依存関係管理ガイド
- コーディング規約

## 教訓

### ✅ うまくいったこと
- 段階的診断アプローチ
- バックアップを取ってから修正
- 既存実装の再利用

### ⚠️ 改善点
- リファクタリング時のimport更新を自動化
- 依存関係の可視化ツール導入
- pre-commit hookでimportチェック

