/**
 * App Shell — routing, sidebar, session management
 */

const App = (() => {
  let currentUser = null;
  let currentPage = 'dashboard';

  const pageMap = {
    dashboard: { label: 'Dashboard',  load: () => DashboardPage.load() },
    guests:    { label: 'Guests',     load: () => GuestsPage.load() },
    rooms:     { label: 'Rooms',      load: () => RoomsPage.load() },
    bookings:  { label: 'Bookings',   load: () => BookingsPage.load() },
    services:  { label: 'Services',   load: () => ServicesPage.load() },
    employees: { label: 'Employees',  load: () => EmployeesPage.load() },
    payments:  { label: 'Payments',   load: () => PaymentsPage.load() },
  };

  function showAuth() {
    document.getElementById('auth-container').style.display = 'block';
    document.getElementById('app-shell').style.display = 'none';
    Auth.renderLogin();
  }

  function init(user) {
    currentUser = user;
    document.getElementById('auth-container').style.display = 'none';
    document.getElementById('app-shell').style.display = 'flex';

    // populate user info
    const initials = fmt.initials(user.full_name || user.username);
    document.getElementById('user-avatar').textContent = initials;
    document.getElementById('user-name').textContent = user.full_name || user.username;
    document.getElementById('user-role').textContent = user.role || 'Staff';

    // wire up nav
    document.querySelectorAll('.nav-item[data-page]').forEach(item => {
      item.addEventListener('click', () => navigate(item.dataset.page));
    });

    // logout
    document.getElementById('btn-logout').addEventListener('click', () => {
      API.clearToken();
      currentUser = null;
      showAuth();
    });

    navigate('dashboard');
  }

  function navigate(page) {
    if (!pageMap[page]) return;
    currentPage = page;

    // update nav active state
    document.querySelectorAll('.nav-item[data-page]').forEach(item => {
      item.classList.toggle('active', item.dataset.page === page);
    });

    // update page title
    document.getElementById('topbar-page-title').textContent = pageMap[page].label;

    // show correct page panel
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    const panel = document.getElementById(`page-${page}`);
    if (panel) panel.classList.add('active');

    // load page content
    pageMap[page].load();
  }

  async function checkSession() {
    const token = API.getToken();
    if (!token) { showAuth(); return; }
    try {
      const me = await API.auth.me();
      init(me);
    } catch {
      showAuth();
    }
  }

  return { init, navigate, showAuth, checkSession };
})();

// ── Bootstrap ──────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  Toast.init();
  App.checkSession();
});
