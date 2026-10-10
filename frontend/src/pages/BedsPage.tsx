import React, { useState } from 'react';
import {
  Bed as BedIcon,
  AlertOctagon,
  CheckCircle2,
  RefreshCw,
  Filter,
  Layers,
  AlertTriangle,
  Download,
  Search,
  UserCheck,
  Sparkles,
  Zap,
  Edit3,
  X,
  Check,
  Clock,
} from 'lucide-react';
import { Bed, BedUpdateRequest, Patient } from '../types';
import { Badge } from '../components/Badge';
import { Modal } from '../components/Modal';

interface BedsPageProps {
  beds: Bed[];
  patients?: Patient[];
  loading: boolean;
  onBedUpdate?: (bedId: string, updates: BedUpdateRequest) => Promise<void>;
}

export const BedsPage: React.FC<BedsPageProps> = ({ beds, patients = [], loading, onBedUpdate }) => {
  const [wardFilter, setWardFilter] = useState('ALL');
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [searchQuery, setSearchQuery] = useState('');
  const [viewMode, setViewMode] = useState<'grid' | 'table'>('grid');

  // Interactive State Allocation Modal
  const [selectedBed, setSelectedBed] = useState<Bed | null>(null);
  const [editAvailability, setEditAvailability] = useState('Available');
  const [editOccupancy, setEditOccupancy] = useState('Unoccupied');
  const [editStatus, setEditStatus] = useState('Ready for Admission');
  const [editPatientId, setEditPatientId] = useState('');
  const [editBlockedReason, setEditBlockedReason] = useState('');
  const [isSaving, setIsSaving] = useState(false);
  const [quickLoadingId, setQuickLoadingId] = useState<string | null>(null);

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
    const matchesSearch =
      searchQuery.trim() === '' ||
      b.bed_id.toLowerCase().includes(searchQuery.toLowerCase()) ||
      b.ward.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (b.patient_id && b.patient_id.toLowerCase().includes(searchQuery.toLowerCase())) ||
      (b.blocked_reason && b.blocked_reason.toLowerCase().includes(searchQuery.toLowerCase())) ||
      b.admission_discharge_status.toLowerCase().includes(searchQuery.toLowerCase());

    return matchesWard && matchesStatus && matchesSearch;
  });

  // Accurate counts derived directly from live beds array
  const totalBeds = beds.length;
  const occupiedCount = beds.filter((b) => b.occupancy === 'Occupied').length;
  const availableCount = beds.filter((b) => b.availability === 'Available').length;
  const blockedCount = beds.filter((b) => b.availability === 'Blocked').length;
  const cleaningCount = beds.filter((b) => b.availability === 'Cleaning').length;

  // Open Edit Modal
  const handleOpenEdit = (bed: Bed) => {
    setSelectedBed(bed);
    setEditAvailability(bed.availability);
    setEditOccupancy(bed.occupancy);
    setEditStatus(bed.admission_discharge_status);
    setEditPatientId(bed.patient_id || '');
    setEditBlockedReason(bed.blocked_reason || '');
  };

  // Quick Action: Instant Unblock
  const handleQuickUnblock = async (bed: Bed) => {
    if (!onBedUpdate) return;
    setQuickLoadingId(bed.bed_id);
    try {
      await onBedUpdate(bed.bed_id, {
        availability: 'Available',
        occupancy: 'Unoccupied',
        admission_discharge_status: 'Available - Ready for Admission',
        blocked_reason: '',
      });
    } finally {
      setQuickLoadingId(null);
    }
  };

  // Quick Action: Mark Cleaned & Ready
  const handleQuickMarkClean = async (bed: Bed) => {
    if (!onBedUpdate) return;
    setQuickLoadingId(bed.bed_id);
    try {
      await onBedUpdate(bed.bed_id, {
        availability: 'Available',
        occupancy: 'Unoccupied',
        admission_discharge_status: 'Available - Sanitized',
      });
    } finally {
      setQuickLoadingId(null);
    }
  };

  // Quick Action: Send to Housekeeping
  const handleQuickSendCleaning = async (bed: Bed) => {
    if (!onBedUpdate) return;
    setQuickLoadingId(bed.bed_id);
    try {
      await onBedUpdate(bed.bed_id, {
        availability: 'Cleaning',
        occupancy: 'Unoccupied',
        admission_discharge_status: 'Cleaning Required',
        patient_id: '',
      });
    } finally {
      setQuickLoadingId(null);
    }
  };

  // Save Modal Changes
  const handleSaveModal = async () => {
    if (!selectedBed || !onBedUpdate) return;
    setIsSaving(true);
    try {
      await onBedUpdate(selectedBed.bed_id, {
        availability: editAvailability,
        occupancy: editOccupancy,
        admission_discharge_status: editStatus,
        patient_id: editPatientId.trim() || undefined,
        blocked_reason: editAvailability === 'Blocked' ? editBlockedReason : undefined,
      });
      setSelectedBed(null);
    } catch (err: any) {
      alert(`Error updating bed: ${err.message}`);
    } finally {
      setIsSaving(false);
    }
  };

  // Export Beds to CSV
  const handleExportCsv = () => {
    const headers = ['Bed ID', 'Ward', 'Bed Type', 'Occupancy', 'Availability', 'Status', 'Patient ID', 'Blocked Reason'];
    const rows = filteredBeds.map((b) => [
      b.bed_id,
      `"${b.ward}"`,
      b.bed_type,
      b.occupancy,
      b.availability,
      `"${b.admission_discharge_status}"`,
      b.patient_id || '',
      `"${(b.blocked_reason || '').replace(/"/g, '""')}"`,
    ]);

    const csvContent = 'data:text/csv;charset=utf-8,' + [headers.join(','), ...rows.map((r) => r.join(','))].join('\n');
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', `sanjeevani_beds_allocation_${new Date().toISOString().slice(0, 10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  // Waiting patients list
  const waitingPatients = patients.filter(
    (p) => p.status.toLowerCase().includes('wait') || p.status.toLowerCase().includes('await')
  );

  return (
    <div>
      {/* Strict Operational Consistency Notice */}
      <div className="alert-box alert-warning">
        <AlertTriangle size={18} color="var(--high-amber)" style={{ flexShrink: 0, marginTop: 2 }} />
        <div>
          <strong>Operational Capacity Rule:</strong> A blocked bed is <em>never</em> counted as available for a new admission, even if clinically ready for discharge.
          Use the <strong>"Change Allocation / State"</strong> controls below to unblock cleared beds, dispatch to housekeeping, or allocate arriving patients to verified available units.
        </div>
      </div>

      {/* Summary KPI Badges */}
      <div className="grid-4" style={{ marginBottom: '1.25rem' }}>
        <div className="card" style={{ padding: '0.85rem 1rem', marginBottom: 0, borderLeft: '4px solid var(--primary-blue)' }}>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600 }}>TOTAL CAPACITY</div>
          <div style={{ fontSize: '1.45rem', fontWeight: 800, color: 'var(--text-primary)' }}>{totalBeds} Units</div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Across {wards.length} hospital wards</div>
        </div>
        <div className="card" style={{ padding: '0.85rem 1rem', marginBottom: 0, borderLeft: '4px solid var(--success-green)' }}>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600 }}>AVAILABLE (READY)</div>
          <div style={{ fontSize: '1.45rem', fontWeight: 800, color: 'var(--success-green)' }}>{availableCount} Units</div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Sanitized &amp; unallocated</div>
        </div>
        <div className="card" style={{ padding: '0.85rem 1rem', marginBottom: 0, borderLeft: '4px solid var(--critical-red)' }}>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600 }}>BLOCKED BEDS</div>
          <div style={{ fontSize: '1.45rem', fontWeight: 800, color: 'var(--critical-red)' }}>{blockedCount} Units</div>
          <div style={{ fontSize: '0.75rem', color: 'var(--critical-red)', fontWeight: 600 }}>Holds &amp; Paperwork delays</div>
        </div>
        <div className="card" style={{ padding: '0.85rem 1rem', marginBottom: 0, borderLeft: '4px solid var(--high-amber)' }}>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600 }}>CLEANING / NOT READY</div>
          <div style={{ fontSize: '1.45rem', fontWeight: 800, color: 'var(--high-amber)' }}>{cleaningCount} Units</div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Housekeeping active</div>
        </div>
      </div>

      {/* Filter and Productivity Bar */}
      <div className="card filter-bar">
        <div className="filter-group">
          {/* Quick Search */}
          <div style={{ position: 'relative', display: 'flex', alignItems: 'center' }}>
            <Search size={14} color="var(--text-muted)" style={{ position: 'absolute', left: 10 }} />
            <input
              type="text"
              className="search-input"
              placeholder="Search bed ID, ward, patient, or hold..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              style={{ paddingLeft: '1.9rem', width: 260 }}
            />
          </div>

          {/* Ward Selector */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
            <Filter size={14} color="var(--text-muted)" />
            <select className="select-input" value={wardFilter} onChange={(e) => setWardFilter(e.target.value)}>
              <option value="ALL">All Wards ({wards.length})</option>
              {wards.map((w) => (
                <option key={w} value={w}>
                  {w}
                </option>
              ))}
            </select>
          </div>

          {/* Status Selector */}
          <select className="select-input" value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
            <option value="ALL">All Bed Statuses</option>
            <option value="Available">Available (Ready for Admission)</option>
            <option value="Occupied">Occupied (Active Care)</option>
            <option value="Blocked">Blocked Holds Only</option>
            <option value="Cleaning">Cleaning Required</option>
          </select>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          {/* Export CSV */}
          <button
            className="btn btn-outline btn-sm"
            onClick={handleExportCsv}
            title="Download beds data as CSV"
          >
            <Download size={14} />
            <span>Export CSV</span>
          </button>

          {/* View Mode Toggle */}
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
            gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
            gap: '1rem',
          }}
        >
          {filteredBeds.map((bed) => {
            const isBlocked = bed.availability === 'Blocked';
            const isCleaning = bed.availability === 'Cleaning';
            const isAvailable = bed.availability === 'Available';
            const isOccupied = bed.availability === 'Occupied';
            const isActionLoading = quickLoadingId === bed.bed_id;

            return (
              <div
                key={bed.bed_id}
                className={`bed-card ${bed.availability.toLowerCase()} ${isBlocked ? 'blocked-highlight' : ''}`}
              >
                <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: '0.65rem' }}>
                  <div>
                    <span style={{ fontSize: '1.15rem', fontWeight: 800, color: isBlocked ? 'var(--critical-red)' : 'var(--text-primary)' }}>
                      {bed.bed_id}
                    </span>
                    <div style={{ fontSize: '0.785rem', color: 'var(--text-muted)' }}>
                      {bed.ward} • {bed.bed_type}
                    </div>
                  </div>
                  <Badge label={bed.availability} variant={bed.availability.toLowerCase() as any} />
                </div>

                <div style={{ fontSize: '0.825rem', color: 'var(--text-secondary)', marginBottom: '0.4rem' }}>
                  Workflow: <strong>{bed.admission_discharge_status}</strong>
                </div>

                {bed.patient_id && (
                  <div style={{ fontSize: '0.785rem', color: 'var(--text-secondary)', marginBottom: '0.3rem' }}>
                    Allocated Patient: <strong style={{ color: 'var(--primary-blue)', fontFamily: 'monospace' }}>{bed.patient_id}</strong>
                  </div>
                )}

                {bed.current_admission_id && (
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontFamily: 'monospace', marginBottom: '0.3rem' }}>
                    Admission: <strong>{bed.current_admission_id}</strong>
                  </div>
                )}

                {bed.blocked_reason && (
                  <div
                    style={{
                      marginTop: '0.5rem',
                      background: 'var(--critical-red-light)',
                      border: '1px solid var(--critical-red-border)',
                      borderRadius: '6px',
                      padding: '0.5rem 0.65rem',
                      fontSize: '0.765rem',
                      color: 'var(--critical-red)',
                      lineHeight: 1.4,
                    }}
                  >
                    <strong>Blocked Reason:</strong> {bed.blocked_reason}
                  </div>
                )}

                {/* Quick Bed State Allocation Actions */}
                <div style={{ marginTop: 'auto', paddingTop: '0.85rem', display: 'flex', gap: '0.4rem', flexWrap: 'wrap' }}>
                  {isBlocked && (
                    <button
                      className="btn btn-sm btn-outline"
                      style={{ color: 'var(--success-green)', borderColor: 'var(--success-green-border)', fontSize: '0.72rem' }}
                      disabled={isActionLoading}
                      onClick={() => handleQuickUnblock(bed)}
                      title="Clear administrative hold and release bed"
                    >
                      <Zap size={12} />
                      <span>{isActionLoading ? 'Updating...' : 'Unblock Bed'}</span>
                    </button>
                  )}

                  {isCleaning && (
                    <button
                      className="btn btn-sm btn-outline"
                      style={{ color: 'var(--success-green)', borderColor: 'var(--success-green-border)', fontSize: '0.72rem' }}
                      disabled={isActionLoading}
                      onClick={() => handleQuickMarkClean(bed)}
                      title="Confirm housekeeping finished"
                    >
                      <Sparkles size={12} />
                      <span>{isActionLoading ? 'Updating...' : 'Mark Clean'}</span>
                    </button>
                  )}

                  {isOccupied && (
                    <button
                      className="btn btn-sm btn-outline"
                      style={{ color: 'var(--high-amber)', borderColor: 'var(--high-amber-border)', fontSize: '0.72rem' }}
                      disabled={isActionLoading}
                      onClick={() => handleQuickSendCleaning(bed)}
                      title="Discharge patient and send bed to cleaning"
                    >
                      <span>Send to Cleaning</span>
                    </button>
                  )}

                  <button
                    className="btn btn-sm btn-outline"
                    style={{ fontSize: '0.72rem', marginLeft: 'auto' }}
                    onClick={() => handleOpenEdit(bed)}
                    title="Change bed allocation, patient, and operational state"
                  >
                    <Edit3 size={12} />
                    <span>Change State</span>
                  </button>
                </div>
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
                <th>Patient ID</th>
                <th>Admission State</th>
                <th>Blocked Reason</th>
                <th style={{ textAlign: 'right' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredBeds.map((b) => (
                <tr key={b.bed_id} style={{ background: b.availability === 'Blocked' ? 'var(--critical-red-light)' : undefined }}>
                  <td style={{ fontWeight: 700, color: b.availability === 'Blocked' ? 'var(--critical-red)' : 'var(--text-primary)' }}>
                    {b.bed_id}
                  </td>
                  <td>{b.ward}</td>
                  <td>{b.bed_type}</td>
                  <td>{b.occupancy}</td>
                  <td>
                    <Badge label={b.availability} variant={b.availability.toLowerCase() as any} />
                  </td>
                  <td style={{ fontFamily: 'monospace', fontWeight: 600, color: 'var(--primary-blue)' }}>
                    {b.patient_id || '—'}
                  </td>
                  <td>{b.admission_discharge_status}</td>
                  <td style={{ fontSize: '0.8rem', color: b.blocked_reason ? 'var(--critical-red)' : 'var(--text-muted)', maxWidth: 240 }}>
                    {b.blocked_reason || '—'}
                  </td>
                  <td style={{ textAlign: 'right' }}>
                    <div style={{ display: 'inline-flex', gap: '0.35rem' }}>
                      {b.availability === 'Blocked' && (
                        <button
                          className="btn btn-sm btn-outline"
                          style={{ color: 'var(--success-green)', fontSize: '0.72rem', padding: '0.2rem 0.5rem' }}
                          onClick={() => handleQuickUnblock(b)}
                        >
                          Unblock
                        </button>
                      )}
                      <button
                        className="btn btn-sm btn-outline"
                        style={{ fontSize: '0.72rem', padding: '0.2rem 0.5rem' }}
                        onClick={() => handleOpenEdit(b)}
                      >
                        Edit State
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Bed State & Allocation Management Modal */}
      {selectedBed && (
        <Modal
          isOpen={!!selectedBed}
          onClose={() => setSelectedBed(null)}
          title={`Bed State & Allocation: ${selectedBed.bed_id} (${selectedBed.ward})`}
          footer={
            <>
              <button className="btn btn-outline" onClick={() => setSelectedBed(null)} disabled={isSaving}>
                Cancel
              </button>
              <button className="btn btn-primary" onClick={handleSaveModal} disabled={isSaving}>
                {isSaving ? 'Applying Changes...' : 'Save & Apply State Changes'}
              </button>
            </>
          }
        >
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            {/* Quick Context Bar */}
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                padding: '0.75rem 1rem',
                background: 'var(--bg-card-subtle)',
                borderRadius: '8px',
                border: '1px solid var(--border-subtle)',
              }}
            >
              <div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>WARD &amp; BED TYPE</div>
                <div style={{ fontWeight: 700, color: 'var(--text-primary)' }}>
                  {selectedBed.ward} • {selectedBed.bed_type}
                </div>
              </div>
              <div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>CURRENT STATE</div>
                <Badge label={selectedBed.availability} variant={selectedBed.availability.toLowerCase() as any} />
              </div>
            </div>

            {/* Availability Target */}
            <div>
              <label style={{ display: 'block', fontSize: '0.825rem', fontWeight: 600, marginBottom: '0.35rem', color: 'var(--text-primary)' }}>
                Target Availability State:
              </label>
              <select
                className="select-input"
                style={{ width: '100%' }}
                value={editAvailability}
                onChange={(e) => {
                  const val = e.target.value;
                  setEditAvailability(val);
                  if (val === 'Available') {
                    setEditOccupancy('Unoccupied');
                    setEditStatus('Available - Ready for Admission');
                    setEditPatientId('');
                    setEditBlockedReason('');
                  } else if (val === 'Cleaning') {
                    setEditOccupancy('Unoccupied');
                    setEditStatus('Cleaning Required');
                    setEditPatientId('');
                  } else if (val === 'Blocked') {
                    setEditStatus('Discharge Paperwork Blocked');
                  } else if (val === 'Occupied') {
                    setEditOccupancy('Occupied');
                    setEditStatus('Admitted');
                  }
                }}
              >
                <option value="Available">Available (Sanitized &amp; Ready for Immediate Admission)</option>
                <option value="Occupied">Occupied (Patient Admitted to Bed)</option>
                <option value="Blocked">Blocked (Hold: Discharge Paperwork or Lab Verification)</option>
                <option value="Cleaning">Cleaning Required (Housekeeping sanitization in progress)</option>
              </select>
            </div>

            {/* Occupancy Target */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
              <div>
                <label style={{ display: 'block', fontSize: '0.825rem', fontWeight: 600, marginBottom: '0.35rem', color: 'var(--text-primary)' }}>
                  Physical Occupancy:
                </label>
                <select
                  className="select-input"
                  style={{ width: '100%' }}
                  value={editOccupancy}
                  onChange={(e) => setEditOccupancy(e.target.value)}
                >
                  <option value="Unoccupied">Unoccupied (Bed physically empty)</option>
                  <option value="Occupied">Occupied (Patient physically in bed)</option>
                </select>
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.825rem', fontWeight: 600, marginBottom: '0.35rem', color: 'var(--text-primary)' }}>
                  Workflow / Admission Status:
                </label>
                <input
                  type="text"
                  className="search-input"
                  style={{ width: '100%', minWidth: 'unset' }}
                  value={editStatus}
                  onChange={(e) => setEditStatus(e.target.value)}
                  placeholder="e.g. Admitted, Ready for Admission, Discharge pending"
                />
              </div>
            </div>

            {/* Patient Allocation */}
            <div>
              <label style={{ display: 'block', fontSize: '0.825rem', fontWeight: 600, marginBottom: '0.35rem', color: 'var(--text-primary)' }}>
                Allocate Patient ID:
              </label>

              {waitingPatients.length > 0 && (
                <div style={{ marginBottom: '0.5rem' }}>
                  <select
                    className="select-input"
                    style={{ width: '100%', fontSize: '0.8rem' }}
                    onChange={(e) => {
                      if (e.target.value) {
                        setEditPatientId(e.target.value);
                        setEditOccupancy('Occupied');
                        setEditAvailability('Occupied');
                        setEditStatus('Admitted');
                      }
                    }}
                    defaultValue=""
                  >
                    <option value="" disabled>
                      -- Quick Select from Waiting Emergency Patients ({waitingPatients.length}) --
                    </option>
                    {waitingPatients.map((p) => (
                      <option key={p.patient_id} value={p.patient_id}>
                        {p.patient_id} ({p.department} - {p.visit_type} - {p.status})
                      </option>
                    ))}
                  </select>
                </div>
              )}

              <div style={{ display: 'flex', gap: '0.5rem' }}>
                <input
                  type="text"
                  className="search-input"
                  style={{ flex: 1, minWidth: 'unset' }}
                  value={editPatientId}
                  onChange={(e) => setEditPatientId(e.target.value)}
                  placeholder="Enter patient ID e.g. P1078 or leave empty to deallocate"
                />
                {editPatientId && (
                  <button
                    type="button"
                    className="btn btn-outline btn-sm"
                    onClick={() => {
                      setEditPatientId('');
                      if (editAvailability === 'Occupied') setEditAvailability('Available');
                      setEditOccupancy('Unoccupied');
                    }}
                  >
                    Clear Patient
                  </button>
                )}
              </div>
            </div>

            {/* Blocked Reason (Visible if Blocked) */}
            {editAvailability === 'Blocked' && (
              <div>
                <label style={{ display: 'block', fontSize: '0.825rem', fontWeight: 600, marginBottom: '0.35rem', color: 'var(--critical-red)' }}>
                  Blocked Reason / Operational Hold:
                </label>
                <div style={{ display: 'flex', gap: '0.35rem', flexWrap: 'wrap', marginBottom: '0.45rem' }}>
                  <button
                    type="button"
                    className="btn btn-sm btn-outline"
                    style={{ fontSize: '0.72rem' }}
                    onClick={() => setEditBlockedReason('Discharge summary awaiting physician counter-signature')}
                  >
                    Summary not signed
                  </button>
                  <button
                    type="button"
                    className="btn btn-sm btn-outline"
                    style={{ fontSize: '0.72rem' }}
                    onClick={() => setEditBlockedReason('Pending STAT CT Scan report (Central Radiology backlog)')}
                  >
                    CT Scan pending
                  </button>
                  <button
                    type="button"
                    className="btn btn-sm btn-outline"
                    style={{ fontSize: '0.72rem' }}
                    onClick={() => setEditBlockedReason('TPA Insurance cashless approval hold')}
                  >
                    TPA Insurance hold
                  </button>
                </div>
                <textarea
                  className="search-input"
                  style={{ width: '100%', minHeight: 70, resize: 'vertical' }}
                  value={editBlockedReason}
                  onChange={(e) => setEditBlockedReason(e.target.value)}
                  placeholder="Describe reason this bed is blocked from receiving new admissions..."
                />
              </div>
            )}
          </div>
        </Modal>
      )}
    </div>
  );
};
