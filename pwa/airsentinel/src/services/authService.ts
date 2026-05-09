import apiClient from "./apiClient";
import { User, UserCreate, UserLogin, Token, UserRegisterResponse } from "../types/auth";

const AUTH_TOKEN_KEY = "access_token";

const authService = {
  /**
   * Registers a new user and stores the returned token.
   * @param userData UserCreate information.
   */
  async register(userData: UserCreate): Promise<UserRegisterResponse> {
    const response = await apiClient.post<UserRegisterResponse>("auth/register", userData);
    const data = response.data;
    
    if (typeof window !== "undefined" && data.token) {
      localStorage.setItem(AUTH_TOKEN_KEY, data.token.access_token);
    }
    
    return data;
  },

  /**
   * Logs in a user and stores the token.
   * @param credentials UserLogin information.
   */
  async login(credentials: UserLogin): Promise<Token> {
    const response = await apiClient.post<Token>("auth/login", credentials);
    const token = response.data;
    
    if (typeof window !== "undefined") {
      localStorage.setItem(AUTH_TOKEN_KEY, token.access_token);
    }
    
    return token;
  },

  /**
   * Logs out the user by removing the token.
   */
  updateProfile: async (data: { full_name?: string; email?: string; subscribed_city?: string }) => {
    const response = await apiClient.patch("users/me", data);
    return response.data;
  },

  logout: () => {
    if (typeof window !== "undefined") {
      localStorage.removeItem(AUTH_TOKEN_KEY);
    }
  },

  /**
   * Retrieves the current user's information.
   */
  async getCurrentUser(): Promise<User> {
    const response = await apiClient.get<User>("auth/me");
    return response.data;
  },

  /**
   * Checks if the user is currently authenticated (has a token).
   */
  isAuthenticated(): boolean {
    if (typeof window !== "undefined") {
      return !!localStorage.getItem(AUTH_TOKEN_KEY);
    }
    return false;
  },
};

export default authService;
