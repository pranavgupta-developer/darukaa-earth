/**
 * Site API service.
 */

import api from '../lib/api';
import type { GeoJSONFeatureCollection, Site, SiteCreate, SiteListResponse } from '../types';

export const siteService = {
  async create(projectId: string, data: SiteCreate): Promise<Site> {
    const response = await api.post<Site>(`/projects/${projectId}/sites`, data);
    return response.data;
  },

  async listByProject(projectId: string): Promise<SiteListResponse> {
    const response = await api.get<SiteListResponse>(`/projects/${projectId}/sites`);
    return response.data;
  },

  async getGeoJSON(projectId: string): Promise<GeoJSONFeatureCollection> {
    const response = await api.get<GeoJSONFeatureCollection>(
      `/projects/${projectId}/sites/geojson`,
    );
    return response.data;
  },

  async getById(siteId: string): Promise<Site> {
    const response = await api.get<Site>(`/sites/${siteId}`);
    return response.data;
  },

  async update(siteId: string, data: Partial<SiteCreate>): Promise<Site> {
    const response = await api.put<Site>(`/sites/${siteId}`, data);
    return response.data;
  },

  async delete(siteId: string): Promise<void> {
    await api.delete(`/sites/${siteId}`);
  },
};
