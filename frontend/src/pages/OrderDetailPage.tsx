import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";

import { api, getErrorMessage } from "../api/client";
import { Order } from "../api/types";
import { ErrorState, LoadingState } from "../components/Status";

export function OrderDetailPage() {
  const { id } = useParams();
  const [order, setOrder] = useState<Order | null>(null);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(true);

  async function load() {
    if (!id) return;
    setIsLoading(true);
    try {
      const response = await api.get<Order>(`/orders/${id}/`);
      setOrder(response.data);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, [id]);

  async function cancelOrder() {
    if (!order) return;
    await api.post(`/orders/${order.id}/cancel/`);
    await load();
  }

  if (isLoading) return <LoadingState />;
  if (error) return <ErrorState message={error} />;
  if (!order) return null;

  return (
    <section>
      <div className="page-heading row-heading">
        <h1>Заказ #{order.id}</h1>
        {["CREATED", "PROCESSING"].includes(order.status) && <button className="danger-button" onClick={cancelOrder}>Отменить</button>}
      </div>
      <div className="panel">
        <p>Статус: <strong>{order.status}</strong></p>
        <p>Адрес: {order.delivery_address}</p>
        <p>Телефон: {order.phone}</p>
        <p>Комментарий: {order.comment || "нет"}</p>
      </div>
      <div className="table-list">
        {order.items.map((item) => (
          <div key={item.id} className="table-row">
            <span>{item.product_title_snapshot}</span>
            <span>{item.quantity} шт.</span>
            <strong>{item.subtotal} ₽</strong>
          </div>
        ))}
      </div>
      <div className="checkout-summary">
        <strong>Итого: {order.total_price} ₽</strong>
      </div>
    </section>
  );
}
