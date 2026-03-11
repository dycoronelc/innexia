import { apiRequest } from './api';

// Tipos para gestión de usuarios
export interface User {
  id: number;
  email: string;
  username: string;
  first_name: string;
  last_name: string;
  avatar_url?: string;
  bio?: string;
  phone?: string;
  date_of_birth?: string;
  gender?: string;
  location?: string;
  timezone?: string;
  language?: string;
  is_active: boolean;
  is_verified: boolean;
  is_premium: boolean;
  subscription_status?: string;
  subscription_expires_at?: string;
  created_at: string;
  updated_at?: string;
  last_login_at?: string;
}

export interface UserProfile {
  id: number;
  user_id: number;
  business_name?: string;
  business_type?: string;
  industry?: string;
  company_size?: string;
  role?: string;
  experience_level?: string;
  goals?: string[];
  interests?: string[];
  skills?: string[];
  preferences?: any;
  created_at: string;
  updated_at?: string;
}

export interface UserSettings {
  id: number;
  user_id: number;
  email_notifications: boolean;
  push_notifications: boolean;
  sms_notifications: boolean;
  marketing_emails: boolean;
  privacy_level: string;
  theme: string;
  language: string;
  timezone: string;
  created_at: string;
  updated_at?: string;
}

export interface UserActivity {
  id: number;
  user_id: number;
  activity_type: string;
  description: string;
  metadata?: any;
  ip_address?: string;
  user_agent?: string;
  created_at: string;
}

export interface UserSession {
  id: number;
  user_id: number;
  session_token: string;
  ip_address: string;
  user_agent: string;
  is_active: boolean;
  expires_at: string;
  created_at: string;
  last_activity_at?: string;
}

export interface UserSubscription {
  id: number;
  user_id: number;
  plan_name: string;
  plan_type: string;
  status: string;
  amount: number;
  currency: string;
  billing_cycle: string;
  start_date: string;
  end_date?: string;
  auto_renew: boolean;
  payment_method?: string;
  created_at: string;
  updated_at?: string;
}

export interface UserNotification {
  id: number;
  user_id: number;
  title: string;
  message: string;
  type: string;
  is_read: boolean;
  action_url?: string;
  metadata?: any;
  created_at: string;
  read_at?: string;
}

// Servicio de gestión de usuarios
export class UserService {
  private token: string;

  constructor(token: string) {
    this.token = token;
  }

  // Obtener perfil del usuario actual
  async getCurrentUser(): Promise<User> {
    const response = await apiRequest<User>(
      '/api/users/me',
      {
        method: 'GET'
      },
      this.token
    );

    if (response.status === 'error') {
      throw new Error(response.error || 'Error al obtener usuario');
    }

    return response.data!;
  }

  // Actualizar perfil del usuario
  async updateProfile(profileData: Partial<User>): Promise<User> {
    const response = await apiRequest<User>(
      '/api/users/me',
      {
        method: 'PUT',
        body: JSON.stringify(profileData)
      },
      this.token
    );

    if (response.status === 'error') {
      throw new Error(response.error || 'Error al actualizar perfil');
    }

    return response.data!;
  }

  // Obtener perfil de negocio
  async getBusinessProfile(): Promise<UserProfile> {
    const response = await apiRequest<UserProfile>(
      '/api/users/business-profile',
      {
        method: 'GET'
      },
      this.token
    );

    if (response.status === 'error') {
      throw new Error(response.error || 'Error al obtener perfil de negocio');
    }

    return response.data!;
  }

  // Actualizar perfil de negocio
  async updateBusinessProfile(profileData: Partial<UserProfile>): Promise<UserProfile> {
    const response = await apiRequest<UserProfile>(
      '/api/users/business-profile',
      {
        method: 'PUT',
        body: JSON.stringify(profileData)
      },
      this.token
    );

    if (response.status === 'error') {
      throw new Error(response.error || 'Error al actualizar perfil de negocio');
    }

    return response.data!;
  }

  // Obtener configuración del usuario
  async getUserSettings(): Promise<UserSettings> {
    const response = await apiRequest<UserSettings>(
      '/api/users/settings',
      {
        method: 'GET'
      },
      this.token
    );

    if (response.status === 'error') {
      throw new Error(response.error || 'Error al obtener configuración');
    }

    return response.data!;
  }

  // Actualizar configuración del usuario
  async updateUserSettings(settings: Partial<UserSettings>): Promise<UserSettings> {
    const response = await apiRequest<UserSettings>(
      '/api/users/settings',
      {
        method: 'PUT',
        body: JSON.stringify(settings)
      },
      this.token
    );

    if (response.status === 'error') {
      throw new Error(response.error || 'Error al actualizar configuración');
    }

    return response.data!;
  }

  // Obtener actividad del usuario
  async getUserActivity(limit: number = 20, offset: number = 0): Promise<UserActivity[]> {
    const response = await apiRequest<UserActivity[]>(
      `/api/users/activity?limit=${limit}&offset=${offset}`,
      {
        method: 'GET'
      },
      this.token
    );

    if (response.status === 'error') {
      throw new Error(response.error || 'Error al obtener actividad');
    }

    return response.data!;
  }

  // Obtener sesiones activas
  async getActiveSessions(): Promise<UserSession[]> {
    const response = await apiRequest<UserSession[]>(
      '/api/users/sessions',
      {
        method: 'GET'
      },
      this.token
    );

    if (response.status === 'error') {
      throw new Error(response.error || 'Error al obtener sesiones');
    }

    return response.data!;
  }

  // Cerrar sesión específica
  async logoutSession(sessionId: number): Promise<{ success: boolean; message: string }> {
    const response = await apiRequest<{ success: boolean; message: string }>(
      `/api/users/sessions/${sessionId}/logout`,
      {
        method: 'POST'
      },
      this.token
    );

    if (response.status === 'error') {
      throw new Error(response.error || 'Error al cerrar sesión');
    }

    return response.data!;
  }

  // Cerrar todas las sesiones excepto la actual
  async logoutAllSessions(): Promise<{ success: boolean; message: string }> {
    const response = await apiRequest<{ success: boolean; message: string }>(
      '/api/users/sessions/logout-all',
      {
        method: 'POST'
      },
      this.token
    );

    if (response.status === 'error') {
      throw new Error(response.error || 'Error al cerrar todas las sesiones');
    }

    return response.data!;
  }

  // Obtener suscripción del usuario
  async getUserSubscription(): Promise<UserSubscription | null> {
    const response = await apiRequest<UserSubscription | null>(
      '/api/users/subscription',
      {
        method: 'GET'
      },
      this.token
    );

    if (response.status === 'error') {
      throw new Error(response.error || 'Error al obtener suscripción');
    }

    return response.data!;
  }

  // Obtener notificaciones del usuario
  async getUserNotifications(limit: number = 20, offset: number = 0, unreadOnly: boolean = false): Promise<UserNotification[]> {
    const queryParams = new URLSearchParams();
    queryParams.append('limit', limit.toString());
    queryParams.append('offset', offset.toString());
    if (unreadOnly) queryParams.append('unread_only', 'true');

    const response = await apiRequest<UserNotification[]>(
      `/api/users/notifications?${queryParams.toString()}`,
      {
        method: 'GET'
      },
      this.token
    );

    if (response.status === 'error') {
      throw new Error(response.error || 'Error al obtener notificaciones');
    }

    return response.data!;
  }

  // Marcar notificación como leída
  async markNotificationRead(notificationId: number): Promise<{ success: boolean; message: string }> {
    const response = await apiRequest<{ success: boolean; message: string }>(
      `/api/users/notifications/${notificationId}/read`,
      {
        method: 'PUT'
      },
      this.token
    );

    if (response.status === 'error') {
      throw new Error(response.error || 'Error al marcar notificación como leída');
    }

    return response.data!;
  }

  // Marcar todas las notificaciones como leídas
  async markAllNotificationsRead(): Promise<{ success: boolean; message: string }> {
    const response = await apiRequest<{ success: boolean; message: string }>(
      '/api/users/notifications/read-all',
      {
        method: 'PUT'
      },
      this.token
    );

    if (response.status === 'error') {
      throw new Error(response.error || 'Error al marcar todas las notificaciones como leídas');
    }

    return response.data!;
  }

  // Eliminar notificación
  async deleteNotification(notificationId: number): Promise<{ success: boolean; message: string }> {
    const response = await apiRequest<{ success: boolean; message: string }>(
      `/api/users/notifications/${notificationId}`,
      {
        method: 'DELETE'
      },
      this.token
    );

    if (response.status === 'error') {
      throw new Error(response.error || 'Error al eliminar notificación');
    }

    return response.data!;
  }

  // Cambiar contraseña
  async changePassword(currentPassword: string, newPassword: string): Promise<{ success: boolean; message: string }> {
    const response = await apiRequest<{ success: boolean; message: string }>(
      '/api/users/change-password',
      {
        method: 'POST',
        body: JSON.stringify({
          current_password: currentPassword,
          new_password: newPassword
        })
      },
      this.token
    );

    if (response.status === 'error') {
      throw new Error(response.error || 'Error al cambiar contraseña');
    }

    return response.data!;
  }

  // Solicitar eliminación de cuenta
  async requestAccountDeletion(reason?: string): Promise<{ success: boolean; message: string }> {
    const response = await apiRequest<{ success: boolean; message: string }>(
      '/api/users/request-deletion',
      {
        method: 'POST',
        body: JSON.stringify({
          reason
        })
      },
      this.token
    );

    if (response.status === 'error') {
      throw new Error(response.error || 'Error al solicitar eliminación de cuenta');
    }

    return response.data!;
  }

  // Obtener estadísticas del usuario
  async getUserStats(): Promise<{
    total_projects: number;
    completed_projects: number;
    total_activities: number;
    completed_activities: number;
    total_content_viewed: number;
    total_time_spent: number;
    days_active: number;
    last_activity: string;
  }> {
    const response = await apiRequest<{
      total_projects: number;
      completed_projects: number;
      total_activities: number;
      completed_activities: number;
      total_content_viewed: number;
      total_time_spent: number;
      days_active: number;
      last_activity: string;
    }>(
      '/api/users/stats',
      {
        method: 'GET'
      },
      this.token
    );

    if (response.status === 'error') {
      throw new Error(response.error || 'Error al obtener estadísticas');
    }

    return response.data!;
  }

  // Métodos de conveniencia para el chatbot
  async getUserPreferences(): Promise<any> {
    const profile = await this.getBusinessProfile();
    return profile.preferences || {};
  }

  async getUserGoals(): Promise<string[]> {
    const profile = await this.getBusinessProfile();
    return profile.goals || [];
  }

  async getUserInterests(): Promise<string[]> {
    const profile = await this.getBusinessProfile();
    return profile.interests || [];
  }

  async getUserSkills(): Promise<string[]> {
    const profile = await this.getBusinessProfile();
    return profile.skills || [];
  }

  async isPremiumUser(): Promise<boolean> {
    const user = await this.getCurrentUser();
    return user.is_premium;
  }

  async getUserBusinessInfo(): Promise<{
    business_name?: string;
    business_type?: string;
    industry?: string;
    company_size?: string;
    role?: string;
  }> {
    const profile = await this.getBusinessProfile();
    return {
      business_name: profile.business_name,
      business_type: profile.business_type,
      industry: profile.industry,
      company_size: profile.company_size,
      role: profile.role
    };
  }
}

