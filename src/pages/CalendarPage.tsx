import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  ToggleButton,
  ToggleButtonGroup,
  Card,
  CardContent,
  Chip,
  useTheme
} from '@mui/material';
import { useAuth } from '../contexts/AuthContext';
import { activityService } from '../services/api';
import {
  ViewModule as MonthIcon,
  ViewWeek as WeekIcon,
  ViewList as AgendaIcon,
  CalendarToday as CalendarIcon,
  Event as EventIcon,
  Schedule as ScheduleIcon,
  Person as PersonIcon
} from '@mui/icons-material';
import type { ProjectActivity } from '../types';

type ViewMode = 'month' | 'week' | 'agenda';
type DateDisplayMode = 'start' | 'end' | 'both';

interface CalendarPageProps {}

const CalendarPage: React.FC<CalendarPageProps> = () => {
  const { token } = useAuth();
  const [viewMode, setViewMode] = useState<ViewMode>('month');
  const [dateDisplayMode, setDateDisplayMode] = useState<DateDisplayMode>('both');
  const [currentDate, setCurrentDate] = useState(new Date());
  const [activities, setActivities] = useState<ProjectActivity[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const theme = useTheme();

  // Cargar actividades reales desde el backend
  useEffect(() => {
    if (token) {
      fetchActivities();
    }
  }, [token]);

  const fetchActivities = async () => {
    if (!token) return;
    
    setLoading(true);
    setError('');
    
    try {
      console.log('Fetching all activities for calendar...');
      const response = await activityService.getActivities(token);
      console.log('Activities response:', response);
      
      if (response.status === 'success' && response.data) {
        const processedActivities = response.data.map((activity: any) => ({
          id: activity.id.toString(),
          title: activity.title,
          description: activity.description,
          status: activity.status,
          priority: activity.priority,
          assignee: activity.assignee || 'Sin asignar',
          startDate: activity.start_date ? new Date(activity.start_date) : new Date(),
          dueDate: activity.due_date ? new Date(activity.due_date) : new Date(),
          createdAt: activity.created_at ? new Date(activity.created_at) : new Date(),
          updatedAt: activity.updated_at ? new Date(activity.updated_at) : new Date(),
          projectId: activity.project_id?.toString() || '1'
        }));
        setActivities(processedActivities);
      } else {
        console.log('Error in activities response:', response.error);
        setError(response.error || 'Error al cargar las actividades');
      }
    } catch (error) {
      console.error('Error fetching activities:', error);
      setError('Error al cargar las actividades');
    } finally {
      setLoading(false);
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return '#d32f2f'; // Rojo
      case 'medium': return '#ed6c02'; // Naranja
      case 'low': return '#2e7d32'; // Verde
      default: return '#757575'; // Gris
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return '#2e7d32'; // Verde
      case 'in-progress': return '#ed6c02'; // Naranja
      case 'review': return '#9c27b0'; // Púrpura
      case 'todo': return '#1976d2'; // Azul
      default: return '#757575'; // Gris
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'completed': return 'Completado';
      case 'in-progress': return 'En Progreso';
      case 'review': return 'En Revisión';
      case 'todo': return 'Por Hacer';
      default: return status;
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

  const renderMonthView = () => {
    const year = currentDate.getFullYear();
    const month = currentDate.getMonth();
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const startDate = new Date(firstDay);
    startDate.setDate(startDate.getDate() - firstDay.getDay());

    const days = [];
    const currentDateObj = new Date(startDate);

    while (currentDateObj <= lastDay || currentDateObj.getDay() !== 0) {
      days.push(new Date(currentDateObj));
      currentDateObj.setDate(currentDateObj.getDate() + 1);
    }

    const getActivitiesForDate = (date: Date) => {
      return activities.filter(activity => {
        const start = new Date(activity.startDate);
        const end = new Date(activity.dueDate);
        const current = new Date(date);
        
        if (dateDisplayMode === 'start') {
          return start.toDateString() === current.toDateString();
        } else if (dateDisplayMode === 'end') {
          return end.toDateString() === current.toDateString();
        } else {
          return current >= start && current <= end;
        }
      });
    };

    return (
      <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(7, 1fr)', gap: 1 }}>
        {['Dom', 'Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb'].map(day => (
          <Box key={day} sx={{ p: 1, textAlign: 'center', fontWeight: 'bold', backgroundColor: 'background.paper' }}>
            {day}
          </Box>
        ))}
        
        {days.map((date, index) => {
          const isCurrentMonth = date.getMonth() === month;
          const isToday = date.toDateString() === new Date().toDateString();
          const dayActivities = getActivitiesForDate(date);
          
          return (
            <Box
              key={index}
              sx={{
                minHeight: 120,
                p: 1,
                border: '1px solid',
                borderColor: 'divider',
                backgroundColor: isCurrentMonth ? 'background.paper' : 'background.default',
                opacity: isCurrentMonth ? 1 : 0.5,
                position: 'relative',
                ...(isToday && {
                  backgroundColor: 'primary.light',
                  color: 'primary.contrastText'
                })
              }}
            >
              <Typography
                variant="body2"
                sx={{
                  fontWeight: isToday ? 'bold' : 'normal',
                  textAlign: 'right',
                  mb: 1
                }}
              >
                {date.getDate()}
              </Typography>
              
              {dayActivities.slice(0, 3).map(activity => (
                <Chip
                  key={activity.id}
                  label={activity.title}
                  size="small"
                  sx={{
                    fontSize: '0.7rem',
                    height: 20,
                    mb: 0.5,
                    backgroundColor: getStatusColor(activity.status),
                    color: 'white',
                    '& .MuiChip-label': {
                      px: 1
                    }
                  }}
                />
              ))}
              
              {dayActivities.length > 3 && (
                <Typography variant="caption" sx={{ color: 'text.secondary' }}>
                  +{dayActivities.length - 3} más
                </Typography>
              )}
            </Box>
          );
        })}
      </Box>
    );
  };

  const renderWeekView = () => {
    const startOfWeek = new Date(currentDate);
    const day = startOfWeek.getDay();
    startOfWeek.setDate(startOfWeek.getDate() - day);
    
    const weekDays = [];
    for (let i = 0; i < 7; i++) {
      const date = new Date(startOfWeek);
      date.setDate(date.getDate() + i);
      weekDays.push(date);
    }

    const getActivitiesForDate = (date: Date) => {
      return activities.filter(activity => {
        const start = new Date(activity.startDate);
        const end = new Date(activity.dueDate);
        const current = new Date(date);
        
        if (dateDisplayMode === 'start') {
          return start.toDateString() === current.toDateString();
        } else if (dateDisplayMode === 'end') {
          return end.toDateString() === current.toDateString();
        } else {
          return current >= start && current <= end;
        }
      });
    };

    return (
      <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(7, 1fr)', gap: 1 }}>
        {weekDays.map((date, index) => {
          const isToday = date.toDateString() === new Date().toDateString();
          const dayActivities = getActivitiesForDate(date);
          
          return (
            <Box
              key={index}
              sx={{
                minHeight: 200,
                p: 1,
                border: '1px solid',
                borderColor: 'divider',
                backgroundColor: 'background.paper',
                ...(isToday && {
                  backgroundColor: 'primary.light',
                  color: 'primary.contrastText'
                })
              }}
            >
              <Typography
                variant="subtitle2"
                sx={{
                  fontWeight: 'bold',
                  textAlign: 'center',
                  mb: 1,
                  textTransform: 'capitalize'
                }}
              >
                {date.toLocaleDateString('es-ES', { weekday: 'short' })}
              </Typography>
              
              <Typography
                variant="body2"
                sx={{
                  textAlign: 'center',
                  mb: 2,
                  fontWeight: isToday ? 'bold' : 'normal'
                }}
              >
                {date.getDate()}
              </Typography>
              
              {dayActivities.map(activity => (
                <Card key={activity.id} sx={{ mb: 1, fontSize: '0.7rem' }}>
                  <CardContent sx={{ p: 1, '&:last-child': { pb: 1 } }}>
                    <Typography variant="caption" sx={{ fontWeight: 'bold', display: 'block' }}>
                      {activity.title}
                    </Typography>
                    <Typography variant="caption" sx={{ color: 'text.secondary', display: 'block' }}>
                      {activity.assignee}
                    </Typography>
                    <Box sx={{ display: 'flex', gap: 0.5, mt: 0.5 }}>
                      <Chip
                        label={getPriorityText(activity.priority)}
                        size="small"
                        sx={{ 
                          height: 16, 
                          fontSize: '0.6rem',
                          backgroundColor: getPriorityColor(activity.priority),
                          color: 'white'
                        }}
                      />
                      <Chip
                        label={getStatusText(activity.status)}
                        size="small"
                        sx={{ 
                          height: 16, 
                          fontSize: '0.6rem',
                          backgroundColor: getStatusColor(activity.status),
                          color: 'white'
                        }}
                      />
                    </Box>
                  </CardContent>
                </Card>
              ))}
            </Box>
          );
        })}
      </Box>
    );
  };

  const renderAgendaView = () => {
    const sortedActivities = [...activities].sort((a, b) => {
      if (dateDisplayMode === 'start') {
        return new Date(a.startDate).getTime() - new Date(b.startDate).getTime();
      } else if (dateDisplayMode === 'end') {
        return new Date(a.dueDate).getTime() - new Date(b.dueDate).getTime();
      } else {
        return new Date(a.startDate).getTime() - new Date(b.startDate).getTime();
      }
    });

    return (
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
        {sortedActivities.map(activity => (
          <Card key={activity.id}>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
                <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
                  {activity.title}
                </Typography>
                <Box sx={{ display: 'flex', gap: 1 }}>
                  <Chip
                    label={getPriorityText(activity.priority)}
                    size="small"
                    sx={{
                      backgroundColor: getPriorityColor(activity.priority),
                      color: 'white'
                    }}
                  />
                  <Chip
                    label={getStatusText(activity.status)}
                    size="small"
                    sx={{
                      backgroundColor: getStatusColor(activity.status),
                      color: 'white'
                    }}
                  />
                </Box>
              </Box>
              
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                {activity.description}
              </Typography>
              
              <Box sx={{ display: 'flex', gap: 3, flexWrap: 'wrap' }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <PersonIcon fontSize="small" color="primary" />
                  <Typography variant="body2">
                    {activity.assignee}
                  </Typography>
                </Box>
                
                {dateDisplayMode === 'start' || dateDisplayMode === 'both' ? (
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <EventIcon fontSize="small" color="primary" />
                    <Typography variant="body2">
                      Inicio: {new Date(activity.startDate).toLocaleDateString()}
                    </Typography>
                  </Box>
                ) : null}
                
                {dateDisplayMode === 'end' || dateDisplayMode === 'both' ? (
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <ScheduleIcon fontSize="small" color="primary" />
                    <Typography variant="body2">
                      Vencimiento: {new Date(activity.dueDate).toLocaleDateString()}
                    </Typography>
                  </Box>
                ) : null}
              </Box>
            </CardContent>
          </Card>
        ))}
      </Box>
    );
  };

  const navigateMonth = (direction: 'prev' | 'next') => {
    const newDate = new Date(currentDate);
    if (direction === 'prev') {
      newDate.setMonth(newDate.getMonth() - 1);
    } else {
      newDate.setMonth(newDate.getMonth() + 1);
    }
    setCurrentDate(newDate);
  };

  const navigateWeek = (direction: 'prev' | 'next') => {
    const newDate = new Date(currentDate);
    if (direction === 'prev') {
      newDate.setDate(newDate.getDate() - 7);
    } else {
      newDate.setDate(newDate.getDate() + 7);
    }
    setCurrentDate(newDate);
  };

  const getCurrentPeriodText = () => {
    if (viewMode === 'month') {
      return currentDate.toLocaleDateString('es-ES', { month: 'long', year: 'numeric' });
    } else if (viewMode === 'week') {
      const startOfWeek = new Date(currentDate);
      const day = startOfWeek.getDay();
      startOfWeek.setDate(startOfWeek.getDate() - day);
      const endOfWeek = new Date(startOfWeek);
      endOfWeek.setDate(endOfWeek.getDate() + 6);
      return `${startOfWeek.toLocaleDateString()} - ${endOfWeek.toLocaleDateString()}`;
    }
    return '';
  };

  return (
    <Box>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <CalendarIcon color="primary" sx={{ fontSize: 32 }} />
          <Typography variant="h4" component="h1">
            Calendario
          </Typography>
        </Box>
      </Box>

      {/* Controls */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Box sx={{ display: 'flex', flexDirection: { xs: 'column', md: 'row' }, gap: 2, alignItems: 'center' }}>
          {/* View Mode Toggle */}
          <ToggleButtonGroup
            value={viewMode}
            exclusive
            onChange={(_, newValue) => newValue && setViewMode(newValue)}
            size="small"
          >
            <ToggleButton value="month">
              <MonthIcon sx={{ mr: 1 }} />
              Mes
            </ToggleButton>
            <ToggleButton value="week">
              <WeekIcon sx={{ mr: 1 }} />
              Semana
            </ToggleButton>
            <ToggleButton value="agenda">
              <AgendaIcon sx={{ mr: 1 }} />
              Agenda
            </ToggleButton>
          </ToggleButtonGroup>

          {/* Date Display Mode */}
          <FormControl size="small" sx={{ minWidth: 200 }}>
            <InputLabel>Mostrar por</InputLabel>
            <Select
              value={dateDisplayMode}
              label="Mostrar por"
              onChange={(e) => setDateDisplayMode(e.target.value as DateDisplayMode)}
            >
              <MenuItem value="start">Fecha de inicio</MenuItem>
              <MenuItem value="end">Fecha de vencimiento</MenuItem>
              <MenuItem value="both">Ambas fechas</MenuItem>
            </Select>
          </FormControl>

          {/* Navigation */}
          <Box sx={{ display: 'flex', gap: 1 }}>
            <Button
              variant="outlined"
              size="small"
              onClick={() => viewMode === 'month' ? navigateMonth('prev') : navigateWeek('prev')}
            >
              Anterior
            </Button>
            <Button
              variant="outlined"
              size="small"
              onClick={() => viewMode === 'month' ? navigateMonth('next') : navigateWeek('next')}
            >
              Siguiente
            </Button>
            <Button
              variant="outlined"
              size="small"
              onClick={() => setCurrentDate(new Date())}
            >
              Hoy
            </Button>
          </Box>
        </Box>

        {/* Current Period Display */}
        {viewMode !== 'agenda' && (
          <Typography variant="h6" sx={{ mt: 2, textAlign: 'center', fontWeight: 'bold' }}>
            {getCurrentPeriodText()}
          </Typography>
        )}
      </Paper>

      {/* Calendar Content */}
      <Paper sx={{ p: 2 }}>
        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
            <Typography>Cargando actividades...</Typography>
          </Box>
        ) : error ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
            <Typography color="error">{error}</Typography>
          </Box>
        ) : (
          <>
            {viewMode === 'month' && renderMonthView()}
            {viewMode === 'week' && renderWeekView()}
            {viewMode === 'agenda' && renderAgendaView()}
          </>
        )}
      </Paper>
    </Box>
  );
};

export default CalendarPage;
