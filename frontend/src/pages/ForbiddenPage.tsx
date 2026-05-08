import { Link } from "react-router-dom";

export function ForbiddenPage() {
  return (
    <section className="page-status">
      <h1>403</h1>
      <p>Недостаточно прав для просмотра страницы.</p>
      <Link to="/products">Вернуться в каталог</Link>
    </section>
  );
}
