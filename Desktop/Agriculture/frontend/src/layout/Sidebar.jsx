import { NavLink } from 'react-router-dom';
import * as Icons from 'lucide-react';
import { NAV_ITEMS } from '../data/mockData.js';

export default function Sidebar({ onNavigate }) {
  return (
    <nav aria-label="Main" className="flex h-full flex-col gap-1 p-3">
      {NAV_ITEMS.map(({ path, label, icon }) => {
        const Icon = Icons[icon];
        return (
          <NavLink
            key={path}
            to={path}
            end={path === '/'}
            onClick={onNavigate}
            className={({ isActive }) =>
              `flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
                isActive ? 'bg-forest-100 text-forest-800' : 'text-slate-600 hover:bg-slate-100'
              }`
            }
          >
            <Icon size={18} aria-hidden="true" />
            {label}
          </NavLink>
        );
      })}
    </nav>
  );
}
