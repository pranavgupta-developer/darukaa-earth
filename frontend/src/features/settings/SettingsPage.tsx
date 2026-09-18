/**
 * Settings Page
 * User profile and preferences
 */

import React from 'react';
import Navbar from '../../components/Navbar';
import { useAuth } from '../auth/AuthContext';

const SettingsPage: React.FC = () => {
  const { user, logout } = useAuth();

  return (
    <div className="page-wrapper">
      <Navbar />
      <main className="main-content">
        <div className="form-page" style={{ maxWidth: '800px', margin: '0 auto', paddingTop: '2rem' }}>
          <div className="form-card">
            <h1>Account Settings</h1>
            <p className="form-subtitle">Manage your personal information and preferences.</p>

            <div className="settings-section" style={{ marginTop: '2rem' }}>
              <h3>Profile</h3>
              <div className="form-group" style={{ marginTop: '1rem' }}>
                <label>Name</label>
                <input type="text" value={user?.name || ''} disabled className="input-disabled" />
              </div>
              <div className="form-group">
                <label>Email Address</label>
                <input type="email" value={user?.email || ''} disabled className="input-disabled" />
              </div>
              <p className="text-muted" style={{ fontSize: '0.85rem' }}>
                Please contact support to change your email address or name.
              </p>
            </div>

            <div className="settings-section" style={{ marginTop: '3rem', borderTop: '1px solid var(--border)', paddingTop: '2rem' }}>
              <h3 style={{ color: 'var(--error)' }}>Danger Zone</h3>
              <p className="text-muted" style={{ marginBottom: '1rem' }}>
                Sign out of your account on this device.
              </p>
              <button onClick={logout} className="btn btn-danger">
                Sign Out
              </button>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default SettingsPage;
