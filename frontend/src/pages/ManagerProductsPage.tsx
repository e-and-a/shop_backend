import { FormEvent, useEffect, useState } from "react";

import { api, getErrorMessage } from "../api/client";
import { Brand, Category, Page, Product } from "../api/types";
import { ErrorState, LoadingState } from "../components/Status";

type Mode = "products" | "categories" | "brands";

export function ManagerProductsPage({ mode = "products" }: { mode?: Mode }) {
  if (mode === "categories") return <CategoryManagement />;
  if (mode === "brands") return <BrandManagement />;
  return <ProductManagement />;
}

function ProductManagement() {
  const [products, setProducts] = useState<Product[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [brands, setBrands] = useState<Brand[]>([]);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [form, setForm] = useState({
    category: "",
    brand: "",
    title: "",
    slug: "",
    description: "",
    price: "",
    old_price: "",
    stock: "0",
    sku: "",
    warranty_months: "12",
    characteristics: "{}",
    is_active: true,
  });

  async function load() {
    setIsLoading(true);
    const [productsResponse, categoriesResponse, brandsResponse] = await Promise.all([
      api.get<Page<Product>>("/products/?page_size=100"),
      api.get<Page<Category>>("/categories/?page_size=100"),
      api.get<Page<Brand>>("/brands/?page_size=100"),
    ]);
    setProducts(productsResponse.data.results);
    setCategories(categoriesResponse.data.results);
    setBrands(brandsResponse.data.results);
    setIsLoading(false);
  }

  useEffect(() => {
    load().catch((err) => {
      setError(getErrorMessage(err));
      setIsLoading(false);
    });
  }, []);

  function startEdit(product: Product) {
    setEditingId(product.id);
    setForm({
      category: String(product.category),
      brand: String(product.brand),
      title: product.title,
      slug: product.slug,
      description: product.description,
      price: product.price,
      old_price: product.old_price || "",
      stock: String(product.stock),
      sku: product.sku,
      warranty_months: String(product.warranty_months),
      characteristics: JSON.stringify(product.characteristics, null, 2),
      is_active: product.is_active,
    });
  }

  async function submit(event: FormEvent) {
    event.preventDefault();
    setError("");
    try {
      const payload = {
        ...form,
        category: Number(form.category),
        brand: Number(form.brand),
        price: form.price,
        old_price: form.old_price || null,
        stock: Number(form.stock),
        warranty_months: Number(form.warranty_months),
        characteristics: JSON.parse(form.characteristics || "{}"),
      };
      if (editingId) {
        await api.patch(`/products/${editingId}/`, payload);
      } else {
        await api.post("/products/", payload);
      }
      setEditingId(null);
      setForm({ ...form, title: "", slug: "", description: "", price: "", sku: "", characteristics: "{}" });
      await load();
    } catch (err) {
      setError(getErrorMessage(err));
    }
  }

  async function softDelete(product: Product) {
    await api.delete(`/products/${product.id}/`);
    await load();
  }

  return (
    <section>
      <h1>Управление товарами</h1>
      {error && <ErrorState message={error} />}
      <form className="manager-form" onSubmit={submit}>
        <select value={form.category} onChange={(event) => setForm({ ...form, category: event.target.value })} required>
          <option value="">Категория</option>
          {categories.map((category) => <option key={category.id} value={category.id}>{category.name}</option>)}
        </select>
        <select value={form.brand} onChange={(event) => setForm({ ...form, brand: event.target.value })} required>
          <option value="">Бренд</option>
          {brands.map((brand) => <option key={brand.id} value={brand.id}>{brand.name}</option>)}
        </select>
        <input placeholder="Название" value={form.title} onChange={(event) => setForm({ ...form, title: event.target.value })} required />
        <input placeholder="Slug" value={form.slug} onChange={(event) => setForm({ ...form, slug: event.target.value })} required />
        <input placeholder="SKU" value={form.sku} onChange={(event) => setForm({ ...form, sku: event.target.value })} required />
        <input placeholder="Цена" value={form.price} onChange={(event) => setForm({ ...form, price: event.target.value })} required />
        <input placeholder="Старая цена" value={form.old_price} onChange={(event) => setForm({ ...form, old_price: event.target.value })} />
        <input placeholder="Остаток" value={form.stock} onChange={(event) => setForm({ ...form, stock: event.target.value })} required />
        <input placeholder="Гарантия, мес." value={form.warranty_months} onChange={(event) => setForm({ ...form, warranty_months: event.target.value })} />
        <textarea placeholder="Описание" value={form.description} onChange={(event) => setForm({ ...form, description: event.target.value })} required />
        <textarea placeholder="JSON характеристики" value={form.characteristics} onChange={(event) => setForm({ ...form, characteristics: event.target.value })} />
        <label className="checkbox-line">
          <input type="checkbox" checked={form.is_active} onChange={(event) => setForm({ ...form, is_active: event.target.checked })} />
          Активен
        </label>
        <button>{editingId ? "Сохранить" : "Создать"}</button>
      </form>
      {isLoading ? <LoadingState /> : (
        <div className="table-list">
          {products.map((product) => (
            <div key={product.id} className="table-row">
              <span>{product.title}</span>
              <span>{product.stock} шт.</span>
              <span>{product.is_active ? "active" : "inactive"}</span>
              <button onClick={() => startEdit(product)}>Редактировать</button>
              <button className="danger-button" onClick={() => softDelete(product)}>Soft delete</button>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}

function CategoryManagement() {
  const [items, setItems] = useState<Category[]>([]);
  const [form, setForm] = useState({ name: "", slug: "", description: "" });
  const [error, setError] = useState("");

  async function load() {
    const response = await api.get<Page<Category>>("/categories/?page_size=100");
    setItems(response.data.results);
  }

  useEffect(() => {
    load().catch((err) => setError(getErrorMessage(err)));
  }, []);

  async function submit(event: FormEvent) {
    event.preventDefault();
    await api.post("/categories/", { ...form, is_active: true });
    setForm({ name: "", slug: "", description: "" });
    await load();
  }

  return (
    <EntityManagement title="Категории" error={error} items={items} form={form} setForm={setForm} submit={submit} />
  );
}

function BrandManagement() {
  const [items, setItems] = useState<Brand[]>([]);
  const [form, setForm] = useState({ name: "", slug: "", description: "", country: "" });
  const [error, setError] = useState("");

  async function load() {
    const response = await api.get<Page<Brand>>("/brands/?page_size=100");
    setItems(response.data.results);
  }

  useEffect(() => {
    load().catch((err) => setError(getErrorMessage(err)));
  }, []);

  async function submit(event: FormEvent) {
    event.preventDefault();
    await api.post("/brands/", { ...form, is_active: true });
    setForm({ name: "", slug: "", description: "", country: "" });
    await load();
  }

  return <EntityManagement title="Бренды" error={error} items={items} form={form} setForm={setForm} submit={submit} />;
}

function EntityManagement<T extends { id: number; name: string; slug: string; description: string }>({
  title,
  error,
  items,
  form,
  setForm,
  submit,
}: {
  title: string;
  error: string;
  items: T[];
  form: Record<string, string>;
  setForm: (form: any) => void;
  submit: (event: FormEvent) => void;
}) {
  return (
    <section>
      <h1>{title}</h1>
      {error && <ErrorState message={error} />}
      <form className="manager-form compact" onSubmit={submit}>
        <input placeholder="Название" value={form.name} onChange={(event) => setForm({ ...form, name: event.target.value })} required />
        <input placeholder="Slug" value={form.slug} onChange={(event) => setForm({ ...form, slug: event.target.value })} required />
        {"country" in form && <input placeholder="Страна" value={form.country} onChange={(event) => setForm({ ...form, country: event.target.value })} />}
        <input placeholder="Описание" value={form.description} onChange={(event) => setForm({ ...form, description: event.target.value })} />
        <button>Создать</button>
      </form>
      <div className="table-list">
        {items.map((item) => (
          <div key={item.id} className="table-row">
            <span>{item.name}</span>
            <span>{item.slug}</span>
            <span>{item.description}</span>
          </div>
        ))}
      </div>
    </section>
  );
}
