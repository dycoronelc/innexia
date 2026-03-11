import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Chip,
  Button,
  TextField,
  InputAdornment,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  IconButton,
  Tooltip,
  Avatar,
  Divider,
  Skeleton,
  Alert,
  Tabs,
  Tab,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Link,
  useTheme
} from '@mui/material';
import {
  Search,
  FilterList,
  Bookmark,
  BookmarkBorder,
  Share,
  OpenInNew,
  Refresh,
  TrendingUp,
  Business,
  Computer,
  AttachMoney,
  Campaign,
  BusinessCenter,
  RssFeed,
  AccessTime,
  Person,
  Favorite,
  FavoriteBorder,
  KeyboardArrowDown
} from '@mui/icons-material';

interface NewsItem {
  id: string;
  title: string;
  description: string;
  content: string;
  url: string;
  imageUrl: string;
  source: string;
  author: string;
  publishDate: string;
  category: string;
  tags: string[];
  isBookmarked: boolean;
  isFavorite: boolean;
  readTime: string;
}

interface NewsFeedProps {
  onBookmarkToggle?: (itemId: string) => void;
  onFavoriteToggle?: (itemId: string) => void;
}

const NewsFeed: React.FC<NewsFeedProps> = ({
  onBookmarkToggle,
  onFavoriteToggle
}) => {
  const theme = useTheme();
  const [newsItems, setNewsItems] = useState<NewsItem[]>([]);
  const [filteredNews, setFilteredNews] = useState<NewsItem[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [selectedSource, setSelectedSource] = useState('all');
  const [currentTab, setCurrentTab] = useState(0);
  const [loading, setLoading] = useState(true);
  const [selectedNews, setSelectedNews] = useState<NewsItem | null>(null);
  const [showNewsDialog, setShowNewsDialog] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Mock data - En producción esto vendría de RSS feeds reales
  const mockNewsItems: NewsItem[] = [
    {
      id: '1',
      title: 'Nuevas Tendencias en Emprendimiento Digital para 2024',
      description: 'Descubre las estrategias más efectivas que están transformando el panorama empresarial este año.',
      content: 'El emprendimiento digital continúa evolucionando a un ritmo acelerado. Las empresas que adoptan tecnologías emergentes como IA, blockchain y automatización están viendo resultados extraordinarios...',
      url: 'https://example.com/news/1',
      imageUrl: 'https://images.unsplash.com/photo-1551434678-e076c223a692?w=400&h=200&fit=crop&crop=center',
      source: 'Emprendedor Digital',
      author: 'María González',
      publishDate: '2024-01-15T10:30:00Z',
      category: 'tendencias',
      tags: ['Emprendimiento', 'Digital', 'Tendencias', '2024'],
      isBookmarked: false,
      isFavorite: false,
      readTime: '5 min'
    },
    {
      id: '2',
      title: 'Cómo las Startups Latinoamericanas Están Revolucionando la Fintech',
      description: 'Un análisis profundo del ecosistema fintech en América Latina y sus innovaciones más disruptivas.',
      content: 'América Latina se ha convertido en un hub de innovación fintech. Las startups de la región están desarrollando soluciones únicas que abordan problemas específicos del mercado local...',
      url: 'https://example.com/news/2',
      imageUrl: 'https://images.unsplash.com/photo-1554224155-6726b3ff858f?w=400&h=200&fit=crop&crop=center',
      source: 'TechCrunch',
      author: 'Carlos Mendoza',
      publishDate: '2024-01-14T15:45:00Z',
      category: 'fintech',
      tags: ['Fintech', 'Startups', 'Latinoamérica', 'Innovación'],
      isBookmarked: true,
      isFavorite: false,
      readTime: '8 min'
    },
    {
      id: '3',
      title: 'Guía Completa: Validación de Ideas de Negocio en 5 Pasos',
      description: 'Metodología probada para validar tu idea de negocio antes de invertir tiempo y recursos.',
      content: 'La validación de ideas es crucial para el éxito de cualquier emprendimiento. Este proceso te ayuda a confirmar que tu producto o servicio resuelve un problema real del mercado...',
      url: 'https://example.com/news/3',
      imageUrl: 'https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=400&h=200&fit=crop&crop=center',
      source: 'Harvard Business Review',
      author: 'Ana Rodríguez',
      publishDate: '2024-01-13T09:15:00Z',
      category: 'estrategia',
      tags: ['Validación', 'Ideas', 'Negocio', 'Metodología'],
      isBookmarked: false,
      isFavorite: true,
      readTime: '12 min'
    },
    {
      id: '4',
      title: 'El Impacto de la IA en la Gestión de Proyectos Empresariales',
      description: 'Cómo la inteligencia artificial está transformando la forma en que las empresas gestionan sus proyectos.',
      content: 'La inteligencia artificial está revolucionando la gestión de proyectos. Desde la planificación hasta la ejecución, las herramientas de IA están mejorando la eficiencia y precisión...',
      url: 'https://example.com/news/4',
      imageUrl: 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400&h=200&fit=crop&crop=center',
      source: 'MIT Technology Review',
      author: 'Roberto Silva',
      publishDate: '2024-01-12T14:20:00Z',
      category: 'tecnologia',
      tags: ['IA', 'Gestión', 'Proyectos', 'Tecnología'],
      isBookmarked: true,
      isFavorite: false,
      readTime: '6 min'
    },
    {
      id: '5',
      title: 'Estrategias de Marketing Digital que Funcionan en 2024',
      description: 'Las tácticas de marketing digital más efectivas para conectar con tu audiencia este año.',
      content: 'El marketing digital evoluciona constantemente. Las estrategias que funcionaban hace un año pueden no ser tan efectivas hoy. Es crucial mantenerse actualizado con las últimas tendencias...',
      url: 'https://example.com/news/5',
      imageUrl: 'https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=400&h=200&fit=crop&crop=center',
      source: 'Marketing Week',
      author: 'Laura Fernández',
      publishDate: '2024-01-11T11:30:00Z',
      category: 'marketing',
      tags: ['Marketing', 'Digital', 'Estrategias', '2024'],
      isBookmarked: false,
      isFavorite: true,
      readTime: '7 min'
    },
    {
      id: '6',
      title: 'Financiamiento Alternativo para Startups: Más Allá del Venture Capital',
      description: 'Explora opciones de financiamiento innovadoras que están ganando popularidad entre emprendedores.',
      content: 'El venture capital no es la única opción para financiar tu startup. Nuevas formas de financiamiento están emergiendo, ofreciendo alternativas más flexibles y accesibles...',
      url: 'https://example.com/news/6',
      imageUrl: 'https://images.unsplash.com/photo-1559136555-9303baea8ebd?w=400&h=200&fit=crop&crop=center',
      source: 'Forbes',
      author: 'Patricia López',
      publishDate: '2024-01-10T16:45:00Z',
      category: 'finanzas',
      tags: ['Financiamiento', 'Startups', 'Venture Capital', 'Alternativas'],
      isBookmarked: true,
      isFavorite: false,
      readTime: '9 min'
    },
    {
      id: '7',
      title: 'Design Thinking: La Metodología que Está Cambiando la Innovación',
      description: 'Cómo las empresas más exitosas están usando Design Thinking para crear productos revolucionarios.',
      content: 'Design Thinking se ha convertido en la metodología de innovación más adoptada por empresas de todos los tamaños. Esta aproximación centrada en el usuario está generando resultados extraordinarios...',
      url: 'https://example.com/news/7',
      imageUrl: 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400&h=200&fit=crop&crop=center',
      source: 'Innovation Weekly',
      author: 'Dr. María González',
      publishDate: '2024-01-09T08:15:00Z',
      category: 'innovacion',
      tags: ['Design Thinking', 'Innovación', 'Metodología', 'UX'],
      isBookmarked: false,
      isFavorite: true,
      readTime: '10 min'
    },
    {
      id: '8',
      title: 'Mindset Emprendedor: Los Hábitos de los Fundadores Exitosos',
      description: 'Descubre los patrones mentales y hábitos que distinguen a los emprendedores más exitosos.',
      content: 'El éxito empresarial no solo depende de una buena idea o financiamiento. Los emprendedores más exitosos comparten ciertos patrones mentales y hábitos que los distinguen del resto...',
      url: 'https://example.com/news/8',
      imageUrl: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&h=200&fit=crop&crop=center',
      source: 'Psychology Today',
      author: 'Ana Rodríguez',
      publishDate: '2024-01-08T12:30:00Z',
      category: 'psicologia',
      tags: ['Mindset', 'Emprendimiento', 'Hábitos', 'Éxito'],
      isBookmarked: true,
      isFavorite: false,
      readTime: '8 min'
    },
    {
      id: '9',
      title: 'Escalabilidad Empresarial: Preparando tu Negocio para el Crecimiento',
      description: 'Estrategias probadas para escalar tu empresa de manera sostenible y eficiente.',
      content: 'La escalabilidad es uno de los desafíos más grandes que enfrentan los emprendedores. Preparar tu negocio para el crecimiento requiere planificación estratégica y ejecución cuidadosa...',
      url: 'https://example.com/news/9',
      imageUrl: 'https://images.unsplash.com/photo-1559136555-9303baea8ebd?w=400&h=200&fit=crop&crop=center',
      source: 'Business Growth',
      author: 'Carlos Mendoza',
      publishDate: '2024-01-07T14:45:00Z',
      category: 'estrategia',
      tags: ['Escalabilidad', 'Crecimiento', 'Estrategia', 'Empresa'],
      isBookmarked: false,
      isFavorite: true,
      readTime: '11 min'
    },
    {
      id: '10',
      title: 'Liderazgo Ágil: Construyendo Equipos de Alto Rendimiento',
      description: 'Cómo los líderes modernos están adaptando sus estilos para equipos más productivos.',
      content: 'El liderazgo tradicional está siendo reemplazado por enfoques más ágiles y adaptativos. Los líderes modernos están desarrollando nuevas habilidades para gestionar equipos distribuidos y diversos...',
      url: 'https://example.com/news/10',
      imageUrl: 'https://images.unsplash.com/photo-1522071820081-009f0129c71c?w=400&h=200&fit=crop&crop=center',
      source: 'Leadership Today',
      author: 'Patricia López',
      publishDate: '2024-01-06T09:20:00Z',
      category: 'liderazgo',
      tags: ['Liderazgo', 'Equipos', 'Productividad', 'Ágil'],
      isBookmarked: true,
      isFavorite: false,
      readTime: '9 min'
    },
    {
      id: '11',
      title: 'Innovación Disruptiva: Creando Mercados Completamente Nuevos',
      description: 'Casos de estudio de empresas que crearon industrias enteras desde cero.',
      content: 'La innovación disruptiva va más allá de mejorar productos existentes. Las empresas más visionarias están creando mercados completamente nuevos, cambiando la forma en que vivimos y trabajamos...',
      url: 'https://example.com/news/11',
      imageUrl: 'https://images.unsplash.com/photo-1518709268805-4e9042af2176?w=400&h=200&fit=crop&crop=center',
      source: 'Innovation Hub',
      author: 'Roberto Silva',
      publishDate: '2024-01-05T16:10:00Z',
      category: 'innovacion',
      tags: ['Innovación', 'Disrupción', 'Mercados', 'Casos de Estudio'],
      isBookmarked: false,
      isFavorite: true,
      readTime: '13 min'
    },
    {
      id: '12',
      title: 'Gestión del Tiempo para Emprendedores: Técnicas que Realmente Funcionan',
      description: 'Métodos probados para maximizar la productividad y equilibrar vida personal y profesional.',
      content: 'Los emprendedores enfrentan desafíos únicos en la gestión del tiempo. Entre múltiples responsabilidades y decisiones constantes, encontrar técnicas efectivas de productividad es crucial...',
      url: 'https://example.com/news/12',
      imageUrl: 'https://images.unsplash.com/photo-1611224923853-80b023f02d71?w=400&h=200&fit=crop&crop=center',
      source: 'Productivity Pro',
      author: 'Laura Fernández',
      publishDate: '2024-01-04T11:45:00Z',
      category: 'productividad',
      tags: ['Productividad', 'Gestión del Tiempo', 'Emprendimiento', 'Equilibrio'],
      isBookmarked: true,
      isFavorite: false,
      readTime: '7 min'
    }
  ];

  const categories = [
    { value: 'all', label: 'Todas', icon: <RssFeed /> },
    { value: 'tendencias', label: 'Tendencias', icon: <TrendingUp /> },
    { value: 'fintech', label: 'Fintech', icon: <AttachMoney /> },
    { value: 'estrategia', label: 'Estrategia', icon: <Business /> },
    { value: 'tecnologia', label: 'Tecnología', icon: <Computer /> },
    { value: 'marketing', label: 'Marketing', icon: <Campaign /> },
    { value: 'finanzas', label: 'Finanzas', icon: <AttachMoney /> },
    { value: 'innovacion', label: 'Innovación', icon: <TrendingUp /> },
    { value: 'psicologia', label: 'Crecimiento Personal', icon: <BusinessCenter /> },
    { value: 'liderazgo', label: 'Liderazgo', icon: <BusinessCenter /> },
    { value: 'productividad', label: 'Productividad', icon: <BusinessCenter /> }
  ];

  const sources = [
    { value: 'all', label: 'Todas las fuentes' },
    { value: 'Emprendedor Digital', label: 'Emprendedor Digital' },
    { value: 'TechCrunch', label: 'TechCrunch' },
    { value: 'Harvard Business Review', label: 'Harvard Business Review' },
    { value: 'MIT Technology Review', label: 'MIT Technology Review' },
    { value: 'Marketing Week', label: 'Marketing Week' },
    { value: 'Forbes', label: 'Forbes' },
    { value: 'Innovation Weekly', label: 'Innovation Weekly' },
    { value: 'Psychology Today', label: 'Psychology Today' },
    { value: 'Business Growth', label: 'Business Growth' },
    { value: 'Leadership Today', label: 'Leadership Today' },
    { value: 'Innovation Hub', label: 'Innovation Hub' },
    { value: 'Productivity Pro', label: 'Productivity Pro' }
  ];

  const tabs = [
    { label: 'Últimas Noticias', value: 0 },
    { label: 'Más Leídas', value: 1 },
    { label: 'Tendencias', value: 2 },
    { label: 'Mis Guardadas', value: 3 }
  ];

  useEffect(() => {
    // Simular carga de datos
    setTimeout(() => {
      setNewsItems(mockNewsItems);
      setFilteredNews(mockNewsItems);
      setLoading(false);
    }, 1000);
  }, []);

  useEffect(() => {
    const filtered = newsItems.filter(item => {
      const matchesSearch = item.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           item.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           item.tags.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()));
      
      const matchesCategory = selectedCategory === 'all' || item.category === selectedCategory;
      const matchesSource = selectedSource === 'all' || item.source === selectedSource;

      return matchesSearch && matchesCategory && matchesSource;
    });

    setFilteredNews(filtered);
  }, [newsItems, searchTerm, selectedCategory, selectedSource]);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setCurrentTab(newValue);
  };

  const handleBookmarkToggle = (itemId: string) => {
    setNewsItems(prev => prev.map(item => 
      item.id === itemId ? { ...item, isBookmarked: !item.isBookmarked } : item
    ));
    onBookmarkToggle?.(itemId);
  };

  const handleFavoriteToggle = (itemId: string) => {
    setNewsItems(prev => prev.map(item => 
      item.id === itemId ? { ...item, isFavorite: !item.isFavorite } : item
    ));
    onFavoriteToggle?.(itemId);
  };

  const handleNewsClick = (item: NewsItem) => {
    setSelectedNews(item);
    setShowNewsDialog(true);
  };

  const handleRefresh = () => {
    setLoading(true);
    setTimeout(() => {
      setLoading(false);
    }, 1000);
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInHours = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60));
    
    if (diffInHours < 1) return 'Hace menos de 1 hora';
    if (diffInHours < 24) return `Hace ${diffInHours} horas`;
    if (diffInHours < 48) return 'Ayer';
    return date.toLocaleDateString();
  };

  if (loading) {
    return (
      <Box>
        <Grid container spacing={3}>
          {[1, 2, 3, 4, 5, 6].map((item) => (
            <Grid size={{ xs: 12, md: 6 }} key={item}>
              <Card>
                <CardContent>
                  <Skeleton variant="text" width="80%" height={32} />
                  <Skeleton variant="text" width="60%" height={20} />
                  <Skeleton variant="text" width="100%" height={16} />
                  <Skeleton variant="text" width="100%" height={16} />
                  <Skeleton variant="text" width="40%" height={16} />
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Box>
    );
  }

  return (
    <Box>
             {/* Header */}
       <Box sx={{ mb: 3 }}>
         <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
           <Typography variant="h4" component="h2" sx={{ fontWeight: 'bold' }}>
             Noticias de Emprendimiento e Innovación
           </Typography>
           <Tooltip title="Actualizar noticias">
             <IconButton onClick={handleRefresh}>
               <Refresh />
             </IconButton>
           </Tooltip>
         </Box>
         
         {error && (
           <Alert severity="error" sx={{ mb: 2 }}>
             {error}
           </Alert>
         )}
       </Box>

       {/* Udemy-style Header with Filters */}
       <Box sx={{ mb: 4 }}>
         {/* Single Row with Filters and Search */}
         <Box sx={{ 
           display: 'flex', 
           alignItems: 'center', 
           gap: { xs: 2, sm: 3 },
           flexWrap: 'wrap',
           justifyContent: 'space-between'
         }}>
           {/* Left side - Filters */}
           <Box sx={{ 
             display: 'flex', 
             alignItems: 'center', 
             gap: { xs: 1, sm: 2 },
             flexWrap: 'wrap',
             flexGrow: 1
           }}>
             <Typography variant="body2" color="text.secondary" sx={{ fontWeight: 500 }}>
               Ordenar por:
             </Typography>
             <Button
               variant="contained"
               size="small"
               endIcon={<KeyboardArrowDown />}
               sx={{ 
                 backgroundColor: 'primary.main',
                 color: 'white',
                 '&:hover': { backgroundColor: 'primary.dark' }
               }}
             >
               Más recientes
             </Button>
             <Button
               variant="outlined"
               size="small"
               endIcon={<KeyboardArrowDown />}
               sx={{ borderColor: 'grey.300' }}
             >
               Categorías
             </Button>
             <Button
               variant="text"
               size="small"
               sx={{ color: 'text.secondary' }}
             >
               Restablecer
             </Button>
           </Box>
           
           {/* Right side - Search */}
           <Box sx={{ 
             display: 'flex', 
             gap: 1,
             minWidth: { xs: '100%', sm: 250 },
             maxWidth: { sm: 350 },
             flexShrink: 0
           }}>
             <TextField
               fullWidth
               placeholder="Buscar noticias"
               value={searchTerm}
               onChange={(e) => setSearchTerm(e.target.value)}
               size="small"
               sx={{ 
                 '& .MuiOutlinedInput-root': {
                   backgroundColor: 'white',
                   '&:hover': {
                     '& .MuiOutlinedInput-notchedOutline': {
                       borderColor: 'primary.main',
                     }
                   }
                 }
               }}
             />
             <IconButton
               sx={{ 
                 backgroundColor: 'primary.main',
                 color: 'white',
                 '&:hover': { backgroundColor: 'primary.dark' }
               }}
             >
               <Search />
             </IconButton>
           </Box>
         </Box>
       </Box>

      {/* Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={currentTab} onChange={handleTabChange}>
          {tabs.map((tab) => (
            <Tab key={tab.value} label={tab.label} />
          ))}
        </Tabs>
      </Box>

             {/* News Grid - CSS Grid Style */}
       <Box sx={{
         display: 'grid',
         gridTemplateColumns: {
           xs: '1fr',
           sm: '1fr',
           md: 'repeat(2, 1fr)',
           lg: 'repeat(3, 1fr)',
           xl: 'repeat(4, 1fr)'
         },
         gap: { xs: 2, sm: 3, md: 3 },
         width: '100%'
       }}>
         {filteredNews.map((item) => (
           <Box key={item.id} sx={{ width: '100%' }}>
            <Card 
              sx={{ 
                height: '100%',
                display: 'flex', 
                flexDirection: 'column',
                transition: 'all 0.2s ease-in-out',
                border: '1px solid',
                borderColor: 'grey.200',
                '&:hover': {
                  transform: 'translateY(-2px)',
                  boxShadow: theme.shadows[4],
                  cursor: 'pointer'
                }
              }}
              onClick={() => handleNewsClick(item)}
            >
              {/* Image with Menu */}
              <Box sx={{ position: 'relative' }}>
                <img
                  src={item.imageUrl}
                  alt={item.title}
                  style={{
                    width: '100%',
                    height: 200,
                    objectFit: 'cover'
                  }}
                />
                <Box sx={{ 
                  position: 'absolute', 
                  top: 8, 
                  right: 8, 
                  display: 'flex', 
                  gap: 1 
                }}>
                  <Tooltip title={item.isBookmarked ? 'Quitar de guardados' : 'Guardar'}>
                    <IconButton
                      size="small"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleBookmarkToggle(item.id);
                      }}
                      sx={{ backgroundColor: 'rgba(255,255,255,0.9)' }}
                    >
                      {item.isBookmarked ? <Bookmark color="primary" /> : <BookmarkBorder />}
                    </IconButton>
                  </Tooltip>
                  <Tooltip title={item.isFavorite ? 'Quitar de favoritos' : 'Agregar a favoritos'}>
                    <IconButton
                      size="small"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleFavoriteToggle(item.id);
                      }}
                      sx={{ backgroundColor: 'rgba(255,255,255,0.9)' }}
                    >
                      {item.isFavorite ? <Favorite color="error" /> : <FavoriteBorder />}
                    </IconButton>
                  </Tooltip>
                </Box>
              </Box>
              
              <CardContent sx={{ 
                p: 2, 
                display: 'flex', 
                flexDirection: 'column',
                flexGrow: 1,
                justifyContent: 'space-between'
              }}>
                {/* Top Section */}
                <Box>
                  {/* Source and Date */}
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                    <Chip 
                      label={item.source} 
                      size="small" 
                      variant="outlined"
                      sx={{ fontSize: '0.7rem' }}
                    />
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, ml: 'auto' }}>
                      <AccessTime sx={{ fontSize: 14 }} />
                      <Typography variant="caption" color="text.secondary">
                        {formatDate(item.publishDate)}
                      </Typography>
                    </Box>
                  </Box>
                  
                  {/* Title - Altura fija */}
                  <Typography variant="h6" component="h3" sx={{ 
                    fontSize: '1rem', 
                    fontWeight: 600,
                    lineHeight: 1.3,
                    display: '-webkit-box',
                    WebkitLineClamp: 2,
                    WebkitBoxOrient: 'vertical',
                    overflow: 'hidden',
                    height: '2.6em',
                    mb: 1
                  }}>
                    {item.title}
                  </Typography>
                  
                  {/* Description - Altura fija */}
                  <Typography variant="body2" color="text.secondary" sx={{ 
                    mb: 2,
                    display: '-webkit-box',
                    WebkitLineClamp: 3,
                    WebkitBoxOrient: 'vertical',
                    overflow: 'hidden',
                    height: '4.5em'
                  }}>
                    {item.description}
                  </Typography>

                  {/* Author and Read Time - Altura fija */}
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2, height: '1.2em' }}>
                    <Person sx={{ fontSize: 16 }} />
                    <Typography variant="caption" color="text.secondary">
                      {item.author}
                    </Typography>
                    <Typography variant="caption" color="text.secondary" sx={{ ml: 'auto' }}>
                      {item.readTime}
                    </Typography>
                  </Box>
                </Box>
                
                {/* Bottom Section */}
                <Box sx={{ 
                  display: 'flex', 
                  alignItems: 'center', 
                  justifyContent: 'space-between',
                  height: '2rem'
                }}>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                    {item.tags.slice(0, 2).map((tag) => (
                      <Chip 
                        key={tag} 
                        label={tag} 
                        size="small" 
                        variant="outlined"
                        sx={{ fontSize: '0.7rem' }}
                      />
                    ))}
                    {item.tags.length > 2 && (
                      <Chip 
                        label={`+${item.tags.length - 2}`} 
                        size="small" 
                        variant="outlined"
                        sx={{ fontSize: '0.7rem' }}
                      />
                    )}
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Box>
        ))}
      </Box>

      {/* Empty State */}
      {filteredNews.length === 0 && (
        <Box sx={{ textAlign: 'center', py: 8 }}>
          <RssFeed sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
          <Typography variant="h6" color="text.secondary" gutterBottom>
            No se encontraron noticias
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Intenta ajustar los filtros o buscar con otros términos
          </Typography>
        </Box>
      )}

      {/* News Dialog */}
      <Dialog 
        open={showNewsDialog} 
        onClose={() => setShowNewsDialog(false)}
        maxWidth="md"
        fullWidth
      >
        {selectedNews && (
          <>
            <DialogTitle>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <Typography variant="h6">{selectedNews.title}</Typography>
              </Box>
            </DialogTitle>
            <DialogContent>
              <Box sx={{ mb: 2 }}>
                <img 
                  src={selectedNews.imageUrl} 
                  alt={selectedNews.title}
                  style={{ width: '100%', height: 250, objectFit: 'cover', borderRadius: 8 }}
                />
              </Box>
              <Typography variant="body1" paragraph>
                {selectedNews.content}
              </Typography>
              <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                {selectedNews.tags.map((tag) => (
                  <Chip key={tag} label={tag} size="small" />
                ))}
              </Box>
              <Divider sx={{ my: 2 }} />
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                  <Avatar>{selectedNews.author.split(' ').map(n => n[0]).join('')}</Avatar>
                  <Box>
                    <Typography variant="body2" fontWeight={500}>{selectedNews.author}</Typography>
                    <Typography variant="caption" color="text.secondary">
                      {selectedNews.source} • {formatDate(selectedNews.publishDate)}
                    </Typography>
                  </Box>
                </Box>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Typography variant="caption" color="text.secondary">
                    {selectedNews.readTime}
                  </Typography>
                </Box>
              </Box>
            </DialogContent>
            <DialogActions>
              <Button onClick={() => setShowNewsDialog(false)}>Cerrar</Button>
              <Button 
                variant="contained" 
                startIcon={<OpenInNew />}
                component={Link}
                href={selectedNews.url}
                target="_blank"
              >
                Leer Completo
              </Button>
            </DialogActions>
          </>
        )}
      </Dialog>
    </Box>
  );
};

export default NewsFeed;
