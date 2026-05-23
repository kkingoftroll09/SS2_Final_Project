(() => {
  const localHostnames = new Set(['localhost', '127.0.0.1', '::1']);
  const isLocalDev = localHostnames.has(window.location.hostname);
  const defaultApiBase = isLocalDev
    ? 'http://127.0.0.1:8000'
    : 'https://ss2-final-project-frontend.onrender.com';

  // Allow overriding from index.html (or if Render injects env vars into the static HTML).
  // Set window.API_BASE_URL *before* config.js loads.
  window.API_BASE_URL = window.API_BASE_URL || defaultApiBase;

  console.log('[config] API_BASE_URL =', window.API_BASE_URL);
})();

