import axios from 'axios';
import toast from 'react-hot-toast';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    } else if (error.response?.status >= 500) {
      toast.error('Server error. Please try again later.');
    } else if (error.response?.data?.detail) {
      toast.error(error.response.data.detail);
    }
    return Promise.reject(error);
  }
);

// API service functions
export const authAPI = {
  login: (email: string, password: string) => {
    const formData = new FormData();
    formData.append('username', email);
    formData.append('password', password);
    return api.post('/auth/token', formData);
  },
  register: (userData: any) => api.post('/auth/register', userData),
  getMe: () => api.get('/auth/me'),
};

export const casesAPI = {
  getCases: (params?: any) => api.get('/cases', { params }),
  getCase: (id: number) => api.get(`/cases/${id}`),
  createCase: (caseData: any) => api.post('/cases', caseData),
  updateCaseStatus: (id: number, status: string, notes?: string) => 
    api.put(`/cases/${id}/status`, { new_status: status, notes }),
  getCaseHistory: (id: number) => api.get(`/cases/${id}/history`),
  searchByNumber: (caseNumber: string) => api.get(`/cases/search/${caseNumber}`),
  assignJudge: (caseId: number, judgeId: number) => 
    api.put(`/cases/${caseId}/assign-judge`, { judge_id: judgeId }),
  calculateComplexity: (data: any) => api.post('/cases/calculate-complexity', null, { params: data }),
  getCaseDelays: (id: number) => api.get(`/cases/${id}/delays`),
  getDelayedCases: (thresholdDays?: number) => api.get('/cases/delayed', { params: { threshold_days: thresholdDays } }),
};

export const judgesAPI = {
  getJudges: (params?: any) => api.get('/judges', { params }),
  getJudge: (id: number) => api.get(`/judges/${id}`),
  createJudge: (judgeData: any) => api.post('/judges', judgeData),
  updateAvailability: (id: number, isAvailable: boolean) => 
    api.put(`/judges/${id}/availability`, { is_available: isAvailable }),
  createRecusal: (judgeId: number, caseId: number, reason: string) => 
    api.post('/judges/recusals', { judge_id: judgeId, case_id: caseId, reason }),
  getWorkloadAnalysis: (courtId?: number) => 
    api.get('/judges/workload-analysis', { params: { court_id: courtId } }),
  getWorkload: (id: number) => api.get(`/judges/${id}/workload`),
  getSchedule: (id: number, startDate?: string, endDate?: string) => 
    api.get(`/judges/${id}/schedule`, { params: { start_date: startDate, end_date: endDate } }),
};

export const schedulingAPI = {
  findSlots: (request: any) => api.post('/scheduling/find-slots', request),
  scheduleHearing: (hearingData: any) => api.post('/scheduling/schedule-hearing', hearingData),
  getConflicts: (caseId: number, proposedDate: string, duration: number) => 
    api.get(`/scheduling/conflicts/${caseId}`, { 
      params: { proposed_date: proposedDate, duration_hours: duration } 
    }),
  rescheduleHearing: (hearingId: number, newDate: string, reason: string) => 
    api.post(`/scheduling/reschedule/${hearingId}`, { new_date: newDate, reason }),
  getOptimizationReport: (courtId?: number) => 
    api.get('/scheduling/optimization-report', { params: { court_id: courtId } }),
};

export const calendarAPI = {
  getHeatmap: (startDate: string, endDate: string, courtId?: number) => 
    api.get('/calendar/heatmap', { 
      params: { start_date: startDate, end_date: endDate, court_id: courtId } 
    }),
  getDayView: (date: string, courtId?: number) => 
    api.get('/calendar/day-view', { params: { target_date: date, court_id: courtId } }),
  getWeekView: (weekStart: string, courtId?: number) => 
    api.get('/calendar/week-view', { params: { week_start: weekStart, court_id: courtId } }),
  getUpcomingHearings: (daysAhead?: number, judgeId?: number, courtroomId?: number) => 
    api.get('/calendar/upcoming-hearings', { 
      params: { days_ahead: daysAhead, judge_id: judgeId, courtroom_id: courtroomId } 
    }),
  dragDropReschedule: (hearingId: number, newDatetime: string, newCourtroomId?: number) => 
    api.post('/calendar/drag-drop-reschedule', { 
      hearing_id: hearingId, 
      new_datetime: newDatetime, 
      new_courtroom_id: newCourtroomId 
    }),
};

export const documentsAPI = {
  uploadDocument: (caseId: number, title: string, documentType: string, isPublic: boolean, file: File) => {
    const formData = new FormData();
    formData.append('case_id', caseId.toString());
    formData.append('title', title);
    formData.append('document_type', documentType);
    formData.append('is_public', isPublic.toString());
    formData.append('file', file);
    return api.post('/documents/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
  },
  getCaseDocuments: (caseId: number, documentType?: string) => 
    api.get(`/documents/case/${caseId}`, { params: { document_type: documentType } }),
  getDocument: (id: number) => api.get(`/documents/${id}`),
  downloadDocument: (id: number) => api.get(`/documents/${id}/download`, { responseType: 'blob' }),
  verifyDocument: (id: number) => api.post(`/documents/${id}/verify`),
  semanticSearch: (query: string, caseId?: number, documentType?: string, limit?: number) => 
    api.get('/documents/search/semantic', { 
      params: { query, case_id: caseId, document_type: documentType, limit } 
    }),
  extractLegalEntities: (documentId: number) => 
    api.get(`/documents/legal-entities/extract?document_id=${documentId}`),
  getCitationNetwork: (documentId: number, depth?: number) => 
    api.get(`/documents/citation-network/${documentId}`, { params: { depth } }),
};

export const mlAPI = {
  // Complete case analysis
  analyzeCase: (data: any) => api.post('/ml/analyze-case', data),
  
  // Individual predictions
  predictDuration: (data: any) => api.post('/ml/predict-duration', data),
  predictOutcome: (data: any) => api.post('/ml/predict-outcome', data),
  recommendJudges: (data: any) => api.post('/ml/recommend-judges', data),
  predictSettlement: (data: any) => api.post('/ml/predict-settlement', data),
  
  // ML service status
  getMLStatus: () => api.get('/ml/ml-status'),
};


export const courtsAPI = {
  getCourts: (level?: string) => api.get('/courts', { params: { level } }),
  getHierarchy: () => api.get('/courts/hierarchy'),
  getStatistics: () => api.get('/courts/statistics'),
};
