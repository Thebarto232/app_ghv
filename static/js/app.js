document.addEventListener('DOMContentLoaded', () => {

    // ── Sidebar toggle ──────────────────────────────────────
    const toggle = document.getElementById('menuToggle');
    const body = document.body;

    if (toggle) {
        toggle.addEventListener('click', () => {
            const sidebar = document.getElementById('sidebar');
            if (window.innerWidth <= 768) {
                sidebar.classList.toggle('open');
            } else {
                body.classList.toggle('sidebar-collapsed');
            }
        });
    }

    // ── Ctrl+K to focus search ──────────────────────────────
    const globalSearch = document.getElementById('globalSearch');
    document.addEventListener('keydown', (e) => {
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            if (globalSearch) globalSearch.focus();
        }
        if (e.key === 'Escape' && globalSearch) {
            globalSearch.blur();
            globalSearch.value = '';
            globalSearch.dispatchEvent(new Event('input'));
        }
    });

    // ── Table search / filter (only for NON-paginated tables) ──
    const tableFilter = document.getElementById('tableFilter');
    const hasPagination = document.querySelector('.paginated-table');
    if (tableFilter && !hasPagination) {
        tableFilter.addEventListener('input', () => {
            const term = tableFilter.value.toLowerCase();
            const rows = document.querySelectorAll('.data-table tbody tr');
            let visible = 0;
            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                const show = text.includes(term);
                row.style.display = show ? '' : 'none';
                if (show) visible++;
            });
            const info = document.getElementById('tableInfo');
            if (info) info.textContent = `${visible} registros`;
        });
    }

    // ── Global search → table filter dispatch ───────────────
    if (globalSearch && tableFilter && !hasPagination) {
        globalSearch.addEventListener('input', () => {
            tableFilter.value = globalSearch.value;
            tableFilter.dispatchEvent(new Event('input'));
        });
    }

    // ── Column sorting ──────────────────────────────────────
    document.querySelectorAll('.data-table th[data-sort]').forEach(th => {
        th.addEventListener('click', () => {
            const table = th.closest('table');
            const tbody = table.querySelector('tbody');
            const idx = Array.from(th.parentNode.children).indexOf(th);
            const rows = Array.from(tbody.querySelectorAll('tr:not(.depto-header-row)'));
            const asc = !th.classList.contains('sorted-asc');

            table.querySelectorAll('th').forEach(h => {
                h.classList.remove('sorted', 'sorted-asc', 'sorted-desc');
            });
            th.classList.add('sorted', asc ? 'sorted-asc' : 'sorted-desc');

            rows.sort((a, b) => {
                const aVal = a.children[idx]?.textContent.trim() || '';
                const bVal = b.children[idx]?.textContent.trim() || '';
                const aNum = parseFloat(aVal.replace(/,/g, ''));
                const bNum = parseFloat(bVal.replace(/,/g, ''));
                if (!isNaN(aNum) && !isNaN(bNum)) {
                    return asc ? aNum - bNum : bNum - aNum;
                }
                return asc ? aVal.localeCompare(bVal) : bVal.localeCompare(aVal);
            });

            rows.forEach(row => tbody.appendChild(row));
        });
    });

    // ── Modal close ─────────────────────────────────────────
    document.querySelectorAll('.modal-overlay').forEach(overlay => {
        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) overlay.classList.remove('active');
        });
    });
    document.querySelectorAll('[data-close-modal]').forEach(btn => {
        btn.addEventListener('click', () => {
            btn.closest('.modal-overlay').classList.remove('active');
        });
    });

    // ── Auto-dismiss alerts ─────────────────────────────────
    document.querySelectorAll('.alert').forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            alert.style.transform = 'translateY(-4px)';
            alert.style.transition = 'all .3s ease-out';
            setTimeout(() => alert.remove(), 300);
        }, 4000);
    });

    // ── Close sidebar on mobile when clicking outside ───────
    document.addEventListener('click', (e) => {
        const sidebar = document.getElementById('sidebar');
        if (window.innerWidth <= 768 && sidebar?.classList.contains('open')) {
            if (!sidebar.contains(e.target) && !toggle?.contains(e.target)) {
                sidebar.classList.remove('open');
            }
        }
    });

    // ── Active nav item scroll into view ────────────────────
    const activeNav = document.querySelector('.nav-item.active');
    if (activeNav) {
        activeNav.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
    }

    // ── Real-time engine init ────────────────────────────────
    RT.init();
});

/* ═══════════════════════════════════════════════════════════
   REAL-TIME ENGINE
   - Intercepts all modal forms → AJAX submit → no full reload
   - Auto-refreshes page content every 50 s
   - Toast notifications
   - Live indicator with timestamp
═══════════════════════════════════════════════════════════ */
const RT = {
    pollMs: 50000,          // auto-refresh interval
    _timer: null,
    _refreshing: false,

    /* ── Init ───────────────────────────────────────── */
    init() {
        this._bindModalForms();
        this._startPolling();
        this._setLiveTs();
    },

    /* ── Bind AJAX submit to every form inside a modal ─ */
    _bindModalForms() {
        document.addEventListener('submit', (e) => {
            const form = e.target;
            if (!form.closest('.modal-overlay')) return;
            // Skip forms that explicitly opt-out
            if (form.dataset.noAjax) return;
            e.preventDefault();
            this._submitForm(form);
        });
    },

    /* ── Submit a modal form via fetch ─────────────── */
    async _submitForm(form) {
        const btn = form.querySelector('[type="submit"]');
        const originalHTML = btn ? btn.innerHTML : '';
        if (btn) {
            btn.disabled = true;
            btn.innerHTML = '<span style="display:inline-flex;align-items:center;gap:6px"><span class="material-symbols-outlined" style="font-size:16px;animation:spin .7s linear infinite">progress_activity</span> Guardando…</span>';
        }

        try {
            const res = await fetch(form.action || window.location.href, {
                method: form.method || 'POST',
                body: new FormData(form),
                redirect: 'follow',
            });

            const html = await res.text();

            // Close the modal
            const overlay = form.closest('.modal-overlay');
            if (overlay) overlay.classList.remove('active');

            // Extract flash messages from returned HTML and show as toasts
            const doc = new DOMParser().parseFromString(html, 'text/html');
            doc.querySelectorAll('.alert').forEach(a => {
                const isError = a.classList.contains('alert-error');
                const msg = a.textContent.trim().replace(/^(check_circle|error|info)\s*/i, '');
                this.toast(msg, isError ? 'error' : 'success');
            });

            // Refresh page content with the returned HTML
            await this._applyContent(html);

        } catch (err) {
            this.toast('Error al guardar. Intenta de nuevo.', 'error');
        } finally {
            if (btn) {
                btn.disabled = false;
                btn.innerHTML = originalHTML;
            }
        }
    },

    /* ── Replace #pageContent with fresh HTML ───────── */
    async _applyContent(html) {
        const doc = new DOMParser().parseFromString(html, 'text/html');
        const newBody = doc.getElementById('pageContent');
        const curBody = document.getElementById('pageContent');

        if (newBody && curBody) {
            curBody.innerHTML = newBody.innerHTML;
            curBody.style.animation = 'none';
            curBody.offsetHeight; // reflow
            curBody.style.animation = 'fadeIn .3s ease-out';
            this._reinit(curBody);
        }

        this._setLiveTs();
        this._setLiveState('synced');
    },

    /* ── Auto-polling ────────────────────────────────── */
    _startPolling() {
        clearInterval(this._timer);
        this._timer = setInterval(() => this._autoRefresh(), this.pollMs);
    },

    async _autoRefresh() {
        // Skip if a modal or calendar detail panel is open, or already refreshing
        if (document.querySelector('.modal-overlay.active') ||
            document.querySelector('.cal-detail-overlay.active') ||
            this._refreshing) return;
        // No reemplazar contenido en páginas con calendario: el calendario se pinta por JS
        // y el HTML del servidor tiene calBody vacío; al reemplazar #pageContent quedaría en blanco.
        if (document.querySelector('.cal-container')) {
            this._setLiveTs();
            return;
        }
        this._refreshing = true;
        this._setLiveState('syncing');
        try {
            const res = await fetch(window.location.href, { cache: 'no-store' });
            if (res.ok) await this._applyContent(await res.text());
        } catch (_) {
            this._setLiveState('error');
        } finally {
            this._refreshing = false;
        }
    },

    /* ── Re-initialize dynamic components after DOM swap */
    _reinit(container) {
        // Count-up animations
        container.querySelectorAll('.count-up[data-target]').forEach(el => {
            const target = parseInt(el.dataset.target) || 0;
            if (!target) { el.textContent = '0'; return; }
            let cur = 0;
            const step = Math.max(1, Math.ceil(target / 40));
            clearInterval(el._t);
            el._t = setInterval(() => {
                cur = Math.min(cur + step, target);
                el.textContent = cur;
                if (cur >= target) clearInterval(el._t);
            }, 16);
        });

        // Re-bind modal close buttons
        container.querySelectorAll('[data-close-modal]').forEach(btn => {
            btn.addEventListener('click', () => {
                btn.closest('.modal-overlay')?.classList.remove('active');
            });
        });

        // Table filter (non-paginated)
        const tf = document.getElementById('tableFilter');
        const hasPag = container.querySelector('.paginated-table');
        if (tf && !hasPag) {
            tf.addEventListener('input', () => {
                const q = tf.value.toLowerCase();
                let vis = 0;
                container.querySelectorAll('.data-table tbody tr').forEach(r => {
                    const show = r.textContent.toLowerCase().includes(q);
                    r.style.display = show ? '' : 'none';
                    if (show) vis++;
                });
                const info = document.getElementById('tableInfo');
                if (info) info.textContent = `${vis} registros`;
            });
        }

        // Re-run any inline scripts in the new content
        container.querySelectorAll('script').forEach(s => {
            try { eval(s.textContent); } catch(_) {}
        });
    },

    /* ── Live indicator ──────────────────────────────── */
    _setLiveTs() {
        const el = document.getElementById('liveTs');
        if (el) el.textContent = new Date().toLocaleTimeString('es-CO', { hour: '2-digit', minute: '2-digit' });
    },

    _setLiveState(state) {
        const ind = document.getElementById('liveIndicator');
        if (!ind) return;
        ind.dataset.state = state;
    },

    /* ── Toast notifications ─────────────────────────── */
    toast(msg, type = 'success', durationMs = 4000) {
        const icons = { success: 'check_circle', error: 'error', info: 'info' };
        const container = document.getElementById('toastContainer');
        if (!container) return;

        const t = document.createElement('div');
        t.className = `toast toast-${type}`;
        t.innerHTML = `
            <span class="material-symbols-outlined toast-icon">${icons[type] || 'info'}</span>
            <span class="toast-msg">${msg}</span>
            <button class="toast-close" onclick="this.closest('.toast').remove()">
                <span class="material-symbols-outlined">close</span>
            </button>`;
        container.appendChild(t);

        // Animate in
        requestAnimationFrame(() => t.classList.add('toast-show'));

        // Auto-dismiss
        setTimeout(() => {
            t.classList.remove('toast-show');
            setTimeout(() => t.remove(), 350);
        }, durationMs);
    },
};

// Expose toast globally so calendar.js and other scripts can use it
window.toast = (msg, type, ms) => RT.toast(msg, type, ms);
