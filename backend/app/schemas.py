from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict


class _ORM(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# ---- requests ----
class CreateEmployeeRequest(BaseModel):
    description: str
    name: Optional[str] = None


class CorpusRequest(BaseModel):
    title: str = ""
    text: str


class EvaluateRequest(BaseModel):
    phase: str = "baseline"  # baseline | post_training
    training_run_id: Optional[int] = None


class TaskRequest(BaseModel):
    prompt: str


class LabelRequest(BaseModel):
    rating: str  # good | bad
    comment: str = ""
    labeler: str = "human"


class PromotionDecision(BaseModel):
    approve: bool
    expert: str = "expert"
    comment: str = ""


# ---- responses ----
class SkillOut(_ORM):
    id: int
    name: str
    description: str
    category: str
    proficiency: int
    source: str
    version: int


class StandardOut(_ORM):
    id: int
    name: str
    metrics: Any
    rubric: Any
    source: str
    version: int


class SOPOut(_ORM):
    id: int
    title: str
    steps: Any
    source: str
    version: int


class RuleOut(_ORM):
    id: int
    name: str
    rule_expr: str
    severity: str
    source: str
    version: int


class OutlineOut(_ORM):
    id: int
    content: Any


class EmployeeOut(_ORM):
    id: int
    name: str
    persona: str
    description: str
    avatar: Any
    level: int
    experience: int
    status: str
    created_at: datetime


class EmployeeDetailOut(EmployeeOut):
    outline: Optional[OutlineOut] = None
    skills: list[SkillOut] = []
    standards: list[StandardOut] = []
    sops: list[SOPOut] = []
    rules: list[RuleOut] = []


class LevelingOut(BaseModel):
    level: int
    experience: int
    exp_for_current: int
    exp_for_next: int
    progress: float
    needs_expert_approval: bool


class ExperienceLogOut(_ORM):
    id: int
    delta: int
    reason: str
    balance_after: int
    created_at: datetime


class CurvePoint(BaseModel):
    level: int
    cumulative_exp: int
    step_exp: int


class StatsOut(BaseModel):
    employees: int
    avg_level: float
    total_experience: int
    tasks: int
    labels_good: int
    labels_bad: int
    deposits: int
    pending_promotions: int


class EvaluationOut(_ORM):
    id: int
    phase: str
    score: float
    questions: Any
    answers: Any
    created_at: datetime


class EvaluationCompareOut(BaseModel):
    baseline: Optional[float] = None
    post_training: Optional[float] = None
    improved: Optional[bool] = None
    delta: Optional[float] = None


class PromotionOut(_ORM):
    id: int
    employee_id: int
    from_level: int
    to_level: int
    status: str
    expert: str
    comment: str
    created_at: datetime
