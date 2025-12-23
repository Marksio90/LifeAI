const API_URL = process.env.NEXT_PUBLIC_API_URL!;

export interface User {
  id: string;
  email: string;
  full_name?: string;
  preferred_language: string;
  preferred_voice: string;
  is_premium: boolean;
  created_at: string;
  preferences?: {
    auto_play_tts?: boolean;
    [key: string]: any;
  };
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface RegisterData {
  email: string;
  password: string;
  full_name?: string;
  preferred_language?: string;
}

export interface LoginData {
  email: string;
  password: string;
}

// Token management
export function setTokens(tokens: AuthTokens): void {
  localStorage.setItem('access_token', tokens.access_token);
  localStorage.setItem('refresh_token', tokens.refresh_token);
}

export function getAccessToken(): string | null {
  return localStorage.getItem('access_token');
}

export function getRefreshToken(): string | null {
  return localStorage.getItem('refresh_token');
}

export function clearTokens(): void {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
}

// API functions
export async function register(data: RegisterData): Promise<AuthTokens> {
  const res = await fetch(`${API_URL}/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });

  if (!res.ok) {
    const error = await res.json();
    throw new Error(error.detail || 'Registration failed');
  }

  return res.json();
}

export async function login(data: LoginData): Promise<AuthTokens> {
  const res = await fetch(`${API_URL}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });

  if (!res.ok) {
    const error = await res.json();
    throw new Error(error.detail || 'Login failed');
  }

  return res.json();
}

export async function getCurrentUser(): Promise<User> {
  const token = getAccessToken();
  if (!token) {
    throw new Error('No access token');
  }

  const res = await fetch(`${API_URL}/auth/me`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!res.ok) {
    if (res.status === 401) {
      clearTokens();
      throw new Error('Unauthorized');
    }
    throw new Error('Failed to fetch user');
  }

  return res.json();
}

export async function updateUser(data: Partial<User>): Promise<User> {
  const token = getAccessToken();
  if (!token) {
    throw new Error('No access token');
  }

  const params = new URLSearchParams();
  if (data.full_name) params.append('full_name', data.full_name);
  if (data.preferred_language) params.append('preferred_language', data.preferred_language);
  if (data.preferred_voice) params.append('preferred_voice', data.preferred_voice);

  const res = await fetch(`${API_URL}/auth/me?${params.toString()}`, {
    method: 'PUT',
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!res.ok) {
    throw new Error('Failed to update user');
  }

  return res.json();
}

export function logout(): void {
  clearTokens();
  window.location.href = '/login';
}
