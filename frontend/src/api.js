/**
 * API Client for Resume Matcher Backend.
 *
 * Handles all HTTP requests to the FastAPI backend.
 */
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor for request logging
api.interceptors.request.use(
  (config) => {
    console.log(`[API] ${config.method?.toUpperCase()} ${config.url}`, config.data ? { data: config.data } : {});
    return config;
  },
  (error) => {
    console.error('[API] Request Error:', error);
    return Promise.reject(error);
  }
);

// Interceptor for response logging
api.interceptors.response.use(
  (response) => {
    console.log(`[API] ${response.status} ${response.config.url}`, response.data);
    return response;
  },
  (error) => {
    console.error('[API] Response Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

/**
 * Upload a resume file for parsing.
 * @param {File} file - The resume file (PDF or DOCX)
 * @returns {Promise} Response with parsed resume data
 */
export const uploadResume = async (file) => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await api.post('/upload-resume', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });

  return response.data;
};

/**
 * Parse resume from raw text.
 * @param {string} text - Raw resume text
 * @param {string} resumeId - Optional existing resume ID
 * @returns {Promise} Response with parsed resume data
 */
export const parseResumeText = async (text, resumeId = null) => {
  const params = new URLSearchParams();
  params.append('text', text);
  if (resumeId) params.append('resume_id', resumeId);

  const response = await api.post('/parse-text', {}, { params });
  return response.data;
};

/**
 * Search for jobs.
 * @param {Object} params - Search parameters
 * @param {string} params.role - Job role to search for
 * @param {string} params.location - Optional location
 * @param {Array} params.skills - Optional skills list
 * @param {number} params.maxResults - Maximum results (default: 20)
 * @returns {Promise} List of matching jobs
 */
export const searchJobs = async ({ role, location = null, skills = [], maxResults = 20 }) => {
  const params = new URLSearchParams();
  params.append('role', role);
  if (location) params.append('location', location);
  if (skills.length > 0) params.append('skills', skills.join(','));
  params.append('max_results', maxResults.toString());

  const response = await api.get('/jobs', { params });
  return response.data;
};

/**
 * Match a parsed resume to jobs.
 * @param {Object} params - Match parameters
 * @param {string} params.resumeId - The parsed resume ID
 * @param {string} params.role - Optional role filter
 * @param {string} params.location - Optional location filter
 * @returns {Promise} Matched jobs with scores
 */
export const matchJobs = async ({ resumeId, role = null, location = null }) => {
  const response = await api.post('/match-jobs', {
    resume_id: resumeId,
    role,
    location,
  });

  return response.data;
};

/**
 * Get a parsed resume by ID.
 * @param {string} resumeId - The resume ID
 * @returns {Promise} Resume data
 */
export const getResume = async (resumeId) => {
  const response = await api.get(`/resume/${resumeId}`);
  return response.data;
};

/**
 * Get system statistics.
 * @returns {Promise} System stats
 */
export const getStats = async () => {
  const response = await api.get('/stats');
  return response.data;
};

/**
 * Redirect to job application URL.
 * @param {string} url - The apply URL
 */
export const applyToJob = (url) => {
  window.open(url, '_blank');
};

/**
 * Health check endpoint.
 * @returns {Promise} Health status
 */
export const healthCheck = async () => {
  const response = await api.get('/health');
  return response.data;
};

export default api;
