import React, { useState, useEffect } from 'react';
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
  InputAdornment,
  IconButton,
  Select,
  MenuItem,
  FormControl,
  InputLabel
} from '@mui/material';
import { 
  LockOutlined, 
  PersonOutline, 
  Visibility, 
  VisibilityOff,
  Business as BusinessIcon
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import { InnexiaLogo } from '../components/InnexiaLogo';

const LoginPage: React.FC = () => {
  const [credentials, setCredentials] = useState({ 
    username: '', 
    password: '', 
    companyId: 1 // Por defecto Innexia
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [sessionExpiredMessage, setSessionExpiredMessage] = useState('');
  const { login } = useAuth();
  const navigate = useNavigate();

  // Verificar parámetros de URL para mensaje de sesión expirada
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const message = urlParams.get('message');
    const type = urlParams.get('type');
    
    if (type === 'session_expired' && message) {
      setSessionExpiredMessage(decodeURIComponent(message));
      // Limpiar la URL para evitar mostrar el mensaje en recargas
      window.history.replaceState({}, document.title, window.location.pathname);
    }
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setError('');
    setSessionExpiredMessage(''); // limpiar mensaje de sesión expirada al reintentar
    setLoading(true);

    try {
      await login(credentials);
      navigate('/dashboard');
    } catch (err) {
      setError('Credenciales inválidas. Intente nuevamente.');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement> | any) => {
    const name = e.target.name;
    const value = e.target.value;
    
    setCredentials({
      ...credentials,
      [name]: name === 'companyId' ? parseInt(value) : value
    });
  };

  const handleClickShowPassword = () => {
    setShowPassword(!showPassword);
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
              <InnexiaLogo 
                variant="full" 
                size="large" 
                color="custom"
              />
              <Typography variant="h5" sx={{ opacity: 0.9, mb: 3 }}>
                Business Model Canvas
              </Typography>
              <Typography variant="body1" sx={{ opacity: 0.8, maxWidth: 400 }}>
                Transforme sus ideas en modelos de negocio exitosos con nuestra plataforma inteligente de gestión empresarial.
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
                <Typography variant="body2">Gestión intuitiva de proyectos</Typography>
              </Box>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Box sx={{ 
                  width: 8, 
                  height: 8, 
                  borderRadius: '50%', 
                  backgroundColor: 'white' 
                }} />
                <Typography variant="body2">Análisis de modelos de negocio</Typography>
              </Box>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Box sx={{ 
                  width: 8, 
                  height: 8, 
                  borderRadius: '50%', 
                  backgroundColor: 'white' 
                }} />
                <Typography variant="body2">Seguimiento de actividades</Typography>
              </Box>
            </Box>
          </Grid>

          {/* Right Side - Login Form */}
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
                  <LockOutlined sx={{ color: 'white', fontSize: 32 }} />
                </Box>

                <Typography component="h1" variant="h4" gutterBottom sx={{ fontWeight: 600 }}>
                  Bienvenido de vuelta
                </Typography>

                <Typography variant="body1" color="text.secondary">
                  Ingrese sus credenciales para acceder
                </Typography>
              </Box>

              {sessionExpiredMessage && (
                <Alert 
                  severity="warning" 
                  sx={{ 
                    width: '100%', 
                    mb: 3, 
                    borderRadius: 2,
                    '& .MuiAlert-message': {
                      width: '100%'
                    }
                  }}
                  icon={
                    <Box
                      sx={{
                        width: 24,
                        height: 24,
                        borderRadius: '50%',
                        backgroundColor: 'warning.main',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        color: 'white',
                        fontSize: '14px',
                        fontWeight: 'bold'
                      }}
                    >
                      !
                    </Box>
                  }
                >
                  <Typography variant="body2" sx={{ fontWeight: 500 }}>
                    {sessionExpiredMessage}
                  </Typography>
                </Alert>
              )}

              {error && (
                <Alert severity="error" sx={{ width: '100%', mb: 3, borderRadius: 2 }}>
                  {error}
                </Alert>
              )}

              <Box component="form" onSubmit={handleSubmit} sx={{ width: '100%' }}>
                <TextField
                  margin="normal"
                  required
                  fullWidth
                  id="username"
                  label="Usuario"
                  name="username"
                  autoComplete="username"
                  autoFocus
                  value={credentials.username}
                  onChange={handleChange}
                  disabled={loading}
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <PersonOutline color="action" />
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
                
                <TextField
                  margin="normal"
                  required
                  fullWidth
                  name="password"
                  label="Contraseña"
                  type={showPassword ? 'text' : 'password'}
                  id="password"
                  autoComplete="current-password"
                  value={credentials.password}
                  onChange={handleChange}
                  disabled={loading}
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <LockOutlined color="action" />
                      </InputAdornment>
                    ),
                    endAdornment: (
                      <InputAdornment position="end">
                        <IconButton
                          aria-label="toggle password visibility"
                          onClick={handleClickShowPassword}
                          edge="end"
                        >
                          {showPassword ? <VisibilityOff /> : <Visibility />}
                        </IconButton>
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

                <FormControl
                  fullWidth
                  margin="normal"
                  disabled={loading}
                >
                  <InputLabel>Empresa</InputLabel>
                  <Select
                    name="companyId"
                    value={credentials.companyId}
                    onChange={handleChange}
                    label="Empresa"
                    startAdornment={
                      <InputAdornment position="start">
                        <BusinessIcon color="action" />
                      </InputAdornment>
                    }
                    sx={{
                      borderRadius: 2,
                      '&:hover .MuiOutlinedInput-notchedOutline': {
                        borderColor: 'primary.main',
                      },
                    }}
                  >
                    <MenuItem value={1}>Innexia</MenuItem>
                    <MenuItem value={2}>TechCorp</MenuItem>
                  </Select>
                </FormControl>

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
                  {loading ? <CircularProgress size={24} /> : 'Iniciar Sesión'}
                </Button>

                <Box sx={{ textAlign: 'center', mb: 2 }}>
                  <Link 
                    href="/forgot-password" 
                    variant="body2" 
                    underline="hover"
                    sx={{ 
                      color: 'primary.main',
                      fontWeight: 500,
                      '&:hover': {
                        color: 'primary.dark',
                      }
                    }}
                  >
                    ¿Olvidó su contraseña?
                  </Link>
                </Box>

                <Box sx={{ 
                  textAlign: 'center',
                  pt: 2,
                  borderTop: '1px solid',
                  borderColor: 'divider'
                }}>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                    ¿No tiene una cuenta?
                  </Typography>
                  <Link 
                    href="/register" 
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
                    Crear cuenta
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

export default LoginPage;

