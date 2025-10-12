# dev_agent_acf.py
"""ACF（Advanced Custom Fields）専用開発モジュール"""
import asyncio
import logging
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime
import re
import json

from configuration.config_utils import ErrorHandler, PathManager, config

logger = logging.getLogger(__name__)


# =============================================================================
# ACFフィールドグループ専用プロンプト
# =============================================================================

ACF_FIELD_GROUP_PROMPT = """あなたはACF ProとWordPress開発の専門家です。

【ACFカスタムフィールドグループの作成】

以下の要件に基づいて、完全に動作するACFフィールドグループの定義を生成してください。

【必須要素】
1. フィールドグループの基本設定
   - タイトル、キー、配置場所（投稿タイプ）
2. 各フィールドの詳細定義
   - フィールドタイプ（text, number, select, relationship など）
   - ラベル、名前、キー
   - 検証ルール、デフォルト値
3. 条件付きロジック（必要に応じて）
4. PHP登録コード（`acf_add_local_field_group`）
5. JSON形式のエクスポート（WP-CLIインポート用）

【出力形式】

## ACFフィールドグループ: {group_title}

### 概要
（このフィールドグループの目的と用途）

### PHP登録コード（functions.phpに追加）

```php
<?php
/**
 * ACF Field Group: {group_title}
 * 投稿タイプ: {post_type}
 */

if (function_exists('acf_add_local_field_group')) {{
    acf_add_local_field_group(array(
        'key' => 'group_{unique_key}',
        'title' => '{group_title}',
        'fields' => array(
            // フィールド定義
            array(
                'key' => 'field_{field_key}',
                'label' => '{field_label}',
                'name' => '{field_name}',
                'type' => '{field_type}',
                'required' => {{true|false}},
                'default_value' => '',
            ),
        ),
        'location' => array(
            array(
                array(
                    'param' => 'post_type',
                    'operator' => '==',
                    'value' => '{post_type}',
                ),
            ),
        ),
        'menu_order' => 0,
        'position' => 'normal',
        'style' => 'default',
        'label_placement' => 'top',
        'instruction_placement' => 'label',
        'active' => true,
        'show_in_rest' => 1,
    ));
}}
?>
```

### JSON定義（WP-CLIインポート用）

```json
{{
  "key": "group_{unique_key}",
  "title": "{group_title}",
  "fields": [
    {{
      "key": "field_{field_key}",
      "label": "{field_label}",
      "name": "{field_name}",
      "type": "{field_type}",
      "required": {{true|false}}
    }}
  ],
  "location": [
    [
      {{
        "param": "post_type",
        "operator": "==",
        "value": "{post_type}"
      }}
    ]
  ]
}}
```

### 使用方法

#### テンプレートでの取得
```php
<?php
// 単一値の取得
$value = get_field('field_name', $post_id);

// 条件付き表示
if (get_field('field_name')) :
    echo esc_html(get_field('field_name'));
endif;
?>
```

### 注意事項
- ACF Pro 6.0以上が必要です
- フィールドキーは一意である必要があります
"""


# =============================================================================
# ACFDevAgentクラス（ACF専用機能）
# =============================================================================

class ACFDevAgent:
    """ACF（Advanced Custom Fields）専用開発エージェント"""
    
    def __init__(self, browser, output_folder: Path):
        """
        初期化
        
        Args:
            browser: BrowserControllerインスタンス
            output_folder: 出力先フォルダ
        """
        self.browser = browser
        self.output_folder = output_folder
        self.output_folder.mkdir(parents=True, exist_ok=True)
    
    # =========================================================================
    # パート1: タスク判定メソッド
    # =========================================================================
    
    def is_acf_task(self, task: Dict) -> bool:
        """
        ACFフィールドグループ作成タスクか判定
        
        Args:
            task: タスク辞書
            
        Returns:
            bool: ACFタスクの場合True
        """
        description = task.get('description', '').lower()
        keywords = [
            'acf',
            'advanced custom fields',
            'カスタムフィールド',
            'フィールドグループ',
            'field group'
        ]
        return any(kw in description for kw in keywords)
    
    # =========================================================================
    # パート2: ACFタスク処理メイン
    # =========================================================================
    
    async def process_acf_task(self, task: Dict) -> Dict:
        """
        ACFフィールドグループ作成タスクを処理
        
        Args:
            task: タスク辞書
            
        Returns:
            Dict: 処理結果
        """
        try:
            logger.info("="*60)
            logger.info("ACFフィールドグループ作成タスク")
            logger.info("="*60)
            
            # === パート2-1: タスクから情報を抽出 ===
            acf_info = self._extract_acf_info(task)
            
            # === パート2-2: プロンプトを構築 ===
            full_prompt = self._build_acf_prompt(task, acf_info)
            
            # === パート2-3: Geminiに送信 ===
            logger.info("Geminiにタスクを送信中...")
            await self.browser.send_prompt(full_prompt)
            
            # === パート2-4: 応答待機 ===
            success = await self.browser.wait_for_text_generation(
                max_wait=config.WP_DEV_TIMEOUT if hasattr(config, 'WP_DEV_TIMEOUT') else 300
            )
            
            if not success:
                return {
                    'success': False,
                    'error': '開発AI: タイムアウト（ACFフィールドグループ作成）'
                }
            
            # === パート2-5: 応答を取得 ===
            response_text = await self.browser.extract_latest_text_response()
            
            if not response_text:
                return {
                    'success': False,
                    'error': '開発AI: 応答取得失敗'
                }
            
            logger.info(f"開発AI: 応答取得完了（{len(response_text)}文字）")
            
            # === パート2-6: コード検証 ===
            validation_result = self._validate_acf_code(response_text)
            if not validation_result['is_valid']:
                logger.warning(f"⚠️ ACFコード検証で問題検出: {validation_result['issues']}")
            
            # === パート2-7: 結果を保存 ===
            output_files = self._save_acf_code(response_text, task, acf_info)
            
            # === パート2-8: サマリー作成 ===
            summary = self._create_acf_summary(acf_info, output_files, validation_result)
            
            return {
                'success': True,
                'output_files': output_files,
                'summary': summary,
                'full_text': response_text,
                'validation': validation_result
            }
            
        except Exception as e:
            ErrorHandler.log_error(e, "ACFフィールドグループ作成")
            return {
                'success': False,
                'error': str(e)
            }
    
    # =========================================================================
    # パート3: ACF情報抽出
    # =========================================================================
    
    def _extract_acf_info(self, task: Dict) -> Dict:
        """
        タスクからACF情報を抽出
        
        Args:
            task: タスク辞書
            
        Returns:
            Dict: ACF情報
        """
        description = task.get('description', '')
        parameters = task.get('parameters', {})
        
        if isinstance(parameters, str):
            try:
                parameters = json.loads(parameters)
            except:
                parameters = {}
        
        return {
            'group_title': parameters.get('group_title', 'M&A案件フィールド'),
            'post_type': parameters.get('post_type', 'ma_case'),
            'field_count': parameters.get('field_count', 10),
            'unique_key': parameters.get('unique_key', 'ma_case_fields')
        }
    
    # =========================================================================
    # パート4: プロンプト構築
    # =========================================================================
    
    def _build_acf_prompt(self, task: Dict, acf_info: Dict) -> str:
        """
        ACFフィールドグループ用のプロンプトを構築
        
        Args:
            task: タスク辞書
            acf_info: ACF情報
            
        Returns:
            str: 完全なプロンプト
        """
        prompt = ACF_FIELD_GROUP_PROMPT.format(
            group_title=acf_info['group_title'],
            post_type=acf_info['post_type'],
            unique_key=acf_info['unique_key'],
            field_label='例: 企業名',
            field_name='company_name',
            field_key='company_name',
            field_type='text'
        )
        
        prompt += f"""

【このタスクの具体的な要件】
{task.get('description', '')}

【重要な指示】
1. PHPコードは完全に動作する状態で生成してください
2. JSON形式の定義も必ず含めてください
3. すべてのフィールドにキー（key）を設定してください
4. セキュリティ（エスケープ処理）を考慮してください
5. 多言語対応（Polylang）を考慮してください

上記の要件に基づいて、完全なACFフィールドグループの定義を生成してください。
"""
        
        return prompt
    
    # =========================================================================
    # パート5: ACFコード検証
    # =========================================================================
    
    def _validate_acf_code(self, text: str) -> Dict:
        """
        ACFコードの検証
        
        Args:
            text: 検証対象のテキスト
            
        Returns:
            Dict: 検証結果
        """
        issues = []
        
        # === パート5-1: 必須関数のチェック ===
        if 'acf_add_local_field_group' not in text:
            issues.append('acf_add_local_field_group() 関数が見つかりません')
        
        # === パート5-2: フィールドキーの一意性チェック ===
        field_keys = re.findall(r"'key'\s*=>\s*'(field_[^']+)'", text)
        if len(field_keys) != len(set(field_keys)):
            issues.append('フィールドキーが重複しています')
        
        # === パート5-3: JSONの妥当性チェック ===
        json_blocks = re.findall(r'```json\s*(.*?)```', text, re.DOTALL)
        for json_str in json_blocks:
            try:
                json.loads(json_str)
            except json.JSONDecodeError:
                issues.append('JSON形式が不正です')
        
        # === パート5-4: セキュリティ関数のチェック ===
        if 'get_field(' in text and 'esc_html' not in text and 'esc_attr' not in text:
            issues.append('出力エスケープ関数が不足しています（esc_html, esc_attr）')
        
        return {
            'is_valid': len(issues) == 0,
            'issues': issues
        }
    
    # =========================================================================
    # パート6: ファイル保存
    # =========================================================================
    
    def _save_acf_code(self, text: str, task: Dict, acf_info: Dict) -> list:
        """
        ACFフィールドグループのコードを保存
        
        Args:
            text: 保存対象のテキスト
            task: タスク辞書
            acf_info: ACF情報
            
        Returns:
            list: 保存されたファイル情報のリスト
        """
        output_files = []
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        try:
            # === パート6-1: 完全なドキュメントを保存 ===
            doc_filename = f"acf_{acf_info['unique_key']}_{timestamp}.md"
            doc_path = self.output_folder / doc_filename
            
            with open(doc_path, 'w', encoding='utf-8') as f:
                f.write(f"# ACFフィールドグループ: {acf_info['group_title']}\n\n")
                f.write(f"作成日時: {datetime.now().isoformat()}\n\n")
                f.write(text)
            
            output_files.append({
                'type': 'ドキュメント',
                'path': doc_path
            })
            logger.info(f"ドキュメント保存: {doc_filename}")
            
            # === パート6-2: PHPコードを抽出して保存 ===
            php_code = self._extract_php_code(text)
            if php_code:
                php_filename = f"acf_{acf_info['unique_key']}_{timestamp}.php"
                php_path = self.output_folder / php_filename
                
                with open(php_path, 'w', encoding='utf-8') as f:
                    f.write("<?php\n")
                    f.write(f"/**\n * ACF Field Group: {acf_info['group_title']}\n */\n\n")
                    f.write(php_code)
                
                output_files.append({
                    'type': 'PHPコード',
                    'path': php_path
                })
                logger.info(f"PHPコード保存: {php_filename}")
            
            # === パート6-3: JSON定義を抽出して保存 ===
            json_data = self._extract_json_from_text(text)
            if json_data:
                json_filename = f"acf_{acf_info['unique_key']}_{timestamp}.json"
                json_path = self.output_folder / json_filename
                
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(json_data, f, ensure_ascii=False, indent=2)
                
                output_files.append({
                    'type': 'JSON定義',
                    'path': json_path
                })
                logger.info(f"JSON定義保存: {json_filename}")
            
            # === パート6-4: READMEを生成 ===
            readme_filename = f"README_acf_{acf_info['unique_key']}_{timestamp}.md"
            readme_path = self.output_folder / readme_filename
            
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(f"# {acf_info['group_title']} - インストールガイド\n\n")
                f.write(f"## 概要\n\n")
                f.write(f"投稿タイプ: {acf_info['post_type']}\n\n")
                f.write(f"## インストール方法\n\n")
                f.write(f"### 方法1: PHPコードで登録\n\n")
                f.write(f"1. `{php_filename}` の内容を `functions.php` に追加\n\n")
                f.write(f"### 方法2: WP-CLI経由\n\n")
                f.write(f"```bash\nwp acf import {json_filename}\n```\n\n")
            
            output_files.append({
                'type': 'README',
                'path': readme_path
            })
            logger.info(f"README保存: {readme_filename}")
            
            return output_files
            
        except Exception as e:
            logger.error(f"ファイル保存エラー: {e}")
            return output_files
    
    # =========================================================================
    # パート7: コード抽出ヘルパー
    # =========================================================================
    
    def _extract_php_code(self, text: str) -> Optional[str]:
        """PHPコードを抽出"""
        php_pattern = r'```php\s*(.*?)```'
        matches = re.findall(php_pattern, text, re.DOTALL)
        
        if matches:
            longest_code = max(matches, key=len)
            longest_code = re.sub(r'^\s*<\?php\s*', '', longest_code)
            return longest_code.strip()
        
        return None
    
    def _extract_json_from_text(self, text: str) -> Optional[Dict]:
        """JSON定義を抽出"""
        json_pattern = r'```json\s*(.*?)```'
        matches = re.findall(json_pattern, text, re.DOTALL)
        
        if matches:
            try:
                return json.loads(matches[0])
            except json.JSONDecodeError:
                return None
        
        return None
    
    # =========================================================================
    # パート8: サマリー作成
    # =========================================================================
    
    def _create_acf_summary(self, acf_info: Dict, output_files: list, 
                           validation_result: Dict) -> str:
        """ACFタスクのサマリーを作成"""
        summary = f"""✅ ACFフィールドグループ作成完了

【フィールドグループ情報】
- タイトル: {acf_info['group_title']}
- 投稿タイプ: {acf_info['post_type']}
- フィールド数: {acf_info['field_count']}

【生成ファイル】
"""
        for file_info in output_files:
            summary += f"- {file_info['type']}: {file_info['path'].name}\n"
        
        if not validation_result['is_valid']:
            summary += f"\n【検証結果】\n"
            for issue in validation_result['issues']:
                summary += f"⚠️ {issue}\n"
        
        return summary