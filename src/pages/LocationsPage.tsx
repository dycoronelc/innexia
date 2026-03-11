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
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Menu,
  ListItemIcon,
  ListItemText,
  Snackbar
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  LocationOn as LocationIcon,
  MoreVert as MoreVertIcon,
  CalendarToday as CalendarIcon
} from '@mui/icons-material';
import { DataGrid, GridActionsCellItem } from '@mui/x-data-grid';
import type { GridColDef } from '@mui/x-data-grid';
import type { Location } from '../types';
import { masterService } from '../services/api';
import { formatDate } from '../utils/dateUtils';
import ConfirmationDialog from '../components/ConfirmationDialog';


const LocationsPage: React.FC = () => {
  const [locations, setLocations] = useState<Location[]>([]);
  const [loading, setLoading] = useState(true);
  const [openDialog, setOpenDialog] = useState(false);
  const [editingLocation, setEditingLocation] = useState<Location | null>(null);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    country: '',
    region: '',
    timezone: '',
    active: true
  });
  const [error, setError] = useState('');
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [selectedLocation, setSelectedLocation] = useState<Location | null>(null);
  
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
    fetchLocations();
  }, []);

  const fetchLocations = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('innexia_token');
      if (!token) {
        throw new Error('No hay token de autenticación. Por favor, inicie sesión nuevamente.');
      }
      
      const response = await masterService.getLocations(token);
      if (response.status === 'success') {
        console.log('Locations data:', response.data);
        // Asegurarnos de que las fechas se manejen correctamente
        const processedData = (response.data || []).map(location => ({
          ...location,
          created_at: location.created_at || null,
          updated_at: location.updated_at || null
        }));
        console.log('Processed locations data:', processedData);
        setLocations(processedData);
      } else {
        throw new Error(response.error || 'Error al cargar las ubicaciones');
      }
    } catch (error) {
      console.error('Error fetching locations:', error);
      if (error instanceof Error) {
        setError(error.message);
      } else {
        setError('Error al cargar las ubicaciones desde la base de datos');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleOpenDialog = (location?: Location) => {
    if (location) {
      setEditingLocation(location);
      setFormData({
        name: location.name,
        description: location.description,
        country: location.country,
        region: location.region,
        timezone: location.timezone,
        active: location.active
      });
    } else {
      setEditingLocation(null);
      setFormData({
        name: '',
        description: '',
        country: '',
        region: '',
        timezone: '',
        active: true
      });
    }
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setEditingLocation(null);
    setFormData({
      name: '',
      description: '',
      country: '',
      region: '',
      timezone: '',
      active: true
    });
  };

  const handleSubmit = async () => {
    try {
      const token = localStorage.getItem('innexia_token');
      if (!token) {
        throw new Error('No hay token de autenticación. Por favor, inicie sesión nuevamente.');
      }

      if (editingLocation) {
        // Update existing location
        const response = await masterService.updateLocation(editingLocation.id, formData, token);
        if (response.status === 'success') {
          await fetchLocations(); // Recargar ubicaciones
        } else {
          throw new Error(response.error || 'Error al actualizar la ubicación');
        }
      } else {
        // Create new location
        const response = await masterService.createLocation(formData, token);
        if (response.status === 'success') {
          await fetchLocations(); // Recargar ubicaciones
        } else {
          throw new Error(response.error || 'Error al crear la ubicación');
        }
      }
      handleCloseDialog();
    } catch (error) {
      console.error('Error saving location:', error);
      if (error instanceof Error) {
        setError(error.message);
      } else {
        setError('Error al guardar la ubicación');
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
    const location = locations.find(l => l.id === id);
    const locationName = location?.name || 'esta ubicación';
    
    showConfirmationDialog(
      'Eliminar Ubicación',
      `¿Está seguro de que desea eliminar la ubicación "${locationName}"? Esta acción no se puede deshacer.`,
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

      const response = await masterService.deleteLocation(id, token);
      if (response.status === 'success') {
        // Actualizar lista localmente para actualización inmediata
        setLocations(prev => prev.filter(l => l.id !== id));
        
        // Mostrar mensaje de éxito
        setSnackbar({
          open: true,
          message: 'Ubicación eliminada exitosamente',
          severity: 'success'
        });
        
        closeConfirmationDialog();
      } else {
        setSnackbar({
          open: true,
          message: response.error || 'Error al eliminar la ubicación',
          severity: 'error'
        });
      }
    } catch (error) {
      console.error('Error deleting location:', error);
      const errorMessage = error instanceof Error ? error.message : 'Error al eliminar la ubicación';
      setSnackbar({
        open: true,
        message: errorMessage,
        severity: 'error'
      });
    } finally {
      setConfirmationDialog(prev => ({ ...prev, loading: false }));
    }
  };

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>, location: Location) => {
    event.stopPropagation();
    setAnchorEl(event.currentTarget);
    setSelectedLocation(location);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
    setSelectedLocation(null);
  };

  const handleEditLocation = (location: Location) => {
    handleMenuClose();
    handleOpenDialog(location);
  };

  const handleToggleActive = async (id: string) => {
    handleMenuClose();
    try {
      const token = localStorage.getItem('innexia_token');
      if (!token) {
        throw new Error('No hay token de autenticación. Por favor, inicie sesión nuevamente.');
      }

      const location = locations.find(l => l.id === id);
      if (!location) {
        throw new Error('Ubicación no encontrada');
      }

      const response = await masterService.updateLocation(id, { ...location, active: !location.active }, token);
      if (response.status === 'success') {
        await fetchLocations(); // Recargar ubicaciones
      } else {
        throw new Error(response.error || 'Error al actualizar el estado de la ubicación');
      }
    } catch (error) {
      console.error('Error toggling location status:', error);
      if (error instanceof Error) {
        setError(error.message);
      } else {
        setError('Error al actualizar el estado de la ubicación');
      }
    }
  };

  const handleDeleteLocation = (id: string) => {
    handleMenuClose();
    handleDelete(id);
  };

  const handleCloseSnackbar = () => {
    setSnackbar(prev => ({ ...prev, open: false }));
  };

  const countries = ['Colombia', 'Estados Unidos', 'México', 'Argentina', 'Chile', 'Perú', 'Brasil'];
  const regions = ['Cundinamarca', 'Antioquia', 'Valle del Cauca', 'Atlántico', 'Florida', 'Distrito Federal', 'Buenos Aires'];
  const timezones = [
    'America/Bogota',
    'America/New_York',
    'America/Mexico_City',
    'America/Argentina/Buenos_Aires',
    'America/Santiago',
    'America/Lima',
    'America/Sao_Paulo'
  ];

  // Función para obtener el color del avatar basado en el nombre de la ubicación
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
      headerName: 'Ubicación',
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
              backgroundColor: getAvatarColor(params.value),
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
      field: 'country',
      headerName: 'País',
      width: 120,
      renderCell: (params) => (
        <Chip
          label={params.value || 'No Aplica'}
          size="small"
          variant="outlined"
          color={params.value ? "primary" : "default"}
          sx={{ borderRadius: 2 }}
        />
      )
    },
    {
      field: 'region',
      headerName: 'Región',
      width: 120,
      renderCell: (params) => (
        <Typography variant="body2" color="text.secondary">
          {params.value || 'No Aplica'}
        </Typography>
      )
    },
    {
      field: 'timezone',
      headerName: 'Zona Horaria',
      width: 150,
      renderCell: (params) => (
        <Typography variant="body2" color="text.secondary">
          {params.value || 'No Aplica'}
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
          Cargando ubicaciones...
        </Typography>
      </Box>
    );
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <LocationIcon color="primary" sx={{ fontSize: 32 }} />
          <Typography variant="h4" component="h1">
            Ubicaciones
          </Typography>
        </Box>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => handleOpenDialog()}
        >
          Nueva Ubicación
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
          rows={locations}
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
        <MenuItem onClick={() => selectedLocation && handleEditLocation(selectedLocation)}>
          <ListItemIcon>
            <EditIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>Editar Ubicación</ListItemText>
        </MenuItem>
        <MenuItem onClick={() => selectedLocation && handleToggleActive(selectedLocation.id)}>
          <ListItemIcon>
            {selectedLocation?.active ? <DeleteIcon fontSize="small" /> : <AddIcon fontSize="small" />}
          </ListItemIcon>
          <ListItemText>{selectedLocation?.active ? 'Desactivar' : 'Activar'}</ListItemText>
        </MenuItem>
        <MenuItem onClick={() => selectedLocation && handleDeleteLocation(selectedLocation.id)}>
          <ListItemIcon>
            <DeleteIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>Eliminar Ubicación</ListItemText>
        </MenuItem>
      </Menu>

      {/* Create/Edit Location Dialog */}
      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="md" fullWidth>
        <DialogTitle>
          {editingLocation ? 'Editar Ubicación' : 'Nueva Ubicación'}
        </DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3, mt: 1 }}>
            {/* Nombre de la Ciudad - Ancho completo */}
            <TextField
              fullWidth
              label="Nombre de la Ciudad"
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

            {/* País - Ancho completo */}
            <FormControl fullWidth>
              <InputLabel>País</InputLabel>
              <Select
                value={formData.country}
                label="País"
                onChange={(e) => setFormData({ ...formData, country: e.target.value })}
                required
                size="medium"
                sx={{
                  '& .MuiOutlinedInput-root': {
                    borderRadius: 2,
                  }
                }}
              >
                {countries.map((country) => (
                  <MenuItem key={country} value={country}>
                    {country}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            {/* Región/Estado - Ancho completo */}
            <FormControl fullWidth>
              <InputLabel>Región/Estado</InputLabel>
              <Select
                value={formData.region}
                label="Región/Estado"
                onChange={(e) => setFormData({ ...formData, region: e.target.value })}
                required
                size="medium"
                sx={{
                  '& .MuiOutlinedInput-root': {
                    borderRadius: 2,
                  }
                }}
              >
                {regions.map((region) => (
                  <MenuItem key={region} value={region}>
                    {region}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            {/* Zona Horaria - Ancho completo */}
            <FormControl fullWidth>
              <InputLabel>Zona Horaria</InputLabel>
              <Select
                value={formData.timezone}
                label="Zona Horaria"
                onChange={(e) => setFormData({ ...formData, timezone: e.target.value })}
                required
                size="medium"
                sx={{
                  '& .MuiOutlinedInput-root': {
                    borderRadius: 2,
                  }
                }}
              >
                {timezones.map((timezone) => (
                  <MenuItem key={timezone} value={timezone}>
                    {timezone}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancelar</Button>
          <Button 
            onClick={handleSubmit} 
            variant="contained"
            disabled={!formData.name || !formData.description || !formData.country || !formData.region || !formData.timezone}
          >
            {editingLocation ? 'Actualizar' : 'Crear'}
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

export default LocationsPage;
