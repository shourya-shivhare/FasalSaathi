import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import {
  LayoutDashboard,
  ScanLine,
  MessageCircle,
  TrendingUp,
  Landmark,
  Sprout,
  User,
  Leaf,
  ChevronLeft,
  ChevronRight,
  LogOut,
  Bell,
  MapPin,
} from 'lucide-react';
import { useUserStore } from '../../stores/useUserStore.jsx';
import { useNotificationStore } from '../../stores/useNotificationStore.jsx';

const navItems = [
  { path: '/dashboard', label: 'Dashboard',     icon: LayoutDashboard },
  { path: '/farms',     label: 'My Farms',       icon: MapPin },
  { path: '/detect',    label: 'Scan Crop',      icon: ScanLine },
  { path: '/chat',      label: 'AI Advisory',    icon: MessageCircle },
  { path: '/market',    label: 'Market Prices',  icon: TrendingUp },
  { path: '/schemes',   label: 'Gov Schemes',    icon: Landmark },
  { path: '/crop-suggestion', label: 'Crop Suggest', icon: Sprout },
  { path: '/profile',   label: 'Profile',        icon: User },
];

const Sidebar = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { farmer, logout } = useUserStore();
  const { unreadCount, fetchUnreadCount, notifications, fetchNotifications, markRead, markAllRead } = useNotificationStore();
  const [collapsed, setCollapsed] = useState(false);
  const [showNotifs, setShowNotifs] = useState(false);

  useEffect(() => {
    fetchUnreadCount();
    const interval = setInterval(fetchUnreadCount, 60000); // poll every 60s
    return () => clearInterval(interval);
  }, []);

  const toggle = () => {
    const next = !collapsed;
    setCollapsed(next);
    document.documentElement.style.setProperty('--sidebar-width', next ? '72px' : '240px');
  };

  const openNotifs = () => {
    if (notifications.length === 0) fetchNotifications();
    setShowNotifs(!showNotifs);
  };

  return (
    <aside
      className="sidebar"
      style={{ width: collapsed ? '72px' : '240px' }}
    >
      {/* Logo + Collapse Toggle */}
      <div
        className="sidebar-logo"
        style={{ justifyContent: collapsed ? 'center' : 'space-between' }}
      >
        {!collapsed && (
          <>
            <div className="sidebar-logo-icon">
              <Leaf size={20} color="#fff" />
            </div>
            <div className="sidebar-logo-text" style={{ flex: 1 }}>
              <span className="sidebar-title">FasalSaathi</span>
              <span className="sidebar-subtitle">Precision AI</span>
            </div>
          </>
        )}
        <button
          className="sidebar-collapse-btn"
          onClick={toggle}
          title={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          {collapsed ? <ChevronRight size={15} /> : <ChevronLeft size={15} />}
        </button>
      </div>

      {/* Notification Bell */}
      <div style={{ padding: collapsed ? '8px' : '8px 16px', position: 'relative' }}>
        <button
          onClick={openNotifs}
          title="Notifications"
          style={{
            display: 'flex', alignItems: 'center', gap: '10px',
            width: '100%', background: showNotifs ? 'var(--color-section-header-bg)' : 'transparent',
            border: 'none', borderRadius: '10px', padding: collapsed ? '10px' : '10px 14px',
            cursor: 'pointer', color: 'var(--color-text-primary)', fontSize: '0.875rem',
            fontWeight: 600, justifyContent: collapsed ? 'center' : 'flex-start',
            transition: 'background 0.15s',
          }}
        >
          <div style={{ position: 'relative' }}>
            <Bell size={20} />
            {unreadCount > 0 && (
              <span style={{
                position: 'absolute', top: -4, right: -6,
                background: '#ef4444', color: '#fff', fontSize: '0.6rem',
                fontWeight: 800, minWidth: '16px', height: '16px',
                borderRadius: '8px', display: 'flex', alignItems: 'center',
                justifyContent: 'center', padding: '0 4px',
              }}>
                {unreadCount > 9 ? '9+' : unreadCount}
              </span>
            )}
          </div>
          {!collapsed && <span>Notifications</span>}
        </button>

        {/* Notification Dropdown */}
        {showNotifs && !collapsed && (
          <div style={{
            position: 'absolute', left: '100%', top: 0, marginLeft: '8px',
            width: '320px', maxHeight: '400px', overflowY: 'auto',
            background: 'var(--color-surface)', borderRadius: '16px',
            border: '1px solid var(--color-border)',
            boxShadow: '0 12px 40px rgba(0,0,0,0.15)', zIndex: 100, padding: '12px',
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
              <span style={{ fontWeight: 700, fontSize: '0.9rem', color: 'var(--color-text-primary)' }}>Notifications</span>
              {unreadCount > 0 && (
                <button
                  onClick={() => markAllRead()}
                  style={{ border: 'none', background: 'none', color: 'var(--color-accent-primary)', fontSize: '0.78rem', fontWeight: 600, cursor: 'pointer' }}
                >
                  Mark all read
                </button>
              )}
            </div>
            {notifications.length === 0 ? (
              <p style={{ color: 'var(--color-text-secondary)', fontSize: '0.83rem', textAlign: 'center', padding: '20px 0' }}>
                No notifications yet
              </p>
            ) : (
              notifications.slice(0, 15).map((n) => (
                <div
                  key={n.id}
                  onClick={() => { if (!n.is_read) markRead(n.id); }}
                  style={{
                    padding: '10px 12px', borderRadius: '10px', marginBottom: '6px',
                    background: n.is_read ? 'transparent' : 'var(--color-section-header-bg)',
                    cursor: n.is_read ? 'default' : 'pointer',
                    borderLeft: n.is_read ? 'none' : '3px solid var(--color-accent-primary)',
                    transition: 'background 0.15s',
                  }}
                >
                  <div style={{ fontWeight: 600, fontSize: '0.82rem', color: 'var(--color-text-primary)', marginBottom: '3px' }}>
                    {n.notification_type === 'PEST_ALERT' ? '🐛' : '📊'} {n.title}
                  </div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--color-text-secondary)' }}>
                    {n.message}
                  </div>
                  <div style={{ fontSize: '0.65rem', color: 'var(--color-text-secondary)', marginTop: '4px' }}>
                    {new Date(n.created_at).toLocaleString()}
                  </div>
                </div>
              ))
            )}
          </div>
        )}
      </div>

      {/* Nav Items */}
      <nav className="sidebar-nav">
        {navItems.map(({ path, label, icon: Icon }) => {
          const active = location.pathname === path;
          return (
            <button
              key={path}
              className={`sidebar-nav-item ${active ? 'active' : ''}`}
              onClick={() => { navigate(path); setShowNotifs(false); }}
              title={collapsed ? label : undefined}
            >
              <div className="sidebar-nav-icon">
                <Icon size={20} />
              </div>
              {!collapsed && (
                <span className="sidebar-nav-label">{label}</span>
              )}
              {active && <span className="sidebar-active-dot" />}
            </button>
          );
        })}
      </nav>

      {/* Footer User */}
      <div className="sidebar-footer">
        <button
          type="button"
          onClick={() => { logout(); navigate('/'); }}
          title="Log out"
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
            width: '100%',
            background: 'transparent',
            border: 'none',
            padding: 0,
            cursor: 'pointer',
            color: 'inherit',
            font: 'inherit',
            textAlign: 'left',
          }}
        >
          <div className="sidebar-user-avatar">
            {(farmer?.name?.[0] || 'F').toUpperCase()}
          </div>
          {!collapsed && (
            <div className="sidebar-user-info" style={{ flex: 1, minWidth: 0 }}>
              <span className="sidebar-user-name">{farmer?.name || 'Farmer'}</span>
              <span className="sidebar-user-role" style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <LogOut size={12} /> Log out
              </span>
            </div>
          )}
        </button>
      </div>
    </aside>
  );
};

export { Sidebar };

