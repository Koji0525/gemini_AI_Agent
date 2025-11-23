
---

## 🔒 重要なインシデント履歴

### INCIDENT-2025-11-23-001: Flake8非Pythonファイル誤検証

**問題**: 3,000+個の非Pythonファイル（.sh, .json, .yaml, .mdなど）がFlake8で誤検証され、すべてのコミットが失敗

**解決策**: `_get_changed_python_files()` メソッドに拡張子フィルタを追加

**詳細**: `docs/incident_registry/incident_*_flake8_non_python_files.md` を参照

**重要度**: 🔴 Critical

**変更箇所**: このファイル内の `_get_changed_python_files()` メソッドのreturn文

⚠️ **この部分を変更する前に、必ずインシデント報告書を読んでください**

