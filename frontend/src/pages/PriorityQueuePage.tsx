import React, { useState } from 'react';
import { ListOrdered, ArrowUpRight, CheckCircle2, ShieldAlert, Plus, Check } from 'lucide-react';
import { BottleneckIssue, Recommendation, ActionCreateRequest } from '../types';
import { Badge } from '../components/Badge';
import { api } from '../services/api';

interface PriorityQueuePageProps {
  priorityQueue: BottleneckIssue[];
  recommendations: Recommendation[];
  loading: boolean;
  onActionCreated?: () => void;
}

export const PriorityQueuePage: React.FC<PriorityQueuePageProps> = ({
  priorityQueue,
  recommendations,
  loading,
  onActionCreated,
}) => {
  const [createdActionRecId, setCreatedActionRecId] = useState<string | null>(null);
  const [isCreating, setIsCreating] = useState(false);

  if (loading) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '60vh' }}>
        <div className="spinner" style={{ width: 40, height: 40 }} />
      </div>
    );
  }

  const handleCreateAction = async (rec: Recommendation, issue: BottleneckIssue) => {
    setIsCreating(true);
    try {
      const payload: ActionCreateRequest = {
        recommendation_id: rec.recommendation_id,
        related_issue_id: issue.issue_id,
        proposed_action: rec.proposed_action,
        responsible_team: rec.responsible_team,
        target_department: issue.affected_department,
        priority: rec.priority,
        notes: `Converted from Priority Queue: ${rec.category}`,
      };
      await api.createAction(payload);
      setCreatedActionRecId(rec.recommendation_id);
      if (onActionCreated) onActionCreated();
      setTimeout(() => setCreatedActionRecId(null), 3000);
    } catch (err: any) {
      alert(`Failed to create simulated action: ${err.message}`);
    } finally {
      setIsCreating(false);
    }
  };

  return (
    <div>
      {/* Priority Scoring Methodology Disclosure */}
      <div className="alert-box alert-info">
        <ListOrdered size={18} color="#2563eb" style={{ flexShrink: 0, marginTop: 2 }} />
        <div>
          <strong>Transparent Operational Prioritization Formula (0–100):</strong>
          <div style={{ marginTop: '0.25rem', fontFamily: 'monospace', fontSize: '0.8rem' }}>
            Score = Urgency Points (10–40) + Impact Points (10–40) + Context Modifiers (+10 Escalation, +2..10 Delay).
          </div>
          <div style={{ marginTop: '0.25rem', fontSize: '0.75rem', color: '#64748b' }}>
            Ranked so hospital supervisors address systemic bottlenecks first. This is strictly an operational triage tool, not a clinical risk metric.
          </div>
        </div>
      </div>

      {/* Priority Queue List */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
        {priorityQueue.map((issue, rank) => {
          const recs = recommendations.filter((r) => r.related_issue_id === issue.issue_id);
          const isCritical = issue.priority_level === 'Critical';

          return (
            <div
              key={issue.issue_id}
              className="card"
              style={{
                borderLeft: `5px solid ${isCritical ? '#dc2626' : issue.priority_level === 'High' ? '#d97706' : '#2563eb'}`,
                marginBottom: 0,
              }}
            >
              {/* Header with Rank & Score */}
              <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: '0.75rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                  <div
                    style={{
                      width: 32,
                      height: 32,
                      borderRadius: 6,
                      background: isCritical ? '#dc2626' : '#0f172a',
                      color: '#ffffff',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontWeight: 800,
                      fontSize: '0.95rem',
                    }}
                  >
                    #{rank + 1}
                  </div>
                  <div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: '#0f172a' }}>{issue.title}</h3>
                      {issue.escalation_required && <Badge label="Executive Alert" variant="critical" />}
                    </div>
                    <div style={{ fontSize: '0.75rem', color: '#64748b' }}>
                      ID: <span style={{ fontFamily: 'monospace' }}>{issue.issue_id}</span> • Department: <strong>{issue.affected_department}</strong>
                    </div>
                  </div>
                </div>

                <div style={{ textAlign: 'right' }}>
                  <div style={{ fontSize: '1.35rem', fontWeight: 800, color: isCritical ? '#dc2626' : '#0f172a' }}>
                    {issue.priority_score}<span style={{ fontSize: '0.8rem', color: '#94a3b8' }}>/100</span>
                  </div>
                  <Badge label={issue.priority_level} variant={issue.priority_level.toLowerCase() as any} />
                </div>
              </div>

              {/* Evidence & Impact */}
              <div
                style={{
                  display: 'grid',
                  gridTemplateColumns: '1fr 1fr',
                  gap: '0.75rem',
                  marginBottom: '1rem',
                  background: '#f8fafc',
                  border: '1px solid #e2e8f0',
                  borderRadius: '6px',
                  padding: '0.75rem',
                  fontSize: '0.825rem',
                }}
              >
                <div>
                  <div style={{ fontWeight: 700, color: '#475569', textTransform: 'uppercase', marginBottom: '0.25rem', fontSize: '0.7rem' }}>
                    Why it Needs Attention:
                  </div>
                  <p style={{ color: '#334155' }}>{issue.evidence[0] || 'Operational delay verified against documented baseline.'}</p>
                </div>
                <div>
                  <div style={{ fontWeight: 700, color: '#475569', textTransform: 'uppercase', marginBottom: '0.25rem', fontSize: '0.7rem' }}>
                    Responsible Operational Team:
                  </div>
                  <p style={{ color: '#334155' }}>
                    <strong>{issue.responsible_team}</strong> (Impact: {issue.operational_impact})
                  </p>
                </div>
              </div>

              {/* Actionable Recommendations linked to this issue */}
              <div>
                <div style={{ fontSize: '0.75rem', fontWeight: 700, color: '#475569', textTransform: 'uppercase', marginBottom: '0.5rem' }}>
                  Recommended Actionable Steps ({recs.length}):
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                  {recs.map((rec) => {
                    const wasCreated = createdActionRecId === rec.recommendation_id;
                    return (
                      <div
                        key={rec.recommendation_id}
                        style={{
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'space-between',
                          background: '#ffffff',
                          border: '1px solid #e2e8f0',
                          borderRadius: '6px',
                          padding: '0.65rem 0.85rem',
                          gap: '1rem',
                        }}
                      >
                        <div style={{ flex: 1 }}>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.2rem' }}>
                            <Badge label={rec.category} variant="medium" />
                            <span style={{ fontSize: '0.75rem', color: '#64748b', fontFamily: 'monospace' }}>
                              {rec.recommendation_id}
                            </span>
                          </div>
                          <div style={{ fontSize: '0.85rem', fontWeight: 600, color: '#0f172a' }}>
                            {rec.proposed_action}
                          </div>
                        </div>

                        <button
                          className={`btn btn-sm ${wasCreated ? 'btn-success' : 'btn-outline'}`}
                          onClick={() => handleCreateAction(rec, issue)}
                          disabled={isCreating || wasCreated}
                          title="Convert this recommendation to a reviewable simulated action"
                        >
                          {wasCreated ? (
                            <>
                              <Check size={14} />
                              <span>Task Queued!</span>
                            </>
                          ) : (
                            <>
                              <Plus size={14} />
                              <span>Queue Task</span>
                            </>
                          )}
                        </button>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
