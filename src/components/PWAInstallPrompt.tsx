import React, { useState } from 'react';
import {
  Card,
  CardContent,
  CardActions,
  Button,
  Typography,
  Box,
  Chip,
  IconButton,
  Collapse,
  // Alert removido ya que no se usa
} from '@mui/material';
import {
  GetApp as InstallIcon,
  Close as CloseIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  CheckCircle as CheckCircleIcon
} from '@mui/icons-material';
import { usePWAInstall } from '../hooks/usePWAInstall';

interface PWAInstallPromptProps {
  onClose?: () => void;
}

export const PWAInstallPrompt: React.FC<PWAInstallPromptProps> = ({ onClose }) => {
  const { canInstall, isInstalled, install } = usePWAInstall();
  const [expanded, setExpanded] = useState(false);
  const [installing, setInstalling] = useState(false);
  const [showSuccess, setShowSuccess] = useState(false);
  const [isVisible, setIsVisible] = useState(() => {
    // Check if user previously dismissed the prompt
    const dismissed = localStorage.getItem('pwa-install-dismissed');
    return dismissed !== 'true';
  });

  // Reset function for development/testing
  const resetPrompt = () => {
    localStorage.removeItem('pwa-install-dismissed');
    setIsVisible(true);
  };

  const handleInstall = async () => {
    if (!canInstall) return;

    setInstalling(true);
    try {
      await install();
      setShowSuccess(true);
      setTimeout(() => {
        setShowSuccess(false);
        onClose?.();
      }, 2000);
    } catch (error) {
      console.error('Installation failed:', error);
    } finally {
      setInstalling(false);
    }
  };

  const handleClose = () => {
    setIsVisible(false);
    // Remember that user dismissed the prompt
    localStorage.setItem('pwa-install-dismissed', 'true');
    onClose?.();
  };

  // Don't show if already installed, can't install, or user closed it
  if (isInstalled || !canInstall || !isVisible) {
    return null;
  }

  if (showSuccess) {
    return (
      <Card sx={{ 
        position: 'fixed', 
        bottom: 20, 
        right: 20, 
        zIndex: 1000,
        minWidth: 300,
        bgcolor: 'success.light',
        color: 'success.contrastText'
      }}>
        <CardContent sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <CheckCircleIcon />
          <Typography variant="body1">
            ¡Aplicación instalada exitosamente!
          </Typography>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card sx={{ 
      position: 'fixed', 
      bottom: 20, 
      right: 20, 
      zIndex: 1000,
      minWidth: 300,
      maxWidth: 400,
      boxShadow: 6
    }}>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
                      <Typography variant="h6" component="h3">
              Instalar Innexia
            </Typography>
          <IconButton size="small" onClick={handleClose}>
            <CloseIcon />
          </IconButton>
        </Box>
        
        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
          Instala esta aplicación en tu dispositivo para acceder más rápido y trabajar offline.
        </Typography>

        <Box sx={{ display: 'flex', gap: 1, mb: 2, flexWrap: 'wrap' }}>
          <Chip 
            label="Trabajo offline" 
            size="small" 
            color="primary" 
            variant="outlined" 
          />
          <Chip 
            label="Acceso rápido" 
            size="small" 
            color="primary" 
            variant="outlined" 
          />
          <Chip 
            label="Notificaciones" 
            size="small" 
            color="primary" 
            variant="outlined" 
          />
          {import.meta.env.DEV && (
            <Chip 
              label="Reset" 
              size="small" 
              color="secondary" 
              variant="outlined"
              onClick={resetPrompt}
              sx={{ cursor: 'pointer' }}
            />
          )}
        </Box>

        <Collapse in={expanded}>
          <Box sx={{ mt: 2, p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
            <Typography variant="body2" color="text.secondary">
              <strong>Beneficios de la instalación:</strong>
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
              • Acceso directo desde el escritorio o pantalla de inicio
            </Typography>
            <Typography variant="body2" color="text.secondary">
              • Funcionalidad completa sin conexión a internet
            </Typography>
            <Typography variant="body2" color="text.secondary">
              • Sincronización automática cuando vuelvas a estar online
            </Typography>
            <Typography variant="body2" color="text.secondary">
              • Notificaciones push para actualizaciones importantes
            </Typography>
          </Box>
        </Collapse>
      </CardContent>

      <CardActions sx={{ justifyContent: 'space-between', px: 2, pb: 2 }}>
        <Button
          size="small"
          onClick={() => setExpanded(!expanded)}
          endIcon={expanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
        >
          {expanded ? 'Menos' : 'Más info'}
        </Button>
        
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button
            size="small"
            variant="outlined"
            onClick={handleClose}
          >
            Más tarde
          </Button>
          <Button
            size="small"
            variant="contained"
            startIcon={<InstallIcon />}
            onClick={handleInstall}
            disabled={installing}
          >
            {installing ? 'Instalando...' : 'Instalar'}
          </Button>
        </Box>
      </CardActions>
    </Card>
  );
};
