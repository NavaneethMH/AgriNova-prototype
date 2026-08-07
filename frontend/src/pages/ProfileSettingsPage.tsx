import React from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';

export const ProfileSettingsPage: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="space-y-6 max-w-3xl mx-auto">
      <div>
        <h2 className="text-headline-lg font-headline-lg text-on-surface">Account & Settings</h2>
        <p className="text-body-md text-on-surface-variant">Manage your profile, preferences, and security</p>
      </div>

      {/* User Card */}
      <div className="bg-surface-container-lowest rounded-xl border border-outline-variant/20 p-6 shadow-sm flex items-center gap-6">
        <div className="w-16 h-16 rounded-full bg-primary-container text-on-primary-container flex items-center justify-center font-bold text-2xl shadow-sm">
          {user?.full_name?.charAt(0).toUpperCase() || 'U'}
        </div>
        <div>
          <h3 className="text-headline-md font-headline-md text-on-surface">{user?.full_name || 'User'}</h3>
          <p className="text-body-md text-on-surface-variant">{user?.email}</p>
          <span className="inline-block mt-1 px-3 py-0.5 rounded-full bg-primary-container/20 text-primary text-xs font-semibold uppercase">
            Role: {user?.role || 'Farmer'}
          </span>
        </div>
      </div>

      {/* Settings Form Card */}
      <div className="bg-surface-container-lowest rounded-xl border border-outline-variant/20 p-6 shadow-sm space-y-4">
        <h3 className="text-headline-md font-headline-md text-on-surface mb-2">Profile Information</h3>
        <div className="space-y-4">
          <div>
            <label className="block text-label-md text-on-surface-variant mb-1">Full Name</label>
            <input type="text" defaultValue={user?.full_name || ''} className="input-field" readOnly />
          </div>
          <div>
            <label className="block text-label-md text-on-surface-variant mb-1">Email Address</label>
            <input type="email" defaultValue={user?.email || ''} className="input-field" readOnly />
          </div>
          <div>
            <label className="block text-label-md text-on-surface-variant mb-1">Organization / Farm Name</label>
            <input type="text" defaultValue={user?.organization || 'Green Valley Farms'} className="input-field" />
          </div>
        </div>

        <div className="pt-6 border-t border-outline-variant/20 flex justify-between items-center">
          <button
            onClick={handleLogout}
            className="px-6 py-2.5 bg-error-container text-on-error-container rounded-xl text-label-md font-semibold hover:bg-error hover:text-white transition-colors"
          >
            Sign Out of Account
          </button>
        </div>
      </div>
    </div>
  );
};
