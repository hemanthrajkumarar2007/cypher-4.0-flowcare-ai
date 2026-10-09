import React from 'react';
import {
  LayoutDashboard,
  AlertTriangle,
  Bed,
  Activity,
  LogOut,
  Users,
  Network,
  ListOrdered,
  ClipboardList,
  ShieldCheck,
  Stethoscope,
} from 'lucide-react';
import { NavigationTab } from '../types';

interface SidebarProps {
  currentTab: NavigationTab;
  onSelectTab: (tab: NavigationTab) => void;
  counts?: {
    bottlenecks?: number;
    blockedBeds?: number;
    actionsPending?: number;
  };
}

export const Sidebar: React.FC<SidebarProps> = ({ currentTab, onSelectTab, counts }) => {
  const navItems: Array<{
    id: NavigationTab;
    label: string;
    icon: React.ReactNode;
    badgeCount?: number;
    badgeVariant?: string;
  }> = [
    {
      id: 'overview',
      label: 'Overview Dashboard',
      icon: <LayoutDashboard size={18} />,
    },
    {
      id: 'bottlenecks',
      label: 'Bottlenecks Intelligence',
      icon: <AlertTriangle size={18} />,
      badgeCount: counts?.bottlenecks,
      badgeVariant: '#ef4444',
    },
    {
      id: 'beds',
      label: 'Bed Management',
      icon: <Bed size={18} />,
      badgeCount: counts?.blockedBeds,
      badgeVariant: '#dc2626',
    },
    {
      id: 'diagnostics',
      label: 'Diagnostics & Labs',
      icon: <Activity size={18} />,
    },
    {
      id: 'discharges',
      label: 'Discharge Clearance',
      icon: <LogOut size={18} />,
    },
    {
      id: 'staff-appointments',
      label: 'Staff & Appointments',
      icon: <Users size={18} />,
    },
    {
      id: 'causal-links',
      label: 'Root-Cause Causal Links',
      icon: <Network size={18} />,
    },
    {
      id: 'priority-queue',
      label: 'Actionable Priority Queue',
      icon: <ListOrdered size={18} />,
    },
    {
      id: 'actions-audit',
      label: 'Simulated Tasks & Audit',
      icon: <ClipboardList size={18} />,
      badgeCount: counts?.actionsPending,
      badgeVariant: '#2563eb',
    },
    {
      id: 'data-quality',
      label: 'Data Quality & Integrity',
      icon: <ShieldCheck size={18} />,
    },
  ];

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <div className="brand-badge">
          <div className="brand-icon">
            <Stethoscope size={20} />
          </div>
          <div>
            <div className="brand-title">FlowCare AI</div>
            <div className="brand-subtitle">Sanjeevani Hospital</div>
          </div>
        </div>
      </div>

      <nav className="sidebar-nav">
        {navItems.map((item) => {
          const isActive = currentTab === item.id;
          return (
            <button
              key={item.id}
              className={`nav-item ${isActive ? 'active' : ''}`}
              onClick={() => onSelectTab(item.id)}
            >
              {item.icon}
              <span style={{ flex: 1, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                {item.label}
              </span>
              {typeof item.badgeCount === 'number' && item.badgeCount > 0 && (
                <span
                  className="nav-badge"
                  style={{
                    backgroundColor: isActive ? '#ffffff' : item.badgeVariant || '#ef4444',
                    color: isActive ? '#0b1329' : '#ffffff',
                  }}
                >
                  {item.badgeCount}
                </span>
              )}
            </button>
          );
        })}
      </nav>

      <div className="sidebar-footer">
        <div style={{ fontWeight: 600, color: '#94a3b8', marginBottom: '0.2rem' }}>Cypher 2026 Hackathon</div>
        <div>Challenge: "The Blocked Bed"</div>
        <div style={{ fontSize: '0.7rem', color: '#64748b', marginTop: '0.25rem' }}>
          Backend: FastAPI (Port 8000)
        </div>
      </div>
    </aside>
  );
};
