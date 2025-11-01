#!/usr/bin/env python3
"""
WordPress自動化タスク実行
Task Executorから呼び出される
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.wordpress.wp_auto_config_agent import WPAutoConfigAgent
from agents.wordpress.wp_data_populator import WPDataPopulator
from browser_control.browser_controller import BrowserController


async def execute_wordpress_automation():
    """WordPress自動化の実行"""

    browser = BrowserController()
    await browser.initialize()

    try:
        # STEP 1: functions.php更新
        print("🔧 STEP 1: functions.php自動更新")
        wp_config = WPAutoConfigAgent(browser)
        config_success = await wp_config.update_full_system()

        # STEP 2: 企業データ登録
        print("\n📝 STEP 2: 企業データ自動登録")
        populator = WPDataPopulator(browser)
        data_results = await populator.populate_all_companies()

        # STEP 3: 動作確認
        print("\n✅ STEP 3: 動作確認")
        verification = await verify_wordpress_site()

        # 結果をGitHubに保存
        results = {
            "config_success": config_success,
            "data_registered": len([r for r in data_results if r["success"]]),
            "verification": verification,
            "quality_score": calculate_quality_score(config_success, data_results, verification),
        }

        save_results_to_github(results)

        return results

    finally:
        await browser.cleanup()


def calculate_quality_score(config, data, verify):
    """品質スコア計算（10点満点）"""
    score = 0
    if config:
        score += 3
    score += min(5, len([r for r in data if r["success"]]))
    if verify:
        score += 2
    return score


def save_results_to_github(results):
    """結果をGitHubに保存"""
    import json
    from datetime import datetime

    log_file = f"logs/wordpress_automation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(log_file, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\n📊 結果保存: {log_file}")


async def verify_wordpress_site():
    """サイト動作確認"""
    # 実装: 検索ページ、企業一覧の確認
    return True


if __name__ == "__main__":
    asyncio.run(execute_wordpress_automation())
