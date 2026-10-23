export default function DemoBadge({ className = '' }) {
  return (
    <span className={`inline-flex items-center rounded-md bg-amber-50 px-1.5 py-0.5 text-xs font-semibold text-amber-800 ring-1 ring-amber-200 ${className}`}>
      DEMO DATA
    </span>
  );
}
