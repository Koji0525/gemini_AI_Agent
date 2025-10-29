# 🏷️ バージョン管理ガイド

## セマンティックバージョニング

このプロジェクトは[Semantic Versioning 2.0.0](https://semver.org/)に従います。

### バージョン形式
```
vMAJOR.MINOR.PATCH[-LABEL]
```

### いつバージョンを上げるか

#### MAJOR (破壊的変更)
- APIの互換性がなくなる変更
- 設定ファイルの形式変更
- 使い方が大きく変わる変更

例:
```bash
# v1.0.0 → v2.0.0
- Google Sheetsの列構造を大幅変更
- 実行コマンドの引数が変更
```

#### MINOR (新機能追加)
- 後方互換性を保ったまま新機能追加
- 新しいエージェント追加
- 新しいオプション追加

例:
```bash
# v1.0.0 → v1.1.0
- 新しいWordPressエージェント追加
- 進捗レポート機能追加
```

#### PATCH (バグ修正)
- バグ修正のみ
- ドキュメント修正
- パフォーマンス改善

例:
```bash
# v1.0.0 → v1.0.1
- パスエラー修正
- タイポ修正
```

#### LABEL (開発段階)
- `alpha`: 開発中（不安定）
- `beta`: テスト中（ほぼ安定）
- `rc`: リリース候補
- `integrated`: 統合版（カスタムラベル）

### ブランチ戦略
```
main (または master)
  └── 本番リリース版のみ
  
develop
  └── 開発版（次のリリース候補）
  
feature/xxx
  └── 新機能開発
  
hotfix/xxx
  └── 緊急バグ修正
  
release/vX.Y.Z
  └── リリース準備
```

### タグの付け方
```bash
# アノテーテッドタグ（推奨）
git tag -a v1.0.0 -m "Initial release"

# 軽量タグ
git tag v1.0.0

# タグをプッシュ
git push origin v1.0.0

# すべてのタグをプッシュ
git push origin --tags
```

### リリースフロー例
```bash
# 1. 開発版から新機能ブランチ作成
git checkout develop
git checkout -b feature/new-agent

# 2. 開発・コミット
git add .
git commit -m "feat: 新しいエージェント追加"

# 3. developにマージ
git checkout develop
git merge feature/new-agent

# 4. リリースブランチ作成
git checkout -b release/v1.1.0

# 5. VERSION更新
echo "v1.1.0" > VERSION

# 6. CHANGELOG更新
# CHANGELOG.mdに変更内容記載

# 7. コミット
git add VERSION CHANGELOG.md
git commit -m "chore: bump version to v1.1.0"

# 8. mainにマージ
git checkout main
git merge release/v1.1.0

# 9. タグ作成
git tag -a v1.1.0 -m "新機能: XXXエージェント追加"

# 10. プッシュ
git push origin main --tags

# 11. developに反映
git checkout develop
git merge main
```

### コミットメッセージ規約
```
feat: 新機能
fix: バグ修正
docs: ドキュメント
style: フォーマット
refactor: リファクタリング
test: テスト
chore: その他

例:
feat: WordPressエージェント追加
fix: パスエラー修正
docs: README更新
```

