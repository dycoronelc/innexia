import React, { useState, useEffect } from 'react';
import {
  Box,
  Drawer,
  AppBar,
  Toolbar,
  List,
  Typography,
  Divider,
  IconButton,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Collapse,
  Avatar,
  Menu,
  MenuItem,
  TextField,
  InputAdornment,
  useTheme as useMuiTheme,
  useMediaQuery,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  Select,
  Chip,
  Button
} from '@mui/material';
import {
  Menu as MenuIcon,
  Dashboard,
  Business,
  Category,
  LocalOffer,
  LocationOn,
  People,
  Security,
  AccountCircle,
  ExpandLess,
  ExpandMore,
  Search,
  FilterList,
  Logout,
  DarkMode,
  LightMode,
  Apps,
  Person,
  CalendarToday as CalendarIcon,
  School,
  Description,
  Analytics
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import { useTheme } from '../contexts/ThemeContext';
import { useNavigate, useLocation } from 'react-router-dom';
import { PWAInstallPrompt } from '../components/PWAInstallPrompt';
import { InnexiaLogo } from '../components/InnexiaLogo';
import { SidebarBrand } from '../components/SidebarBrand';

const drawerWidth = 260;
const collapsedDrawerWidth = 64;

interface MainLayoutProps {
  children: React.ReactNode;
}

const MainLayout: React.FC<MainLayoutProps> = ({ children }) => {
  const [mobileOpen, setMobileOpen] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [openSubmenus, setOpenSubmenus] = useState<{ [key: string]: boolean }>({
    academia: false,
    maestros: false,
    seguridad: false
  });
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filtersOpen, setFiltersOpen] = useState(false);
  const [showPWAInstall, setShowPWAInstall] = useState(true);
  const [activeFilters, setActiveFilters] = useState({
    dateRange: { start: '', end: '' },
    categories: [] as string[],
    tags: [] as string[],
    locations: [] as string[],
    assignees: [] as string[]
  });
  const { user, logout } = useAuth();
  const { mode, toggleTheme } = useTheme();
  const navigate = useNavigate();
  const location = useLocation();
  const themeMui = useMuiTheme();
  const isMobile = useMediaQuery(themeMui.breakpoints.down('md'));

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const handleSidebarToggle = () => {
    setSidebarOpen(!sidebarOpen);
  };

  // Auto-hide sidebar on small screens
  useEffect(() => {
    if (isMobile) {
      setSidebarOpen(false);
    }
  }, [isMobile]);

  // Keyboard shortcut to toggle sidebar (Ctrl/Cmd + B)
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if ((event.ctrlKey || event.metaKey) && event.key === 'b') {
        event.preventDefault();
        setSidebarOpen(prev => !prev);
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, []);

  const handleSubmenuToggle = (submenu: string) => {
    setOpenSubmenus(prev => ({
      ...prev,
      [submenu]: !prev[submenu]
    }));
  };

  const handleUserMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleUserMenuClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
    handleUserMenuClose();
  };

  const handleFiltersOpen = () => {
    setFiltersOpen(true);
  };

  const handleFiltersClose = () => {
    setFiltersOpen(false);
  };

  const handleApplyFilters = () => {
    // Aquí se aplicarían los filtros a la pantalla actual
    console.log('Filtros aplicados:', activeFilters);
    setFiltersOpen(false);
  };

  const handleClearFilters = () => {
    setActiveFilters({
      dateRange: { start: '', end: '' },
      categories: [],
      tags: [],
      locations: [],
      assignees: []
    });
  };

  const handlePWAInstallClose = () => {
    setShowPWAInstall(false);
  };

  const hasActiveFilters = () => {
    return (
      activeFilters.dateRange.start !== '' ||
      activeFilters.dateRange.end !== '' ||
      activeFilters.categories.length > 0 ||
      activeFilters.tags.length > 0 ||
      activeFilters.locations.length > 0 ||
      activeFilters.assignees.length > 0
    );
  };

  // Mock data for filter options
  const filterOptions = {
    categories: [
      { id: '1', name: 'Tecnología', color: '#2196F3' },
      { id: '2', name: 'Servicios', color: '#4CAF50' },
      { id: '3', name: 'Educación', color: '#FF9800' },
      { id: '4', name: 'Salud', color: '#F44336' },
      { id: '5', name: 'Finanzas', color: '#9C27B0' }
    ],
    tags: [
      { id: '1', name: 'E-commerce', color: '#2196F3' },
      { id: '2', name: 'SaaS', color: '#4CAF50' },
      { id: '3', name: 'B2B', color: '#FF9800' },
      { id: '4', name: 'Mobile', color: '#F44336' },
      { id: '5', name: 'AI', color: '#9C27B0' },
      { id: '6', name: 'Fintech', color: '#607D8B' }
    ],
    locations: [
      { id: '1', name: 'Bogotá, Colombia' },
      { id: '2', name: 'Medellín, Colombia' },
      { id: '3', name: 'Cali, Colombia' },
      { id: '4', name: 'Barranquilla, Colombia' },
      { id: '5', name: 'Cartagena, Colombia' }
    ],
    assignees: [
      { id: '1', name: 'Juan Pérez', username: 'juan.perez' },
      { id: '2', name: 'María García', username: 'maria.garcia' },
      { id: '3', name: 'Carlos Rodríguez', username: 'carlos.rodriguez' },
      { id: '4', name: 'Ana Martínez', username: 'ana.martinez' },
      { id: '5', name: 'Luis Hernández', username: 'luis.hernandez' }
    ]
  };

  const menuItems = [
    {
      text: 'Dashboard',
      icon: <Dashboard />,
      path: '/dashboard',
      onClick: () => navigate('/dashboard')
    },
    {
      text: 'Calendario',
      icon: <CalendarIcon />,
      path: '/calendar',
      onClick: () => navigate('/calendar')
    },
    {
      text: 'Proyectos',
      icon: <Business />,
      path: '/projects',
      onClick: () => navigate('/projects')
    },
    {
      text: 'Análisis de Datos',
      icon: <Analytics />,
      path: '/analytics',
      onClick: () => navigate('/analytics')
    },
    {
      text: 'Academia',
      icon: <School />,
      submenu: 'academia',
      children: [
        { text: 'Aprende', icon: <School />, path: '/learn' },
        { text: 'Gestión de Contenido', icon: <School />, path: '/content-management' },
        { text: 'Documentos Oficiales', icon: <Description />, path: '/documents' }
      ]
    },
    {
      text: 'Maestros',
      icon: <Apps />,
      submenu: 'maestros',
      children: [
        { text: 'Categorías', icon: <Category />, path: '/categories' },
        { text: 'Etiquetas', icon: <LocalOffer />, path: '/tags' },
        { text: 'Ubicaciones', icon: <LocationOn />, path: '/locations' }
      ]
    },
    {
      text: 'Seguridad',
      icon: <Security />,
      submenu: 'seguridad',
      children: [
        { text: 'Usuarios', icon: <People />, path: '/users' },
        { text: 'Bitácoras', icon: <Security />, path: '/audit-log' }
      ]
    }
  ];

  const drawer = (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Logo/Brand Section */}
      <Box sx={{ 
        borderBottom: '1px solid',
        borderColor: 'divider',
        backgroundColor: 'background.paper'
      }}>
        <SidebarBrand 
          isOpen={sidebarOpen}
          size="medium"
        />
      </Box>

      {/* Navigation Menu */}
      <Box sx={{ flexGrow: 1, overflow: 'auto' }}>
        <List sx={{ pt: 1 }}>
          {menuItems.map((item) => (
            <Box key={item.text}>
              {item.submenu ? (
                <>
                  <ListItem disablePadding>
                                         <ListItemButton 
                       onClick={() => handleSubmenuToggle(item.submenu!)}
                       sx={{
                         mx: 1,
                         borderRadius: 2,
                         mb: 0.5,
                         justifyContent: sidebarOpen ? 'flex-start' : 'center',
                         minHeight: 48,
                         '&:hover': {
                           backgroundColor: 'action.hover',
                         },
                         '&.Mui-selected': {
                           backgroundColor: 'primary.main',
                           color: 'primary.contrastText',
                           '&:hover': {
                             backgroundColor: 'primary.dark',
                           },
                         },
                       }}
                     >
                       <ListItemIcon sx={{ 
                         minWidth: sidebarOpen ? 40 : 0,
                         color: 'inherit'
                       }}>
                         {item.icon}
                       </ListItemIcon>
                       {sidebarOpen && (
                         <>
                           <ListItemText 
                             primary={item.text} 
                             primaryTypographyProps={{ 
                               fontSize: '0.875rem',
                               fontWeight: 500
                             }}
                           />
                           {openSubmenus[item.submenu!] ? <ExpandLess /> : <ExpandMore />}
                         </>
                       )}
                     </ListItemButton>
                  </ListItem>
                  {sidebarOpen && (
                    <Collapse in={openSubmenus[item.submenu!]} timeout="auto" unmountOnExit>
                    <List component="div" disablePadding>
                      {item.children?.map((child) => (
                        <ListItemButton
                          key={child.text}
                          sx={{ 
                            pl: 6, 
                            pr: 2,
                            mx: 1,
                            borderRadius: 2,
                            mb: 0.5,
                            '&:hover': {
                              backgroundColor: 'action.hover',
                            },
                            '&.Mui-selected': {
                              backgroundColor: 'primary.main',
                              color: 'primary.contrastText',
                              '&:hover': {
                                backgroundColor: 'primary.dark',
                              },
                            },
                          }}
                          onClick={() => navigate(child.path)}
                          selected={location.pathname === child.path}
                        >
                          <ListItemIcon sx={{ 
                            minWidth: 32,
                            color: 'inherit'
                          }}>
                            {child.icon}
                          </ListItemIcon>
                          <ListItemText 
                            primary={child.text} 
                            primaryTypographyProps={{ 
                              fontSize: '0.8rem'
                            }}
                          />
                        </ListItemButton>
                      ))}
                    </List>
                  </Collapse>
                  )}
                </>
              ) : (
                <ListItem disablePadding>
                                      <ListItemButton
                      onClick={item.onClick}
                      selected={location.pathname === item.path}
                      sx={{
                        mx: 1,
                        borderRadius: 2,
                        mb: 0.5,
                        justifyContent: sidebarOpen ? 'flex-start' : 'center',
                        minHeight: 48,
                        '&:hover': {
                          backgroundColor: 'action.hover',
                        },
                        '&.Mui-selected': {
                          backgroundColor: 'primary.main',
                          color: 'primary.contrastText',
                          '&:hover': {
                            backgroundColor: 'primary.dark',
                          },
                        },
                      }}
                    >
                      <ListItemIcon sx={{ 
                        minWidth: sidebarOpen ? 40 : 0,
                        color: 'inherit'
                      }}>
                        {item.icon}
                      </ListItemIcon>
                      {sidebarOpen && (
                        <ListItemText 
                          primary={item.text} 
                          primaryTypographyProps={{ 
                            fontSize: '0.875rem',
                            fontWeight: 500
                          }}
                        />
                      )}
                    </ListItemButton>
                </ListItem>
              )}
            </Box>
          ))}
        </List>
      </Box>

      {/* User Profile Section */}
      <Box sx={{ 
        p: 2, 
        borderTop: '1px solid',
        borderColor: 'divider',
        backgroundColor: 'background.paper',
        display: 'flex',
        justifyContent: sidebarOpen ? 'flex-start' : 'center'
      }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Avatar 
            sx={{ 
              width: 40, 
              height: 40, 
              background: 'linear-gradient(135deg, #4D2581 0%, #ED682B 100%)'
            }}
          >
            {user?.full_name?.charAt(0) || 'U'}
          </Avatar>
          {sidebarOpen && (
            <Box sx={{ flexGrow: 1, minWidth: 0 }}>
              <Typography variant="body2" sx={{ fontWeight: 600, fontSize: '0.875rem' }}>
                {user?.full_name || 'Usuario'}
              </Typography>
              <Typography variant="caption" color="text.secondary" sx={{ fontSize: '0.75rem' }}>
                {user?.role === 'admin' ? 'Administrador' : 'Usuario'}
              </Typography>
            </Box>
          )}
        </Box>
      </Box>
    </Box>
  );

  return (
    <Box sx={{ display: 'flex', height: '100vh', width: '100vw' }}>
      {/* App Bar */}
      <AppBar
        position="fixed"
        elevation={0}
        sx={{
          width: { sm: sidebarOpen ? `calc(100% - ${drawerWidth}px)` : `calc(100% - ${collapsedDrawerWidth}px)` },
          ml: { sm: sidebarOpen ? `${drawerWidth}px` : `${collapsedDrawerWidth}px` },
          backgroundColor: 'background.paper',
          borderBottom: '1px solid',
          borderColor: 'divider',
          color: 'text.primary',
          borderRadius: 0,
          transition: 'width 0.3s ease, margin-left 0.3s ease',
          zIndex: (theme) => theme.zIndex.drawer + 1
        }}
      >
        <Toolbar 
          sx={{ 
            minHeight: 64, 
            '&.MuiToolbar-root': {
              borderRadius: 0,
              paddingLeft: 0,
              paddingRight: 0
            }
          }}
        >
          {/* Mobile Menu Button */}
          <IconButton
            color="inherit"
            aria-label="open drawer"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ 
              mr: 2, 
              display: { sm: 'none' },
              ml: { sm: sidebarOpen ? '16px' : '16px' },
              transition: 'margin-left 0.3s ease'
            }}
          >
            <MenuIcon />
          </IconButton>

          {/* Desktop Sidebar Toggle Button */}
          <Tooltip title={`${sidebarOpen ? "Colapsar" : "Expandir"} barra lateral (Ctrl+B)`}>
            <IconButton
              color="inherit"
              aria-label="toggle sidebar"
              edge="start"
              onClick={handleSidebarToggle}
              sx={{ 
                mr: 2, 
                display: { xs: 'none', sm: 'flex' },
                backgroundColor: sidebarOpen ? 'action.hover' : 'transparent',
                '&:hover': {
                  backgroundColor: 'action.hover'
                },
                ml: { sm: sidebarOpen ? '16px' : '16px' },
                transition: 'margin-left 0.3s ease'
              }}
            >
              <MenuIcon />
            </IconButton>
          </Tooltip>



          {/* Search Bar */}
          <Box sx={{ flexGrow: 1, display: 'flex', alignItems: 'center', gap: 2 }}>
            <TextField
              size="small"
              placeholder="Buscar proyectos, categorías..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              sx={{
                minWidth: 300,
                '& .MuiOutlinedInput-root': {
                  borderRadius: 0,
                  backgroundColor: 'background.default',
                  '& fieldset': {
                    borderColor: 'divider',
                  },
                  '&:hover fieldset': {
                    borderColor: 'primary.main',
                  },
                  '&.Mui-focused fieldset': {
                    borderColor: 'primary.main',
                  },
                },
              }}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <Search sx={{ color: 'text.secondary', fontSize: 20 }} />
                  </InputAdornment>
                ),
              }}
            />
          </Box>

          {/* Right Side Actions */}
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            {/* Filters */}
            <Tooltip title="Filtros">
              <IconButton 
                color="inherit" 
                size="large"
                onClick={handleFiltersOpen}
                sx={{
                  color: hasActiveFilters() ? 'primary.main' : 'inherit',
                  '&:hover': {
                    backgroundColor: 'rgba(255, 255, 255, 0.1)',
                  }
                }}
              >
                <FilterList />
              </IconButton>
            </Tooltip>

            {/* Theme Toggle */}
            <Tooltip title={`Cambiar a modo ${mode === 'dark' ? 'claro' : 'oscuro'}`}>
              <IconButton color="inherit" size="large" onClick={toggleTheme}>
                {mode === 'dark' ? <LightMode /> : <DarkMode />}
              </IconButton>
            </Tooltip>

            {/* User Menu */}
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, ml: 2 }}>
              <Box sx={{ textAlign: 'right', display: { xs: 'none', sm: 'block' } }}>
                <Typography variant="body2" sx={{ fontWeight: 500, fontSize: '0.875rem' }}>
                  {user?.full_name}
                </Typography>
                <Typography variant="caption" color="text.secondary" sx={{ fontSize: '0.75rem' }}>
                  {user?.email}
                </Typography>
              </Box>
              <IconButton
                onClick={handleUserMenuOpen}
                sx={{ 
                  color: 'inherit',
                  border: '2px solid',
                  borderColor: 'divider',
                  '&:hover': {
                    borderColor: 'primary.main',
                  }
                }}
              >
                <Avatar sx={{ 
                  width: 36, 
                  height: 36,
                  background: 'linear-gradient(135deg, #4D2581 0%, #ED682B 100%)'
                }}>
                  {user?.full_name?.charAt(0) || 'U'}
                </Avatar>
              </IconButton>
            </Box>
          </Box>
        </Toolbar>
      </AppBar>

      {/* Sidebar */}
      <Box
        component="nav"
        sx={{ 
          width: { sm: sidebarOpen ? drawerWidth : collapsedDrawerWidth }, 
          flexShrink: { sm: 0 },
          transition: 'width 0.3s ease'
        }}
      >
        <Drawer
          variant="temporary"
          open={mobileOpen}
          onClose={handleDrawerToggle}
          ModalProps={{
            keepMounted: true,
          }}
          sx={{
            display: { xs: 'block', sm: 'none' },
            '& .MuiDrawer-paper': { 
              boxSizing: 'border-box', 
              width: drawerWidth,
              border: 'none'
            },
          }}
        >
          {drawer}
        </Drawer>
        <Drawer
          variant="permanent"
          sx={{
            display: { xs: 'none', sm: 'block' },
            '& .MuiDrawer-paper': { 
              boxSizing: 'border-box', 
              width: sidebarOpen ? drawerWidth : collapsedDrawerWidth,
              border: 'none',
              backgroundColor: 'background.paper',
              transition: 'width 0.3s ease',
              overflow: 'hidden',
              zIndex: (theme) => theme.zIndex.drawer
            },
          }}
          open
        >
          {drawer}
        </Drawer>
      </Box>

      {/* Main Content */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          width: { sm: sidebarOpen ? `calc(100% - ${drawerWidth}px)` : `calc(100% - ${collapsedDrawerWidth}px)` },
          mt: '64px',
          backgroundColor: 'background.default',
          minHeight: 'calc(100vh - 64px - 60px)',
          overflow: 'auto',
          display: 'flex',
          flexDirection: 'column',
          transition: 'all 0.3s ease'
        }}
      >
        <Box sx={{ flexGrow: 1 }}>
          {children}
        </Box>
        
        {/* Footer */}
        <Box
          component="footer"
          sx={{
            mt: 4,
            py: 2,
            px: 3,
            backgroundColor: 'background.paper',
            borderTop: '1px solid',
            borderColor: 'divider',
            textAlign: 'center'
          }}
        >
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 1 }}>
            <InnexiaLogo 
              size="small" 
              color="custom"
            />
            <Typography variant="body2" color="text.secondary">
              © {new Date().getFullYear()} Innexia. Todos los derechos reservados.
            </Typography>
          </Box>
        </Box>
      </Box>

      {/* User Menu Dropdown */}
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleUserMenuClose}
        onClick={handleUserMenuClose}
        transformOrigin={{ horizontal: 'right', vertical: 'top' }}
        anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
        PaperProps={{
          elevation: 8,
          sx: {
            mt: 1,
            minWidth: 200,
            borderRadius: 2,
            '& .MuiMenuItem-root': {
              py: 1.5,
              px: 2,
            }
          }
        }}
      >
        <MenuItem onClick={() => navigate('/profile')}>
          <AccountCircle sx={{ mr: 2, fontSize: 20 }} />
          Mi Perfil
        </MenuItem>
        <MenuItem onClick={toggleTheme}>
          {mode === 'dark' ? (
            <>
              <LightMode sx={{ mr: 2, fontSize: 20 }} />
              Modo Claro
            </>
          ) : (
            <>
              <DarkMode sx={{ mr: 2, fontSize: 20 }} />
              Modo Oscuro
            </>
          )}
        </MenuItem>
        <Divider />
        <MenuItem onClick={handleLogout} sx={{ color: 'error.main' }}>
          <Logout sx={{ mr: 2, fontSize: 20 }} />
          Cerrar Sesión
        </MenuItem>
      </Menu>

      {/* Filters Modal */}
      <Dialog 
        open={filtersOpen} 
        onClose={handleFiltersClose} 
        maxWidth="md" 
        fullWidth
        PaperProps={{
          sx: {
            borderRadius: 2,
            maxHeight: '90vh'
          }
        }}
      >
        <DialogTitle sx={{ 
          display: 'flex', 
          alignItems: 'center', 
          gap: 1,
          borderBottom: '1px solid',
          borderColor: 'divider'
        }}>
          <FilterList color="primary" />
          Filtros
        </DialogTitle>
        
        <DialogContent sx={{ pt: 3 }}>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
            {/* Rango de Fechas */}
            <Box>
              <Typography variant="subtitle1" sx={{ mb: 2, fontWeight: 600 }}>
                Rango de Fechas
              </Typography>
              <Box sx={{ display: 'flex', gap: 2, flexDirection: { xs: 'column', sm: 'row' } }}>
                <TextField
                  label="Fecha Inicio"
                  type="date"
                  value={activeFilters.dateRange.start}
                  onChange={(e) => setActiveFilters(prev => ({
                    ...prev,
                    dateRange: { ...prev.dateRange, start: e.target.value }
                  }))}
                  InputLabelProps={{ shrink: true }}
                  fullWidth
                  size="medium"
                  sx={{
                    '& .MuiOutlinedInput-root': {
                      borderRadius: 2,
                    }
                  }}
                />
                <TextField
                  label="Fecha Fin"
                  type="date"
                  value={activeFilters.dateRange.end}
                  onChange={(e) => setActiveFilters(prev => ({
                    ...prev,
                    dateRange: { ...prev.dateRange, end: e.target.value }
                  }))}
                  InputLabelProps={{ shrink: true }}
                  fullWidth
                  size="medium"
                  sx={{
                    '& .MuiOutlinedInput-root': {
                      borderRadius: 2,
                    }
                  }}
                />
              </Box>
            </Box>

            {/* Categorías */}
            <Box>
              <Typography variant="subtitle1" sx={{ mb: 2, fontWeight: 600 }}>
                Categorías
              </Typography>
              <FormControl fullWidth>
                <Select
                  multiple
                  value={activeFilters.categories}
                  onChange={(e) => setActiveFilters(prev => ({
                    ...prev,
                    categories: e.target.value as string[]
                  }))}
                  renderValue={(selected) => (
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                      {selected.map((value) => (
                        <Chip key={value} label={value} size="small" />
                      ))}
                    </Box>
                  )}
                  size="medium"
                  sx={{
                    '& .MuiOutlinedInput-root': {
                      borderRadius: 2,
                    }
                  }}
                >
                  {filterOptions.categories.map((category) => (
                    <MenuItem key={category.id} value={category.name}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Box
                          sx={{
                            width: 16,
                            height: 16,
                            borderRadius: '50%',
                            backgroundColor: category.color,
                            border: '1px solid #ddd'
                          }}
                        />
                        {category.name}
                      </Box>
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Box>

            {/* Etiquetas */}
            <Box>
              <Typography variant="subtitle1" sx={{ mb: 2, fontWeight: 600 }}>
                Etiquetas
              </Typography>
              <FormControl fullWidth>
                <Select
                  multiple
                  value={activeFilters.tags}
                  onChange={(e) => setActiveFilters(prev => ({
                    ...prev,
                    tags: e.target.value as string[]
                  }))}
                  renderValue={(selected) => (
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                      {selected.map((value) => (
                        <Chip key={value} label={value} size="small" />
                      ))}
                    </Box>
                  )}
                  size="medium"
                  sx={{
                    '& .MuiOutlinedInput-root': {
                      borderRadius: 2,
                    }
                  }}
                >
                  {filterOptions.tags.map((tag) => (
                    <MenuItem key={tag.id} value={tag.name}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Box
                          sx={{
                            width: 16,
                            height: 16,
                            borderRadius: '50%',
                            backgroundColor: tag.color,
                            border: '1px solid #ddd'
                          }}
                        />
                        {tag.name}
                      </Box>
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Box>

            {/* Ubicaciones */}
            <Box>
              <Typography variant="subtitle1" sx={{ mb: 2, fontWeight: 600 }}>
                Ubicaciones
              </Typography>
              <FormControl fullWidth>
                <Select
                  multiple
                  value={activeFilters.locations}
                  onChange={(e) => setActiveFilters(prev => ({
                    ...prev,
                    locations: e.target.value as string[]
                  }))}
                  renderValue={(selected) => (
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                      {selected.map((value) => (
                        <Chip key={value} label={value} size="small" />
                      ))}
                    </Box>
                  )}
                  size="medium"
                  sx={{
                    '& .MuiOutlinedInput-root': {
                      borderRadius: 2,
                    }
                  }}
                >
                  {filterOptions.locations.map((location) => (
                    <MenuItem key={location.id} value={location.name}>
                      {location.name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Box>

            {/* Responsables */}
            <Box>
              <Typography variant="subtitle1" sx={{ mb: 2, fontWeight: 600 }}>
                Responsables
              </Typography>
              <FormControl fullWidth>
                <Select
                  multiple
                  value={activeFilters.assignees}
                  onChange={(e) => setActiveFilters(prev => ({
                    ...prev,
                    assignees: e.target.value as string[]
                  }))}
                  renderValue={(selected) => (
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                      {selected.map((value) => (
                        <Chip key={value} label={value} size="small" />
                      ))}
                    </Box>
                  )}
                  size="medium"
                  sx={{
                    '& .MuiOutlinedInput-root': {
                      borderRadius: 2,
                    }
                  }}
                >
                  {filterOptions.assignees.map((assignee) => (
                    <MenuItem key={assignee.id} value={assignee.name}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Person color="primary" fontSize="small" />
                        <Typography variant="body2">
                          {assignee.name}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          ({assignee.username})
                        </Typography>
                      </Box>
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Box>
          </Box>
        </DialogContent>

        <DialogActions sx={{ 
          px: 3, 
          py: 2, 
          borderTop: '1px solid', 
          borderColor: 'divider',
          gap: 2
        }}>
          <Button 
            onClick={handleClearFilters}
            variant="outlined"
            color="secondary"
            sx={{ borderRadius: 2 }}
          >
            Limpiar Filtros
          </Button>
          <Box sx={{ flexGrow: 1 }} />
          <Button 
            onClick={handleFiltersClose}
            variant="outlined"
            sx={{ borderRadius: 2 }}
          >
            Cerrar
          </Button>
          <Button 
            onClick={handleApplyFilters}
            variant="contained"
            sx={{ borderRadius: 2 }}
          >
            Aplicar Filtros
          </Button>
        </DialogActions>
      </Dialog>
      
      {/* PWA Install Prompt */}
      {showPWAInstall && (
        <PWAInstallPrompt onClose={handlePWAInstallClose} />
      )}
    </Box>
  );
};

export default MainLayout;

