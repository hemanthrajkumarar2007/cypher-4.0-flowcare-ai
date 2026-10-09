import React, { useState } from 'react';
import { Activity, Clock, AlertTriangle, CheckCircle2, Filter } from 'lucide-react';
import { Diagnostic } from '../types';
import { Badge } from '../components/Badge';

interface DiagnosticsPageProps {
  diagnostics: Diagnostic[];
  loading: boolean;
  referenceTime: string;
}

export const DiagnosticsPage: React.FC<DiagnosticsPageProps> = ({
  diagnostics,
  loading,
  referenceTime,
}) => {
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [deptFilter, setDeptFilter] = useState('ALL');

  if (loading) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '60vh' }}>
        <div className="spinner" style={{ width: 40, height: 40 }} />
      </div>
    );
  }

  const depts = Array.from(new Set(diagnostics.map((d) => d.department)));

  const filtered = diagnostics.filter((d) => {
    const matchesStatus = statusFilter === 'ALL' || d.status.toLowerCase() === statusFilter.toLowerCase();
    const matchesDept = deptFilter === 'ALL' || d.department === deptFilter;
    return matchesStatus && matchesDept;
  });

  const overdueCount = diagnostics.filter((d) => d.status === 'overdue').length;

  return (
    <div>
      {/* Alert Header */}
      {overdueCount > 0 && (
        <div className="alert-box alert-danger">
          <AlertTriangle size={18} color="#dc2626" style={{ flexShrink: 0, marginTop: 2 }} />
          <div>
            <strong>Laboratory Bottleneck Alert:</strong> {overdueCount} diagnostic tests are past their expected turnaround time at Central Lab.
            Attending emergency clinicians cannot finalize admission or discharge dispositions for cardiac and head trauma patients without these reports,
            forcing observation beds <strong>EMERG-01</strong> and <strong>EMERG-02</strong> to remain occupied.
          </div>
        </div>
      )}

      {/* Filter Bar */}
      <div className="card filter-bar">
        <div className="filter-group">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
            <Filter size={14} color="#64748b" />
            <select className="select-input" value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
              <option value="ALL">All Test Statuses</option>
              <option value="overdue">Overdue Only ({overdueCount})</option>
              <option value="in-progress">In-Progress</option>
              <option value="pending">Pending</option>
              <option value="completed">Completed</option>
            </select>
          </div>

          <select className="select-input" value={deptFilter} onChange={(e) => setDeptFilter(e.target.value)}>
            <option value="ALL">All Departments</option>
            {depts.map((d) => (
              <option key={d} value={d}>
                {d}
              </option>
            ))}
          </select>
        </div>

        <div style={{ fontSize: '0.85rem', color: '#64748b' }}>
          Reference Clock: <strong>{referenceTime.replace('T', ' ')}</strong>
        </div>
      </div>

      {/* Diagnostic Records Table */}
      <div className="card table-responsive">
        <table className="data-table">
          <thead>
            <tr>
              <th>Order ID</th>
              <th>Test Name</th>
              <th>Patient ID</th>
              <th>Ordering Dept</th>
              <th>Order Placed</th>
              <th>Expected By</th>
              <th>Status</th>
              <th>Operational Impact &amp; Delay</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((d) => {
              const isOverdue = d.status === 'overdue';
              return (
                <tr key={d.test_id} style={{ background: isOverdue ? '#fff5f5' : undefined }}>
                  <td style={{ fontWeight: 700, fontFamily: 'monospace' }}>{d.test_id}</td>
                  <td style={{ fontWeight: 600, color: '#0f172a' }}>{d.test}</td>
                  <td style={{ fontFamily: 'monospace', color: '#2563eb' }}>{d.patient}</td>
                  <td>{d.department}</td>
                  <td style={{ fontSize: '0.8rem', color: '#64748b' }}>{d.requested_time.replace('T', ' ')}</td>
                  <td style={{ fontSize: '0.8rem', color: isOverdue ? '#dc2626' : '#64748b', fontWeight: isOverdue ? 600 : 400 }}>
                    {d.expected_completion.replace('T', ' ')}
                  </td>
                  <td>
                    <Badge
                      label={d.status.toUpperCase()}
                      variant={isOverdue ? 'critical' : d.status === 'completed' ? 'available' : 'high'}
                    />
                  </td>
                  <td style={{ fontSize: '0.8rem', maxWidth: 280 }}>
                    {isOverdue ? (
                      <span style={{ color: '#991b1b', fontWeight: 600 }}>
                        ⚠ Late Turnaround (~180m delay). Holding patient clinical disposition in bed.
                      </span>
                    ) : d.status === 'completed' ? (
                      <span style={{ color: '#16a34a' }}>Completed at {d.completed_time?.replace('T', ' ') || 'on schedule'}</span>
                    ) : (
                      <span style={{ color: '#64748b' }}>Processing in central laboratory queue</span>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
};
