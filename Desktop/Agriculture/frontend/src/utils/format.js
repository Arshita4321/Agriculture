export const formatDate = (d) =>
  new Date(d).toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' });
export const RISK_COLORS = { Low: '#2f9e6b', Moderate: '#e8a317', High: '#e2661f', 'Very high': '#c62d2d' };
export const riskLevel = (score) => (score < 25 ? 'Low' : score < 50 ? 'Moderate' : score < 75 ? 'High' : 'Very high');
