import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  Tabs,
  Tab,
  Card,
  CardContent,
  Button,
  IconButton,
  Chip,
  TextField,
  InputAdornment,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Grid,
  Paper,
  Divider,
  Alert,
  Skeleton,
  Fab,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Snackbar,
  Menu,
  ListItemIcon,
  ListItemText,
  LinearProgress
} from '@mui/material';
import {
  Add,
  Search,
  FilterList,
  School,
  Article,
  VideoLibrary,
  Mic,
  Timeline,
  PlayCircle,
  Web,
  Edit,
  Delete,
  Visibility,
  Publish,
  Archive,
  MoreVert,
  ContentCopy,
  Download,
  Share,
  Bookmark,
  ThumbUp,
  Visibility as ViewsIcon
} from '@mui/icons-material';
import { useTheme } from '@mui/material/styles';
import { useAuth } from '../contexts/AuthContext';
import { educationalContentService } from '../services/api';
import ContentForm, { type ContentFormData } from '../components/ContentForm';

interface ContentItem {
  id: number;
  title: string;
  description: string;
  content_type: 'article' | 'video' | 'podcast' | 'infographic' | 'course' | 'webinar';
  content_source: 'internal' | 'rss_feed' | 'youtube' | 'vimeo' | 'spotify' | 'custom_api';
  source_url?: string;
  content_data?: any;
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  duration_minutes?: number;
  author?: string;
  instructor?: string;
  thumbnail_url?: string;
  tags?: string[];
  categories?: string[];
  status: 'draft' | 'published' | 'archived' | 'moderation';
  published_at?: string;
  created_at: string;
  updated_at: string;
  created_by: number;
  moderated_by?: number;
  moderation_notes?: string;
  view_count: number;
  like_count: number;
  bookmark_count: number;
  rating: number;
  rating_count: number;
}

const ContentManagementPage: React.FC = () => {
  const theme = useTheme();
  const { token } = useAuth();
  const [activeTab, setActiveTab] = useState(0);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedType, setSelectedType] = useState('all');
  const [selectedDifficulty, setSelectedDifficulty] = useState('all');
  const [selectedStatus, setSelectedStatus] = useState('all');
  const [showFilters, setShowFilters] = useState(false);
  const [contentItems, setContentItems] = useState<ContentItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedContent, setSelectedContent] = useState<ContentItem | null>(null);
  const [showContentDialog, setShowContentDialog] = useState(false);
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [showEditDialog, setShowEditDialog] = useState(false);
  const [formLoading, setFormLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [selectedItem, setSelectedItem] = useState<ContentItem | null>(null);

  // Cargar contenido desde la API
  const fetchContent = async () => {
    if (!token) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const filters = {
        search: searchTerm || undefined,
        content_type: selectedType !== 'all' ? selectedType : undefined,
        difficulty: selectedDifficulty !== 'all' ? selectedDifficulty : undefined,
        status: selectedStatus !== 'all' ? selectedStatus : undefined,
        limit: 50,
        offset: 0
      };

      const response = await educationalContentService.getContent(filters, token);
      
      if (response.status === 'success' && response.data) {
        setContentItems(response.data);
      } else {
        setError('Error al cargar el contenido');
      }
    } catch (error) {
      console.error('Error fetching content:', error);
      setError('Error al cargar el contenido');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchContent();
  }, [token, searchTerm, selectedType, selectedDifficulty, selectedStatus]);

  const tabs = [
    { label: 'Todos los Contenidos', value: 0, icon: <School /> },
    { label: 'Videos', value: 1, icon: <VideoLibrary /> },
    { label: 'Podcasts', value: 2, icon: <Mic /> },
    { label: 'Artículos', value: 3, icon: <Article /> },
    { label: 'Cursos', value: 4, icon: <PlayCircle /> },
    { label: 'Noticias', value: 5, icon: <Web /> }
  ];

  const contentTypes = [
    { value: 'all', label: 'Todos los tipos' },
    { value: 'article', label: 'Artículos' },
    { value: 'course', label: 'Cursos' },
    { value: 'news', label: 'Noticias' },
    { value: 'podcast', label: 'Podcasts' },
    { value: 'video', label: 'Videos' }
  ];

  const difficulties = [
    { value: 'all', label: 'Todos los niveles' },
    { value: 'beginner', label: 'Principiante' },
    { value: 'intermediate', label: 'Intermedio' },
    { value: 'advanced', label: 'Avanzado' }
  ];

  const statuses = [
    { value: 'all', label: 'Todos los estados' },
    { value: 'draft', label: 'Borrador' },
    { value: 'moderation', label: 'En moderación' },
    { value: 'published', label: 'Publicado' },
    { value: 'archived', label: 'Archivado' }
  ];

  const filteredContent = contentItems.filter(item => {
    const matchesSearch = item.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         item.description.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesType = selectedType === 'all' || item.content_type === selectedType;
    const matchesDifficulty = selectedDifficulty === 'all' || item.difficulty === selectedDifficulty;
    const matchesStatus = selectedStatus === 'all' || item.status === selectedStatus;

    return matchesSearch && matchesType && matchesDifficulty && matchesStatus;
  });

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
    // Filtrar por tipo de contenido según la pestaña
    if (newValue > 0) {
      const contentTypes = ['video', 'podcast', 'article', 'course', 'news'];
      setSelectedType(contentTypes[newValue - 1]);
    } else {
      setSelectedType('all');
    }
  };

  const getContentTypeIcon = (type: string) => {
    switch (type) {
      case 'article': return <Article />;
      case 'video': return <VideoLibrary />;
      case 'podcast': return <Mic />;
      case 'course': return <PlayCircle />;
      case 'webinar': return <Web />;
      case 'infographic': return <Timeline />;
      default: return <School />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'draft': return 'default';
      case 'moderation': return 'warning';
      case 'published': return 'success';
      case 'archived': return 'error';
      default: return 'default';
    }
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'beginner': return 'success';
      case 'intermediate': return 'warning';
      case 'advanced': return 'error';
      default: return 'default';
    }
  };

  const handleContentClick = (content: ContentItem) => {
    setSelectedContent(content);
    setShowContentDialog(true);
  };

  const handleCreateContent = () => {
    setShowCreateDialog(true);
  };

  const handleEditContent = (content: ContentItem) => {
    setSelectedContent(content);
    setShowEditDialog(true);
    setAnchorEl(null);
  };

  const handleMenuClick = (event: React.MouseEvent<HTMLElement>, content: ContentItem) => {
    setAnchorEl(event.currentTarget);
    setSelectedItem(content);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
    setSelectedItem(null);
  };

  // Función helper para formatear errores de validación
  const formatValidationError = (error: any): string => {
    if (typeof error === 'string') {
      return error;
    }
    
    if (Array.isArray(error)) {
      return error.map(err => {
        if (typeof err === 'object' && err.msg) {
          return `${err.loc?.join('.') || 'Campo'}: ${err.msg}`;
        }
        return String(err);
      }).join(', ');
    }
    
    if (typeof error === 'object' && error !== null) {
      if (error.msg) {
        return `${error.loc?.join('.') || 'Campo'}: ${error.msg}`;
      }
      return JSON.stringify(error);
    }
    
    return String(error);
  };

  const handleCreateSubmit = async (formData: any) => {
    if (!token) return;
    
    setFormLoading(true);
    try {
      console.log('Datos que se envían al backend:', formData);
      const response = await educationalContentService.createContent(formData, token);
      
      if (response.status === 'success') {
        setSuccess('Contenido creado exitosamente');
        setShowCreateDialog(false);
        fetchContent(); // Recargar la lista
      } else {
        const errorMessage = formatValidationError(response.error);
        setError(errorMessage || 'Error al crear el contenido');
      }
    } catch (error) {
      console.error('Error creating content:', error);
      setError('Error al crear el contenido');
    } finally {
      setFormLoading(false);
    }
  };

  const handleEditSubmit = async (formData: any) => {
    if (!token || !selectedContent) return;
    
    setFormLoading(true);
    try {
      const response = await educationalContentService.updateContent(selectedContent.id, formData, token);
      
      if (response.status === 'success') {
        setSuccess('Contenido actualizado exitosamente');
        setShowEditDialog(false);
        fetchContent(); // Recargar la lista
      } else {
        const errorMessage = formatValidationError(response.error);
        setError(errorMessage || 'Error al actualizar el contenido');
      }
    } catch (error) {
      console.error('Error updating content:', error);
      setError('Error al actualizar el contenido');
    } finally {
      setFormLoading(false);
    }
  };

  const handlePublishContent = async (content: ContentItem) => {
    if (!token) return;
    
    try {
      const response = await educationalContentService.publishContent(content.id, token);
      
      if (response.status === 'success') {
        setSuccess('Contenido publicado exitosamente');
        fetchContent(); // Recargar la lista
      } else {
        setError(response.error || 'Error al publicar el contenido');
      }
    } catch (error) {
      console.error('Error publishing content:', error);
      setError('Error al publicar el contenido');
    }
    handleMenuClose();
  };

  const handleArchiveContent = async (content: ContentItem) => {
    if (!token) return;
    
    try {
      const response = await educationalContentService.archiveContent(content.id, token);
      
      if (response.status === 'success') {
        setSuccess('Contenido archivado exitosamente');
        fetchContent(); // Recargar la lista
      } else {
        setError(response.error || 'Error al archivar el contenido');
      }
    } catch (error) {
      console.error('Error archiving content:', error);
      setError('Error al archivar el contenido');
    }
    handleMenuClose();
  };

  const handleDeleteContent = async (content: ContentItem) => {
    if (!token) return;
    
    if (!window.confirm('¿Estás seguro de que quieres eliminar este contenido?')) {
      return;
    }
    
    try {
      const response = await educationalContentService.deleteContent(content.id, token);
      
      if (response.status === 'success') {
        setSuccess('Contenido eliminado exitosamente');
        fetchContent(); // Recargar la lista
      } else {
        setError(response.error || 'Error al eliminar el contenido');
      }
    } catch (error) {
      console.error('Error deleting content:', error);
      setError('Error al eliminar el contenido');
    }
    handleMenuClose();
  };

  return (
    <Container maxWidth={false} sx={{ py: 3, px: { xs: 2, sm: 3, md: 4 } }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
          <School sx={{ fontSize: 40, color: 'primary.main' }} />
          <Typography variant="h3" component="h1" sx={{ fontWeight: 'bold' }}>
            Gestión de Contenido
          </Typography>
        </Box>
        <Typography variant="h6" color="text.secondary" sx={{ mb: 3 }}>
          Administra todo el contenido educativo de la plataforma
        </Typography>
      </Box>

      {/* Tabs de navegación */}
      <Paper sx={{ mb: 3 }}>
        <Tabs value={activeTab} onChange={handleTabChange} variant="scrollable" scrollButtons="auto">
          {tabs.map((tab) => (
            <Tab 
              key={tab.value} 
              label={tab.label} 
              value={tab.value}
              icon={tab.icon}
              iconPosition="start"
            />
          ))}
        </Tabs>
      </Paper>

      {/* Filtros y búsqueda */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Grid container spacing={3} alignItems="center">
          {/* Búsqueda */}
          <Grid size={{ xs: 12, md: 4 }}>
            <TextField
              fullWidth
              placeholder="Buscar contenido..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <Search />
                  </InputAdornment>
                ),
              }}
            />
          </Grid>

          {/* Filtros */}
          <Grid size={{ xs: 12, md: 8 }}>
            <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
              <FormControl size="small" sx={{ minWidth: 120 }}>
                <InputLabel>Tipo</InputLabel>
                <Select
                  value={selectedType}
                  label="Tipo"
                  onChange={(e) => setSelectedType(e.target.value)}
                >
                  {contentTypes.map((type) => (
                    <MenuItem key={type.value} value={type.value}>
                      {type.label}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>

              <FormControl size="small" sx={{ minWidth: 140 }}>
                <InputLabel>Dificultad</InputLabel>
                <Select
                  value={selectedDifficulty}
                  label="Dificultad"
                  onChange={(e) => setSelectedDifficulty(e.target.value)}
                >
                  {difficulties.map((diff) => (
                    <MenuItem key={diff.value} value={diff.value}>
                      {diff.label}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>

              <FormControl size="small" sx={{ minWidth: 140 }}>
                <InputLabel>Estado</InputLabel>
                <Select
                  value={selectedStatus}
                  label="Estado"
                  onChange={(e) => setSelectedStatus(e.target.value)}
                >
                  {statuses.map((status) => (
                    <MenuItem key={status.value} value={status.value}>
                      {status.label}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>

              <Button
                variant="outlined"
                startIcon={<FilterList />}
                onClick={() => setShowFilters(!showFilters)}
              >
                Más filtros
              </Button>
            </Box>
          </Grid>
        </Grid>
      </Paper>

      {/* Botón de crear contenido */}
      <Box sx={{ display: 'flex', justifyContent: 'flex-end', mb: 3 }}>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={handleCreateContent}
          sx={{ px: 3 }}
        >
          Crear Contenido
        </Button>
      </Box>

      {/* Lista de contenido */}
      {loading ? (
        <Grid container spacing={3}>
          {[...Array(6)].map((_, index) => (
            <Grid size={{ xs: 12, sm: 6, md: 4 }} key={index}>
              <Card>
                <CardContent>
                  <Skeleton variant="text" width="80%" height={24} />
                  <Skeleton variant="text" width="60%" height={20} />
                  <Skeleton variant="text" width="40%" height={16} />
                  <Box sx={{ mt: 2 }}>
                    <Skeleton variant="rectangular" height={120} />
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      ) : (
        <Grid container spacing={3}>
          {filteredContent.map((item) => (
            <Grid size={{ xs: 12, sm: 6, md: 4 }} key={item.id}>
              <Card 
                sx={{ 
                  height: '100%',
                  cursor: 'pointer',
                  transition: 'all 0.2s ease-in-out',
                  '&:hover': {
                    transform: 'translateY(-2px)',
                    boxShadow: theme.shadows[4]
                  }
                }}
                onClick={() => handleContentClick(item)}
              >
                <CardContent>
                  {/* Header */}
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                    {getContentTypeIcon(item.content_type)}
                    <Typography variant="body2" color="text.secondary">
                      {item.content_type.toUpperCase()}
                    </Typography>
                    <Box sx={{ ml: 'auto', display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Chip 
                        label={item.status} 
                        size="small" 
                        color={getStatusColor(item.status) as any}
                      />
                      <IconButton
                        size="small"
                        onClick={(e) => handleMenuClick(e, item)}
                      >
                        <MoreVert />
                      </IconButton>
                    </Box>
                  </Box>

                  {/* Título */}
                  <Typography variant="h6" component="h3" sx={{ mb: 1, fontWeight: 600 }}>
                    {item.title}
                  </Typography>

                  {/* Descripción */}
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                    {item.description}
                  </Typography>

                  {/* Metadatos */}
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                    <Chip 
                      label={item.difficulty} 
                      size="small" 
                      color={getDifficultyColor(item.difficulty) as any}
                    />
                    <Typography variant="caption" color="text.secondary">
                      {item.duration_minutes} min
                    </Typography>
                  </Box>

                  {/* Autor y fecha */}
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                    <Typography variant="caption" color="text.secondary">
                      Por {item.author}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {new Date(item.created_at).toLocaleDateString()}
                    </Typography>
                  </Box>

                  {/* Estadísticas */}
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                        <ViewsIcon sx={{ fontSize: 14, color: 'text.secondary' }} />
                        <Typography variant="caption" color="text.secondary">
                          {item.view_count}
                        </Typography>
                      </Box>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                        <ThumbUp sx={{ fontSize: 14, color: 'text.secondary' }} />
                        <Typography variant="caption" color="text.secondary">
                          {item.like_count}
                        </Typography>
                      </Box>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                        <Bookmark sx={{ fontSize: 14, color: 'text.secondary' }} />
                        <Typography variant="caption" color="text.secondary">
                          {item.bookmark_count}
                        </Typography>
                      </Box>
                      {item.rating > 0 && (
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                          <Typography variant="caption" color="text.secondary">
                            ⭐ {item.rating.toFixed(1)}
                          </Typography>
                        </Box>
                      )}
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      {/* Estado vacío */}
      {!loading && filteredContent.length === 0 && (
        <Box sx={{ textAlign: 'center', py: 8 }}>
          <School sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
          <Typography variant="h6" color="text.secondary" gutterBottom>
            No se encontró contenido
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Intenta ajustar los filtros o crear nuevo contenido
          </Typography>
        </Box>
      )}

      {/* Dialog para ver contenido */}
      <Dialog 
        open={showContentDialog} 
        onClose={() => setShowContentDialog(false)}
        maxWidth="md"
        fullWidth
      >
        {selectedContent && (
          <>
            <DialogTitle>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                {getContentTypeIcon(selectedContent.content_type)}
                <Typography variant="h6">{selectedContent.title}</Typography>
              </Box>
            </DialogTitle>
            <DialogContent>
              <Typography variant="body1" paragraph>
                {selectedContent.description}
              </Typography>
              <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                <Chip label={selectedContent.difficulty} color={getDifficultyColor(selectedContent.difficulty) as any} />
                <Chip label={selectedContent.status} color={getStatusColor(selectedContent.status) as any} />
                <Chip label={`${selectedContent.duration_minutes} min`} />
              </Box>
              <Divider sx={{ my: 2 }} />
              <Typography variant="body2" color="text.secondary">
                <strong>Autor:</strong> {selectedContent.author}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                <strong>Creado:</strong> {new Date(selectedContent.created_at).toLocaleDateString()}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                <strong>Vistas:</strong> {selectedContent.view_count} | <strong>Likes:</strong> {selectedContent.like_count} | <strong>Rating:</strong> {selectedContent.rating}
              </Typography>
            </DialogContent>
            <DialogActions>
              <Button onClick={() => setShowContentDialog(false)}>Cerrar</Button>
              <Button variant="contained" startIcon={<Edit />}>
                Editar
              </Button>
            </DialogActions>
          </>
        )}
      </Dialog>

      {/* Menú de acciones */}
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleMenuClose}
      >
        <MenuItem onClick={() => selectedItem && handleEditContent(selectedItem)}>
          <ListItemIcon>
            <Edit fontSize="small" />
          </ListItemIcon>
          <ListItemText>Editar</ListItemText>
        </MenuItem>
        
        {selectedItem?.status === 'draft' && (
          <MenuItem onClick={() => selectedItem && handlePublishContent(selectedItem)}>
            <ListItemIcon>
              <Publish fontSize="small" />
            </ListItemIcon>
            <ListItemText>Publicar</ListItemText>
          </MenuItem>
        )}
        
        {selectedItem?.status === 'published' && (
          <MenuItem onClick={() => selectedItem && handleArchiveContent(selectedItem)}>
            <ListItemIcon>
              <Archive fontSize="small" />
            </ListItemIcon>
            <ListItemText>Archivar</ListItemText>
          </MenuItem>
        )}
        
        <MenuItem onClick={() => selectedItem && handleDeleteContent(selectedItem)} sx={{ color: 'error.main' }}>
          <ListItemIcon>
            <Delete fontSize="small" color="error" />
          </ListItemIcon>
          <ListItemText>Eliminar</ListItemText>
        </MenuItem>
      </Menu>

      {/* Formulario para crear contenido */}
      <ContentForm
        open={showCreateDialog}
        onClose={() => setShowCreateDialog(false)}
        onSubmit={handleCreateSubmit}
        loading={formLoading}
        mode="create"
      />

      {/* Formulario para editar contenido */}
      <ContentForm
        open={showEditDialog}
        onClose={() => setShowEditDialog(false)}
        onSubmit={handleEditSubmit}
        initialData={selectedContent ? (selectedContent as Partial<ContentFormData>) : undefined}
        loading={formLoading}
        mode="edit"
      />

      {/* Notificaciones */}
      <Snackbar
        open={!!error}
        autoHideDuration={6000}
        onClose={() => setError(null)}
      >
        <Alert onClose={() => setError(null)} severity="error">
          {error}
        </Alert>
      </Snackbar>

      <Snackbar
        open={!!success}
        autoHideDuration={4000}
        onClose={() => setSuccess(null)}
      >
        <Alert onClose={() => setSuccess(null)} severity="success">
          {success}
        </Alert>
      </Snackbar>

      {/* FAB para crear contenido */}
      <Fab
        color="primary"
        aria-label="crear contenido"
        sx={{ position: 'fixed', bottom: 16, right: 16 }}
        onClick={handleCreateContent}
      >
        <Add />
      </Fab>
    </Container>
  );
};

export default ContentManagementPage;

