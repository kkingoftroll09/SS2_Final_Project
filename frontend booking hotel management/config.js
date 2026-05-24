(() => {
  const localHostnames = new Set(['localhost', '127.0.0.1', '::1']);
  const isLocalDev = localHostnames.has(window.location.hostname);

  const defaultApiBase = isLocalDev
    ? 'http://127.0.0.1:8000'
    : 'https://ss2-backend.onrender.com';

  window.API_BASE_URL = defaultApiBase;

  console.log('[config] API_BASE_URL =', window.API_BASE_URL);
})();

