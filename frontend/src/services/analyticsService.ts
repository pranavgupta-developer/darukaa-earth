/**
 * Analytics API service.
 */

import api from '../lib/api';
import type { SiteAnalyticsResponse, GlobalAnalyticsResponse } from '../types';

export const analyticsService = {
  async getSiteAnalytics(
    siteId: string,
    startDate?: string,
    endDate?: string,
  ): Promise<SiteAnalyticsResponse> {
    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);

    const query = params.toString() ? `?${params.toString()}` : '';
    const response = await api.get<SiteAnalyticsResponse>(`/sites/${siteId}/analytics${query}`);
    return response.data;
  },

  async getGlobalAnalytics(params: {
    projectIds?: string[];
    siteIds?: string[];
    projectTypes?: string[];
    startDate?: string;
    endDate?: string;
    compareBy?: 'site' | 'project';
  }): Promise<GlobalAnalyticsResponse> {
    const searchParams = new URLSearchParams();
    if (params.projectIds) {
      params.projectIds.forEach(id => searchParams.append('project_ids', id));
    }
    if (params.siteIds) {
      params.siteIds.forEach(id => searchParams.append('site_ids', id));
    }
    if (params.projectTypes) {
      params.projectTypes.forEach(type => searchParams.append('project_types', type));
    }
    if (params.startDate) searchParams.append('start_date', params.startDate);
    if (params.endDate) searchParams.append('end_date', params.endDate);
    if (params.compareBy) searchParams.append('compare_by', params.compareBy);

    const query = searchParams.toString() ? `?${searchParams.toString()}` : '';
    const response = await api.get<GlobalAnalyticsResponse>(`/analytics/global${query}`);
    return response.data;
  },
};
