import axios from "axios";

const axiosClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "",
  headers: {
    "Content-Type": "application/json",
  },
});

axiosClient.interceptors.request.use((config) => {
  const token = localStorage.getItem("coursematch_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

axiosClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const detail = error?.response?.data?.detail || "";
    const isExpiredToken = error?.response?.status === 401 && String(detail).toLowerCase().includes("token");
    if (isExpiredToken) {
      localStorage.removeItem("coursematch_token");
      sessionStorage.setItem("coursematch_auth_message", "PhiÃªn Ä‘Äƒng nháº­p Ä‘Ã£ háº¿t háº¡n. Vui lÃ²ng Ä‘Äƒng nháº­p láº¡i.");
      window.dispatchEvent(new Event("coursematch:auth-expired"));
      if (!window.location.pathname.includes("/login")) {
        window.location.assign("/login");
      }
    }
    return Promise.reject(error);
  },
);

export function getApiError(error) {
  const detail = error?.response?.data?.detail;
  if (Array.isArray(detail)) {
    return detail.map((item) => item.msg).join(", ");
  }
  if (error?.response?.status === 401 && String(detail || "").toLowerCase().includes("token")) {
    return "PhiÃªn Ä‘Äƒng nháº­p Ä‘Ã£ háº¿t háº¡n. Vui lÃ²ng Ä‘Äƒng nháº­p láº¡i.";
  }
  return detail || error?.message || "Co loi xay ra.";
}

export default axiosClient;

