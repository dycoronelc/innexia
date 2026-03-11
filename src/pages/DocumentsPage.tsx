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
  FormControlLabel,
  Checkbox,
  Input,
  LinearProgress
} from '@mui/material';
import {
  Add,
  Search,
  FilterList,
  Description,
  Upload,
  Download,
  Edit,
  Delete,
  Visibility,
  CheckCircle,
  Cancel,
  Schedule,
  Public,
  Lock,
  CloudUpload,
  FileCopy,
  MoreVert
} from '@mui/icons-material';
import { useTheme } from '@mui/material/styles';

interface DocumentItem {
  id: number;
  title: string;
  description: string;
  document_type: 'guide' | 'manual' | 'brochure' | 'policy' | 'procedure' | 'template' | 'form';
  category: 'hr' | 'operations' | 'finance' | 'marketing' | 'sales' | 'technical' | 'compliance' | 'training';
  file_name: string;
  file_size: number;
  file_type: string;
  version: string;
  approval_status: 'draft' | 'pending' | 'approved' | 'rejected' | 'archived';
  is_public: boolean;
  requires_approval: boolean;
  created_at: string;
  created_by: number;
  download_count: number;
  view_count: number;
}

const DocumentsPage: React.FC = () => {
  const theme = useTheme();
  const [activeTab, setActiveTab] = useState(0);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedType, setSelectedType] = useState('all');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [selectedStatus, setSelectedStatus] = useState('all');
  const [showFilters, setShowFilters] = useState(false);
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedDocument, setSelectedDocument] = useState<DocumentItem | null>(null);
  const [showDocumentDialog, setShowDocumentDialog] = useState(false);
  const [showUploadDialog, setShowUploadDialog] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploading, setUploading] = useState(false);

  // Mock data - En producción esto vendría de la API
  useEffect(() => {
    // Simular carga de datos
    setTimeout(() => {
      setDocuments([
        {
          id: 1,
          title: 'Manual de Procedimientos Empresariales',
          description: 'Guía completa de todos los procedimientos operativos de la empresa',
          document_type: 'manual',
          category: 'operations',
          file_name: 'manual_procedimientos_v2.1.pdf',
          file_size: 2048576, // 2MB
          file_type: 'pdf',
          version: '2.1',
          approval_status: 'approved',
          is_public: true,
          requires_approval: true,
          created_at: '2024-01-15',
          created_by: 1,
          download_count: 45,
          view_count: 123
        },
        {
          id: 2,
          title: 'Política de Recursos Humanos',
          description: 'Políticas y procedimientos para la gestión del personal',
          document_type: 'policy',
          category: 'hr',
          file_name: 'politica_rrhh_v1.0.docx',
          file_size: 1048576, // 1MB
          file_type: 'docx',
          version: '1.0',
          approval_status: 'pending',
          is_public: false,
          requires_approval: true,
          created_at: '2024-01-10',
          created_by: 2,
          download_count: 0,
          view_count: 8
        },
        {
          id: 3,
          title: 'Plantilla de Presupuesto Mensual',
          description: 'Plantilla Excel para el control presupuestario mensual',
          document_type: 'template',
          category: 'finance',
          file_name: 'plantilla_presupuesto_v1.2.xlsx',
          file_size: 512000, // 500KB
          file_type: 'xlsx',
          version: '1.2',
          approval_status: 'approved',
          is_public: true,
          requires_approval: false,
          created_at: '2024-01-08',
          created_by: 3,
          download_count: 67,
          view_count: 189
        }
      ]);
      setLoading(false);
    }, 1000);
  }, []);

  const tabs = [
    { label: 'Todos los Documentos', value: 0, icon: <Description /> },
    { label: 'Pendientes de Aprobación', value: 1, icon: <Schedule /> },
    { label: 'Aprobados', value: 2, icon: <CheckCircle /> },
    { label: 'Rechazados', value: 3, icon: <Cancel /> },
    { label: 'Archivados', value: 4, icon: <Delete /> }
  ];

  const documentTypes = [
    { value: 'all', label: 'Todos los tipos' },
    { value: 'guide', label: 'Guías' },
    { value: 'manual', label: 'Manuales' },
    { value: 'brochure', label: 'Folletos' },
    { value: 'policy', label: 'Políticas' },
    { value: 'procedure', label: 'Procedimientos' },
    { value: 'template', label: 'Plantillas' },
    { value: 'form', label: 'Formularios' }
  ];

  const categories = [
    { value: 'all', label: 'Todas las categorías' },
    { value: 'hr', label: 'Recursos Humanos' },
    { value: 'operations', label: 'Operaciones' },
    { value: 'finance', label: 'Finanzas' },
    { value: 'marketing', label: 'Marketing' },
    { value: 'sales', label: 'Ventas' },
    { value: 'technical', label: 'Técnico' },
    { value: 'compliance', label: 'Cumplimiento' },
    { value: 'training', label: 'Capacitación' }
  ];

  const statuses = [
    { value: 'all', label: 'Todos los estados' },
    { value: 'draft', label: 'Borrador' },
    { value: 'pending', label: 'Pendiente' },
    { value: 'approved', label: 'Aprobado' },
    { value: 'rejected', label: 'Rechazado' },
    { value: 'archived', label: 'Archivado' }
  ];

  const filteredDocuments = documents.filter(doc => {
    const matchesSearch = doc.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         doc.description.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesType = selectedType === 'all' || doc.document_type === selectedType;
    const matchesCategory = selectedCategory === 'all' || doc.category === selectedCategory;
    const matchesStatus = selectedStatus === 'all' || doc.approval_status === selectedStatus;

    return matchesSearch && matchesType && matchesCategory && matchesStatus;
  });

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
    // Filtrar por estado según la pestaña
    if (newValue === 1) setSelectedStatus('pending');
    else if (newValue === 2) setSelectedStatus('approved');
    else if (newValue === 3) setSelectedStatus('rejected');
    else if (newValue === 4) setSelectedStatus('archived');
    else setSelectedStatus('all');
  };

  const getDocumentTypeIcon = (type: string) => {
    switch (type) {
      case 'guide': return <Description />;
      case 'manual': return <Description />;
      case 'brochure': return <Description />;
      case 'policy': return <Description />;
      case 'procedure': return <Description />;
      case 'template': return <FileCopy />;
      case 'form': return <Description />;
      default: return <Description />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'draft': return 'default';
      case 'pending': return 'warning';
      case 'approved': return 'success';
      case 'rejected': return 'error';
      case 'archived': return 'default';
      default: return 'default';
    }
  };

  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'hr': return 'primary';
      case 'operations': return 'secondary';
      case 'finance': return 'success';
      case 'marketing': return 'info';
      case 'sales': return 'warning';
      case 'technical': return 'error';
      case 'compliance': return 'default';
      case 'training': return 'primary';
      default: return 'default';
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const handleDocumentClick = (document: DocumentItem) => {
    setSelectedDocument(document);
    setShowDocumentDialog(true);
  };

  const handleUploadDocument = () => {
    setShowUploadDialog(true);
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // Simular progreso de subida
    setUploading(true);
    setUploadProgress(0);
    
    const interval = setInterval(() => {
      setUploadProgress(prev => {
        if (prev >= 100) {
          clearInterval(interval);
          setUploading(false);
          setShowUploadDialog(false);
          return 100;
        }
        return prev + 10;
      });
    }, 200);

    // Aquí iría la lógica real de subida a la API
  };

  return (
    <Container maxWidth={false} sx={{ py: 3, px: { xs: 2, sm: 3, md: 4 } }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
          <Description sx={{ fontSize: 40, color: 'primary.main' }} />
          <Typography variant="h3" component="h1" sx={{ fontWeight: 'bold' }}>
            Documentos Oficiales
          </Typography>
        </Box>
        <Typography variant="h6" color="text.secondary" sx={{ mb: 3 }}>
          Gestiona todos los documentos oficiales de la empresa
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
              placeholder="Buscar documentos..."
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
                  {documentTypes.map((type) => (
                    <MenuItem key={type.value} value={type.value}>
                      {type.label}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>

              <FormControl size="small" sx={{ minWidth: 140 }}>
                <InputLabel>Categoría</InputLabel>
                <Select
                  value={selectedCategory}
                  label="Categoría"
                  onChange={(e) => setSelectedCategory(e.target.value)}
                >
                  {categories.map((cat) => (
                    <MenuItem key={cat.value} value={cat.value}>
                      {cat.label}
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

      {/* Botón de subir documento */}
      <Box sx={{ display: 'flex', justifyContent: 'flex-end', mb: 3 }}>
        <Button
          variant="contained"
          startIcon={<Upload />}
          onClick={handleUploadDocument}
          sx={{ px: 3 }}
        >
          Subir Documento
        </Button>
      </Box>

      {/* Lista de documentos */}
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
          {filteredDocuments.map((doc) => (
            <Grid size={{ xs: 12, sm: 6, md: 4 }} key={doc.id}>
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
                onClick={() => handleDocumentClick(doc)}
              >
                <CardContent>
                  {/* Header */}
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                    {getDocumentTypeIcon(doc.document_type)}
                    <Typography variant="body2" color="text.secondary">
                      {doc.document_type.toUpperCase()}
                    </Typography>
                    <Box sx={{ ml: 'auto' }}>
                      <Chip 
                        label={doc.approval_status} 
                        size="small" 
                        color={getStatusColor(doc.approval_status) as any}
                      />
                    </Box>
                  </Box>

                  {/* Título */}
                  <Typography variant="h6" component="h3" sx={{ mb: 1, fontWeight: 600 }}>
                    {doc.title}
                  </Typography>

                  {/* Descripción */}
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                    {doc.description}
                  </Typography>

                  {/* Metadatos */}
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                    <Chip 
                      label={doc.category} 
                      size="small" 
                      color={getCategoryColor(doc.category) as any}
                    />
                    <Typography variant="caption" color="text.secondary">
                      v{doc.version}
                    </Typography>
                  </Box>

                  {/* Información del archivo */}
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                    <Typography variant="caption" color="text.secondary">
                      {doc.file_name}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {formatFileSize(doc.file_size)}
                    </Typography>
                  </Box>

                  {/* Visibilidad y estadísticas */}
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      {doc.is_public ? <Public sx={{ fontSize: 16 }} /> : <Lock sx={{ fontSize: 16 }} />}
                      <Typography variant="caption" color="text.secondary">
                        {doc.is_public ? 'Público' : 'Privado'}
                      </Typography>
                    </Box>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Typography variant="caption" color="text.secondary">
                        👁️ {doc.view_count}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        📥 {doc.download_count}
                      </Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      {/* Estado vacío */}
      {!loading && filteredDocuments.length === 0 && (
        <Box sx={{ textAlign: 'center', py: 8 }}>
          <Description sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
          <Typography variant="h6" color="text.secondary" gutterBottom>
            No se encontraron documentos
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Intenta ajustar los filtros o subir un nuevo documento
          </Typography>
        </Box>
      )}

                   {/* Dialog para ver documento */}
             <Dialog 
               open={showDocumentDialog} 
               onClose={() => setShowDocumentDialog(false)}
               maxWidth="md"
               fullWidth
               PaperProps={{
                 sx: {
                   borderRadius: 3,
                   maxHeight: '90vh'
                 }
               }}
             >
               {selectedDocument && (
                 <>
                   <DialogTitle sx={{ 
                     display: 'flex', 
                     alignItems: 'center', 
                     gap: 2,
                     borderBottom: '1px solid',
                     borderColor: 'divider',
                     pb: 2
                   }}>
                     {getDocumentTypeIcon(selectedDocument.document_type)}
                     <Typography variant="h6" component="h2">
                       {selectedDocument.title}
                     </Typography>
                   </DialogTitle>
                   
                   <DialogContent sx={{ pt: 3 }}>
                     <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
                       {/* Descripción */}
                       <Box>
                         <Typography variant="subtitle2" color="text.secondary" sx={{ mb: 1 }}>
                           Descripción
                         </Typography>
                         <Typography variant="body1" sx={{ 
                           p: 2, 
                           backgroundColor: 'grey.50', 
                           borderRadius: 2,
                           border: '1px solid',
                           borderColor: 'grey.200'
                         }}>
                           {selectedDocument.description}
                         </Typography>
                       </Box>

                       {/* Chips de información */}
                       <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                         <Chip 
                           label={selectedDocument.document_type} 
                           color="primary" 
                           sx={{ borderRadius: 2 }}
                         />
                         <Chip 
                           label={selectedDocument.category} 
                           color={getCategoryColor(selectedDocument.category) as any}
                           sx={{ borderRadius: 2 }}
                         />
                         <Chip 
                           label={selectedDocument.approval_status} 
                           color={getStatusColor(selectedDocument.approval_status) as any}
                           sx={{ borderRadius: 2 }}
                         />
                         <Chip 
                           label={`v${selectedDocument.version}`}
                           variant="outlined"
                           sx={{ borderRadius: 2 }}
                         />
                       </Box>

                       {/* Información del archivo */}
                       <Box sx={{ 
                         p: 3, 
                         backgroundColor: 'grey.50', 
                         borderRadius: 2,
                         border: '1px solid',
                         borderColor: 'grey.200'
                       }}>
                         <Typography variant="subtitle2" color="text.secondary" sx={{ mb: 2 }}>
                           Información del archivo
                         </Typography>
                         
                         <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                           <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                             <Typography variant="body2" color="text.secondary">
                               <strong>Archivo:</strong>
                             </Typography>
                             <Typography variant="body2" fontWeight={600}>
                               {selectedDocument.file_name}
                             </Typography>
                           </Box>
                           
                           <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                             <Typography variant="body2" color="text.secondary">
                               <strong>Tamaño:</strong>
                             </Typography>
                             <Typography variant="body2" fontWeight={600}>
                               {formatFileSize(selectedDocument.file_size)}
                             </Typography>
                           </Box>
                           
                           <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                             <Typography variant="body2" color="text.secondary">
                               <strong>Visibilidad:</strong>
                             </Typography>
                             <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                               {selectedDocument.is_public ? <Public sx={{ fontSize: 16 }} /> : <Lock sx={{ fontSize: 16 }} />}
                               <Typography variant="body2" fontWeight={600}>
                                 {selectedDocument.is_public ? 'Público' : 'Privado'}
                               </Typography>
                             </Box>
                           </Box>
                         </Box>
                       </Box>

                       {/* Estadísticas */}
                       <Box sx={{ 
                         p: 3, 
                         backgroundColor: 'primary.50', 
                         borderRadius: 2,
                         border: '1px solid',
                         borderColor: 'primary.200'
                       }}>
                         <Typography variant="subtitle2" color="primary.main" sx={{ mb: 2, fontWeight: 600 }}>
                           Estadísticas
                         </Typography>
                         
                         <Box sx={{ display: 'flex', gap: 4 }}>
                           <Box sx={{ textAlign: 'center' }}>
                             <Typography variant="h6" color="primary.main" fontWeight={600}>
                               {selectedDocument.view_count}
                             </Typography>
                             <Typography variant="caption" color="primary.main">
                               Vistas
                             </Typography>
                           </Box>
                           
                           <Box sx={{ textAlign: 'center' }}>
                             <Typography variant="h6" color="primary.main" fontWeight={600}>
                               {selectedDocument.download_count}
                             </Typography>
                             <Typography variant="caption" color="primary.main">
                               Descargas
                             </Typography>
                           </Box>
                         </Box>
                       </Box>
                     </Box>
                   </DialogContent>

                   <DialogActions sx={{ 
                     px: 3, 
                     py: 2, 
                     borderTop: '1px solid',
                     borderColor: 'divider',
                     gap: 2
                   }}>
                     <Button 
                       onClick={() => setShowDocumentDialog(false)}
                       variant="outlined"
                       sx={{ borderRadius: 2, px: 3 }}
                     >
                       Cerrar
                     </Button>
                     <Button 
                       variant="contained" 
                       startIcon={<Download />}
                       sx={{ borderRadius: 2, px: 4 }}
                     >
                       Descargar
                     </Button>
                     <Button 
                       variant="outlined" 
                       startIcon={<Edit />}
                       sx={{ borderRadius: 2, px: 3 }}
                     >
                       Editar
                     </Button>
                   </DialogActions>
                 </>
               )}
             </Dialog>

                   {/* Dialog para subir documento */}
             <Dialog 
               open={showUploadDialog} 
               onClose={() => setShowUploadDialog(false)}
               maxWidth="md"
               fullWidth
               PaperProps={{
                 sx: {
                   borderRadius: 3,
                   maxHeight: '90vh'
                 }
               }}
             >
               <DialogTitle sx={{ 
                 display: 'flex', 
                 alignItems: 'center', 
                 gap: 2,
                 borderBottom: '1px solid',
                 borderColor: 'divider',
                 pb: 2
               }}>
                 <CloudUpload color="primary" />
                 <Typography variant="h6" component="h2">
                   Subir Nuevo Documento
                 </Typography>
               </DialogTitle>
               
               <DialogContent sx={{ pt: 3 }}>
                 <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
                   {/* Título del documento */}
                   <TextField
                     fullWidth
                     label="Título del documento"
                     placeholder="Ej: Manual de Procedimientos Empresariales"
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
                     placeholder="Descripción detallada del documento..."
                     multiline
                     rows={4}
                     size="medium"
                     sx={{
                       '& .MuiOutlinedInput-root': {
                         borderRadius: 2,
                       }
                     }}
                   />

                   {/* Tipo y Categoría en fila */}
                   <Box sx={{ 
                     display: 'flex', 
                     gap: 3, 
                     flexDirection: { xs: 'column', sm: 'row' } 
                   }}>
                     <FormControl fullWidth>
                       <InputLabel>Tipo de documento</InputLabel>
                       <Select 
                         label="Tipo de documento" 
                         required
                         size="medium"
                         sx={{
                           '& .MuiOutlinedInput-root': {
                             borderRadius: 2,
                           }
                         }}
                       >
                         {documentTypes.slice(1).map((type) => (
                           <MenuItem key={type.value} value={type.value}>
                             {type.label}
                           </MenuItem>
                         ))}
                       </Select>
                     </FormControl>

                     <FormControl fullWidth>
                       <InputLabel>Categoría</InputLabel>
                       <Select 
                         label="Categoría" 
                         required
                         size="medium"
                         sx={{
                           '& .MuiOutlinedInput-root': {
                             borderRadius: 2,
                           }
                         }}
                       >
                         {categories.slice(1).map((cat) => (
                           <MenuItem key={cat.value} value={cat.value}>
                             {cat.label}
                           </MenuItem>
                         ))}
                       </Select>
                     </FormControl>
                   </Box>

                   {/* Versión y Tags en fila */}
                   <Box sx={{ 
                     display: 'flex', 
                     gap: 3, 
                     flexDirection: { xs: 'column', sm: 'row' } 
                   }}>
                     <TextField
                       fullWidth
                       label="Versión"
                       placeholder="1.0"
                       defaultValue="1.0"
                       size="medium"
                       sx={{
                         '& .MuiOutlinedInput-root': {
                           borderRadius: 2,
                         }
                       }}
                     />

                     <TextField
                       fullWidth
                       label="Tags (separados por comas)"
                       placeholder="procedimientos, manual, empresa"
                       size="medium"
                       sx={{
                         '& .MuiOutlinedInput-root': {
                           borderRadius: 2,
                         }
                       }}
                     />
                   </Box>

                   {/* Fecha de expiración */}
                   <TextField
                     fullWidth
                     label="Fecha de expiración (opcional)"
                     type="date"
                     InputLabelProps={{ shrink: true }}
                     size="medium"
                     sx={{
                       '& .MuiOutlinedInput-root': {
                         borderRadius: 2,
                       }
                     }}
                   />

                   {/* Área de subida de archivo */}
                   <Box sx={{ 
                     border: '2px dashed', 
                     borderColor: 'grey.300', 
                     borderRadius: 3, 
                     p: 4, 
                     textAlign: 'center',
                     backgroundColor: 'grey.50',
                     transition: 'all 0.2s ease-in-out',
                     '&:hover': {
                       borderColor: 'primary.main',
                       backgroundColor: 'primary.50'
                     }
                   }}>
                     <CloudUpload sx={{ fontSize: 64, color: 'grey.400', mb: 3 }} />
                     <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                       Arrastra y suelta el archivo aquí
                     </Typography>
                     <Typography variant="body2" color="text.secondary" gutterBottom sx={{ mb: 3 }}>
                       O haz clic para seleccionar un archivo
                     </Typography>
                     <Button
                       variant="outlined"
                       component="label"
                       startIcon={<Upload />}
                       size="large"
                       sx={{ 
                         borderRadius: 2,
                         px: 4,
                         py: 1.5
                       }}
                     >
                       Seleccionar Archivo
                       <input
                         type="file"
                         hidden
                         accept=".pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx,.txt,.rtf"
                         onChange={handleFileUpload}
                       />
                     </Button>
                     <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 2 }}>
                       Tipos permitidos: PDF, DOC, DOCX, XLS, XLSX, PPT, PPTX, TXT, RTF
                     </Typography>
                     <Typography variant="caption" color="text.secondary">
                       Tamaño máximo: 50MB
                     </Typography>
                   </Box>

                   {/* Barra de progreso */}
                   {uploading && (
                     <Box sx={{ width: '100%' }}>
                       <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                         <Typography variant="body2" color="text.secondary">
                           Subiendo archivo...
                         </Typography>
                         <Typography variant="body2" color="primary.main" fontWeight={600}>
                           {uploadProgress}%
                         </Typography>
                       </Box>
                       <LinearProgress 
                         variant="determinate" 
                         value={uploadProgress} 
                         sx={{ 
                           height: 8, 
                           borderRadius: 4,
                           backgroundColor: 'grey.200',
                           '& .MuiLinearProgress-bar': {
                             borderRadius: 4
                           }
                         }}
                       />
                     </Box>
                   )}

                   {/* Opciones adicionales */}
                   <Box sx={{ 
                     display: 'flex', 
                     flexDirection: 'column', 
                     gap: 2,
                     p: 3,
                     backgroundColor: 'grey.50',
                     borderRadius: 2,
                     border: '1px solid',
                     borderColor: 'grey.200'
                   }}>
                     <Typography variant="subtitle2" color="text.secondary" sx={{ mb: 1 }}>
                       Configuración del documento
                     </Typography>
                     
                     <FormControlLabel
                       control={<Checkbox defaultChecked />}
                       label="Requiere aprobación antes de ser publicado"
                     />
                     
                     <FormControlLabel
                       control={<Checkbox />}
                       label="Documento público (visible para todos los usuarios)"
                     />
                   </Box>
                 </Box>
               </DialogContent>

               <DialogActions sx={{ 
                 px: 3, 
                 py: 2, 
                 borderTop: '1px solid',
                 borderColor: 'divider',
                 gap: 2
               }}>
                 <Button 
                   onClick={() => setShowUploadDialog(false)}
                   variant="outlined"
                   sx={{ borderRadius: 2, px: 3 }}
                 >
                   Cancelar
                 </Button>
                 <Button 
                   variant="contained" 
                   startIcon={<Upload />} 
                   disabled={uploading}
                   sx={{ 
                     borderRadius: 2, 
                     px: 4,
                     py: 1.5
                   }}
                 >
                   {uploading ? 'Subiendo...' : 'Subir Documento'}
                 </Button>
               </DialogActions>
             </Dialog>

      {/* FAB para subir documento */}
      <Fab
        color="primary"
        aria-label="subir documento"
        sx={{ position: 'fixed', bottom: 16, right: 16 }}
        onClick={handleUploadDocument}
      >
        <Upload />
      </Fab>
    </Container>
  );
};

export default DocumentsPage;
