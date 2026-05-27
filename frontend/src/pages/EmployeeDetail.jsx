import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import {
  compareEval,
  evaluate,
  getDeposits,
  getEmployee,
  getLeveling,
  labelTask,
  runTask,
  train,
  uploadCorpus,
} from "../api.js";

export default function EmployeeDetail() {
  const { id } = useParams();
  const [emp, setEmp] = useState(null);
  const [leveling, setLeveling] = useState(null);
  const [deposits, setDeposits] = useState(null);
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
  };

  useEffect(() => {
    refresh();
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
    setTaskMsg(`产出：${r.output}`);
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
      {/* avatar + leveling header (features 6 & 5) */}
      <div className="card empcard">
        <div className="avatar" style={{ background: emp.avatar?.color || "#4f46e5" }}>
          {emp.avatar?.emoji || "🧑‍💼"}
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
        {["profile", "train", "evaluate", "task"].map((t) => (
          <button key={t} className={tab === t ? "active" : ""} onClick={() => setTab(t)}>
            {{ profile: "档案/沉淀物", train: "培训", evaluate: "测评", task: "工作&打标" }[t]}
          </button>
        ))}
      </div>

      {tab === "profile" && deposits && (
        <>
          <Section title="工作大纲">
            <pre style={{ whiteSpace: "pre-wrap" }}>{JSON.stringify(emp.outline?.content, null, 2)}</pre>
          </Section>
          <DepositTable title="技能" items={deposits.skills} cols={["name", "category", "proficiency"]} />
          <DepositTable title="工作标准" items={deposits.standards} cols={["name"]} />
          <DepositTable title="SOP" items={deposits.sops} cols={["title"]} />
          <DepositTable title="数据质量规则" items={deposits.rules} cols={["name", "rule_expr", "severity"]} />
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
          {cmp && (
            <table style={{ marginTop: 12 }}>
              <tbody>
                <tr><td>基线得分</td><td>{cmp.baseline ?? "—"}</td></tr>
                <tr><td>培训后得分</td><td>{cmp.post_training ?? "—"}</td></tr>
                <tr>
                  <td>提升</td>
                  <td style={{ color: cmp.improved ? "#16a34a" : "#dc2626" }}>
                    {cmp.delta == null ? "—" : `${cmp.delta > 0 ? "+" : ""}${cmp.delta}（${cmp.improved ? "已提升" : "未提升"}）`}
                  </td>
                </tr>
              </tbody>
            </table>
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
            <div className="row" style={{ marginTop: 10 }}>
              <button className="good" onClick={() => doLabel("good")}>👍 好（加经验）</button>
              <button className="bad" onClick={() => doLabel("bad")}>👎 差（扣经验）</button>
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
              <td>
                <span className={`tag ${it.source === "deposited" ? "deposited" : ""}`}>
                  {it.source === "deposited" ? "培训沉淀" : "初始生成"}
                </span>
              </td>
              <td>v{it.version}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
