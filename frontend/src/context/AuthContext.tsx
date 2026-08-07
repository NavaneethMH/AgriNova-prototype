import React, { createContext, useContext, useState, useEffect } from 'react';
import { User, AuthTokens } from '../types';
import { authService } from '../services/api';

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (data: { email: string; password: string; full_name: string; organization?: string }) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const initAuth = async () => {
      const token = localStorage.getItem('agrinova_access_token');
      if (token) {
        try {
          const userData = await authService.getMe();
          setUser(userData);
        } catch {
          localStorage.removeItem('agrinova_access_token');
          localStorage.removeItem('agrinova_refresh_token');
        }
      }
      setIsLoading(false);
    };
    initAuth();
  }, []);

  const login = async (email: string, password: string) => {
    const tokens: AuthTokens = await authService.login(email, password);
    localStorage.setItem('agrinova_access_token', tokens.access_token);
    localStorage.setItem('agrinova_refresh_token', tokens.refresh_token);
    const userData = await authService.getMe();
    setUser(userData);
  };

  const register = async (data: { email: string; password: string; full_name: string; organization?: string }) => {
    const tokens: AuthTokens = await authService.register(data);
    localStorage.setItem('agrinova_access_token', tokens.access_token);
    localStorage.setItem('agrinova_refresh_token', tokens.refresh_token);
    const userData = await authService.getMe();
    setUser(userData);
  };

  const logout = () => {
    localStorage.removeItem('agrinova_access_token');
    localStorage.removeItem('agrinova_refresh_token');
    setUser(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        isLoading,
        login,
        register,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
