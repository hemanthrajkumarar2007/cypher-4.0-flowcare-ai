import React, { useState } from 'react';
import { RefreshCw, RotateCcw, Wifi, WifiOff, Clock } from 'lucide-react';
import { NavigationTab } from '../types';

interface HeaderProps {
  currentTab: NavigationTab;
  backendOnline: boolean;
  referenceTime: string;
  onRefresh: () => void;
  onResetDemo: () => Promise<void>;
  isRefreshing?: boolean;
}

export const Header: React.FC<HeaderProps> = ({
  currentTab,
  backendOnline,
  referenceTime,
  onRefresh,
  onResetDemo,
  isRefreshing = false,
}) => {
  const [resetting, setResetting] = useState(false);

  const getTabTitle = (tab: NavigationTab) => {
    switch (tab) {
      case 'overview':
        return { title: 'Executive Operations Overview', sub: 'Real-time telemetry, bed utilization & acute alerts' };
      case 'bottlenecks':
        return { title: 'Operational Bottleneck Intelligence', sub: 'Ranked clinical and administrative process delays' };
      case 'beds':
        return { title: 'Ward & Bed Capacity Management', sub: 'Individual unit states: Occupied, Blocked, Available, Cleaning' };
      case 'diagnostics':
        return { title: 'Laboratory & Diagnostic Imaging', sub: 'STAT turnaround monitoring & overdue order impact' };
      case 'discharges':
        return { title: 'Discharge Clearance Workflow', sub: 'Administrative, TPA insurance & clinical task completion' };
      case 'staff-appointments':
        return { title: 'Personnel Coverage & Consultation Queue', sub: 'Shift rostering stress & outpatient appointment tracking' };
      case 'causal-links':
        return { title: 'Root-Cause Cross-Domain Causal Links', sub: 'Evidence-backed causal graph connecting delayed processes' };
      case 'priority-queue':
        return { title: 'Actionable Priority Queue', sub: 'Prioritized issue queue ranked by urgency and impact' };
      case 'actions-audit':
        return { title: 'Simulated Tasks & Operator Review Log', sub: 'Human-in-the-loop task review with immutable audit trail' };
      case 'data-quality':
        return { title: 'Relational Integrity & Validation Audit', sub: 'Comprehensive data-quality check across all 8 categories' };
    }
  };

  const { title, sub } = getTabTitle(currentTab);

  const handleReset = async () => {
    if (confirm('Reset hospital records and simulated actions back to benchmark scenario?')) {
      setResetting(true);
      try {
        await onResetDemo();
      } finally {
        setResetting(false);
      }
    }
  };

  return (
    <header className="top-header">
      <div className="header-left">
        <div className="header-title-wrapper">
          <h1 className="header-title">{title}</h1>
          <span className="header-subtitle">{sub}</span>
        </div>
      </div>

      <div className="header-right">
        {/* Reference Timestamp */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.4rem',
            background: '#f1f5f9',
            padding: '0.35rem 0.65rem',
            borderRadius: '6px',
            fontSize: '0.75rem',
            color: '#475569',
            fontWeight: 500,
          }}
        >
          <Clock size={14} color="#64748b" />
          <span>Ref: {referenceTime.replace('T', ' ')}</span>
        </div>

        {/* Backend Connection Status */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.4rem',
            background: backendOnline ? '#f0fdf4' : '#fef2f2',
            border: `1px solid ${backendOnline ? '#bbf7d0' : '#fecaca'}`,
            padding: '0.35rem 0.65rem',
            borderRadius: '6px',
            fontSize: '0.75rem',
            fontWeight: 600,
            color: backendOnline ? '#166534' : '#991b1b',
          }}
        >
          {backendOnline ? <Wifi size={14} color="#16a34a" /> : <WifiOff size={14} color="#dc2626" />}
          <span>{backendOnline ? 'Backend Online (Port 8000)' : 'Backend Offline'}</span>
        </div>

        {/* Refresh Button */}
        <button
          className="btn btn-outline btn-sm"
          onClick={onRefresh}
          disabled={isRefreshing}
          title="Reload live metrics from backend"
        >
          <RefreshCw size={14} className={isRefreshing ? 'spinner' : ''} />
          <span>Refresh</span>
        </button>

        {/* Reset Demo Button */}
        <button
          className="btn btn-outline btn-sm"
          onClick={handleReset}
          disabled={resetting}
          style={{ color: '#d97706', borderColor: '#fde68a' }}
          title="Reset hospital state back to benchmark scenario"
        >
          <RotateCcw size={14} />
          <span>{resetting ? 'Resetting...' : 'Reset Demo'}</span>
        </button>
      </div>
    </header>
  );
};
