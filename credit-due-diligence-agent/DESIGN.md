# 信贷尽调智能体 (Credit Due Diligence Agent)

## 设计理念：Claude Code 单 Agent 模式

> "一个 Agent，极致压缩，无限上下文，自我迭代"

---

## 核心架构

### 1. 三层上下文压缩系统

```
┌─────────────────────────────────────────────────────────────┐
│  Layer 1: 元数据层 (Metadata Layer) - 常驻内存               │
│  - 当前任务状态 (task_state)                                │
│  - 关键实体索引 (entity_index)                              │
│  - 会话摘要 (session_summary)                               │
│  Token: ~500                                                │
├─────────────────────────────────────────────────────────────┤
│  Layer 2: 工作记忆层 (Working Memory) - 按需加载             │
│  - 当前分析对象 (current_target)                            │
│  - 分析框架 (analysis_framework)                            │
│  - 中间结论 (interim_findings)                              │
│  Token: ~2000                                               │
├─────────────────────────────────────────────────────────────┤
│  Layer 3: 深度知识层 (Deep Knowledge) - 引用加载             │
│  - 行业知识库 (industry_knowledge/)                         │
│  - 尽调模板库 (templates/)                                  │
│  - 历史案例库 (cases/)                                      │
│  Token: 按需，单次 <3000                                    │
└─────────────────────────────────────────────────────────────┘
```

### 2. 记忆会话管理 (Memory Session Management)

```typescript
// 会话状态机
interface SessionState {
  // 当前阶段
  phase: 'INIT' | 'DATA_COLLECTION' | 'ANALYSIS' | 'DRAFT' | 'REVIEW' | 'FINAL';
  
  // 关键实体
  entities: {
    company: CompanyProfile;
    industry: IndustryInfo;
    financials: FinancialData;
    risks: RiskAssessment;
    collateral?: CollateralInfo;
  };
  
  // 上下文指针
  pointers: {
    lastAction: string;
    nextAction: string;
    pendingQuestions: string[];
    completedTasks: string[];
  };
  
  // 压缩摘要
  summary: CompressedSummary;
}

// 压缩摘要算法
interface CompressedSummary {
  version: number;           // 迭代版本
  keyFindings: string[];     // 关键发现 (最多10条)
  riskFlags: RiskFlag[];     // 风险标记
  confidence: number;        // 置信度评分
  expertNotes: string;       // 专家批注
}
```

### 3. Harness Engineering 设计

```
┌─────────────────────────────────────────────────────────────┐
│  Harness Core - 核心控制层                                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │  Input      │───→│  Context    │───→│  Output     │     │
│  │  Parser     │    │  Manager    │    │  Generator  │     │
│  └─────────────┘    └─────────────┘    └─────────────┘     │
│         │                  │                  │             │
│         ↓                  ↓                  ↓             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Self-Improvement Loop                   │   │
│  │  ┌─────────┐   ┌─────────┐   ┌─────────┐           │   │
│  │  │ Evaluate│ → │ Reflect │ → │ Evolve  │           │   │
│  │  └─────────┘   └─────────┘   └─────────┘           │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 核心组件详解

### 3.1 上下文压缩引擎 (Context Compression Engine)

```python
class ContextCompressor:
    """
    将冗长信息压缩为结构化摘要
    """
    
    def compress_financial_data(self, raw_data: FinancialReport) -> CompressedFinancial:
        """
        压缩前: 50页财务报表 → 压缩后: 关键指标卡片
        """
        return {
            "revenue_trend": self._extract_trend(raw_data.revenue, years=3),
            "profitability": {
                "gross_margin": raw_data.gross_margin,
                "net_margin": raw_data.net_margin,
                "trend": self._calculate_trend(raw_data.net_margin_history)
            },
            "liquidity": {
                "current_ratio": raw_data.current_ratio,
                "quick_ratio": raw_data.quick_ratio,
                "cash_flow": raw_data.operating_cash_flow
            },
            "leverage": {
                "debt_to_equity": raw_data.de_ratio,
                "interest_coverage": raw_data.interest_coverage
            },
            "red_flags": self._detect_anomalies(raw_data),
            "summary": self._generate_one_line_summary(raw_data)
        }
    
    def compress_industry_analysis(self, full_analysis: IndustryReport) -> CompressedIndustry:
        """
        压缩行业分析为决策关键信息
        """
        return {
            "cycle_position": full_analysis.cycle_phase,  # 上行/下行/筑底
            "competitive_landscape": full_analysis.competition_level,  # 红海/蓝海
            "policy_risk": full_analysis.regulatory_outlook,
            "key_drivers": full_analysis.growth_drivers[:3],
            "warning_signals": full_analysis.warning_signals[:5]
        }
```

### 3.2 记忆分层系统 (Memory Hierarchy)

```
记忆层级:

L1 - 瞬时记忆 (Transient)
├── 当前对话轮次
├── 用户刚输入的信息
└── 临时计算结果

L2 - 工作记忆 (Working) - 会话级
├── 本次尽调的目标企业
├── 已收集的关键数据
├── 当前分析进度
└── 待确认的问题清单

L3 - 短期记忆 (Short-term) - 跨会话
├── 最近3次尽调的经验
├── 用户偏好设置
└── 常用模板片段

L4 - 长期记忆 (Long-term) - 持久化
├── 行业知识图谱
├── 历史尽调案例库
├── 专家规则库
└── 自我进化记录
```

### 3.3 自我迭代机制 (Self-Improvement)

```python
class SelfImprovementEngine:
    """
    让 Agent 越写越像专家
    """
    
    def evaluate_report(self, report: Report, feedback: Feedback) -> Evaluation:
        """
        评估报告质量
        """
        return {
            "completeness": self._check_coverage(report),
            "depth": self._assess_analysis_depth(report),
            "accuracy": self._verify_facts(report),
            "expertise_level": self._rate_expertise(report),
            "improvement_areas": self._identify_gaps(report, feedback)
        }
    
    def evolve_knowledge(self, evaluation: Evaluation):
        """
        基于评估结果进化知识库
        """
        # 1. 更新权重
        self.update_template_weights(evaluation)
        
        # 2. 学习新表达
        self.learn_expert_phrases(evaluation.expertise_level)
        
        # 3. 修正错误模式
        self.correct_error_patterns(evaluation.improvement_areas)
        
        # 4. 版本迭代
        self.version += 1
        self.save_checkpoint()
    
    def learn_from_expert_reports(self, expert_reports: List[Report]):
        """
        学习专家报告的风格和深度
        """
        for report in expert_reports:
            # 提取专家表达模式
            patterns = self._extract_patterns(report)
            
            # 分析论证结构
            argument_structure = self._analyze_argument_flow(report)
            
            # 识别行业黑话和术语
            terminology = self._extract_terminology(report)
            
            # 更新知识库
            self.expert_knowledge_base.update({
                "patterns": patterns,
                "structures": argument_structure,
                "terminology": terminology
            })
```

---

## 尽调工作流 (Due Diligence Workflow)

```
┌─────────────────────────────────────────────────────────────┐
│  Phase 1: 初始化与数据收集                                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  输入: 企业名称 + 基础信息                                    │
│  │                                                          │
│  ▼                                                          │
│  ┌─────────────────────────────────────────┐               │
│  │ 1.1 企业画像快速构建                     │               │
│  │     - 工商信息抓取                       │               │
│  │     - 股权结构分析                       │               │
│  │     - 关联企业图谱                       │               │
│  └─────────────────────────────────────────┘               │
│  │                                                          │
│  ▼                                                          │
│  ┌─────────────────────────────────────────┐               │
│  │ 1.2 行业定位与对标                       │               │
│  │     - 行业分类与生命周期判断              │               │
│  │     - 可比公司筛选                       │               │
│  │     - 行业关键指标基准                    │               │
│  └─────────────────────────────────────────┘               │
│  │                                                          │
│  ▼                                                          │
│  ┌─────────────────────────────────────────┐               │
│  │ 1.3 数据缺口识别                         │               │
│  │     - 缺失数据清单                       │               │
│  │     - 数据质量评估                       │               │
│  │     - 替代数据源建议                      │               │
│  └─────────────────────────────────────────┘               │
│                                                             │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  Phase 2: 深度分析                                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  2.1 财务分析模块
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│  │ 盈利能力    │ │ 偿债能力    │ │ 运营效率    │
│  │ 分析       │ │ 分析       │ │ 分析       │
│  └─────────────┘ └─────────────┘ └─────────────┘
│         │              │              │
│         └──────────────┼──────────────┘
│                        ▼
│              ┌─────────────────┐
│              │ 财务健康度评分   │
│              │ 与预警指标      │
│              └─────────────────┘
│
│  2.2 经营分析模块
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│  │ 商业模式    │ │ 竞争优势    │ │ 管理团队    │
│  │ 分析       │ │ 评估       │ │ 评估       │
│  └─────────────┘ └─────────────┘ └─────────────┘
│
│  2.3 风险识别模块
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│  │ 信用风险    │ │ 行业风险    │ │ 担保/抵押   │
│  │           │ │           │ │ 风险       │
│  └─────────────┘ └─────────────┘ └─────────────┘
│
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  Phase 3: 报告生成与迭代                                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────┐
│  │ 3.1 初稿生成                            │
│  │   - 基于模板填充                        │
│  │   - 智能段落生成                        │
│  │   - 数据可视化建议                      │
│  └─────────────────────────────────────────┘
│                   │
│                   ▼
│  ┌─────────────────────────────────────────┐
│  │ 3.2 自我审查                            │
│  │   - 逻辑一致性检查                      │
│  │   - 数据交叉验证                        │
│  │   - 专家标准对标                        │
│  └─────────────────────────────────────────┘
│                   │
│                   ▼
│  ┌─────────────────────────────────────────┐
│  │ 3.3 迭代优化                            │
│  │   - 识别薄弱章节                        │
│  │   - 补充深度分析                        │
│  │   - 提升专业表达                        │
│  └─────────────────────────────────────────┘
│                   │
│                   ▼
│  ┌─────────────────────────────────────────┐
│  │ 3.4 输出生成                            │
│  │   - 多格式导出 (Word/PDF/Markdown)      │
│  │   - 关键结论摘要                        │
│  │   - 决策建议                            │
│  └─────────────────────────────────────────┘
│                                                             │
└─────────────────────────────────────────────────────────────┘

---

## 关键技术实现

### 4.1 极致上下文压缩算法

```python
class ExtremeCompression:
    """
    将任意长文档压缩为固定大小的结构化表示
    """
    
    MAX_TOKENS = 2000  # 目标压缩后大小
    
    def compress(self, document: Document) -> CompressedDoc:
        # 第一层: 提取关键句子
        key_sentences = self._extractive_summary(document, ratio=0.1)
        
        # 第二层: 实体关系图谱
        entity_graph = self._build_entity_graph(document)
        
        # 第三层: 数值指标提取
        metrics = self._extract_all_metrics(document)
        
        # 第四层: 情感与风险信号
        sentiment_signals = self._analyze_sentiment(document)
        
        return CompressedDoc(
            summary=key_sentences,
            entities=entity_graph,
            metrics=metrics,
            signals=sentiment_signals,
            hash=self._compute_hash(document)
        )
    
    def decompress_hint(self, compressed: CompressedDoc, query: str) -> str:
        """
        根据查询意图，生成解压缩提示
        """
        relevant_entities = self._find_relevant_entities(compressed.entities, query)
        relevant_metrics = self._filter_metrics(compressed.metrics, query)
        
        return f"""
        基于压缩文档 {compressed.hash}:
        - 相关实体: {relevant_entities}
        - 相关指标: {relevant_metrics}
        - 摘要: {compressed.summary[:200]}...
        
        如需完整信息，请引用原文。
        """
```

### 4.2 记忆索引系统

```python
class MemoryIndex:
    """
    快速定位历史信息
    """
    
    def __init__(self):
        self.entity_index = {}      # 实体 → 会话列表
        self.topic_index = {}       # 主题 → 相关段落
        self.time_index = []        # 时间线索引
        self.version_index = {}     # 版本 → 变更摘要
    
    def index_session(self, session: Session):
        """索引新会话"""
        for entity in session.entities:
            self.entity_index.setdefault(entity, []).append(session.id)
        
        for topic in session.topics:
            self.topic_index.setdefault(topic, []).append(session.id)
        
        self.time_index.append({
            "timestamp": session.timestamp,
            "session_id": session.id,
            "summary": session.summary
        })
    
    def retrieve_relevant(self, query: Query, k: int = 5) -> List[MemoryChunk]:
        """检索相关记忆"""
        # 实体匹配
        entity_matches = self._match_entities(query)
        
        # 语义相似度
        semantic_matches = self._semantic_search(query)
        
        # 时间衰减加权
        time_weighted = self._apply_time_decay(semantic_matches)
        
        # 融合排序
        return self._fusion_rank(entity_matches, time_weighted, k=k)
```

### 4.3 专家知识蒸馏

```python
class ExpertKnowledgeDistillation:
    """
    从专家报告中学习，提升生成质量
    """
    
    def distill(self, expert_reports: List[Report], iterations: int = 100):
        """
        知识蒸馏主流程
        """
        for i in range(iterations):
            # 采样专家报告
            expert_sample = random.sample(expert_reports, k=3)
            
            # 提取专家特征
            expert_features = self._extract_features(expert_sample)
            
            # 生成对比样本
            generated = self._generate_with_current_model(expert_sample[0].input_data)
            
            # 计算差距
            gap = self._compute_quality_gap(expert_sample[0], generated)
            
            # 更新模型
            self._update_weights(gap, expert_features)
            
            # 记录进步
            self._log_progress(i, gap)
    
    def _extract_features(self, reports: List[Report]) -> ExpertFeatures:
        """提取专家报告特征"""
        return {
            "vocabulary": self._extract_domain_terms(reports),
            "sentence_patterns": self._extract_patterns(reports),
            "argument_flows": self._analyze_argument_structures(reports),
            "depth_markers": self._identify_depth_indicators(reports),
            "risk_expression": self._learn_risk_phrases(reports)
        }
```

---

## 交互设计

### 5.1 对话模式

```
用户: 帮我写一份关于[某某科技]的信贷尽调报告

Agent: 🎯 启动信贷尽调流程

【当前状态】
📋 阶段: 数据收集
🏢 目标: 某某科技有限公司
⏱️  预计时间: 15-20分钟

【已获取信息】
✓ 工商注册信息
✓ 股权结构 (3层穿透)
✓ 行业分类: 软件和信息技术服务业
⏳ 财务数据获取中...

【需要您确认】
1. 该企业是否有合并报表范围外的重大关联交易?
2. 是否有特定的关注重点 (如: 现金流、担保情况、行业风险)?

请回复数字或输入具体问题...
```

### 5.2 进度可视化

```
【尽调进度】████████████████░░░░ 80%

Phase 1: 数据收集    ████████████ ✓
Phase 2: 深度分析    ████████████ ✓
Phase 3: 报告生成    ████████░░░░ 进行中

当前: 生成风险分析章节...
```

### 5.3 智能提示

```
【洞察提示】💡

检测到该企业应收账款周转天数从45天增至78天，
建议深入分析:
1. 主要客户信用状况变化
2. 收入确认政策是否变更
3. 行业整体回款周期趋势

需要我展开分析吗? (Y/n)
```

---

## 技术栈建议

### 核心框架
- **Agent Core**: 基于 OpenClaw ACP 架构
- **Context Management**: 自研分层压缩系统
- **Memory Store**: SQLite + 向量数据库 (如 Chroma)
- **Document Generation**: Python-docx + Jinja2 模板

### 关键依赖
```
openclaw-acp          # Agent 运行时
chromadb              # 向量记忆存储
sentence-transformers # 语义编码
networkx              # 关系图谱
pandas/numpy          # 数据分析
python-docx           # Word 生成
```

---

## 实施路线图

### Phase 1: MVP (2-3周)
- [ ] 基础上下文压缩
- [ ] 简单尽调模板
- [ ] 单会话记忆
- [ ] 基础报告生成

### Phase 2: 增强 (3-4周)
- [ ] 分层记忆系统
- [ ] 行业知识库
- [ ] 自我审查机制
- [ ] 迭代优化循环

### Phase 3: 专家级 (4-6周)
- [ ] 专家知识蒸馏
- [ ] 高级风险识别
- [ ] 多格式输出
- [ ] 性能优化

### Phase 4: 持续进化 (长期)
- [ ] 用户反馈学习
- [ ] 新行业扩展
- [ ] 报告质量追踪
- [ ] A/B 测试框架

---

## 关键成功指标 (KPI)

| 指标 | 目标值 | 测量方式 |
|------|--------|----------|
| 报告生成时间 | < 30分钟 | 端到端耗时 |
| 专家评分 | > 4.0/5.0 | 盲评测试 |
| 上下文压缩率 | > 90% | 原始/压缩后 Token 比 |
| 记忆召回准确率 | > 85% | 相关记忆检索测试 |
| 用户满意度 | > 4.5/5.0 | 反馈调查 |

---

## 与 Claude Code 的对比

| 特性 | Claude Code | 信贷尽调 Agent |
|------|-------------|----------------|
| 领域 | 通用编程 | 信贷尽调专业 |
| 上下文 | 代码仓库 | 企业数据 + 行业知识 |
| 输出 | 代码/配置 | 专业报告 |
| 迭代 | 代码调试 | 报告质量提升 |
| 学习 | 代码模式 | 专家报告风格 |

---

## 总结

这个设计的核心理念是：

1. **单 Agent 架构** - 避免多 Agent 协调复杂性
2. **极致上下文压缩** - 在有限 Token 内处理海量信息
3. **分层记忆管理** - 快速检索历史经验
4. **自我迭代进化** - 越用越像行业专家
5. **Harness Engineering** - 精心设计的控制流和反馈循环

这是一个"活"的系统，会随着使用不断进化，最终达到甚至超越人类专家的水平。