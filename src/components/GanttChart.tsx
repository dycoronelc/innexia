import React, { useState, useMemo } from 'react';
import {
  Box,
  Paper,
  Typography,
  Chip,
  IconButton,
  Tooltip,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField
} from '@mui/material';
import {
  Download,
  Edit,
  Person,
  Schedule,
  Event
} from '@mui/icons-material';
import type { ProjectActivity } from '../types';

interface GanttChartProps {
  activities: ProjectActivity[];
  projectStartDate: Date;
  projectEndDate: Date;
  onUpdateActivity?: (activity: ProjectActivity) => void;
}

interface GanttActivity {
  id: string;
  title: string;
  startDate: Date;
  endDate: Date;
  duration: number;
  status: string;
  priority: string;
  assignee: string;
  color: string;
}

const GanttChart: React.FC<GanttChartProps> = ({
  activities,
  projectStartDate,
  projectEndDate,
  onUpdateActivity
}) => {
  const [zoomLevel, setZoomLevel] = useState<'day' | 'week' | 'month'>('week');
  const [filterAssignee, setFilterAssignee] = useState<string>('all');
  const [filterPriority, setFilterPriority] = useState<string>('all');
  const [selectedActivity, setSelectedActivity] = useState<GanttActivity | null>(null);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [editForm, setEditForm] = useState({
    startDate: '',
    endDate: ''
  });

  // Procesar actividades para el Gantt
  const ganttActivities = useMemo(() => {
    // Para debugging, usar fechas hardcodeadas si no hay actividades válidas
    if (activities.length === 0) {
      const now = new Date();
      const testActivities = [
        {
          id: 'test1',
          title: 'Actividad de Prueba 1',
          startDate: new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000), // 7 días atrás
          endDate: new Date(now.getTime() + 3 * 24 * 60 * 60 * 1000), // 3 días adelante
          duration: 10,
          status: 'in-progress',
          priority: 'high',
          assignee: 'Usuario Test',
          color: getStatusColor('in-progress')
        },
        {
          id: 'test2',
          title: 'Actividad de Prueba 2',
          startDate: new Date(now.getTime() + 2 * 24 * 60 * 60 * 1000), // 2 días adelante
          endDate: new Date(now.getTime() + 10 * 24 * 60 * 60 * 1000), // 10 días adelante
          duration: 8,
          status: 'todo',
          priority: 'medium',
          assignee: 'Usuario Test 2',
          color: getStatusColor('todo')
        }
      ];
      // Using test activities
      return testActivities;
    }
    
    const processed = activities.filter(activity => {
      // Filtrar actividades con fechas válidas
      const startDate = new Date(activity.startDate);
      const endDate = new Date(activity.dueDate);
      return !isNaN(startDate.getTime()) && !isNaN(endDate.getTime());
    }).map(activity => {
      const startDate = new Date(activity.startDate);
      const endDate = new Date(activity.dueDate);
      return {
        id: activity.id,
        title: activity.title,
        startDate,
        endDate,
        duration: Math.max(1, Math.ceil((endDate.getTime() - startDate.getTime()) / (1000 * 60 * 60 * 24))),
        status: activity.status,
        priority: activity.priority,
        assignee: activity.assignee,
        color: getStatusColor(activity.status)
      };
    });
    
    // Debug: Log de actividades procesadas - removido para limpiar consola
    
    return processed;
  }, [activities]);

  // Filtrar actividades
  const filteredActivities = useMemo(() => {
    return ganttActivities.filter(activity => {
      const assigneeMatch = filterAssignee === 'all' || activity.assignee === filterAssignee;
      const priorityMatch = filterPriority === 'all' || activity.priority === filterPriority;
      return assigneeMatch && priorityMatch;
    });
  }, [ganttActivities, filterAssignee, filterPriority]);

  // Función para obtener el lunes de una semana
  const getMondayOfWeek = (date: Date): Date => {
    const d = new Date(date);
    const day = d.getDay();
    const diff = d.getDate() - day + (day === 0 ? -6 : 1); // Ajustar para que lunes sea 1
    return new Date(d.setDate(diff));
  };

  // Calcular timeline
  const timeline = useMemo(() => {
    // Validar fechas del proyecto
    if (!projectStartDate || !projectEndDate || 
        isNaN(projectStartDate.getTime()) || isNaN(projectEndDate.getTime())) {
      // Si no hay fechas válidas, crear un timeline básico de 30 días
      const now = new Date();
      const dates: Date[] = [];
      for (let i = 0; i < 5; i++) {
        const date = new Date(now);
        date.setDate(now.getDate() + (i * 7));
        dates.push(date);
      }
      return dates;
    }
    
    const start = new Date(projectStartDate);
    const end = new Date(projectEndDate);
    const dates: Date[] = [];
    
    // Asegurar que end no sea anterior a start
    if (end < start) {
      end.setTime(start.getTime() + 30 * 24 * 60 * 60 * 1000); // 30 días después
    }
    
    // Extender el timeline un poco antes y después para mejor visualización
    const extendedStart = new Date(start);
    extendedStart.setDate(start.getDate() - 7); // Una semana antes
    const extendedEnd = new Date(end);
    extendedEnd.setDate(end.getDate() + 7); // Una semana después
    
    if (zoomLevel === 'week') {
      // Para vista semanal, comenzar desde el lunes de la semana del proyecto
      let current = getMondayOfWeek(extendedStart);
      const endMonday = getMondayOfWeek(extendedEnd);
      
      while (current <= endMonday) {
        dates.push(new Date(current));
        current.setDate(current.getDate() + 7);
      }
    } else {
      // Para vista diaria y mensual, mantener el comportamiento original
      let current = new Date(extendedStart);
      while (current <= extendedEnd) {
        dates.push(new Date(current));
        if (zoomLevel === 'day') {
          current.setDate(current.getDate() + 1);
        } else {
          current.setMonth(current.getMonth() + 1);
        }
      }
    }
    
    // Asegurar que al menos hay una fecha en el timeline
    if (dates.length === 0) {
      dates.push(new Date());
    }
    
    return dates;
  }, [projectStartDate, projectEndDate, zoomLevel]);

  // Obtener color por estado
  function getStatusColor(status: string): string {
    switch (status) {
      case 'completed': return '#2e7d32';
      case 'in-progress': return '#ed6c02';
      case 'review': return '#9c27b0';
      case 'todo': return '#1976d2';
      default: return '#757575';
    }
  }

  // Obtener color por prioridad
  function getPriorityColor(priority: string): string {
    switch (priority) {
      case 'high': return '#d32f2f';
      case 'medium': return '#ed6c02';
      case 'low': return '#2e7d32';
      default: return '#757575';
    }
  }

  // Calcular posición X de una fecha en píxeles
  function getTimelinePosition(date: Date): number {
    // Validar que las fechas son válidas
    if (!date || !projectStartDate || !projectEndDate || 
        isNaN(date.getTime()) || isNaN(projectStartDate.getTime()) || isNaN(projectEndDate.getTime())) {
      return 0;
    }
    
    // Calcular posición basada en el timeline visible
    const timelineStart = timeline[0];
    const timelineEnd = timeline[timeline.length - 1];
    const timelineDuration = timelineEnd.getTime() - timelineStart.getTime();
    
    if (timelineDuration <= 0) {
      return 0;
    }
    
    // Calcular posición relativa dentro del timeline visible
    const relativePosition = (date.getTime() - timelineStart.getTime()) / timelineDuration;
    const timelineWidth = timeline.length * 120; // 120px por columna
    const position = relativePosition * timelineWidth;
    
    // Debug: Log de cálculo de posición - removido para limpiar consola
    
    return Math.max(0, Math.min(position, timelineWidth));
  }

  // Calcular ancho de una actividad en píxeles
  function getTimelineWidth(startDate: Date, endDate: Date): number {
    // Validar que las fechas son válidas
    if (!startDate || !endDate || !projectStartDate || !projectEndDate || 
        isNaN(startDate.getTime()) || isNaN(endDate.getTime()) || 
        isNaN(projectStartDate.getTime()) || isNaN(projectEndDate.getTime())) {
      return 60; // Ancho mínimo por defecto
    }
    
    const activityDuration = endDate.getTime() - startDate.getTime();
    
    // Calcular ancho basado en el timeline visible
    const timelineStart = timeline[0];
    const timelineEnd = timeline[timeline.length - 1];
    const timelineDuration = timelineEnd.getTime() - timelineStart.getTime();
    
    if (timelineDuration <= 0) {
      return 60;
    }
    
    // Calcular ancho basado en la duración relativa dentro del timeline visible
    const relativeDuration = activityDuration / timelineDuration;
    const timelineWidth = timeline.length * 120; // 120px por columna
    const width = relativeDuration * timelineWidth;
    
    // Debug: Log de cálculo de ancho - removido para limpiar consola
    
    return Math.max(60, Math.min(width, timelineWidth)); // Mínimo 60px para que sea visible
  }

  // Manejar edición de fechas
  const handleEditDates = (activity: GanttActivity) => {
    setSelectedActivity(activity);
    setEditForm({
      startDate: activity.startDate.toISOString().split('T')[0],
      endDate: activity.endDate.toISOString().split('T')[0]
    });
    setEditDialogOpen(true);
  };

  const handleSaveDates = () => {
    if (selectedActivity && onUpdateActivity) {
      const updatedActivity = activities.find(a => a.id === selectedActivity.id);
      if (updatedActivity) {
        const updated = {
          ...updatedActivity,
          startDate: new Date(editForm.startDate),
          dueDate: new Date(editForm.endDate)
        };
        onUpdateActivity(updated);
      }
    }
    setEditDialogOpen(false);
  };

  // Obtener asignados únicos
  const assignees = useMemo(() => {
    const unique = [...new Set(activities.map(a => a.assignee))];
    return unique;
  }, [activities]);

  return (
    <Box sx={{ width: '100%' }}>
      {/* Header con controles */}
      <Box sx={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center', 
        mb: 3,
        flexWrap: 'wrap',
        gap: 2
      }}>
        <Typography variant="h6" component="h2" sx={{ fontWeight: 700, color: '#1e293b' }}>
          Cronograma del Proyecto
        </Typography>
        
        <Box sx={{ display: 'flex', gap: 2, alignItems: 'center', flexWrap: 'wrap' }}>
          {/* Controles de zoom */}
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Tooltip title="Vista diaria">
              <IconButton 
                size="small" 
                onClick={() => setZoomLevel('day')}
                color={zoomLevel === 'day' ? 'primary' : 'default'}
              >
                <Schedule />
              </IconButton>
            </Tooltip>
            <Tooltip title="Vista semanal">
              <IconButton 
                size="small" 
                onClick={() => setZoomLevel('week')}
                color={zoomLevel === 'week' ? 'primary' : 'default'}
              >
                <Event />
              </IconButton>
            </Tooltip>
            <Tooltip title="Vista mensual">
              <IconButton 
                size="small" 
                onClick={() => setZoomLevel('month')}
                color={zoomLevel === 'month' ? 'primary' : 'default'}
              >
                <Event />
              </IconButton>
            </Tooltip>
          </Box>

          {/* Filtros */}
          <FormControl size="small" sx={{ minWidth: 120 }}>
            <InputLabel>Responsable</InputLabel>
            <Select
              value={filterAssignee}
              label="Responsable"
              onChange={(e) => setFilterAssignee(e.target.value)}
            >
              <MenuItem value="all">Todos</MenuItem>
              {assignees.map(assignee => (
                <MenuItem key={assignee} value={assignee}>{assignee}</MenuItem>
              ))}
            </Select>
          </FormControl>

          <FormControl size="small" sx={{ minWidth: 120 }}>
            <InputLabel>Prioridad</InputLabel>
            <Select
              value={filterPriority}
              label="Prioridad"
              onChange={(e) => setFilterPriority(e.target.value)}
            >
              <MenuItem value="all">Todas</MenuItem>
              <MenuItem value="high">Alta</MenuItem>
              <MenuItem value="medium">Media</MenuItem>
              <MenuItem value="low">Baja</MenuItem>
            </Select>
          </FormControl>

          <Button
            variant="outlined"
            startIcon={<Download />}
            size="small"
          >
            Exportar
          </Button>
        </Box>
      </Box>

      {/* Timeline */}
      <Paper sx={{ p: 2, mb: 2, overflow: 'auto' }}>
        <Box sx={{ 
          display: 'flex', 
          minWidth: 'max-content',
          borderBottom: '2px solid #e2e8f0'
        }}>
          {/* Columna de actividades */}
          <Box sx={{ width: 300, flexShrink: 0, borderRight: '1px solid #e2e8f0' }}>
            <Box sx={{ 
              p: 2, 
              backgroundColor: '#f8fafc', 
              borderBottom: '1px solid #e2e8f0',
              fontWeight: 600
            }}>
              Actividades
            </Box>
          </Box>
          
          {/* Headers de fechas */}
          {timeline.map((date, index) => (
            <Tooltip 
              key={index}
              title={
                zoomLevel === 'week' 
                  ? `Semana del ${date.toLocaleDateString('es-ES', { 
                      day: 'numeric', 
                      month: 'long', 
                      year: 'numeric' 
                    })} al ${new Date(date.getTime() + 6 * 24 * 60 * 60 * 1000).toLocaleDateString('es-ES', { 
                      day: 'numeric', 
                      month: 'long', 
                      year: 'numeric' 
                    })}`
                  : date.toLocaleDateString('es-ES', { 
                      weekday: 'long', 
                      day: 'numeric', 
                      month: 'long', 
                      year: 'numeric' 
                    })
              }
            >
              <Box sx={{ 
                width: 120, 
                flexShrink: 0, 
                p: 1, 
                textAlign: 'center',
                borderRight: '1px solid #e2e8f0',
                backgroundColor: '#f8fafc',
                borderBottom: '1px solid #e2e8f0',
                cursor: 'help'
              }}>
                <Typography variant="caption" sx={{ fontWeight: 600 }}>
                  {zoomLevel === 'day' && date.toLocaleDateString('es-ES', { day: '2-digit', month: '2-digit' })}
                  {zoomLevel === 'week' && `Sem ${date.toLocaleDateString('es-ES', { day: '2-digit', month: '2-digit' })}`}
                  {zoomLevel === 'month' && date.toLocaleDateString('es-ES', { month: 'short', year: '2-digit' })}
                </Typography>
              </Box>
            </Tooltip>
          ))}
        </Box>

        {/* Filas de actividades */}
        {filteredActivities.length === 0 ? (
          <Box sx={{ 
            display: 'flex', 
            justifyContent: 'center',
            alignItems: 'center',
            p: 4,
            borderBottom: '1px solid #e2e8f0'
          }}>
            <Typography variant="body2" color="text.secondary">
              No hay actividades para mostrar en el cronograma
            </Typography>
          </Box>
        ) : filteredActivities.map((activity) => (
          <Box key={activity.id} sx={{ 
            display: 'flex', 
            minWidth: 'max-content',
            borderBottom: '1px solid #e2e8f0',
            '&:hover': { backgroundColor: '#f8fafc' }
          }}>
            {/* Información de la actividad */}
            <Box sx={{ 
              width: 300, 
              flexShrink: 0, 
              p: 2, 
              borderRight: '1px solid #e2e8f0',
              display: 'flex',
              flexDirection: 'column',
              gap: 1
            }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <Typography variant="subtitle2" sx={{ fontWeight: 600, flex: 1 }}>
                  {activity.title}
                </Typography>
                <IconButton 
                  size="small" 
                  onClick={() => handleEditDates(activity)}
                  sx={{ ml: 1 }}
                >
                  <Edit fontSize="small" />
                </IconButton>
              </Box>
              
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Person fontSize="small" color="action" />
                <Typography variant="caption">{activity.assignee}</Typography>
              </Box>
              
              <Box sx={{ display: 'flex', gap: 1 }}>
                <Chip 
                  label={activity.status} 
                  size="small" 
                  sx={{ 
                    backgroundColor: activity.color, 
                    color: 'white',
                    fontSize: '0.7rem'
                  }} 
                />
                <Chip 
                  label={activity.priority} 
                  size="small" 
                  sx={{ 
                    backgroundColor: getPriorityColor(activity.priority), 
                    color: 'white',
                    fontSize: '0.7rem'
                  }} 
                />
              </Box>
            </Box>
            
            {/* Barras de tiempo */}
            <Box sx={{ 
              position: 'relative',
              height: 80,
              width: timeline.length * 120, // Ancho fijo basado en el número de columnas
              overflow: 'hidden'
            }}>
              {/* Barra de actividad continua */}
              <Box sx={{
                position: 'absolute',
                left: `${getTimelinePosition(activity.startDate)}px`,
                width: `${getTimelineWidth(activity.startDate, activity.endDate)}px`,
                height: '60%',
                top: '20%',
                backgroundColor: activity.color,
                borderRadius: 1,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                cursor: 'pointer',
                zIndex: 1,
                minWidth: '60px',
                '&:hover': {
                  opacity: 0.8,
                  transform: 'scale(1.02)'
                }
              }}>
                <Typography variant="caption" sx={{ color: 'white', fontWeight: 600 }}>
                  {activity.duration}d
                </Typography>
              </Box>
              
              {/* Línea de separación inicial */}
              <Box sx={{ 
                position: 'absolute',
                left: '0px',
                top: 0,
                bottom: 0,
                width: '1px',
                backgroundColor: '#e2e8f0',
                zIndex: 0
              }} />
              
              {/* Líneas de separación del timeline */}
              {timeline.map((_, dateIndex) => (
                <Box key={dateIndex} sx={{ 
                  position: 'absolute',
                  left: `${(dateIndex + 1) * 120}px`,
                  top: 0,
                  bottom: 0,
                  width: '1px',
                  backgroundColor: '#e2e8f0',
                  zIndex: 0
                }} />
              ))}
            </Box>
          </Box>
        ))}
      </Paper>

      {/* Leyenda */}
      <Paper sx={{ p: 2 }}>
        <Typography variant="subtitle2" sx={{ mb: 2, fontWeight: 600 }}>
          Leyenda
        </Typography>
        <Box sx={{ display: 'flex', gap: 3, flexWrap: 'wrap' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Box sx={{ width: 20, height: 12, backgroundColor: '#1976d2', borderRadius: 1 }} />
            <Typography variant="caption">Por Hacer</Typography>
          </Box>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Box sx={{ width: 20, height: 12, backgroundColor: '#ed6c02', borderRadius: 1 }} />
            <Typography variant="caption">En Progreso</Typography>
          </Box>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Box sx={{ width: 20, height: 12, backgroundColor: '#9c27b0', borderRadius: 1 }} />
            <Typography variant="caption">En Revisión</Typography>
          </Box>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Box sx={{ width: 20, height: 12, backgroundColor: '#2e7d32', borderRadius: 1 }} />
            <Typography variant="caption">Completado</Typography>
          </Box>
        </Box>
      </Paper>

      {/* Dialog para editar fechas */}
      <Dialog open={editDialogOpen} onClose={() => setEditDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Editar Fechas de Actividad</DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3, pt: 1 }}>
            <TextField
              fullWidth
              label="Fecha de Inicio"
              type="date"
              value={editForm.startDate}
              onChange={(e) => setEditForm({ ...editForm, startDate: e.target.value })}
              InputLabelProps={{ shrink: true }}
            />
            <TextField
              fullWidth
              label="Fecha de Finalización"
              type="date"
              value={editForm.endDate}
              onChange={(e) => setEditForm({ ...editForm, endDate: e.target.value })}
              InputLabelProps={{ shrink: true }}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditDialogOpen(false)}>Cancelar</Button>
          <Button onClick={handleSaveDates} variant="contained">Guardar</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

// Extensión de Date para obtener número de semana
declare global {
  interface Date {
    getWeek(): number;
  }
}

Date.prototype.getWeek = function() {
  const d = new Date(this.getTime());
  d.setHours(0, 0, 0, 0);
  d.setDate(d.getDate() + 4 - (d.getDay() || 7));
  const yearStart = new Date(d.getFullYear(), 0, 1);
  const weekNo = Math.ceil((((d.getTime() - yearStart.getTime()) / 86400000) + 1) / 7);
  return weekNo;
};

export default GanttChart;
