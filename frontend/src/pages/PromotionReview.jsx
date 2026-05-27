import { useEffect, useState } from "react";
import { decidePromotion, listPromotions } from "../api.js";

export default function PromotionReview() {
  const [promotions, setPromotions] = useState([]);
  const [expert, setExpert] = useState("专家");

  const refresh = () => listPromotions("pending").then(setPromotions);
  useEffect(() => {
    refresh();
  }, []);

  const decide = async (pid, approve) => {
    await decidePromotion(pid, approve, expert);
    refresh();
  };

  return (
    <div>
      <h2>升级审批（人工专家确认）</h2>
      <div className="card">
        <label>专家名称</label>
        <input value={expert} onChange={(e) => setExpert(e.target.value)} />
      </div>
      {promotions.length === 0 && <p className="muted">暂无待确认的升级申请。</p>}
      {promotions.map((p) => (
        <div key={p.id} className="card">
          <div style={{ fontWeight: 600 }}>
            员工 #{p.employee_id} 申请升级：L{p.from_level} → L{p.to_level}
          </div>
          <div className="muted">达到高等级，需专家确认能力是否达标。</div>
          <div className="row" style={{ marginTop: 12 }}>
            <button className="good" onClick={() => decide(p.id, true)}>确认升级</button>
            <button className="bad" onClick={() => decide(p.id, false)}>驳回</button>
          </div>
        </div>
      ))}
    </div>
  );
}
