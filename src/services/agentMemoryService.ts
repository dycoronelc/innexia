import { apiRequest } from './api';

// Tipos para la memoria del agente
export interface AgentMemory {
  id: number;
  user_id: number;
  session_id: string;
  memory_type: string;
  key: string;
  value: any;
  importance: number;
  expires_at?: string;
  created_at: string;
  updated_at?: string;
}

export interface ConversationSession {
  id: number;
  user_id: number;
  session_id: string;
  project_id?: number;
  current_context?: any;
  conversation_summary?: string;
  user_intent?: string;
  is_active: boolean;
  started_at: string;
  last_activity?: string;
}

export interface ConversationMessage {
  id: number;
  session_id: number;
  message_type: string;
  content: string;
  metadata_info?: any;
  intent_detected?: string;
  confidence_score?: number;
  created_at: string;
}

export interface UserContext {
  id: number;
  user_id: number;
  current_project_id?: number;
  expertise_level: string;
  business_sector?: string;
  preferred_language: string;
  notification_preferences?: any;
  learning_goals?: any;
  last_interaction?: string;
  created_at: string;
}

// Servicio de memoria del agente
export class AgentMemoryService {
  private token: string;

  constructor(token: string) {
    this.token = token;
  }

  // Crear o obtener sesión de conversación
  async createOrGetSession(projectId?: number): Promise<ConversationSession> {
    const response = await apiRequest<ConversationSession>(
      '/api/agent-memory/sessions',
      {
        method: 'POST',
        body: JSON.stringify({
          project_id: projectId,
          current_context: {},
          conversation_summary: '',
          user_intent: ''
        })
      },
      this.token
    );

    if (response.status === 'error') {
      throw new Error(response.error || 'Error al crear sesión');
    }

    return response.data!;
  }

  // Obtener sesión actual
  async getCurrentSession(): Promise<ConversationSession> {
    const response = await apiRequest<ConversationSession>(
      '/api/agent-memory/sessions/current',
      {
        method: 'GET'
      },
      this.token
    );

    if (response.status === 'error') {
      throw new Error(response.error || 'Error al obtener sesión');
    }

    return response.data!;
  }

  // Actualizar contexto de sesión
  async updateSessionContext(sessionId: number, context: any): Promise<ConversationSession> {
    const response = await apiRequest<ConversationSession>(
      `/api/agent-memory/sessions/${sessionId}`,
      {
        method: 'PUT',
        body: JSON.stringify({
          current_context: context
        })
      },
      this.token
    );

    if (response.status === 'error') {
      throw new Error(response.error || 'Error al actualizar contexto');
    }

    return response.data!;
  }

  // Añadir mensaje a la conversación
  async addMessage(sessionId: number, message: Omit<ConversationMessage, 'id' | 'session_id' | 'created_at'>): Promise<ConversationMessage> {
    const response = await apiRequest<ConversationMessage>(
      `/api/agent-memory/sessions/${sessionId}/messages`,
      {
        method: 'POST',
        body: JSON.stringify(message)
      },
      this.token
    );

    if (response.status === 'error') {
      throw new Error(response.error || 'Error al añadir mensaje');
    }

    return response.data!;
  }

  // Obtener historial de mensajes
  async getConversationHistory(sessionId: number, limit: number = 10): Promise<ConversationMessage[]> {
    const response = await apiRequest<ConversationMessage[]>(
      `/api/agent-memory/sessions/${sessionId}/messages?limit=${limit}`,
      {
        method: 'GET'
      },
      this.token
    );

    if (response.status === 'error') {
      throw new Error(response.error || 'Error al obtener historial');
    }

    return response.data!;
  }

  // Almacenar memoria
  async storeMemory(memory: Omit<AgentMemory, 'id' | 'user_id' | 'created_at' | 'updated_at'>): Promise<AgentMemory> {
    const response = await apiRequest<AgentMemory>(
      '/api/agent-memory/memories',
      {
        method: 'POST',
        body: JSON.stringify(memory)
      },
      this.token
    );

    if (response.status === 'error') {
      throw new Error(response.error || 'Error al almacenar memoria');
    }

    return response.data!;
  }

  // Obtener memorias
  async getMemories(query: {
    memory_type?: string;
    key?: string;
    session_id?: string;
    importance_min?: number;
    include_expired?: boolean;
  }): Promise<AgentMemory[]> {
    const params = new URLSearchParams();
    if (query.memory_type) params.append('memory_type', query.memory_type);
    if (query.key) params.append('key', query.key);
    if (query.session_id) params.append('session_id', query.session_id);
    if (query.importance_min) params.append('importance_min', query.importance_min.toString());
    if (query.include_expired) params.append('include_expired', query.include_expired.toString());

    const response = await apiRequest<AgentMemory[]>(
      `/api/agent-memory/memories?${params.toString()}`,
      {
        method: 'GET'
      },
      this.token
    );

    if (response.status === 'error') {
      throw new Error(response.error || 'Error al obtener memorias');
    }

    return response.data!;
  }

  // Obtener contexto del usuario
  async getUserContext(): Promise<UserContext> {
    const response = await apiRequest<UserContext>(
      '/api/agent-memory/context',
      {
        method: 'GET'
      },
      this.token
    );

    if (response.status === 'error') {
      throw new Error(response.error || 'Error al obtener contexto');
    }

    return response.data!;
  }

  // Actualizar contexto del usuario
  async updateUserContext(context: Partial<UserContext>): Promise<UserContext> {
    const response = await apiRequest<UserContext>(
      '/api/agent-memory/context',
      {
        method: 'PUT',
        body: JSON.stringify(context)
      },
      this.token
    );

    if (response.status === 'error') {
      throw new Error(response.error || 'Error al actualizar contexto');
    }

    return response.data!;
  }

  // Métodos estáticos para uso directo desde componentes
  private static getToken(): string {
    const TOKEN_KEY = 'innexia_token';
    const token = localStorage.getItem(TOKEN_KEY);
    if (!token) {
      throw new Error('No hay token de autenticación disponible');
    }
    return token;
  }

  static async getCurrentSession(): Promise<ConversationSession> {
    const token = AgentMemoryService.getToken();
    const service = new AgentMemoryService(token);
    return await service.getCurrentSession();
  }

  static async getUserContext(): Promise<UserContext> {
    const token = AgentMemoryService.getToken();
    const service = new AgentMemoryService(token);
    return await service.getUserContext();
  }

  static async storeProjectContext(projectId: number): Promise<void> {
    const token = AgentMemoryService.getToken();
    const service = new AgentMemoryService(token);
    await service.updateUserContext({ current_project_id: projectId });
  }

  static async createOrGetSession(projectId?: number): Promise<ConversationSession> {
    const token = AgentMemoryService.getToken();
    const service = new AgentMemoryService(token);
    return await service.createOrGetSession(projectId);
  }
}

