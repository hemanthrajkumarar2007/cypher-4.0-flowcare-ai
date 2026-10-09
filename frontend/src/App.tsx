import React, { useState, useEffect, useCallback } from 'react';
import {
  NavigationTab,
  DashboardSummary,
  BottleneckIssue,
  Bed,
  Diagnostic,
  Admission,
  Discharge,
  Staff,
  Appointment,
  CausalLink,
  Recommendation,
  SimulatedAction,
  AuditLogEntry,
  DataQualityReport,
} from './types';
import { api } from './services/api';
import { Sidebar } from './components/Sidebar';
import { Header } from './components/Header';
import { DashboardPage } from './pages/DashboardPage';
import { BottlenecksPage } from './pages/BottlenecksPage';
import { BedsPage } from './pages/BedsPage';
import { DiagnosticsPage } from './pages/DiagnosticsPage';
import { DischargePage } from './pages/DischargePage';
import { StaffAppointmentsPage } from './pages/StaffAppointmentsPage';
import { CausalLinksPage } from './pages/CausalLinksPage';
import { PriorityQueuePage } from './pages/PriorityQueuePage';
import { ActionsAuditPage } from './pages/ActionsAuditPage';
import { DataQualityPage } from './pages/DataQualityPage';
import { AlertCircle, RefreshCw } from 'lucide-react';

export const App: React.FC = () => {
  const [currentTab, setCurrentTab] = useState<NavigationTab>('overview');
  const [backendOnline, setBackendOnline] = useState<boolean>(false);
  const [referenceTime, setReferenceTime] = useState<string>('2026-10-10T10:00:00');
  const [loading, setLoading] = useState<boolean>(true);
  const [isRefreshing, setIsRefreshing] = useState<boolean>(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // Core Data States
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [bottlenecks, setBottlenecks] = useState<BottleneckIssue[]>([]);
  const [beds, setBeds] = useState<Bed[]>([]);
  const [diagnostics, setDiagnostics] = useState<Diagnostic[]>([]);
  const [admissions, setAdmissions] = useState<Admission[]>([]);
  const [discharges, setDischarges] = useState<Discharge[]>([]);
  const [staff, setStaff] = useState<Staff[]>([]);
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [causalLinks, setCausalLinks] = useState<CausalLink[]>([]);
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [priorityQueue, setPriorityQueue] = useState<BottleneckIssue[]>([]);
  const [actions, setActions] = useState<SimulatedAction[]>([]);
  const [auditLog, setAuditLog] = useState<AuditLogEntry[]>([]);
  const [dataQualityReport, setDataQualityReport] = useState<DataQualityReport | null>(null);
  const [dataOverview, setDataOverview] = useState<any | null>(null);

  // Load all telemetry from FastAPI backend
  const loadData = useCallback(async (silent = false) => {
    if (!silent) setLoading(true);
    setIsRefreshing(true);
    setErrorMessage(null);

    try {
      // 1. Health check
      const health = await api.checkHealth();
      setBackendOnline(true);
      if (health.reference_timestamp) {
        setReferenceTime(health.reference_timestamp);
      }

      // 2. Parallel data fetching
      const [
        dashData,
        bottlenecksData,
        bedsData,
        diagData,
        admData,
        disData,
        staffData,
        aptData,
        linksData,
        recsData,
        queueData,
        actionsData,
        auditData,
        qualityData,
        overviewData,
      ] = await Promise.all([
        api.getDashboard().catch(() => null),
        api.getBottlenecks().catch(() => []),
        api.getBeds().catch(() => []),
        api.getDiagnostics().catch(() => []),
        api.getAdmissions().catch(() => []),
        api.getDischarges().catch(() => []),
        api.getStaff().catch(() => []),
        api.getAppointments().catch(() => []),
        api.getCausalLinks().catch(() => []),
        api.getRecommendations().catch(() => []),
        api.getPriorityQueue().catch(() => []),
        api.getActions().catch(() => []),
        api.getAuditLog().catch(() => []),
        api.getDataQuality().catch(() => null),
        api.getDataOverview().catch(() => null),
      ]);

      setSummary(dashData);
      setBottlenecks(bottlenecksData);
      setBeds(bedsData);
      setDiagnostics(diagData);
      setAdmissions(admData);
      setDischarges(disData);
      setStaff(staffData);
      setAppointments(aptData);
      setCausalLinks(linksData);
      setRecommendations(recsData);
      setPriorityQueue(queueData);
      setActions(actionsData);
      setAuditLog(auditData);
      setDataQualityReport(qualityData);
      setDataOverview(overviewData);
    } catch (err: any) {
      setBackendOnline(false);
      setErrorMessage(err.message || 'Failed to connect to FlowCare AI Backend');
    } finally {
      setLoading(false);
      setIsRefreshing(false);
    }
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  // Handle Demo Benchmark Reset
  const handleResetDemo = async () => {
    try {
      await api.resetDemo();
      await loadData(true);
    } catch (err: any) {
      alert(`Reset error: ${err.message}`);
    }
  };

  // Badge counts for sidebar
  const pendingActionsCount = actions.filter((a) => a.status === 'Awaiting review').length;
  const blockedBedsCount = beds.filter((b) => b.availability === 'Blocked').length;

  return (
    <div className="app-container">
      {/* Dark Navy Sidebar */}
      <Sidebar
        currentTab={currentTab}
        onSelectTab={setCurrentTab}
        counts={{
          bottlenecks: bottlenecks.length,
          blockedBeds: blockedBedsCount,
          actionsPending: pendingActionsCount,
        }}
      />

      {/* Main Workspace */}
      <div className="main-wrapper">
        <Header
          currentTab={currentTab}
          backendOnline={backendOnline}
          referenceTime={referenceTime}
          onRefresh={() => loadData(true)}
          onResetDemo={handleResetDemo}
          isRefreshing={isRefreshing}
        />

        <main className="content-area">
          {/* Error Banner when Backend is Offline */}
          {errorMessage && (
            <div className="alert-box alert-danger" style={{ marginBottom: '1.25rem' }}>
              <AlertCircle size={20} color="#dc2626" style={{ flexShrink: 0, marginTop: 2 }} />
              <div>
                <strong style={{ fontSize: '0.95rem' }}>Backend Connection Error:</strong>
                <p style={{ marginTop: '0.2rem' }}>{errorMessage}</p>
                <div style={{ marginTop: '0.5rem', fontSize: '0.8rem', color: '#7f1d1d' }}>
                  Please ensure your FastAPI backend is running with the following command in PowerShell:
                  <code style={{ display: 'block', background: '#fee2e2', padding: '0.35rem 0.6rem', borderRadius: '4px', marginTop: '0.25rem', fontFamily: 'monospace' }}>
                    uvicorn main:app --reload --host 127.0.0.1 --port 8000
                  </code>
                </div>
              </div>
            </div>
          )}

          {/* Section Router */}
          {currentTab === 'overview' && (
            <DashboardPage
              summary={summary}
              bottlenecks={bottlenecks}
              onNavigate={setCurrentTab}
              loading={loading}
            />
          )}

          {currentTab === 'bottlenecks' && (
            <BottlenecksPage bottlenecks={bottlenecks} loading={loading} />
          )}

          {currentTab === 'beds' && (
            <BedsPage beds={beds} loading={loading} />
          )}

          {currentTab === 'diagnostics' && (
            <DiagnosticsPage
              diagnostics={diagnostics}
              loading={loading}
              referenceTime={referenceTime}
            />
          )}

          {currentTab === 'discharges' && (
            <DischargePage
              discharges={discharges}
              admissions={admissions}
              beds={beds}
              loading={loading}
            />
          )}

          {currentTab === 'staff-appointments' && (
            <StaffAppointmentsPage
              staff={staff}
              appointments={appointments}
              loading={loading}
            />
          )}

          {currentTab === 'causal-links' && (
            <CausalLinksPage causalLinks={causalLinks} loading={loading} />
          )}

          {currentTab === 'priority-queue' && (
            <PriorityQueuePage
              priorityQueue={priorityQueue}
              recommendations={recommendations}
              loading={loading}
              onActionCreated={() => loadData(true)}
            />
          )}

          {currentTab === 'actions-audit' && (
            <ActionsAuditPage
              actions={actions}
              auditLog={auditLog}
              loading={loading}
              onRefresh={() => loadData(true)}
            />
          )}

          {currentTab === 'data-quality' && (
            <DataQualityPage
              report={dataQualityReport}
              overview={dataOverview}
              loading={loading}
            />
          )}
        </main>
      </div>
    </div>
  );
};
