import React from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Chip,
  SvgIcon
} from '@mui/material';

interface ProjectCardProps {
  title: string;
  value: number | string;
  icon: React.ReactElement;
  bgColor: string;
  borderColor: string;
  subtitle: string;
  trend: string;
  trendColor?: string;
}

const ProjectCard: React.FC<ProjectCardProps> = ({
  title,
  value,
  icon,
  bgColor,
  borderColor,
  subtitle,
  trend,
  trendColor = 'success.main'
}) => {
  return (
    <Box sx={{ flex: { xs: '1 1 100%', sm: '1 1 calc(50% - 12px)', md: '1 1 calc(25% - 18px)' } }}>
      <Card sx={{ 
        height: 160, 
        background: bgColor,
        borderRadius: 3,
        boxShadow: '0 8px 32px rgba(0,0,0,0.08)',
        border: `1px solid ${borderColor}20`,
        position: 'relative',
        overflow: 'hidden'
      }}>
        <CardContent sx={{ p: 3, height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <Box>
              <Typography variant="h4" component="div" sx={{ 
                fontWeight: 800, 
                color: borderColor,
                mb: 0.5
              }}>
                {value}
              </Typography>
              <Typography variant="body2" sx={{ 
                color: '#64748b',
                fontWeight: 500
              }}>
                {title}
              </Typography>
            </Box>
            <Box sx={{ 
              backgroundColor: `${borderColor}15`, 
              borderRadius: 2, 
              p: 1.5,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}>
              {icon}
            </Box>
          </Box>
          
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography variant="caption" sx={{ 
              color: '#64748b',
              fontWeight: 500
            }}>
              {subtitle}
            </Typography>
            <Chip 
              label={trend} 
              size="small" 
              sx={{ 
                backgroundColor: `${borderColor}20`,
                color: borderColor,
                fontWeight: 600,
                fontSize: '0.75rem'
              }} 
            />
          </Box>
        </CardContent>
      </Card>
    </Box>
  );
};

export default ProjectCard;
