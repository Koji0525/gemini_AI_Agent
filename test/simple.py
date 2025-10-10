@echo off
rem =======================================================
rem Gemini自動化 手動セットアップバッチファイル
rem 管理者権限で実行することを推奨します
rem =======================================================

cd /d "C:\Users\color\Documents\gemini_auto_image"

echo ========================================
echo  Gemini自動化 手動セットアップ
echo ========================================
echo.

rem 管理者権限チェック
net session >nul 2>&1
if %errorlevel% == 0 (
    echo [管理者権限] 有効
) else (
    echo [管理者権限] 無効
    echo 推奨: 管理者権限で実行してください
    echo.
)

rem Python確認
echo [Step 1] Python環境確認
python --version
if errorlevel 1 (
    echo エラー: Pythonが見つかりません
    echo https://www.python.org/ からインストールしてください
    pause
    exit /b 1
)
echo.

rem pip更新
echo [Step 2] pip更新
python -m pip install --upgrade pip
echo.

rem 基本ライブラリインストール
echo [Step 3] 基本ライブラリインストール
echo インストール中... (数分かかります)
pip install playwright --upgrade --no-cache-dir
pip install gspread --upgrade --no-cache-dir  
pip install oauth2client --upgrade --no-cache-dir
pip install google-auth --upgrade --no-cache-dir
pip install google-auth-oauthlib --upgrade --no-cache-dir
pip install aiohttp --upgrade --no-cache-dir

if errorlevel 1 (
    echo.
    echo ライブラリインストールでエラーが発生しました
    echo 別の方法を試行します...
    
    rem ユーザーディレクトリにインストール
    echo ユーザーディレクトリにインストール中...
    pip install playwright gspread oauth2client google-auth google-auth-oauthlib aiohttp --user --upgrade
)
echo.

rem Playwrightブラウザインストール
echo [Step 4] Playwright Chromiumブラウザインストール
echo ブラウザインストール中... (数分かかります)

rem 複数の方法を順次試行
echo 方法1: python -m playwright install chromium
python -m playwright install chromium
if errorlevel 0 goto browser_success

echo.
echo 方法2: playwright install chromium  
playwright install chromium
if errorlevel 0 goto browser_success

echo.
echo 方法3: 依存関係込みでインストール
python -m playwright install chromium --with-deps
if errorlevel 0 goto browser_success

echo.
echo 方法4: 強制再インストール
python -m playwright install --force chromium
if errorlevel 0 goto browser_success

rem ブラウザインストール失敗時の対応
echo.
echo ========================================
echo  ブラウザインストール失敗
echo ========================================
echo 手動での解決方法:
echo 1. 管理者権限でコマンドプロンプトを開く
echo 2. cd "C:\Users\color\Documents\gemini_auto_image"
echo 3. python -m playwright install chromium --with-deps
echo.
echo または以下のサイトから手動でダウンロード:
echo https://playwright.dev/python/docs/browsers
echo.
goto test_imports

:browser_success
echo ✓ ブラウザインストール成功
echo.

:test_imports
rem インポートテスト
echo [Step 5] インストール確認テスト
python -c "
try:
    import playwright
    print('✓ playwright: OK')
except ImportError as e:
    print('✗ playwright: NG -', e)

try:
    import gspread
    print('✓ gspread: OK')
except ImportError as e:
    print('✗ gspread: NG -', e)

try:
    from oauth2client.service_account import ServiceAccountCredentials
    print('✓ oauth2client: OK')
except ImportError as e:
    print('✗ oauth2client: NG -', e)

try:
    import google.auth
    print('✓ google-auth: OK')
except ImportError as e:
    print('✗ google-auth: NG -', e)

try:
    import aiohttp
    print('✓ aiohttp: OK')
except ImportError as e:
    print('✗ aiohttp: NG -', e)

print('\\n=== ブラウザ動作テスト ===')
try:
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        browser.close()
    print('✓ Chromiumブラウザ: 正常動作')
except Exception as e:
    print('✗ Chromiumブラウザ: 動作不良 -', e)
"

echo.
echo ========================================
echo  セットアップ完了
echo ========================================
echo 次のステップ:
echo 1. Google Sheets APIの設定
echo 2. service_account.json の配置
echo 3. スプレッドシートの共有設定
echo 4. python gemini_automation.py で実行
echo.

rem 設定確認スクリプトの実行
if exist "config_checker.py" (
    echo 設定確認を実行しますか？ (y/n)
    set /p confirm=
    if /i "%confirm%"=="y" (
        python config_checker.py
    )
)

echo.
pause