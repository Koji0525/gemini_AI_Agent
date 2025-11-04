"""
拡張ナレッジベースマネージャー
標準レポートフォーマットに対応
"""

from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass, field, asdict
from enum import Enum


class StepStatus(Enum):
    SUCCESS = "✅ 成功"
    FAILED = "❌ 失敗"
    RETRY = "🔄 リトライ"
    PENDING = "⏳ 保留"


class KnowledgeType(Enum):
    BEST_PRACTICE = "best_practice"
    ERROR_FIX = "error_fix"
    COMMON_PITFALL = "common_pitfall"
    OPTIMIZATION = "optimization"


@dataclass
class ExecutionStep:
    step_number: int
    step_name: str
    status: StepStatus
    attempt_count: int = 1
    error_message: Optional[str] = None
    error_type: Optional[str] = None
    root_cause: Optional[str] = None
    solution: Optional[str] = None
    execution_time: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict:
        d = asdict(self)
        d["status"] = self.status.value
        return d


@dataclass
class KnowledgeEntry:
    knowledge_id: str
    knowledge_type: KnowledgeType
    scenario: str
    problem: Optional[str] = None
    solution: str = ""
    best_practice: str = ""
    avoid_patterns: List[str] = field(default_factory=list)
    success_rate: float = 0.0
    confidence: float = 0.0
    source_count: int = 1
    related_errors: List[str] = field(default_factory=list)
    execution_time_avg: float = 0.0
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict:
        d = asdict(self)
        d["knowledge_type"] = self.knowledge_type.value
        return d


@dataclass
class TaskReport:
    task_id: str
    task_name: str
    task_description: str
    start_time: str
    end_time: Optional[str] = None
    total_duration: float = 0.0
    final_status: StepStatus = StepStatus.PENDING
    steps: List[ExecutionStep] = field(default_factory=list)
    retry_count: int = 0
    quality_score: float = 0.0
    extracted_knowledge: List[KnowledgeEntry] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            "task_id": self.task_id,
            "task_name": self.task_name,
            "task_description": self.task_description,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "total_duration": self.total_duration,
            "final_status": self.final_status.value,
            "steps": [s.to_dict() for s in self.steps],
            "retry_count": self.retry_count,
            "quality_score": self.quality_score,
            "extracted_knowledge": [k.to_dict() for k in self.extracted_knowledge],
        }


class TaskReportGenerator:
    def __init__(self, task_id: str, task_name: str, task_description: str = ""):
        self.report = TaskReport(
            task_id=task_id,
            task_name=task_name,
            task_description=task_description,
            start_time=datetime.now().isoformat(),
        )
        self.current_step: Optional[ExecutionStep] = None
        self.step_start_time: Optional[datetime] = None
        print(f"\n{'='*80}")
        print(f"📊 タスクレポート生成開始")
        print(f"{'='*80}")
        print(f"タスクID: {task_id}")
        print(f"タスク名: {task_name}")

    def start_step(self, step_number: int, step_name: str):
        self.current_step = ExecutionStep(
            step_number=step_number, step_name=step_name, status=StepStatus.PENDING
        )
        self.step_start_time = datetime.now()
        print(f"\n{'='*60}")
        print(f"▶️  STEP {step_number}: {step_name}")
        print(f"{'='*60}")

    def success_step(self, execution_time: Optional[float] = None, method: str = ""):
        if not self.current_step:
            return
        if execution_time is None and self.step_start_time:
            execution_time = (datetime.now() - self.step_start_time).total_seconds()
        self.current_step.status = StepStatus.SUCCESS
        self.current_step.execution_time = execution_time or 0.0
        self.current_step.solution = method
        self.report.steps.append(self.current_step)
        print(f"✅ 成功 - {execution_time:.1f}秒")
        if method:
            print(f"   方法: {method}")

    def fail_step(self, error: Exception, root_cause: str = "", error_type: str = ""):
        if not self.current_step:
            return
        execution_time = 0.0
        if self.step_start_time:
            execution_time = (datetime.now() - self.step_start_time).total_seconds()
        self.current_step.status = StepStatus.FAILED
        self.current_step.error_message = str(error)
        self.current_step.error_type = error_type or type(error).__name__
        self.current_step.root_cause = root_cause
        self.current_step.execution_time = execution_time
        print(f"❌ 失敗 - {execution_time:.1f}秒")
        print(f"   エラー: {self.current_step.error_type}")
        if root_cause:
            print(f"   原因: {root_cause}")

    def retry_step(self, new_method: str = ""):
        if not self.current_step:
            return
        self.report.steps.append(self.current_step)
        self.report.retry_count += 1
        self.current_step = ExecutionStep(
            step_number=self.current_step.step_number,
            step_name=self.current_step.step_name,
            status=StepStatus.RETRY,
            attempt_count=self.current_step.attempt_count + 1,
        )
        self.step_start_time = datetime.now()
        print(f"\n🔄 リトライ {self.current_step.attempt_count}回目")
        if new_method:
            print(f"   新しい方法: {new_method}")

    def finalize(self) -> TaskReport:
        self.report.end_time = datetime.now().isoformat()
        start = datetime.fromisoformat(self.report.start_time)
        end = datetime.fromisoformat(self.report.end_time)
        self.report.total_duration = (end - start).total_seconds()
        if all(s.status == StepStatus.SUCCESS for s in self.report.steps):
            self.report.final_status = StepStatus.SUCCESS
        elif any(s.status == StepStatus.FAILED for s in self.report.steps):
            self.report.final_status = StepStatus.FAILED
        self.report.quality_score = self._calculate_quality_score()
        self.report.extracted_knowledge = self._extract_knowledge()
        self._print_report()
        return self.report

    def _calculate_quality_score(self) -> float:
        if not self.report.steps:
            return 0.0
        success_count = sum(1 for s in self.report.steps if s.status == StepStatus.SUCCESS)
        success_rate = success_count / len(self.report.steps)
        retry_penalty = min(self.report.retry_count * 0.5, 3.0)
        score = (success_rate * 10) - retry_penalty
        return max(0.0, min(10.0, score))

    def _extract_knowledge(self) -> List[KnowledgeEntry]:
        knowledge_list = []
        for step in self.report.steps:
            if step.status == StepStatus.SUCCESS and step.solution:
                knowledge = KnowledgeEntry(
                    knowledge_id=f"BP_{self.report.task_id}_{step.step_number}",
                    knowledge_type=KnowledgeType.BEST_PRACTICE,
                    scenario=f"{self.report.task_name} - {step.step_name}",
                    best_practice=step.solution,
                    success_rate=1.0,
                    confidence=0.8 if step.attempt_count == 1 else 0.6,
                    execution_time_avg=step.execution_time,
                )
                knowledge_list.append(knowledge)
            if step.status == StepStatus.FAILED and step.error_type:
                next_step = self._find_next_attempt(step)
                if next_step and next_step.status == StepStatus.SUCCESS:
                    knowledge = KnowledgeEntry(
                        knowledge_id=f"FIX_{self.report.task_id}_{step.step_number}",
                        knowledge_type=KnowledgeType.ERROR_FIX,
                        scenario=f"{step.step_name}時の{step.error_type}",
                        problem=step.error_message or "",
                        solution=next_step.solution or "リトライで解決",
                        success_rate=0.85,
                        confidence=0.7,
                        related_errors=[step.error_type],
                        execution_time_avg=next_step.execution_time,
                    )
                    knowledge_list.append(knowledge)
                if step.root_cause:
                    knowledge = KnowledgeEntry(
                        knowledge_id=f"PITFALL_{self.report.task_id}_{step.step_number}",
                        knowledge_type=KnowledgeType.COMMON_PITFALL,
                        scenario=f"{step.step_name}",
                        problem=step.error_message or "",
                        avoid_patterns=[step.root_cause],
                        success_rate=0.0,
                        confidence=0.9,
                        related_errors=[step.error_type],
                    )
                    knowledge_list.append(knowledge)
        return knowledge_list

    def _find_next_attempt(self, failed_step: ExecutionStep) -> Optional[ExecutionStep]:
        found_failed = False
        for step in self.report.steps:
            if step == failed_step:
                found_failed = True
            elif found_failed and step.step_number == failed_step.step_number:
                return step
        return None

    def _print_report(self):
        print(f"\n{'='*80}")
        print("📊 タスク実行レポート")
        print(f"{'='*80}")
        print(f"\n### 🎯 タスク概要")
        print(f"- **タスクID**: {self.report.task_id}")
        print(f"- **タスク名**: {self.report.task_name}")
        print(f"- **実行日時**: {self.report.start_time[:19]}")
        print(f"\n### 🔄 実行ステップ")
        current_step_num = None
        for step in self.report.steps:
            if step.step_number != current_step_num:
                print(f"\n#### STEP {step.step_number}: {step.step_name}")
                current_step_num = step.step_number
            print(f"\n**試行{step.attempt_count}**")
            print(f"- 状態: {step.status.value}")
            if step.error_message:
                print(f"- エラー: {step.error_type}")
                if step.root_cause:
                    print(f"- 原因: {step.root_cause}")
            if step.solution:
                print(f"- 方法: {step.solution}")
            print(f"- 所要時間: {step.execution_time:.1f}秒")
            if step.status == StepStatus.SUCCESS and step.solution:
                print(f"\n📋 **学習ポイント**")
                print(f"- ナレッジタイプ: best_practice")
                print(f"- シナリオ: {step.step_name}")
                print(f"- ベストプラクティス: {step.solution}")
                confidence = 0.8 if step.attempt_count == 1 else 0.6
                print(f"- 信頼度: {confidence*100:.0f}%")
        print(f"\n### 📊 総合結果")
        print(
            f"{self.report.final_status.value} **最終ステータス**: {self.report.final_status.name}"
        )
        print(f"⏱️ **総実行時間**: {self.report.total_duration:.1f}秒")
        print(f"🔄 **リトライ回数**: {self.report.retry_count}回")
        print(f"⭐ **品質スコア**: {self.report.quality_score:.1f}/10")
        print(f"\n### 🎓 今回のタスクから学んだこと")
        success_knowledge = [
            k
            for k in self.report.extracted_knowledge
            if k.knowledge_type == KnowledgeType.BEST_PRACTICE
        ]
        error_knowledge = [
            k
            for k in self.report.extracted_knowledge
            if k.knowledge_type == KnowledgeType.ERROR_FIX
        ]
        pitfall_knowledge = [
            k
            for k in self.report.extracted_knowledge
            if k.knowledge_type == KnowledgeType.COMMON_PITFALL
        ]
        if success_knowledge:
            print(f"\n#### ✅ 成功パターン（再現可能）")
            for i, k in enumerate(success_knowledge, 1):
                print(f"{i}. **{k.scenario}**: {k.best_practice} （信頼度{k.confidence*100:.0f}%）")
        if pitfall_knowledge:
            print(f"\n#### ❌ 失敗パターン（避けるべき）")
            for i, k in enumerate(pitfall_knowledge, 1):
                print(f"{i}. **{k.scenario}**: {', '.join(k.avoid_patterns)}")
        if error_knowledge:
            print(f"\n#### 💡 エラー修正方法")
            for i, k in enumerate(error_knowledge, 1):
                print(f"{i}. **{k.scenario}**: {k.solution}")


if __name__ == "__main__":
    print("✅ EnhancedKnowledgeManager モジュール読み込み完了")
