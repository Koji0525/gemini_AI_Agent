"""
WordPress自動化ダッシュボード
Streamlitを使用したリアルタイム可視化
"""

import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

# ページ設定
st.set_page_config(page_title="WordPress自動化ダッシュボード", page_icon="🚀", layout="wide")

# パス設定
KB_PATH = "/workspaces/gemini_AI_Agent/knowledge_base/wordpress_automation"
LOGS_PATH = "/workspaces/gemini_AI_Agent/uz-manda-portal/logs/day4"


def load_statistics():
    """統計情報を読み込み"""
    stats_file = f"{KB_PATH}/statistics.json"
    if os.path.exists(stats_file):
        with open(stats_file, "r") as f:
            return json.load(f)
    return {}


def load_execution_logs():
    """実行ログを読み込み"""
    logs = []
    if os.path.exists(LOGS_PATH):
        for filename in sorted(os.listdir(LOGS_PATH)):
            if filename.endswith(".json"):
                filepath = os.path.join(LOGS_PATH, filename)
                with open(filepath, "r") as f:
                    logs.append(json.load(f))
    return logs


def load_patterns(pattern_type):
    """パターンファイルを読み込み"""
    filepath = f"{KB_PATH}/{pattern_type}_patterns.jsonl"
    patterns = []
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            for line in f:
                try:
                    patterns.append(json.loads(line.strip()))
                except:
                    continue
    return patterns


# メインタイトル
st.title("🚀 WordPress自動化ダッシュボード")
st.markdown("---")

# サイドバー - 概要統計
st.sidebar.header("📊 システム概要")

stats = load_statistics()
if stats:
    st.sidebar.metric("総実行回数", f"{stats.get('total_executions', 0)}回")
    st.sidebar.metric("総投稿数", f"{stats.get('total_posts_created', 0)}社")
    st.sidebar.metric("平均品質スコア", f"{stats.get('average_quality_score', 0):.1f}/10")
    st.sidebar.metric("成功率", f"{stats.get('success_rate', 0):.1f}%")
else:
    st.sidebar.info("統計データがありません")

st.sidebar.markdown("---")
st.sidebar.markdown("**最終実行**: " + (stats.get("last_execution", "N/A") if stats else "N/A"))

# メインエリア - タブ
tab1, tab2, tab3, tab4 = st.tabs(["📈 品質推移", "📋 実行履歴", "🧠 学習パターン", "💡 改善提案"])

# タブ1: 品質推移
with tab1:
    st.header("品質スコア推移")

    logs = load_execution_logs()
    if logs:
        # データフレーム作成
        df_data = []
        for log in logs:
            df_data.append(
                {
                    "timestamp": log.get("timestamp", ""),
                    "quality_score": log["results"].get("quality_score", 0),
                    "successful_posts": log["results"].get("successful_posts", 0),
                    "failed_posts": log["results"].get("failed_posts", 0),
                }
            )

        df = pd.DataFrame(df_data)

        # 品質スコアグラフ
        fig = px.line(
            df,
            x="timestamp",
            y="quality_score",
            title="品質スコアの推移",
            labels={"quality_score": "品質スコア", "timestamp": "実行日時"},
        )
        fig.update_traces(mode="lines+markers")
        st.plotly_chart(fig, use_container_width=True)

        # 成功/失敗グラフ
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(name="成功", x=df["timestamp"], y=df["successful_posts"], marker_color="green"))
        fig2.add_trace(go.Bar(name="失敗", x=df["timestamp"], y=df["failed_posts"], marker_color="red"))
        fig2.update_layout(barmode="stack", title="投稿成功/失敗の推移")
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("実行ログがありません")

# タブ2: 実行履歴
with tab2:
    st.header("実行履歴")

    if logs:
        for i, log in enumerate(reversed(logs), 1):
            with st.expander(f"実行 #{i} - {log.get('timestamp', 'N/A')}"):
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric("ステータス", log.get("status", "N/A").upper())
                    st.metric("実行時間", log.get("execution_time", "N/A"))

                with col2:
                    st.metric("成功", f"{log['results']['successful_posts']}社")
                    st.metric("失敗", f"{log['results']['failed_posts']}社")

                with col3:
                    st.metric("DD項目", f"{log['results']['dd_items_added']}項目")
                    st.metric("品質スコア", f"{log['results']['quality_score']:.1f}/10")

                st.markdown("**作成された投稿:**")
                for post_id in log["results"]["post_ids"]:
                    st.markdown(f"- [投稿 #{post_id}](https://uzbek-ma.com/?p={post_id})")
    else:
        st.info("実行履歴がありません")

# タブ3: 学習パターン
with tab3:
    st.header("🧠 学習パターン分析")

    success_patterns = load_patterns("success")
    partial_patterns = load_patterns("partial_success")
    failure_patterns = load_patterns("failure")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("成功パターン", len(success_patterns), delta="+1" if success_patterns else None)
    with col2:
        st.metric("部分成功", len(partial_patterns))
    with col3:
        st.metric("失敗パターン", len(failure_patterns))

    # 成功パターンの詳細
    if success_patterns:
        st.subheader("✅ 最新の成功パターン")
        latest_success = success_patterns[-1]

        st.json(
            {
                "timestamp": latest_success.get("timestamp", "N/A"),
                "quality_score": latest_success.get("quality_score", "N/A"),
                "conditions": latest_success.get("conditions", {}),
                "best_practices": latest_success.get("best_practices", []),
            }
        )

# タブ4: 改善提案
with tab4:
    st.header("💡 改善提案")

    if success_patterns:
        latest = success_patterns[-1]

        st.subheader("ベストプラクティス")
        for practice in latest.get("best_practices", []):
            st.success(f"✅ {practice}")

    st.subheader("次のアクション")
    st.info("📌 Day 6: GitHub Actions自動実行設定")
    st.info("📌 Slack/Email通知機能実装")
    st.info("📌 GitHub Issues自動生成")

    # フィードバック入力
    st.subheader("人間からのフィードバック")
    feedback = st.text_area("改善提案やコメントを入力してください")
    if st.button("フィードバックを送信"):
        if feedback:
            # フィードバックを保存
            feedback_file = f"{KB_PATH}/human_feedback.jsonl"
            with open(feedback_file, "a") as f:
                f.write(
                    json.dumps({"timestamp": datetime.now().isoformat(), "feedback": feedback}, ensure_ascii=False)
                    + "\n"
                )
            st.success("✅ フィードバックを記録しました！")
        else:
            st.warning("フィードバックを入力してください")

# フッター
st.markdown("---")
st.markdown("**WordPress自動化システム** | Day 5: Self Learning Pipeline統合")
