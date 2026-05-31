from datetime import datetime

from sqlalchemy import (
    JSON,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from .database import Base


def _now():
    return datetime.utcnow()


class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    persona = Column(Text, default="")
    description = Column(Text, default="")  # original natural-language brief
    avatar = Column(JSON, default=dict)  # {style, color, emoji, image_url}
    level = Column(Integer, default=1)
    experience = Column(Integer, default=0)
    status = Column(String, default="active")
    created_at = Column(DateTime, default=_now)

    outline = relationship("WorkOutline", back_populates="employee", uselist=False, cascade="all, delete-orphan")
    skills = relationship("Skill", back_populates="employee", cascade="all, delete-orphan")
    standards = relationship("WorkStandard", back_populates="employee", cascade="all, delete-orphan")
    sops = relationship("SOP", back_populates="employee", cascade="all, delete-orphan")
    rules = relationship("DataQualityRule", back_populates="employee", cascade="all, delete-orphan")


class WorkOutline(Base):
    __tablename__ = "work_outlines"

    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))
    content = Column(JSON, default=dict)  # {responsibilities, goals, scope}
    created_at = Column(DateTime, default=_now)

    employee = relationship("Employee", back_populates="outline")


class Skill(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))
    name = Column(String, nullable=False)
    description = Column(Text, default="")
    category = Column(String, default="general")
    proficiency = Column(Integer, default=1)
    source = Column(String, default="generated")  # generated | trained | deposited
    version = Column(Integer, default=1)
    created_at = Column(DateTime, default=_now)

    employee = relationship("Employee", back_populates="skills")


class WorkStandard(Base):
    __tablename__ = "work_standards"

    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))
    name = Column(String, nullable=False)
    metrics = Column(JSON, default=list)
    rubric = Column(JSON, default=dict)
    source = Column(String, default="generated")
    version = Column(Integer, default=1)
    created_at = Column(DateTime, default=_now)

    employee = relationship("Employee", back_populates="standards")


class SOP(Base):
    __tablename__ = "sops"

    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))
    title = Column(String, nullable=False)
    steps = Column(JSON, default=list)
    source = Column(String, default="generated")
    version = Column(Integer, default=1)
    created_at = Column(DateTime, default=_now)

    employee = relationship("Employee", back_populates="sops")


class DataQualityRule(Base):
    __tablename__ = "data_quality_rules"

    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))
    name = Column(String, nullable=False)
    rule_expr = Column(Text, default="")
    severity = Column(String, default="medium")
    source = Column(String, default="deposited")
    version = Column(Integer, default=1)
    created_at = Column(DateTime, default=_now)

    employee = relationship("Employee", back_populates="rules")


class TrainingCorpus(Base):
    __tablename__ = "training_corpus"

    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))
    title = Column(String, default="")
    raw_text = Column(Text, default="")
    # Supervised-signal fields for the "distill Triston" use case.
    # label: "pass" | "fail" | None (plain unlabeled text still supported).
    # split: "train" (default) | "test" — the employee only trains on train.
    label = Column(String, nullable=True)
    feedback = Column(Text, default="")
    split = Column(String, default="train")
    created_at = Column(DateTime, default=_now)


class CorpusChunk(Base):
    __tablename__ = "corpus_chunks"

    id = Column(Integer, primary_key=True)
    corpus_id = Column(Integer, ForeignKey("training_corpus.id"))
    text = Column(Text, default="")
    idx = Column(Integer, default=0)


class TrainingRun(Base):
    __tablename__ = "training_runs"

    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))
    corpus_ids = Column(JSON, default=list)
    status = Column(String, default="completed")
    summary = Column(Text, default="")
    created_at = Column(DateTime, default=_now)


class Evaluation(Base):
    __tablename__ = "evaluations"

    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))
    training_run_id = Column(Integer, ForeignKey("training_runs.id"), nullable=True)
    phase = Column(String, default="baseline")  # baseline | post_training
    questions = Column(JSON, default=list)
    answers = Column(JSON, default=list)
    score = Column(Float, default=0.0)
    created_at = Column(DateTime, default=_now)


class WorkTask(Base):
    __tablename__ = "work_tasks"

    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))
    prompt = Column(Text, default="")
    output = Column(Text, default="")
    status = Column(String, default="completed")
    created_at = Column(DateTime, default=_now)


class TaskLabel(Base):
    __tablename__ = "task_labels"

    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey("work_tasks.id"))
    rating = Column(String, default="good")  # good | bad
    exp_delta = Column(Integer, default=0)
    labeler = Column(String, default="human")
    comment = Column(Text, default="")
    created_at = Column(DateTime, default=_now)


class ExperienceLog(Base):
    __tablename__ = "experience_logs"

    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))
    delta = Column(Integer, default=0)
    reason = Column(String, default="")
    balance_after = Column(Integer, default=0)
    created_at = Column(DateTime, default=_now)


class Judgment(Base):
    """A judgment Triston makes on a transcript: prediction + (optional) truth."""

    __tablename__ = "judgments"

    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))
    corpus_id = Column(Integer, ForeignKey("training_corpus.id"), nullable=True)
    transcript_preview = Column(Text, default="")
    prediction = Column(String, default="pass")  # pass | fail
    confidence = Column(Float, default=0.5)
    reasoning = Column(Text, default="")
    matched_criteria = Column(JSON, default=list)
    ground_truth = Column(String, nullable=True)  # pass | fail | None
    correct = Column(Integer, nullable=True)  # 1/0/None (None when no ground truth)
    created_at = Column(DateTime, default=_now)


class PromotionRequest(Base):
    __tablename__ = "promotion_requests"

    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))
    from_level = Column(Integer, default=1)
    to_level = Column(Integer, default=2)
    status = Column(String, default="pending")  # pending | approved | rejected
    expert = Column(String, default="")
    comment = Column(Text, default="")
    decided_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=_now)
