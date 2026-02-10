import axios from 'axios';

const API_HOST = process.env.REACT_APP_API_HOST || 'http://127.0.0.1:5000';
const API_PREFIX = '/api/v1';

const apiClient = axios.create({
  baseURL: API_HOST,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor
apiClient.interceptors.response.use(
  (response) => response.data,
  (error) => {
    console.error('API Error:', error.response || error);
    
    const message =
      error?.response?.data?.error ||
      error?.response?.data?.message ||
      error?.message ||
      'Request failed';
    return Promise.reject({ message });
  }
);

// Price endpoints
export const getPrices = (params = {}) => 
  apiClient.get(`${API_PREFIX}/prices/`, { params });

export const getReturns = (params = {}) => 
  apiClient.get(`${API_PREFIX}/prices/returns`, { params });

export const getPriceSummary = () => 
  apiClient.get(`${API_PREFIX}/prices/summary`);

// Event endpoints
export const getEvents = (params = {}) => 
  apiClient.get(`${API_PREFIX}/events/`, { params });

export const getEventImpact = (params = {}) => 
  apiClient.get(`${API_PREFIX}/events/impact`, { params });

// Change point endpoints
export const getChangePoints = () => 
  apiClient.get(`${API_PREFIX}/changepoint/`);

export const getChangePointImpact = (date, params = {}) => 
  apiClient.get(`${API_PREFIX}/changepoint/${date}/impact`, { params });

// Analysis endpoints
export const getAnalysisSummary = () => 
  apiClient.get(`${API_PREFIX}/analysis/summary`);

export const getEventCorrelation = () => 
  apiClient.get(`${API_PREFIX}/analysis/correlation`);

// Health check
export const checkHealth = () => 
  axios.get(`${API_HOST}/health`);

export const api = {
  getPrices,
  getReturns,
  getPriceSummary,
  getEvents,
  getEventImpact,
  getChangePoints,
  getChangePointImpact,
  getAnalysisSummary,
  getEventCorrelation,
  checkHealth
};

export { apiClient };
export default api;