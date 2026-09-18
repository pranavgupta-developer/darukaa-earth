/**
 * Project list dashboard page.
 *
 * Displays all projects for the authenticated user with
 * loading, empty, and error states.
 */

import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { projectService } from '../../services/projectService';
import type { Project } from '../../types';
import Navbar from '../../components/Navbar';

const ProjectListPage: React.FC = () => {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    const fetchProjects = async () => {
      try {
        const data = await projectService.list();
        setProjects(data.projects);
      } catch {
        setError('Failed to load projects');
      } finally {
        setLoading(false);
      }
    };
    fetchProjects();
  }, []);

  const getTypeIcon = (type: string): string => {
    switch (type) {
      case 'Carbon Sequestration':
        return '🌿';
      case 'Biodiversity Conservation':
        return '🦜';
      case 'Reforestation':
        return '🌲';
      default:
        return '📁';
    }
  };

  const getTypeBadgeClass = (type: string): string => {
    switch (type) {
      case 'Carbon Sequestration':
        return 'badge badge-carbon';
      case 'Biodiversity Conservation':
        return 'badge badge-biodiversity';
      case 'Reforestation':
        return 'badge badge-reforestation';
      default:
        return 'badge';
    }
  };

  return (
    <div className="page-wrapper">
      <Navbar />
      <main className="main-content">
        <div className="page-header">
          <div>
            <h1>Dashboard</h1>
            <p className="page-subtitle">Overview of your environmental projects</p>
          </div>
          <Link to="/projects/new" className="btn btn-primary">
            + New Project
          </Link>
        </div>

        {!loading && !error && projects.length > 0 && (
          <div className="kpi-row" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1.5rem', marginBottom: '2rem' }}>
            <div className="summary-card" style={{ backgroundColor: 'var(--surface-light)' }}>
              <span className="summary-label">Total Projects</span>
              <span className="summary-value" style={{ fontSize: '2rem', color: 'var(--text-primary)' }}>{projects.length}</span>
            </div>
            <div className="summary-card" style={{ backgroundColor: 'var(--surface-light)' }}>
              <span className="summary-label">Total Sites Managed</span>
              <span className="summary-value" style={{ fontSize: '2rem', color: 'var(--text-primary)' }}>
                {projects.reduce((acc, p) => acc + p.site_count, 0)}
              </span>
            </div>
            <div className="summary-card" style={{ backgroundColor: 'var(--surface-light)' }}>
              <span className="summary-label">Carbon Projects</span>
              <span className="summary-value" style={{ fontSize: '2rem', color: 'var(--carbon)' }}>
                {projects.filter(p => p.project_type === 'Carbon Sequestration').length}
              </span>
            </div>
            <div className="summary-card" style={{ backgroundColor: 'var(--surface-light)' }}>
              <span className="summary-label">Biodiversity Projects</span>
              <span className="summary-value" style={{ fontSize: '2rem', color: 'var(--biodiversity)' }}>
                {projects.filter(p => p.project_type === 'Biodiversity Conservation').length}
              </span>
            </div>
          </div>
        )}

        <div className="page-header" style={{ marginTop: '1rem', borderTop: '1px solid var(--border)', paddingTop: '1.5rem' }}>
          <div>
            <h2>Your Projects</h2>
          </div>
        </div>

        {loading && (
          <div className="loading-state">
            <div className="spinner" />
            <p>Loading projects...</p>
          </div>
        )}

        {error && <div className="alert alert-error">{error}</div>}

        {!loading && !error && projects.length === 0 && (
          <div className="empty-state">
            <div className="empty-state-icon">🌍</div>
            <h2>No projects yet</h2>
            <p>Create your first project to start tracking environmental impact.</p>
            <Link to="/projects/new" className="btn btn-primary">
              Create Project
            </Link>
          </div>
        )}

        {!loading && projects.length > 0 && (
          <div className="project-grid">
            {projects.map((project) => (
              <div
                key={project.id}
                className="project-card"
                onClick={() => navigate(`/projects/${project.id}`)}
                role="button"
                tabIndex={0}
                onKeyDown={(e) => e.key === 'Enter' && navigate(`/projects/${project.id}`)}
                style={{ position: 'relative' }}
              >
                <div className="project-card-header">
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <span className="project-icon">{getTypeIcon(project.project_type)}</span>
                    <span className={getTypeBadgeClass(project.project_type)}>
                      {project.project_type}
                    </span>
                  </div>
                  <div style={{ display: 'flex', gap: '0.25rem' }} onClick={(e) => e.stopPropagation()}>
                    <button
                      className="btn btn-ghost btn-sm text-muted"
                      style={{ padding: '4px' }}
                      title="Edit project"
                      onClick={(e) => {
                        e.stopPropagation();
                        navigate(`/projects/${project.id}/edit`);
                      }}
                    >
                      ✎
                    </button>
                    <button
                      className="btn btn-ghost btn-sm text-muted"
                      style={{ padding: '4px' }}
                      title="Delete project"
                      onClick={async (e) => {
                        e.stopPropagation();
                        if (confirm('Are you sure you want to delete this project?')) {
                          try {
                            await projectService.delete(project.id);
                            setProjects((prev) => prev.filter((p) => p.id !== project.id));
                          } catch (err) {
                            alert('Failed to delete project');
                          }
                        }
                      }}
                    >
                      ✕
                    </button>
                  </div>
                </div>
                <h3 className="project-card-title">{project.name}</h3>
                <p className="project-card-desc">
                  {project.description || 'No description provided'}
                </p>
                <div className="project-card-footer">
                  <span className="project-card-meta">
                    📍 {project.site_count} site{project.site_count !== 1 ? 's' : ''}
                  </span>
                  <span className="project-card-meta">
                    {new Date(project.created_at).toLocaleDateString()}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
};

export default ProjectListPage;
