import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { listEmployees } from "../api.js";

export default function EmployeeList() {
  const [employees, setEmployees] = useState([]);
  useEffect(() => {
    listEmployees().then(setEmployees);
  }, []);

  return (
    <div>
      <h2>数字员工列表</h2>
      {employees.length === 0 && (
        <p className="muted">
          还没有数字员工。<Link to="/create">去创建一个</Link>
        </p>
      )}
      {employees.map((e) => (
        <Link key={e.id} to={`/employees/${e.id}`}>
          <div className="card empcard">
            <div
              className="avatar"
              style={{ background: e.avatar?.color || "#4f46e5" }}
            >
              {e.avatar?.emoji || "🧑‍💼"}
            </div>
            <div style={{ flex: 1 }}>
              <div style={{ fontWeight: 600, fontSize: 16 }}>{e.name}</div>
              <div className="muted">{e.persona}</div>
            </div>
            <div style={{ textAlign: "center" }}>
              <span className="badge">L{e.level}</span>
              <div className="muted">{e.experience} EXP</div>
            </div>
          </div>
        </Link>
      ))}
    </div>
  );
}
