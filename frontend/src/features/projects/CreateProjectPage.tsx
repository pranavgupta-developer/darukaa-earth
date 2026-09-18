/**
 * Create project page.
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { projectService } from '../../services/projectService';
import type { ProjectType } from '../../types';
import Navbar from '../../components/Navbar';
import { AxiosError } from 'axios';

const PROJECT_TYPES: ProjectType[] = [
  'Carbon Sequestration',
  'Biodiversity Conservation',
  'Reforestation',
];

const CreateProjectPage: React.FC = () => {
  const navigate = useNavigate();
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [projectType, setProjectType] = useState<ProjectType>('Carbon Sequestration');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const project = await projectService.create({
        name,
        description: description || undefined,
        project_type: projectType,
      });
      navigate(`/projects/${project.id}`);
    } catch (err) {
      if (err instanceof AxiosError && err.response?.data?.error) {
        setError(err.response.data.error);
      } else {
        setError('Failed to create project');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page-wrapper">
      <Navbar />
      <main className="main-content">
        <div className="form-page">
          <button onClick={() => navigate('/dashboard')} className="btn btn-ghost back-btn">
            ← Back to Projects
          </button>

          <div className="form-card">
            <h1>Create New Project</h1>
            <p className="form-subtitle">Set up a new environmental monitoring project</p>

            {error && <div className="alert alert-error">{error}</div>}

            <form onSubmit={handleSubmit} className="auth-form">
              <div className="form-group">
                <label htmlFor="project-name" className="form-label">Project Name</label>
                <input
                  id="project-name"
                  type="text"
                  className="form-input"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="e.g., Amazon Reforestation Initiative"
                  required
                  maxLength={255}
                />
              </div>

              <div className="form-group">
                <label htmlFor="project-type" className="form-label">Project Type</label>
                <select
                  id="project-type"
                  className="form-input"
                  value={projectType}
                  onChange={(e) => setProjectType(e.target.value as ProjectType)}
                  required
                >
                  {PROJECT_TYPES.map((type) => (
                    <option key={type} value={type}>
                      {type}
                    </option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label htmlFor="project-desc" className="form-label">Description</label>
                <textarea
                  id="project-desc"
                  className="form-input"
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="Describe the project goals and scope..."
                  rows={4}
                  maxLength={2000}
                />
              </div>

              <div className="form-actions">
                <button
                  type="button"
                  onClick={() => navigate('/dashboard')}
                  className="btn btn-ghost"
                >
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary" disabled={loading}>
                  {loading ? 'Creating...' : 'Create Project'}
                </button>
              </div>
            </form>
          </div>
        </div>
      </main>
    </div>
  );
};

export default CreateProjectPage;
