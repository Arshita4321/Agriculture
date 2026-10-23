import DemoBadge from './DemoBadge.jsx';
export default function PagePlaceholder({ title }) {
  return (
    <div className="card p-8">
      <div className="flex items-center gap-2">
        <h1 className="text-xl font-semibold text-forest-900">{title}</h1>
        <DemoBadge />
      </div>
      <p className="mt-2 max-w-prose text-sm text-slate-600">
        This page is built in a later part. Routing, layout and filters are already wired.
      </p>
    </div>
  );
}
