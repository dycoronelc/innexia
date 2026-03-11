import feedparser
import concurrent.futures
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dateutil import parser as date_parser

logger = logging.getLogger(__name__)

class RSSFeedService:
    def __init__(self):
        self.cache = {}
        self.cache_duration = timedelta(hours=1)
        
        # Feeds RSS predefinidos en español
        self.DEFAULT_RSS_FEEDS = [
            {
                "name": "Emprendedores - Noticias",
                "url": "https://www.emprendedores.es/rss/",
                "category": "Emprendimiento",
                "language": "es"
            },
            {
                "name": "Entrepreneur en Español",
                "url": "https://www.entrepreneur.com/es/feed",
                "category": "Emprendimiento",
                "language": "es"
            }
        ]

    def fetch_feed(self, feed_url: str, feed_name: str = "Unknown") -> List[Dict]:
        """Extrae artículos de un feed RSS individual"""
        try:
            logger.info(f"Fetching feed: {feed_name} from {feed_url}")
            
            # Verificar cache
            cache_key = f"feed_{hash(feed_url)}"
            if cache_key in self.cache:
                cached_data, cached_time = self.cache[cache_key]
                if datetime.now() - cached_time < self.cache_duration:
                    logger.info(f"Using cached data for {feed_name}")
                    return cached_data
            
            # Parsear feed
            feed = feedparser.parse(feed_url)
            
            if feed.bozo:
                logger.warning(f"Feed {feed_name} has parsing issues: {feed.bozo_exception}")
            
            articles = []
            
            for entry in feed.entries[:20]:  # Limitar a 20 artículos por feed
                try:
                    # Extraer fecha de publicación
                    published_date = None
                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                        published_date = datetime(*entry.published_parsed[:6])
                    elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                        published_date = datetime(*entry.updated_parsed[:6])
                    
                    if not published_date:
                        published_date = datetime.now()
                    
                    # Extraer imagen
                    image_url = None
                    if hasattr(entry, 'media_content') and entry.media_content:
                        image_url = entry.media_content[0].get('url')
                    elif hasattr(entry, 'media_thumbnail') and entry.media_thumbnail:
                        image_url = entry.media_thumbnail[0].get('url')
                    elif hasattr(entry, 'enclosures') and entry.enclosures:
                        for enclosure in entry.enclosures:
                            if enclosure.get('type', '').startswith('image/'):
                                image_url = enclosure.get('href')
                                break
                    
                    # Si no hay imagen del feed, generar una única basada en el título
                    if not image_url:
                        image_url = self._generate_news_image(entry.title if hasattr(entry, 'title') else f"Article {len(articles)}")
                    
                    # Extraer descripción
                    description = ""
                    if hasattr(entry, 'summary'):
                        description = entry.summary
                    elif hasattr(entry, 'description'):
                        description = entry.description
                    
                    # Limpiar HTML de la descripción
                    import re
                    description = re.sub(r'<[^>]+>', '', description)
                    description = description.strip()[:300]  # Limitar longitud
                    
                    # Extraer autor
                    author = ""
                    if hasattr(entry, 'author'):
                        author = entry.author
                    elif hasattr(entry, 'author_detail') and hasattr(entry.author_detail, 'name'):
                        author = entry.author_detail.name
                    
                    article = {
                        "title": entry.title if hasattr(entry, 'title') else "Sin título",
                        "description": description,
                        "url": entry.link if hasattr(entry, 'link') else "",
                        "published_date": published_date.isoformat(),
                        "author": author,
                        "source": feed_name,
                        "category": "Emprendimiento",
                        "image_url": image_url
                    }
                    
                    articles.append(article)
                    
                except Exception as e:
                    logger.error(f"Error processing article from {feed_name}: {e}")
                    continue
            
            # Guardar en cache
            self.cache[cache_key] = (articles, datetime.now())
            logger.info(f"Successfully fetched {len(articles)} articles from {feed_name}")
            
            return articles
            
        except Exception as e:
            logger.error(f"Error fetching feed {feed_name}: {e}")
            return []

    def _generate_news_image(self, title: str) -> str:
        """Genera una imagen única basada en el título del artículo"""
        import hashlib
        
        # Crear un hash del título para consistencia
        title_hash = hashlib.md5(title.encode('utf-8')).hexdigest()
        
        # Convertir hash a número para seleccionar imagen
        hash_number = int(title_hash[:8], 16)
        
        # Lista de imágenes de noticias/negocios de Unsplash
        news_images = [
            "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&h=225&fit=crop&crop=center",  # Business meeting
            "https://images.unsplash.com/photo-1551434678-e076c223a692?w=400&h=225&fit=crop&crop=center",  # Charts and graphs
            "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=400&h=225&fit=crop&crop=center",  # Financial news
            "https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=400&h=225&fit=crop&crop=center",  # Newspaper
            "https://images.unsplash.com/photo-1559136555-9303baea8ebd?w=400&h=225&fit=crop&crop=center",  # Business handshake
            "https://images.unsplash.com/photo-1554224155-6726b3ff858f?w=400&h=225&fit=crop&crop=center",  # Technology innovation
            "https://images.unsplash.com/photo-1553877522-43269d4ea984?w=400&h=225&fit=crop&crop=center",  # Office workspace
            "https://images.unsplash.com/photo-1559136555-9303baea8ebd?w=400&h=225&fit=crop&crop=center",  # Business presentation
            "https://images.unsplash.com/photo-1554224155-6726b3ff858f?w=400&h=225&fit=crop&crop=center",  # Startup scene
            "https://images.unsplash.com/photo-1553877522-43269d4ea984?w=400&h=225&fit=crop&crop=center",  # Team collaboration
        ]
        
        # Seleccionar imagen basada en el hash
        image_index = hash_number % len(news_images)
        return news_images[image_index]

    def fetch_all_default_feeds(self) -> List[Dict]:
        """Obtiene artículos de todos los feeds predefinidos en paralelo"""
        logger.info("Fetching all default RSS feeds")
        
        all_articles = []
        
        def fetch_single_feed(feed_info):
            try:
                return self.fetch_feed(feed_info["url"], feed_info["name"])
            except Exception as e:
                logger.error(f"Error fetching {feed_info['name']}: {e}")
                return []
        
        # Procesar feeds en paralelo
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            futures = [executor.submit(fetch_single_feed, feed_info) for feed_info in self.DEFAULT_RSS_FEEDS]
            
            # Esperar a que todos terminen con timeout de 15 segundos
            concurrent.futures.wait(futures, timeout=15)
            
            for future in futures:
                try:
                    if future.done() and not future.cancelled():
                        articles = future.result(timeout=1)
                        all_articles.extend(articles)
                except Exception as e:
                    logger.error(f"Error processing future result: {e}")
        
        # Ordenar por fecha de publicación (más recientes primero)
        all_articles.sort(key=lambda x: x["published_date"], reverse=True)
        
        return all_articles

    def fetch_custom_feeds(self, feed_urls: List[str]) -> List[Dict]:
        """Obtiene artículos de feeds personalizados"""
        logger.info(f"Fetching {len(feed_urls)} custom feeds")
        
        all_articles = []
        
        for url in feed_urls:
            try:
                articles = self.fetch_feed(url, f"Custom Feed {url[:30]}...")
                all_articles.extend(articles)
            except Exception as e:
                logger.error(f"Error fetching custom feed {url}: {e}")
                continue
        
        # Ordenar por fecha de publicación
        all_articles.sort(key=lambda x: x["published_date"], reverse=True)
        
        return all_articles

    def clear_cache(self):
        """Limpia el cache de feeds"""
        self.cache.clear()
        logger.info("RSS feed cache cleared")


# Instancia global del servicio
rss_service = RSSFeedService()

