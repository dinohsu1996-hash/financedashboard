// frontend/lib/api.ts
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api',
});

// ... previous functions ...
export const fetchNewsSummary = async (urls: string[], topic: string) => {
  const response = await api.post('/news', { urls, topic });
  return response.data;
};

export const fetchMacroData = async (seriesId: string, label: string, years: number = 2) => {
  const response = await api.post('/macro/data', { series_id: seriesId, label, years });
  return response.data;
};

export const synthesizeMacro = async (groupedIndicators: any, analysisFocus: string) => {
  const response = await api.post('/macro/synthesize', { grouped_indicators: groupedIndicators, analysis_focus: analysisFocus });
  return response.data;
};

// ... new stock functions ...

export const fetchStockOverview = async (ticker: string) => {
  const response = await api.get(`/stock/${ticker}/overview`);
  return response.data;
};

export const fetchStockHistory = async (ticker: string, period: string = "1y", interval: string = "1d") => {
  const response = await api.get(`/stock/${ticker}/history`, { params: { period, interval } });
  return response.data;
};

export const fetchStockFinancials = async (ticker: string, statementType: string, source: string = "yahoo") => {
  const response = await api.get(`/stock/${ticker}/financials/${statementType}`, { params: { source } });
  return response.data;
};
