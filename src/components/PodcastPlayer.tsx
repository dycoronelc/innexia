import React, { useState, useRef, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  IconButton,
  Slider,
  LinearProgress,
  Chip,
  Avatar,
  Button,
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
  Divider,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Tooltip,
  TextField,
  useTheme
} from '@mui/material';
import {
  PlayArrow,
  Pause,
  SkipPrevious,
  SkipNext,
  VolumeUp,
  VolumeOff,
  Speed,
  QueueMusic,
  Favorite,
  FavoriteBorder,
  Share,
  Download,
  AccessTime,
  Person,
  Search,
  KeyboardArrowDown
} from '@mui/icons-material';

interface Episode {
  id: string;
  title: string;
  description: string;
  duration: number; // in seconds
  audioUrl: string;
  imageUrl: string;
  author: string;
  publishDate: string;
  isFavorite: boolean;
}

interface PodcastPlayerProps {
  episode?: Episode;
  episodes?: Episode[];
  onEpisodeChange?: (episode: Episode) => void;
  onFavoriteToggle?: (episodeId: string) => void;
}

const PodcastPlayer: React.FC<PodcastPlayerProps> = ({
  episode,
  episodes = [],
  onEpisodeChange,
  onFavoriteToggle
}) => {
  const theme = useTheme();
  const audioRef = useRef<HTMLAudioElement>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(1);
  const [isMuted, setIsMuted] = useState(false);
  const [playbackRate, setPlaybackRate] = useState(1);
  const [showPlaylist, setShowPlaylist] = useState(false);
  const [showSpeedDialog, setShowSpeedDialog] = useState(false);

  useEffect(() => {
    if (episode && audioRef.current) {
      audioRef.current.src = episode.audioUrl;
      audioRef.current.load();
    }
  }, [episode]);

  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;

    const updateTime = () => setCurrentTime(audio.currentTime);
    const updateDuration = () => setDuration(audio.duration);
    const handleEnded = () => {
      setIsPlaying(false);
      setCurrentTime(0);
      // Auto-play next episode if available
      if (episodes.length > 0 && episode) {
        const currentIndex = episodes.findIndex(ep => ep.id === episode.id);
        const nextEpisode = episodes[currentIndex + 1];
        if (nextEpisode && onEpisodeChange) {
          onEpisodeChange(nextEpisode);
        }
      }
    };

    audio.addEventListener('timeupdate', updateTime);
    audio.addEventListener('loadedmetadata', updateDuration);
    audio.addEventListener('ended', handleEnded);

    return () => {
      audio.removeEventListener('timeupdate', updateTime);
      audio.removeEventListener('loadedmetadata', updateDuration);
      audio.removeEventListener('ended', handleEnded);
    };
  }, [episode, episodes, onEpisodeChange]);

  const togglePlay = () => {
    if (!audioRef.current) return;

    if (isPlaying) {
      audioRef.current.pause();
    } else {
      audioRef.current.play();
    }
    setIsPlaying(!isPlaying);
  };

  const handleSeek = (event: Event, newValue: number | number[]) => {
    if (!audioRef.current) return;
    const time = newValue as number;
    audioRef.current.currentTime = time;
    setCurrentTime(time);
  };

  const handleVolumeChange = (event: Event, newValue: number | number[]) => {
    if (!audioRef.current) return;
    const newVolume = newValue as number;
    audioRef.current.volume = newVolume;
    setVolume(newVolume);
    setIsMuted(newVolume === 0);
  };

  const toggleMute = () => {
    if (!audioRef.current) return;
    if (isMuted) {
      audioRef.current.volume = volume;
      setIsMuted(false);
    } else {
      audioRef.current.volume = 0;
      setIsMuted(true);
    }
  };

  const changePlaybackRate = (rate: number) => {
    if (!audioRef.current) return;
    audioRef.current.playbackRate = rate;
    setPlaybackRate(rate);
    setShowSpeedDialog(false);
  };

  const formatTime = (time: number) => {
    const minutes = Math.floor(time / 60);
    const seconds = Math.floor(time % 60);
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
  };

  const handlePrevious = () => {
    if (episodes.length > 0 && episode) {
      const currentIndex = episodes.findIndex(ep => ep.id === episode.id);
      const prevEpisode = episodes[currentIndex - 1];
      if (prevEpisode && onEpisodeChange) {
        onEpisodeChange(prevEpisode);
      }
    }
  };

  const handleNext = () => {
    if (episodes.length > 0 && episode) {
      const currentIndex = episodes.findIndex(ep => ep.id === episode.id);
      const nextEpisode = episodes[currentIndex + 1];
      if (nextEpisode && onEpisodeChange) {
        onEpisodeChange(nextEpisode);
      }
    }
  };

  if (!episode) {
    return (
      <Card sx={{ p: 3, textAlign: 'center' }}>
        <Typography variant="h6" color="text.secondary">
          Selecciona un episodio para reproducir
        </Typography>
      </Card>
    );
  }

  return (
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
              placeholder="Buscar podcasts"
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

      {/* Main Player Card */}
      <Card sx={{ p: 2, mb: 3 }}>
        <CardContent sx={{ p: 0 }}>
                     {/* Episode Info */}
           <Box sx={{ 
             display: 'flex', 
             gap: 2, 
             mb: 2,
             flexDirection: { xs: 'column', sm: 'row' },
             alignItems: { xs: 'center', sm: 'flex-start' }
           }}>
             <Avatar
               src={episode.imageUrl}
               sx={{ 
                 width: { xs: 120, sm: 80 }, 
                 height: { xs: 120, sm: 80 } 
               }}
             />
                         <Box sx={{ flexGrow: 1, textAlign: { xs: 'center', sm: 'left' } }}>
               <Typography variant="h6" gutterBottom sx={{ fontSize: { xs: '1.1rem', sm: '1.25rem' } }}>
                 {episode.title}
               </Typography>
               <Typography variant="body2" color="text.secondary" gutterBottom>
                 {episode.description}
               </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Person sx={{ fontSize: 16 }} />
                <Typography variant="caption" color="text.secondary">
                  {episode.author}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  • {new Date(episode.publishDate).toLocaleDateString()}
                </Typography>
              </Box>
            </Box>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
              <Tooltip title={episode.isFavorite ? 'Quitar de favoritos' : 'Agregar a favoritos'}>
                <IconButton
                  size="small"
                  onClick={() => onFavoriteToggle?.(episode.id)}
                >
                  {episode.isFavorite ? <Favorite color="error" /> : <FavoriteBorder />}
                </IconButton>
              </Tooltip>
              <Tooltip title="Compartir">
                <IconButton size="small">
                  <Share />
                </IconButton>
              </Tooltip>
              <Tooltip title="Descargar">
                <IconButton size="small">
                  <Download />
                </IconButton>
              </Tooltip>
            </Box>
          </Box>

          {/* Audio Element */}
          <audio ref={audioRef} preload="metadata" />

          {/* Progress Bar */}
          <Box sx={{ mb: 2 }}>
            <Slider
              value={currentTime}
              max={duration}
              onChange={handleSeek}
              sx={{
                '& .MuiSlider-thumb': {
                  width: 12,
                  height: 12,
                },
              }}
            />
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 1 }}>
              <Typography variant="caption" color="text.secondary">
                {formatTime(currentTime)}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                {formatTime(duration)}
              </Typography>
            </Box>
          </Box>

                     {/* Controls */}
           <Box sx={{ 
             display: 'flex', 
             alignItems: 'center', 
             justifyContent: 'center', 
             gap: { xs: 1, sm: 2 },
             flexWrap: 'wrap'
           }}>
            <Tooltip title="Episodio anterior">
              <IconButton onClick={handlePrevious} disabled={episodes.length === 0}>
                <SkipPrevious />
              </IconButton>
            </Tooltip>
            
                         <IconButton
               onClick={togglePlay}
               sx={{
                 width: { xs: 48, sm: 56 },
                 height: { xs: 48, sm: 56 },
                 backgroundColor: 'primary.main',
                 color: 'primary.contrastText',
                 '&:hover': {
                   backgroundColor: 'primary.dark',
                 },
               }}
             >
               {isPlaying ? <Pause /> : <PlayArrow />}
             </IconButton>

            <Tooltip title="Siguiente episodio">
              <IconButton onClick={handleNext} disabled={episodes.length === 0}>
                <SkipNext />
              </IconButton>
            </Tooltip>
          </Box>

          {/* Secondary Controls */}
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mt: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Tooltip title={isMuted ? 'Activar sonido' : 'Silenciar'}>
                <IconButton onClick={toggleMute} size="small">
                  {isMuted ? <VolumeOff /> : <VolumeUp />}
                </IconButton>
              </Tooltip>
              <Slider
                value={isMuted ? 0 : volume}
                onChange={handleVolumeChange}
                min={0}
                max={1}
                step={0.1}
                sx={{ width: 100 }}
              />
            </Box>

            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Tooltip title="Velocidad de reproducción">
                <IconButton
                  size="small"
                  onClick={() => setShowSpeedDialog(true)}
                >
                  <Speed />
                </IconButton>
              </Tooltip>
              <Chip
                label={`${playbackRate}x`}
                size="small"
                variant="outlined"
                onClick={() => setShowSpeedDialog(true)}
              />
              <Tooltip title="Lista de episodios">
                <IconButton
                  size="small"
                  onClick={() => setShowPlaylist(true)}
                >
                  <QueueMusic />
                </IconButton>
              </Tooltip>
            </Box>
          </Box>
        </CardContent>
      </Card>

      {/* Episodes Grid */}
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
        {episodes.map((ep) => (
          <Box key={ep.id} sx={{ width: '100%' }}>
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
              onClick={() => onEpisodeChange?.(ep)}
            >
              {/* Image with Menu */}
              <Box sx={{ position: 'relative' }}>
                <img
                  src={ep.imageUrl}
                  alt={ep.title}
                  style={{
                    width: '100%',
                    height: 200,
                    objectFit: 'cover'
                  }}
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
                    onFavoriteToggle?.(ep.id);
                  }}
                >
                  {ep.isFavorite ? <Favorite color="error" /> : <FavoriteBorder />}
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
                    {ep.title}
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
                    {ep.author}
                  </Typography>
                  
                  {/* Duration - Altura fija */}
                  <Box sx={{ mb: 2 }}>
                    <Box sx={{ 
                      display: 'flex', 
                      justifyContent: 'space-between', 
                      alignItems: 'center',
                      mb: 0.5
                    }}>
                      <Typography variant="caption" color="text.secondary">
                        {formatTime(ep.duration)}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {new Date(ep.publishDate).toLocaleDateString()}
                      </Typography>
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
                  <Button
                    variant="contained"
                    size="small"
                    startIcon={<PlayArrow />}
                    sx={{ 
                      backgroundColor: 'primary.main',
                      color: 'white',
                      fontSize: '0.75rem',
                      '&:hover': { backgroundColor: 'primary.dark' }
                    }}
                  >
                    REPRODUCIR
                  </Button>
                </Box>
              </CardContent>
            </Card>
          </Box>
        ))}
      </Box>

      {/* Playlist Dialog */}
      <Dialog
        open={showPlaylist}
        onClose={() => setShowPlaylist(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Lista de Episodios</DialogTitle>
        <DialogContent>
          <List>
            {episodes.map((ep, index) => (
              <React.Fragment key={ep.id}>
                <ListItem
                  button
                  selected={ep.id === episode?.id}
                  onClick={() => {
                    onEpisodeChange?.(ep);
                    setShowPlaylist(false);
                  }}
                >
                  <ListItemAvatar>
                    <Avatar src={ep.imageUrl} />
                  </ListItemAvatar>
                  <ListItemText
                    primary={ep.title}
                    secondary={
                      <Box>
                        <Typography variant="caption" display="block">
                          {ep.author} • {new Date(ep.publishDate).toLocaleDateString()}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {formatTime(ep.duration)}
                        </Typography>
                      </Box>
                    }
                  />
                  <IconButton
                    size="small"
                    onClick={(e) => {
                      e.stopPropagation();
                      onFavoriteToggle?.(ep.id);
                    }}
                  >
                    {ep.isFavorite ? <Favorite color="error" /> : <FavoriteBorder />}
                  </IconButton>
                </ListItem>
                {index < episodes.length - 1 && <Divider />}
              </React.Fragment>
            ))}
          </List>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowPlaylist(false)}>Cerrar</Button>
        </DialogActions>
      </Dialog>

      {/* Speed Dialog */}
      <Dialog
        open={showSpeedDialog}
        onClose={() => setShowSpeedDialog(false)}
        maxWidth="xs"
        fullWidth
      >
        <DialogTitle>Velocidad de Reproducción</DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
            {[0.5, 0.75, 1, 1.25, 1.5, 2].map((rate) => (
              <Button
                key={rate}
                variant={playbackRate === rate ? 'contained' : 'outlined'}
                onClick={() => changePlaybackRate(rate)}
                sx={{ minWidth: 60 }}
              >
                {rate}x
              </Button>
            ))}
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowSpeedDialog(false)}>Cerrar</Button>
        </DialogActions>
      </Dialog>
    </>
  );
};

export default PodcastPlayer;
