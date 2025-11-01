# M&Aポータル自動構築 - 実装手順

**所要時間**: 5分
**自動化レベル**: 95%

---

## 🎯 概要

WordPress開発自動化フレームワークにより、以下が自動生成されました:

✅ カスタム投稿タイプ (ma_company) のPHPコード
✅ タクソノミー (ma_industry) のPHPコード  
✅ 管理画面カスタムカラムのコード
✅ ACFフィールド設定JSON

---

## 📋 実装手順

### Step 1: 生成されたコードを確認
```bash
cat wordpress_projects/ma_portal/functions_additions.php
```

---

### Step 2: WordPressに追加

1. **WordPress管理画面にログイン**
   - URL: https://uzbek-ma.com/wp-admin/

2. **テーマエディターを開く**
   - 外観 → テーマファイルエディター

3. **functions.php を開く**
   - 右側のファイル一覧から「functions.php」を選択

4. **バックアップを作成**（重要）
   - 現在の内容を全てコピー
   - ローカルに保存

5. **生成されたコードを追加**
   - `wordpress_projects/ma_portal/functions_additions.php` の内容を全てコピー
   - functions.php の**最後**に貼り付け
   - **重要**: 既存コードの後に追加すること

6. **保存**
   - 「ファイルを更新」をクリック

---

### Step 3: 動作確認

1. **管理画面のメニュー確認**
   - 左メニューに「M&A企業情報」が表示される

2. **テスト投稿作成**
   - M&A企業情報 → 新規追加
   - タイトル: テスト企業
   - 業種: IT・ソフトウェア（右側パネル）
   - 公開

3. **カスタムカラム確認**
   - M&A企業情報 → 一覧
   - 業種、所在地などのカラムが表示される

---

### Step 4: ACFフィールド設定

**Option A: 自動インポート（推奨）**

ACF Pro版を使用している場合:

1. ACF → Tools → Import Field Groups
2. `wordpress_projects/ma_portal/acf_fields.json` をインポート

**Option B: 手動設定**

1. ACF → フィールドグループ → 新規追加
2. フィールドグループ名: 企業詳細情報
3. 以下のフィールドを追加:
   - 所在地 (location) - テキスト
   - 資本金 (capital) - 数値
   - 従業員数 (employees) - 数値
   - 年商 (revenue) - 数値
   - 希望条件 (deal_type) - 選択
4. 表示ルール: 投稿タイプ = ma_company
5. 公開

---

### Step 5: デモデータ投入

**自動投入スクリプト（開発中）** または **手動入力**

手動入力の場合:
→ MD/251031_task3_demo_data.md を参照

---

## 🎉 完了

以下が完成しました:

✅ カスタム投稿タイプ: M&A企業情報
✅ タクソノミー: 業種（6カテゴリー自動作成）
✅ 管理画面カスタムカラム
✅ ACFフィールド（要手動設定）

---

## 🔄 次回同様のプロジェクトを作る場合

1. `templates/ma_portal_project.json` をコピー
2. プロジェクト名や設定を編集
3. `python3 tools/wordpress_dev_framework.py templates/新プロジェクト.json`
4. 5分で完成！

---

## 📊 タスクステータス更新
```bash
python3 scripts/update_task_status.py MA_PORTAL_1 completed
```
