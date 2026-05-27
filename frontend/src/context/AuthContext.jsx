import { createContext, useContext, useEffect, useMemo, useState } from "react";
import axiosClient from "../api/axiosClient";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem("coursematch_token"));
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(Boolean(token));

  useEffect(() => {
    let ignore = false;
    async function loadUser() {
      if (!token) {
        setLoading(false);
        setUser(null);
        return;
      }
      try {
        const { data } = await axiosClient.get("/auth/me");
        if (!ignore) setUser(data);
      } catch {
        localStorage.removeItem("coursematch_token");
        if (!ignore) {
          setToken(null);
          setUser(null);
        }
      } finally {
        if (!ignore) setLoading(false);
      }
    }
    loadUser();
    return () => {
      ignore = true;
    };
  }, [token]);

  async function login(email, password) {
    const { data } = await axiosClient.post("/auth/login", { email, password });
    localStorage.setItem("coursematch_token", data.access_token);
    setToken(data.access_token);
    const me = await axiosClient.get("/auth/me");
    setUser(me.data);
  }

  async function register(payload) {
    await axiosClient.post("/auth/register", payload);
  }

  function logout() {
    localStorage.removeItem("coursematch_token");
    setToken(null);
    setUser(null);
  }

  const value = useMemo(
    () => ({ token, user, loading, login, register, logout }),
    [token, user, loading]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  return useContext(AuthContext);
}

