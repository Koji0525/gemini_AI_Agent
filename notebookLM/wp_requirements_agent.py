"""
WordPress要件定義書作成エージェント（完全版）
エラー処理・検証・フォールバック完備
"""

import asyncio
import logging
from typing import Dict, Optional, List
from pathlib import Path
from datetime import datetime
import json
import re

logger = logging.getLogger(__name__)


class WordPressRequirementsAgent:
    """WordPress要件定義書作成専門エージェント（完全版）"""
    
    # プロンプトは長いので簡潔版に変更
    PROMPT_TEMPLATE = """あなたはWordPress開発の専門家で、要件定義のプロフェッショナルです。

【あなたの役割】
ウズベキスタンのM&Aポータルサイトの完全な要件定義書を作成してください。

【プロジェクト情報】
- **サイト名**: ウズベキスタンM&Aポータル
- **WordPressテーマ**: Cocoon（日本製高機能テーマ）
- **多言語**: Polylang（日英露ウズ中韓トルコ語の7言語）
- **主要プラグイン**: ACF PRO, FacetWP, Relevanssi, Wordfence, WP Rocket

【要件定義書の構成】
以下の構造で**詳細な要件定義書**を出力してください：

# 1.0 プロジェクト概要
## 1.1 プロジェクト名
## 1.2 目的・背景
## 1.3 対象ユーザー
## 1.4 成功指標（KPI）

# 2.0 システム構成
## 2.1 技術スタック
- WordPress 6.4+、Cocoon、Polylang Pro、ACF PRO、FacetWP、Relevanssi
## 2.2 サーバー要件
- PHP 8.0+、MySQL 8.0+、メモリ 512MB+
## 2.3 開発・本番環境

# 3.0 機能要件
## 3.1 カスタム投稿タイプ
### 3.1.1 M&A案件（ma_case）
- supports: title, editor, thumbnail, custom-fields, excerpt
- taxonomies: industry_category, region, deal_type
### 3.1.2 企業情報（company）
### 3.1.3 ニュース（news）

## 3.2 カスタムタクソノミー
### 3.2.1 業種分類（industry_category） - 階層型
### 3.2.2 地域（region） - 階層型
### 3.2.3 案件タイプ（deal_type） - 非階層型

## 3.3 ACFカスタムフィールド
### M&A案件用フィールド（20個定義）
1. case_id（案件ID） - テキスト、必須
2. ma_scheme（M&Aスキーム） - セレクト、必須
3. desired_price（希望価格） - 数値
4. established_year（設立年） - 数値
5. employees（従業員数） - 数値
6. annual_revenue（年商） - 数値
7. reason_for_sale（売却理由） - テキストエリア
8. confidential_level（機密レベル） - セレクト
9-20. その他フィールド（具体的に記載）

## 3.4 検索・フィルター（FacetWP）
- 業種別検索（チェックボックス）
- 地域別検索（ドロップダウン）
- 価格帯検索（スライダー）
- 案件タイプ検索（チェックボックス）
- キーワード検索（Relevanssi）

## 3.5 多言語機能（Polylang）
### 言語設定
- デフォルト: 日本語（ja）
- 翻訳言語: en, ru, uz, zh, ko, tr
### URLマッピング
日本語: https://example.com/ma-cases/
英語: https://example.com/en/ma-cases/
ロシア語: https://example.com/ru/ma-cases/

## 3.6 ユーザー管理
### カスタムロール: ma_partner
- 自身の作成した ma_case のみ編集可能
- 他ユーザーの案件は閲覧・編集不可

## 3.7 問い合わせ機能
- Contact Form 7
- 多言語対応フォーム

## 3.8 SEO対策（Cocoon活用）
- 構造化データ自動生成
- OGPタグ設定
- パンくずリスト

## 3.9 セキュリティ（Wordfence）
- ファイアウォール: enabled
- スキャン: 週1回

## 3.10 パフォーマンス（WP Rocket + Cocoon）
- モバイルキャッシュ: 有効
- CSS/JS縮小化: 有効

# 4.0 非機能要件
## 4.1 パフォーマンス
- ページ読み込み: 3秒以内
- PageSpeed Insights: 80点以上
## 4.2 可用性
- サーバー稼働率: 99.9%以上
## 4.3 Pydanticモデル移行計画

# 5.0 画面設計
## 5.1 トップページ
## 5.2 M&A案件一覧
## 5.3 M&A案件詳細

# 6.0 データ構造
## 6.1 カスタム投稿タイプ定義（JSON）
```json
{
  "ma_case": {
    "labels": {
      "ja": "M&A案件",
      "en": "M&A Cases"
    },
    "supports": ["title", "editor", "thumbnail"],
    "taxonomies": ["industry_category", "region"],
    "has_archive": true
  }
}
6.2 ACFフィールドグループ定義（JSON）
json{
  "ma_case_fields": {
    "title": "M&A案件基本情報",
    "fields": [
      {
        "name": "case_id",
        "type": "text",
        "required": true
      }
    ]
  }
}
7.0 実装計画
フェーズ1: 基本構築（1-2週間）
フェーズ2: 機能実装（2-3週間）
フェーズ3: コンテンツ登録（1週間）
フェーズ4: テスト・調整（1週間）
フェーズ5: 本番公開（1週間）
8.0 運用保守
定期作業

WordPress/プラグイン更新（月1回）
バックアップ確認（週1回）

9.0 コスト見積もり
初期費用
月額費用
10.0 リスクと対策
技術的リスク
対策

【出力要件】

すべての章立て（1.0～10.0）を完全に記載
JSONコードブロックは必ず閉じる（```で終了）
具体的な数値・名称を記載
Cocoon、Polylangの機能を明記
15,000文字以上を目標

それでは、完全な要件定義書を出力してください。
"""
def __init__(self, browser, output_folder: Path):
    self.browser = browser
    self.output_folder = output_folder
    self.output_folder.mkdir(parents=True, exist_ok=True)
    
    # 統計情報
    self.stats = {
        'total_attempts': 0,
        'successful': 0,
        'failed': 0
    }
    
    logger.info("✅ WordPressRequirementsAgent 初期化完了")
    logger.info(f"📁 出力フォルダ: {self.output_folder}")

async def execute(self, task: Dict) -> Dict:
    """要件定義書作成タスクを実行（完全版）"""
    task_id = task.get('task_id', 'UNKNOWN')
    self.stats['total_attempts'] += 1
    
    try:
        logger.info("\n" + "="*70)
        logger.info("📋 WordPress要件定義書作成開始")
        logger.info(f"タスクID: {task_id}")
        logger.info("="*70 + "\n")
        
        # ステップ1: ブラウザ確認
        if not self._verify_browser():
            return self._create_error_result(task_id, 'ブラウザが利用できません')
        
        # ステップ2: プロンプト送信
        logger.info("📤 ステップ1: Geminiにプロンプト送信")
        if not await self._send_prompt():
            return self._create_error_result(task_id, 'プロンプト送信失敗')
        
        # ステップ3: 応答待機
        logger.info("⏱️ ステップ2: 応答待機（最大300秒）")
        if not await self._wait_for_response():
            return self._create_error_result(task_id, 'タイムアウト（300秒）')
        
        # ステップ4: 応答取得
        logger.info("📥 ステップ3: 応答取得")
        response_text = await self._extract_response()
        
        if not response_text:
            return self._create_error_result(task_id, '応答取得失敗')
        
        # ステップ5: 品質検証
        logger.info("🔍 ステップ4: 品質検証")
        validation_result = self._validate_response(response_text)
        
        if not validation_result['valid']:
            logger.warning(f"⚠️ 品質警告: {validation_result['warnings']}")
        
        # ステップ6: ファイル保存
        logger.info("💾 ステップ5: ファイル保存")
        output_files = await self._save_requirements(response_text, task_id)
        
        # ステップ7: 成功結果の作成
        self.stats['successful'] += 1
        
        logger.info("\n" + "="*70)
        logger.info("✅ WordPress要件定義書作成完了")
        logger.info(f"📄 文字数: {len(response_text):,}文字")
        logger.info(f"📁 保存ファイル: {len(output_files)}件")
        logger.info("="*70 + "\n")
        
        return {
            'success': True,
            'message': '要件定義書作成完了',
            'task_id': task_id,
            'content_length': len(response_text),
            'output_files': [str(f['path']) for f in output_files],
            'validation': validation_result,
            'summary': f'要件定義書作成完了（{len(response_text):,}文字、{len(output_files)}ファイル）',
            'full_text': response_text[:1000] + '...' if len(response_text) > 1000 else response_text
        }
        
    except Exception as e:
        self.stats['failed'] += 1
        logger.error(f"❌ 要件定義書作成エラー: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return self._create_error_result(task_id, str(e))

def _verify_browser(self) -> bool:
    """ブラウザの状態を確認"""
    if not self.browser:
        logger.error("❌ ブラウザコントローラーが初期化されていません")
        return False
    
    if not hasattr(self.browser, 'send_prompt'):
        logger.error("❌ ブラウザに send_prompt メソッドがありません")
        return False
    
    logger.info("✅ ブラウザ確認: OK")
    return True

async def _send_prompt(self) -> bool:
    """プロンプトを送信"""
    try:
        await self.browser.send_prompt(self.PROMPT_TEMPLATE)
        logger.info("✅ プロンプト送信完了")
        return True
    except Exception as e:
        logger.error(f"❌ プロンプト送信エラー: {e}")
        return False

async def _wait_for_response(self, max_wait: int = 300) -> bool:
    """応答を待機"""
    try:
        success = await self.browser.wait_for_text_generation(max_wait=max_wait)
        if success:
            logger.info(f"✅ 応答待機完了（{max_wait}秒以内）")
        else:
            logger.error(f"❌ タイムアウト（{max_wait}秒）")
        return success
    except Exception as e:
        logger.error(f"❌ 応答待機エラー: {e}")
        return False

async def _extract_response(self) -> Optional[str]:
    """応答テキストを抽出"""
    try:
        response_text = await self.browser.extract_latest_text_response()
        
        if response_text:
            logger.info(f"✅ 応答取得: {len(response_text):,}文字")
        else:
            logger.error("❌ 応答が空です")
        
        return response_text
    except Exception as e:
        logger.error(f"❌ 応答抽出エラー: {e}")
        return None

def _validate_response(self, text: str) -> Dict:
    """応答の品質を検証"""
    warnings = []
    
    # 長さチェック
    if len(text) < 10000:
        warnings.append(f'文字数が少ない（{len(text):,}文字）')
    
    # 章立てチェック
    required_sections = [
        '1.0 プロジェクト概要',
        '2.0 システム構成',
        '3.0 機能要件',
        '4.0 非機能要件',
        '5.0 画面設計',
        '6.0 データ構造',
        '7.0 実装計画',
        '8.0 運用保守',
        '9.0 コスト見積もり',
        '10.0 リスクと対策'
    ]
    
    missing_sections = [s for s in required_sections if s not in text]
    if missing_sections:
        warnings.append(f'欠落セクション: {", ".join(missing_sections)}')
    
    # JSONブロックチェック
    json_blocks = re.findall(r'```json', text)
    if len(json_blocks) < 2:
        warnings.append(f'JSONブロックが少ない（{len(json_blocks)}個）')
    
    # Cocoonキーワードチェック
    if 'Cocoon' not in text and 'cocoon' not in text:
        warnings.append('Cocoonテーマの記述が見つかりません')
    
    # Polylangキーワードチェック
    if 'Polylang' not in text and 'polylang' not in text:
        warnings.append('Polylangプラグインの記述が見つかりません')
    
    valid = len(warnings) == 0
    
    if valid:
        logger.info("✅ 品質検証: 合格")
    else:
        logger.warning(f"⚠️ 品質検証: 警告あり（{len(warnings)}件）")
        for w in warnings:
            logger.warning(f"  - {w}")
    
    return {
        'valid': valid,
        'warnings': warnings,
        'length': len(text),
        'sections_found': len(required_sections) - len(missing_sections),
        'sections_total': len(required_sections)
    }

async def _save_requirements(self, text: str, task_id: str) -> List[Dict]:
    """要件定義書を保存"""
    output_files = []
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    try:
        # 1. メイン要件定義書（Markdown）
        doc_filename = f"requirements_wordpress_{task_id}_{timestamp}.md"
        doc_path = self.output_folder / doc_filename
        
        with open(doc_path, 'w', encoding='utf-8') as f:
            f.write(f"# WordPress要件定義書 - ウズベキスタンM&Aポータル\n\n")
            f.write(f"**作成日時**: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}\n")
            f.write(f"**タスクID**: {task_id}\n")
            f.write(f"**文字数**: {len(text):,}文字\n\n")
            f.write("---\n\n")
            f.write(text)
        
        output_files.append({
            'type': '要件定義書（Markdown）',
            'path': doc_path,
            'size': len(text)
        })
        logger.info(f"✅ 保存: {doc_filename} ({len(text):,}文字)")
        
        # 2. JSON構造（もし抽出できれば）
        json_data = self._extract_json_structures(text)
        if json_data:
            json_filename = f"data_structures_{task_id}_{timestamp}.json"
            json_path = self.output_folder / json_filename
            
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, ensure_ascii=False, indent=2)
            
            output_files.append({
                'type': 'データ構造（JSON）',
                'path': json_path,
                'size': json_path.stat().st_size
            })
            logger.info(f"✅ 保存: {json_filename}")
        
        # 3. 実装チェックリスト
        checklist_filename = f"checklist_{task_id}_{timestamp}.md"
        checklist_path = self.output_folder / checklist_filename
        
        checklist_content = self._generate_checklist()
        with open(checklist_path, 'w', encoding='utf-8') as f:
            f.write(checklist_content)
        
        output_files.append({
            'type': '実装チェックリスト',
            'path': checklist_path,
            'size': len(checklist_content)
        })
        logger.info(f"✅ 保存: {checklist_filename}")
        
        logger.info(f"✅ 合計 {len(output_files)} ファイル保存完了")
        return output_files
        
    except Exception as e:
        logger.error(f"❌ ファイル保存エラー: {e}")
        return output_files

def _extract_json_structures(self, text: str) -> Optional[Dict]:
    """JSONブロックを抽出"""
    try:
        json_blocks = re.findall(r'```json\s*(.*?)```', text, re.DOTALL)
        
        if not json_blocks:
            return None
        
        combined_data = {}
        for i, json_str in enumerate(json_blocks, 1):
            try:
                data = json.loads(json_str)
                combined_data[f"block_{i}"] = data
            except json.JSONDecodeError:
                logger.warning(f"⚠️ JSONブロック {i} のパースに失敗")
                continue
        
        return combined_data if combined_data else None
        
    except Exception as e:
        logger.warning(f"⚠️ JSON抽出エラー: {e}")
        return None

def _generate_checklist(self) -> str:
    """実装チェックリストを生成"""
    return """# WordPress M&Aポータル 実装チェックリスト
フェーズ1: 基本構築 ✅

 WordPress 6.4+ インストール
 Cocoonテーマ インストール・有効化
 Polylang Pro インストール・設定（7言語）
 必須プラグイン インストール

 Advanced Custom Fields PRO
 Custom Post Type UI
 FacetWP
 Relevanssi
 Wordfence Security
 WP Rocket
 Contact Form 7
 User Role Editor



フェーズ2: カスタム投稿タイプ 🔧

 M&A案件（ma_case）作成

 ラベル設定（7言語）
 サポート機能設定
 パーマリンク設定


 企業情報（company）作成
 ニュース（news）作成

フェーズ3: タクソノミー 🏷️

 業種分類（industry_category）作成 - 階層型
 地域（region）作成 - 階層型
 案件タイプ（deal_type）作成 - 非階層型
 Polylang翻訳設定

フェーズ4: ACFフィールド 📝

 M&A案件フィールドグループ作成

 基本情報（case_id, ma_scheme, etc.）
 財務情報（desired_price, revenue, etc.）
 連絡先情報


 企業情報フィールドグループ作成
 Polylang連携設定

フェーズ5: 検索・フィルター 🔍

 FacetWP設定

 業種別ファセット
 地域別ファセット
 価格帯スライダー
 案件タイプファセット


 Relevanssi設定

 インデックス構築
 カスタムフィールド検索設定

フェーズ6: セキュリティ・最適化 🔒

 Wordfence Security設定

 ファイアウォール有効化
 スキャンスケジュール設定


 WP Rocket設定

 モバイルキャッシュ有効化
 CSS/JS縮小化


 Cocoon高速化設定

フェーズ7: ユーザー管理 👥

 カスタムロール（ma_partner）作成
 権限設定
 テストユーザー作成・検証

フェーズ8: コンテンツ登録 📄

 サンプルM&A案件登録（各言語）
 サンプル企業情報登録
 固定ページ作成
 メニュー設定

フェーズ9: テスト 🧪

 多言語表示確認
 検索機能テスト
 フィルター機能テスト
 フォーム送信テスト
 パフォーマンステスト
 セキュリティスキャン

フェーズ10: 本番公開 🚀

 DNS設定
 SSL証明書設定
 本番環境移行
 最終確認


作成日: {datetime}
バージョン: 1.0
""".format(datetime=datetime.now().strftime('%Y-%m-%d %H:%M'))
def _create_error_result(self, task_id: str, error: str) -> Dict:
    """エラー結果を作成"""
    logger.error(f"❌ エラー: {error}")
    
    return {
        'success': False,
        'error': error,
        'task_id': task_id,
        'stats': self.stats.copy()
    }

def get_stats(self) -> Dict:
    """統計情報を取得"""
    return self.stats.copy()



### 3. `wordpress/wp_dev/wp_cpt_agent.py`（完全版）

"""
WordPressカスタム投稿タイプ作成エージェント（完全版）
"""

import asyncio
import logging
from typing import Dict
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


class WordPressCPTAgent:
    """CPT作成専門エージェント（完全版）"""
    
    PROMPT_TEMPLATE = """あなたはWordPress開発の専門家です。

【タスク】
以下のカスタム投稿タイプを作成するPHPコードを生成してください：

**投稿タイプ情報**:
- スラッグ: {cpt_slug}
- 表示名（単数）: {cpt_singular}
- 表示名（複数）: {cpt_plural}
- サポート機能: {supports}
- タクソノミー: {taxonomies}

【要件】
1. `register_post_type()` を使用した完全なPHPコード
2. Polylang多言語対応
3. REST API対応（show_in_rest: true）
4. has_archive: true
5. エラーハンドリング付き
6. 詳細なコメント付き

【出力形式】
```php
<?php
/**
 * カスタム投稿タイプ: {cpt_name}
 * 作成日: {date}
 * Polylang対応
 */

function register_cpt_{cpt_slug_clean}() {{
    $labels = array(
        'name' => __( '{cpt_plural}', 'textdomain' ),
        'singular_name' => __( '{cpt_singular}', 'textdomain' ),
        // ... その他のラベル
    );
    
    $args = array(
        'labels' => $labels,
        'public' => true,
        'has_archive' => true,
        'show_in_rest' => true,
        'supports' => {supports_array},
        'taxonomies' => {taxonomies_array},
        // ... その他の設定
    );
    
    register_post_type( '{cpt_slug}', $args );
}}
add_action( 'init', 'register_cpt_{cpt_slug_clean}', 0 );
?>
完全に動作するPHPコードを出力してください。
"""
def __init__(self, browser, output_folder: Path):
    self.browser = browser
    self.output_folder = output_folder
    self.output_folder.mkdir(parents=True, exist_ok=True)
    logger.info("✅ WordPressCPTAgent 初期化")

async def execute(self, task: Dict) -> Dict:
    """CPT作成タスクを実行"""
    task_id = task.get('task_id', 'UNKNOWN')
    description = task.get('description', '')
    
    try:
        logger.info("=" * 70)
        logger.info("🔧 カスタム投稿タイプ作成開始")
        logger.info("=" * 70)
        
        # CPT仕様を抽出
        cpt_spec = self._extract_cpt_spec(description)
        logger.info(f"📊 CPT仕様: {cpt_spec['slug']}")
        
        # プロンプト構築
        prompt = self._build_prompt(cpt_spec)
        
        # Geminiに送信
        await self.browser.send_prompt(prompt)
        
        # 応答待機
        success = await self.browser.wait_for_text_generation(max_wait=180)
        
        if not success:
            return {'success': False, 'error': 'タイムアウト', 'task_id': task_id}
        
        # 応答取得
        response_text = await self.browser.extract_latest_text_response()
        
        if not response_text:
            return {'success': False, 'error': '応答取得失敗', 'task_id': task_id}
        
        # PHP保存
        output_file = await self._save_php_code(response_text, cpt_spec, task_id)
        
        logger.info("=" * 70)
        logger.info("✅ CPT作成完了")
        logger.info("=" * 70)
        
        return {
            'success': True,
            'message': f'CPT作成完了: {cpt_spec["slug"]}',
            'output_file': str(output_file),
            'cpt_slug': cpt_spec['slug'],
            'task_id': task_id,
            'summary': f'カスタム投稿タイプ {cpt_spec["slug"]} 作成完了'
        }
        
    except Exception as e:
        logger.error(f"❌ CPT作成エラー: {e}")
        return {'success': False, 'error': str(e), 'task_id': task_id}

def _extract_cpt_spec(self, description: str) -> Dict:
    """説明からCPT仕様を抽出"""
    desc_lower = description.lower()
    
    # M&A案件
    if 'ma_case' in desc_lower or 'm&a案件' in desc_lower:
        return {
            'slug': 'ma_case',
            'singular': 'M&A案件',
            'plural': 'M&A案件一覧',
            'supports': ['title', 'editor', 'thumbnail', 'custom-fields', 'excerpt'],
            'taxonomies': ['industry_category', 'region', 'deal_type']
        }
    
    # 企業情報
    elif 'company' in desc_lower or '企業情報' in desc_lower:
        return {
            'slug': 'company',
            'singular': '企業情報',
            'plural': '企業情報一覧',
            'supports': ['title', 'editor', 'thumbnail', 'custom-fields'],
            'taxonomies': ['industry_category', 'region']
        }
    
    # ニュース
    elif 'news' in desc_lower or 'ニュース' in desc_lower:
        return {
            'slug': 'news',
            'singular': 'ニュース',
            'plural': 'ニュース一覧',
            'supports': ['title', 'editor', 'thumbnail', 'excerpt'],
            'taxonomies': []
        }
    
    # デフォルト
    return {
        'slug': 'custom_post',
        'singular': 'カスタム投稿',
        'plural': 'カスタム投稿一覧',
        'supports': ['title', 'editor', 'thumbnail'],
        'taxonomies': []
    }

def _build_prompt(self, cpt_spec: Dict) -> str:
    """プロンプトを構築"""
    slug_clean = cpt_spec['slug'].replace('-', '_')
    
    return self.PROMPT_TEMPLATE.format(
        cpt_slug=cpt_spec['slug'],
        cpt_singular=cpt_spec['singular'],
        cpt_plural=cpt_spec['plural'],
        cpt_name=cpt_spec['singular'],
        cpt_slug_clean=slug_clean,
        supports=', '.join(cpt_spec['supports']),
        taxonomies=', '.join(cpt_spec['taxonomies']) if cpt_spec['taxonomies'] else 'なし',
        supports_array=str(cpt_spec['supports']).replace("'", '"'),
        taxonomies_array=str(cpt_spec['taxonomies']).replace("'", '"'),
        date=datetime.now().strftime('%Y-%m-%d')
    )

async def _save_php_code(self, code: str, cpt_spec: Dict, task_id: str) -> Path:
    """PHPコードを保存"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"cpt_{cpt_spec['slug']}_{task_id}_{timestamp}.php"
    output_path = self.output_folder / filename
    
    with open(output_path, 'w', encoding='utf-8') as f:
        # ヘッダーコメント追加
        f.write(f"<?php\n")
        f.write(f"/**\n")
        f.write(f" * カスタム投稿タイプ: {cpt_spec['singular']}\n")
        f.write(f" * スラッグ: {cpt_spec['slug']}\n")
        f.write(f" * 作成日: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f" */\n\n")
        
        # コード本体
        if '<?php' in code:
            # 既にPHPタグがある場合はそのまま
            f.write(code)
        else:
            # PHPタグがない場合は追加
            f.write(code)
    
    logger.info(f"✅ PHP保存: {filename}")
    return output_path

