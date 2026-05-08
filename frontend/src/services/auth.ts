import { api } from "../api/client";
import { User } from "../api/types";
import { tokenStorage } from "./tokenStorage";

interface LoginResponse {
  access: string;
  refresh: string;
  user: User;
}

export async function login(email: string, password: string) {
  const response = await api.post<LoginResponse>("/auth/login/", { email, password });
  tokenStorage.setTokens(response.data.access, response.data.refresh);
  return response.data.user;
}

export async function register(payload: {
  email: string;
  password: string;
  password_confirm: string;
  first_name?: string;
  last_name?: string;
  phone?: string;
}) {
  const response = await api.post<User>("/auth/register/", payload);
  return response.data;
}

export async function fetchCurrentUser() {
  const response = await api.get<User>("/auth/me/");
  return response.data;
}

export async function updateProfile(payload: Partial<Pick<User, "username" | "first_name" | "last_name" | "phone">>) {
  const response = await api.patch<User>("/auth/me/", payload);
  return response.data;
}

export async function logout() {
  const refresh = tokenStorage.getRefreshToken();
  try {
    if (refresh) {
      await api.post("/auth/logout/", { refresh });
    }
  } finally {
    tokenStorage.clear();
  }
}
