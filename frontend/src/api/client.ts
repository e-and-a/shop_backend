import axios, { AxiosError, InternalAxiosRequestConfig } from "axios";

import { tokenStorage } from "../services/tokenStorage";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000/api/v1";

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

let refreshPromise: Promise<string> | null = null;

api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = tokenStorage.getAccessToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as (InternalAxiosRequestConfig & { _retry?: boolean }) | undefined;
    const refresh = tokenStorage.getRefreshToken();

    if (error.response?.status !== 401 || !originalRequest || originalRequest._retry || !refresh) {
      return Promise.reject(error);
    }

    originalRequest._retry = true;
    try {
      refreshPromise =
        refreshPromise ||
        axios
          .post(`${API_BASE_URL}/auth/token/refresh/`, { refresh })
          .then((response) => {
            tokenStorage.setTokens(response.data.access, response.data.refresh);
            return response.data.access as string;
          })
          .finally(() => {
            refreshPromise = null;
          });

      const access = await refreshPromise;
      originalRequest.headers.Authorization = `Bearer ${access}`;
      return api(originalRequest);
    } catch (refreshError) {
      tokenStorage.clear();
      window.dispatchEvent(new Event("auth:logout"));
      return Promise.reject(refreshError);
    }
  },
);

export function getErrorMessage(error: unknown) {
  if (axios.isAxiosError(error)) {
    const data = error.response?.data;
    if (typeof data === "string") return data;
    if (data && typeof data === "object") return JSON.stringify(data);
    return error.message;
  }
  return "Unexpected error";
}
