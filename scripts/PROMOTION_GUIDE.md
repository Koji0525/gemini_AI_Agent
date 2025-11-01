# WIP → 本番への昇格ガイド

## 基本的な流れ

1. **WIPで開発＆テスト**
```bash
   DISPLAY=:1 python3 _WIP/pm_agent_automation.py
```

2. **昇格スクリプト実行**
```bash
   bash scripts/promote_to_production.sh
```

3. **本番環境でテスト**
```bash
   DISPLAY=:1 python3 agents/pm_agent/automation.py
```

4. **コミット**
```bash
   git add agents/pm_agent/
   git commit -m "✨ PM Agent機能追加: activeなゴール自動処理"
   git push
```

## 昇格スクリプトの機能

- ✅ 構文チェック自動実行
- ✅ 既存ファイルの自動バックアップ
- ✅ ワンコマンドで複数ファイル昇格
- ✅ 確認プロンプト付き（誤操作防止）

## WIPファイルの扱い

- ✅ 昇格後もWIPファイルは削除しない
- ✅ 次回の開発はWIPから継続
- ✅ 定期的にWIPと本番を同期

## トラブルシューティング

### 昇格後に問題が発生した場合
```bash
# バックアップから復元
cp _BACKUP/promotion_YYYYMMDD_HHMMSS/*.py agents/pm_agent/
```

### WIPと本番がずれてしまった場合
```bash
# 本番 → WIPへコピー
cp agents/pm_agent/*.py _WIP/
```
