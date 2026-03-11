import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Chip,
  Alert,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  Button,
  Menu,
  ListItemIcon,
  ListItemText
} from '@mui/material';
import {
  History as HistoryIcon,
  FilterList as FilterIcon,
  Clear as ClearIcon,
  MoreVert as MoreVertIcon,
  CalendarToday as CalendarIcon,
  Person as PersonIcon,
  Security
} from '@mui/icons-material';
import { DataGrid, GridActionsCellItem } from '@mui/x-data-grid';
import type { GridColDef } from '@mui/x-data-grid';
import { auditLogService } from '../services/api';
import { formatDate } from '../utils/dateUtils';
import { useAuth } from '../contexts/AuthContext';

interface AuditLogUser {
  username: string;
  full_name: string;
}

interface AuditLog {
  id: number;
  user_id: number;
  action: string;
  entity_type: string;
  entity_id: number;
  details: string;
  ip_address: string;
  created_at: string;
  user: AuditLogUser;
}

const AuditLogPage: React.FC = () => {
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [selectedLog, setSelectedLog] = useState<AuditLog | null>(null);
  const { user: currentUser } = useAuth();
  // Verificar si el usuario tiene permisos para ver las bitácoras
  if (currentUser?.role !== 'admin' && currentUser?.role !== 'super_admin') {
    return (
      <Box sx={{ width: '100%' }}>
        <Alert severity="error">
          No tiene permisos para ver las bitácoras
        </Alert>
      </Box>
    );
  }
  const [filters, setFilters] = useState({
    action: '',
    entity_type: '',
    username: '',
    dateFrom: '',
    dateTo: ''
  });

  useEffect(() => {
    fetchLogs();
  }, []);

  const fetchLogs = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('innexia_token');
      if (!token) {
        throw new Error('No hay token de autenticación. Por favor, inicie sesión nuevamente.');
      }
      
      const response = await auditLogService.getLogs(token, filters);
      if (response.status === 'success') {
        console.log('Audit logs data:', response.data);
        const processedData = (response.data || []).map((log: any) => ({
          ...log,
          id: log.id,
          user_id: log.user_id,
          action: log.action,
          entity_type: log.entity_type,
          entity_id: log.entity_id || 'N/A',
          details: log.details || 'Sin detalles',
          ip_address: log.ip_address || 'N/A',
          timestamp: log.timestamp,
          user: log.user || { username: 'Usuario Eliminado', full_name: 'Usuario Eliminado' }
        }));
        console.log('Processed audit logs data:', processedData);
        setLogs(processedData);
      } else {
        throw new Error(response.error || 'Error al cargar las bitácoras');
      }
    } catch (error) {
      console.error('Error fetching audit logs:', error);
      if (error instanceof Error) {
        setError(error.message);
      } else {
        setError('Error al cargar las bitácoras desde la base de datos');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (field: string, value: string) => {
    setFilters(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleApplyFilters = () => {
    fetchLogs();
  };

  const handleClearFilters = () => {
    setFilters({
      action: '',
      entity_type: '',
      username: '',
      dateFrom: '',
      dateTo: ''
    });
    fetchLogs();
  };

  const getActionColor = (action: string) => {
    switch (action.toLowerCase()) {
      case 'create':
        return 'success';
      case 'update':
        return 'primary';
      case 'delete':
        return 'error';
      case 'login':
        return 'info';
      default:
        return 'default';
    }
  };

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>, log: AuditLog) => {
    event.stopPropagation();
    setAnchorEl(event.currentTarget);
    setSelectedLog(log);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
    setSelectedLog(null);
  };

  const handleViewDetails = (log: AuditLog) => {
    handleMenuClose();
    // Aquí podrías abrir un modal con los detalles completos
    console.log('Ver detalles del log:', log);
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
      getActions: (params) => [
        <GridActionsCellItem
          icon={<MoreVertIcon />}
          label="Acciones"
          onClick={(event) => handleMenuOpen(event, params.row)}
        />
      ]
    },
    {
      field: 'user',
      headerName: 'Usuario',
      width: 250,
      valueGetter: (params: { row: AuditLog }) => {
        try {
          return params.row.user?.username || 'Usuario Eliminado';
        } catch (error) {
          return 'Usuario Eliminado';
        }
      },
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
              backgroundColor: getAvatarColor(String(params.value)),
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'white',
              fontSize: '1rem',
              fontWeight: 600,
              flexShrink: 0
            }}
          >
            {String(params.value).charAt(0).toUpperCase()}
          </Box>
          <Box sx={{ display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
            <Typography variant="body2" sx={{ fontWeight: 600, color: '#1e293b', mb: 0.5 }}>
              {String(params.value)}
            </Typography>
            <Typography variant="caption" sx={{ color: '#64748b' }}>
              ID: {params.row.user_id}
            </Typography>
          </Box>
        </Box>
      )
    },
    {
      field: 'action',
      headerName: 'Acción',
      width: 120,
      renderCell: (params) => (
        <Chip
          label={params.value}
          size="small"
          color={getActionColor(params.value)}
          sx={{ borderRadius: 2 }}
        />
      )
    },
    {
      field: 'entity_type',
      headerName: 'Entidad',
      width: 150
    },
    {
      field: 'entity_id',
      headerName: 'ID Entidad',
      width: 100
    },
    {
      field: 'details',
      headerName: 'Detalles',
      flex: 1,
      minWidth: 300,
      renderCell: (params) => (
        <Typography variant="body2" sx={{
          overflow: 'hidden',
          textOverflow: 'ellipsis',
          whiteSpace: 'nowrap'
        }}>
          {params.value}
        </Typography>
      )
    },
    {
      field: 'ip_address',
      headerName: 'Dirección IP',
      width: 150
    },
    {
      field: 'timestamp',
      headerName: 'Fecha',
      width: 150,
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
          Cargando bitácoras...
        </Typography>
      </Box>
    );
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Security color="primary" sx={{ fontSize: 32 }} />
          <Typography variant="h4" component="h1">
            Bitácora de Actividades
          </Typography>
        </Box>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {/* Filtros */}
      <Paper sx={{ p: 2, mb: 2 }}>
        <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
          <FormControl sx={{ minWidth: 120 }}>
            <InputLabel>Acción</InputLabel>
            <Select
              value={filters.action}
              label="Acción"
              onChange={(e) => handleFilterChange('action', e.target.value)}
              size="small"
            >
              <MenuItem value="">Todas</MenuItem>
              <MenuItem value="create">Crear</MenuItem>
              <MenuItem value="update">Actualizar</MenuItem>
              <MenuItem value="delete">Eliminar</MenuItem>
              <MenuItem value="login">Login</MenuItem>
            </Select>
          </FormControl>

          <FormControl sx={{ minWidth: 120 }}>
            <InputLabel>Entidad</InputLabel>
            <Select
              value={filters.entity_type}
              label="Entidad"
              onChange={(e) => handleFilterChange('entity_type', e.target.value)}
              size="small"
            >
              <MenuItem value="">Todas</MenuItem>
              <MenuItem value="user">Usuario</MenuItem>
              <MenuItem value="project">Proyecto</MenuItem>
              <MenuItem value="category">Categoría</MenuItem>
              <MenuItem value="tag">Etiqueta</MenuItem>
              <MenuItem value="location">Ubicación</MenuItem>
            </Select>
          </FormControl>

          <TextField
            label="Usuario"
            value={filters.username}
            onChange={(e) => handleFilterChange('username', e.target.value)}
            size="small"
          />

          <TextField
            label="Desde"
            type="date"
            value={filters.dateFrom}
            onChange={(e) => handleFilterChange('dateFrom', e.target.value)}
            size="small"
            InputLabelProps={{ shrink: true }}
          />

          <TextField
            label="Hasta"
            type="date"
            value={filters.dateTo}
            onChange={(e) => handleFilterChange('dateTo', e.target.value)}
            size="small"
            InputLabelProps={{ shrink: true }}
          />

          <Button
            variant="contained"
            startIcon={<FilterIcon />}
            onClick={handleApplyFilters}
          >
            Filtrar
          </Button>

          <Button
            variant="outlined"
            startIcon={<ClearIcon />}
            onClick={handleClearFilters}
          >
            Limpiar
          </Button>
        </Box>
      </Paper>

      <Paper sx={{ 
        height: 600, 
        width: '100%',
        borderRadius: 3,
        boxShadow: '0 4px 20px rgba(0,0,0,0.08)',
        border: '1px solid #e2e8f0',
        overflow: 'hidden'
      }}>
        <DataGrid
          rows={logs}
          columns={columns}
          pageSizeOptions={[10, 25, 50, 100]}
          initialState={{
            pagination: {
              paginationModel: { page: 0, pageSize: 25 },
            },
            sorting: {
              sortModel: [{ field: 'created_at', sort: 'desc' }],
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
        <MenuItem onClick={() => selectedLog && handleViewDetails(selectedLog)}>
          <ListItemIcon>
            <HistoryIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>Ver Detalles</ListItemText>
        </MenuItem>
      </Menu>
    </Box>
  );
};

export default AuditLogPage;