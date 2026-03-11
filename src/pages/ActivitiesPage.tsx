import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Button,
  Paper,
  Grid,
  Chip,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Alert
} from '@mui/material';
import {
  Add as AddIcon,
  FilterList as FilterIcon,
  Assignment as AssignmentIcon,
  CalendarToday as CalendarIcon
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import { activityService, masterService, userService } from '../services/api';
import ActivityCard from '../components/ActivityCard';
import type { ProjectActivity, Category, Tag, User } from '../types';

const ActivitiesPage: React.FC = () => {
  const { token } = useAuth();
  const [activities, setActivities] = useState<ProjectActivity[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [tags, setTags] = useState<Tag[]>([]);
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [openDialog, setOpenDialog] = useState(false);
  const [filters, setFilters] = useState({
    status: '',
    priority: '',
    assignee: '',
    project: ''
  });

  useEffect(() => {
    if (token) {
      fetchData();
    }
  }, [token]);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [activitiesRes, categoriesRes, tagsRes, usersRes] = await Promise.all([
        activityService.getActivities(token!),
        masterService.getCategories(token!),
        masterService.getTags(token!),
        userService.getUsers(token!)
      ]);

      if (activitiesRes.status === 'success') {
        // Procesar actividades para incluir las nuevas propiedades
        const processedActivities = activitiesRes.data.map((activity: any) => ({
          ...activity,
          id: activity.id.toString(),
          assignees: activity.assignees || [activity.assignee || ''],
          tags: activity.tags || [],
          comments: activity.comments || [],
          checklists: activity.checklists || [],
          attachments: activity.attachments || [],
          labels: activity.labels || [],
          startDate: activity.start_date ? new Date(activity.start_date) : new Date(),
          dueDate: activity.due_date ? new Date(activity.due_date) : new Date(),
          createdAt: activity.created_at ? new Date(activity.created_at) : new Date(),
          updatedAt: activity.updated_at ? new Date(activity.updated_at) : new Date()
        }));
        setActivities(processedActivities);
      }

      if (categoriesRes.status === 'success') {
        setCategories(categoriesRes.data || []);
      }

      if (tagsRes.status === 'success') {
        setTags(tagsRes.data || []);
      }

      if (usersRes.status === 'success') {
        setUsers(usersRes.data || []);
      }
    } catch (error) {
      console.error('Error fetching data:', error);
      setError('Error al cargar los datos');
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateActivity = async (updatedActivity: ProjectActivity) => {
    try {
      // TODO: Implementar actualización en el backend
      setActivities(prev => 
        prev.map(activity => 
          activity.id === updatedActivity.id ? updatedActivity : activity
        )
      );
    } catch (error) {
      console.error('Error updating activity:', error);
      setError('Error al actualizar la actividad');
    }
  };

  const handleDeleteActivity = async (id: string) => {
    try {
      // TODO: Implementar eliminación en el backend
      setActivities(prev => prev.filter(activity => activity.id !== id));
    } catch (error) {
      console.error('Error deleting activity:', error);
      setError('Error al eliminar la actividad');
    }
  };

  const filteredActivities = activities.filter(activity => {
    if (filters.status && activity.status !== filters.status) return false;
    if (filters.priority && activity.priority !== filters.priority) return false;
    if (filters.assignee && !activity.assignees.includes(filters.assignee)) return false;
    return true;
  });

  const groupedActivities = {
    todo: filteredActivities.filter(a => a.status === 'todo'),
    'in-progress': filteredActivities.filter(a => a.status === 'in-progress'),
    review: filteredActivities.filter(a => a.status === 'review'),
    completed: filteredActivities.filter(a => a.status === 'completed')
  };

  if (loading) {
    return (
      <Box sx={{ p: 3 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Cargando actividades...
        </Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <AssignmentIcon color="primary" sx={{ fontSize: 32 }} />
          <Typography variant="h4" component="h1">
            Actividades
          </Typography>
        </Box>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setOpenDialog(true)}
        >
          Nueva Actividad
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {/* Filters */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
          <FormControl size="small" sx={{ minWidth: 120 }}>
            <InputLabel>Estado</InputLabel>
            <Select
              value={filters.status}
              label="Estado"
              onChange={(e) => setFilters({ ...filters, status: e.target.value })}
            >
              <MenuItem value="">Todos</MenuItem>
              <MenuItem value="todo">Por Hacer</MenuItem>
              <MenuItem value="in-progress">En Progreso</MenuItem>
              <MenuItem value="review">En Revisión</MenuItem>
              <MenuItem value="completed">Completadas</MenuItem>
            </Select>
          </FormControl>

          <FormControl size="small" sx={{ minWidth: 120 }}>
            <InputLabel>Prioridad</InputLabel>
            <Select
              value={filters.priority}
              label="Prioridad"
              onChange={(e) => setFilters({ ...filters, priority: e.target.value })}
            >
              <MenuItem value="">Todas</MenuItem>
              <MenuItem value="low">Baja</MenuItem>
              <MenuItem value="medium">Media</MenuItem>
              <MenuItem value="high">Alta</MenuItem>
            </Select>
          </FormControl>

          <FormControl size="small" sx={{ minWidth: 150 }}>
            <InputLabel>Responsable</InputLabel>
            <Select
              value={filters.assignee}
              label="Responsable"
              onChange={(e) => setFilters({ ...filters, assignee: e.target.value })}
            >
              <MenuItem value="">Todos</MenuItem>
              {users.map(user => (
                <MenuItem key={user.id} value={user.id}>
                  {user.fullName}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Box>
      </Paper>

      {/* Kanban Board */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={3}>
          <Paper sx={{ p: 2, height: 'fit-content' }}>
            <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
              Por Hacer ({groupedActivities.todo.length})
            </Typography>
                         {groupedActivities.todo.map(activity => (
               <ActivityCard
                 key={activity.id}
                 activity={activity}
                 onUpdate={handleUpdateActivity}
                 onDelete={handleDeleteActivity}
                 availableTags={tags.map(t => ({ id: t.id, name: t.name, color: t.color }))}
                 availableUsers={users.map(u => ({ id: u.id, fullName: u.fullName, username: u.username, role: u.role }))}
                 availableCategories={categories.map(c => ({ id: c.id, name: c.name, color: c.color }))}
               />
             ))}
          </Paper>
        </Grid>

        <Grid item xs={12} md={3}>
          <Paper sx={{ p: 2, height: 'fit-content' }}>
            <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
              En Progreso ({groupedActivities['in-progress'].length})
            </Typography>
                         {groupedActivities['in-progress'].map(activity => (
               <ActivityCard
                 key={activity.id}
                 activity={activity}
                 onUpdate={handleUpdateActivity}
                 onDelete={handleDeleteActivity}
                 availableTags={tags.map(t => ({ id: t.id, name: t.name, color: t.color }))}
                 availableUsers={users.map(u => ({ id: u.id, fullName: u.fullName, username: u.username, role: u.role }))}
                 availableCategories={categories.map(c => ({ id: c.id, name: c.name, color: c.color }))}
               />
             ))}
          </Paper>
        </Grid>

        <Grid item xs={12} md={3}>
          <Paper sx={{ p: 2, height: 'fit-content' }}>
            <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
              En Revisión ({groupedActivities.review.length})
            </Typography>
                         {groupedActivities.review.map(activity => (
               <ActivityCard
                 key={activity.id}
                 activity={activity}
                 onUpdate={handleUpdateActivity}
                 onDelete={handleDeleteActivity}
                 availableTags={tags.map(t => ({ id: t.id, name: t.name, color: t.color }))}
                 availableUsers={users.map(u => ({ id: u.id, fullName: u.fullName, username: u.username, role: u.role }))}
                 availableCategories={categories.map(c => ({ id: c.id, name: c.name, color: c.color }))}
               />
             ))}
          </Paper>
        </Grid>

        <Grid item xs={12} md={3}>
          <Paper sx={{ p: 2, height: 'fit-content' }}>
            <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
              Completadas ({groupedActivities.completed.length})
            </Typography>
                         {groupedActivities.completed.map(activity => (
               <ActivityCard
                 key={activity.id}
                 activity={activity}
                 onUpdate={handleUpdateActivity}
                 onDelete={handleDeleteActivity}
                 availableTags={tags.map(t => ({ id: t.id, name: t.name, color: t.color }))}
                 availableUsers={users.map(u => ({ id: u.id, fullName: u.fullName, username: u.username, role: u.role }))}
                 availableCategories={categories.map(c => ({ id: c.id, name: c.name, color: c.color }))}
               />
             ))}
          </Paper>
        </Grid>
      </Grid>

      {/* New Activity Dialog */}
      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>Nueva Actividad</DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary">
            Funcionalidad de creación de actividades en desarrollo...
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDialog(false)}>Cerrar</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ActivitiesPage;
