#!/usr/bin/env python3
"""
WPCPTAgent - WordPressカスタム投稿タイプ管理エージェント
PHPコード生成アプローチ

v1.0 - 初回実装
運用ルール準拠: 1ファイル1000行以下、PEP 8準拠
"""

import sys
import requests
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

sys.path.insert(0, '/workspaces/gemini_AI_Agent')
from configuration.config_loader import ConfigLoader


@dataclass
class CPTSpecification:
    """カスタム投稿タイプの仕様"""
    post_type: str  # 投稿タイプ名（slug）
    singular_name: str  # 単数形ラベル
    plural_name: str  # 複数形ラベル
    description: str = ""  # 説明
    public: bool = True  # 公開するか
    has_archive: bool = True  # アーカイブページを持つか
    hierarchical: bool = False  # 階層構造（ページのような）
    supports: List[str] = None  # サポート機能
    menu_icon: str = "dashicons-admin-post"  # メニューアイコン
    show_in_rest: bool = True  # REST APIで表示
    
    def __post_init__(self):
        """デフォルト値の設定"""
        if self.supports is None:
            self.supports = ['title', 'editor', 'thumbnail', 'excerpt']


class WPCPTAgent:
    """WordPressカスタム投稿タイプ管理エージェント"""
    
    def __init__(self, config_loader: ConfigLoader):
        """
        初期化（依存性注入）
        
        Args:
            config_loader: ConfigLoaderインスタンス
        """
        self.config = config_loader
        self.wp_url = self.config._config.get("WP_URL")
        self.wp_user = self.config._config.get("wp_user")
        self.wp_pass = self.config._config.get("wp_pass")
        self.auth = (self.wp_user, self.wp_pass)
    
    async def list_post_types(self) -> Dict[str, Any]:
        """
        既存の投稿タイプ一覧を取得
        
        Returns:
            Dict: 投稿タイプ情報
        """
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
                
                # カスタム投稿タイプを抽出（標準以外）
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
        """
        投稿タイプの存在を確認
        
        Args:
            post_type: 投稿タイプ名
            
        Returns:
            bool: 存在する場合True
        """
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
        """
        register_post_type()のPHPコードを生成
        
        Args:
            spec: CPT仕様
            
        Returns:
            str: 生成されたPHPコード
        """
        print(f"\n🔧 PHPコード生成中: {spec.post_type}")
        
        # サポート機能をPHP配列形式に変換
        supports_str = "array('" + "', '".join(spec.supports) + "')"
        
        # ラベル設定
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
        
        # PHPコード生成
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
        """
        生成したPHPコードをファイルに保存
        
        Args:
            php_code: PHPコード
            filename: ファイル名
            
        Returns:
            str: 保存先パス
        """
        import os
        
        output_dir = "/workspaces/gemini_AI_Agent/agent_outputs/wordpress_cpt"
        os.makedirs(output_dir, exist_ok=True)
        
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(php_code)
        
        print(f"✅ PHPコード保存: {filepath}")
        return filepath
    
    async def create_cpt(self, spec: CPTSpecification) -> Dict[str, Any]:
        """
        カスタム投稿タイプを作成（PHPコード生成）
        
        Args:
            spec: CPT仕様
            
        Returns:
            Dict: 実行結果
        """
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
            "",
            "【方法2: カスタムプラグインとして使用】",
            f"1. 生成されたファイル ({filename}) をそのまま使用",
            "2. wp-content/plugins/ ディレクトリに配置",
            "3. WordPressダッシュボードでプラグインを有効化",
            "",
            "⚠️  重要: パーマリンク設定の更新を忘れずに！",
            "   （設定 > パーマリンク設定 > 変更を保存）"
        ]
        
        result["instructions"] = instructions
        result["success"] = True
        
        print("\n" + "=" * 80)
        print("✅ CPT作成処理完了")
        print("=" * 80)
        
        for instruction in instructions:
            print(instruction)
        
        return result


# テスト用のメイン関数
async def test_cpt_agent():
    """WPCPTAgentのテスト"""
    print("=" * 80)
    print("🧪 WPCPTAgent テスト")
    print("=" * 80)
    
    from dotenv import load_dotenv
    load_dotenv("/workspaces/gemini_AI_Agent/.env")
    
    config = ConfigLoader()
    agent = WPCPTAgent(config)
    
    # 1. 既存の投稿タイプ一覧
    await agent.list_post_types()
    
    # 2. テスト用CPT仕様
    test_spec = CPTSpecification(
        post_type="portfolio",
        singular_name="ポートフォリオ",
        plural_name="ポートフォリオ一覧",
        description="作品ポートフォリオを管理",
        has_archive=True,
        hierarchical=False,
        supports=['title', 'editor', 'thumbnail', 'excerpt', 'custom-fields'],
        menu_icon="dashicons-portfolio"
    )
    
    # 3. CPT作成（PHPコード生成）
    result = await agent.create_cpt(test_spec)
    
    print("\n" + "=" * 80)
    print("📊 テスト結果:")
    print(f"   成功: {result['success']}")
    print(f"   投稿タイプ: {result['post_type']}")
    print(f"   保存先: {result['filepath']}")
    print("=" * 80)


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_cpt_agent())
