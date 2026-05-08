import { useEffect, useState } from "react";

import { api, getErrorMessage } from "../api/client";
import { Page, Product, Review } from "../api/types";
import { ErrorState, LoadingState } from "../components/Status";

interface ModerationItem extends Review {
  productId: number;
}

export function ManagerReviewsPage() {
  const [reviews, setReviews] = useState<ModerationItem[]>([]);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(true);

  async function load() {
    setIsLoading(true);
    try {
      const productsResponse = await api.get<Page<Product>>("/products/?page_size=100");
      const reviewResponses = await Promise.all(
        productsResponse.data.results.map((product) =>
          api.get<Page<Review>>(`/products/${product.id}/reviews/`).then((response) =>
            response.data.results.map((review) => ({ ...review, productId: product.id })),
          ),
        ),
      );
      setReviews(reviewResponses.flat());
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function moderate(review: ModerationItem, is_moderated: boolean) {
    await api.patch(`/reviews/${review.id}/`, { is_moderated });
    await load();
  }

  async function remove(review: ModerationItem) {
    await api.delete(`/reviews/${review.id}/`);
    await load();
  }

  return (
    <section>
      <h1>Модерация отзывов</h1>
      {error && <ErrorState message={error} />}
      {isLoading && <LoadingState />}
      <div className="table-list">
        {reviews.map((review) => (
          <div key={review.id} className="table-row review-row">
            <span>{review.product_title}</span>
            <strong>{review.rating}/5</strong>
            <span>{review.text}</span>
            <span>{review.is_moderated ? "moderated" : "pending"}</span>
            <button onClick={() => moderate(review, !review.is_moderated)}>
              {review.is_moderated ? "Скрыть" : "Одобрить"}
            </button>
            <button className="danger-button" onClick={() => remove(review)}>Удалить</button>
          </div>
        ))}
      </div>
    </section>
  );
}
