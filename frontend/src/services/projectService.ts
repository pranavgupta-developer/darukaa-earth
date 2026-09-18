/**
 * Project API service.
 */

import api from '../lib/api';
import type { Project, ProjectCreate, ProjectListResponse } from '../types';

export const projectService = {
  async create(data: ProjectCreate): Promise<Project> {
    const response = await api.post<Project>('/projects', data);
    return response.data;
  },

  async list(): Promise<ProjectListResponse> {
    const response = await api.get<ProjectListResponse>('/projects');
    return response.data;
  },

  async getById(id: string): Promise<Project> {
    const response = await api.get<Project>(`/projects/${id}`);
    return response.data;
  },

  async update(id: string, data: Partial<ProjectCreate>): Promise<Project> {
    const response = await api.put<Project>(`/projects/${id}`, data);
    return response.data;
  },

  async delete(id: string): Promise<void> {
    await api.delete(`/projects/${id}`);
  },
};
