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
  InputAdornment,
  IconButton
} from '@mui/material';
import { 
  PersonAddOutlined, 
  PersonOutline, 
  EmailOutlined, 
  LockOutlined,
  Visibility, 
  VisibilityOff,
  Business as BusinessIcon
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';

const RegisterPage: React.FC = () => {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
    fullName: ''
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (formData.password !== formData.confirmPassword) {
      setError('Las contraseñas no coinciden');
      return;
    }

    if (formData.password.length < 6) {
      setError('La contraseña debe tener al menos 6 caracteres');
      return;
    }

    setLoading(true);

    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // In a real app, this would create the user account
      navigate('/login');
    } catch (err) {
      setError('Error al crear la cuenta. Intente nuevamente.');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleClickShowPassword = () => {
    setShowPassword(!showPassword);
  };

  const handleClickShowConfirmPassword = () => {
    setShowConfirmPassword(!showConfirmPassword);
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
                Únase a nuestra comunidad de emprendedores y transforme sus ideas en modelos de negocio exitosos.
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
                <Typography variant="body2">Acceso completo a la plataforma</Typography>
              </Box>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Box sx={{ 
                  width: 8, 
                  height: 8, 
                  borderRadius: '50%', 
                  backgroundColor: 'white' 
                }} />
                <Typography variant="body2">Herramientas profesionales de BMC</Typography>
              </Box>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Box sx={{ 
                  width: 8, 
                  height: 8, 
                  borderRadius: '50%', 
                  backgroundColor: 'white' 
                }} />
                <Typography variant="body2">Soporte y recursos exclusivos</Typography>
              </Box>
            </Box>
          </Grid>

          {/* Right Side - Registration Form */}
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
                maxWidth: 500,
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
                  <PersonAddOutlined sx={{ color: 'white', fontSize: 32 }} />
                </Box>

                <Typography component="h1" variant="h4" gutterBottom sx={{ fontWeight: 600 }}>
                  Crear Cuenta
                </Typography>

                <Typography variant="body1" color="text.secondary">
                  Únase a Innexia y comience su viaje empresarial
                </Typography>
              </Box>

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
                  id="fullName"
                  label="Nombre Completo"
                  name="fullName"
                  autoComplete="name"
                  autoFocus
                  value={formData.fullName}
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
                  id="username"
                  label="Usuario"
                  name="username"
                  autoComplete="username"
                  value={formData.username}
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
                  id="email"
                  label="Correo Electrónico"
                  name="email"
                  type="email"
                  autoComplete="email"
                  value={formData.email}
                  onChange={handleChange}
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

                <TextField
                  margin="normal"
                  required
                  fullWidth
                  name="password"
                  label="Contraseña"
                  type={showPassword ? 'text' : 'password'}
                  id="password"
                  autoComplete="new-password"
                  value={formData.password}
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

                <TextField
                  margin="normal"
                  required
                  fullWidth
                  name="confirmPassword"
                  label="Confirmar Contraseña"
                  type={showConfirmPassword ? 'text' : 'password'}
                  id="confirmPassword"
                  value={formData.confirmPassword}
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
                          aria-label="toggle confirm password visibility"
                          onClick={handleClickShowConfirmPassword}
                          edge="end"
                        >
                          {showConfirmPassword ? <VisibilityOff /> : <Visibility />}
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
                  {loading ? <CircularProgress size={24} /> : 'Crear Cuenta'}
                </Button>

                <Box sx={{ 
                  textAlign: 'center',
                  pt: 2,
                  borderTop: '1px solid',
                  borderColor: 'divider'
                }}>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                    ¿Ya tiene una cuenta?
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
                    Iniciar sesión
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

export default RegisterPage;

