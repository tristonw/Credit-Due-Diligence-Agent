# 模块三：记忆系统 (Memory System)

> "Agent 越用越聪明，因为它记得每一次尽调的经验"

---

## 记忆的层次

```
┌─────────────────────────────────────────────────────────────┐
│  L1: 瞬时记忆 (Transient Memory)                            │
│  当前对话轮次，临时计算结果                                    │
├─────────────────────────────────────────────────────────────┤
│  • 用户刚说的话                                               │
│  • 刚提取的实体                                               │
│  • 临时计算结果                                               │
│  生命周期: 秒级                                               │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  L2: 工作记忆 (Working Memory)                              │
│  当前会话的上下文                                             │
├─────────────────────────────────────────────────────────────┤
│  • 本次尽调的目标企业                                         │
│  • 已收集的关键数据                                           │
│  • 当前分析进度                                               │
│  • 待确认的问题清单                                           │
│  生命周期: 会话级                                             │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  L3: 短期记忆 (Short-term Memory)                           │
│  跨会话的经验积累                                             │
├─────────────────────────────────────────────────────────────┤
│  • 最近几次尽调的教训                                         │
│  • 用户偏好设置                                               │
│  • 常用模板片段                                               │
│  生命周期: 天/周级                                            │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  L4: 长期记忆 (Long-term Memory)                            │
│  持久化的知识资产                                             │
├─────────────────────────────────────────────────────────────┤
│  • 行业知识图谱                                               │
│  • 历史尽调案例库                                             │
│  • 专家规则库                                                 │
│  • 自我进化记录                                               │
│  生命周期: 永久                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 记忆索引系统

### 核心问题

当 Agent 需要"回忆"时，如何快速找到相关信息？

```
Agent: "我记得之前做过一个类似的制造业企业..."
        ↓
如何找到那个案例？
        ↓
需要多维度索引
```

### 索引设计

```python
class MemoryIndex:
    """多维度记忆索引"""
    
    def __init__(self):
        # 实体索引: 人名、公司、行业 → 相关记忆
        self.entity_index = {
            # "张三": [memory_id_1, memory_id_2],
            # "制造业": [memory_id_1, memory_id_3],
        }
        
        # 主题索引: 主题 → 相关段落
        self.topic_index = {
            # "现金流分析": [memory_id_1, memory_id_4],
            # "关联交易": [memory_id_2, memory_id_5],
        }
        
        # 时间索引: 时间线
        self.time_index = [
            # {"timestamp": "2024-04-01", "memory_id": "...", "summary": "..."},
        ]
        
        # 类型索引: 记忆类型
        self.type_index = {
            # "case": [...],      # 案例
            # "lesson": [...],    # 教训
            # "template": [...],  # 模板
        }
        
        # 向量索引: 语义相似度
        self.vector_store = ChromaDB()
    
    def index_memory(self, memory: Memory):
        """索引新记忆"""
        # 1. 提取实体
        entities = extract_entities(memory.content)
        for entity in entities:
            self.entity_index.setdefault(entity, []).append(memory.id)
        
        # 2. 提取主题
        topics = extract_topics(memory.content)
        for topic in topics:
            self.topic_index.setdefault(topic, []).append(memory.id)
        
        # 3. 时间索引
        self.time_index.append({
            "timestamp": memory.timestamp,
            "memory_id": memory.id,
            "summary": memory.summary
        })
        
        # 4. 类型索引
        self.type_index.setdefault(memory.type, []).append(memory.id)
        
        # 5. 向量索引
        embedding = self.encode(memory.content)
        self.vector_store.add(memory.id, embedding, {
            "type": memory.type,
            "entities": entities,
            "topics": topics
        })
    
    def retrieve(self, query: Query, k: int = 5) -> List[Memory]:
        """检索相关记忆"""
        # 1. 实体匹配
        entity_matches = self._match_entities(query.entities)
        
        # 2. 语义相似度
        query_embedding = self.encode(query.text)
        semantic_matches = self.vector_store.similarity_search(
            query_embedding, k=k*2
        )
        
        # 3. 主题匹配
        topic_matches = self._match_topics(query.topics)
        
        # 4. 时间衰减加权
        time_weighted = self._apply_time_decay(semantic_matches)
        
        # 5. 融合排序
        return self._fusion_rank(
            entity_matches, 
            topic_matches, 
            time_weighted, 
            k=k
        )
```

---

## 记忆类型

### 1. 案例记忆 (Case Memory)

```python
@dataclass
class CaseMemory:
    """尽调案例记忆"""
    id: str
    timestamp: DateTime
    
    # 企业信息
    company: {
        "name": str,
        "industry": str,
        "scale": str,
        "region": str,
    }
    
    # 尽调结果
    findings: List[Finding]
    
    # 关键指标
    key_metrics: Dict[str, Any]
    
    # 风险点
    risks: List[Risk]
    
    # 报告质量评分
    quality_score: float
    
    # 用户反馈
    user_feedback: Feedback
    
    # 可复用的分析片段
    reusable_snippets: List[Snippet]
    
    def similarity_to(self, target: Company) -> float:
        """计算与目标企业的相似度"""
        scores = [
            industry_match(self.company.industry, target.industry),
            scale_match(self.company.scale, target.scale),
            region_match(self.company.region, target.region),
        ]
        return weighted_average(scores)
```

### 2. 教训记忆 (Lesson Memory)

```python
@dataclass
class LessonMemory:
    """从失败或成功中学到的经验"""
    id: str
    timestamp: DateTime
    
    # 教训类型
    type: "mistake" | "success" | "insight"
    
    # 情境
    context: str
    
    # 发生了什么
    what_happened: str
    
    # 为什么发生
    root_cause: str
    
    # 学到了什么
    lesson: str
    
    # 如何应用
    application: str
    
    # 适用场景
    applicable_scenarios: List[str]
    
    # 使用次数
    usage_count: int
    
    def is_applicable(self, situation: Situation) -> bool:
        """判断此教训是否适用于当前情境"""
        return any(
            match(situation, scenario) 
            for scenario in self.applicable_scenarios
        )
```

### 3. 模板记忆 (Template Memory)

```python
@dataclass
class TemplateMemory:
    """可复用的分析模板"""
    id: str
    timestamp: DateTime
    
    # 模板名称
    name: str
    
    # 适用场景
    applicable_to: {
        "industries": List[str],
        "scenarios": List[str],
        "risk_types": List[str],
    }
    
    # 模板内容
    template: str  # Jinja2 模板
    
    # 使用统计
    usage_stats: {
        "used_count": int,
        "avg_quality_score": float,
        "last_used": DateTime,
    }
    
    # 版本历史
    versions: List[TemplateVersion]
    
    def render(self, context: Dict) -> str:
        """渲染模板"""
        return jinja2_render(self.template, context)
```

---

## 记忆检索策略

### 策略一：相似案例检索

```python
def find_similar_cases(company: Company, k: int = 3) -> List[CaseMemory]:
    """找到相似的尽调案例"""
    
    # 1. 同行业案例
    same_industry = index.query(
        filter={"company.industry": company.industry},
        sort="quality_score"
    )
    
    # 2. 相似规模
    similar_scale = index.query(
        filter={"company.scale": company.scale},
        sort="quality_score"
    )
    
    # 3. 同地区
    same_region = index.query(
        filter={"company.region": company.region}
    )
    
    # 4. 综合排序
    candidates = merge(same_industry, similar_scale, same_region)
    
    # 5. 计算相似度
    for case in candidates:
        case.similarity = case.similarity_to(company)
    
    # 6. 返回 top k
    return sorted(candidates, key=lambda x: x.similarity, reverse=True)[:k]
```

### 策略二：情境匹配

```python
def retrieve_lessons(situation: Situation) -> List[LessonMemory]:
    """检索适用的经验教训"""
    
    # 1. 提取当前情境特征
    features = extract_features(situation)
    
    # 2. 语义检索
    embedding = encode(situation.description)
    semantic_matches = vector_store.similarity_search(embedding, k=10)
    
    # 3. 过滤适用性
    applicable = [
        lesson for lesson in semantic_matches
        if lesson.is_applicable(situation)
    ]
    
    # 4. 按使用频率排序
    return sorted(applicable, key=lambda x: x.usage_count, reverse=True)
```

### 策略三：模板推荐

```python
def recommend_templates(task: Task) -> List[TemplateMemory]:
    """推荐适用的模板"""
    
    # 1. 行业匹配
    industry_match = index.query(
        filter={"applicable_to.industries": task.industry}
    )
    
    # 2. 场景匹配
    scenario_match = index.query(
        filter={"applicable_to.scenarios": task.scenario}
    )
    
    # 3. 风险类型匹配
    risk_match = index.query(
        filter={"applicable_to.risk_types": task.risk_type}
    )
    
    # 4. 综合评分
    candidates = merge(industry_match, scenario_match, risk_match)
    
    for template in candidates:
        template.relevance_score = calculate_relevance(template, task)
    
    return sorted(candidates, key=lambda x: x.relevance_score, reverse=True)
```

---

## 记忆应用示例

### 场景：新尽调开始

```
用户: "帮我做一家新能源电池企业的尽调"

Agent: 🔍 检索相关记忆...

【发现 3 个相似案例】
1. 【某锂电池企业】2024-03-15 | 相似度: 92%
   行业: 新能源电池 | 规模: 中型
   关键发现: 客户集中度高(前5大客户占比80%)
   风险点: 原材料价格波动大
   
2. 【某动力电池企业】2024-02-20 | 相似度: 85%
   行业: 新能源电池 | 规模: 大型
   关键发现: 技术路线存在争议
   风险点: 产能过剩预警
   
3. 【某储能电池企业】2024-01-10 | 相似度: 78%
   行业: 储能电池 | 规模: 中型
   关键发现: 出口增长快但汇率风险

【检索到 2 条适用教训】
⚠️ 教训: 新能源电池企业应收账款周期长
   来源: 某锂电池企业尽调
   建议: 重点关注回款能力和坏账准备

💡 教训: 技术迭代快，需评估研发投入持续性
   来源: 某动力电池企业尽调
   建议: 对比研发费用率和同行水平

【推荐模板】
📋 模板: 新能源行业尽调框架
   适用: 电池/储能/材料企业
   使用次数: 15次 | 平均评分: 4.6/5.0

Agent: 基于以上经验，我建议重点关注:
1. 客户集中度风险
2. 原材料价格波动
3. 技术路线和研发投入
4. 应收账款质量

是否开始尽调?
```

### 场景：风险识别

```
Agent: 💡 记忆提醒

在分析财务数据时，发现该企业的应收账款周转天数
从45天增至78天。

【历史相似情况】
2024-03-15 某锂电池企业也有类似情况:
- 原因: 大客户延长账期
- 风险: 实际为隐性资金占用
- 建议: 核查主要客户信用状况

需要我深入分析这个风险点吗?
```

---

## 记忆维护

### 遗忘机制

```python
def apply_forgetting(memory: Memory):
    """应用遗忘曲线"""
    
    # 艾宾浩斯遗忘曲线
    time_since_last_use = now() - memory.last_accessed
    
    # 重要记忆遗忘慢
    importance_factor = memory.importance_score
    
    # 使用频率高的遗忘慢
    frequency_factor = min(memory.access_count / 10, 1.0)
    
    # 计算保留概率
    retention = calculate_retention(
        time=time_since_last_use,
        importance=importance_factor,
        frequency=frequency_factor
    )
    
    if retention < 0.1:
        # 归档到冷存储
        archive_memory(memory)
    elif retention < 0.5:
        # 降低优先级
        memory.priority = "low"
```

### 记忆整合

```python
def consolidate_memories():
    """定期整合记忆"""
    
    # 1. 合并相似记忆
    similar_pairs = find_similar_memories(threshold=0.9)
    for pair in similar_pairs:
        merged = merge_memories(pair)
        replace_memories(pair, merged)
    
    # 2. 提取通用模式
    patterns = extract_patterns(all_memories)
    for pattern in patterns:
        create_abstract_memory(pattern)
    
    # 3. 更新索引
    rebuild_index()
```

---

## 关键设计原则

1. **多维度索引** - 实体、主题、时间、语义多管齐下
2. **主动推荐** - 不等待查询，主动推送相关记忆
3. **情境感知** - 理解当前情境，匹配最相关的记忆
4. **持续学习** - 每次使用都更新记忆权重
5. **遗忘机制** - 不重要的记忆逐渐淡化

---

## 下一步

- [ ] 实现向量存储集成
- [ ] 设计记忆 schema
- [ ] 实现多维度索引
- [ ] 开发记忆检索 API
