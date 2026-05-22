const API = (() => {
  const BASE = window.API_BASE_URL || 'http://127.0.0.1:8000';

  const getToken = () => localStorage.getItem('token');
  const setToken = (t) => localStorage.setItem('token', t);
  const clearToken = () => localStorage.removeItem('token');

  async function request(method, path, body = null) {
    const headers = { 'Content-Type': 'application/json' };
    const token = getToken();
    if (token) headers['Authorization'] = `Bearer ${token}`;

    const opts = { method, headers };
    if (body) opts.body = JSON.stringify(body);

    let res;
    try {
      res = await fetch(`${BASE}${path}`, opts);
    } catch (err) {
      console.error('Network request failed', { method, url: `${BASE}${path}`, opts, err });
      throw new Error(`Network request failed: ${err && err.message ? err.message : err}`);
    }

    if (res.status === 401) {
      clearToken();
      window.App && App.showAuth();
      throw { message: 'Phiên làm việc hết hạn' };
    }

    let data;
    try { data = await res.json(); } catch { data = await res.text(); }

    if (!res.ok) throw data?.detail || data || `Lỗi ${res.status}`;
    return data;
  }

  async function requestForm(method, path, fields) {
    const headers = { 'Content-Type': 'application/x-www-form-urlencoded' };
    const token = getToken();
    if (token) headers['Authorization'] = `Bearer ${token}`;

    const body = new URLSearchParams(fields);
    let res;
    try {
      res = await fetch(`${BASE}${path}`, { method, headers, body });
    } catch (err) {
      console.error('Network request (form) failed', { method, url: `${BASE}${path}`, headers, body, err });
      throw new Error(`Network request failed: ${err && err.message ? err.message : err}`);
    }

    if (res.status === 401) {
      clearToken();
      window.App && App.showAuth();
      throw { message: 'Phiên làm việc hết hạn' };
    }

    let data;
    try { data = await res.json(); } catch { data = await res.text(); }

    if (!res.ok) throw data?.detail || data || `Lỗi ${res.status}`;
    return data;
  }

  return {
    getToken, setToken, clearToken,

    dashboard: {
      stats: async () => {
        const [bookings, rooms] = await Promise.all([
          request('GET', '/api/bookings'),
          request('GET', '/rooms'),
        ]);

        const bookingList = Array.isArray(bookings) ? bookings : (bookings?.items || bookings?.data || []);
        const roomList = Array.isArray(rooms) ? rooms : (rooms?.items || rooms?.data || []);
        const now = new Date();
        const thisYear = now.getFullYear();
        const thisMonth = now.getMonth();

        const monthlyRevenue = bookingList.reduce((sum, b) => {
          const d = b?.check_in_date ? new Date(b.check_in_date) : null;
          if (!d || Number.isNaN(d.getTime())) return sum;
          if (d.getFullYear() !== thisYear || d.getMonth() !== thisMonth) return sum;
          return sum + Number(b?.total_price || 0);
        }, 0);

        const availableRooms = roomList.filter(r => r?.status === 'available').length;
        const totalGuests = new Set(bookingList.map(b => b?.guest_id).filter(Boolean)).size;

        const recentBookings = bookingList
          .slice()
          .sort((a, b) => Number(b?.id || b?.booking_id || 0) - Number(a?.id || a?.booking_id || 0))
          .slice(0, 5)
          .map(b => ({
            booking_id: b?.booking_id ?? b?.id,
            guest_name: b?.guest_name || (b?.guest_id ? `Guest #${b.guest_id}` : '—'),
            check_in_date: b?.check_in_date,
            check_out_date: b?.check_out_date,
            number_of_guests: b?.number_of_guests ?? '—',
            total_amount: b?.total_amount ?? b?.total_price ?? 0,
            status: b?.status || 'pending',
          }));

        const roomStatus = roomList
          .slice()
          .sort((a, b) => String(a?.room_number || '').localeCompare(String(b?.room_number || ''), undefined, { numeric: true }))
          .map(r => ({
            room_id: r?.room_id ?? r?.id,
            room_number: r?.room_number,
            floor: r?.floor ?? '—',
            type_name: r?.type_name || r?.room_type || '—',
            status: r?.status || 'available',
          }));

        return {
          total_bookings: bookingList.length,
          available_rooms: availableRooms,
          total_guests: totalGuests,
          monthly_revenue: monthlyRevenue,
          recent_bookings: recentBookings,
          room_status: roomStatus,
        };
      },
    },

    auth: {
      login: (username, password) => requestForm('POST', '/auth/login', { username, password }),
      register: (data) => request('POST', '/auth/register', data),
      me: () => request('GET', '/auth/me'),
    },

    guests: {
      list: (params = {}) => {
        const q = new URLSearchParams();
        if (params.skip) q.append('skip', params.skip);
        if (params.limit) q.append('limit', params.limit);
        if (params.search) q.append('search', params.search);
        return request('GET', `/api/guests?${q}`).then(res => ({
          ...res,
          items: (res.items || []).map(item => ({ ...item, name: item.full_name, guest_id: item.guest_id || item.id }))
        }));
      },
      get: (id) => request('GET', `/api/guests/${id}`).then(g => ({ ...g, name: g.full_name, guest_id: g.id })),
      create: (d) => request('POST', '/api/guests', { full_name: d.name, email: d.email, phone: d.phone, address: d.address }),
      update: (id, d) => request('PUT', `/api/guests/${id}`, { full_name: d.name, email: d.email, phone: d.phone, address: d.address }),
      delete: (id) => request('DELETE', `/api/guests/${id}`),
    },

    rooms: {
      list: (params = {}) => {
        const q = new URLSearchParams();
        if (params.skip) q.append('skip', params.skip);
        if (params.limit) q.append('limit', params.limit);
        if (params.search) q.append('search', params.search);
        return request('GET', `/rooms?${q}`);
      },
      get: (id) => request('GET', `/rooms/${id}`),
      create: (d) => request('POST', '/rooms', d),
      update: (id, d) => request('PUT', `/rooms/${id}`, d),
      delete: (id) => request('DELETE', `/rooms/${id}`),
    },

    roomTypes: {
      list: () => request('GET', '/room-types'),
    },

    bookings: {
      list: (params = {}) => {
        const q = new URLSearchParams();
        if (params.skip) q.append('skip', params.skip);
        if (params.limit) q.append('limit', params.limit);
        if (params.search) q.append('search', params.search);
        return request('GET', `/api/bookings?${q}`);
      },
      create: (d) => request('POST', '/api/bookings', d),
      get: (id) => request('GET', `/api/bookings/${id}`),
      update: (id, d) => request('PUT', `/api/bookings/${id}`, d),
      delete: (id) => request('DELETE', `/api/bookings/${id}`),
    },

    services: {
      list: (params = {}) => {
        const q = new URLSearchParams();
        if (params.skip) q.append('skip', params.skip);
        if (params.limit) q.append('limit', params.limit);
        if (params.search) q.append('search', params.search);
        return request('GET', `/services?${q}`);
      },
      get: (id) => request('GET', `/services/${id}`),
      create: (d) => request('POST', '/services', d),
      update: (id, d) => request('PUT', `/services/${id}`, d),
      delete: (id) => request('DELETE', `/services/${id}`),
    },

    employees: {
      normalize: (e = {}) => ({
        employee_id: e.employee_id ?? e.id,
        id: e.id ?? e.employee_id,
        name: e.name ?? e.full_name ?? '',
        full_name: e.full_name ?? e.name ?? '',
        phone: e.phone ?? '',
        email: e.email ?? '',
        role: e.role ?? '',
        position: e.position ?? '',
        username: e.username ?? '',
      }),
      list: (params = {}) => {
        const q = new URLSearchParams();
        if (params.skip) q.append('skip', params.skip);
        if (params.limit) q.append('limit', params.limit);
        if (params.search) q.append('search', params.search);
        return request('GET', `/employees?${q}`).then((res) => ({
          ...res,
          items: (res.items || []).map((e) => API.employees.normalize(e)),
        }));
      },
      create: (d) => {
        const safeName = String(d.name || d.full_name || 'employee').trim();
        const usernameBase = safeName.toLowerCase().replace(/[^a-z0-9]+/g, '.').replace(/^\.+|\.+$/g, '') || 'employee';
        return request('POST', '/employees', {
          full_name: safeName,
          position: d.position || d.role || 'staff',
          role: String(d.role || 'receptionist').toLowerCase(),
          username: d.username || `${usernameBase}.${Date.now().toString().slice(-4)}`,
          password: d.password || 'password123',
        });
      },
      get: (id) => request('GET', `/employees/${id}`).then((e) => API.employees.normalize(e)),
      update: (id, d) => request('PUT', `/employees/${id}`, {
        full_name: d.name ?? d.full_name,
        position: d.position ?? d.role,
        role: d.role ? String(d.role).toLowerCase() : undefined,
        username: d.username,
      }),
      delete: (id) => request('DELETE', `/employees/${id}`),
    },

    payments: {
      list: () => request('GET', '/payments'),
      get: (id) => request('GET', `/payments/${id}`),
      create: (d) => request('POST', `/bookings/${d.booking_id}/payments`, d),
      update: (id, d) => request('PUT', `/payments/${id}`, d),
      listForBooking: (id) => request('GET', `/bookings/${id}/payments`),
      add: (booking_id, d) => request('POST', `/bookings/${booking_id}/payments`, d),
    },

    housekeeping: {
      createTask: (d) => request('POST', '/housekeeping/tasks', d),
      listTasks: () => request('GET', '/housekeeping/tasks'),
    }
  };
})();