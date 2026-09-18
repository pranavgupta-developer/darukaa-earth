/**
 * Navbar component with auth state and navigation.
 */

import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../features/auth/AuthContext';

const Navbar: React.FC = () => {
  const { user, logout, isAuthenticated } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <nav className="navbar">
      <Link to="/dashboard" className="navbar-brand">
        🌍 Darukaa.Earth
      </Link>
      {isAuthenticated && (
        <div className="navbar-actions">
          <Link to="/settings" className="navbar-user" style={{ textDecoration: 'none' }}>
            {user?.name}
          </Link>
          <button onClick={handleLogout} className="btn btn-ghost btn-sm">
            Sign Out
          </button>
        </div>
      )}
    </nav>
  );
};

export default Navbar;
