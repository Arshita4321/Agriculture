import { Routes, Route } from 'react-router-dom';
import AppLayout from './layout/AppLayout.jsx';
import PagePlaceholder from './components/PagePlaceholder.jsx';
import { NAV_ITEMS } from './data/mockData.js';

// Later parts replace each PagePlaceholder with the real page component.
export default function App() {
  return (
    <Routes>
      <Route element={<AppLayout />}>
        {NAV_ITEMS.map((n) => (
          <Route key={n.path} path={n.path} element={<PagePlaceholder title={n.label} />} />
        ))}
        <Route path="*" element={<PagePlaceholder title="Page not found" />} />
      </Route>
    </Routes>
  );
}
