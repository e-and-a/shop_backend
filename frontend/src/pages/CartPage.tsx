import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { api, getErrorMessage } from "../api/client";
import { Cart } from "../api/types";
import { EmptyState, ErrorState, LoadingState } from "../components/Status";

export function CartPage() {
  const [cart, setCart] = useState<Cart | null>(null);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(true);

  async function load() {
    setIsLoading(true);
    try {
      const response = await api.get<Cart>("/cart/");
      setCart(response.data);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function updateQuantity(id: number, quantity: number) {
    if (quantity < 1) return;
    await api.patch(`/cart/items/${id}/`, { quantity });
    await load();
  }

  async function removeItem(id: number) {
    await api.delete(`/cart/items/${id}/`);
    await load();
  }

  async function clearCart() {
    await api.delete("/cart/clear/");
    await load();
  }

  return (
    <section>
      <div className="page-heading row-heading">
        <h1>Корзина</h1>
        {cart && cart.items.length > 0 && <button className="danger-button" onClick={clearCart}>Очистить</button>}
      </div>
      {error && <ErrorState message={error} />}
      {isLoading && <LoadingState />}
      {!isLoading && cart?.items.length === 0 && <EmptyState title="Корзина пуста" text="Добавьте товары из каталога." />}
      <div className="table-list">
        {cart?.items.map((item) => (
          <div key={item.id} className="table-row cart-row">
            <span>{item.product.title}</span>
            <strong>{item.subtotal} ₽</strong>
            <div className="stepper">
              <button onClick={() => updateQuantity(item.id, item.quantity - 1)}>-</button>
              <span>{item.quantity}</span>
              <button onClick={() => updateQuantity(item.id, item.quantity + 1)}>+</button>
            </div>
            <button className="danger-button" onClick={() => removeItem(item.id)}>Удалить</button>
          </div>
        ))}
      </div>
      {cart && cart.items.length > 0 && (
        <div className="checkout-summary">
          <strong>Итого: {cart.total_price} ₽</strong>
          <Link className="primary-link" to="/checkout">Оформить заказ</Link>
        </div>
      )}
    </section>
  );
}
