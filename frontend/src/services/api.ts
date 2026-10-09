/**
 * FlowCare AI — Centralized Backend API Client
 * Hospital: Sanjeevani Multispeciality Hospital
 */

import {
  Patient,
  Appointment,
  Bed,
  Staff,
  Diagnostic,
  Admission,
  Discharge,
  Feedback,
  DataQualityReport,
  BottleneckIssue,
  CausalLink,
  Recommendation,
  SimulatedAction,
  ActionCreateRequest,
  ActionReviewRequest,
  ActionCompleteRequest,
  AuditLogEntry,
  DashboardSummary,
} from '../types';

export const DEFAULT_API_BASE = 'http://127.0.0.1:8000';

class ApiService {
  private baseUrl: string;

  constructor() {
    this.baseUrl = localStorage.getItem('flowcare_api_url') || DEFAULT_API_BASE;
  }

  public getBaseUrl(): string {
    return this.baseUrl;
  }

  public setBaseUrl(url: string): void {
    this.baseUrl = url.trim().replace(/\/+$/, '');
    localStorage.setItem('flowcare_api_url', this.baseUrl);
  }

  public resetBaseUrl(): void {
    this.baseUrl = DEFAULT_API_BASE;
    localStorage.removeItem('flowcare_api_url');
  }

  private async request<T>(path: string, options?: RequestInit): Promise<T> {
    const directUrl = `${this.baseUrl}${path.startsWith('/') ? path : `/${path}`}`;
    const proxyUrl = `/api${path.startsWith('/') ? path : `/${path}`}`;
    
    // First attempt: direct backend URL
    try {
      const response = await fetch(directUrl, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          Accept: 'application/json',
          ...options?.headers,
        },
      });

      if (!response.ok) {
        let errDetail = response.statusText;
        try {
          const jsonErr = await response.json();
          if (jsonErr.detail) {
            errDetail = typeof jsonErr.detail === 'string' ? jsonErr.detail : JSON.stringify(jsonErr.detail);
          }
        } catch {
          // Keep response.statusText
        }
        throw new Error(`API Error [${response.status}] at ${path}: ${errDetail}`);
      }

      return (await response.json()) as T;
    } catch (err: any) {
      // If direct fetch had a network error (e.g. CORS or localhost blocking), attempt Vite proxy fallback
      if (err.name === 'TypeError' || err.message?.includes('Failed to fetch')) {
        try {
          const proxyResponse = await fetch(proxyUrl, {
            ...options,
            headers: {
              'Content-Type': 'application/json',
              Accept: 'application/json',
              ...options?.headers,
            },
          });
          if (proxyResponse.ok) {
            return (await proxyResponse.json()) as T;
          }
        } catch {
          // Proxy fallback also failed, show clear error
        }
        throw new Error(
          `Unable to reach backend at ${this.baseUrl} or via proxy /api. Please verify FastAPI is running: uvicorn main:app --reload --host 127.0.0.1 --port 8000`
        );
      }
      throw err;
    }
  }

  // General & Health
  public async checkHealth(): Promise<{ status: string; service: string; hospital: string; version: string; reference_timestamp: string }> {
    return this.request('/health');
  }

  public async resetDemo(): Promise<{ status: string; message: string }> {
    return this.request('/demo/reset', { method: 'POST' });
  }

  // Data & Quality
  public async getDataQuality(): Promise<DataQualityReport> {
    return this.request('/data-quality');
  }

  public async getDataOverview(): Promise<{ hospital: string; reference_timestamp: string; counts: Record<string, number> }> {
    return this.request('/data/overview');
  }

  public async getPatients(params?: { department?: string; status?: string; age_group?: string; visit_type?: string }): Promise<Patient[]> {
    const query = new URLSearchParams(params as any).toString();
    return this.request(`/data/patients${query ? `?${query}` : ''}`);
  }

  public async getAppointments(params?: { department?: string; doctor?: string; status?: string }): Promise<Appointment[]> {
    const query = new URLSearchParams(params as any).toString();
    return this.request(`/data/appointments${query ? `?${query}` : ''}`);
  }

  public async getBeds(params?: { ward?: string; bed_type?: string; occupancy?: string; availability?: string }): Promise<Bed[]> {
    const query = new URLSearchParams(params as any).toString();
    return this.request(`/data/beds${query ? `?${query}` : ''}`);
  }

  public async getStaff(params?: { department?: string; shift?: string; availability?: string; role?: string }): Promise<Staff[]> {
    const query = new URLSearchParams(params as any).toString();
    return this.request(`/data/staff${query ? `?${query}` : ''}`);
  }

  public async getDiagnostics(params?: { status?: string; department?: string; patient?: string }): Promise<Diagnostic[]> {
    const query = new URLSearchParams(params as any).toString();
    return this.request(`/data/diagnostics${query ? `?${query}` : ''}`);
  }

  public async getAdmissions(params?: { department?: string; ward?: string; status?: string }): Promise<Admission[]> {
    const query = new URLSearchParams(params as any).toString();
    return this.request(`/data/admissions${query ? `?${query}` : ''}`);
  }

  public async getDischarges(params?: { request_status?: string; document_status?: string }): Promise<Discharge[]> {
    const query = new URLSearchParams(params as any).toString();
    return this.request(`/data/discharges${query ? `?${query}` : ''}`);
  }

  public async getFeedback(params?: { category?: string; severity?: string; department?: string }): Promise<Feedback[]> {
    const query = new URLSearchParams(params as any).toString();
    return this.request(`/data/feedback${query ? `?${query}` : ''}`);
  }

  // Operational Intelligence
  public async getDashboard(): Promise<DashboardSummary> {
    return this.request('/dashboard');
  }

  public async getBottlenecks(): Promise<BottleneckIssue[]> {
    return this.request('/bottlenecks');
  }

  public async getBottleneckById(issueId: string): Promise<BottleneckIssue> {
    return this.request(`/bottlenecks/${encodeURIComponent(issueId)}`);
  }

  public async getCausalLinks(): Promise<CausalLink[]> {
    return this.request('/causal-links');
  }

  public async getRecommendations(): Promise<Recommendation[]> {
    return this.request('/recommendations');
  }

  public async getPriorityQueue(): Promise<BottleneckIssue[]> {
    return this.request('/priority-queue');
  }

  // Simulated Actions & Audit
  public async getActions(status?: string): Promise<SimulatedAction[]> {
    const query = status ? `?status=${encodeURIComponent(status)}` : '';
    return this.request(`/actions${query}`);
  }

  public async createAction(payload: ActionCreateRequest): Promise<SimulatedAction> {
    return this.request('/actions', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  public async reviewAction(actionId: string, payload: ActionReviewRequest): Promise<SimulatedAction> {
    return this.request(`/actions/${encodeURIComponent(actionId)}/review`, {
      method: 'PATCH',
      body: JSON.stringify(payload),
    });
  }

  public async completeAction(actionId: string, payload: ActionCompleteRequest): Promise<SimulatedAction> {
    return this.request(`/actions/${encodeURIComponent(actionId)}/complete`, {
      method: 'PATCH',
      body: JSON.stringify(payload),
    });
  }

  public async getAuditLog(actionId?: string): Promise<AuditLogEntry[]> {
    const query = actionId ? `?action_id=${encodeURIComponent(actionId)}` : '';
    return this.request(`/audit-log${query}`);
  }
}

export const api = new ApiService();
