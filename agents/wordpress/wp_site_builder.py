#!/usr/bin/env python3
"""
WPSiteBuilder - WordPress統合サイト構築オーケストレーター

複数のWordPressエージェントを統合してサイトを自動構築

v1.0 - 初回実装
運用ルール準拠: 1ファイル1000行以下、PEP 8準拠
"""

import sys
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

sys.path.insert(0, '/workspaces/gemini_AI_Agent')
from configuration.config_loader import ConfigLoader
from tools.sheets_manager import GoogleSheetsManager
from agents.wordpress.specialized import (
    WPCPTAgent, 
    CPTSpecification,
    WPTaxonomyAgent,
    TaxonomySpecification
)


@dataclass
class PortfolioSiteSpec:
    """ポートフォリオサイトの仕様"""
    site_name: str
    cpt_spec: CPTSpecification
    taxonomy_specs: List[TaxonomySpecification]


class WPSiteBuilder:
    """WordPress統合サイト構築オーケストレーター"""
    
    def __init__(self, config_loader: ConfigLoader, sheets_manager: Optional[GoogleSheetsManager] = None):
        """
        初期化（依存性注入）
        
        Args:
            config_loader: ConfigLoaderインスタンス
            sheets_manager: GoogleSheetsManagerインスタンス
        """
        self.config = config_loader
        self.sheets_manager = sheets_manager
        
        # エージェント初期化
        self.cpt_agent = WPCPTAgent(config_loader, sheets_manager)
        self.taxonomy_agent = WPTaxonomyAgent(config_loader, sheets_manager)
    
    async def build_portfolio_site(self, site_spec: PortfolioSiteSpec) -> Dict[str, Any]:
        """
        ポートフォリオサイトを自動構築
        
        Args:
            site_spec: サイト仕様
            
        Returns:
            Dict: 構築結果
        """
        print("=" * 80)
        print(f"🏗️  ポートフォリオサイト構築開始: {site_spec.site_name}")
        print("=" * 80)
        
        results = {
            "site_name": site_spec.site_name,
            "cpt_result": None,
            "taxonomy_results": [],
            "success": False,
            "php_files": []
        }
        
        # 1. カスタム投稿タイプ作成
        print("\n【STEP 1: カスタム投稿タイプ作成】")
        print("=" * 80)
        cpt_result = await self.cpt_agent.create_cpt(site_spec.cpt_spec)
        results["cpt_result"] = cpt_result
        
        if cpt_result["success"]:
            results["php_files"].append(cpt_result["filepath"])
            print(f"✅ CPT作成成功: {cpt_result['post_type']}")
        else:
            print(f"❌ CPT作成失敗: {cpt_result.get('message', '不明なエラー')}")
            return results
        
        # 2. タクソノミー作成
        print("\n【STEP 2: タクソノミー作成】")
        print("=" * 80)
        
        for i, tax_spec in enumerate(site_spec.taxonomy_specs, 1):
            print(f"\n[{i}/{len(site_spec.taxonomy_specs)}] {tax_spec.plural_name}を作成中...")
            
            tax_result = await self.taxonomy_agent.create_taxonomy(tax_spec)
            results["taxonomy_results"].append(tax_result)
            
            if tax_result["success"]:
                results["php_files"].append(tax_result["filepath"])
                print(f"✅ タクソノミー作成成功: {tax_result['taxonomy']}")
            else:
                print(f"⚠️  タクソノミー作成失敗: {tax_result.get('message', '不明なエラー')}")
        
        # 3. 成功判定
        all_taxonomies_success = all(r["success"] for r in results["taxonomy_results"])
        results["success"] = cpt_result["success"] and all_taxonomies_success
        
        # 4. サマリー表示
        print("\n" + "=" * 80)
        print("📊 構築サマリー")
        print("=" * 80)
        print(f"サイト名: {site_spec.site_name}")
        print(f"CPT: {'✅' if cpt_result['success'] else '❌'} {site_spec.cpt_spec.post_type}")
        print(f"タクソノミー:")
        for tax_result in results["taxonomy_results"]:
            status = '✅' if tax_result['success'] else '❌'
            print(f"  {status} {tax_result['taxonomy']}")
        
        print(f"\n生成されたPHPファイル: {len(results['php_files'])}個")
        for php_file in results["php_files"]:
            print(f"  📄 {php_file}")
        
        if results["success"]:
            print("\n🎉 サイト構築完了！")
        else:
            print("\n⚠️  一部のコンポーネントの作成に失敗しました")
        
        print("=" * 80)
        
        return results
    
    async def build_demo_portfolio_site(self) -> Dict[str, Any]:
        """
        デモ用ポートフォリオサイトを構築
        
        Returns:
            Dict: 構築結果
        """
        print("\n🎬 デモ: Webデザイナーのポートフォリオサイト構築")
        print("=" * 80)
        
        # CPT仕様
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
        
        # タクソノミー仕様
        taxonomy_specs = [
            # 1. スキル（階層型）
            TaxonomySpecification(
                taxonomy="skill",
                singular_name="スキル",
                plural_name="スキル一覧",
                post_types=['portfolio'],
                description="プロジェクトで使用したスキル・技術",
                hierarchical=True,
                show_admin_column=True
            ),
            # 2. プロジェクトカテゴリー（階層型）
            TaxonomySpecification(
                taxonomy="project_category",
                singular_name="プロジェクトカテゴリー",
                plural_name="プロジェクトカテゴリー一覧",
                post_types=['portfolio'],
                description="プロジェクトの種類",
                hierarchical=True,
                show_admin_column=True
            ),
            # 3. プロジェクトタグ（非階層型）
            TaxonomySpecification(
                taxonomy="project_tag",
                singular_name="プロジェクトタグ",
                plural_name="プロジェクトタグ一覧",
                post_types=['portfolio'],
                description="プロジェクトの特徴",
                hierarchical=False,
                show_admin_column=False
            ),
        ]
        
        # サイト仕様
        site_spec = PortfolioSiteSpec(
            site_name="Webデザイナーポートフォリオ",
            cpt_spec=cpt_spec,
            taxonomy_specs=taxonomy_specs
        )
        
        # サイト構築実行
        result = await self.build_portfolio_site(site_spec)
        
        return result


async def test_site_builder():
    """WPSiteBuilderのテスト"""
    print("=" * 80)
    print("🧪 WPSiteBuilder テスト")
    print("=" * 80)
    
    from dotenv import load_dotenv
    load_dotenv("/workspaces/gemini_AI_Agent/.env")
    
    config = ConfigLoader()
    
    # SheetsManager初期化
    sheets_manager = GoogleSheetsManager(
        spreadsheet_id=config._config.get("SPREADSHEET_ID"),
        service_account_file=config._config.get("GOOGLE_SERVICE_ACCOUNT_FILE")
    )
    
    # SiteBuilder初期化
    builder = WPSiteBuilder(config, sheets_manager)
    
    # デモサイト構築
    result = await builder.build_demo_portfolio_site()
    
    print("\n" + "=" * 80)
    print("📊 最終結果:")
    print(f"   成功: {result['success']}")
    print(f"   生成ファイル数: {len(result['php_files'])}")
    print("=" * 80)


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_site_builder())
