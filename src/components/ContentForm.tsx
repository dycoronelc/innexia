import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Grid,
  Box,
  Typography,
  Chip,
  IconButton,
  Alert,
  LinearProgress,
  FormControlLabel,
  Switch,
  Autocomplete,
  Card,
  CardContent,
  Divider,
  Snackbar
} from '@mui/material';
import {
  Add as AddIcon,
  Delete as DeleteIcon,
  CloudUpload as UploadIcon,
  Image as ImageIcon,
  Save as SaveIcon,
  Cancel as CancelIcon,
  Preview as PreviewIcon,
  CheckCircle as CheckCircleIcon
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import { educationalContentService } from '../services/api';

export interface ContentFormData {
  title: string;
  description: string;
  content_type: 'article' | 'video' | 'podcast' | 'course' | 'news';
  content_source: 'internal' | 'rss_feed' | 'youtube' | 'vimeo' | 'spotify' | 'custom_api';
  source_url: string;
  content_data: any;
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  duration_minutes: number;
  duration_formatted?: string; // Campo interno para el formulario, no se envía al backend
  author: string;
  instructor: string;
  thumbnail_url: string;
  tags: string[];
  categories: string[];
  status?: 'draft' | 'published' | 'archived' | 'moderation';
}

interface ContentFormProps {
  open: boolean;
  onClose: () => void;
  onSubmit: (data: ContentFormData) => Promise<void>;
  initialData?: Partial<ContentFormData>;
  loading?: boolean;
  mode: 'create' | 'edit';
}

const ContentForm: React.FC<ContentFormProps> = ({
  open,
  onClose,
  onSubmit,
  initialData,
  loading = false,
  mode
}) => {
  const { token } = useAuth();
  const [formData, setFormData] = useState<ContentFormData>({
    title: '',
    description: '',
    content_type: 'article',
    content_source: 'internal',
    source_url: '',
    content_data: {},
    difficulty: 'beginner',
    duration_minutes: 0,
    duration_formatted: '00:00',
    author: '',
    instructor: '',
    thumbnail_url: '',
    tags: [],
    categories: []
  });

  const [publishImmediately, setPublishImmediately] = useState(true);

  const [tagInput, setTagInput] = useState('');
  const [categoryInput, setCategoryInput] = useState('');
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [uploadProgress, setUploadProgress] = useState(0);
  const [isUploading, setIsUploading] = useState(false);
  
  // Estados para subida de thumbnail
  const [isUploadingThumbnail, setIsUploadingThumbnail] = useState(false);
  const [thumbnailUploadProgress, setThumbnailUploadProgress] = useState(0);

  // Funciones para manejar duración en formato mm:ss
  const convertMinutesToFormatted = (minutes: number): string => {
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    if (hours > 0) {
      return `${hours}:${mins.toString().padStart(2, '0')}:00`;
    }
    return `${mins}:00`;
  };

  const convertFormattedToMinutes = (formatted: string): number => {
    const parts = formatted.split(':');
    if (parts.length === 3) {
      // Formato hh:mm:ss
      const hours = parseInt(parts[0]) || 0;
      const minutes = parseInt(parts[1]) || 0;
      return hours * 60 + minutes;
    } else if (parts.length === 2) {
      // Formato mm:ss - redondear hacia arriba para evitar decimales
      const minutes = parseInt(parts[0]) || 0;
      const seconds = parseInt(parts[1]) || 0;
      const totalMinutes = minutes + (seconds / 60);
      return Math.ceil(totalMinutes); // Redondear hacia arriba
    }
    return 0;
  };
  const [thumbnailPreview, setThumbnailPreview] = useState<string | null>(null);

  // Cargar datos iniciales cuando se abre el modal
  useEffect(() => {
    if (open && initialData) {
      setFormData(prev => ({
        ...prev,
        title: initialData.title || '',
        description: initialData.description || '',
        content_type: initialData.content_type || 'article',
        content_source: initialData.content_source || 'internal',
        source_url: initialData.source_url || '',
        content_data: initialData.content_data || {},
        difficulty: initialData.difficulty || 'beginner',
        duration_minutes: initialData.duration_minutes || 0,
        duration_formatted: initialData.duration_formatted || convertMinutesToFormatted(initialData.duration_minutes || 0),
        author: initialData.author || '',
        instructor: initialData.instructor || '',
        thumbnail_url: initialData.thumbnail_url || '',
        tags: initialData.tags || [],
        categories: initialData.categories || []
      }));
    } else if (open && mode === 'create') {
      // Resetear formulario para crear nuevo contenido
      setFormData({
        title: '',
        description: '',
        content_type: 'article',
        content_source: 'internal',
        source_url: '',
        content_data: {},
        difficulty: 'beginner',
        duration_minutes: 0,
        author: '',
        instructor: '',
        thumbnail_url: '',
        tags: [],
        categories: []
      });
    }
    setErrors({});
  }, [open, initialData, mode]);

  const contentTypes = [
    { value: 'article', label: 'Artículo' },
    { value: 'course', label: 'Curso' },
    { value: 'news', label: 'Noticia' },
    { value: 'podcast', label: 'Podcast' },
    { value: 'video', label: 'Video' }
  ];

  const contentSources = [
    { value: 'internal', label: 'Contenido Interno' },
    { value: 'youtube', label: 'YouTube' },
    { value: 'vimeo', label: 'Vimeo' },
    { value: 'spotify', label: 'Spotify' },
    { value: 'rss_feed', label: 'RSS Feed' },
    { value: 'custom_api', label: 'API Personalizada' }
  ];

  const difficulties = [
    { value: 'beginner', label: 'Principiante' },
    { value: 'intermediate', label: 'Intermedio' },
    { value: 'advanced', label: 'Avanzado' }
  ];

  const predefinedCategories = [
    'Estrategia de Negocio',
    'Marketing Digital',
    'Finanzas',
    'Liderazgo',
    'Innovación',
    'Tecnología',
    'Emprendimiento',
    'Crecimiento Personal',
    'Productividad',
    'Ventas'
  ];

  const predefinedTags = [
    'BMC', 'Canvas', 'Propuesta de Valor', 'Validación', 'MVP',
    'Marketing', 'SEO', 'Redes Sociales', 'Email Marketing',
    'Finanzas', 'Flujo de Caja', 'Presupuesto', 'Inversión',
    'Liderazgo', 'Equipos', 'Gestión', 'Comunicación',
    'Innovación', 'Disrupción', 'Tecnología', 'Digital'
  ];

  const handleInputChange = (field: keyof ContentFormData, value: any) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
    
    // Limpiar error del campo cuando se modifica
    if (errors[field]) {
      setErrors(prev => ({
        ...prev,
        [field]: ''
      }));
    }
  };

  const handleDurationChange = (value: string) => {
    setFormData(prev => ({ 
      ...prev, 
      duration_formatted: value,
      duration_minutes: convertFormattedToMinutes(value)
    }));
    if (errors.duration_minutes) {
      setErrors(prev => ({ ...prev, duration_minutes: '' }));
    }
  };

  const handleAddTag = () => {
    if (tagInput.trim() && !formData.tags.includes(tagInput.trim())) {
      setFormData(prev => ({
        ...prev,
        tags: [...prev.tags, tagInput.trim()]
      }));
      setTagInput('');
    }
  };

  const handleRemoveTag = (tagToRemove: string) => {
    setFormData(prev => ({
      ...prev,
      tags: prev.tags.filter(tag => tag !== tagToRemove)
    }));
  };

  const handleAddCategory = () => {
    if (categoryInput.trim() && !formData.categories.includes(categoryInput.trim())) {
      setFormData(prev => ({
        ...prev,
        categories: [...prev.categories, categoryInput.trim()]
      }));
      setCategoryInput('');
    }
  };

  const handleRemoveCategory = (categoryToRemove: string) => {
    setFormData(prev => ({
      ...prev,
      categories: prev.categories.filter(category => category !== categoryToRemove)
    }));
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file || !token) return;

    setIsUploading(true);
    setUploadProgress(0);

    try {
      // Determinar el tipo de contenido basado en el tipo de archivo
      let contentType = 'document';
      if (file.type.startsWith('video/')) {
        contentType = 'video';
      } else if (file.type.startsWith('audio/')) {
        contentType = 'audio';
      } else if (file.type.startsWith('image/')) {
        contentType = 'image';
      }

      // Simular progreso de subida
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return 90;
          }
          return prev + 10;
        });
      }, 200);

      // Subir archivo real
      const uploadResponse = await educationalContentService.uploadContentFile(file, contentType, token);
      
      setUploadProgress(100);
      setIsUploading(false);
      clearInterval(progressInterval);
      
      if (uploadResponse.status === 'success' && uploadResponse.data) {
        // Actualizar el formulario con la URL del archivo subido
        handleInputChange('thumbnail_url', uploadResponse.data.url);
        
        // Si es un video o audio, también actualizar source_url
        if (contentType === 'video' || contentType === 'audio') {
          handleInputChange('source_url', uploadResponse.data.url);
        }
        
        console.log('Archivo subido exitosamente:', uploadResponse.data);
      } else {
        throw new Error(uploadResponse.error || 'Error al subir archivo');
      }

    } catch (error) {
      setIsUploading(false);
      setUploadProgress(0);
      console.error('Error al subir archivo:', error);
      // Aquí podrías mostrar un mensaje de error al usuario
    }
  };

  const handleThumbnailUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file || !token) return;

    // Validar que sea una imagen
    if (!file.type.startsWith('image/')) {
      console.error('Por favor selecciona un archivo de imagen válido.');
      return;
    }

    // Validar tamaño (máximo 10MB)
    if (file.size > 10 * 1024 * 1024) {
      console.error('La imagen es demasiado grande. Máximo 10MB.');
      return;
    }

    setIsUploadingThumbnail(true);
    setThumbnailUploadProgress(0);

    try {
      // Crear preview de la imagen
      const reader = new FileReader();
      reader.onload = (e) => {
        setThumbnailPreview(e.target?.result as string);
      };
      reader.readAsDataURL(file);

      // Simular progreso de subida
      const progressInterval = setInterval(() => {
        setThumbnailUploadProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return 90;
          }
          return prev + 10;
        });
      }, 200);

      const result = await educationalContentService.uploadThumbnail(file, token);
      
      setThumbnailUploadProgress(100);
      setIsUploadingThumbnail(false);
      clearInterval(progressInterval);
      
      if (result.status === 'success' && result.data) {
        // Actualizar el campo thumbnail_url con la URL de la imagen procesada
        handleInputChange('thumbnail_url', result.data.url);
        console.log('Thumbnail subido y procesado exitosamente:', result.data);
      } else {
        throw new Error(result.error || 'Error al subir thumbnail');
      }
      
    } catch (error) {
      setIsUploadingThumbnail(false);
      setThumbnailUploadProgress(0);
      setThumbnailPreview(null);
      console.error('Error al subir thumbnail:', error);
    }
  };

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.title.trim()) {
      newErrors.title = 'El título es requerido';
    }

    if (!formData.description.trim()) {
      newErrors.description = 'La descripción es requerida';
    }

    if (formData.content_source !== 'internal' && !formData.source_url.trim()) {
      newErrors.source_url = 'La URL es requerida para contenido externo';
    }

    if (formData.duration_minutes <= 0 || !formData.duration_formatted?.match(/^(\d{1,2}:\d{2}(:\d{2})?)$/)) {
      newErrors.duration_minutes = 'Ingresa una duración válida en formato mm:ss o hh:mm:ss';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async () => {
    if (!validateForm()) {
      return;
    }

    try {
      // Preparar datos para envío, excluyendo campos que el backend no espera
      const { duration_formatted, ...formDataForBackend } = formData;
      
      // Asegurar que los arrays tengan valores por defecto y duration_minutes sea entero
      const cleanedData = {
        ...formDataForBackend,
        duration_minutes: Math.round(formDataForBackend.duration_minutes) || 0, // Asegurar que sea entero
        tags: formDataForBackend.tags || [],
        categories: formDataForBackend.categories || [],
        content_data: formDataForBackend.content_data || {},
        author: formDataForBackend.author || '',
        instructor: formDataForBackend.instructor || '',
        thumbnail_url: formDataForBackend.thumbnail_url || '',
        source_url: formDataForBackend.source_url || ''
      };
      
      // Incluir el estado de publicación en los datos
      const dataWithStatus: ContentFormData = {
        ...cleanedData,
        status: publishImmediately ? 'published' : 'draft',
      };
      
      await onSubmit(dataWithStatus);
      onClose();
    } catch (error) {
      console.error('Error al enviar formulario:', error);
    }
  };

  const getSourceInputLabel = () => {
    switch (formData.content_source) {
      case 'youtube':
        return 'URL de YouTube';
      case 'vimeo':
        return 'URL de Vimeo';
      case 'spotify':
        return 'URL de Spotify';
      case 'rss_feed':
        return 'URL del RSS Feed';
      case 'custom_api':
        return 'URL de la API';
      default:
        return 'URL del contenido';
    }
  };

  return (
    <Dialog 
      open={open} 
      onClose={onClose}
      maxWidth="md"
      fullWidth
    >
      <DialogTitle>
        {mode === 'create' ? 'Nuevo Contenido' : 'Editar Contenido'}
      </DialogTitle>

      <DialogContent>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3, mt: 1 }}>

          {/* Título */}
          <TextField
            fullWidth
            label="Título"
            value={formData.title}
            onChange={(e) => handleInputChange('title', e.target.value)}
            error={!!errors.title}
            helperText={errors.title}
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
            value={formData.description}
            onChange={(e) => handleInputChange('description', e.target.value)}
            error={!!errors.description}
            helperText={errors.description}
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

          {/* Tipo de Contenido */}
          <FormControl fullWidth required>
            <InputLabel>Tipo de Contenido</InputLabel>
            <Select
              value={formData.content_type}
              label="Tipo de Contenido"
              onChange={(e) => handleInputChange('content_type', e.target.value)}
              size="medium"
              sx={{
                '& .MuiOutlinedInput-root': {
                  borderRadius: 2,
                }
              }}
            >
              {contentTypes.map((type) => (
                <MenuItem key={type.value} value={type.value}>
                  {type.label}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          {/* Fuente del Contenido */}
          <FormControl fullWidth required>
            <InputLabel>Fuente del Contenido</InputLabel>
            <Select
              value={formData.content_source}
              label="Fuente del Contenido"
              onChange={(e) => handleInputChange('content_source', e.target.value)}
              size="medium"
              sx={{
                '& .MuiOutlinedInput-root': {
                  borderRadius: 2,
                }
              }}
            >
              {contentSources.map((source) => (
                <MenuItem key={source.value} value={source.value}>
                  {source.label}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          {/* Dificultad */}
          <FormControl fullWidth required>
            <InputLabel>Dificultad</InputLabel>
            <Select
              value={formData.difficulty}
              label="Dificultad"
              onChange={(e) => handleInputChange('difficulty', e.target.value)}
              size="medium"
              sx={{
                '& .MuiOutlinedInput-root': {
                  borderRadius: 2,
                }
              }}
            >
              {difficulties.map((diff) => (
                <MenuItem key={diff.value} value={diff.value}>
                  {diff.label}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          {/* Estado de Publicación */}
          <FormControl fullWidth>
            <InputLabel>Estado de Publicación</InputLabel>
            <Select
              value={publishImmediately ? 'published' : 'draft'}
              label="Estado de Publicación"
              onChange={(e) => setPublishImmediately(e.target.value === 'published')}
              size="medium"
              sx={{
                '& .MuiOutlinedInput-root': {
                  borderRadius: 2,
                }
              }}
            >
              <MenuItem value="published">
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <CheckCircleIcon sx={{ color: 'success.main', fontSize: 16 }} />
                  <Box>
                    <Typography variant="body2" sx={{ fontWeight: 500 }}>
                      Publicar inmediatamente
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      El contenido será visible en la sección de aprendizaje
                    </Typography>
                  </Box>
                </Box>
              </MenuItem>
              <MenuItem value="draft">
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <SaveIcon sx={{ color: 'warning.main', fontSize: 16 }} />
                  <Box>
                    <Typography variant="body2" sx={{ fontWeight: 500 }}>
                      Guardar como borrador
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      Solo visible para administradores y editores
                    </Typography>
                  </Box>
                </Box>
              </MenuItem>
            </Select>
          </FormControl>

          {/* URL del Contenido */}
          <TextField
            fullWidth
            label={getSourceInputLabel()}
            value={formData.source_url}
            onChange={(e) => handleInputChange('source_url', e.target.value)}
            error={!!errors.source_url}
            helperText={errors.source_url}
            disabled={formData.content_source === 'internal'}
            size="medium"
            sx={{
              '& .MuiOutlinedInput-root': {
                borderRadius: 2,
              }
            }}
            InputProps={{
              startAdornment: <ImageIcon sx={{ mr: 1, color: 'text.secondary' }} />
            }}
          />

          {/* Autor */}
          <TextField
            fullWidth
            label="Autor"
            value={formData.author}
            onChange={(e) => handleInputChange('author', e.target.value)}
            size="medium"
            sx={{
              '& .MuiOutlinedInput-root': {
                borderRadius: 2,
              }
            }}
          />

          {/* Instructor */}
          <TextField
            fullWidth
            label="Instructor"
            value={formData.instructor}
            onChange={(e) => handleInputChange('instructor', e.target.value)}
            size="medium"
            sx={{
              '& .MuiOutlinedInput-root': {
                borderRadius: 2,
              }
            }}
          />

          {/* Duración */}
          <TextField
            fullWidth
            label="Duración (mm:ss o hh:mm:ss)"
            value={formData.duration_formatted}
            onChange={(e) => handleDurationChange(e.target.value)}
            error={!!errors.duration_minutes}
            helperText={errors.duration_minutes || "Formato: mm:ss (ej: 5:30) o hh:mm:ss (ej: 1:30:45)"}
            placeholder="5:30"
            required
            size="medium"
            sx={{
              '& .MuiOutlinedInput-root': {
                borderRadius: 2,
              }
            }}
          />

          {/* Subida de Imagen Miniatura */}
          <Box sx={{ 
            border: '2px dashed', 
            borderColor: 'grey.300', 
            borderRadius: 2, 
            p: 3, 
            textAlign: 'center',
            backgroundColor: 'grey.50'
          }}>
            <input
              accept="image/*"
              style={{ display: 'none' }}
              id="thumbnail-upload"
              type="file"
              onChange={handleThumbnailUpload}
            />
            <label htmlFor="thumbnail-upload">
              <Button
                variant="outlined"
                component="span"
                startIcon={<ImageIcon />}
                disabled={isUploadingThumbnail}
                size="large"
                sx={{ mb: 2 }}
              >
                {isUploadingThumbnail ? 'Procesando...' : 'Subir Imagen Miniatura'}
              </Button>
            </label>
            {isUploadingThumbnail && (
              <Box sx={{ mb: 2 }}>
                <LinearProgress variant="determinate" value={thumbnailUploadProgress} />
                <Typography variant="caption" color="text.secondary">
                  {thumbnailUploadProgress}% completado
                </Typography>
              </Box>
            )}
            {thumbnailPreview && (
              <Box sx={{ mt: 2 }}>
                <img 
                  src={thumbnailPreview} 
                  alt="Preview" 
                  style={{ 
                    maxWidth: '200px', 
                    maxHeight: '120px', 
                    borderRadius: '8px',
                    border: '1px solid #ddd'
                  }} 
                />
              </Box>
            )}
            <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
              Tamaño recomendado: 400x225px (16:9). La imagen se redimensionará automáticamente.
              <br />
              Formatos: JPG, PNG, GIF, WEBP (máximo 10MB)
            </Typography>
          </Box>

          {/* Subida de Archivos */}
          <Box sx={{ 
            border: '2px dashed', 
            borderColor: 'grey.300', 
            borderRadius: 2, 
            p: 3, 
            textAlign: 'center',
            backgroundColor: 'grey.50'
          }}>
            <input
              accept="image/*,video/*,audio/*,.pdf,.doc,.docx"
              style={{ display: 'none' }}
              id="file-upload"
              type="file"
              onChange={handleFileUpload}
            />
            <label htmlFor="file-upload">
              <Button
                variant="outlined"
                component="span"
                startIcon={<UploadIcon />}
                disabled={isUploading}
                size="large"
                sx={{ mb: 2 }}
              >
                {isUploading ? 'Subiendo...' : 'Subir Archivo'}
              </Button>
            </label>
            {isUploading && (
              <Box sx={{ mb: 2 }}>
                <LinearProgress variant="determinate" value={uploadProgress} />
                <Typography variant="caption" color="text.secondary">
                  {uploadProgress}% completado
                </Typography>
              </Box>
            )}
            <Typography variant="body2" color="text.secondary">
              Formatos soportados: 
              {formData.content_type === 'video' && ' MP4, AVI, MOV, WMV, FLV, WEBM'}
              {formData.content_type === 'podcast' && ' MP3, WAV, OGG, M4A, AAC'}
              {formData.content_type === 'article' && ' PDF, DOC, DOCX, PPT, PPTX'}
              {formData.content_type === 'course' && ' MP4, PDF, DOC, PPT'}
              {(formData.content_type as string) === 'webinar' && ' MP4, AVI, MOV, WMV'}
              {(formData.content_type as string) === 'infographic' && ' JPG, PNG, GIF, WEBP, PDF'}
            </Typography>
          </Box>

          {/* Categorías */}
          <Autocomplete
            multiple
            freeSolo
            options={predefinedCategories}
            value={formData.categories}
            onChange={(event, newValue) => {
              handleInputChange('categories', newValue);
            }}
            renderTags={(value, getTagProps) =>
              value.map((option, index) => (
                <Chip
                  variant="outlined"
                  label={option}
                  {...getTagProps({ index })}
                  key={option}
                  onDelete={() => handleRemoveCategory(option)}
                />
              ))
            }
            renderInput={(params) => (
              <TextField
                {...params}
                label="Categorías"
                placeholder="Selecciona o agrega categorías"
                size="medium"
                sx={{
                  '& .MuiOutlinedInput-root': {
                    borderRadius: 2,
                  }
                }}
              />
            )}
          />

          {/* Etiquetas */}
          <Autocomplete
            multiple
            freeSolo
            options={predefinedTags}
            value={formData.tags}
            onChange={(event, newValue) => {
              handleInputChange('tags', newValue);
            }}
            renderTags={(value, getTagProps) =>
              value.map((option, index) => (
                <Chip
                  variant="outlined"
                  label={option}
                  {...getTagProps({ index })}
                  key={option}
                  onDelete={() => handleRemoveTag(option)}
                />
              ))
            }
            renderInput={(params) => (
              <TextField
                {...params}
                label="Etiquetas"
                placeholder="Selecciona o agrega etiquetas"
                size="medium"
                sx={{
                  '& .MuiOutlinedInput-root': {
                    borderRadius: 2,
                  }
                }}
              />
            )}
          />
        </Box>
      </DialogContent>

      <DialogActions>
        <Button onClick={onClose}>Cancelar</Button>
        <Button
          onClick={handleSubmit}
          variant="contained"
          disabled={loading || !formData.title || !formData.description || !formData.duration_formatted}
        >
          {loading ? 'Guardando...' : (mode === 'create' ? 'Crear' : 'Actualizar')}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default ContentForm;
