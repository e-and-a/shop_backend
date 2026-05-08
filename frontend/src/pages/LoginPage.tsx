import { FormEvent, useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";

import { getErrorMessage } from "../api/client";
import { useAuth } from "../context/AuthContext";

export function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [email, setEmail] = useState("customer@example.com");
  const [password, setPassword] = useState("customer12345");
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setError("");
    setIsSubmitting(true);
    try {
      await login(email, password);
      const target = (location.state as { from?: { pathname?: string } } | null)?.from?.pathname || "/products";
      navigate(target, { replace: true });
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <section className="auth-panel">
      <h1>Вход</h1>
      {error && <div className="alert error">{error}</div>}
      <form onSubmit={handleSubmit} className="form-grid">
        <label>
          Email
          <input value={email} onChange={(event) => setEmail(event.target.value)} type="email" required />
        </label>
        <label>
          Пароль
          <input value={password} onChange={(event) => setPassword(event.target.value)} type="password" required />
        </label>
        <button disabled={isSubmitting}>{isSubmitting ? "Вход..." : "Войти"}</button>
      </form>
      <p>
        Нет аккаунта? <Link to="/register">Зарегистрироваться</Link>
      </p>
    </section>
  );
}
