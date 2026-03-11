export const formatDate = (dateString: string | Date | null): string => {
  if (!dateString) return 'No disponible';
  
  try {
    // Si es una fecha ISO string del backend (2024-01-15T00:00:00)
    if (typeof dateString === 'string' && dateString.includes('T')) {
      const isoDate = dateString.split('T')[0]; // Tomar solo la parte de la fecha
      dateString = isoDate;
    }
    
    const date = typeof dateString === 'string' ? new Date(dateString) : dateString;
    
    if (isNaN(date.getTime())) {
      return 'Fecha inválida';
    }
    
    const formattedDate = new Intl.DateTimeFormat('es-ES', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit'
    }).format(date);
    
    return formattedDate;
  } catch (error) {
    console.error('Error formatting date:', error, dateString);
    return 'Fecha inválida';
  }
};