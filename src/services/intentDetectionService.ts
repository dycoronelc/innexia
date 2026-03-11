/**
 * Servicio de Detección de Intenciones con IA
 * Utiliza OpenAI para detectar la intención del usuario de manera inteligente
 */

import { apiRequest } from './api';

// Tipos de intenciones disponibles
export type UserIntent = 
  | 'bmc_generation'
  | 'business_plan'
  | 'marketing_plan'
  | 'market_research'
  | 'project_analysis'
  | 'activity_recommendations'
  | 'guided_conversation'
  | 'business_interview'
  | 'complete_project_generation'
  | 'general_conversation';

export interface IntentDetectionResult {
  intent: UserIntent;
  confidence: number; // 0-1
  extractedContext: string;
  suggestedAction: string;
  reasoning?: string;
}

export interface ConversationContext {
  recentMessages: Array<{
    text: string;
    sender: 'user' | 'ai';
    timestamp: string;
  }>;
  currentProject?: {
    id: string;
    name: string;
    description: string;
  };
  userProfile?: {
    role: string;
    preferences: string[];
  };
}

class IntentDetectionService {
  private readonly INTENT_DETECTION_PROMPT = `
Eres un asistente especializado en emprendimiento e innovación que ayuda a detectar la intención de los usuarios.

ANALIZA el mensaje del usuario y determina su INTENCIÓN PRINCIPAL basándote en:

1. **CONTENIDO DEL MENSAJE**: ¿Qué está pidiendo específicamente?
2. **CONTEXTO DE CONVERSACIÓN**: ¿Qué se ha discutido anteriormente?
3. **PALABRAS CLAVE**: Identifica términos técnicos y de negocio
4. **NIVEL DE DETALLE**: ¿Es una solicitud específica o general?

INTENCIONES DISPONIBLES:
- **bmc_generation**: Solicita Business Model Canvas, modelo de negocio, BMC
- **business_plan**: Solicita plan de negocio, business plan, plan empresarial
- **marketing_plan**: Solicita plan de marketing, estrategia de marketing, marketing plan
- **market_research**: Solicita investigación de mercado, análisis de mercado, market research
- **project_analysis**: Solicita análisis de proyecto, estado del proyecto, revisar proyecto
- **activity_recommendations**: Solicita recomendaciones, mejoras, optimización de actividades
- **guided_conversation**: Solicita conversación guiada, preguntas paso a paso, entrevista
- **business_interview**: Solicita entrevista de negocio, cuestionario empresarial
- **complete_project_generation**: Solicita crear proyecto completo, generar proyecto desde cero
- **general_conversation**: Conversación general, preguntas generales, dudas

CONTEXTO DE LA CONVERSACIÓN:
{conversationContext}

MENSAJE DEL USUARIO: "{userMessage}"

INSTRUCCIONES:
1. Analiza el mensaje y contexto cuidadosamente
2. Determina la intención MÁS PROBABLE
3. Extrae información relevante del contexto
4. Proporciona una acción sugerida específica
5. Asigna un nivel de confianza (0-1)

Responde ÚNICAMENTE en formato JSON válido:
{
  "intent": "intención_detectada",
  "confidence": 0.95,
  "extractedContext": "contexto_extraído_del_mensaje_y_conversación",
  "suggestedAction": "acción_específica_sugerida",
  "reasoning": "breve_explicación_del_razonamiento"
}`;

  /**
   * Detecta la intención del usuario usando IA
   */
  async detectIntent(
    userMessage: string,
    conversationContext: ConversationContext,
    token: string
  ): Promise<IntentDetectionResult> {
    try {
      // Construir el contexto de conversación
      const contextString = this.buildConversationContext(conversationContext);
      
      // Crear el prompt completo
      const fullPrompt = this.INTENT_DETECTION_PROMPT
        .replace('{conversationContext}', contextString)
        .replace('{userMessage}', userMessage);

      // Llamar a OpenAI para detectar la intención
      const response = await apiRequest('/api/chatbot/detect-intent', {
        method: 'POST',
        body: JSON.stringify({
          message: userMessage,
          conversation_context: conversationContext,
          prompt: fullPrompt
        }),
      }, token);

      if (response.status === 'success' && response.data) {
        return this.parseIntentResponse(response.data);
      } else {
        throw new Error(response.error || 'Error al detectar intención');
      }
    } catch (error) {
      console.error('Error en detección de intención:', error);
      
      // Fallback: detección básica por palabras clave
      return this.fallbackIntentDetection(userMessage);
    }
  }

  /**
   * Construye el contexto de conversación como string
   */
  private buildConversationContext(context: ConversationContext): string {
    let contextString = '';

    // Agregar mensajes recientes
    if (context.recentMessages && context.recentMessages.length > 0) {
      contextString += 'MENSAGES RECIENTES:\n';
      context.recentMessages.slice(-5).forEach(msg => {
        contextString += `- ${msg.sender}: ${msg.text}\n`;
      });
    }

    // Agregar información del proyecto actual
    if (context.currentProject) {
      contextString += `\nPROYECTO ACTUAL: ${context.currentProject.name}\n`;
      contextString += `Descripción: ${context.currentProject.description}\n`;
    }

    // Agregar perfil del usuario
    if (context.userProfile) {
      contextString += `\nPERFIL USUARIO: ${context.userProfile.role}\n`;
      if (context.userProfile.preferences.length > 0) {
        contextString += `Preferencias: ${context.userProfile.preferences.join(', ')}\n`;
      }
    }

    return contextString || 'Sin contexto previo disponible.';
  }

  /**
   * Parsea la respuesta de OpenAI
   */
  private parseIntentResponse(responseData: any): IntentDetectionResult {
    try {
      // Si la respuesta ya viene parseada
      if (typeof responseData === 'object') {
        return {
          intent: responseData.intent || 'general_conversation',
          confidence: Math.max(0, Math.min(1, responseData.confidence || 0.5)),
          extractedContext: responseData.extractedContext || '',
          suggestedAction: responseData.suggestedAction || '',
          reasoning: responseData.reasoning
        };
      }

      // Si viene como string, intentar parsear JSON
      if (typeof responseData === 'string') {
        const parsed = JSON.parse(responseData);
        return {
          intent: parsed.intent || 'general_conversation',
          confidence: Math.max(0, Math.min(1, parsed.confidence || 0.5)),
          extractedContext: parsed.extractedContext || '',
          suggestedAction: parsed.suggestedAction || '',
          reasoning: parsed.reasoning
        };
      }

      throw new Error('Formato de respuesta inválido');
    } catch (error) {
      console.error('Error parseando respuesta de intención:', error);
      return this.fallbackIntentDetection('');
    }
  }

  /**
   * Detección de fallback usando palabras clave (para casos de error)
   */
  private fallbackIntentDetection(userMessage: string): IntentDetectionResult {
    const lowerMessage = userMessage.toLowerCase();

    // Detectar BMC
    if (lowerMessage.includes('bmc') || 
        lowerMessage.includes('business model canvas') ||
        lowerMessage.includes('modelo de negocio')) {
      return {
        intent: 'bmc_generation',
        confidence: 0.8,
        extractedContext: userMessage,
        suggestedAction: 'Generar Business Model Canvas',
        reasoning: 'Fallback: Detección por palabras clave'
      };
    }

    // Detectar plan de negocio
    if (lowerMessage.includes('plan de negocio') || 
        lowerMessage.includes('business plan')) {
      return {
        intent: 'business_plan',
        confidence: 0.8,
        extractedContext: userMessage,
        suggestedAction: 'Generar plan de negocio',
        reasoning: 'Fallback: Detección por palabras clave'
      };
    }

    // Detectar plan de marketing
    if (lowerMessage.includes('plan de marketing') || 
        lowerMessage.includes('marketing plan')) {
      return {
        intent: 'marketing_plan',
        confidence: 0.8,
        extractedContext: userMessage,
        suggestedAction: 'Generar plan de marketing',
        reasoning: 'Fallback: Detección por palabras clave'
      };
    }

    // Conversación general por defecto
    return {
      intent: 'general_conversation',
      confidence: 0.6,
      extractedContext: userMessage,
      suggestedAction: 'Iniciar conversación general',
      reasoning: 'Fallback: Conversación general por defecto'
    };
  }

  /**
   * Obtiene información detallada sobre una intención
   */
  getIntentInfo(intent: UserIntent): {
    name: string;
    description: string;
    icon: string;
    color: string;
  } {
    const intentInfo = {
      bmc_generation: {
        name: 'Business Model Canvas',
        description: 'Generar un modelo de negocio completo',
        icon: '📊',
        color: '#2196F3'
      },
      business_plan: {
        name: 'Plan de Negocio',
        description: 'Crear un plan de negocio detallado',
        icon: '📋',
        color: '#4CAF50'
      },
      marketing_plan: {
        name: 'Plan de Marketing',
        description: 'Desarrollar estrategia de marketing',
        icon: '📈',
        color: '#FF9800'
      },
      market_research: {
        name: 'Investigación de Mercado',
        description: 'Analizar mercado y competencia',
        icon: '🔍',
        color: '#9C27B0'
      },
      project_analysis: {
        name: 'Análisis de Proyecto',
        description: 'Revisar y analizar proyecto actual',
        icon: '📊',
        color: '#607D8B'
      },
      activity_recommendations: {
        name: 'Recomendaciones',
        description: 'Obtener recomendaciones de mejora',
        icon: '💡',
        color: '#FF5722'
      },
      guided_conversation: {
        name: 'Conversación Guiada',
        description: 'Entrevista paso a paso',
        icon: '🗣️',
        color: '#795548'
      },
      business_interview: {
        name: 'Entrevista de Negocio',
        description: 'Cuestionario empresarial completo',
        icon: '📝',
        color: '#3F51B5'
      },
      complete_project_generation: {
        name: 'Proyecto Completo',
        description: 'Generar proyecto desde cero',
        icon: '🚀',
        color: '#E91E63'
      },
      general_conversation: {
        name: 'Conversación General',
        description: 'Charla general sobre emprendimiento',
        icon: '💬',
        color: '#009688'
      }
    };

    return intentInfo[intent];
  }
}

// Exportar instancia singleton
export const intentDetectionService = new IntentDetectionService();
export default intentDetectionService;
