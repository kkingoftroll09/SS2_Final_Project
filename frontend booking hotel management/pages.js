/**
 * Pages — all main modules
 * Each module: list with search/pagination, create modal, edit modal, delete confirm
 */

// ── Shared table builder ───────────────────────────────────────────────────
function buildTableCard({ id, title, btnLabel, btnId, searchId, cols, renderRow, emptyMsg = 'No records found.' }) {
  return `
    <div class="table-card" id="${id}-card">
      <div class="table-header">
        <span class="table-title">${title}</span>
        <div class="table-actions">
          <input class="search-input" id="${searchId}" placeholder="Search…" type="search">
          <button class="btn btn-primary btn-sm" id="${btnId}">+ ${btnLabel}</button>
        </div>
      </div>
      <div style="overflow-x:auto">
        <table>
          <thead><tr>${cols.map(c => `<th>${c}</th>`).join('')}</tr></thead>
          <tbody id="${id}-tbody"><tr><td colspan="${cols.length}" class="table-empty"><span class="spinner"></span> Loading…</td></tr></tbody>
        </table>
      </div>
      <div class="pagination" id="${id}-pagination" style="display:none">
        <span id="${id}-info"></span>
        <div class="pagination-pages" id="${id}-pages"></div>
      </div>
    </div>`;
}

function renderPagination(prefix, { page, total, limit, onPage }) {
  const pages = Math.ceil(total / limit);
  const info  = document.getElementById(`${prefix}-info`);
  const pgs   = document.getElementById(`${prefix}-pages`);
  const wrap  = document.getElementById(`${prefix}-pagination`);
  if (!info || !pgs) return;

  wrap.style.display = total > 0 ? 'flex' : 'none';
  info.textContent = `${Math.min((page - 1) * limit + 1, total)}–${Math.min(page * limit, total)} of ${total}`;

  pgs.innerHTML = '';
  const addBtn = (label, p, disabled = false, active = false) => {
    const b = document.createElement('button');
    b.className = 'page-btn' + (active ? ' active' : '');
    b.textContent = label;
    b.disabled = disabled;
    b.addEventListener('click', () => onPage(p));
    pgs.appendChild(b);
  };
  addBtn('‹', page - 1, page === 1);
  for (let i = 1; i <= pages; i++) {
    if (pages > 7 && Math.abs(i - page) > 2 && i !== 1 && i !== pages) {
      if (i === 2 || i === pages - 1) { addBtn('…', i, true); }
      continue;
    }
    addBtn(i, i, false, i === page);
  }
  addBtn('›', page + 1, page === pages);
}

// ═══════════════════════════════════════════════════════════════════════════
// DASHBOARD
// ═══════════════════════════════════════════════════════════════════════════
const DashboardPage = (() => {
  async function load() {
    const el = document.getElementById('page-dashboard');
    el.innerHTML = `<div class="loading-overlay"><span class="spinner"></span> Loading dashboard…</div>`;
    try {
      const stats = await API.dashboard.stats();
      render(stats);
    } catch {
      el.innerHTML = `<p style="color:var(--text-muted);padding:2rem">Could not load dashboard data.</p>`;
    }
  }

  function render(s) {
    document.getElementById('page-dashboard').innerHTML = `
      <div class="stats-grid">
        <div class="stat-card"><div class="stat-label">Total Bookings</div><div class="stat-value">${s.total_bookings ?? 0}</div><div class="stat-sub">All time</div></div>
        <div class="stat-card"><div class="stat-label">Rooms Available</div><div class="stat-value">${s.available_rooms ?? 0}</div><div class="stat-sub">Right now</div></div>
        <div class="stat-card"><div class="stat-label">Total Guests</div><div class="stat-value">${s.total_guests ?? 0}</div><div class="stat-sub">Registered</div></div>
        <div class="stat-card"><div class="stat-label">Revenue (month)</div><div class="stat-value">${fmt.currency(s.monthly_revenue ?? 0)}</div><div class="stat-sub">Current month</div></div>
      </div>
      <div class="quick-actions">
        <button class="quick-action-btn" onclick="BookingsPage.create()"><span class="quick-action-icon"><svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="1" y="2" width="14" height="13" rx="1.5"/><path d="M5 1v2M11 1v2M1 6h14"/></svg></span>New Booking</button>
        <button class="quick-action-btn" onclick="GuestsPage.create()"><span class="quick-action-icon"><svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="8" cy="5" r="3"/><path d="M2 14c0-3.314 2.686-6 6-6s6 2.686 6 6"/></svg></span>Add Guest</button>
        <button class="quick-action-btn" onclick="RoomsPage.create()"><span class="quick-action-icon"><svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="1" y="4" width="14" height="10" rx="1.5"/><path d="M4 4V2.5a1 1 0 011-1h6a1 1 0 011 1V4"/><path d="M1 10h14"/></svg></span>Manage Rooms</button>
        <button class="quick-action-btn" onclick="PaymentsPage.create()"><span class="quick-action-icon"><svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="1" y="4" width="14" height="9" rx="1.5"/><path d="M1 7h14M5 11h2"/></svg></span>Payments</button>
      </div>
      <div class="recent-grid">
        <div class="table-card">
          <div class="table-header"><span class="table-title">Recent Bookings</span></div>
          <table>
            <thead><tr><th>Booking ID</th><th>Guest</th><th>Check-in</th><th>Check-out</th><th>Party Size</th><th>Total</th><th>Status</th></tr></thead>
            <tbody>
              ${(s.recent_bookings || []).map(b => `
                <tr class="clickable-row" style="cursor:pointer" onclick="BookingsPage.view(${b.booking_id ?? 'null'})">
                  <td><span style="font-family:monospace;font-size:0.8rem;color:var(--accent)">#${b.booking_id ?? '—'}</span></td>
                  <td>${b.guest_name || '—'}</td>
                  <td>${fmt.date(b.check_in_date)}</td>
                  <td>${fmt.date(b.check_out_date)}</td>
                  <td>${b.number_of_guests || '—'}</td>
                  <td>${fmt.currency(b.total_amount || 0)}</td>
                  <td>${fmt.badge(b.status, statusMap.booking)}</td>
                </tr>`).join('') || '<tr><td colspan="7" class="table-empty">No recent bookings</td></tr>'}
            </tbody>
          </table>
        </div>
        <div class="table-card">
          <div class="table-header"><span class="table-title">Room Status</span></div>
          <div class="room-status-summary">
            <span class="badge badge-success">Available: ${(s.room_status || []).filter(r => (r.status || '').toLowerCase() === 'available').length}</span>
            <span class="badge badge-danger">Occupied: ${(s.room_status || []).filter(r => (r.status || '').toLowerCase() === 'occupied').length}</span>
            <span class="badge badge-warning">Cleaning: ${(s.room_status || []).filter(r => (r.status || '').toLowerCase() === 'cleaning' || (r.status || '').toLowerCase() === 'needs_cleaning').length}</span>
            <span class="badge badge-info">Maintenance: ${(s.room_status || []).filter(r => (r.status || '').toLowerCase() === 'maintenance').length}</span>
          </div>
          <table>
            <thead><tr><th>Room</th><th>Floor</th><th>Type</th><th>Status</th></tr></thead>
            <tbody>
              ${(s.room_status || []).map(r => `
                <tr class="clickable-row" style="cursor:pointer" onclick="RoomsPage.view(${r.room_id ?? 'null'})">
                  <td>${r.room_number}</td>
                  <td>${r.floor ?? '—'}</td>
                  <td>${r.type_name || '—'}</td>
                  <td>${fmt.badge(r.status, statusMap.room)}</td>
                </tr>`).join('') || '<tr><td colspan="3" class="table-empty">No rooms</td></tr>'}
            </tbody>
          </table>
        </div>
      </div>`;
  }

  return { load };
})();

// ═══════════════════════════════════════════════════════════════════════════
// GUESTS
// ═══════════════════════════════════════════════════════════════════════════
const GuestsPage = (() => {
  let state = { page: 1, limit: 10, search: '', total: 0 };

  async function load() {
    document.getElementById('page-guests').innerHTML = buildTableCard({
      id: 'guests', title: 'Guests', btnLabel: 'Add Guest', btnId: 'btn-add-guest',
      searchId: 'guests-search',
      cols: ['Name', 'Phone', 'Email', 'Address', 'Nationality', 'Actions'],
    });
    document.getElementById('btn-add-guest').addEventListener('click', () => openForm());
    let timer;
    document.getElementById('guests-search').addEventListener('input', (e) => {
      clearTimeout(timer);
      timer = setTimeout(() => { state.search = e.target.value; state.page = 1; fetchList(); }, 350);
    });
    fetchList();
  }

  async function fetchList() {
    const tbody = document.getElementById('guests-tbody');
    tbody.innerHTML = `<tr><td colspan="6" class="table-empty"><span class="spinner"></span></td></tr>`;
    try {
      const res = await API.guests.list({ skip: (state.page - 1) * state.limit, limit: state.limit, search: state.search });
      const items = Array.isArray(res) ? res : (res.items || res.data || []);
      state.total = res.total ?? items.length;
      tbody.innerHTML = items.length === 0
        ? `<tr><td colspan="6" class="table-empty">No guests found.</td></tr>`
        : items.map(g => `
          <tr>
            <td><div style="font-weight:500">${g.name}</div></td>
            <td>${g.phone || '—'}</td>
            <td>${g.email || '—'}</td>
            <td style="max-width:180px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">${g.address || '—'}</td>
            <td>${g.nationality || '—'}</td>
            <td>
              <div style="display:flex;gap:6px">
                <button class="btn btn-icon" onclick="GuestsPage.edit(${g.guest_id})" title="Edit"><svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M2 14l9.5-9.5M11 4.5l2.5-2.5a1.41 1.41 0 0 0 0-2 1.41 1.41 0 0 0-2 0l-2.5 2.5"/></svg></button>
                <button class="btn btn-icon danger" onclick="GuestsPage.del(${g.guest_id},'${g.name}')" title="Delete"><svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M2 4h12M6 7v5M10 7v5M3 4l1 10c0 .6.4 1 1 1h6c.6 0 1-.4 1-1l1-10M6 2h4"/></svg></button>
              </div>
            </td>
          </tr>`).join('');
      renderPagination('guests', { page: state.page, total: state.total, limit: state.limit, onPage: (p) => { state.page = p; fetchList(); } });
    } catch (err) {
      tbody.innerHTML = `<tr><td colspan="6" class="table-empty" style="color:var(--danger)">${err.message}</td></tr>`;
    }
  }

  function formHTML(g = {}) {
    return `
      <div class="form-group">
        <label class="form-label" for="g-name">Full Name <span class="required">*</span></label>
        <input class="form-control" id="g-name" name="name" value="${g.name || ''}" placeholder="John Doe">
        <div class="form-error" id="g-name-err"></div>
      </div>
      <div class="form-row">
        <div class="form-group">
          <label class="form-label" for="g-phone">Phone <span class="required">*</span></label>
          <input class="form-control" id="g-phone" name="phone" value="${g.phone || ''}" placeholder="+1 555 0000">
          <div class="form-error" id="g-phone-err"></div>
        </div>
        <div class="form-group">
          <label class="form-label" for="g-email">Email</label>
          <input class="form-control" id="g-email" name="email" type="email" value="${g.email || ''}" placeholder="guest@email.com">
          <div class="form-error" id="g-email-err"></div>
        </div>
      </div>
      <div class="form-group">
        <label class="form-label" for="g-address">Address</label>
        <input class="form-control" id="g-address" name="address" value="${g.address || ''}" placeholder="123 Main St, City">
      </div>
      <div class="form-group">
        <label class="form-label" for="g-nationality">Nationality</label>
        <input class="form-control" id="g-nationality" name="nationality" value="${g.nationality || ''}" placeholder="e.g. American">
      </div>`;
  }

  const schema = {
    'g-name':  [Validate.rules.required],
    'g-phone': [Validate.rules.required, Validate.rules.phone],
    'g-email': [(v) => v ? Validate.rules.email(v) : null],
  };

  function openForm(g = null) {
    const isEdit = !!g;
    const { el, close } = Modal.create(
      isEdit ? 'Edit Guest' : 'Add New Guest',
      formHTML(g || {}),
      `<button class="btn btn-outline" id="modal-cancel">Cancel</button>
       <button class="btn btn-primary" id="modal-save">${isEdit ? 'Save Changes' : 'Create Guest'}</button>`
    );
    Validate.attachLiveValidation(schema);
    el.querySelector('#modal-cancel').addEventListener('click', close);
    el.querySelector('#modal-save').addEventListener('click', async () => {
      if (!Validate.validateForm(schema)) return;
      const btn = el.querySelector('#modal-save');
      setLoading(btn, true);
      const data = Validate.getFormData(el.querySelector('.modal-body'));
      try {
        if (isEdit) await API.guests.update(g.guest_id, data);
        else        await API.guests.create(data);
        Toast.success(isEdit ? 'Guest updated.' : 'Guest created.');
        close(); fetchList();
      } catch (err) { Toast.error(err.message); }
      finally { setLoading(btn, false); }
    });
  }

  async function edit(id) {
    try {
      const g = await API.guests.get(id);
      openForm(g);
    } catch (err) { Toast.error(err.message); }
  }

  function del(id, name) {
    confirmDialog(`This will permanently delete <strong>${name}</strong>.`, async () => {
      try {
        await API.guests.delete(id);
        Toast.success('Guest deleted.');
        fetchList();
      } catch (err) { Toast.error(err.message); }
    });
  }

  return { load, edit, del, create: () => openForm() };
})();

// ═══════════════════════════════════════════════════════════════════════════
// ROOMS
// ═══════════════════════════════════════════════════════════════════════════
const RoomsPage = (() => {
  let state = { page: 1, limit: 10, search: '', total: 0 };
  let roomTypes = [];

  const normalizeRoomType = (t = {}) => ({
    room_type_id: t.room_type_id ?? t.id,
    type_name: t.type_name ?? t.name ?? '—',
    base_price: t.base_price ?? null,
    max_occupancy: t.max_occupancy ?? null,
  });

  const toTypeKey = (v) => String(v || '').trim().toLowerCase();

  const deriveFloor = (room = {}) => {
    if (room.floor !== null && room.floor !== undefined && room.floor !== '') return room.floor;
    const roomNumber = String(room.room_number || '').trim();
    if (!/^\d{3,}$/.test(roomNumber)) return '—';
    const derived = Number(roomNumber.slice(0, -2));
    return Number.isFinite(derived) && derived > 0 ? derived : '—';
  };

  const getTypeMeta = (room = {}) => {
    const typeId = room.room_type_id ?? room.type_id;
    const roomTypeNameKey = toTypeKey(room.type_name ?? room.room_type);
    const matched = roomTypes.find((t) => {
      if (typeId !== null && typeId !== undefined && Number(t.room_type_id) === Number(typeId)) return true;
      if (!roomTypeNameKey) return false;
      return toTypeKey(t.type_name) === roomTypeNameKey;
    });
    return {
      typeName: room.type_name ?? room.room_type ?? matched?.type_name ?? '—',
      basePrice: room.base_price ?? matched?.base_price ?? null,
      occupancy: room.max_occupancy ?? matched?.max_occupancy ?? null,
    };
  };

  async function load() {
    document.getElementById('page-rooms').innerHTML = buildTableCard({
      id: 'rooms', title: 'Rooms', btnLabel: 'Add Room', btnId: 'btn-add-room',
      searchId: 'rooms-search',
      cols: ['Room #', 'Floor', 'Type', 'Status', 'Base Price', 'Occupancy', 'Actions'],
    });
    try {
      const types = await API.roomTypes.list();
      roomTypes = (Array.isArray(types) ? types : []).map(normalizeRoomType);
    } catch {
      roomTypes = [];
    }
    document.getElementById('btn-add-room').addEventListener('click', () => openForm());
    let timer;
    document.getElementById('rooms-search').addEventListener('input', (e) => {
      clearTimeout(timer);
      timer = setTimeout(() => { state.search = e.target.value; state.page = 1; fetchList(); }, 350);
    });
    fetchList();
  }

  async function fetchList() {
    const tbody = document.getElementById('rooms-tbody');
    tbody.innerHTML = `<tr><td colspan="7" class="table-empty"><span class="spinner"></span></td></tr>`;
    try {
      const res = await API.rooms.list({ skip: (state.page - 1) * state.limit, limit: state.limit, search: state.search });
      const items = Array.isArray(res) ? res : (res.items || []);
      state.total = res.total ?? items.length;
      tbody.innerHTML = items.length === 0
        ? `<tr><td colspan="7" class="table-empty">No rooms found.</td></tr>`
        : items.map(r => {
          const meta = getTypeMeta(r);
          const roomId = r.room_id ?? r.id;
          return `
          <tr>
            <td><strong>${r.room_number}</strong></td>
            <td>${deriveFloor(r)}</td>
            <td>${meta.typeName}</td>
            <td>${fmt.badge(r.status, statusMap.room)}</td>
            <td>${meta.basePrice !== null && meta.basePrice !== undefined ? fmt.currency(meta.basePrice) : '—'}</td>
            <td>${meta.occupancy ?? '—'}</td>
            <td>
              <div style="display:flex;gap:6px">
                <button class="btn btn-icon" onclick="RoomsPage.edit(${roomId})" title="Edit"><svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M2 14l9.5-9.5M11 4.5l2.5-2.5a1.41 1.41 0 0 0 0-2 1.41 1.41 0 0 0-2 0l-2.5 2.5"/></svg></button>
                <button class="btn btn-icon danger" onclick="RoomsPage.del(${roomId},'${r.room_number}')" title="Delete"><svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M2 4h12M6 7v5M10 7v5M3 4l1 10c0 .6.4 1 1 1h6c.6 0 1-.4 1-1l1-10M6 2h4"/></svg></button>
              </div>
            </td>
          </tr>`;
        }).join('');
      renderPagination('rooms', { page: state.page, total: state.total, limit: state.limit, onPage: (p) => { state.page = p; fetchList(); } });
    } catch (err) {
      tbody.innerHTML = `<tr><td colspan="7" class="table-empty" style="color:var(--danger)">${err.message}</td></tr>`;
    }
  }

  function formHTML(r = {}) {
    const typeOpts = roomTypes
      .map(t => `<option value="${t.room_type_id}" ${r.room_type_id == t.room_type_id ? 'selected' : ''}>${t.type_name}</option>`)
      .join('');
    return `
      <div class="form-row">
        <div class="form-group">
          <label class="form-label" for="r-number">Room Number <span class="required">*</span></label>
          <input class="form-control" id="r-number" name="room_number" value="${r.room_number || ''}" placeholder="101">
          <div class="form-error" id="r-number-err"></div>
        </div>
        <div class="form-group">
          <label class="form-label" for="r-floor">Floor <span class="required">*</span></label>
          <input class="form-control" id="r-floor" name="floor" type="number" value="${r.floor || ''}" placeholder="1">
          <div class="form-error" id="r-floor-err"></div>
        </div>
      </div>
      <div class="form-row">
        <div class="form-group">
          <label class="form-label" for="r-type">Room Type</label>
          <select class="form-control" id="r-type" name="room_type_id">
            <option value="">— Select type —</option>${typeOpts}
          </select>
        </div>
        <div class="form-group">
          <label class="form-label" for="r-status">Status <span class="required">*</span></label>
          <select class="form-control" id="r-status" name="status">
            <option value="available" ${r.status === 'available' ? 'selected' : ''}>Available</option>
            <option value="occupied"  ${r.status === 'occupied'  ? 'selected' : ''}>Occupied</option>
            <option value="cleaning"  ${r.status === 'cleaning'  ? 'selected' : ''}>Cleaning</option>
            <option value="maintenance" ${r.status === 'maintenance' ? 'selected' : ''}>Maintenance</option>
          </select>
        </div>
      </div>`;
  }

  const schema = {
    'r-number': [Validate.rules.required],
    'r-floor':  [Validate.rules.required, Validate.rules.positiveNum],
  };

  function openForm(r = null) {
    const isEdit = !!r;
    const { el, close } = Modal.create(
      isEdit ? 'Edit Room' : 'Add New Room',
      formHTML(r || {}),
      `<button class="btn btn-outline" id="modal-cancel">Cancel</button>
       <button class="btn btn-primary" id="modal-save">${isEdit ? 'Save Changes' : 'Create Room'}</button>`
    );
    Validate.attachLiveValidation(schema);
    el.querySelector('#modal-cancel').addEventListener('click', close);
    el.querySelector('#modal-save').addEventListener('click', async () => {
      if (!Validate.validateForm(schema)) return;
      const btn = el.querySelector('#modal-save');
      setLoading(btn, true);
      const data = Validate.getFormData(el.querySelector('.modal-body'));
      try {
        if (isEdit) await API.rooms.update(r.room_id, data);
        else        await API.rooms.create(data);
        Toast.success(isEdit ? 'Room updated.' : 'Room created.');
        close(); fetchList();
      } catch (err) { Toast.error(err.message); }
      finally { setLoading(btn, false); }
    });
  }

  function detailHTML(r) {
    const meta = getTypeMeta(r);
    return `
      <div class="detail-grid" style="display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px">
        <div class="detail-card"><div class="stat-label">Room</div><div class="stat-value" style="font-size:1.2rem">${r.room_number || '—'}</div></div>
        <div class="detail-card"><div class="stat-label">Status</div><div class="stat-value" style="font-size:1.2rem">${fmt.badge(r.status, statusMap.room)}</div></div>
        <div class="detail-card"><div class="stat-label">Floor</div><div class="stat-value" style="font-size:1.2rem">${deriveFloor(r)}</div></div>
        <div class="detail-card"><div class="stat-label">Type</div><div class="stat-value" style="font-size:1.2rem">${meta.typeName}</div></div>
        <div class="detail-card"><div class="stat-label">Base Price</div><div class="stat-value" style="font-size:1.2rem">${meta.basePrice !== null && meta.basePrice !== undefined ? fmt.currency(meta.basePrice) : '—'}</div></div>
        <div class="detail-card"><div class="stat-label">Occupancy</div><div class="stat-value" style="font-size:1.2rem">${meta.occupancy ?? '—'}</div></div>
      </div>
    `;
  }

  async function view(id) {
    if (!id) return;
    try {
      const room = await API.rooms.get(id);
      const { el, close } = Modal.create(
        `Room #${room.room_number || id} Details`,
        detailHTML(room),
        `<button class="btn btn-outline" id="room-detail-close">Close</button>
         <button class="btn btn-primary" id="room-detail-edit">Edit Room</button>`
      );
      el.querySelector('#room-detail-close').addEventListener('click', close);
      el.querySelector('#room-detail-edit').addEventListener('click', () => { close(); openForm(room); });
    } catch (err) {
      Toast.error(err.message);
    }
  }

  async function edit(id) {
    try { openForm(await API.rooms.get(id)); } catch (err) { Toast.error(err.message); }
  }

  function del(id, num) {
    confirmDialog(`Delete room <strong>#${num}</strong>? This cannot be undone.`, async () => {
      try { await API.rooms.delete(id); Toast.success('Room deleted.'); fetchList(); }
      catch (err) { Toast.error(err.message); }
    });
  }

  return { load, view, edit, del, create: () => openForm() };
})();

// ═══════════════════════════════════════════════════════════════════════════
// BOOKINGS
// ═══════════════════════════════════════════════════════════════════════════
const BookingsPage = (() => {
  let state = { page: 1, limit: 10, search: '', total: 0 };

  async function load() {
    document.getElementById('page-bookings').innerHTML = buildTableCard({
      id: 'bookings', title: 'Bookings', btnLabel: 'New Booking', btnId: 'btn-add-booking',
      searchId: 'bookings-search',
      cols: ['Booking ID', 'Guest', 'Check-in', 'Check-out', 'Party Size', 'Total', 'Status', 'Actions'],
    });
    document.getElementById('btn-add-booking').addEventListener('click', () => openForm());
    let timer;
    document.getElementById('bookings-search').addEventListener('input', (e) => {
      clearTimeout(timer);
      timer = setTimeout(() => { state.search = e.target.value; state.page = 1; fetchList(); }, 350);
    });
    fetchList();
  }

  async function fetchList() {
    const tbody = document.getElementById('bookings-tbody');
    tbody.innerHTML = `<tr><td colspan="8" class="table-empty"><span class="spinner"></span></td></tr>`;
    try {
      const res = await API.bookings.list({ skip: (state.page - 1) * state.limit, limit: state.limit, search: state.search });
      const items = Array.isArray(res) ? res : (res.items || []);
      state.total = res.total ?? items.length;
      tbody.innerHTML = items.length === 0
        ? `<tr><td colspan="8" class="table-empty">No bookings found.</td></tr>`
        : items.map(b => {
          const bookingId = b.booking_id ?? b.id;
          const guestName = b.guest_name || (b.guest_id ? `Guest #${b.guest_id}` : '—');
          const totalAmount = b.total_amount ?? b.total_price ?? 0;
          return `
          <tr class="clickable-row" style="cursor:pointer" onclick="BookingsPage.view(${bookingId})">
            <td><span style="font-family:monospace;font-size:0.8rem;color:var(--accent)">#${bookingId ?? '—'}</span></td>
            <td>${guestName}</td>
            <td>${fmt.date(b.check_in_date)}</td>
            <td>${fmt.date(b.check_out_date)}</td>
            <td>${b.number_of_guests || '—'}</td>
            <td>${fmt.currency(totalAmount)}</td>
            <td>${fmt.badge(b.status, statusMap.booking)}</td>
            <td>
              <div style="display:flex;gap:6px" onclick="event.stopPropagation()">
                <button class="btn btn-icon" onclick="event.stopPropagation(); BookingsPage.edit(${bookingId})" title="Edit"><svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M2 14l9.5-9.5M11 4.5l2.5-2.5a1.41 1.41 0 0 0 0-2 1.41 1.41 0 0 0-2 0l-2.5 2.5"/></svg></button>
                <button class="btn btn-icon danger" onclick="event.stopPropagation(); BookingsPage.del(${bookingId})" title="Delete"><svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M2 4h12M6 7v5M10 7v5M3 4l1 10c0 .6.4 1 1 1h6c.6 0 1-.4 1-1l1-10M6 2h4"/></svg></button>
              </div>
            </td>
          </tr>`;
        }).join('');
      renderPagination('bookings', { page: state.page, total: state.total, limit: state.limit, onPage: (p) => { state.page = p; fetchList(); } });
    } catch (err) {
      tbody.innerHTML = `<tr><td colspan="8" class="table-empty" style="color:var(--danger)">${err.message}</td></tr>`;
    }
  }

  function formHTML(b = {}) {
    return `
      <div class="form-row">
        <div class="form-group">
          <label class="form-label" for="b-guest">Guest ID <span class="required">*</span></label>
          <input class="form-control" id="b-guest" name="guest_id" type="number" value="${b.guest_id || ''}" placeholder="Guest ID">
          <div class="form-error" id="b-guest-err"></div>
        </div>
        <div class="form-group">
          <label class="form-label" for="b-guests-num">Party Size <span class="required">*</span></label>
          <input class="form-control" id="b-guests-num" name="number_of_guests" type="number" min="1" value="${b.number_of_guests || 1}">
          <div class="form-error" id="b-guests-num-err"></div>
        </div>
      </div>
      <div class="form-row">
        <div class="form-group">
          <label class="form-label" for="b-checkin">Check-in Date <span class="required">*</span></label>
          <input class="form-control" id="b-checkin" name="check_in_date" type="date" value="${b.check_in_date || ''}">
          <div class="form-error" id="b-checkin-err"></div>
        </div>
        <div class="form-group">
          <label class="form-label" for="b-checkout">Check-out Date <span class="required">*</span></label>
          <input class="form-control" id="b-checkout" name="check_out_date" type="date" value="${b.check_out_date || ''}">
          <div class="form-error" id="b-checkout-err"></div>
        </div>
      </div>
      <div class="form-row">
        <div class="form-group">
          <label class="form-label" for="b-total">Total Amount</label>
          <input class="form-control" id="b-total" name="total_amount" type="number" step="0.01" value="${b.total_amount || ''}" placeholder="0.00">
        </div>
        <div class="form-group">
          <label class="form-label" for="b-status">Status <span class="required">*</span></label>
          <select class="form-control" id="b-status" name="status">
            <option value="pending"     ${b.status === 'pending'      ? 'selected' : ''}>Pending</option>
            <option value="confirmed"   ${b.status === 'confirmed'    ? 'selected' : ''}>Confirmed</option>
            <option value="checked-in"  ${b.status === 'checked-in'   ? 'selected' : ''}>Checked In</option>
            <option value="checked-out" ${b.status === 'checked-out'  ? 'selected' : ''}>Checked Out</option>
            <option value="cancelled"   ${b.status === 'cancelled'    ? 'selected' : ''}>Cancelled</option>
          </select>
        </div>
      </div>`;
  }

  const schema = {
    'b-guest':      [Validate.rules.required, Validate.rules.positiveNum],
    'b-guests-num': [Validate.rules.required, Validate.rules.positiveNum],
    'b-checkin':    [Validate.rules.required],
    'b-checkout':   [Validate.rules.required, (v) => {
      const ci = document.getElementById('b-checkin')?.value;
      return ci && v && new Date(v) > new Date(ci) ? null : 'Check-out must be after check-in.';
    }],
  };

  function openForm(b = null) {
    const isEdit = !!b;
    const { el, close } = Modal.create(
      isEdit ? 'Edit Booking' : 'New Booking',
      formHTML(b || {}),
      `<button class="btn btn-outline" id="modal-cancel">Cancel</button>
       <button class="btn btn-primary" id="modal-save">${isEdit ? 'Save Changes' : 'Create Booking'}</button>`
    );
    Validate.attachLiveValidation(schema);
    el.querySelector('#modal-cancel').addEventListener('click', close);
    el.querySelector('#modal-save').addEventListener('click', async () => {
      if (!Validate.validateForm(schema)) return;
      const btn = el.querySelector('#modal-save');
      setLoading(btn, true);
      const data = Validate.getFormData(el.querySelector('.modal-body'));
      try {
        if (isEdit) await API.bookings.update(b.booking_id ?? b.id, data);
        else        await API.bookings.create(data);
        Toast.success(isEdit ? 'Booking updated.' : 'Booking created.');
        close(); fetchList();
      } catch (err) { Toast.error(err.message); }
      finally { setLoading(btn, false); }
    });
  }

  function detailHTML(b) {
    const rooms = (b.details || []).map(d => `
      <tr>
        <td>${d.room_number || '—'}</td>
        <td>${d.room_type || '—'}</td>
        <td>${fmt.currency(d.price_per_night || 0)}</td>
      </tr>
    `).join('');

    return `
      <div class="detail-grid" style="display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px">
        <div class="detail-card"><div class="stat-label">Booking ID</div><div class="stat-value" style="font-size:1.2rem">#${b.id ?? '—'}</div></div>
        <div class="detail-card"><div class="stat-label">Status</div><div class="stat-value" style="font-size:1.2rem">${fmt.badge(b.status, statusMap.booking)}</div></div>
        <div class="detail-card"><div class="stat-label">Guest</div><div class="stat-value" style="font-size:1.05rem">${b.guest_name || '—'}</div></div>
        <div class="detail-card"><div class="stat-label">Party Size</div><div class="stat-value" style="font-size:1.2rem">${b.number_of_guests || '—'}</div></div>
        <div class="detail-card"><div class="stat-label">Check-in</div><div class="stat-value" style="font-size:1.05rem">${fmt.date(b.check_in_date)}</div></div>
        <div class="detail-card"><div class="stat-label">Check-out</div><div class="stat-value" style="font-size:1.05rem">${fmt.date(b.check_out_date)}</div></div>
        <div class="detail-card" style="grid-column:1 / -1"><div class="stat-label">Total</div><div class="stat-value" style="font-size:1.2rem">${fmt.currency(b.total_amount || b.total_price || 0)}</div></div>
      </div>
      <div style="margin-top:16px">
        <div class="table-title" style="margin-bottom:10px">Rooms</div>
        <table>
          <thead><tr><th>Room #</th><th>Type</th><th>Price / Night</th></tr></thead>
          <tbody>
            ${rooms || '<tr><td colspan="3" class="table-empty">No room details</td></tr>'}
          </tbody>
        </table>
      </div>
    `;
  }

  async function view(id) {
    if (!id) return;
    try {
      const booking = await API.bookings.get(id);
      const { el, close } = Modal.create(
        `Booking #${booking.id ?? id} Details`,
        detailHTML(booking),
        `<button class="btn btn-outline" id="detail-close">Close</button>
         <button class="btn btn-primary" id="detail-edit">Edit Booking</button>`
      );
      el.querySelector('#detail-close').addEventListener('click', close);
      el.querySelector('#detail-edit').addEventListener('click', () => { close(); openForm(booking); });
    } catch (err) {
      Toast.error(err.message);
    }
  }

  async function edit(id) {
    try { openForm(await API.bookings.get(id)); } catch (err) { Toast.error(err.message); }
  }

  function del(id) {
    confirmDialog(`Delete booking <strong>#${id}</strong>?`, async () => {
      try { await API.bookings.delete(id); Toast.success('Booking deleted.'); fetchList(); }
      catch (err) { Toast.error(err.message); }
    });
  }

  return { load, view, edit, del, create: () => openForm() };
})();

// ═══════════════════════════════════════════════════════════════════════════
// SERVICES
// ═══════════════════════════════════════════════════════════════════════════
const ServicesPage = (() => {
  let state = { page: 1, limit: 10, search: '', total: 0 };

  async function load() {
    document.getElementById('page-services').innerHTML = buildTableCard({
      id: 'services', title: 'Services', btnLabel: 'Add Service', btnId: 'btn-add-service',
      searchId: 'services-search',
      cols: ['Service Name', 'Price', 'Description', 'Actions'],
    });
    document.getElementById('btn-add-service').addEventListener('click', () => openForm());
    let timer;
    document.getElementById('services-search').addEventListener('input', (e) => {
      clearTimeout(timer);
      timer = setTimeout(() => { state.search = e.target.value; state.page = 1; fetchList(); }, 350);
    });
    fetchList();
  }

  async function fetchList() {
    const tbody = document.getElementById('services-tbody');
    tbody.innerHTML = `<tr><td colspan="4" class="table-empty"><span class="spinner"></span></td></tr>`;
    try {
      const res = await API.services.list({ skip: (state.page - 1) * state.limit, limit: state.limit, search: state.search });
      const items = Array.isArray(res) ? res : (res.items || []);
      state.total = res.total ?? items.length;
      tbody.innerHTML = items.length === 0
        ? `<tr><td colspan="4" class="table-empty">No services found.</td></tr>`
        : items.map(s => `
          <tr>
            <td><strong>${s.service_name}</strong></td>
            <td>${s.service_price ? fmt.currency(s.service_price) : '—'}</td>
            <td style="color:var(--text-muted);font-size:0.85rem">${s.description || '—'}</td>
            <td>
              <div style="display:flex;gap:6px">
                 <button class="btn btn-icon" onclick="ServicesPage.edit(${s.service_id})" title="Edit"><svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M2 14l9.5-9.5M11 4.5l2.5-2.5a1.41 1.41 0 0 0 0-2 1.41 1.41 0 0 0-2 0l-2.5 2.5"/></svg></button>
                 <button class="btn btn-icon danger" onclick="ServicesPage.del(${s.service_id},'${s.service_name}')" title="Delete"><svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M2 4h12M6 7v5M10 7v5M3 4l1 10c0 .6.4 1 1 1h6c.6 0 1-.4 1-1l1-10M6 2h4"/></svg></button>
              </div>
            </td>
          </tr>`).join('');
      renderPagination('services', { page: state.page, total: state.total, limit: state.limit, onPage: (p) => { state.page = p; fetchList(); } });
    } catch (err) {
      tbody.innerHTML = `<tr><td colspan="4" class="table-empty" style="color:var(--danger)">${err.message}</td></tr>`;
    }
  }

  function formHTML(s = {}) {
    return `
      <div class="form-group">
        <label class="form-label" for="svc-name">Service Name <span class="required">*</span></label>
        <input class="form-control" id="svc-name" name="service_name" value="${s.service_name || ''}" placeholder="Spa, Room Service…">
        <div class="form-error" id="svc-name-err"></div>
      </div>
      <div class="form-group">
        <label class="form-label" for="svc-price">Price <span class="required">*</span></label>
        <input class="form-control" id="svc-price" name="service_price" type="number" step="0.01" value="${s.service_price || ''}" placeholder="0.00">
        <div class="form-error" id="svc-price-err"></div>
      </div>
      <div class="form-group">
        <label class="form-label" for="svc-desc">Description</label>
        <textarea class="form-control" id="svc-desc" name="description" rows="3" placeholder="Describe the service…" style="resize:vertical">${s.description || ''}</textarea>
      </div>`;
  }

  const schema = {
    'svc-name':  [Validate.rules.required],
    'svc-price': [Validate.rules.required, Validate.rules.nonNegNum],
  };

  function openForm(s = null) {
    const isEdit = !!s;
    const { el, close } = Modal.create(
      isEdit ? 'Edit Service' : 'Add Service',
      formHTML(s || {}),
      `<button class="btn btn-outline" id="modal-cancel">Cancel</button>
       <button class="btn btn-primary" id="modal-save">${isEdit ? 'Save Changes' : 'Create Service'}</button>`
    );
    Validate.attachLiveValidation(schema);
    el.querySelector('#modal-cancel').addEventListener('click', close);
    el.querySelector('#modal-save').addEventListener('click', async () => {
      if (!Validate.validateForm(schema)) return;
      const btn = el.querySelector('#modal-save');
      setLoading(btn, true);
      const data = Validate.getFormData(el.querySelector('.modal-body'));
      try {
        if (isEdit) await API.services.update(s.service_id, data);
        else        await API.services.create(data);
        Toast.success(isEdit ? 'Service updated.' : 'Service created.');
        close(); fetchList();
      } catch (err) { Toast.error(err.message); }
      finally { setLoading(btn, false); }
    });
  }

  async function edit(id) {
    try { openForm(await API.services.get(id)); } catch (err) { Toast.error(err.message); }
  }

  function del(id, name) {
    confirmDialog(`Delete service <strong>${name}</strong>?`, async () => {
      try { await API.services.delete(id); Toast.success('Service deleted.'); fetchList(); }
      catch (err) { Toast.error(err.message); }
    });
  }

  return { load, edit, del, create: () => openForm() };
})();

// ═══════════════════════════════════════════════════════════════════════════
// EMPLOYEES
// ═══════════════════════════════════════════════════════════════════════════
const EmployeesPage = (() => {
  let state = { page: 1, limit: 10, search: '', total: 0 };

  async function load() {
    document.getElementById('page-employees').innerHTML = buildTableCard({
      id: 'employees', title: 'Employees', btnLabel: 'Add Employee', btnId: 'btn-add-employee',
      searchId: 'employees-search',
      cols: ['Name', 'Phone', 'Email', 'Role', 'Actions'],
    });
    document.getElementById('btn-add-employee').addEventListener('click', () => openForm());
    let timer;
    document.getElementById('employees-search').addEventListener('input', (e) => {
      clearTimeout(timer);
      timer = setTimeout(() => { state.search = e.target.value; state.page = 1; fetchList(); }, 350);
    });
    fetchList();
  }

  async function fetchList() {
    const tbody = document.getElementById('employees-tbody');
    tbody.innerHTML = `<tr><td colspan="5" class="table-empty"><span class="spinner"></span></td></tr>`;
    try {
      const res = await API.employees.list({ skip: (state.page - 1) * state.limit, limit: state.limit, search: state.search });
      const items = Array.isArray(res) ? res : (res.items || []);
      state.total = res.total ?? items.length;
      tbody.innerHTML = items.length === 0
        ? `<tr><td colspan="5" class="table-empty">No employees found.</td></tr>`
        : items.map(e => {
          const employeeId = e.employee_id ?? e.id;
          const safeName = String(e.name || e.full_name || 'Employee').replace(/'/g, "\\'");
          return `
          <tr>
            <td>
              <div style="display:flex;align-items:center;gap:8px">
                <div style="width:30px;height:30px;border-radius:50%;background:var(--accent-dim);color:var(--accent);display:flex;align-items:center;justify-content:center;font-size:0.75rem;font-weight:600;flex-shrink:0">${fmt.initials(e.name)}</div>
                <span style="font-weight:500">${e.name}</span>
              </div>
            </td>
            <td>${e.phone || '—'}</td>
            <td>${e.email || '—'}</td>
            <td>${e.role ? `<span class="badge badge-info">${e.role}</span>` : '—'}</td>
            <td>
              <div style="display:flex;gap:6px">
                 <button class="btn btn-icon" onclick="EmployeesPage.edit(${employeeId})" title="Edit"><svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M2 14l9.5-9.5M11 4.5l2.5-2.5a1.41 1.41 0 0 0 0-2 1.41 1.41 0 0 0-2 0l-2.5 2.5"/></svg></button>
                 <button class="btn btn-icon danger" onclick="EmployeesPage.del(${employeeId},'${safeName}')" title="Delete"><svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M2 4h12M6 7v5M10 7v5M3 4l1 10c0 .6.4 1 1 1h6c.6 0 1-.4 1-1l1-10M6 2h4"/></svg></button>
              </div>
            </td>
          </tr>`;
        }).join('');
      renderPagination('employees', { page: state.page, total: state.total, limit: state.limit, onPage: (p) => { state.page = p; fetchList(); } });
    } catch (err) {
      tbody.innerHTML = `<tr><td colspan="5" class="table-empty" style="color:var(--danger)">${err.message}</td></tr>`;
    }
  }

  function formHTML(e = {}) {
    return `
      <div class="form-group">
        <label class="form-label" for="emp-name">Full Name <span class="required">*</span></label>
        <input class="form-control" id="emp-name" name="name" value="${e.name || ''}" placeholder="Jane Smith">
        <div class="form-error" id="emp-name-err"></div>
      </div>
      <div class="form-row">
        <div class="form-group">
          <label class="form-label" for="emp-phone">Phone <span class="required">*</span></label>
          <input class="form-control" id="emp-phone" name="phone" value="${e.phone || ''}" placeholder="+1 555 0000">
          <div class="form-error" id="emp-phone-err"></div>
        </div>
        <div class="form-group">
          <label class="form-label" for="emp-email">Email</label>
          <input class="form-control" id="emp-email" name="email" type="email" value="${e.email || ''}" placeholder="staff@hotel.com">
          <div class="form-error" id="emp-email-err"></div>
        </div>
      </div>
      <div class="form-group">
        <label class="form-label" for="emp-role">Role <span class="required">*</span></label>
        <select class="form-control" id="emp-role" name="role">
          <option value="">— Select role —</option>
          ${['Receptionist','Housekeeping','Manager','Concierge','Security','Maintenance','Chef','Waiter'].map(r =>
            `<option value="${r}" ${e.role === r ? 'selected' : ''}>${r}</option>`).join('')}
        </select>
        <div class="form-error" id="emp-role-err"></div>
      </div>`;
  }

  const schema = {
    'emp-name':  [Validate.rules.required],
    'emp-phone': [Validate.rules.required, Validate.rules.phone],
    'emp-email': [(v) => v ? Validate.rules.email(v) : null],
    'emp-role':  [Validate.rules.required],
  };

  function openForm(e = null) {
    const isEdit = !!e;
    const { el, close } = Modal.create(
      isEdit ? 'Edit Employee' : 'Add Employee',
      formHTML(e || {}),
      `<button class="btn btn-outline" id="modal-cancel">Cancel</button>
       <button class="btn btn-primary" id="modal-save">${isEdit ? 'Save Changes' : 'Add Employee'}</button>`
    );
    Validate.attachLiveValidation(schema);
    el.querySelector('#modal-cancel').addEventListener('click', close);
    el.querySelector('#modal-save').addEventListener('click', async () => {
      if (!Validate.validateForm(schema)) return;
      const btn = el.querySelector('#modal-save');
      setLoading(btn, true);
      const data = Validate.getFormData(el.querySelector('.modal-body'));
      try {
        if (isEdit) await API.employees.update(e.employee_id ?? e.id, data);
        else        await API.employees.create(data);
        Toast.success(isEdit ? 'Employee updated.' : 'Employee added.');
        close(); fetchList();
      } catch (err) { Toast.error(err.message); }
      finally { setLoading(btn, false); }
    });
  }

  async function edit(id) {
    try { openForm(await API.employees.get(id)); } catch (err) { Toast.error(err.message); }
  }

  function del(id, name) {
    confirmDialog(`Delete employee <strong>${name}</strong>?`, async () => {
      try { await API.employees.delete(id); Toast.success('Employee deleted.'); fetchList(); }
      catch (err) { Toast.error(err.message); }
    });
  }

  return { load, edit, del, create: () => openForm() };
})();

// ═══════════════════════════════════════════════════════════════════════════
// PAYMENTS
// ═══════════════════════════════════════════════════════════════════════════
const PaymentsPage = (() => {
  let state = { page: 1, limit: 10, search: '', total: 0 };

  async function load() {
    document.getElementById('page-payments').innerHTML = buildTableCard({
      id: 'payments', title: 'Payments', btnLabel: 'Record Payment', btnId: 'btn-add-payment',
      searchId: 'payments-search',
      cols: ['Payment ID', 'Booking ID', 'Date', 'Amount', 'Method', 'Transaction ID', 'Status', 'Actions'],
    });
    document.getElementById('btn-add-payment').addEventListener('click', () => openForm());
    let timer;
    document.getElementById('payments-search').addEventListener('input', (e) => {
      clearTimeout(timer);
      timer = setTimeout(() => { state.search = e.target.value; state.page = 1; fetchList(); }, 350);
    });
    fetchList();
  }

  async function fetchList() {
    const tbody = document.getElementById('payments-tbody');
    tbody.innerHTML = `<tr><td colspan="8" class="table-empty"><span class="spinner"></span></td></tr>`;
    try {
      const res = await API.payments.list({ skip: (state.page - 1) * state.limit, limit: state.limit, search: state.search });
      const items = Array.isArray(res) ? res : (res.items || []);
      state.total = res.total ?? items.length;
      tbody.innerHTML = items.length === 0
        ? `<tr><td colspan="8" class="table-empty">No payments found.</td></tr>`
        : items.map(p => `
          <tr>
            <td><span style="font-family:monospace;font-size:0.8rem;color:var(--accent)">#${p.payment_id}</span></td>
            <td>#${p.booking_id}</td>
            <td>${fmt.date(p.payment_date)}</td>
            <td><strong>${p.amount ? fmt.currency(p.amount) : '—'}</strong></td>
            <td>${p.payment_method || '—'}</td>
            <td style="font-family:monospace;font-size:0.78rem;color:var(--text-muted)">${p.transaction_id || '—'}</td>
            <td>${fmt.badge(p.status, statusMap.payment)}</td>
            <td>
                <button class="btn btn-icon" onclick="PaymentsPage.edit(${p.payment_id})" title="Edit"><svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M2 14l9.5-9.5M11 4.5l2.5-2.5a1.41 1.41 0 0 0 0-2 1.41 1.41 0 0 0-2 0l-2.5 2.5"/></svg></button>
            </td>
          </tr>`).join('');
      renderPagination('payments', { page: state.page, total: state.total, limit: state.limit, onPage: (pg) => { state.page = pg; fetchList(); } });
    } catch (err) {
      tbody.innerHTML = `<tr><td colspan="8" class="table-empty" style="color:var(--danger)">${err.message}</td></tr>`;
    }
  }

  function formHTML(p = {}) {
    return `
      <div class="form-row">
        <div class="form-group">
          <label class="form-label" for="pay-booking">Booking ID <span class="required">*</span></label>
          <input class="form-control" id="pay-booking" name="booking_id" type="number" value="${p.booking_id || ''}" placeholder="Booking ID">
          <div class="form-error" id="pay-booking-err"></div>
        </div>
        <div class="form-group">
          <label class="form-label" for="pay-amount">Amount <span class="required">*</span></label>
          <input class="form-control" id="pay-amount" name="amount" type="number" step="0.01" value="${p.amount || ''}" placeholder="0.00">
          <div class="form-error" id="pay-amount-err"></div>
        </div>
      </div>
      <div class="form-row">
        <div class="form-group">
          <label class="form-label" for="pay-date">Payment Date <span class="required">*</span></label>
          <input class="form-control" id="pay-date" name="payment_date" type="date" value="${p.payment_date || new Date().toISOString().slice(0,10)}">
          <div class="form-error" id="pay-date-err"></div>
        </div>
        <div class="form-group">
          <label class="form-label" for="pay-method">Method <span class="required">*</span></label>
          <select class="form-control" id="pay-method" name="payment_method">
            ${['Cash','Credit Card','Debit Card','Bank Transfer','Online'].map(m =>
              `<option value="${m}" ${p.payment_method === m ? 'selected':''}>${m}</option>`).join('')}
          </select>
        </div>
      </div>
      <div class="form-row">
        <div class="form-group">
          <label class="form-label" for="pay-txn">Transaction ID</label>
          <input class="form-control" id="pay-txn" name="transaction_id" value="${p.transaction_id || ''}" placeholder="TXN-001">
        </div>
        <div class="form-group">
          <label class="form-label" for="pay-status">Status</label>
          <select class="form-control" id="pay-status" name="status">
            ${['pending','completed','failed','refunded'].map(s =>
              `<option value="${s}" ${p.status === s ? 'selected':''}>${s}</option>`).join('')}
          </select>
        </div>
      </div>`;
  }

  const schema = {
    'pay-booking': [Validate.rules.required, Validate.rules.positiveNum],
    'pay-amount':  [Validate.rules.required, Validate.rules.positiveNum],
    'pay-date':    [Validate.rules.required],
  };

  function openForm(p = null) {
    const isEdit = !!p;
    const { el, close } = Modal.create(
      isEdit ? 'Edit Payment' : 'Record Payment',
      formHTML(p || {}),
      `<button class="btn btn-outline" id="modal-cancel">Cancel</button>
       <button class="btn btn-primary" id="modal-save">${isEdit ? 'Save Changes' : 'Record'}</button>`
    );
    Validate.attachLiveValidation(schema);
    el.querySelector('#modal-cancel').addEventListener('click', close);
    el.querySelector('#modal-save').addEventListener('click', async () => {
      if (!Validate.validateForm(schema)) return;
      const btn = el.querySelector('#modal-save');
      setLoading(btn, true);
      const data = Validate.getFormData(el.querySelector('.modal-body'));
      try {
        if (isEdit) await API.payments.update(p.payment_id, data);
        else        await API.payments.create(data);
        Toast.success(isEdit ? 'Payment updated.' : 'Payment recorded.');
        close(); fetchList();
      } catch (err) { Toast.error(err.message); }
      finally { setLoading(btn, false); }
    });
  }

  async function edit(id) {
    try { openForm(await API.payments.get(id)); } catch (err) { Toast.error(err.message); }
  }

  return { load, edit, create: () => openForm() };
})();
