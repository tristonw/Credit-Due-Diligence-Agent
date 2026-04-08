# 模块一：上下文压缩系统 (Context Compression System)

> "把 100 页材料压缩成 1 页精华，只保留 AI 需要的信息"

---

## 为什么需要上下文压缩？

### 问题
- 尽调材料动辄几百页：财报、合同、征信、舆情...
- LLM 上下文有限，装不下全部内容
- 重复加载浪费 token，响应变慢

### 解决思路
像人类专家一样：**快速浏览 → 抓取关键 → 结构化记忆**

---

## 三层压缩架构

```
┌─────────────────────────────────────────────────────────────┐
│  Layer 1: 元数据层 (Metadata Layer)                         │
│  常驻内存，随时可用                                           │
├─────────────────────────────────────────────────────────────┤
│  • 当前阶段: DATA_COLLECTION / ANALYSIS / DRAFT            │
│  • 目标企业: {name, industry, scale}                        │
│  • 关键实体索引: 人/公司/数字/风险标签                        │
│  • 会话摘要: 50字一句话总结                                   │
│                                                             │
│  Token: ~500 (极轻量)                                        │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  Layer 2: 工作记忆层 (Working Memory)                        │
│  按需加载，当前焦点                                           │
├─────────────────────────────────────────────────────────────┤
│  • 当前分析对象: 财务/经营/风险/担保                          │
│  • 分析框架: 正在使用的分析模型                               │
│  • 中间结论: 已确认的发现                                     │
│  • 待解决问题: 需要补充的信息                                 │
│                                                             │
│  Token: ~2000 (适中)                                         │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  Layer 3: 深度知识层 (Deep Knowledge)                        │
│  引用加载，用时再取                                           │
├─────────────────────────────────────────────────────────────┤
│  • 行业知识库: 行业特点/周期/政策/标杆                        │
│  • 尽调模板库: 各类报告的标准结构                             │
│  • 历史案例库: 相似企业尽调经验                               │
│  • 法规政策库: 相关法律条文                                   │
│                                                             │
│  Token: 按需，单次 <3000                                     │
└─────────────────────────────────────────────────────────────┘
```

---

## 压缩算法详解

### 1. 财务数据压缩

**原始数据**: 50页年度财报
```
资产负债表、利润表、现金流量表
附注、会计政策、审计意见...
```

**压缩后**: 财务健康度卡片
```json
{
  "revenue": {
    "current": "12.5亿",
    "yoy_growth": "+23%",
    "trend": "连续3年增长",
    "quality": "高(现金收入比>90%)"
  },
  "profitability": {
    "gross_margin": "35%",
    "net_margin": "12%",
    "vs_industry": "高于均值5pct",
    "trend": "稳定"
  },
  "liquidity": {
    "current_ratio": "1.8",
    "quick_ratio": "1.2",
    "cash_flow": "正向",
    "warning": "应收账款增速>收入增速"
  },
  "leverage": {
    "debt_to_equity": "45%",
    "interest_coverage": "8.5x",
    "risk_level": "中等"
  },
  "red_flags": [
    "应收账款周转天数从45天增至78天",
    "存货周转率连续2年下降"
  ],
  "summary": "财务整体健康，但营运资金效率需关注"
}
```

### 2. 行业分析压缩

**原始数据**: 行业研究报告 30页

**压缩后**: 行业定位卡片
```json
{
  "industry": "新能源汽车零部件",
  "lifecycle": "成长期(渗透率30%)",
  "cycle_position": "上行周期",
  "competition": "红海(产能过剩预警)",
  "policy": "支持(补贴退坡但双碳目标)",
  "key_drivers": [
    "电动车渗透率提升",
    "国产替代加速",
    "出口增长"
  ],
  "risk_signals": [
    "价格战加剧",
    "原材料成本波动",
    "客户集中度高"
  ],
  "benchmark": {
    "avg_gross_margin": "25%",
    "avg_debt_ratio": "50%",
    "avg_roe": "12%"
  }
}
```

### 3. 舆情信息压缩

**原始数据**: 100条新闻 + 社交媒体

**压缩后**: 舆情摘要
```json
{
  "sentiment": "中性偏正面",
  "volume": "月均15篇(行业均值20)",
  "key_topics": [
    "产能扩张(正面)",
    "技术突破(正面)",
    "诉讼纠纷(负面-已解决)"
  ],
  "risk_alerts": [],
  "summary": "舆情平稳，无重大负面"
}
```

---

## 压缩策略

### 策略一：结构化提取
```python
def compress_document(doc, schema):
    """
    按预定义 schema 提取信息
    """
    return {
        field: extract(doc, field_rule) 
        for field, field_rule in schema.items()
    }
```

### 策略二：关键句提取
```python
def extract_key_sentences(doc, ratio=0.1):
    """
    提取 top 10% 关键句子
    基于：位置权重 + 关键词密度 + 实体密度
    """
    sentences = split_sentences(doc)
    scores = [score(s) for s in sentences]
    return top_k(sentences, scores, k=len(sentences)*ratio)
```

### 策略三：实体关系图谱
```python
def build_entity_graph(doc):
    """
    提取实体和关系，构建图谱
    """
    entities = extract_entities(doc)  # 人名、公司、数字、时间
    relations = extract_relations(doc, entities)
    return {
        "nodes": entities,
        "edges": relations,
        "key_paths": find_key_paths(entities, relations)
    }
```

### 策略四：指标卡片化
```python
def extract_metrics(doc):
    """
    提取所有数值指标，标准化存储
    """
    metrics = find_all_numbers(doc)
    return {
        m.name: {
            "value": m.value,
            "unit": m.unit,
            "period": m.period,
            "source": m.source,
            "confidence": m.confidence
        }
        for m in metrics
    }
```

---

## 压缩质量评估

| 指标 | 定义 | 目标值 |
|------|------|--------|
| 压缩率 | 压缩后 Token / 原始 Token | < 20% |
| 信息保留率 | 关键信息是否保留 | > 95% |
| 检索准确率 | 基于压缩内容回答问题 | > 90% |
| 生成质量 | 基于压缩内容生成报告 | 专家评分 > 4.0 |

---

## 实现代码示例

```python
class ContextCompressor:
    """上下文压缩引擎"""
    
    def __init__(self):
        self.schemas = load_schemas()  # 加载各类 schema
        self.extractor = LLMExtractor()
    
    def compress(self, document: Document, doc_type: str) -> CompressedDoc:
        # 1. 根据文档类型选择 schema
        schema = self.schemas[doc_type]
        
        # 2. 结构化提取
        structured = self.extractor.extract(document, schema)
        
        # 3. 生成摘要
        summary = self.generate_summary(structured)
        
        # 4. 提取实体关系
        entity_graph = self.build_entity_graph(document)
        
        # 5. 计算置信度
        confidence = self.assess_confidence(structured)
        
        return CompressedDoc(
            type=doc_type,
            data=structured,
            summary=summary,
            entities=entity_graph,
            confidence=confidence,
            hash=compute_hash(document)
        )
    
    def decompress_hint(self, compressed: CompressedDoc, query: str) -> str:
        """
        根据查询生成解压缩提示
        不真正解压缩，而是指导 LLM 如何利用压缩信息
        """
        relevant = self.find_relevant(compressed, query)
        return f"""
        基于 {compressed.type} 文档 (置信度: {compressed.confidence}):
        相关信息: {relevant}
        摘要: {compressed.summary}
        如需详细数据，请引用原文。
        """
```

---

## 关键洞察

1. **压缩不是丢失，是结构化** - 把非结构化文本变成机器友好的格式
2. **分层按需** - 不是所有信息都需要同时加载
3. **保留溯源** - 压缩内容要保留指向原文的链接
4. **置信度标记** - 明确告知 AI 哪些信息可靠

---

## 下一步

- [ ] 实现财务数据压缩 schema
- [ ] 实现行业报告压缩 schema
- [ ] 实现舆情信息压缩 schema
- [ ] 压缩质量评估测试
