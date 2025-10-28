#!/usr/bin/env python3
"""
WPCPTAgent - WordPressカスタム投稿タイプ管理エージェント
PHPコード生成アプローチ + スプレッドシート記録

v2.0 - ログ記録機能追加
運用ルール準拠: 1ファイル1000行以下、PEP 8準拠
"""

import sys
import requests
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

sys.path.insert(0, '/workspaces/gemini_AI_Agent')
from configuration.config_loader import ConfigLoader
from tools.sheets_manager import GoogleSheetsManager
from agents.wordpress.specialized.wp_agent_logger import WPAgentLogger


@dataclass
class CPTSpecification:
    """カスタム投稿タイプの仕様"""
    post_type: str
    singular_name: str
    plural_name: str
    description: str = ""
    public: bool = True
    has_archive: bool = True
    hierarchical: bool = False
    supports: List[str] = None
    menu_icon: str = "dashicons-admin-post"
    show_in_rest: bool = True
    
    def __post_init__(self):
        if self.supports is None:
            self.supports = ['title', 'editor', 'thumbnail', 'excerpt']


class WPCPTAgent:
    """WordPressカスタム投稿タイプ管理エージェント"""
    
    def __init__(self, config_loader: ConfigLoader, sheets_manager: Optional[GoogleSheetsManager] = None):
        """
        初期化（依存性注入）
        
        Args:
            config_loader: ConfigLoaderインスタンス
            sheets_manager: GoogleSheetsManagerインスタンス（オプション）
        """
        self.config = config_loader
        self.wp_url = self.config._config.get("WP_URL")
        self.wp_user = self.config._config.get("wp_user")
        self.wp_pass = self.config._config.get("wp_pass")
        self.auth = (self.wp_user, self.wp_pass)
        
        # ロガーの初期化
        self.logger = WPAgentLogger(sheets_manager) if sheets_manager else None
    
    async def list_post_types(self) -> Dict[str, Any]:
        """既存の投稿タイプ一覧を取得"""
        print("\n📋 既存の投稿タイプを取得中...")
        try:
            response = requests.get(
                f"{self.wp_url}/wp-json/wp/v2/types",
                auth=self.auth,
                timeout=10
            )
            
            if response.status_code == 200:
                types = response.json()
                print(f"✅ 投稿タイプ数: {len(types)}個")
                
                standard_types = ['post', 'page', 'attachment', 'nav_menu_item', 
                                'wp_block', 'wp_template', 'wp_template_part',
                                'wp_global_styles', 'wp_navigation', 'wp_font_family', 'wp_font_face']
                
                custom_types = {k: v for k, v in types.items() if k not in standard_types}
                
                if custom_types:
                    print(f"   カスタム投稿タイプ: {len(custom_types)}個")
                    for type_name, type_data in custom_types.items():
                        print(f"   - {type_name}: {type_data.get('name', 'N/A')}")
                
                return types
            else:
                print(f"❌ 取得失敗: Status {response.status_code}")
                return {}
                
        except Exception as e:
            print(f"❌ エラー: {e}")
            return {}
    
    async def verify_post_type(self, post_type: str) -> bool:
        """投稿タイプの存在を確認"""
        try:
            response = requests.get(
                f"{self.wp_url}/wp-json/wp/v2/types/{post_type}",
                auth=self.auth,
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"✅ 投稿タイプ '{post_type}' が存在します")
                return True
            else:
                print(f"❌ 投稿タイプ '{post_type}' は存在しません")
                return False
                
        except Exception as e:
            print(f"❌ エラー: {e}")
            return False
    
    def generate_php_code(self, spec: CPTSpecification) -> str:
        """register_post_type()のPHPコードを生成"""
        print(f"\n🔧 PHPコード生成中: {spec.post_type}")
        
        supports_str = "array('" + "', '".join(spec.supports) + "')"
        
        labels = {
            'name': spec.plural_name,
            'singular_name': spec.singular_name,
            'add_new': f'新規{spec.singular_name}追加',
            'add_new_item': f'新しい{spec.singular_name}を追加',
            'edit_item': f'{spec.singular_name}を編集',
            'new_item': f'新しい{spec.singular_name}',
            'view_item': f'{spec.singular_name}を表示',
            'search_items': f'{spec.plural_name}を検索',
            'not_found': f'{spec.plural_name}が見つかりませんでした',
            'not_found_in_trash': f'ゴミ箱に{spec.plural_name}はありません',
        }
        
        labels_str = "array(\n"
        for key, value in labels.items():
            labels_str += f"        '{key}' => '{value}',\n"
        labels_str += "    )"
        
        php_code = f"""<?php
/**
 * カスタム投稿タイプ: {spec.plural_name}
 * 生成日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
 */

function register_cpt_{spec.post_type}() {{
    $labels = {labels_str};
    
    $args = array(
        'labels' => $labels,
        'description' => '{spec.description}',
        'public' => {str(spec.public).lower()},
        'has_archive' => {str(spec.has_archive).lower()},
        'hierarchical' => {str(spec.hierarchical).lower()},
        'supports' => {supports_str},
        'menu_icon' => '{spec.menu_icon}',
        'show_in_rest' => {str(spec.show_in_rest).lower()},
        'rewrite' => array('slug' => '{spec.post_type}'),
    );
    
    register_post_type('{spec.post_type}', $args);
}}

add_action('init', 'register_cpt_{spec.post_type}');
?>"""
        
        print("✅ PHPコード生成完了")
        return php_code
    
    def save_php_code(self, php_code: str, filename: str) -> str:
        """生成したPHPコードをファイルに保存"""
        import os
        
        output_dir = "/workspaces/gemini_AI_Agent/agent_outputs/wordpress_cpt"
        os.makedirs(output_dir, exist_ok=True)
        
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(php_code)
        
        print(f"✅ PHPコード保存: {filepath}")
        return filepath
    
    async def create_cpt(self, spec: CPTSpecification) -> Dict[str, Any]:
        """カスタム投稿タイプを作成（PHPコード生成）"""
        print("=" * 80)
        print(f"🚀 カスタム投稿タイプ作成: {spec.plural_name}")
        print("=" * 80)
        
        result = {
            "success": False,
            "post_type": spec.post_type,
            "php_code": "",
            "filepath": "",
            "instructions": []
        }
        
        # 1. 既存の確認
        existing = await self.verify_post_type(spec.post_type)
        if existing:
            print(f"⚠️  投稿タイプ '{spec.post_type}' は既に存在します")
            result["success"] = False
            result["message"] = "既に存在します"
            return result
        
        # 2. PHPコード生成
        php_code = self.generate_php_code(spec)
        result["php_code"] = php_code
        
        # 3. ファイルに保存
        filename = f"cpt_{spec.post_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.php"
        filepath = self.save_php_code(php_code, filename)
        result["filepath"] = filepath
        
        # 4. 配置方法の指示
        instructions = [
            "📋 カスタム投稿タイプの有効化手順:",
            "",
            "【方法1: functions.phpに追加】",
            f"1. 生成されたコード ({filepath}) を開く",
            "2. <?php と ?> を除いたコードをコピー",
            "3. テーマの functions.php に貼り付け",
            "4. WordPressダッシュボードでパーマリンク設定を更新",
        ]
        
        result["instructions"] = instructions
        result["success"] = True
        
        # 5. スプレッドシートに記録
        if self.logger:
            await self.logger.log_cpt_creation(result, spec)
        
        print("\n" + "=" * 80)
        print("✅ CPT作成処理完了")
        print("=" * 80)
        
        for instruction in instructions:
            print(instruction)
        
        return result


# テスト用のメイン関数
async def test_cpt_agent_with_logging():
    """WPCPTAgent（ログ記録付き）のテスト"""
    print("=" * 80)
    print("�� WPCPTAgent（ログ記録付き）テスト")
    print("=" * 80)
    
    from dotenv import load_dotenv
    load_dotenv("/workspaces/gemini_AI_Agent/.env")
    
    config = ConfigLoader()
    
    # SheetsManager初期化
    sheets_manager = GoogleSheetsManager(
        spreadsheet_id=config._config.get("SPREADSHEET_ID"),
        service_account_file=config._config.get("GOOGLE_SERVICE_ACCOUNT_FILE")
    )
    
    # CPTAgent初期化
    agent = WPCPTAgent(config, sheets_manager)
    
    # テスト用CPT仕様
    test_spec = CPTSpecification(
        post_type="event",
        singular_name="イベント",
        plural_name="イベント一覧",
        description="イベント情報を管理",
        has_archive=True,
        hierarchical=False,
        supports=['title', 'editor', 'thumbnail', 'excerpt'],
        menu_icon="dashicons-calendar"
    )
    
    # CPT作成
    result = await agent.create_cpt(test_spec)
    
    print("\n" + "=" * 80)
    print("📊 テスト結果:")
    print(f"   成功: {result['success']}")
    print(f"   投稿タイプ: {result['post_type']}")
    print(f"   保存先: {result['filepath']}")
    print("=" * 80)


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_cpt_agent_with_logging())
