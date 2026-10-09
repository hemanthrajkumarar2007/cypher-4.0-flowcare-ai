import React from 'react';

interface BadgeProps {
  label: string;
  variant?: 'critical' | 'high' | 'medium' | 'low' | 'available' | 'occupied' | 'blocked' | 'cleaning' | 'default';
  icon?: React.ReactNode;
}

export const Badge: React.FC<BadgeProps> = ({ label, variant = 'default', icon }) => {
  let badgeClass = 'badge ';
  switch (variant.toLowerCase()) {
    case 'critical':
      badgeClass += 'badge-critical';
      break;
    case 'high':
      badgeClass += 'badge-high';
      break;
    case 'medium':
      badgeClass += 'badge-medium';
      break;
    case 'low':
      badgeClass += 'badge-low';
      break;
    case 'available':
      badgeClass += 'badge-available';
      break;
    case 'occupied':
      badgeClass += 'badge-occupied';
      break;
    case 'blocked':
      badgeClass += 'badge-blocked';
      break;
    case 'cleaning':
      badgeClass += 'badge-cleaning';
      break;
    default:
      badgeClass += 'badge-low';
  }

  return (
    <span className={badgeClass}>
      {icon}
      {label}
    </span>
  );
};
