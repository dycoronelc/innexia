import { apiRequest } from './api';

// Tipos para gestión de notificaciones
export interface Notification {
  id: number;
  user_id: number;
  title: string;
  message: string;
  type: string;
  category?: string;
  priority: string;
  is_read: boolean;
  is_actionable: boolean;
  action_url?: string;
  action_text?: string;
  action_type?: string;
  metadata?: any;
  expires_at?: string;
  created_at: string;
  read_at?: string;
}

export interface NotificationTemplate {
  id: number;
  name: string;
  description?: string;
  title_template: string;
  message_template: string;
  type: string;
  category?: string;
  priority: string;
  is_actionable: boolean;
  action_url_template?: string;
  action_text?: string;
  action_type?: string;
  variables?: string[];
  is_active: boolean;
  created_at: string;
  updated_at?: string;
}

export interface NotificationPreference {
  id: number;
  user_id: number;
  notification_type: string;
  email_enabled: boolean;
  push_enabled: boolean;
  sms_enabled: boolean;
  in_app_enabled: boolean;
  frequency: string;
  quiet_hours_start?: string;
  quiet_hours_end?: string;
  created_at: string;
  updated_at?: string;
}

export interface NotificationSchedule {
  id: number;
  user_id: number;
  template_id: number;
  scheduled_at: string;
  variables?: any;
  status: string;
  sent_at?: string;
  created_at: string;
}

export interface NotificationChannel {
  id: number;
  user_id: number;
  channel_type: string;
  channel_value: string;
  is_verified: boolean;
  is_active: boolean;
  created_at: string;
  verified_at?: string;
}

// Servicio de gestión de notificaciones
export class NotificationService {
  private token: string;

  constructor(token: string) {
    this.token = token;
  }

  // Obtener notificaciones del usuario
  async getNotifications(filters?: {
    type?: string;
    category?: string;
    is_read?: boolean;
    priority?: string;
  }, limit: number = 20, offset: number = 0): Promise<{
    notifications: Notification[];
    total_count: number;
    unread_count: number;
    has_more: boolean;
  }> {
    const queryParams = new URLSearchParams();
    if (filters?.type) queryParams.append('type', filters.type);
    if (filters?.category) queryParams.append('category', filters.category);
    if (filters?.is_read !== undefined) queryParams.append('is_read', filters.is_read.toString());
    if (filters?.priority) queryParams.append('priority', filters.priority);
    queryParams.append('limit', limit.toString());
    queryParams.append('offset', offset.toString());

    const response = await apiRequest<{
      notifications: Notification[];
      total_count: number;
      unread_count: number;
      has_more: boolean;
    }>(
      `/api/notifications?${queryParams.toString()}`,
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

  // Obtener notificación por ID
  async getNotificationById(notificationId: number): Promise<Notification> {
    const response = await apiRequest<Notification>(
      `/api/notifications/${notificationId}`,
      {
        method: 'GET'
      },
      this.token
    );

    if (response.status === 'error') {
      throw new Error(response.error || 'Error al obtener notificación');
    }

    return response.data!;
  }

  // Marcar notificación como leída
  async markNotificationRead(notificationId: number): Promise<{ success: boolean; message: string }> {
    const response = await apiRequest<{ success: boolean; message: string }>(
      `/api/notifications/${notificationId}/read`,
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
  async markAllNotificationsRead(filters?: {
    type?: string;
    category?: string;
  }): Promise<{ success: boolean; message: string; count: number }> {
    const queryParams = new URLSearchParams();
    if (filters?.type) queryParams.append('type', filters.type);
    if (filters?.category) queryParams.append('category', filters.category);

    const url = queryParams.toString() 
      ? `/api/notifications/read-all?${queryParams.toString()}`
      : '/api/notifications/read-all';

    const response = await apiRequest<{ success: boolean; message: string; count: number }>(
      url,
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
      `/api/notifications/${notificationId}`,
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

  // Eliminar todas las notificaciones leídas
  async deleteReadNotifications(): Promise<{ success: boolean; message: string; count: number }> {
    const response = await apiRequest<{ success: boolean; message: string; count: number }>(
      '/api/notifications/delete-read',
      {
        method: 'DELETE'
      },
      this.token
    );

    if (response.status === 'error') {
      throw new Error(response.error || 'Error al eliminar notificaciones leídas');
    }

    return response.data!;
  }

  // Obtener preferencias de notificación
  async getNotificationPreferences(): Promise<NotificationPreference[]> {
    const response = await apiRequest<NotificationPreference[]>(
      '/api/notifications/preferences',
      {
        method: 'GET'
      },
      this.token
    );

    if (response.status === 'error') {
      throw new Error(response.error || 'Error al obtener preferencias de notificación');
    }

    return response.data!;
  }

  // Actualizar preferencia de notificación
  async updateNotificationPreference(notificationType: string, preferences: Partial<NotificationPreference>): Promise<NotificationPreference> {
    const response = await apiRequest<NotificationPreference>(
      `/api/notifications/preferences/${notificationType}`,
      {
        method: 'PUT',
        body: JSON.stringify(preferences)
      },
      this.token
    );

    if (response.status === 'error') {
      throw new Error(response.error || 'Error al actualizar preferencia de notificación');
    }

    return response.data!;
  }

  // Obtener canales de notificación
  async getNotificationChannels(): Promise<NotificationChannel[]> {
    const response = await apiRequest<NotificationChannel[]>(
      '/api/notifications/channels',
      {
        method: 'GET'
      },
      this.token
    );

    if (response.status === 'error') {
      throw new Error(response.error || 'Error al obtener canales de notificación');
    }

    return response.data!;
  }

  // Agregar canal de notificación
  async addNotificationChannel(channelData: Omit<NotificationChannel, 'id' | 'user_id' | 'created_at' | 'verified_at'>): Promise<NotificationChannel> {
    const response = await apiRequest<NotificationChannel>(
      '/api/notifications/channels',
      {
        method: 'POST',
        body: JSON.stringify(channelData)
      },
      this.token
    );

    if (response.status === 'error') {
      throw new Error(response.error || 'Error al agregar canal de notificación');
    }

    return response.data!;
  }

  // Verificar canal de notificación
  async verifyNotificationChannel(channelId: number, verificationCode: string): Promise<{ success: boolean; message: string }> {
    const response = await apiRequest<{ success: boolean; message: string }>(
      `/api/notifications/channels/${channelId}/verify`,
      {
        method: 'POST',
        body: JSON.stringify({
          verification_code: verificationCode
        })
      },
      this.token
    );

    if (response.status === 'error') {
      throw new Error(response.error || 'Error al verificar canal de notificación');
    }

    return response.data!;
  }

  // Eliminar canal de notificación
  async deleteNotificationChannel(channelId: number): Promise<{ success: boolean; message: string }> {
    const response = await apiRequest<{ success: boolean; message: string }>(
      `/api/notifications/channels/${channelId}`,
      {
        method: 'DELETE'
      },
      this.token
    );

    if (response.status === 'error') {
      throw new Error(response.error || 'Error al eliminar canal de notificación');
    }

    return response.data!;
  }

  // Obtener notificaciones programadas
  async getScheduledNotifications(): Promise<NotificationSchedule[]> {
    const response = await apiRequest<NotificationSchedule[]>(
      '/api/notifications/scheduled',
      {
        method: 'GET'
      },
      this.token
    );

    if (response.status === 'error') {
      throw new Error(response.error || 'Error al obtener notificaciones programadas');
    }

    return response.data!;
  }

  // Programar notificación
  async scheduleNotification(scheduleData: Omit<NotificationSchedule, 'id' | 'user_id' | 'created_at'>): Promise<NotificationSchedule> {
    const response = await apiRequest<NotificationSchedule>(
      '/api/notifications/schedule',
      {
        method: 'POST',
        body: JSON.stringify(scheduleData)
      },
      this.token
    );

    if (response.status === 'error') {
      throw new Error(response.error || 'Error al programar notificación');
    }

    return response.data!;
  }

  // Cancelar notificación programada
  async cancelScheduledNotification(scheduleId: number): Promise<{ success: boolean; message: string }> {
    const response = await apiRequest<{ success: boolean; message: string }>(
      `/api/notifications/scheduled/${scheduleId}/cancel`,
      {
        method: 'POST'
      },
      this.token
    );

    if (response.status === 'error') {
      throw new Error(response.error || 'Error al cancelar notificación programada');
    }

    return response.data!;
  }

  // Obtener templates de notificación
  async getNotificationTemplates(): Promise<NotificationTemplate[]> {
    const response = await apiRequest<NotificationTemplate[]>(
      '/api/notifications/templates',
      {
        method: 'GET'
      },
      this.token
    );

    if (response.status === 'error') {
      throw new Error(response.error || 'Error al obtener templates de notificación');
    }

    return response.data!;
  }

  // Obtener template por ID
  async getNotificationTemplateById(templateId: number): Promise<NotificationTemplate> {
    const response = await apiRequest<NotificationTemplate>(
      `/api/notifications/templates/${templateId}`,
      {
        method: 'GET'
      },
      this.token
    );

    if (response.status === 'error') {
      throw new Error(response.error || 'Error al obtener template de notificación');
    }

    return response.data!;
  }

  // Métodos de conveniencia para el chatbot
  async getUnreadNotifications(): Promise<Notification[]> {
    const result = await this.getNotifications({ is_read: false });
    return result.notifications;
  }

  async getHighPriorityNotifications(): Promise<Notification[]> {
    const result = await this.getNotifications({ priority: 'high' });
    return result.notifications;
  }

  async getProjectNotifications(): Promise<Notification[]> {
    const result = await this.getNotifications({ category: 'project' });
    return result.notifications;
  }

  async getDocumentNotifications(): Promise<Notification[]> {
    const result = await this.getNotifications({ category: 'document' });
    return result.notifications;
  }

  async getSystemNotifications(): Promise<Notification[]> {
    const result = await this.getNotifications({ category: 'system' });
    return result.notifications;
  }

  async getActionableNotifications(): Promise<Notification[]> {
    const result = await this.getNotifications();
    return result.notifications.filter(notification => notification.is_actionable);
  }

  // Métodos para el chatbot
  async sendProjectCompletionNotification(projectId: number, projectName: string): Promise<void> {
    // Este método sería llamado internamente por el sistema
    // No necesita implementación en el cliente
    console.log(`Notificación de proyecto completado: ${projectName} (ID: ${projectId})`);
  }

  async sendDocumentApprovalNotification(documentId: number, documentTitle: string): Promise<void> {
    // Este método sería llamado internamente por el sistema
    // No necesita implementación en el cliente
    console.log(`Notificación de documento aprobado: ${documentTitle} (ID: ${documentId})`);
  }

  async sendActivityReminderNotification(activityId: number, activityTitle: string, dueDate: string): Promise<void> {
    // Este método sería llamado internamente por el sistema
    // No necesita implementación en el cliente
    console.log(`Recordatorio de actividad: ${activityTitle} (ID: ${activityId}) - Vence: ${dueDate}`);
  }

  async sendRecommendationNotification(recommendationId: number, recommendationTitle: string): Promise<void> {
    // Este método sería llamado internamente por el sistema
    // No necesita implementación en el cliente
    console.log(`Nueva recomendación: ${recommendationTitle} (ID: ${recommendationId})`);
  }
}

