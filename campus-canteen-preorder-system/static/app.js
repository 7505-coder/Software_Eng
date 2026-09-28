(() => {
  const state = {
    csrf: '',
    user: null,
    menu: [],
    cart: new Map(),
    category: 'All',
    query: '',
    authMode: 'login',
    previousStatuses: new Map(),
    hasLoadedOrders: false,
    toastTimer: null,
  };

  const $ = (selector) => document.querySelector(selector);
  const menuGrid = $('#menuGrid');
  const ordersPanel = $('#studentOrders');
  const authDialog = $('#authDialog');

  function escapeHtml(value) {
    return String(value ?? '').replace(/[&<>"']/g, (char) => ({
      '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;',
    })[char]);
  }

  function rupees(value) {
    const amount = Number(value);
    return new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR' }).format(Number.isFinite(amount) ? amount : 0);
  }

  async function api(path, options = {}) {
    const method = (options.method || 'GET').toUpperCase();
    const headers = { Accept: 'application/json', ...(options.headers || {}) };
    let body = options.body;
    if (body && typeof body !== 'string') {
      headers['Content-Type'] = 'application/json';
      body = JSON.stringify(body);
    }
    if (!['GET', 'HEAD', 'OPTIONS'].includes(method)) headers['X-CSRF-Token'] = state.csrf;
    const response = await fetch(path, { ...options, method, headers, body, credentials: 'same-origin' });
    const data = await response.json().catch(() => ({}));
    if (data.csrf_token) state.csrf = data.csrf_token;
    if (!response.ok) {
      if (response.status === 401 && state.user) setUser(null);
      throw new Error(data.error || `Request failed (${response.status}).`);
    }
    return data;
  }

  function toast(message) {
    const node = $('#toast');
    node.textContent = message;
    node.hidden = false;
    window.clearTimeout(state.toastTimer);
    state.toastTimer = window.setTimeout(() => { node.hidden = true; }, 4200);
  }

  function setUser(user) {
    state.user = user;
    const loggedIn = Boolean(user);
    $('#authOpen').hidden = loggedIn;
    $('#logoutButton').hidden = !loggedIn;
    $('#userBadge').hidden = !loggedIn;
    $('#userBadge').textContent = loggedIn ? `${user.name} · ${user.role}` : '';
    $('#ordersToggle').hidden = !loggedIn || user.role !== 'student';
    $('#staffPanel').hidden = !loggedIn || !['staff', 'admin'].includes(user.role);
    $('#dashboard').hidden = !loggedIn || !['staff', 'admin'].includes(user.role);
    $('#adminMenuPanel').hidden = !loggedIn || user.role !== 'admin';
    if (loggedIn && ['staff', 'admin'].includes(user.role)) {
      loadDashboard();
      loadOrders();
      if (user.role === 'admin') loadMenuAdmin();
    } else {
      $('#staffOrders').replaceChildren();
      $('#dashboard').replaceChildren();
      if (!loggedIn || user.role !== 'student') ordersPanel.hidden = true;
    }
    renderMenu();
  }

  function categoryEmoji(category) {
    const key = String(category || '').toLowerCase();
    if (key.includes('drink')) return ['☕', 'drinks'];
    if (key.includes('snack')) return ['🥟', 'snacks'];
    if (key.includes('meal') || key.includes('lunch')) return ['🍛', 'meals'];
    return ['🍽️', 'specials'];
  }

  async function loadMenu() {
    const params = new URLSearchParams();
    if (state.query) params.set('q', state.query);
    const data = await api(`/api/menu?${params.toString()}`);
    state.menu = data.items;
    renderCategories();
    renderMenu();
    renderCart();
    if (state.user?.role === 'admin') renderMenuAdmin();
  }

  function renderCategories() {
    const categories = ['All', ...new Set(state.menu.map((item) => item.category))];
    if (!categories.includes(state.category)) state.category = 'All';
    $('#categoryFilters').innerHTML = categories.map((category) => `
      <button type="button" class="filter-chip ${state.category === category ? 'active' : ''}" data-category="${escapeHtml(category)}" aria-pressed="${state.category === category}">${escapeHtml(category)}</button>
    `).join('');
  }

  function renderMenu() {
    const visible = state.menu.filter((item) => state.category === 'All' || item.category === state.category);
    if (!visible.length) {
      menuGrid.innerHTML = '<p class="empty-menu">No menu items match that search.</p>';
      return;
    }
    const mayAdd = !state.user || state.user.role === 'student';
    menuGrid.innerHTML = visible.map((item) => {
      const [emoji, iconClass] = categoryEmoji(item.category);
      return `<article class="menu-card">
        <div class="menu-card-top"><span class="dish-icon ${iconClass}" aria-hidden="true">${emoji}</span><span class="availability ${item.available ? '' : 'unavailable'}">${item.available ? 'Available' : 'Sold out'}</span></div>
        <div><h3>${escapeHtml(item.name)}</h3><p>${escapeHtml(item.description || item.category)}</p></div>
        <div class="menu-card-bottom"><span class="price">${rupees(item.price)}</span><button class="add-button" type="button" data-add="${item.id}" aria-label="Add ${escapeHtml(item.name)} to order" ${!item.available || !mayAdd ? 'disabled' : ''}>+</button></div>
      </article>`;
    }).join('');
  }

  function renderCart() {
    const entries = [...state.cart.entries()];
    const count = entries.reduce((sum, [, value]) => sum + value.quantity, 0);
    const total = entries.reduce((sum, [, value]) => sum + Math.round(Number(value.item.price) * 100) * value.quantity, 0);
    $('#cartCount').textContent = String(count);
    $('#cartTotal').textContent = rupees(total / 100);
    $('#checkoutButton').disabled = count === 0;
    if (!entries.length) {
      $('#cartItems').innerHTML = '<p class="empty-state">Your basket is waiting for something tasty.</p>';
      return;
    }
    $('#cartItems').innerHTML = entries.map(([id, value]) => `
      <div class="cart-line">
        <div><strong>${escapeHtml(value.item.name)}</strong><small>${rupees(value.item.price)} each</small>
          <div class="quantity-controls"><button type="button" data-quantity="${id}" data-delta="-1" aria-label="Remove one ${escapeHtml(value.item.name)}">−</button><span>${value.quantity}</span><button type="button" data-quantity="${id}" data-delta="1" aria-label="Add one ${escapeHtml(value.item.name)}">+</button></div>
        </div><span class="line-price">${rupees(Number(value.item.price) * value.quantity)}</span>
      </div>`).join('');
  }

  function openAuth(mode = 'login') {
    setAuthMode(mode);
    if (!authDialog.open) authDialog.showModal();
    window.setTimeout(() => $('#authForm [name="email"]').focus(), 20);
  }

  function setAuthMode(mode) {
    state.authMode = mode;
    const registering = mode === 'register';
    $('#nameField').hidden = !registering;
    $('#authTitle').textContent = registering ? 'Create a student account' : 'Sign in';
    $('#authIntro').textContent = registering ? 'Use your campus email. New accounts can place and track orders.' : 'Sign in to place an order and track pickup status.';
    $('#authSubmit').textContent = registering ? 'Create account' : 'Sign in';
    $('#loginTab').classList.toggle('active', !registering);
    $('#registerTab').classList.toggle('active', registering);
    $('#loginTab').setAttribute('aria-selected', String(!registering));
    $('#registerTab').setAttribute('aria-selected', String(registering));
    $('#authError').hidden = true;
    $('#authForm [name="password"]').autocomplete = registering ? 'new-password' : 'current-password';
    $('#authForm [name="name"]').required = registering;
  }

  async function loadOrders() {
    if (!state.user) return;
    try {
      const data = await api('/api/orders');
      const orders = data.orders;
      if (state.user.role === 'student') {
        $('#myOrdersList').innerHTML = orders.length ? orders.map((order) => orderCard(order, false)).join('') : '<p class="no-orders">You have not placed an order yet.</p>';
      } else {
        $('#staffOrders').innerHTML = orders.length ? orders.map((order) => orderCard(order, true)).join('') : '<p class="no-orders">The order queue is clear.</p>';
      }
      if (state.hasLoadedOrders) {
        for (const order of orders) {
          if (order.status === 'ready' && state.previousStatuses.get(order.id) !== 'ready' && state.user.role === 'student') {
            toast(`Order ${order.code} is ready for pickup.`);
          }
        }
      }
      state.previousStatuses = new Map(orders.map((order) => [order.id, order.status]));
      state.hasLoadedOrders = true;
    } catch (error) {
      toast(error.message);
    }
  }

  function orderCard(order, staffView) {
    const items = order.items.map((item) => `${item.quantity} × ${escapeHtml(item.name)}`).join(' · ');
    const date = new Date(order.created_at);
    const formatted = Number.isNaN(date.getTime()) ? '' : date.toLocaleString([], { month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit' });
    const next = { pending: 'accepted', accepted: 'preparing', preparing: 'ready', ready: 'completed' }[order.status];
    const nextLabel = { accepted: 'Accept order', preparing: 'Start preparing', ready: 'Mark ready', completed: 'Complete pickup' }[next];
    const canCancel = staffView && ['pending', 'accepted', 'preparing'].includes(order.status);
    return `<article class="order-card" data-order-id="${order.id}">
      <div class="order-card-head"><div><span class="order-code">${escapeHtml(order.code)}</span><div class="order-meta">${staffView ? `${escapeHtml(order.student)} · ` : ''}${escapeHtml(formatted)}${order.pickup_slot ? ` · Pickup ${escapeHtml(order.pickup_slot)}` : ''}</div></div><span class="status-pill ${escapeHtml(order.status)}">${escapeHtml(order.status)}</span></div>
      <p class="order-items-text">${items}${order.note ? `<br><span>Note: ${escapeHtml(order.note)}</span>` : ''}</p>
      <div class="order-card-foot"><span>${rupees(order.total)}</span><span>${order.status === 'ready' ? 'Ready for pickup' : escapeHtml(order.status.replace('_', ' '))}</span></div>
      ${staffView && next ? `<div class="order-actions"><button class="order-action" type="button" data-order-status="${next}" data-order-id="${order.id}">${nextLabel}</button>${canCancel ? `<button class="order-action cancel" type="button" data-order-status="cancelled" data-order-id="${order.id}">Cancel</button>` : ''}</div>` : ''}
    </article>`;
  }

  async function loadDashboard() {
    try {
      const data = await api('/api/dashboard');
      $('#dashboard').innerHTML = [
        ['Orders today', data.today_orders], ['Active orders', data.active_orders], ['Ready for pickup', data.ready_orders], ['Completed sales', rupees(data.completed_sales)],
      ].map(([label, value]) => `<div class="metric-card"><span>${label}</span><strong>${value}</strong></div>`).join('');
    } catch (error) { toast(error.message); }
  }

  function renderMenuAdmin() {
    $('#menuAdminList').innerHTML = state.menu.map((item) => `<div class="menu-admin-row"><span>${escapeHtml(item.name)} · ${rupees(item.price)}</span><span><button type="button" data-menu-toggle="${item.id}">${item.available ? 'Mark sold out' : 'Mark available'}</button> <button class="archive" type="button" data-menu-archive="${item.id}">Archive</button></span></div>`).join('');
  }

  async function loadMenuAdmin() {
    try { await loadMenu(); renderMenuAdmin(); } catch (error) { toast(error.message); }
  }

  async function placeOrder() {
    if (!state.user) {
      openAuth('login');
      toast('Sign in or create a student account to place your order.');
      return;
    }
    if (state.user.role !== 'student') {
      toast('Only student accounts can place student orders.');
      return;
    }
    const items = [...state.cart.entries()].map(([id, value]) => ({ menu_item_id: id, quantity: value.quantity }));
    try {
      const data = await api('/api/orders', { method: 'POST', body: { items, pickup_slot: $('#pickupSlot').value, note: $('#orderNote').value } });
      state.cart.clear();
      $('#pickupSlot').value = '';
      $('#orderNote').value = '';
      renderCart();
      toast(`Order ${data.order.code} placed. We will update its status here.`);
      ordersPanel.hidden = false;
      await loadOrders();
      ordersPanel.scrollIntoView({ behavior: 'smooth', block: 'start' });
    } catch (error) { toast(error.message); }
  }

  async function onAuthSubmit(event) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const body = { email: form.get('email'), password: form.get('password') };
    const endpoint = state.authMode === 'register' ? '/api/auth/register' : '/api/auth/login';
    if (state.authMode === 'register') body.name = form.get('name');
    $('#authError').hidden = true;
    try {
      const data = await api(endpoint, { method: 'POST', body });
      setUser(data.user);
      authDialog.close();
      event.currentTarget.reset();
      toast(`Signed in as ${data.user.name}.`);
    } catch (error) {
      $('#authError').textContent = error.message;
      $('#authError').hidden = false;
    }
  }

  async function handleOrderAction(event) {
    const button = event.target.closest('[data-order-status]');
    if (!button) return;
    button.disabled = true;
    try {
      await api(`/api/staff/orders/${button.dataset.orderId}`, { method: 'PATCH', body: { status: button.dataset.orderStatus } });
      await Promise.all([loadOrders(), loadDashboard()]);
      toast('Order status updated.');
    } catch (error) { toast(error.message); button.disabled = false; }
  }

  async function handleMenuAdmin(event) {
    const toggle = event.target.closest('[data-menu-toggle]');
    const archive = event.target.closest('[data-menu-archive]');
    try {
      if (toggle) {
        const item = state.menu.find((candidate) => candidate.id === Number(toggle.dataset.menuToggle));
        await api(`/api/menu/${item.id}`, { method: 'PATCH', body: { available: !item.available } });
        await loadMenu();
        toast('Menu availability updated.');
      } else if (archive) {
        await api(`/api/menu/${archive.dataset.menuArchive}`, { method: 'DELETE' });
        await loadMenu();
        toast('Menu item archived.');
      }
    } catch (error) { toast(error.message); }
  }

  async function initialize() {
    try {
      const sessionData = await api('/api/session');
      state.csrf = sessionData.csrf_token;
      setUser(sessionData.user);
      await loadMenu();
    } catch (error) { toast(error.message); }

    $('#authOpen').addEventListener('click', () => openAuth('login'));
    $('#loginTab').addEventListener('click', () => setAuthMode('login'));
    $('#registerTab').addEventListener('click', () => setAuthMode('register'));
    $('#authForm').addEventListener('submit', onAuthSubmit);
    $('#logoutButton').addEventListener('click', async () => {
      try { await api('/api/auth/logout', { method: 'POST', body: {} }); setUser(null); state.previousStatuses.clear(); state.hasLoadedOrders = false; toast('You are signed out.'); await loadMenu(); }
      catch (error) { toast(error.message); }
    });
    $('#categoryFilters').addEventListener('click', (event) => {
      const chip = event.target.closest('[data-category]');
      if (!chip) return;
      state.category = chip.dataset.category;
      renderCategories();
      renderMenu();
    });
    $('#menuGrid').addEventListener('click', (event) => {
      const button = event.target.closest('[data-add]');
      if (!button) return;
      const item = state.menu.find((candidate) => candidate.id === Number(button.dataset.add));
      if (!item) return;
      const existing = state.cart.get(item.id);
      if (existing) existing.quantity = Math.min(existing.quantity + 1, 20);
      else state.cart.set(item.id, { item, quantity: 1 });
      renderCart();
    });
    $('#cartItems').addEventListener('click', (event) => {
      const button = event.target.closest('[data-quantity]');
      if (!button) return;
      const id = Number(button.dataset.quantity);
      const current = state.cart.get(id);
      if (!current) return;
      current.quantity += Number(button.dataset.delta);
      if (current.quantity <= 0) state.cart.delete(id);
      renderCart();
    });
    $('#checkoutButton').addEventListener('click', placeOrder);
    $('#ordersToggle').addEventListener('click', async () => {
      ordersPanel.hidden = !ordersPanel.hidden;
      if (!ordersPanel.hidden) { await loadOrders(); ordersPanel.scrollIntoView({ behavior: 'smooth', block: 'start' }); }
    });
    $('#refreshOrders').addEventListener('click', () => { loadOrders(); loadDashboard(); });
    $('#staffOrders').addEventListener('click', handleOrderAction);
    $('#menuAdminList').addEventListener('click', handleMenuAdmin);
    $('#menuForm').addEventListener('submit', async (event) => {
      event.preventDefault();
      const form = new FormData(event.currentTarget);
      try {
        await api('/api/menu', { method: 'POST', body: Object.fromEntries(form.entries()) });
        event.currentTarget.reset();
        await loadMenu();
        toast('Menu item added.');
      } catch (error) { toast(error.message); }
    });
    let searchTimer;
    $('#menuSearch').addEventListener('input', () => {
      window.clearTimeout(searchTimer);
      searchTimer = window.setTimeout(async () => {
        state.query = $('#menuSearch').value.trim();
        try { await loadMenu(); } catch (error) { toast(error.message); }
      }, 220);
    });
    window.setInterval(() => {
      if (state.user) {
        loadOrders();
        if (['staff', 'admin'].includes(state.user.role)) loadDashboard();
      }
    }, 12000);
  }

  document.addEventListener('DOMContentLoaded', initialize);
})();
