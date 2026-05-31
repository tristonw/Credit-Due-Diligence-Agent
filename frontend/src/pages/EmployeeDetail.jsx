import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import {
  compareEval,
  evaluate,
  evaluateJudgment,
  getDeposits,
  getEmployee,
  getExperienceLog,
  getLeveling,
  getLevelingCurve,
  judge,
  labelTask,
  listCorpus,
  runTask,
  train,
  uploadCorpus,
} from "../api.js";
import { BarChart, LineChart, ProficiencyDots, RadialProgress } from "../components/charts.jsx";
import Avatar from "../components/Avatar.jsx";

export default function EmployeeDetail() {
  const { id } = useParams();
  const [emp, setEmp] = useState(null);
  const [leveling, setLeveling] = useState(null);
  const [deposits, setDeposits] = useState(null);
  const [expLog, setExpLog] = useState([]);
  const [curve, setCurve] = useState([]);
  const [tab, setTab] = useState("profile");

  const [corpusTitle, setCorpusTitle] = useState("");
  const [corpusText, setCorpusText] = useState("");
  const [corpusLabel, setCorpusLabel] = useState("");
  const [corpusFeedback, setCorpusFeedback] = useState("");
  const [corpusSplit, setCorpusSplit] = useState("train");
  const [corpusList, setCorpusList] = useState([]);
  const [trainMsg, setTrainMsg] = useState("");

  const [judgeText, setJudgeText] = useState("");
  const [judgeTruth, setJudgeTruth] = useState("");
  const [lastJudgment, setLastJudgment] = useState(null);
  const [accuracy, setAccuracy] = useState(null);
  const [judgeBusy, setJudgeBusy] = useState(false);

  const [cmp, setCmp] = useState(null);
  const [evalMsg, setEvalMsg] = useState("");

  const [taskPrompt, setTaskPrompt] = useState("");
  const [lastTask, setLastTask] = useState(null);
  const [taskMsg, setTaskMsg] = useState("");

  const refresh = async () => {
    setEmp(await getEmployee(id));
    setLeveling(await getLeveling(id));
    setDeposits(await getDeposits(id));
    setCmp(await compareEval(id));
    setExpLog(await getExperienceLog(id));
    setCorpusList(await listCorpus(id));
  };

  useEffect(() => {
    refresh();
    getLevelingCurve(8).then(setCurve);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id]);

  if (!emp || !leveling) return <p className="muted">加载中…</p>;

  const doUpload = async () => {
    if (!corpusText.trim()) return;
    await uploadCorpus(id, {
      title: corpusTitle,
      text: corpusText,
      label: corpusLabel || null,
      feedback: corpusFeedback,
      split: corpusSplit,
    });
    setCorpusText("");
    setCorpusTitle("");
    setCorpusFeedback("");
    setCorpusLabel("");
    setCorpusSplit("train");
    setTrainMsg("语料已上传。可继续追加，或点击「开始培训」蒸馏判定标准。");
    refresh();
  };
  const doTrain = async () => {
    setTrainMsg("培训中…");
    const r = await train(id);
    const mode = r.mode === "labeled" ? "监督蒸馏" : "通用培训";
    const labelInfo = r.mode === "labeled" ? `（${r.pass_size} 份通过 / ${r.fail_size} 份不通过）` : "";
    setTrainMsg(
      `${mode}完成${labelInfo}：${r.summary} — 新增沉淀 技能${r.deposits.skills} / 标准${r.deposits.standards} / SOP${r.deposits.sops} / 规则${r.deposits.rules}`
    );
    refresh();
  };
  const doJudge = async () => {
    if (!judgeText.trim()) return;
    setJudgeBusy(true);
    try {
      const r = await judge(id, judgeText, judgeTruth || null);
      setLastJudgment(r);
      refresh();
    } finally {
      setJudgeBusy(false);
    }
  };
  const doEvalJudgment = async () => {
    const r = await evaluateJudgment(id);
    setAccuracy(r);
    refresh();
  };
  const doEval = async (phase) => {
    setEvalMsg(`正在进行${phase === "baseline" ? "基线" : "培训后"}测评…`);
    const r = await evaluate(id, phase);
    setEvalMsg(`测评完成，得分 ${r.score}`);
    setCmp(await compareEval(id));
  };
  const doTask = async () => {
    if (!taskPrompt.trim()) return;
    const r = await runTask(id, taskPrompt);
    setLastTask(r);
    setTaskMsg("");
    setTaskPrompt("");
    refresh();
  };
  const doLabel = async (rating) => {
    if (!lastTask) return;
    const r = await labelTask(lastTask.task_id, rating);
    setTaskMsg(`已打标 ${rating}，经验 ${r.exp_delta > 0 ? "+" : ""}${r.exp_delta}` + (r.promotion_request_id ? "（已触发升级审批，需专家确认）" : ""));
    refresh();
  };

  return (
    <div>
      {/* avatar with level ring + leveling header (features 6 & 5) */}
      <div className="card empcard">
        <div style={{ position: "relative", width: 96, height: 96 }}>
          <RadialProgress progress={leveling.progress} size={96} />
          <div style={{ position: "absolute", top: 11, left: 11 }}>
            <Avatar avatar={emp.avatar} size={74} />
          </div>
        </div>
        <div style={{ flex: 1 }}>
          <div style={{ fontWeight: 700, fontSize: 20 }}>
            {emp.name} <span className="badge">L{emp.level}</span>
          </div>
          <div className="muted">{emp.persona}</div>
          <div style={{ marginTop: 8 }}>
            <div className="expbar">
              <div style={{ width: `${Math.round(leveling.progress * 100)}%` }} />
            </div>
            <div className="muted" style={{ marginTop: 4 }}>
              {emp.experience} / {leveling.exp_for_next} EXP → L{emp.level + 1}
              {leveling.needs_expert_approval && "（下一级需专家确认）"}
            </div>
          </div>
        </div>
      </div>

      <div className="tabs">
        {["profile", "train", "judge", "evaluate", "growth", "task"].map((t) => (
          <button key={t} className={tab === t ? "active" : ""} onClick={() => setTab(t)}>
            {{
              profile: "档案/沉淀物",
              train: "语料&培训",
              judge: "判定&准确率",
              evaluate: "基线对比",
              growth: "成长曲线",
              task: "工作&打标",
            }[t]}
          </button>
        ))}
      </div>

      {tab === "profile" && deposits && (
        <>
          <Section title="工作大纲">
            <pre style={{ whiteSpace: "pre-wrap" }}>{JSON.stringify(emp.outline?.content, null, 2)}</pre>
          </Section>
          <SkillTable items={deposits.skills} />
          <DepositTable title="工作标准" items={deposits.standards} cols={["name"]} />
          <DepositTable title="SOP" items={deposits.sops} cols={["title"]} />
          <DepositTable title="数据质量规则" items={deposits.rules} cols={["name", "rule_expr", "severity"]} />
        </>
      )}

      {tab === "growth" && (
        <>
          <Section title="经验成长轨迹">
            {expLog.length ? (
              <LineChart points={expLog.map((e, i) => ({ x: i + 1, y: e.balance_after }))} />
            ) : (
              <p className="muted">还没有经验记录，去「工作&打标」让员工做点事吧。</p>
            )}
            <p className="muted">每个点是一次经验变动后的累计值（完成任务/人工打标）。</p>
          </Section>
          <Section title="升级难度曲线">
            <LineChart
              points={curve.map((c) => ({ x: c.level, y: c.step_exp }))}
              color="#7c3aed"
              fill="rgba(124,58,237,0.12)"
            />
            <p className="muted">
              当前 L{emp.level}，升到 L{emp.level + 1} 需 {leveling.exp_for_next - leveling.exp_for_current} 经验，越往后越陡。
            </p>
          </Section>
          <Section title="经验流水">
            <table>
              <thead><tr><th>变动</th><th>原因</th><th>余额</th></tr></thead>
              <tbody>
                {[...expLog].reverse().map((e) => (
                  <tr key={e.id}>
                    <td style={{ color: e.delta >= 0 ? "#16a34a" : "#dc2626", fontWeight: 600 }}>
                      {e.delta > 0 ? "+" : ""}{e.delta}
                    </td>
                    <td>{e.reason}</td>
                    <td>{e.balance_after}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </Section>
        </>
      )}

      {tab === "train" && (
        <>
          <Section title="上传语料（可标注 通过/不通过 用于蒸馏）">
            <label>语料标题</label>
            <input
              value={corpusTitle}
              onChange={(e) => setCorpusTitle(e.target.value)}
              placeholder="例如：候选人A 后端面试记录"
            />
            <label>语料内容</label>
            <textarea
              rows={6}
              value={corpusText}
              onChange={(e) => setCorpusText(e.target.value)}
              placeholder="粘贴面试记录原文…"
            />
            <div className="row" style={{ marginTop: 8, gap: 18 }}>
              <div style={{ flex: 1, minWidth: 180 }}>
                <label>标签（面试反馈）</label>
                <select
                  value={corpusLabel}
                  onChange={(e) => setCorpusLabel(e.target.value)}
                  style={{ width: "100%", padding: "9px 12px", borderRadius: 8, border: "1px solid var(--border)" }}
                >
                  <option value="">无标签（纯文本）</option>
                  <option value="pass">通过</option>
                  <option value="fail">不通过</option>
                </select>
              </div>
              <div style={{ flex: 1, minWidth: 180 }}>
                <label>用途</label>
                <select
                  value={corpusSplit}
                  onChange={(e) => setCorpusSplit(e.target.value)}
                  style={{ width: "100%", padding: "9px 12px", borderRadius: 8, border: "1px solid var(--border)" }}
                >
                  <option value="train">训练集（用于蒸馏）</option>
                  <option value="test">测试集（用于验证准确率）</option>
                </select>
              </div>
            </div>
            <label>反馈备注（可选，描述为什么通过/不通过）</label>
            <input
              value={corpusFeedback}
              onChange={(e) => setCorpusFeedback(e.target.value)}
              placeholder="例如：系统设计权衡讲得清楚，但量化结果不够"
            />
            <div className="row" style={{ marginTop: 14 }}>
              <button className="secondary" onClick={doUpload}>上传语料</button>
              <button onClick={doTrain}>开始培训/蒸馏</button>
            </div>
            {trainMsg && <p className="muted" style={{ marginTop: 10 }}>{trainMsg}</p>}
          </Section>

          <Section title={`已上传语料（${corpusList.length}）`}>
            {corpusList.length === 0 ? (
              <p className="muted">还没有语料，上传几份带标签的面试记录开始吧。</p>
            ) : (
              <table>
                <thead>
                  <tr><th>标题</th><th>标签</th><th>用途</th><th>反馈</th></tr>
                </thead>
                <tbody>
                  {corpusList.map((c) => (
                    <tr key={c.id}>
                      <td>{c.title || `语料 #${c.id}`}</td>
                      <td>
                        {c.label === "pass" && <span className="tag" style={{ background: "#dcfce7", color: "#15803d" }}>通过</span>}
                        {c.label === "fail" && <span className="tag" style={{ background: "#fee2e2", color: "#b91c1c" }}>不通过</span>}
                        {!c.label && <span className="muted">—</span>}
                      </td>
                      <td>
                        <span className="tag">{c.split === "test" ? "测试集" : "训练集"}</span>
                      </td>
                      <td className="muted" style={{ maxWidth: 320 }}>{c.feedback || "—"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </Section>
        </>
      )}

      {tab === "judge" && (
        <>
          <Section title="判定新候选人">
            <label>面试记录全文</label>
            <textarea
              rows={6}
              value={judgeText}
              onChange={(e) => setJudgeText(e.target.value)}
              placeholder="粘贴新候选人的面试记录…"
            />
            <label>真实结果（可选，用于校对并计算经验奖励）</label>
            <select
              value={judgeTruth}
              onChange={(e) => setJudgeTruth(e.target.value)}
              style={{ width: 240, padding: "9px 12px", borderRadius: 8, border: "1px solid var(--border)" }}
            >
              <option value="">未知</option>
              <option value="pass">通过</option>
              <option value="fail">不通过</option>
            </select>
            <div style={{ marginTop: 12 }}>
              <button onClick={doJudge} disabled={judgeBusy || !judgeText.trim()}>
                {judgeBusy ? "判定中…" : "让员工判定"}
              </button>
            </div>
            {lastJudgment && (
              <JudgmentResult result={lastJudgment} />
            )}
          </Section>

          <Section title="批量测试集准确率（hold-out）">
            <p className="muted">
              在「语料&培训」中标记为<strong>测试集</strong>的带标签语料会被自动隐藏在培训外，用于客观计算准确率。
            </p>
            <button onClick={doEvalJudgment}>跑测试集评估</button>
            {accuracy && <AccuracyPanel result={accuracy} />}
          </Section>
        </>
      )}

      {tab === "evaluate" && (
        <Section title="基线测评与提升对比">
          <div className="row">
            <button className="secondary" onClick={() => doEval("baseline")}>培训前基线测评</button>
            <button onClick={() => doEval("post_training")}>培训后测评</button>
          </div>
          {evalMsg && <p className="muted" style={{ marginTop: 10 }}>{evalMsg}</p>}
          {cmp && (cmp.baseline != null || cmp.post_training != null) && (
            <div style={{ marginTop: 16 }}>
              <BarChart
                max={100}
                data={[
                  { label: "培训前", value: cmp.baseline ?? 0, color: "#9ca3af" },
                  { label: "培训后", value: cmp.post_training ?? 0, color: "#16a34a" },
                ]}
              />
              {cmp.delta != null && (
                <p style={{ color: cmp.improved ? "#16a34a" : "#dc2626", fontWeight: 600 }}>
                  提升 {cmp.delta > 0 ? "+" : ""}{cmp.delta} 分（{cmp.improved ? "已提升 ✅" : "未提升"}）
                </p>
              )}
            </div>
          )}
        </Section>
      )}

      {tab === "task" && (
        <Section title="执行工作 & 人工打标">
          <label>任务描述</label>
          <textarea rows={3} value={taskPrompt} onChange={(e) => setTaskPrompt(e.target.value)} />
          <div style={{ marginTop: 12 }}>
            <button onClick={doTask}>让员工执行</button>
          </div>
          {taskMsg && <p className="muted" style={{ marginTop: 10 }}>{taskMsg}</p>}
          {lastTask && (
            <div style={{ marginTop: 14, padding: 14, background: "#f9fafb", borderRadius: 10 }}>
              <div style={{ marginBottom: 8 }}>
                <span className="tag">套用SOP：{lastTask.applied_sop}</span>
                <span className="tag" style={{ background: "#fef3c7", color: "#92400e" }}>
                  质量分 {Math.round(lastTask.quality * 100)}
                </span>
                <span className="tag deposited">+{lastTask.exp_gained} EXP</span>
              </div>
              <pre style={{ whiteSpace: "pre-wrap", margin: "8px 0" }}>{lastTask.output}</pre>
              {lastTask.dq_findings?.length > 0 && (
                <div className="muted" style={{ marginTop: 8 }}>
                  数据质量校验：
                  {lastTask.dq_findings.map((f, i) => (
                    <span key={i} style={{ marginLeft: 8, color: f.passed ? "#16a34a" : "#dc2626" }}>
                      {f.passed ? "✅" : "⚠️"} {f.rule}
                    </span>
                  ))}
                </div>
              )}
              <div className="row" style={{ marginTop: 12 }}>
                <button className="good" onClick={() => doLabel("good")}>👍 好（加经验）</button>
                <button className="bad" onClick={() => doLabel("bad")}>👎 差（扣经验）</button>
              </div>
            </div>
          )}
        </Section>
      )}
    </div>
  );
}

function Section({ title, children }) {
  return (
    <div className="card">
      <h3 style={{ marginTop: 0 }}>{title}</h3>
      {children}
    </div>
  );
}

function SourceTag({ source }) {
  return (
    <span className={`tag ${source === "deposited" ? "deposited" : ""}`}>
      {source === "deposited" ? "培训沉淀" : "初始生成"}
    </span>
  );
}

function SkillTable({ items }) {
  return (
    <div className="card">
      <h3 style={{ marginTop: 0 }}>技能（{items.length}）</h3>
      <table>
        <thead>
          <tr><th>name</th><th>category</th><th>熟练度</th><th>来源</th><th>版本</th></tr>
        </thead>
        <tbody>
          {items.map((it) => (
            <tr key={it.id}>
              <td>{it.name}</td>
              <td>{it.category}</td>
              <td><ProficiencyDots value={it.proficiency} /></td>
              <td><SourceTag source={it.source} /></td>
              <td>v{it.version}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function JudgmentResult({ result }) {
  const j = result.judgment;
  const verdictColor = j.prediction === "pass" ? "#16a34a" : "#dc2626";
  const correctTag =
    j.correct === 1 ? (
      <span className="tag" style={{ background: "#dcfce7", color: "#15803d" }}>判定正确 ✅</span>
    ) : j.correct === 0 ? (
      <span className="tag" style={{ background: "#fee2e2", color: "#b91c1c" }}>判定错误 ❌</span>
    ) : null;
  return (
    <div style={{ marginTop: 16, padding: 14, background: "#f9fafb", borderRadius: 10 }}>
      <div style={{ marginBottom: 8 }}>
        <span style={{ fontSize: 22, fontWeight: 700, color: verdictColor, marginRight: 12 }}>
          {j.prediction === "pass" ? "通过" : "不通过"}
        </span>
        <span className="tag" style={{ background: "#fef3c7", color: "#92400e" }}>
          信心 {Math.round(j.confidence * 100)}%
        </span>
        {correctTag}
        <span className="tag deposited">{result.exp_gained > 0 ? "+" : ""}{result.exp_gained} EXP</span>
      </div>
      <div style={{ marginBottom: 8 }}>{j.reasoning}</div>
      {j.matched_criteria?.length > 0 && (
        <div>
          <div className="muted" style={{ marginBottom: 4 }}>命中证据：</div>
          {j.matched_criteria.map((m, i) => {
            const isPass = m.type === "pass_criterion" || m.type === "keyword" && j.prediction === "pass";
            const bg = m.type === "fail_signal" ? "#fee2e2" : isPass ? "#dcfce7" : "#eef2ff";
            const fg = m.type === "fail_signal" ? "#b91c1c" : isPass ? "#15803d" : "#4f46e5";
            return (
              <span key={i} className="tag" style={{ background: bg, color: fg }}>
                {m.type === "fail_signal" ? "⚠️ " : m.type === "pass_criterion" ? "✅ " : ""}
                {m.name}
              </span>
            );
          })}
        </div>
      )}
    </div>
  );
}

function AccuracyPanel({ result }) {
  if (result.test_size === 0) {
    return (
      <p className="muted" style={{ marginTop: 12 }}>
        测试集为空。请在「语料&培训」里上传一些带标签且用途=测试集的语料。
      </p>
    );
  }
  const pct = (v) => (v == null ? "—" : `${Math.round(v * 100)}%`);
  return (
    <div style={{ marginTop: 16 }}>
      <div className="row">
        <div className="card" style={{ flex: 1, textAlign: "center", marginBottom: 0 }}>
          <div style={{ fontSize: 30, fontWeight: 700, color: "#16a34a" }}>{pct(result.accuracy)}</div>
          <div className="muted">准确率</div>
        </div>
        <div className="card" style={{ flex: 1, textAlign: "center", marginBottom: 0 }}>
          <div style={{ fontSize: 30, fontWeight: 700, color: "#0891b2" }}>{pct(result.precision_pass)}</div>
          <div className="muted">通过精确率</div>
        </div>
        <div className="card" style={{ flex: 1, textAlign: "center", marginBottom: 0 }}>
          <div style={{ fontSize: 30, fontWeight: 700, color: "#7c3aed" }}>{pct(result.recall_pass)}</div>
          <div className="muted">通过召回率</div>
        </div>
        <div className="card" style={{ flex: 1, textAlign: "center", marginBottom: 0 }}>
          <div style={{ fontSize: 30, fontWeight: 700 }}>{result.train_size} / {result.test_size}</div>
          <div className="muted">训练 / 测试样本</div>
        </div>
      </div>
      <div className="card" style={{ marginTop: 16 }}>
        <h4 style={{ marginTop: 0 }}>混淆矩阵</h4>
        <table>
          <thead>
            <tr><th></th><th>真值=通过</th><th>真值=不通过</th></tr>
          </thead>
          <tbody>
            <tr>
              <td><strong>预测=通过</strong></td>
              <td style={{ background: "#dcfce7", fontWeight: 600 }}>TP {result.tp}</td>
              <td style={{ background: "#fef3c7", fontWeight: 600 }}>FP {result.fp}</td>
            </tr>
            <tr>
              <td><strong>预测=不通过</strong></td>
              <td style={{ background: "#fef3c7", fontWeight: 600 }}>FN {result.fn}</td>
              <td style={{ background: "#dcfce7", fontWeight: 600 }}>TN {result.tn}</td>
            </tr>
          </tbody>
        </table>
      </div>
      {result.judgments?.length > 0 && (
        <div className="card">
          <h4 style={{ marginTop: 0 }}>测试集判定明细</h4>
          <table>
            <thead>
              <tr><th>样本</th><th>真值</th><th>预测</th><th>信心</th><th>结果</th></tr>
            </thead>
            <tbody>
              {result.judgments.map((j) => (
                <tr key={j.id}>
                  <td className="muted" style={{ maxWidth: 320 }}>{j.transcript_preview.slice(0, 60)}…</td>
                  <td>{j.ground_truth === "pass" ? "通过" : "不通过"}</td>
                  <td style={{ color: j.prediction === "pass" ? "#16a34a" : "#dc2626", fontWeight: 600 }}>
                    {j.prediction === "pass" ? "通过" : "不通过"}
                  </td>
                  <td>{Math.round(j.confidence * 100)}%</td>
                  <td>{j.correct === 1 ? "✅" : "❌"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

function DepositTable({ title, items, cols }) {
  return (
    <div className="card">
      <h3 style={{ marginTop: 0 }}>{title}（{items.length}）</h3>
      <table>
        <thead>
          <tr>
            {cols.map((c) => <th key={c}>{c}</th>)}
            <th>来源</th><th>版本</th>
          </tr>
        </thead>
        <tbody>
          {items.map((it) => (
            <tr key={it.id}>
              {cols.map((c) => <td key={c}>{String(it[c])}</td>)}
              <td><SourceTag source={it.source} /></td>
              <td>v{it.version}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
