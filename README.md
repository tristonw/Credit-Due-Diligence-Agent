# 数字员工平台 (Digital Employee Platform)

基于自然语言生成、培训、测评、沉淀并养成数字员工的平台。构建于 Credit-Due-Diligence-Agent 之上。

## 功能

1. **数字员工生成** — 用自然语言描述，自动生成工作大纲、初始技能、工作标准基线、SOP 与数字形象。
2. **文本语料培训** — 上传文本语料，员工学习并形成培训摘要。
3. **基线测评** — 培训前/后两次测评，量化对比能力提升。
4. **硬沉淀物** — 培训后生成/更新带版本的 SOP、工作标准、技能、数据质量规则（`source=deposited`）。
5. **经验与养成** — 完成任务得经验；人工打标「好」加经验、「差」扣经验；升级曲线越往后越陡。
6. **数字形象** — 每个员工有头像、等级徽章与经验条。
7. **专家确认升级** — 达到高等级（默认 L5+）的升级需人工专家在审批页确认。

## 技术栈

- 后端：FastAPI + SQLAlchemy + SQLite
- 前端：React + Vite
- 大模型：Anthropic Claude（`anthropic` SDK，开启 prompt caching）

> 未配置 `ANTHROPIC_API_KEY` 时，平台自动运行在确定性 **mock 模式**，全流程（含测试）可无密钥跑通。

## 运行

### 后端

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # 可选：填入 ANTHROPIC_API_KEY 启用真实 LLM
uvicorn app.main:app --reload   # http://localhost:8000  (文档 /docs)
```

### 前端

```bash
cd frontend
npm install
npm run dev   # http://localhost:5173 （/api 已代理到后端 8000）
```

### 测试

```bash
cd backend && source .venv/bin/activate && pytest
```

## 端到端流程

创建员工 → 上传语料并培训（看到沉淀物版本递增）→ 培训前/后测评对比提升 → 执行任务并人工打标变更经验 → 攒够经验触发高等级升级 → 在「升级审批」页由专家确认。

## 主要接口

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| POST | `/api/employees` | 自然语言生成数字员工 |
| GET | `/api/employees` / `/api/employees/{id}` | 列表 / 详情 |
| POST | `/api/employees/{id}/corpus` | 上传语料 |
| POST | `/api/employees/{id}/train` | 培训并沉淀 |
| POST | `/api/employees/{id}/evaluate` | 测评（phase=baseline/post_training）|
| GET | `/api/employees/{id}/evaluations/compare` | 前后对比 |
| GET | `/api/employees/{id}/deposits` | 沉淀物（含版本与来源）|
| POST | `/api/employees/{id}/tasks` | 执行任务 |
| POST | `/api/tasks/{id}/label` | 人工打标（加/扣经验）|
| GET | `/api/employees/{id}/leveling` | 经验/等级/进度 |
| GET | `/api/promotions?status=pending` | 待确认升级 |
| POST | `/api/promotions/{id}/decide` | 专家确认/驳回 |
