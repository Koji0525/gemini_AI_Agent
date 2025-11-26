#!/usr/bin/env python3
"""
DAG可視化システム

機能:
- NetworkXグラフのHTML可視化
- タスク状態の色分け表示
- クリティカルパスのハイライト
- インタラクティブなノード情報表示
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    import matplotlib
    import networkx as nx

    matplotlib.use("Agg")  # GUI不要
    import matplotlib.pyplot as plt
except ImportError:
    print("⚠️  必要なライブラリをインストール中...")
    import subprocess

    subprocess.check_call([sys.executable, "-m", "pip", "install", "networkx", "matplotlib"])
    import matplotlib
    import networkx as nx

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt


class DAGVisualizer:
    """
    DAG可視化システム

    責務:
    - NetworkXグラフの視覚化
    - タスク状態の色分け
    - クリティカルパスの強調表示
    - HTML出力
    """

    # タスク状態の色定義
    STATE_COLORS = {
        "pending": "#E0E0E0",  # グレー
        "in_progress": "#FFD700",  # ゴールド
        "completed": "#90EE90",  # ライトグリーン
        "failed": "#FF6B6B",  # レッド
        "blocked": "#FFA07A",  # ライトサーモン
        "split": "#87CEEB",  # スカイブルー
        "alternative": "#DDA0DD",  # プラム
    }

    def __init__(self):
        """初期化"""
        print("✅ DAGVisualizer初期化")

    def visualize_to_png(
        self,
        dag: nx.DiGraph,
        output_path: str = "shared_states/dag_visualization.png",
        highlight_critical_path: bool = True,
        show_task_details: bool = True,
    ) -> str:
        """
        DAGをPNG画像として出力

        Args:
            dag: NetworkXのDAGオブジェクト
            output_path: 出力先パス
            highlight_critical_path: クリティカルパス強調表示
            show_task_details: タスク詳細表示

        Returns:
            出力ファイルパス
        """
        print(f"\n📊 DAG可視化: {output_path}")

        # 図のサイズ設定（ノード数に応じて調整）
        node_count = len(dag.nodes())
        fig_width = max(20, node_count * 2)
        fig_height = max(12, node_count * 1.5)

        plt.figure(figsize=(fig_width, fig_height))

        # レイアウト計算（階層型）
        try:
            pos = nx.nx_agraph.graphviz_layout(dag, prog="dot")
        except:
            # graphviz未インストール時はspring_layout
            pos = nx.spring_layout(dag, k=2, iterations=50)

        # ノードの色決定
        node_colors = []
        for node_id in dag.nodes():
            node_data = dag.nodes[node_id]
            state = node_data.get("status", "pending")
            node_colors.append(self.STATE_COLORS.get(state, "#E0E0E0"))

        # エッジの描画（通常の依存関係）
        nx.draw_networkx_edges(
            dag, pos, edge_color="#888888", arrows=True, arrowsize=20, width=2, alpha=0.6
        )

        # クリティカルパスの強調表示
        if highlight_critical_path:
            try:
                critical_path = self._calculate_critical_path(dag)
                critical_edges = list(zip(critical_path[:-1], critical_path[1:]))
                nx.draw_networkx_edges(
                    dag, pos, edgelist=critical_edges, edge_color="red", width=4, alpha=0.8
                )
            except:
                pass  # クリティカルパス計算失敗時はスキップ

        # ノードの描画
        nx.draw_networkx_nodes(
            dag,
            pos,
            node_color=node_colors,
            node_size=3000,
            alpha=0.9,
            linewidths=2,
            edgecolors="black",
        )

        # ラベルの描画
        if show_task_details:
            labels = {}
            for node_id in dag.nodes():
                node_data = dag.nodes[node_id]
                title = node_data.get("title", node_id)
                # 長いタイトルは省略
                if len(title) > 30:
                    title = title[:27] + "..."

                status = node_data.get("status", "pending")
                estimated_hours = node_data.get("estimated_hours", "?")

                labels[node_id] = f"{title}\n({status}, {estimated_hours}h)"
        else:
            labels = {
                node_id: dag.nodes[node_id].get("title", node_id)[:20] for node_id in dag.nodes()
            }

        nx.draw_networkx_labels(dag, pos, labels, font_size=8, font_weight="bold")

        # 凡例追加
        legend_elements = [
            plt.Line2D(
                [0], [0], marker="o", color="w", markerfacecolor=color, markersize=10, label=state
            )
            for state, color in self.STATE_COLORS.items()
        ]
        plt.legend(handles=legend_elements, loc="upper left", fontsize=10)

        # タイトル
        plt.title(f"タスク依存関係グラフ (ノード数: {node_count})", fontsize=16, fontweight="bold")

        plt.axis("off")
        plt.tight_layout()

        # 保存
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_path, dpi=150, bbox_inches="tight")
        plt.close()

        print(f"✅ PNG出力完了: {output_path}")
        return output_path

    def visualize_to_html(
        self,
        dag: nx.DiGraph,
        output_path: str = "shared_states/dag_visualization.html",
        include_statistics: bool = True,
    ) -> str:
        """
        DAGをインタラクティブなHTMLとして出力

        Args:
            dag: NetworkXのDAGオブジェクト
            output_path: 出力先パス
            include_statistics: 統計情報を含める

        Returns:
            出力ファイルパス
        """
        print(f"\n📊 DAG可視化（HTML）: {output_path}")

        # ノードとエッジのデータ構築
        nodes_data = []
        for node_id in dag.nodes():
            node = dag.nodes[node_id]
            nodes_data.append(
                {
                    "id": node_id,
                    "label": node.get("title", node_id),
                    "status": node.get("status", "pending"),
                    "color": self.STATE_COLORS.get(node.get("status", "pending"), "#E0E0E0"),
                    "estimated_hours": node.get("estimated_hours", 0),
                    "description": node.get("description", "")[:100],
                }
            )

        edges_data = []
        for source, target in dag.edges():
            edges_data.append({"from": source, "to": target})

        # 統計情報
        statistics = {}
        if include_statistics:
            statistics = self._calculate_statistics(dag)

        # HTML生成
        html_content = self._generate_html_template(nodes_data, edges_data, statistics)

        # 保存
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        print(f"✅ HTML出力完了: {output_path}")
        print(f"   ブラウザで開く: file://{Path(output_path).absolute()}")
        return output_path

    def _calculate_critical_path(self, dag: nx.DiGraph) -> List[str]:
        """
        クリティカルパス計算

        Args:
            dag: DAGオブジェクト

        Returns:
            クリティカルパスのノードIDリスト
        """
        # 最長パスを計算
        longest_path = nx.dag_longest_path(
            dag, weight=lambda u, v, d: dag.nodes[v].get("estimated_hours", 1)
        )
        return longest_path

    def _calculate_statistics(self, dag: nx.DiGraph) -> Dict:
        """
        DAG統計情報計算

        Args:
            dag: DAGオブジェクト

        Returns:
            統計情報の辞書
        """
        total_nodes = len(dag.nodes())
        total_edges = len(dag.edges())

        # 状態別カウント
        status_counts = {}
        total_hours = 0
        for node_id in dag.nodes():
            node = dag.nodes[node_id]
            status = node.get("status", "pending")
            status_counts[status] = status_counts.get(status, 0) + 1
            total_hours += node.get("estimated_hours", 0)

        # クリティカルパス
        try:
            critical_path = self._calculate_critical_path(dag)
            critical_path_length = len(critical_path)
            critical_path_hours = sum(
                dag.nodes[node_id].get("estimated_hours", 0) for node_id in critical_path
            )
        except:
            critical_path_length = 0
            critical_path_hours = 0

        # 並列度（最大幅）
        try:
            levels = list(nx.topological_generations(dag))
            max_parallelism = max(len(level) for level in levels) if levels else 0
        except:
            max_parallelism = 0

        return {
            "total_nodes": total_nodes,
            "total_edges": total_edges,
            "status_counts": status_counts,
            "total_estimated_hours": total_hours,
            "critical_path_length": critical_path_length,
            "critical_path_hours": critical_path_hours,
            "max_parallelism": max_parallelism,
            "timestamp": datetime.now().isoformat(),
        }

    def _generate_html_template(
        self, nodes: List[Dict], edges: List[Dict], statistics: Dict
    ) -> str:
        """
        HTML可視化テンプレート生成

        Args:
            nodes: ノードデータ
            edges: エッジデータ
            statistics: 統計情報

        Returns:
            HTMLコンテンツ
        """
        return f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DAG可視化 - タスク依存関係グラフ</title>
    <script src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            padding: 20px;
        }}
        h1 {{
            color: #333;
            margin-top: 0;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }}
        .stat-card {{
            background: #f9f9f9;
            border-left: 4px solid #4CAF50;
            padding: 15px;
            border-radius: 4px;
        }}
        .stat-card h3 {{
            margin: 0 0 10px 0;
            font-size: 14px;
            color: #666;
        }}
        .stat-card .value {{
            font-size: 24px;
            font-weight: bold;
            color: #333;
        }}
        #network {{
            width: 100%;
            height: 600px;
            border: 1px solid #ddd;
            border-radius: 4px;
        }}
        .legend {{
            display: flex;
            flex-wrap: wrap;
            gap: 15px;
            margin-top: 20px;
            padding: 15px;
            background: #f9f9f9;
            border-radius: 4px;
        }}
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .legend-color {{
            width: 20px;
            height: 20px;
            border-radius: 50%;
            border: 2px solid #333;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 タスク依存関係グラフ (DAG)</h1>
        
        <div class="stats-grid">
            <div class="stat-card">
                <h3>総タスク数</h3>
                <div class="value">{statistics.get('total_nodes', 0)}</div>
            </div>
            <div class="stat-card">
                <h3>依存関係数</h3>
                <div class="value">{statistics.get('total_edges', 0)}</div>
            </div>
            <div class="stat-card">
                <h3>推定総時間</h3>
                <div class="value">{statistics.get('total_estimated_hours', 0)}h</div>
            </div>
            <div class="stat-card">
                <h3>クリティカルパス</h3>
                <div class="value">{statistics.get('critical_path_hours', 0)}h</div>
            </div>
            <div class="stat-card">
                <h3>最大並列度</h3>
                <div class="value">{statistics.get('max_parallelism', 0)}</div>
            </div>
        </div>
        
        <div id="network"></div>
        
        <div class="legend">
            <div class="legend-item">
                <div class="legend-color" style="background-color: #E0E0E0;"></div>
                <span>保留中 (pending)</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background-color: #FFD700;"></div>
                <span>実行中 (in_progress)</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background-color: #90EE90;"></div>
                <span>完了 (completed)</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background-color: #FF6B6B;"></div>
                <span>失敗 (failed)</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background-color: #FFA07A;"></div>
                <span>ブロック中 (blocked)</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background-color: #87CEEB;"></div>
                <span>分割タスク (split)</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background-color: #DDA0DD;"></div>
                <span>代替タスク (alternative)</span>
            </div>
        </div>
    </div>
    
    <script>
        const nodes = new vis.DataSet({json.dumps(nodes, ensure_ascii=False)});
        const edges = new vis.DataSet({json.dumps(edges, ensure_ascii=False)});
        
        const container = document.getElementById('network');
        const data = {{
            nodes: nodes,
            edges: edges
        }};
        
        const options = {{
            layout: {{
                hierarchical: {{
                    direction: 'UD',
                    sortMethod: 'directed',
                    levelSeparation: 150,
                    nodeSpacing: 200
                }}
            }},
            physics: false,
            nodes: {{
                shape: 'box',
                font: {{
                    size: 14,
                    face: 'monospace'
                }},
                borderWidth: 2,
                shadow: true,
                margin: 10
            }},
            edges: {{
                arrows: {{
                    to: {{
                        enabled: true,
                        scaleFactor: 0.5
                    }}
                }},
                smooth: {{
                    type: 'cubicBezier',
                    forceDirection: 'vertical'
                }},
                width: 2
            }},
            interaction: {{
                hover: true,
                zoomView: true,
                dragView: true
            }}
        }};
        
        const network = new vis.Network(container, data, options);
        
        // クリックイベント
        network.on('click', function(params) {{
            if (params.nodes.length > 0) {{
                const nodeId = params.nodes[0];
                const node = nodes.get(nodeId);
                alert(`タスク: ${{node.label}}\n状態: ${{node.status}}\n推定時間: ${{node.estimated_hours}}h\n\n${{node.description}}`);
            }}
        }});
    </script>
</body>
</html>"""


def main():
    """テスト実行"""
    print("=" * 60)
    print("📊 DAGVisualizer テスト")
    print("=" * 60)

    visualizer = DAGVisualizer()

    # テスト用DAG作成
    dag = nx.DiGraph()

    # ノード追加
    tasks = [
        ("task_1", {"title": "データ収集", "status": "completed", "estimated_hours": 2}),
        ("task_2", {"title": "データクリーニング", "status": "completed", "estimated_hours": 1}),
        ("task_3", {"title": "分析実行", "status": "in_progress", "estimated_hours": 3}),
        ("task_4", {"title": "レポート作成", "status": "pending", "estimated_hours": 2}),
        ("task_5", {"title": "テスト", "status": "pending", "estimated_hours": 1}),
    ]

    for task_id, attrs in tasks:
        dag.add_node(task_id, **attrs)

    # エッジ追加（依存関係）
    edges = [
        ("task_1", "task_2"),
        ("task_2", "task_3"),
        ("task_3", "task_4"),
        ("task_3", "task_5"),
    ]
    dag.add_edges_from(edges)

    # PNG出力
    print("\n[1/2] PNG出力...")
    png_path = visualizer.visualize_to_png(dag)
    print(f"   ✅ {png_path}")

    # HTML出力
    print("\n[2/2] HTML出力...")
    html_path = visualizer.visualize_to_html(dag)
    print(f"   ✅ {html_path}")

    print("\n" + "=" * 60)
    print("✅ テスト完了")
    print("=" * 60)


if __name__ == "__main__":
    main()
