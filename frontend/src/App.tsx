import { Route, Routes } from "react-router-dom";

import { Layout } from "./components/Layout";
import { ProtectedRoute } from "./components/ProtectedRoute";
import { AdminDashboard } from "./pages/AdminDashboard";
import { CartPage } from "./pages/CartPage";
import { CheckoutPage } from "./pages/CheckoutPage";
import { FavoritesPage } from "./pages/FavoritesPage";
import { ForbiddenPage } from "./pages/ForbiddenPage";
import { HomePage } from "./pages/HomePage";
import { LoginPage } from "./pages/LoginPage";
import { ManagerDashboard } from "./pages/ManagerDashboard";
import { ManagerOrdersPage } from "./pages/ManagerOrdersPage";
import { ManagerProductsPage } from "./pages/ManagerProductsPage";
import { ManagerReviewsPage } from "./pages/ManagerReviewsPage";
import { NotFoundPage } from "./pages/NotFoundPage";
import { OrderDetailPage } from "./pages/OrderDetailPage";
import { OrdersPage } from "./pages/OrdersPage";
import { ProductDetailPage } from "./pages/ProductDetailPage";
import { ProductListPage } from "./pages/ProductListPage";
import { ProfilePage } from "./pages/ProfilePage";
import { RegisterPage } from "./pages/RegisterPage";

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<HomePage />} />
        <Route path="products" element={<ProductListPage />} />
        <Route path="products/:id" element={<ProductDetailPage />} />
        <Route path="login" element={<LoginPage />} />
        <Route path="register" element={<RegisterPage />} />
        <Route path="403" element={<ForbiddenPage />} />

        <Route element={<ProtectedRoute roles={["CUSTOMER", "MANAGER", "ADMIN"]} />}>
          <Route path="profile" element={<ProfilePage />} />
        </Route>

        <Route element={<ProtectedRoute roles={["CUSTOMER"]} />}>
          <Route path="favorites" element={<FavoritesPage />} />
          <Route path="cart" element={<CartPage />} />
          <Route path="checkout" element={<CheckoutPage />} />
          <Route path="orders" element={<OrdersPage />} />
          <Route path="orders/:id" element={<OrderDetailPage />} />
        </Route>

        <Route element={<ProtectedRoute roles={["MANAGER", "ADMIN"]} />}>
          <Route path="manager" element={<ManagerDashboard />} />
          <Route path="manager/products" element={<ManagerProductsPage />} />
          <Route path="manager/categories" element={<ManagerProductsPage mode="categories" />} />
          <Route path="manager/brands" element={<ManagerProductsPage mode="brands" />} />
          <Route path="manager/orders" element={<ManagerOrdersPage />} />
          <Route path="manager/orders/:id" element={<OrderDetailPage />} />
          <Route path="manager/reviews" element={<ManagerReviewsPage />} />
        </Route>

        <Route element={<ProtectedRoute roles={["ADMIN"]} />}>
          <Route path="admin" element={<AdminDashboard />} />
        </Route>

        <Route path="*" element={<NotFoundPage />} />
      </Route>
    </Routes>
  );
}
