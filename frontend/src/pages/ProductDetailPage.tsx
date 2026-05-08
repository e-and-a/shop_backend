import { FormEvent, useEffect, useState } from "react";
import { useParams } from "react-router-dom";

import { api, getErrorMessage } from "../api/client";
import { Page, Product, Review } from "../api/types";
import { ErrorState, LoadingState } from "../components/Status";
import { useAuth } from "../context/AuthContext";

export function ProductDetailPage() {
  const { id } = useParams();
  const { user } = useAuth();
  const [product, setProduct] = useState<Product | null>(null);
  const [reviews, setReviews] = useState<Review[]>([]);
  const [reviewForm, setReviewForm] = useState({ rating: 5, text: "" });
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(true);

  async function load() {
    if (!id) return;
    setIsLoading(true);
    try {
      const [productResponse, reviewResponse] = await Promise.all([
        api.get<Product>(`/products/${id}/`),
        api.get<Page<Review>>(`/products/${id}/reviews/`),
      ]);
      setProduct(productResponse.data);
      setReviews(reviewResponse.data.results);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, [id]);

  async function addToCart() {
    if (!product) return;
    await api.post("/cart/items/", { product_id: product.id, quantity: 1 });
    alert("Добавлено в корзину");
  }

  async function addToFavorites() {
    if (!product) return;
    await api.post("/favorites/", { product_id: product.id });
    alert("Добавлено в избранное");
  }

  async function submitReview(event: FormEvent) {
    event.preventDefault();
    if (!id) return;
    try {
      await api.post(`/products/${id}/reviews/`, reviewForm);
      setReviewForm({ rating: 5, text: "" });
      await load();
    } catch (err) {
      alert(getErrorMessage(err));
    }
  }

  if (isLoading) return <LoadingState />;
  if (error) return <ErrorState message={error} />;
  if (!product) return null;

  return (
    <section className="detail-grid">
      <div className="detail-media">{product.image ? <img src={product.image} alt={product.title} /> : product.brand_name}</div>
      <div className="detail-main">
        <h1>{product.title}</h1>
        <p>{product.description}</p>
        <div className="price-line">{product.price} ₽</div>
        <p>{product.category_name} · {product.brand_name} · SKU {product.sku}</p>
        <p>Рейтинг: {product.average_rating ?? "нет"} · отзывов: {product.reviews_count}</p>
        <div className="button-row">
          {user?.role === "CUSTOMER" && <button onClick={addToCart} disabled={product.stock <= 0}>В корзину</button>}
          {user?.role === "CUSTOMER" && <button className="secondary-button" onClick={addToFavorites}>В избранное</button>}
        </div>
        <h2>Характеристики</h2>
        <dl className="spec-list">
          {Object.entries(product.characteristics || {}).map(([key, value]) => (
            <div key={key}>
              <dt>{key}</dt>
              <dd>{String(value)}</dd>
            </div>
          ))}
        </dl>
      </div>
      <section className="wide-panel">
        <h2>Отзывы</h2>
        {reviews.length === 0 && <p>Отзывов пока нет.</p>}
        {reviews.map((review) => (
          <article key={review.id} className="review-item">
            <strong>{review.user_email}</strong>
            <span>{review.rating}/5</span>
            <p>{review.text}</p>
          </article>
        ))}
        {user?.role === "CUSTOMER" && (
          <form onSubmit={submitReview} className="form-grid narrow-form">
            <h3>Добавить отзыв</h3>
            <label>
              Оценка
              <select value={reviewForm.rating} onChange={(event) => setReviewForm({ ...reviewForm, rating: Number(event.target.value) })}>
                {[1, 2, 3, 4, 5].map((rating) => <option key={rating} value={rating}>{rating}</option>)}
              </select>
            </label>
            <label>
              Текст
              <textarea value={reviewForm.text} onChange={(event) => setReviewForm({ ...reviewForm, text: event.target.value })} required />
            </label>
            <button>Отправить</button>
          </form>
        )}
      </section>
    </section>
  );
}
