"""
API endpoints para noticias desde feeds RSS
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
import logging

from app.services.rss_feed_service import rss_service
from app.core.auth import get_current_user
from app.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/news-feed", tags=["news-feed"])


class NewsArticle(BaseModel):
    """Modelo para un artículo de noticias"""
    title: str
    description: str
    url: str
    image_url: Optional[str] = None
    published_date: str
    author: str
    source: str
    category: Optional[str] = "General"
    language: Optional[str] = "es"


class NewsResponse(BaseModel):
    """Respuesta con lista de noticias"""
    status: str
    data: List[NewsArticle]
    total: int


class CustomFeedRequest(BaseModel):
    """Request para agregar un feed RSS personalizado"""
    feed_url: str
    feed_name: Optional[str] = None


@router.get("/", response_model=NewsResponse)
async def get_news_feed(
    limit: Optional[int] = Query(50, ge=1, le=100),
    category: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene las noticias de los feeds RSS predefinidos
    
    Args:
        limit: Número máximo de artículos a retornar
        category: Filtrar por categoría (opcional)
        current_user: Usuario autenticado
        
    Returns:
        Lista de artículos de noticias
    """
    try:
        logger.info(f"Fetching news feed for user {current_user.id}")
        
        # Obtener artículos de todos los feeds predefinidos
        articles = rss_service.fetch_all_default_feeds()
        
        # Filtrar por categoría si se especifica
        if category and category.lower() != 'all':
            articles = [a for a in articles if a.get('category', '').lower() == category.lower()]
        
        # Limitar número de resultados
        articles = articles[:limit]
        
        return NewsResponse(
            status="success",
            data=articles,
            total=len(articles)
        )
        
    except Exception as e:
        logger.error(f"Error fetching news feed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al obtener noticias: {str(e)}")


@router.post("/custom-feed", response_model=NewsResponse)
async def fetch_custom_feed(
    request: CustomFeedRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Consume un feed RSS personalizado
    
    Args:
        request: Datos del feed RSS personalizado
        current_user: Usuario autenticado
        
    Returns:
        Lista de artículos del feed personalizado
    """
    try:
        logger.info(f"Fetching custom feed {request.feed_url} for user {current_user.id}")
        
        feed_name = request.feed_name or request.feed_url
        articles = rss_service.fetch_feed(request.feed_url, feed_name)
        
        if not articles:
            raise HTTPException(
                status_code=400, 
                detail="No se pudieron obtener artículos del feed RSS proporcionado"
            )
        
        return NewsResponse(
            status="success",
            data=articles,
            total=len(articles)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching custom feed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al obtener feed personalizado: {str(e)}")


@router.post("/clear-cache")
async def clear_news_cache(
    current_user: User = Depends(get_current_user)
):
    """
    Limpia el cache de feeds RSS (solo para administradores)
    
    Args:
        current_user: Usuario autenticado
        
    Returns:
        Mensaje de confirmación
    """
    try:
        rss_service.clear_cache()
        
        return {
            "status": "success",
            "message": "Cache de noticias limpiado exitosamente"
        }
        
    except Exception as e:
        logger.error(f"Error clearing cache: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al limpiar cache: {str(e)}")


@router.get("/feeds")
async def get_available_feeds(
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene la lista de feeds RSS predefinidos disponibles
    
    Args:
        current_user: Usuario autenticado
        
    Returns:
        Lista de feeds RSS disponibles
    """
    from app.services.rss_feed_service import DEFAULT_RSS_FEEDS
    
    return {
        "status": "success",
        "data": DEFAULT_RSS_FEEDS,
        "total": len(DEFAULT_RSS_FEEDS)
    }


