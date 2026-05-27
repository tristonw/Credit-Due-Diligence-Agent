import { Link, Route, Routes } from "react-router-dom";
import EmployeeList from "./pages/EmployeeList.jsx";
import CreateEmployee from "./pages/CreateEmployee.jsx";
import EmployeeDetail from "./pages/EmployeeDetail.jsx";
import PromotionReview from "./pages/PromotionReview.jsx";

export default function App() {
  return (
    <>
      <nav>
        <span className="brand">🧑‍💼 数字员工平台</span>
        <Link to="/">员工列表</Link>
        <Link to="/create">创建数字员工</Link>
        <Link to="/promotions">升级审批</Link>
      </nav>
      <div className="container">
        <Routes>
          <Route path="/" element={<EmployeeList />} />
          <Route path="/create" element={<CreateEmployee />} />
          <Route path="/employees/:id" element={<EmployeeDetail />} />
          <Route path="/promotions" element={<PromotionReview />} />
        </Routes>
      </div>
    </>
  );
}
