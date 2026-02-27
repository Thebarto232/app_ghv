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

    const calBody = document.getElementById('calBody');
    const calTitle = document.getElementById('calTitle');
    const detailOverlay = document.getElementById('detailOverlay');
    const detailName = document.getElementById('detailName');
    const detailBody = document.getElementById('detailBody');

    // ── Fetch data ──────────────────────────────────────────
    async function fetchData(year, month) {
        const res = await fetch(`${API_URL}?year=${year}&month=${month}`);
        calendarData = await res.json();
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

    // ── Render ───────────────────────────────────────────────
    function render() {
        updateTitle();
        if (currentView === 'month') renderMonth();
        else if (currentView === 'week') renderWeek();
        else renderDay();
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

    function getForDay(day) { return calendarData.filter(b => b.dia === day); }

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
                h += `<div class="cal-event" data-cedula="${b.id_cedula}">${b.apellidos_nombre}</div>`;
            });
            h += '</div>';
        }
        h += '</div></div>';
        calBody.innerHTML = h;
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
        for (let i = 0; i < 7; i++) {
            const d = new Date(start); d.setDate(d.getDate() + i);
            const items = calendarData.filter(b => b.dia === d.getDate() && d.getMonth() === currentDate.getMonth());
            h += '<div class="cal-week-col">';
            items.forEach(b => { h += `<div class="cal-event" data-cedula="${b.id_cedula}">${b.apellidos_nombre}</div>`; });
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
        calBody.innerHTML = h;
        attachEventListeners();
    }

    // ── DAY VIEW ────────────────────────────────────────────
    function renderDay() {
        const items = getForDay(currentDate.getDate());
        let h = '<div class="cal-day">';
        h += `<div class="cal-day-header"><div class="cal-time-gutter"></div><div class="cal-day-label">${DAYS_SHORT[currentDate.getDay()]}</div></div>`;
        h += '<div class="cal-day-events"><div class="cal-time-gutter"></div><div class="cal-day-event-col">';
        items.forEach(b => { h += `<div class="cal-event full-width" data-cedula="${b.id_cedula}">${b.apellidos_nombre}</div>`; });
        h += '</div></div><div class="cal-day-body"><div class="cal-time-gutter">';
        for (let hr = 6; hr <= 23; hr++) {
            const l = hr < 12 ? `${hr} AM` : hr === 12 ? '12 PM' : `${hr-12} PM`;
            h += `<div class="cal-time-slot">${l}</div>`;
        }
        h += '</div><div class="cal-day-col">';
        for (let hr = 6; hr <= 23; hr++) h += '<div class="cal-time-cell"></div>';
        h += '</div></div></div>';
        calBody.innerHTML = h;
        attachEventListeners();
    }

    // ── Event click → Detail panel ──────────────────────────
    function attachEventListeners() {
        document.querySelectorAll('.cal-event').forEach(el => {
            el.addEventListener('click', () => {
                const person = calendarData.find(b => b.id_cedula === el.dataset.cedula);
                if (person) showDetail(person);
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
                editCelular: p.celular,
                editCorreo: p.correo,
                editFechaNac: p.fecha_nacimiento || '',
                editEstado: p.estado,
                editTipoDoc: p.tipo_documento,
                editNivelEdu: p.nivel_educativo,
                editProfesion: p.profesion,
                editContacto: p.contacto_emergencia || '',
                editTelContacto: p.telefono_contacto || '',
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
            const formData = {};
            editForm.querySelectorAll('input[name], select[name]').forEach(el => {
                formData[el.name] = el.value;
            });
            const res = await fetch(`/api/empleado/${id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData),
            });
            if (res.ok) {
                editModal.classList.remove('active');
                detailOverlay.classList.remove('active');
                fetchData(currentDate.getFullYear(), currentDate.getMonth() + 1);
            }
        });
    }

    // ── Init ────────────────────────────────────────────────
    fetchData(currentDate.getFullYear(), currentDate.getMonth() + 1);
});
