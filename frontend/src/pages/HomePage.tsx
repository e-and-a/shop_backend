import { Link } from "react-router-dom";

export function HomePage() {
  return (
    <section className="hero">
      <div>
        <h1>Tech Store</h1>
        <p>Интернет-магазин смартфонов, ноутбуков, комплектующих, периферии и бытовой электроники.</p>
        <Link className="primary-link" to="/products">
          Перейти в каталог
        </Link>
      </div>
    </section>
  );
}
