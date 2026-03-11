import React, { useState, useRef } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { documentService } from '../services/api';
import {
  Box,
  Paper,
  Typography,
  Button,
  Card,
  CardContent,
  CardActions,
  IconButton,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Alert,
  LinearProgress,

  Tooltip
} from '@mui/material';
import {
  Upload as UploadIcon,
  Description as DocumentIcon,
  Image as ImageIcon,
  PictureAsPdf as PdfIcon,
  Delete as DeleteIcon,
  Download as DownloadIcon,
  Visibility as ViewIcon,
  Add as AddIcon,
  Edit as EditIcon
} from '@mui/icons-material';
import type { ProjectDocument } from '../types';

interface ProjectDocumentsProps {
  documents: ProjectDocument[];
  projectId: string;
  onAddDocument: (document: ProjectDocument) => void;
  onDeleteDocument: (documentId: string) => void;
  onUpdateDocument: (document: ProjectDocument) => void;
}

const ProjectDocuments: React.FC<ProjectDocumentsProps> = ({
  documents,
  projectId,
  onAddDocument,
  onDeleteDocument,
  onUpdateDocument
}) => {
  const { token } = useAuth();
  const [uploadDialogOpen, setUploadDialogOpen] = useState(false);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [selectedDocument, setSelectedDocument] = useState<ProjectDocument | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadError, setUploadError] = useState('');
  const [editForm, setEditForm] = useState({
    name: '',
    description: ''
  });
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setEditForm({
        name: file.name.split('.')[0] || file.name,
        description: ''
      });
      setSelectedDocument({
        id: '',
        name: file.name.split('.')[0] || file.name,
        originalName: file.name,
        fileType: file.type || file.name.split('.').pop() || 'unknown',
        fileSize: file.size,
        uploadedBy: 'Usuario Actual', // En una app real, esto vendría del contexto de autenticación
        uploadedAt: new Date(),
        projectId
      });
    }
  };

  const handleUpload = async () => {
    if (!selectedDocument) return;

    setUploading(true);
    setUploadProgress(0);
    setUploadError('');

    try {
      // Simular proceso de subida
      for (let i = 0; i <= 100; i += 10) {
        await new Promise(resolve => setTimeout(resolve, 100));
        setUploadProgress(i);
      }

      // Crear documento con ID único
      const newDocument: ProjectDocument = {
        ...selectedDocument,
        id: Date.now().toString(),
        name: editForm.name,
        description: editForm.description
      };

      onAddDocument(newDocument);
      handleCloseUploadDialog();
    } catch (error) {
      setUploadError('Error al subir el documento');
    } finally {
      setUploading(false);
      setUploadProgress(0);
    }
  };

  const handleEditDocument = (document: ProjectDocument) => {
    setSelectedDocument(document);
    setEditForm({
      name: document.name,
      description: document.description || ''
    });
    setEditDialogOpen(true);
  };

  const handleSaveEdit = () => {
    if (selectedDocument) {
      const updatedDocument: ProjectDocument = {
        ...selectedDocument,
        name: editForm.name,
        description: editForm.description
      };
      onUpdateDocument(updatedDocument);
      setEditDialogOpen(false);
    }
  };

  const handleDeleteDocument = (documentId: string) => {
    if (window.confirm('¿Está seguro de que desea eliminar este documento?')) {
      onDeleteDocument(documentId);
    }
  };

  const handleView = async (document: ProjectDocument) => {
    if (!token) {
      console.error('No hay token de autenticación');
      return;
    }

    try {
      // Para visualizar, primero obtenemos el documento y luego lo abrimos en una nueva pestaña
      const response = await documentService.downloadDocument(document.id, token);
      
      // Determinar el tipo MIME basado en la extensión del archivo
      const getMimeType = (filename: string) => {
        const ext = filename.split('.').pop()?.toLowerCase();
        switch (ext) {
          case 'pdf':
            return 'application/pdf';
          case 'jpg':
          case 'jpeg':
            return 'image/jpeg';
          case 'png':
            return 'image/png';
          case 'gif':
            return 'image/gif';
          case 'txt':
            return 'text/plain';
          case 'doc':
          case 'docx':
            return 'application/msword';
          case 'xls':
          case 'xlsx':
            return 'application/vnd.ms-excel';
          default:
            return 'application/octet-stream';
        }
      };

      const mimeType = getMimeType(document.originalName || document.name);
      
      // Crear URL del blob con el tipo MIME correcto
      const blob = new Blob([response], { type: mimeType });
      const url = window.URL.createObjectURL(blob);
      
      // Para PDFs e imágenes, abrir en nueva pestaña
      if (mimeType === 'application/pdf' || mimeType.startsWith('image/')) {
        window.open(url, '_blank');
      } else {
        // Para otros tipos de archivo, descargar directamente
        const link = window.document.createElement('a');
        link.href = url;
        link.download = document.originalName || document.name;
        window.document.body.appendChild(link);
        link.click();
        window.document.body.removeChild(link);
      }
      
      // Limpiar la URL después de un tiempo
      setTimeout(() => {
        window.URL.revokeObjectURL(url);
      }, 1000);
    } catch (error) {
      console.error('Error al visualizar documento:', error);
      alert('Error al visualizar el documento. Por favor, inténtelo de nuevo.');
    }
  };

  const handleDownload = async (document: ProjectDocument) => {
    if (!token) {
      console.error('No hay token de autenticación');
      return;
    }

    try {
      // Descargar el documento
      const response = await documentService.downloadDocument(document.id, token);
      
      // Determinar el tipo MIME basado en la extensión del archivo
      const getMimeType = (filename: string) => {
        const ext = filename.split('.').pop()?.toLowerCase();
        switch (ext) {
          case 'pdf':
            return 'application/pdf';
          case 'jpg':
          case 'jpeg':
            return 'image/jpeg';
          case 'png':
            return 'image/png';
          case 'gif':
            return 'image/gif';
          case 'txt':
            return 'text/plain';
          case 'doc':
          case 'docx':
            return 'application/msword';
          case 'xls':
          case 'xlsx':
            return 'application/vnd.ms-excel';
          default:
            return 'application/octet-stream';
        }
      };

      const mimeType = getMimeType(document.originalName || document.name);
      
      // Crear URL del blob con el tipo MIME correcto
      const blob = new Blob([response], { type: mimeType });
      const url = window.URL.createObjectURL(blob);
      
      // Crear enlace de descarga
      const link = window.document.createElement('a');
      link.href = url;
      link.download = document.originalName || document.name;
      link.style.display = 'none';
      window.document.body.appendChild(link);
      link.click();
      
      // Limpiar
      window.document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error al descargar documento:', error);
      alert('Error al descargar el documento. Por favor, inténtelo de nuevo.');
    }
  };

  const handleCloseUploadDialog = () => {
    setUploadDialogOpen(false);
    setSelectedDocument(null);
    setEditForm({ name: '', description: '' });
    setUploadError('');
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleCloseEditDialog = () => {
    setEditDialogOpen(false);
    setSelectedDocument(null);
    setEditForm({ name: '', description: '' });
  };

  const getFileIcon = (fileType: string) => {
    if (!fileType || fileType === 'unknown') return <DocumentIcon />;
    const lowerType = fileType.toLowerCase();
    if (lowerType.includes('pdf')) return <PdfIcon />;
    if (lowerType.includes('image') || lowerType.includes('jpg') || lowerType.includes('png') || lowerType.includes('gif')) return <ImageIcon />;
    if (lowerType.includes('word') || lowerType.includes('docx')) return <DocumentIcon />;
    if (lowerType.includes('excel') || lowerType.includes('xlsx')) return <DocumentIcon />;
    return <DocumentIcon />;
  };

  const getFileTypeColor = (fileType: string) => {
    if (!fileType || fileType === 'unknown') return 'default';
    const lowerType = fileType.toLowerCase();
    if (lowerType.includes('pdf')) return 'error';
    if (lowerType.includes('image') || lowerType.includes('jpg') || lowerType.includes('png') || lowerType.includes('gif')) return 'success';
    if (lowerType.includes('word') || lowerType.includes('docx')) return 'primary';
    if (lowerType.includes('excel') || lowerType.includes('xlsx')) return 'success';
    return 'default';
  };

  const formatFileSize = (bytes: number) => {
    if (!bytes || bytes === 0) return 'Tamaño no disponible';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const openUploadDialog = () => {
    setUploadDialogOpen(true);
  };

  return (
    <Box sx={{ width: '100%' }}>
      {/* Header con botón de subida */}
      <Box sx={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center', 
        mb: 3 
      }}>
        <Typography variant="h6" component="h2" sx={{ fontWeight: 600 }}>
          Documentos del Proyecto
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={openUploadDialog}
        >
          Subir Documento
        </Button>
      </Box>

      {/* Lista de documentos */}
      {documents.length === 0 ? (
        <Paper sx={{ p: 4, textAlign: 'center' }}>
          <DocumentIcon sx={{ fontSize: 60, color: 'text.secondary', mb: 2 }} />
          <Typography variant="h6" color="text.secondary" gutterBottom>
            No hay documentos
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Sube documentos para mantener todo organizado en un solo lugar
          </Typography>
          <Button
            variant="outlined"
            startIcon={<UploadIcon />}
            onClick={openUploadDialog}
          >
            Subir Primer Documento
          </Button>
        </Paper>
      ) : (
        <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', sm: 'repeat(2, 1fr)', md: 'repeat(3, 1fr)' }, gap: 3 }}>
          {documents.map((document) => (
            <Box key={document.id}>
              <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                <CardContent sx={{ flexGrow: 1 }}>
                  <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 1, mb: 2 }}>
                    <Box sx={{ color: 'primary.main', mt: 0.5 }}>
                      {getFileIcon(document.fileType)}
                    </Box>
                    <Box sx={{ flexGrow: 1, minWidth: 0 }}>
                      <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1 }}>
                        {document.name || 'Sin nombre'}
                      </Typography>
                      <Typography variant="caption" color="text.secondary" sx={{ display: 'block' }}>
                        {document.originalName || 'Sin nombre original'}
                      </Typography>
                    </Box>
                  </Box>
                  
                  <Box sx={{ display: 'flex', gap: 1, mb: 2, flexWrap: 'wrap' }}>
                    <Chip
                      label={document.fileType && document.fileType !== 'unknown' ? document.fileType.toUpperCase() : 'DOCUMENTO'}
                      size="small"
                      color={getFileTypeColor(document.fileType) as any}
                      variant="outlined"
                    />
                    <Chip
                      label={formatFileSize(document.fileSize || 0)}
                      size="small"
                      variant="outlined"
                    />
                  </Box>
                  
                  {document.description && (
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                      {document.description}
                    </Typography>
                  )}
                  
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                    <Typography variant="caption" color="text.secondary">
                      Subido por: {document.uploadedBy || 'Sin especificar'}
                    </Typography>
                  </Box>
                  
                  <Typography variant="caption" color="text.secondary">
                    {document.uploadedAt ? document.uploadedAt.toLocaleDateString() : 'Fecha no disponible'}
                  </Typography>
                </CardContent>
                
                <CardActions sx={{ justifyContent: 'space-between', px: 2, pb: 2 }}>
                  <Box>
                    <Tooltip title="Ver">
                      <IconButton 
                        size="small" 
                        color="primary"
                        onClick={() => handleView(document)}
                      >
                        <ViewIcon />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Descargar">
                      <IconButton 
                        size="small" 
                        color="primary"
                        onClick={() => handleDownload(document)}
                      >
                        <DownloadIcon />
                      </IconButton>
                    </Tooltip>
                  </Box>
                  
                  <Box>
                    <Tooltip title="Editar">
                      <IconButton 
                        size="small" 
                        color="primary"
                        onClick={() => handleEditDocument(document)}
                      >
                        <EditIcon />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Eliminar">
                      <IconButton 
                        size="small" 
                        color="error"
                        onClick={() => handleDeleteDocument(document.id)}
                      >
                        <DeleteIcon />
                      </IconButton>
                    </Tooltip>
                  </Box>
                </CardActions>
              </Card>
            </Box>
          ))}
        </Box>
      )}

      {/* Dialog para subir documento */}
      <Dialog open={uploadDialogOpen} onClose={handleCloseUploadDialog} maxWidth="sm" fullWidth>
        <DialogTitle>
          Subir Nuevo Documento
        </DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3, pt: 1 }}>
            <Box>
              <input
                type="file"
                ref={fileInputRef}
                onChange={handleFileSelect}
                accept=".pdf,.jpg,.jpeg,.png,.doc,.docx,.xls,.xlsx,.txt"
                style={{ display: 'none' }}
              />
              <Button
                variant="outlined"
                startIcon={<UploadIcon />}
                onClick={() => fileInputRef.current?.click()}
                fullWidth
                sx={{ py: 2 }}
              >
                Seleccionar Archivo
              </Button>
              {selectedDocument && (
                <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                  Archivo seleccionado: {selectedDocument.originalName}
                </Typography>
              )}
            </Box>
            
            <TextField
              fullWidth
              label="Nombre del Documento"
              value={editForm.name}
              onChange={(e) => setEditForm({ ...editForm, name: e.target.value })}
              required
            />
            
            <TextField
              fullWidth
              label="Descripción (opcional)"
              value={editForm.description}
              onChange={(e) => setEditForm({ ...editForm, description: e.target.value })}
              multiline
              rows={3}
            />
            
            {uploading && (
              <Box>
                <LinearProgress variant="determinate" value={uploadProgress} sx={{ mb: 1 }} />
                <Typography variant="body2" color="text.secondary">
                  Subiendo... {uploadProgress}%
                </Typography>
              </Box>
            )}
            
            {uploadError && (
              <Alert severity="error">{uploadError}</Alert>
            )}
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseUploadDialog} disabled={uploading}>
            Cancelar
          </Button>
          <Button 
            onClick={handleUpload} 
            variant="contained"
            disabled={!selectedDocument || !editForm.name || uploading}
            startIcon={uploading ? undefined : <UploadIcon />}
          >
            {uploading ? 'Subiendo...' : 'Subir Documento'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Dialog para editar documento */}
      <Dialog open={editDialogOpen} onClose={handleCloseEditDialog} maxWidth="sm" fullWidth>
        <DialogTitle>
          Editar Documento
        </DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3, pt: 1 }}>
            <TextField
              fullWidth
              label="Nombre del Documento"
              value={editForm.name}
              onChange={(e) => setEditForm({ ...editForm, name: e.target.value })}
              required
            />
            
            <TextField
              fullWidth
              label="Descripción"
              value={editForm.description}
              onChange={(e) => setEditForm({ ...editForm, description: e.target.value })}
              multiline
              rows={3}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseEditDialog}>
            Cancelar
          </Button>
          <Button 
            onClick={handleSaveEdit} 
            variant="contained"
            disabled={!editForm.name}
          >
            Guardar Cambios
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ProjectDocuments;
