import axios from "axios";

// Access the API URL, ensuring the /api/v1/ prefix is present
const rawBaseURL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const cleanBaseURL = rawBaseURL.replace(/\/+$/, ""); // Supprime les slashs de fin
const baseURL = cleanBaseURL.endsWith("/api/v1") ? `${cleanBaseURL}/` : `${cleanBaseURL}/api/v1/`;

const apiClient = axios.create({
  baseURL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Interceptor to attach Authorization header if token exists
apiClient.interceptors.request.use(
  (config) => {
    // Only access localStorage if in browser environment
    if (typeof window !== "undefined") {
      const token = localStorage.getItem("access_token");
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }

      // Add Accept-Language header
      const lang = localStorage.getItem("app_lang") || "fr";
      config.headers["Accept-Language"] = lang;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Interceptor to handle responses and common errors
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // Check if error is 401 Unauthorized
    if (error.response?.status === 401) {
      if (typeof window !== "undefined") {
        localStorage.removeItem("access_token");
        // Optionally redirect to login page
        // window.location.href = "/auth/login";
      }
    }
    return Promise.reject(error);
  }
);

export default apiClient;
