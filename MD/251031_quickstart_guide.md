# M&Aポータル クイックスタートガイド

## ⚡ 3分で完成（推奨手順）

### 前提条件
- WordPressサイト稼働中
- 管理者権限でログイン可能
- 既存のfunctions.phpのバックアップ

---

## 🚀 実装ステップ

### Step 1: 環境チェック（30秒）
```bash
python3 tools/wordpress_readiness_checker.py
```

**確認項目**:
- ✅ WordPress接続: OK
- ⚠️ カスタム投稿タイプ: 未登録（これから追加）

---

### Step 2: functions.php コード追加（2分）

#### 2-1. コードをコピー
```bash
cat wordpress_projects/ma_portal/PASTE_TO_WORDPRESS.txt
```

全て選択してコピー（約70行）

#### 2-2. WordPress管理画面を開く

https://uzbek-ma.com/wp-admin/theme-editor.php

#### 2-3. コードを追加

1. 右側のファイル一覧から「functions.php」を選択
2. **最下行までスクロール**（重要）
3. 既存コードの後に貼り付け
4. 「ファイルを更新」をクリック

#### 2-4. 動作確認

- エラーが表示されない → ✅
- 左メニューに「M&A企業情報」が表示 → ✅
- M&A企業情報 → 新規追加 が開ける → ✅

---

### Step 3: ACFフィールド設定（2分）

#### 手順表示
```bash
python3 tools/acf_auto_setup.py wordpress_projects/ma_portal/acf_fields.json
```

#### 設定内容（コピペ）

**ACF → フィールドグループ → 新規追加**

**フィールドグループ名**: 企業詳細情報

**フィールド追加（5個）**:

1. **所在地**
   - 名前: location
   - タイプ: テキスト
   - 必須: はい

2. **資本金（万円）**
   - 名前: capital
   - タイプ: 数値
   - 必須: はい
   - 最小値: 0

3. **従業員数**
   - 名前: employees
   - タイプ: 数値
   - 必須: はい

4. **年商（万円）**
   - 名前: revenue
   - タイプ: 数値
   - 必須: はい

5. **希望条件**
   - 名前: deal_type
   - タイプ: 選択
   - 選択肢:
     - 売却希望 : 売却希望
     - 買収希望 : 買収希望
   - 必須: はい

**表示ルール**:
- 投稿タイプ = ma_company

**公開** をクリック

---

### Step 4: デモデータ投入（自動・30秒）
```bash
python3 tools/demo_data_importer.py scripts/ma_demo_data.json
```

**投入内容**:
- テックカンパニーA（IT・売却希望）
- 製造業B（製造業・売却希望）
- サービスC（サービス業・買収希望）
- 小売店D（小売業・売却希望）
- 建設E（建設業・買収希望）

---

## ✅ 完了確認

### 管理画面で確認

1. **M&A企業情報 → 一覧**
   - 5社のデータが表示される
   - 業種・所在地・資本金・希望条件のカラムが表示
   - 希望条件が色分け表示（売却=赤、買収=緑）

2. **業種カテゴリー**
   - M&A企業情報 → 業種
   - 6つのカテゴリーが自動作成されている

3. **新規投稿テスト**
   - M&A企業情報 → 新規追加
   - 5つのカスタムフィールドが表示される
   - 業種が選択できる

---

## 🎯 タスク完了報告
```bash
# Task 1-3 完了
python3 scripts/update_task_status.py MA_PORTAL_1 completed
python3 scripts/update_task_status.py MA_PORTAL_2 completed
python3 scripts/update_task_status.py MA_PORTAL_3 completed

# 進捗確認
python3 scripts/check_ma_portal_progress.py
```

---

## 🔄 次のステップ

### Task 4: 検索ページ作成
→ MD/251031_ma_portal_implementation_plan.md 参照

### Task 5: 動作確認
→ チェックリストに従って確認

---

## ⚠️ トラブルシューティング

### エラー: "Cannot redeclare function"

**原因**: 関数名の重複

**対処**:
1. バックアップから復元
2. 既存のfunctions.phpに同名の関数がないか確認
3. 追加したコードを削除して再度追加

### M&A企業情報メニューが表示されない

**原因**: コードが正しく保存されていない

**対処**:
1. functions.phpを再度開く
2. 追加したコードが存在するか確認
3. 「ファイルを更新」を再度クリック
4. WordPressのキャッシュをクリア

### デモデータ投入失敗

**原因**: カスタム投稿タイプ未登録

**対処**:
1. 環境チェック実行: `python3 tools/wordpress_readiness_checker.py`
2. functions.phpが正しく保存されているか確認
3. パーマリンク再設定: 設定 → パーマリンク設定 → 保存

---

## 📊 所要時間実績

| タスク | 予定 | 実績 |
|--------|------|------|
| 環境チェック | 30秒 | 30秒 |
| functions.php追加 | 2分 | 2分 |
| ACF設定 | 2分 | 3-5分 |
| デモデータ投入 | 30秒 | 30秒 |
| **合計** | **5分** | **6-8分** |

手動実装の場合: 60分 → **92%削減**
