import axios from 'axios';
import {
  AuthTokens,
  User,
  Farm,
  DashboardData,
  WeatherData,
  SatelliteData,
  Prediction,
  RecommendationResponse,
  AnalyticsResponse,
  Notification,
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor: Attach JWT Bearer token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('agrinova_access_token');
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor: Handle 401 & token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      const refreshToken = localStorage.getItem('agrinova_refresh_token');
      if (refreshToken) {
        try {
          const res = await axios.post<AuthTokens>(`${API_BASE_URL}/auth/refresh`, {
            refresh_token: refreshToken,
          });
          localStorage.setItem('agrinova_access_token', res.data.access_token);
          localStorage.setItem('agrinova_refresh_token', res.data.refresh_token);
          originalRequest.headers.Authorization = `Bearer ${res.data.access_token}`;
          return api(originalRequest);
        } catch {
          localStorage.removeItem('agrinova_access_token');
          localStorage.removeItem('agrinova_refresh_token');
          window.location.href = '/login';
        }
      } else {
        localStorage.removeItem('agrinova_access_token');
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

// ---- API SERVICE FUNCTIONS ----

export const authService = {
  login: async (email: string, password: string): Promise<AuthTokens> => {
    const res = await api.post<AuthTokens>('/auth/login', { email, password });
    return res.data;
  },
  register: async (data: { email: string; password: string; full_name: string; organization?: string }): Promise<AuthTokens> => {
    const res = await api.post<AuthTokens>('/auth/register', data);
    return res.data;
  },
  getMe: async (): Promise<User> => {
    const res = await api.get<User>('/auth/me');
    return res.data;
  },
};

export const dashboardService = {
  getDashboard: async (): Promise<DashboardData> => {
    const res = await api.get<DashboardData>('/dashboard');
    return res.data;
  },
};

export const farmService = {
  getFarms: async (page = 1, pageSize = 20): Promise<{ items: Farm[]; total: number }> => {
    const res = await api.get('/farms', { params: { page, page_size: pageSize } });
    return res.data;
  },
  getFarm: async (id: string): Promise<Farm> => {
    const res = await api.get<Farm>(`/farms/${id}`);
    return res.data;
  },
  createFarm: async (data: Partial<Farm>): Promise<Farm> => {
    const res = await api.post<Farm>('/farms', data);
    return res.data;
  },
  updateFarm: async (id: string, data: Partial<Farm>): Promise<Farm> => {
    const res = await api.put<Farm>(`/farms/${id}`, data);
    return res.data;
  },
  deleteFarm: async (id: string): Promise<void> => {
    await api.delete(`/farms/${id}`);
  },
};

export const weatherService = {
  getWeather: async (farmId: string): Promise<WeatherData> => {
    const res = await api.get<WeatherData>(`/weather/${farmId}`);
    return res.data;
  },
  refreshWeather: async (farmId: string): Promise<WeatherData> => {
    const res = await api.post<WeatherData>(`/weather/${farmId}/refresh`);
    return res.data;
  },
  getHistory: async (farmId: string, days = 7): Promise<{ items: WeatherData[] }> => {
    const res = await api.get(`/weather/${farmId}/history`, { params: { days } });
    return res.data;
  },
};

export const satelliteService = {
  getSatellite: async (farmId: string): Promise<SatelliteData> => {
    const res = await api.get<SatelliteData>(`/satellite/${farmId}`);
    return res.data;
  },
  fetchSatellite: async (farmId: string): Promise<SatelliteData> => {
    const res = await api.post<SatelliteData>(`/satellite/${farmId}/fetch`);
    return res.data;
  },
};

export const predictionService = {
  predict: async (data: { farm_id: string; ndvi?: number; ndwi?: number; temperature?: number; humidity?: number; rainfall?: number }): Promise<Prediction> => {
    const res = await api.post<Prediction>('/predict', data);
    return res.data;
  },
  getHistory: async (farmId: string, limit = 10): Promise<Prediction[]> => {
    const res = await api.get<Prediction[]>(`/predict/history/${farmId}`, { params: { limit } });
    return res.data;
  },
  getRecommendations: async (farmId: string): Promise<RecommendationResponse> => {
    const res = await api.get<RecommendationResponse>(`/predict/recommendations/${farmId}`);
    return res.data;
  },
};

export const analyticsService = {
  getAnalytics: async (farmId: string, period: 'weekly' | 'monthly' | 'all' = 'weekly'): Promise<AnalyticsResponse> => {
    const res = await api.get<AnalyticsResponse>(`/analytics/${farmId}`, { params: { period } });
    return res.data;
  },
};

export const notificationService = {
  getNotifications: async (page = 1, unreadOnly = false): Promise<{ items: Notification[]; total: number; unread_count: number }> => {
    const res = await api.get('/notifications', { params: { page, unread_only: unreadOnly } });
    return res.data;
  },
  markRead: async (id: string): Promise<Notification> => {
    const res = await api.patch<Notification>(`/notifications/${id}/read`);
    return res.data;
  },
  markAllRead: async (): Promise<{ marked_read: number }> => {
    const res = await api.patch('/notifications/read-all');
    return res.data;
  },
  dismiss: async (id: string): Promise<void> => {
    await api.patch(`/notifications/${id}/dismiss`);
  },
};
