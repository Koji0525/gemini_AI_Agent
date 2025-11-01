#!/usr/bin/env python3
"""
ネットワーク診断スクリプト
WordPressサイトの接続性を確認
"""

import asyncio
import aiohttp
import time
import sys
import os
from dotenv import load_dotenv

load_dotenv()


async def check_url_connectivity(session, url, timeout=30):
    """URLの接続性をチェック"""
    try:
        start_time = time.time()
        async with session.get(url, timeout=timeout) as response:
            end_time = time.time()
            response_time = (end_time - start_time) * 1000  # ミリ秒

            return {"url": url, "status": response.status, "response_time_ms": round(response_time, 2), "success": True}
    except asyncio.TimeoutError:
        return {"url": url, "status": "timeout", "response_time_ms": timeout * 1000, "success": False}
    except Exception as e:
        return {"url": url, "status": f"error: {str(e)}", "response_time_ms": 0, "success": False}


async def diagnose_wordpress_connectivity():
    """WordPressサイトの接続性を診断"""
    wp_url = os.getenv("WP_URL")

    if not wp_url:
        print("❌ WP_URLが設定されていません")
        return False

    print(f"🔍 WordPress接続性診断: {wp_url}")
    print("=" * 50)

    # チェックするURL一覧
    urls_to_check = [f"{wp_url}/", f"{wp_url}/wp-admin/", f"{wp_url}/wp-admin/post-new.php", f"{wp_url}/wp-login.php"]

    timeout = aiohttp.ClientTimeout(total=30)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        tasks = [check_url_connectivity(session, url) for url in urls_to_check]
        results = await asyncio.gather(*tasks)

    # 結果表示
    all_success = True
    for result in results:
        status_icon = "✅" if result["success"] else "❌"
        print(f"{status_icon} {result['url']}")
        print(f"   ステータス: {result['status']}")
        print(f"   応答時間: {result['response_time_ms']}ms")

        if not result["success"]:
            all_success = False

    print("\n📊 診断結果サマリー:")
    success_count = sum(1 for r in results if r["success"])
    print(f"   成功: {success_count}/{len(results)}")

    if all_success:
        print("�� すべての接続テストに成功しました")
        return True
    else:
        print("❌ 一部の接続テストに失敗しました")
        print("💡 対策:")
        print("   • ネットワーク接続を確認")
        print("   • WordPressサイトがアクティブか確認")
        print("   • ファイアウォール設定を確認")
        return False


if __name__ == "__main__":
    success = asyncio.run(diagnose_wordpress_connectivity())
    sys.exit(0 if success else 1)
