import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getLevelingCurve, getStats, listEmployees } from "../api.js";
import { BarChart, LineChart, StatCard } from "../components/charts.jsx";

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [employees, setEmployees] = useState([]);
  const [curve, setCurve] = useState([]);

  useEffect(() => {
    getStats().then(setStats);
    listEmployees().then(setEmployees);
    getLevelingCurve(8).then(setCurve);
  }, []);

  if (!stats) return <p className="muted">加载中…</p>;

  return (
    <div>
      <h2>平台看板</h2>
      <div className="row" style={{ marginBottom: 16 }}>
        <StatCard label="数字员工" value={stats.employees} />
        <StatCard label="平均等级" value={stats.avg_level} accent="#0891b2" />
        <StatCard label="累计经验" value={stats.total_experience} accent="#7c3aed" />
        <StatCard label="待专家确认" value={stats.pending_promotions} accent="#dc2626" />
      </div>
      <div className="row" style={{ marginBottom: 16 }}>
        <StatCard label="执行任务数" value={stats.tasks} accent="#2563eb" />
        <StatCard label="好评打标" value={stats.labels_good} accent="#16a34a" />
        <StatCard label="差评打标" value={stats.labels_bad} accent="#dc2626" />
        <StatCard label="培训沉淀物" value={stats.deposits} accent="#047857" />
      </div>

      <div className="card">
        <h3 style={{ marginTop: 0 }}>升级经验曲线（越往后越难）</h3>
        <LineChart
          points={curve.map((c) => ({ x: c.level, y: c.step_exp }))}
          color="#7c3aed"
          fill="rgba(124,58,237,0.12)"
        />
        <p className="muted">横轴=等级，纵轴=升到下一级所需经验，体现升级难度递增。</p>
      </div>

      <div className="card">
        <h3 style={{ marginTop: 0 }}>各员工等级对比</h3>
        {employees.length ? (
          <BarChart
            data={employees.map((e) => ({
              label: e.name,
              value: e.level,
              color: e.avatar?.color || "#4f46e5",
            }))}
          />
        ) : (
          <p className="muted">还没有数字员工。<Link to="/create">去创建一个</Link></p>
        )}
      </div>
    </div>
  );
}
