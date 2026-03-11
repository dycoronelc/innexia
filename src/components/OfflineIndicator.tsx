import React from 'react';
import {
  Alert,
  AlertTitle,
  Button,
  Snackbar,
  Chip,
  Box,
  Typography,
  LinearProgress
} from '@mui/material';
import {
  WifiOff as WifiOffIcon,
  Wifi as WifiIcon,
  Sync as SyncIcon,
  CheckCircle as CheckCircleIcon
} from '@mui/icons-material';
import { useOffline } from '../hooks/useOffline';

interface OfflineIndicatorProps {
  showOfflineData?: boolean;
}

export const OfflineIndicator: React.FC<OfflineIndicatorProps> = ({ 
  showOfflineData = true 
}) => {
  const {
    isOnline,
    isOffline,
    offlineData,
    syncOfflineData,
    clearOfflineData
  } = useOffline();

  const [showSnackbar, setShowSnackbar] = React.useState(false);
  const [syncing, setSyncing] = React.useState(false);
  const [syncMessage, setSyncMessage] = React.useState('');

  const handleSync = async () => {
    if (offlineData.length === 0) return;

    setSyncing(true);
    setSyncMessage('Sincronizando datos offline...');
    setShowSnackbar(true);

    try {
      await syncOfflineData();
      setSyncMessage('Sincronización completada');
      setTimeout(() => {
        setShowSnackbar(false);
        setSyncing(false);
      }, 2000);
    } catch (error) {
      setSyncMessage('Error en la sincronización');
      setTimeout(() => {
        setShowSnackbar(false);
        setSyncing(false);
      }, 3000);
    }
  };

  const handleClearOfflineData = () => {
    clearOfflineData();
    setShowSnackbar(false);
  };

  if (isOnline && offlineData.length === 0) {
    return null;
  }

  return (
    <>
      {/* Offline Alert */}
      {isOffline && (
        <Alert
          severity="warning"
          icon={<WifiOffIcon />}
          action={
            <Button
              color="inherit"
              size="small"
              onClick={() => window.location.reload()}
            >
              Recargar
            </Button>
          }
          sx={{ mb: 2 }}
        >
          <AlertTitle>Modo Offline</AlertTitle>
          Estás trabajando sin conexión. Los cambios se guardarán localmente y se sincronizarán cuando vuelvas a estar online.
        </Alert>
      )}

      {/* Offline Data Queue */}
      {showOfflineData && offlineData.length > 0 && (
        <Alert
          severity="info"
          icon={<WifiIcon />}
          action={
            <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
              <Chip
                label={`${offlineData.length} pendiente${offlineData.length > 1 ? 's' : ''}`}
                size="small"
                color="primary"
                variant="outlined"
              />
              <Button
                color="inherit"
                size="small"
                onClick={handleSync}
                disabled={syncing || isOffline}
                startIcon={syncing ? <LinearProgress sx={{ width: 16, height: 16 }} /> : <SyncIcon />}
              >
                {syncing ? 'Sincronizando...' : 'Sincronizar'}
              </Button>
              <Button
                color="inherit"
                size="small"
                onClick={handleClearOfflineData}
                disabled={syncing}
              >
                Limpiar
              </Button>
            </Box>
          }
          sx={{ mb: 2 }}
        >
          <AlertTitle>Datos Offline Pendientes</AlertTitle>
          Tienes {offlineData.length} cambio{offlineData.length > 1 ? 's' : ''} pendiente{offlineData.length > 1 ? 's' : ''} de sincronización.
          {isOffline && ' Los datos se sincronizarán automáticamente cuando vuelvas a estar online.'}
        </Alert>
      )}

      {/* Sync Progress Snackbar */}
      <Snackbar
        open={showSnackbar}
        autoHideDuration={null}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert
          severity={syncMessage.includes('Error') ? 'error' : 'success'}
          icon={syncMessage.includes('Error') ? <WifiOffIcon /> : <CheckCircleIcon />}
          sx={{ width: '100%' }}
        >
          <Typography variant="body2">{syncMessage}</Typography>
          {syncing && (
            <LinearProgress 
              sx={{ mt: 1, width: '100%' }} 
              color="primary" 
            />
          )}
        </Alert>
      </Snackbar>
    </>
  );
};


