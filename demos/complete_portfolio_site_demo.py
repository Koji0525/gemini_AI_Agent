#!/usr/bin/env python3
"""
完全版ポートフォリオサイト自動構築デモ

CPT + Taxonomy + ACF を統合した完全自動構築

v1.0 - 最終版
"""

import sys
import asyncio
from dotenv import load_dotenv

sys.path.insert(0, '/workspaces/gemini_AI_Agent')
from configuration.config_loader import ConfigLoader
from tools.sheets_manager import GoogleSheetsManager
from agents.wordpress.specialized import (
    WPCPTAgent,
    CPTSpecification,
    WPTaxonomyAgent,
    TaxonomySpecification,
    WPACFAgent,
    ACFFieldGroupSpec,
    ACFFieldSpec
)


async def build_complete_portfolio_site():
    """完全版ポートフォリオサイトを構築"""
    print("╔════════════════════════════════════════════════════════════════════════════╗")
    print("║              🏗️  完全版ポートフォリオサイト自動構築                      ║")
    print("╚════════════════════════════════════════════════════════════════════════════╝")
    print()
    
    # 初期化
    load_dotenv("/workspaces/gemini_AI_Agent/.env")
    config = ConfigLoader()
    sheets_manager = GoogleSheetsManager(
        spreadsheet_id=config._config.get("SPREADSHEET_ID"),
        service_account_file=config._config.get("GOOGLE_SERVICE_ACCOUNT_FILE")
    )
    
    cpt_agent = WPCPTAgent(config, sheets_manager)
    taxonomy_agent = WPTaxonomyAgent(config, sheets_manager)
    acf_agent = WPACFAgent(config, sheets_manager)
    
    results = {
        "cpt": None,
        "taxonomies": [],
        "acf": None,
        "php_files": [],
        "json_files": []
    }
    
    # STEP 1: カスタム投稿タイプ作成
    print("【STEP 1/4: カスタム投稿タイプ作成】")
    print("=" * 80)
    cpt_spec = CPTSpecification(
        post_type="portfolio",
        singular_name="ポートフォリオ",
        plural_name="ポートフォリオ一覧",
        description="プロジェクト実績を管理",
        has_archive=True,
        hierarchical=False,
        supports=['title', 'editor', 'thumbnail', 'excerpt', 'custom-fields'],
        menu_icon="dashicons-portfolio"
    )
    
    cpt_result = await cpt_agent.create_cpt(cpt_spec)
    results["cpt"] = cpt_result
    if cpt_result["success"]:
        results["php_files"].append(cpt_result["filepath"])
    
    # STEP 2: タクソノミー作成
    print("\n【STEP 2/4: タクソノミー作成】")
    print("=" * 80)
    taxonomy_specs = [
        TaxonomySpecification(
            taxonomy="skill",
            singular_name="スキル",
            plural_name="スキル一覧",
            post_types=['portfolio'],
            description="使用技術・スキル",
            hierarchical=True
        ),
        TaxonomySpecification(
            taxonomy="project_category",
            singular_name="プロジェクトカテゴリー",
            plural_name="プロジェクトカテゴリー一覧",
            post_types=['portfolio'],
            description="プロジェクトの種類",
            hierarchical=True
        ),
        TaxonomySpecification(
            taxonomy="project_tag",
            singular_name="プロジェクトタグ",
            plural_name="プロジェクトタグ一覧",
            post_types=['portfolio'],
            description="プロジェクトの特徴",
            hierarchical=False
        ),
    ]
    
    for tax_spec in taxonomy_specs:
        tax_result = await taxonomy_agent.create_taxonomy(tax_spec)
        results["taxonomies"].append(tax_result)
        if tax_result["success"]:
            results["php_files"].append(tax_result["filepath"])
    
    # STEP 3: ACFフィールドグループ作成
    print("\n【STEP 3/4: ACFカスタムフィールド作成】")
    print("=" * 80)
    acf_spec = ACFFieldGroupSpec(
        key="group_portfolio_details",
        title="ポートフォリオ詳細情報",
        fields=[
            ACFFieldSpec(
                key="field_client_name",
                label="クライアント名",
                name="client_name",
                type="text",
                placeholder="例: 株式会社サンプル"
            ),
            ACFFieldSpec(
                key="field_project_url",
                label="プロジェクトURL",
                name="project_url",
                type="url",
                placeholder="https://example.com"
            ),
            ACFFieldSpec(
                key="field_project_date",
                label="プロジェクト日付",
                name="project_date",
                type="date_picker"
            ),
            ACFFieldSpec(
                key="field_github_url",
                label="GitHub URL",
                name="github_url",
                type="url"
            ),
            ACFFieldSpec(
                key="field_project_images",
                label="プロジェクト画像",
                name="project_images",
                type="gallery"
            ),
        ],
        location_post_type="portfolio"
    )
    
    acf_result = await acf_agent.create_field_group(acf_spec)
    results["acf"] = acf_result
    if acf_result["success"]:
        results["json_files"].append(acf_result["json_filepath"])
        results["php_files"].append(acf_result["php_filepath"])
    
    # STEP 4: サマリー表示
    print("\n【STEP 4/4: 構築サマリー】")
    print("=" * 80)
    print("\n✅ 構築完了!")
    print(f"  CPT: {'✅' if results['cpt']['success'] else '❌'} portfolio")
    print(f"  Taxonomies: {len([t for t in results['taxonomies'] if t['success']])}/3")
    print(f"  ACF: {'✅' if results['acf']['success'] else '❌'} ポートフォリオ詳細情報")
    print(f"\n📄 生成されたファイル:")
    print(f"  PHP: {len(results['php_files'])}個")
    print(f"  JSON: {len(results['json_files'])}個")
    
    print("\n" + "=" * 80)
    print("🎉 完全版ポートフォリオサイトの構築が完了しました！")
    print("=" * 80)
    
    return results


if __name__ == "__main__":
    asyncio.run(build_complete_portfolio_site())
