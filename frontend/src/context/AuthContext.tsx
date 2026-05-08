import { createContext, ReactNode, useCallback, useContext, useEffect, useMemo, useState } from "react";

import { User } from "../api/types";
import * as authService from "../services/auth";
import { tokenStorage } from "../services/tokenStorage";

interface AuthContextValue {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: Parameters<typeof authService.register>[0] extends infer T ? (payload: T) => Promise<void> : never;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const refreshUser = useCallback(async () => {
    const currentUser = await authService.fetchCurrentUser();
    setUser(currentUser);
  }, []);

  useEffect(() => {
    let mounted = true;
    async function bootstrap() {
      if (!tokenStorage.getAccessToken()) {
        setIsLoading(false);
        return;
      }
      try {
        const currentUser = await authService.fetchCurrentUser();
        if (mounted) setUser(currentUser);
      } catch {
        tokenStorage.clear();
      } finally {
        if (mounted) setIsLoading(false);
      }
    }
    bootstrap();
    const onLogout = () => setUser(null);
    window.addEventListener("auth:logout", onLogout);
    return () => {
      mounted = false;
      window.removeEventListener("auth:logout", onLogout);
    };
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    const currentUser = await authService.login(email, password);
    setUser(currentUser);
  }, []);

  const register = useCallback(async (payload: Parameters<typeof authService.register>[0]) => {
    await authService.register(payload);
  }, []);

  const logout = useCallback(async () => {
    await authService.logout();
    setUser(null);
  }, []);

  const value = useMemo(
    () => ({
      user,
      isLoading,
      isAuthenticated: Boolean(user),
      login,
      register,
      logout,
      refreshUser,
    }),
    [isLoading, login, logout, refreshUser, register, user],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used inside AuthProvider");
  }
  return context;
}
