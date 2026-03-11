/**
 * Servicio para interactuar con el sistema de agentes OpenAI
 */

import { apiRequest } from './api';

export interface IntentDetectionRequest {
  message: string;
  conversation_context: {
    recent_messages: Array<{
      text: string;
      sender: 'user' | 'ai';
      timestamp: string;
    }>;
    current_project?: {
      id: string;
      name: string;
      description: string;
    };
    user_profile?: {
      role: string;
      preferences: string[];
    };
  };
}

export interface IntentDetectionResult {
  intent: string;
  confidence: number;
  extractedContext: string;
  suggestedAction: string;
  reasoning?: string;
}

export interface BMCGenerationRequest {
  business_idea: string;
  use_high_quality?: boolean;
}

export interface BMCData {
  key_partners: string[];
  key_activities: string[];
  key_resources: string[];
  value_propositions: string[];
  customer_relationships: string[];
  channels: string[];
  customer_segments: string[];
  cost_structure: string[];
  revenue_streams: string[];
}

export interface BMCResult {
  bmc: BMCData;
  recommended_activities: Array<{
    title: string;
    description: string;
    priority: string;
    estimated_duration_days: number;
  }>;
}

export interface BusinessPlanRequest {
  business_idea: string;
}

export interface MarketingPlanRequest {
  business_idea: string;
}

export interface ProjectAnalysisRequest {
  project_data: Record<string, any>;
}

class AgentsService {
  /**
   * Detecta la intención del usuario usando agentes especializados
   */
  async detectIntent(
    request: IntentDetectionRequest,
    token: string
  ): Promise<IntentDetectionResult> {
    const response = await apiRequest('/api/agents/detect-intent', {
      method: 'POST',
      body: JSON.stringify(request),
    }, token);

    if (response.status === 'success' && response.data) {
      return response.data;
    } else {
      throw new Error(response.error || 'Error al detectar intención');
    }
  }

  /**
   * Genera Business Model Canvas usando agente especializado
   */
  async generateBMC(
    request: BMCGenerationRequest,
    token: string
  ): Promise<BMCResult> {
    const response = await apiRequest('/api/agents/generate-bmc', {
      method: 'POST',
      body: JSON.stringify(request),
    }, token);

    if (response.status === 'success' && response.data) {
      return response.data;
    } else {
      throw new Error(response.error || 'Error al generar BMC');
    }
  }

  /**
   * Genera plan de negocio usando agente especializado
   */
  async generateBusinessPlan(
    request: BusinessPlanRequest,
    token: string
  ): Promise<Record<string, any>> {
    const response = await apiRequest('/api/agents/generate-business-plan', {
      method: 'POST',
      body: JSON.stringify(request),
    }, token);

    if (response.status === 'success' && response.data) {
      return response.data;
    } else {
      throw new Error(response.error || 'Error al generar plan de negocio');
    }
  }

  /**
   * Genera plan de marketing usando agente especializado
   */
  async generateMarketingPlan(
    request: MarketingPlanRequest,
    token: string
  ): Promise<Record<string, any>> {
    const response = await apiRequest('/api/agents/generate-marketing-plan', {
      method: 'POST',
      body: JSON.stringify(request),
    }, token);

    if (response.status === 'success' && response.data) {
      return response.data;
    } else {
      throw new Error(response.error || 'Error al generar plan de marketing');
    }
  }

  /**
   * Analiza proyecto usando agente especializado
   */
  async analyzeProject(
    request: ProjectAnalysisRequest,
    token: string
  ): Promise<Record<string, any>> {
    const response = await apiRequest('/api/agents/analyze-project', {
      method: 'POST',
      body: JSON.stringify(request),
    }, token);

    if (response.status === 'success' && response.data) {
      return response.data;
    } else {
      throw new Error(response.error || 'Error al analizar proyecto');
    }
  }
}

export const agentsService = new AgentsService();
export default agentsService;

