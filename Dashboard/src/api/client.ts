/**
 * API Client for Callbot Dashboard
 * This client communicates with the FastAPI backend
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

interface RequestOptions extends RequestInit {
  params?: Record<string, string | number | boolean>;
}

async function apiCall<T>(
  endpoint: string,
  options: RequestOptions = {}
): Promise<T> {
  const { params, ...requestOptions } = options;

  let url = `${API_BASE_URL}${endpoint}`;

  if (params) {
    const queryParams = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
      queryParams.append(key, String(value));
    });
    url += `?${queryParams.toString()}`;
  }

  const response = await fetch(url, {
    headers: {
      'Content-Type': 'application/json',
      ...requestOptions.headers,
    },
    ...requestOptions,
  });

  if (!response.ok) {
    throw new Error(`API Error: ${response.status} ${response.statusText}`);
  }

  return response.json() as Promise<T>;
}

export const apiClient = {
  // Interactions endpoints
  getInteractions: (limit = 50, offset = 0, filters?: { status?: string; channel?: string }) =>
    apiCall('/interactions', {
      params: { limit, offset, ...filters },
    }),

  getInteraction: (id: string) =>
    apiCall(`/interactions/${id}`),

  // Views endpoints
  getActiveInteractions: (limit = 100) =>
    apiCall('/views/active-interactions', { params: { limit } }),

  getPendingHandoffs: (limit = 100) =>
    apiCall('/views/pending-handoffs', { params: { limit } }),

  getDailyStats: (limit = 60) =>
    apiCall('/views/daily-stats', { params: { limit } }),

  getStatisticsSummary: () =>
    apiCall('/views/statistics/summary'),

  getStatisticsByIntent: () =>
    apiCall('/views/statistics/by-intent'),

  getStatisticsByChannel: () =>
    apiCall('/views/statistics/by-channel'),

  getSatisfactionDaily: (limit = 90) =>
  apiCall('/views/satisfaction/daily', { params: { limit } }),

  getSatisfactionByIntent: () =>
    apiCall('/views/satisfaction/by-intent'),

  getUnsatisfiedInteractions: (limit = 50) =>
    apiCall('/views/satisfaction/unsatisfied', { params: { limit } }),

  getSatisfactionByAction: () =>
    apiCall('/views/satisfaction/by-action'),

};

export default apiClient;
