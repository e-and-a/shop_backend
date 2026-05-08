import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { api, getErrorMessage } from "../api/client";
import { Order, Page } from "../api/types";
import { EmptyState, ErrorState, LoadingState } from "../components/Status";

export function OrdersPage() {
  const [orders, setOrders] = useState<Order[]>([]);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    api
      .get<Page<Order>>("/orders/")
      .then((response) => setOrders(response.data.results))
      .catch((err) => setError(getErrorMessage(err)))
      .finally(() => setIsLoading(false));
  }, []);

  return (
    <section>
      <h1>Мои заказы</h1>
      {error && <ErrorState message={error} />}
      {isLoading && <LoadingState />}
      {!isLoading && orders.length === 0 && <EmptyState title="Заказов пока нет" />}
      <div className="table-list">
        {orders.map((order) => (
          <Link key={order.id} to={`/orders/${order.id}`} className="table-row">
            <span>Заказ #{order.id}</span>
            <span>{order.status}</span>
            <strong>{order.total_price} ₽</strong>
          </Link>
        ))}
      </div>
    </section>
  );
}
