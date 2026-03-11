import React, { useState, useCallback } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  IconButton,
  List,
  ListItem,
  ListItemText
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon
} from '@mui/icons-material';
import type { BusinessModelCanvas as BMCType } from '../types';
import { useOffline } from '../hooks/useOffline';
import { OfflineIndicator } from './OfflineIndicator';

interface BusinessModelCanvasProps {
  canvas: BMCType;
  onUpdate: (canvas: BMCType) => void;
  readOnly?: boolean;
  projectId?: string;
}

interface CanvasBlockProps {
  title: string;
  items: string[];
  onAdd: (item: string) => void;
  onEdit: (index: number, item: string) => void;
  onDelete: (index: number) => void;
  readOnly?: boolean;
  color: string;
}

const CanvasBlock: React.FC<CanvasBlockProps> = ({
  title,
  items,
  onAdd,
  onEdit,
  onDelete,
  readOnly = false,
  color
}) => {
  const [isAdding, setIsAdding] = useState(false);
  const [newItem, setNewItem] = useState('');
  const [editingIndex, setEditingIndex] = useState<number | null>(null);
  const [editingText, setEditingText] = useState('');

  const handleAdd = () => {
    if (newItem.trim()) {
      onAdd(newItem.trim());
      setNewItem('');
      setIsAdding(false);
    }
  };

  const handleEdit = () => {
    if (editingIndex !== null && editingText.trim()) {
      onEdit(editingIndex, editingText.trim());
      setEditingIndex(null);
      setEditingText('');
    }
  };

  const handleCancelEdit = () => {
    setEditingIndex(null);
    setEditingText('');
  };

  const startEdit = (index: number, text: string) => {
    setEditingIndex(index);
    setEditingText(text);
  };

  return (
    <Paper
      sx={{
        p: 2,
        height: '100%',
        minHeight: 200,
        width: '100%',
        display: 'flex',
        flexDirection: 'column',
        borderTop: `4px solid ${color}`,
        flex: 1,
        '&:hover': {
          boxShadow: 4,
        }
      }}
    >
      <Typography
        variant="h6"
        component="h3"
        gutterBottom
        sx={{
          color: color,
          fontWeight: 'bold',
          textAlign: 'center',
          mb: 2
        }}
      >
        {title}
      </Typography>

      <List sx={{ flexGrow: 1, mb: 2 }}>
        {items.map((item, index) => (
          <ListItem
            key={index}
            sx={{
              mb: 1,
              backgroundColor: 'background.paper',
              borderRadius: 1,
              border: '1px solid',
              borderColor: 'divider'
            }}
          >
            {editingIndex === index ? (
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, width: '100%' }}>
                <TextField
                  fullWidth
                  size="small"
                  value={editingText}
                  onChange={(e) => setEditingText(e.target.value)}
                  autoFocus
                />
                <IconButton size="small" onClick={handleEdit} color="primary">
                  <EditIcon />
                </IconButton>
                <IconButton size="small" onClick={handleCancelEdit} color="error">
                  <DeleteIcon />
                </IconButton>
              </Box>
            ) : (
              <Box sx={{ display: 'flex', alignItems: 'center', width: '100%', gap: 1 }}>
                <ListItemText
                  primary={item}
                  primaryTypographyProps={{
                    variant: 'body2',
                    sx: { 
                      wordBreak: 'break-word',
                      flexGrow: 1,
                      pr: 2
                    }
                  }}
                />
                {!readOnly && (
                  <Box sx={{ display: 'flex', gap: 0.5, flexShrink: 0 }}>
                    <IconButton
                      size="small"
                      onClick={() => startEdit(index, item)}
                    >
                      <EditIcon fontSize="small" />
                    </IconButton>
                    <IconButton
                      size="small"
                      onClick={() => onDelete(index)}
                      color="error"
                    >
                      <DeleteIcon fontSize="small" />
                    </IconButton>
                  </Box>
                )}
              </Box>
            )}
          </ListItem>
        ))}
      </List>

      {!readOnly && (
        <Box>
          {isAdding ? (
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <TextField
                fullWidth
                size="small"
                placeholder="Agregar elemento..."
                value={newItem}
                onChange={(e) => setNewItem(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleAdd()}
                autoFocus
              />
              <Button size="small" onClick={handleAdd} variant="contained">
                Agregar
              </Button>
              <Button size="small" onClick={() => setIsAdding(false)}>
                Cancelar
              </Button>
            </Box>
          ) : (
            <Button
              fullWidth
              startIcon={<AddIcon />}
              onClick={() => setIsAdding(true)}
              variant="outlined"
              size="small"
              sx={{ borderColor: color, color: color }}
            >
              Agregar
            </Button>
          )}
        </Box>
      )}
    </Paper>
  );
};

const BusinessModelCanvas: React.FC<BusinessModelCanvasProps> = ({
  canvas,
  onUpdate,
  readOnly = false,
  projectId
}) => {
  const { addOfflineData } = useOffline();
  const updateBlock = useCallback((field: keyof BMCType, items: string[]) => {
    const updatedCanvas = {
      ...canvas,
      [field]: items,
      updatedAt: new Date()
    };
    
    onUpdate(updatedCanvas);
    
    // Add to offline queue if we have a project ID
    if (projectId) {
      addOfflineData({
        id: `canvas-${field}-${Date.now()}`,
        type: 'canvas',
        action: 'update',
        data: {
          id: projectId,
          canvas: updatedCanvas
        },
        timestamp: Date.now()
      });
    }
  }, [canvas, onUpdate, projectId, addOfflineData]);

  const addItem = useCallback((field: keyof BMCType, item: string) => {
    const currentItems = canvas[field] as string[];
    updateBlock(field, [...currentItems, item]);
  }, [canvas, updateBlock]);

  const editItem = useCallback((field: keyof BMCType, index: number, item: string) => {
    const currentItems = [...(canvas[field] as string[])];
    currentItems[index] = item;
    updateBlock(field, currentItems);
  }, [canvas, updateBlock]);

  const deleteItem = useCallback((field: keyof BMCType, index: number) => {
    const currentItems = [...(canvas[field] as string[])];
    currentItems.splice(index, 1);
    updateBlock(field, currentItems);
  }, [canvas, updateBlock]);

  const blocks = [
    {
      key: 'keyPartners' as keyof BMCType,
      title: 'Socios Clave',
      color: '#FF6B6B',
      description: 'Alianzas estratégicas y colaboraciones'
    },
    {
      key: 'keyActivities' as keyof BMCType,
      title: 'Actividades Clave',
      color: '#4ECDC4',
      description: 'Acciones principales para entregar valor'
    },
    {
      key: 'keyResources' as keyof BMCType,
      title: 'Recursos Clave',
      color: '#45B7D1',
      description: 'Activos necesarios para el modelo'
    },
    {
      key: 'customerRelationships' as keyof BMCType,
      title: 'Relaciones con Clientes',
      color: '#FFEAA7',
      description: 'Tipo de relación con cada segmento'
    },
    {
      key: 'channels' as keyof BMCType,
      title: 'Canales',
      color: '#DDA0DD',
      description: 'Cómo llegar a los clientes'
    },
    {
      key: 'customerSegments' as keyof BMCType,
      title: 'Segmentos de Clientes',
      color: '#98D8C8',
      description: 'Grupos de personas a servir'
    },
    {
      key: 'costStructure' as keyof BMCType,
      title: 'Estructura de Costos',
      color: '#F7DC6F',
      description: 'Costos para operar el modelo'
    },
    {
      key: 'revenueStreams' as keyof BMCType,
      title: 'Flujos de Ingresos',
      color: '#BB8FCE',
      description: 'Formas de generar ingresos'
    },
    {
      key: 'valuePropositions' as keyof BMCType,
      title: 'Propuesta de Valor',
      color: '#96CEB4',
      description: 'Beneficios únicos para el cliente'
    }
  ];

  return (
    <Box>
      <OfflineIndicator />
      <Box sx={{ mb: 3, textAlign: 'center' }}>
                    <Typography variant="h4" component="h1" gutterBottom>
              Innexia - Business Model Canvas
            </Typography>
        <Typography variant="body1" color="text.secondary">
          Visualice y gestione su modelo de negocio de manera intuitiva
        </Typography>
      </Box>

      {/* ===== BUSINESS MODEL CANVAS - LAYOUT OPTIMIZADO AL 100% ===== */}
      <Box sx={{ mb: 3 }}>
        {/* Top Row - 3 columnas de igual ancho */}
        <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
          <Box sx={{ flex: { xs: '1 1 100%', md: '1 1 calc(33.33% - 16px)' } }}>
            <CanvasBlock
              title={blocks[0].title}
              items={canvas[blocks[0].key] as string[]}
              onAdd={(item) => addItem(blocks[0].key, item)}
              onEdit={(index, item) => editItem(blocks[0].key, index, item)}
              onDelete={(index) => deleteItem(blocks[0].key, index)}
              readOnly={readOnly}
              color={blocks[0].color}
            />
          </Box>
          <Box sx={{ flex: { xs: '1 1 100%', md: '1 1 calc(33.33% - 16px)' } }}>
            <CanvasBlock
              title={blocks[1].title}
              items={canvas[blocks[1].key] as string[]}
              onAdd={(item) => addItem(blocks[1].key, item)}
              onEdit={(index, item) => editItem(blocks[1].key, index, item)}
              onDelete={(index) => deleteItem(blocks[1].key, index)}
              readOnly={readOnly}
              color={blocks[1].color}
            />
          </Box>
          <Box sx={{ flex: { xs: '1 1 100%', md: '1 1 calc(33.33% - 16px)' } }}>
            <CanvasBlock
              title={blocks[2].title}
              items={canvas[blocks[2].key] as string[]}
              onAdd={(item) => addItem(blocks[2].key, item)}
              onEdit={(index, item) => editItem(blocks[2].key, index, item)}
              onDelete={(index) => deleteItem(blocks[2].key, index)}
              readOnly={readOnly}
              color={blocks[2].color}
            />
          </Box>
        </Box>

        {/* Middle Row - 3 columnas de igual ancho */}
        <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
          <Box sx={{ flex: { xs: '1 1 100%', md: '1 1 calc(33.33% - 16px)' } }}>
            <CanvasBlock
              title={blocks[3].title}
              items={canvas[blocks[3].key] as string[]}
              onAdd={(item) => addItem(blocks[3].key, item)}
              onEdit={(index, item) => editItem(blocks[3].key, index, item)}
              onDelete={(index) => deleteItem(blocks[3].key, index)}
              readOnly={readOnly}
              color={blocks[3].color}
            />
          </Box>
          <Box sx={{ flex: { xs: '1 1 100%', md: '1 1 calc(33.33% - 16px)' } }}>
            <CanvasBlock
              title="Propuesta de Valor"
              items={canvas.valuePropositions as string[]}
              onAdd={(item) => addItem('valuePropositions', item)}
              onEdit={(index, item) => editItem('valuePropositions', index, item)}
              onDelete={(index) => deleteItem('valuePropositions', index)}
              readOnly={readOnly}
              color="#96CEB4"
            />
          </Box>
          <Box sx={{ flex: { xs: '1 1 100%', md: '1 1 calc(33.33% - 16px)' } }}>
            <CanvasBlock
              title={blocks[4].title}
              items={canvas[blocks[4].key] as string[]}
              onAdd={(item) => addItem(blocks[4].key, item)}
              onEdit={(index, item) => editItem(blocks[4].key, index, item)}
              onDelete={(index) => deleteItem(blocks[4].key, index)}
              readOnly={readOnly}
              color={blocks[4].color}
            />
          </Box>
        </Box>

        {/* Bottom Row - 3 columnas de igual ancho */}
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Box sx={{ flex: { xs: '1 1 100%', md: '1 1 calc(33.33% - 16px)' } }}>
            <CanvasBlock
              title={blocks[5].title}
              items={canvas[blocks[5].key] as string[]}
              onAdd={(item) => addItem(blocks[5].key, item)}
              onEdit={(index, item) => editItem(blocks[5].key, index, item)}
              onDelete={(index) => deleteItem(blocks[5].key, index)}
              readOnly={readOnly}
              color={blocks[5].color}
            />
          </Box>
          <Box sx={{ flex: { xs: '1 1 100%', md: '1 1 calc(33.33% - 16px)' } }}>
            <CanvasBlock
              title={blocks[6].title}
              items={canvas[blocks[6].key] as string[]}
              onAdd={(item) => addItem(blocks[6].key, item)}
              onEdit={(index, item) => editItem(blocks[6].key, index, item)}
              onDelete={(index) => deleteItem(blocks[6].key, index)}
              readOnly={readOnly}
              color={blocks[6].color}
            />
          </Box>
          <Box sx={{ flex: { xs: '1 1 100%', md: '1 1 calc(33.33% - 16px)' } }}>
            <CanvasBlock
              title={blocks[7].title}
              items={canvas[blocks[7].key] as string[]}
              onAdd={(item) => addItem(blocks[7].key, item)}
              onEdit={(index, item) => editItem(blocks[7].key, index, item)}
              onDelete={(index) => deleteItem(blocks[7].key, index)}
              readOnly={readOnly}
              color={blocks[7].color}
            />
          </Box>
        </Box>
      </Box>

      <Box sx={{ mt: 3, textAlign: 'center' }}>
        <Typography variant="body2" color="text.secondary">
          Última actualización: {canvas.updatedAt.toLocaleDateString()}
        </Typography>
      </Box>
    </Box>
  );
};

export default BusinessModelCanvas;

