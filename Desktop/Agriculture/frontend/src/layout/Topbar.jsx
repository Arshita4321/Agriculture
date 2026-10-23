import { useState } from 'react';
import { Menu, Bell, User, Sprout, MapPin, RotateCcw } from 'lucide-react';
import { useFilters } from '../hooks/useFilters.jsx';
import { DISTRICTS, REGION, MOCK_ALERTS } from '../data/mockData.js';
import { formatDate } from '../utils/format.js';

function Popover({ label, icon: Icon, children }) {
  const [open, setOpen] = useState(false);
  return (
    <div className="relative" onKeyDown={(e) => e.key === 'Escape' && setOpen(false)}>
      <button
        aria-label={label}
        aria-expanded={open}
        onClick={() => setOpen((o) => !o)}
        className="grid h-9 w-9 place-items-center rounded-lg border border-slate-200 text-slate-600 hover:bg-slate-50"
      >
        <Icon size={18} />
      </button>
      {open && <div className="card absolute right-0 z-30 mt-2 w-72 p-3 text-sm">{children}</div>}
    </div>
  );
}

export default function Topbar({ onMenu }) {
  const { filters, setFilter, resetFilters } = useFilters();
  return (
    <header className="sticky top-0 z-20 flex flex-wrap items-center gap-3 border-b border-slate-200 bg-white px-4 py-2.5">
      <button aria-label="Open navigation" onClick={onMenu} className="grid h-9 w-9 place-items-center rounded-lg border border-slate-200 lg:hidden">
        <Menu size={18} />
      </button>
      <div className="flex items-center gap-2 font-semibold text-forest-800">
        <span className="grid h-8 w-8 place-items-center rounded-lg bg-forest-600 text-white"><Sprout size={18} /></span>
        <span className="hidden sm:inline">AgriRisk Intelligence</span>
      </div>
      <div className="ml-2 hidden items-center gap-1 text-sm text-slate-600 md:flex">
        <MapPin size={14} aria-hidden="true" /> {REGION}
      </div>
      <div className="ml-auto flex flex-wrap items-center gap-2">
        <label className="sr-only" htmlFor="district">District</label>
        <select id="district" className="field" value={filters.district} onChange={(e) => setFilter('district', e.target.value)}>
          <option>All districts</option>
          {DISTRICTS.map((d) => <option key={d}>{d}</option>)}
        </select>
        <label className="sr-only" htmlFor="date">Data date</label>
        <input id="date" type="date" className="field" value={filters.date} onChange={(e) => setFilter('date', e.target.value)} />
        <button onClick={resetFilters} className="field flex items-center gap-1.5 hover:bg-slate-50">
          <RotateCcw size={14} aria-hidden="true" /> Reset filters
        </button>
        <Popover label="Notifications" icon={Bell}>
          <p className="mb-2 font-semibold">Recent alerts <span className="text-xs font-normal text-amber-700">(demo)</span></p>
          {MOCK_ALERTS.map((a) => (
            <p key={a.id} className="border-t border-slate-100 py-1.5">
              <strong>{a.district}</strong>: {a.text}
              <span className="block text-xs text-slate-500">{formatDate(a.date)}</span>
            </p>
          ))}
        </Popover>
        <Popover label="User menu" icon={User}>
          <p className="font-semibold">Demo user</p>
          <p className="text-xs text-slate-500">Authentication is not connected to a backend.</p>
        </Popover>
      </div>
    </header>
  );
}
