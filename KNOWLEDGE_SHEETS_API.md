# Google Sheets API 使用ガイド

## 正しいメソッド

### ✅ 推奨メソッド
```python
# 行追加（複数行）
sheets.append_rows('sheet_name', [[data1, data2], [data3, data4]])

# 範囲更新
sheets.update_range('sheet_name!A1:Z10', [[data]])

# 範囲読み取り
data = sheets.read_range('sheet_name!A1:Z100')

❌ 非推奨・削除済みメソッド
# これらは使用禁止
sheets.append_row(...)    # ❌ 削除済み
sheets.write_data(...)    # ❌ 削除済み
sheets.write_rows(...)    # ❌ 存在しない

自動修正ツールの使用

# 互換性問題の自動修正
python3 tools/api_compatibility_checker.py --auto-fix

# 手動修正が必要な場合の確認
python3 tools/api_compatibility_checker.py --report

SafeSheetsWrapperの使用


```bash
# ポストモーテムドキュメントを作成
cat > POST_MORTEM_write_data_error.md << 'EOF'
# ポストモーテム: write_data/append_row エラー

## 問題概要
- **発生日**: 2024年11月
- **影響**: 30ファイルでAPI互換性エラー
- **根本原因**: GoogleSheetsManagerのメソッド名変更

## 影響を受けたメソッド
1. `append_row` → `append_rows` (複数形)
2. `write_data` → `update_range` または `append_rows`

## 修正方針
1. 自動修正ツールの使用
2. SafeSheetsWrapperの強制使用
3. 回帰テストの実施

## 再発防止策
- 新しいコードでは必ずSafeSheetsWrapperを使用
- API変更時の自動検出ツール導入
- 定期的な互換性チェックの実施
