/**
 * Project detail page.
 *
 * Displays project info, interactive Mapbox map with site polygons,
 * site list, and site creation via polygon drawing.
 */

import React, { useCallback, useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { projectService } from '../../services/projectService';
import { siteService } from '../../services/siteService';
import type { GeoJSONFeatureCollection, GeoJSONPolygon, Project, Site } from '../../types';
import Navbar from '../../components/Navbar';
import MapView from '../map/MapView';
import AnalyticsDashboard from '../analytics/AnalyticsDashboard';
import { AxiosError } from 'axios';

const ProjectDetailPage: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();

  const [project, setProject] = useState<Project | null>(null);
  const [sites, setSites] = useState<Site[]>([]);
  const [geojson, setGeojson] = useState<GeoJSONFeatureCollection | null>(null);
  const [selectedSiteId, setSelectedSiteId] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // Site creation state
  const [isDrawing, setIsDrawing] = useState(false);
  const [drawnPolygon, setDrawnPolygon] = useState<GeoJSONPolygon | null>(null);
  const [siteName, setSiteName] = useState('');
  const [siteDesc, setSiteDesc] = useState('');
  const [creating, setCreating] = useState(false);
  const [createError, setCreateError] = useState('');

  const fetchData = useCallback(async () => {
    if (!projectId) return;
    try {
      const [proj, siteList, geoData] = await Promise.all([
        projectService.getById(projectId),
        siteService.listByProject(projectId),
        siteService.getGeoJSON(projectId),
      ]);
      setProject(proj);
      setSites(siteList.sites);
      setGeojson(geoData);
    } catch {
      setError('Failed to load project data');
    } finally {
      setLoading(false);
    }
  }, [projectId]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handlePolygonDrawn = (polygon: GeoJSONPolygon) => {
    setDrawnPolygon(polygon);
    setIsDrawing(false);
  };

  const handleCreateSite = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!drawnPolygon || !projectId) return;

    setCreating(true);
    setCreateError('');

    try {
      await siteService.create(projectId, {
        name: siteName,
        description: siteDesc || undefined,
        geometry: drawnPolygon,
      });
      // Reset and refresh
      setDrawnPolygon(null);
      setSiteName('');
      setSiteDesc('');
      await fetchData();
    } catch (err) {
      if (err instanceof AxiosError && err.response?.data?.error) {
        setCreateError(err.response.data.error);
      } else {
        setCreateError('Failed to create site');
      }
    } finally {
      setCreating(false);
    }
  };

  const handleSiteClick = (siteId: string) => {
    setSelectedSiteId(siteId === selectedSiteId ? null : siteId);
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

  if (error || !project) {
    return (
      <div className="page-wrapper">
        <Navbar />
        <div className="main-content">
          <div className="alert alert-error">{error || 'Project not found'}</div>
          <button onClick={() => navigate('/dashboard')} className="btn btn-ghost">
            ← Back to Projects
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="page-wrapper">
      <Navbar />
      <main className="project-detail">
        {/* Header */}
        <div className="project-detail-header">
          <button onClick={() => navigate('/dashboard')} className="btn btn-ghost back-btn">
            ← Back
          </button>
          <div className="project-detail-info">
            <h1>{project.name}</h1>
            <span className="badge badge-outline">{project.project_type}</span>
            <div style={{ marginLeft: 'auto', display: 'flex', gap: '0.5rem' }}>
              <button onClick={() => navigate(`/projects/${project.id}/edit`)} className="btn btn-ghost btn-sm">
                Edit Project
              </button>
              <button 
                onClick={async () => {
                  if (confirm('Are you sure you want to delete this project? This will permanently delete all its sites and analytics.')) {
                    try {
                      await projectService.delete(project.id);
                      navigate('/dashboard');
                    } catch (err) {
                      alert('Failed to delete project.');
                    }
                  }
                }} 
                className="btn btn-danger btn-sm"
              >
                Delete Project
              </button>
            </div>
          </div>
          {project.description && <p className="project-detail-desc">{project.description}</p>}
        </div>

        {/* Map + Sidebar layout */}
        <div className="project-layout">
          {/* Map */}
          <div className="map-container">
            <div className="map-toolbar">
              <button
                onClick={() => setIsDrawing(!isDrawing)}
                className={`btn btn-sm ${isDrawing ? 'btn-danger' : 'btn-primary'}`}
              >
                {isDrawing ? '✕ Cancel Drawing' : '✏️ Draw Site Polygon'}
              </button>
            </div>
            <MapView
              geojson={geojson}
              isDrawing={isDrawing}
              onPolygonDrawn={handlePolygonDrawn}
              onSiteClick={handleSiteClick}
              selectedSiteId={selectedSiteId}
            />
          </div>

          {/* Sidebar */}
          <div className="project-sidebar">
            {/* Site creation form */}
            {drawnPolygon && (
              <div className="sidebar-card">
                <h3>Create Site</h3>
                {createError && <div className="alert alert-error alert-sm">{createError}</div>}
                <form onSubmit={handleCreateSite}>
                  <div className="form-group">
                    <label htmlFor="site-name">Site Name</label>
                    <input
                      id="site-name"
                      type="text"
                      value={siteName}
                      onChange={(e) => setSiteName(e.target.value)}
                      placeholder="e.g., North Canopy Zone"
                      required
                    />
                  </div>
                  <div className="form-group">
                    <label htmlFor="site-desc">Description</label>
                    <textarea
                      id="site-desc"
                      value={siteDesc}
                      onChange={(e) => setSiteDesc(e.target.value)}
                      placeholder="Optional description..."
                      rows={2}
                    />
                  </div>
                  <div className="form-actions">
                    <button
                      type="button"
                      onClick={() => setDrawnPolygon(null)}
                      className="btn btn-ghost btn-sm"
                    >
                      Discard
                    </button>
                    <button type="submit" className="btn btn-primary btn-sm" disabled={creating}>
                      {creating ? 'Saving...' : 'Save Site'}
                    </button>
                  </div>
                </form>
              </div>
            )}

            {/* Site list */}
            <div className="sidebar-card">
              <h3>Sites ({sites.length})</h3>
              {sites.length === 0 ? (
                <p className="text-muted">Draw a polygon on the map to add sites.</p>
              ) : (
                <ul className="site-list">
                  {sites.map((site) => (
                    <li
                      key={site.id}
                      className={`site-list-item ${selectedSiteId === site.id ? 'active' : ''}`}
                      onClick={() => handleSiteClick(site.id)}
                      role="button"
                      tabIndex={0}
                      onKeyDown={(e) => e.key === 'Enter' && handleSiteClick(site.id)}
                    >
                      <div className="site-list-item-name">{site.name}</div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                        <div className="site-list-item-meta">
                          {site.area_hectares ? `${site.area_hectares.toFixed(1)} ha` : 'N/A'}
                        </div>
                        <button 
                          className="btn btn-ghost btn-sm text-muted"
                          style={{ padding: '0 4px' }}
                          onClick={async (e) => {
                            e.stopPropagation();
                            if (confirm('Delete this site?')) {
                              try {
                                await siteService.delete(site.id);
                                if (selectedSiteId === site.id) setSelectedSiteId(null);
                                await fetchData();
                              } catch (err) {
                                alert('Failed to delete site.');
                              }
                            }
                          }}
                          title="Delete site"
                        >
                          ✕
                        </button>
                      </div>
                    </li>
                  ))}
                </ul>
              )}
            </div>

            {/* Analytics panel */}
            {selectedSiteId && (
              <div className="sidebar-card sidebar-card-analytics">
                <AnalyticsDashboard siteId={selectedSiteId} />
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
};

export default ProjectDetailPage;
