import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Chip,
  LinearProgress,
  Button,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  Alert,
  CircularProgress,
  IconButton,
  Tooltip
} from '@mui/material';
import {
  Analytics,
  TrendingUp,
  TrendingDown,
  CheckCircle,
  Warning,
  Lightbulb,
  School,
  Business,
  Psychology,
  Refresh,
  Visibility,
  CheckCircleOutline
} from '@mui/icons-material';
import { DataAnalysisService } from '../services/dataAnalysisService';
import type { DashboardData, RecommendationEngine } from '../types/dataAnalysis';

const AnalyticsDashboard: React.FC = () => {
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await DataAnalysisService.getDashboardData();
      setDashboardData(data);
    } catch (err) {
      setError('Error al cargar los datos del dashboard');
      console.error('Error fetching dashboard data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const handleMarkRecommendationRead = async (recommendationId: number) => {
    try {
      await DataAnalysisService.markRecommendationRead(recommendationId);
      // Actualizar el estado local
      if (dashboardData) {
        setDashboardData({
          ...dashboardData,
          top_recommendations: (dashboardData.top_recommendations || []).map(rec =>
            rec.id === recommendationId ? { ...rec, is_read: true } : rec
          )
        });
      }
    } catch (err) {
      console.error('Error marking recommendation as read:', err);
    }
  };

  const handleMarkRecommendationApplied = async (recommendationId: number) => {
    try {
      await DataAnalysisService.markRecommendationApplied(recommendationId);
      // Actualizar el estado local
      if (dashboardData) {
        setDashboardData({
          ...dashboardData,
          top_recommendations: (dashboardData.top_recommendations || []).map(rec =>
            rec.id === recommendationId ? { ...rec, is_applied: true } : rec
          )
        });
      }
    } catch (err) {
      console.error('Error marking recommendation as applied:', err);
    }
  };

  const getPriorityColor = (priority: number) => {
    switch (priority) {
      case 1: return 'error';
      case 2: return 'warning';
      case 3: return 'info';
      case 4: return 'success';
      case 5: return 'default';
      default: return 'default';
    }
  };

  const getMetricIcon = (metric: string, value: number) => {
    if (value >= 70) return <TrendingUp color="success" />;
    if (value >= 40) return <TrendingUp color="warning" />;
    return <TrendingDown color="error" />;
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" action={
        <Button color="inherit" size="small" onClick={fetchDashboardData}>
          Reintentar
        </Button>
      }>
        {error}
      </Alert>
    );
  }

  if (!dashboardData) {
    return <Alert severity="info">No hay datos disponibles</Alert>;
  }

  const { analytics, insights, learning_progress, top_recommendations } = dashboardData;

  return (
    <Box sx={{ 
      p: { xs: 2, sm: 3, md: 4 },
      maxWidth: '100%',
      overflow: 'hidden'
    }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3} flexWrap="wrap" gap={2}>
        <Typography variant="h4" component="h1" display="flex" alignItems="center" gap={1}>
          <Analytics color="primary" />
          Dashboard de Análisis
        </Typography>
        <Button
          variant="outlined"
          startIcon={<Refresh />}
          onClick={fetchDashboardData}
          disabled={loading}
        >
          Actualizar
        </Button>
      </Box>

      <Grid container spacing={{ xs: 2, sm: 3 }} sx={{ maxWidth: '100%' }}>
        {/* Métricas Principales */}
        <Grid size={{ xs: 12, md: 6, lg: 3 }}>
          <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
            <CardContent sx={{ flexGrow: 1 }}>
              <Typography color="textSecondary" gutterBottom variant="subtitle2">
                Finalización de Proyectos
              </Typography>
              <Box display="flex" alignItems="center" gap={1} mb={1}>
                {getMetricIcon('project_completion', analytics.project_completion_rate)}
                <Typography variant="h4" component="div">
                  {(analytics.project_completion_rate || 0).toFixed(1)}%
                </Typography>
              </Box>
              <LinearProgress
                variant="determinate"
                value={analytics.project_completion_rate || 0}
                sx={{ height: 8, borderRadius: 4 }}
              />
            </CardContent>
          </Card>
        </Grid>

        <Grid size={{ xs: 12, md: 6, lg: 3 }}>
          <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
            <CardContent sx={{ flexGrow: 1 }}>
              <Typography color="textSecondary" gutterBottom variant="subtitle2">
                Finalización de Actividades
              </Typography>
              <Box display="flex" alignItems="center" gap={1} mb={1}>
                {getMetricIcon('activity_completion', analytics.activity_completion_rate)}
                <Typography variant="h4" component="div">
                  {(analytics.activity_completion_rate || 0).toFixed(1)}%
                </Typography>
              </Box>
              <LinearProgress
                variant="determinate"
                value={analytics.activity_completion_rate || 0}
                sx={{ height: 8, borderRadius: 4 }}
              />
            </CardContent>
          </Card>
        </Grid>

        <Grid size={{ xs: 12, md: 6, lg: 3 }}>
          <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
            <CardContent sx={{ flexGrow: 1 }}>
              <Typography color="textSecondary" gutterBottom variant="subtitle2">
                Consumo de Contenido
              </Typography>
              <Box display="flex" alignItems="center" gap={1} mb={1}>
                {getMetricIcon('content_consumption', (analytics.content_consumption_rate || 0) * 10)}
                <Typography variant="h4" component="div">
                  {(analytics.content_consumption_rate || 0).toFixed(1)}
                </Typography>
              </Box>
              <Typography variant="body2" color="textSecondary">
                por semana
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid size={{ xs: 12, md: 6, lg: 3 }}>
          <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
            <CardContent sx={{ flexGrow: 1 }}>
              <Typography color="textSecondary" gutterBottom variant="subtitle2">
                Complejidad BMC
              </Typography>
              <Box display="flex" alignItems="center" gap={1} mb={1}>
                {getMetricIcon('bmc_complexity', (analytics.business_model_complexity || 0) * 100)}
                <Typography variant="h4" component="div">
                  {((analytics.business_model_complexity || 0) * 100).toFixed(1)}%
                </Typography>
              </Box>
              <LinearProgress
                variant="determinate"
                value={(analytics.business_model_complexity || 0) * 100}
                sx={{ height: 8, borderRadius: 4 }}
              />
            </CardContent>
          </Card>
        </Grid>

        {/* Insights y Fortalezas */}
        <Grid size={{ xs: 12, md: 6 }}>
          <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
            <CardContent sx={{ flexGrow: 1 }}>
              <Typography variant="h6" gutterBottom display="flex" alignItems="center" gap={1}>
                <Lightbulb color="primary" />
                Fortalezas
              </Typography>
              <Box display="flex" flexWrap="wrap" gap={1}>
                {(insights.strengths || []).map((strength, index) => (
                  <Chip
                    key={index}
                    label={strength}
                    color="success"
                    variant="outlined"
                    icon={<CheckCircle />}
                    size="small"
                  />
                ))}
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid size={{ xs: 12, md: 6 }}>
          <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
            <CardContent sx={{ flexGrow: 1 }}>
              <Typography variant="h6" gutterBottom display="flex" alignItems="center" gap={1}>
                <Warning color="warning" />
                Áreas de Mejora
              </Typography>
              <Box display="flex" flexWrap="wrap" gap={1}>
                {(insights.improvement_areas || []).map((area, index) => (
                  <Chip
                    key={index}
                    label={area}
                    color="warning"
                    variant="outlined"
                    icon={<Warning />}
                    size="small"
                  />
                ))}
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Progreso de Aprendizaje */}
        <Grid size={{ xs: 12, md: 6 }}>
          <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
            <CardContent sx={{ flexGrow: 1 }}>
              <Typography variant="h6" gutterBottom display="flex" alignItems="center" gap={1}>
                <School color="primary" />
                Progreso de Aprendizaje
              </Typography>
              <Typography variant="h4" component="div" gutterBottom>
                {(learning_progress.overall_progress || 0).toFixed(1)}%
              </Typography>
              <LinearProgress
                variant="determinate"
                value={learning_progress.overall_progress || 0}
                sx={{ mb: 2, height: 8, borderRadius: 4 }}
              />
              <Typography variant="body2" color="textSecondary" gutterBottom>
                Próximas recomendaciones:
              </Typography>
              <List dense>
                {(learning_progress.next_recommendations || []).map((rec, index) => (
                  <ListItem key={index} sx={{ py: 0.5 }}>
                    <ListItemIcon sx={{ minWidth: 30 }}>
                      <CheckCircleOutline fontSize="small" />
                    </ListItemIcon>
                    <ListItemText primary={rec} />
                  </ListItem>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>

        {/* Recomendaciones */}
        <Grid size={{ xs: 12, md: 6 }}>
          <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
            <CardContent sx={{ flexGrow: 1, overflow: 'auto' }}>
              <Typography variant="h6" gutterBottom display="flex" alignItems="center" gap={1}>
                <Psychology color="primary" />
                Recomendaciones Inteligentes
              </Typography>
              <List sx={{ maxHeight: 400, overflow: 'auto' }}>
                {(top_recommendations || []).map((recommendation) => (
                  <React.Fragment key={recommendation.id}>
                    <ListItem
                      sx={{
                        backgroundColor: recommendation.is_read ? 'action.hover' : 'background.paper',
                        borderRadius: 1,
                        mb: 1,
                        border: '1px solid',
                        borderColor: 'divider',
                        opacity: recommendation.is_read ? 0.7 : 1,
                        flexDirection: 'column',
                        alignItems: 'flex-start',
                        py: 2
                      }}
                    >
                      <Box display="flex" alignItems="center" gap={1} width="100%" mb={1}>
                        <Chip
                          label={`P${recommendation.priority}`}
                          color={getPriorityColor(recommendation.priority) as any}
                          size="small"
                        />
                        <Typography variant="subtitle1" sx={{ flexGrow: 1 }}>
                          {recommendation.title}
                        </Typography>
                        <Box display="flex" gap={1}>
                          {!recommendation.is_read && (
                            <Tooltip title="Marcar como leída">
                              <IconButton
                                size="small"
                                onClick={() => handleMarkRecommendationRead(recommendation.id)}
                              >
                                <Visibility />
                              </IconButton>
                            </Tooltip>
                          )}
                          {!recommendation.is_applied && (
                            <Tooltip title="Marcar como aplicada">
                              <IconButton
                                size="small"
                                onClick={() => handleMarkRecommendationApplied(recommendation.id)}
                              >
                                <CheckCircle />
                              </IconButton>
                            </Tooltip>
                          )}
                        </Box>
                      </Box>
                      <Typography variant="body2" color="textSecondary" sx={{ mb: 1 }}>
                        {recommendation.description}
                      </Typography>
                      <Box display="flex" gap={1} flexWrap="wrap">
                        <Chip
                          label={recommendation.recommendation_type}
                          size="small"
                          variant="outlined"
                        />
                        <Chip
                          label={`${((recommendation.confidence_score || 0) * 100).toFixed(0)}% confianza`}
                          size="small"
                          variant="outlined"
                        />
                      </Box>
                    </ListItem>
                    <Divider />
                  </React.Fragment>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default AnalyticsDashboard;

