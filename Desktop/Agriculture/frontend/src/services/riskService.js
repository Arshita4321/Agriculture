import { getHealth } from './api.js';

// Demo mode is used whenever the backend health check fails. The UI never claims a live model in demo mode.
export async function detectMode() {
  try {
    const h = await getHealth();
    return { mode: 'live', detail: h };
  } catch {
    return { mode: 'demo', detail: null };
  }
}
