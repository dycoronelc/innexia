import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  LinearProgress,
  FormControl,
  FormLabel,
  RadioGroup,
  FormControlLabel,
  Radio,
  Checkbox,
  FormGroup,
  Chip,
  Alert,
  Stepper,
  Step,
  StepLabel,
  Card,
  CardContent,
  Divider,
  CircularProgress
} from '@mui/material';
import {
  Business as BusinessIcon,
  Assessment as AssessmentIcon,
  CheckCircle as CheckCircleIcon,
  ArrowForward as ArrowForwardIcon,
  ArrowBack as ArrowBackIcon
} from '@mui/icons-material';

interface InterviewQuestion {
  id: string;
  question: string;
  field: string;
  type: string;
  options?: string[];
  required: boolean;
}

interface InterviewProgress {
  current_question?: InterviewQuestion;
  progress_percentage: number;
  completed_fields: string[];
  remaining_fields: string[];
  is_complete: boolean;
}

interface BusinessInterviewProps {
  onComplete: (businessData: any) => void;
  onCancel: () => void;
}

const BusinessInterview: React.FC<BusinessInterviewProps> = ({ onComplete, onCancel }) => {
  const [progress, setProgress] = useState<InterviewProgress | null>(null);
  const [currentAnswer, setCurrentAnswer] = useState<any>('');
  const [answers, setAnswers] = useState<Record<string, any>>({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeStep, setActiveStep] = useState(0);
  const [sessionId, setSessionId] = useState<string | null>(null);

  // Inicializar entrevista
  useEffect(() => {
    startInterview();
  }, []);

  const startInterview = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('innexia_token');
      console.log('Token obtenido:', token ? 'Existe' : 'No existe');
      
      const response = await fetch('http://localhost:8000/api/business-interview/start', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      console.log('Respuesta del servidor:', response.status, response.statusText);
      
      if (response.ok) {
        const data = await response.json();
        console.log('Datos recibidos:', data);
        setProgress(data);
        setSessionId(data.session_id);
        setActiveStep(0);
      } else {
        const errorText = await response.text();
        console.error('Error iniciando entrevista:', response.status, response.statusText, errorText);
        throw new Error(`Error iniciando entrevista: ${response.status} ${response.statusText}`);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error desconocido');
    } finally {
      setLoading(false);
    }
  };

  const answerQuestion = async () => {
    if (!progress?.current_question) return;

    try {
      setLoading(true);
      const response = await fetch('http://localhost:8000/api/business-interview/answer', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('innexia_token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          field: progress.current_question.field,
          value: currentAnswer,
          session_id: sessionId
        })
      });

      if (response.ok) {
        const data = await response.json();
        setProgress(data);
        if (data.session_id) {
          setSessionId(data.session_id);
        }
        
        // Guardar respuesta
        setAnswers(prev => ({
          ...prev,
          [progress.current_question!.field]: currentAnswer
        }));

        // Limpiar respuesta actual
        setCurrentAnswer('');
        setActiveStep(prev => prev + 1);

        // Si la entrevista está completa, proceder
        if (data.is_complete) {
          // Incluir la respuesta actual en los datos antes de completar
          const updatedAnswers = {
            ...answers,
            [progress.current_question!.field]: currentAnswer
          };
          completeInterview(updatedAnswers);
        }
      } else {
        throw new Error('Error respondiendo pregunta');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error desconocido');
    } finally {
      setLoading(false);
    }
  };

  const completeInterview = async (answersToUse?: Record<string, any>) => {
    try {
      setLoading(true);
      const finalAnswers = answersToUse || answers;
      console.log('Intentando completar entrevista con datos:', finalAnswers);
      console.log('Número de respuestas:', Object.keys(finalAnswers).length);
      console.log('Campos respondidos:', Object.keys(finalAnswers));
      
      const response = await fetch('http://localhost:8000/api/business-interview/complete', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('innexia_token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          business_data: finalAnswers,
          project_id: null
        })
      });

      if (response.ok) {
        const data = await response.json();
        onComplete(finalAnswers);
      } else {
        throw new Error('Error completando entrevista');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error desconocido');
    } finally {
      setLoading(false);
    }
  };

  const handleAnswerChange = (value: any) => {
    setCurrentAnswer(value);
  };

  const renderQuestionInput = () => {
    if (!progress?.current_question) return null;

    const question = progress.current_question;

    switch (question.type) {
      case 'multiple_choice':
        return (
          <FormControl component="fieldset">
            <RadioGroup
              value={currentAnswer}
              onChange={(e) => handleAnswerChange(e.target.value)}
            >
              {question.options?.map((option) => (
                <FormControlLabel
                  key={option}
                  value={option}
                  control={<Radio />}
                  label={option}
                />
              ))}
            </RadioGroup>
          </FormControl>
        );

      case 'number':
        return (
          <TextField
            fullWidth
            type="number"
            value={currentAnswer}
            onChange={(e) => handleAnswerChange(parseFloat(e.target.value) || 0)}
            placeholder="Ingresa un número"
            variant="outlined"
          />
        );

      case 'list':
        return (
          <FormGroup>
            {question.options?.map((option) => (
              <FormControlLabel
                key={option}
                control={
                  <Checkbox
                    checked={Array.isArray(currentAnswer) && currentAnswer.includes(option)}
                    onChange={(e) => {
                      const currentList = Array.isArray(currentAnswer) ? currentAnswer : [];
                      if (e.target.checked) {
                        handleAnswerChange([...currentList, option]);
                      } else {
                        handleAnswerChange(currentList.filter(item => item !== option));
                      }
                    }}
                  />
                }
                label={option}
              />
            ))}
          </FormGroup>
        );

      default: // text
        return (
          <TextField
            fullWidth
            multiline
            rows={3}
            value={currentAnswer}
            onChange={(e) => handleAnswerChange(e.target.value)}
            placeholder="Describe tu respuesta aquí..."
            variant="outlined"
          />
        );
    }
  };

  if (loading && !progress) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ mb: 2 }}>
        {error}
      </Alert>
    );
  }

  if (!progress) {
    return null;
  }

  return (
    <Box sx={{ maxWidth: 800, mx: 'auto', p: 2 }}>
      <Paper elevation={3} sx={{ p: 3 }}>
        {/* Header */}
        <Box sx={{ mb: 3, textAlign: 'center' }}>
          <BusinessIcon sx={{ fontSize: 48, color: 'primary.main', mb: 1 }} />
          <Typography variant="h4" component="h1" gutterBottom>
            Entrevista de Negocio
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Te haremos algunas preguntas para entender mejor tu idea de negocio y generar un análisis más preciso.
          </Typography>
        </Box>

        {/* Progress */}
        <Box sx={{ mb: 3 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
            <Typography variant="body2" color="text.secondary">
              Progreso: {Math.round(progress.progress_percentage)}%
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {progress.completed_fields.length} de {progress.completed_fields.length + progress.remaining_fields.length} completadas
            </Typography>
          </Box>
          <LinearProgress 
            variant="determinate" 
            value={progress.progress_percentage} 
            sx={{ height: 8, borderRadius: 4 }}
          />
        </Box>

        {/* Stepper */}
        <Stepper activeStep={activeStep} alternativeLabel sx={{ mb: 3 }}>
          {progress.completed_fields.map((field, index) => (
            <Step key={field} completed>
              <StepLabel>{field.replace('_', ' ').toUpperCase()}</StepLabel>
            </Step>
          ))}
          {progress.current_question && (
            <Step active>
              <StepLabel>{progress.current_question.field.replace('_', ' ').toUpperCase()}</StepLabel>
            </Step>
          )}
        </Stepper>

        {/* Current Question */}
        {progress.current_question && (
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                {progress.current_question.question}
                {progress.current_question.required && (
                  <Chip label="Requerido" size="small" color="primary" sx={{ ml: 1 }} />
                )}
              </Typography>
              
              <Box sx={{ mt: 2 }}>
                {renderQuestionInput()}
              </Box>
            </CardContent>
          </Card>
        )}

        {/* Completed Fields Summary */}
        {progress.completed_fields.length > 0 && (
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                <CheckCircleIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                Información Completada
              </Typography>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                {progress.completed_fields.map((field) => (
                  <Chip
                    key={field}
                    label={field.replace('_', ' ').toUpperCase()}
                    color="success"
                    size="small"
                  />
                ))}
              </Box>
            </CardContent>
          </Card>
        )}

        {/* Actions */}
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 3 }}>
          <Button
            variant="outlined"
            startIcon={<ArrowBackIcon />}
            onClick={onCancel}
            disabled={loading}
          >
            Cancelar
          </Button>
          
          <Button
            variant="contained"
            endIcon={<ArrowForwardIcon />}
            onClick={answerQuestion}
            disabled={loading || !currentAnswer || (Array.isArray(currentAnswer) && currentAnswer.length === 0)}
          >
            {progress.is_complete ? 'Completar Entrevista' : 'Siguiente Pregunta'}
          </Button>
        </Box>

        {loading && (
          <Box sx={{ mt: 2 }}>
            <LinearProgress />
          </Box>
        )}
      </Paper>
    </Box>
  );
};

export default BusinessInterview;
