import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Button,
  Chip,
  Avatar,
  LinearProgress,
  Card,
  CardContent,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton
} from '@mui/material';
import {
  Business,
  Schedule,
  Flag,
  CheckCircle,
  Warning,
  CalendarToday,
  Assignment,
  Speed,
  Timeline,
  Visibility,
  Dashboard as DashboardIcon
} from '@mui/icons-material';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';
import type { Project, ProjectActivity } from '../types';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { projectService, activityService } from '../services/api';
import ProjectCard from '../components/ProjectCard';
import ActivityMetricCard from '../components/ActivityMetricCard';
// import { PWAStatus } from '../components/PWAStatus';

const DashboardPage: React.FC = () => {
  const { token, isAuthenticated } = useAuth();
  const [projects, setProjects] = useState<Project[]>([]);
  const [activities, setActivities] = useState<ProjectActivity[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    if (token && isAuthenticated) {
      fetchDashboardData();
    } else if (!isAuthenticated) {
      setError('Usuario no autenticado. Por favor, inicie sesión.');
      setLoading(false);
    }
  }, [token, isAuthenticated, navigate]);

  // Escuchar eventos de creación de proyectos desde el ChatBot
  useEffect(() => {
    const handleProjectCreated = (event: CustomEvent) => {
      // Proyecto creado detectado en Dashboard
      // Refrescar los datos del dashboard
      fetchDashboardData();
    };

    window.addEventListener('projectCreated', handleProjectCreated as EventListener);
    
    return () => {
      window.removeEventListener('projectCreated', handleProjectCreated as EventListener);
    };
  }, []);

  const fetchDashboardData = async () => {
    if (!token) return;
    
    setLoading(true);
    setError('');
    
    try {
      // Fetch projects and activities in parallel
      const [projectsResponse, activitiesResponse] = await Promise.all([
        projectService.getProjects(token),
        activityService.getActivities(token)
      ]);
      
      // Dashboard data responses recibidas
      
      // Process projects
      if (projectsResponse.status === 'success' && projectsResponse.data) {
        const processedProjects = projectsResponse.data.map((project: any) => ({
          id: project.id.toString(),
          name: project.name,
          description: project.description,
          category: project.category || '',
          tags: project.tags || [],
          location: project.location || '',
          status: project.status,
          createdAt: project.created_at ? new Date(project.created_at) : new Date(),
          updatedAt: project.updated_at ? new Date(project.updated_at) : new Date()
        }));
        setProjects(processedProjects);
      } else {
        console.error('Error in projects response:', projectsResponse.error);
        setError(projectsResponse.error || 'Error al cargar proyectos');
      }
      
      // Process activities
      if (activitiesResponse.status === 'success' && activitiesResponse.data) {
        const processedActivities = activitiesResponse.data.map((activity: any) => ({
          id: activity.id.toString(),
          title: activity.title,
          description: activity.description,
          status: activity.status,
          priority: activity.priority,
          assignee: activity.assignee_name || 'Sin asignar',
          startDate: activity.start_date ? new Date(activity.start_date) : new Date(),
          dueDate: activity.due_date ? new Date(activity.due_date) : new Date(),
          createdAt: activity.created_at ? new Date(activity.created_at) : new Date(),
          updatedAt: activity.updated_at ? new Date(activity.updated_at) : new Date(),
          projectId: activity.project_id?.toString() || '1'
        }));
        setActivities(processedActivities);
      } else {
        console.error('Error in activities response:', activitiesResponse.error);
        setError(activitiesResponse.error || 'Error al cargar actividades');
      }
      
    } catch (error: any) {
      console.error('Error fetching dashboard data:', error);
      
      // Check if it's an authentication error
      if (error.message && error.message.includes('Token inválido')) {
        setError('Sesión expirada. Por favor, inicie sesión nuevamente.');
        // Optionally redirect to login after a few seconds
        setTimeout(() => {
          navigate('/login');
        }, 3000);
      } else {
        setError('Error al cargar datos del dashboard');
      }
    } finally {
      setLoading(false);
    }
  };

  const getActivityStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'success';
      case 'in-progress': return 'primary';
      case 'review': return 'warning';
      case 'todo': return 'default';
      default: return 'default';
    }
  };

  const getActivityStatusText = (status: string) => {
    switch (status) {
      case 'completed': return 'Completada';
      case 'in-progress': return 'En Progreso';
      case 'review': return 'En Revisión';
      case 'todo': return 'Pendiente';
      default: return status;
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'error';
      case 'medium': return 'warning';
      case 'low': return 'success';
      default: return 'default';
    }
  };

  const getPriorityText = (priority: string) => {
    switch (priority) {
      case 'high': return 'Alta';
      case 'medium': return 'Media';
      case 'low': return 'Baja';
      default: return priority;
    }
  };

  // Calculate KPIs
  const totalActivities = activities.length;
  const completedActivities = activities.filter(a => a.status === 'completed').length;
  const inProgressActivities = activities.filter(a => a.status === 'in-progress').length;
  const overdueActivities = activities.filter(a => {
    return a.status !== 'completed' && new Date() > a.dueDate;
  }).length;
  const highPriorityActivities = activities.filter(a => a.priority === 'high').length;
  const completionRate = totalActivities > 0 ? Math.round((completedActivities / totalActivities) * 100) : 0;
  
  // Calculate average completion time
  const completedWithDates = activities.filter(a => a.status === 'completed');
  const avgCompletionTime = completedWithDates.length > 0 
    ? Math.round(completedWithDates.reduce((acc, activity) => {
        const start = new Date(activity.startDate);
        const end = new Date(activity.updatedAt);
        return acc + (end.getTime() - start.getTime()) / (1000 * 60 * 60 * 24);
      }, 0) / completedWithDates.length)
    : 0;

  // Generate chart data for activities by week
  const generateChartData = () => {
    // Generate 8 weeks: 4 weeks back + current week + 3 weeks forward
    const weeks = Array.from({ length: 8 }, (_, i) => {
      const date = new Date();
      date.setDate(date.getDate() - (4 - i) * 7);
      // Get the Monday of each week
      const day = date.getDay();
      const diff = date.getDate() - day + (day === 0 ? -6 : 1);
      date.setDate(diff);
      return date;
    });

    const chartData = weeks.map(weekStart => {
      const weekEnd = new Date(weekStart);
      weekEnd.setDate(weekEnd.getDate() + 6);

      const activitiesInWeek = activities.filter(activity => {
        const activityStart = new Date(activity.startDate);
        const activityEnd = new Date(activity.dueDate);
        
        // Check if activity overlaps with the week
        return activityStart <= weekEnd && activityEnd >= weekStart;
      });

      return {
        date: `Sem ${weekStart.toLocaleDateString('es-ES', { day: '2-digit', month: '2-digit' })}`,
        weekLabel: `Sem ${weekStart.toLocaleDateString('es-ES', { day: '2-digit', month: '2-digit' })}`,
        weekStart: weekStart,
        completed: activitiesInWeek.filter(a => a.status === 'completed').length,
        inProgress: activitiesInWeek.filter(a => a.status === 'in-progress').length,
        todo: activitiesInWeek.filter(a => a.status === 'todo').length
      };
    });

    return chartData;
  };

  const chartData = generateChartData();
  
  // Generate period title
  const getPeriodTitle = () => {
    if (chartData.length >= 2) {
      const startDate = chartData[0].weekStart;
      const endDate = new Date(chartData[chartData.length - 1].weekStart);
      endDate.setDate(endDate.getDate() + 6); // End of last week
      
      return `Actividades por Semana (Del ${startDate.toLocaleDateString('es-ES', { day: '2-digit', month: '2-digit' })} al ${endDate.toLocaleDateString('es-ES', { day: '2-digit', month: '2-digit' })})`;
    }
    return 'Actividades por Semana';
  };

  const mainStats = [
    {
      title: 'Total Proyectos',
      value: projects.length,
      icon: <Business sx={{ fontSize: 28, color: '#4D2581' }} />,
      bgColor: 'linear-gradient(145deg, #ffffff 0%, #f8fafc 100%)',
      borderColor: '#4D2581',
      subtitle: `${projects.filter(p => p.status === 'active').length} activos`,
      trend: '+12%',
      trendColor: 'success.main'
    },
    {
      title: 'Total Actividades',
      value: totalActivities,
      icon: <Assignment sx={{ fontSize: 28, color: '#f5576c' }} />,
      bgColor: 'linear-gradient(145deg, #ffffff 0%, #fef7f7 100%)',
      borderColor: '#f5576c',
      subtitle: `${completionRate}% completadas`,
      trend: '+8%',
      trendColor: 'success.main'
    },
    {
      title: 'En Progreso',
      value: inProgressActivities,
      icon: <Timeline sx={{ fontSize: 28, color: '#4facfe' }} />,
      bgColor: 'linear-gradient(145deg, #ffffff 0%, #f0f8ff 100%)',
      borderColor: '#4facfe',
      subtitle: `${Math.round((inProgressActivities / totalActivities) * 100)}% del total`,
      trend: '+5%',
      trendColor: 'info.main'
    },
    {
      title: 'Prioridad Alta',
      value: highPriorityActivities,
      icon: <Flag sx={{ fontSize: 28, color: '#fa709a' }} />,
      bgColor: 'linear-gradient(145deg, #ffffff 0%, #fef7f7 100%)',
      borderColor: '#fa709a',
      subtitle: `${overdueActivities} vencidas`,
      trend: '-3%',
      trendColor: 'error.main'
    }
  ];

  const performanceMetrics = [
    {
      title: 'Tasa de Completación',
      value: `${completionRate}%`,
      icon: <CheckCircle sx={{ fontSize: 24, color: '#10b981' }} />,
      color: '#10b981',
      bgColor: 'linear-gradient(145deg, #ffffff 0%, #f0fdf4 100%)',
      borderColor: '#10b981',
      progress: completionRate
    },
    {
      title: 'Tiempo Promedio',
      value: `${avgCompletionTime} días`,
      icon: <Schedule sx={{ fontSize: 24, color: '#3b82f6' }} />,
      color: '#3b82f6',
      bgColor: 'linear-gradient(145deg, #ffffff 0%, #f0f8ff 100%)',
      borderColor: '#3b82f6',
      progress: Math.min(avgCompletionTime * 10, 100)
    },
    {
      title: 'Actividades Vencidas',
      value: overdueActivities,
      icon: <Warning sx={{ fontSize: 24, color: '#f59e0b' }} />,
      color: '#f59e0b',
      bgColor: 'linear-gradient(145deg, #ffffff 0%, #fffbeb 100%)',
      borderColor: '#f59e0b',
      progress: Math.min(overdueActivities * 20, 100)
    },
    {
      title: 'Velocidad del Equipo',
      value: `${Math.round(completedActivities / Math.max(1, Math.ceil((new Date().getTime() - new Date('2024-11-01').getTime()) / (1000 * 60 * 60 * 24))))} act/día`,
      icon: <Speed sx={{ fontSize: 24, color: '#8b5cf6' }} />,
      color: '#8b5cf6',
      bgColor: 'linear-gradient(145deg, #ffffff 0%, #faf5ff 100%)',
      borderColor: '#8b5cf6',
      progress: Math.min(completedActivities * 15, 100)
    }
  ];

  if (loading) {
    return (
      <Box sx={{ width: '100%' }}>
        <LinearProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3, backgroundColor: '#f8fafc', minHeight: '100vh', width: '100%' }}>
      {/* Header Section */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <DashboardIcon color="primary" sx={{ fontSize: 32 }} />
          <Typography variant="h4" component="h1">
            Dashboard
          </Typography>
        </Box>
      </Box>
      


      {/* PWA Status - OCULTO */}
      {/* <PWAStatus showDetails={false} /> */}

      {/* Error Display */}
      {error && (
        <Box sx={{ mb: 3, textAlign: 'center' }}>
          <Typography variant="body1" sx={{ color: 'error.main', mb: 2 }}>
            {error}
          </Typography>
          {!isAuthenticated && (
            <Button
              variant="contained"
              color="primary"
              onClick={() => navigate('/login')}
              sx={{ mt: 2 }}
            >
              Ir a Iniciar Sesión
            </Button>
          )}
        </Box>
      )}

      {/* ===== MAIN STATISTICS CARDS - LAYOUT OPTIMIZADO AL 100% ===== */}
      <Typography variant="h5" component="h2" sx={{ 
        fontWeight: 600, 
        color: '#1e293b',
        mb: 2
      }}>
        Proyectos
      </Typography>
      <Box sx={{ display: 'flex', gap: 3, mb: 4, flexWrap: 'wrap' }}>
        {mainStats.map((stat, index) => (
          <ProjectCard
            key={index}
            title={stat.title}
            value={stat.value}
            icon={stat.icon}
            bgColor={stat.bgColor}
            borderColor={stat.borderColor}
            subtitle={stat.subtitle}
            trend={stat.trend}
            trendColor={stat.trendColor}
          />
        ))}
      </Box>

      {/* Performance Metrics - Layout Optimizado */}
      <Typography variant="h5" component="h2" sx={{ 
        fontWeight: 600, 
        color: '#1e293b',
        mb: 2
      }}>
        Actividades
      </Typography>
      <Box sx={{ display: 'flex', gap: 3, mb: 4, flexWrap: 'wrap' }}>
        {performanceMetrics.map((metric, index) => (
          <ActivityMetricCard
            key={index}
            title={metric.title}
            value={metric.value}
            icon={metric.icon}
            color={metric.color}
            bgColor={metric.bgColor}
            borderColor={metric.borderColor}
            progress={metric.progress}
          />
        ))}
      </Box>

      {/* Gráfico y Estado de Actividades - Lado a Lado */}
      <Box sx={{ display: 'flex', gap: 3, mb: 4, flexWrap: 'wrap' }}>
        {/* Activities Line Chart */}
        <Box sx={{ 
          flex: { xs: '1 1 100%', lg: '0 0 calc(66.67% - 12px)' },
          minWidth: { lg: 'calc(66.67% - 12px)' }
        }}>
          <Card sx={{ 
            height: 420, 
            borderRadius: 3,
            boxShadow: '0 4px 20px rgba(0,0,0,0.08)',
            border: '1px solid #e2e8f0'
          }}>
            <CardContent sx={{ p: 3, height: '100%' }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                <Typography variant="h6" component="h2" sx={{ fontWeight: 700, color: '#1e293b' }}>
                  {getPeriodTitle()}
                </Typography>
                <IconButton size="small" sx={{ color: '#64748b' }}>
                  <Visibility />
                </IconButton>
              </Box>
              
              {/* Recharts Line Chart */}
              <Box sx={{ height: 300, width: '100%' }}>
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart
                    data={chartData}
                    margin={{
                      top: 20,
                      right: 30,
                      left: 20,
                      bottom: 20,
                    }}
                  >
                    <CartesianGrid 
                      strokeDasharray="3 3" 
                      stroke="#e2e8f0"
                      opacity={0.5}
                    />
                    <XAxis 
                      dataKey="weekLabel" 
                      stroke="#64748b"
                      fontSize={12}
                      fontWeight={500}
                      tickLine={false}
                      axisLine={false}
                    />
                    <YAxis 
                      stroke="#64748b"
                      fontSize={12}
                      fontWeight={500}
                      tickLine={false}
                      axisLine={false}
                      domain={[0, 8]}
                    />
                    <Tooltip 
                      contentStyle={{
                        backgroundColor: '#ffffff',
                        border: '1px solid #e2e8f0',
                        borderRadius: '8px',
                        boxShadow: '0 4px 20px rgba(0,0,0,0.1)'
                      }}
                      labelStyle={{
                        color: '#1e293b',
                        fontWeight: 600
                      }}
                    />
                    <Legend 
                      wrapperStyle={{
                        paddingTop: '10px'
                      }}
                    />
                    <Line
                      type="monotone"
                      dataKey="completed"
                      stroke="#10b981"
                      strokeWidth={3}
                      dot={{ 
                        fill: '#10b981', 
                        strokeWidth: 2, 
                        stroke: '#ffffff',
                        r: 4
                      }}
                      activeDot={{ r: 6 }}
                      name="Completadas"
                    />
                    <Line
                      type="monotone"
                      dataKey="inProgress"
                      stroke="#3b82f6"
                      strokeWidth={3}
                      dot={{ 
                        fill: '#3b82f6', 
                        strokeWidth: 2, 
                        stroke: '#ffffff',
                        r: 4
                      }}
                      activeDot={{ r: 6 }}
                      name="En Progreso"
                    />
                    <Line
                      type="monotone"
                      dataKey="todo"
                      stroke="#6b7280"
                      strokeWidth={3}
                      dot={{ 
                        fill: '#6b7280', 
                        strokeWidth: 2, 
                        stroke: '#ffffff',
                        r: 4
                      }}
                      activeDot={{ r: 6 }}
                      name="Pendientes"
                    />
                  </LineChart>
                </ResponsiveContainer>
              </Box>
              
              {/* Legend */}
              <Box sx={{ 
                display: 'flex', 
                justifyContent: 'center', 
                gap: 3, 
                mt: 2,
                pt: 2,
                borderTop: '1px solid #e2e8f0'
              }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Box sx={{ width: 12, height: 12, backgroundColor: '#10b981', borderRadius: 1 }} />
                  <Typography variant="caption" sx={{ color: '#64748b', fontWeight: 500 }}>
                    Completadas
                  </Typography>
                </Box>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Box sx={{ width: 12, height: 12, backgroundColor: '#3b82f6', borderRadius: 1 }} />
                  <Typography variant="caption" sx={{ color: '#64748b', fontWeight: 500 }}>
                    En Progreso
                  </Typography>
                </Box>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Box sx={{ width: 12, height: 12, backgroundColor: '#6b7280', borderRadius: 1 }} />
                  <Typography variant="caption" sx={{ color: '#64748b', fontWeight: 500 }}>
                    Pendientes
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Box>

        {/* Activity Status Chart */}
        <Box sx={{ 
          flex: { xs: '1 1 100%', lg: '0 0 calc(33.33% - 12px)' },
          minWidth: { lg: 'calc(33.33% - 12px)' },
          flexShrink: 0
        }}>
          <Card sx={{ 
            height: 420, 
            borderRadius: 3,
            boxShadow: '0 4px 20px rgba(0,0,0,0.08)',
            border: '1px solid #e2e8f0'
          }}>
            <CardContent sx={{ p: 3, height: '100%' }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                <Typography variant="h6" component="h2" sx={{ fontWeight: 700, color: '#1e293b' }}>
                  Estado de Actividades
                </Typography>
                <IconButton size="small" sx={{ color: '#64748b' }}>
                  <Visibility />
                </IconButton>
              </Box>
              
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
                {['todo', 'in-progress', 'review', 'completed'].map((status) => {
                  const count = activities.filter(a => a.status === status).length;
                  const percentage = totalActivities > 0 ? (count / totalActivities) * 100 : 0;
                  
                  return (
                    <Box key={status} sx={{ display: 'flex', alignItems: 'center', gap: 3 }}>
                      <Box sx={{ 
                        width: 80, 
                        textAlign: 'center',
                        backgroundColor: '#f8fafc',
                        borderRadius: 2,
                        py: 1
                      }}>
                        <Typography variant="h5" sx={{ 
                          fontWeight: 800, 
                          color: getActivityStatusColor(status),
                          mb: 0.5
                        }}>
                          {count}
                        </Typography>
                        <Typography variant="caption" sx={{ 
                          color: '#64748b',
                          fontWeight: 600,
                          textTransform: 'uppercase',
                          letterSpacing: '0.5px'
                        }}>
                          {getActivityStatusText(status)}
                        </Typography>
                      </Box>
                      <Box sx={{ flexGrow: 1 }}>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1.5 }}>
                          <Typography variant="body2" sx={{ fontWeight: 600, color: '#1e293b' }}>
                            {getActivityStatusText(status)}
                          </Typography>
                          <Typography variant="body2" sx={{ 
                            color: '#64748b', 
                            fontWeight: 600,
                            backgroundColor: '#f1f5f9',
                            px: 1.5,
                            py: 0.5,
                            borderRadius: 1
                          }}>
                            {Math.round(percentage)}%
                          </Typography>
                        </Box>
                        <LinearProgress
                          variant="determinate"
                          value={percentage}
                          sx={{
                            height: 10,
                            borderRadius: 5,
                            backgroundColor: '#e2e8f0',
                            '& .MuiLinearProgress-bar': {
                              backgroundColor: getActivityStatusColor(status),
                              borderRadius: 5
                            }
                          }}
                        />
                      </Box>
                    </Box>
                  );
                })}
              </Box>
            </CardContent>
          </Card>
        </Box>

        {/* Recent Activities */}
        <Box sx={{ width: '100%' }}>
          <Card sx={{ 
            borderRadius: 3,
            boxShadow: '0 4px 20px rgba(0,0,0,0.08)',
            border: '1px solid #e2e8f0'
          }}>
            <CardContent sx={{ p: 3 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                <Typography variant="h6" component="h2" sx={{ fontWeight: 700, color: '#1e293b' }}>
                  Actividades Recientes
                </Typography>
                <Button
                  size="small"
                  variant="outlined"
                  onClick={() => navigate('/projects')}
                  sx={{ 
                    borderRadius: 2,
                    textTransform: 'none',
                    fontWeight: 600
                  }}
                >
                  Ver Todas
                </Button>
              </Box>
              
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow sx={{ backgroundColor: '#f8fafc' }}>
                      <TableCell sx={{ fontWeight: 600, color: '#64748b', borderBottom: '2px solid #e2e8f0' }}>
                        Proyecto
                      </TableCell>
                      <TableCell sx={{ fontWeight: 600, color: '#64748b', borderBottom: '2px solid #e2e8f0' }}>
                        Actividad
                      </TableCell>
                      <TableCell sx={{ fontWeight: 600, color: '#64748b', borderBottom: '2px solid #e2e8f0' }}>
                        Asignado
                      </TableCell>
                      <TableCell sx={{ fontWeight: 600, color: '#64748b', borderBottom: '2px solid #e2e8f0' }}>
                        Estado
                      </TableCell>
                      <TableCell sx={{ fontWeight: 600, color: '#64748b', borderBottom: '2px solid #e2e8f0' }}>
                        Prioridad
                      </TableCell>
                      <TableCell sx={{ fontWeight: 600, color: '#64748b', borderBottom: '2px solid #e2e8f0' }}>
                        Vencimiento
                      </TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {(() => {
                      // Group activities by project
                      const groupedActivities = activities.reduce((acc, activity) => {
                        const projectId = activity.projectId;
                        if (!acc[projectId]) {
                          acc[projectId] = [];
                        }
                        acc[projectId].push(activity);
                        return acc;
                      }, {} as Record<string, typeof activities>);

                      // Get project names
                      const getProjectName = (projectId: string) => {
                        const project = projects.find(p => String(p.id) === projectId);
                        return project ? project.name : 'Proyecto Desconocido';
                      };

                      // Flatten grouped activities with project info
                      const flattenedActivities = Object.entries(groupedActivities)
                        .flatMap(([projectId, projectActivities]) => 
                          projectActivities.slice(0, 3).map((activity, index) => ({
                            ...activity,
                            projectName: getProjectName(projectId),
                            isFirstInProject: index === 0
                          }))
                        )
                        .slice(0, 8); // Limit to 8 activities

                      return flattenedActivities.map((activity) => (
                        <TableRow key={activity.id} hover sx={{ 
                          '&:hover': { backgroundColor: '#f8fafc' },
                          '&:last-child td': { border: 0 },
                          backgroundColor: activity.isFirstInProject ? '#f8fafc' : 'transparent'
                        }}>
                          <TableCell>
                            {activity.isFirstInProject && (
                              <Box>
                                <Typography variant="body2" sx={{ fontWeight: 600, color: '#4D2581', mb: 0.5 }}>
                                  {activity.projectName}
                                </Typography>
                                <Typography variant="caption" sx={{ color: '#64748b' }}>
                                  {groupedActivities[activity.projectId]?.length || 0} actividades
                                </Typography>
                              </Box>
                            )}
                          </TableCell>
                          <TableCell>
                            <Box>
                              <Typography variant="body2" sx={{ fontWeight: 600, color: '#1e293b', mb: 0.5 }}>
                                {activity.title}
                              </Typography>
                              <Typography variant="caption" sx={{ color: '#64748b' }}>
                                {activity.description}
                              </Typography>
                            </Box>
                          </TableCell>
                        <TableCell>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                            <Avatar sx={{ 
                              width: 32, 
                              height: 32, 
                              fontSize: '0.875rem',
                              backgroundColor: '#3b82f6',
                              fontWeight: 600
                            }}>
                              {activity.assignee.split(' ').map(n => n[0]).join('')}
                            </Avatar>
                            <Typography variant="body2" sx={{ fontWeight: 500, color: '#1e293b' }}>
                              {activity.assignee}
                            </Typography>
                          </Box>
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={getActivityStatusText(activity.status)}
                            size="small"
                            color={getActivityStatusColor(activity.status) as any}
                            variant="outlined"
                            sx={{ 
                              fontWeight: 600,
                              borderRadius: 2,
                              textTransform: 'none'
                            }}
                          />
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={getPriorityText(activity.priority)}
                            size="small"
                            color={getPriorityColor(activity.priority) as any}
                            variant="outlined"
                            sx={{ 
                              fontWeight: 600,
                              borderRadius: 2,
                              textTransform: 'none'
                            }}
                          />
                        </TableCell>
                        <TableCell>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <CalendarToday sx={{ fontSize: 18, color: '#64748b' }} />
                            <Typography variant="body2" sx={{ fontWeight: 500, color: '#1e293b' }}>
                              {activity.dueDate.toLocaleDateString()}
                            </Typography>
                          </Box>
                        </TableCell>
                      </TableRow>
                    ));
                    })()}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Box>
      </Box>

    </Box>
  );
};

export default DashboardPage;

