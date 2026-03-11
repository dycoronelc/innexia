import React, { useState, useEffect } from 'react';
import { useTheme } from '@mui/material/styles';
import {
  Box,
  Container,
  Typography,
  Card,
  CardContent,
  CardMedia,
  CardActions,
  Button,
  Chip,
  TextField,
  InputAdornment,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Tabs,
  Tab,
  IconButton,
  Tooltip,
  Badge,
  Avatar,
  Rating,
  Divider,
  Alert,
  Skeleton,
  Fab,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Snackbar,
  CircularProgress
} from '@mui/material';
import {
  Search,
  FilterList,
  Bookmark,
  BookmarkBorder,
  PlayArrow,
  ReadMore,
  School,
  Business,
  TrendingUp,
  Lightbulb,
  Psychology,
  AttachMoney,
  Campaign,
  Group,
  Timeline,
  Star,
  AccessTime,
  Person,
  Share,
  Favorite,
  FavoriteBorder,
  RssFeed,
  KeyboardArrowDown,
  MoreVert,
  Visibility,
  ThumbUp,
  BookmarkAdd
} from '@mui/icons-material';

import { useAuth } from '../contexts/AuthContext';
import { educationalContentService } from '../services/api';
import { newsFeedService } from '../services/newsFeedService';
import type { NewsArticle } from '../services/newsFeedService';

interface ContentItem {
  id: number;
  title: string;
  description: string;
  content_type: 'article' | 'video' | 'podcast' | 'course' | 'news';
  content_source: 'internal' | 'rss_feed' | 'youtube' | 'vimeo' | 'spotify' | 'custom_api';
  source_url?: string;
  content_data?: any;
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  duration_minutes?: number;
  author?: string;
  instructor?: string;
  thumbnail_url?: string;
  tags?: string[];
  categories?: string[];
  status: 'draft' | 'published' | 'archived' | 'moderation';
  published_at?: string;
  created_at: string;
  updated_at: string;
  created_by: number;
  moderated_by?: number;
  moderation_notes?: string;
  view_count: number;
  like_count: number;
  bookmark_count: number;
  rating: number;
  rating_count: number;
}

const LearnPage: React.FC = () => {
  const theme = useTheme();
  const { token } = useAuth();
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [selectedDifficulty, setSelectedDifficulty] = useState('all');
  const [selectedType, setSelectedType] = useState('all');
  const [currentTab, setCurrentTab] = useState(0);
  const [showFilters, setShowFilters] = useState(false);
  const [loading, setLoading] = useState(false);
  const [selectedContent, setSelectedContent] = useState<ContentItem | null>(null);
  const [showContentDialog, setShowContentDialog] = useState(false);
  const [showPlayer, setShowPlayer] = useState(false);
  const [activeSection, setActiveSection] = useState<'all' | 'video' | 'podcast' | 'article' | 'course' | 'news'>('all');
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const [contentItems, setContentItems] = useState<ContentItem[]>([]);
  const [newsArticles, setNewsArticles] = useState<NewsArticle[]>([]);
  const [newsLoading, setNewsLoading] = useState(false);

  // Función para extraer ID de video de YouTube
  const extractYouTubeVideoId = (url: string): string | null => {
    const regExp = /^.*(youtu.be\/|v\/|u\/\w\/|embed\/|watch\?v=|&v=)([^#&?]*).*/;
    const match = url.match(regExp);
    const videoId = (match && match[2].length === 11) ? match[2] : null;
    return videoId;
  };

  // Función para extraer ID de video de Vimeo
  const extractVimeoVideoId = (url: string): string | null => {
    const regExp = /(?:vimeo)\.com.*(?:videos|video|channels|)\/([\d]+)/;
    const match = url.match(regExp);
    return match ? match[1] : null;
  };

  // Función para extraer ID y tipo de podcast de Spotify
  const extractSpotifyId = (url: string): { id: string; type: 'episode' | 'show' } | null => {
    const regExp = /spotify\.com\/(episode|show)\/([a-zA-Z0-9]+)/;
    const match = url.match(regExp);
    if (match) {
      return {
        type: match[1] as 'episode' | 'show',
        id: match[2]
      };
    }
    return null;
  };

  // Función para generar imagen automática basada en el contenido
  const generateContentImage = (item: ContentItem): string => {
    // Si ya tiene thumbnail_url, usarla
    if (item.thumbnail_url) {
      return item.thumbnail_url;
    }

    // Generar imagen única basada en el ID del contenido, tipo y título
    const contentId = item.id;
    const titleHash = item.title.split('').reduce((a, b) => {
      a = ((a << 5) - a) + b.charCodeAt(0);
      return a & a;
    }, 0);
    
    // Usar una combinación del ID y hash del título para mayor variación
    const uniqueSeed = Math.abs(contentId + titleHash);
    
    const typeImages = {
      video: [
        'https://images.unsplash.com/photo-1611224923853-80b023f02d71?w=400&h=225&fit=crop&crop=center',
        'https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=400&h=225&fit=crop&crop=center',
        'https://images.unsplash.com/photo-1593720213428-28a5b9e94613?w=400&h=225&fit=crop&crop=center',
        'https://images.unsplash.com/photo-1581833971358-2c8b550f87b3?w=400&h=225&fit=crop&crop=center',
        'https://images.unsplash.com/photo-1522202176988-66273c2fd55f?w=400&h=225&fit=crop&crop=center'
      ],
      podcast: [
        'https://images.unsplash.com/photo-1478737270239-2f02b77fc618?w=400&h=225&fit=crop&crop=center',
        'https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?w=400&h=225&fit=crop&crop=center',
        'https://images.unsplash.com/photo-1583394838336-acd977736f90?w=400&h=225&fit=crop&crop=center',
        'https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?w=400&h=225&fit=crop&crop=center',
        'https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=400&h=225&fit=crop&crop=center'
      ],
      article: [
        'https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=400&h=225&fit=crop&crop=center',
        'https://images.unsplash.com/photo-1434030216411-0b793f4b4173?w=400&h=225&fit=crop&crop=center',
        'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&h=225&fit=crop&crop=center',
        'https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=400&h=225&fit=crop&crop=center',
        'https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=400&h=225&fit=crop&crop=center'
      ],
      news: [
        'https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=400&h=225&fit=crop&crop=center',
        'https://images.unsplash.com/photo-1585829365295-ab7cd400c167?w=400&h=225&fit=crop&crop=center',
        'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&h=225&fit=crop&crop=center',
        'https://images.unsplash.com/photo-1434030216411-0b793f4b4173?w=400&h=225&fit=crop&crop=center',
        'https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=400&h=225&fit=crop&crop=center'
      ],
      course: [
        'https://images.unsplash.com/photo-1522202176988-66273c2fd55f?w=400&h=225&fit=crop&crop=center',
        'https://images.unsplash.com/photo-1513475382585-d06e58bcb0e0?w=400&h=225&fit=crop&crop=center',
        'https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=225&fit=crop&crop=center',
        'https://images.unsplash.com/photo-1515187029135-18ee286d815b?w=400&h=225&fit=crop&crop=center',
        'https://images.unsplash.com/photo-1522202176988-66273c2fd55f?w=400&h=225&fit=crop&crop=center'
      ],
    };

    const typeImagesArray = typeImages[item.content_type] || typeImages.article;
    const imageIndex = uniqueSeed % typeImagesArray.length;
    
    return typeImagesArray[imageIndex];
  };

  // Cargar contenido desde la API
  const fetchContent = async () => {
    if (!token) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const filters = {
        search: searchTerm || undefined,
        content_type: selectedType !== 'all' ? selectedType : undefined,
        difficulty: selectedDifficulty !== 'all' ? selectedDifficulty : undefined,
        status: 'published', // Solo mostrar contenido publicado
        limit: 50,
        offset: 0
      };

      const response = await educationalContentService.getContent(filters, token);
      
      if (response.status === 'success' && response.data) {
        setContentItems(response.data);
      } else {
        setError('Error al cargar el contenido');
      }
    } catch (error) {
      console.error('Error fetching content:', error);
      setError('Error al cargar el contenido');
    } finally {
      setLoading(false);
    }
  };

  // Función para cargar noticias desde RSS
  const fetchNews = async () => {
    if (!token) return;
    
    setNewsLoading(true);
    try {
      const response = await newsFeedService.getNews({ limit: 50 }, token);
      
      if (response.status === 'success') {
        const data = (response as { data?: unknown }).data;
        const articlesData = Array.isArray(data) ? data : (data && typeof data === 'object' && 'data' in data ? (data as { data: unknown[] }).data : []);
        setNewsArticles((Array.isArray(articlesData) ? articlesData : []) as import('../services/newsFeedService').NewsArticle[]);
      }
    } catch (error) {
      console.error('Error fetching news:', error);
    } finally {
      setNewsLoading(false);
    }
  };

  useEffect(() => {
    fetchContent();
  }, [token, searchTerm, selectedType, selectedDifficulty]);

  useEffect(() => {
    fetchNews();
  }, [token]);

  const categories = [
    { value: 'all', label: 'Todos', icon: <School /> },
    { value: 'Estrategia de Negocio', label: 'Estrategia de Negocio', icon: <Business /> },
    { value: 'Marketing Digital', label: 'Marketing Digital', icon: <Campaign /> },
    { value: 'Finanzas', label: 'Finanzas', icon: <AttachMoney /> },
    { value: 'Liderazgo', label: 'Liderazgo', icon: <Group /> },
    { value: 'Innovación', label: 'Innovación', icon: <Lightbulb /> },
    { value: 'Crecimiento Personal', label: 'Crecimiento Personal', icon: <Psychology /> },
    { value: 'Tecnología', label: 'Tecnología', icon: <TrendingUp /> },
    { value: 'Emprendimiento', label: 'Emprendimiento', icon: <School /> },
    { value: 'Productividad', label: 'Productividad', icon: <Timeline /> },
    { value: 'Ventas', label: 'Ventas', icon: <AttachMoney /> }
  ];

  const difficulties = [
    { value: 'all', label: 'Todos los niveles' },
    { value: 'beginner', label: 'Principiante' },
    { value: 'intermediate', label: 'Intermedio' },
    { value: 'advanced', label: 'Avanzado' }
  ];

  const types = [
    { value: 'all', label: 'Todos los tipos' },
    { value: 'article', label: 'Artículos' },
    { value: 'video', label: 'Videos' },
    { value: 'podcast', label: 'Podcasts' },
    { value: 'infographic', label: 'Infografías' }
  ];

  const tabs = [
    { label: 'Recomendados', value: 0 },
    { label: 'Más Populares', value: 1 },
    { label: 'Recientes', value: 2 },
    { label: 'Mis Favoritos', value: 3 }
  ];

  const sectionTabs = [
    { label: 'Todos los Contenidos', value: 'all', icon: <School /> },
    { label: 'Videos', value: 'video', icon: <PlayArrow /> },
    { label: 'Podcasts', value: 'podcast', icon: <PlayArrow /> },
    { label: 'Artículos', value: 'article', icon: <ReadMore /> },
    { label: 'Cursos', value: 'course', icon: <School /> },
    { label: 'Noticias', value: 'news', icon: <RssFeed /> }
  ];

  const filteredContent = contentItems.filter(item => {
    const matchesSearch = item.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         item.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         (item.tags && item.tags.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase())));
    
    const matchesCategory = selectedCategory === 'all' || 
                           (item.categories && item.categories.includes(selectedCategory));
    const matchesDifficulty = selectedDifficulty === 'all' || item.difficulty === selectedDifficulty;
    const matchesType = selectedType === 'all' || item.content_type === selectedType;
    
    // Filtro por sección activa
    const matchesSection = activeSection === 'all' || 
                          (activeSection === 'news' ? false : item.content_type === activeSection);

    return matchesSearch && matchesCategory && matchesDifficulty && matchesType && matchesSection;
  });


  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setCurrentTab(newValue);
  };

  const handleBookmarkToggle = async (itemId: number) => {
    // Aquí iría la lógica para manejar bookmarks en el backend
    // Por ahora solo actualizamos el estado local
    setContentItems(prev => prev.map(item => 
      item.id === itemId ? { ...item, bookmark_count: item.bookmark_count + 1 } : item
    ));
    setSuccess('Contenido agregado a favoritos');
  };

  const handleLikeToggle = async (itemId: number) => {
    // Aquí iría la lógica para manejar likes en el backend
    // Por ahora solo actualizamos el estado local
    setContentItems(prev => prev.map(item => 
      item.id === itemId ? { ...item, like_count: item.like_count + 1 } : item
    ));
    setSuccess('¡Gracias por tu like!');
  };

  const handleContentClick = (item: ContentItem) => {
    setSelectedContent(item);
    setShowContentDialog(true);
    
    // Para videos y podcasts, activar el reproductor automáticamente si hay source_url
    if ((item.content_type === 'video' || item.content_type === 'podcast') && item.source_url) {
      setShowPlayer(true);
    } else {
      setShowPlayer(false);
    }
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'beginner': return 'success';
      case 'intermediate': return 'warning';
      case 'advanced': return 'error';
      default: return 'default';
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'video': return <PlayArrow />;
      case 'podcast': return <PlayArrow />;
      case 'article': return <ReadMore />;
      case 'course': return <School />;
      case 'news': return <RssFeed />;
      default: return <School />;
    }
  };

  const handleSectionChange = (section: 'all' | 'video' | 'podcast' | 'article' | 'course' | 'news') => {
    setActiveSection(section);
  };

  return (
    <Container maxWidth={false} sx={{ py: 3, px: { xs: 2, sm: 3, md: 4 } }}>
      {/* Header Section */}
      <Box sx={{ mb: 4 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
          <School sx={{ fontSize: 40, color: 'primary.main' }} />
          <Typography variant="h3" component="h1" sx={{ fontWeight: 'bold' }}>
            Aprende
          </Typography>
        </Box>
        <Typography variant="h6" color="text.secondary" sx={{ mb: 3 }}>
          Cursos especializados en emprendimiento, innovación y crecimiento personal para impulsar tu negocio
        </Typography>
      </Box>

      {/* Section Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs 
          value={activeSection} 
          onChange={(e, newValue) => handleSectionChange(newValue)}
          variant="scrollable"
          scrollButtons="auto"
        >
          {sectionTabs.map((tab) => (
            <Tab 
              key={tab.value} 
              label={tab.label} 
              value={tab.value}
              icon={tab.icon}
              iconPosition="start"
            />
          ))}
        </Tabs>
      </Box>

             {/* Content Section */}
       {activeSection !== 'news' && (
         <>
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
                    Visitados recientemente
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
                    placeholder="Buscar mis cursos"
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

          {/* Content Tabs */}
          <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
            <Tabs value={currentTab} onChange={handleTabChange}>
              {tabs.map((tab) => (
                <Tab key={tab.value} label={tab.label} />
              ))}
            </Tabs>
          </Box>
        </>
      )}

                                                       {/* Content Grid - CSS Grid Style */}
         {(activeSection === 'all' || activeSection === 'video' || activeSection === 'article' || activeSection === 'course') && (
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
             {filteredContent.map((item) => (
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
                  onClick={() => handleContentClick(item)}
                >
                 {/* Image with Menu */}
                 <Box sx={{ position: 'relative' }}>
                                       <CardMedia
                      component="img"
                      height="200"
                      image={generateContentImage(item)}
                      alt={item.title}
                      sx={{ objectFit: 'cover', flexShrink: 0 }}
                    />
                   <IconButton
                     sx={{
                       position: 'absolute',
                       top: 8,
                       right: 8,
                       backgroundColor: 'rgba(255,255,255,0.9)',
                       '&:hover': { backgroundColor: 'rgba(255,255,255,1)' }
                     }}
                     onClick={(e) => {
                       e.stopPropagation();
                       // Handle menu
                     }}
                   >
                     <MoreVert />
                   </IconButton>
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
                      
                      {/* Author - Altura fija */}
                      <Typography variant="body2" color="text.secondary" sx={{ 
                        fontSize: '0.875rem',
                        height: '1.2em',
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                        whiteSpace: 'nowrap',
                        mb: 2
                      }}>
                        {item.author || item.instructor || 'Autor no especificado'}
                      </Typography>
                      
                      {/* Duration and Stats - Altura fija */}
                      <Box sx={{ mb: 2 }}>
                        <Box sx={{ 
                          display: 'flex', 
                          justifyContent: 'space-between', 
                          alignItems: 'center',
                          mb: 0.5
                        }}>
                          <Typography variant="caption" color="text.secondary">
                            {item.duration_minutes ? `${item.duration_minutes} min` : 'Duración no especificada'}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {item.view_count} vistas
                          </Typography>
                        </Box>
                        <Box sx={{ 
                          display: 'flex', 
                          justifyContent: 'space-between', 
                          alignItems: 'center'
                        }}>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <ThumbUp sx={{ fontSize: 14, color: 'text.secondary' }} />
                            <Typography variant="caption" color="text.secondary">
                              {item.like_count}
                            </Typography>
                          </Box>
                          {item.rating > 0 && (
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                              <Star sx={{ fontSize: 14, color: 'warning.main' }} />
                              <Typography variant="caption" color="text.secondary">
                                {item.rating.toFixed(1)}
                              </Typography>
                            </Box>
                          )}
                        </Box>
                      </Box>
                    </Box>
                    
                    {/* Bottom Section */}
                    <Box sx={{ 
                      display: 'flex', 
                      alignItems: 'center', 
                      justifyContent: 'space-between',
                      height: '2rem'
                    }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <IconButton
                          size="small"
                          onClick={(e) => {
                            e.stopPropagation();
                            handleLikeToggle(item.id);
                          }}
                        >
                          <ThumbUp sx={{ fontSize: 16 }} />
                        </IconButton>
                        <IconButton
                          size="small"
                          onClick={(e) => {
                            e.stopPropagation();
                            handleBookmarkToggle(item.id);
                          }}
                        >
                          <BookmarkAdd sx={{ fontSize: 16 }} />
                        </IconButton>
                      </Box>
                      <Button
                        variant="contained"
                        size="small"
                        sx={{ 
                          backgroundColor: 'primary.main',
                          color: 'white',
                          fontSize: '0.75rem',
                          '&:hover': { backgroundColor: 'primary.dark' }
                        }}
                      >
                        {item.content_type === 'video' || item.content_type === 'podcast' ? 'VER' : 'LEER'}
                      </Button>
                    </Box>
                  </CardContent>
                               </Card>
              </Box>
            ))}
          </Box>
       )}

      {/* Podcasts Section */}
      {activeSection === 'podcast' && (
        <Box>
          <Typography variant="h5" gutterBottom sx={{ mb: 3 }}>
            🎧 Podcasts Disponibles
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
            Descubre contenido de audio especializado en emprendimiento e innovación
          </Typography>
          {/* Mostrar contenidos de podcast filtrados */}
          {filteredContent.length > 0 ? (
            <Box sx={{ 
              display: 'grid', 
              gridTemplateColumns: { xs: '1fr', sm: 'repeat(2, 1fr)', md: 'repeat(3, 1fr)' },
              gap: 3 
            }}>
              {filteredContent.map((item) => (
                <Card 
                  key={item.id}
                  sx={{ 
                    cursor: 'pointer',
                    transition: 'all 0.2s ease',
                    '&:hover': {
                      transform: 'translateY(-4px)',
                      boxShadow: 4
                    }
                  }}
                  onClick={() => handleContentClick(item)}
                >
                  <CardMedia
                    component="img"
                    height="200"
                    image={generateContentImage(item)}
                    alt={item.title}
                    sx={{ objectFit: 'cover', flexShrink: 0 }}
                  />
                  <CardContent>
                    <Typography variant="h6" component="h3" gutterBottom sx={{ 
                      fontWeight: 'bold',
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                      display: '-webkit-box',
                      WebkitLineClamp: 2,
                      WebkitBoxOrient: 'vertical'
                    }}>
                      {item.title}
                    </Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                      {item.description}
                    </Typography>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                      <Typography variant="caption" color="text.secondary">
                        {item.author || 'Autor desconocido'}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {item.duration_minutes} min
                      </Typography>
                    </Box>
                    <Button 
                      variant="contained" 
                      fullWidth
                      startIcon={<PlayArrow />}
                      onClick={(e) => {
                        e.stopPropagation();
                        handleContentClick(item);
                      }}
                    >
                      REPRODUCIR
                    </Button>
                  </CardContent>
                </Card>
              ))}
            </Box>
          ) : (
            <Box sx={{ textAlign: 'center', py: 8 }}>
              <PlayArrow sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
              <Typography variant="h6" color="text.secondary" gutterBottom>
                No hay podcasts disponibles
              </Typography>
              <Typography variant="body2" color="text.secondary">
                No hay contenido de podcast disponible en este momento
              </Typography>
            </Box>
          )}
        </Box>
      )}

      {/* Empty State for Content Section */}
      {activeSection !== 'news' && filteredContent.length === 0 && (
        <Box sx={{ textAlign: 'center', py: 8 }}>
          {activeSection === 'all' ? (
            <School sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
          ) : activeSection === 'video' ? (
            <PlayArrow sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
          ) : activeSection === 'podcast' ? (
            <PlayArrow sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
          ) : activeSection === 'article' ? (
            <ReadMore sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
          ) : (
            <School sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
          )}
          <Typography variant="h6" color="text.secondary" gutterBottom>
            {activeSection === 'all' ? 'No se encontró contenido' :
             activeSection === 'video' ? 'No hay videos disponibles' :
             activeSection === 'podcast' ? 'No hay podcasts disponibles' :
             activeSection === 'article' ? 'No hay artículos disponibles' :
             activeSection === 'course' ? 'No hay cursos disponibles' :
             activeSection === 'news' ? 'No hay noticias disponibles' :
             'No se encontró contenido'}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {activeSection === 'all' ? 'Intenta ajustar los filtros o buscar con otros términos' :
             'No hay contenido de este tipo disponible en este momento'}
          </Typography>
        </Box>
      )}

      {/* News Section */}
      {activeSection === 'news' && (
        <Box>
          <Typography variant="h5" gutterBottom sx={{ mb: 3, fontWeight: 'bold' }}>
            📰 Noticias de Emprendimiento e Innovación
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
            Mantente actualizado con las últimas noticias del ecosistema emprendedor
          </Typography>
          
          {newsLoading ? (
            <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', sm: 'repeat(2, 1fr)', md: 'repeat(3, 1fr)' }, gap: 3 }}>
              {[1, 2, 3, 4, 5, 6].map((i) => (
                <Card key={i}>
                  <Skeleton variant="rectangular" height={200} />
                  <CardContent>
                    <Skeleton variant="text" width="80%" />
                    <Skeleton variant="text" width="60%" />
                    <Skeleton variant="text" width="90%" />
                  </CardContent>
                </Card>
              ))}
            </Box>
          ) : newsArticles.length > 0 ? (
            <Box sx={{ 
              display: 'grid', 
              gridTemplateColumns: { xs: '1fr', sm: 'repeat(2, 1fr)', md: 'repeat(3, 1fr)' },
              gap: 3 
            }}>
              {newsArticles.map((article, index) => (
                <Card 
                  key={index}
                  sx={{ 
                    cursor: 'pointer',
                    transition: 'all 0.2s ease',
                    '&:hover': {
                      transform: 'translateY(-4px)',
                      boxShadow: 4
                    }
                  }}
                  onClick={() => window.open(article.url, '_blank')}
                >
                  <CardMedia
                    component="img"
                    height="200"
                    image={article.image_url || 'https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=400&h=225&fit=crop&crop=center'}
                    alt={article.title}
                    sx={{ objectFit: 'cover', flexShrink: 0 }}
                  />
                  <CardContent>
                    <Chip 
                      label={article.category || 'General'} 
                      size="small" 
                      sx={{ mb: 1 }}
                      color="primary"
                      variant="outlined"
                    />
                    <Typography variant="h6" component="h3" gutterBottom sx={{ 
                      fontWeight: 'bold',
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                      display: '-webkit-box',
                      WebkitLineClamp: 2,
                      WebkitBoxOrient: 'vertical',
                      minHeight: '3em'
                    }}>
                      {article.title}
                    </Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ 
                      mb: 2,
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                      display: '-webkit-box',
                      WebkitLineClamp: 3,
                      WebkitBoxOrient: 'vertical',
                      minHeight: '4.5em'
                    }}>
                      {article.description}
                    </Typography>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                      <Typography variant="caption" color="text.secondary">
                        {article.source}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {new Date(article.published_date).toLocaleDateString()}
                      </Typography>
                    </Box>
                    <Button 
                      variant="outlined" 
                      fullWidth
                      startIcon={<RssFeed />}
                      onClick={(e) => {
                        e.stopPropagation();
                        window.open(article.url, '_blank');
                      }}
                    >
                      LEER NOTICIA
                    </Button>
                  </CardContent>
                </Card>
              ))}
            </Box>
          ) : (
            <Box sx={{ textAlign: 'center', py: 8 }}>
              <RssFeed sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
              <Typography variant="h6" color="text.secondary" gutterBottom>
                No hay noticias disponibles
              </Typography>
              <Typography variant="body2" color="text.secondary">
                No se pudieron cargar las noticias en este momento
              </Typography>
            </Box>
          )}
        </Box>
      )}

      {/* Content Dialog */}
      <Dialog 
        open={showContentDialog} 
        onClose={() => setShowContentDialog(false)}
        maxWidth="md"
        fullWidth
      >
        {selectedContent && (
          <>
            <DialogTitle>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                {getTypeIcon(selectedContent.content_type)}
                <Typography variant="h6">{selectedContent.title}</Typography>
              </Box>
            </DialogTitle>
            <DialogContent>
              {/* Reproductor integrado o imagen */}
              {showPlayer && selectedContent.source_url ? (
                <Box sx={{ mb: 2, position: 'relative', paddingBottom: '56.25%', height: 0, overflow: 'hidden' }}>
                  {selectedContent.content_source === 'youtube' ? (
                    (() => {
                      const videoId = extractYouTubeVideoId(selectedContent.source_url);
                      return videoId ? (
                        <iframe
                          src={`https://www.youtube.com/embed/${videoId}?autoplay=1&rel=0&modestbranding=1&playsinline=1`}
                          title={selectedContent.title}
                          style={{
                            position: 'absolute',
                            top: 0,
                            left: 0,
                            width: '100%',
                            height: '100%',
                            border: 0,
                            borderRadius: 8
                          }}
                          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
                          allowFullScreen
                        />
                      ) : (
                        <Box sx={{ 
                          position: 'absolute', 
                          top: 0, 
                          left: 0, 
                          width: '100%', 
                          height: '100%', 
                          display: 'flex', 
                          alignItems: 'center', 
                          justifyContent: 'center',
                          backgroundColor: '#f5f5f5',
                          borderRadius: 8
                        }}>
                          <Typography variant="body2" color="text.secondary">
                            No se pudo cargar el video. 
                            <Button 
                              size="small" 
                              onClick={() => window.open(selectedContent.source_url, '_blank')}
                            >
                              Abrir en YouTube
                            </Button>
                          </Typography>
                        </Box>
                      );
                    })()
                  ) : selectedContent.content_source === 'vimeo' ? (
                    <iframe
                      src={`https://player.vimeo.com/video/${extractVimeoVideoId(selectedContent.source_url)}?autoplay=1`}
                      title={selectedContent.title}
                      style={{
                        position: 'absolute',
                        top: 0,
                        left: 0,
                        width: '100%',
                        height: '100%',
                        border: 0,
                        borderRadius: 8
                      }}
                      allow="autoplay; fullscreen; picture-in-picture"
                      allowFullScreen
                    />
                  ) : selectedContent.content_source === 'spotify' ? (
                    (() => {
                      const spotifyData = extractSpotifyId(selectedContent.source_url);
                      return spotifyData ? (
                        <iframe
                          src={`https://open.spotify.com/embed/${spotifyData.type}/${spotifyData.id}`}
                          title={selectedContent.title}
                          style={{
                            position: 'absolute',
                            top: 0,
                            left: 0,
                            width: '100%',
                            height: spotifyData.type === 'episode' ? '232px' : '352px',
                            border: 0,
                            borderRadius: 8
                          }}
                          allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture"
                        />
                      ) : (
                        <Box sx={{ 
                          position: 'absolute', 
                          top: 0, 
                          left: 0, 
                          width: '100%', 
                          height: '100%', 
                          display: 'flex', 
                          alignItems: 'center', 
                          justifyContent: 'center',
                          backgroundColor: '#f5f5f5',
                          borderRadius: 8
                        }}>
                          <Typography variant="body2" color="text.secondary">
                            No se pudo cargar el podcast. 
                            <Button 
                              size="small" 
                              onClick={() => window.open(selectedContent.source_url, '_blank')}
                            >
                              Abrir en Spotify
                            </Button>
                          </Typography>
                        </Box>
                      );
                    })()
                  ) : null}
                </Box>
              ) : (
                <Box sx={{ mb: 2, position: 'relative' }}>
                  <img 
                    src={generateContentImage(selectedContent)} 
                    alt={selectedContent.title}
                    style={{ width: '100%', height: 200, objectFit: 'cover', borderRadius: 8 }}
                  />
                  {(selectedContent.content_type === 'video' || selectedContent.content_type === 'podcast') && selectedContent.source_url && (
                    <Box
                      sx={{
                        position: 'absolute',
                        top: '50%',
                        left: '50%',
                        transform: 'translate(-50%, -50%)',
                        backgroundColor: 'rgba(0, 0, 0, 0.7)',
                        borderRadius: '50%',
                        width: 60,
                        height: 60,
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        cursor: 'pointer',
                        transition: 'all 0.2s ease',
                        '&:hover': {
                          backgroundColor: 'rgba(0, 0, 0, 0.9)',
                          transform: 'translate(-50%, -50%) scale(1.1)'
                        }
                      }}
                      onClick={() => setShowPlayer(true)}
                    >
                      <PlayArrow sx={{ color: 'white', fontSize: 32 }} />
                    </Box>
                  )}
                </Box>
              )}
              <Typography variant="body1" paragraph>
                {selectedContent.description}
              </Typography>
              {selectedContent.tags && selectedContent.tags.length > 0 && (
                <Box sx={{ display: 'flex', gap: 1, mb: 2, flexWrap: 'wrap' }}>
                  {selectedContent.tags.map((tag) => (
                    <Chip key={tag} label={tag} size="small" />
                  ))}
                </Box>
              )}
              <Divider sx={{ my: 2 }} />
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                  <Avatar>
                    {(selectedContent.author || 'Autor').split(' ').map(n => n[0]).join('')}
                  </Avatar>
                  <Box>
                    <Typography variant="body2" fontWeight={500}>
                      {selectedContent.author || 'Autor desconocido'}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      Publicado el {new Date(selectedContent.published_at || selectedContent.created_at).toLocaleDateString()}
                    </Typography>
                  </Box>
                </Box>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Star sx={{ color: 'warning.main' }} />
                  <Typography variant="body2">{selectedContent.rating}</Typography>
                </Box>
              </Box>
            </DialogContent>
            <DialogActions>
              <Button onClick={() => {
                setShowContentDialog(false);
                setShowPlayer(false);
              }}>
                Cerrar
              </Button>
              {(selectedContent.content_type === 'video' || selectedContent.content_type === 'podcast') && selectedContent.source_url ? (
                showPlayer ? (
                  <Button 
                    variant="outlined"
                    onClick={() => setShowPlayer(false)}
                  >
                    Ocultar Reproductor
                  </Button>
                ) : (
                  <Button 
                    variant="contained" 
                    startIcon={<PlayArrow />}
                    onClick={() => setShowPlayer(true)}
                  >
                    {selectedContent.content_type === 'video' ? 'Reproducir Video' : 'Escuchar Podcast'}
                  </Button>
                )
              ) : selectedContent.source_url ? (
                <Button 
                  variant="contained" 
                  startIcon={getTypeIcon(selectedContent.content_type)}
                  onClick={() => window.open(selectedContent.source_url, '_blank')}
                >
                  {selectedContent.content_type === 'article' ? 'Leer Artículo' : 
                   selectedContent.content_type === 'course' ? 'Ver Curso' :
                   (selectedContent.content_type as string) === 'webinar' ? 'Ver Webinar' :
                   'Ver contenido'}
                </Button>
              ) : null}
            </DialogActions>
          </>
        )}
      </Dialog>

      {/* Notificaciones */}
      <Snackbar
        open={!!error}
        autoHideDuration={6000}
        onClose={() => setError(null)}
      >
        <Alert onClose={() => setError(null)} severity="error">
          {error}
        </Alert>
      </Snackbar>

      <Snackbar
        open={!!success}
        autoHideDuration={4000}
        onClose={() => setSuccess(null)}
      >
        <Alert onClose={() => setSuccess(null)} severity="success">
          {success}
        </Alert>
      </Snackbar>
    </Container>
  );
};

export default LearnPage;
