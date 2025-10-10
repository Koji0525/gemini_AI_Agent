# Google Drive JSONアップローダー

python drive_uploader.py で実行！
Yで実行して
kojikjazu0525@gmail.com　を選択する



ローカルフォルダのJSONファイルをGoogle Driveにアップロードし、アップロード後にoldフォルダに移動するツールです。

**⚠️ 重要**: サービスアカウントにはストレージクォータがないため、**OAuth2認証**を使用します。

## 📋 機能

- ✅ temp_textsフォルダ内の全JSONファイルを自動検出
- ✅ Google Driveの指定フォルダにアップロード（OAuth2認証）
- ✅ アップロード成功後、自動的にoldフォルダに移動
- ✅ 詳細なログ出力（コンソール + ログファイル）
- ✅ スプレッドシート連携版も用意

## 🔧 事前準備（重要！）

### OAuth2認証のセットアップ

**必ず先に `OAuth2認証セットアップ手順.md` を参照して、OAuth2クライアントIDを作成してください。**

簡単な手順：
1. Google Cloud Consoleでプロジェクト作成
2. Google Drive APIを有効化
3. OAuth 2.0クライアントID（デスクトップアプリ）を作成
4. `credentials.json` をダウンロードして配置

詳細は **`OAuth2認証セットアップ手順.md`** を参照してください。

## 🚀 セットアップ

### 1. 必要なライブラリをインストール

```bash
pip install -r requirements_drive.txt
```

### 2. ファイル構成

以下のファイルを同じフォルダに配置してください：

```
gemini_auto_generate/
├── drive_manager.py              # Google Drive管理クラス（OAuth2版）
├── drive_uploader.py             # 単体実行版
├── drive_uploader_with_sheets.py # スプレッドシート連携版
├── sheets_manager.py             # 既存のGoogleSheetsManagerクラス
├── config_utils.py               # 既存の設定ユーティリティ
├── credentials.json              # ★ OAuth2クライアントシークレット（要作成）
├── token.pickle                  # 認証トークン（初回実行時に自動生成）
├── service_account.json          # サービスアカウント（スプレッドシート用）
├── requirements.txt              # 必要なライブラリ
└── temp_texts/                   # アップロード元フォルダ
    ├── *.json                    # アップロード対象
    └── old/                      # 移動先フォルダ（自動作成）
```

## 📖 使い方

### パターン1: 単体実行版（推奨：まずはこれで動作確認）

設定値が直接コードに書かれているシンプル版です。

```bash
python drive_uploader.py
```

**設定変更方法：**
`drive_uploader.py`の`main()`関数内の以下の部分を編集：

```python
SOURCE_FOLDER = r"C:\Users\color\Documents\gemini_auto_generate\temp_texts"
TARGET_FOLDER_ID = "16QVK_-z8JVmhLQuLVprOx9_DnoNc4eUc"
CREDENTIALS_FILE = r"C:\Users\color\Documents\gemini_auto_generate\credentials.json"
```

**初回実行時**：
- ブラウザが自動で開きます
- Googleアカウント（colorful-air-world@hotmail.co.jp）でログイン
- アプリへのアクセス許可を承認
- `token.pickle`が自動生成されます

**2回目以降**：
- `token.pickle`が存在するため、ブラウザ認証は不要

### パターン2: スプレッドシート連携版

スプレッドシートの`setting`シートから設定を読み込みます。

```bash
# デフォルト（PC_ID=1）
python drive_uploader_with_sheets.py

# PC_IDを指定
python drive_uploader_with_sheets.py --pc-id 2
```

**必要な設定：**
スプレッドシート（ID: `1jz-4t7PI71KDDdldyLNWIwUehrkADcdNiCGe94LU0b4`）の`setting`シートに以下を設定：

| 設定項目 | 値 |
|---------|-----|
| PC_ID | 1 |
| Download_Text_Folder | C:\Users\color\Documents\gemini_auto_generate\temp_texts |
| Service_Account | C:\Users\color\Documents\gemini_auto_generate\service_account.json |

## 🔧 動作フロー

1. **JSONファイル検出**
   - `temp_texts`フォルダ内の`*.json`ファイルを検出

2. **Google Drive認証**
   - サービスアカウントで認証

3. **アップロード**
   - 各JSONファイルを指定フォルダにアップロード

4. **ファイル移動**
   - アップロード成功後、`temp_texts/old/`に移動
   - 同名ファイルがある場合はタイムスタンプ付与

5. **レポート出力**
   - 成功/失敗の件数を表示
   - 詳細ログを`drive_upload.log`に保存

## 📝 ログ出力例

```
2025-01-15 10:30:15 - __main__ - INFO - ============================================================
2025-01-15 10:30:15 - __main__ - INFO - Google Drive JSONファイルアップロード開始
2025-01-15 10:30:15 - __main__ - INFO - ============================================================
2025-01-15 10:30:15 - __main__ - INFO - 📂 ソースフォルダ: C:\Users\color\Documents\gemini_auto_generate\temp_texts
2025-01-15 10:30:15 - drive_manager - INFO - Google Drive API認証中...
2025-01-15 10:30:16 - drive_manager - INFO - ✅ Google Drive API認証成功
2025-01-15 10:30:16 - __main__ - INFO - 📁 検出されたJSONファイル: 5件
2025-01-15 10:30:16 - drive_manager - INFO - 📤 アップロード中: response_001.json
2025-01-15 10:30:18 - drive_manager - INFO - ✅ アップロード成功: response_001.json (1,234 bytes) [ID: abc123...]
2025-01-15 10:30:18 - __main__ - INFO - 📦 移動完了: response_001.json -> old/response_001.json
```

## ⚙️ カスタマイズ

### アップロード先フォルダIDの変更

Google DriveのフォルダURLから取得：
```
https://drive.google.com/drive/folders/16QVK_-z8JVmhLQuLVprOx9_DnoNc4eUc
                                          ↑
                                    このIDを使用
```

### 同名ファイルの処理変更

`drive_manager.py`の`upload_file()`メソッドで、アップロード前に既存ファイルをチェック可能：

```python
if self.check_file_exists(file_path.name):
    logger.warning(f"同名ファイルが既に存在: {file_path.name}")
    # スキップまたは上書きの処理を追加
```

## 🔍 トラブルシューティング

### エラー: 認証ファイルが見つかりません

→ `service_account.json`のパスを確認してください

### エラー: フォルダにアクセスできません

→ サービスアカウントのメールアドレスに、Google Driveフォルダの編集権限を付与してください

### ファイルが移動されない

→ アップロードは成功しているが移動に失敗しています。ログで詳細を確認してください

## 📌 今後の拡張案

- [ ] 自動実行（スケジューラー連携）
- [ ] ファイル監視による自動アップロード
- [ ] アップロード結果のスプレッドシート記録
- [ ] 重複ファイルの自動検出とスキップ
- [ ] メール通知機能

## 📄 ライセンス

このプロジェクトは内部使用を目的としています。