"""
TimelineView - トレースタイムライン可視化

【Phase 2.2: タイムライン可視化】
ウォーターフォール形式でトレース表示
"""

from datetime import datetime
from typing import Any, Dict, List


class TimelineView:
    """タイムライン可視化エンジン"""

    def __init__(self):
        print("✅ TimelineView初期化完了")

    def generate_waterfall_html(self, traces: List[Dict[str, Any]]) -> str:
        """
        ウォーターフォール図のHTML生成

        Args:
            traces: トレースデータのリスト

        Returns:
            HTMLコード
        """
        if not traces:
            return "<p>トレースデータがありません</p>"

        html_parts = ['<div class="timeline-container">']

        # 最小・最大時刻を計算
        timestamps = []
        for trace in traces:
            if "timestamp" in trace:
                timestamps.append(datetime.fromisoformat(trace["timestamp"]))

        if not timestamps:
            return "<p>タイムスタンプがありません</p>"

        min_time = min(timestamps)
        max_time = max(timestamps)
        time_range = (max_time - min_time).total_seconds()

        if time_range == 0:
            time_range = 1  # ゼロ除算回避

        # 各トレースをバーとして表示
        for trace in traces:
            if "timestamp" not in trace:
                continue

            trace_time = datetime.fromisoformat(trace["timestamp"])
            offset_sec = (trace_time - min_time).total_seconds()
            position_percent = (offset_sec / time_range) * 100

            duration_ms = trace.get("duration_ms", 100)
            width_percent = (duration_ms / 1000 / time_range) * 100
            width_percent = max(width_percent, 2)  # 最小2%

            status = trace.get("status", "unknown")
            color = "#34d399" if status == "success" else "#f87171"

            operation = trace.get("operation_name", "unknown")
            trace_id = trace.get("trace_id", "N/A")

            bar_html = f"""
            <div class="timeline-bar" style="
                left: {position_percent:.2f}%;
                width: {width_percent:.2f}%;
                background: {color};
            " title="{operation} - {trace_id}">
                <span class="bar-label">{operation}</span>
            </div>
            """

            html_parts.append(bar_html)

        html_parts.append("</div>")

        # スタイル追加
        style = """
        <style>
        .timeline-container {
            position: relative;
            height: 400px;
            background: rgba(255,255,255,0.03);
            border-radius: 8px;
            padding: 20px;
            overflow-x: auto;
        }
        .timeline-bar {
            position: absolute;
            height: 40px;
            border-radius: 4px;
            display: flex;
            align-items: center;
            padding: 0 10px;
            transition: transform 0.2s;
            cursor: pointer;
        }
        .timeline-bar:hover {
            transform: scaleY(1.2);
            z-index: 10;
        }
        .bar-label {
            color: white;
            font-size: 0.85em;
            font-weight: bold;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        </style>
        """

        return style + "".join(html_parts)

    def export_timeline_json(self, traces: List[Dict[str, Any]]) -> Dict[str, Any]:
        """タイムラインデータをJSON形式でエクスポート"""
        return {
            "timeline_type": "waterfall",
            "trace_count": len(traces),
            "traces": traces,
            "exported_at": datetime.now().isoformat(),
        }


if __name__ == "__main__":
    print("🧪 TimelineView テスト")

    view = TimelineView()

    # テストデータ
    test_traces = [
        {
            "trace_id": "test-1",
            "operation_name": "PMAgent.plan",
            "status": "success",
            "timestamp": "2024-01-20T10:00:00",
            "duration_ms": 200,
        },
        {
            "trace_id": "test-2",
            "operation_name": "TaskExecutor.execute",
            "status": "success",
            "timestamp": "2024-01-20T10:00:01",
            "duration_ms": 500,
        },
        {
            "trace_id": "test-3",
            "operation_name": "ReviewAgent.review",
            "status": "error",
            "timestamp": "2024-01-20T10:00:02",
            "duration_ms": 150,
        },
    ]

    html = view.generate_waterfall_html(test_traces)
    print(f"✅ HTML生成: {len(html)}文字")

    json_data = view.export_timeline_json(test_traces)
    print(f"✅ JSON生成: {json_data['trace_count']}件")
