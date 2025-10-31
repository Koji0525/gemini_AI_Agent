# M&Aポータル実装チェックリスト

## ✅ Task 1: functions.php コード追加

### 準備
- [ ] WordPress管理画面にログイン
- [ ] 外観 → テーマファイルエディター
- [ ] functions.php のバックアップ作成

### 実装
- [ ] `PASTE_TO_WORDPRESS.txt` の内容を全てコピー
- [ ] functions.php の最後に貼り付け
- [ ] 「ファイルを更新」をクリック

### 確認
- [ ] エラーが表示されない
- [ ] 管理画面に「M&A企業情報」メニューが表示
- [ ] M&A企業情報 → 新規追加 が開ける
- [ ] 右側に「業種」パネルが表示
- [ ] 6個の業種（IT、製造業、等）が自動作成されている

---

## ✅ Task 2: ACFフィールド設定

### 前提
- [ ] Advanced Custom Fields プラグインがインストール済み

### 設定
- [ ] ACF → フィールドグループ → 新規追加
- [ ] フィールドグループ名: 企業詳細情報
- [ ] 以下のフィールドを追加:
  - [ ] 所在地 (location) - テキスト - 必須
  - [ ] 資本金 (capital) - 数値 - 必須
  - [ ] 従業員数 (employees) - 数値 - 必須
  - [ ] 年商 (revenue) - 数値 - 必須
  - [ ] 希望条件 (deal_type) - 選択 - 必須
- [ ] 表示ルール: 投稿タイプ = ma_company
- [ ] 公開

### 確認
- [ ] M&A企業情報の編集画面に5つのフィールドが表示

---

## ✅ Task 3: デモデータ投入

- [ ] テックカンパニーA 入力
- [ ] 製造業B 入力
- [ ] サービスC 入力
- [ ] 小売店D 入力
- [ ] 建設E 入力

データ: `scripts/ma_demo_data.json` または `MD/251031_task3_demo_data.md`

### 確認
- [ ] M&A企業情報一覧に5社表示
- [ ] 業種カラムに各業種が表示
- [ ] 所在地・資本金・希望条件が表示
- [ ] 希望条件が色分け表示（売却=赤、買収=緑）

---

## ✅ 完了

全て完了したら:
```bash
python3 scripts/update_task_status.py MA_PORTAL_1 completed
python3 scripts/update_task_status.py MA_PORTAL_2 completed
python3 scripts/update_task_status.py MA_PORTAL_3 completed
```

---

## 🎯 次のステップ

Task 4: 検索ページ作成
→ MD/251031_ma_portal_implementation_plan.md 参照
