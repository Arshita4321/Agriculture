import { useState } from 'react';
import { Outlet } from 'react-router-dom';
import { X } from 'lucide-react';
import Sidebar from './Sidebar.jsx';
import Topbar from './Topbar.jsx';

export default function AppLayout() {
  const [open, setOpen] = useState(false);
  return (
    <div className="min-h-screen">
      <Topbar onMenu={() => setOpen(true)} />
      <div className="flex">
        <aside className="sticky top-[57px] hidden h-[calc(100vh-57px)] w-60 shrink-0 border-r border-slate-200 bg-white lg:block">
          <Sidebar />
        </aside>
        {open && (
          <div className="fixed inset-0 z-40 lg:hidden" role="dialog" aria-modal="true" aria-label="Navigation">
            <button aria-label="Close navigation" className="absolute inset-0 bg-slate-900/40" onClick={() => setOpen(false)} />
            <div className="relative h-full w-64 bg-white shadow-xl">
              <button aria-label="Close" onClick={() => setOpen(false)} className="absolute right-2 top-2 p-2"><X size={18} /></button>
              <div className="pt-10"><Sidebar onNavigate={() => setOpen(false)} /></div>
            </div>
          </div>
        )}
        <main className="min-w-0 flex-1 p-4 md:p-6"><Outlet /></main>
      </div>
    </div>
  );
}
