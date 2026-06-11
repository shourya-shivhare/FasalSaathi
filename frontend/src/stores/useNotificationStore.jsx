import { create } from 'zustand';
import { api } from '../lib/api.jsx';
import { useUserStore } from './useUserStore.jsx';

export const useNotificationStore = create((set, get) => ({
  notifications: [],
  unreadCount: 0,
  loading: false,

  fetchNotifications: async () => {
    const token = useUserStore.getState().accessToken;
    if (!token) return;
    set({ loading: true });
    try {
      const [notifications, { unread_count }] = await Promise.all([
        api.getNotifications(token),
        api.getUnreadCount(token),
      ]);
      set({ notifications, unreadCount: unread_count, loading: false });
    } catch {
      set({ loading: false });
    }
  },

  fetchUnreadCount: async () => {
    const token = useUserStore.getState().accessToken;
    if (!token) return;
    try {
      const { unread_count } = await api.getUnreadCount(token);
      set({ unreadCount: unread_count });
    } catch { /* silent */ }
  },

  markRead: async (notifId) => {
    const token = useUserStore.getState().accessToken;
    await api.markNotificationRead(token, notifId);
    set((s) => ({
      notifications: s.notifications.map((n) =>
        n.id === notifId ? { ...n, is_read: true } : n
      ),
      unreadCount: Math.max(0, s.unreadCount - 1),
    }));
  },

  markAllRead: async () => {
    const token = useUserStore.getState().accessToken;
    await api.markAllNotificationsRead(token);
    set((s) => ({
      notifications: s.notifications.map((n) => ({ ...n, is_read: true })),
      unreadCount: 0,
    }));
  },
}));
