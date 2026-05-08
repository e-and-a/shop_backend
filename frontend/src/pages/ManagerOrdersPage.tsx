import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { api, getErrorMessage } from "../api/client";
import { Order, OrderStatus, Page } from "../api/types";
import { ErrorState, LoadingState } from "../components/Status";

const statuses: OrderStatus[] = ["CREATED", "PAID", "PROCESSING", "SHIPPED", "COMPLETED", "CANCELLED"];

export function ManagerOrdersPage() {
  const [orders, setOrders] = useState<Order[]>([]);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(true);

  async function load() {
    setIsLoading(true);
    try {
      const response = await api.get<Page<Order>>("/orders/?page_size=100");
      setOrders(response.data.results);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function updateStatus(order: Order, status: OrderStatus) {
    await api.patch(`/orders/${order.id}/status/`, { status });
    await load();
  }

  async function cancel(order: Order) {
    await api.post(`/orders/${order.id}/cancel/`);
    await load();
  }

  return (
    <section>
      <h1>Управление заказами</h1>
      {error && <ErrorState message={error} />}
      {isLoading && <LoadingState />}
      <div className="table-list">
        {orders.map((order) => (
          <div key={order.id} className="table-row">
            <Link to={`/manager/orders/${order.id}`}>#{order.id}</Link>
            <span>{order.user_email}</span>
            <strong>{order.total_price} ₽</strong>
            <select value={order.status} onChange={(event) => updateStatus(order, event.target.value as OrderStatus)}>
              {statuses.map((status) => <option key={status} value={status}>{status}</option>)}
            </select>
            {["CREATED", "PROCESSING"].includes(order.status) && <button className="danger-button" onClick={() => cancel(order)}>Отменить</button>}
          </div>
        ))}
      </div>
    </section>
  );
}
