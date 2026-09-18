/**
 * Shared TypeScript type definitions for the Darukaa.Earth frontend.
 *
 * These types mirror the backend Pydantic response schemas to ensure
 * type-safe API communication.
 */

// ─── User & Auth ─────────────────────────────────────────────────────────

export interface User {
  id: string;
  email: string;
  name: string;
  created_at: string;
  updated_at: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  name: string;
}

// ─── Projects ────────────────────────────────────────────────────────────

export type ProjectType =
  | 'Carbon Sequestration'
  | 'Biodiversity Conservation'
  | 'Reforestation';

export interface Project {
  id: string;
  name: string;
  description: string | null;
  project_type: ProjectType;
  owner_id: string;
  created_at: string;
  updated_at: string;
  site_count: number;
}

export interface ProjectCreate {
  name: string;
  description?: string;
  project_type: ProjectType;
}

export interface ProjectListResponse {
  projects: Project[];
  total: number;
}

// ─── Sites ───────────────────────────────────────────────────────────────

export interface GeoJSONPolygon {
  type: 'Polygon';
  coordinates: number[][][];
}

export interface SiteCreate {
  name: string;
  description?: string;
  geometry: GeoJSONPolygon;
}

export interface Site {
  id: string;
  name: string;
  description: string | null;
  project_id: string;
  geometry: GeoJSONPolygon;
  area_hectares: number | null;
  created_at: string;
  updated_at: string;
}

export interface SiteListResponse {
  sites: Site[];
  total: number;
}

export interface GeoJSONFeature {
  type: 'Feature';
  id: string;
  geometry: GeoJSONPolygon;
  properties: {
    id: string;
    name: string;
    description: string | null;
    area_hectares: number | null;
    project_id: string;
  };
}

export interface GeoJSONFeatureCollection {
  type: 'FeatureCollection';
  features: GeoJSONFeature[];
}

// ─── Analytics ───────────────────────────────────────────────────────────

export interface AnalyticsDataPoint {
  recorded_date: string;
  ndvi: number | null;
  carbon_sequestration_tons: number | null;
  biodiversity_index: number | null;
  canopy_cover_pct: number | null;
}

export interface AnalyticsSummary {
  latest_value: number | null;
  average: number | null;
  min_value: number | null;
  max_value: number | null;
  trend_pct: number | null;
}

export interface SiteAnalyticsResponse {
  site_id: string;
  site_name: string;
  start_date: string | null;
  end_date: string | null;
  total_records: number;
  data: AnalyticsDataPoint[];
  summary: Record<string, AnalyticsSummary>;
}

// ─── Common ──────────────────────────────────────────────────────────────

export interface ApiError {
  error: string;
  detail?: unknown;
}
