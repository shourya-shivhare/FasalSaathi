import React, { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import {
  LayoutDashboard,
  ScanLine,
  History,
  MessageCircle,
  TrendingUp,
  Landmark,
  Sprout,
  User,
  Leaf,
  ChevronLeft,
  ChevronRight,
  LogOut,
} from 'lucide-react';
import { useUserStore } from '../../stores/useUserStore.jsx';

const navItems = [
  { path: '/dashboard', label: 'Dashboard',     icon: LayoutDashboard },
  { path: '/detect',     label: 'Scan Crop',      icon: ScanLine },
  { path: '/chat',      label: 'AI Advisory',    icon: MessageCircle },
  // { path: '/market',    label: 'Market Prices',  icon: TrendingUp },
  { path: '/schemes',   label: 'Gov Schemes',    icon: Landmark },
  { path: '/crop-suggestion', label: 'Crop Suggest', icon: Sprout },
  { path: '/profile',   label: 'Profile',        icon: User },
];

const Sidebar = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { farmer, logout } = useUserStore();
  const [collapsed, setCollapsed] = useState(false);

  const toggle = () => {
    const next = !collapsed;
    setCollapsed(next);
    document.documentElement.style.setProperty('--sidebar-width', next ? '72px' : '240px');
  };

  return (
    <aside
      className="sidebar"
      style={{ width: collapsed ? '72px' : '240px' }}
    >
      {/* Logo + Collapse Toggle (same row) */}
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

      {/* Nav Items */}
      <nav className="sidebar-nav">
        {navItems.map(({ path, label, icon: Icon }) => {
          const active = location.pathname === path;
          return (
            <button
              key={path}
              className={`sidebar-nav-item ${active ? 'active' : ''}`}
              onClick={() => navigate(path)}
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
