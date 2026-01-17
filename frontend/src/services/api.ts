/**
 * API client for communicating with the FastAPI backend.
 */

import axios from 'axios';
import type {
  ApplicationFormData,
  ApplicationResponse,
  Constants,
  DMOSubmission,
  DMOSubmissionCreate,
  MonthlyReportSummary,
  Payment,
  PaymentCreate,
  PaymentDocument,
  PaymentUpdate,
  PaymentVerify,
} from '../types/application';

const API_BASE = import.meta.env.VITE_API_URL || '/api';

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for adding auth token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/admin/login';
    }
    return Promise.reject(error);
  }
);

// Public API endpoints
export const publicApi = {
  /**
   * Fetch form constants (banks, categories, etc.)
   */
  getConstants: async (): Promise<Constants> => {
    const response = await api.get('/constants');
    return response.data;
  },

  /**
   * Submit a new application.
   */
  submitApplication: async (data: ApplicationFormData): Promise<ApplicationResponse> => {
    const response = await api.post('/applications', data);
    return response.data;
  },

  /**
   * Get application by ID.
   */
  getApplication: async (id: number): Promise<ApplicationResponse> => {
    const response = await api.get(`/applications/${id}`);
    return response.data;
  },

  /**
   * Get PDF download URL for an application.
   */
  getPdfUrl: (id: number): string => {
    return `${API_BASE}/applications/${id}/pdf`;
  },

  /**
   * Download PDF for an application.
   */
  downloadPdf: async (id: number): Promise<Blob> => {
    const response = await api.get(`/applications/${id}/pdf`, {
      responseType: 'blob',
    });
    return response.data;
  },
};

// Admin API endpoints
export const adminApi = {
  /**
   * Login and get JWT token.
   */
  login: async (username: string, password: string): Promise<{ access_token: string }> => {
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);

    const response = await api.post('/auth/login', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });
    return response.data;
  },

  /**
   * Get current user info.
   */
  getCurrentUser: async (): Promise<{ username: string; is_admin: boolean }> => {
    const response = await api.get('/auth/me');
    return response.data;
  },

  /**
   * Get dashboard summary metrics.
   */
  getSummary: async () => {
    const response = await api.get('/admin/summary');
    return response.data;
  },

  /**
   * Get analytics data for charts.
   */
  getAnalytics: async () => {
    const response = await api.get('/admin/analytics');
    return response.data;
  },

  /**
   * Get paginated list of applications.
   */
  getApplications: async (params: {
    page?: number;
    page_size?: number;
    applicant_types?: string[];
    tenors?: string[];
    start_date?: string;
    end_date?: string;
    min_value?: number;
    max_value?: number;
    is_resident?: boolean;
    payment_statuses?: string[];
    search?: string;
  }) => {
    const response = await api.get('/admin/applications', { params });
    return response.data;
  },

  /**
   * Export applications to CSV.
   */
  exportCsv: async (params: Record<string, unknown>): Promise<Blob> => {
    const response = await api.get('/admin/export/csv', {
      params,
      responseType: 'blob',
    });
    return response.data;
  },

  /**
   * Export applications to Excel.
   */
  exportExcel: async (params: Record<string, unknown>): Promise<Blob> => {
    const response = await api.get('/admin/export/excel', {
      params,
      responseType: 'blob',
    });
    return response.data;
  },

  // ==========================================================================
  // PAYMENT MANAGEMENT
  // ==========================================================================

  /**
   * Record a payment for an application.
   */
  recordPayment: async (applicationId: number, data: PaymentCreate): Promise<Payment> => {
    const response = await api.post(`/admin/applications/${applicationId}/payment`, data);
    return response.data;
  },

  /**
   * Get payment details for an application.
   */
  getPayment: async (applicationId: number): Promise<Payment> => {
    const response = await api.get(`/admin/applications/${applicationId}/payment`);
    return response.data;
  },

  /**
   * Update payment details.
   */
  updatePayment: async (paymentId: number, data: PaymentUpdate): Promise<Payment> => {
    const response = await api.patch(`/admin/payments/${paymentId}`, data);
    return response.data;
  },

  /**
   * Verify or reject a payment.
   */
  verifyPayment: async (paymentId: number, data: PaymentVerify): Promise<Payment> => {
    const response = await api.post(`/admin/payments/${paymentId}/verify`, data);
    return response.data;
  },

  /**
   * Delete a payment.
   */
  deletePayment: async (paymentId: number): Promise<void> => {
    await api.delete(`/admin/payments/${paymentId}`);
  },

  // ==========================================================================
  // DOCUMENT MANAGEMENT
  // ==========================================================================

  /**
   * Upload a payment evidence document.
   */
  uploadDocument: async (paymentId: number, file: File): Promise<PaymentDocument> => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await api.post(`/admin/payments/${paymentId}/documents`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  /**
   * List documents for a payment.
   */
  listDocuments: async (paymentId: number): Promise<PaymentDocument[]> => {
    const response = await api.get(`/admin/payments/${paymentId}/documents`);
    return response.data;
  },

  /**
   * Get download URL for a document.
   */
  getDocumentDownloadUrl: (documentId: number): string => {
    return `${API_BASE}/admin/documents/${documentId}/download`;
  },

  /**
   * Delete a document.
   */
  deleteDocument: async (documentId: number): Promise<void> => {
    await api.delete(`/admin/documents/${documentId}`);
  },

  // ==========================================================================
  // DMO REPORTING
  // ==========================================================================

  /**
   * Get monthly report summary.
   */
  getMonthlyReportSummary: async (
    monthOfOffer: string,
    year: number
  ): Promise<MonthlyReportSummary> => {
    const response = await api.get('/admin/reports/monthly-summary', {
      params: { month_of_offer: monthOfOffer, year },
    });
    return response.data;
  },

  /**
   * Export DMO report as Excel.
   */
  exportDmoReportExcel: async (
    monthOfOffer: string,
    year: number,
    includePending: boolean = false
  ): Promise<Blob> => {
    const response = await api.get('/admin/reports/export/excel', {
      params: { month_of_offer: monthOfOffer, year, include_pending: includePending },
      responseType: 'blob',
    });
    return response.data;
  },

  /**
   * Mark month as submitted to DMO.
   */
  markAsSubmittedToDmo: async (data: DMOSubmissionCreate): Promise<DMOSubmission> => {
    const response = await api.post('/admin/reports/submit-to-dmo', data);
    return response.data;
  },

  /**
   * Get DMO submission history.
   */
  getDmoSubmissions: async (): Promise<DMOSubmission[]> => {
    const response = await api.get('/admin/reports/submissions');
    return response.data;
  },
};

export default api;
