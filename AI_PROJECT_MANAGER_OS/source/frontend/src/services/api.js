import axios from 'axios';

const API_BASE_URL = '/api';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth services
export const authService = {
  login: async (username, password) => {
    const response = await api.post('/auth/login', { username, password });
    return response.data;
  },
  
  logout: async () => {
    await api.post('/auth/logout');
  },
  
  getCurrentUser: async () => {
    const response = await api.get('/auth/me');
    return response.data;
  },
};

// Project services
export const projectService = {
  getAll: async () => {
    const response = await api.get('/projects');
    return response.data;
  },
  
  getById: async (id) => {
    const response = await api.get(`/projects/${id}`);
    return response.data;
  },
  
  create: async (data) => {
    const response = await api.post('/projects', data);
    return response.data;
  },
  
  update: async (id, data) => {
    const response = await api.put(`/projects/${id}`, data);
    return response.data;
  },
  
  delete: async (id) => {
    const response = await api.delete(`/projects/${id}`);
    return response.data;
  },
  
  clone: async (id, newName) => {
    const response = await api.post(`/projects/${id}/clone`, { newName });
    return response.data;
  },
  
  archive: async (id) => {
    const response = await api.post(`/projects/${id}/archive`);
    return response.data;
  },
  
  restore: async (id) => {
    const response = await api.post(`/projects/${id}/restore`);
    return response.data;
  },
};

// Session services
export const sessionService = {
  getByProject: async (projectId) => {
    const response = await api.get(`/sessions/project/${projectId}`);
    return response.data;
  },
  
  getById: async (id) => {
    const response = await api.get(`/sessions/${id}`);
    return response.data;
  },
  
  create: async (projectId, name) => {
    const response = await api.post('/sessions', { project_id: projectId, name });
    return response.data;
  },
  
  update: async (id, data) => {
    const response = await api.put(`/sessions/${id}`, data);
    return response.data;
  },
  
  delete: async (id) => {
    const response = await api.delete(`/sessions/${id}`);
    return response.data;
  },
  
  generateSummary: async (id) => {
    const response = await api.post(`/sessions/${id}/summary`);
    return response.data;
  },
  
  getHistory: async (sessionId, page = 1, limit = 50) => {
    const response = await api.get(`/sessions/${sessionId}/history`, { 
      params: { page, limit } 
    });
    return response.data;
  },
};

// Chat services
export const chatService = {
  send: async (sessionId, content) => {
    const response = await api.post('/chat/send', { session_id: sessionId, content });
    return response.data;
  },
  
  getHistory: async (sessionId, page = 1, limit = 50) => {
    const response = await api.get(`/chat/history/${sessionId}`, { 
      params: { page, limit } 
    });
    return response.data;
  },
  
  retry: async (sessionId) => {
    const response = await api.post('/chat/retry', { session_id: sessionId });
    return response.data;
  },
  
  export: async (sessionId, format = 'markdown') => {
    const response = await api.post('/chat/export', { session_id: sessionId, format });
    return response.data;
  },
};

// File services
export const fileService = {
  getTree: async (projectId, root = '') => {
    const response = await api.get('/files/tree', { 
      params: { project_id: projectId, root } 
    });
    return response.data;
  },
  
  getContent: async (projectId, filePath) => {
    const response = await api.get('/files/content', { 
      params: { project_id: projectId, file_path: filePath } 
    });
    return response.data;
  },
  
  create: async (projectId, path, type = 'file', content = '') => {
    const response = await api.post('/files', { 
      project_id: projectId, 
      path, 
      type, 
      content 
    });
    return response.data;
  },
  
  update: async (projectId, path, content) => {
    const response = await api.put('/files', { 
      project_id: projectId, 
      path, 
      content 
    });
    return response.data;
  },
  
  delete: async (projectId, path) => {
    const response = await api.delete('/files', { 
      params: { project_id: projectId, path } 
    });
    return response.data;
  },
  
  rename: async (projectId, oldPath, newPath) => {
    const response = await api.put('/files/rename', { 
      project_id: projectId, 
      path: oldPath, 
      newPath 
    });
    return response.data;
  },
};

// Git services
export const gitService = {
  getStatus: async (projectId) => {
    const response = await api.get('/git/status', { 
      params: { project_id: projectId } 
    });
    return response.data;
  },
  
  init: async (projectId) => {
    const response = await api.post('/git/init', { project_id: projectId });
    return response.data;
  },
  
  commit: async (projectId, message, files = []) => {
    const response = await api.post('/git/commit', { 
      project_id: projectId, 
      message, 
      files 
    });
    return response.data;
  },
  
  push: async (projectId, remote = 'origin', branch) => {
    const response = await api.post('/git/push', { 
      project_id: projectId, 
      remote, 
      branch 
    });
    return response.data;
  },
  
  pull: async (projectId, remote = 'origin', branch) => {
    const response = await api.post('/git/pull', { 
      project_id: projectId, 
      remote, 
      branch 
    });
    return response.data;
  },
  
  getBranches: async (projectId) => {
    const response = await api.get('/git/branches', { 
      params: { project_id: projectId } 
    });
    return response.data;
  },
  
  createBranch: async (projectId, name, from = 'HEAD') => {
    const response = await api.post('/git/branch', { 
      project_id: projectId, 
      name, 
      from 
    });
    return response.data;
  },
  
  merge: async (projectId, branch) => {
    const response = await api.post('/git/merge', { 
      project_id: projectId, 
      branch 
    });
    return response.data;
  },
  
  getDiff: async (projectId, file) => {
    const response = await api.get('/git/diff', { 
      params: { project_id: projectId, file } 
    });
    return response.data;
  },
  
  getLog: async (projectId, limit = 20) => {
    const response = await api.get('/git/log', { 
      params: { project_id: projectId, limit } 
    });
    return response.data;
  },
};

export default api;
