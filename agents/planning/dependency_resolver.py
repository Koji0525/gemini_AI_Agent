#!/usr/bin/env python3
"""
依存関係解決システム

目的: タスク間の依存関係を分析し、実行可能なタスクを特定

機能:
1. 依存関係の検証
2. 実行可能タスクの抽出
3. ブロッカーの検出
4. クリティカルパスの計算
"""

from typing import Dict, List, Set, Optional
import networkx as nx

class DependencyResolver:
    """
    依存関係解決システム
    
    責務:
    - 依存関係の検証
    - 実行可能タスクの特定
    - ブロッカー検出
    - クリティカルパス計算
    
    使用例:
        resolver = DependencyResolver(dag)
        
        # 実行可能なタスクを取得
        ready_tasks = resolver.get_ready_tasks()
        
        # ブロッカーを検出
        blockers = resolver.find_blockers()
    """
    
    def __init__(self, dag_manager):
        """
        初期化
        
        Args:
            dag_manager: DynamicDAGManagerインスタンス
        """
        self.dag = dag_manager
        self.graph = dag_manager.graph
    
    def get_ready_tasks(
        self,
        completed_tasks: Set[str] = None
    ) -> List[str]:
        """
        実行可能なタスクを取得
        
        Args:
            completed_tasks: 完了済みタスクのセット
        
        Returns:
            実行可能なタスクIDのリスト
        """
        if completed_tasks is None:
            completed_tasks = set()
        
        ready = []
        
        for task_id in self.graph.nodes():
            # すでに完了している場合はスキップ
            if task_id in completed_tasks:
                continue
            
            # 依存タスクを確認
            dependencies = list(self.graph.predecessors(task_id))
            
            # すべての依存タスクが完了している場合、実行可能
            if all(dep in completed_tasks for dep in dependencies):
                ready.append(task_id)
        
        return ready
    
    def find_blockers(
        self,
        target_task: str,
        completed_tasks: Set[str] = None
    ) -> List[str]:
        """
        特定タスクのブロッカーを検出
        
        Args:
            target_task: 対象タスクID
            completed_tasks: 完了済みタスクのセット
        
        Returns:
            ブロッカータスクIDのリスト
        """
        if completed_tasks is None:
            completed_tasks = set()
        
        if target_task not in self.graph:
            return []
        
        # target_taskに到達するすべてのパスを取得
        blockers = []
        
        for node in self.graph.nodes():
            if node in completed_tasks:
                continue
            
            # このノードがtarget_taskへのパス上にあるか確認
            if nx.has_path(self.graph, node, target_task):
                # 直接の依存関係のみをブロッカーとする
                if node in self.graph.predecessors(target_task):
                    blockers.append(node)
        
        return blockers
    
    def get_critical_path(self) -> List[str]:
        """
        クリティカルパスを計算
        
        Returns:
            クリティカルパス上のタスクIDのリスト
        """
        if self.graph.number_of_nodes() == 0:
            return []
        
        # 各ノードの所要時間を取得
        for node in self.graph.nodes():
            if 'estimated_duration_hours' not in self.graph.nodes[node]:
                self.graph.nodes[node]['estimated_duration_hours'] = 1
        
        # 最長パスを見つける（簡易実装）
        try:
            # トポロジカルソートで順序を取得
            order = list(nx.topological_sort(self.graph))
            
            # 最長パスの計算
            longest_path = []
            max_duration = 0
            
            for node in order:
                # このノードから始まるパスを計算
                paths = self._get_all_paths_from(node)
                for path in paths:
                    duration = sum(
                        self.graph.nodes[n].get('estimated_duration_hours', 1)
                        for n in path
                    )
                    if duration > max_duration:
                        max_duration = duration
                        longest_path = path
            
            return longest_path
            
        except:
            return []
    
    def _get_all_paths_from(self, start_node: str) -> List[List[str]]:
        """指定ノードから始まるすべてのパスを取得"""
        paths = []
        
        # 後続ノードがない場合
        successors = list(self.graph.successors(start_node))
        if not successors:
            return [[start_node]]
        
        # 各後続ノードへのパスを再帰的に取得
        for succ in successors:
            sub_paths = self._get_all_paths_from(succ)
            for sub_path in sub_paths:
                paths.append([start_node] + sub_path)
        
        return paths
    
    def validate_dependencies(self) -> Dict:
        """
        依存関係を検証
        
        Returns:
            検証結果
        """
        issues = []
        
        # 1. 循環参照チェック
        if not nx.is_directed_acyclic_graph(self.graph):
            try:
                cycle = nx.find_cycle(self.graph)
                issues.append({
                    'type': 'circular_dependency',
                    'severity': 'critical',
                    'message': f"循環参照が検出されました: {cycle}"
                })
            except:
                pass
        
        # 2. 孤立ノードチェック
        isolated = list(nx.isolates(self.graph))
        if isolated:
            issues.append({
                'type': 'isolated_tasks',
                'severity': 'warning',
                'message': f"孤立タスク: {isolated}"
            })
        
        # 3. 存在しない依存関係チェック
        for node in self.graph.nodes():
            for dep in self.graph.predecessors(node):
                if dep not in self.graph:
                    issues.append({
                        'type': 'missing_dependency',
                        'severity': 'error',
                        'message': f"{node} が存在しない依存 {dep} を参照"
                    })
        
        return {
            'is_valid': len([i for i in issues if i['severity'] == 'critical']) == 0,
            'issues': issues
        }
    
    def get_execution_plan(
        self,
        max_parallel: int = 10
    ) -> List[Dict]:
        """
        実行計画を生成
        
        Args:
            max_parallel: 最大並列実行数
        
        Returns:
            実行計画（各ステップの実行タスクリスト）
        """
        completed = set()
        plan = []
        
        while len(completed) < self.graph.number_of_nodes():
            # 実行可能なタスクを取得
            ready = self.get_ready_tasks(completed)
            
            if not ready:
                # デッドロック
                break
            
            # 並列実行数を制限
            batch = ready[:max_parallel]
            
            plan.append({
                'step': len(plan) + 1,
                'tasks': batch,
                'parallel_count': len(batch)
            })
            
            # 完了扱いにする
            completed.update(batch)
        
        return plan

# ========================================
# テスト
# ========================================
if __name__ == "__main__":
    print("="*60)
    print("🔗 DependencyResolver テスト")
    print("="*60)
    
    # DAG作成
    from agents.planning.dynamic_dag_manager import DynamicDAGManager
    
    dag = DynamicDAGManager(goal_id="test_resolver")
    
    # テストタスク追加
    dag.add_task("A", {"description": "タスクA", "estimated_duration_hours": 2})
    dag.add_task("B", {"description": "タスクB", "estimated_duration_hours": 3}, depends_on=["A"])
    dag.add_task("C", {"description": "タスクC", "estimated_duration_hours": 1}, depends_on=["A"])
    dag.add_task("D", {"description": "タスクD", "estimated_duration_hours": 2}, depends_on=["B", "C"])
    
    # Resolver作成
    resolver = DependencyResolver(dag)
    
    print("\n[1/5] 実行可能タスク取得...")
    ready = resolver.get_ready_tasks(completed_tasks=set())
    print(f"   実行可能: {ready}")
    
    print("\n[2/5] ブロッカー検出...")
    blockers = resolver.find_blockers("D", completed_tasks={"A"})
    print(f"   Dのブロッカー: {blockers}")
    
    print("\n[3/5] クリティカルパス...")
    critical = resolver.get_critical_path()
    print(f"   クリティカルパス: {' → '.join(critical)}")
    
    print("\n[4/5] 依存関係検証...")
    validation = resolver.validate_dependencies()
    print(f"   有効: {validation['is_valid']}")
    print(f"   問題: {len(validation['issues'])}件")
    
    print("\n[5/5] 実行計画生成...")
    plan = resolver.get_execution_plan(max_parallel=2)
    for step in plan:
        print(f"   ステップ{step['step']}: {', '.join(step['tasks'])} (並列数: {step['parallel_count']})")
    
    print("\n" + "="*60)
    print("✅ テスト完了")
    print("="*60)
