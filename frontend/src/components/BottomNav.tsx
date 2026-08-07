import React from 'react';
import { NavLink } from 'react-router-dom';

export const BottomNav: React.FC = () => {
  const items = [
    { label: 'Dashboard', path: '/dashboard', icon: 'dashboard' },
    { label: 'My Farms', path: '/farms', icon: 'agriculture' },
    { label: 'Analytics', path: '/analytics', icon: 'analytics' },
    { label: 'Alerts', path: '/notifications', icon: 'notifications', badge: true },
  ];

  return (
    <nav className="md:hidden fixed bottom-0 left-0 w-full z-50 flex justify-around items-center h-20 px-4 pb-safe bg-surface/90 dark:bg-inverse-surface/90 backdrop-blur-lg border-t border-outline-variant/20 shadow-lg rounded-t-xl text-primary dark:text-secondary-fixed">
      {items.map((item) => (
        <NavLink
          key={item.path}
          to={item.path}
          className={({ isActive }) =>
            `flex flex-col items-center justify-center transition-all ${
              isActive
                ? 'bg-secondary-container dark:bg-secondary text-on-secondary-container dark:text-on-secondary rounded-full px-4 py-1 scale-105 duration-200'
                : 'text-on-surface-variant dark:text-outline hover:text-primary'
            }`
          }
        >
          {({ isActive }) => (
            <div className="relative flex flex-col items-center">
              <span
                className="material-symbols-outlined mb-1"
                style={{ fontVariationSettings: isActive ? "'FILL' 1" : "'FILL' 0" }}
              >
                {item.icon}
              </span>
              {item.badge && !isActive && (
                <span className="absolute top-0 right-0 w-2 h-2 bg-error rounded-full" />
              )}
              <span className="text-label-sm font-label-sm">{item.label}</span>
            </div>
          )}
        </NavLink>
      ))}
    </nav>
  );
};
