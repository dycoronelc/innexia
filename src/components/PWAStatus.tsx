import React, { useState, useEffect } from 'react';
import {
  Card,
  CardContent,
  CardHeader,
  Typography,
  Box,
  Chip,
  Button,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
  Alert,
  IconButton,
  Collapse,
  LinearProgress
} from '@mui/material';
import {
  CheckCircle as CheckIcon,
  Error as ErrorIcon,
  Warning as WarningIcon,
  Info as InfoIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  Refresh as RefreshIcon,
  Clear as ClearIcon,
  // SettingsIcon removido ya que no se usa
  BugReport as DebugIcon
} from '@mui/icons-material';
import { useOffline } from '../hooks/useOffline';
import { usePWAInstall } from '../hooks/usePWAInstall';

interface PWAStatusProps {
  showDetails?: boolean;
}

interface PWAFeature {
  name: string;
  status: 'working' | 'error' | 'warning' | 'info';
  description: string;
  details?: string;
}

export const PWAStatus: React.FC<PWAStatusProps> = ({ showDetails = false }) => {
  const { isOnline, offlineData } = useOffline();
  const { canInstall, isInstalled } = usePWAInstall();
  const [expanded, setExpanded] = useState(showDetails);
  const [swStatus, setSwStatus] = useState<'active' | 'inactive' | 'error'>('inactive');
  const [cacheInfo, setCacheInfo] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    checkServiceWorkerStatus();
    getCacheInfo();
  }, []);

  const checkServiceWorkerStatus = async () => {
    if ('serviceWorker' in navigator) {
      try {
        const registration = await navigator.serviceWorker.getRegistration();
        if (registration && registration.active) {
          setSwStatus('active');
        } else {
          setSwStatus('inactive');
        }
      } catch (error) {
        setSwStatus('error');
      }
    }
  };

  const getCacheInfo = async () => {
    if ('caches' in window) {
      try {
        const cacheNames = await caches.keys();
        const cacheDetails = await Promise.all(
          cacheNames.map(async (name) => {
            const cache = await caches.open(name);
            const keys = await cache.keys();
            return { name, size: keys.length };
          })
        );
        setCacheInfo(cacheDetails);
      } catch (error) {
        console.error('Error getting cache info:', error);
      }
    }
  };

  const handleRefresh = async () => {
    setLoading(true);
    await checkServiceWorkerStatus();
    await getCacheInfo();
    setLoading(false);
  };

  const handleClearCache = async () => {
    if ('caches' in window) {
      try {
        const cacheNames = await caches.keys();
        await Promise.all(
          cacheNames.map(cacheName => caches.delete(cacheName))
        );
        await getCacheInfo();
        console.log('Cache limpiado');
      } catch (error) {
        console.error('Error clearing cache:', error);
      }
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'working':
        return <CheckIcon color="success" />;
      case 'error':
        return <ErrorIcon color="error" />;
      case 'warning':
        return <WarningIcon color="warning" />;
      case 'info':
        return <InfoIcon color="info" />;
      default:
        return <InfoIcon color="info" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'working':
        return 'success';
      case 'error':
        return 'error';
      case 'warning':
        return 'warning';
      case 'info':
        return 'info';
      default:
        return 'default';
    }
  };

  const features: PWAFeature[] = [
    {
      name: 'Service Worker',
      status: swStatus === 'active' ? 'working' : swStatus === 'error' ? 'error' : 'warning',
      description: 'Maneja cache offline y sincronización',
      details: swStatus === 'active' ? 'Activo y funcionando' : 'No activo o con errores'
    },
    {
      name: 'Instalación PWA',
      status: isInstalled ? 'working' : canInstall ? 'info' : 'warning',
      description: 'Permite instalar la app como aplicación nativa',
      details: isInstalled ? 'Aplicación instalada' : canInstall ? 'Lista para instalar' : 'No disponible'
    },
    {
      name: 'Funcionalidad Offline',
      status: 'working',
      description: 'Trabajo sin conexión a internet',
      details: `${offlineData.length} cambios pendientes de sincronización`
    },
    {
      name: 'Cache de Recursos',
      status: cacheInfo ? 'working' : 'warning',
      description: 'Almacenamiento local de recursos',
      details: cacheInfo ? `${cacheInfo.length} caches activos` : 'No disponible'
    },
    {
      name: 'Sincronización',
      status: isOnline ? 'working' : 'warning',
      description: 'Sincronización automática de datos',
      details: isOnline ? 'Online - Sincronización activa' : 'Offline - Sincronización pendiente'
    }
  ];

  const overallStatus = features.every(f => f.status === 'working') ? 'working' :
                       features.some(f => f.status === 'error') ? 'error' :
                       features.some(f => f.status === 'warning') ? 'warning' : 'info';

  return (
    <Card sx={{ mb: 2 }}>
      <CardHeader
        title={
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Typography variant="h6">Estado de la PWA</Typography>
            <Chip
              label={overallStatus === 'working' ? 'Funcionando' : 
                     overallStatus === 'error' ? 'Con Errores' :
                     overallStatus === 'warning' ? 'Advertencias' : 'Información'}
              color={getStatusColor(overallStatus)}
              size="small"
            />
          </Box>
        }
        action={
          <Box sx={{ display: 'flex', gap: 1 }}>
            <IconButton onClick={handleRefresh} disabled={loading}>
              <RefreshIcon />
            </IconButton>
            <IconButton onClick={() => setExpanded(!expanded)}>
              {expanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
            </IconButton>
          </Box>
        }
      />
      
      <CardContent>
        {loading && <LinearProgress sx={{ mb: 2 }} />}
        
        {/* Estado general */}
        <Box sx={{ mb: 2 }}>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            Estado de conexión: {isOnline ? 'Online' : 'Offline'}
          </Typography>
          {offlineData.length > 0 && (
            <Alert severity="info" sx={{ mb: 2 }}>
              {offlineData.length} cambio{offlineData.length > 1 ? 's' : ''} pendiente{offlineData.length > 1 ? 's' : ''} de sincronización
            </Alert>
          )}
        </Box>

        {/* Lista de características */}
        <List dense>
          {features.map((feature, index) => (
            <React.Fragment key={feature.name}>
              <ListItem>
                <ListItemIcon>
                  {getStatusIcon(feature.status)}
                </ListItemIcon>
                <ListItemText
                  primary={feature.name}
                  secondary={feature.description}
                />
                <Chip
                  label={feature.status === 'working' ? 'OK' : 
                         feature.status === 'error' ? 'Error' :
                         feature.status === 'warning' ? 'Advertencia' : 'Info'}
                  color={getStatusColor(feature.status)}
                  size="small"
                  variant="outlined"
                />
              </ListItem>
              {index < features.length - 1 && <Divider />}
            </React.Fragment>
          ))}
        </List>

        {/* Detalles expandibles */}
        <Collapse in={expanded}>
          <Box sx={{ mt: 2, pt: 2, borderTop: '1px solid', borderColor: 'divider' }}>
            <Typography variant="subtitle2" gutterBottom>
              Detalles Técnicos
            </Typography>
            
            {/* Información del Service Worker */}
            <Box sx={{ mb: 2 }}>
              <Typography variant="body2" color="text.secondary">
                Service Worker: {swStatus}
              </Typography>
              {cacheInfo && (
                <Typography variant="body2" color="text.secondary">
                  Caches: {cacheInfo.map((c: any) => `${c.name} (${c.size})`).join(', ')}
                </Typography>
              )}
            </Box>

            {/* Acciones */}
            <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
              <Button
                size="small"
                variant="outlined"
                onClick={handleClearCache}
                startIcon={<ClearIcon />}
              >
                Limpiar Cache
              </Button>
              <Button
                size="small"
                variant="outlined"
                onClick={() => (window as any).setSWDebug?.((window as any).getSWConfig?.()?.debug?.verbose)}
                startIcon={<DebugIcon />}
              >
                {(window as any).getSWConfig?.()?.debug?.verbose ? 'Desactivar' : 'Activar'} Debug
              </Button>
              <Button
                size="small"
                variant="outlined"
                onClick={() => (window as any).forceSWSync?.()}
                startIcon={<RefreshIcon />}
              >
                Forzar Sincronización
              </Button>
            </Box>
          </Box>
        </Collapse>
      </CardContent>
    </Card>
  );
};


