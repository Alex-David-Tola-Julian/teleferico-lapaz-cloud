import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
});

export const getConfig = async () => {
  const res = await api.get('/config');
  return res.data;
};

export const getMetrics = async (filters) => {
  const res = await api.post('/metrics', filters);
  return res.data;
};

export const getMapData = async (filters) => {
  const res = await api.post('/map', filters);
  return res.data;
};

export const getTemporalData = async (filters) => {
  const res = await api.post('/temporal', filters);
  return res.data;
};

export const getHeatmap = async (filters, linea = "Todas") => {
  const res = await api.post('/heatmap', filters, { params: { linea } });
  return res.data;
};

export const getRanking = async (filters) => {
  const res = await api.post('/ranking', filters);
  return res.data;
};

export const getPrediction = async (filters, linea, dias_pred) => {
  const res = await api.post('/predict', { filters, linea, dias_pred });
  return res.data;
};
