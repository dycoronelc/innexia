import React from 'react';
import { Box } from '@mui/material';
import type { BoxProps } from '@mui/material';

interface InnexiaLogoProps extends Omit<BoxProps, 'component'> {
  variant?: 'full' | 'compact' | 'icon';
  size?: 'small' | 'medium' | 'large';
  color?: 'primary' | 'secondary' | 'custom';
  customColor?: string;
  showText?: boolean;
}

export const InnexiaLogo: React.FC<InnexiaLogoProps> = ({
  variant = 'full',
  size = 'medium',
  color = 'primary',
  customColor,
  showText = true,
  ...boxProps
}) => {
  const getSize = () => {
    switch (size) {
      case 'small': return { width: 32, height: 32 };
      case 'large': return { width: '100%', height: 'auto' };
      default: return { width: 48, height: 48 };
    }
  };

  const { width, height } = getSize();

  return (
    <Box
      component="img"
      src="/logo-blanco.png"
      alt="Innexia Logo"
      sx={{
        width,
        height,
        objectFit: 'contain',
        ...boxProps.sx
      }}
      {...boxProps}
    />
  );
};
