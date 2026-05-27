import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import {
  compareEval,
  evaluate,
  getDeposits,
  getEmployee,
  getExperienceLog,
  getLeveling,
  getLevelingCurve,
  labelTask,
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
  const [trainMsg, setTrainMsg] = useState("");

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
  };

  useEffect(() => {
    refresh();
    getLevelingCurve(8).then(setCurve);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id]);

  if (!emp || !leveling) return <p className="muted">加载中…</p>;

  const doUpload = async () => {
    if (!corpusText.trim()) return;
    await uploadCorpus(id, corpusTitle, corpusText);
    setCorpusText("");
    setCorpusTitle("");
    setTrainMsg("语料已上传，可点击「开始培训」。");
  };
  const doTrain = async () => {
    setTrainMsg("培训中…");
    const r = await train(id);
    setTrainMsg(`培训完成：${r.summary}（新增沉淀 技能${r.deposits.skills}/标准${r.deposits.standards}/SOP${r.deposits.sops}/规则${r.deposits.rules}）`);
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
        {["profile", "growth", "train", "evaluate", "task"].map((t) => (
          <button key={t} className={tab === t ? "active" : ""} onClick={() => setTab(t)}>
            {{ profile: "档案/沉淀物", growth: "成长曲线", train: "培训", evaluate: "测评", task: "工作&打标" }[t]}
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
        <Section title="文本语料培训">
          <label>语料标题</label>
          <input value={corpusTitle} onChange={(e) => setCorpusTitle(e.target.value)} />
          <label>语料内容</label>
          <textarea rows={6} value={corpusText} onChange={(e) => setCorpusText(e.target.value)} />
          <div className="row" style={{ marginTop: 12 }}>
            <button className="secondary" onClick={doUpload}>上传语料</button>
            <button onClick={doTrain}>开始培训</button>
          </div>
          {trainMsg && <p className="muted" style={{ marginTop: 10 }}>{trainMsg}</p>}
        </Section>
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
