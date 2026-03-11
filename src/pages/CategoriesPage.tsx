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
  Alert,
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText,
  Snackbar
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  MoreVert as MoreVertIcon,
  CalendarToday as CalendarIcon,
  Category as CategoryIcon
} from '@mui/icons-material';
import { DataGrid, GridActionsCellItem } from '@mui/x-data-grid';
import type { GridColDef } from '@mui/x-data-grid';
import type { Category } from '../types';
import { masterService } from '../services/api';
import { formatDate } from '../utils/dateUtils';
import ConfirmationDialog from '../components/ConfirmationDialog';

const CategoriesPage: React.FC = () => {
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);
  const [openDialog, setOpenDialog] = useState(false);
  const [editingCategory, setEditingCategory] = useState<Category | null>(null);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    color: '#1976d2',
    active: true
  });
  const [error, setError] = useState('');
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [selectedCategory, setSelectedCategory] = useState<Category | null>(null);
  
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
    fetchCategories();
  }, []);

  const fetchCategories = async () => {
    setLoading(true);
    setError('');
    
    try {
      // Intentar diferentes claves de token
      const token = localStorage.getItem('innexia_token') || 
                   localStorage.getItem('access_token') || 
                   localStorage.getItem('authToken');
      
      if (!token) {
        throw new Error('No hay token de autenticación. Por favor, inicie sesión nuevamente.');
      }
      
      const response = await masterService.getCategories(token);
      
      if (response.status === 'success') {
        console.log('Categories data:', response.data);
        // Asegurarnos de que las fechas se manejen correctamente
        const processedData = (response.data || []).map(category => ({
          ...category,
          created_at: category.created_at || null,
          updated_at: category.updated_at || null
        }));
        console.log('Processed categories data:', processedData);
        setCategories(processedData);
      } else {
        throw new Error(response.error || 'Error al cargar las categorías');
      }
    } catch (error) {
      console.error('Error fetching categories:', error);
      if (error instanceof Error) {
        setError(error.message);
      } else {
        setError('Error al cargar las categorías desde la base de datos');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleOpenDialog = (category?: Category) => {
    if (category) {
      setEditingCategory(category);
      setFormData({
        name: category.name,
        description: category.description,
        color: category.color,
        active: category.active
      });
    } else {
      setEditingCategory(null);
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
    setEditingCategory(null);
    setFormData({
      name: '',
      description: '',
      color: '#1976d2',
      active: true
    });
  };

  const handleSubmit = async () => {
    try {
      if (editingCategory) {
        // Update existing category
        const updatedCategory = {
          ...editingCategory,
          ...formData,
          updatedAt: new Date()
        };
        setCategories(prev => prev.map(c => c.id === editingCategory.id ? updatedCategory : c));
      } else {
        // Create new category
        const newCategory: Category = {
          id: Date.now().toString(),
          ...formData,
          createdAt: new Date(),
          updatedAt: new Date()
        };
        setCategories(prev => [...prev, newCategory]);
      }
      handleCloseDialog();
    } catch (error) {
      setError('Error al guardar la categoría');
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
    const category = categories.find(c => c.id === id);
    const categoryName = category?.name || 'esta categoría';
    
    showConfirmationDialog(
      'Eliminar Categoría',
      `¿Está seguro de que desea eliminar la categoría "${categoryName}"? Esta acción no se puede deshacer.`,
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

      const response = await masterService.deleteCategory(id, token);
      if (response.status === 'success') {
        // Actualizar lista localmente para actualización inmediata
        setCategories(prev => prev.filter(c => c.id !== id));
        
        // Mostrar mensaje de éxito
        setSnackbar({
          open: true,
          message: 'Categoría eliminada exitosamente',
          severity: 'success'
        });
        
        closeConfirmationDialog();
      } else {
        setSnackbar({
          open: true,
          message: response.error || 'Error al eliminar la categoría',
          severity: 'error'
        });
      }
    } catch (error) {
      console.error('Error al eliminar categoría:', error);
      const errorMessage = error instanceof Error ? error.message : 'Error al eliminar la categoría';
      setSnackbar({
        open: true,
        message: errorMessage,
        severity: 'error'
      });
    } finally {
      setConfirmationDialog(prev => ({ ...prev, loading: false }));
    }
  };

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>, category: Category) => {
    event.stopPropagation();
    setAnchorEl(event.currentTarget);
    setSelectedCategory(category);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
    setSelectedCategory(null);
  };

  const handleEditCategory = (category: Category) => {
    handleMenuClose();
    handleOpenDialog(category);
  };

  const handleToggleActive = async (id: string) => {
    handleMenuClose();
    setCategories(prev => prev.map(c => 
      c.id === id ? { ...c, active: !c.active, updatedAt: new Date() } : c
    ));
  };

  const handleDeleteCategory = (id: string) => {
    handleMenuClose();
    handleDelete(id);
  };

  const handleCloseSnackbar = () => {
    setSnackbar(prev => ({ ...prev, open: false }));
  };

  // Función para obtener el color del avatar basado en el nombre de la categoría
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
      headerName: 'Categoría',
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
          Cargando categorías...
        </Typography>
      </Box>
    );
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <CategoryIcon color="primary" sx={{ fontSize: 32 }} />
          <Typography variant="h4" component="h1">
            Categorías
          </Typography>
        </Box>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => handleOpenDialog()}
        >
          Nueva Categoría
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
          rows={categories}
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
        <MenuItem onClick={() => selectedCategory && handleEditCategory(selectedCategory)}>
          <ListItemIcon>
            <EditIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>Editar Categoría</ListItemText>
        </MenuItem>
        <MenuItem onClick={() => selectedCategory && handleToggleActive(selectedCategory.id)}>
          <ListItemIcon>
            {selectedCategory?.active ? <DeleteIcon fontSize="small" /> : <AddIcon fontSize="small" />}
          </ListItemIcon>
          <ListItemText>{selectedCategory?.active ? 'Desactivar' : 'Activar'}</ListItemText>
        </MenuItem>
        <MenuItem onClick={() => selectedCategory && handleDeleteCategory(selectedCategory.id)}>
          <ListItemIcon>
            <DeleteIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>Eliminar Categoría</ListItemText>
        </MenuItem>
      </Menu>

      {/* Create/Edit Category Dialog */}
      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="md" fullWidth>
        <DialogTitle>
          {editingCategory ? 'Editar Categoría' : 'Nueva Categoría'}
        </DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3, mt: 1 }}>
            {/* Nombre de la Categoría - Ancho completo */}
            <TextField
              fullWidth
              label="Nombre de la Categoría"
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
                Color de la Categoría
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
            {editingCategory ? 'Actualizar' : 'Crear'}
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

export default CategoriesPage;
