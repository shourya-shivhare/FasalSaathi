import { useState, useEffect } from 'react';

export const useOfflineSync = () => {
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [syncStatus, setSyncStatus] = useState('idle'); // 'idle', 'syncing', 'success', 'error'
  const [lastSync, setLastSync] = useState(null);

  useEffect(() => {
    const handleOnline = () => {
      setIsOnline(true);
      triggerSync();
    };

    const handleOffline = () => {
      setIsOnline(false);
    };

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  const triggerSync = async () => {
    if (!isOnline) return;

    setSyncStatus('syncing');

    try {
      // Simulate sync process
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      setSyncStatus('success');
      setLastSync(new Date());
      
      // Reset status after 3 seconds
      setTimeout(() => setSyncStatus('idle'), 3000);
    } catch (error) {
      console.error('Sync failed:', error);
      setSyncStatus('error');
      
      // Reset status after 3 seconds
      setTimeout(() => setSyncStatus('idle'), 3000);
    }
  };

  const queueOfflineAction = (action) => {
    // Store action in localStorage for later sync
    const offlineQueue = JSON.parse(localStorage.getItem('offlineQueue') || '[]');
    offlineQueue.push({
      ...action,
      timestamp: new Date().toISOString(),
    });
    localStorage.setItem('offlineQueue', JSON.stringify(offlineQueue));
  };

  const processOfflineQueue = async () => {
    const offlineQueue = JSON.parse(localStorage.getItem('offlineQueue') || '[]');
    
    if (offlineQueue.length === 0) return;

    setSyncStatus('syncing');

    try {
      // Process each queued action
      for (const action of offlineQueue) {
        // Simulate processing each action
        await new Promise(resolve => setTimeout(resolve, 500));
      }
      
      // Clear the queue
      localStorage.removeItem('offlineQueue');
      
      setSyncStatus('success');
      setLastSync(new Date());
      
      setTimeout(() => setSyncStatus('idle'), 3000);
    } catch (error) {
      console.error('Failed to process offline queue:', error);
      setSyncStatus('error');
      
      setTimeout(() => setSyncStatus('idle'), 3000);
    }
  };

  return {
    isOnline,
    syncStatus,
    lastSync,
    triggerSync,
    queueOfflineAction,
    processOfflineQueue,
  };
};
