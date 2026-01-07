import { create } from 'zustand';
import { api } from '@/lib/api';
import type { AuthState, TokenResponse, AdminUser } from '@/types/auth';

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isAuthenticated: false,
  isLoading: false,
  error: null,

  login: async (email: string, password: string) => {
    set({ isLoading: true, error: null });
    try {
      const { data } = await api.post<TokenResponse>('/api/v1/auth/login', {
        email,
        password,
      });

      localStorage.setItem('access_token', data.access_token);
      localStorage.setItem('refresh_token', data.refresh_token);

      // Fetch user data
      const userResponse = await api.get<AdminUser>('/api/v1/auth/me');
      
      set({
        user: userResponse.data,
        isAuthenticated: true,
        isLoading: false,
        error: null,
      });
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 'Login failed';
      set({
        user: null,
        isAuthenticated: false,
        isLoading: false,
        error: errorMessage,
      });
      throw error;
    }
  },

  logout: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    set({
      user: null,
      isAuthenticated: false,
      error: null,
    });
  },

  fetchUser: async () => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      set({ isAuthenticated: false, user: null, isLoading: false });
      return;
    }

    set({ isLoading: true });
    try {
      const { data } = await api.get<AdminUser>('/api/v1/auth/me');
      set({
        user: data,
        isAuthenticated: true,
        isLoading: false,
      });
    } catch (error) {
      // Don't clear tokens on failed refresh - might be network issue
      console.error('Failed to fetch user:', error);
      set({
        isLoading: false,
      });
    }
  },

  clearError: () => set({ error: null }),
}));
