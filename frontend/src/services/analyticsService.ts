/**
 * Analytics API service.
 */

import api from '../lib/api';
import type { SiteAnalyticsResponse } from '../types';

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
};
