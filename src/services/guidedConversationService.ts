import { apiRequest } from './api';

export interface GuidedQuestion {
  id: string;
  question: string;
  type: string;
  placeholder: string;
  required: boolean;
  context: string;
}

export interface GuidedConversationRequest {
  business_idea: string;
  answers: Record<string, string>;
}

export interface GuidedConversationResponse {
  project_id: number;
  project_name: string;
  bmc_data: Record<string, any>;
  activities: Array<Record<string, any>>;
  business_plan: string;
}

export const guidedConversationService = {
  /**
   * Obtener las preguntas de la conversación guiada
   */
  async getQuestions(token: string): Promise<{ questions: GuidedQuestion[]; total_questions: number }> {
    try {
      const response = await apiRequest<{ questions: GuidedQuestion[]; total_questions: number }>('/api/guided-conversation/questions', {
        method: 'GET'
      }, token);
      
      if (response.status === 'success' && response.data) {
        return response.data;
      } else {
        throw new Error(response.error || 'Error al cargar las preguntas');
      }
    } catch (error) {
      console.error('Error fetching guided questions:', error);
      throw new Error('Error al cargar las preguntas de la conversación guiada');
    }
  },

  /**
   * Generar plan de negocio basado en conversación guiada
   */
  async generateBusinessPlan(request: GuidedConversationRequest, token: string): Promise<GuidedConversationResponse> {
    try {
      console.log('Enviando solicitud de generación:', request);
      
      const response = await apiRequest<GuidedConversationResponse>('/api/guided-conversation/generate', {
        method: 'POST',
        body: JSON.stringify(request)
      }, token);
      
      console.log('Respuesta de generación:', response);
      
      if (response.status === 'success' && response.data) {
        return response.data;
      } else {
        throw new Error(response.error || 'Error al generar el plan de negocio');
      }
    } catch (error) {
      console.error('Error generating business plan:', error);
      throw new Error('Error al generar el plan de negocio');
    }
  }
};
