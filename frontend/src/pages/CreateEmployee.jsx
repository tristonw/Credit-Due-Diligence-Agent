import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { createEmployee } from "../api.js";

export default function CreateEmployee() {
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [loading, setLoading] = useState(false);
  const nav = useNavigate();

  const submit = async () => {
    if (!description.trim()) return;
    setLoading(true);
    try {
      const emp = await createEmployee(description, name);
      nav(`/employees/${emp.id}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h2>创建数字员工</h2>
      <div className="card">
        <label>名称（可选）</label>
        <input value={name} onChange={(e) => setName(e.target.value)} placeholder="例如：信贷调查员" />
        <label>用自然语言描述这个数字员工的职责</label>
        <textarea
          rows={5}
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="例如：负责企业信贷尽职调查，分析财务报表、识别风险点并产出尽调报告。"
        />
        <div style={{ marginTop: 12 }}>
          <button onClick={submit} disabled={loading || !description.trim()}>
            {loading ? "生成中…" : "生成数字员工"}
          </button>
        </div>
        <p className="muted" style={{ marginTop: 10 }}>
          系统会基于描述生成：工作大纲、初始技能、工作标准基线、SOP 和数字形象。
        </p>
      </div>
    </div>
  );
}
