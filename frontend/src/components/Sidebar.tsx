import React from 'react';
import { NavLink } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export const Sidebar: React.FC = () => {
  const { user } = useAuth();

  const navItems = [
    { label: 'Dashboard', path: '/dashboard', icon: 'dashboard' },
    { label: 'My Farms', path: '/farms', icon: 'agriculture' },
    { label: 'Register Farm', path: '/farms/register', icon: 'add_location_alt' },
    { label: 'Stress Analysis', path: '/stress-analysis', icon: 'water_drop' },
    { label: 'Weather', path: '/weather', icon: 'cloud_sync' },
    { label: 'Recommendations', path: '/recommendations', icon: 'psychology' },
    { label: 'Analytics', path: '/analytics', icon: 'insights' },
  ];

  const bottomNavItems = [
    { label: 'Notifications', path: '/notifications', icon: 'notifications' },
    { label: 'Settings', path: '/settings', icon: 'settings' },
  ];

  return (
    <nav className="hidden md:flex flex-col fixed left-0 top-0 h-full z-[60] p-4 w-sidebar-width rounded-r-xl bg-surface dark:bg-inverse-surface border-r border-outline-variant/30 shadow-xl">
      {/* Brand Header */}
      <div className="flex items-center gap-4 mb-8 p-2">
        <div className="w-12 h-12 rounded-full bg-primary-container text-on-primary-container flex items-center justify-center font-bold text-xl shadow-sm">
          <span className="material-symbols-outlined text-[28px]">psychology</span>
        </div>
        <div className="flex flex-col">
          <span className="text-headline-md font-headline-md text-primary font-bold">AgriNova AI</span>
          <span className="text-label-sm font-label-sm text-on-surface-variant">Precision Ag Intelligence</span>
        </div>
      </div>

      {/* Main Navigation */}
      <ul className="flex flex-col gap-2 flex-grow">
        {navItems.map((item) => (
          <li key={item.path}>
            <NavLink
              to={item.path}
              className={({ isActive }) =>
                `flex items-center gap-3 px-4 py-3 rounded-lg transition-all ease-in-out duration-300 ${
                  isActive
                    ? 'bg-primary-container text-on-primary-container font-semibold shadow-sm'
                    : 'text-on-surface-variant hover:bg-surface-variant/50 hover:translate-x-1'
                }`
              }
            >
              {({ isActive }) => (
                <>
                  <span
                    className="material-symbols-outlined"
                    style={{ fontVariationSettings: isActive ? "'FILL' 1" : "'FILL' 0" }}
                  >
                    {item.icon}
                  </span>
                  <span className="text-label-md font-label-md">{item.label}</span>
                </>
              )}
            </NavLink>
          </li>
        ))}
      </ul>

      {/* Footer Navigation */}
      <ul className="flex flex-col gap-2 mt-auto border-t border-outline-variant/30 pt-4">
        {bottomNavItems.map((item) => (
          <li key={item.path}>
            <NavLink
              to={item.path}
              className={({ isActive }) =>
                `flex items-center gap-3 px-4 py-3 rounded-lg transition-all ease-in-out duration-300 ${
                  isActive
                    ? 'bg-primary-container text-on-primary-container font-semibold'
                    : 'text-on-surface-variant hover:bg-surface-variant/50 hover:translate-x-1'
                }`
              }
            >
              <span className="material-symbols-outlined">{item.icon}</span>
              <span className="text-label-md font-label-md">{item.label}</span>
            </NavLink>
          </li>
        ))}
        {user && (
          <div className="pt-2 flex items-center justify-between text-xs text-on-surface-variant px-2">
            <span className="truncate">{user.email}</span>
          </div>
        )}
      </ul>
    </nav>
  );
};
