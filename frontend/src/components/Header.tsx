import React from 'react';
import { useAuth } from '../context/AuthContext';
import { Link } from 'react-router-dom';

interface HeaderProps {
  title?: string;
  onMenuClick?: () => void;
}

export const Header: React.FC<HeaderProps> = ({ title = 'AgriNova', onMenuClick }) => {
  const { user } = useAuth();

  return (
    <header className="fixed top-0 w-full z-50 flex justify-between items-center px-gutter h-16 bg-surface/80 dark:bg-inverse-surface/80 backdrop-blur-md border-b border-outline-variant/30 shadow-sm text-primary dark:text-primary-fixed md:pl-[296px]">
      <div className="flex items-center gap-3">
        <button
          onClick={onMenuClick}
          className="md:hidden text-on-surface-variant hover:bg-primary/10 p-2 rounded-full flex items-center justify-center transition-colors"
        >
          <span className="material-symbols-outlined text-headline-md">menu</span>
        </button>
        <span className="text-headline-md font-headline-md font-bold text-primary dark:text-primary-fixed">
          {title}
        </span>
      </div>

      <div className="flex items-center gap-4">
        <div className="hidden md:flex bg-surface-container-highest rounded-full px-4 py-2 items-center text-on-surface-variant focus-within:ring-2 focus-within:ring-primary">
          <span className="material-symbols-outlined mr-2 text-outline">search</span>
          <input
            className="bg-transparent border-none focus:ring-0 text-label-md w-48 outline-none placeholder:text-on-surface-variant/50 text-on-surface"
            placeholder="Search fields & farms..."
            type="text"
          />
        </div>

        <Link to="/settings" className="flex items-center gap-2">
          <div className="w-9 h-9 rounded-full bg-primary-container text-on-primary-container flex items-center justify-center font-bold text-sm border border-outline-variant/30 hover:scale-105 transition-transform">
            {user?.full_name ? user.full_name.charAt(0).toUpperCase() : 'U'}
          </div>
        </Link>
      </div>
    </header>
  );
};
