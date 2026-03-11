import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  Menu,
  ListItemIcon,
  ListItemText,
  Snackbar
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  LocalOffer,
  MoreVert as MoreVertIcon,
  CalendarToday as CalendarIcon
} from '@mui/icons-material';
import { DataGrid, GridActionsCellItem } from '@mui/x-data-grid';
import type { GridColDef } from '@mui/x-data-grid';
import type { Tag } from '../types';
import { masterService } from '../services/api';
import { formatDate } from '../utils/dateUtils';
import ConfirmationDialog from '../components/ConfirmationDialog';

const TagsPage: React.FC = () => {
  const [tags, setTags] = useState<Tag[]>([]);
  const [loading, setLoading] = useState(true);
  const [openDialog, setOpenDialog] = useState(false);
  const [editingTag, setEditingTag] = useState<Tag | null>(null);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    color: '#1976d2',
    active: true
  });
  const [error, setError] = useState('');
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [selectedTag, setSelectedTag] = useState<Tag | null>(null);
  
  // Estados para el diálogo de confirmación
  const [confirmationDialog, setConfirmationDialog] = useState({
    open: false,
    title: '',
    message: '',
    severity: 'warning' as 'warning' | 'error' | 'info',
    onConfirm: () => {},
    loading: false
  });
  
  // Estados para notificaciones
  const [snackbar, setSnackbar] = useState({
    open: false,
    message: '',
    severity: 'success' as 'success' | 'error' | 'warning' | 'info'
  });

  useEffect(() => {
    fetchTags();
  }, []);

  const fetchTags = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('innexia_token');
      if (!token) {
        throw new Error('No hay token de autenticación. Por favor, inicie sesión nuevamente.');
      }
      
      const response = await masterService.getTags(token);
      if (response.status === 'success') {
        console.log('Tags data:', response.data);
        // Asegurarnos de que las fechas se manejen correctamente
        const processedData = (response.data || []).map((tag: { created_at?: string | null; updated_at?: string | null; [key: string]: unknown }) => ({
          ...tag,
          created_at: tag.created_at || null,
          updated_at: tag.updated_at || null
        }));
        console.log('Processed tags data:', processedData);
        setTags(processedData);
      } else {
        throw new Error(response.error || 'Error al cargar las etiquetas');
      }
    } catch (error) {
      console.error('Error fetching tags:', error);
      if (error instanceof Error) {
        setError(error.message);
      } else {
        setError('Error al cargar las etiquetas desde la base de datos');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleOpenDialog = (tag?: Tag) => {
    if (tag) {
      setEditingTag(tag);
      setFormData({
        name: tag.name,
        description: tag.description,
        color: tag.color,
        active: tag.active
      });
    } else {
      setEditingTag(null);
      setFormData({
        name: '',
        description: '',
        color: '#1976d2',
        active: true
      });
    }
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setEditingTag(null);
    setFormData({
      name: '',
      description: '',
      color: '#1976d2',
      active: true
    });
  };

  const handleSubmit = async () => {
    try {
      const token = localStorage.getItem('innexia_token');
      if (!token) {
        throw new Error('No hay token de autenticación. Por favor, inicie sesión nuevamente.');
      }

      if (editingTag) {
        // Update existing tag
        const response = await masterService.updateTag(editingTag.id, formData, token);
        if (response.status === 'success') {
          await fetchTags(); // Recargar etiquetas
        } else {
          throw new Error(response.error || 'Error al actualizar la etiqueta');
        }
      } else {
        // Create new tag
        const response = await masterService.createTag(formData, token);
        if (response.status === 'success') {
          await fetchTags(); // Recargar etiquetas
        } else {
          throw new Error(response.error || 'Error al crear la etiqueta');
        }
      }
      handleCloseDialog();
    } catch (error) {
      console.error('Error saving tag:', error);
      if (error instanceof Error) {
        setError(error.message);
      } else {
        setError('Error al guardar la etiqueta');
      }
    }
  };

  const showConfirmationDialog = (
    title: string,
    message: string,
    onConfirm: () => void,
    severity: 'warning' | 'error' | 'info' = 'warning'
  ) => {
    setConfirmationDialog({
      open: true,
      title,
      message,
      severity,
      onConfirm,
      loading: false
    });
  };

  const closeConfirmationDialog = () => {
    setConfirmationDialog(prev => ({ ...prev, open: false }));
  };

  const handleDelete = async (id: string) => {
    const tag = tags.find(t => t.id === id);
    const tagName = tag?.name || 'esta etiqueta';
    
    showConfirmationDialog(
      'Eliminar Etiqueta',
      `¿Está seguro de que desea eliminar la etiqueta "${tagName}"? Esta acción no se puede deshacer.`,
      () => performDelete(id),
      'error'
    );
  };

  const performDelete = async (id: string) => {
    setConfirmationDialog(prev => ({ ...prev, loading: true }));
    
    try {
      const token = localStorage.getItem('innexia_token');
      if (!token) {
        throw new Error('No hay token de autenticación. Por favor, inicie sesión nuevamente.');
      }

      const response = await masterService.deleteTag(id, token);
      if (response.status === 'success') {
        // Actualizar lista localmente para actualización inmediata
        setTags(prev => prev.filter(t => t.id !== id));
        
        // Mostrar mensaje de éxito
        setSnackbar({
          open: true,
          message: 'Etiqueta eliminada exitosamente',
          severity: 'success'
        });
        
        closeConfirmationDialog();
      } else {
        setSnackbar({
          open: true,
          message: response.error || 'Error al eliminar la etiqueta',
          severity: 'error'
        });
      }
    } catch (error) {
      console.error('Error deleting tag:', error);
      const errorMessage = error instanceof Error ? error.message : 'Error al eliminar la etiqueta';
      setSnackbar({
        open: true,
        message: errorMessage,
        severity: 'error'
      });
    } finally {
      setConfirmationDialog(prev => ({ ...prev, loading: false }));
    }
  };

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>, tag: Tag) => {
    event.stopPropagation();
    setAnchorEl(event.currentTarget);
    setSelectedTag(tag);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
    setSelectedTag(null);
  };

  const handleEditTag = (tag: Tag) => {
    handleMenuClose();
    handleOpenDialog(tag);
  };

  const handleToggleActive = async (id: string) => {
    handleMenuClose();
    try {
      const token = localStorage.getItem('innexia_token');
      if (!token) {
        throw new Error('No hay token de autenticación. Por favor, inicie sesión nuevamente.');
      }

      const tag = tags.find(t => t.id === id);
      if (!tag) {
        throw new Error('Etiqueta no encontrada');
      }

      const response = await masterService.updateTag(id, { ...tag, active: !tag.active }, token);
      if (response.status === 'success') {
        await fetchTags(); // Recargar etiquetas
      } else {
        throw new Error(response.error || 'Error al actualizar el estado de la etiqueta');
      }
    } catch (error) {
      console.error('Error toggling tag status:', error);
      if (error instanceof Error) {
        setError(error.message);
      } else {
        setError('Error al actualizar el estado de la etiqueta');
      }
    }
  };

  const handleDeleteTag = (id: string) => {
    handleMenuClose();
    handleDelete(id);
  };

  const handleCloseSnackbar = () => {
    setSnackbar(prev => ({ ...prev, open: false }));
  };



  // Función para obtener el color del avatar basado en el nombre de la etiqueta
  const getAvatarColor = (name: string) => {
    const colors = ['#4D2581', '#f5576c', '#4facfe', '#fa709a', '#10b981', '#3b82f6', '#f59e0b', '#8b5cf6'];
    const index = name.charCodeAt(0) % colors.length;
    return colors[index];
  };

  const columns: GridColDef[] = [
    {
      field: 'actions',
      type: 'actions',
      headerName: 'Acciones',
      width: 100,
      sortable: false,
      filterable: false,
      getActions: (params) => [
        <GridActionsCellItem
          icon={<MoreVertIcon />}
          label="Acciones"
          onClick={(event) => handleMenuOpen(event, params.row)}
        />
      ]
    },
    {
      field: 'name',
      headerName: 'Etiqueta',
      flex: 1,
      minWidth: 250,
      renderCell: (params) => (
        <Box sx={{ 
          display: 'flex', 
          alignItems: 'center', 
          gap: 2,
          height: '100%',
          justifyContent: 'flex-start'
        }}>
          <Box
            sx={{
              width: 40,
              height: 40,
              borderRadius: '50%',
              backgroundColor: params.row.color || getAvatarColor(params.value),
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'white',
              fontSize: '1rem',
              fontWeight: 600,
              flexShrink: 0
            }}
          >
            {params.value.charAt(0).toUpperCase()}
          </Box>
          <Box sx={{ display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
            <Typography variant="body2" sx={{ fontWeight: 600, color: '#1e293b', mb: 0.5 }}>
              {params.value}
            </Typography>
            <Typography variant="caption" sx={{ color: '#64748b' }}>
              ID: {params.row.id}
            </Typography>
          </Box>
        </Box>
      )
    },
    {
      field: 'description',
      headerName: 'Descripción',
      flex: 1.5,
      minWidth: 300,
      renderCell: (params) => (
        <Typography variant="body2" color="text.secondary" sx={{ 
          overflow: 'hidden',
          textOverflow: 'ellipsis',
          whiteSpace: 'nowrap',
          maxWidth: 280
        }}>
          {params.value}
        </Typography>
      )
    },
    {
      field: 'active',
      headerName: 'Estado',
      width: 120,
      renderCell: (params) => (
        <Chip
          label={params.value ? 'Activa' : 'Inactiva'}
          size="small"
          color={params.value ? 'success' : 'default'}
          sx={{ borderRadius: 2 }}
        />
      )
    },
    {
      field: 'created_at',
      headerName: 'Creada',
      width: 120,
      renderCell: (params) => (
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <CalendarIcon sx={{ fontSize: 16, color: '#64748b' }} />
          <Typography variant="body2" color="text.secondary">
            {formatDate(params.value)}
          </Typography>
        </Box>
      )
    }
  ];

  if (loading) {
    return (
      <Box sx={{ width: '100%' }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Cargando etiquetas...
        </Typography>
      </Box>
    );
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <LocalOffer color="primary" sx={{ fontSize: 32 }} />
          <Typography variant="h4" component="h1">
            Etiquetas
          </Typography>
        </Box>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => handleOpenDialog()}
        >
          Nueva Etiqueta
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Paper sx={{ 
        height: 600, 
        width: '100%',
        borderRadius: 3,
        boxShadow: '0 4px 20px rgba(0,0,0,0.08)',
        border: '1px solid #e2e8f0',
        overflow: 'hidden'
      }}>
        <DataGrid
          rows={tags}
          columns={columns}
          pageSizeOptions={[10, 25, 50]}
          initialState={{
            pagination: {
              paginationModel: { page: 0, pageSize: 10 },
            },
          }}
          disableRowSelectionOnClick
          rowHeight={62}
          sx={{
            '& .MuiDataGrid-cell:focus': {
              outline: 'none',
            },
            '& .MuiDataGrid-columnHeaders': {
              backgroundColor: '#f8fafc',
              borderBottom: '2px solid #e2e8f0',
            },
            '& .MuiDataGrid-columnHeader': {
              borderRight: '1px solid #e2e8f0',
            },
            '& .MuiDataGrid-cell': {
              borderRight: '1px solid #e2e8f0',
            },
            '& .MuiDataGrid-row:hover': {
              backgroundColor: '#f8fafc',
            },
            '& .MuiDataGrid-footerContainer': {
              borderTop: '2px solid #e2e8f0',
              backgroundColor: '#f8fafc',
            },
            '& .MuiDataGrid-virtualScroller': {
              backgroundColor: '#ffffff',
            },
            '& .MuiDataGrid-columnHeaderTitle': {
              fontWeight: 600,
              color: '#64748b',
            },
          }}
        />
      </Paper>

      {/* Actions Menu */}
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleMenuClose}
        anchorOrigin={{
          vertical: 'bottom',
          horizontal: 'right',
        }}
        transformOrigin={{
          vertical: 'top',
          horizontal: 'right',
        }}
      >
        <MenuItem onClick={() => selectedTag && handleEditTag(selectedTag)}>
          <ListItemIcon>
            <EditIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>Editar Etiqueta</ListItemText>
        </MenuItem>
        <MenuItem onClick={() => selectedTag && handleToggleActive(selectedTag.id)}>
          <ListItemIcon>
            {selectedTag?.active ? <DeleteIcon fontSize="small" /> : <AddIcon fontSize="small" />}
          </ListItemIcon>
          <ListItemText>{selectedTag?.active ? 'Desactivar' : 'Activar'}</ListItemText>
        </MenuItem>
        <MenuItem onClick={() => selectedTag && handleDeleteTag(selectedTag.id)}>
          <ListItemIcon>
            <DeleteIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>Eliminar Etiqueta</ListItemText>
        </MenuItem>
      </Menu>

      {/* Create/Edit Tag Dialog */}
      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="md" fullWidth>
        <DialogTitle>
          {editingTag ? 'Editar Etiqueta' : 'Nueva Etiqueta'}
        </DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3, mt: 1 }}>
            {/* Nombre de la Etiqueta - Ancho completo */}
            <TextField
              fullWidth
              label="Nombre de la Etiqueta"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              required
              size="medium"
              sx={{
                '& .MuiOutlinedInput-root': {
                  borderRadius: 2,
                }
              }}
            />

            {/* Descripción - Ancho completo */}
            <TextField
              fullWidth
              label="Descripción"
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              multiline
              rows={4}
              required
              size="medium"
              sx={{
                '& .MuiOutlinedInput-root': {
                  borderRadius: 2,
                }
              }}
            />



            {/* Color - Ancho completo con mejor presentación */}
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
              <Typography variant="body2" color="text.secondary">
                Color de la Etiqueta
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <TextField
                  type="color"
                  value={formData.color}
                  onChange={(e) => setFormData({ ...formData, color: e.target.value })}
                  sx={{
                    width: '80px',
                    height: '56px',
                    '& .MuiOutlinedInput-root': {
                      borderRadius: 2,
                      padding: '4px',
                    },
                    '& input[type="color"]': {
                      width: '100%',
                      height: '100%',
                      border: 'none',
                      borderRadius: '4px',
                      cursor: 'pointer',
                    }
                  }}
                />
                <Typography variant="body2" color="text.secondary">
                  {formData.color}
                </Typography>
              </Box>
            </Box>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancelar</Button>
          <Button 
            onClick={handleSubmit} 
            variant="contained"
            disabled={!formData.name || !formData.description}
          >
            {editingTag ? 'Actualizar' : 'Crear'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Confirmation Dialog */}
      <ConfirmationDialog
        open={confirmationDialog.open}
        onClose={closeConfirmationDialog}
        onConfirm={confirmationDialog.onConfirm}
        title={confirmationDialog.title}
        message={confirmationDialog.message}
        severity={confirmationDialog.severity}
        loading={confirmationDialog.loading}
        confirmText="Eliminar"
        cancelText="Cancelar"
      />

      {/* Snackbar for notifications */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={handleCloseSnackbar}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert 
          onClose={handleCloseSnackbar} 
          severity={snackbar.severity}
          variant="filled"
          sx={{ width: '100%' }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default TagsPage;
