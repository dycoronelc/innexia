import { apiRequest } from './api';

export interface NewsArticle {
  title: string;
  description: string;
  url: string;
  published_date: string;
  author: string;
  source: string;
  category: string;
  image_url?: string;
}

export interface NewsResponse {
  data: NewsArticle[];
  status: string;
  message: string;
  total?: number;
}

export interface CustomFeedRequest {
  feed_urls: string[];
}

export interface AvailableFeed {
  name: string;
  url: string;
  category: string;
  language: string;
}

class NewsFeedService {
  /**
   * Obtiene noticias de los feeds RSS predefinidos
   */
  async getNews(params: { limit?: number; offset?: number } = {}, token: string): Promise<NewsResponse> {
    const queryParams = new URLSearchParams();
    
    if (params.limit) {
      queryParams.append('limit', params.limit.toString());
    }
    
    if (params.offset) {
      queryParams.append('offset', params.offset.toString());
    }

    const url = `/api/news-feed${queryParams.toString() ? `?${queryParams.toString()}` : ''}`;
    return apiRequest<NewsResponse>(url, {
      method: 'GET',
    }, token);
  }

  /**
   * Obtiene noticias de feeds RSS personalizados
   */
  async getCustomFeed(feedUrls: string[], token: string): Promise<NewsResponse> {
    return apiRequest<NewsResponse>('/api/news-feed/custom-feed', {
      method: 'POST',
      body: JSON.stringify({ feed_urls: feedUrls }),
    }, token);
  }

  /**
   * Limpia el cache de noticias
   */
  async clearCache(token: string): Promise<{ message: string }> {
    return apiRequest<{ message: string }>('/api/news-feed/clear-cache', {
      method: 'POST',
    }, token);
  }

  /**
   * Obtiene la lista de feeds disponibles
   */
  async getAvailableFeeds(token: string): Promise<{ feeds: AvailableFeed[] }> {
    return apiRequest<{ feeds: AvailableFeed[] }>('/api/news-feed/feeds', {
      method: 'GET',
    }, token);
  }
}

// Exportar instancia del servicio
export const newsFeedService = new NewsFeedService();

