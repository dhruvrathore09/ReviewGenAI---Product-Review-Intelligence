import axios from 'axios';

// Detect whether running locally or on a cloud host (e.g. Vercel, Render)
const isLocal = typeof window !== 'undefined' && 
  (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1');

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 
  (isLocal ? 'http://localhost:8000/api' : 'https://reviewgenai-api.onrender.com/api');

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000, // 60s timeout to allow free cloud tier cold starts (Render/Neon)
  headers: {
    'Content-Type': 'application/json',
  },
});

export const api = {
  // Service health check
  getHealth: async () => {
    const response = await apiClient.get('/health');
    return response.data;
  },

  // Dashboard & global analytics overview
  getDashboardOverview: async () => {
    const response = await apiClient.get('/dashboard/overview');
    return response.data;
  },

  // Deep review analytics hub data (category benchmarks, product duels, failure radar)
  getAnalyticsHub: async () => {
    const response = await apiClient.get('/dashboard/analytics-hub');
    return response.data;
  },

  // Category products for comparator dropdowns
  getCategoryProducts: async (category, limit = 50) => {
    const response = await apiClient.get('/dashboard/category-products', { params: { category, limit } });
    return response.data;
  },

  // Dynamic on-the-fly head-to-head comparison
  compareProducts: async (productA, productB) => {
    const response = await apiClient.get('/dashboard/compare', {
      params: { product_a: productA, product_b: productB },
    });
    return response.data;
  },

  // Paginated product catalog listing with filters
  getProducts: async (params = {}) => {
    const response = await apiClient.get('/products', { params });
    return response.data;
  },

  // Product keyword search (supports optional category and brand scoping)
  searchProducts: async (query, page = 1, pageSize = 20, category = null, brand = null) => {
    const params = { q: query, page, page_size: pageSize };
    if (category) params.category = category;
    if (brand) params.brand = brand;
    const response = await apiClient.get('/products/search', { params });
    return response.data;
  },

  // Single product detail
  getProduct: async (productId) => {
    const response = await apiClient.get(`/products/${encodeURIComponent(productId)}`);
    return response.data;
  },

  // Product statistics & star distribution
  getProductStatistics: async (productId) => {
    const response = await apiClient.get(`/products/${encodeURIComponent(productId)}/statistics`);
    return response.data;
  },

  // Executive product intelligence & overall review report
  getProductReport: async (productId) => {
    const response = await apiClient.get(`/products/${encodeURIComponent(productId)}/report`);
    return response.data;
  },

  // Paginated customer reviews for a product
  getProductReviews: async (productId, params = {}) => {
    const response = await apiClient.get(`/products/${encodeURIComponent(productId)}/reviews`, { params });
    return response.data;
  },

  // AI Review Intelligence Assistant
  chatWithAssistant: async (messages, query = null) => {
    const response = await apiClient.post('/assistant/chat', { messages, query });
    return response.data;
  },

  getStarterPrompts: async () => {
    const response = await apiClient.get('/assistant/starter-prompts');
    return response.data;
  },

  getAssistantStatus: async () => {
    const response = await apiClient.get('/assistant/status');
    return response.data;
  },
};

export default api;

