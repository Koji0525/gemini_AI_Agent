#!/usr/bin/env python3
"""
GitHub開発効率化ツール - CLIインターフェース

タスクID: {task_id}
説明: {description}
"""

import sys
import click
import json
from pathlib import Path
from typing import Optional, List
from datetime import datetime


class GitHubDevTools:
    """GitHub開発効率化ツールのコアクラス"""
    
    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or Path.home() / ".github-dev-tools" / "config.json"
        self.config = self._load_config()
    
    def _load_config(self) -> dict:
        """設定ファイルを読み込み"""
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                return json.load(f)
        return {{
            "default_branch": "main",
            "ai_model": "claude-sonnet-4",
            "auto_commit": False,
            "code_style": "google"
        }
    
    def save_config(self):
        """設定を保存"""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def generate_code(self, code_type: str, description: str) -> str:
        """コード生成"""
        template = f'''
class {{code_type.title().replace("-", "")}}:
    """
    {description}
    
    自動生成日時: {datetime.now().isoformat()}
    """
    
    def __init__(self):
        self.description = "{description}"
        self.created_at = "{datetime.now().isoformat()}"
    
    def execute(self):
        """メイン処理"""
        print(f"Executing: {{self.description}")
        # TODO: 実装
        pass
    
    def validate(self) -> bool:
        """バリデーション"""
        # TODO: 実装
        return True
'''
        return template
    
    def generate_commit_message(self, diff: str) -> str:
        """コミットメッセージ生成"""
        lines = diff.split('\n')
        added = len([l for l in lines if l.startswith('+')])
        removed = len([l for l in lines if l.startswith('-')])
        
        if added > removed:
            return f"✨ feat: Add {{added}} lines"
        elif removed > added:
            return f"🔥 refactor: Remove {{removed}} lines"
        else:
            return f"🔧 chore: Update {{added}} lines"


@click.group()
@click.version_option(version='1.0.0')
@click.pass_context
def cli(ctx):
    """GitHub開発効率化ツール - AI駆動の開発支援CLI"""
    ctx.ensure_object(dict)
    ctx.obj['tools'] = GitHubDevTools()


@cli.command()
@click.option('--type', type=click.Choice(['feature', 'fix', 'docs', 'test', 'refactor']), 
              required=True, help='生成するコードのタイプ')
@click.option('--description', '-d', required=True, help='機能の説明')
@click.option('--output', '-o', type=click.Path(), help='出力先ファイル')
@click.option('--language', '-l', default='python', help='プログラミング言語')
@click.pass_context
def generate(ctx, type, description, output, language):
    """AIを使ってコード生成
    
    使用例:
        github-dev-tools generate --type feature -d "ユーザー認証機能" -o auth.py
        github-dev-tools generate --type test -d "認証テスト" -o test_auth.py
        github-dev-tools generate --type fix -d "ログインバグ修正" -o fix_login.py
    """
    tools = ctx.obj['tools']
    
    click.echo(f"\n{'='*60}")
    click.echo(f"🤖 {{type}}コードを生成中...")
    click.echo(f"📝 説明: {description}")
    click.echo(f"🔤 言語: {{language}")
    click.echo(f"{'='*60}\n")
    
    code = tools.generate_code(type, description)
    
    if output:
        output_path = Path(output)
        output_path.write_text(code)
        click.echo(f"✅ 生成完了: {{output_path}")
        click.echo(f"📏 サイズ: {{len(code)}} bytes")
    else:
        click.echo("--- Generated Code ---")
        click.echo(code)


@cli.command()
@click.option('--auto', is_flag=True, help='自動でステージング＆コミット')
@click.option('--message', '-m', help='カスタムコミットメッセージ')
@click.option('--push', is_flag=True, help='コミット後にプッシュ')
@click.pass_context
def commit(ctx, auto, message, push):
    """差分から自動でコミットメッセージ生成
    
    使用例:
        github-dev-tools commit --auto
        github-dev-tools commit -m "カスタムメッセージ" --push
        github-dev-tools commit --auto --push
    """
    tools = ctx.obj['tools']
    
    import subprocess
    
    # ステージング済み差分を取得
    result = subprocess.run(['git', 'diff', '--staged'], 
                          capture_output=True, text=True)
    diff = result.stdout
    
    if not diff:
        click.echo("⚠️  ステージングされた変更がありません")
        click.echo("💡 ヒント: git add <file> でファイルをステージング")
        return
    
    # コミットメッセージ生成
    if not message:
        click.echo("🤖 コミットメッセージを生成中...")
        message = tools.generate_commit_message(diff)
    
    click.echo(f"\n📝 コミットメッセージ:")
    click.echo(f"   {{message}}\n")
    
    if auto:
        subprocess.run(['git', 'commit', '-m', message], check=True)
        click.echo("✅ コミット完了")
        
        if push:
            click.echo("🚀 プッシュ中...")
            subprocess.run(['git', 'push'], check=True)
            click.echo("✅ プッシュ完了")
    else:
        click.echo("実行するには --auto フラグを追加してください")


@cli.command()
@click.option('--commits', '-c', multiple=True, help='含めるコミットハッシュ')
@click.option('--output', '-o', type=click.Path(), default='pr_description.md')
@click.option('--template', type=click.Choice(['simple', 'detailed']), default='simple')
def pr(commits, output, template):
    """PR説明文を自動生成
    
    使用例:
        github-dev-tools pr
        github-dev-tools pr -c abc123 -c def456
        github-dev-tools pr --template detailed -o my_pr.md
    """
    import subprocess
    
    if not commits:
        result = subprocess.run(['git', 'log', '--oneline', '-5'],
                              capture_output=True, text=True)
        commits = result.stdout.strip().split('\n')
    
    click.echo(f"\n🤖 PR説明文を生成中... ({{len(commits)}}コミット)\n")
    
    if template == 'detailed':
        description = f"""## 📋 変更内容

{len(commits)}個のコミットを含みます

### コミット一覧
{chr(10).join(f'- {c}' for c in commits[:10])}

## ✅ チェックリスト
- [ ] テスト追加済み
- [ ] ドキュメント更新済み
- [ ] CI/CDパス確認済み
- [ ] レビュー依頼済み

## 🔍 レビューポイント
- 実装の妥当性
- テストカバレッジ
- パフォーマンス影響

## 📸 スクリーンショット
（必要に応じて追加）
"""
    else:
        description = f"""## 変更内容

{len(commits)}個のコミット

## チェックリスト
- [ ] テスト追加
- [ ] ドキュメント更新
"""
    
    output_path = Path(output)
    output_path.write_text(description)
    
    click.echo(f"✅ 生成完了: {{output_path}")
    click.echo("\n--- Preview ---")
    click.echo(description[:300] + "...")


@cli.command()
@click.option('--file', '-f', type=click.Path(exists=True), required=True)
@click.option('--detailed', is_flag=True, help='詳細なレビュー')
@click.option('--format', type=click.Choice(['text', 'json']), default='text')
def review(file, detailed, format):
    """コードレビュー支援
    
    使用例:
        github-dev-tools review -f src/main.py
        github-dev-tools review -f src/main.py --detailed
        github-dev-tools review -f src/main.py --format json
    """
    click.echo(f"\n🔍 レビュー中: {{file}}\n")
    
    file_path = Path(file)
    code = file_path.read_text()
    lines = code.split('\n')
    
    issues = []
    
    # 基本チェック
    if len(lines) > 500:
        issues.append({{"type": "warning", "message": f"ファイルが長い ({{len(lines)}}行)"}})
    
    if 'TODO' in code:
        todo_count = code.count('TODO')
        issues.append({{"type": "info", "message": f"TODO: {{todo_count}}個"}})
    
    if 'FIXME' in code:
        issues.append({{"type": "warning", "message": f"FIXME: {{code.count('FIXME')}}個"}})
    
    # 詳細チェック
    if detailed:
        if len([l for l in lines if len(l) > 100]) > 10:
            issues.append({{"type": "style", "message": "長い行が多い"}})
        
        if code.count('\t') > 0:
            issues.append({{"type": "style", "message": "タブ文字使用"}})
    
    # 出力
    if format == 'json':
        click.echo(json.dumps({{"file": str(file), "issues": issues}}, indent=2))
    else:
        if not issues:
            click.echo("✅ 問題は検出されませんでした")
        else:
            click.echo("検出された問題:")
            for issue in issues:
                icon = {{"warning": "⚠️", "info": "📝", "style": "🎨"}}.get(issue['type'], "•")
                click.echo(f"  {{icon}} {{issue['message']}")
        
        if detailed:
            click.echo(f"\n統計:")
            click.echo(f"  - 行数: {{len(lines)}")
            click.echo(f"  - 文字数: {{len(code)}")
            click.echo(f"  - 空行: {{len([l for l in lines if not l.strip()])}")


@cli.group()
def config():
    """設定管理"""
    pass


@config.command('show')
@click.pass_context
def config_show(ctx):
    """現在の設定を表示"""
    tools = ctx.obj['tools']
    click.echo("\n現在の設定:")
    click.echo(json.dumps(tools.config, indent=2))
    click.echo(f"\n設定ファイル: {{tools.config_path}")


@config.command('set')
@click.argument('key')
@click.argument('value')
@click.pass_context
def config_set(ctx, key, value):
    """設定を変更
    
    使用例:
        github-dev-tools config set default_branch develop
        github-dev-tools config set ai_model claude-opus-4
        github-dev-tools config set auto_commit true
    """
    tools = ctx.obj['tools']
    
    # 型変換
    if value.lower() == 'true':
        value = True
    elif value.lower() == 'false':
        value = False
    
    tools.config[key] = value
    tools.save_config()
    
    click.echo(f"✅ {{key}} = {{value}")
    click.echo(f"設定ファイル: {{tools.config_path}")


if __name__ == '__main__':
    cli(obj={})
