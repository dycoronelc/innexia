import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Chip,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  Button,
  TextField,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Checkbox,
  Tooltip,
  InputAdornment,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  Snackbar
} from '@mui/material';
import {
  Comment as CommentIcon,
  Label as LabelIcon,
  Checklist as ChecklistIcon,
  Person as PersonIcon,
  AttachFile as AttachFileIcon,
  CalendarToday as CalendarIcon,
  Flag as FlagIcon,
  Send as SendIcon,
  Close as CloseIcon,
  Delete as DeleteIcon
} from '@mui/icons-material';
import type { ProjectActivity } from '../types';
import { formatDate } from '../utils/dateUtils';
import { useActivityTrello } from '../hooks/useActivityTrello';
import { useAuth } from '../contexts/AuthContext';

// Estilos CSS para la animación de spin
const spinAnimation = `
  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
`;

// Agregar estilos al head del documento
if (!document.getElementById('spin-animation')) {
  const style = document.createElement('style');
  style.id = 'spin-animation';
  style.textContent = spinAnimation;
  document.head.appendChild(style);
}

interface ActivityCardProps {
  activity: ProjectActivity;
  onUpdate: (activity: ProjectActivity) => void;
  onDelete?: (id: string) => void | Promise<void>;
  availableTags: Array<{ id: string; name: string; color: string }>;
  availableUsers: Array<{ id: string; fullName: string; username: string; role: string }>;
  availableCategories: Array<{ id: string; name: string; color: string }>;
}

const ActivityCard: React.FC<ActivityCardProps> = ({
  activity,
  onUpdate,
  onDelete,
  availableTags,
  availableUsers,
  availableCategories
}) => {
  const { token } = useAuth();
  const [openDialog, setOpenDialog] = useState(false);
  const [newComment, setNewComment] = useState('');
  const [newChecklistTitle, setNewChecklistTitle] = useState('');
  const [newChecklistItem, setNewChecklistItem] = useState('');

  // Usar el hook personalizado para manejar las funcionalidades de Trello
  const {
    loading,
    error,
    success,
    assignees,
    comments,
    checklists,
    loadActivityData,
    addComment,
    deleteComment,
    createChecklist,
    addChecklistItem,
    toggleChecklistItem,
    deleteChecklistItem,
    clearMessages
  } = useActivityTrello({
    activityId: parseInt(activity.id),
    token: token || ''
  });

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return '#d32f2f';
      case 'medium': return '#ed6c02';
      case 'low': return '#2e7d32';
      default: return '#757575';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return '#2e7d32';
      case 'in-progress': return '#1976d2';
      case 'review': return '#ed6c02';
      case 'todo': return '#757575';
      default: return '#757575';
    }
  };

  // Cargar datos cuando se abre el diálogo
  useEffect(() => {
    if (openDialog && token) {
      loadActivityData();
    }
  }, [openDialog, token, loadActivityData]);

  // Evitar re-renderizados innecesarios
  const handleUpdateActivity = (updatedActivity: ProjectActivity) => {
    // Solo actualizar si realmente hay cambios
    const hasChanges = JSON.stringify(updatedActivity) !== JSON.stringify(activity);
    if (hasChanges) {
      onUpdate(updatedActivity);
    }
  };

  const handleAddComment = async () => {
    if (!newComment.trim() || loading) return;
    
    try {
      await addComment(newComment);
      setNewComment('');
    } catch (error) {
      console.error('Error adding comment:', error);
      // El error ya se maneja en el hook
    }
  };

  const handleDeleteComment = async (commentId: number) => {
    if (loading) return;
    
    try {
      await deleteComment(commentId);
    } catch (error) {
      console.error('Error deleting comment:', error);
      // El error ya se maneja en el hook
    }
  };

  const handleAddChecklist = async () => {
    if (!newChecklistTitle.trim() || loading) return;
    
    try {
      await createChecklist(newChecklistTitle);
      setNewChecklistTitle('');
    } catch (error) {
      console.error('Error creating checklist:', error);
      // El error ya se maneja en el hook
    }
  };

  const handleAddChecklistItem = async (checklistId: number) => {
    if (!newChecklistItem.trim() || loading) return;
    
    try {
      await addChecklistItem(checklistId, newChecklistItem);
      setNewChecklistItem('');
    } catch (error) {
      console.error('Error adding checklist item:', error);
      // El error ya se maneja en el hook
    }
  };

  const handleToggleChecklistItem = async (itemId: number) => {
    if (loading) return;
    
    try {
      await toggleChecklistItem(itemId);
    } catch (error) {
      console.error('Error toggling checklist item:', error);
      // El error ya se maneja en el hook
    }
  };

  const handleDeleteChecklistItem = async (itemId: number) => {
    if (loading) return;
    
    try {
      await deleteChecklistItem(itemId);
    } catch (error) {
      console.error('Error deleting checklist item:', error);
      // El error ya se maneja en el hook
    }
  };

  const getTagName = (tagId: string) => {
    const tag = availableTags.find(t => t.id === tagId);
    return tag ? tag.name : 'Etiqueta desconocida';
  };

  const getTagColor = (tagId: string) => {
    const tag = availableTags.find(t => t.id === tagId);
    return tag ? tag.color : '#757575';
  };

  const getCategoryColor = (categoryId: string) => {
    const category = availableCategories.find(c => c.id === categoryId);
    return category ? category.color : '#757575';
  };

  // Filtrar usuarios que no sean admin
  const filteredUsers = availableUsers.filter(user => user.role !== 'admin');
  
  // Fallback para usuarios de prueba si no hay datos
  const usersToShow = filteredUsers.length > 0 ? filteredUsers : [
    { id: '1', fullName: 'Juan Pérez', username: 'juan', role: 'user' },
    { id: '2', fullName: 'María García', username: 'maria', role: 'user' },
    { id: '3', fullName: 'Carlos López', username: 'carlos', role: 'user' }
  ];

  const completedChecklistItems = checklists.reduce(
    (total, checklist) => total + checklist.items.filter(item => item.completed).length,
    0
  );

  const totalChecklistItems = checklists.reduce(
    (total, checklist) => total + checklist.items.length,
    0
  );

  return (
    <>
      <Card 
        sx={{ 
          mb: 2, 
          cursor: 'pointer',
          '&:hover': { boxShadow: 3 },
          transition: 'box-shadow 0.2s'
        }}
        onClick={() => setOpenDialog(true)}
      >
        <CardContent sx={{ p: 2 }}>
          {/* Labels */}
          {activity.labels.length > 0 && (
            <Box sx={{ display: 'flex', gap: 0.5, mb: 1, flexWrap: 'wrap' }}>
              {activity.labels.map(labelId => (
                <Box
                  key={labelId}
                  sx={{
                    width: 40,
                    height: 8,
                    borderRadius: 1,
                    backgroundColor: getCategoryColor(labelId),
                    flexShrink: 0
                  }}
                />
              ))}
            </Box>
          )}

          {/* Title */}
          <Typography variant="h6" sx={{ mb: 1, fontWeight: 600 }}>
            {activity.title}
          </Typography>

          {/* Description */}
          {activity.description && (
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              {activity.description.length > 100 
                ? `${activity.description.substring(0, 100)}...` 
                : activity.description
              }
            </Typography>
          )}

          {/* Tags */}
          {activity.tags.length > 0 && (
            <Box sx={{ display: 'flex', gap: 0.5, mb: 1, flexWrap: 'wrap' }}>
              {activity.tags.slice(0, 3).map(tagId => (
                <Chip
                  key={tagId}
                  label={getTagName(tagId)}
                  size="small"
                  sx={{ 
                    backgroundColor: getTagColor(tagId),
                    color: 'white',
                    fontSize: '0.7rem'
                  }}
                />
              ))}
              {activity.tags.length > 3 && (
                <Chip
                  label={`+${activity.tags.length - 3}`}
                  size="small"
                  variant="outlined"
                  sx={{ fontSize: '0.7rem' }}
                />
              )}
            </Box>
          )}

          {/* Bottom row with metadata */}
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mt: 2 }}>
            <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
              {/* Priority */}
              <Tooltip title={`Prioridad: ${activity.priority}`}>
                <FlagIcon 
                  sx={{ 
                    fontSize: 16, 
                    color: getPriorityColor(activity.priority) 
                  }} 
                />
              </Tooltip>

              {/* Due date */}
              <Tooltip title={`Vence: ${formatDate(activity.dueDate)}`}>
                <CalendarIcon sx={{ fontSize: 16, color: '#757575' }} />
              </Tooltip>

              {/* Assignees */}
              {assignees.length > 0 && (
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                  <PersonIcon sx={{ fontSize: 16, color: '#757575' }} />
                  <Typography variant="caption" color="text.secondary">
                    {assignees.length}
                  </Typography>
                </Box>
              )}

              {/* Comments */}
              {comments.length > 0 && (
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                  <CommentIcon sx={{ fontSize: 16, color: '#757575' }} />
                  <Typography variant="caption" color="text.secondary">
                    {comments.length}
                  </Typography>
                </Box>
              )}

              {/* Checklist progress */}
              {totalChecklistItems > 0 && (
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                  <ChecklistIcon sx={{ fontSize: 16, color: '#757575' }} />
                  <Typography variant="caption" color="text.secondary">
                    {completedChecklistItems}/{totalChecklistItems}
                  </Typography>
                </Box>
              )}
            </Box>

            {/* Status */}
            <Chip
              label={activity.status === 'in-progress' ? 'En Progreso' : 
                     activity.status === 'completed' ? 'Completada' :
                     activity.status === 'review' ? 'En Revisión' : 'Por Hacer'}
              size="small"
              sx={{ 
                backgroundColor: getStatusColor(activity.status),
                color: 'white',
                fontSize: '0.7rem'
              }}
            />
          </Box>
        </CardContent>
      </Card>

      {/* Detailed Dialog */}
      <Dialog 
        open={openDialog} 
        onClose={() => setOpenDialog(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle sx={{ pb: 1 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography variant="h6" sx={{ fontWeight: 600 }}>
              {activity.title}
            </Typography>
            <IconButton onClick={() => setOpenDialog(false)}>
              <CloseIcon />
            </IconButton>
          </Box>
        </DialogTitle>

        <DialogContent sx={{ pt: 0 }}>
          <Box sx={{ display: 'flex', gap: 3 }}>
            {/* Main content */}
            <Box sx={{ flex: 1 }}>
              {/* Basic Information */}
              <Box sx={{ mb: 3 }}>
                <Typography variant="subtitle2" sx={{ mb: 2, fontWeight: 600 }}>
                  Información básica
                </Typography>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                  {/* Title */}
                  <TextField
                    fullWidth
                    label="Título"
                    value={activity.title}
                    onChange={(e) => {
                      const updatedActivity = {
                        ...activity,
                        title: e.target.value
                      };
                      handleUpdateActivity(updatedActivity);
                    }}
                    size="small"
                  />
                  
                  {/* Description */}
                  <TextField
                    fullWidth
                    label="Descripción"
                    value={activity.description}
                    onChange={(e) => {
                      const updatedActivity = {
                        ...activity,
                        description: e.target.value
                      };
                      handleUpdateActivity(updatedActivity);
                    }}
                    multiline
                    rows={3}
                    size="small"
                  />

                  {/* Status and Priority */}
                  <Box sx={{ display: 'flex', gap: 2 }}>
                    <FormControl size="small" sx={{ flex: 1 }}>
                      <InputLabel>Estado</InputLabel>
                      <Select
                        value={activity.status}
                        label="Estado"
                        onChange={(e: any) => {
                          const updatedActivity = {
                            ...activity,
                            status: e.target.value as 'todo' | 'in-progress' | 'review' | 'completed'
                          };
                          handleUpdateActivity(updatedActivity);
                        }}
                      >
                        <MenuItem value="todo">Por Hacer</MenuItem>
                        <MenuItem value="in-progress">En Progreso</MenuItem>
                        <MenuItem value="review">En Revisión</MenuItem>
                        <MenuItem value="completed">Completado</MenuItem>
                      </Select>
                    </FormControl>

                    <FormControl size="small" sx={{ flex: 1 }}>
                      <InputLabel>Prioridad</InputLabel>
                      <Select
                        value={activity.priority}
                        label="Prioridad"
                        onChange={(e: any) => {
                          const updatedActivity = {
                            ...activity,
                            priority: e.target.value as 'low' | 'medium' | 'high'
                          };
                          handleUpdateActivity(updatedActivity);
                        }}
                      >
                        <MenuItem value="low">Baja</MenuItem>
                        <MenuItem value="medium">Media</MenuItem>
                        <MenuItem value="high">Alta</MenuItem>
                      </Select>
                    </FormControl>
                  </Box>

                  {/* Assignees */}
                  <FormControl size="small" fullWidth>
                    <InputLabel>Responsables</InputLabel>
                    <Select
                      multiple
                      value={activity.assignees}
                      label="Responsables"
                      onChange={(e: any) => {
                        const updatedActivity = {
                          ...activity,
                          assignees: e.target.value
                        };
                        handleUpdateActivity(updatedActivity);
                      }}
                      renderValue={(selected) => (
                        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                          {selected.map((value: string) => {
                            const user = usersToShow.find(u => u.id === value);
                            return (
                              <Chip
                                key={value}
                                label={user ? user.fullName : 'Usuario desconocido'}
                                size="small"
                                sx={{ fontSize: '0.7rem' }}
                              />
                            );
                          })}
                        </Box>
                      )}
                    >
                      {usersToShow.map((user) => (
                        <MenuItem key={user.id} value={user.id}>
                          {user.fullName}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Box>
              </Box>

              {/* Dates section */}
              <Box sx={{ mb: 3 }}>
                <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 600 }}>
                  Fechas
                </Typography>
                <Box sx={{ display: 'flex', gap: 2 }}>
                  <TextField
                    label="Fecha de inicio"
                    type="date"
                    value={activity.startDate.toISOString().split('T')[0]}
                    onChange={(e) => {
                      const updatedActivity = {
                        ...activity,
                        startDate: new Date(e.target.value)
                      };
                      handleUpdateActivity(updatedActivity);
                    }}
                    size="small"
                    sx={{ flex: 1 }}
                    InputLabelProps={{ shrink: true }}
                  />
                  <TextField
                    label="Fecha de fin"
                    type="date"
                    value={activity.dueDate.toISOString().split('T')[0]}
                    onChange={(e) => {
                      const updatedActivity = {
                        ...activity,
                        dueDate: new Date(e.target.value)
                      };
                      handleUpdateActivity(updatedActivity);
                    }}
                    size="small"
                    sx={{ flex: 1 }}
                    InputLabelProps={{ shrink: true }}
                  />
                </Box>
              </Box>

              {/* Add section */}
              <Box sx={{ mb: 3 }}>
                <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 600 }}>
                  Añadir a la actividad
                </Typography>
                <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                  <Button
                    variant="outlined"
                    size="small"
                    startIcon={<LabelIcon />}
                    onClick={() => {/* TODO: Open labels menu */}}
                  >
                    Etiquetas
                  </Button>
                  <Button
                    variant="outlined"
                    size="small"
                    startIcon={<ChecklistIcon />}
                    onClick={() => setNewChecklistTitle('')}
                  >
                    Checklist
                  </Button>
                  <Button
                    variant="outlined"
                    size="small"
                    startIcon={<AttachFileIcon />}
                    onClick={() => {/* TODO: Open attachments menu */}}
                  >
                    Adjuntos
                  </Button>
                </Box>
              </Box>

              {/* Checklists */}
              {checklists.length > 0 && (
                <Box sx={{ mb: 3 }}>
                  <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 600 }}>
                    Checklists
                  </Typography>
                  {checklists.map(checklist => (
                    <Box key={checklist.id} sx={{ mb: 2 }}>
                      <Typography variant="body2" sx={{ mb: 1, fontWeight: 500 }}>
                        {checklist.title}
                      </Typography>
                      <List dense>
                        {checklist.items.map(item => (
                          <ListItem key={item.id} sx={{ py: 0 }}>
                            <ListItemIcon sx={{ minWidth: 32 }}>
                              <Checkbox
                                checked={item.completed}
                                onChange={() => handleToggleChecklistItem(item.id)}
                                size="small"
                                disabled={loading}
                              />
                            </ListItemIcon>
                            <ListItemText
                              primary={item.content}
                              sx={{
                                textDecoration: item.completed ? 'line-through' : 'none',
                                color: item.completed ? 'text.secondary' : 'text.primary'
                              }}
                            />
                            <IconButton
                              size="small"
                              onClick={() => handleDeleteChecklistItem(item.id)}
                              disabled={loading}
                            >
                              <DeleteIcon fontSize="small" />
                            </IconButton>
                          </ListItem>
                        ))}
                      </List>
                      <Box sx={{ display: 'flex', gap: 1, mt: 1 }}>
                        <TextField
                          size="small"
                          placeholder="Añadir elemento..."
                          value={newChecklistItem}
                          onChange={(e) => setNewChecklistItem(e.target.value)}
                          onKeyPress={(e) => {
                            if (e.key === 'Enter') {
                              handleAddChecklistItem(checklist.id);
                            }
                          }}
                          sx={{ flex: 1 }}
                          disabled={loading}
                        />
                        <Button
                          size="small"
                          onClick={() => handleAddChecklistItem(checklist.id)}
                          disabled={!newChecklistItem.trim() || loading}
                        >
                          Añadir
                        </Button>
                      </Box>
                      {loading && (
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 1 }}>
                          <Box sx={{ width: 12, height: 12, border: '2px solid #e0e0e0', borderTop: '2px solid #1976d2', borderRadius: '50%', animation: 'spin 1s linear infinite' }} />
                          <Typography variant="caption" color="text.secondary">
                            Agregando elemento...
                          </Typography>
                        </Box>
                      )}
                    </Box>
                  ))}
                </Box>
              )}

              {/* Add new checklist */}
              <Box sx={{ mb: 3 }}>
                <TextField
                  fullWidth
                  size="small"
                  placeholder="Añadir checklist..."
                  value={newChecklistTitle}
                  onChange={(e) => setNewChecklistTitle(e.target.value)}
                  onKeyPress={(e) => {
                    if (e.key === 'Enter') {
                      handleAddChecklist();
                    }
                  }}
                  InputProps={{
                    endAdornment: (
                      <InputAdornment position="end">
                        <Button
                          size="small"
                          onClick={handleAddChecklist}
                          disabled={!newChecklistTitle.trim() || loading}
                        >
                          Añadir
                        </Button>
                      </InputAdornment>
                    )
                  }}
                  disabled={loading}
                />
                {loading && (
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 1 }}>
                    <Box sx={{ width: 16, height: 16, border: '2px solid #e0e0e0', borderTop: '2px solid #1976d2', borderRadius: '50%', animation: 'spin 1s linear infinite' }} />
                    <Typography variant="caption" color="text.secondary">
                      Creando checklist...
                    </Typography>
                  </Box>
                )}
              </Box>
            </Box>

            {/* Sidebar */}
            <Box sx={{ width: 300 }}>
              <Typography variant="subtitle2" sx={{ mb: 2, fontWeight: 600 }}>
                Comentarios y Actividad
              </Typography>

              {/* Comments */}
              <Box sx={{ mb: 3 }}>
                <TextField
                  fullWidth
                  multiline
                  rows={3}
                  placeholder="Escribe un comentario..."
                  value={newComment}
                  onChange={(e) => setNewComment(e.target.value)}
                  InputProps={{
                    endAdornment: (
                      <InputAdornment position="end">
                        <IconButton
                          onClick={handleAddComment}
                          disabled={!newComment.trim() || loading}
                          size="small"
                        >
                          <SendIcon />
                        </IconButton>
                      </InputAdornment>
                    )
                  }}
                  disabled={loading}
                />
                {loading && (
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 1 }}>
                    <Box sx={{ width: 16, height: 16, border: '2px solid #e0e0e0', borderTop: '2px solid #1976d2', borderRadius: '50%', animation: 'spin 1s linear infinite' }} />
                    <Typography variant="caption" color="text.secondary">
                      Guardando comentario...
                    </Typography>
                  </Box>
                )}
              </Box>

              {/* Comments list */}
              <List dense>
                {comments.map(comment => (
                  <ListItem key={comment.id} sx={{ px: 0 }}>
                    <ListItemText
                      primary={comment.content}
                      secondary={`${comment.author_name} - ${formatDate(new Date(comment.created_at))}`}
                      primaryTypographyProps={{ variant: 'body2' }}
                      secondaryTypographyProps={{ variant: 'caption' }}
                    />
                    <IconButton
                      size="small"
                      onClick={() => handleDeleteComment(comment.id)}
                      disabled={loading}
                    >
                      <DeleteIcon fontSize="small" />
                    </IconButton>
                  </ListItem>
                ))}
              </List>
            </Box>
          </Box>
        </DialogContent>
      </Dialog>

      {/* Notifications */}
      <Snackbar
        open={!!error}
        autoHideDuration={6000}
        onClose={clearMessages}
      >
        <Alert onClose={clearMessages} severity="error">
          {error}
        </Alert>
      </Snackbar>

      <Snackbar
        open={!!success}
        autoHideDuration={3000}
        onClose={clearMessages}
      >
        <Alert onClose={clearMessages} severity="success">
          {success}
        </Alert>
      </Snackbar>
    </>
  );
};

export default ActivityCard;
