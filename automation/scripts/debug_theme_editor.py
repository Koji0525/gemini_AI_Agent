"""
テーマエディターのデバッグ - ファイル選択問題の調査
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

load_dotenv()

project_root = "/workspaces/gemini_AI_Agent"
sys.path.insert(0, project_root)

from browser_control.browser_controller import BrowserController


async def debug_theme_editor():
    """テーマエディターのHTML構造を調査"""
    print("🔍 テーマエディターデバッグ開始")
    print("=" * 60)

    browser = BrowserController()

    try:
        await browser.setup_browser(headless=True)

        # ログイン
        wp_url = os.getenv("WP_URL")
        wp_user = os.getenv("WP_USER")
        wp_pass = os.getenv("WP_PASS")

        await browser.page.goto(f"{wp_url}/wp-admin")
        await browser.page.fill("#user_login", wp_user)
        await browser.page.fill("#user_pass", wp_pass)
        await browser.page.click("#wp-submit")
        await browser.page.wait_for_selector("#wpadminbar")

        print("✅ WordPressログイン成功")

        # テーマエディターに移動
        await browser.page.goto(f"{wp_url}/wp-admin/theme-editor.php")
        print(f"📍 URL: {browser.page.url}")

        # ページのHTML構造を分析
        print("\n🔍 ファイル選択要素の調査:")

        # 1. select要素の確認
        selects = await browser.page.query_selector_all("select")
        print(f"\n📋 select要素の数: {len(selects)}")

        for i, select in enumerate(selects):
            name = await select.get_attribute("name")
            id_attr = await select.get_attribute("id")
            print(f"\n  Select {i+1}:")
            print(f"    name: {name}")
            print(f"    id: {id_attr}")

            # オプションを取得
            options = await select.query_selector_all("option")
            print(f"    オプション数: {len(options)}")

            for j, option in enumerate(options[:5]):  # 最初の5個だけ表示
                value = await option.get_attribute("value")
                text = await option.text_content()
                print(f"      {j+1}. value='{value}' text='{text.strip()}'")

            if len(options) > 5:
                print(f"      ... 他 {len(options) - 5} 個")

        # 2. functions.phpの存在確認
        print("\n🔍 functions.phpの検索:")

        # ページ全体のテキストからfunctions.phpを検索
        content = await browser.page.content()
        if "functions.php" in content:
            print("  ✅ functions.phpがページ内に存在")

            # 詳細な位置を特定
            functions_elements = await browser.page.query_selector_all('*:has-text("functions.php")')
            print(f"  📍 functions.phpを含む要素: {len(functions_elements)}個")

            for i, elem in enumerate(functions_elements[:3]):
                tag = await elem.evaluate("el => el.tagName")
                print(f"    {i+1}. {tag}")
        else:
            print("  ❌ functions.phpがページ内に見つかりません")

        # 3. テーマ選択の確認
        print("\n🔍 テーマ選択の状態:")

        theme_select = await browser.page.query_selector('select[name="theme"]')
        if theme_select:
            selected = await theme_select.evaluate("el => el.value")
            print(f"  現在のテーマ: {selected}")

            themes = await theme_select.query_selector_all("option")
            print(f"  利用可能なテーマ: {len(themes)}個")
            for theme in themes:
                value = await theme.get_attribute("value")
                text = await theme.text_content()
                is_selected = await theme.evaluate("el => el.selected")
                marker = "✓" if is_selected else " "
                print(f"    [{marker}] {text.strip()} (value: {value})")
        else:
            print("  ❌ テーマ選択ドロップダウンが見つかりません")

        # 4. 現在表示されているファイル
        print("\n🔍 現在のファイル:")

        file_input = await browser.page.query_selector('input[name="file"]')
        if file_input:
            current_file = await file_input.get_attribute("value")
            print(f"  現在のファイル: {current_file}")

        # 5. スクリーンショット保存
        await browser.page.screenshot(path="automation/logs/day2/theme_editor_debug.png")
        print("\n📸 スクリーンショット保存: automation/logs/day2/theme_editor_debug.png")

        # 6. HTML構造を保存
        html_content = await browser.page.content()
        with open("automation/logs/day2/theme_editor_html.html", "w", encoding="utf-8") as f:
            f.write(html_content)
        print("📄 HTML保存: automation/logs/day2/theme_editor_html.html")

        print("\n" + "=" * 60)
        print("🔍 デバッグ完了")

    except Exception as e:
        print(f"❌ デバッグエラー: {e}")
        import traceback

        traceback.print_exc()
    finally:
        await browser.cleanup()


if __name__ == "__main__":
    asyncio.run(debug_theme_editor())
