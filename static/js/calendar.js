document.addEventListener('DOMContentLoaded', () => {
    const MONTHS = [
        'enero','febrero','marzo','abril','mayo','junio',
        'julio','agosto','septiembre','octubre','noviembre','diciembre'
    ];
    const DAYS_SHORT = ['do','lu','ma','mi','ju','vi','sá'];
    const DAYS_FULL = ['domingo','lunes','martes','miércoles','jueves','viernes','sábado'];

    // ── Read config from data attributes on cal-container ────
    const container = document.querySelector('.cal-container');
    if (!container) return;

    const API_URL = container.dataset.api || '/api/cumpleanos';
    const DETAIL_FIELDS_RAW = container.dataset.fields || '';
    const EDIT_ENABLED = container.dataset.edit !== 'false';

    let detailFieldDefs = [];
    if (DETAIL_FIELDS_RAW) {
        try { detailFieldDefs = JSON.parse(DETAIL_FIELDS_RAW); } catch(e) {}
    }

    let currentView = 'month';
    let currentDate = new Date();
    let calendarData = [];
    let selectedPerson = null;
    let searchQuery = ''; // filtro del buscador global (Aniversario / Cumpleaños)

    const calBody = document.getElementById('calBody');
    const calTitle = document.getElementById('calTitle');
    const detailOverlay = document.getElementById('detailOverlay');
    const detailName = document.getElementById('detailName');
    const detailBody = document.getElementById('detailBody');

    if (!calBody || !calTitle) {
        console.error('Calendario: faltan elementos calBody o calTitle en el DOM');
        if (container) container.innerHTML = '<p class="cal-error-msg">No se pudo cargar el calendario. Recargue la página.</p>';
        return;
    }

    let fetchAbort = null; // para cancelar peticiones anteriores y evitar pantalla en blanco por respuestas desordenadas

    // ── Fetch data ──────────────────────────────────────────
    async function fetchData(year, month) {
        if (fetchAbort) fetchAbort.abort();
        fetchAbort = new AbortController();
        const signal = fetchAbort.signal;
        try {
            const res = await fetch(`${API_URL}?year=${year}&month=${month}`, { signal });
            if (res.status === 401) {
                window.location.href = '/login';
                return;
            }
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            const data = await res.json();
            calendarData = Array.isArray(data) ? data : [];
        } catch(e) {
            if (e.name === 'AbortError') return;
            console.error('Error cargando calendario:', e);
            calendarData = [];
        }
        fetchAbort = null;
        render();
    }

    // ── Navigation ──────────────────────────────────────────
    document.getElementById('calPrev').addEventListener('click', () => navigate(-1));
    document.getElementById('calNext').addEventListener('click', () => navigate(1));
    document.getElementById('calToday').addEventListener('click', () => {
        currentDate = new Date();
        fetchData(currentDate.getFullYear(), currentDate.getMonth() + 1);
    });

    function navigate(dir) {
        if (currentView === 'month') currentDate.setMonth(currentDate.getMonth() + dir);
        else if (currentView === 'week') currentDate.setDate(currentDate.getDate() + dir * 7);
        else currentDate.setDate(currentDate.getDate() + dir);
        fetchData(currentDate.getFullYear(), currentDate.getMonth() + 1);
    }

    // ── View buttons ────────────────────────────────────────
    document.querySelectorAll('.cal-view-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.cal-view-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentView = btn.dataset.view;
            render();
        });
    });

    // ── Buscador global: filtrar calendario (Aniversario / Cumpleaños) ──
    const globalSearch = document.getElementById('globalSearch');
    if (globalSearch) {
        globalSearch.addEventListener('input', () => {
            searchQuery = (globalSearch.value || '').trim().toLowerCase();
            render();
        });
        globalSearch.addEventListener('keyup', (e) => {
            if (e.key === 'Escape') {
                globalSearch.value = '';
                searchQuery = '';
                render();
            }
        });
    }

    /** Datos del mes filtrados por el texto del buscador (nombre, área, departamento). */
    function getFilteredData() {
        if (!searchQuery) return calendarData;
        const q = searchQuery;
        return calendarData.filter(b => {
            const nombre = (b.apellidos_nombre || '').toLowerCase();
            const area = (b.area || '').toLowerCase();
            const depto = (b.departamento || '').toLowerCase();
            return nombre.includes(q) || area.includes(q) || depto.includes(q);
        });
    }

    // ── Render ───────────────────────────────────────────────
    function render() {
        try {
            updateTitle();
            if (currentView === 'month') renderMonth();
            else if (currentView === 'week') renderWeek();
            else renderDay();
            if (container.dataset.showStats === 'true') updateMiniStats();
        } catch (err) {
            console.error('Error al dibujar calendario:', err);
            if (calBody) calBody.innerHTML = '<div class="cal-error-msg">Error al mostrar el calendario. <button type="button" class="btn btn-outline btn-sm" onclick="location.reload()">Recargar</button></div>';
        }
    }

    // ── Mini estadísticas para Bienestar (Aniversario Laboral) ──
    function updateMiniStats() {
        const wrap = document.getElementById('calMiniStatsWrap');
        const box = document.getElementById('calMiniStats');
        if (!wrap || !box) return;
        const dataForStats = searchQuery ? getFilteredData() : calendarData;
        const total = dataForStats.length;
        if (total === 0) {
            wrap.classList.remove('has-stats');
            box.innerHTML = '<p class="cal-mini-stats-empty">' + (searchQuery ? 'No hay resultados para "' + escapeHtml(searchQuery) + '".' : 'No hay aniversarios este mes.') + '</p>';
            return;
        }
        const byDay = {};
        const byArea = {};
        dataForStats.forEach(b => {
            const d = b && (b.dia != null) ? Number(b.dia) : null;
            if (d != null && !isNaN(d)) byDay[d] = (byDay[d] || 0) + 1;
            const area = (b && (b.area || b.departamento) || 'Sin área').toString().trim() || 'Sin área';
            byArea[area] = (byArea[area] || 0) + 1;
        });
        const daysInOrder = Object.keys(byDay).map(Number).sort((a, b) => a - b);
        let html = '<div class="cal-mini-stats-header">';
        html += '<span class="material-symbols-outlined cal-mini-stats-header-icon">celebration</span>';
        html += '<span>Resumen para Bienestar</span>';
        html += '</div>';
        html += '<div class="cal-mini-stats-grid">';
        html += '<div class="cal-mini-stats-card cal-mini-stats-card-main">';
        html += '<span class="material-symbols-outlined cal-mini-stats-card-icon">cake</span>';
        html += '<span class="cal-mini-stats-value">' + total + '</span><span class="cal-mini-stats-label">Aniversarios este mes</span></div>';
        html += '<div class="cal-mini-stats-card cal-mini-stats-card-days">';
        html += '<span class="material-symbols-outlined cal-mini-stats-card-icon">event</span>';
        html += '<span class="cal-mini-stats-value">' + daysInOrder.length + '</span><span class="cal-mini-stats-label">Días con eventos</span></div>';
        html += '</div>';
        html += '<div class="cal-mini-stats-section cal-mini-stats-section-day">';
        html += '<strong><span class="material-symbols-outlined cal-mini-stats-section-icon">calendar_today</span> Por día</strong><ul class="cal-mini-stats-list">';
        daysInOrder.forEach(day => {
            html += '<li><span class="cal-mini-stats-day-badge">' + String(day).padStart(2, '0') + '</span> <strong>' + byDay[day] + '</strong> persona' + (byDay[day] !== 1 ? 's' : '') + '</li>';
        });
        html += '</ul></div>';
        const areasOrder = Object.keys(byArea).sort((a, b) => byArea[b] - byArea[a]);
        html += '<div class="cal-mini-stats-section cal-mini-stats-section-area">';
        html += '<strong><span class="material-symbols-outlined cal-mini-stats-section-icon">business</span> Por área / departamento</strong><ul class="cal-mini-stats-list">';
        areasOrder.forEach(area => {
            html += '<li><span class="cal-mini-stats-area-name">' + escapeHtml(area) + '</span> <span class="cal-mini-stats-count-pill">' + byArea[area] + '</span></li>';
        });
        html += '</ul></div>';
        box.innerHTML = html;
        wrap.classList.add('has-stats');
    }
    function escapeHtml(s) {
        const div = document.createElement('div');
        div.textContent = s;
        return div.innerHTML;
    }

    function updateTitle() {
        if (currentView === 'month') {
            calTitle.textContent = `${MONTHS[currentDate.getMonth()]} ${currentDate.getFullYear()}`;
        } else if (currentView === 'week') {
            const start = getWeekStart(currentDate);
            const end = new Date(start); end.setDate(end.getDate() + 6);
            calTitle.textContent = `${fmtShort(start)} — ${fmtShort(end)}`;
        } else {
            const d = currentDate;
            calTitle.textContent = `${DAYS_FULL[d.getDay()]} ${MONTHS[d.getMonth()].substring(0,3)}. ${String(d.getDate()).padStart(2,'0')}`;
        }
    }

    function fmtShort(d) { return `${MONTHS[d.getMonth()].substring(0,3)}. ${d.getDate()}`; }

    function getWeekStart(d) {
        const c = new Date(d); c.setDate(c.getDate() - c.getDay()); return c;
    }

    function getForDay(day) { return getFilteredData().filter(b => b.dia === day); }

    // ── MONTH VIEW ──────────────────────────────────────────
    function renderMonth() {
        const year = currentDate.getFullYear(), month = currentDate.getMonth();
        const firstDay = new Date(year, month, 1).getDay();
        const daysInMonth = new Date(year, month + 1, 0).getDate();
        const today = new Date();

        let h = '<div class="cal-month"><div class="cal-month-header">';
        DAYS_SHORT.forEach(d => { h += `<div class="cal-month-day-label">${d}</div>`; });
        h += '</div><div class="cal-month-grid">';

        for (let i = 0; i < firstDay; i++) h += '<div class="cal-month-cell empty"></div>';

        for (let day = 1; day <= daysInMonth; day++) {
            const isToday = today.getFullYear() === year && today.getMonth() === month && today.getDate() === day;
            const items = getForDay(day);
            h += `<div class="cal-month-cell${isToday ? ' today' : ''}">`;
            h += `<div class="cal-month-date">${String(day).padStart(2,'0')}</div>`;
            items.forEach(b => {
                const fullName = (b.apellidos_nombre || '').replace(/"/g, '&quot;');
                h += `<div class="cal-event" data-cedula="${b.id_cedula}" title="${fullName} — Clic para ver detalle" tabindex="0" role="button">${b.apellidos_nombre}</div>`;
            });
            h += '</div>';
        }
        h += '</div></div>';
        if (calBody) calBody.innerHTML = h;
        attachEventListeners();
    }

    // ── WEEK VIEW ───────────────────────────────────────────
    function renderWeek() {
        const start = getWeekStart(currentDate);
        const today = new Date();
        let h = '<div class="cal-week"><div class="cal-week-header"><div class="cal-time-gutter"></div>';
        for (let i = 0; i < 7; i++) {
            const d = new Date(start); d.setDate(d.getDate() + i);
            const isToday = d.toDateString() === today.toDateString();
            h += `<div class="cal-week-day-label${isToday ? ' today' : ''}">${DAYS_SHORT[i]}<br><span>${String(d.getDate()).padStart(2,'0')}</span></div>`;
        }
        h += '</div><div class="cal-week-events"><div class="cal-time-gutter"></div>';
        const filtered = getFilteredData();
        for (let i = 0; i < 7; i++) {
            const d = new Date(start); d.setDate(d.getDate() + i);
            const items = filtered.filter(b => b.dia === d.getDate() && d.getMonth() === currentDate.getMonth());
            h += '<div class="cal-week-col">';
            items.forEach(b => {
                const fullName = (b.apellidos_nombre || '').replace(/"/g, '&quot;');
                h += `<div class="cal-event" data-cedula="${b.id_cedula}" title="${fullName} — Clic para ver detalle" tabindex="0" role="button">${b.apellidos_nombre}</div>`;
            });
            h += '</div>';
        }
        h += '</div><div class="cal-week-body"><div class="cal-time-gutter">';
        for (let hr = 6; hr <= 23; hr++) {
            const l = hr < 12 ? `${hr} AM` : hr === 12 ? '12 PM' : `${hr-12} PM`;
            h += `<div class="cal-time-slot">${l}</div>`;
        }
        h += '</div>';
        for (let i = 0; i < 7; i++) { h += '<div class="cal-week-col">'; for (let hr = 6; hr <= 23; hr++) h += '<div class="cal-time-cell"></div>'; h += '</div>'; }
        h += '</div></div>';
        if (calBody) calBody.innerHTML = h;
        attachEventListeners();
    }

    // ── DAY VIEW ────────────────────────────────────────────
    function renderDay() {
        const items = getForDay(currentDate.getDate());
        let h = '<div class="cal-day">';
        h += `<div class="cal-day-header"><div class="cal-time-gutter"></div><div class="cal-day-label">${DAYS_SHORT[currentDate.getDay()]}</div></div>`;
        h += '<div class="cal-day-events"><div class="cal-time-gutter"></div><div class="cal-day-event-col">';
        items.forEach(b => {
            const fullName = (b.apellidos_nombre || '').replace(/"/g, '&quot;');
            h += `<div class="cal-event full-width" data-cedula="${b.id_cedula}" title="${fullName} — Clic para ver detalle" tabindex="0" role="button">${b.apellidos_nombre}</div>`;
        });
        h += '</div></div><div class="cal-day-body"><div class="cal-time-gutter">';
        for (let hr = 6; hr <= 23; hr++) {
            const l = hr < 12 ? `${hr} AM` : hr === 12 ? '12 PM' : `${hr-12} PM`;
            h += `<div class="cal-time-slot">${l}</div>`;
        }
        h += '</div><div class="cal-day-col">';
        for (let hr = 6; hr <= 23; hr++) h += '<div class="cal-time-cell"></div>';
        h += '</div></div></div>';
        if (calBody) calBody.innerHTML = h;
        attachEventListeners();
    }

    // ── Event click → Detail panel (interactivo) ─────────────
    function openEventDetail(el) {
        const person = calendarData.find(b => b.id_cedula === el.dataset.cedula);
        if (person) showDetail(person);
    }

    function attachEventListeners() {
        document.querySelectorAll('.cal-event').forEach(el => {
            el.addEventListener('click', (e) => { e.preventDefault(); openEventDetail(el); });
            el.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); openEventDetail(el); }
            });
        });
    }

    function showDetail(person) {
        selectedPerson = person;
        detailName.textContent = person.apellidos_nombre;

        let html = '';
        detailFieldDefs.forEach(f => {
            const val = person[f.key] ?? '';
            html += `<div class="cal-detail-field">
                <label>${f.label}</label>
                <span>${val || '—'}</span>
            </div>`;
        });
        detailBody.innerHTML = html;
        detailOverlay.classList.add('active');
    }

    // ── Close detail ────────────────────────────────────────
    document.getElementById('btnCloseDetail').addEventListener('click', closeDetail);
    detailOverlay.addEventListener('click', (e) => { if (e.target === detailOverlay) closeDetail(); });
    function closeDetail() { detailOverlay.classList.remove('active'); selectedPerson = null; }

    // ── Edit ────────────────────────────────────────────────
    const btnEdit = document.getElementById('btnEdit');
    const editModal = document.getElementById('editModal');
    const editForm = document.getElementById('editForm');

    function normalizeDisplayValue(val) {
        if (val == null || val === '') return '';
        const s = String(val).trim();
        if (s.endsWith('.0') && /^\d+\.0$/.test(s)) return s.slice(0, -2);
        return s;
    }

    if (btnEdit && editModal && EDIT_ENABLED) {
        btnEdit.addEventListener('click', () => {
            if (!selectedPerson) return;
            const p = selectedPerson;
            const fields = {
                editId: p.id_cedula,
                editCedula: p.id_cedula,
                editNombre: p.apellidos_nombre,
                editDepto: p.departamento,
                editArea: p.area,
                editSexo: p.sexo,
                editCelular: normalizeDisplayValue(p.celular),
                editCorreo: p.correo,
                editFechaNac: p.fecha_nacimiento || '',
                editEstado: p.estado,
                editTipoDoc: p.tipo_documento,
                editNivelEdu: p.nivel_educativo,
                editProfesion: p.profesion,
                editContacto: p.contacto_emergencia || '',
                editTelContacto: normalizeDisplayValue(p.telefono_contacto),
                editParentezco: p.parentezco || '',
            };
            Object.entries(fields).forEach(([id, val]) => {
                const el = document.getElementById(id);
                if (el) el.value = val || '';
            });
            editModal.classList.add('active');
        });
    }

    if (editForm) {
        editForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const id = document.getElementById('editId').value;
            const saveBtn = editForm.querySelector('button[type="submit"]');
            const formData = {};
            editForm.querySelectorAll('input[name], select[name]').forEach(el => {
                formData[el.name] = el.value;
            });

            // Loading state
            if (saveBtn) { saveBtn.disabled = true; saveBtn.textContent = 'Guardando...'; }

            try {
                const res = await fetch(`/api/empleado/${id}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(formData),
                });

                if (res.ok) {
                    editModal.classList.remove('active');
                    detailOverlay.classList.remove('active');
                    fetchData(currentDate.getFullYear(), currentDate.getMonth() + 1);
                    if (window.toast) window.toast('Empleado actualizado correctamente', 'success');
                } else {
                    const err = await res.json().catch(() => ({}));
                    const msg = err.error || `Error al guardar (${res.status})`;
                    if (window.toast) window.toast(msg, 'error');
                    else alert(msg);
                }
            } catch (err) {
                const msg = 'Error de conexión al guardar';
                if (window.toast) window.toast(msg, 'error');
                else alert(msg);
            } finally {
                if (saveBtn) { saveBtn.disabled = false; saveBtn.textContent = 'Guardar'; }
            }
        });
    }

    // ── Init ────────────────────────────────────────────────
    fetchData(currentDate.getFullYear(), currentDate.getMonth() + 1);
});
