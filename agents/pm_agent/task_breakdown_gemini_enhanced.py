"""
task_breakdown_gemini.pyのJSONパース強化版
"""

import re
import json
from typing import List, Dict, Any


def _clean_json_string(json_str: str) -> str:
    """JSON文字列から制御文字を除去"""
    # 制御文字を除去（改行、タブ、復帰以外）
    cleaned = re.sub(r"[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F]", "", json_str)

    # 複数の改行を1つに
    cleaned = re.sub(r"\n+", "\n", cleaned)

    return cleaned


def _extract_json_from_response(response_text: str) -> str:
    """Gemini応答からJSON部分を抽出"""
    # パターン1: ```json ... ```
    json_match = re.search(r"```json\s*(\[.*?\])\s*```", response_text, re.DOTALL)
    if json_match:
        return json_match.group(1)

    # パターン2: ``` ... ``` (json指定なし)
    json_match = re.search(r"```\s*(\[.*?\])\s*```", response_text, re.DOTALL)
    if json_match:
        return json_match.group(1)

    # パターン3: [...] のみ
    json_match = re.search(r"(\[.*\])", response_text, re.DOTALL)
    if json_match:
        return json_match.group(1)

    return ""


def parse_gemini_response_robust(response_text: str, goal_id: str) -> List[Dict[str, Any]]:
    """Gemini応答を堅牢にパース"""
    try:
        # JSON部分を抽出
        json_str = _extract_json_from_response(response_text)
        if not json_str:
            print("⚠️ JSON部分が見つかりません")
            return _parse_text_fallback(response_text, goal_id)

        # クリーニング
        json_str = _clean_json_string(json_str)
        print(f"🔧 クリーニング後のJSON: {json_str[:200]}...")

        # パース実行
        tasks_data = json.loads(json_str)

        # タスクデータを整形
        formatted_tasks = []
        for i, task in enumerate(tasks_data, 1):
            formatted_task = {
                "goal_id": goal_id,
                "task_number": i,
                "title": task.get("title", f"タスク{i}"),
                "description": task.get("description", ""),
                "agent": task.get("agent", "dev"),
                "priority": task.get("priority", "medium"),
                "dependencies": task.get("dependencies", ""),
                "execution_type": task.get("execution_type", "gemini"),
                "estimated_hours": task.get("estimated_hours", 8),
            }
            formatted_tasks.append(formatted_task)

        print(f"✅ {len(formatted_tasks)}個のタスクをパース成功")
        return formatted_tasks

    except json.JSONDecodeError as e:
        print(f"❌ JSONパースエラー: {e}")
        return _parse_text_fallback(response_text, goal_id)
    except Exception as e:
        print(f"❌ パースエラー: {e}")
        return []


def _parse_text_fallback(response_text: str, goal_id: str) -> List[Dict[str, Any]]:
    """テキストベースのフォールバックパース"""
    print("🔄 テキストベースのパースを試行...")

    tasks = []

    # タスクのパターンを検出
    task_patterns = [
        r"(?:タスク|Task)\s*(\d+)[：:]\s*(.+?)(?=\n|$)",
        r'"title"\s*:\s*"([^"]+)"',
        r"title\s*:\s*([^\n]+)",
    ]

    for pattern in task_patterns:
        matches = re.finditer(pattern, response_text)
        for i, match in enumerate(matches, 1):
            title = match.group(1) if len(match.groups()) >= 1 else match.group(0)

            task = {
                "goal_id": goal_id,
                "task_number": i,
                "title": title.strip(),
                "description": f"【目的】\n{title}を実行する\n\n【完了判定】\n✅ タスクが完了していること",
                "agent": "dev",
                "priority": "medium",
                "dependencies": "",
                "execution_type": "gemini",
                "estimated_hours": 8,
            }
            tasks.append(task)

        if tasks:
            break

    print(f"✅ {len(tasks)}個のタスクをテキスト抽出")
    return tasks
