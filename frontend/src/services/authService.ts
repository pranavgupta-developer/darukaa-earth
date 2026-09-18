/**
 * Authentication API service.
 */

import api from '../lib/api';
import type { LoginRequest, RegisterRequest, TokenResponse } from '../types';

export const authService = {
  async register(data: RegisterRequest): Promise<TokenResponse> {
    const response = await api.post<TokenResponse>('/auth/register', data);
    return response.data;
  },

  async login(data: LoginRequest): Promise<TokenResponse> {
    const response = await api.post<TokenResponse>('/auth/login', data);
    return response.data;
  },

  async getMe(): Promise<TokenResponse['user']> {
    const response = await api.get<TokenResponse['user']>('/auth/me');
    return response.data;
  },
};
