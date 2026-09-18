/**
 * Edit project page.
 */

import React, { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { projectService } from '../../services/projectService';
import type { ProjectType } from '../../types';
import Navbar from '../../components/Navbar';
import { AxiosError } from 'axios';

const PROJECT_TYPES: ProjectType[] = [
  'Carbon Sequestration',
  'Biodiversity Conservation',
  'Reforestation',
];

const EditProjectPage: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [projectType, setProjectType] = useState<ProjectType>('Carbon Sequestration');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    const fetchProject = async () => {
      if (!projectId) return;
      try {
        const project = await projectService.getById(projectId);
        setName(project.name);
        setDescription(project.description || '');
        setProjectType(project.project_type);
      } catch (err) {
        setError('Failed to load project details');
      } finally {
        setLoading(false);
      }
    };
    fetchProject();
  }, [projectId]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!projectId) return;
    
    setError('');
    setSaving(true);

    try {
      await projectService.update(projectId, {
        name,
        description: description || undefined,
        project_type: projectType,
      });
      navigate(`/projects/${projectId}`);
    } catch (err) {
      if (err instanceof AxiosError && err.response?.data?.error) {
        setError(err.response.data.error);
      } else {
        setError('Failed to update project');
      }
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="page-wrapper">
        <Navbar />
        <div className="loading-state">
          <div className="spinner" />
          <p>Loading project...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="page-wrapper">
      <Navbar />
      <main className="main-content">
        <div className="form-page">
          <button onClick={() => navigate(`/projects/${projectId}`)} className="btn btn-ghost back-btn">
            ← Back to Project
          </button>

          <div className="form-card">
            <h1>Edit Project</h1>
            <p className="form-subtitle">Update your environmental project settings</p>

            {error && <div className="alert alert-error">{error}</div>}

            <form onSubmit={handleSubmit} className="auth-form">
              <div className="form-group">
                <label htmlFor="project-name">Project Name</label>
                <input
                  id="project-name"
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  required
                  maxLength={255}
                />
              </div>

              <div className="form-group">
                <label htmlFor="project-type">Project Type</label>
                <select
                  id="project-type"
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
                <label htmlFor="project-desc">Description</label>
                <textarea
                  id="project-desc"
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  rows={4}
                  maxLength={2000}
                />
              </div>

              <div className="form-actions">
                <button
                  type="button"
                  onClick={() => navigate(`/projects/${projectId}`)}
                  className="btn btn-ghost"
                >
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary" disabled={saving}>
                  {saving ? 'Saving...' : 'Save Changes'}
                </button>
              </div>
            </form>
          </div>
        </div>
      </main>
    </div>
  );
};

export default EditProjectPage;
