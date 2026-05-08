import { FormEvent, useState } from "react";

import { getErrorMessage } from "../api/client";
import { useAuth } from "../context/AuthContext";
import { updateProfile } from "../services/auth";

export function ProfilePage() {
  const { user, refreshUser } = useAuth();
  const [form, setForm] = useState({
    username: user?.username || "",
    first_name: user?.first_name || "",
    last_name: user?.last_name || "",
    phone: user?.phone || "",
  });
  const [message, setMessage] = useState("");

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setMessage("");
    try {
      await updateProfile(form);
      await refreshUser();
      setMessage("Профиль обновлён");
    } catch (err) {
      setMessage(getErrorMessage(err));
    }
  }

  if (!user) return null;

  return (
    <section className="panel narrow">
      <h1>Профиль</h1>
      <p>{user.email} · {user.role}</p>
      {message && <div className="alert">{message}</div>}
      <form onSubmit={handleSubmit} className="form-grid">
        <label>
          Username
          <input value={form.username} onChange={(event) => setForm({ ...form, username: event.target.value })} />
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
        <button>Сохранить</button>
      </form>
    </section>
  );
}
