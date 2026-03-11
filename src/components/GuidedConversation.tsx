import React, { useState, useEffect } from 'react';
import { 
  Box, Typography, Button, TextField, Alert, Card, CardContent, 
  Avatar, Fade, LinearProgress, Backdrop, CircularProgress, 
  IconButton
} from '@mui/material';
import { 
  Business, Send, Cancel, Refresh, Rocket, Check
} from '@mui/icons-material';
import { guidedConversationService } from '../services/guidedConversationService';

interface GuidedConversationProps {
  onComplete: (projectId: string) => void;
  onCancel: () => void;
  token: string;
}

interface ConversationMessage {
  id: string;
  text: string;
  sender: 'user' | 'ai';
  timestamp: Date;
  type: 'text' | 'question' | 'suggestion' | 'confirmation';
  data?: any;
}

const GuidedConversation: React.FC<GuidedConversationProps> = ({ 
  onComplete, 
  onCancel, 
  token 
}) => {
  const [messages, setMessages] = useState<ConversationMessage[]>([]);
  const [currentInput, setCurrentInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [conversationContext, setConversationContext] = useState<any>({});
  const [currentPhase, setCurrentPhase] = useState<'introduction' | 'discovery' | 'planning' | 'generation'>('introduction');
  const [showProgress, setShowProgress] = useState(false);
  const [progressValue, setProgressValue] = useState(0);

  // Mensajes iniciales para crear una conversación natural
  useEffect(() => {
    const initialMessages: ConversationMessage[] = [
      {
        id: '1',
        text: "¡Hola! 👋 Soy tu asistente de Business Model Canvas. Me encantaría ayudarte a desarrollar tu idea de negocio de manera más personalizada.",
        sender: 'ai',
        timestamp: new Date(),
        type: 'text'
      },
      {
        id: '2',
        text: "En lugar de hacerte preguntas formales, ¿te parece si conversamos un poco sobre tu idea? Cuéntame qué tienes en mente y juntos vamos a explorar las posibilidades.",
        sender: 'ai',
        timestamp: new Date(),
        type: 'text'
      }
    ];
    setMessages(initialMessages);
  }, []);

  const handleSendMessage = async () => {
    if (!currentInput.trim() || isLoading) return;

    const userMessage: ConversationMessage = {
      id: Date.now().toString(),
      text: currentInput,
      sender: 'user',
      timestamp: new Date(),
      type: 'text'
    };

    setMessages(prev => [...prev, userMessage]);
    setCurrentInput('');
    setIsLoading(true);
    setError('');

    try {
      // Simular respuesta conversacional basada en el contexto
      const aiResponse = await generateConversationalResponse(currentInput, conversationContext);
      
      const aiMessage: ConversationMessage = {
        id: (Date.now() + 1).toString(),
        text: aiResponse.text,
        sender: 'ai',
        timestamp: new Date(),
        type: aiResponse.type,
        data: aiResponse.data
      };

      setMessages(prev => [...prev, aiMessage]);
      setConversationContext((prev: any) => ({ ...prev, ...aiResponse.context }));

      // Determinar si debemos pasar a la siguiente fase
      if (aiResponse.shouldAdvancePhase && aiResponse.nextPhase) {
        setCurrentPhase(aiResponse.nextPhase as 'introduction' | 'discovery' | 'planning' | 'generation');
      }

    } catch (error) {
      setError('Error en la conversación. Por favor, intenta de nuevo.');
    } finally {
      setIsLoading(false);
    }
  };

  const generateConversationalResponse = async (userInput: string, context: any) => {
    // Análisis simple del input del usuario para generar respuestas contextuales
    const input = userInput.toLowerCase();
    
    // Detectar fase de la conversación
    if (currentPhase === 'introduction') {
      if (input.includes('idea') || input.includes('negocio') || input.includes('proyecto')) {
        return {
          text: "¡Perfecto! 🚀 Me encanta que tengas una idea clara. Cuéntame más sobre tu proyecto. ¿Qué problema estás resolviendo o qué necesidad quieres satisfacer?",
          type: 'question' as const,
          context: { hasIdea: true },
          shouldAdvancePhase: true,
          nextPhase: 'discovery',
          data: null
        };
      }
      return {
        text: "No te preocupes si no tienes todo claro aún. ¿Hay algún sector o tipo de negocio que te interese? O tal vez algo que hayas notado que falta en el mercado...",
        type: 'suggestion' as const,
        context: {},
        shouldAdvancePhase: false,
        data: null
      };
    }

    if (currentPhase === 'discovery') {
      // Extraer información clave del input
      const extractedInfo = extractBusinessInfo(userInput);
      
      if (extractedInfo.industry) {
        return {
          text: `¡Interesante! ${getIndustryResponse(extractedInfo.industry)} Ahora cuéntame, ¿quiénes serían tus clientes ideales? ¿Qué tipo de personas o empresas se beneficiarían más de tu solución?`,
          type: 'question' as const,
          context: { ...context, ...extractedInfo },
          shouldAdvancePhase: true,
          nextPhase: 'planning',
          data: null
        };
      }
      
      return {
        text: "Entiendo. Para ayudarte mejor, ¿podrías contarme en qué sector o industria te gustaría trabajar? Por ejemplo: tecnología, salud, educación, servicios, etc.",
        type: 'question' as const,
        context: context,
        shouldAdvancePhase: false,
        data: null
      };
    }

    if (currentPhase === 'planning') {
      const customerInfo = extractCustomerInfo(userInput);
      
      if (customerInfo.customers) {
        return {
          text: `Excelente elección de clientes! 👥 Ahora, ¿tienes alguna idea de cómo llegarías a ellos? ¿Qué canales usarías para darte a conocer?`,
          type: 'question' as const,
          context: { ...context, ...customerInfo },
          shouldAdvancePhase: false,
          data: null
        };
      }
      
      return {
        text: "Entiendo. ¿Podrías describir un poco más a tus clientes ideales? Por ejemplo: su edad, ubicación, necesidades específicas, etc.",
        type: 'question' as const,
        context: context,
        shouldAdvancePhase: false,
        data: null
      };
    }

    // Fase de generación
    return {
      text: "¡Perfecto! 🎉 Con toda esta información, estoy listo para generar tu Business Model Canvas. ¿Quieres que proceda a crear el plan completo con actividades recomendadas?",
      type: 'confirmation' as const,
      context: { ...context, readyToGenerate: true },
      shouldAdvancePhase: true,
      nextPhase: 'generation',
      data: null
    };
  };

  const extractBusinessInfo = (input: string) => {
    const info: any = {};
    
    // Detectar industria/sector
    if (input.includes('tech') || input.includes('tecnología') || input.includes('app') || input.includes('software')) {
      info.industry = 'tecnología';
    } else if (input.includes('salud') || input.includes('health') || input.includes('médico') || input.includes('fitness')) {
      info.industry = 'salud';
    } else if (input.includes('educación') || input.includes('education') || input.includes('curso') || input.includes('aprendizaje')) {
      info.industry = 'educación';
    } else if (input.includes('servicio') || input.includes('consultoría') || input.includes('asesoría')) {
      info.industry = 'servicios';
    }
    
    return info;
  };

  const extractCustomerInfo = (input: string) => {
    const info: any = {};
    
    if (input.includes('empresa') || input.includes('b2b') || input.includes('corporativo')) {
      info.customers = 'empresas';
    } else if (input.includes('consumidor') || input.includes('persona') || input.includes('individual')) {
      info.customers = 'consumidores';
    }
    
    return info;
  };

  const getIndustryResponse = (industry: string) => {
    const responses = {
      'tecnología': 'El sector tecnológico está en constante evolución. 💻',
      'salud': 'La salud es un sector muy importante y en crecimiento. 🏥',
      'educación': 'La educación es fundamental para el desarrollo. 📚',
      'servicios': 'Los servicios son la base de muchas economías. 🛠️'
    };
    return responses[industry as keyof typeof responses] || '¡Interesante sector!';
  };

  const handleGeneratePlan = async () => {
    setShowProgress(true);
    setProgressValue(0);
    
    try {
      // Simular progreso
      const progressInterval = setInterval(() => {
        setProgressValue(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return 90;
          }
          return prev + 10;
        });
      }, 500);

      // Generar el plan de negocio
      const response = await guidedConversationService.generateBusinessPlan(
        conversationContext,
        token
      );

      clearInterval(progressInterval);
      setProgressValue(100);

      // Mostrar resultado
      const resultMessage: ConversationMessage = {
        id: Date.now().toString(),
        text: "¡Excelente! 🎉 He generado tu Business Model Canvas completo con actividades recomendadas. ¿Te gustaría ver el resultado o prefieres que lo guarde directamente en un nuevo proyecto?",
        sender: 'ai',
        timestamp: new Date(),
        type: 'confirmation',
        data: response
      };

      setMessages(prev => [...prev, resultMessage]);

    } catch (error) {
      setError('Error al generar el plan. Por favor, intenta de nuevo.');
    } finally {
      setShowProgress(false);
      setProgressValue(0);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <Box sx={{ 
      maxWidth: 800, 
      mx: 'auto', 
      p: 3, 
      bgcolor: 'background.paper',
      borderRadius: 2,
      boxShadow: 3
    }}>
      {/* Header con progreso */}
      <Fade in={true}>
        <Box sx={{ 
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          color: 'white',
          p: 3,
          borderRadius: 2,
          mb: 3,
          display: 'flex',
          alignItems: 'center',
          gap: 2
        }}>
          <Avatar sx={{ bgcolor: 'rgba(255,255,255,0.2)' }}>
            <Business />
          </Avatar>
          <Box>
            <Typography variant="h5" fontWeight="bold">
              Conversación Guiada
            </Typography>
            <Typography variant="body2" sx={{ opacity: 0.9 }}>
              Vamos a explorar tu idea de negocio juntos
            </Typography>
          </Box>
        </Box>
      </Fade>

      {/* Barra de progreso */}
      <LinearProgress 
        variant="determinate" 
        value={progressValue} 
        sx={{ mb: 2, height: 8, borderRadius: 4 }}
      />

      {/* Mensajes de la conversación */}
      <Box sx={{ 
        height: 400, 
        overflowY: 'auto', 
        mb: 3,
        p: 2,
        bgcolor: 'grey.50',
        borderRadius: 2,
        border: '1px solid',
        borderColor: 'grey.200'
      }}>
        {messages.map((message) => (
          <Fade key={message.id} in={true}>
            <Box sx={{ 
              mb: 2,
              display: 'flex',
              justifyContent: message.sender === 'user' ? 'flex-end' : 'flex-start'
            }}>
              <Card sx={{ 
                maxWidth: '80%',
                bgcolor: message.sender === 'user' ? 'primary.main' : 'white',
                color: message.sender === 'user' ? 'white' : 'text.primary',
                boxShadow: 2
              }}>
                <CardContent sx={{ p: 2 }}>
                  <Typography variant="body1">
                    {message.text}
                  </Typography>
                  {message.type === 'confirmation' && message.data && (
                    <Box sx={{ mt: 2 }}>
                      <Button 
                        variant="contained" 
                        color="secondary"
                        onClick={handleGeneratePlan}
                        startIcon={<Rocket />}
                        sx={{ mr: 1 }}
                      >
                        Generar Plan Completo
                      </Button>
                      <Button 
                        variant="outlined"
                        onClick={() => onComplete('new-project')}
                        startIcon={<Check />}
                      >
                        Crear Proyecto
                      </Button>
                    </Box>
                  )}
                </CardContent>
              </Card>
            </Box>
          </Fade>
        ))}
        
        {isLoading && (
          <Fade in={true}>
            <Box sx={{ display: 'flex', justifyContent: 'flex-start', mb: 2 }}>
              <Card sx={{ bgcolor: 'grey.100' }}>
                <CardContent sx={{ p: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
                  <CircularProgress size={20} />
                  <Typography variant="body2" color="text.secondary">
                    Pensando...
                  </Typography>
                </CardContent>
              </Card>
            </Box>
          </Fade>
        )}
      </Box>

      {/* Input de mensaje */}
      <Box sx={{ display: 'flex', gap: 1 }}>
        <TextField
          fullWidth
          multiline
          maxRows={3}
          value={currentInput}
          onChange={(e) => setCurrentInput(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Escribe tu mensaje aquí..."
          variant="outlined"
          disabled={isLoading}
          sx={{
            '& .MuiOutlinedInput-root': {
              borderRadius: 3,
              '&:hover fieldset': {
                borderColor: 'primary.main',
              },
            },
          }}
        />
        <IconButton
          onClick={handleSendMessage}
          disabled={!currentInput.trim() || isLoading}
          color="primary"
          sx={{ 
            bgcolor: 'primary.main',
            color: 'white',
            '&:hover': {
              bgcolor: 'primary.dark',
            },
            '&:disabled': {
              bgcolor: 'grey.300',
            }
          }}
        >
          <Send />
        </IconButton>
      </Box>

      {/* Botones de acción */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 3 }}>
        <Button
          variant="outlined"
          onClick={onCancel}
          startIcon={<Cancel />}
          color="error"
        >
          Cancelar
        </Button>
        
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button
            variant="outlined"
            onClick={() => window.location.reload()}
            startIcon={<Refresh />}
          >
            Reiniciar
          </Button>
        </Box>
      </Box>

      {/* Backdrop para progreso */}
      <Backdrop
        sx={{ color: '#fff', zIndex: (theme) => theme.zIndex.drawer + 1 }}
        open={showProgress}
      >
        <Box sx={{ textAlign: 'center' }}>
          <CircularProgress color="inherit" sx={{ mb: 2 }} />
          <Typography variant="h6" sx={{ mb: 1 }}>
            Generando tu Business Model Canvas...
          </Typography>
          <LinearProgress 
            variant="determinate" 
            value={progressValue} 
            sx={{ width: 300, height: 8, borderRadius: 4 }}
          />
          <Typography variant="body2" sx={{ mt: 1 }}>
            {progressValue}% completado
          </Typography>
        </Box>
      </Backdrop>

      {/* Error */}
      {error && (
        <Alert severity="error" sx={{ mt: 2 }}>
          {error}
        </Alert>
      )}
    </Box>
  );
};

export default GuidedConversation;
