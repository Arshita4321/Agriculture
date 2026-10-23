import { createContext, useContext, useState, useCallback } from 'react';
import { DATA_DATE } from '../data/mockData.js';

const defaults = { district: 'All districts', crop: 'Wheat', season: 'Rabi', date: DATA_DATE };
const Ctx = createContext(null);

export function FilterProvider({ children }) {
  const [filters, setFilters] = useState(defaults);
  const setFilter = useCallback((k, v) => setFilters((f) => ({ ...f, [k]: v })), []);
  const resetFilters = useCallback(() => setFilters(defaults), []);
  return <Ctx.Provider value={{ filters, setFilter, resetFilters }}>{children}</Ctx.Provider>;
}
export const useFilters = () => useContext(Ctx);
