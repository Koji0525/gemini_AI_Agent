#!/usr/bin/env python3
"""
詳細タスク記述テンプレート
タスクの品質を向上させるための標準化されたテンプレート
"""

class TaskDescriptionTemplate:
    """タスク記述の詳細化テンプレート"""
    
    # 詳細記述用のプロンプトテンプレート
    DETAILED_TEMPLATE = """
【タスク記述の詳細化指示】

以下の簡潔なタスクを、実行可能な詳細タスクに展開してください。

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
元のタスク: {original_task}
コンテキスト: {context}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【必須要素を含めた詳細記述を作成してください】

1. 【目的】
   - なぜこのタスクが必要か？
   - どんな価値を提供するか？

2. 【ゴール条件】
   - 何が達成されれば完了か？
   - 定量的な成功基準は？

3. 【具体的要件】
   - 何を作成/設定するか？
   - どのような仕様か？
   - 技術的な制約は？

4. 【完了判定】
   - どうやって確認するか？
   - チェックリスト形式で列挙
   - 各項目は具体的かつ検証可能に

5. 【注意事項】
   - 気をつけるべきポイント
   - 既存システムとの整合性
   - セキュリティ・パフォーマンス考慮

【出力形式】
上記5つのセクションを必ず含め、各セクション3-5行程度で記述してください。
WordPress関連タスクの場合は、管理画面での確認方法も明記してください。
"""

    # WordPress CPT用の詳細テンプレート
    WP_CPT_TEMPLATE = """
【目的】
{purpose}

【ゴール条件】
- 投稿タイプ名: {post_type_name}
- スラッグ: {slug}
- 管理画面表示: {show_in_menu}
- 公開設定: public=true
- アーカイブページ: 有効
- REST API: 有効

【具体的要件】
1. 基本設定
   - ラベル（単数形/複数形）
   - アイコン（dashicon）
   - メニュー位置
   - サポート機能（title, editor, thumbnail, etc.）

2. カスタムフィールド連携
   {custom_fields}

3. タクソノミー連携
   {taxonomies}

【完了判定】
✅ 管理画面に「{post_type_label}」メニューが表示される
✅ 新規作成画面で基本フィールドが入力できる
✅ パーマリンク構造が /{slug}/%postname%/ になる
✅ アーカイブページ /{slug}/ が表示される
✅ REST API エンドポイント /wp-json/wp/v2/{slug} が応答する

【注意事項】
- 既存の投稿タイプと名前が被らないこと
- スラッグは英数字とハイフンのみ使用
- ラベルは日本語で分かりやすく
- rewrite ルールの flush が必要（プラグイン有効化時）
"""

    # WordPress ACF用の詳細テンプレート
    WP_ACF_TEMPLATE = """
【目的】
{purpose}

【ゴール条件】
- フィールドグループ名: {field_group_name}
- 対象投稿タイプ: {post_type}
- フィールド数: {field_count}個
- すべてのフィールドが管理画面で表示・編集可能

【具体的要件】
{field_details}

【完了判定】
✅ ACF管理画面に「{field_group_name}」が表示される
✅ {post_type}の編集画面に全フィールドが表示される
✅ 各フィールドのバリデーションが動作する
✅ 保存した値が正しく読み込まれる
✅ REST APIで値が取得できる（必要な場合）

【注意事項】
- フィールド名は英数字とアンダースコアのみ
- ラベルは日本語で分かりやすく
- 必須フィールドには required=true を設定
- 数値フィールドには min/max を適切に設定
- 選択フィールドには choices を明確に定義
"""

    @staticmethod
    def format_cpt_description(post_type_name: str, purpose: str, 
                               custom_fields: str = "", taxonomies: str = "") -> str:
        """CPTタスク用の詳細記述を生成"""
        slug = post_type_name.lower().replace(" ", "-")
        post_type_label = post_type_name
        
        return TaskDescriptionTemplate.WP_CPT_TEMPLATE.format(
            purpose=purpose,
            post_type_name=post_type_name,
            slug=slug,
            show_in_menu="true",
            custom_fields=custom_fields or "（後続タスクで設定）",
            taxonomies=taxonomies or "（後続タスクで設定）",
            post_type_label=post_type_label
        )
    
    @staticmethod
    def format_acf_description(field_group_name: str, post_type: str,
                               purpose: str, field_details: str) -> str:
        """ACFタスク用の詳細記述を生成"""
        field_count = field_details.count("\n   -") if field_details else 0
        
        return TaskDescriptionTemplate.WP_ACF_TEMPLATE.format(
            purpose=purpose,
            field_group_name=field_group_name,
            post_type=post_type,
            field_count=field_count,
            field_details=field_details
        )
    
    @staticmethod
    def enhance_task_description(original_description: str, 
                                 context: dict = None) -> str:
        """
        簡潔なタスク記述を詳細化するためのプロンプトを生成
        
        Args:
            original_description: 元の簡潔なタスク記述
            context: 追加のコンテキスト情報
        
        Returns:
            Geminiに送信する詳細化プロンプト
        """
        context_str = ""
        if context:
            context_str = "\n".join([f"- {k}: {v}" for k, v in context.items()])
        
        return TaskDescriptionTemplate.DETAILED_TEMPLATE.format(
            original_task=original_description,
            context=context_str or "（追加情報なし）"
        )


# テスト用のサンプル
if __name__ == "__main__":
    template = TaskDescriptionTemplate()
    
    # サンプル1: CPT作成タスク
    print("=" * 70)
    print("【サンプル1: CPTタスクの詳細記述】")
    print("=" * 70)
    cpt_desc = template.format_cpt_description(
        post_type_name="MA案件",
        purpose="ウズベキスタンのM&A案件を一元管理し、案件情報を効率的に検索・表示するため",
        custom_fields="""
   - 価格帯（数値、単位：万ドル、範囲：100-10000）
   - 業種（テキスト、例：製造業、IT、小売など）
   - 地域（選択、ウズベキスタンの州名）
   - 案件ステータス（選択：交渉中/デューデリ/成約/終了）
   - 担当者（ユーザー選択）
        """,
        taxonomies="地域（ウズベキスタンの州）、業種カテゴリー"
    )
    print(cpt_desc)
    print()
    
    # サンプル2: 簡潔な記述の詳細化プロンプト
    print("=" * 70)
    print("【サンプル2: 簡潔記述の詳細化プロンプト】")
    print("=" * 70)
    enhance_prompt = template.enhance_task_description(
        original_description="WordPressにカスタム投稿タイプを作成",
        context={
            "プロジェクト": "ウズベキスタンM&Aポータルサイト",
            "技術スタック": "WordPress + ACF",
            "目的": "M&A案件の管理と検索"
        }
    )
    print(enhance_prompt)
