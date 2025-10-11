"""
DependencyResolver - 依存関係解決と管理エージェント

パッケージ依存関係の分析、競合の検出と解決、バージョン互換性チェック、
自動アップデート提案、依存関係グラフの生成を提供する。
"""

import subprocess
import json
import re
from pathlib import Path
from typing import Dict, Any, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class DependencyStatus(Enum):
    """依存関係ステータス"""
    SATISFIED = "satisfied"
    MISSING = "missing"
    OUTDATED = "outdated"
    CONFLICT = "conflict"
    INCOMPATIBLE = "incompatible"


@dataclass
class Package:
    """パッケージ情報"""
    name: str
    installed_version: Optional[str] = None
    required_version: Optional[str] = None
    latest_version: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "installed_version": self.installed_version,
            "required_version": self.required_version,
            "latest_version": self.latest_version,
            "dependencies": self.dependencies
        }


@dataclass
class DependencyIssue:
    """依存関係の問題"""
    status: DependencyStatus
    package: Package
    description: str
    resolution: Optional[str] = None
    severity: str = "medium"  # low, medium, high, critical
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status.value,
            "package": self.package.to_dict(),
            "description": self.description,
            "resolution": self.resolution,
            "severity": self.severity
        }


@dataclass
class DependencyGraph:
    """依存関係グラフ"""
    nodes: Dict[str, Package]
    edges: List[Tuple[str, str]]  # (from_package, to_package)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "nodes": {name: pkg.to_dict() for name, pkg in self.nodes.items()},
            "edges": [{"from": f, "to": t} for f, t in self.edges]
        }


class DependencyResolverAgent:
    """
    依存関係解決と管理エージェント
    
    主な機能:
    1. パッケージ依存関係の分析
    2. バージョン競合の検出と解決
    3. バージョン互換性チェック
    4. 自動アップデート提案
    5. 依存関係グラフの生成
    """
    
    def __init__(self, requirements_file: str = "requirements.txt"):
        self.requirements_file = requirements_file
        
        # パッケージ情報
        self.packages: Dict[str, Package] = {}
        self.issues: List[DependencyIssue] = []
        
        # 統計情報
        self.stats = {
            "total_packages": 0,
            "satisfied": 0,
            "missing": 0,
            "outdated": 0,
            "conflicts": 0
        }
        
        logger.info("DependencyResolverAgent initialized")
    
    def analyze_dependencies(self) -> List[DependencyIssue]:
        """
        依存関係を分析
        
        Returns:
            検出された問題のリスト
        """
        self.issues = []
        self.packages = {}
        
        # requirements.txtを読み込む
        required_packages = self._parse_requirements()
        
        # インストール済みパッケージを取得
        installed_packages = self._get_installed_packages()
        
        # 各パッケージを分析
        for pkg_spec in required_packages:
            pkg_name, version_spec = self._parse_package_spec(pkg_spec)
            
            package = Package(
                name=pkg_name,
                required_version=version_spec
            )
            
            # インストール状況をチェック
            if pkg_name in installed_packages:
                package.installed_version = installed_packages[pkg_name]
                
                # バージョン互換性をチェック
                if not self._is_version_compatible(
                    package.installed_version,
                    version_spec
                ):
                    issue = DependencyIssue(
                        status=DependencyStatus.INCOMPATIBLE,
                        package=package,
                        description=f"Installed version {package.installed_version} "
                                  f"does not satisfy requirement {version_spec}",
                        resolution=f"pip install {pkg_name}{version_spec}",
                        severity="high"
                    )
                    self.issues.append(issue)
                    self.stats["conflicts"] += 1
                else:
                    self.stats["satisfied"] += 1
            else:
                # パッケージが未インストール
                issue = DependencyIssue(
                    status=DependencyStatus.MISSING,
                    package=package,
                    description=f"Package {pkg_name} is not installed",
                    resolution=f"pip install {pkg_spec}",
                    severity="critical"
                )
                self.issues.append(issue)
                self.stats["missing"] += 1
            
            self.packages[pkg_name] = package
            self.stats["total_packages"] += 1
        
        # 最新バージョンをチェック
        self._check_latest_versions()
        
        # 依存関係の依存をチェック
        self._check_transitive_dependencies()
        
        return self.issues
    
    def _parse_requirements(self) -> List[str]:
        """requirements.txtをパース"""
        if not Path(self.requirements_file).exists():
            logger.warning(f"Requirements file not found: {self.requirements_file}")
            return []
        
        requirements = []
        with open(self.requirements_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # コメントと空行をスキップ
                if line and not line.startswith('#'):
                    requirements.append(line)
        
        return requirements
    
    def _get_installed_packages(self) -> Dict[str, str]:
        """インストール済みパッケージの一覧を取得"""
        try:
            result = subprocess.run(
                ['pip', 'list', '--format=json'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                packages_data = json.loads(result.stdout)
                return {
                    pkg['name'].lower(): pkg['version']
                    for pkg in packages_data
                }
        except Exception as e:
            logger.error(f"Failed to get installed packages: {e}")
        
        return {}
    
    def _parse_package_spec(self, spec: str) -> Tuple[str, Optional[str]]:
        """
        パッケージ指定をパース
        
        例: "package==1.0.0" -> ("package", "==1.0.0")
        """
        # バージョン指定子を抽出
        match = re.match(r'^([a-zA-Z0-9_-]+)(.*)$', spec)
        if match:
            name = match.group(1).lower()
            version_spec = match.group(2).strip() if match.group(2) else None
            return name, version_spec
        
        return spec.lower(), None
    
    def _is_version_compatible(self, 
                              installed: str,
                              required: Optional[str]) -> bool:
        """
        バージョン互換性をチェック
        
        簡易版の実装（より正確にはpackaging.specifiersを使用すべき）
        """
        if not required:
            return True
        
        # ==, >=, <=, >, <, != などの演算子をパース
        operators = ['==', '>=', '<=', '>', '<', '!=', '~=']
        
        for op in operators:
            if op in required:
                version = required.replace(op, '').strip()
                return self._compare_versions(installed, version, op)
        
        return True
    
    def _compare_versions(self, v1: str, v2: str, op: str) -> bool:
        """バージョンを比較"""
        try:
            # バージョンを数値のタプルに変換
            v1_parts = tuple(int(x) for x in v1.split('.'))
            v2_parts = tuple(int(x) for x in v2.split('.'))
            
            if op == '==':
                return v1_parts == v2_parts
            elif op == '>=':
                return v1_parts >= v2_parts
            elif op == '<=':
                return v1_parts <= v2_parts
            elif op == '>':
                return v1_parts > v2_parts
            elif op == '<':
                return v1_parts < v2_parts
            elif op == '!=':
                return v1_parts != v2_parts
            elif op == '~=':
                # Compatible release (PEP 440)
                # ~=1.4.5 は >=1.4.5, <1.5.0 と同等
                return v1_parts >= v2_parts and v1_parts[0] == v2_parts[0]
        except:
            # バージョン比較に失敗した場合はTrueを返す
            return True
        
        return True
    
    def _check_latest_versions(self):
        """最新バージョンをチェック"""
        for pkg_name, package in self.packages.items():
            if not package.installed_version:
                continue
            
            try:
                # PyPIから最新バージョンを取得
                result = subprocess.run(
                    ['pip', 'index', 'versions', pkg_name],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode == 0:
                    # 出力から最新バージョンを抽出
                    match = re.search(r'Available versions: ([\d.]+)', result.stdout)
                    if match:
                        latest = match.group(1)
                        package.latest_version = latest
                        
                        # アップデート可能かチェック
                        if self._compare_versions(package.installed_version, latest, '<'):
                            issue = DependencyIssue(
                                status=DependencyStatus.OUTDATED,
                                package=package,
                                description=f"Package {pkg_name} can be updated from "
                                          f"{package.installed_version} to {latest}",
                                resolution=f"pip install --upgrade {pkg_name}",
                                severity="low"
                            )
                            self.issues.append(issue)
                            self.stats["outdated"] += 1
            except Exception as e:
                logger.debug(f"Failed to check latest version for {pkg_name}: {e}")
    
    def _check_transitive_dependencies(self):
        """推移的依存関係をチェック"""
        for pkg_name, package in self.packages.items():
            if not package.installed_version:
                continue
            
            try:
                # パッケージの依存関係を取得
                result = subprocess.run(
                    ['pip', 'show', pkg_name],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode == 0:
                    # Requires行から依存関係を抽出
                    for line in result.stdout.split('\n'):
                        if line.startswith('Requires:'):
                            deps = line.replace('Requires:', '').strip()
                            if deps:
                                package.dependencies = [
                                    d.strip() for d in deps.split(',')
                                ]
            except Exception as e:
                logger.debug(f"Failed to check dependencies for {pkg_name}: {e}")
    
    def detect_conflicts(self) -> List[DependencyIssue]:
        """バージョン競合を検出"""
        conflicts = []
        
        # すべてのパッケージの依存関係をチェック
        dependency_requirements = {}
        
        for pkg_name, package in self.packages.items():
            for dep in package.dependencies:
                dep_name, dep_version = self._parse_package_spec(dep)
                
                if dep_name not in dependency_requirements:
                    dependency_requirements[dep_name] = []
                
                dependency_requirements[dep_name].append({
                    'required_by': pkg_name,
                    'version_spec': dep_version
                })
        
        # 競合をチェック
        for dep_name, requirements in dependency_requirements.items():
            if len(requirements) > 1:
                # 複数のバージョン要求がある場合、競合の可能性
                version_specs = [req['version_spec'] for req in requirements]
                if len(set(version_specs)) > 1:
                    package = self.packages.get(dep_name, Package(name=dep_name))
                    
                    issue = DependencyIssue(
                        status=DependencyStatus.CONFLICT,
                        package=package,
                        description=f"Version conflict for {dep_name}: "
                                  f"required by {', '.join(req['required_by'] for req in requirements)} "
                                  f"with different version specs",
                        resolution="Manually resolve version requirements",
                        severity="high"
                    )
                    conflicts.append(issue)
        
        return conflicts
    
    def generate_dependency_graph(self) -> DependencyGraph:
        """依存関係グラフを生成"""
        nodes = {}
        edges = []
        
        for pkg_name, package in self.packages.items():
            nodes[pkg_name] = package
            
            for dep in package.dependencies:
                dep_name, _ = self._parse_package_spec(dep)
                edges.append((pkg_name, dep_name))
        
        return DependencyGraph(nodes=nodes, edges=edges)
    
    def suggest_updates(self) -> List[Dict[str, Any]]:
        """
        アップデート推奨を生成
        
        Returns:
            アップデート推奨のリスト
        """
        suggestions = []
        
        for issue in self.issues:
            if issue.status == DependencyStatus.OUTDATED:
                pkg = issue.package
                suggestions.append({
                    "package": pkg.name,
                    "current_version": pkg.installed_version,
                    "latest_version": pkg.latest_version,
                    "command": issue.resolution,
                    "priority": self._calculate_update_priority(pkg)
                })
        
        # 優先度でソート
        suggestions.sort(key=lambda x: x["priority"], reverse=True)
        
        return suggestions
    
    def _calculate_update_priority(self, package: Package) -> int:
        """アップデート優先度を計算（0-100）"""
        if not package.installed_version or not package.latest_version:
            return 0
        
        try:
            current_parts = tuple(int(x) for x in package.installed_version.split('.'))
            latest_parts = tuple(int(x) for x in package.latest_version.split('.'))
            
            # メジャーバージョンが異なる: 高優先度
            if current_parts[0] < latest_parts[0]:
                return 90
            
            # マイナーバージョンが異なる: 中優先度
            if len(current_parts) > 1 and len(latest_parts) > 1:
                if current_parts[1] < latest_parts[1]:
                    return 60
            
            # パッチバージョンのみ: 低優先度
            return 30
        except:
            return 50  # デフォルト
    
    def generate_report(self) -> Dict[str, Any]:
        """分析レポートを生成"""
        # 重大度別の問題
        by_severity = {
            "critical": [],
            "high": [],
            "medium": [],
            "low": []
        }
        
        for issue in self.issues:
            by_severity[issue.severity].append(issue.to_dict())
        
        # 依存関係グラフ
        graph = self.generate_dependency_graph()
        
        return {
            "summary": {
                **self.stats,
                "total_issues": len(self.issues)
            },
            "issues_by_severity": {
                severity: len(issues)
                for severity, issues in by_severity.items()
            },
            "issues": [issue.to_dict() for issue in self.issues],
            "update_suggestions": self.suggest_updates(),
            "dependency_graph": graph.to_dict()
        }
    
    def export_report(self, filepath: str):
        """レポートをファイルにエクスポート"""
        report = self.generate_report()
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Dependency report exported to {filepath}")
    
    def auto_fix_issues(self, 
                       fix_missing: bool = True,
                       fix_outdated: bool = False) -> List[str]:
        """
        問題を自動修正
        
        Args:
            fix_missing: 欠落パッケージをインストール
            fix_outdated: 古いパッケージをアップデート
        
        Returns:
            実行されたコマンドのリスト
        """
        executed_commands = []
        
        for issue in self.issues:
            if not issue.resolution:
                continue
            
            should_fix = False
            
            if fix_missing and issue.status == DependencyStatus.MISSING:
                should_fix = True
            elif fix_outdated and issue.status == DependencyStatus.OUTDATED:
                should_fix = True
            
            if should_fix:
                try:
                    logger.info(f"Executing: {issue.resolution}")
                    result = subprocess.run(
                        issue.resolution.split(),
                        capture_output=True,
                        text=True,
                        timeout=300
                    )
                    
                    if result.returncode == 0:
                        executed_commands.append(issue.resolution)
                        logger.info(f"Successfully fixed: {issue.package.name}")
                    else:
                        logger.error(f"Failed to fix {issue.package.name}: {result.stderr}")
                except Exception as e:
                    logger.error(f"Error fixing {issue.package.name}: {e}")
        
        return executed_commands


# 使用例
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    resolver = DependencyResolverAgent("requirements.txt")
    
    # 依存関係を分析
    print("\n=== Analyzing Dependencies ===")
    issues = resolver.analyze_dependencies()
    
    print(f"\nFound {len(issues)} issues:")
    for issue in issues[:5]:  # 最初の5件を表示
        print(f"[{issue.status.value}] {issue.package.name}: {issue.description}")
        if issue.resolution:
            print(f"  → {issue.resolution}")
    
    # レポート生成
    print("\n=== Dependency Report ===")
    report = resolver.generate_report()
    print(json.dumps(report["summary"], indent=2))
    
    # アップデート推奨
    print("\n=== Update Suggestions ===")
    suggestions = resolver.suggest_updates()
    for sugg in suggestions[:3]:
        print(f"{sugg['package']}: {sugg['current_version']} → {sugg['latest_version']}")
        print(f"  Priority: {sugg['priority']}/100")
        print(f"  Command: {sugg['command']}")
