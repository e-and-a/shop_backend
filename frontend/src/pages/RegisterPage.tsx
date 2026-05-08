import { FormEvent, useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { getErrorMessage } from "../api/client";
import { useAuth } from "../context/AuthContext";

export function RegisterPage() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({
    email: "",
    password: "",
    password_confirm: "",
    first_name: "",
    last_name: "",
    phone: "",
  });
  const [error, setError] = useState("");

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setError("");
    try {
      await register(form);
      navigate("/login");
    } catch (err) {
      setError(getErrorMessage(err));
    }
  }

  return (
    <section className="auth-panel">
      <h1>Регистрация</h1>
      {error && <div className="alert error">{error}</div>}
      <form onSubmit={handleSubmit} className="form-grid">
        <label>
          Email
          <input value={form.email} onChange={(event) => setForm({ ...form, email: event.target.value })} type="email" required />
        </label>
        <label>
          Имя
          <input value={form.first_name} onChange={(event) => setForm({ ...form, first_name: event.target.value })} />
        </label>
        <label>
          Фамилия
          <input value={form.last_name} onChange={(event) => setForm({ ...form, last_name: event.target.value })} />
        </label>
        <label>
          Телефон
          <input value={form.phone} onChange={(event) => setForm({ ...form, phone: event.target.value })} />
        </label>
        <label>
          Пароль
          <input value={form.password} onChange={(event) => setForm({ ...form, password: event.target.value })} type="password" required />
        </label>
        <label>
          Повтор пароля
          <input
            value={form.password_confirm}
            onChange={(event) => setForm({ ...form, password_confirm: event.target.value })}
            type="password"
            required
          />
        </label>
        <button>Создать аккаунт</button>
      </form>
      <p>
        Уже есть аккаунт? <Link to="/login">Войти</Link>
      </p>
    </section>
  );
}
