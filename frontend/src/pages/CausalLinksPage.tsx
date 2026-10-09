import React from 'react';
import { Network, ArrowRight, ShieldAlert, AlertTriangle, CheckCircle2, HelpCircle } from 'lucide-react';
import { CausalLink } from '../types';
import { Badge } from '../components/Badge';

interface CausalLinksPageProps {
  causalLinks: CausalLink[];
  loading: boolean;
}

export const CausalLinksPage: React.FC<CausalLinksPageProps> = ({ causalLinks, loading }) => {
  if (loading) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '60vh' }}>
        <div className="spinner" style={{ width: 40, height: 40 }} />
      </div>
    );
  }

  return (
    <div>
      {/* Causal Methodology Banner */}
      <div className="alert-box alert-info">
        <Network size={18} color="#2563eb" style={{ flexShrink: 0, marginTop: 2 }} />
        <div>
          <strong>Cross-Domain Causal Reasoning:</strong> Rather than displaying independent KPIs, FlowCare AI correlates
          operational signals across Admissions, Discharges, Beds, Central Lab, and Shift Rosters to explain <em>why</em> delays compound.
          All causal connections are grounded in verifiable records with explicit operational uncertainty notes.
        </div>
      </div>

      {/* Visual Flow diagram summary */}
      <div className="card" style={{ background: '#f8fafc', padding: '1.25rem' }}>
        <div style={{ fontSize: '0.8rem', fontWeight: 700, color: '#475569', textTransform: 'uppercase', marginBottom: '0.75rem' }}>
          Sanjeevani Hospital Operational Bottleneck Propagation Path:
        </div>
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            flexWrap: 'wrap',
            gap: '0.75rem',
            background: '#ffffff',
            border: '1px solid #e2e8f0',
            borderRadius: '8px',
            padding: '1rem',
          }}
        >
          <div style={{ textAlign: 'center', flex: 1, minWidth: 160 }}>
            <div style={{ fontSize: '0.75rem', fontWeight: 700, color: '#dc2626' }}>1. DISCHARGE DELAY</div>
            <div style={{ fontSize: '0.85rem', fontWeight: 600 }}>Beds EMERG-03 &amp; 04</div>
            <div style={{ fontSize: '0.7rem', color: '#64748b' }}>Pending TPA &amp; signatures</div>
          </div>
          <ArrowRight size={18} color="#94a3b8" />
          <div style={{ textAlign: 'center', flex: 1, minWidth: 160 }}>
            <div style={{ fontSize: '0.75rem', fontWeight: 700, color: '#d97706' }}>2. LAB LATENCY</div>
            <div style={{ fontSize: '0.85rem', fontWeight: 600 }}>Troponin-T Late (~3h)</div>
            <div style={{ fontSize: '0.7rem', color: '#64748b' }}>Beds EMERG-01 &amp; 02 held</div>
          </div>
          <ArrowRight size={18} color="#94a3b8" />
          <div style={{ textAlign: 'center', flex: 1, minWidth: 160 }}>
            <div style={{ fontSize: '0.75rem', fontWeight: 700, color: '#dc2626' }}>3. INTAKE CHOKE</div>
            <div style={{ fontSize: '0.85rem', fontWeight: 600 }}>Emergency Triage Wait</div>
            <div style={{ fontSize: '0.7rem', color: '#64748b' }}>Average wait: 95+ mins</div>
          </div>
          <ArrowRight size={18} color="#94a3b8" />
          <div style={{ textAlign: 'center', flex: 1, minWidth: 160 }}>
            <div style={{ fontSize: '0.75rem', fontWeight: 700, color: '#7c3aed' }}>4. SHIFT RISK</div>
            <div style={{ fontSize: '0.85rem', fontWeight: 600 }}>Evening Roster Gap</div>
            <div style={{ fontSize: '0.7rem', color: '#64748b' }}>Only 1 doctor, 1 nurse</div>
          </div>
        </div>
      </div>

      {/* Causal Links Cards */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
        {causalLinks.map((link) => (
          <div
            key={link.link_id}
            className="card"
            style={{
              borderLeft: '5px solid #0d9488',
              marginBottom: 0,
            }}
          >
            {/* Header */}
            <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: '0.75rem' }}>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.25rem' }}>
                  <span style={{ fontSize: '0.75rem', fontFamily: 'monospace', fontWeight: 700, color: '#64748b' }}>
                    {link.link_id}
                  </span>
                  <Badge label={link.relationship_type.replace(/_/g, ' ')} variant="medium" />
                  <Badge
                    label={`Confidence: ${link.confidence}`}
                    variant={link.confidence === 'High' ? 'available' : 'high'}
                  />
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem', fontSize: '0.95rem', fontWeight: 700, color: '#0f172a' }}>
                  <span>{link.source_department}</span>
                  <ArrowRight size={16} color="#0d9488" />
                  <span>{link.target_department}</span>
                </div>
              </div>

              <div style={{ fontSize: '0.75rem', color: '#64748b', fontFamily: 'monospace' }}>
                {link.source_issue_id} → {link.target_issue_id}
              </div>
            </div>

            {/* Explanation */}
            <div style={{ background: '#f8fafc', padding: '0.85rem 1rem', borderRadius: '6px', border: '1px solid #e2e8f0', marginBottom: '0.75rem' }}>
              <div style={{ fontSize: '0.75rem', fontWeight: 700, color: '#475569', textTransform: 'uppercase', marginBottom: '0.25rem' }}>
                Operational Relationship Explanation:
              </div>
              <p style={{ fontSize: '0.875rem', color: '#1e293b', lineHeight: 1.6 }}>{link.explanation}</p>
            </div>

            {/* Supporting Evidence */}
            <div style={{ marginBottom: '0.75rem' }}>
              <div style={{ fontSize: '0.75rem', fontWeight: 700, color: '#475569', textTransform: 'uppercase', marginBottom: '0.35rem' }}>
                Supporting Evidence from Connected Records:
              </div>
              <ul style={{ paddingLeft: '1.2rem', fontSize: '0.825rem', color: '#334155', lineHeight: 1.5 }}>
                {link.supporting_evidence.map((ev, i) => (
                  <li key={i}>{ev}</li>
                ))}
              </ul>
            </div>

            {/* Uncertainty Note */}
            <div
              style={{
                display: 'flex',
                alignItems: 'flex-start',
                gap: '0.5rem',
                background: '#fffbeb',
                border: '1px solid #fde68a',
                padding: '0.65rem 0.85rem',
                borderRadius: '6px',
                fontSize: '0.775rem',
                color: '#92400e',
              }}
            >
              <HelpCircle size={15} color="#b45309" style={{ flexShrink: 0, marginTop: 2 }} />
              <div>
                <strong>Operational Uncertainty Disclosure:</strong> {link.uncertainty_note}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
