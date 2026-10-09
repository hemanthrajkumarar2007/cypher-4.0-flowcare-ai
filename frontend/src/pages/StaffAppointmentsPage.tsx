import React, { useState } from 'react';
import { Users, Calendar, Clock, AlertTriangle, CheckCircle2, XCircle } from 'lucide-react';
import { Staff, Appointment } from '../types';
import { Badge } from '../components/Badge';

interface StaffAppointmentsPageProps {
  staff: Staff[];
  appointments: Appointment[];
  loading: boolean;
}

export const StaffAppointmentsPage: React.FC<StaffAppointmentsPageProps> = ({
  staff,
  appointments,
  loading,
}) => {
  const [activeSubtab, setActiveSubtab] = useState<'staff' | 'appointments'>('staff');
  const [staffDeptFilter, setStaffDeptFilter] = useState('ALL');
  const [aptDeptFilter, setAptDeptFilter] = useState('ALL');

  if (loading) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '60vh' }}>
        <div className="spinner" style={{ width: 40, height: 40 }} />
      </div>
    );
  }

  // Filter staff
  const staffDepts = Array.from(new Set(staff.map((s) => s.department)));
  const filteredStaff = staff.filter((s) => staffDeptFilter === 'ALL' || s.department === staffDeptFilter);

  // Filter appointments
  const aptDepts = Array.from(new Set(appointments.map((a) => a.department)));
  const filteredApts = appointments.filter((a) => aptDeptFilter === 'ALL' || a.department === aptDeptFilter);

  return (
    <div>
      {/* Subtab Toggle */}
      <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1.25rem' }}>
        <button
          className={`btn ${activeSubtab === 'staff' ? 'btn-primary' : 'btn-outline'}`}
          onClick={() => setActiveSubtab('staff')}
        >
          <Users size={16} />
          <span>Staff Rostering &amp; Workload ({staff.length})</span>
        </button>
        <button
          className={`btn ${activeSubtab === 'appointments' ? 'btn-primary' : 'btn-outline'}`}
          onClick={() => setActiveSubtab('appointments')}
        >
          <Calendar size={16} />
          <span>Appointments &amp; Waiting Times ({appointments.length})</span>
        </button>
      </div>

      {/* TAB 1: STAFF ROSTERING */}
      {activeSubtab === 'staff' && (
        <div>
          {/* Staff Shortage Notice */}
          <div className="alert-box alert-warning">
            <AlertTriangle size={18} color="#b45309" style={{ flexShrink: 0, marginTop: 2 }} />
            <div>
              <strong>Impending Shift Gap:</strong> Emergency Department Evening shift has only <strong>1 Doctor</strong> (Dr. Ananya Roy)
              and <strong>1 Nurse</strong> (Nurse Preeti Verma) scheduled, with workload already flagged as Critical.
              Meanwhile, Dermatology Outpatient has 2 doctors with Low workload and Available status (spare capacity).
            </div>
          </div>

          {/* Filter Bar */}
          <div className="card filter-bar">
            <div className="filter-group">
              <select className="select-input" value={staffDeptFilter} onChange={(e) => setStaffDeptFilter(e.target.value)}>
                <option value="ALL">All Staff Departments</option>
                {staffDepts.map((d) => (
                  <option key={d} value={d}>
                    {d}
                  </option>
                ))}
              </select>
            </div>
            <div style={{ fontSize: '0.85rem', color: '#64748b' }}>
              Showing {filteredStaff.length} personnel records
            </div>
          </div>

          {/* Staff Table */}
          <div className="card table-responsive">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Staff ID</th>
                  <th>Name</th>
                  <th>Role</th>
                  <th>Department</th>
                  <th>Shift</th>
                  <th>Availability</th>
                  <th>Workload Pressure</th>
                </tr>
              </thead>
              <tbody>
                {filteredStaff.map((s) => {
                  const isCriticalWorkload = s.workload === 'Critical';
                  const isHighWorkload = s.workload === 'High';
                  return (
                    <tr key={s.staff_id} style={{ background: isCriticalWorkload ? '#fff5f5' : undefined }}>
                      <td style={{ fontWeight: 600, fontFamily: 'monospace' }}>{s.staff_id}</td>
                      <td style={{ fontWeight: 600 }}>{s.name}</td>
                      <td>{s.role}</td>
                      <td>{s.department}</td>
                      <td>
                        <span style={{ fontWeight: 500 }}>{s.shift} Shift</span>
                      </td>
                      <td>
                        <Badge
                          label={s.availability}
                          variant={s.availability === 'On Duty' ? 'occupied' : s.availability === 'Available' ? 'available' : 'high'}
                        />
                      </td>
                      <td>
                        <Badge
                          label={s.workload}
                          variant={isCriticalWorkload ? 'critical' : isHighWorkload ? 'high' : 'low'}
                        />
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* TAB 2: APPOINTMENTS & WAITS */}
      {activeSubtab === 'appointments' && (
        <div>
          {/* Scheduling Bottleneck Notice */}
          <div className="alert-box alert-info">
            <Clock size={18} color="#2563eb" style={{ flexShrink: 0, marginTop: 2 }} />
            <div>
              <strong>Outpatient Scheduling Bottlenecks:</strong> Cardiology clinic at 10:00 AM has 5 simultaneous bookings booked against a single doctor (slot capacity: 2).
              In contrast, Orthopedics recorded 100% non-attendance (2 cancellations, 2 no-shows) resulting in idle clinical time.
            </div>
          </div>

          {/* Filter Bar */}
          <div className="card filter-bar">
            <div className="filter-group">
              <select className="select-input" value={aptDeptFilter} onChange={(e) => setAptDeptFilter(e.target.value)}>
                <option value="ALL">All Appointment Departments</option>
                {aptDepts.map((d) => (
                  <option key={d} value={d}>
                    {d}
                  </option>
                ))}
              </select>
            </div>
            <div style={{ fontSize: '0.85rem', color: '#64748b' }}>
              Showing {filteredApts.length} appointment consultations
            </div>
          </div>

          {/* Appointments Table */}
          <div className="card table-responsive">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Appointment ID</th>
                  <th>Attending Physician</th>
                  <th>Department</th>
                  <th>Slot Time</th>
                  <th>Status</th>
                  <th>Measured Wait</th>
                  <th>Observation</th>
                </tr>
              </thead>
              <tbody>
                {filteredApts.map((a) => {
                  const isHighWait = a.waiting_time >= 75;
                  return (
                    <tr key={a.appointment_id} style={{ background: isHighWait ? '#fff8f8' : undefined }}>
                      <td style={{ fontWeight: 600, fontFamily: 'monospace' }}>{a.appointment_id}</td>
                      <td style={{ fontWeight: 600 }}>{a.doctor}</td>
                      <td>{a.department}</td>
                      <td style={{ fontSize: '0.8rem', color: '#64748b' }}>{a.datetime.replace('T', ' ')}</td>
                      <td>
                        <Badge
                          label={a.status.toUpperCase()}
                          variant={
                            a.status === 'completed'
                              ? 'available'
                              : a.status === 'scheduled'
                              ? 'medium'
                              : 'critical'
                          }
                        />
                      </td>
                      <td style={{ fontWeight: 700, color: isHighWait ? '#dc2626' : '#0f172a' }}>
                        {a.waiting_time} mins
                      </td>
                      <td style={{ fontSize: '0.8rem', color: '#64748b' }}>
                        {a.waiting_time > 80 ? (
                          <span style={{ color: '#dc2626', fontWeight: 600 }}>Severe delay (Exceeds triage threshold)</span>
                        ) : a.status === 'cancelled' || a.status === 'no-show' ? (
                          <span style={{ color: '#b45309' }}>Non-attendance slot gap</span>
                        ) : (
                          'Within standard tolerance'
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};
