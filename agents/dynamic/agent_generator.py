"""
Week 6: AgentGenerator - エージェント自動生成システム

テンプレートベースでエージェントを動的に生成
"""

import os
import re
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path


class AgentGenerator:
    """
    エージェントを自動生成するジェネレータ
    """

    def __init__(self, templates_dir: str = "agents/dynamic/templates"):
        """
        Args:
            templates_dir: テンプレートディレクトリのパス
        """
        self.templates_dir = Path(templates_dir)
        self.generated_agents = []
        self.generation_count = 0

    def generate_from_template(self, template_name: str, agent_name: str, config: Dict[str, Any]) -> str:
        """
        テンプレートからエージェントコードを生成

        Args:
            template_name: テンプレート名
            agent_name: 生成するエージェント名
            config: エージェント設定

        Returns:
            生成されたPythonコード
        """
        # テンプレートファイルを読み込み
        template_path = self.templates_dir / f"{template_name}.py.template"

        if not template_path.exists():
            raise FileNotFoundError(f"Template not found: {template_path}")

        with open(template_path, "r", encoding="utf-8") as f:
            template_code = f.read()

        # プレースホルダーを置換
        agent_code = self._replace_placeholders(template_code, agent_name, config)

        self.generation_count += 1
        self.generated_agents.append({"name": agent_name, "template": template_name, "generated_at": datetime.now()})

        return agent_code

    def _replace_placeholders(self, template_code: str, agent_name: str, config: Dict[str, Any]) -> str:
        """
        テンプレート内のプレースホルダーを置換

        Args:
            template_code: テンプレートコード
            agent_name: エージェント名
            config: 設定

        Returns:
            置換後のコード
        """
        # 基本的なプレースホルダー
        replacements = {
            "{{AGENT_NAME}}": agent_name,
            "{{AGENT_CLASS}}": self._to_class_name(agent_name),
            "{{VERSION}}": config.get("version", "1.0.0"),
            "{{DESCRIPTION}}": config.get("description", f"{agent_name} agent"),
            "{{AUTHOR}}": config.get("author", "System"),
            "{{CREATED_AT}}": datetime.now().isoformat(),
        }

        # 置換実行
        code = template_code
        for placeholder, value in replacements.items():
            code = code.replace(placeholder, str(value))

        return code

    def _to_class_name(self, agent_name: str) -> str:
        """
        エージェント名をクラス名に変換（PascalCase）

        Args:
            agent_name: エージェント名

        Returns:
            クラス名（PascalCase）

        Examples:
            'test_api_agent' -> 'TestApiAgent'
            'TestAPIAgent' -> 'TestApiAgent'
            'my-agent' -> 'MyAgent'
        """
        # まず全てを小文字に
        name = agent_name.lower()

        # アンダースコア、ハイフン、スペースで分割
        parts = re.split(r"[-_\s]+", name)

        # 各パートの最初の文字を大文字に（PascalCase）
        return "".join(word.capitalize() for word in parts if word)

    def save_agent(self, agent_code: str, agent_name: str, output_dir: str = "agents/dynamic/generated") -> str:
        """
        生成したエージェントをファイルに保存

        Args:
            agent_code: エージェントコード
            agent_name: エージェント名
            output_dir: 出力ディレクトリ

        Returns:
            保存したファイルのパス
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # ファイル名を生成
        filename = f"{agent_name.lower().replace(' ', '_')}.py"
        filepath = output_path / filename

        # ファイルに保存
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(agent_code)

        return str(filepath)

    def list_templates(self) -> List[str]:
        """
        利用可能なテンプレートのリストを取得

        Returns:
            テンプレート名のリスト（拡張子なし）
        """
        if not self.templates_dir.exists():
            return []

        templates = []
        for file in self.templates_dir.glob("*.py.template"):
            # 拡張子 .py.template を除去
            template_name = file.name.replace(".py.template", "")
            templates.append(template_name)

        return sorted(templates)

    def get_statistics(self) -> Dict[str, Any]:
        """
        生成統計を取得

        Returns:
            統計情報
        """
        return {
            "total_generated": self.generation_count,
            "templates_available": len(self.list_templates()),
            "recent_agents": self.generated_agents[-5:] if self.generated_agents else [],
        }


# ================================================
# デモ用関数
# ================================================


def demo_agent_generator():
    """AgentGeneratorのデモンストレーション"""
    print("\n" + "=" * 70)
    print("AgentGenerator デモンストレーション")
    print("=" * 70)

    generator = AgentGenerator()

    # 利用可能なテンプレート表示
    print("\n【利用可能なテンプレート】")
    templates = generator.list_templates()
    if templates:
        for i, template in enumerate(templates, 1):
            print(f"  {i}. {template}")
    else:
        print("  （テンプレートがまだありません）")

    # 統計表示
    print("\n【統計情報】")
    stats = generator.get_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    demo_agent_generator()
