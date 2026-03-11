import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Chip,
  Button,
  IconButton,
  Collapse,
  Alert,
  CircularProgress,
  Badge,
  Tooltip
} from '@mui/material';
import {
  Lightbulb as LightbulbIcon,
  Notifications as NotificationsIcon,
  Close as CloseIcon,
  CheckCircle as CheckCircleIcon,
  Warning as WarningIcon,
  TrendingUp as TrendingUpIcon,
  Schedule as ScheduleIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { ProactiveSuggestionService, type ProactiveSuggestion } from '../services/proactiveSuggestionService';

interface ProactiveSuggestionsProps {
  maxSuggestions?: number;
  showBadge?: boolean;
  onSuggestionAction?: (suggestion: ProactiveSuggestion) => void;
}

const ProactiveSuggestions: React.FC<ProactiveSuggestionsProps> = ({
  maxSuggestions = 5,
  showBadge = true,
  onSuggestionAction
}) => {
  const navigate = useNavigate();
  const [suggestions, setSuggestions] = useState<ProactiveSuggestion[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expanded, setExpanded] = useState(false);

  useEffect(() => {
    loadSuggestions();
  }, []);

  const loadSuggestions = async () => {
    try {
      setLoading(true);
      const data = await ProactiveSuggestionService.getDashboardSuggestions();
      setSuggestions(data.slice(0, maxSuggestions));
      setError(null);
    } catch (err: any) {
      setError('Error al cargar las sugerencias');
      console.error('Error loading suggestions:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleMarkAsRead = async (suggestion: ProactiveSuggestion) => {
    try {
      await ProactiveSuggestionService.markAsRead(suggestion.id);
      setSuggestions(prev => prev.map(s => 
        s.id === suggestion.id ? { ...s, is_read: true } : s
      ));
    } catch (err) {
      console.error('Error marking suggestion as read:', err);
    }
  };

  const handleDismiss = async (suggestion: ProactiveSuggestion) => {
    try {
      await ProactiveSuggestionService.dismissSuggestion(suggestion.id);
      setSuggestions(prev => prev.filter(s => s.id !== suggestion.id));
    } catch (err) {
      console.error('Error dismissing suggestion:', err);
    }
  };

  const handleAction = (suggestion: ProactiveSuggestion) => {
    if (onSuggestionAction) {
      onSuggestionAction(suggestion);
    } else if (suggestion.action_url) {
      navigate(suggestion.action_url);
    }
    handleMarkAsRead(suggestion);
  };

  const getSuggestionIcon = (type: string) => {
    switch (type) {
      case 'recommendation':
        return <LightbulbIcon color="primary" />;
      case 'reminder':
        return <ScheduleIcon color="warning" />;
      case 'alert':
        return <WarningIcon color="error" />;
      case 'opportunity':
        return <TrendingUpIcon color="success" />;
      default:
        return <NotificationsIcon color="info" />;
    }
  };

  const getPriorityColor = (priority: number) => {
    if (priority >= 8) return 'error';
    if (priority >= 6) return 'warning';
    return 'default';
  };

  const getSuggestionTypeLabel = (type: string) => {
    switch (type) {
      case 'recommendation':
        return 'Recomendación';
      case 'reminder':
        return 'Recordatorio';
      case 'alert':
        return 'Alerta';
      case 'opportunity':
        return 'Oportunidad';
      default:
        return 'Sugerencia';
    }
  };

  const getCategoryLabel = (category?: string) => {
    switch (category) {
      case 'bmc':
        return 'BMC';
      case 'activity':
        return 'Actividades';
      case 'project':
        return 'Proyecto';
      case 'learning':
        return 'Aprendizaje';
      case 'weekly_review':
        return 'Revisión Semanal';
      default:
        return category || 'General';
    }
  };

  if (loading) {
    return (
      <Card>
        <CardContent>
          <Box display="flex" justifyContent="center" alignItems="center" minHeight={100}>
            <CircularProgress />
          </Box>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <CardContent>
          <Alert severity="error">{error}</Alert>
        </CardContent>
      </Card>
    );
  }

  if (suggestions.length === 0) {
    return null;
  }

  const unreadCount = suggestions.filter(s => !s.is_read).length;

  return (
    <Card>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Box display="flex" alignItems="center" gap={1}>
            {showBadge && unreadCount > 0 ? (
              <Badge badgeContent={unreadCount} color="primary">
                <LightbulbIcon color="primary" />
              </Badge>
            ) : (
              <LightbulbIcon color="primary" />
            )}
            <Typography variant="h6" component="h2">
              Sugerencias Inteligentes
            </Typography>
          </Box>
          <Box display="flex" gap={1}>
            <IconButton
              size="small"
              onClick={() => setExpanded(!expanded)}
            >
              {expanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
            </IconButton>
          </Box>
        </Box>

        <Collapse in={expanded || suggestions.length <= 2}>
          <Box display="flex" flexDirection="column" gap={2}>
            {suggestions.map((suggestion) => (
              <Box
                key={suggestion.id}
                sx={{
                  p: 2,
                  border: 1,
                  borderColor: suggestion.is_read ? 'grey.300' : 'primary.main',
                  borderRadius: 1,
                  backgroundColor: suggestion.is_read ? 'grey.50' : 'background.paper',
                  opacity: suggestion.is_read ? 0.7 : 1,
                  transition: 'all 0.2s ease-in-out',
                  '&:hover': {
                    backgroundColor: 'grey.50',
                    transform: 'translateY(-1px)',
                    boxShadow: 1
                  }
                }}
              >
                <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={1}>
                  <Box display="flex" alignItems="center" gap={1}>
                    {getSuggestionIcon(suggestion.suggestion_type)}
                    <Typography variant="subtitle2" fontWeight="bold">
                      {suggestion.title}
                    </Typography>
                  </Box>
                  <Box display="flex" gap={0.5}>
                    <Chip
                      label={getSuggestionTypeLabel(suggestion.suggestion_type)}
                      size="small"
                      color={getPriorityColor(suggestion.priority)}
                      variant="outlined"
                    />
                    {suggestion.category && (
                      <Chip
                        label={getCategoryLabel(suggestion.category)}
                        size="small"
                        variant="outlined"
                      />
                    )}
                  </Box>
                </Box>

                <Typography variant="body2" color="text.secondary" mb={2}>
                  {suggestion.description}
                </Typography>

                <Box display="flex" justifyContent="space-between" alignItems="center">
                  <Box display="flex" gap={1}>
                    {suggestion.action_url && suggestion.action_text && (
                      <Button
                        size="small"
                        variant="contained"
                        onClick={() => handleAction(suggestion)}
                        startIcon={<CheckCircleIcon />}
                      >
                        {suggestion.action_text}
                      </Button>
                    )}
                  </Box>
                  <Box display="flex" gap={0.5}>
                    {!suggestion.is_read && (
                      <Tooltip title="Marcar como leída">
                        <IconButton
                          size="small"
                          onClick={() => handleMarkAsRead(suggestion)}
                        >
                          <CheckCircleIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                    )}
                    <Tooltip title="Descartar">
                      <IconButton
                        size="small"
                        onClick={() => handleDismiss(suggestion)}
                      >
                        <CloseIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                  </Box>
                </Box>
              </Box>
            ))}
          </Box>
        </Collapse>

        {suggestions.length > 2 && !expanded && (
          <Box mt={2} textAlign="center">
            <Button
              size="small"
              onClick={() => setExpanded(true)}
              startIcon={<ExpandMoreIcon />}
            >
              Ver {suggestions.length - 2} más
            </Button>
          </Box>
        )}
      </CardContent>
    </Card>
  );
};

export default ProactiveSuggestions;

