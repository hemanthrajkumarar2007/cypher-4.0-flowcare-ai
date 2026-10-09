import React, { useState } from 'react';
import { AlertTriangle, Search, Filter, ShieldAlert, CheckCircle, ChevronRight, Eye } from 'lucide-react';
import { BottleneckIssue } from '../types';
import { Badge } from '../components/Badge';
import { Modal } from '../components/Modal';

interface BottlenecksPageProps {
  bottlenecks: BottleneckIssue[];
  loading: boolean;
}

export const BottlenecksPage: React.FC<BottlenecksPageProps> = ({ bottlenecks, loading }) => {
  const [search, setSearch] = useState('');
  const [deptFilter, setDeptFilter] = useState('ALL');
  const [levelFilter, setLevelFilter] = useState('ALL');
  const [selectedIssue, setSelectedIssue] = useState<BottleneckIssue | null>(null);

  if (loading) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '60vh' }}>
        <div className="spinner" style={{ width: 40, height: 40 }} />
      </div>
    );
  }

  // Filter logic
  const departments = Array.from(new Set(bottlenecks.map((b) => b.affected_department)));
  const filtered = bottlenecks.filter((item) => {
    const matchesSearch =
      item.title.toLowerCase().includes(search.toLowerCase()) ||
      item.issue_id.toLowerCase().includes(search.toLowerCase()) ||
      item.evidence.some((e) => e.toLowerCase().includes(search.toLowerCase()));
    const matchesDept = deptFilter === 'ALL' || item.affected_department === deptFilter;
    const matchesLevel = levelFilter === 'ALL' || item.priority_level === levelFilter;
    return matchesSearch && matchesDept && matchesLevel;
  });

  return (
    <div>
      {/* Filter and Search Bar */}
      <div className="card filter-bar">
        <div className="filter-group">
          <div style={{ display: 'flex', alignItems: 'center', position: 'relative' }}>
            <Search size={16} color="#94a3b8" style={{ position: 'absolute', left: 10 }} />
            <input
              type="text"
              placeholder="Search bottlenecks by title, ID, evidence..."
              className="search-input"
              style={{ paddingLeft: '2rem' }}
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
            <Filter size={14} color="#64748b" />
            <select className="select-input" value={deptFilter} onChange={(e) => setDeptFilter(e.target.value)}>
              <option value="ALL">All Departments</option>
              {departments.map((d) => (
                <option key={d} value={d}>
                  {d}
                </option>
              ))}
            </select>
          </div>

          <select className="select-input" value={levelFilter} onChange={(e) => setLevelFilter(e.target.value)}>
            <option value="ALL">All Priority Levels</option>
            <option value="Critical">Critical Only</option>
            <option value="High">High Only</option>
            <option value="Medium">Medium Only</option>
            <option value="Low">Low Only</option>
          </select>
        </div>

        <div style={{ fontSize: '0.85rem', color: '#64748b', fontWeight: 500 }}>
          Showing <strong>{filtered.length}</strong> of {bottlenecks.length} detected bottlenecks
        </div>
      </div>

      {/* Bottlenecks List / Grid */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        {filtered.map((issue) => {
          const isCritical = issue.priority_level === 'Critical';
          return (
            <div
              key={issue.issue_id}
              className="card"
              style={{
                borderLeft: `4px solid ${
                  isCritical ? '#dc2626' : issue.priority_level === 'High' ? '#d97706' : '#2563eb'
                }`,
                marginBottom: 0,
              }}
            >
              <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: '1rem' }}>
                <div style={{ flex: 1 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.25rem' }}>
                    <span style={{ fontSize: '0.75rem', color: '#64748b', fontFamily: 'monospace', fontWeight: 600 }}>
                      {issue.issue_id}
                    </span>
                    <Badge label={issue.issue_type.replace(/_/g, ' ')} variant="default" />
                    {issue.escalation_required && <Badge label="Executive Escalation" variant="critical" />}
                  </div>

                  <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: '#0f172a', marginBottom: '0.35rem' }}>
                    {issue.title}
                  </h3>

                  <div style={{ display: 'flex', alignItems: 'center', gap: '1.25rem', fontSize: '0.8rem', color: '#64748b', marginBottom: '0.75rem' }}>
                    <span>Dept: <strong>{issue.affected_department}</strong></span>
                    <span>Team: <strong>{issue.responsible_team}</strong></span>
                    <span>Impact: <strong>{issue.operational_impact}</strong></span>
                  </div>

                  {/* Supporting Evidence preview */}
                  <div style={{ background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: '6px', padding: '0.65rem 0.85rem', marginBottom: '0.75rem' }}>
                    <div style={{ fontSize: '0.75rem', fontWeight: 600, color: '#475569', textTransform: 'uppercase', marginBottom: '0.25rem' }}>
                      Key Supporting Telemetry Evidence:
                    </div>
                    <ul style={{ paddingLeft: '1.2rem', fontSize: '0.825rem', color: '#334155', lineHeight: 1.5 }}>
                      {issue.evidence.slice(0, 2).map((ev, idx) => (
                        <li key={idx}>{ev}</li>
                      ))}
                    </ul>
                  </div>

                  {/* Action preview */}
                  {issue.recommended_actions.length > 0 && (
                    <div style={{ fontSize: '0.825rem', color: '#0d9488', fontWeight: 500 }}>
                      → Recommended: {issue.recommended_actions[0]}
                    </div>
                  )}
                </div>

                {/* Score & View Button */}
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '0.65rem', flexShrink: 0 }}>
                  <div style={{ textAlign: 'right' }}>
                    <div style={{ fontSize: '1.35rem', fontWeight: 800, color: isCritical ? '#dc2626' : '#0f172a' }}>
                      {issue.priority_score}<span style={{ fontSize: '0.8rem', fontWeight: 500, color: '#94a3b8' }}>/100</span>
                    </div>
                    <Badge label={issue.priority_level} variant={issue.priority_level.toLowerCase() as any} />
                  </div>

                  <button className="btn btn-outline btn-sm" onClick={() => setSelectedIssue(issue)}>
                    <Eye size={14} />
                    <span>View Evidence</span>
                  </button>
                </div>
              </div>
            </div>
          );
        })}

        {filtered.length === 0 && (
          <div className="card" style={{ textAlign: 'center', padding: '3rem' }}>
            <AlertTriangle size={32} color="#94a3b8" style={{ margin: '0 auto 0.75rem auto' }} />
            <h3 style={{ fontSize: '1rem', fontWeight: 600, color: '#475569' }}>No bottlenecks match active filters</h3>
            <p style={{ fontSize: '0.85rem', color: '#64748b' }}>Try clearing the search query or selecting "All Departments".</p>
          </div>
        )}
      </div>

      {/* Issue Detail Modal */}
      <Modal
        isOpen={!!selectedIssue}
        onClose={() => setSelectedIssue(null)}
        title={selectedIssue ? `Bottleneck: ${selectedIssue.title}` : ''}
        footer={
          <button className="btn btn-primary btn-sm" onClick={() => setSelectedIssue(null)}>
            Close
          </button>
        }
      >
        {selectedIssue && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
              <Badge label={`ID: ${selectedIssue.issue_id}`} variant="default" />
              <Badge label={`Dept: ${selectedIssue.affected_department}`} variant="default" />
              <Badge label={`Priority: ${selectedIssue.priority_level} (${selectedIssue.priority_score}/100)`} variant={selectedIssue.priority_level.toLowerCase() as any} />
              {selectedIssue.escalation_required && <Badge label="Executive Escalation Required" variant="critical" />}
            </div>

            <div>
              <h4 style={{ fontSize: '0.85rem', fontWeight: 700, color: '#0f172a', marginBottom: '0.35rem' }}>
                Supporting Evidence from Records
              </h4>
              <ul style={{ paddingLeft: '1.2rem', fontSize: '0.85rem', color: '#334155', lineHeight: 1.6 }}>
                {selectedIssue.evidence.map((ev, i) => (
                  <li key={i}>{ev}</li>
                ))}
              </ul>
            </div>

            <div>
              <h4 style={{ fontSize: '0.85rem', fontWeight: 700, color: '#0f172a', marginBottom: '0.35rem' }}>
                Plausible Operational Drivers
              </h4>
              <ul style={{ paddingLeft: '1.2rem', fontSize: '0.85rem', color: '#475569', lineHeight: 1.6 }}>
                {selectedIssue.possible_causes.map((c, i) => (
                  <li key={i}>{c}</li>
                ))}
              </ul>
            </div>

            <div>
              <h4 style={{ fontSize: '0.85rem', fontWeight: 700, color: '#0f172a', marginBottom: '0.35rem' }}>
                Recommended Operational Actions
              </h4>
              <ul style={{ paddingLeft: '1.2rem', fontSize: '0.85rem', color: '#0d9488', lineHeight: 1.6 }}>
                {selectedIssue.recommended_actions.map((a, i) => (
                  <li key={i}>{a}</li>
                ))}
              </ul>
            </div>

            <div style={{ background: '#f8fafc', padding: '0.75rem', borderRadius: '6px', fontSize: '0.8rem', color: '#64748b' }}>
              <div>Responsible Operational Team: <strong>{selectedIssue.responsible_team}</strong></div>
              <div>Urgency Rating: <strong>{selectedIssue.urgency}</strong> | Operational Impact: <strong>{selectedIssue.operational_impact}</strong></div>
              <div>Status: <strong>{selectedIssue.status}</strong></div>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
};
