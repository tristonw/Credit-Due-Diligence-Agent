# 模块六：企业知识管理 (Enterprise Knowledge Management)

> "每个企业都应该有自己的知识库，一套让 AI 能读懂的 Wiki"
> 
> —— 受 Karpathy AI 知识库理念启发

---

## 核心理念

### 为什么需要企业知识库？

```
┌─────────────────────────────────────────────────────────────┐
│  没有知识库                          有知识库               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Agent: "请提供企业信息"              Agent: "我了解你们"   │
│  用户:  (上传一堆文件)                用户: "分析下现金流"  │
│  Agent: (从头学习)                    Agent: "基于你们过去  │
│         ↓                                    3年的财务数据..│
│  每次都要重复学习                     直接基于知识分析      │
│  上下文容易丢失                       历史信息随时可用      │
│  无法积累洞察                         越用越懂企业          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 设计原则

1. **结构化** - 不是文档堆，是机器可读的知识图谱
2. **可检索** - AI 能快速找到需要的信息
3. **持续更新** - 知识库随企业成长而进化
4. **多源融合** - 整合内部数据 + 外部信息
5. **权限控制** - 敏感信息分级管理

---

## 知识库架构

```
┌─────────────────────────────────────────────────────────────┐
│                    企业知识库架构                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  知识图谱层 (Knowledge Graph)                        │   │
│  │  • 实体: 人、公司、产品、项目、合同                  │   │
│  │  • 关系: 股权、任职、交易、担保                      │   │
│  │  • 事件: 融资、诉讼、并购、变更                      │   │
│  └─────────────────────────────────────────────────────┘   │
│                         ↑↓                                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  文档智能层 (Document Intelligence)                  │   │
│  │  • 财报解析: 自动提取财务指标                        │   │
│  │  • 合同理解: 关键条款识别                            │   │
│  │  • 舆情监控: 新闻/社交媒体追踪                       │   │
│  │  • 报告生成: 结构化尽调报告                          │   │
│  └─────────────────────────────────────────────────────┘   │
│                         ↑↓                                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  数据融合层 (Data Fusion)                            │   │
│  │  • 内部数据: ERP/财务/CRM/HR                         │   │
│  │  • 外部数据: 工商/征信/舆情/行业                     │   │
│  │  • 实时数据: 股价/舆情/政策                          │   │
│  └─────────────────────────────────────────────────────┘   │
│                         ↑↓                                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  接口服务层 (API Services)                           │   │
│  │  • GraphQL API: 知识图谱查询                         │   │
│  │  • Search API: 语义搜索                              │   │
│  │  • Alert API: 风险预警                               │   │
│  │  • Report API: 报告生成                              │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 知识图谱设计

### 实体类型

```typescript
// 企业实体
interface Company {
  id: string;
  name: string;
  unifiedCode: string;      // 统一社会信用代码
  industry: string;
  scale: string;
  status: 'active' | 'inactive' | 'liquidation';
  
  // 基本信息
  basicInfo: {
    registeredCapital: number;
    establishmentDate: Date;
    legalRepresentative: string;
    address: string;
    businessScope: string[];
  };
  
  // 财务摘要 (压缩)
  financialSummary: FinancialSummary;
  
  // 风险画像
  riskProfile: RiskProfile;
  
  // 时间线
  timeline: Event[];
}

// 人员实体
interface Person {
  id: string;
  name: string;
  idNumber: string;         // 脱敏存储
  
  // 关联关系
  roles: Role[];            // 在哪些公司担任什么职务
  investments: Investment[]; // 投资记录
  relations: Relation[];    // 人际关系
  
  // 风险信息
  risks: Risk[];
}

// 合同实体
interface Contract {
  id: string;
  type: 'sales' | 'purchase' | 'loan' | 'guarantee' | 'other';
  parties: Party[];
  amount: number;
  startDate: Date;
  endDate: Date;
  
  // 关键条款 (结构化)
  keyTerms: {
    paymentTerms: string;
    deliveryTerms: string;
    warrantyTerms: string;
    terminationTerms: string;
    penaltyTerms: string;
  };
  
  // 履约情况
  performance: Performance;
}

// 事件实体
interface Event {
  id: string;
  type: 'financing' | 'litigation' | 'acquisition' | 'personnel_change' | 'policy_change';
  date: Date;
  description: string;
  impact: 'positive' | 'negative' | 'neutral';
  severity: 'low' | 'medium' | 'high' | 'critical';
  relatedEntities: string[];
}
```

### 关系类型

```typescript
// 股权关系
interface Shareholding {
  from: string;           // 股东
  to: string;             // 被投资企业
  percentage: number;
  amount: number;
  date: Date;
}

// 担保关系
interface Guarantee {
  guarantor: string;      // 担保方
  guaranteed: string;     // 被担保方
  creditor: string;       // 债权人
  amount: number;
  type: 'joint' | 'several';
  status: 'active' | 'released';
}

// 交易关系
interface Transaction {
  buyer: string;
  seller: string;
  amount: number;
  date: Date;
  contractId: string;
}

// 关联关系
interface Affiliation {
  entity1: string;
  entity2: string;
  type: 'family' | 'control' | 'influence' | 'business';
  strength: number;       // 关联强度 0-1
}
```

---

## 文档智能

### 财报解析

```python
class FinancialReportParser:
    """财报智能解析"""
    
    def parse(self, report: Document) -> FinancialData:
        """解析财报文档"""
        
        # 1. 文档分类
        doc_type = self.classify(report)  # 年报/季报/半年报
        
        # 2. 表格提取
        tables = self.extract_tables(report)
        
        # 3. 科目识别
        for table in tables:
            if self.is_balance_sheet(table):
                balance_sheet = self.parse_balance_sheet(table)
            elif self.is_income_statement(table):
                income_statement = self.parse_income_statement(table)
            elif self.is_cash_flow(table):
                cash_flow = self.parse_cash_flow(table)
        
        # 4. 附注解析
        notes = self.parse_notes(report)
        
        # 5. 指标计算
        metrics = self.calculate_metrics(
            balance_sheet, 
            income_statement, 
            cash_flow
        )
        
        # 6. 异常检测
        anomalies = self.detect_anomalies(metrics)
        
        return FinancialData(
            type=doc_type,
            period=report.period,
            balanceSheet=balance_sheet,
            incomeStatement=income_statement,
            cashFlow=cash_flow,
            metrics=metrics,
            anomalies=anomalies,
            notes=notes
        )
    
    def detect_anomalies(self, metrics: Metrics) -> List[Anomaly]:
        """检测财务异常"""
        
        anomalies = []
        
        # 异常1: 收入增长但现金流下降
        if metrics.revenue_growth > 0.1 and metrics.cash_flow_growth < -0.1:
            anomalies.append(Anomaly(
                type="revenue_cash_flow_divergence",
                severity="high",
                description="收入增长但现金流下降，可能存在收入质量问题",
                indicators=["revenue_growth", "cash_flow_growth"]
            ))
        
        # 异常2: 应收账款增速超过收入增速
        if metrics.ar_growth > metrics.revenue_growth * 1.2:
            anomalies.append(Anomaly(
                type="ar_growth_anomaly",
                severity="medium",
                description="应收账款增速超过收入增速，回款能力可能恶化",
                indicators=["ar_growth", "revenue_growth"]
            ))
        
        # 异常3: 存货周转率持续下降
        if metrics.inventory_turnover_trend == "declining":
            anomalies.append(Anomaly(
                type="inventory_turnover_decline",
                severity="medium",
                description="存货周转率持续下降，可能存在滞销或减值风险",
                indicators=["inventory_turnover"]
            ))
        
        return anomalies
```

### 合同理解

```python
class ContractAnalyzer:
    """合同智能分析"""
    
    def analyze(self, contract: Document) -> ContractInsight:
        """分析合同内容"""
        
        # 1. 合同分类
        contract_type = self.classify_contract(contract)
        
        # 2. 关键条款提取
        key_terms = self.extract_key_terms(contract)
        
        # 3. 风险条款识别
        risk_clauses = self.identify_risk_clauses(contract)
        
        # 4. 义务权利分析
        obligations = self.analyze_obligations(contract)
        
        # 5. 生成摘要
        summary = self.generate_summary(contract, key_terms)
        
        return ContractInsight(
            type=contract_type,
            parties=self.extract_parties(contract),
            amount=self.extract_amount(contract),
            duration=self.extract_duration(contract),
            keyTerms=key_terms,
            riskClauses=risk_clauses,
            obligations=obligations,
            summary=summary
        )
    
    def identify_risk_clauses(self, contract: Document) -> List[RiskClause]:
        """识别风险条款"""
        
        risks = []
        
        # 风险1: 单方解约权
        if self.has_unilateral_termination(contract):
            risks.append(RiskClause(
                type="unilateral_termination",
                severity="high",
                description="对方拥有单方解约权，业务稳定性存在风险",
                mitigation="建议增加解约提前期或违约金条款"
            ))
        
        # 风险2: 无限连带责任
        if self.has_unlimited_liability(contract):
            risks.append(RiskClause(
                type="unlimited_liability",
                severity="critical",
                description="承担无限连带责任，风险敞口过大",
                mitigation="强烈建议改为有限责任或设置责任上限"
            ))
        
        # 风险3: 自动续约
        if self.has_auto_renewal(contract):
            risks.append(RiskClause(
                type="auto_renewal",
                severity="medium",
                description="合同自动续约，可能无法及时调整合作条件",
                mitigation="建议增加续约前的重新评估机制"
            ))
        
        return risks
```

### 舆情监控

```python
class SentimentMonitor:
    """舆情监控"""
    
    def __init__(self):
        self.sources = [
            NewsSource(),
            SocialMediaSource(),
            CourtSource(),
            RegulatorySource(),
        ]
    
    async def monitor(self, company: Company) -> SentimentReport:
        """监控企业舆情"""
        
        # 1. 收集信息
        mentions = []
        for source in self.sources:
            mentions.extend(await source.search(company.name))
        
        # 2. 去重和排序
        mentions = self.deduplicate(mentions)
        mentions = sorted(mentions, key=lambda x: x.timestamp, reverse=True)
        
        # 3. 情感分析
        for mention in mentions:
            mention.sentiment = self.analyze_sentiment(mention.content)
            mention.relevance = self.assess_relevance(mention, company)
        
        # 4. 风险事件识别
        risk_events = self.identify_risk_events(mentions)
        
        # 5. 生成报告
        return SentimentReport(
            company=company.name,
            period="last_30_days",
            totalMentions=len(mentions),
            sentimentDistribution=self.calculate_distribution(mentions),
            riskEvents=risk_events,
            keyTopics=self.extract_topics(mentions),
            trend=self.analyze_trend(mentions)
        )
    
    def identify_risk_events(self, mentions: List[Mention]) -> List[RiskEvent]:
        """识别风险事件"""
        
        events = []
        
        # 负面舆情聚类
        negative = [m for m in mentions if m.sentiment == "negative"]
        clusters = self.cluster_by_topic(negative)
        
        for cluster in clusters:
            if len(cluster) >= 3:  # 3条以上相关负面
                events.append(RiskEvent(
                    type="negative_publicity",
                    severity=self.assess_severity(cluster),
                    description=self.summarize_cluster(cluster),
                    sources=cluster,
                    date=cluster[0].timestamp
                ))
        
        return events
```

---

## 数据融合

### 多源数据整合

```python
class DataFusionEngine:
    """数据融合引擎"""
    
    def __init__(self):
        self.adapters = {
            "erp": ERPAdapter(),
            "crm": CRMAdapter(),
            "credit": CreditAdapter(),
            "industry": IndustryAdapter(),
            "news": NewsAdapter(),
        }
    
    async def fuse(self, company: Company) -> UnifiedView:
        """融合多源数据"""
        
        # 1. 并行获取各源数据
        tasks = [
            self.adapters["erp"].fetch(company),
            self.adapters["crm"].fetch(company),
            self.adapters["credit"].fetch(company),
            self.adapters["industry"].fetch(company),
            self.adapters["news"].fetch(company),
        ]
        
        results = await asyncio.gather(*tasks)
        
        # 2. 实体对齐
        aligned = self.align_entities(results)
        
        # 3. 冲突解决
        resolved = self.resolve_conflicts(aligned)
        
        # 4. 数据增强
        enhanced = self.enhance_data(resolved)
        
        # 5. 生成统一视图
        return UnifiedView(
            company=company,
            financials=enhanced["erp"],
            customers=enhanced["crm"],
            credit=enhanced["credit"],
            industry=enhanced["industry"],
            sentiment=enhanced["news"],
            conflicts=self.get_conflicts(aligned),
            confidence=self.calculate_confidence(enhanced)
        )
    
    def align_entities(self, results: List[DataSource]) -> AlignedData:
        """实体对齐"""
        
        # 使用统一标识符对齐
        aligned = AlignedData()
        
        for source in results:
            for entity in source.entities:
                # 尝试匹配已有实体
                matched = self.find_match(entity, aligned)
                
                if matched:
                    # 合并属性
                    matched.merge(entity)
                else:
                    # 创建新实体
                    aligned.add(entity)
        
        return aligned
    
    def resolve_conflicts(self, aligned: AlignedData) -> ResolvedData:
        """冲突解决"""
        
        for entity in aligned.entities:
            for attr in entity.attributes:
                if attr.has_conflict():
                    # 基于数据源可信度解决
                    attr.value = self.resolve_by_reliability(attr.sources)
        
        return aligned
```

---

## API 服务

### GraphQL API

```graphql
# 知识图谱查询 API

type Query {
  # 查询企业
  company(id: ID!): Company
  companies(filter: CompanyFilter): [Company]
  
  # 查询关系
  shareholders(companyId: ID!): [Shareholding]
  guarantees(companyId: ID!): [Guarantee]
  affiliates(companyId: ID!): [Affiliation]
  
  # 查询事件
  events(companyId: ID!, type: EventType): [Event]
  timeline(companyId: ID!, from: Date, to: Date): [Event]
  
  # 搜索
  search(query: String!, type: SearchType): [SearchResult]
  
  # 风险分析
  riskProfile(companyId: ID!): RiskProfile
  riskFactors(companyId: ID!): [RiskFactor]
}

type Company {
  id: ID!
  name: String!
  unifiedCode: String
  industry: String
  
  # 财务摘要
  financialSummary: FinancialSummary
  
  # 关系
  shareholders: [Shareholding]
  subsidiaries: [Company]
  affiliates: [Affiliation]
  
  # 风险
  riskProfile: RiskProfile
  riskEvents: [RiskEvent]
  
  # 时间线
  timeline: [Event]
}

type Mutation {
  # 导入数据
  importFinancialReport(companyId: ID!, report: FinancialReportInput!): ImportResult
  importContract(companyId: ID!, contract: ContractInput!): ImportResult
  
  # 更新知识
  updateCompany(id: ID!, data: CompanyInput!): Company
  addEvent(companyId: ID!, event: EventInput!): Event
  
  # 触发分析
  analyzeRisk(companyId: ID!): RiskProfile
  generateReport(companyId: ID!, type: ReportType!): Report
}
```

### 语义搜索 API

```python
class SemanticSearch:
    """语义搜索服务"""
    
    def __init__(self, vector_store):
        self.vector_store = vector_store
        self.encoder = SentenceEncoder()
    
    async def search(self, query: str, filters: Filters) -> SearchResults:
        """语义搜索"""
        
        # 1. 编码查询
        query_embedding = self.encoder.encode(query)
        
        # 2. 向量检索
        candidates = self.vector_store.similarity_search(
            query_embedding,
            k=50,
            filters=filters
        )
        
        # 3. 重排序
        reranked = self.rerank(candidates, query)
        
        # 4. 生成摘要
        for result in reranked:
            result.summary = self.generate_summary(result, query)
        
        return SearchResults(
            query=query,
            results=reranked[:10],
            total=len(candidates)
        )
    
    def rerank(self, candidates: List[Candidate], query: str) -> List[Candidate]:
        """重排序"""
        
        for candidate in candidates:
            # 语义相似度
            semantic_score = candidate.similarity
            
            # 实体匹配度
            entity_score = self.calculate_entity_match(candidate, query)
            
            # 时效性
            recency_score = self.calculate_recency(candidate)
            
            # 权威性
            authority_score = self.calculate_authority(candidate)
            
            # 综合评分
            candidate.score = weighted_sum([
                semantic_score * 0.4,
                entity_score * 0.3,
                recency_score * 0.2,
                authority_score * 0.1
            ])
        
        return sorted(candidates, key=lambda x: x.score, reverse=True)
```

---

## 与 Agent 的集成

### Agent 调用知识库

```python
class KnowledgeClient:
    """知识库客户端"""
    
    def __init__(self, api_endpoint: str):
        self.client = GraphQLClient(api_endpoint)
    
    async def get_company_profile(self, company_id: str) -> CompanyProfile:
        """获取企业画像"""
        
        query = """
        query GetCompany($id: ID!) {
          company(id: $id) {
            id
            name
            industry
            financialSummary {
              revenue
              profit
              assets
              liabilities
            }
            riskProfile {
              overallScore
              factors {
                type
                severity
                description
              }
            }
            timeline(limit: 10) {
              date
              type
              description
            }
          }
        }
        """
        
        result = await self.client.execute(query, {"id": company_id})
        return CompanyProfile(result["company"])
    
    async def search_knowledge(self, query: str, context: Context) -> List[Knowledge]:
        """搜索知识"""
        
        # 语义搜索
        search_result = await self.semantic_search(query, context.filters)
        
        # 过滤相关度
        relevant = [r for r in search_result if r.score > 0.7]
        
        # 获取完整内容
        knowledge = []
        for result in relevant:
            content = await self.get_full_content(result.id)
            knowledge.append(Knowledge(
                id=result.id,
                content=content,
                relevance=result.score,
                source=result.source
            ))
        
        return knowledge
    
    async def alert_risks(self, company_id: str) -> List[RiskAlert]:
        """获取风险预警"""
        
        query = """
        query GetRiskAlerts($companyId: ID!) {
          riskFactors(companyId: $companyId) {
            type
            severity
            description
            indicators {
              name
              value
              threshold
            }
          }
        }
        """
        
        result = await self.client.execute(query, {"companyId": company_id})
        
        alerts = []
        for factor in result["riskFactors"]:
            if factor["severity"] in ["high", "critical"]:
                alerts.append(RiskAlert(
                    type=factor["type"],
                    severity=factor["severity"],
                    description=factor["description"],
                    indicators=factor["indicators"]
                ))
        
        return alerts
```

### 尽调流程中的知识调用

```
用户: "帮我做某某科技的尽调"

Agent: 调用知识库 API...

┌─────────────────────────────────────────────────────────────┐
│  1. 获取企业画像                                             │
├─────────────────────────────────────────────────────────────┤
│  GET /api/companies/某某科技                                  │
│  → 基本信息、财务摘要、风险画像、近期事件                     │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  2. 搜索相关案例                                             │
├─────────────────────────────────────────────────────────────┤
│  POST /api/search                                            │
│  {                                                           │
│    "query": "软件行业 中型企业 应收账款风险",                 │
│    "filters": {"industry": "软件", "scale": "medium"}         │
│  }                                                           │
│  → 相似案例、历史教训、专家模板                              │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  3. 风险预警检查                                             │
├─────────────────────────────────────────────────────────────┤
│  GET /api/companies/某某科技/risk-alerts                    │
│  → 当前风险因子、预警指标、需要关注的点                       │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  4. 获取缺失数据清单                                         │
├─────────────────────────────────────────────────────────────┤
│  GET /api/companies/某某科技/data-gaps                      │
│  → 需要补充的财务数据、合同、征信报告等                       │
└─────────────────────────────────────────────────────────────┘

Agent: 基于知识库信息，我已经了解了该企业：
- 成立5年，年营收3亿，软件行业
- 风险等级: 中等
- 近期风险: 应收账款周转天数增加
- 相似案例: 发现3个可参考案例

开始尽调...
```

---

## 知识库维护

### 数据更新策略

```python
class KnowledgeMaintenance:
    """知识库维护"""
    
    async def scheduled_update(self):
        """定时更新"""
        
        # 1. 更新外部数据
        await self.update_external_data()
        
        # 2. 重新计算指标
        await self.recalculate_metrics()
        
        # 3. 更新风险画像
        await self.update_risk_profiles()
        
        # 4. 生成洞察
        await self.generate_insights()
    
    async def update_external_data(self):
        """更新外部数据"""
        
        for company in self.get_active_companies():
            # 工商信息
            business_info = await self.fetch_business_info(company)
            if business_info.changed:
                await self.update_company(company, business_info)
            
            # 舆情信息
            sentiment = await self.fetch_sentiment(company)
            await self.add_sentiment_data(company, sentiment)
            
            # 股价信息 (上市公司)
            if company.is_public:
                stock = await self.fetch_stock_data(company)
                await self.update_stock_data(company, stock)
    
    async def generate_insights(self):
        """生成洞察"""
        
        for company in self.get_active_companies():
            # 趋势分析
            trends = self.analyze_trends(company)
            
            # 异常检测
            anomalies = self.detect_anomalies(company)
            
            # 风险预警
            risks = self.assess_risks(company)
            
            # 保存洞察
            await self.save_insights(company, {
                "trends": trends,
                "anomalies": anomalies,
                "risks": risks
            })
```

---

## 关键设计原则

1. **知识图谱为核心** - 所有信息都关联到实体和关系
2. **文档智能** - 自动解析非结构化文档
3. **多源融合** - 内部 + 外部数据整合
4. **实时更新** - 持续监控，及时更新
5. **API 优先** - 所有功能通过 API 暴露给 Agent

---

## 与 Karpathy 知识库理念的对比

| 维度 | Karpathy 个人知识库 | 企业知识管理 |
|------|---------------------|--------------|
| 目标 | 个人学习、笔记管理 | 企业尽调、风险分析 |
| 内容 | 文章、代码、想法 | 财务、合同、舆情、关系 |
| 结构 | 标签 + 链接 | 知识图谱 + 实体关系 |
| 更新 | 手动为主 | 自动 + 手动 |
| 使用 | 个人查询 | Agent API 调用 |
| 核心 | 让 AI 读懂我 | 让 AI 懂企业 |

---

## 下一步

- [ ] 设计知识图谱 schema
- [ ] 实现财报解析器
- [ ] 搭建 GraphQL API
- [ ] 集成向量搜索
- [ ] 开发数据融合引擎


