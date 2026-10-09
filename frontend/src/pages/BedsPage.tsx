import React, { useState } from 'react';
import { Bed as BedIcon, AlertOctagon, CheckCircle2, RefreshCw, Filter, Layers, AlertTriangle } from 'lucide-react';
import { Bed } from '../types';
import { Badge } from '../components/Badge';

interface BedsPageProps {
  beds: Bed[];
  loading: boolean;
}

export const BedsPage: React.FC<BedsPageProps> = ({ beds, loading }) => {
  const [wardFilter, setWardFilter] = useState('ALL');
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [viewMode, setViewMode] = useState<'grid' | 'table'>('grid');

  if (loading) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '60vh' }}>
        <div className="spinner" style={{ width: 40, height: 40 }} />
      </div>
    );
  }

  // Wards and statuses
  const wards = Array.from(new Set(beds.map((b) => b.ward)));

  // Filter
  const filteredBeds = beds.filter((b) => {
    const matchesWard = wardFilter === 'ALL' || b.ward === wardFilter;
    const matchesStatus = statusFilter === 'ALL' || b.availability === statusFilter;
    return matchesWard && matchesStatus;
  });

  // Accurate counts derived directly from beds array
  const totalBeds = beds.length;
  const occupiedCount = beds.filter((b) => b.occupancy === 'Occupied').length;
  const availableCount = beds.filter((b) => b.availability === 'Available').length;
  const blockedCount = beds.filter((b) => b.availability === 'Blocked').length;
  const cleaningCount = beds.filter((b) => b.availability === 'Cleaning').length;

  return (
    <div>
      {/* Strict Operational Consistency Notice */}
      <div className="alert-box alert-warning">
        <AlertTriangle size={18} color="#b45309" style={{ flexShrink: 0, marginTop: 2 }} />
        <div>
          <strong>Operational Capacity Rule:</strong> A blocked bed is <em>never</em> counted as available for a new admission, even if clinically ready for discharge.
          At Sanjeevani Hospital, beds <strong>EMERG-03</strong> and <strong>EMERG-04</strong> remain occupied and blocked by administrative paperwork clearance.
          Authorized staff must complete clearance and cleaning before a bed is released.
        </div>
      </div>

      {/* Summary KPI Badges */}
      <div className="grid-4" style={{ marginBottom: '1rem' }}>
        <div className="card" style={{ padding: '0.85rem 1rem', marginBottom: 0, borderLeft: '4px solid #2563eb' }}>
          <div style={{ fontSize: '0.75rem', color: '#64748b', fontWeight: 600 }}>TOTAL BEDS</div>
          <div style={{ fontSize: '1.45rem', fontWeight: 800 }}>{totalBeds} Units</div>
          <div style={{ fontSize: '0.75rem', color: '#64748b' }}>Across 3 hospital wards</div>
        </div>
        <div className="card" style={{ padding: '0.85rem 1rem', marginBottom: 0, borderLeft: '4px solid #16a34a' }}>
          <div style={{ fontSize: '0.75rem', color: '#64748b', fontWeight: 600 }}>AVAILABLE (READY)</div>
          <div style={{ fontSize: '1.45rem', fontWeight: 800, color: '#16a34a' }}>{availableCount} Units</div>
          <div style={{ fontSize: '0.75rem', color: '#64748b' }}>Unoccupied &amp; sanitized</div>
        </div>
        <div className="card" style={{ padding: '0.85rem 1rem', marginBottom: 0, borderLeft: '4px solid #dc2626' }}>
          <div style={{ fontSize: '0.75rem', color: '#64748b', fontWeight: 600 }}>BLOCKED BEDS</div>
          <div style={{ fontSize: '1.45rem', fontWeight: 800, color: '#dc2626' }}>{blockedCount} Units</div>
          <div style={{ fontSize: '0.75rem', color: '#dc2626', fontWeight: 600 }}>EMERG-03, EMERG-04</div>
        </div>
        <div className="card" style={{ padding: '0.85rem 1rem', marginBottom: 0, borderLeft: '4px solid #d97706' }}>
          <div style={{ fontSize: '0.75rem', color: '#64748b', fontWeight: 600 }}>CLEANING / NOT READY</div>
          <div style={{ fontSize: '1.45rem', fontWeight: 800, color: '#d97706' }}>{cleaningCount} Units</div>
          <div style={{ fontSize: '0.75rem', color: '#64748b' }}>Housekeeping active</div>
        </div>
      </div>

      {/* Filter Bar */}
      <div className="card filter-bar">
        <div className="filter-group">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
            <Filter size={14} color="#64748b" />
            <select className="select-input" value={wardFilter} onChange={(e) => setWardFilter(e.target.value)}>
              <option value="ALL">All Wards ({wards.length})</option>
              {wards.map((w) => (
                <option key={w} value={w}>
                  {w}
                </option>
              ))}
            </select>
          </div>

          <select className="select-input" value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
            <option value="ALL">All Bed Statuses</option>
            <option value="Available">Available Only</option>
            <option value="Occupied">Occupied (Active Care)</option>
            <option value="Blocked">Blocked Only</option>
            <option value="Cleaning">Cleaning Required</option>
          </select>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <button
            className={`btn btn-sm ${viewMode === 'grid' ? 'btn-primary' : 'btn-outline'}`}
            onClick={() => setViewMode('grid')}
          >
            Grid View
          </button>
          <button
            className={`btn btn-sm ${viewMode === 'table' ? 'btn-primary' : 'btn-outline'}`}
            onClick={() => setViewMode('table')}
          >
            Table View
          </button>
        </div>
      </div>

      {/* Grid Mode */}
      {viewMode === 'grid' && (
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
            gap: '1rem',
          }}
        >
          {filteredBeds.map((bed) => {
            const isBlocked = bed.availability === 'Blocked';
            return (
              <div
                key={bed.bed_id}
                className={`bed-card ${bed.availability.toLowerCase()} ${isBlocked ? 'blocked-highlight' : ''}`}
              >
                <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                  <div>
                    <span style={{ fontSize: '1.05rem', fontWeight: 800, color: isBlocked ? '#dc2626' : '#0f172a' }}>
                      {bed.bed_id}
                    </span>
                    <div style={{ fontSize: '0.75rem', color: '#64748b' }}>
                      {bed.ward} • {bed.bed_type}
                    </div>
                  </div>
                  <Badge label={bed.availability} variant={bed.availability.toLowerCase() as any} />
                </div>

                <div style={{ fontSize: '0.8rem', color: '#475569', marginBottom: '0.35rem' }}>
                  Workflow: <strong>{bed.admission_discharge_status}</strong>
                </div>

                {bed.current_admission_id && (
                  <div style={{ fontSize: '0.75rem', color: '#64748b', fontFamily: 'monospace' }}>
                    Linked Admission: <strong>{bed.current_admission_id}</strong>
                  </div>
                )}

                {bed.blocked_reason && (
                  <div
                    style={{
                      marginTop: '0.5rem',
                      background: '#fef2f2',
                      border: '1px solid #fecaca',
                      borderRadius: '4px',
                      padding: '0.45rem 0.6rem',
                      fontSize: '0.75rem',
                      color: '#991b1b',
                      lineHeight: 1.4,
                    }}
                  >
                    <strong>Blocked Reason:</strong> {bed.blocked_reason}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}

      {/* Table Mode */}
      {viewMode === 'table' && (
        <div className="card table-responsive">
          <table className="data-table">
            <thead>
              <tr>
                <th>Bed ID</th>
                <th>Ward</th>
                <th>Bed Type</th>
                <th>Occupancy</th>
                <th>Availability</th>
                <th>Admission / Discharge State</th>
                <th>Linked Admission</th>
                <th>Blocked Reason</th>
              </tr>
            </thead>
            <tbody>
              {filteredBeds.map((b) => (
                <tr key={b.bed_id} style={{ background: b.availability === 'Blocked' ? '#fef2f2' : undefined }}>
                  <td style={{ fontWeight: 700, color: b.availability === 'Blocked' ? '#dc2626' : undefined }}>
                    {b.bed_id}
                  </td>
                  <td>{b.ward}</td>
                  <td>{b.bed_type}</td>
                  <td>{b.occupancy}</td>
                  <td>
                    <Badge label={b.availability} variant={b.availability.toLowerCase() as any} />
                  </td>
                  <td>{b.admission_discharge_status}</td>
                  <td style={{ fontFamily: 'monospace', fontSize: '0.8rem' }}>{b.current_admission_id || '—'}</td>
                  <td style={{ fontSize: '0.8rem', color: b.blocked_reason ? '#991b1b' : '#64748b', maxWidth: 260 }}>
                    {b.blocked_reason || '—'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};
