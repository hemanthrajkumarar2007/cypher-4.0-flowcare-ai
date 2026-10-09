import React, { useState } from 'react';
import {
  ClipboardList,
  CheckCircle2,
  XCircle,
  Clock,
  History,
  Check,
  RotateCcw,
  UserCheck,
  Shield,
} from 'lucide-react';
import { SimulatedAction, AuditLogEntry, ActionReviewRequest, ActionCompleteRequest } from '../types';
import { Badge } from '../components/Badge';
import { Modal } from '../components/Modal';
import { api } from '../services/api';

interface ActionsAuditPageProps {
  actions: SimulatedAction[];
  auditLog: AuditLogEntry[];
  loading: boolean;
  onRefresh: () => void;
}

export const ActionsAuditPage: React.FC<ActionsAuditPageProps> = ({
  actions,
  auditLog,
  loading,
  onRefresh,
}) => {
  const [activeTab, setActiveTab] = useState<'actions' | 'audit'>('actions');
  const [reviewingAction, setReviewingAction] = useState<SimulatedAction | null>(null);
  const [completingAction, setCompletingAction] = useState<SimulatedAction | null>(null);

  // Form states
  const [reviewerLabel, setReviewerLabel] = useState('Dr. Ramesh Gupta (Shift Medical Officer)');
  const [reviewNotes, setReviewNotes] = useState('');
  const [completeNotes, setCompleteNotes] = useState('Task executed and verified in simulation environment.');
  const [submitting, setSubmitting] = useState(false);

  if (loading) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '60vh' }}>
        <div className="spinner" style={{ width: 40, height: 40 }} />
      </div>
    );
  }

  const handleReview = async (status: 'Approved' | 'Rejected') => {
    if (!reviewingAction) return;
    setSubmitting(true);
    try {
      const payload: ActionReviewRequest = {
        status,
        reviewer_label: reviewerLabel || 'Authorized Operator',
        notes: reviewNotes || undefined,
      };
      await api.reviewAction(reviewingAction.action_id, payload);
      setReviewingAction(null);
      setReviewNotes('');
      onRefresh();
    } catch (err: any) {
      alert(`Review Failed: ${err.message}`);
    } finally {
      setSubmitting(false);
    }
  };

  const handleComplete = async () => {
    if (!completingAction) return;
    setSubmitting(true);
    try {
      const payload: ActionCompleteRequest = {
        reviewer_label: reviewerLabel || 'Floor Supervisor',
        notes: completeNotes || undefined,
      };
      await api.completeAction(completingAction.action_id, payload);
      setCompletingAction(null);
      setCompleteNotes('');
      onRefresh();
    } catch (err: any) {
      alert(`Completion Failed: ${err.message}`);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div>
      {/* Safeguard Banner */}
      <div className="alert-box alert-warning">
        <Shield size={18} color="#b45309" style={{ flexShrink: 0, marginTop: 2 }} />
        <div>
          <strong>Human-in-the-Loop Operational Safeguard:</strong> FlowCare AI recommends simulated actions but
          <strong> never executes automated clinical or operational changes</strong> without authorized operator review.
          Every state transition is timestamped and recorded in the immutable audit log below.
        </div>
      </div>

      {/* Tabs */}
      <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1.25rem' }}>
        <button
          className={`btn ${activeTab === 'actions' ? 'btn-primary' : 'btn-outline'}`}
          onClick={() => setActiveTab('actions')}
        >
          <ClipboardList size={16} />
          <span>Simulated Tasks Queue ({actions.length})</span>
        </button>
        <button
          className={`btn ${activeTab === 'audit' ? 'btn-primary' : 'btn-outline'}`}
          onClick={() => setActiveTab('audit')}
        >
          <History size={16} />
          <span>Historical Audit Log ({auditLog.length})</span>
        </button>
      </div>

      {/* TAB 1: ACTIONS QUEUE */}
      {activeTab === 'actions' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {actions.map((act) => {
            const isAwaiting = act.status === 'Awaiting review';
            const isApproved = act.status === 'Approved';
            const isCompleted = act.status === 'Completed';
            const isRejected = act.status === 'Rejected';

            return (
              <div
                key={act.action_id}
                className="card"
                style={{
                  borderLeft: `5px solid ${
                    isCompleted ? '#16a34a' : isApproved ? '#2563eb' : isRejected ? '#64748b' : '#d97706'
                  }`,
                  marginBottom: 0,
                }}
              >
                <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: '1rem' }}>
                  <div style={{ flex: 1 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.25rem' }}>
                      <span style={{ fontSize: '0.75rem', fontFamily: 'monospace', fontWeight: 700, color: '#64748b' }}>
                        {act.action_id}
                      </span>
                      <Badge label={`Priority: ${act.priority}`} variant={act.priority.toLowerCase() as any} />
                      <Badge label={`Dept: ${act.target_department}`} variant="default" />
                      <Badge label={`Team: ${act.responsible_team}`} variant="default" />
                    </div>

                    <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: '#0f172a', marginBottom: '0.35rem' }}>
                      {act.title}
                    </h3>

                    <p style={{ fontSize: '0.875rem', color: '#334155', lineHeight: 1.5, marginBottom: '0.65rem' }}>
                      {act.description}
                    </p>

                    <div style={{ display: 'flex', gap: '1rem', fontSize: '0.75rem', color: '#64748b', background: '#f8fafc', padding: '0.4rem 0.65rem', borderRadius: '4px' }}>
                      <span>Created By: <strong>{act.created_by}</strong></span>
                      <span>Created: <strong>{act.created_at.replace('T', ' ').slice(0, 19)}</strong></span>
                      {act.reviewed_by && (
                        <span>Reviewed By: <strong>{act.reviewed_by}</strong></span>
                      )}
                      {act.completed_at && (
                        <span style={{ color: '#16a34a' }}>Completed: <strong>{act.completed_at.replace('T', ' ').slice(0, 19)}</strong></span>
                      )}
                    </div>

                    {act.review_notes && (
                      <div style={{ marginTop: '0.45rem', fontSize: '0.75rem', color: '#475569' }}>
                        <strong>Review Notes:</strong> {act.review_notes}
                      </div>
                    )}
                  </div>

                  {/* Action Controls */}
                  <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '0.5rem', flexShrink: 0 }}>
                    <Badge
                      label={act.status}
                      variant={isCompleted ? 'available' : isApproved ? 'occupied' : isRejected ? 'default' : 'high'}
                    />

                    {isAwaiting && (
                      <div style={{ display: 'flex', gap: '0.4rem', marginTop: '0.5rem' }}>
                        <button
                          className="btn btn-primary btn-sm"
                          onClick={() => {
                            setReviewingAction(act);
                            setReviewNotes('');
                          }}
                        >
                          <UserCheck size={14} />
                          <span>Review Task</span>
                        </button>
                      </div>
                    )}

                    {isApproved && (
                      <button
                        className="btn btn-success btn-sm"
                        style={{ marginTop: '0.5rem' }}
                        onClick={() => {
                          setCompletingAction(act);
                          setCompleteNotes('');
                        }}
                      >
                        <Check size={14} />
                        <span>Complete Task</span>
                      </button>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* TAB 2: AUDIT LOG TABLE */}
      {activeTab === 'audit' && (
        <div className="card table-responsive">
          <table className="data-table">
            <thead>
              <tr>
                <th>Audit ID</th>
                <th>Action ID</th>
                <th>Transition</th>
                <th>Timestamp</th>
                <th>Authorized Reviewer</th>
                <th>Audit Notes</th>
              </tr>
            </thead>
            <tbody>
              {auditLog.map((log) => (
                <tr key={log.audit_id}>
                  <td style={{ fontWeight: 700, fontFamily: 'monospace' }}>{log.audit_id}</td>
                  <td style={{ fontFamily: 'monospace', color: '#2563eb' }}>{log.action_id}</td>
                  <td>
                    <span style={{ color: '#64748b' }}>{log.previous_status}</span>
                    <span style={{ margin: '0 0.35rem', color: '#0d9488' }}>→</span>
                    <strong style={{ color: '#0f172a' }}>{log.new_status}</strong>
                  </td>
                  <td style={{ fontSize: '0.8rem', color: '#64748b' }}>{log.timestamp.replace('T', ' ').slice(0, 19)}</td>
                  <td style={{ fontWeight: 600 }}>{log.reviewer_label}</td>
                  <td style={{ fontSize: '0.8rem', color: '#475569', maxWidth: 300 }}>{log.notes || '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Operator Review Modal */}
      <Modal
        isOpen={!!reviewingAction}
        onClose={() => setReviewingAction(null)}
        title={reviewingAction ? `Authorized Review: ${reviewingAction.action_id}` : ''}
        footer={
          <>
            <button
              className="btn btn-danger btn-sm"
              disabled={submitting}
              onClick={() => handleReview('Rejected')}
            >
              <XCircle size={14} />
              <span>Reject Action</span>
            </button>
            <button
              className="btn btn-primary btn-sm"
              disabled={submitting}
              onClick={() => handleReview('Approved')}
            >
              <CheckCircle2 size={14} />
              <span>Approve Action</span>
            </button>
          </>
        }
      >
        {reviewingAction && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
            <div>
              <label style={{ fontSize: '0.75rem', fontWeight: 600, color: '#475569', textTransform: 'uppercase' }}>
                Proposed Task:
              </label>
              <div style={{ fontSize: '0.9rem', fontWeight: 600, color: '#0f172a', marginTop: '0.2rem' }}>
                {reviewingAction.title}
              </div>
              <div style={{ fontSize: '0.8rem', color: '#475569', marginTop: '0.2rem' }}>
                {reviewingAction.description}
              </div>
            </div>

            <div>
              <label style={{ fontSize: '0.75rem', fontWeight: 600, color: '#475569', display: 'block', marginBottom: '0.25rem' }}>
                Reviewer Label / Title:
              </label>
              <input
                type="text"
                className="search-input"
                style={{ width: '100%' }}
                value={reviewerLabel}
                onChange={(e) => setReviewerLabel(e.target.value)}
              />
            </div>

            <div>
              <label style={{ fontSize: '0.75rem', fontWeight: 600, color: '#475569', display: 'block', marginBottom: '0.25rem' }}>
                Operational Review Notes (Optional):
              </label>
              <textarea
                className="search-input"
                style={{ width: '100%', minHeight: 70, resize: 'vertical' }}
                placeholder="Enter approval condition or rejection rationale..."
                value={reviewNotes}
                onChange={(e) => setReviewNotes(e.target.value)}
              />
            </div>
          </div>
        )}
      </Modal>

      {/* Operator Complete Modal */}
      <Modal
        isOpen={!!completingAction}
        onClose={() => setCompletingAction(null)}
        title={completingAction ? `Complete Action: ${completingAction.action_id}` : ''}
        footer={
          <button
            className="btn btn-success btn-sm"
            disabled={submitting}
            onClick={handleComplete}
          >
            <Check size={14} />
            <span>Mark Completed</span>
          </button>
        }
      >
        {completingAction && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
            <p style={{ fontSize: '0.85rem', color: '#334155' }}>
              Confirm that simulated task <strong>{completingAction.action_id}</strong> (<em>{completingAction.title}</em>) has been finalized.
            </p>

            <div>
              <label style={{ fontSize: '0.75rem', fontWeight: 600, color: '#475569', display: 'block', marginBottom: '0.25rem' }}>
                Completion Verification Notes:
              </label>
              <textarea
                className="search-input"
                style={{ width: '100%', minHeight: 70 }}
                value={completeNotes}
                onChange={(e) => setCompleteNotes(e.target.value)}
              />
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
};
