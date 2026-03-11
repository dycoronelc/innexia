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
  People,
  MoreVert as MoreVertIcon,
  CalendarToday as CalendarIcon
} from '@mui/icons-material';
import { DataGrid, GridActionsCellItem } from '@mui/x-data-grid';
import type { GridColDef } from '@mui/x-data-grid';
import { userService } from '../services/api';
import { formatDate } from '../utils/dateUtils';
import { useAuth } from '../contexts/AuthContext';
import ConfirmationDialog from '../components/ConfirmationDialog';

interface User {
  id: number;
  username: string;
  email: string;
  full_name: string;
  role: string;
  company_id: number;
  active: boolean;
  created_at: string;
  updated_at: string | null;
}

const UsersPage: React.FC = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [openDialog, setOpenDialog] = useState(false);
  const [editingUser, setEditingUser] = useState<User | null>(null);
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    full_name: '',
    role: 'user',
    password: '',
    confirm_password: '',
    active: true
  });
  const [error, setError] = useState('');
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [selectedUser, setSelectedUser] = useState<User | null>(null);
  
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
  const { user: currentUser } = useAuth();

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('innexia_token');
      if (!token) {
        throw new Error('No hay token de autenticación. Por favor, inicie sesión nuevamente.');
      }
      
      const response = await userService.getUsers(token);
      if (response.status === 'success') {
        console.log('Users data:', response.data);
        const processedData = (response.data || []).map(user => ({
          ...user,
          created_at: user.created_at || null,
          updated_at: user.updated_at || null
        }));
        console.log('Processed users data:', processedData);
        setUsers(processedData);
      } else {
        throw new Error(response.error || 'Error al cargar los usuarios');
      }
    } catch (error) {
      console.error('Error fetching users:', error);
      if (error instanceof Error) {
        setError(error.message);
      } else {
        setError('Error al cargar los usuarios desde la base de datos');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleOpenDialog = (user?: User) => {
    if (user) {
      setEditingUser(user);
      setFormData({
        username: user.username,
        email: user.email,
        full_name: user.full_name,
        role: user.role,
        password: '',
        confirm_password: '',
        active: user.active
      });
    } else {
      setEditingUser(null);
      setFormData({
        username: '',
        email: '',
        full_name: '',
        role: 'user',
        password: '',
        confirm_password: '',
        active: true
      });
    }
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setEditingUser(null);
    setFormData({
      username: '',
      email: '',
      full_name: '',
      role: 'user',
      password: '',
      confirm_password: '',
      active: true
    });
  };

  const handleSubmit = async () => {
    try {
      const token = localStorage.getItem('innexia_token');
      if (!token) {
        throw new Error('No hay token de autenticación. Por favor, inicie sesión nuevamente.');
      }

      // Validar contraseñas
      if (!editingUser && formData.password !== formData.confirm_password) {
        throw new Error('Las contraseñas no coinciden');
      }

      if (editingUser) {
        // Update existing user
        const response = await userService.updateUser(
          editingUser.id.toString(),
          {
            username: formData.username,
            email: formData.email,
            full_name: formData.full_name,
            role: formData.role,
            active: formData.active,
            ...(formData.password ? { password: formData.password } : {})
          },
          token
        );
        if (response.status === 'success') {
          await fetchUsers();
        } else {
          throw new Error(response.error || 'Error al actualizar el usuario');
        }
      } else {
        // Create new user
        const response = await userService.createUser(
          {
            username: formData.username,
            email: formData.email,
            full_name: formData.full_name,
            role: formData.role,
            password: formData.password,
            active: formData.active
          },
          token
        );
        if (response.status === 'success') {
          await fetchUsers();
        } else {
          throw new Error(response.error || 'Error al crear el usuario');
        }
      }
      handleCloseDialog();
    } catch (error) {
      console.error('Error saving user:', error);
      if (error instanceof Error) {
        setError(error.message);
      } else {
        setError('Error al guardar el usuario');
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
    const user = users.find(u => u.id.toString() === id);
    const userName = user?.full_name || user?.username || 'este usuario';
    
    showConfirmationDialog(
      'Eliminar Usuario',
      `¿Está seguro de que desea eliminar el usuario "${userName}"? Esta acción no se puede deshacer.`,
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

      const response = await userService.deleteUser(id, token);
      if (response.status === 'success') {
        // Actualizar lista localmente para actualización inmediata
        setUsers(prev => prev.filter(u => u.id.toString() !== id));
        
        // Mostrar mensaje de éxito
        setSnackbar({
          open: true,
          message: 'Usuario eliminado exitosamente',
          severity: 'success'
        });
        
        closeConfirmationDialog();
      } else {
        setSnackbar({
          open: true,
          message: response.error || 'Error al eliminar el usuario',
          severity: 'error'
        });
      }
    } catch (error) {
      console.error('Error deleting user:', error);
      const errorMessage = error instanceof Error ? error.message : 'Error al eliminar el usuario';
      setSnackbar({
        open: true,
        message: errorMessage,
        severity: 'error'
      });
    } finally {
      setConfirmationDialog(prev => ({ ...prev, loading: false }));
    }
  };

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>, user: User) => {
    event.stopPropagation();
    setAnchorEl(event.currentTarget);
    setSelectedUser(user);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
    setSelectedUser(null);
  };

  const handleEditUser = (user: User) => {
    handleMenuClose();
    handleOpenDialog(user);
  };

  const handleToggleActive = async (id: string) => {
    handleMenuClose();
    try {
      const token = localStorage.getItem('innexia_token');
      if (!token) {
        throw new Error('No hay token de autenticación. Por favor, inicie sesión nuevamente.');
      }

      const user = users.find(u => u.id.toString() === id);
      if (!user) {
        throw new Error('Usuario no encontrado');
      }

      const response = await userService.updateUser(
        id,
        { ...user, active: !user.active },
        token
      );
      if (response.status === 'success') {
        await fetchUsers();
      } else {
        throw new Error(response.error || 'Error al actualizar el estado del usuario');
      }
    } catch (error) {
      console.error('Error toggling user status:', error);
      if (error instanceof Error) {
        setError(error.message);
      } else {
        setError('Error al actualizar el estado del usuario');
      }
    }
  };

  const handleDeleteUser = (id: string) => {
    handleMenuClose();
    handleDelete(id);
  };

  const handleCloseSnackbar = () => {
    setSnackbar(prev => ({ ...prev, open: false }));
  };

  // Función para obtener el color del avatar basado en el nombre del usuario
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
      getActions: (params) => {
        // Solo permitir acciones si el usuario actual es admin o super_admin
        if (currentUser?.role !== 'admin' && currentUser?.role !== 'super_admin') {
          return [];
        }

        // No permitir acciones sobre super_admin si el usuario actual no es super_admin
        if (params.row.role === 'super_admin' && currentUser?.role !== 'super_admin') {
          return [];
        }

        return [
          <GridActionsCellItem
            icon={<MoreVertIcon />}
            label="Acciones"
            onClick={(event) => handleMenuOpen(event, params.row)}
          />
        ];
      }
    },
    {
      field: 'username',
      headerName: 'Usuario',
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
      field: 'full_name',
      headerName: 'Nombre Completo',
      flex: 1.5,
      minWidth: 200
    },
    {
      field: 'email',
      headerName: 'Email',
      flex: 1.5,
      minWidth: 200
    },
    {
      field: 'role',
      headerName: 'Rol',
      width: 120,
      renderCell: (params) => (
        <Chip
          label={params.value === 'super_admin' ? 'Super Admin' : params.value === 'admin' ? 'Admin' : 'Usuario'}
          size="small"
          color={params.value === 'super_admin' ? 'error' : params.value === 'admin' ? 'primary' : 'default'}
          sx={{ borderRadius: 2 }}
        />
      )
    },
    {
      field: 'active',
      headerName: 'Estado',
      width: 120,
      renderCell: (params) => (
        <Chip
          label={params.value ? 'Activo' : 'Inactivo'}
          size="small"
          color={params.value ? 'success' : 'default'}
          sx={{ borderRadius: 2 }}
        />
      )
    },
    {
      field: 'created_at',
      headerName: 'Creado',
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
          Cargando usuarios...
        </Typography>
      </Box>
    );
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <People color="primary" sx={{ fontSize: 32 }} />
          <Typography variant="h4" component="h1">
            Usuarios
          </Typography>
        </Box>
        {(currentUser?.role === 'admin' || currentUser?.role === 'super_admin') && (
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => handleOpenDialog()}
          >
            Nuevo Usuario
          </Button>
        )}
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
          rows={users}
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
        <MenuItem onClick={() => selectedUser && handleEditUser(selectedUser)}>
          <ListItemIcon>
            <EditIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>Editar Usuario</ListItemText>
        </MenuItem>
        <MenuItem onClick={() => selectedUser && handleToggleActive(selectedUser.id.toString())}>
          <ListItemIcon>
            {selectedUser?.active ? <DeleteIcon fontSize="small" /> : <AddIcon fontSize="small" />}
          </ListItemIcon>
          <ListItemText>{selectedUser?.active ? 'Desactivar' : 'Activar'}</ListItemText>
        </MenuItem>
        <MenuItem onClick={() => selectedUser && handleDeleteUser(selectedUser.id.toString())}>
          <ListItemIcon>
            <DeleteIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>Eliminar Usuario</ListItemText>
        </MenuItem>
      </Menu>

      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="md" fullWidth>
        <DialogTitle>
          {editingUser ? 'Editar Usuario' : 'Nuevo Usuario'}
        </DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3, mt: 1 }}>
            <TextField
              fullWidth
              label="Nombre de Usuario"
              value={formData.username}
              onChange={(e) => setFormData({ ...formData, username: e.target.value })}
              required
              disabled={editingUser !== null}
              size="medium"
              sx={{
                '& .MuiOutlinedInput-root': {
                  borderRadius: 2,
                }
              }}
            />

            <TextField
              fullWidth
              label="Nombre Completo"
              value={formData.full_name}
              onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
              required
              size="medium"
              sx={{
                '& .MuiOutlinedInput-root': {
                  borderRadius: 2,
                }
              }}
            />

            <TextField
              fullWidth
              type="email"
              label="Email"
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              required
              size="medium"
              sx={{
                '& .MuiOutlinedInput-root': {
                  borderRadius: 2,
                }
              }}
            />

            <FormControl fullWidth>
              <InputLabel>Rol</InputLabel>
              <Select
                value={formData.role}
                label="Rol"
                onChange={(e) => setFormData({ ...formData, role: e.target.value })}
                required
                size="medium"
                disabled={currentUser?.role !== 'super_admin'}
                sx={{
                  '& .MuiOutlinedInput-root': {
                    borderRadius: 2,
                  }
                }}
              >
                <MenuItem value="user">Usuario</MenuItem>
                <MenuItem value="admin">Administrador</MenuItem>
                {currentUser?.role === 'super_admin' && (
                  <MenuItem value="super_admin">Super Administrador</MenuItem>
                )}
              </Select>
            </FormControl>

            <TextField
              fullWidth
              type="password"
              label={editingUser ? "Nueva Contraseña (opcional)" : "Contraseña"}
              value={formData.password}
              onChange={(e) => setFormData({ ...formData, password: e.target.value })}
              required={!editingUser}
              size="medium"
              sx={{
                '& .MuiOutlinedInput-root': {
                  borderRadius: 2,
                }
              }}
            />

            {(!editingUser || formData.password) && (
              <TextField
                fullWidth
                type="password"
                label="Confirmar Contraseña"
                value={formData.confirm_password}
                onChange={(e) => setFormData({ ...formData, confirm_password: e.target.value })}
                required={!editingUser || !!formData.password}
                size="medium"
                sx={{
                  '& .MuiOutlinedInput-root': {
                    borderRadius: 2,
                  }
                }}
              />
            )}
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancelar</Button>
          <Button 
            onClick={handleSubmit} 
            variant="contained"
            disabled={
              !formData.username || 
              !formData.email || 
              !formData.full_name || 
              (!editingUser && !formData.password) ||
              (formData.password && formData.password !== formData.confirm_password)
            }
          >
            {editingUser ? 'Actualizar' : 'Crear'}
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

export default UsersPage;