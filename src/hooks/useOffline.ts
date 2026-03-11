import { useState, useEffect, useCallback } from 'react';

interface OfflineData {
  id: string;
  type: 'project' | 'canvas' | 'document';
  action: 'create' | 'update' | 'delete';
  data: any;
  timestamp: number;
}

interface UseOfflineReturn {
  isOnline: boolean;
  isOffline: boolean;
  offlineData: OfflineData[];
  addOfflineData: (data: OfflineData) => void;
  removeOfflineData: (id: string) => void;
  syncOfflineData: () => Promise<void>;
  clearOfflineData: () => void;
}

export const useOffline = (): UseOfflineReturn => {
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [offlineData, setOfflineData] = useState<OfflineData[]>([]);

  // Check online status
  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    // Load offline data from localStorage
    const savedOfflineData = localStorage.getItem('innexia-offline-data');
    if (savedOfflineData) {
      try {
        setOfflineData(JSON.parse(savedOfflineData));
      } catch (error) {
        console.error('Error loading offline data:', error);
      }
    }

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  // Save offline data to localStorage whenever it changes
  useEffect(() => {
    localStorage.setItem('innexia-offline-data', JSON.stringify(offlineData));
  }, [offlineData]);

  // Add data to offline queue
  const addOfflineData = useCallback((data: OfflineData) => {
    setOfflineData(prev => [...prev, data]);
  }, []);

  // Remove data from offline queue
  const removeOfflineData = useCallback((id: string) => {
    setOfflineData(prev => prev.filter(item => item.id !== id));
  }, []);

  // Clear all offline data
  const clearOfflineData = useCallback(() => {
    setOfflineData([]);
    localStorage.removeItem('innexia-offline-data');
  }, []);

  // Sync offline data when back online
  const syncOfflineData = useCallback(async () => {
    if (!isOnline || offlineData.length === 0) {
      return;
    }

    console.log('Syncing offline data...', offlineData);

    try {
      // Process each offline action
      for (const item of offlineData) {
        try {
          switch (item.type) {
            case 'project':
              await syncProject(item);
              break;
            case 'canvas':
              await syncCanvas(item);
              break;
            case 'document':
              await syncDocument(item);
              break;
          }
          
          // Remove successfully synced item
          removeOfflineData(item.id);
        } catch (error) {
          console.error(`Failed to sync ${item.type}:`, error);
          // Keep failed items in queue for retry
        }
      }
    } catch (error) {
      console.error('Error during offline sync:', error);
    }
  }, [isOnline, offlineData, removeOfflineData]);

  // Auto-sync when coming back online
  useEffect(() => {
    if (isOnline && offlineData.length > 0) {
      // Small delay to ensure connection is stable
      const timer = setTimeout(() => {
        syncOfflineData();
      }, 1000);

      return () => clearTimeout(timer);
    }
  }, [isOnline, offlineData.length, syncOfflineData]);

  return {
    isOnline,
    isOffline: !isOnline,
    offlineData,
    addOfflineData,
    removeOfflineData,
    syncOfflineData,
    clearOfflineData
  };
};

// Helper functions for syncing different types of data
async function syncProject(item: OfflineData) {
  const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
  
  switch (item.action) {
    case 'create':
      await fetch(`${baseUrl}/api/projects/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(item.data)
      });
      break;
    case 'update':
      await fetch(`${baseUrl}/api/projects/${item.data.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(item.data)
      });
      break;
    case 'delete':
      await fetch(`${baseUrl}/api/projects/${item.data.id}`, {
        method: 'DELETE'
      });
      break;
  }
}

async function syncCanvas(item: OfflineData) {
  const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
  
  switch (item.action) {
    case 'create':
      await fetch(`${baseUrl}/api/business-model-canvas/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(item.data)
      });
      break;
    case 'update':
      await fetch(`${baseUrl}/api/business-model-canvas/${item.data.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(item.data)
      });
      break;
    case 'delete':
      await fetch(`${baseUrl}/api/business-model-canvas/${item.data.id}`, {
        method: 'DELETE'
      });
      break;
  }
}

async function syncDocument(item: OfflineData) {
  const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
  
  switch (item.action) {
    case 'create':
      await fetch(`${baseUrl}/api/documents/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(item.data)
      });
      break;
    case 'update':
      await fetch(`${baseUrl}/api/documents/${item.data.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(item.data)
      });
      break;
    case 'delete':
      await fetch(`${baseUrl}/api/documents/${item.data.id}`, {
        method: 'DELETE'
      });
      break;
  }
}


