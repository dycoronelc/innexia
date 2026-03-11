import React, { useState } from 'react';
import {
  Box,
  Paper,
  TextField,
  Button,
  Typography,
  Link,
  Alert,
  CircularProgress,
  Container,
  Grid,
  InputAdornment
} from '@mui/material';
import { 
  EmailOutlined, 
  Business as BusinessIcon
} from '@mui/icons-material';


const ForgotPasswordPage: React.FC = () => {
  const [email, setEmail] = useState('');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);


  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setMessage('');
    setLoading(true);

    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      setMessage('Se ha enviado un enlace de recuperación a su correo electrónico.');
    } catch (err) {
      setError('Error al enviar el enlace de recuperación. Intente nuevamente.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box
      sx={{
        minHeight: '100vh',
        width: '100vw',
        background: 'linear-gradient(135deg, #4D2581 0%, #ED682B 100%)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        margin: 0,
        padding: 0,
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0
      }}
    >
      <Container maxWidth="lg" sx={{ height: '100%', display: 'flex', alignItems: 'center' }}>
        <Grid container sx={{ alignItems: 'center', justifyContent: 'center' }}>
          {/* Left Side - Branding */}
          <Grid 
            columns={{ xs: 12, md: 6 }} 
            sx={{ 
              display: { xs: 'none', md: 'flex' },
              flexDirection: 'column',
              justifyContent: 'center',
              alignItems: 'center',
              color: 'white',
              textAlign: 'center',
              pr: 4
            }}
          >
            <Box sx={{ mb: 4 }}>
              <BusinessIcon sx={{ fontSize: 80, mb: 2, opacity: 0.9 }} />
              <Typography variant="h2" component="h1" sx={{ fontWeight: 700, mb: 2 }}>
                Innexia
              </Typography>
              <Typography variant="h5" sx={{ opacity: 0.9, mb: 3 }}>
                Business Model Canvas
              </Typography>
              <Typography variant="body1" sx={{ opacity: 0.8, maxWidth: 400 }}>
                No se preocupe, le ayudaremos a recuperar el acceso a su cuenta de manera segura y rápida.
              </Typography>
            </Box>
            
            <Box sx={{ 
              display: 'flex', 
              flexDirection: 'column', 
              gap: 2,
              opacity: 0.8 
            }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Box sx={{ 
                  width: 8, 
                  height: 8, 
                  borderRadius: '50%', 
                  backgroundColor: 'white' 
                }} />
                <Typography variant="body2">Recuperación segura de contraseña</Typography>
              </Box>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Box sx={{ 
                  width: 8, 
                  height: 8, 
                  borderRadius: '50%', 
                  backgroundColor: 'white' 
                }} />
                <Typography variant="body2">Enlace enviado por correo electrónico</Typography>
              </Box>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Box sx={{ 
                  width: 8, 
                  height: 8, 
                  borderRadius: '50%', 
                  backgroundColor: 'white' 
                }} />
                <Typography variant="body2">Proceso simple y confiable</Typography>
              </Box>
            </Box>
          </Grid>

          {/* Right Side - Password Recovery Form */}
          <Grid 
            columns={{ xs: 12, md: 6 }} 
            sx={{ 
              display: 'flex',
              justifyContent: 'center',
              alignItems: 'center'
            }}
          >
            <Paper
              elevation={24}
              sx={{
                padding: { xs: 3, sm: 4, md: 5 },
                borderRadius: 3,
                width: '100%',
                maxWidth: 450,
                background: 'rgba(255, 255, 255, 0.95)',
                backdropFilter: 'blur(10px)',
                border: '1px solid rgba(255, 255, 255, 0.2)'
              }}
            >
              <Box sx={{ textAlign: 'center', mb: 4 }}>
                <Box
                  sx={{
                    backgroundColor: 'primary.main',
                    borderRadius: '50%',
                    width: 64,
                    height: 64,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    margin: '0 auto 16px',
                    boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)'
                  }}
                >
                  <EmailOutlined sx={{ color: 'white', fontSize: 32 }} />
                </Box>

                <Typography component="h1" variant="h4" gutterBottom sx={{ fontWeight: 600 }}>
                  Recuperar Contraseña
                </Typography>

                <Typography variant="body1" color="text.secondary">
                  Ingrese su correo electrónico para recibir el enlace de recuperación
                </Typography>
              </Box>

              {error && (
                <Alert severity="error" sx={{ width: '100%', mb: 3, borderRadius: 2 }}>
                  {error}
                </Alert>
              )}

              {message && (
                <Alert severity="success" sx={{ width: '100%', mb: 3, borderRadius: 2 }}>
                  {message}
                </Alert>
              )}

              <Box component="form" onSubmit={handleSubmit} sx={{ width: '100%' }}>
                <TextField
                  margin="normal"
                  required
                  fullWidth
                  id="email"
                  label="Correo Electrónico"
                  name="email"
                  type="email"
                  autoComplete="email"
                  autoFocus
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  disabled={loading}
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <EmailOutlined color="action" />
                      </InputAdornment>
                    ),
                  }}
                  sx={{
                    '& .MuiOutlinedInput-root': {
                      borderRadius: 2,
                      '&:hover fieldset': {
                        borderColor: 'primary.main',
                      },
                    },
                  }}
                />

                <Button
                  type="submit"
                  fullWidth
                  variant="contained"
                  sx={{ 
                    mt: 4, 
                    mb: 3, 
                    height: 52,
                    borderRadius: 2,
                    fontSize: '1.1rem',
                    fontWeight: 600,
                    textTransform: 'none',
                    boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)',
                    '&:hover': {
                      boxShadow: '0 12px 40px rgba(0, 0, 0, 0.15)',
                    }
                  }}
                  disabled={loading}
                >
                  {loading ? <CircularProgress size={24} /> : 'Enviar Enlace de Recuperación'}
                </Button>

                <Box sx={{ 
                  textAlign: 'center',
                  pt: 2,
                  borderTop: '1px solid',
                  borderColor: 'divider'
                }}>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                    ¿Recordó su contraseña?
                  </Typography>
                  <Link 
                    href="/login" 
                    variant="body1" 
                    underline="hover"
                    sx={{ 
                      color: 'primary.main',
                      fontWeight: 600,
                      '&:hover': {
                        color: 'primary.dark',
                      }
                    }}
                  >
                    Volver al inicio de sesión
                  </Link>
                </Box>
              </Box>
            </Paper>
          </Grid>
        </Grid>
      </Container>
    </Box>
  );
};

export default ForgotPasswordPage;

