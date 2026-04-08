# 模块五：Agent 自我迭代 (Agent Self-Improvement)

> "Agent 不是静态的，它会从每一次尽调中学习，越用越强"

---

## 迭代循环

```
┌─────────────────────────────────────────────────────────────┐
│                    自我迭代循环                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   ┌─────────┐     ┌─────────┐     ┌─────────┐              │
│   │ Execute │────→│ Evaluate│────→│ Reflect │              │
│   │ 执行    │     │ 评估    │     │ 反思    │              │
│   └─────────┘     └─────────┘     └─────────┘              │
│        ↑                               │                    │
│        │                               ▼                    │
│        │                        ┌─────────┐                │
│        │                        │  Evolve │                │
│        │                        │ 进化    │                │
│        │                        └─────────┘                │
│        │                               │                    │
│        └───────────────────────────────┘                    │
│                                                             │
│   每一次尽调都是一次学习机会                                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 执行 (Execute)

```python
class ExecutionTracker:
    """执行过程追踪"""
    
    def __init__(self):
        self.execution_log = []
        self.decisions = []
        self.interventions = []
    
    def track(self, action: Action, context: Context):
        """追踪执行动作"""
        
        log_entry = {
            "timestamp": now(),
            "action": action.name,
            "input": action.input,
            "output": action.output,
            "context": {
                "phase": context.phase,
                "focus": context.focus,
                "memory_used": context.memory_ids,
            },
            "duration": action.duration,
            "tokens": action.token_usage,
        }
        
        self.execution_log.append(log_entry)
    
    def record_decision(self, decision: Decision):
        """记录决策过程"""
        
        self.decisions.append({
            "timestamp": now(),
            "situation": decision.situation,
            "options": decision.options,
            "chosen": decision.chosen,
            "reasoning": decision.reasoning,
            "confidence": decision.confidence,
        })
    
    def record_intervention(self, intervention: Intervention):
        """记录人工干预"""
        
        self.interventions.append({
            "timestamp": now(),
            "type": intervention.type,  # correction / guidance / override
            "target": intervention.target_action,
            "feedback": intervention.feedback,
            "user": intervention.user_id,
        })
```

---

## 评估 (Evaluate)

### 多维度评估

```python
class Evaluator:
    """尽调质量评估"""
    
    def evaluate(self, session: Session) -> EvaluationResult:
        """评估本次尽调质量"""
        
        return {
            "completeness": self.evaluate_completeness(session),
            "accuracy": self.evaluate_accuracy(session),
            "depth": self.evaluate_depth(session),
            "expertise": self.evaluate_expertise(session),
            "efficiency": self.evaluate_efficiency(session),
            "user_satisfaction": self.evaluate_satisfaction(session),
        }
    
    def evaluate_completeness(self, session: Session) -> Score:
        """评估完整性"""
        
        # 检查是否覆盖了所有必要章节
        required_sections = self.get_required_sections(session.target.industry)
        covered_sections = [s.name for s in session.report.sections]
        
        missing = set(required_sections) - set(covered_sections)
        
        # 检查每个章节的完整性
        section_scores = []
        for section in session.report.sections:
            score = self.check_section_completeness(section)
            section_scores.append(score)
        
        return Score(
            value=mean(section_scores) * (1 - len(missing) / len(required_sections)),
            details={"missing_sections": list(missing)}
        )
    
    def evaluate_depth(self, session: Session) -> Score:
        """评估分析深度"""
        
        depth_scores = []
        
        for analysis in session.analysis.findings:
            # 评估每个分析点的深度
            depth = self.assess_analysis_depth(analysis)
            depth_scores.append(depth)
        
        return Score(
            value=mean(depth_scores),
            distribution=self.calculate_distribution(depth_scores)
        )
    
    def evaluate_expertise(self, session: Session) -> Score:
        """评估专业度"""
        
        # 对比专家知识库
        expert_knowledge = load_expert_knowledge()
        
        # 评估词汇使用
        vocab_score = self.compare_vocabulary(
            session.report, 
            expert_knowledge.vocabulary
        )
        
        # 评估结构
        structure_score = self.compare_structure(
            session.report,
            expert_knowledge.structures
        )
        
        # 评估深度
        depth_score = self.compare_depth(
            session.report,
            expert_knowledge.depth_standards
        )
        
        return Score(
            value=weighted_mean([vocab_score, structure_score, depth_score]),
            details={
                "vocabulary": vocab_score,
                "structure": structure_score,
                "depth": depth_score
            }
        )
    
    def evaluate_efficiency(self, session: Session) -> Score:
        """评估效率"""
        
        # 时间效率
        time_score = self.compare_to_baseline(
            session.duration,
            self.baseline_duration(session.target)
        )
        
        # Token 效率
        token_score = self.compare_to_baseline(
            session.token_usage,
            self.baseline_tokens(session.target)
        )
        
        # 迭代次数
        iteration_score = self.score_iterations(session.revision_count)
        
        return Score(
            value=weighted_mean([time_score, token_score, iteration_score]),
            details={
                "time": time_score,
                "tokens": token_score,
                "iterations": iteration_score
            }
        )
```

---

## 反思 (Reflect)

```python
class ReflectionEngine:
    """反思引擎"""
    
    def reflect(self, session: Session, evaluation: EvaluationResult) -> Reflection:
        """生成反思"""
        
        reflection = Reflection(
            timestamp=now(),
            session_id=session.id,
            evaluation=evaluation
        )
        
        # 1. 识别成功之处
        reflection.successes = self.identify_successes(session, evaluation)
        
        # 2. 识别失败之处
        reflection.failures = self.identify_failures(session, evaluation)
        
        # 3. 分析原因
        reflection.root_causes = self.analyze_root_causes(
            reflection.failures,
            session.execution_log
        )
        
        # 4. 提取教训
        reflection.lessons = self.extract_lessons(
            reflection.successes,
            reflection.failures,
            reflection.root_causes
        )
        
        # 5. 提出改进建议
        reflection.improvements = self.suggest_improvements(
            reflection.lessons,
            session
        )
        
        return reflection
    
    def identify_successes(self, session: Session, evaluation: EvaluationResult) -> List[Success]:
        """识别成功之处"""
        
        successes = []
        
        # 高评分的分析点
        for finding in session.analysis.findings:
            if finding.quality_score > 0.8:
                successes.append(Success(
                    type="high_quality_analysis",
                    target=finding.id,
                    reason=finding.quality_factors
                ))
        
        # 用户满意的交互
        for feedback in session.user_feedback:
            if feedback.rating >= 4:
                successes.append(Success(
                    type="user_satisfaction",
                    target=feedback.target,
                    reason=feedback.comment
                ))
        
        # 高效的处理
        if evaluation.efficiency.value > 0.8:
            successes.append(Success(
                type="efficient_execution",
                target="overall",
                reason="Completed faster than baseline with good quality"
            ))
        
        return successes
    
    def identify_failures(self, session: Session, evaluation: EvaluationResult) -> List[Failure]:
        """识别失败之处"""
        
        failures = []
        
        # 低评分的分析点
        for finding in session.analysis.findings:
            if finding.quality_score < 0.5:
                failures.append(Failure(
                    type="low_quality_analysis",
                    target=finding.id,
                    reason="Insufficient depth or missing key points"
                ))
        
        # 用户不满意的交互
        for feedback in session.user_feedback:
            if feedback.rating < 3:
                failures.append(Failure(
                    type="user_dissatisfaction",
                    target=feedback.target,
                    reason=feedback.comment
                ))
        
        # 人工干预
        for intervention in session.interventions:
            failures.append(Failure(
                type="required_intervention",
                target=intervention.target,
                reason=intervention.feedback
            ))
        
        return failures
    
    def analyze_root_causes(self, failures: List[Failure], log: ExecutionLog) -> List[RootCause]:
        """分析根本原因"""
        
        causes = []
        
        for failure in failures:
            # 回溯执行日志
            related_actions = self.find_related_actions(failure, log)
            
            # 分析决策过程
            if failure.type == "low_quality_analysis":
                cause = self.analyze_quality_failure(failure, related_actions)
            elif failure.type == "user_dissatisfaction":
                cause = self.analyze_satisfaction_failure(failure, related_actions)
            elif failure.type == "required_intervention":
                cause = self.analyze_intervention_failure(failure, related_actions)
            
            causes.append(cause)
        
        return causes
    
    def extract_lessons(self, successes: List[Success], failures: List[Failure], causes: List[RootCause]) -> List[Lesson]:
        """提取教训"""
        
        lessons = []
        
        # 从成功中学习
        for success in successes:
            lesson = Lesson(
                type="best_practice",
                situation=success.target,
                action="What worked well",
                outcome="Positive result",
                applicability=self.assess_applicability(success)
            )
            lessons.append(lesson)
        
        # 从失败中学习
        for failure, cause in zip(failures, causes):
            lesson = Lesson(
                type="avoid_mistake",
                situation=failure.target,
                action="What went wrong",
                outcome="Negative result",
                root_cause=cause,
                applicability=self.assess_applicability(failure)
            )
            lessons.append(lesson)
        
        return lessons
```

---

## 进化 (Evolve)

```python
class EvolutionEngine:
    """进化引擎"""
    
    def evolve(self, reflection: Reflection) -> Evolution:
        """基于反思进行进化"""
        
        evolution = Evolution(
            timestamp=now(),
            based_on=reflection.id
        )
        
        for improvement in reflection.improvements:
            # 根据改进建议类型执行不同进化
            if improvement.type == "prompt_optimization":
                change = self.evolve_prompt(improvement)
            elif improvement.type == "knowledge_update":
                change = self.evolve_knowledge(improvement)
            elif improvement.type == "template_update":
                change = self.evolve_template(improvement)
            elif improvement.type == "parameter_tuning":
                change = self.evolve_parameters(improvement)
            
            evolution.changes.append(change)
        
        # 版本迭代
        evolution.new_version = self.increment_version()
        
        return evolution
    
    def evolve_prompt(self, improvement: Improvement) -> Change:
        """进化 Prompt"""
        
        # 1. 分析当前 prompt 的问题
        current_prompt = load_current_prompt()
        
        # 2. 根据改进建议修改
        if improvement.issue == "insufficient_depth":
            new_prompt = self.add_depth_instructions(current_prompt)
        elif improvement.issue == "poor_structure":
            new_prompt = self.add_structure_guidance(current_prompt)
        elif improvement.issue == "weak_vocabulary":
            new_prompt = self.enhance_vocabulary(current_prompt)
        
        # 3. A/B 测试新版本
        test_result = self.ab_test_prompt(current_prompt, new_prompt)
        
        if test_result.improvement > 0.1:  # 10% 提升
            return Change(
                type="prompt",
                before=current_prompt,
                after=new_prompt,
                reason=improvement.reason,
                test_result=test_result
            )
        else:
            return None  # 不采用
    
    def evolve_knowledge(self, improvement: Improvement) -> Change:
        """进化知识库"""
        
        # 更新专家知识
        knowledge = load_expert_knowledge()
        
        if improvement.target == "vocabulary":
            knowledge.vocabulary.update(improvement.new_terms)
        elif improvement.target == "structure":
            knowledge.structures.update(improvement.new_patterns)
        elif improvement.target == "depth_standards":
            knowledge.depth_standards.update(improvement.new_standards)
        
        save_expert_knowledge(knowledge)
        
        return Change(
            type="knowledge",
            target=improvement.target,
            additions=improvement.additions,
            reason=improvement.reason
        )
    
    def evolve_template(self, improvement: Improvement) -> Change:
        """进化模板"""
        
        template = load_template(improvement.template_name)
        
        # 根据反馈修改模板
        if improvement.issue == "missing_section":
            template.add_section(improvement.section)
        elif improvement.issue == "weak_content":
            template.enhance_section(improvement.section, improvement.enhancement)
        
        save_template(template)
        
        return Change(
            type="template",
            template=improvement.template_name,
            changes=improvement.changes
        )
```

---

## 版本管理

```python
class VersionManager:
    """版本管理"""
    
    def __init__(self):
        self.versions = []
        self.current_version = None
    
    def create_version(self, evolution: Evolution) -> Version:
        """创建新版本"""
        
        version = Version(
            number=self.next_version_number(),
            timestamp=now(),
            changes=evolution.changes,
            based_on=evolution.based_on,
            performance_baseline=self.measure_baseline()
        )
        
        self.versions.append(version)
        self.current_version = version
        
        return version
    
    def rollback(self, version_number: int):
        """回滚到指定版本"""
        
        target = find(self.versions, number=version_number)
        
        if not target:
            raise VersionNotFoundError(version_number)
        
        # 应用版本的所有变更的逆操作
        for change in reversed(target.changes):
            self.revert_change(change)
        
        self.current_version = target
        
        return target
    
    def compare_versions(self, v1: int, v2: int) -> Comparison:
        """比较两个版本"""
        
        version1 = find(self.versions, number=v1)
        version2 = find(self.versions, number=v2)
        
        return Comparison(
            version1=version1,
            version2=version2,
            performance_diff=self.compare_performance(v1, v2),
            change_diff=self.compare_changes(v1, v2)
        )
```

---

## 迭代效果追踪

```
版本迭代记录:

v1.0 (2024-01-15) - 初始版本
├── 基础尽调功能
├── 简单报告生成
└── 评分: 3.2/5.0

v1.1 (2024-02-01) - Prompt 优化
├── 改进: 增加深度分析指令
├── 效果: 深度评分 +15%
└── 评分: 3.5/5.0

v1.2 (2024-02-15) - 知识库增强
├── 改进: 引入行业术语库
├── 效果: 专业度评分 +20%
└── 评分: 3.8/5.0

v1.3 (2024-03-01) - 模板优化
├── 改进: 结构化报告模板
├── 效果: 完整性评分 +25%
└── 评分: 4.1/5.0

v1.4 (2024-03-15) - 专家蒸馏
├── 改进: 学习专家报告模式
├── 效果: 专业度评分 +30%
└── 评分: 4.4/5.0

v1.5 (2024-04-01) - 记忆系统
├── 改进: 引入案例记忆
├── 效果: 效率 +40%，满意度 +15%
└── 评分: 4.6/5.0
```

---

## 关键设计原则

1. **闭环反馈** - 执行 → 评估 → 反思 → 进化 → 再执行
2. **数据驱动** - 基于量化指标评估，而非主观感受
3. **渐进迭代** - 小步快跑，每次改进都有验证
4. **可回滚** - 新版本不好可以回退
5. **透明可解释** - 知道 Agent 为什么这样进化

---

## 下一步

- [ ] 实现执行追踪
- [ ] 设计评估指标体系
- [ ] 开发反思引擎
- [ ] 构建进化机制

