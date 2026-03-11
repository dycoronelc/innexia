import { apiRequest } from './api';

// Interfaces para gestión avanzada de estado de conversaciones
export interface ConversationState {
  id: number;
  session_id: string;
  user_id: number;
  current_state: string;
  state_type: 'active' | 'paused' | 'completed' | 'abandoned' | 'transitioning';
  state_data: Record<string, any>;
  primary_context?: string;
  secondary_contexts: string[];
  context_stack: Record<string, any>[];
  current_intent?: string;
  intent_type: 'primary' | 'secondary' | 'contextual' | 'fallback';
  intent_confidence: number;
  intent_history: Record<string, any>[];
  flow_id?: string;
  flow_step: number;
  flow_data: Record<string, any>;
  flow_history: Record<string, any>[];
  short_term_memory: Record<string, any>;
  long_term_memory: Record<string, any>;
  memory_priority: Record<string, number>;
  active_threads: string[];
  thread_priorities: Record<string, number>;
  thread_contexts: Record<string, any>;
  previous_state?: string;
  transition_reason?: string;
  transition_data: Record<string, any>;
  created_at: string;
  updated_at?: string;
  last_activity: string;
}

export interface StateTransitionRequest {
  session_id: string;
  to_state: string;
  transition_type: string;
  transition_reason?: string;
  context_data?: Record<string, any>;
  intent_data?: Record<string, any>;
}

export interface ContextUpdateRequest {
  session_id: string;
  primary_context?: string;
  secondary_contexts?: string[];
  context_stack?: Record<string, any>[];
}

export interface MemoryUpdateRequest {
  session_id: string;
  memory_type: 'short_term' | 'long_term';
  memory_key: string;
  memory_value: any;
  priority?: number;
}

export interface ComplexConversationState {
  session_id: string;
  current_state: string;
  contexts: Record<string, any>;
  intents: Record<string, any>[];
  flows: Record<string, any>[];
  threads: Record<string, any>[];
  memories: Record<string, any>;
  last_activity: string;
}

export class AdvancedConversationStateService {
  // Gestión de estado
  static async createOrGetState(sessionId: string): Promise<ConversationState> {
    const response = await apiRequest<ConversationState>('/conversation-state/state', {
      method: 'POST',
      body: { session_id: sessionId }
    });
    return response.data;
  }

  static async transitionState(request: StateTransitionRequest): Promise<ConversationState> {
    const response = await apiRequest<ConversationState>('/conversation-state/transition', {
      method: 'POST',
      body: request
    });
    return response.data;
  }

  // Gestión de contexto
  static async updateContext(request: ContextUpdateRequest): Promise<ConversationState> {
    const response = await apiRequest<ConversationState>('/conversation-state/context', {
      method: 'PUT',
      body: request
    });
    return response.data;
  }

  // Gestión de memoria
  static async updateMemory(request: MemoryUpdateRequest): Promise<ConversationState> {
    const response = await apiRequest<ConversationState>('/conversation-state/memory', {
      method: 'PUT',
      body: request
    });
    return response.data;
  }

  // Estado complejo
  static async getComplexState(sessionId: string): Promise<ComplexConversationState> {
    const response = await apiRequest<ComplexConversationState>(`/conversation-state/complex-state/${sessionId}`, {
      method: 'GET'
    });
    return response.data;
  }

  // Tracking de eventos
  static async trackConversationEvent(
    sessionId: string, 
    eventType: string, 
    eventData: Record<string, any>
  ): Promise<{ session_id: string; event_type: string; state_updated: boolean }> {
    const response = await apiRequest<{ session_id: string; event_type: string; state_updated: boolean }>('/conversation-state/track-conversation-event', {
      method: 'POST',
      body: { session_id: sessionId, event_type: eventType, event_data: eventData }
    });
    return response.data;
  }

  // Métodos de utilidad para el chatbot
  static async initializeConversationSession(sessionId: string): Promise<ConversationState> {
    return this.createOrGetState(sessionId);
  }

  static async updateConversationIntent(
    sessionId: string, 
    intent: string, 
    confidence: number = 0.8,
    intentType: 'primary' | 'secondary' | 'contextual' | 'fallback' = 'primary'
  ): Promise<ConversationState> {
    return this.transitionState({
      session_id: sessionId,
      to_state: 'intent_identified',
      transition_type: 'automatic',
      transition_reason: `Intent identified: ${intent}`,
      intent_data: {
        current_intent: intent,
        intent_type: intentType,
        intent_confidence: confidence
      }
    });
  }

  static async storeConversationMemory(
    sessionId: string,
    memoryType: 'short_term' | 'long_term',
    key: string,
    value: any,
    priority: number = 1
  ): Promise<ConversationState> {
    return this.updateMemory({
      session_id: sessionId,
      memory_type: memoryType,
      memory_key: key,
      memory_value: value,
      priority
    });
  }

  static async getConversationContext(sessionId: string): Promise<ComplexConversationState> {
    return this.getComplexState(sessionId);
  }
}


