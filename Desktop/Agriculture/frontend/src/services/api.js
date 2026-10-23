import axios from 'axios';

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  timeout: 8000,
});

export const getHealth = () => api.get('/api/health').then((r) => r.data);
export const getDistricts = () => api.get('/api/districts').then((r) => r.data);
export const getRisk = (params) => api.get('/api/risk', { params }).then((r) => r.data);
export const getYieldPrediction = (params) => api.get('/api/yield-prediction', { params }).then((r) => r.data);
export const getAnalytics = (params) => api.get('/api/analytics', { params }).then((r) => r.data);
