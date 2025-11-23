"""
重複ファイル検出モジュール

目的:
- ファイル名の類似度からバージョン違いファイルを検出
- pm_agent_v2.py, pm_agent_v3.py などの重複を特定
- 安全な削除候補を提案

設計方針:
- 既存システムに依存しない独立モジュール
- 読み取り専用（ファイルシステムへの変更なし）
"""

import re
from collections import defaultdict
from pathlib import Path
from typing import Dict, List


class DuplicateDetector:
    """重複ファイル検出器"""

    def __init__(self, project_root: Path):
        """
        初期化

        Args:
            project_root: プロジェクトルートディレクトリ
        """
        self.project_root = Path(project_root)

        # バージョン番号のパターン
        self.version_patterns = [
            r"_v(\d+)",  # _v2, _v30
            r"_(\d+)$",  # _2, _30
            r"\.v(\d+)\.",  # .v2.py
        ]

    def detect_duplicates(self, file_list: List[Path]) -> Dict[str, List[Dict]]:
        """
        重複ファイルを検出

        Args:
            file_list: 検査対象ファイルのリスト

        Returns:
            {
                "group_name": [
                    {
                        "path": "agents/pm_agent_v2.py",
                        "version": 2,
                        "size": 1200,
                        "last_modified": "2024-10-15",
                        "is_latest": False
                    },
                    ...
                ]
            }
        """
        # ベース名でグループ化
        grouped = self._group_by_base_name(file_list)

        # 重複グループのみ抽出（2個以上のファイルがあるグループ）
        duplicates = {}
        for base_name, files in grouped.items():
            if len(files) >= 2:
                duplicates[base_name] = self._analyze_duplicate_group(files)

        return duplicates

    def _group_by_base_name(self, file_list: List[Path]) -> Dict[str, List[Path]]:
        """
        ファイルをベース名でグループ化

        例: pm_agent_v2.py, pm_agent_v3.py → "pm_agent"グループ
        """
        groups = defaultdict(list)

        for file_path in file_list:
            base_name = self._extract_base_name(file_path.name)
            groups[base_name].append(file_path)

        return groups

    def _extract_base_name(self, filename: str) -> str:
        """
        ファイル名からベース名を抽出

        例:
        - pm_agent_v2.py → pm_agent
        - task_executor_v30.py → task_executor
        - sheets_manager.py → sheets_manager（変更なし）
        """
        # 拡張子を除去
        name_without_ext = filename.rsplit(".", 1)[0]

        # バージョン番号を除去
        for pattern in self.version_patterns:
            name_without_ext = re.sub(pattern, "", name_without_ext)

        return name_without_ext.rstrip("_")

    def _extract_version(self, filename: str) -> int:
        """
        ファイル名からバージョン番号を抽出

        Returns:
            バージョン番号（見つからない場合は0）
        """
        for pattern in self.version_patterns:
            match = re.search(pattern, filename)
            if match:
                return int(match.group(1))
        return 0

    def _analyze_duplicate_group(self, files: List[Path]) -> List[Dict]:
        """
        重複グループを分析

        - 最終更新日時を取得
        - ファイルサイズを取得
        - 最新バージョンを判定
        """
        file_info_list = []

        for file_path in files:
            try:
                stat = file_path.stat()
                version = self._extract_version(file_path.name)

                file_info_list.append(
                    {
                        "path": str(file_path.relative_to(self.project_root)),
                        "version": version,
                        "size": stat.st_size,
                        "last_modified": stat.st_mtime,
                        "is_latest": False,  # 後で更新
                    }
                )
            except Exception:
                # ファイルアクセスエラーは無視
                continue

        # 最新ファイルを判定（バージョン番号 → 更新日時の順）
        if file_info_list:
            sorted_by_version = sorted(
                file_info_list, key=lambda x: (x["version"], x["last_modified"]), reverse=True
            )
            sorted_by_version[0]["is_latest"] = True

        return file_info_list


def find_project_duplicates(project_root: str = "/workspaces/gemini_AI_Agent") -> Dict:
    """
    プロジェクト全体の重複ファイルを検出（便利関数）

    Returns:
        {
            "duplicates": {...},
            "summary": {
                "total_groups": 10,
                "total_files": 40,
                "candidates_for_removal": 30
            }
        }
    """
    detector = DuplicateDetector(Path(project_root))

    # Pythonファイルのみを対象
    python_files = list(Path(project_root).rglob("*.py"))

    # 除外ディレクトリ（既存の運用ルールに従う）
    exclude_dirs = {".git", "__pycache__", ".pytest_cache", "venv", "node_modules"}
    filtered_files = [
        f for f in python_files if not any(excluded in f.parts for excluded in exclude_dirs)
    ]

    # 重複検出
    duplicates = detector.detect_duplicates(filtered_files)

    # サマリー計算
    total_files = sum(len(group) for group in duplicates.values())
    candidates_for_removal = sum(
        len([f for f in group if not f["is_latest"]]) for group in duplicates.values()
    )

    return {
        "duplicates": duplicates,
        "summary": {
            "total_groups": len(duplicates),
            "total_files": total_files,
            "candidates_for_removal": candidates_for_removal,
        },
    }


# テスト実行用
if __name__ == "__main__":
    import json

    result = find_project_duplicates()
    print(json.dumps(result, indent=2, ensure_ascii=False))
