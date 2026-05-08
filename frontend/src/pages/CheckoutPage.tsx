import { FormEvent, useState } from "react";
import { useNavigate } from "react-router-dom";

import { api, getErrorMessage } from "../api/client";

export function CheckoutPage() {
  const navigate = useNavigate();
  const [form, setForm] = useState({ delivery_address: "", phone: "", comment: "" });
  const [error, setError] = useState("");

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setError("");
    try {
      const response = await api.post("/orders/create-from-cart/", form);
      navigate(`/orders/${response.data.id}`);
    } catch (err) {
      setError(getErrorMessage(err));
    }
  }

  return (
    <section className="panel narrow">
      <h1>Оформление заказа</h1>
      {error && <div className="alert error">{error}</div>}
      <form onSubmit={handleSubmit} className="form-grid">
        <label>
          Адрес доставки
          <textarea value={form.delivery_address} onChange={(event) => setForm({ ...form, delivery_address: event.target.value })} required />
        </label>
        <label>
          Телефон
          <input value={form.phone} onChange={(event) => setForm({ ...form, phone: event.target.value })} required />
        </label>
        <label>
          Комментарий
          <textarea value={form.comment} onChange={(event) => setForm({ ...form, comment: event.target.value })} />
        </label>
        <button>Создать заказ</button>
      </form>
    </section>
  );
}
