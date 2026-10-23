// All values in this module are DEMO DATA. Replace via src/services once FastAPI is live.
export const REGION = 'Punjab, India';
export const DATA_DATE = '2026-10-15';

export const DISTRICTS = ['Ludhiana', 'Amritsar', 'Patiala', 'Bathinda', 'Jalandhar'];
export const CROPS = ['Wheat', 'Rice', 'Maize'];
export const SEASONS = ['Kharif', 'Rabi'];
export const RISK_LEVELS = ['Low', 'Moderate', 'High', 'Very high'];

export const NAV_ITEMS = [
  { path: '/', label: 'Overview', icon: 'LayoutDashboard' },
  { path: '/risk-map', label: 'Agricultural Risk Map', icon: 'Map' },
  { path: '/crop-risk', label: 'Crop Risk Analysis', icon: 'Wheat' },
  { path: '/yield-prediction', label: 'Yield Prediction', icon: 'Sprout' },
  { path: '/weather', label: 'Weather Analytics', icon: 'CloudRain' },
  { path: '/trends', label: 'Historical Trends', icon: 'LineChart' },
  { path: '/recommendations', label: 'Recommendations', icon: 'ClipboardList' },
  { path: '/data-sources', label: 'Data Sources', icon: 'Database' },
];

export const MOCK_ALERTS = [
  { id: 1, district: 'Bathinda', text: 'Rainfall deficit indicator elevated (demo)', level: 'High', date: DATA_DATE },
  { id: 2, district: 'Ludhiana', text: 'Heat-stress indicator rising (demo)', level: 'Moderate', date: DATA_DATE },
];
