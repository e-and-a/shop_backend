import { useEffect, useState } from "react";

import { api, getErrorMessage } from "../api/client";
import { Favorite, Page } from "../api/types";
import { EmptyState, ErrorState, LoadingState } from "../components/Status";

export function FavoritesPage() {
  const [favorites, setFavorites] = useState<Favorite[]>([]);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(true);

  async function load() {
    setIsLoading(true);
    try {
      const response = await api.get<Page<Favorite>>("/favorites/");
      setFavorites(response.data.results);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function removeFavorite(id: number) {
    await api.delete(`/favorites/${id}/`);
    await load();
  }

  return (
    <section>
      <h1>Избранное</h1>
      {error && <ErrorState message={error} />}
      {isLoading && <LoadingState />}
      {!isLoading && favorites.length === 0 && <EmptyState title="Избранных товаров нет" />}
      <div className="table-list">
        {favorites.map((favorite) => (
          <div key={favorite.id} className="table-row">
            <span>{favorite.product.title}</span>
            <strong>{favorite.product.price} ₽</strong>
            <button className="danger-button" onClick={() => removeFavorite(favorite.id)}>Удалить</button>
          </div>
        ))}
      </div>
    </section>
  );
}
