"""
WordPress専用要件定義書生成機能を追加した wp_dev.py
"""

# ... 既存のインポート ...
import asyncio
import logging
from pathlib import Path
from typing import Dict, Optional, List
from datetime import datetime
import re
import json

from config_utils import ErrorHandler, PathManager
from browser_controller import BrowserController

logger = logging.getLogger(__name__)


class DevAgent:
    """開発AI - WordPress要件定義書対応版"""
    
    # ... 既存のプロンプトは省略 ...
    
    WORDPRESS_REQUIREMENTS_PROMPT = """あなたはWordPress開発の専門家で、要件定義のプロフェッショナルです。

【あなたの役割】
ウズベキスタンのM&Aポータルサイトの要件定義書を作成してください。

【プロジェクト情報】
- **サイト名**: ウズベキスタンM&Aポータル
- **目的**: M&A案件情報の多言語発信と企業マッチング
- **WordPressテーマ**: Cocoon（日本製の無料高機能テーマ）
- **多言語プラグイン**: Polylang
- **対応言語**: 日本語、英語、ロシア語、ウズベク語、中国語、韓国語、トルコ語（7言語）

【Cocoonテーマの特徴を活かす】
1. **高速表示**: キャッシュ最適化、画像遅延読み込み
2. **SEO最適化**: 構造化データ、パンくずリスト
3. **モバイル対応**: レスポンシブデザイン
4. **広告管理**: アドセンス対応
5. **カスタマイズ性**: 豊富なスキン、ウィジェット

【Polylang多言語対応の要件】
1. **言語切り替え**: ヘッダーに言語スイッチャー
2. **URL構造**: 言語コード付きURL（例: /en/ma-cases/、/ru/ma-cases/）
3. **翻訳管理**: 
   - 投稿・固定ページの翻訳
   - カスタム投稿タイプの翻訳
   - タクソノミーの翻訳
   - メニューの翻訳
4. **言語別設定**: 各言語ごとのSEO設定

【要件定義書の構成】
必ず以下の構造で出力してください：

# 1.0 プロジェクト概要
## 1.1 プロジェクト名
## 1.2 目的・背景
## 1.3 対象ユーザー
## 1.4 成功指標（KPI）

# 2.0 システム構成
## 2.1 技術スタック
- WordPress 6.4以上
- Cocoonテーマ
- Polylangプラグイン
- その他必要なプラグイン

## 2.2 サーバー要件
- PHP 8.0以上
- MySQL 8.0以上
- メモリ 512MB以上

## 2.3 開発・本番環境

# 3.0 機能要件
## 3.1 カスタム投稿タイプ
### 3.1.1 M&A案件（ma_case）
- フィールド定義
- タクソノミー
- アーカイブページ
- 単一ページテンプレート

### 3.1.2 企業情報（company）
- フィールド定義
- タクソノミー

### 3.1.3 ニュース（news）

## 3.2 カスタムタクソノミー
### 3.2.1 業種分類（industry）
### 3.2.2 地域（region）
### 3.2.3 案件タイプ（deal_type）

## 3.3 ACFカスタムフィールド
### M&A案件用フィールド
1. 基本情報
   - 企業名
   - 所在地
   - 業種
   - 資本金
   - 従業員数
   
2. 案件情報
   - 案件タイプ（売却/買収/提携）
   - 希望価格
   - 交渉状況
   - 公開状態
   
3. 連絡先情報
   - 担当者名
   - メールアドレス
   - 電話番号

## 3.4 検索・フィルター機能（FacetWP）
- 業種別検索
- 地域別検索
- 価格帯検索
- 案件タイプ検索
- キーワード検索（Relevanssi）

## 3.5 多言語機能（Polylang）
### 3.5.1 言語設定
- デフォルト言語: 日本語
- 翻訳言語: 英語、ロシア語、ウズベク語、中国語、韓国語、トルコ語

### 3.5.2 翻訳対象
- すべての投稿タイプ
- すべてのタクソノミー
- カスタムフィールドラベル
- メニュー
- ウィジェット

### 3.5.3 URL構造
```
日本語: https://example.com/ma-cases/
英語: https://example.com/en/ma-cases/
ロシア語: https://example.com/ru/ma-cases/
ウズベク語: https://example.com/uz/ma-cases/
中国語: https://example.com/zh/ma-cases/
韓国語: https://example.com/ko/ma-cases/
トルコ語: https://example.com/tr/ma-cases/
```

## 3.6 ユーザー管理・権限
### 3.6.1 ユーザーロール
- 管理者: すべての権限
- 編集者: 案件管理、企業情報管理
- 投稿者: 案件投稿のみ
- 購読者: 閲覧のみ

### 3.6.2 会員機能（オプション）
- 会員登録
- ログイン
- 案件お気に入り
- 問い合わせ履歴

## 3.7 問い合わせ機能
- Contact Form 7
- 多言語対応
- 自動返信メール
- 管理者通知

## 3.8 SEO対策
### 3.8.1 基本設定
- タイトルタグ最適化
- メタディスクリプション
- OGPタグ設定
- 構造化データ

### 3.8.2 Cocoon SEO機能活用
- パンくずリスト
- カテゴリ・タグ説明文
- 目次自動生成

## 3.9 セキュリティ
- Wordfence Security
- ログイン試行回数制限
- 2段階認証
- SSL/HTTPS化
- バックアップ（UpdraftPlus）

## 3.10 パフォーマンス最適化
- WP Rocket（キャッシュ）
- 画像最適化（EWWW Image Optimizer）
- CDN設定（Cloudflare）
- Cocoonの高速化機能活用

# 4.0 非機能要件
## 4.1 パフォーマンス
- ページ読み込み時間: 3秒以内
- モバイル PageSpeed Insights: 80点以上

## 4.2 可用性
- サーバー稼働率: 99.9%以上
- バックアップ: 1日1回自動

## 4.3 セキュリティ
- SSL/TLS 1.3
- 定期的なプラグイン更新
- 脆弱性スキャン

## 4.4 互換性
- ブラウザ: Chrome, Firefox, Safari, Edge（最新版）
- デバイス: PC, タブレット, スマートフォン

# 5.0 画面設計
## 5.1 トップページ
- ヘッダー（言語スイッチャー、メニュー）
- メインビジュアル
- 注目案件一覧
- 新着ニュース
- フッター

## 5.2 M&A案件一覧ページ
- 検索フィルター（左サイドバー）
- 案件カード一覧
- ページネーション

## 5.3 M&A案件詳細ページ
- 案件情報
- 企業情報
- 問い合わせフォーム
- 関連案件

## 5.4 企業情報ページ
- 企業概要
- 保有案件一覧

## 5.5 言語別ページ
- 各言語で同じ構成
- 右書き言語対応（アラビア語など将来対応）

# 6.0 データ構造
## 6.1 カスタム投稿タイプ定義（JSON形式）
```json
{
  "ma_case": {
    "labels": {
      "ja": "M&A案件",
      "en": "M&A Cases",
      "ru": "Сделки M&A",
      "uz": "M&A bitimlar",
      "zh": "并购案例",
      "ko": "인수합병 사례",
      "tr": "Birleşme ve Devralma Vakaları"
    },
    "supports": ["title", "editor", "thumbnail", "custom-fields", "excerpt"],
    "taxonomies": ["industry", "region", "deal_type"],
    "has_archive": true,
    "public": true,
    "show_in_rest": true
  }
}
```

## 6.2 ACFフィールドグループ定義

## 6.3 タクソノミー定義

# 7.0 実装計画
## 7.1 フェーズ1: 基本構築（1-2週間）
- WordPress + Cocoon インストール
- Polylang設定
- カスタム投稿タイプ作成
- ACFフィールド作成

## 7.2 フェーズ2: 機能実装（2-3週間）
- 検索機能（FacetWP）
- 問い合わせフォーム
- ユーザー管理

## 7.3 フェーズ3: コンテンツ登録（1週間）
- サンプル案件登録
- 各言語への翻訳

## 7.4 フェーズ4: テスト・調整（1週間）
- 多言語表示確認
- 検索動作確認
- パフォーマンステスト

## 7.5 フェーズ5: 本番公開（1週間）
- DNS設定
- SSL証明書
- 本番環境移行

# 8.0 運用保守
## 8.1 定期作業
- WordPress/プラグイン更新（月1回）
- バックアップ確認（週1回）
- セキュリティスキャン（週1回）

## 8.2 監視項目
- サーバー稼働率
- ページ表示速度
- エラーログ

## 8.3 サポート体制
- 平日9:00-18:00サポート
- 緊急時対応

# 9.0 コスト見積もり
## 9.1 初期費用
- サーバー費用
- ドメイン費用
- 有料プラグインライセンス
- 開発費用

## 9.2 月額費用
- サーバー費用
- プラグインライセンス更新
- 保守費用

# 10.0 リスクと対策
## 10.1 技術的リスク
- Polylangの制限事項
- Cocoonとプラグインの互換性

## 10.2 運用リスク
- 多言語コンテンツの管理負荷
- 翻訳品質の確保

## 10.3 対策
- 翻訳ワークフローの確立
- プラグイン選定の慎重な検討

---

【出力形式】
上記の構成に従って、**完全で詳細な要件定義書**を生成してください。
- すべてのセクションを埋めること
- 具体的な仕様を記載すること
- JSON形式のデータ構造を含めること
- 実装可能なレベルの詳細度で記述すること

【重要】
- 出力は20,000文字以上の詳細な要件定義書にすること
- コードブロックは完全に閉じること（```で開始・終了）
- すべての章立てを網羅すること
- Cocoonテーマの機能を最大限活用すること
- Polylangの多言語対応を徹底すること
"""

    def __init__(self, browser: BrowserController, output_folder: Path = None):

        self.browser = browser
        
        if output_folder is None:
            from config_utils import config
            if config.AGENT_OUTPUT_FOLDER:
                self.output_folder = PathManager.get_safe_path(config.AGENT_OUTPUT_FOLDER)
                logger.info(f"Agent出力先（B14から取得）: {self.output_folder}")
            else:
                self.output_folder = Path.home() / "Documents" / "gemini_auto_generate" / "agent_outputs"
                self.output_folder.mkdir(exist_ok=True, parents=True)
                logger.warning(f"B14が空のため、デフォルトフォルダを使用: {self.output_folder}")
        else:
            self.output_folder = output_folder
        
        self.design_docs = {}
    
    async def process_task(self, task: Dict) -> Dict:
        """開発タスクを処理（WordPress要件定義対応強化版）"""
        try:
            logger.info(f"開発AI: タスク処理開始 - {task['description']}")
            
            # === パート1: タスク種別判定 ===
            # WordPress要件定義タスクか判定
            if self._is_wordpress_requirements_task(task):
                return await self._process_wordpress_requirements_task(task)
            
            # WordPress カスタム投稿タイプ作成タスクか判定
            if self._is_wordpress_cpt_task(task):
                return await self._process_wordpress_cpt_task(task)
            
            # === パート2: 通常タスク処理 ===
            # 通常の開発タスク
            return await self._process_general_task(task)
            
        except Exception as e:
            ErrorHandler.log_error(e, "開発AI処理")
            return {
                'success': False,
                'error': str(e)
            }
    
    # wordpress/wp_dev.py の WordPressDevAgent クラス内に追加

    async def process_ma_case_cpt_task(self, task: Dict) -> Dict:
        """M&A案件カスタム投稿タイプ作成タスクを専用処理"""
        try:
            logger.info("🎯 M&A案件CPT作成タスクを専用処理")
        
            # === パート1: CPT定義の生成 ===
            cpt_definition = await self._generate_ma_case_cpt_definition(task)
            if not cpt_definition.get('success'):
                return cpt_definition
        
            # === パート2: PHPコードの生成 ===
            php_code = await self._generate_cpt_php_code(cpt_definition['definition'])
            if not php_code.get('success'):
                return php_code
        
            # === パート3: コードのデプロイ ===
            deploy_result = await self._deploy_cpt_code(php_code['php_code'], task)
            if not deploy_result.get('success'):
                return deploy_result
        
            # === パート4: デプロイ後の検証 ===
            verification_result = await self._verify_cpt_deployment('ma_case')
            if not verification_result.get('success'):
                return verification_result
        
            # === パート5: 結果の統合と返却 ===
            return {
                'success': True,
                'summary': f"✅ M&A案件カスタム投稿タイプ作成完了\n\n" \
                          f"スラッグ: ma_case\n" \
                          f"表示名: M&A案件 / M&A案件一覧\n" \
                          f"デプロイ先: {deploy_result.get('deploy_path', 'N/A')}\n" \
                          f"検証結果: {verification_result.get('verification_message', 'N/A')}",
                'full_text': f"CPT定義: {cpt_definition['definition']}\n\nPHPコード:\n{php_code['php_code']}",
                'cpt_slug': 'ma_case',
                'deploy_info': deploy_result,
                'verification_info': verification_result
            }
        
        except Exception as e:
            ErrorHandler.log_error(e, "M&A案件CPT作成タスク")
            return {
                'success': False,
                'error': f'M&A案件CPT作成エラー: {str(e)}'
            }

    async def _generate_ma_case_cpt_definition(self, task: Dict) -> Dict:
        """M&A案件CPTの構造化定義を生成"""
        try:
            logger.info("📝 M&A案件CPT定義を生成中...")
        
            # 構造化されたCPT定義
            cpt_definition = {
                'slug': 'ma_case',
                'labels': {
                    'name': 'M&A案件一覧',
                    'singular_name': 'M&A案件',
                    'menu_name': 'M&A案件',
                    'name_admin_bar': 'M&A案件',
                    'archives': 'M&A案件アーカイブ',
                    'attributes': 'M&A案件属性',
                    'parent_item_colon': '親M&A案件:',
                    'all_items': 'すべてのM&A案件',
                    'add_new_item': '新規M&A案件を追加',
                    'add_new': '新規追加',
                    'new_item': '新規M&A案件',
                    'edit_item': 'M&A案件を編集',
                    'update_item': 'M&A案件を更新',
                    'view_item': 'M&A案件を表示',
                    'view_items': 'M&A案件一覧を表示',
                    'search_items': 'M&A案件を検索',
                    'not_found': 'M&A案件が見つかりません',
                    'not_found_in_trash': 'ゴミ箱にM&A案件はありません'
                },
                'description': 'M&A案件の管理',
                'public': True,
                'has_archive': True,
                'show_ui': True,
                'show_in_menu': True,
                'menu_position': 5,
                'menu_icon': 'dashicons-portfolio',
                'supports': ['title', 'editor', 'thumbnail', 'custom-fields', 'excerpt'],
                'taxonomies': ['industry', 'region', 'deal_type'],
                'hierarchical': False,
                'show_in_rest': True,
                'rest_base': 'ma_cases',
                'rewrite': {
                    'slug': 'ma-cases',
                    'with_front': False
                }
            }
        
            logger.info("✅ M&A案件CPT定義生成完了")
            return {
                'success': True,
                'definition': cpt_definition
            }
        
        except Exception as e:
            ErrorHandler.log_error(e, "CPT定義生成")
            return {
                'success': False,
                'error': f'CPT定義生成エラー: {str(e)}'
            }

    async def _generate_cpt_php_code(self, cpt_definition: Dict) -> Dict:
        """CPT定義からPHPコードを生成"""
        try:
            logger.info("💻 CPT PHPコードを生成中...")
        
            php_code = f"""
    function register_cpt_ma_case() {{
        $labels = array(
            'name'                  => _x( '{cpt_definition['labels']['name']}', 'Post Type General Name', 'textdomain' ),
            'singular_name'         => _x( '{cpt_definition['labels']['singular_name']}', 'Post Type Singular Name', 'textdomain' ),
            'menu_name'             => __( '{cpt_definition['labels']['menu_name']}', 'textdomain' ),
            'name_admin_bar'        => __( '{cpt_definition['labels']['name_admin_bar']}', 'textdomain' ),
            'archives'              => __( '{cpt_definition['labels']['archives']}', 'textdomain' ),
            'attributes'            => __( '{cpt_definition['labels']['attributes']}', 'textdomain' ),
            'parent_item_colon'     => __( '{cpt_definition['labels']['parent_item_colon']}', 'textdomain' ),
            'all_items'             => __( '{cpt_definition['labels']['all_items']}', 'textdomain' ),
            'add_new_item'          => __( '{cpt_definition['labels']['add_new_item']}', 'textdomain' ),
            'add_new'               => __( '{cpt_definition['labels']['add_new']}', 'textdomain' ),
            'new_item'              => __( '{cpt_definition['labels']['new_item']}', 'textdomain' ),
            'edit_item'             => __( '{cpt_definition['labels']['edit_item']}', 'textdomain' ),
            'update_item'           => __( '{cpt_definition['labels']['update_item']}', 'textdomain' ),
            'view_item'             => __( '{cpt_definition['labels']['view_item']}', 'textdomain' ),
            'view_items'            => __( '{cpt_definition['labels']['view_items']}', 'textdomain' ),
            'search_items'          => __( '{cpt_definition['labels']['search_items']}', 'textdomain' ),
            'not_found'             => __( '{cpt_definition['labels']['not_found']}', 'textdomain' ),
            'not_found_in_trash'    => __( '{cpt_definition['labels']['not_found_in_trash']}', 'textdomain' ),
        );
    
        $args = array(
            'label'                 => __( '{cpt_definition['labels']['singular_name']}', 'textdomain' ),
            'description'           => __( '{cpt_definition['description']}', 'textdomain' ),
            'labels'                => $labels,
            'supports'              => {cpt_definition['supports']},
            'taxonomies'            => {cpt_definition['taxonomies']},
            'hierarchical'          => {str(cpt_definition['hierarchical']).lower()},
            'public'                => {str(cpt_definition['public']).lower()},
            'show_ui'               => {str(cpt_definition['show_ui']).lower()},
            'show_in_menu'          => {str(cpt_definition['show_in_menu']).lower()},
            'menu_position'         => {cpt_definition['menu_position']},
            'menu_icon'             => '{cpt_definition['menu_icon']}',
            'show_in_admin_bar'     => true,
            'show_in_nav_menus'     => true,
            'can_export'            => true,
            'has_archive'           => {str(cpt_definition['has_archive']).lower()},
            'exclude_from_search'   => false,
            'publicly_queryable'    => true,
            'capability_type'       => 'post',
            'show_in_rest'          => {str(cpt_definition['show_in_rest']).lower()},
            'rest_base'             => '{cpt_definition['rest_base']}',
            'rewrite'               => {cpt_definition['rewrite']},
        );
    
        register_post_type( '{cpt_definition['slug']}', $args );
    }}
    add_action( 'init', 'register_cpt_ma_case', 0 );
    """
        
            logger.info("✅ CPT PHPコード生成完了")
            return {
                'success': True,
                'php_code': php_code
            }
        
        except Exception as e:
            ErrorHandler.log_error(e, "PHPコード生成")
            return {
                'success': False,
                'error': f'PHPコード生成エラー: {str(e)}'
            }

    async def _deploy_cpt_code(self, php_code: str, task: Dict) -> Dict:
        """CPTコードをWordPress環境にデプロイ"""
        try:
            logger.info("🚀 CPTコードをデプロイ中...")
        
            if not hasattr(self, 'command_monitor') or not self.command_monitor:
                logger.warning("⚠️ コマンド監視エージェント未設定 - ファイル書き込みで代替")
                return await self._deploy_via_file_write(php_code, task)
        
            # === パート1: プラグインファイルの作成 ===
            plugin_dir = "/path/to/wp-content/plugins/ma-case-cpt"
            create_plugin_cmd = f"mkdir -p {plugin_dir} && cd {plugin_dir}"
        
            # === パート2: メインプラグインファイル作成 ===
            main_plugin_content = f"""<?php
    /**
     * Plugin Name: M&A案件カスタム投稿タイプ
     * Description: M&A案件管理用のカスタム投稿タイプを提供します
     * Version: 1.0.0
     * Author: AI Agent
     */
 
    {php_code}
    """
        
            # プラグインファイル作成コマンド
            create_file_cmd = f'echo {repr(main_plugin_content)} > {plugin_dir}/ma-case-cpt.php'
        
            # === パート3: コマンド実行 ===
            result = await self.command_monitor.execute_command(
                f"{create_plugin_cmd} && {create_file_cmd}"
            )
        
            if result.get('has_errors'):
                logger.error("❌ CPTデプロイ失敗")
                return {
                    'success': False,
                    'error': f'デプロイコマンドエラー: {result.get("errors", [])}'
                }
        
            # === パート4: プラグイン有効化 ===
            activate_cmd = "wp plugin activate ma-case-cpt"
            activate_result = await self.command_monitor.execute_command(activate_cmd)
        
            if activate_result.get('has_errors'):
                logger.warning("⚠️ プラグイン有効化に問題があります")
        
            logger.info("✅ CPTコードデプロイ完了")
            return {
                'success': True,
                'deploy_path': f"{plugin_dir}/ma-case-cpt.php",
                'command_results': [result, activate_result]
            }
        
        except Exception as e:
            ErrorHandler.log_error(e, "CPTコードデプロイ")
            return {
                'success': False,
                'error': f'デプロイエラー: {str(e)}'
            }

    async def _verify_cpt_deployment(self, cpt_slug: str) -> Dict:
        """CPTデプロイ後の検証"""
        try:
            logger.info("🔍 CPTデプロイを検証中...")
        
            if not hasattr(self, 'command_monitor') or not self.command_monitor:
                logger.warning("⚠️ コマンド監視エージェント未設定 - 検証スキップ")
                return {
                    'success': True,
                    'verification_message': '検証スキップ（コマンド監視エージェント未設定）'
                }
        
            # === パート1: 投稿タイプリストで確認 ===
            list_cmd = f"wp post-type list --field=name"
            list_result = await self.command_monitor.execute_command(list_cmd)
        
            if list_result.get('has_errors'):
                return {
                    'success': False,
                    'error': f'投稿タイプリスト取得エラー: {list_result.get("errors", [])}'
                }
        
            # ma_case が登録されているか確認
            if cpt_slug in list_result.get('stdout', ''):
                logger.info("✅ CPT登録確認完了")
                verification_msg = f"カスタム投稿タイプ '{cpt_slug}' が正常に登録されました"
            else:
                logger.warning("⚠️ CPT登録を確認できませんでした")
                verification_msg = f"カスタム投稿タイプ '{cpt_slug}' の登録を確認できませんでした"
        
            # === パート2: プラグイン状態確認 ===
            plugin_cmd = "wp plugin list --status=active --field=name"
            plugin_result = await self.command_monitor.execute_command(plugin_cmd)
        
            if 'ma-case-cpt' in plugin_result.get('stdout', ''):
                logger.info("✅ プラグイン有効化確認完了")
                verification_msg += " - プラグインは正常に有効化されています"
            else:
                logger.warning("⚠️ プラグイン有効化を確認できませんでした")
                verification_msg += " - プラグインの有効化に問題がある可能性があります"
        
            return {
                'success': True,
                'verification_message': verification_msg,
                'verification_details': {
                    'post_type_list': list_result.get('stdout', ''),
                    'plugin_list': plugin_result.get('stdout', '')
                }
            }
        
        except Exception as e:
            ErrorHandler.log_error(e, "CPTデプロイ検証")
            return {
                'success': False,
                'error': f'検証エラー: {str(e)}'
            }

    async def _deploy_via_file_write(self, php_code: str, task: Dict) -> Dict:
        """ファイル書き込みによる代替デプロイ方法"""
        try:
            logger.info("📁 ファイル書き込みでCPTコードをデプロイ")
        
            # 出力ディレクトリにPHPファイルを保存
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"cpt_ma_case_{timestamp}.php"
            output_path = Path(__file__).parent.parent / "output" / filename
        
            # 出力ディレクトリ作成
            output_path.parent.mkdir(exist_ok=True, parents=True)
        
            # PHPファイル書き込み
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("<?php\n")
                f.write("/**\n")
                f.write(" * M&A案件カスタム投稿タイプ\n")
                f.write(" * 生成日時: " + datetime.now().isoformat() + "\n")
                f.write(" */\n\n")
                f.write(php_code)
        
            logger.info(f"✅ CPTコードをファイルに保存: {output_path}")
        
            return {
                'success': True,
                'deploy_path': str(output_path),
                'method': 'file_write',
                'instructions': "このファイルをテーマのfunctions.phpまたは専用プラグインに追加してください"
            }
        
        except Exception as e:
            ErrorHandler.log_error(e, "ファイル書き込みデプロイ")
            return {
                'success': False,
                'error': f'ファイル書き込みエラー: {str(e)}'
            }
    
    def _is_wordpress_requirements_task(self, task: Dict) -> bool:
        """WordPress要件定義タスクか判定"""
        description = task.get('description', '').lower()
        keywords = [
            '要件定義',
            'ポータルサイト',
            'wordpress',
            'cocoon',
            'polylang',
            '多言語'
        ]
        # 複数のキーワードが含まれる場合
        matches = sum(1 for kw in keywords if kw in description)
        return matches >= 2
    
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
    
    async def _process_wordpress_requirements_task(self, task: Dict) -> Dict:
        """WordPress要件定義タスクを処理"""
        try:
            # ============================================================
            # === パート1: タスク開始とプロジェクト情報抽出 ===
            # ============================================================
            logger.info("="*60)
            logger.info("WordPress要件定義書作成タスク")
            logger.info("="*60)
            
            # タスクから情報を抽出
            project_info = self._extract_project_info(task)
            
            logger.info(f"プロジェクト名: {project_info['name']}")
            logger.info(f"対応言語: {', '.join(project_info['languages'])}")
            logger.info(f"テーマ: {project_info['theme']}")
            
            # ============================================================
            # === パート2: プロンプト構築とGemini送信 ===
            # ============================================================
            # プロンプトを構築
            full_prompt = self._build_wordpress_requirements_prompt(task, project_info)
            
            # Geminiに送信
            logger.info("Geminiに要件定義書作成タスクを送信中...")
            await self.browser.send_prompt(full_prompt)
            
            # 応答待機（要件定義書は長いので300秒）
            logger.info("⏱️ 待機時間: 300秒（要件定義書作成）")
            success = await self.browser.wait_for_text_generation(max_wait=300)
            
            if not success:
                return {
                    'success': False,
                    'error': '開発AI: タイムアウト（要件定義書作成: 300秒）'
                }
            
            # ============================================================
            # === パート3: 応答取得と検証 ===
            # ============================================================
            # 応答を取得
            response_text = await self.browser.extract_latest_text_response()
            
            if not response_text:
                return {
                    'success': False,
                    'error': '開発AI: 応答取得失敗'
                }
            
            logger.info(f"開発AI: 応答取得完了（{len(response_text)}文字）")
            
            # 出力完全性チェック
            if len(response_text) < 5000:
                logger.warning(f"⚠️ 出力が短すぎます（{len(response_text)}文字）")
                logger.warning("要件定義書が不完全な可能性があります")
            
            # ============================================================
            # === パート4: ファイル保存とサマリー作成 ===
            # ============================================================
            # 結果を保存
            output_files = self._save_wordpress_requirements(response_text, task, project_info)
            
            # サマリーを作成
            summary = f"""✅ WordPress要件定義書作成完了

【プロジェクト情報】
- プロジェクト名: {project_info['name']}
- テーマ: {project_info['theme']}
- 多言語プラグイン: {project_info['multilang_plugin']}
- 対応言語: {len(project_info['languages'])}言語

【生成ファイル】
"""
            for file_info in output_files:
                summary += f"- {file_info['type']}: {file_info['path'].name}\n"
            
            summary += f"\n【出力文字数】\n"
            summary += f"- 合計: {len(response_text):,}文字\n"
            
            summary += f"\n【次のステップ】\n"
            summary += f"1. 要件定義書を確認\n"
            summary += f"2. カスタム投稿タイプの実装タスクを作成\n"
            summary += f"3. ACFフィールドの実装タスクを作成\n"
            summary += f"4. 多言語設定の実装タスクを作成\n"
            
            return {
                'success': True,
                'output_files': output_files,
                'summary': summary,
                'full_text': response_text,
                'project_name': project_info['name']
            }
            
        except Exception as e:
            ErrorHandler.log_error(e, "WordPress要件定義書作成")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _extract_project_info(self, task: Dict) -> Dict:
        """タスクからプロジェクト情報を抽出"""
        description = task.get('description', '')
        parameters = task.get('parameters', {})
        
        if isinstance(parameters, str):
            try:
                parameters = json.loads(parameters)
            except:
                parameters = {}
        
        # デフォルト値
        project_info = {
            'name': 'ウズベキスタンM&Aポータルサイト',
            'theme': 'Cocoon',
            'multilang_plugin': 'Polylang',
            'languages': ['日本語', '英語', 'ロシア語', 'ウズベク語', '中国語', '韓国語', 'トルコ語'],
            'language_codes': ['ja', 'en', 'ru', 'uz', 'zh', 'ko', 'tr']
        }
        
        # parametersから上書き
        if parameters.get('project_name'):
            project_info['name'] = parameters['project_name']
        if parameters.get('theme'):
            project_info['theme'] = parameters['theme']
        if parameters.get('languages'):
            project_info['languages'] = parameters['languages']
        
        return project_info
    
    def _build_wordpress_requirements_prompt(self, task: Dict, project_info: Dict) -> str:
        """WordPress要件定義用のプロンプトを構築"""
        prompt = self.WORDPRESS_REQUIREMENTS_PROMPT
        
        # プロジェクト情報を含める
        prompt += f"""

【このタスクの具体的な要件】
{task.get('description', '')}

【プロジェクト固有情報】
- プロジェクト名: {project_info['name']}
- WordPressテーマ: {project_info['theme']}
- 多言語プラグイン: {project_info['multilang_plugin']}
- 対応言語: {', '.join(project_info['languages'])}

上記の情報を元に、完全で詳細なWordPress要件定義書を生成してください。
特に以下の点を重視してください：

1. **Cocoonテーマの機能を最大限活用**する設計
2. **Polylangでの7言語対応**を詳細に記載
3. **カスタム投稿タイプとACFの定義**を具体的に
4. **検索・フィルター機能**の詳細仕様
5. **実装可能なレベル**の具体性

【重要】
- 20,000文字以上の詳細な要件定義書を生成してください
- すべての章立て（1.0～10.0）を完全に埋めてください
- コードブロック（```）は必ず閉じてください
- JSON形式のデータ構造を含めてください
"""
        
        return prompt
    
    def _save_wordpress_requirements(self, text: str, task: Dict, project_info: Dict) -> list:
        """WordPress要件定義書を保存"""
        output_files = []
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        try:
            # ============================================================
            # === パート1: 完全な要件定義書を保存（Markdown） ===
            # ============================================================
            doc_filename = f"requirements_wordpress_{timestamp}.md"
            doc_path = self.output_folder / doc_filename
            
            with open(doc_path, 'w', encoding='utf-8') as f:
                f.write(f"# {project_info['name']} 要件定義書\n\n")
                f.write(f"作成日時: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}\n")
                f.write(f"タスクID: {task.get('task_id', 'N/A')}\n\n")
                f.write("---\n\n")
                f.write(text)
            
            output_files.append({
                'type': '要件定義書（Markdown）',
                'path': doc_path
            })
            logger.info(f"要件定義書保存: {doc_filename}")
            
            # ============================================================
            # === パート2: README（実装手順）を生成 ===
            # ============================================================
            readme_filename = f"README_requirements_{timestamp}.md"
            readme_path = self.output_folder / readme_filename
            
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(f"# {project_info['name']} 実装ガイド\n\n")
                f.write(f"## 📋 概要\n\n")
                f.write(f"このドキュメントは、{project_info['name']}の要件定義に基づく実装手順を示します。\n\n")
                f.write(f"## 🎯 プロジェクト情報\n\n")
                f.write(f"- **プロジェクト名**: {project_info['name']}\n")
                f.write(f"- **テーマ**: {project_info['theme']}\n")
                f.write(f"- **多言語プラグイン**: {project_info['multilang_plugin']}\n")
                f.write(f"- **対応言語**: {len(project_info['languages'])}言語\n\n")
                f.write(f"## 🚀 実装フェーズ\n\n")
                f.write(f"### フェーズ1: 基本構築（1-2週間）\n")
                f.write(f"1. WordPress + Cocoon インストール\n")
                f.write(f"2. Polylang設定（7言語）\n")
                f.write(f"3. 必要なプラグインのインストール\n")
                f.write(f"   - Advanced Custom Fields Pro\n")
                f.write(f"   - FacetWP\n")
                f.write(f"   - Contact Form 7\n")
                f.write(f"   - Wordfence Security\n")
                f.write(f"   - WP Rocket\n\n")
                f.write(f"### フェーズ2: カスタム投稿タイプ作成（1週間）\n")
                f.write(f"1. M&A案件投稿タイプ作成\n")
                f.write(f"2. 企業情報投稿タイプ作成\n")
                f.write(f"3. タクソノミー作成\n\n")
                f.write(f"### フェーズ3: ACFフィールド設定（1週間）\n")
                f.write(f"1. M&A案件用フィールドグループ作成\n")
                f.write(f"2. 企業情報用フィールドグループ作成\n")
                f.write(f"3. Polylangとの連携設定\n\n")
                f.write(f"### フェーズ4: 検索機能実装（1週間）\n")
                f.write(f"1. FacetWP設定\n")
                f.write(f"2. 検索フィルター作成\n")
                f.write(f"3. 検索結果ページカスタマイズ\n\n")
                f.write(f"### フェーズ5: 多言語コンテンツ登録（1週間）\n")
                f.write(f"1. サンプル案件登録\n")
                f.write(f"2. 各言語への翻訳\n")
                f.write(f"3. 翻訳品質チェック\n\n")
                f.write(f"## 📂 関連ドキュメント\n\n")
                f.write(f"- 要件定義書: `{doc_filename}`\n")
                f.write(f"- Cocoon公式: https://wp-cocoon.com/\n")
                f.write(f"- Polylang公式: https://polylang.pro/\n\n")
            
            output_files.append({
                'type': '実装ガイド',
                'path': readme_path
            })
            logger.info(f"実装ガイド保存: {readme_filename}")
            
            # ============================================================
            # === パート3: JSON形式のデータ構造を抽出して保存 ===
            # ============================================================
            json_data = self._extract_json_structures(text)
            if json_data:
                json_filename = f"data_structures_{timestamp}.json"
                json_path = self.output_folder / json_filename
                
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(json_data, f, ensure_ascii=False, indent=2)
                
                output_files.append({
                    'type': 'データ構造（JSON）',
                    'path': json_path
                })
                logger.info(f"データ構造保存: {json_filename}")
            
            return output_files
            
        except Exception as e:
            logger.error(f"ファイル保存エラー: {e}")
            return output_files
    
    def _extract_json_structures(self, text: str) -> Optional[Dict]:
        """テキストからJSON構造を抽出"""
        try:
            # ```json ... ``` パターンを探す
            json_blocks = re.findall(r'```json\s*(.*?)```', text, re.DOTALL)
            
            if not json_blocks:
                return None
            
            # すべてのJSONブロックを統合
            combined_data = {}
            for i, json_str in enumerate(json_blocks):
                try:
                    data = json.loads(json_str)
                    combined_data[f"structure_{i+1}"] = data
                except json.JSONDecodeError:
                    continue
            
            return combined_data if combined_data else None
            
        except Exception as e:
            logger.warning(f"JSON抽出エラー: {e}")
            return None

    async def _process_wordpress_cpt_task(self, task: Dict) -> Dict:
        """WordPressカスタム投稿タイプ作成タスクを処理"""
        try:
            # ============================================================
            # === パート1: タスク開始と情報抽出 ===
            # ============================================================
            logger.info("="*60)
            logger.info("WordPress カスタム投稿タイプ作成タスク")
            logger.info("="*60)
            
            # タスクから情報を抽出
            cpt_info = self._extract_cpt_info(task)
            
            logger.info(f"投稿タイプスラッグ: {cpt_info['slug']}")
            logger.info(f"表示名（単数）: {cpt_info['singular_name']}")
            logger.info(f"表示名（複数）: {cpt_info['plural_name']}")
            
            # ============================================================
            # === パート2: プロンプト構築とGemini送信 ===
            # ============================================================
            # プロンプトを構築
            full_prompt = self._build_wordpress_cpt_prompt(task, cpt_info)
            
            # Geminiに送信
            logger.info("Geminiにカスタム投稿タイプ作成タスクを送信中...")
            await self.browser.send_prompt(full_prompt)
            
            # 応答待機
            success = await self.browser.wait_for_text_generation(max_wait=300)
            
            if not success:
                return {
                    'success': False,
                    'error': '開発AI: タイムアウト（300秒）'
                }
            
            # ============================================================
            # === パート3: 応答取得と検証 ===
            # ============================================================
            # 応答を取得
            response_text = await self.browser.extract_latest_text_response()
            
            if not response_text:
                return {
                    'success': False,
                    'error': '開発AI: 応答取得失敗'
                }
            
            logger.info(f"開発AI: 応答取得完了（{len(response_text)}文字）")
            
            # ============================================================
            # === パート4: ファイル保存とサマリー作成 ===
            # ============================================================
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

    async def _process_general_task(self, task: Dict) -> Dict:
        """通常の開発タスクを処理"""
        try:
            # ============================================================
            # === パート1: タスク開始と設計書読み込み ===
            # ============================================================
            logger.info("通常の開発タスクとして処理")
            
            # 対応する設計書があれば読み込む
            design_context = self._load_design_context(task)
            
            # ============================================================
            # === パート2: プロンプト構築 ===
            # ============================================================
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
            
            # ============================================================
            # === パート3: Gemini送信と応答待機 ===
            # ============================================================
            # Geminiに送信
            logger.info("Geminiに開発タスクを送信中...")
            await self.browser.send_prompt(full_prompt)
            
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
            
            # ============================================================
            # === パート4: 応答取得と検証 ===
            # ============================================================
            # 応答を取得
            response_text = await self.browser.extract_latest_text_response()
            
            if not response_text:
                return {
                    'success': False,
                    'error': '開発AI: 応答取得失敗'
                }
            
            logger.info(f"開発AI: 応答取得完了（{len(response_text)}文字）")
            
            # ============================================================
            # === パート5: ファイル保存とコード抽出 ===
            # ============================================================
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
            
            # ============================================================
            # === パート6: サマリー作成と結果返却 ===
            # ============================================================
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