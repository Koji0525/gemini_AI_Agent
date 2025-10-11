# dev_agent.py
"""開発AI - コード生成とテストコード、WordPress専用機能の作成"""
import asyncio
import logging
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime
import re
import json

from config_utils import ErrorHandler, PathManager
from browser_controller import BrowserController

logger = logging.getLogger(__name__)

class DevAgent:
    """開発AI - コード生成とテストコード、WordPress専用機能の作成"""
    
    DEV_SYSTEM_PROMPT = """あなたは経験豊富なソフトウェアエンジニアです。

【あなたの役割】
- 高品質なコードの実装
- テストコードの作成
- エラーハンドリングの実装
- コメントとドキュメントの作成

【コーディング原則】
1. 可読性の高いコードを書く
2. セキュリティを考慮する
3. エラーハンドリングを適切に行う
4. テスト可能な設計にする
5. 最新のベストプラクティスに従う

【出力形式】
以下の形式でコードを出力してください：

## タスク概要
（タスクの理解）

## 実装内容
（実装の説明）

## コード
```python
# または他の言語
# 完全に動作するコード
```

## テストコード
```python
# 単体テストまたは統合テスト
```

## 使用方法
（コードの使い方）

## 注意事項
（実装時の注意点や制約）"""

    WORDPRESS_CPT_PROMPT = """あなたはWordPress開発の専門家です。

【WordPress カスタム投稿タイプ作成の専門家】

以下の要件に基づいて、完全に動作するWordPressカスタム投稿タイプのPHPコードを生成してください。

【必須要素】
1. register_post_type() 関数を使用
2. 適切なラベル（labels）の定義
3. サポート機能（supports）の指定
4. 管理画面での表示設定
5. REST API対応
6. リライトルール
7. アーカイブページの有効化

【出力形式】
以下の形式で出力してください：

## カスタム投稿タイプ: {post_type_slug}

### 概要
（このカスタム投稿タイプの説明）

### functions.php に追加するコード

```php
<?php
/**
 * カスタム投稿タイプ: {post_type_slug}
 * 
 * @package WordPress
 * @since 1.0.0
 */

// カスタム投稿タイプの登録
function register_cpt_{post_type_slug}() {{
    $labels = array(
        'name'                  => _x( '{plural_name}', 'Post Type General Name', 'textdomain' ),
        'singular_name'         => _x( '{singular_name}', 'Post Type Singular Name', 'textdomain' ),
        'menu_name'             => __( '{menu_name}', 'textdomain' ),
        'name_admin_bar'        => __( '{singular_name}', 'textdomain' ),
        'archives'              => __( '{plural_name} アーカイブ', 'textdomain' ),
        'attributes'            => __( '{singular_name} 属性', 'textdomain' ),
        'parent_item_colon'     => __( '親 {singular_name}:', 'textdomain' ),
        'all_items'             => __( 'すべての {plural_name}', 'textdomain' ),
        'add_new_item'          => __( '新規 {singular_name} を追加', 'textdomain' ),
        'add_new'               => __( '新規追加', 'textdomain' ),
        'new_item'              => __( '新規 {singular_name}', 'textdomain' ),
        'edit_item'             => __( '{singular_name} を編集', 'textdomain' ),
        'update_item'           => __( '{singular_name} を更新', 'textdomain' ),
        'view_item'             => __( '{singular_name} を表示', 'textdomain' ),
        'view_items'            => __( '{plural_name} を表示', 'textdomain' ),
        'search_items'          => __( '{plural_name} を検索', 'textdomain' ),
        'not_found'             => __( '見つかりません', 'textdomain' ),
        'not_found_in_trash'    => __( 'ゴミ箱にありません', 'textdomain' ),
        'featured_image'        => __( 'アイキャッチ画像', 'textdomain' ),
        'set_featured_image'    => __( 'アイキャッチ画像を設定', 'textdomain' ),
        'remove_featured_image' => __( 'アイキャッチ画像を削除', 'textdomain' ),
        'use_featured_image'    => __( 'アイキャッチ画像として使用', 'textdomain' ),
        'insert_into_item'      => __( '{singular_name} に挿入', 'textdomain' ),
        'uploaded_to_this_item' => __( 'この {singular_name} にアップロード', 'textdomain' ),
        'items_list'            => __( '{plural_name} リスト', 'textdomain' ),
        'items_list_navigation' => __( '{plural_name} リストナビゲーション', 'textdomain' ),
        'filter_items_list'     => __( '{plural_name} リストをフィルタ', 'textdomain' ),
    );
    
    $args = array(
        'label'                 => __( '{singular_name}', 'textdomain' ),
        'description'           => __( '{description}', 'textdomain' ),
        'labels'                => $labels,
        'supports'              => array( {supports} ),
        'taxonomies'            => array( {taxonomies} ),
        'hierarchical'          => {hierarchical},
        'public'                => true,
        'show_ui'               => true,
        'show_in_menu'          => true,
        'menu_position'         => 5,
        'menu_icon'             => '{menu_icon}',
        'show_in_admin_bar'     => true,
        'show_in_nav_menus'     => true,
        'can_export'            => true,
        'has_archive'           => true,
        'exclude_from_search'   => false,
        'publicly_queryable'    => true,
        'capability_type'       => 'post',
        'show_in_rest'          => true,
        'rest_base'             => '{rest_base}',
        'rest_controller_class' => 'WP_REST_Posts_Controller',
        'rewrite'               => array(
            'slug'       => '{slug}',
            'with_front' => false,
        ),
    );
    
    register_post_type( '{post_type_slug}', $args );
}}
add_action( 'init', 'register_cpt_{post_type_slug}', 0 );
?>
```

### 関連するカスタムタクソノミー（必要に応じて）

```php
<?php
// カスタムタクソノミーをここに追加
?>
```

### テンプレートファイル

#### single-{post_type_slug}.php
```php
<?php
// 単一投稿表示用テンプレート
?>
```

#### archive-{post_type_slug}.php
```php
<?php
// アーカイブ表示用テンプレート
?>
```

### 使用方法

1. 上記のコードを `functions.php` または専用のプラグインファイルに追加
2. WordPressの管理画面にアクセス
3. 左メニューに「{menu_name}」が表示されることを確認
4. パーマリンク設定を保存（設定 > パーマリンク設定）

### 注意事項

- カスタム投稿タイプのスラッグは20文字以内にしてください
- 予約語（post, page, attachmentなど）は使用できません
- プラグインとして実装する場合は、適切なヘッダー情報を追加してください
- テーマの functions.php に追加する場合は、子テーマを使用することを推奨します
"""

    def __init__(self, browser: BrowserController, output_folder: Path = None):
        self.browser = browser
        # 出力フォルダが指定されていない場合はB14から取得
        if output_folder is None:
            from config_utils import config
            if config.AGENT_OUTPUT_FOLDER:
                self.output_folder = PathManager.get_safe_path(config.AGENT_OUTPUT_FOLDER)
                logger.info(f"Agent出力先（B14から取得）: {self.output_folder}")
            else:
                # フォールバック: デフォルトパス
                self.output_folder = Path.home() / "Documents" / "gemini_auto_generate" / "agent_outputs"
                self.output_folder.mkdir(exist_ok=True, parents=True)
                logger.warning(f"B14が空のため、デフォルトフォルダを使用: {self.output_folder}")
        else:
            self.output_folder = output_folder
        
        self.design_docs = {}  # 設計書を参照できるようにする
        
    
    
    async def process_task(self, task: Dict) -> Dict:
        """開発タスクを処理（WordPress対応強化版）"""
        try:
            logger.info(f"開発AI: タスク処理開始 - {task['description']}")
            
            # WordPress カスタム投稿タイプ作成タスクか判定
            if self._is_wordpress_cpt_task(task):
                return await self._process_wordpress_cpt_task(task)
            
            # WordPress タクソノミー作成タスクか判定
            if self._is_wordpress_taxonomy_task(task):
                return await self._process_wordpress_taxonomy_task(task)
            
            # 通常の開発タスク
            return await self._process_general_task(task)
            
        except Exception as e:
            ErrorHandler.log_error(e, "開発AI処理")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _is_wordpress_cpt_task(self, task: Dict) -> bool:
        """WordPressカスタム投稿タイプ作成タスクか判定"""
        description = task.get('description', '').lower()
        keywords = [
            'custom post type',
            'カスタム投稿タイプ',
            'cpt',
            'register_post_type',
            '投稿タイプ'
        ]
        return any(kw in description for kw in keywords)
    
    def _is_wordpress_taxonomy_task(self, task: Dict) -> bool:
        """WordPressタクソノミー作成タスクか判定"""
        description = task.get('description', '').lower()
        keywords = [
            'taxonomy',
            'タクソノミー',
            'カスタム分類',
            'register_taxonomy'
        ]
        return any(kw in description for kw in keywords)
    
    async def _process_wordpress_cpt_task(self, task: Dict) -> Dict:
        """WordPressカスタム投稿タイプ作成タスクを処理"""
        try:
            logger.info("="*60)
            logger.info("WordPress カスタム投稿タイプ作成タスク")
            logger.info("="*60)
            
            # タスクから情報を抽出
            cpt_info = self._extract_cpt_info(task)
            
            logger.info(f"投稿タイプスラッグ: {cpt_info['slug']}")
            logger.info(f"表示名（単数）: {cpt_info['singular_name']}")
            logger.info(f"表示名（複数）: {cpt_info['plural_name']}")
            
            # プロンプトを構築
            full_prompt = self._build_wordpress_cpt_prompt(task, cpt_info)
            
            # Geminiに送信
            logger.info("Geminiに要件定義書作成タスクを送信中...")
            await self.browser.send_prompt(full_prompt)
    
            # 応答待機（要件定義書は長いので300秒）
            logger.info("⏱️ 待機時間: 300秒（要件定義書作成）")
    
            # ここが修正箇所！
            success = await self.browser._wait_for_generation_complete()  # ← この行を修正
            # 修正後:
            # success = await self.browser.wait_for_text_generation(max_wait=300)
    
            if not success:
                return {
                    'success': False,
                    'error': '開発AI: タイムアウト（要件定義書作成: 300秒）'
                }
            
            # 応答を取得
            response_text = await self.browser.extract_latest_text_response()
            
            if not response_text:
                return {
                    'success': False,
                    'error': '開発AI: 応答取得失敗'
                }
            
            logger.info(f"開発AI: 応答取得完了（{len(response_text)}文字）")
            
            # 結果を保存
            output_files = self._save_wordpress_cpt_code(response_text, task, cpt_info)
            
            # サマリーを作成
            summary = f"""✅ WordPressカスタム投稿タイプ作成完了

【投稿タイプ情報】
- スラッグ: {cpt_info['slug']}
- 表示名: {cpt_info['singular_name']} / {cpt_info['plural_name']}
- サポート機能: {', '.join(cpt_info['supports'])}

【生成ファイル】
"""
            for file_info in output_files:
                summary += f"- {file_info['type']}: {file_info['path'].name}\n"
            
            summary += f"\n【次のステップ】\n"
            summary += f"1. functions.php または専用プラグインに追加\n"
            summary += f"2. パーマリンク設定を保存（設定 > パーマリンク設定）\n"
            summary += f"3. 管理画面で「{cpt_info['menu_name']}」メニューを確認\n"
            
            return {
                'success': True,
                'output_files': output_files,
                'summary': summary,
                'full_text': response_text,
                'cpt_slug': cpt_info['slug']
            }
            
        except Exception as e:
            ErrorHandler.log_error(e, "WordPressカスタム投稿タイプ作成")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _extract_cpt_info(self, task: Dict) -> Dict:
        """タスクからカスタム投稿タイプの情報を抽出"""
        description = task.get('description', '')
        parameters = task.get('parameters', {})
        
        # parametersから取得（最優先）
        if isinstance(parameters, str):
            try:
                parameters = json.loads(parameters)
            except:
                parameters = {}
        
        # デフォルト値
        cpt_info = {
            'slug': parameters.get('cpt_slug', 'ma_case'),
            'singular_name': parameters.get('singular_name', 'M&A案件'),
            'plural_name': parameters.get('plural_name', 'M&A案件一覧'),
            'menu_name': parameters.get('menu_name', 'M&A案件'),
            'description': parameters.get('description', 'M&A案件の管理'),
            'supports': parameters.get('supports', ['title', 'editor', 'thumbnail', 'custom-fields']),
            'taxonomies': parameters.get('taxonomies', []),
            'hierarchical': parameters.get('hierarchical', False),
            'menu_icon': parameters.get('menu_icon', 'dashicons-portfolio'),
            'rest_base': parameters.get('rest_base', None),
        }
        
        # rest_base が未設定の場合はslugを使用
        if not cpt_info['rest_base']:
            cpt_info['rest_base'] = cpt_info['slug']
        
        # descriptionから情報を抽出（フォールバック）
        if 'ma_case' in description.lower() or 'm&a' in description.lower():
            cpt_info['slug'] = 'ma_case'
            cpt_info['singular_name'] = 'M&A案件'
            cpt_info['plural_name'] = 'M&A案件一覧'
            cpt_info['menu_name'] = 'M&A案件'
            cpt_info['description'] = 'M&A案件の管理'
            cpt_info['menu_icon'] = 'dashicons-portfolio'
        
        return cpt_info
    
    def _build_wordpress_cpt_prompt(self, task: Dict, cpt_info: Dict) -> str:
        """WordPressカスタム投稿タイプ用のプロンプトを構築"""
        supports_str = "'" + "', '".join(cpt_info['supports']) + "'"
        taxonomies_str = "'" + "', '".join(cpt_info['taxonomies']) + "'" if cpt_info['taxonomies'] else ""
        hierarchical_str = 'true' if cpt_info['hierarchical'] else 'false'
        
        prompt = self.WORDPRESS_CPT_PROMPT.format(
            post_type_slug=cpt_info['slug'],
            singular_name=cpt_info['singular_name'],
            plural_name=cpt_info['plural_name'],
            menu_name=cpt_info['menu_name'],
            description=cpt_info['description'],
            supports=supports_str,
            taxonomies=taxonomies_str,
            hierarchical=hierarchical_str,
            menu_icon=cpt_info['menu_icon'],
            rest_base=cpt_info['rest_base'],
            slug=cpt_info['slug']
        )
        
        prompt += f"""

【追加の要件】
{task.get('description', '')}

【注意事項】
- 完全に動作する実装可能なコードを生成してください
- すべての必須要素を含めてください
- 日本語のラベルを適切に設定してください
- コメントを含めて可読性を高めてください
- ベストプラクティスに従ってください

上記の要件に基づいて、完全なカスタム投稿タイプのコードを生成してください。
"""
        
        return prompt
    
    def _save_wordpress_cpt_code(self, text: str, task: Dict, cpt_info: Dict) -> list:
        """WordPressカスタム投稿タイプのコードを保存"""
        output_files = []
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        try:
            # 1. 完全なドキュメントを保存
            doc_filename = f"cpt_{cpt_info['slug']}_{timestamp}.md"
            doc_path = self.output_folder / doc_filename
            
            with open(doc_path, 'w', encoding='utf-8') as f:
                f.write(f"# カスタム投稿タイプ: {cpt_info['slug']}\n\n")
                f.write(f"タスクID: {task['task_id']}\n")
                f.write(f"作成日時: {datetime.now().isoformat()}\n\n")
                f.write("---\n\n")
                f.write(text)
            
            output_files.append({
                'type': 'ドキュメント',
                'path': doc_path
            })
            logger.info(f"ドキュメント保存: {doc_filename}")
            
            # 2. PHPコードを抽出して保存
            php_code = self._extract_php_code(text)
            if php_code:
                php_filename = f"cpt_{cpt_info['slug']}_{timestamp}.php"
                php_path = self.output_folder / php_filename
                
                with open(php_path, 'w', encoding='utf-8') as f:
                    f.write("<?php\n")
                    f.write(f"/**\n")
                    f.write(f" * カスタム投稿タイプ: {cpt_info['singular_name']}\n")
                    f.write(f" * スラッグ: {cpt_info['slug']}\n")
                    f.write(f" * \n")
                    f.write(f" * @package WordPress\n")
                    f.write(f" * @since 1.0.0\n")
                    f.write(f" * @generated {datetime.now().isoformat()}\n")
                    f.write(f" */\n\n")
                    f.write(php_code)
                
                output_files.append({
                    'type': 'PHPコード',
                    'path': php_path
                })
                logger.info(f"PHPコード保存: {php_filename}")
            
            # 3. インストール手順を保存
            readme_filename = f"README_cpt_{cpt_info['slug']}_{timestamp}.md"
            readme_path = self.output_folder / readme_filename
            
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(f"# {cpt_info['singular_name']} カスタム投稿タイプ\n\n")
                f.write(f"## 概要\n\n")
                f.write(f"{cpt_info['description']}\n\n")
                f.write(f"## インストール方法\n\n")
                f.write(f"### 方法1: functions.php に追加\n\n")
                f.write(f"1. `{php_filename}` の内容をコピー\n")
                f.write(f"2. テーマの `functions.php`（子テーマ推奨）に貼り付け\n")
                f.write(f"3. WordPressを再読み込み\n\n")
                f.write(f"### 方法2: プラグインとして実装\n\n")
                f.write(f"1. `wp-content/plugins/cpt-{cpt_info['slug']}/` フォルダを作成\n")
                f.write(f"2. プラグインヘッダーを追加した `{php_filename}` を配置\n")
                f.write(f"3. 管理画面でプラグインを有効化\n\n")
                f.write(f"## 使用方法\n\n")
                f.write(f"1. WordPress管理画面にログイン\n")
                f.write(f"2. 左メニューに「{cpt_info['menu_name']}」が表示されることを確認\n")
                f.write(f"3. 「設定 > パーマリンク設定」を開いて保存（リライトルール更新）\n")
                f.write(f"4. 新しい{cpt_info['singular_name']}を作成\n\n")
                f.write(f"## 仕様\n\n")
                f.write(f"- **スラッグ**: `{cpt_info['slug']}`\n")
                f.write(f"- **サポート機能**: {', '.join(cpt_info['supports'])}\n")
                f.write(f"- **REST API**: 有効\n")
                f.write(f"- **アーカイブページ**: 有効\n")
                f.write(f"- **階層構造**: {'有効' if cpt_info['hierarchical'] else '無効'}\n\n")
            
            output_files.append({
                'type': 'README',
                'path': readme_path
            })
            logger.info(f"README保存: {readme_filename}")
            
            return output_files
            
        except Exception as e:
            logger.error(f"コード保存エラー: {e}")
            return output_files
    
    def _extract_php_code(self, text: str) -> Optional[str]:
        """テキストからPHPコードを抽出"""
        try:
            # ```php ... ``` パターンを探す
            php_pattern = r'```php\s*(.*?)```'
            matches = re.findall(php_pattern, text, re.DOTALL)
            
            if matches:
                # 最も長いコードブロックを返す
                longest_code = max(matches, key=len)
                # 先頭の <?php を削除（後で追加するため）
                longest_code = re.sub(r'^\s*<\?php\s*', '', longest_code)
                return longest_code.strip()
            
            return None
            
        except Exception as e:
            logger.warning(f"PHPコード抽出エラー: {e}")
            return None
    
    async def _process_wordpress_taxonomy_task(self, task: Dict) -> Dict:
        """WordPressタクソノミー作成タスクを処理"""
        # タクソノミー作成用の処理（今後実装）
        logger.warning("タクソノミー作成タスクは現在未実装です")
        return await self._process_general_task(task)
    
    async def _process_general_task(self, task: Dict) -> Dict:
        """通常の開発タスクを処理"""
        try:
            logger.info("通常の開発タスクとして処理")
            
            # 対応する設計書があれば読み込む
            design_context = self._load_design_context(task)
            
            # プロンプトを構築
            full_prompt = f"""{self.DEV_SYSTEM_PROMPT}

【タスク】
{task['description']}"""
            
            if design_context:
                full_prompt += f"""

【設計書（参考）】
{design_context}"""
            
            full_prompt += """

上記のタスクについて、完全に動作するコードを実装してください。
エラーハンドリングとコメントを含めてください。"""
            
            # Geminiに送信
            logger.info("Geminiに開発タスクを送信中...")
            await self.browser.send_prompt(full_prompt)
            
            success = await self.browser._wait_for_generation_complete()
            
            # タスクの種類によって待機時間を調整
            description = task.get('description', '').lower()
        
            if any(word in description for word in ['要件定義', '設計書', 'アーキテクチャ', '仕様書']):
                max_wait = 300  # 要件定義書などは5分
                logger.info("📋 要件定義・設計書タスク - 待機時間を300秒に延長")
            else:
                max_wait = 180  # 通常は3分
        
            # 応答待機
            success = await self.browser.wait_for_text_generation(max_wait=max_wait)

            
            if not success:
                return {
                    'success': False,
                    'error': '開発AI: タイムアウト'
                }
            
            # 応答を取得
            response_text = await self.browser.extract_latest_text_response()
            
            if not response_text:
                return {
                    'success': False,
                    'error': '開発AI: 応答取得失敗'
                }
            
            logger.info(f"開発AI: 応答取得完了（{len(response_text)}文字）")
            
            # コードをファイルに保存
            filename = f"code_{task['task_id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            output_path = self.output_folder / filename
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(f"# コード: {task['description']}\n\n")
                f.write(f"タスクID: {task['task_id']}\n")
                f.write(f"作成日時: {datetime.now().isoformat()}\n\n")
                f.write("---\n\n")
                f.write(response_text)
            
            logger.info(f"コードを保存: {output_path}")
            
            # コード部分を抽出して個別ファイルに保存
            self._extract_and_save_code(response_text, task)
            
            # サマリーを作成
            summary = response_text[:500] + "..." if len(response_text) > 500 else response_text
            
            return {
                'success': True,
                'output_file': str(output_path),
                'summary': summary,
                'full_text': response_text
            }
            
        except Exception as e:
            ErrorHandler.log_error(e, "開発AI処理")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _load_design_context(self, task: Dict) -> str:
        """対応する設計書があれば読み込む"""
        try:
            # design_*.md ファイルを探す
            design_files = list(self.output_folder.glob(f"design_{task['task_id']}_*.md"))
            
            if design_files:
                # 最新のファイルを読み込む
                latest_design = sorted(design_files)[-1]
                with open(latest_design, 'r', encoding='utf-8') as f:
                    content = f.read()
                logger.info(f"設計書を読み込みました: {latest_design.name}")
                return content[:2000]  # 最初の2000文字のみ
            
            return ""
        except Exception as e:
            logger.warning(f"設計書読み込みエラー: {e}")
            return ""
    
    def _extract_and_save_code(self, text: str, task: Dict):
        """コードブロックを抽出して個別ファイルに保存"""
        try:
            # ```言語 ... ``` パターンを抽出
            code_blocks = re.findall(r'```(\w+)\n(.*?)```', text, re.DOTALL)
            
            for i, (lang, code) in enumerate(code_blocks):
                # ファイル拡張子を決定
                ext_map = {
                    'python': '.py',
                    'javascript': '.js',
                    'typescript': '.ts',
                    'html': '.html',
                    'css': '.css',
                    'java': '.java',
                    'cpp': '.cpp',
                    'c': '.c',
                    'php': '.php',
                    'ruby': '.rb',
                    'go': '.go',
                    'rust': '.rs',
                }
                ext = ext_map.get(lang.lower(), '.txt')
                
                # ファイルに保存
                code_filename = f"code_{task['task_id']}_{i+1}{ext}"
                code_path = self.output_folder / code_filename
                
                with open(code_path, 'w', encoding='utf-8') as f:
                    f.write(code)
                
                logger.info(f"コードファイルを保存: {code_filename}")
                
        except Exception as e:
            logger.warning(f"コード抽出エラー: {e}")