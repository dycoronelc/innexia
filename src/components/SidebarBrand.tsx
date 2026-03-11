import React from 'react';
import { Box, Typography } from '@mui/material';

interface SidebarBrandProps {
  isOpen: boolean;
  size?: 'small' | 'medium' | 'large';
}

export const SidebarBrand: React.FC<SidebarBrandProps> = ({
  isOpen,
  size = 'medium'
}) => {
  const getSize = () => {
    switch (size) {
      case 'small': return { 
        logoHeight: 32, 
        logoWidth: 80, 
        fontSize: 16, // 1rem = 16px
        gap: 1,
        containerHeight: 64
      };
      case 'large': return { 
        logoHeight: 48, 
        logoWidth: 120, 
        fontSize: 24, // 1.5rem = 24px
        gap: 1.5,
        containerHeight: 80
      };
      default: return { 
        logoHeight: 40, 
        logoWidth: 100, 
        fontSize: 20, // 1.25rem = 20px
        gap: 1.25,
        containerHeight: 64
      };
    }
  };

  const { logoHeight, fontSize, gap, containerHeight } = getSize();

  // Si la barra está cerrada, mostrar solo el isotipo centrado
  if (!isOpen) {
    return (
      <Box sx={{ 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'flex-start',
        width: '100%',
        height: containerHeight,
        pl: 3,
        pr: 2,
        py: 0,
        boxSizing: 'border-box'
      }}>
        {/* Isotipo - solo el icono */}
        <Box sx={{
          width: logoHeight,
          height: logoHeight,
          borderRadius: 2,
          background: 'linear-gradient(135deg, #4D2581 0%, #ED682B 100%)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: 'white'
        }}>
          <Typography 
            variant="h6" 
            sx={{ 
              fontWeight: 'bold', 
              fontSize: Math.round(fontSize * 0.6),
              color: 'white'
            }}
          >
            I
          </Typography>
        </Box>
      </Box>
    );
  }

  // Si la barra está abierta, mostrar el logo completo
  return (
    <Box sx={{ 
      display: 'flex', 
      alignItems: 'center', 
      justifyContent: 'flex-start',
      width: '100%',
      height: containerHeight,
      pl: 3,
      pr: 2,
      py: 0,
      boxSizing: 'border-box'
    }}>
      <Box sx={{ 
        display: 'flex', 
        alignItems: 'center', 
        gap: gap
      }}>
        {/* Isotipo */}
        <Box sx={{
          width: logoHeight,
          height: logoHeight,
          borderRadius: 2,
          background: 'linear-gradient(135deg, #4D2581 0%, #ED682B 100%)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: 'white'
        }}>
          <Typography 
            variant="h6" 
            sx={{ 
              fontWeight: 'bold', 
              fontSize: Math.round(fontSize * 0.6),
              color: 'white'
            }}
          >
            I
          </Typography>
        </Box>
        
        {/* Logo real de innexia */}
        <Box sx={{ position: 'relative' }}>
          <Typography 
            variant="h6" 
            sx={{ 
              fontWeight: 700, 
              fontSize: fontSize,
              color: '#4c1d95', // Dark purple
              letterSpacing: '-0.5px',
              position: 'relative'
            }}
          >
            Innexia
          </Typography>
          
          {/* Punto naranja de la primera "I" */}
          <Box sx={{
            position: 'absolute',
            top: Math.round(-fontSize * 0.3),
            left: Math.round(fontSize * 0.15),
            width: Math.round(fontSize * 0.4),
            height: Math.round(fontSize * 0.4),
            borderRadius: '50%',
            backgroundColor: '#f97316', // Orange
            zIndex: 1
          }} />
          
          {/* Punto naranja de la segunda "i" */}
          <Box sx={{
            position: 'absolute',
            top: Math.round(-fontSize * 0.3),
            left: Math.round(fontSize * 2.8),
            width: Math.round(fontSize * 0.4),
            height: Math.round(fontSize * 0.4),
            borderRadius: '50%',
            backgroundColor: '#f97316', // Orange
            zIndex: 1
          }} />
          
          {/* Conexión orgánica naranja */}
          <Box sx={{
            position: 'absolute',
            top: Math.round(-fontSize * 0.4),
            left: Math.round(fontSize * 2.8),
            width: Math.round(fontSize * 0.8),
            height: Math.round(fontSize * 0.8),
            backgroundColor: '#f97316', // Orange
            borderRadius: '50%',
            zIndex: 1
          }} />
          
          {/* Línea de conexión */}
          <Box sx={{
            position: 'absolute',
            top: Math.round(-fontSize * 0.2),
            left: Math.round(fontSize * 3.2),
            width: Math.round(fontSize * 0.3),
            height: Math.round(fontSize * 0.1),
            backgroundColor: '#f97316', // Orange
            borderRadius: '50%',
            transform: 'rotate(45deg)',
            zIndex: 1
          }} />
        </Box>
      </Box>
    </Box>
  );
};

export default SidebarBrand;
