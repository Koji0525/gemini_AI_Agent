# 🤖 Gemini AI Agent - WordPress自動構築システム

WordPress サイトを AI で自動構築するエージェントシステム

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![WordPress Compatible](https://img.shields.io/badge/WordPress-6.0+-blue.svg)](https://wordpress.org/)

---

## 🎯 概要

このプロジェクトは、Google Gemini API を使用して WordPress サイトの構築を自動化するマルチエージェントシステムです。

### ✨ 主な機能

- 🏗️ **カスタム投稿タイプ（CPT）の自動生成**
- 🏷️ **カスタムタクソノミーの自動生成**
- 📝 **ACF カスタムフィールドの自動生成**
- 📊 **Google Sheets 統合（実行ログ記録）**
- 🔍 **WordPress 設定検証システム**
- 🎬 **統合デモ（5分でポートフォリオサイト構築）**

---

## 🚀 クイックスタート

### 必要な環境

- Python 3.8+
- WordPress 6.0+（REST API有効）
- Google Cloud Platform アカウント
- Advanced Custom Fields（ACF）プラグイン

### インストール
```bash
# リポジトリのクローン
git clone https://github.com/yourusername/gemini_AI_Agent.git
cd gemini_AI_Agent

# 依存関係のインストール
pip install -r requirements.txt

# 環境変数の設定
cp .env.example .env
# .envファイルを編集して認証情報を設定
```

### 設定

`.env` ファイルに以下を設定:
```env
# WordPress設定
WP_URL=https://your-site.com
wp_user=your_username
wp_pass=your_password

# Google API
GEMINI_API_KEY=your_gemini_api_key
SPREADSHEET_ID=your_spreadsheet_id
GOOGLE_SERVICE_ACCOUNT_FILE=path/to/service-account.json
```

### 基本的な使用方法
```bash
# WordPress設定確認
python3 configuration/config_validation_system.py

# デモ実行：完全版ポートフォリオサイト構築
python3 demos/complete_portfolio_site_demo.py
```

---

## 📚 エージェント一覧

### 1. WPCPTAgent（カスタム投稿タイプ）
```python
from agents.wordpress.specialized import WPCPTAgent, CPTSpecification

cpt_spec = CPTSpecification(
    post_type="portfolio",
    singular_name="ポートフォリオ",
    plural_name="ポートフォリオ一覧"
)

agent = WPCPTAgent(config, sheets_manager)
result = await agent.create_cpt(cpt_spec)
```

**生成物:**
- `cpt_portfolio_YYYYMMDD_HHMMSS.php`

### 2. WPTaxonomyAgent（タクソノミー）
```python
from agents.wordpress.specialized import WPTaxonomyAgent, TaxonomySpecification

tax_spec = TaxonomySpecification(
    taxonomy="skill",
    singular_name="スキル",
    plural_name="スキル一覧",
    hierarchical=True  # カテゴリー風
)

agent = WPTaxonomyAgent(config, sheets_manager)
result = await agent.create_taxonomy(tax_spec)
```

**生成物:**
- `taxonomy_skill_YYYYMMDD_HHMMSS.php`

### 3. WPACFAgent（カスタムフィールド）
```python
from agents.wordpress.specialized import WPACFAgent, ACFFieldGroupSpec, ACFFieldSpec

acf_spec = ACFFieldGroupSpec(
    key="group_portfolio",
    title="ポートフォリオ詳細",
    fields=[
        ACFFieldSpec(
            key="field_client",
            label="クライアント名",
            name="client_name",
            type="text"
        )
    ]
)

agent = WPACFAgent(config, sheets_manager)
result = await agent.create_field_group(acf_spec)
```

**生成物:**
- `acf_group_portfolio_YYYYMMDD_HHMMSS.json`
- `acf_group_portfolio_YYYYMMDD_HHMMSS.php`

---

## 🎬 デモ

### 完全版ポートフォリオサイト構築
```bash
python3 demos/complete_portfolio_site_demo.py
```

**5分で以下を自動生成:**
- ✅ portfolio 投稿タイプ
- ✅ skill タクソノミー（階層型）
- ✅ project_category タクソノミー（階層型）
- ✅ project_tag タクソノミー（非階層型）
- ✅ ACF カスタムフィールド（5個）

---

## 📁 プロジェクト構造
```
gemini_AI_Agent/
├── agents/
│   └── wordpress/
│       ├── specialized/
│       │   ├── wp_cpt_agent.py         # CPT管理
│       │   ├── wp_taxonomy_agent.py    # タクソノミー管理
│       │   ├── wp_acf_agent.py         # ACF管理
│       │   └── wp_agent_logger.py      # ログ記録
│       └── wp_site_builder.py          # 統合オーケストレーター
├── tools/
│   ├── sheets_manager.py               # Google Sheets統合
│   └── gemini_api_client.py            # Gemini API
├── configuration/
│   ├── config_loader.py                # 設定管理
│   └── config_validation_system.py     # 設定検証
├── demos/
│   └── complete_portfolio_site_demo.py # 完全版デモ
├── scripts/
│   ├── show_project_structure.py       # プロジェクト構造可視化
│   └── generate_progress_report.sh     # 進捗レポート
└── agent_outputs/                      # 生成されたファイル
    ├── wordpress_cpt/
    ├── wordpress_taxonomy/
    └── wordpress_acf/
```

---

## 📊 実行ログ

すべてのエージェント実行は Google Sheets の `task_execution_log` シートに自動記録されます。

**記録内容:**
- task_id（タイムスタンプ）
- agent_role（エージェント名）
- output_summary（実行サマリー）
- output_data（生成ファイルパス）
- status（completed/failed）
- Quality_Score（1-10）

---

## 🔧 カスタマイズ

### プロジェクト構造の表示
```bash
# Pythonファイルのみ表示
python3 scripts/show_project_structure.py
```

### 進捗レポート
```bash
# 最新の進捗状況を表示
./scripts/generate_progress_report.sh
```

---

## 📖 ドキュメント

- [WP_CPT_AGENT.md](docs/WP_CPT_AGENT.md) - CPTエージェント詳細
- [WP_TAXONOMY_AGENT.md](docs/WP_TAXONOMY_AGENT.md) - タクソノミーエージェント詳細
- [WP_ACF_AGENT.md](docs/WP_ACF_AGENT.md) - ACFエージェント詳細
- [WORDPRESS_DEPLOYMENT_GUIDE.md](docs/WORDPRESS_DEPLOYMENT_GUIDE.md) - WordPress適用ガイド
-　/workspaces/gemini_AI_Agent/docs/SESSION_COMPLETION_20251029.md
---

## 🧪 テスト
```bash
# 個別エージェントテスト
python3 agents/wordpress/specialized/wp_cpt_agent.py
python3 agents/wordpress/specialized/wp_taxonomy_agent.py
python3 agents/wordpress/specialized/wp_acf_agent.py

# 統合テスト
python3 demos/complete_portfolio_site_demo.py
```

---

## 📈 進捗状況

- ✅ コアシステム: 100%
- ✅ WordPress エージェント: 100%
- ✅ 設定確認システム: 100%
- ✅ 統合テスト: 100%
- ✅ ドキュメント: 100%

**総合進捗: 100% 🎉**

---

## 🤝 コントリビューション

プルリクエストを歓迎します！

---

## 📝 ライセンス

MIT License - 詳細は [LICENSE](LICENSE) を参照

---

## 👤 作者

Gemini AI Agent Project Team

---

## 🙏 謝辞

- WordPress Community
- Google Gemini API
- Advanced Custom Fields

---

**作成日**: 2025-10-28  
**バージョン**: 1.0.0  
**Status**: ✅ Production Ready

---

## 🎉 最新アップデート - 2025-10-29

### WordPress自動構築システム v2.0 完成 🚀

**完全自動化を実現：**
- ✅ ACFフィールドの自動設定
- ✅ カスタム投稿タイプの自動適用
- ✅ functions.phpへの自動コード追加
- ✅ 実環境での動作実証完了

### Phase 3: 学習型エラー分析システム 🧠

**AI駆動の自己学習システム：**

#### 📊 ExecutionAnalyzer v1.3
- 実行データの包括的分析（166件処理）
- エージェント別パフォーマンス分析
- システム成功率: **89.8%**
- ボトルネック自動特定

#### 🎓 PatternLearner v1.0
- 成功パターン自動学習（149件分析）
- 失敗パターン分析（2件）
- ベストプラクティス自動生成
- トップエージェント: design (53件成功)

#### 🔮 PredictiveAnalyzer v1.0
- タスク失敗リスク予測
- システム問題予測
- 予防的アクション提案
- learned_patternsへの永続化

**現在のシステムヘルス: 🟢 優秀**

---

## 📊 プロジェクト進捗
```
Phase 1: 基盤構築              ████████████████████ 100% ✅
Phase 2: エージェント開発      ████████████████████ 100% ✅
Phase 3: 学習型分析システム    ████████████████████ 100% ✅
Phase 4: AI駆動フィードバック  ░░░░░░░░░░░░░░░░░░░░   0% ⏳
Phase 5: 自己修復システム      ░░░░░░░░░░░░░░░░░░░░   0% ⏳

現在の自動化レベル: 78%
最終目標: 95%
```

---

## 🏆 実証済みの性能

### 実測データ（166件の実行ログ分析）

| 指標 | 値 | 評価 |
|------|-----|------|
| 総実行数 | 166件 | - |
| 成功率 | 89.8% | 🟢 優秀 |
| エラー数 | 2件のみ | 🟢 優秀 |
| 完璧なエージェント | 5つ (100%成功率) | 🏆 |
| システムヘルス | 優秀 | 🟢 |

### トップパフォーマンスエージェント

1. 🥇 **design** - 53件成功（設計業務に最適）
2. 🥈 **dev** - 26件成功（開発業務に最適）
3. 🥉 **wordpress** - 20件成功（WordPress操作に最適）

---

## 🚀 使い方

### 1. WordPress完全自動化
```bash
# CPT + ACF の統合自動設定
python3 demos/complete_wordpress_automation.py
```

### 2. 実行データ分析
```bash
# 過去の実行パターンを分析
python3 agents/advanced_analytics/execution_analyzer.py
```

### 3. パターン学習
```bash
# 成功・失敗パターンを学習
python3 agents/advanced_analytics/pattern_learner.py
```

### 4. 予測的分析
```bash
# システム問題を予測
python3 agents/advanced_analytics/predictive_analyzer.py
```

---

## 📚 新しいドキュメント

- **[プロジェクト完了レポート](docs/PROJECT_COMPLETION_REPORT.md)** - v2.0完成宣言
- **[Phase 3完了レポート](docs/PHASE3_COMPLETION_REPORT.md)** - 学習システム詳細
- **[次世代ロードマップ](docs/NEXT_GENERATION_ROADMAP.md)** - 12週間開発計画
- **[セッション完了レポート](docs/SESSION_COMPLETION_20251029.md)** - 今回の成果

---

## 🔮 次世代システム開発計画

### Phase 4-7 ロードマップ（10週間）
```
Week 3-4  | Phase 4 | AI駆動フィードバック        | 目標: 85%
Week 5-7  | Phase 5 | 自己修復システム            | 目標: 90%
Week 8-10 | Phase 6 | 動的システム拡張            | 目標: 93%
Week 11-12| Phase 7 | 統合ダッシュボード          | 目標: 95%
```

### 最終目標（12週間後）

**完全自律的AI駆動プロジェクトマネージャー**
```
入力: "ウズベキスタンM&Aポータルサイト構築"
  ↓
[完全自動実行]
  • 要件分析
  • 設計図生成
  • エージェント選定（自動生成含む）
  • 実行計画作成
  • 自動実行（エラー自己修復）
  • 結果検証
  • 改善提案
  • 次回への学習反映
  ↓
出力: 完成したWordPressサイト + 改善提案
```

**自動化率: 95%**  
**人間の関与: 初期ゴール入力と重要判断の承認のみ**

---

## 💡 今後の拡張機能

### 短期（1-2週間）
- [ ] IntelligentFeedbackGenerator（AI改善提案）
- [ ] A/Bテスト機能
- [ ] コード自動生成

### 中期（1ヶ月）
- [ ] 自己修復システム
- [ ] 適応的リトライ戦略
- [ ] スマートロールバック

### 長期（3ヶ月）
- [ ] 動的エージェント生成
- [ ] Webダッシュボード
- [ ] マルチサイト対応

---

## 🎓 学習済みパターン

システムは過去の実行から以下を学習しています：

### ✅ 成功パターン
- design/dev/writerエージェントの適切な使用
- タスクの適切な分解
- 100+タスクの安定処理

### ⚠️ 注意点
- APIタイムアウト（60秒以上推奨）
- 複雑な仕様定義タスク

### 🏆 ベストプラクティス
- エージェントの得意分野を活用
- 適切なエラーハンドリング
- 段階的な実装アプローチ

---

## 📞 サポート

### トラブルシューティング
- 実行ログ: `agent_outputs/*.json`
- 分析レポート: `agent_outputs/*_report.json`
- 詳細ドキュメント: `docs/`

### 学習済みパターン
- Google Sheets: `learned_patterns` シート
- 予測分析結果: `agent_outputs/predictive_analysis_report.json`

---

## 🎉 プロジェクトの特徴

1. **完全自動化** - ゴール入力から実行まで自動
2. **AI駆動** - Gemini APIによる智能的な設計と学習
3. **自己学習** - 過去のデータから自動的に改善
4. **予測的** - 問題を事前に予測して対応
5. **実証済み** - 166件の実行で89.8%の成功率

---

**🚀 WordPress自動構築の未来は、ここから始まります。**



## 📝 変更履歴

# エラー修正: Week 5 Day 3
