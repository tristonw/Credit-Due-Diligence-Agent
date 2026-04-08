# 模块二：会话管理系统 (Session Management)

> "每一次对话都是一次尽调任务，需要状态机来管理"

---

## 会话的本质

信贷尽调不是一次性问答，而是一个**多阶段、有状态、需协作**的工作流程：

```
用户: "帮我做某某科技的尽调"
   ↓
Agent: "好的，正在收集企业信息..."
   ↓
Agent: "发现几个疑点，需要您确认..."
   ↓
用户: "重点看现金流和关联交易"
   ↓
Agent: "已调整分析重点，这是发现..."
   ↓
... (多轮交互)
   ↓
Agent: "报告已完成，请审阅"
```

---

## 会话状态机

```
                    ┌─────────────┐
         ┌─────────│    INIT     │─────────┐
         │         └─────────────┘         │
         │                │                │
         ▼                ▼                ▼
┌────────────────┐ ┌─────────────┐ ┌─────────────┐
│  INTERRUPTED   │ │ DATA_COLLECTION│  ABORTED    │
│   (中断保存)   │ │  (数据收集)  │   (中止)     │
└────────────────┘ └─────────────┘ └─────────────┘
         │                │
         │                ▼
         │         ┌─────────────┐
         │         │   ANALYSIS  │
         │         │   (分析)    │
         │         └─────────────┘
         │                │
         │                ▼
         │         ┌─────────────┐
         │         │    DRAFT    │
         │         │  (报告起草) │
         │         └─────────────┘
         │                │
         │                ▼
         │         ┌─────────────┐
         │         │   REVIEW    │
         │         │  (审核迭代) │
         │         └─────────────┘
         │                │
         │                ▼
         │         ┌─────────────┐
         └────────→│    FINAL    │←────────┐
                   │  (完成输出) │         │
                   └─────────────┘         │
                          │               │
                          ▼               │
                   ┌─────────────┐        │
                   │  ARCHIVED   │        │
                   │  (归档保存) │────────┘
                   └─────────────┘   (新需求)
```

---

## 会话状态定义

```typescript
interface SessionState {
  // === 基础信息 ===
  sessionId: string;           // 会话唯一ID
  createdAt: DateTime;         // 创建时间
  updatedAt: DateTime;         // 最后更新时间
  userId: string;              // 用户ID
  
  // === 阶段状态 ===
  phase: Phase;                // 当前阶段
  phaseHistory: PhaseLog[];    // 阶段变更历史
  
  // === 目标企业 ===
  target: {
    name: string;              // 企业名称
    unifiedCode: string;       // 统一社会信用代码
    industry: string;          // 行业分类
    scale: string;             // 企业规模
    status: string;            // 经营状态
  };
  
  // === 数据收集状态 ===
  dataCollection: {
    completed: string[];       // 已完成的数据项
    pending: string[];         // 待收集的数据项
    missing: string[];         // 缺失数据清单
    quality: DataQuality;      // 数据质量评估
  };
  
  // === 分析状态 ===
  analysis: {
    financial: AnalysisStatus;
    operational: AnalysisStatus;
    risk: AnalysisStatus;
    collateral?: AnalysisStatus;
  };
  
  // === 报告状态 ===
  report: {
    version: number;           // 报告版本
    sections: SectionStatus[]; // 各章节状态
    currentDraft?: string;     // 当前草稿内容
    feedback?: Feedback[];     // 用户反馈
  };
  
  // === 上下文指针 ===
  pointers: {
    lastAction: string;        // 最后执行的动作
    nextAction: string;        // 下一步动作
    focus: string;             // 当前焦点
    pendingQuestions: string[];// 待用户确认的问题
    userIntent: string;        // 用户意图摘要
  };
  
  // === 压缩摘要 ===
  summary: CompressedSummary;  // 会话整体摘要
}

interface PhaseLog {
  from: Phase;
  to: Phase;
  timestamp: DateTime;
  reason: string;
  triggeredBy: string;
}

interface AnalysisStatus {
  status: 'pending' | 'in_progress' | 'completed' | 'failed';
  progress: number;            // 0-100
  findings: Finding[];         // 分析发现
  confidence: number;          // 置信度
}

interface CompressedSummary {
  version: number;             // 摘要版本
  keyFindings: string[];       // 关键发现(最多10条)
  riskFlags: RiskFlag[];       // 风险标记
  confidence: number;          // 整体置信度
  expertNotes: string;         // 专家批注
  lastCheckpoint: DateTime;    // 最后检查点
}
```

---

## 状态转换规则

```python
class StateMachine:
    """会话状态机"""
    
    TRANSITIONS = {
        'INIT': {
            'start_collection': 'DATA_COLLECTION',
            'abort': 'ABORTED'
        },
        'DATA_COLLECTION': {
            'collection_complete': 'ANALYSIS',
            'insufficient_data': 'INIT',  # 返回补充
            'interrupt': 'INTERRUPTED',
            'abort': 'ABORTED'
        },
        'ANALYSIS': {
            'analysis_complete': 'DRAFT',
            'need_more_data': 'DATA_COLLECTION',
            'interrupt': 'INTERRUPTED',
            'abort': 'ABORTED'
        },
        'DRAFT': {
            'draft_complete': 'REVIEW',
            'need_reanalysis': 'ANALYSIS',
            'interrupt': 'INTERRUPTED',
            'abort': 'ABORTED'
        },
        'REVIEW': {
            'approved': 'FINAL',
            'need_revision': 'DRAFT',
            'need_major_change': 'ANALYSIS',
            'interrupt': 'INTERRUPTED',
            'abort': 'ABORTED'
        },
        'FINAL': {
            'archive': 'ARCHIVED',
            'new_request': 'INIT'
        },
        'INTERRUPTED': {
            'resume': 'DATA_COLLECTION',  # 或回到中断前的阶段
            'abort': 'ABORTED'
        },
        'ABORTED': {
            'restart': 'INIT'
        },
        'ARCHIVED': {
            'clone': 'INIT'  # 基于归档创建新会话
        }
    }
    
    def can_transition(self, from_phase: Phase, action: str) -> bool:
        return action in self.TRANSITIONS.get(from_phase, {})
    
    def transition(self, session: Session, action: str, reason: str) -> Phase:
        if not self.can_transition(session.phase, action):
            raise InvalidTransitionError(f"Cannot {action} from {session.phase}")
        
        new_phase = self.TRANSITIONS[session.phase][action]
        
        # 记录变更
        session.phaseHistory.append({
            'from': session.phase,
            'to': new_phase,
            'timestamp': now(),
            'reason': reason,
            'triggeredBy': action
        })
        
        session.phase = new_phase
        session.updatedAt = now()
        
        return new_phase
```

---

## 会话持久化

### 存储策略

```python
class SessionStore:
    """会话存储管理"""
    
    def __init__(self):
        self.db = SQLite('sessions.db')
        self.cache = LRUCache(maxsize=100)
    
    def save(self, session: Session):
        """保存会话"""
        # 1. 序列化
        data = self.serialize(session)
        
        # 2. 写入数据库
        self.db.execute('''
            INSERT OR REPLACE INTO sessions 
            (id, user_id, phase, data, updated_at)
            VALUES (?, ?, ?, ?, ?)
        ''', [session.sessionId, session.userId, 
              session.phase, data, now()])
        
        # 3. 更新缓存
        self.cache[session.sessionId] = session
    
    def load(self, sessionId: str) -> Session:
        """加载会话"""
        # 1. 检查缓存
        if sessionId in self.cache:
            return self.cache[sessionId]
        
        # 2. 查询数据库
        row = self.db.query(
            'SELECT * FROM sessions WHERE id = ?', 
            [sessionId]
        )
        
        if not row:
            raise SessionNotFoundError(sessionId)
        
        # 3. 反序列化
        session = self.deserialize(row['data'])
        
        # 4. 更新缓存
        self.cache[sessionId] = session
        
        return session
    
    def list_active(self, userId: str) -> List[SessionSummary]:
        """列出用户的活跃会话"""
        return self.db.query('''
            SELECT id, target_name, phase, updated_at, summary
            FROM sessions
            WHERE user_id = ? AND phase NOT IN ('FINAL', 'ARCHIVED', 'ABORTED')
            ORDER BY updated_at DESC
        ''', [userId])
    
    def archive(self, sessionId: str):
        """归档会话"""
        # 移动到归档表
        self.db.execute('''
            INSERT INTO archived_sessions 
            SELECT * FROM sessions WHERE id = ?
        ''', [sessionId])
        
        self.db.execute('DELETE FROM sessions WHERE id = ?', [sessionId])
        
        # 清理缓存
        self.cache.pop(sessionId, None)
```

### 自动保存机制

```python
class AutoSave:
    """自动保存管理"""
    
    def __init__(self, store: SessionStore):
        self.store = store
        self.pending_saves = {}
    
    def mark_dirty(self, sessionId: str):
        """标记会话需要保存"""
        self.pending_saves[sessionId] = now()
    
    async def save_loop(self):
        """自动保存循环"""
        while True:
            await sleep(30)  # 每30秒检查一次
            
            for sessionId, last_change in list(self.pending_saves.items()):
                if now() - last_change > 30:  # 30秒无变更则保存
                    session = active_sessions[sessionId]
                    self.store.save(session)
                    del self.pending_saves[sessionId]
                    logger.info(f"Auto-saved session {sessionId}")
```

---

## 会话恢复

```python
class SessionRecovery:
    """会话恢复管理"""
    
    def create_checkpoint(self, session: Session) -> Checkpoint:
        """创建检查点"""
        checkpoint = {
            'timestamp': now(),
            'phase': session.phase,
            'data': deepcopy(session),
            'summary': generate_checkpoint_summary(session)
        }
        
        session.checkpoints.append(checkpoint)
        
        # 只保留最近10个检查点
        if len(session.checkpoints) > 10:
            session.checkpoints = session.checkpoints[-10:]
        
        return checkpoint
    
    def restore(self, session: Session, checkpointId: str) -> Session:
        """恢复到检查点"""
        checkpoint = find(session.checkpoints, id=checkpointId)
        
        if not checkpoint:
            raise CheckpointNotFoundError(checkpointId)
        
        # 创建恢复记录
        session.recoveryHistory.append({
            'from': session.phase,
            'to': checkpoint['phase'],
            'timestamp': now(),
            'checkpointId': checkpointId
        })
        
        # 恢复状态
        return deepcopy(checkpoint['data'])
    
    def resume_interrupted(self, sessionId: str) -> Session:
        """恢复中断的会话"""
        session = self.store.load(sessionId)
        
        if session.phase != 'INTERRUPTED':
            raise NotInterruptedError(sessionId)
        
        # 找到中断前的阶段
        last_active_phase = session.phaseHistory[-1]['from']
        session.phase = last_active_phase
        
        # 更新摘要
        session.summary.lastCheckpoint = now()
        
        return session
```

---

## 用户交互设计

### 会话启动

```
用户: "帮我做某某科技的尽调"

Agent: 🎯 启动信贷尽调流程

【新建会话】ID: DD-2024-0408-001

📋 阶段: 数据收集
🏢 目标: 某某科技有限公司  
⏱️ 预计: 15-20分钟

【已发现】
✓ 工商注册: 存续，注册资本5000万
✓ 行业分类: 软件和信息技术服务业
✓ 成立时间: 2015年(9年)

【数据缺口】
⏳ 财务报表(需要您上传)
⏳ 征信报告
⏳ 主要合同

请上传相关材料，或告诉我重点关注哪些方面。
```

### 会话恢复

```
用户: "继续之前的尽调"

Agent: 📂 找到 3 个进行中的尽调:

1. 【某某科技】数据收集阶段 (2小时前)
   进度: 60% | 等待: 财务数据

2. 【ABC制造】分析阶段 (昨天)
   进度: 80% | 发现: 2个风险点

3. 【XYZ贸易】报告起草 (3天前)
   进度: 90% | 状态: 待审核

回复数字继续，或输入"新建"开始新尽调。
```

### 状态变更通知

```
Agent: 🔄 阶段推进

【状态变更】
数据收集 → 深度分析

原因: 基础数据已收集完成
时间: 2024-04-08 14:32

【当前焦点】
🔍 财务分析: 盈利能力评估
📊 进度: 35%

预计下一阶段: 报告起草 (约10分钟后)
```

---

## 关键设计原则

1. **显式状态** - 每个阶段清晰定义，用户知道当前在哪
2. **可中断** - 随时可暂停，下次无缝恢复
3. **可追溯** - 完整的历史记录，知道为什么变到这里
4. **可回退** - 检查点机制，可以回到之前的状态
5. **用户可控** - 用户可以强制改变阶段或焦点

---

## 下一步

- [ ] 实现状态机核心逻辑
- [ ] 设计数据库存储 schema
- [ ] 实现自动保存机制
- [ ] 设计用户交互界面
