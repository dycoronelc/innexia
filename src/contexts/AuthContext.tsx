import React, { createContext, useContext, useState, useEffect } from 'react';
import type { ReactNode } from 'react';
import { authService, companyService } from '../services/api';

// Tipos para multiempresa
interface Company {
  id: number;
  name: string;
  slug: string;
  primary_color: string;
  secondary_color: string;
  logo_url?: string;
  industry?: string;
}

interface User {
  id: number;
  username: string;
  email: string;
  full_name: string;
  role: string;
  company_id: number;
  active: boolean;
  created_at: string;
  updated_at?: string;
}

interface LoginCredentials {
  username: string;
  password: string;
  companyId?: number;
}

interface AuthContextType {
  user: User | null;
  company: Company | null;
  token: string | null;
  login: (credentials: LoginCredentials) => Promise<void>;
  logout: () => Promise<void>;
  isAuthenticated: boolean;
  isLoading: boolean;
  isInitialized: boolean;
  error: string | null;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [company, setCompany] = useState<Company | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [isInitialized, setIsInitialized] = useState(false);
  const [error, setError] = useState<string | null>(null);


  // Claves de almacenamiento
  const TOKEN_KEY = import.meta.env.VITE_JWT_STORAGE_KEY || 'innexia_token';
  const REFRESH_TOKEN_KEY = import.meta.env.VITE_REFRESH_TOKEN_KEY || 'innexia_refresh_token';
  const USER_KEY = import.meta.env.VITE_USER_STORAGE_KEY || 'innexia_user';
  const COMPANY_KEY = 'innexia_company';

  useEffect(() => {
    // Verificar si el usuario está autenticado al cargar
    checkAuthStatus();
  }, []);

  // Manejar expiración de tokens globalmente
  useEffect(() => {
    if (!isAuthenticated || !token) return;

    // Interceptar respuestas 401 globalmente
    const originalFetch = window.fetch;
    window.fetch = async (...args) => {
      const requestUrl = typeof args[0] === 'string' ? args[0] : (args[0] instanceof Request ? args[0].url : '');
      const response = await originalFetch(...args);
      
      // 401 en login/register = credenciales incorrectas: no redirigir, que la página muestre el error
      const isAuthEndpoint = /\/api\/auth\/(login|login-company|register)/i.test(requestUrl);
      if (response.status === 401 && isAuthenticated && !isAuthEndpoint) {
        clearAuthData();
        const message = 'Su sesión ha expirado por inactividad. Por favor, inicie sesión nuevamente.';
        window.location.replace(`/login?message=${encodeURIComponent(message)}&type=session_expired`);
      }
      
      return response;
    };

    // Cleanup: restaurar fetch original
    return () => {
      window.fetch = originalFetch;
    };
  }, [isAuthenticated, token]);

  const checkAuthStatus = async () => {
    try {
      const token = localStorage.getItem(TOKEN_KEY);
      const storedUser = localStorage.getItem(USER_KEY);
      const storedCompany = localStorage.getItem(COMPANY_KEY);

      if (token && storedUser && storedCompany) {
        try {
          // Verificar si el token sigue siendo válido
          const response = await authService.verifyToken(token);
          if (response.status === 'success') {
            const userData = JSON.parse(storedUser);
            const companyData = JSON.parse(storedCompany);
            
            setUser(userData);
            setCompany(companyData);
            setToken(token);
            setIsAuthenticated(true);
          } else {
            // Token inválido, limpiar datos
            clearAuthData();
          }
        } catch (error) {
          console.error('Error verificando token:', error);
          clearAuthData();
        }
      } else {
        clearAuthData();
      }
    } catch (error) {
      console.error('Error en checkAuthStatus:', error);
      clearAuthData();
    } finally {
      setIsInitialized(true);
    }
  };

  const login = async (credentials: LoginCredentials) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await authService.login(credentials.username, credentials.password, credentials.companyId);
      
      if (response.status === 'success' && response.data) {
        const { access_token, refresh_token } = response.data;
        
        // Guardar tokens
        localStorage.setItem(TOKEN_KEY, access_token);
        localStorage.setItem(REFRESH_TOKEN_KEY, refresh_token);
        
        // Obtener información del usuario
        const userResponse = await authService.verifyToken(access_token);
        if (userResponse.status === 'success' && userResponse.data) {
                  const userData = userResponse.data;
        setUser(userData);
        setToken(access_token);
        localStorage.setItem(USER_KEY, JSON.stringify(userData));
        
        // Obtener información de la empresa
        const companyResponse = await companyService.getMyCompany(access_token);
        if (companyResponse.status === 'success' && companyResponse.data) {
          const companyData = companyResponse.data;
          setCompany(companyData);
          localStorage.setItem(COMPANY_KEY, JSON.stringify(companyData));
        }
        
        setIsAuthenticated(true);
        }
      } else {
        throw new Error(response.error || 'Error en el login');
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Error en el login';
      setError(errorMessage);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async () => {
    try {
      const token = localStorage.getItem(TOKEN_KEY);
      if (token) {
        await authService.logout(token);
      }
    } catch (error) {
      console.error('Error en logout:', error);
    } finally {
      clearAuthData();
    }
  };

  const clearAuthData = () => {
    setUser(null);
    setCompany(null);
    setToken(null);
    setIsAuthenticated(false);
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
    localStorage.removeItem(COMPANY_KEY);
  };

  const refreshUser = async () => {
    const token = localStorage.getItem(TOKEN_KEY);
    if (token) {
      try {
        const userResponse = await authService.verifyToken(token);
        if (userResponse.status === 'success' && userResponse.data) {
          const userData = userResponse.data;
          setUser(userData);
          localStorage.setItem(USER_KEY, JSON.stringify(userData));
        }
      } catch (error) {
        console.error('Error refreshing user:', error);
      }
    }
  };

  const value: AuthContextType = {
    user,
    company,
    token,
    login,
    logout,
    isAuthenticated,
    isLoading,
    isInitialized,
    error,
    refreshUser
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

