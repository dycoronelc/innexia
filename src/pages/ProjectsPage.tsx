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
  LinearProgress,
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
  Visibility as ViewIcon,
  Business as BusinessIcon,
  MoreVert as MoreVertIcon,
  CalendarToday as CalendarIcon,
  LocationOn as LocationIcon,
  SmartToy as SmartToyIcon
} from '@mui/icons-material';
import { DataGrid, GridActionsCellItem } from '@mui/x-data-grid';
import type { GridColDef } from '@mui/x-data-grid';
import type { Project } from '../types';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { projectService, masterService, agentOutputService } from '../services/api';
import { formatDate } from '../utils/dateUtils';
import ConfirmationDialog from '../components/ConfirmationDialog';

const ProjectsPage: React.FC = () => {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [openDialog, setOpenDialog] = useState(false);
  const [editingProject, setEditingProject] = useState<Project | null>(null);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    category: '',
    tags: [] as string[],
    location: '',
    status: 'active' as 'active' | 'inactive' | 'completed'
  });
  const [error, setError] = useState('');
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [selectedProject, setSelectedProject] = useState<Project | null>(null);
  const [categories, setCategories] = useState<Array<{id: string, name: string, color: string}>>([]);
  const [locations, setLocations] = useState<Array<{id: string, name: string}>>([]);
  const [tags, setTags] = useState<Array<{id: string, name: string, color: string}>>([]);
  const [loadingFormData, setLoadingFormData] = useState(false);
  
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

  // Diálogo crear proyecto desde agente IA (n8n)
  const [agentDialogOpen, setAgentDialogOpen] = useState(false);
  const [agentJsonText, setAgentJsonText] = useState('');
  const [agentDialogLoading, setAgentDialogLoading] = useState(false);
  const [agentDialogError, setAgentDialogError] = useState('');
  
  const navigate = useNavigate();
  const { token } = useAuth();

  useEffect(() => {
    if (token) {
      fetchProjects();
      fetchFormData();
    }
  }, [token]);

  // Escuchar eventos de creación de proyectos desde el ChatBot
  useEffect(() => {
    const handleProjectCreated = (event: CustomEvent) => {
      // Proyecto creado detectado en ProjectsPage
      // Refrescar la lista de proyectos
      fetchProjects().then(() => {
        // Refresh de proyectos completado
      }).catch((error) => {
        console.error('Error en refresh de proyectos:', error);
      });
      // Mostrar notificación
      setSnackbar({
        open: true,
        message: `✅ Nuevo proyecto creado: ${event.detail.projectName}`,
        severity: 'success'
      });
    };

    // Registrando listener de projectCreated en ProjectsPage
    window.addEventListener('projectCreated', handleProjectCreated as EventListener);
    
    return () => {
      // Desregistrando listener de projectCreated en ProjectsPage
      window.removeEventListener('projectCreated', handleProjectCreated as EventListener);
    };
  }, []);

  const fetchProjects = async () => {
    setLoading(true);
    try {
      const response = await projectService.getProjects(token!);
      
      if (response.status === 'success' && response.data) {
        // Procesar los datos para asegurar que las fechas sean válidas
        const processedProjects = response.data.map((project: any) => ({
          ...project,
          id: project.id, // Mantener como número para navegación
          createdAt: project.created_at ? new Date(project.created_at) : new Date(),
          updatedAt: project.updated_at ? new Date(project.updated_at) : new Date(),
          tags: project.tags || []
        }));
        setProjects(processedProjects);
      } else {
        console.error('Error en respuesta:', response.error);
        setError(response.error || 'Error al cargar los proyectos');
      }
    } catch (error) {
      console.error('Error en fetchProjects:', error);
      setError('Error al cargar los proyectos');
    } finally {
      setLoading(false);
    }
  };

  const fetchFormData = async () => {
    setLoadingFormData(true);
    try {
      // Cargar categorías
      const categoriesResponse = await masterService.getCategories(token!);
      if (categoriesResponse.status === 'success' && categoriesResponse.data) {
        const processedCategories = categoriesResponse.data.map((cat: any) => ({
          id: cat.id.toString(),
          name: cat.name,
          color: cat.color || '#2196F3'
        }));
        setCategories(processedCategories);
      }

      // Cargar ubicaciones
      const locationsResponse = await masterService.getLocations(token!);
      if (locationsResponse.status === 'success' && locationsResponse.data) {
        const processedLocations = locationsResponse.data.map((loc: any) => ({
          id: loc.id.toString(),
          name: `${loc.city || ''}, ${loc.country || ''}`.trim().replace(/^,\s*/, '').replace(/,\s*$/, '')
        }));
        setLocations(processedLocations);
      }

      // Cargar etiquetas
      const tagsResponse = await masterService.getTags(token!);
      if (tagsResponse.status === 'success' && tagsResponse.data) {
        const processedTags = tagsResponse.data.map((tag: any) => ({
          id: tag.id.toString(),
          name: tag.name,
          color: tag.color || '#4CAF50'
        }));
        setTags(processedTags);
      }
    } catch (error) {
      console.error('Error al cargar datos del formulario:', error);
    } finally {
      setLoadingFormData(false);
    }
  };

  const handleOpenDialog = (project?: Project) => {
    if (project) {
      setEditingProject(project);
      setFormData({
        name: project.name,
        description: project.description,
        category: project.category,
        tags: project.tags,
        location: project.location,
        status: project.status
      });
    } else {
      setEditingProject(null);
      setFormData({
        name: '',
        description: '',
        category: '',
        tags: [],
        location: '',
        status: 'active'
      });
    }
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setEditingProject(null);
    setFormData({
      name: '',
      description: '',
      category: '',
      tags: [],
      location: '',
      status: 'active'
    });
  };

  const handleSubmit = async () => {
    try {
      const projectData = {
        name: formData.name,
        description: formData.description,
        category: formData.category,
        tags: formData.tags,
        location: formData.location,
        status: formData.status
      };

      if (editingProject) {
        // Actualizar proyecto existente
        const response = await projectService.updateProject(editingProject.id, projectData, token!);
        if (response.status === 'success') {
          await fetchProjects(); // Recargar la lista
          handleCloseDialog();
        } else {
          setError(response.error || 'Error al actualizar el proyecto');
        }
      } else {
        // Crear nuevo proyecto
        const response = await projectService.createProject(projectData, token!);
        if (response.status === 'success') {
          await fetchProjects(); // Recargar la lista
          handleCloseDialog();
        } else {
          setError(response.error || 'Error al crear el proyecto');
        }
      }
    } catch (error) {
      setError('Error al guardar el proyecto');
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
    const project = projects.find(p => p.id === Number(id));
    const projectName = project?.name || 'este proyecto';
    
    showConfirmationDialog(
      'Eliminar Proyecto',
      `¿Está seguro de que desea eliminar el proyecto "${projectName}"? Esta acción no se puede deshacer.`,
      () => performDelete(id),
      'error'
    );
  };

  const performDelete = async (id: string) => {
    setConfirmationDialog(prev => ({ ...prev, loading: true }));
    
    try {
      const response = await projectService.deleteProject(Number(id), token!);
      
      if (response.status === 'success') {
        // Remover el proyecto de la lista localmente para actualización inmediata
        setProjects(prev => prev.filter(project => project.id !== Number(id)));
        
        // Mostrar mensaje de éxito
        setSnackbar({
          open: true,
          message: 'Proyecto eliminado exitosamente',
          severity: 'success'
        });
        
        closeConfirmationDialog();
      } else {
        setSnackbar({
          open: true,
          message: response.error || 'Error al eliminar el proyecto',
          severity: 'error'
        });
      }
    } catch (error) {
      console.error('Error al eliminar proyecto:', error);
      setSnackbar({
        open: true,
        message: 'Error al eliminar el proyecto',
        severity: 'error'
      });
    } finally {
      setConfirmationDialog(prev => ({ ...prev, loading: false }));
    }
  };

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>, project: Project) => {
    event.stopPropagation();
    setAnchorEl(event.currentTarget);
    setSelectedProject(project);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
    setSelectedProject(null);
  };

  const handleViewProject = (project: Project) => {
    handleMenuClose();
    navigate(`/projects/${project.id}`);
  };

  const handleEditProject = (project: Project) => {
    handleMenuClose();
    handleOpenDialog(project);
  };

  const handleDeleteProject = (project: Project) => {
    handleMenuClose();
    handleDelete(String(project.id));
  };

  const handleCloseSnackbar = () => {
    setSnackbar(prev => ({ ...prev, open: false }));
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'success';
      case 'inactive': return 'warning';
      case 'completed': return 'info';
      default: return 'default';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'active': return 'Activo';
      case 'inactive': return 'Inactivo';
      case 'completed': return 'Completado';
      default: return status;
    }
  };

  // Función para obtener el color del avatar basado en el nombre del proyecto
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
      headerName: 'Proyecto',
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
      field: 'category',
      headerName: 'Categoría',
      width: 150,
      renderCell: (params) => (
        <Chip
          label={params.value}
          size="small"
          variant="outlined"
          color="primary"
          sx={{ borderRadius: 2 }}
        />
      )
    },
    {
      field: 'tags',
      headerName: 'Etiquetas',
      width: 200,
      renderCell: (params) => (
        <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
          {params.value.slice(0, 2).map((tag: string, index: number) => (
            <Chip
              key={index}
              label={tag}
              size="small"
              variant="outlined"
              sx={{ borderRadius: 2, fontSize: '0.7rem' }}
            />
          ))}
          {params.value.length > 2 && (
            <Chip
              label={`+${params.value.length - 2}`}
              size="small"
              variant="outlined"
              sx={{ borderRadius: 2, fontSize: '0.7rem' }}
            />
          )}
        </Box>
      )
    },
    {
      field: 'location',
      headerName: 'Ubicación',
      width: 150,
      renderCell: (params) => (
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <LocationIcon sx={{ fontSize: 16, color: '#64748b' }} />
          <Typography variant="body2" color="text.secondary">
            {params.value}
          </Typography>
        </Box>
      )
    },
    {
      field: 'status',
      headerName: 'Estado',
      width: 120,
      renderCell: (params) => (
        <Chip
          label={getStatusText(params.value)}
          size="small"
          color={getStatusColor(params.value) as any}
          sx={{ borderRadius: 2 }}
        />
      )
    },
    {
      field: 'createdAt',
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
        <LinearProgress />
      </Box>
    );
  }

  const handleCreateProjectFromAgent = async () => {
    setAgentDialogError('');
    try {
      const payload = JSON.parse(agentJsonText) as Record<string, unknown>;
      setAgentDialogLoading(true);
      const res = await agentOutputService.createProjectFromPayload(payload, token!);
      if (res.status === 'success' && res.data) {
        const newProject = res.data as { id: number; name?: string };
        setAgentDialogOpen(false);
        setAgentJsonText('');
        fetchProjects();
        setSnackbar({ open: true, message: `Proyecto "${newProject.name || 'Nuevo'}" creado desde agente IA.`, severity: 'success' });
        navigate(`/projects/${newProject.id}`);
      } else {
        setAgentDialogError(res.error || res.message || 'Error al crear el proyecto');
      }
    } catch (e) {
      setAgentDialogError(e instanceof Error ? e.message : 'JSON inválido. Pegue la salida del agente (salidaAgente.json).');
    } finally {
      setAgentDialogLoading(false);
    }
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <BusinessIcon color="primary" sx={{ fontSize: 32 }} />
          <Typography variant="h4" component="h1">
            Proyectos
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button
            variant="outlined"
            startIcon={<SmartToyIcon />}
            onClick={() => { setAgentDialogError(''); setAgentJsonText(''); setAgentDialogOpen(true); }}
          >
            Crear desde agente IA
          </Button>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => handleOpenDialog()}
          >
            Nuevo Proyecto
          </Button>
        </Box>
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
          rows={projects}
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
        <MenuItem onClick={() => selectedProject && handleViewProject(selectedProject)}>
          <ListItemIcon>
            <ViewIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>Ver Proyecto</ListItemText>
        </MenuItem>
        <MenuItem onClick={() => selectedProject && handleEditProject(selectedProject)}>
          <ListItemIcon>
            <EditIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>Editar</ListItemText>
        </MenuItem>
        <MenuItem onClick={() => selectedProject && handleDeleteProject(selectedProject)}>
          <ListItemIcon>
            <DeleteIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>Eliminar</ListItemText>
        </MenuItem>
      </Menu>

      {/* Crear proyecto desde salida del agente IA (n8n) */}
      <Dialog open={agentDialogOpen} onClose={() => !agentDialogLoading && setAgentDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Crear proyecto desde salida del agente IA (n8n)</DialogTitle>
        <DialogContent>
          <Alert severity="info" sx={{ mb: 2 }}>
            Pegue aquí el JSON que devuelve el agente de n8n (ej. salidaAgente.json). Se creará un proyecto con BMC, actividades, estrategia comercial, roadmap, análisis y veredicto.
          </Alert>
          {agentDialogError && (
            <Alert severity="error" sx={{ mb: 2 }} onClose={() => setAgentDialogError('')}>
              {agentDialogError}
            </Alert>
          )}
          <TextField
            fullWidth
            multiline
            minRows={12}
            maxRows={24}
            value={agentJsonText}
            onChange={(e) => setAgentJsonText(e.target.value)}
            placeholder='{"metadata": {...}, "conversacion": {...}, "business_model_canvas": {...}, ...}'
            sx={{ fontFamily: 'monospace', fontSize: '0.85rem' }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setAgentDialogOpen(false)} disabled={agentDialogLoading}>Cancelar</Button>
          <Button variant="contained" onClick={handleCreateProjectFromAgent} disabled={agentDialogLoading || !agentJsonText.trim()}>
            {agentDialogLoading ? 'Creando...' : 'Crear proyecto'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Create/Edit Project Dialog */}
      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="md" fullWidth>
        <DialogTitle>
          {editingProject ? 'Editar Proyecto' : 'Nuevo Proyecto'}
        </DialogTitle>
        <DialogContent>
          {loadingFormData ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
              <LinearProgress />
            </Box>
          ) : (
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3, mt: 1 }}>
              {/* Nombre del Proyecto - Ancho completo */}
              <TextField
                fullWidth
                label="Nombre del Proyecto"
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

              {/* Categoría - Ancho completo */}
              <FormControl fullWidth>
                <InputLabel>Categoría</InputLabel>
                <Select
                  value={formData.category}
                  label="Categoría"
                  onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                  size="medium"
                  sx={{
                    '& .MuiOutlinedInput-root': {
                      borderRadius: 2,
                    }
                  }}
                >
                  {categories.map((category) => (
                    <MenuItem key={category.id} value={category.name}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Box
                          sx={{
                            width: 16,
                            height: 16,
                            borderRadius: '50%',
                            backgroundColor: category.color,
                            border: '1px solid #ddd'
                          }}
                        />
                        {category.name}
                      </Box>
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>

              {/* Estado - Ancho completo */}
              <FormControl fullWidth>
                <InputLabel>Estado</InputLabel>
                <Select
                  value={formData.status}
                  label="Estado"
                  onChange={(e) => setFormData({ ...formData, status: e.target.value as 'active' | 'inactive' | 'completed' })}
                  size="medium"
                  sx={{
                    '& .MuiOutlinedInput-root': {
                      borderRadius: 2,
                    }
                  }}
                >
                  <MenuItem value="active">Activo</MenuItem>
                  <MenuItem value="inactive">Inactivo</MenuItem>
                  <MenuItem value="completed">Completado</MenuItem>
                </Select>
              </FormControl>

              {/* Ubicación - Ancho completo */}
              <FormControl fullWidth>
                <InputLabel>Ubicación</InputLabel>
                <Select
                  value={formData.location}
                  label="Ubicación"
                  onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                  size="medium"
                  sx={{
                    '& .MuiOutlinedInput-root': {
                      borderRadius: 2,
                    }
                  }}
                >
                  {locations.map((location) => (
                    <MenuItem key={location.id} value={location.name}>
                      {location.name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>

              {/* Etiquetas - Ancho completo */}
              <FormControl fullWidth>
                <InputLabel>Etiquetas</InputLabel>
                <Select
                  multiple
                  value={formData.tags}
                  label="Etiquetas"
                  onChange={(e) => setFormData({ ...formData, tags: e.target.value as string[] })}
                  renderValue={(selected) => (
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                      {selected.map((value) => (
                        <Chip key={value} label={value} size="small" />
                      ))}
                    </Box>
                  )}
                  size="medium"
                  sx={{
                    '& .MuiOutlinedInput-root': {
                      borderRadius: 2,
                    }
                  }}
                >
                  {tags.map((tag) => (
                    <MenuItem key={tag.id} value={tag.name}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Box
                          sx={{
                            width: 16,
                            height: 16,
                            borderRadius: '50%',
                            backgroundColor: tag.color,
                            border: '1px solid #ddd'
                          }}
                        />
                        {tag.name}
                      </Box>
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancelar</Button>
          <Button 
            onClick={handleSubmit} 
            variant="contained"
            disabled={!formData.name || !formData.description || !formData.category || !formData.location || loadingFormData}
          >
            {editingProject ? 'Actualizar' : 'Crear'}
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

export default ProjectsPage;

