import { Link } from "react-router-dom";

export function ManagerDashboard() {
  return (
    <section>
      <h1>Панель менеджера</h1>
      <div className="dashboard-grid">
        <Link className="dashboard-card" to="/manager/products">Товары</Link>
        <Link className="dashboard-card" to="/manager/categories">Категории</Link>
        <Link className="dashboard-card" to="/manager/brands">Бренды</Link>
        <Link className="dashboard-card" to="/manager/orders">Заказы</Link>
        <Link className="dashboard-card" to="/manager/reviews">Модерация отзывов</Link>
      </div>
    </section>
  );
}
