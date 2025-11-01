#!/usr/bin/env python3
"""
パターン抽出ロジック

UnifiedLogEntryからパターンを抽出
"""

import re
from typing import List, Dict, Any
from collections import Counter
from dataclasses import dataclass

from tools.data_integration.models import UnifiedLogEntry


@dataclass
class PatternResult:
    """パターン抽出結果"""

    name: str
    confidence: float
    examples: List[str]
    count: int


class PatternExtractor:
    """パターン抽出器"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config

    def extract_all_patterns(self, entries: List[UnifiedLogEntry]) -> Dict[str, List[PatternResult]]:
        """全パターンを抽出"""
        return {
            "failure_patterns": self.extract_failure_patterns(entries),
            "fix_recipes": self.extract_fix_recipes(entries),
            "success_patterns": self.extract_success_patterns(entries),
        }

    def extract_failure_patterns(self, entries: List[UnifiedLogEntry]) -> List[PatternResult]:
        """失敗パターンを抽出"""
        config = self.config.get("failure_patterns", {})
        min_confidence = config.get("min_confidence", 0.6)
        keywords = config.get("keywords", [])

        # エラー関連エントリを抽出
        error_entries = [
            entry
            for entry in entries
            if entry.content_type.value == "error" or any(keyword in entry.content.lower() for keyword in keywords)
        ]

        # エラーパターンを分析
        error_patterns = self._analyze_error_patterns(error_entries, keywords)

        # 信頼度でフィルタリング
        return [
            PatternResult(
                name=pattern["name"],
                confidence=pattern["confidence"],
                examples=pattern["examples"][:5],  # 最大5例
                count=pattern["count"],
            )
            for pattern in error_patterns
            if pattern["confidence"] >= min_confidence
        ]

    def extract_fix_recipes(self, entries: List[UnifiedLogEntry]) -> List[PatternResult]:
        """修正レシピを抽出"""
        config = self.config.get("fix_recipes", {})
        min_confidence = config.get("min_confidence", 0.7)
        success_indicators = config.get("success_indicators", [])

        # 成功関連エントリを抽出
        success_entries = [
            entry for entry in entries if any(indicator in entry.content.lower() for indicator in success_indicators)
        ]

        # 修正パターンを分析
        fix_patterns = self._analyze_fix_patterns(success_entries, success_indicators)

        # 信頼度でフィルタリング
        return [
            PatternResult(
                name=pattern["name"],
                confidence=pattern["confidence"],
                examples=pattern["examples"][:5],
                count=pattern["count"],
            )
            for pattern in fix_patterns
            if pattern["confidence"] >= min_confidence
        ]

    def extract_success_patterns(self, entries: List[UnifiedLogEntry]) -> List[PatternResult]:
        """成功パターンを抽出"""
        config = self.config.get("success_patterns", {})
        min_confidence = config.get("min_confidence", 0.8)
        keywords = config.get("keywords", [])

        # 成功関連エントリを抽出
        success_entries = [entry for entry in entries if any(keyword in entry.content.lower() for keyword in keywords)]

        # 成功パターンを分析
        success_patterns = self._analyze_success_patterns(success_entries, keywords)

        # 信頼度でフィルタリング
        return [
            PatternResult(
                name=pattern["name"],
                confidence=pattern["confidence"],
                examples=pattern["examples"][:5],
                count=pattern["count"],
            )
            for pattern in success_patterns
            if pattern["confidence"] >= min_confidence
        ]

    def _analyze_error_patterns(self, entries: List[UnifiedLogEntry], keywords: List[str]) -> List[Dict[str, Any]]:
        """エラーパターンを分析"""
        if not entries:
            return []

        # エラー内容を分析
        error_contents = [entry.content for entry in entries]

        # キーワードベースのパターン抽出
        patterns = []

        # 1. 認証エラー
        auth_errors = [
            content
            for content in error_contents
            if any(word in content.lower() for word in ["auth", "credential", "permission", "access"])
        ]
        if auth_errors:
            patterns.append(
                {
                    "name": "認証・権限エラー",
                    "confidence": min(0.9, len(auth_errors) / len(entries)),
                    "examples": auth_errors[:3],
                    "count": len(auth_errors),
                }
            )

        # 2. ネットワークエラー
        network_errors = [
            content
            for content in error_contents
            if any(word in content.lower() for word in ["network", "timeout", "connection", "socket"])
        ]
        if network_errors:
            patterns.append(
                {
                    "name": "ネットワーク・タイムアウトエラー",
                    "confidence": min(0.8, len(network_errors) / len(entries)),
                    "examples": network_errors[:3],
                    "count": len(network_errors),
                }
            )

        # 3. データ形式エラー
        format_errors = [
            content
            for content in error_contents
            if any(word in content.lower() for word in ["format", "json", "parsing", "syntax"])
        ]
        if format_errors:
            patterns.append(
                {
                    "name": "データ形式・パースエラー",
                    "confidence": min(0.7, len(format_errors) / len(entries)),
                    "examples": format_errors[:3],
                    "count": len(format_errors),
                }
            )

        # 4. API制限エラー
        api_errors = [
            content
            for content in error_contents
            if any(word in content.lower() for word in ["api", "quota", "limit", "rate"])
        ]
        if api_errors:
            patterns.append(
                {
                    "name": "API制限・クォータエラー",
                    "confidence": min(0.75, len(api_errors) / len(entries)),
                    "examples": api_errors[:3],
                    "count": len(api_errors),
                }
            )

        return patterns

    def _analyze_fix_patterns(self, entries: List[UnifiedLogEntry], indicators: List[str]) -> List[Dict[str, Any]]:
        """修正パターンを分析"""
        if not entries:
            return []

        fix_contents = [entry.content for entry in entries]

        patterns = []

        # 1. 再試行成功
        retry_fixes = [
            content
            for content in fix_contents
            if any(word in content.lower() for word in ["retry", "再試行", "再実行"])
        ]
        if retry_fixes:
            patterns.append(
                {
                    "name": "再試行による解決",
                    "confidence": min(0.85, len(retry_fixes) / len(entries)),
                    "examples": retry_fixes[:3],
                    "count": len(retry_fixes),
                }
            )

        # 2. 設定変更
        config_fixes = [
            content
            for content in fix_contents
            if any(word in content.lower() for word in ["config", "setting", "設定"])
        ]
        if config_fixes:
            patterns.append(
                {
                    "name": "設定変更による解決",
                    "confidence": min(0.8, len(config_fixes) / len(entries)),
                    "examples": config_fixes[:3],
                    "count": len(config_fixes),
                }
            )

        # 3. コード修正
        code_fixes = [
            content
            for content in fix_contents
            if any(word in content.lower() for word in ["code", "fix", "修正", "bug"])
        ]
        if code_fixes:
            patterns.append(
                {
                    "name": "コード修正による解決",
                    "confidence": min(0.9, len(code_fixes) / len(entries)),
                    "examples": code_fixes[:3],
                    "count": len(code_fixes),
                }
            )

        return patterns

    def _analyze_success_patterns(self, entries: List[UnifiedLogEntry], keywords: List[str]) -> List[Dict[str, Any]]:
        """成功パターンを分析"""
        if not entries:
            return []

        success_contents = [entry.content for entry in entries]

        patterns = []

        # 1. 自動化成功
        auto_success = [
            content
            for content in success_contents
            if any(word in content.lower() for word in ["auto", "automation", "自動"])
        ]
        if auto_success:
            patterns.append(
                {
                    "name": "自動化処理成功",
                    "confidence": min(0.95, len(auto_success) / len(entries)),
                    "examples": auto_success[:3],
                    "count": len(auto_success),
                }
            )

        # 2. バッチ処理成功
        batch_success = [
            content
            for content in success_contents
            if any(word in content.lower() for word in ["batch", "一括", "bulk"])
        ]
        if batch_success:
            patterns.append(
                {
                    "name": "バッチ処理成功",
                    "confidence": min(0.9, len(batch_success) / len(entries)),
                    "examples": batch_success[:3],
                    "count": len(batch_success),
                }
            )

        # 3. データ統合成功
        integration_success = [
            content
            for content in success_contents
            if any(word in content.lower() for word in ["integration", "統合", "merge"])
        ]
        if integration_success:
            patterns.append(
                {
                    "name": "データ統合成功",
                    "confidence": min(0.85, len(integration_success) / len(entries)),
                    "examples": integration_success[:3],
                    "count": len(integration_success),
                }
            )

        return patterns
