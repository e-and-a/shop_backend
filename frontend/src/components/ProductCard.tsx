import { Link } from "react-router-dom";

import { Product } from "../api/types";

interface ProductCardProps {
  product: Product;
  onAddToCart?: (product: Product) => void;
  onAddToFavorites?: (product: Product) => void;
}

export function ProductCard({ product, onAddToCart, onAddToFavorites }: ProductCardProps) {
  return (
    <article className="product-card">
      <Link to={`/products/${product.id}`} className="product-image">
        {product.image ? <img src={product.image} alt={product.title} /> : <span>{product.brand_name}</span>}
      </Link>
      <div className="product-card-body">
        <Link to={`/products/${product.id}`} className="product-title">
          {product.title}
        </Link>
        <p>{product.category_name} · {product.brand_name}</p>
        <div className="product-meta">
          <strong>{product.price} ₽</strong>
          <span>{product.stock > 0 ? `В наличии: ${product.stock}` : "Нет в наличии"}</span>
        </div>
        <div className="rating-line">
          Рейтинг: {product.average_rating ?? "нет"} · отзывов: {product.reviews_count}
        </div>
        <div className="button-row">
          {onAddToCart && (
            <button onClick={() => onAddToCart(product)} disabled={product.stock <= 0}>
              В корзину
            </button>
          )}
          {onAddToFavorites && <button className="secondary-button" onClick={() => onAddToFavorites(product)}>В избранное</button>}
        </div>
      </div>
    </article>
  );
}
