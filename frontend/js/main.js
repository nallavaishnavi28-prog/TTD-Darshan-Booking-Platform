// Constants
const IS_LOCAL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
const API_URL = IS_LOCAL ? 'http://localhost:5000' : 'https://ttd-darshan-booking-platform-3.onrender.com';

// Auth
function getToken() {
  return localStorage.getItem('ttd_token');
}

function getUser() {
  const u = localStorage.getItem('ttd_user');
  return u ? JSON.parse(u) : null;
}

function saveAuth(token, user) {
  localStorage.setItem('ttd_token', token);
  localStorage.setItem('ttd_user', JSON.stringify(user));
}

function logout() {
  localStorage.removeItem('ttd_token');
  localStorage.removeItem('ttd_user');
  window.location.href = 'login.html';
}

function isLoggedIn() {
  return !!getToken();
}

function requireLogin() {
  if (!isLoggedIn()) {
    window.location.href = 'login.html';
    return false;
  }
  return true;
}

// API Wrapper
async function api(method, endpoint, body = null) {
  const headers = { 'Content-Type': 'application/json' };
  const token = getToken();
  if (token) headers['Authorization'] = `Bearer ${token}`;

  const options = { method, headers };
  if (body) options.body = JSON.stringify(body);

  const res = await fetch(`${API_URL}${endpoint}`, options);
  
  if (res.status === 401 || res.status === 403) {
    logout();
    throw new Error('Unauthorized');
  }

  return res.json();
}

// Utils
function showAlert(id, msg, type = 'danger') {
  const el = document.getElementById(id);
  if (!el) return;
  el.textContent = msg;
  el.className = `alert alert-${type} show`;
  setTimeout(() => el.classList.remove('show'), 5000);
}

function btnLoading(id, isLoading, originalText) {
  const btn = document.getElementById(id);
  if (!btn) return;
  const text = btn.querySelector('.btn-text');
  const spin = btn.querySelector('.spin');
  if (isLoading) {
    btn.disabled = true;
    if (text) text.textContent = originalText;
    if (spin) spin.style.display = 'inline-block';
  } else {
    btn.disabled = false;
    if (text) text.textContent = originalText;
    if (spin) spin.style.display = 'none';
  }
}

function fDate(dStr) {
  if (!dStr) return '—';
  const d = new Date(dStr);
  return d.toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' });
}

function fTime(tStr) {
  if (!tStr) return '—';
  // Check if it's full time string or just HH:MM
  if (tStr.includes('T')) {
    const d = new Date(tStr);
    return d.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' });
  }
  // If "09:00:00"
  const parts = tStr.split(':');
  if (parts.length >= 2) {
    let h = parseInt(parts[0]);
    const ampm = h >= 12 ? 'PM' : 'AM';
    h = h % 12 || 12;
    return `${h.toString().padStart(2, '0')}:${parts[1]} ${ampm}`;
  }
  return tStr;
}

function fMoney(num) {
  return '₹' + Number(num).toLocaleString('en-IN');
}

function badgeBs(status) {
  if (!status) return '—';
  const s = status.toLowerCase();
  let c = 'badge-pending';
  if (s === 'confirmed' || s === 'success' || s === 'active') c = 'badge-success';
  if (s === 'cancelled' || s === 'failed') c = 'badge-cancelled';
  return `<span class="badge ${c}">${status.toUpperCase()}</span>`;
}
