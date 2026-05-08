import { NavLink, Outlet, useNavigate } from "react-router-dom";

import { useAuth } from "../context/AuthContext";

export function Layout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  async function handleLogout() {
    await logout();
    navigate("/");
  }

  return (
    <div className="app-shell">
      <header className="site-header">
        <NavLink to="/" className="brand">
          Tech Store
        </NavLink>
        <nav className="main-nav">
          <NavLink to="/products">Каталог</NavLink>
          {user?.role === "CUSTOMER" && (
            <>
              <NavLink to="/favorites">Избранное</NavLink>
              <NavLink to="/cart">Корзина</NavLink>
              <NavLink to="/orders">Заказы</NavLink>
            </>
          )}
          {(user?.role === "MANAGER" || user?.role === "ADMIN") && <NavLink to="/manager">Менеджер</NavLink>}
          {user?.role === "ADMIN" && <NavLink to="/admin">Админ</NavLink>}
        </nav>
        <div className="user-menu">
          {user ? (
            <>
              <NavLink to="/profile">{user.email}</NavLink>
              <button className="ghost-button" onClick={handleLogout}>
                Выйти
              </button>
            </>
          ) : (
            <>
              <NavLink to="/login">Войти</NavLink>
              <NavLink to="/register">Регистрация</NavLink>
            </>
          )}
        </div>
      </header>
      <main className="content">
        <Outlet />
      </main>
    </div>
  );
}
