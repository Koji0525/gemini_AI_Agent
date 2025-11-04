"""ナレッジベース統合システムのデモ"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agents.self_healing.logging.enhanced_knowledge_manager import TaskReportGenerator


def demo_image_processing():
    reporter = TaskReportGenerator(
        "task_img_001", "画像処理とアップロード", "画像を取得→圧縮→アップロード"
    )
    reporter.start_step(1, "画像取得")
    try:
        raise ConnectionError("接続タイムアウト")
    except ConnectionError as e:
        reporter.fail_step(e, root_cause="ネットワーク不安定", error_type="ConnectionError")
        reporter.retry_step("タイムアウト延長(3秒→10秒)")
        reporter.success_step(execution_time=8.1, method="requests.get(url, timeout=10)")
    reporter.start_step(2, "画像圧縮")
    reporter.success_step(execution_time=2.0, method="PIL.Image.save(quality=85)")
    reporter.start_step(3, "WordPressアップロード")
    try:
        raise TimeoutError("アップロードタイムアウト")
    except TimeoutError as e:
        reporter.fail_step(e, root_cause="ファイルサイズ大（2.5MB）", error_type="TimeoutError")
        reporter.retry_step("サイズ縮小(2.5MB→500KB)")
        reporter.success_step(execution_time=8.0, method="500KBに圧縮してアップロード")
    return reporter.finalize()


def demo_wordpress_posting():
    reporter = TaskReportGenerator("task_wp_001", "WordPress記事投稿", "記事作成→画像挿入→投稿")
    reporter.start_step(1, "記事コンテンツ生成")
    reporter.success_step(execution_time=15.3, method="Gemini API で記事生成")
    reporter.start_step(2, "アイキャッチ画像設定")
    reporter.success_step(execution_time=3.2, method="メディアライブラリから選択")
    reporter.start_step(3, "WordPress投稿")
    try:
        raise PermissionError("投稿権限エラー")
    except PermissionError as e:
        reporter.fail_step(e, root_cause="認証トークン期限切れ", error_type="PermissionError")
        reporter.retry_step("トークン再取得")
        reporter.success_step(execution_time=2.1, method="トークン更新後に投稿成功")
    return reporter.finalize()


def demo_code_generation():
    reporter = TaskReportGenerator(
        "task_code_001", "コード生成とテスト", "要件定義→コード生成→テスト"
    )
    reporter.start_step(1, "要件分析")
    reporter.success_step(execution_time=5.0, method="タスク分解と設計")
    reporter.start_step(2, "コード生成")
    try:
        raise SyntaxError("構文エラー: インデント不正")
    except SyntaxError as e:
        reporter.fail_step(e, root_cause="LLMが不適切なインデントを生成", error_type="SyntaxError")
        reporter.retry_step("プロンプト修正+全文再生成")
        reporter.success_step(execution_time=8.5, method="明示的なインデント指示を追加")
    reporter.start_step(3, "ユニットテスト実行")
    reporter.success_step(execution_time=3.0, method="pytest で全テスト合格")
    return reporter.finalize()


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("🎬 ナレッジベース統合システム デモ")
    print("=" * 80)
    print("\n【デモ1】画像処理タスク")
    report1 = demo_image_processing()
    print("\n【デモ2】WordPress記事投稿")
    report2 = demo_wordpress_posting()
    print("\n【デモ3】コード生成タスク")
    report3 = demo_code_generation()
    print("\n" + "=" * 80)
    print("📊 全デモの統計")
    print("=" * 80)
    total_knowledge = (
        len(report1.extracted_knowledge)
        + len(report2.extracted_knowledge)
        + len(report3.extracted_knowledge)
    )
    print(f"生成されたナレッジ: {total_knowledge}件")
    print(
        f"平均品質スコア: {(report1.quality_score + report2.quality_score + report3.quality_score) / 3:.1f}/10"
    )
    print(f"総リトライ回数: {report1.retry_count + report2.retry_count + report3.retry_count}回")
    print("\n✅ 全デモ完了")
    import json

    print("\n" + "=" * 80)
    print("📄 レポートJSON出力例")
    print("=" * 80)
    print(json.dumps(report1.to_dict(), ensure_ascii=False, indent=2)[:500] + "...")
