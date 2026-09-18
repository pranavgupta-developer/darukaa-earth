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
            <h1>Projects</h1>
            <p className="page-subtitle">Manage your carbon and biodiversity projects</p>
          </div>
          <Link to="/projects/new" className="btn btn-primary">
            + New Project
          </Link>
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
              >
                <div className="project-card-header">
                  <span className="project-icon">{getTypeIcon(project.project_type)}</span>
                  <span className={getTypeBadgeClass(project.project_type)}>
                    {project.project_type}
                  </span>
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
