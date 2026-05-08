export type Role = "ADMIN" | "MANAGER" | "CUSTOMER";

export interface Page<T> {
  page: number;
  page_size: number;
  count: number;
  total_pages: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface User {
  id: number;
  email: string;
  username: string | null;
  role: Role;
  first_name: string;
  last_name: string;
  phone: string;
  is_active: boolean;
  is_staff: boolean;
  date_joined: string;
}

export interface Category {
  id: number;
  name: string;
  slug: string;
  description: string;
  is_active: boolean;
}

export interface Brand {
  id: number;
  name: string;
  slug: string;
  country: string;
  description: string;
  is_active: boolean;
}

export interface Product {
  id: number;
  category: number;
  category_name: string;
  brand: number;
  brand_name: string;
  title: string;
  slug: string;
  description: string;
  price: string;
  old_price: string | null;
  stock: number;
  sku: string;
  image: string | null;
  characteristics: Record<string, unknown>;
  warranty_months: number;
  is_active: boolean;
  average_rating: number | null;
  reviews_count: number;
  created_at: string;
  updated_at: string;
}

export interface Favorite {
  id: number;
  product: Product;
  created_at: string;
}

export interface CartItem {
  id: number;
  product: Product;
  quantity: number;
  subtotal: string;
}

export interface Cart {
  id: number;
  items: CartItem[];
  items_count: number;
  total_price: string;
}

export type OrderStatus = "CREATED" | "PAID" | "PROCESSING" | "SHIPPED" | "COMPLETED" | "CANCELLED";

export interface OrderItem {
  id: number;
  product: number;
  product_title_snapshot: string;
  product_sku_snapshot: string;
  price_snapshot: string;
  quantity: number;
  subtotal: string;
}

export interface Order {
  id: number;
  user: number;
  user_email: string;
  status: OrderStatus;
  total_price: string;
  delivery_address: string;
  phone: string;
  comment: string;
  items: OrderItem[];
  created_at: string;
  updated_at: string;
}

export interface Review {
  id: number;
  product: number;
  product_title: string;
  user: number;
  user_email: string;
  rating: number;
  text: string;
  is_moderated: boolean;
  created_at: string;
}

export interface AdminStats {
  users_count: number;
  customers_count: number;
  managers_count: number;
  products_count: number;
  active_products_count: number;
  orders_count: number;
  orders_by_status: Record<string, number>;
  completed_orders_total: string;
  top_products: Array<Record<string, string | number>>;
  low_stock_products: Array<Record<string, string | number>>;
}
