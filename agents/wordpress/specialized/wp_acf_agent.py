#!/usr/bin/env python3
"""
WPACFAgent - WordPress ACF（Advanced Custom Fields）管理エージェント
ACF JSON生成アプローチ

v1.0 - 初回実装
運用ルール準拠: 1ファイル1000行以下、PEP 8準拠
"""

import sys
import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime
import os

sys.path.insert(0, '/workspaces/gemini_AI_Agent')
from configuration.config_loader import ConfigLoader
from tools.sheets_manager import GoogleSheetsManager
from agents.wordpress.specialized.wp_agent_logger import WPAgentLogger


@dataclass
class ACFField:
    """ACFフィールドの定義"""
    key: str
    label: str
    name: str
    type: str
    required: bool = False
    default_value: str = ""
    placeholder: str = ""
    instructions: str = ""
    
    # type別の追加設定
    choices: Dict[str, str] = field(default_factory=dict)  # select, radio, checkbox用
    return_format: str = ""  # image, gallery用
    display_format: str = ""  # date_picker用
    min: str = ""  # number, gallery用
    max: str = ""  # number, gallery用
    
    def to_acf_dict(self) -> Dict[str, Any]:
        """ACF JSON形式に変換"""
        base = {
            "key": self.key,
            "label": self.label,
            "name": self.name,
            "type": self.type,
            "required": 1 if self.required else 0,
            "default_value": self.default_value,
            "placeholder": self.placeholder,
            "instructions": self.instructions,
        }
        
        # type別の追加設定
        if self.type in ['select', 'radio', 'checkbox'] and self.choices:
            base["choices"] = self.choices
        
        if self.type in ['image', 'gallery'] and self.return_format:
            base["return_format"] = self.return_format
        
        if self.type == 'date_picker':
            base["display_format"] = self.display_format or "Y/m/d"
            base["return_format"] = self.return_format or "Y-m-d"
        
        if self.type in ['number', 'gallery']:
            if self.min:
                base["min"] = self.min
            if self.max:
                base["max"] = self.max
        
        return base


@dataclass
class ACFFieldGroup:
    """ACFフィールドグループの定義"""
    key: str
    title: str
    fields: List[ACFField]
    post_types: List[str] = field(default_factory=lambda: ['post'])
    position: str = "normal"  # normal, side, acf_after_title
    style: str = "default"  # default, seamless
    active: bool = True
    
    def to_acf_json(self) -> Dict[str, Any]:
        """ACF JSON形式に変換"""
        return {
            "key": self.key,
            "title": self.title,
            "fields": [f.to_acf_dict() for f in self.fields],
            "location": [
                [
                    {
                        "param": "post_type",
                        "operator": "==",
                        "value": post_type
                    }
                ] for post_type in self.post_types
            ],
            "menu_order": 0,
            "position": self.position,
            "style": self.style,
            "label_placement": "top",
            "instruction_placement": "label",
            "active": self.active
        }


class WPACFAgent:
    """WordPress ACF管理エージェント"""
    
    def __init__(self, config_loader: ConfigLoader, sheets_manager: Optional[GoogleSheetsManager] = None):
        """
        初期化（依存性注入）
        
        Args:
            config_loader: ConfigLoaderインスタンス
            sheets_manager: GoogleSheetsManagerインスタンス
        """
        self.config = config_loader
        self.sheets_manager = sheets_manager
        
        # ロガーの初期化
        self.logger = WPAgentLogger(sheets_manager) if sheets_manager else None
    
    def generate_acf_json(self, field_group: ACFFieldGroup) -> str:
        """ACF JSON文字列を生成"""
        print(f"\n🔧 ACF JSON生成中: {field_group.title}")
        
        acf_data = field_group.to_acf_json()
        json_str = json.dumps(acf_data, indent=2, ensure_ascii=False)
        
        print("✅ ACF JSON生成完了")
        return json_str
    
    def generate_php_code(self, field_group: ACFFieldGroup) -> str:
        """ACF登録用のPHPコードを生成"""
        print(f"\n🔧 PHPコード生成中: {field_group.title}")
        
        acf_data = field_group.to_acf_json()
        json_str = json.dumps(acf_data, indent=4, ensure_ascii=False)
        
        # PHPコード生成
        php_code = f"""<?php
/**
 * ACF フィールドグループ: {field_group.title}
 * 対象投稿タイプ: {', '.join(field_group.post_types)}
 * 生成日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
 */

if( function_exists('acf_add_local_field_group') ):

acf_add_local_field_group({json_str});

endif;
?>"""
        
        print("✅ PHPコード生成完了")
        return php_code
    
    def save_acf_json(self, json_str: str, filename: str) -> str:
        """ACF JSONをファイルに保存"""
        output_dir = "/workspaces/gemini_AI_Agent/agent_outputs/wordpress_acf/json"
        os.makedirs(output_dir, exist_ok=True)
        
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(json_str)
        
        print(f"✅ ACF JSON保存: {filepath}")
        return filepath
    
    def save_php_code(self, php_code: str, filename: str) -> str:
        """PHPコードをファイルに保存"""
        output_dir = "/workspaces/gemini_AI_Agent/agent_outputs/wordpress_acf/php"
        os.makedirs(output_dir, exist_ok=True)
        
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(php_code)
        
        print(f"✅ PHPコード保存: {filepath}")
        return filepath
    
    async def create_field_group(self, field_group: ACFFieldGroup) -> Dict[str, Any]:
        """フィールドグループを作成"""
        print("=" * 80)
        print(f"🚀 ACF フィールドグループ作成: {field_group.title}")
        print("=" * 80)
        
        result = {
            "success": False,
            "field_group_key": field_group.key,
            "field_group_title": field_group.title,
            "json_file": "",
            "php_file": "",
            "instructions": []
        }
        
        try:
            # 1. ACF JSON生成
            json_str = self.generate_acf_json(field_group)
            
            # 2. PHPコード生成
            php_code = self.generate_php_code(field_group)
            
            # 3. ファイルに保存
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            json_filename = f"acf_{field_group.key}_{timestamp}.json"
            php_filename = f"acf_{field_group.key}_{timestamp}.php"
            
            json_filepath = self.save_acf_json(json_str, json_filename)
            php_filepath = self.save_php_code(php_code, php_filename)
            
            result["json_file"] = json_filepath
            result["php_file"] = php_filepath
            
            # 4. 配置方法の指示
            instructions = [
                f"📋 ACF フィールドグループの有効化手順:",
                "",
                "【方法1: ACF JSONファイルとして配置（推奨）】",
                f"1. ACF プラグインをインストール・有効化",
                f"2. wp-content/uploads/acf-json/ ディレクトリを作成",
                f"3. 生成されたJSONファイル ({json_filename}) を配置",
                f"4. WordPressダッシュボードで自動的に読み込まれる",
                "",
                "【方法2: functions.phpに追加】",
                f"1. 生成されたPHPコード ({php_filepath}) を開く",
                f"2. <?php と ?> を除いたコードをコピー",
                f"3. テーマの functions.php に貼り付け",
                "",
                f"✅ 対象投稿タイプ: {', '.join(field_group.post_types)}",
                f"✅ フィールド数: {len(field_group.fields)}個",
            ]
            
            result["instructions"] = instructions
            result["success"] = True
            
            # 5. スプレッドシートに記録（簡易版）
            if self.logger:
                # TODO: ACF専用のログメソッドを追加
                pass
            
            print("\n" + "=" * 80)
            print("✅ フィールドグループ作成完了")
            print("=" * 80)
            
            for instruction in instructions:
                print(instruction)
            
        except Exception as e:
            print(f"❌ エラー: {e}")
            result["success"] = False
            result["message"] = str(e)
        
        return result
    
    def create_portfolio_field_group(self) -> ACFFieldGroup:
        """ポートフォリオ用のフィールドグループを作成"""
        fields = [
            ACFField(
                key="field_client_name",
                label="クライアント名",
                name="client_name",
                type="text",
                placeholder="例: 株式会社サンプル",
                instructions="プロジェクトのクライアント名を入力してください"
            ),
            ACFField(
                key="field_project_url",
                label="プロジェクトURL",
                name="project_url",
                type="url",
                placeholder="https://example.com",
                instructions="完成したプロジェクトのURLを入力してください"
            ),
            ACFField(
                key="field_project_date",
                label="プロジェクト完成日",
                name="project_date",
                type="date_picker",
                display_format="Y/m/d",
                return_format="Y-m-d",
                instructions="プロジェクトの完成日を選択してください"
            ),
            ACFField(
                key="field_github_url",
                label="GitHub URL",
                name="github_url",
                type="url",
                placeholder="https://github.com/username/repo",
                instructions="GitHubリポジトリのURLを入力してください"
            ),
            ACFField(
                key="field_project_gallery",
                label="プロジェクト画像",
                name="project_gallery",
                type="gallery",
                return_format="array",
                instructions="プロジェクトのスクリーンショットをアップロードしてください"
            ),
        ]
        
        return ACFFieldGroup(
            key="group_portfolio_details",
            title="ポートフォリオ詳細情報",
            fields=fields,
            post_types=['portfolio'],
            position="normal",
            style="default"
        )


async def test_acf_agent():
    """WPACFAgentのテスト"""
    print("=" * 80)
    print("🧪 WPACFAgent テスト")
    print("=" * 80)
    
    from dotenv import load_dotenv
    load_dotenv("/workspaces/gemini_AI_Agent/.env")
    
    config = ConfigLoader()
    
    # SheetsManager初期化
    sheets_manager = GoogleSheetsManager(
        spreadsheet_id=config._config.get("SPREADSHEET_ID"),
        service_account_file=config._config.get("GOOGLE_SERVICE_ACCOUNT_FILE")
    )
    
    # ACFAgent初期化
    agent = WPACFAgent(config, sheets_manager)
    
    # ポートフォリオ用フィールドグループ作成
    field_group = agent.create_portfolio_field_group()
    
    # フィールドグループ作成実行
    result = await agent.create_field_group(field_group)
    
    print("\n" + "=" * 80)
    print("📊 テスト結果:")
    print(f"   成功: {result['success']}")
    print(f"   JSONファイル: {result['json_file']}")
    print(f"   PHPファイル: {result['php_file']}")
    print("=" * 80)


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_acf_agent())
