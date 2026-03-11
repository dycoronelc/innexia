import React from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  LinearProgress
} from '@mui/material';

interface ActivityMetricCardProps {
  title: string;
  value: string | number;
  icon: React.ReactElement;
  color: string;
  bgColor: string;
  borderColor: string;
  progress: number;
}

const ActivityMetricCard: React.FC<ActivityMetricCardProps> = ({
  title,
  value,
  icon,
  color,
  bgColor,
  borderColor,
  progress
}) => {
  return (
    <Box sx={{ flex: { xs: '1 1 100%', sm: '1 1 calc(50% - 12px)', md: '1 1 calc(25% - 18px)' } }}>
      <Card sx={{
        height: 140,
        borderRadius: 3,
        boxShadow: '0 8px 32px rgba(0,0,0,0.08)',
        border: `1px solid ${borderColor}20`,
        background: bgColor
      }}>
        <CardContent sx={{ p: 3, height: '100%' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <Box sx={{
              backgroundColor: `${borderColor}15`,
              borderRadius: 2,
              p: 1.5,
              mr: 2,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}>
              {icon}
            </Box>
            <Box>
              <Typography variant="h5" component="div" sx={{ fontWeight: 700, color: '#1e293b' }}>
                {value}
              </Typography>
              <Typography variant="body2" sx={{ color: '#64748b', fontWeight: 500 }}>
                {title}
              </Typography>
            </Box>
          </Box>

          <Box sx={{ mt: 2 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
              <Typography variant="caption" sx={{ color: '#64748b', fontWeight: 500 }}>
                Progreso
              </Typography>
              <Typography variant="caption" sx={{ color: borderColor, fontWeight: 600 }}>
                {progress}%
              </Typography>
            </Box>
            <LinearProgress
              variant="determinate"
              value={progress}
              sx={{
                height: 6,
                borderRadius: 3,
                backgroundColor: `${borderColor}20`,
                '& .MuiLinearProgress-bar': {
                  backgroundColor: borderColor,
                  borderRadius: 3
                }
              }}
            />
          </Box>
        </CardContent>
      </Card>
    </Box>
  );
};

export default ActivityMetricCard;
