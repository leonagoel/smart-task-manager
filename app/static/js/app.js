/* ── State ─────────────────────────────────────────────────────────── */
let tasks = [];
let editingId = null;
let activeStatus = '';
let activePriority = '';
let searchQuery = '';

/* ── WebSocket ─────────────────────────────────────────────────────── */
const socket = io({ withCredentials: true });
const wsDot   = document.getElementById('ws-dot');
const wsLabel = document.getElementById('ws-label');

socket.on('connect', () => {
  wsDot.classList.add('connected');
  wsLabel.textContent = 'Live';
  toast('Live updates connected', 'success');
});
socket.on('disconnect', () => {
  wsDot.classList.remove('connected');
  wsLabel.textContent = 'Offline';
  toast('Disconnected from live updates', 'error');
});
socket.on('task_created', t  => { toast(`Task added: "${t.title}"`, 'success'); loadTasks(); loadAnalytics(); });
socket.on('task_updated', t  => { toast(`Task updated: "${t.title}"`, 'success'); loadTasks(); loadAnalytics(); });
socket.on('task_deleted', () => { toast('Task deleted', 'success'); loadTasks(); loadAnalytics(); });

/* ── Toast ─────────────────────────────────────────────────────────── */
let toastTimer;
function toast(msg, type = 'info') {
  const el  = document.getElementById('toast');
  const msg_ = document.getElementById('toast-msg');
  msg_.textContent = msg;
  el.className = `toast show ${type}`;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => el.classList.remove('show'), 3500);
}

/* ── Navigation ────────────────────────────────────────────────────── */
function switchView(name, btn) {
  document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(b => b.classList.remove('active'));
  document.getElementById('view-' + name).classList.add('active');
  btn.classList.add('active');
  if (name === 'analytics') loadAnalytics();
}

/* ── Logout ────────────────────────────────────────────────────────── */
document.getElementById('logout-btn').addEventListener('click', async () => {
  await fetch('/auth/api/logout', { method: 'POST', credentials: 'include' });
  window.location.href = '/auth/login';
});

/* ── Filters ───────────────────────────────────────────────────────── */
document.querySelectorAll('.filter-chip').forEach(chip => {
  chip.addEventListener('click', () => {
    document.querySelectorAll('.filter-chip').forEach(c => c.classList.remove('active'));
    chip.classList.add('active');
    activeStatus = chip.dataset.status;
    renderTasks();
  });
});
document.getElementById('priority-filter').addEventListener('change', e => {
  activePriority = e.target.value; renderTasks();
});
document.getElementById('search-input').addEventListener('input', e => {
  searchQuery = e.target.value.toLowerCase(); renderTasks();
});

/* ── Load tasks ────────────────────────────────────────────────────── */
async function loadTasks() {
  try {
    const res = await fetch('/api/tasks', { credentials: 'include' });
    if (res.redirected || res.status === 401) { window.location.href = '/auth/login'; return; }
    if (!res.ok) { renderEmpty(); return; }
    tasks = await res.json();
    renderTasks();
    updateQuickStats();
  } catch (e) { console.error(e); }
}

function updateQuickStats() {
  const total = tasks.length;
  const done  = tasks.filter(t => t.status === 'done').length;
  const prog  = tasks.filter(t => t.status === 'in_progress').length;
  const pend  = tasks.filter(t => t.status === 'pending').length;
  document.getElementById('qs-total').textContent = total;
  document.getElementById('qs-done').textContent  = done;
  document.getElementById('qs-prog').textContent  = prog;
  document.getElementById('qs-pend').textContent  = pend;
  document.getElementById('nav-count').textContent = total;
}

/* ── Render tasks ──────────────────────────────────────────────────── */
function renderTasks() {
  let list = tasks;
  if (activeStatus)   list = list.filter(t => t.status   === activeStatus);
  if (activePriority) list = list.filter(t => t.priority === activePriority);
  if (searchQuery)    list = list.filter(t =>
    t.title.toLowerCase().includes(searchQuery) ||
    (t.description || '').toLowerCase().includes(searchQuery)
  );

  const sub = document.getElementById('task-subtitle');
  sub.textContent = list.length
    ? `${list.length} task${list.length !== 1 ? 's' : ''}${activeStatus ? ' · ' + activeStatus.replace('_',' ') : ''}`
    : 'No tasks match your filters';

  const el = document.getElementById('task-list');
  if (!list.length) { renderEmpty(); return; }

  el.innerHTML = list.map(t => `
    <div class="task-card priority-${t.priority} ${t.status === 'done' ? 'done-card' : ''}" data-id="${t.id}">
      <div class="task-check ${t.status === 'done' ? 'checked' : ''}"
           onclick="toggleDone(${t.id},'${t.status}')" title="${t.status === 'done' ? 'Mark pending' : 'Mark done'}">
        ${t.status === 'done' ? '✓' : ''}
      </div>
      <div class="task-body">
        <div class="task-title ${t.status === 'done' ? 'done-text' : ''}">${esc(t.title)}</div>
        ${t.description ? `<div class="task-desc">${esc(t.description)}</div>` : ''}
        <div class="task-meta">
          <span class="badge badge-priority-${t.priority}">${t.priority}</span>
          <span class="badge badge-status-${t.status}">${t.status.replace('_',' ')}</span>
          <span class="task-date">${fmtDate(t.created_at)}</span>
        </div>
      </div>
      <div class="task-actions">
        <button class="icon-btn edit"   onclick="openEdit(${t.id})"  title="Edit">✎</button>
        <button class="icon-btn delete" onclick="delTask(${t.id})"   title="Delete">✕</button>
      </div>
    </div>`).join('');
}

function renderEmpty() {
  document.getElementById('task-list').innerHTML = `
    <div class="empty-state">
      <div class="empty-icon">${tasks.length ? '🔍' : '📋'}</div>
      <h3>${tasks.length ? 'No matching tasks' : 'No tasks yet'}</h3>
      <p>${tasks.length ? 'Try changing your filters.' : 'Click <strong>+ Add Task</strong> to get started!'}</p>
    </div>`;
}

/* ── CRUD ──────────────────────────────────────────────────────────── */
async function toggleDone(id, status) {
  const newStatus = status === 'done' ? 'pending' : 'done';
  await fetch(`/api/tasks/${id}`, {
    method: 'PUT', credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ status: newStatus })
  });
}

async function delTask(id) {
  if (!confirm('Delete this task?')) return;
  const res = await fetch(`/api/tasks/${id}`, { method: 'DELETE', credentials: 'include' });
  if (!res.ok) toast('Delete failed', 'error');
}

function openEdit(id) {
  const t = tasks.find(t => t.id === id);
  if (t) openModal(t);
}

/* ── Modal ─────────────────────────────────────────────────────────── */
function openModal(task = null) {
  editingId = task ? task.id : null;
  document.getElementById('modal-title').textContent = task ? 'Edit Task' : 'New Task';
  document.getElementById('modal-sub').textContent   = task ? 'Update task details' : 'Fill in the details below';
  document.getElementById('modal-save-btn').textContent = task ? 'Update Task' : 'Save Task';
  document.getElementById('t-title').value    = task ? task.title : '';
  document.getElementById('t-desc').value     = task ? (task.description || '') : '';
  document.getElementById('t-priority').value = task ? task.priority : 'medium';
  document.getElementById('t-status').value   = task ? task.status   : 'pending';
  document.getElementById('modal-overlay').style.display = 'flex';
  setTimeout(() => document.getElementById('t-title').focus(), 50);
}

function closeModal() {
  document.getElementById('modal-overlay').style.display = 'none';
  editingId = null;
}

document.getElementById('open-modal-btn').addEventListener('click', () => openModal());
document.getElementById('modal-close-btn').addEventListener('click', closeModal);
document.getElementById('modal-cancel-btn').addEventListener('click', closeModal);
document.getElementById('modal-overlay').addEventListener('click', e => {
  if (e.target === document.getElementById('modal-overlay')) closeModal();
});

document.getElementById('modal-save-btn').addEventListener('click', async () => {
  const title = document.getElementById('t-title').value.trim();
  if (!title) { toast('Title is required', 'error'); return; }

  const payload = {
    title,
    description: document.getElementById('t-desc').value.trim(),
    priority:    document.getElementById('t-priority').value,
    status:      document.getElementById('t-status').value,
  };

  const res = await fetch(editingId ? `/api/tasks/${editingId}` : '/api/tasks', {
    method: editingId ? 'PUT' : 'POST',
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });

  if (res.ok) { closeModal(); }
  else { const d = await res.json(); toast(d.error || 'Save failed', 'error'); }
});

/* ── Analytics ─────────────────────────────────────────────────────── */
async function loadAnalytics() {
  try {
    const res = await fetch('/api/analytics', { credentials: 'include' });
    if (!res.ok) return;
    renderAnalytics(await res.json());
  } catch (e) { console.error(e); }
}

function renderAnalytics(d) {
  document.getElementById('stat-total').textContent = d.total;
  document.getElementById('stat-done').textContent  = d.completed;
  document.getElementById('stat-prog').textContent  = d.in_progress;
  document.getElementById('stat-pend').textContent  = d.pending;

  // Ring
  const circ = 314;
  const filled = (d.completion_pct / 100) * circ;
  document.getElementById('ring-fill').setAttribute('stroke-dasharray', `${filled.toFixed(1)} ${circ}`);
  document.getElementById('ring-pct').textContent = `${d.completion_pct}%`;

  // Priority bars
  const maxP = Math.max(d.by_priority.high, d.by_priority.medium, d.by_priority.low, 1);
  setBar('bar-high',   'val-high',   d.by_priority.high,   maxP);
  setBar('bar-medium', 'val-medium', d.by_priority.medium, maxP);
  setBar('bar-low',    'val-low',    d.by_priority.low,    maxP);

  // Status bars
  const maxS = Math.max(d.by_status.done, d.by_status.in_progress, d.by_status.pending, 1);
  setBar('bar-done', 'val-done', d.by_status.done,        maxS);
  setBar('bar-ip',   'val-ip',   d.by_status.in_progress, maxS);
  setBar('bar-pe',   'val-pe',   d.by_status.pending,     maxS);

  // Trend chart
  const tc = document.getElementById('trend-chart');
  if (!d.daily_counts.length) { tc.innerHTML = '<span style="color:var(--text3);font-size:12px">No data yet</span>'; return; }
  const maxC = Math.max(...d.daily_counts.map(r => r.count), 1);
  tc.innerHTML = d.daily_counts.map(r => {
    const h = Math.max(Math.round((r.count / maxC) * 100), 4);
    return `<div class="trend-bar" style="height:${h}%" data-tip="${r.date}: ${r.count} task${r.count!==1?'s':''}"></div>`;
  }).join('');
}

function setBar(fillId, valId, val, max) {
  document.getElementById(fillId).style.width = `${Math.round((val / max) * 100)}%`;
  document.getElementById(valId).textContent  = val;
}

document.getElementById('refresh-analytics-btn').addEventListener('click', loadAnalytics);

/* ── Helpers ───────────────────────────────────────────────────────── */
function esc(s) {
  return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}
function fmtDate(iso) {
  if (!iso) return '';
  return new Date(iso).toLocaleDateString('en-IN', { day:'numeric', month:'short', year:'numeric' });
}

/* ── Init ──────────────────────────────────────────────────────────── */
loadTasks();