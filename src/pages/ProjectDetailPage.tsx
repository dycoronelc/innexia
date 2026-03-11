import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Chip,
  Button,
  Grid,
  Card,
  CardContent,
  LinearProgress,
  Alert,
  Tabs,
  Tab,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions
} from '@mui/material';
import {
  Edit as EditIcon,
  Save as SaveIcon,
  Cancel as CancelIcon,
  Business as BusinessIcon,
  LocationOn,
  Category,
  LocalOffer,
  CalendarToday,
  Person,
  ArrowBack as ArrowBackIcon
} from '@mui/icons-material';
import { useParams, useNavigate } from 'react-router-dom';
import type { Project, BusinessModelCanvas, ProjectActivity, ProjectDocument, User, Category as CategoryType, Tag, ProjectAgentOutput } from '../types';
import BusinessModelCanvasComponent from '../components/BusinessModelCanvas';
import ProjectKanban from '../components/ProjectKanban';
import GanttChart from '../components/GanttChart';
import ProjectDocuments from '../components/ProjectDocuments';
import {
  EstrategiaComercialCards,
  RoadmapCards,
  AnalisisNumericosCards,
  RiesgosCards,
  VeredictoCards,
} from '../components/ProjectAgentOutputCards';
import {
  EstrategiaComercialEditable,
  RoadmapEditable,
  AnalisisFinancieroEditable,
  RiesgosEditable,
  VeredictoEditable,
} from '../components/ProjectAgentOutputEditable';
import { useAuth } from '../contexts/AuthContext';
import { projectService, activityService, bmcService, documentService, masterService, userService, agentOutputService } from '../services/api';
import { formatDate } from '../utils/dateUtils';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`project-tabpanel-${index}`}
      aria-labelledby={`project-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ p: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

const ProjectDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const projectId = id ? parseInt(id) : null;
  const { token } = useAuth();
  const navigate = useNavigate();
  const [project, setProject] = useState<Project | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [tabValue, setTabValue] = useState(0);
  const [editing, setEditing] = useState(false);
  const [editModalOpen, setEditModalOpen] = useState(false);
  const [editForm, setEditForm] = useState({
    name: '',
    description: '',
    category: '',
    tags: [] as string[],
    location: '',
    status: 'active'
  });

  const [projectDocuments, setProjectDocuments] = useState<ProjectDocument[]>([]);
  const [users, setUsers] = useState<User[]>([]);
  const [categories, setCategories] = useState<CategoryType[]>([]);
  const [tags, setTags] = useState<Tag[]>([]);
  const [locations, setLocations] = useState<Array<{id: string, name: string}>>([]);
  const [bmcLoading, setBmcLoading] = useState(false);
  const [bmcError, setBmcError] = useState('');
  const [agentOutput, setAgentOutput] = useState<ProjectAgentOutput | null>(null);
  const [importAgentOpen, setImportAgentOpen] = useState(false);
  const [importAgentJson, setImportAgentJson] = useState('');
  const [importAgentLoading, setImportAgentLoading] = useState(false);
  const [importAgentError, setImportAgentError] = useState('');
  const [projectActivities, setProjectActivities] = useState<ProjectActivity[]>([
    {
      id: '1',
      title: 'Definir arquitectura del sistema',
      description: 'Diseñar la estructura técnica del proyecto',
      status: 'completed',
      priority: 'high',
      assignee: 'Juan Pérez',
      assignees: ['Juan Pérez'],
      startDate: new Date('2024-01-01'),
      dueDate: new Date('2024-01-15'),
      createdAt: new Date('2024-01-01'),
      updatedAt: new Date('2024-01-15'),
      projectId: projectId || 1,
      tags: [],
      comments: [],
      checklists: [],
      attachments: [],
      labels: []
    },
    {
      id: '2',
      title: 'Crear prototipo de UI',
      description: 'Desarrollar mockups y wireframes',
      status: 'in-progress',
      priority: 'medium',
      assignee: 'María García',
      assignees: ['María García'],
      startDate: new Date('2024-01-10'),
      dueDate: new Date('2024-02-01'),
      createdAt: new Date('2024-01-10'),
      updatedAt: new Date('2024-01-20'),
      projectId: projectId || 1,
      tags: [],
      comments: [],
      checklists: [],
      attachments: [],
      labels: []
    },
    {
      id: '3',
      title: 'Implementar autenticación',
      description: 'Sistema de login y registro de usuarios',
      status: 'todo',
      priority: 'high',
      assignee: 'Carlos López',
      assignees: ['Carlos López'],
      startDate: new Date('2024-01-15'),
      dueDate: new Date('2024-02-15'),
      createdAt: new Date('2024-01-15'),
      updatedAt: new Date('2024-01-15'),
      projectId: projectId || 1,
      tags: [],
      comments: [],
      checklists: [],
      attachments: [],
      labels: []
    },
    {
      id: '4',
      title: 'Configurar base de datos',
      description: 'Diseñar esquema y configurar conexiones',
      status: 'review',
      priority: 'medium',
      assignee: 'Ana Martínez',
      assignees: ['Ana Martínez'],
      startDate: new Date('2024-01-05'),
      dueDate: new Date('2024-01-30'),
      createdAt: new Date('2024-01-05'),
      updatedAt: new Date('2024-01-25'),
      projectId: projectId || 1,
      tags: [],
      comments: [],
      checklists: [],
      attachments: [],
      labels: []
    },
    {
      id: '5',
      title: 'Realizar pruebas de integración',
      description: 'Verificar que todos los módulos funcionen correctamente',
      status: 'todo',
      priority: 'low',
      assignee: 'Luis Rodríguez',
      assignees: ['Luis Rodríguez'],
      startDate: new Date('2024-01-20'),
      dueDate: new Date('2024-02-28'),
      createdAt: new Date('2024-01-20'),
      updatedAt: new Date('2024-01-20'),
      projectId: projectId || 1,
      tags: [],
      comments: [],
      checklists: [],
      attachments: [],
      labels: []
    },
    {
      id: '6',
      title: 'Documentar API',
      description: 'Crear documentación técnica para desarrolladores',
      status: 'todo',
      priority: 'medium',
      assignee: 'Sofia Herrera',
      assignees: ['Sofia Herrera'],
      startDate: new Date('2024-01-18'),
      dueDate: new Date('2024-02-10'),
      createdAt: new Date('2024-01-18'),
      updatedAt: new Date('2024-01-18'),
      projectId: projectId || 1,
      tags: [],
      comments: [],
      checklists: [],
      attachments: [],
      labels: []
    }
  ]);

  useEffect(() => {
    if (token && projectId) {
    fetchProject();
    }
  }, [projectId, token]);

  // Función para refrescar solo los documentos
  const refreshDocuments = async () => {
    if (!projectId || !token) return;
    
    try {
      // Refrescando documentos del proyecto
      const documentsResponse = await documentService.getProjectDocuments(projectId, token);
      if (documentsResponse.status === 'success') {
        // Raw documents from backend
        const processedDocuments = documentsResponse.data.map((document: any) => ({
          id: document.id.toString(),
          name: document.filename || 'Sin nombre',
          originalName: document.original_filename || 'Sin nombre original',
          fileType: document.file_type || 'unknown',
          fileSize: document.file_size || 0,
          uploadedBy: document.uploader_name || 'Sin especificar',
          uploadedAt: document.created_at ? new Date(document.created_at) : new Date(),
          description: document.description || '',
          projectId: id
        }));
        // Processed documents
        setProjectDocuments(processedDocuments);
      }
    } catch (error) {
      console.error('Error refreshing documents:', error);
    }
  };

  const fetchProject = async () => {
    if (!projectId || !token) return;

    try {
      setLoading(true);
      
      // Cargar proyecto
      const projectResponse = await projectService.getProject(projectId, token);
      if (projectResponse.status === 'success') {
        // Project loaded from backend
        
        // Procesar proyecto con fallbacks para fechas
        const projectData = {
          ...projectResponse.data,
          createdAt: projectResponse.data.created_at ? new Date(projectResponse.data.created_at) : new Date(),
          updatedAt: projectResponse.data.updated_at ? new Date(projectResponse.data.updated_at) : new Date()
        };
        
        // Processed project data
        setProject(projectData);
      setEditForm({
          name: projectData.name,
          description: projectData.description || '',
          category: projectData.category?.id || '',
          tags: projectData.tags?.map((tag: any) => tag.id) || [],
          location: projectData.location?.id || '',
          status: projectData.status?.id || 'active'
        });
      }

      // Cargar actividades del proyecto
      const activitiesResponse = await activityService.getProjectActivities(id, token);
      if (activitiesResponse.status === 'success') {
        // Raw activities from backend
        const activities = activitiesResponse.data.map((activity: any) => {
          // Validar y crear fechas con fallbacks
          const startDate = activity.start_date ? new Date(activity.start_date) : new Date();
          const dueDate = activity.due_date ? new Date(activity.due_date) : new Date(startDate.getTime() + 7 * 24 * 60 * 60 * 1000);
          const createdAt = activity.created_at ? new Date(activity.created_at) : new Date();
          const updatedAt = activity.updated_at ? new Date(activity.updated_at) : new Date();
          
          return {
            id: activity.id.toString(),
            title: activity.title,
            description: activity.description,
            status: activity.status,
            priority: activity.priority,
            assignee: activity.assignee_user?.full_name || 'Sin asignar',
            assignees: [], // Se cargará desde las APIs de Trello
            tags: [], // Se cargará desde las APIs de Trello
            comments: [], // Se cargará desde las APIs de Trello
            checklists: [], // Se cargará desde las APIs de Trello
            attachments: [], // Se cargará desde las APIs de Trello
            labels: [], // Se cargará desde las APIs de Trello
            startDate,
            dueDate,
            createdAt,
            updatedAt
          };
        });
        // Processed activities for Gantt
        setProjectActivities(activities);
      }

      // Cargar documentos del proyecto
      const documentsResponse = await documentService.getProjectDocuments(id, token);
      if (documentsResponse.status === 'success') {
        // Raw documents from backend
        const processedDocuments = documentsResponse.data.map((document: any) => ({
          id: document.id.toString(),
          name: document.filename || 'Sin nombre',
          originalName: document.original_filename || 'Sin nombre original',
          fileType: document.file_type || 'unknown',
          fileSize: document.file_size || 0,
          uploadedBy: document.uploader_name || 'Sin especificar',
          uploadedAt: document.created_at ? new Date(document.created_at) : new Date(),
          description: document.description || '',
          projectId: id
        }));
        // Processed documents
        setProjectDocuments(processedDocuments);
      }

      // Cargar usuarios
      const usersResponse = await userService.getUsers(token);
      if (usersResponse.status === 'success') {
        setUsers(usersResponse.data);
      }

      // Cargar categorías
      const categoriesResponse = await masterService.getCategories(token);
      if (categoriesResponse.status === 'success') {
        setCategories(categoriesResponse.data);
      }

      // Cargar etiquetas
      const tagsResponse = await masterService.getTags(token);
      if (tagsResponse.status === 'success') {
        setTags(tagsResponse.data);
      }

      // Cargar ubicaciones
      const locationsResponse = await masterService.getLocations(token);
      if (locationsResponse.status === 'success') {
        setLocations(locationsResponse.data);
      }

      // Cargar salida del agente IA (n8n) si existe
      const agentRes = await agentOutputService.getByProject(projectId, token);
      if (agentRes.status === 'success' && agentRes.data) {
        setAgentOutput(agentRes.data as ProjectAgentOutput);
      } else {
        setAgentOutput(null);
      }

      // Cargar Business Model Canvas
      await fetchBusinessModelCanvas();

    } catch (err) {
      console.error('Error fetching project data:', err);
      setError('Error al cargar los datos del proyecto');
    } finally {
      setLoading(false);
    }
  };



  const fetchBusinessModelCanvas = async () => {
    if (!token || !id) return;
    
    try {
      setBmcLoading(true);
      setBmcError('');
            // Fetching BMC for project ID
      
      // Usar el endpoint de prueba para evitar problemas de autenticación
      let response;
      try {
        const testResponse = await fetch(`http://localhost:8000/api/bmc/test/${id}`);
        // Test endpoint status
        
        if (testResponse.ok) {
          const testData = await testResponse.json();
          response = {
            status: 'success',
            data: testData
          };
          // Test endpoint response received
        } else {
          response = {
            status: 'error',
            error: `HTTP ${testResponse.status}: ${testResponse.statusText}`
          };
          // Test endpoint failed
        }
      } catch (testError) {
        console.error('Test endpoint error:', testError);
        response = {
          status: 'error',
          error: testError.message
        };
      }
      
      if (response.status === 'success' && response.data) {
        const bmcData = response.data;
        // Raw BMC data from API
        
        const processedBMC: BusinessModelCanvas = {
          id: bmcData.id.toString(),
          projectId: id,
          keyPartners: bmcData.key_partners || [],
          keyActivities: bmcData.key_activities || [],
          keyResources: bmcData.key_resources || [],
          valuePropositions: bmcData.value_propositions || [],
          customerRelationships: bmcData.customer_relationships || [],
          channels: bmcData.channels || [],
          customerSegments: bmcData.customer_segments || [],
          costStructure: bmcData.cost_structure || [],
          revenueStreams: bmcData.revenue_streams || [],
          createdAt: bmcData.created_at ? new Date(bmcData.created_at) : new Date(),
          updatedAt: bmcData.updated_at ? new Date(bmcData.updated_at) : new Date()
        };
        
        // Processed BMC
        setProject(prevProject => {
          // Previous project state
          const updatedProject = prevProject ? {
            ...prevProject,
            businessModelCanvas: processedBMC
          } : null;
          // Updated project state
          return updatedProject;
        });
      } else {
        // BMC response not successful
        // Solo crear BMC por defecto si realmente no existe
        if (response.status === 'error' && response.error?.includes('no encontrado')) {
          // BMC no encontrado en la base de datos - no creando BMC por defecto
          // No crear BMC por defecto, dejar que el usuario lo cree manualmente
        } else {
          console.error('Error al cargar BMC:', response.error);
        }
      }
    } catch (error: any) {
      console.error('Error fetching BMC:', error);
      
      // Si es un error de autenticación, no crear BMC por defecto
      if (error.message && error.message.includes('Token inválido')) {
        // Authentication error when fetching BMC
        return;
      }
      
      // Para otros errores, no crear BMC por defecto
      console.error('Error al cargar BMC:', error.message);
      // No crear BMC por defecto, dejar que el usuario lo cree manualmente
    } finally {
      setBmcLoading(false);
    }
  };

  const handleTabChange = (_: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const handleEdit = () => {
    if (project) {
      setEditForm({
        name: project.name,
        description: project.description || '',
        category: project.category || '',
        tags: project.tags || [],
        location: project.location || '',
        status: project.status || 'active'
      });
      setEditModalOpen(true);
    }
  };

  const handleCancelEdit = () => {
    setEditing(false);
    setEditForm({
      name: project?.name || '',
      description: project?.description || '',
      category: project?.category || '',
      tags: project?.tags || [],
      location: project?.location || '',
      status: project?.status || 'active'
    });
  };

  const handleCloseEditModal = () => {
    setEditModalOpen(false);
    setEditForm({
      name: project?.name || '',
      description: project?.description || '',
      category: project?.category || '',
      tags: project?.tags || [],
      location: project?.location || '',
      status: project?.status || 'active'
    });
  };

  const handleSave = async () => {
    if (!project || !token) return;

    try {
      const updateData = {
        name: editForm.name,
        description: editForm.description,
        category: editForm.category,
        tags: editForm.tags,
        location: editForm.location,
        status: editForm.status
      };
      
      const response = await projectService.updateProject(project.id, updateData, token);
      
      if (response.status === 'success') {
        // Actualizar el proyecto local con los datos del formulario
      const updatedProject = {
        ...project,
        ...editForm,
        status: editForm.status as 'active' | 'inactive' | 'completed',
        updatedAt: new Date()
      };
      
      setProject(updatedProject);
      setEditing(false);
      setEditModalOpen(false);
        
        // Recargar los datos del proyecto desde el backend
        await fetchProject();
      } else {
        setError(response.error || 'Error al actualizar el proyecto');
      }
    } catch (error) {
      console.error('Error updating project:', error);
      setError('Error al actualizar el proyecto');
    }
  };

  const handleCanvasUpdate = (canvas: BusinessModelCanvas) => {
    if (project) {
      setProject({
        ...project,
        businessModelCanvas: canvas
      });
    }
  };

  const handleActivitiesUpdate = (activities: ProjectActivity[]) => {
    setProjectActivities(activities);
  };

  const handleAddDocument = (document: ProjectDocument) => {
    setProjectDocuments(prev => [...prev, document]);
  };

  const handleDeleteDocument = (documentId: string) => {
    setProjectDocuments(prev => prev.filter(d => d.id !== documentId));
  };

  const handleUpdateDocument = (document: ProjectDocument) => {
    setProjectDocuments(prev => prev.map(d => d.id === document.id ? document : d));
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

  if (loading) {
    return (
      <Box sx={{ width: '100%' }}>
        <LinearProgress />
      </Box>
    );
  }

  if (error || !project) {
    return (
      <Alert severity="error">
        {error || 'Proyecto no encontrado'}
      </Alert>
    );
  }

  // Log para debug - removido para limpiar consola

  const handleImportAgentOutput = async () => {
    if (!project || !token) return;
    setImportAgentError('');
    try {
      const payload = JSON.parse(importAgentJson) as Record<string, unknown>;
      setImportAgentLoading(true);
      const res = await agentOutputService.save(project.id, payload, token);
      if (res.status === 'success' && res.data) {
        setAgentOutput(res.data as ProjectAgentOutput);
        setImportAgentOpen(false);
        setImportAgentJson('');
        // Refrescar proyecto para que la pestaña BMC muestre el canvas sincronizado en business_model_canvases
        await fetchProject();
      } else {
        setImportAgentError(res.error || res.message || 'Error al guardar');
      }
    } catch (e) {
      setImportAgentError(e instanceof Error ? e.message : 'JSON inválido');
    } finally {
      setImportAgentLoading(false);
    }
  };

  const refreshAgentOutput = async () => {
    if (!projectId || !token) return;
    const agentRes = await agentOutputService.getByProject(projectId, token);
    if (agentRes.status === 'success' && agentRes.data) {
      setAgentOutput(agentRes.data as ProjectAgentOutput);
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
          <Box>
           <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
             <BusinessIcon sx={{ fontSize: 32, color: 'primary.main' }} />
             <Typography variant="h4" component="h1">
              {project.name}
            </Typography>
           </Box>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
              <Chip
                label={project.category}
                icon={<Category />}
                variant="outlined"
                color="primary"
              />
              <Chip
                label={getStatusText(project.status)}
                color={getStatusColor(project.status) as any}
              />
              <Chip
                label={project.location}
                icon={<LocationOn />}
                variant="outlined"
              />
            </Box>
          </Box>
          <Box sx={{ display: 'flex', gap: 1 }}>
           <Button
             variant="outlined"
             startIcon={<ArrowBackIcon />}
             onClick={() => navigate('/projects')}
             sx={{ mr: 1 }}
           >
             Volver
           </Button>
           <Button
             variant="outlined"
             onClick={() => { setImportAgentError(''); setImportAgentJson(''); setImportAgentOpen(true); }}
           >
             Importar salida agente
           </Button>
            {editing ? (
              <>
                <Button
                  variant="contained"
                  startIcon={<SaveIcon />}
                  onClick={handleSave}
                >
                  Guardar
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<CancelIcon />}
                  onClick={handleCancelEdit}
                >
                  Cancelar
                </Button>
              </>
            ) : (
              <Button
                variant="outlined"
                startIcon={<EditIcon />}
                onClick={handleEdit}
              >
                Editar
              </Button>
            )}
          </Box>
        </Box>

        <Typography variant="body1" color="text.secondary" sx={{ mb: 2 }}>
          {project.description}
        </Typography>

      {/* Tabs */}
      <Paper sx={{ width: '100%' }}>
        <Tabs value={tabValue} onChange={handleTabChange} aria-label="project tabs">
          <Tab label="Información General" />
          <Tab label="Business Model Canvas" />
          <Tab label="Actividades" />
          <Tab label="Gantt" />
          <Tab label="Documentación" />
          <Tab label="Estrategia Comercial" />
          <Tab label="Roadmap" />
          <Tab label="Números" />
          <Tab label="Riesgos" />
          <Tab label="Veredicto" />
        </Tabs>

        <TabPanel value={tabValue} index={0}>
          <Grid container spacing={3}>
            <Grid columns={{ xs: 12, md: 6 }}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Detalles del Proyecto
                  </Typography>
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Person color="action" />
                      <Typography variant="body2">
                        <strong>Creado:</strong> {project.createdAt ? formatDate(project.createdAt) : 'No disponible'}
                      </Typography>
                    </Box>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <CalendarToday color="action" />
                      <Typography variant="body2">
                        <strong>Última actualización:</strong> {project.updatedAt ? formatDate(project.updatedAt) : 'No disponible'}
                      </Typography>
                    </Box>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Category color="action" />
                      <Typography variant="body2">
                        <strong>Categoría:</strong> {project.category}
                      </Typography>
                    </Box>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <LocationOn color="action" />
                      <Typography variant="body2">
                        <strong>Ubicación:</strong> {project.location}
                      </Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>

            <Grid columns={{ xs: 12, md: 6 }}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Etiquetas
                  </Typography>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                    {project.tags.map((tag, index) => (
                      <Chip
                        key={index}
                        label={tag}
                        icon={<LocalOffer />}
                        variant="outlined"
                        size="small"
                      />
                    ))}
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </TabPanel>

        <TabPanel value={tabValue} index={1}>
          {bmcLoading ? (
            <Box sx={{ textAlign: 'center', py: 4 }}>
              <LinearProgress sx={{ mb: 2 }} />
              <Typography variant="body2" color="text.secondary">
                Cargando Business Model Canvas...
              </Typography>
            </Box>
          ) : bmcError ? (
            <Box sx={{ textAlign: 'center', py: 4 }}>
              <Alert severity="error" sx={{ mb: 2 }}>
                {bmcError}
              </Alert>
              <Button
                variant="outlined"
                onClick={() => fetchBusinessModelCanvas()}
                sx={{ mt: 2 }}
              >
                Reintentar
              </Button>
            </Box>
                     ) : project.businessModelCanvas ? (
             <>
               <Typography variant="body2" sx={{ mb: 2, color: 'success.main' }}>
                 ✓ Business Model Canvas cargado correctamente
               </Typography>
               {(() => {
                 // Rendering BMC component with canvas
                 return (
            <BusinessModelCanvasComponent
              canvas={project.businessModelCanvas}
              onUpdate={handleCanvasUpdate}
            />
                 );
               })()}
             </>
          ) : (
            <Box sx={{ textAlign: 'center', py: 4 }}>
              <BusinessIcon sx={{ fontSize: 60, color: 'text.secondary', mb: 2 }} />
              <Typography variant="h6" color="text.secondary" gutterBottom>
                No hay Business Model Canvas
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Cree un Business Model Canvas para este proyecto
              </Typography>
              <Button
                variant="contained"
                startIcon={<BusinessIcon />}
                sx={{ mt: 2 }}
                onClick={() => {
                  // Create new BMC
                  const newBMC: BusinessModelCanvas = {
                    id: Date.now().toString(),
                    projectId: project.id,
                    keyPartners: [],
                    keyActivities: [],
                    keyResources: [],
                    valuePropositions: [],
                    customerRelationships: [],
                    channels: [],
                    customerSegments: [],
                    costStructure: [],
                    revenueStreams: [],
                    createdAt: new Date(),
                    updatedAt: new Date()
                  };
                  setProject({
                    ...project,
                    businessModelCanvas: newBMC
                  });
                }}
              >
                Crear Business Model Canvas
              </Button>
            </Box>
          )}
        </TabPanel>

        <TabPanel value={tabValue} index={2}>
          {(() => {
            // ProjectKanban props
            return (
          <ProjectKanban
            activities={projectActivities}
            onUpdateActivities={handleActivitiesUpdate}
            projectId={project.id}
                availableTags={tags.map(t => ({ id: t.id, name: t.name, color: t.color }))}
                availableUsers={users.map(u => ({ id: u.id, fullName: u.fullName, username: u.username, role: u.role }))}
                availableCategories={categories.map(c => ({ id: c.id, name: c.name, color: c.color }))}
          />
            );
          })()}
        </TabPanel>

        <TabPanel value={tabValue} index={3}>
          {(() => {
            // Validar que project existe y tiene createdAt
            if (!project || !project.createdAt) {
              console.log('Project or project.createdAt is undefined');
              return (
                <Box sx={{ textAlign: 'center', py: 4 }}>
                  <Typography variant="body2" color="text.secondary">
                    Cargando datos del proyecto...
                  </Typography>
                </Box>
              );
            }
            
            const projectStartDate = project.createdAt;
            const ganttEndDate = projectActivities.length > 0 
              ? new Date(Math.max(...projectActivities.map(a => a.dueDate && !isNaN(a.dueDate.getTime()) ? a.dueDate.getTime() : 0)))
              : new Date(projectStartDate.getTime() + 30 * 24 * 60 * 60 * 1000);
            
            // GanttChart props
            
            return (
          <GanttChart
            activities={projectActivities}
                projectStartDate={projectStartDate}
                projectEndDate={ganttEndDate}
            onUpdateActivity={(updatedActivity) => {
              const updatedActivities = projectActivities.map(a => 
                a.id === updatedActivity.id ? updatedActivity : a
              );
              setProjectActivities(updatedActivities);
            }}
          />
            );
          })()}
        </TabPanel>

        <TabPanel value={tabValue} index={4}>
          <ProjectDocuments
            documents={projectDocuments}
            projectId={project.id}
            onAddDocument={handleAddDocument}
            onDeleteDocument={handleDeleteDocument}
            onUpdateDocument={handleUpdateDocument}
          />
        </TabPanel>

        <TabPanel value={tabValue} index={5}>
          {projectId && token ? (
            <EstrategiaComercialEditable
              data={agentOutput?.estrategia_comercial as Record<string, unknown> | undefined}
              projectId={projectId}
              token={token}
              onSaved={refreshAgentOutput}
            />
          ) : (
            <EstrategiaComercialCards data={agentOutput?.estrategia_comercial as Record<string, unknown> | undefined} />
          )}
        </TabPanel>
        <TabPanel value={tabValue} index={6}>
          {projectId && token ? (
            <RoadmapEditable
              data={agentOutput?.roadmap_estrategico as Record<string, unknown> | undefined}
              projectId={projectId}
              token={token}
              onSaved={refreshAgentOutput}
            />
          ) : (
            <RoadmapCards data={agentOutput?.roadmap_estrategico as Record<string, unknown> | undefined} />
          )}
        </TabPanel>
        <TabPanel value={tabValue} index={7}>
          {projectId && token ? (
            <AnalisisFinancieroEditable
              data={agentOutput?.analisis_financiero as Record<string, unknown> | undefined}
              projectId={projectId}
              token={token}
              onSaved={refreshAgentOutput}
            />
          ) : (
            <AnalisisNumericosCards data={agentOutput?.analisis_financiero as Record<string, unknown> | undefined} />
          )}
        </TabPanel>
        <TabPanel value={tabValue} index={8}>
          {projectId && token ? (
            <RiesgosEditable
              data={agentOutput?.analisis_riesgos as Record<string, unknown> | undefined}
              projectId={projectId}
              token={token}
              onSaved={refreshAgentOutput}
            />
          ) : (
            <RiesgosCards data={agentOutput?.analisis_riesgos as Record<string, unknown> | undefined} />
          )}
        </TabPanel>
        <TabPanel value={tabValue} index={9}>
          {projectId && token ? (
            <VeredictoEditable
              data={agentOutput?.veredicto_final as Record<string, unknown> | undefined}
              projectId={projectId}
              token={token}
              onSaved={refreshAgentOutput}
            />
          ) : (
            <VeredictoCards data={agentOutput?.veredicto_final as Record<string, unknown> | undefined} />
          )}
        </TabPanel>
      </Paper>

      {/* Dialog Importar salida del agente */}
      <Dialog open={importAgentOpen} onClose={() => !importAgentLoading && setImportAgentOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Importar salida del agente IA (n8n)</DialogTitle>
        <DialogContent>
          <Alert severity="info" sx={{ mb: 2 }}>
            Pegue el JSON que devuelve el agente. Se actualizarán las pestañas Estrategia Comercial, Roadmap, Números, Riesgos y Veredicto.
          </Alert>
          {importAgentError && (
            <Alert severity="error" sx={{ mb: 2 }} onClose={() => setImportAgentError('')}>
              {importAgentError}
            </Alert>
          )}
          <TextField
            fullWidth
            multiline
            minRows={10}
            value={importAgentJson}
            onChange={(e) => setImportAgentJson(e.target.value)}
            placeholder='{"metadata": {...}, "business_model_canvas": {...}, "estrategia_comercial": {...}, ...}'
            sx={{ fontFamily: 'monospace', fontSize: '0.85rem' }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setImportAgentOpen(false)} disabled={importAgentLoading}>Cancelar</Button>
          <Button variant="contained" onClick={handleImportAgentOutput} disabled={importAgentLoading || !importAgentJson.trim()}>
            {importAgentLoading ? 'Guardando...' : 'Guardar'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Modal de Edición */}
      <Dialog open={editModalOpen} onClose={handleCloseEditModal} maxWidth="md" fullWidth>
        <DialogTitle>
          Editar Proyecto
        </DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3, pt: 1 }}>
            {/* Nombre del Proyecto */}
            <TextField
              fullWidth
              label="Nombre del Proyecto"
              value={editForm.name}
              onChange={(e) => setEditForm({ ...editForm, name: e.target.value })}
              required
              size="medium"
              sx={{
                '& .MuiOutlinedInput-root': {
                  borderRadius: 2,
                }
              }}
            />

            {/* Descripción */}
            <TextField
              fullWidth
              label="Descripción"
              value={editForm.description}
              onChange={(e) => setEditForm({ ...editForm, description: e.target.value })}
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

            {/* Categoría */}
            <FormControl fullWidth>
              <InputLabel>Categoría</InputLabel>
              <Select
                value={editForm.category}
                label="Categoría"
                onChange={(e) => setEditForm({ ...editForm, category: e.target.value })}
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

            {/* Estado */}
            <FormControl fullWidth>
              <InputLabel>Estado</InputLabel>
              <Select
                value={editForm.status}
                label="Estado"
                onChange={(e) => setEditForm({ ...editForm, status: e.target.value as 'active' | 'inactive' | 'completed' })}
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

            {/* Ubicación */}
            <FormControl fullWidth>
              <InputLabel>Ubicación</InputLabel>
              <Select
                value={editForm.location}
                label="Ubicación"
                onChange={(e) => setEditForm({ ...editForm, location: e.target.value })}
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

            {/* Etiquetas */}
            <FormControl fullWidth>
              <InputLabel>Etiquetas</InputLabel>
              <Select
                multiple
                value={editForm.tags}
                label="Etiquetas"
                onChange={(e) => setEditForm({ ...editForm, tags: e.target.value as string[] })}
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
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseEditModal}>Cancelar</Button>
          <Button 
            onClick={handleSave} 
            variant="contained"
            disabled={!editForm.name || !editForm.description || !editForm.category || !editForm.location}
          >
            Actualizar
          </Button>
        </DialogActions>
      </Dialog>

    </Box>
  );
};

export default ProjectDetailPage;

