import React from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  Box,
  IconButton
} from '@mui/material';
import {
  Warning as WarningIcon,
  Close as CloseIcon
} from '@mui/icons-material';

interface ConfirmationDialogProps {
  open: boolean;
  onClose: () => void;
  onConfirm: () => void;
  title: string;
  message: string;
  confirmText?: string;
  cancelText?: string;
  severity?: 'warning' | 'error' | 'info';
  loading?: boolean;
}

const ConfirmationDialog: React.FC<ConfirmationDialogProps> = ({
  open,
  onClose,
  onConfirm,
  title,
  message,
  confirmText = 'Confirmar',
  cancelText = 'Cancelar',
  severity = 'warning',
  loading = false
}) => {
  const getIconColor = () => {
    switch (severity) {
      case 'error':
        return '#f44336';
      case 'info':
        return '#2196f3';
      case 'warning':
      default:
        return '#ff9800';
    }
  };

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="sm"
      fullWidth
      PaperProps={{
        sx: {
          borderRadius: 3,
          boxShadow: '0 8px 32px rgba(0,0,0,0.12)',
          border: '1px solid #e2e8f0'
        }
      }}
    >
      <DialogTitle sx={{ 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'space-between',
        pb: 1,
        borderBottom: '1px solid #e2e8f0'
      }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <WarningIcon sx={{ color: getIconColor(), fontSize: 28 }} />
          <Typography variant="h6" component="div" sx={{ fontWeight: 600 }}>
            {title}
          </Typography>
        </Box>
        <IconButton
          onClick={onClose}
          size="small"
          sx={{ 
            color: '#64748b',
            '&:hover': { backgroundColor: '#f1f5f9' }
          }}
        >
          <CloseIcon />
        </IconButton>
      </DialogTitle>
      
      <DialogContent sx={{ pt: 3, pb: 2 }}>
        <Typography variant="body1" color="text.secondary" sx={{ lineHeight: 1.6 }}>
          {message}
        </Typography>
      </DialogContent>
      
      <DialogActions sx={{ 
        p: 3, 
        pt: 2,
        borderTop: '1px solid #e2e8f0',
        gap: 1
      }}>
        <Button
          onClick={onClose}
          variant="outlined"
          disabled={loading}
          sx={{
            borderRadius: 2,
            px: 3,
            py: 1,
            textTransform: 'none',
            fontWeight: 500,
            borderColor: '#e2e8f0',
            color: '#64748b',
            '&:hover': {
              borderColor: '#cbd5e1',
              backgroundColor: '#f8fafc'
            }
          }}
        >
          {cancelText}
        </Button>
        <Button
          onClick={onConfirm}
          variant="contained"
          disabled={loading}
          sx={{
            borderRadius: 2,
            px: 3,
            py: 1,
            textTransform: 'none',
            fontWeight: 500,
            backgroundColor: severity === 'error' ? '#ef4444' : '#3b82f6',
            '&:hover': {
              backgroundColor: severity === 'error' ? '#dc2626' : '#2563eb'
            },
            '&:disabled': {
              backgroundColor: '#cbd5e1',
              color: '#94a3b8'
            }
          }}
        >
          {loading ? 'Procesando...' : confirmText}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default ConfirmationDialog;

