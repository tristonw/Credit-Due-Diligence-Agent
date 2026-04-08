# 模块四：专家知识蒸馏 (Expert Knowledge Distillation)

> "让 Agent 学习专家报告，写得越来越像行业专家"

---

## 为什么需要专家蒸馏？

### 问题
- 通用 LLM 写的报告太"通用"
- 缺乏行业深度和专业表达
- 论证逻辑不够严谨
- 风险识别不够敏锐

### 解决思路
像学生向老师学习一样：**分析专家作品 → 提取模式 → 模仿内化**

---

## 专家知识类型

```
┌─────────────────────────────────────────────────────────────┐
│  专家知识资产                                                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. 词汇知识 (Vocabulary)                                    │
│  ├── 行业术语: EBITDA、资产负债率、关联交易                  │
│  ├── 专业表达: "财务稳健" vs "财务健康"                      │
│  └── 量化描述: "显著高于行业均值" vs "略高"                  │
│                                                             │
│  2. 句法模式 (Patterns)                                      │
│  ├── 风险描述模式: "虽然...但是...需关注..."                │
│  ├── 结论推导模式: "基于...考虑到...建议..."                │
│  └── 数据引用模式: "根据XX数据显示..."                      │
│                                                             │
│  3. 论证结构 (Argument Structure)                            │
│  ├── 财务分析: 数据 → 趋势 → 原因 → 风险 → 建议            │
│  ├── 经营分析: 模式 → 优势 → 劣势 → 竞争力 → 展望          │
│  └── 风险分析: 识别 → 评估 → 缓释 → 综合判断               │
│                                                             │
│  4. 深度标记 (Depth Markers)                                 │
│  ├── 表面: "收入增长"                                        │
│  ├── 深入: "收入增长主要来自大客户"                          │
│  └── 深刻: "收入增长主要来自大客户，但前五大客户占比        │
│            达80%，存在客户集中风险，需关注大客户依赖度"      │
│                                                             │
│  5. 风险表达 (Risk Expression)                               │
│  ├── 风险等级: 低风险/中风险/高风险/极高风险                 │
│  ├── 风险描述: 定性 + 定量 + 案例类比                        │
│  └── 缓释措施: 具体、可执行、可追踪                          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 蒸馏流程

```
┌─────────────────────────────────────────────────────────────┐
│  Phase 1: 专家报告收集                                       │
├─────────────────────────────────────────────────────────────┤
│  • 收集高质量尽调报告 (专家评分 > 4.5/5.0)                   │
│  • 按行业、企业规模、尽调类型分类                            │
│  • 标注报告质量评分和用户反馈                                │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  Phase 2: 特征提取                                           │
├─────────────────────────────────────────────────────────────┤
│  • 词汇分析: 提取高频专业术语                                │
│  • 句法分析: 识别常用句式                                    │
│  • 结构分析: 拆解论证逻辑                                    │
│  • 深度分析: 标记分析深度层次                                │
│  • 风险分析: 学习风险识别和表达                              │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  Phase 3: 模式抽象                                           │
├─────────────────────────────────────────────────────────────┤
│  • 归纳通用模式                                              │
│  • 提取可复用模板                                            │
│  • 建立模式-场景映射                                         │
│  • 标注模式适用条件                                          │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  Phase 4: 知识内化                                           │
├─────────────────────────────────────────────────────────────┤
│  • 将模式融入生成模型                                        │
│  • 更新 prompt 和 few-shot 示例                              │
│  • 微调模型参数 (可选)                                       │
│  • 建立模式调用机制                                          │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  Phase 5: 持续迭代                                           │
├─────────────────────────────────────────────────────────────┤
│  • 对比生成 vs 专家报告                                      │
│  • 识别差距并补充知识                                        │
│  • 用户反馈驱动改进                                          │
│  • 定期更新知识库                                            │
└─────────────────────────────────────────────────────────────┘
```

---

## 特征提取详解

### 1. 词汇知识提取

```python
class VocabularyExtractor:
    """提取专家词汇知识"""
    
    def extract(self, reports: List[Report]) -> VocabularyKnowledge:
        """从专家报告中提取词汇知识"""
        
        # 1. 术语提取
        terms = self.extract_terms(reports)
        
        # 2. 表达偏好
        expressions = self.extract_expressions(reports)
        
        # 3. 量化描述
        quantifiers = self.extract_quantifiers(reports)
        
        return VocabularyKnowledge(
            terms=terms,
            expressions=expressions,
            quantifiers=quantifiers
        )
    
    def extract_terms(self, reports: List[Report]) -> Dict[str, TermInfo]:
        """提取专业术语"""
        terms = {}
        
        for report in reports:
            # 使用 NLP 提取候选术语
            candidates = self.nlp.extract_noun_phrases(report.content)
            
            for candidate in candidates:
                if self.is_domain_term(candidate):
                    if candidate not in terms:
                        terms[candidate] = TermInfo(
                            term=candidate,
                            frequency=0,
                            contexts=[],
                            variants=[]
                        )
                    
                    terms[candidate].frequency += 1
                    terms[candidate].contexts.append(
                        self.extract_context(report, candidate)
                    )
        
        # 过滤低频词，保留专业术语
        return {k: v for k, v in terms.items() if v.frequency >= 3}
    
    def extract_expressions(self, reports: List[Report]) -> List[ExpressionPattern]:
        """提取表达模式"""
        expressions = []
        
        # 常见表达模式
        patterns = [
            (r"虽然.+?但是.+?需关注", "转折风险表达"),
            (r"基于.+?考虑到.+?建议", "结论推导表达"),
            (r"从.+?来看.+?表明", "分析判断表达"),
            (r"值得注意的是", "重点提示表达"),
            (r"存在.+?风险", "风险识别表达"),
        ]
        
        for report in reports:
            for pattern, name in patterns:
                matches = re.findall(pattern, report.content)
                for match in matches:
                    expressions.append(ExpressionPattern(
                        pattern=pattern,
                        name=name,
                        example=match,
                        context=self.extract_context(report, match)
                    ))
        
        return expressions
    
    def extract_quantifiers(self, reports: List[Report]) -> List[Quantifier]:
        """提取量化描述"""
        quantifiers = []
        
        # 量化描述模式
        patterns = [
            (r"显著高于.+?均值", "high_positive", 0.8),
            (r"略高于.+?均值", "slight_positive", 0.6),
            (r"与.+?均值相当", "neutral", 0.5),
            (r"略低于.+?均值", "slight_negative", 0.4),
            (r"显著低于.+?均值", "high_negative", 0.2),
        ]
        
        for report in reports:
            for pattern, sentiment, intensity in patterns:
                matches = re.findall(pattern, report.content)
                for match in matches:
                    quantifiers.append(Quantifier(
                        expression=match,
                        sentiment=sentiment,
                        intensity=intensity
                    ))
        
        return quantifiers
```

### 2. 论证结构提取

```python
class StructureExtractor:
    """提取论证结构"""
    
    def extract(self, reports: List[Report]) -> StructureKnowledge:
        """提取论证结构知识"""
        
        structures = {}
        
        for report in reports:
            # 按章节分析
            for section in report.sections:
                section_type = self.classify_section(section)
                
                if section_type not in structures:
                    structures[section_type] = []
                
                # 提取论证结构
                argument_structure = self.parse_argument(section)
                structures[section_type].append(argument_structure)
        
        # 归纳通用结构
        return self.abstract_structures(structures)
    
    def parse_argument(self, section: Section) -> ArgumentStructure:
        """解析论证结构"""
        
        # 识别论证单元
        units = self.identify_argument_units(section)
        
        # 分析单元间关系
        relations = self.analyze_relations(units)
        
        # 提取论证链
        chains = self.extract_chains(units, relations)
        
        return ArgumentStructure(
            units=units,
            relations=relations,
            chains=chains
        )
    
    def abstract_structures(self, structures: Dict) -> StructureKnowledge:
        """抽象通用结构"""
        
        abstracted = {}
        
        for section_type, instances in structures.items():
            # 聚类相似结构
            clusters = self.cluster_similar(instances)
            
            # 提取每个聚类的代表结构
            for cluster in clusters:
                representative = self.extract_representative(cluster)
                
                abstracted[section_type] = SectionTemplate(
                    type=section_type,
                    structure=representative,
                    frequency=len(cluster),
                    examples=cluster[:3]
                )
        
        return StructureKnowledge(templates=abstracted)
```

### 3. 深度标记提取

```python
class DepthExtractor:
    """提取深度标记知识"""
    
    def extract(self, reports: List[Report]) -> DepthKnowledge:
        """提取深度分析模式"""
        
        depth_patterns = {
            "surface": [],    # 表面描述
            "shallow": [],    # 浅层分析
            "medium": [],     # 中等深度
            "deep": [],       # 深度分析
            "expert": []      # 专家级洞察
        }
        
        for report in reports:
            # 按分析点提取
            for analysis_point in report.analysis_points:
                depth = self.assess_depth(analysis_point)
                depth_patterns[depth].append(analysis_point)
        
        # 提取每种深度的特征
        return DepthKnowledge(
            surface_features=self.extract_features(depth_patterns["surface"]),
            shallow_features=self.extract_features(depth_patterns["shallow"]),
            medium_features=self.extract_features(depth_patterns["medium"]),
            deep_features=self.extract_features(depth_patterns["deep"]),
            expert_features=self.extract_features(depth_patterns["expert"])
        )
    
    def assess_depth(self, analysis: AnalysisPoint) -> str:
        """评估分析深度"""
        
        score = 0
        
        # 维度1: 数据支撑
        if analysis.has_data:
            score += 1
        if analysis.has_comparison:
            score += 1
        if analysis.has_trend:
            score += 1
        
        # 维度2: 原因分析
        if analysis.has_cause_analysis:
            score += 2
        
        # 维度3: 影响评估
        if analysis.has_impact_assessment:
            score += 2
        
        # 维度4: 风险识别
        if analysis.has_risk_identification:
            score += 2
        
        # 维度5: 建议提出
        if analysis.has_recommendation:
            score += 1
        
        # 映射到深度等级
        if score >= 9:
            return "expert"
        elif score >= 7:
            return "deep"
        elif score >= 5:
            return "medium"
        elif score >= 3:
            return "shallow"
        else:
            return "surface"
```

---

## 知识内化

### 方式一：Prompt 工程

```python
def build_expert_prompt(expert_knowledge: ExpertKnowledge) -> str:
    """构建专家级 prompt"""
    
    prompt = f"""
    你是一位资深的信贷尽调专家，拥有10年以上行业经验。
    
    ## 专业术语使用
    {format_terms(expert_knowledge.vocabulary.terms)}
    
    ## 表达风格
    {format_expressions(expert_knowledge.vocabulary.expressions)}
    
    ## 分析框架
    {format_structures(expert_knowledge.structures)}
    
    ## 深度要求
    分析必须达到以下深度标准:
    {format_depth_standards(expert_knowledge.depth)}
    
    ## Few-shot 示例
    {format_examples(expert_knowledge.examples[:3])}
    
    请基于以上专业标准，完成以下尽调任务。
    """
    
    return prompt
```

### 方式二：动态模式调用

```python
class ExpertMode:
    """专家模式调用"""
    
    def __init__(self, knowledge: ExpertKnowledge):
        self.knowledge = knowledge
    
    def apply_vocabulary(self, text: str, context: Context) -> str:
        """应用专家词汇"""
        # 识别可替换的通用表达
        # 替换为专家级表达
        pass
    
    def apply_structure(self, section: Section, section_type: str) -> Section:
        """应用专家结构"""
        template = self.knowledge.structures.get(section_type)
        
        if template:
            # 按模板重组内容
            return self.reorganize(section, template)
        
        return section
    
    def apply_depth(self, analysis: AnalysisPoint, target_depth: str) -> AnalysisPoint:
        """应用深度标准"""
        current_depth = self.assess_depth(analysis)
        
        if current_depth < target_depth:
            # 补充分析维度
            analysis = self.deepen(analysis, target_depth)
        
        return analysis
```

---

## 持续迭代

### 评估与反馈

```python
class ExpertEvaluator:
    """专家质量评估"""
    
    def evaluate(self, generated: Report, expert_reports: List[Report]) -> Evaluation:
        """评估生成报告的专家度"""
        
        scores = {
            "vocabulary": self.score_vocabulary(generated, expert_reports),
            "structure": self.score_structure(generated, expert_reports),
            "depth": self.score_depth(generated, expert_reports),
            "risk_expression": self.score_risk_expression(generated, expert_reports),
        }
        
        return Evaluation(
            overall=weighted_average(scores),
            details=scores,
            gaps=self.identify_gaps(generated, expert_reports)
        )
    
    def score_vocabulary(self, generated: Report, experts: List[Report]) -> float:
        """评估词汇专业度"""
        
        # 提取专家常用术语
        expert_terms = self.extract_term_frequencies(experts)
        
        # 提取生成报告术语
        generated_terms = self.extract_term_frequencies([generated])
        
        # 计算术语使用相似度
        return cosine_similarity(expert_terms, generated_terms)
```

### 知识更新

```python
def update_expert_knowledge(
    current: ExpertKnowledge,
    new_reports: List[Report],
    feedback: Feedback
) -> ExpertKnowledge:
    """更新专家知识"""
    
    # 1. 提取新知识
    new_knowledge = extract_features(new_reports)
    
    # 2. 根据反馈调整权重
    if feedback.positive:
        boost_patterns(current, new_knowledge, feedback.highlighted)
    else:
        reduce_patterns(current, new_knowledge, feedback.criticized)
    
    # 3. 合并知识
    merged = merge_knowledge(current, new_knowledge)
    
    # 4. 版本迭代
    merged.version += 1
    merged.last_updated = now()
    
    return merged
```

---

## 关键设计原则

1. **多维度学习** - 词汇、结构、深度、风险表达全面学习
2. **模式抽象** - 从具体案例中提取通用模式
3. **渐进内化** - 从 prompt 到模型的渐进式内化
4. **持续迭代** - 不断对比、评估、更新
5. **可解释性** - 知道 Agent 为什么这样写

---

## 下一步

- [ ] 收集专家报告样本
- [ ] 实现特征提取 pipeline
- [ ] 构建专家知识库
- [ ] 开发评估反馈机制
