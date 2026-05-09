export interface User {
  id: string; // UUID from backend
  email: string;
  full_name: string | null;
  is_active: boolean;
  avatar_url: string | null;
  subscribed_city: string | null;
  is_alerts_enabled: boolean;
  created_at: string; // ISO datetime string
}

export interface UserCreate {
  email: string;
  full_name: string;
  password: string;
  subscribed_city?: string;
}

export interface UserLogin {
  email: string;
  password: string;
}

export interface Token {
  access_token: string;
  token_type: string;
  refresh_token?: string;
}

export interface UserRegisterResponse {
  user: User;
  token: Token;
}
