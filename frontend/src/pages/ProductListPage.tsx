import { FormEvent, useEffect, useState } from "react";

import { api, getErrorMessage } from "../api/client";
import { Brand, Category, Page, Product } from "../api/types";
import { Pagination } from "../components/Pagination";
import { ProductCard } from "../components/ProductCard";
import { EmptyState, ErrorState, LoadingState } from "../components/Status";
import { useAuth } from "../context/AuthContext";

interface Filters {
  category: string;
  brand: string;
  min_price: string;
  max_price: string;
  in_stock: string;
  search: string;
  ordering: string;
}

const initialFilters: Filters = {
  category: "",
  brand: "",
  min_price: "",
  max_price: "",
  in_stock: "",
  search: "",
  ordering: "-created_at",
};

export function ProductListPage() {
  const { user } = useAuth();
  const [products, setProducts] = useState<Page<Product> | null>(null);
  const [categories, setCategories] = useState<Category[]>([]);
  const [brands, setBrands] = useState<Brand[]>([]);
  const [filters, setFilters] = useState(initialFilters);
  const [page, setPage] = useState(1);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(true);

  async function loadProducts(currentPage = page, currentFilters = filters) {
    setIsLoading(true);
    setError("");
    try {
      const response = await api.get<Page<Product>>("/products/", {
        params: { ...currentFilters, page: currentPage },
      });
      setProducts(response.data);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    Promise.all([api.get<Page<Category>>("/categories/"), api.get<Page<Brand>>("/brands/")]).then(([cat, br]) => {
      setCategories(cat.data.results);
      setBrands(br.data.results);
    });
  }, []);

  useEffect(() => {
    loadProducts(page);
  }, [page]);

  function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setPage(1);
    loadProducts(1, filters);
  }

  async function addToCart(product: Product) {
    try {
      await api.post("/cart/items/", { product_id: product.id, quantity: 1 });
      alert("Товар добавлен в корзину");
    } catch (err) {
      alert(getErrorMessage(err));
    }
  }

  async function addToFavorites(product: Product) {
    try {
      await api.post("/favorites/", { product_id: product.id });
      alert("Товар добавлен в избранное");
    } catch (err) {
      alert(getErrorMessage(err));
    }
  }

  return (
    <section>
      <div className="page-heading">
        <h1>Каталог техники</h1>
        <p>Фильтры, поиск, сортировка и пагинация работают через backend API.</p>
      </div>

      <form className="filters" onSubmit={handleSubmit}>
        <input placeholder="Поиск" value={filters.search} onChange={(event) => setFilters({ ...filters, search: event.target.value })} />
        <select value={filters.category} onChange={(event) => setFilters({ ...filters, category: event.target.value })}>
          <option value="">Все категории</option>
          {categories.map((category) => <option key={category.id} value={category.id}>{category.name}</option>)}
        </select>
        <select value={filters.brand} onChange={(event) => setFilters({ ...filters, brand: event.target.value })}>
          <option value="">Все бренды</option>
          {brands.map((brand) => <option key={brand.id} value={brand.id}>{brand.name}</option>)}
        </select>
        <input placeholder="Цена от" value={filters.min_price} onChange={(event) => setFilters({ ...filters, min_price: event.target.value })} />
        <input placeholder="Цена до" value={filters.max_price} onChange={(event) => setFilters({ ...filters, max_price: event.target.value })} />
        <select value={filters.in_stock} onChange={(event) => setFilters({ ...filters, in_stock: event.target.value })}>
          <option value="">Любое наличие</option>
          <option value="true">В наличии</option>
          <option value="false">Нет в наличии</option>
        </select>
        <select value={filters.ordering} onChange={(event) => setFilters({ ...filters, ordering: event.target.value })}>
          <option value="-created_at">Сначала новые</option>
          <option value="price">Цена по возрастанию</option>
          <option value="-price">Цена по убыванию</option>
          <option value="-rating">Рейтинг</option>
          <option value="-stock">Остаток</option>
        </select>
        <button>Применить</button>
      </form>

      {error && <ErrorState message={error} />}
      {isLoading && <LoadingState />}
      {!isLoading && products?.results.length === 0 && <EmptyState title="Товары не найдены" />}
      <div className="product-grid">
        {products?.results.map((product) => (
          <ProductCard
            key={product.id}
            product={product}
            onAddToCart={user?.role === "CUSTOMER" ? addToCart : undefined}
            onAddToFavorites={user?.role === "CUSTOMER" ? addToFavorites : undefined}
          />
        ))}
      </div>
      {products && <Pagination page={products.page} totalPages={products.total_pages} onChange={setPage} />}
    </section>
  );
}
