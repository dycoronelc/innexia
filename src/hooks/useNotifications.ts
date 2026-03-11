import { useState, useEffect, useCallback } from 'react';

interface UseNotificationsReturn {
  permission: NotificationPermission;
  isSupported: boolean;
  requestPermission: () => Promise<NotificationPermission>;
  showNotification: (title: string, options?: NotificationOptions) => void;
  subscribeToPush: () => Promise<void>;
}

export const useNotifications = (): UseNotificationsReturn => {
  const [permission, setPermission] = useState<NotificationPermission>('default');
  const [isSupported, setIsSupported] = useState(false);

  useEffect(() => {
    // Check if notifications are supported
    const supported = 'Notification' in window;
    setIsSupported(supported);

    if (supported) {
      setPermission(Notification.permission);
    }
  }, []);

  const requestPermission = useCallback(async (): Promise<NotificationPermission> => {
    if (!isSupported) {
      throw new Error('Notifications not supported');
    }

    try {
      const result = await Notification.requestPermission();
      setPermission(result);
      return result;
    } catch (error) {
      console.error('Error requesting notification permission:', error);
      throw error;
    }
  }, [isSupported]);

  const showNotification = useCallback((title: string, options?: NotificationOptions) => {
    if (!isSupported || permission !== 'granted') {
      console.warn('Cannot show notification: not supported or permission denied');
      return;
    }

    try {
      new Notification(title, {
        icon: '/vite.svg',
        badge: '/vite.svg',
        ...options
      });
    } catch (error) {
      console.error('Error showing notification:', error);
    }
  }, [isSupported, permission]);

  const subscribeToPush = useCallback(async () => {
    if (!isSupported || permission !== 'granted') {
      throw new Error('Notifications not supported or permission denied');
    }

    try {
      // Check if service worker is registered
      if (!('serviceWorker' in navigator)) {
        throw new Error('Service Worker not supported');
      }

      const registration = await navigator.serviceWorker.ready;
      
      // Check if push manager is supported
      if (!('PushManager' in window)) {
        throw new Error('Push Manager not supported');
      }

      // Get push subscription
      const subscription = await registration.pushManager.getSubscription();
      
      if (subscription) {
        console.log('Already subscribed to push notifications');
        return;
      }

      // Subscribe to push notifications
      const newSubscription = await registration.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: urlBase64ToUint8Array(import.meta.env.VITE_VAPID_PUBLIC_KEY || '')
      });

      console.log('Subscribed to push notifications:', newSubscription);
      
      // Here you would typically send the subscription to your server
      // await sendSubscriptionToServer(newSubscription);
      
    } catch (error) {
      console.error('Error subscribing to push notifications:', error);
      throw error;
    }
  }, [isSupported, permission]);

  return {
    permission,
    isSupported,
    requestPermission,
    showNotification,
    subscribeToPush
  };
};

// Helper function to convert VAPID key
function urlBase64ToUint8Array(base64String: string): Uint8Array {
  const padding = '='.repeat((4 - base64String.length % 4) % 4);
  const base64 = (base64String + padding)
    .replace(/-/g, '+')
    .replace(/_/g, '/');

  const rawData = window.atob(base64);
  const outputArray = new Uint8Array(rawData.length);

  for (let i = 0; i < rawData.length; ++i) {
    outputArray[i] = rawData.charCodeAt(i);
  }
  return outputArray;
}


