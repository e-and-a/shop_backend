import { Navigate, Outlet, useLocation } from "react-router-dom";

import { Role } from "../api/types";
import { useAuth } from "../context/AuthContext";

export function ProtectedRoute({ roles }: { roles?: Role[] }) {
  const { user, isLoading } = useAuth();
  const location = useLocation();

  if (isLoading) {
    return <div className="page-status">Загрузка...</div>;
  }

  if (!user) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }

  if (roles && !roles.includes(user.role)) {
    return <Navigate to="/403" replace />;
  }

  return <Outlet />;
}
