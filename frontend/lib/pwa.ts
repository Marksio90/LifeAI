/**
 * PWA Utilities for LifeAI
 *
 * Handles service worker registration, install prompts, and offline support
 */

export interface BeforeInstallPromptEvent extends Event {
  prompt: () => Promise<void>;
  userChoice: Promise<{ outcome: 'accepted' | 'dismissed' }>;
}

let deferredPrompt: BeforeInstallPromptEvent | null = null;

/**
 * Register the service worker
 */
export async function registerServiceWorker(): Promise<ServiceWorkerRegistration | null> {
  if (typeof window === 'undefined' || !('serviceWorker' in navigator)) {
    console.log('Service Worker not supported');
    return null;
  }

  try {
    const registration = await navigator.serviceWorker.register('/service-worker.js');

    console.log('Service Worker registered:', registration);

    // Check for updates periodically
    setInterval(() => {
      registration.update();
    }, 60 * 60 * 1000); // Check every hour

    // Handle updates
    registration.addEventListener('updatefound', () => {
      const newWorker = registration.installing;

      if (newWorker) {
        newWorker.addEventListener('statechange', () => {
          if (
            newWorker.state === 'installed' &&
            navigator.serviceWorker.controller
          ) {
            // New service worker available
            console.log('New service worker available');

            // Notify user about update
            if (confirm('Nowa wersja jest dostępna. Odświeżyć teraz?')) {
              newWorker.postMessage({ type: 'SKIP_WAITING' });
              window.location.reload();
            }
          }
        });
      }
    });

    return registration;
  } catch (error) {
    console.error('Service Worker registration failed:', error);
    return null;
  }
}

/**
 * Unregister the service worker
 */
export async function unregisterServiceWorker(): Promise<boolean> {
  if (typeof window === 'undefined' || !('serviceWorker' in navigator)) {
    return false;
  }

  try {
    const registration = await navigator.serviceWorker.getRegistration();

    if (registration) {
      const result = await registration.unregister();
      console.log('Service Worker unregistered:', result);
      return result;
    }

    return false;
  } catch (error) {
    console.error('Service Worker unregistration failed:', error);
    return false;
  }
}

/**
 * Setup PWA install prompt handling
 */
export function setupInstallPrompt() {
  if (typeof window === 'undefined') return;

  // Capture the install prompt event
  window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault();
    deferredPrompt = e as BeforeInstallPromptEvent;
    console.log('Install prompt captured');

    // Dispatch custom event that app can listen to
    window.dispatchEvent(new Event('pwa-install-available'));
  });

  // Track successful installation
  window.addEventListener('appinstalled', () => {
    console.log('PWA installed successfully');
    deferredPrompt = null;

    // Dispatch custom event
    window.dispatchEvent(new Event('pwa-installed'));
  });
}

/**
 * Show the PWA install prompt
 */
export async function showInstallPrompt(): Promise<'accepted' | 'dismissed' | 'unavailable'> {
  if (!deferredPrompt) {
    console.log('Install prompt not available');
    return 'unavailable';
  }

  try {
    // Show the install prompt
    await deferredPrompt.prompt();

    // Wait for user response
    const { outcome } = await deferredPrompt.userChoice;

    console.log('Install prompt outcome:', outcome);

    // Clear the deferred prompt
    deferredPrompt = null;

    return outcome;
  } catch (error) {
    console.error('Install prompt error:', error);
    return 'unavailable';
  }
}

/**
 * Check if PWA is installable
 */
export function isInstallable(): boolean {
  return deferredPrompt !== null;
}

/**
 * Check if app is running as PWA
 */
export function isPWA(): boolean {
  if (typeof window === 'undefined') return false;

  return (
    window.matchMedia('(display-mode: standalone)').matches ||
    (window.navigator as any).standalone === true ||
    document.referrer.includes('android-app://')
  );
}

/**
 * Check if device is online
 */
export function isOnline(): boolean {
  if (typeof window === 'undefined') return true;
  return navigator.onLine;
}

/**
 * Setup online/offline event listeners
 */
export function setupConnectivityListeners(
  onOnline?: () => void,
  onOffline?: () => void
) {
  if (typeof window === 'undefined') return;

  if (onOnline) {
    window.addEventListener('online', onOnline);
  }

  if (onOffline) {
    window.addEventListener('offline', onOffline);
  }

  return () => {
    if (onOnline) {
      window.removeEventListener('online', onOnline);
    }
    if (onOffline) {
      window.removeEventListener('offline', onOffline);
    }
  };
}

/**
 * Request notification permission
 */
export async function requestNotificationPermission(): Promise<NotificationPermission> {
  if (typeof window === 'undefined' || !('Notification' in window)) {
    console.log('Notifications not supported');
    return 'denied';
  }

  if (Notification.permission === 'granted') {
    return 'granted';
  }

  if (Notification.permission !== 'denied') {
    const permission = await Notification.requestPermission();
    return permission;
  }

  return Notification.permission;
}

/**
 * Show a notification
 */
export async function showNotification(
  title: string,
  options?: NotificationOptions
): Promise<boolean> {
  if (typeof window === 'undefined' || !('Notification' in window)) {
    return false;
  }

  if (Notification.permission !== 'granted') {
    const permission = await requestNotificationPermission();
    if (permission !== 'granted') {
      return false;
    }
  }

  try {
    const registration = await navigator.serviceWorker.getRegistration();

    if (registration) {
      await registration.showNotification(title, {
        icon: '/icons/icon-192x192.png',
        badge: '/icons/badge-72x72.png',
        ...options,
      });
      return true;
    }

    return false;
  } catch (error) {
    console.error('Notification error:', error);
    return false;
  }
}

/**
 * Subscribe to push notifications
 */
export async function subscribeToPushNotifications(
  vapidPublicKey: string
): Promise<PushSubscription | null> {
  if (typeof window === 'undefined' || !('serviceWorker' in navigator)) {
    return null;
  }

  try {
    const registration = await navigator.serviceWorker.getRegistration();

    if (!registration) {
      console.error('No service worker registration found');
      return null;
    }

    // Check for existing subscription
    let subscription = await registration.pushManager.getSubscription();

    if (!subscription) {
      // Create new subscription
      subscription = await registration.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: urlBase64ToUint8Array(vapidPublicKey),
      });

      console.log('Push subscription created:', subscription);
    }

    return subscription;
  } catch (error) {
    console.error('Push subscription error:', error);
    return null;
  }
}

/**
 * Unsubscribe from push notifications
 */
export async function unsubscribeFromPushNotifications(): Promise<boolean> {
  if (typeof window === 'undefined' || !('serviceWorker' in navigator)) {
    return false;
  }

  try {
    const registration = await navigator.serviceWorker.getRegistration();

    if (registration) {
      const subscription = await registration.pushManager.getSubscription();

      if (subscription) {
        const result = await subscription.unsubscribe();
        console.log('Push subscription removed:', result);
        return result;
      }
    }

    return false;
  } catch (error) {
    console.error('Push unsubscription error:', error);
    return false;
  }
}

/**
 * Helper to convert VAPID key
 */
function urlBase64ToUint8Array(base64String: string): Uint8Array {
  const padding = '='.repeat((4 - (base64String.length % 4)) % 4);
  const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/');

  const rawData = window.atob(base64);
  const outputArray = new Uint8Array(rawData.length);

  for (let i = 0; i < rawData.length; ++i) {
    outputArray[i] = rawData.charCodeAt(i);
  }

  return outputArray;
}

/**
 * Cache a URL for offline access
 */
export async function cacheURL(url: string): Promise<boolean> {
  if (typeof window === 'undefined' || !('caches' in window)) {
    return false;
  }

  try {
    const cache = await caches.open('lifeai-v1');
    await cache.add(url);
    return true;
  } catch (error) {
    console.error('Cache error:', error);
    return false;
  }
}

/**
 * Clear all caches
 */
export async function clearCaches(): Promise<boolean> {
  if (typeof window === 'undefined' || !('caches' in window)) {
    return false;
  }

  try {
    const cacheNames = await caches.keys();
    await Promise.all(cacheNames.map((name) => caches.delete(name)));
    console.log('All caches cleared');
    return true;
  } catch (error) {
    console.error('Clear caches error:', error);
    return false;
  }
}
