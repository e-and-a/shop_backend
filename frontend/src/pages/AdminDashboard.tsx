import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { api, getErrorMessage } from "../api/client";
import { AdminStats } from "../api/types";
import { ErrorState, LoadingState } from "../components/Status";

export function AdminDashboard() {
  const [stats, setStats] = useState<AdminStats | null>(null);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    api
      .get<AdminStats>("/admin/stats/")
      .then((response) => setStats(response.data))
      .catch((err) => setError(getErrorMessage(err)))
      .finally(() => setIsLoading(false));
  }, []);

  return (
    <section>
      <div className="page-heading row-heading">
        <h1>Админ-панель</h1>
        <Link className="primary-link" to="/manager">Функции менеджера</Link>
      </div>
      {error && <ErrorState message={error} />}
      {isLoading && <LoadingState />}
      {stats && (
        <>
          <div className="stats-grid">
            <Stat label="Пользователи" value={stats.users_count} />
            <Stat label="Покупатели" value={stats.customers_count} />
            <Stat label="Менеджеры" value={stats.managers_count} />
            <Stat label="Товары" value={stats.products_count} />
            <Stat label="Активные товары" value={stats.active_products_count} />
            <Stat label="Заказы" value={stats.orders_count} />
            <Stat label="Завершённые продажи" value={`${stats.completed_orders_total} ₽`} />
          </div>
          <div className="dashboard-grid">
            <div className="panel">
              <h2>Заказы по статусам</h2>
              {Object.entries(stats.orders_by_status).map(([status, count]) => (
                <p key={status}>{status}: {count}</p>
              ))}
            </div>
            <div className="panel">
              <h2>Популярные товары</h2>
              {stats.top_products.map((item, index) => (
                <p key={index}>{String(item.product_title_snapshot)} · {String(item.quantity_sold)} шт.</p>
              ))}
            </div>
            <div className="panel">
              <h2>Низкий остаток</h2>
              {stats.low_stock_products.map((item, index) => (
                <p key={index}>{String(item.title)} · {String(item.stock)} шт.</p>
              ))}
            </div>
            <div className="panel">
              <h2>Users overview</h2>
              <p>Отдельный backend endpoint для списка пользователей не реализован, поэтому frontend не делает запрос к несуществующему API.</p>
            </div>
          </div>
        </>
      )}
    </section>
  );
}

function Stat({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="stat-card">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}
