import React from 'react';
import {
  Bed,
  AlertTriangle,
  Activity,
  ClipboardList,
  CheckCircle2,
  ArrowRight,
  ShieldAlert,
  Clock,
  Layers,
} from 'lucide-react';
import { DashboardSummary, BottleneckIssue, NavigationTab } from '../types';
import { StatCard } from '../components/StatCard';
import { Badge } from '../components/Badge';

interface DashboardPageProps {
  summary: DashboardSummary | null;
  bottlenecks: BottleneckIssue[];
  onNavigate: (tab: NavigationTab) => void;
  loading: boolean;
}

export const DashboardPage: React.FC<DashboardPageProps> = ({
  summary,
  bottlenecks,
  onNavigate,
  loading,
}) => {
  if (loading && !summary) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '60vh' }}>
        <div className="spinner" style={{ width: 40, height: 40 }} />
      </div>
    );
  }

  const criticalCount = summary?.critical_issues_count ?? bottlenecks.filter((b) => b.priority_level === 'Critical').length;
  const blockedCount = summary?.blocked_beds ?? 2;
  const availableCount = summary?.available_beds ?? 5;
  const occupiedCount = summary?.occupied_beds ?? 13;
  const totalBeds = summary?.total_beds ?? 22;
  const overdueCount = summary?.overdue_diagnostics_count ?? 3;
  const pendingActions = summary?.pending_actions_count ?? 2;

  return (
    <div>
      {/* Acute Operational Briefing Banner */}
      <div
        className="card"
        style={{
          borderLeft: '5px solid #dc2626',
          background: 'linear-gradient(90deg, #fff5f5 0%, #ffffff 100%)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'flex-start', gap: '1rem' }}>
          <div
            style={{
              width: 42,
              height: 42,
              borderRadius: 8,
              background: '#fef2f2',
              border: '1px solid #fecaca',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#dc2626',
              flexShrink: 0,
            }}
          >
            <ShieldAlert size={22} />
          </div>
          <div style={{ flex: 1 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.35rem' }}>
              <h2 style={{ fontSize: '1.05rem', fontWeight: 700, color: '#991b1b' }}>
                Operational Condition: Level-1 Acute Capacity & Triage Alert
              </h2>
              <Badge label="Active Multi-System Pressure" variant="critical" />
            </div>
            <p style={{ fontSize: '0.875rem', color: '#475569', lineHeight: 1.55 }}>
              Emergency triage waiting time has surged to an average of <strong>95+ minutes</strong>. While 5 beds are occupied in the Emergency Ward,
              <strong> exactly 2 beds (EMERG-03 &amp; EMERG-04) are physically blocked</strong> by clinically stabilized patients awaiting TPA insurance clearance and physician signatures.
              Simultaneously, <strong>STAT cardiac Troponin-T</strong> laboratory results are delayed by 3 hours, holding up clinical dispositions, and the incoming Emergency evening shift is
              <strong> severely short-staffed (only 1 physician, 1 nurse scheduled)</strong>.
            </p>
            <div style={{ display: 'flex', gap: '0.75rem', marginTop: '0.85rem' }}>
              <button className="btn btn-danger btn-sm" onClick={() => onNavigate('causal-links')}>
                <span>Inspect Causal Links</span>
                <ArrowRight size={14} />
              </button>
              <button className="btn btn-outline btn-sm" onClick={() => onNavigate('beds')}>
                <span>View Blocked Beds</span>
              </button>
              <button className="btn btn-outline btn-sm" onClick={() => onNavigate('actions-audit')}>
                <span>Review Pending Tasks ({pendingActions})</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Top Metric Cards */}
      <div className="grid-4">
        <StatCard
          label="Total Hospital Beds"
          value={totalBeds}
          subtext={`${occupiedCount} Occupied (${summary?.occupancy_rate_pct ?? 59.1}%)`}
          icon={<Bed size={22} color="#2563eb" />}
          iconBg="#eff6ff"
        />
        <StatCard
          label="Available Ready Beds"
          value={availableCount}
          subtext="Ready for immediate admission"
          icon={<CheckCircle2 size={22} color="#16a34a" />}
          iconBg="#f0fdf4"
        />
        <StatCard
          label="Blocked Beds"
          value={blockedCount}
          subtext="Blocked by discharge paperwork"
          icon={<AlertTriangle size={22} color="#dc2626" />}
          iconBg="#fef2f2"
        />
        <StatCard
          label="Overdue Diagnostics"
          value={overdueCount}
          subtext="Holding clinical disposition"
          icon={<Activity size={22} color="#d97706" />}
          iconBg="#fffbeb"
        />
      </div>

      <div className="grid-4">
        <StatCard
          label="Active Bottlenecks"
          value={bottlenecks.length || 14}
          subtext={`${criticalCount} Critical, ${bottlenecks.filter((b) => b.priority_level === 'High').length} High priority`}
          icon={<Layers size={22} color="#7c3aed" />}
          iconBg="#f5f3ff"
        />
        <StatCard
          label="Simulated Tasks"
          value={pendingActions}
          subtext="Awaiting operator review"
          icon={<ClipboardList size={22} color="#2563eb" />}
          iconBg="#eff6ff"
        />
        <StatCard
          label="Emergency Triage Wait"
          value="95 mins"
          subtext="Baseline target: 30 mins"
          icon={<Clock size={22} color="#dc2626" />}
          iconBg="#fef2f2"
        />
        <StatCard
          label="ICU Bed Occupancy"
          value="100%"
          subtext="4 of 4 beds full (Zero buffer)"
          icon={<ShieldAlert size={22} color="#ea580c" />}
          iconBg="#fff7ed"
        />
      </div>

      <div className="grid-2">
        {/* Ward Bed Utilization Breakdown */}
        <div className="card">
          <div className="card-header">
            <div className="card-title">
              <Bed size={18} color="#2563eb" />
              <span>Ward Capacity &amp; Availability Telemetry</span>
            </div>
            <button className="btn btn-outline btn-sm" onClick={() => onNavigate('beds')}>
              View Beds Table
            </button>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
            {/* Emergency Ward */}
            <div style={{ border: '1px solid #e2e8f0', borderRadius: '6px', padding: '0.75rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.35rem' }}>
                <span style={{ fontWeight: 600, fontSize: '0.9rem' }}>Emergency Ward (8 Units)</span>
                <span style={{ fontSize: '0.8rem', color: '#dc2626', fontWeight: 600 }}>2 Blocked | 5 Occupied | 2 Available</span>
              </div>
              <div style={{ height: 8, background: '#e2e8f0', borderRadius: 4, overflow: 'hidden', display: 'flex' }}>
                <div style={{ width: '37.5%', background: '#3b82f6' }} title="Occupied (Active Care)" />
                <div style={{ width: '25%', background: '#ef4444' }} title="Blocked by Discharge Paperwork" />
                <div style={{ width: '12.5%', background: '#f59e0b' }} title="Cleaning Required" />
                <div style={{ width: '25%', background: '#22c55e' }} title="Available" />
              </div>
              <div style={{ display: 'flex', gap: '1rem', marginTop: '0.5rem', fontSize: '0.75rem', color: '#64748b' }}>
                <span>• Occupied: 3</span>
                <span style={{ color: '#dc2626', fontWeight: 600 }}>• Blocked: 2 (EMERG-03, 04)</span>
                <span>• Cleaning: 1</span>
                <span style={{ color: '#16a34a', fontWeight: 600 }}>• Available: 2</span>
              </div>
            </div>

            {/* ICU Ward */}
            <div style={{ border: '1px solid #e2e8f0', borderRadius: '6px', padding: '0.75rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.35rem' }}>
                <span style={{ fontWeight: 600, fontSize: '0.9rem' }}>ICU Ward (4 Units)</span>
                <span style={{ fontSize: '0.8rem', color: '#dc2626', fontWeight: 600 }}>100% Saturation (0 Available)</span>
              </div>
              <div style={{ height: 8, background: '#e2e8f0', borderRadius: 4, overflow: 'hidden', display: 'flex' }}>
                <div style={{ width: '100%', background: '#ef4444' }} title="100% Occupied" />
              </div>
              <div style={{ display: 'flex', gap: '1rem', marginTop: '0.5rem', fontSize: '0.75rem', color: '#64748b' }}>
                <span>• Occupied: 4 (ICU-01 to ICU-04)</span>
                <span style={{ color: '#dc2626', fontWeight: 600 }}>• Zero emergency admission reserve</span>
              </div>
            </div>

            {/* General Ward */}
            <div style={{ border: '1px solid #e2e8f0', borderRadius: '6px', padding: '0.75rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.35rem' }}>
                <span style={{ fontWeight: 600, fontSize: '0.9rem' }}>General Ward (10 Units)</span>
                <span style={{ fontSize: '0.8rem', color: '#16a34a', fontWeight: 600 }}>5 Available (Idle Capacity)</span>
              </div>
              <div style={{ height: 8, background: '#e2e8f0', borderRadius: 4, overflow: 'hidden', display: 'flex' }}>
                <div style={{ width: '40%', background: '#3b82f6' }} title="Occupied" />
                <div style={{ width: '10%', background: '#f59e0b' }} title="Cleaning" />
                <div style={{ width: '50%', background: '#22c55e' }} title="Available" />
              </div>
              <div style={{ display: 'flex', gap: '1rem', marginTop: '0.5rem', fontSize: '0.75rem', color: '#64748b' }}>
                <span>• Occupied: 4</span>
                <span>• Cleaning: 1</span>
                <span style={{ color: '#16a34a', fontWeight: 600 }}>• Available: 5 (GEN-05 to GEN-10)</span>
              </div>
            </div>
          </div>
        </div>

        {/* Priority Bottlenecks Queue Summary */}
        <div className="card">
          <div className="card-header">
            <div className="card-title">
              <AlertTriangle size={18} color="#dc2626" />
              <span>Top Operational Bottlenecks</span>
            </div>
            <button className="btn btn-outline btn-sm" onClick={() => onNavigate('priority-queue')}>
              View Full Queue
            </button>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.65rem' }}>
            {bottlenecks.slice(0, 5).map((item) => (
              <div
                key={item.issue_id}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  padding: '0.65rem 0.85rem',
                  borderRadius: '6px',
                  background: '#f8fafc',
                  border: '1px solid #f1f5f9',
                }}
              >
                <div style={{ flex: 1, minWidth: 0, marginRight: '0.75rem' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <span style={{ fontWeight: 600, fontSize: '0.85rem', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                      {item.title}
                    </span>
                    {item.escalation_required && <Badge label="Escalated" variant="critical" />}
                  </div>
                  <div style={{ fontSize: '0.75rem', color: '#64748b' }}>
                    {item.affected_department} • Score: <strong>{item.priority_score}/100</strong>
                  </div>
                </div>
                <Badge label={item.priority_level} variant={item.priority_level.toLowerCase() as any} />
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
