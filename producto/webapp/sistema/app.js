(() => {
  const STORAGE_KEY = 'vida_en_orden_sistema30_v1';
  const TEST_STORAGE_KEY = 'vida_en_orden_test_v1';
  const CONTENT_URL = '../../sistema-30-dias/contenido.json';

  const ACCESS_KEYS = {
    esencial: ['ESENCIAL-2026', 'VIDA-ESENCIAL', 'ORDEN99', 'ESENCIAL99'],
    completa: ['COMPLETA-2026', 'VIDA-COMPLETA', 'ORDEN199', 'VIDA30', 'COMPLETA199']
  };

  const DIMS = [
    { id: 'mente', name: 'Mente', color: '#4A5D4E' },
    { id: 'tiempo', name: 'Tiempo', color: '#C67D5B' },
    { id: 'energia', name: 'Energía', color: '#6E8572' },
    { id: 'dinero', name: 'Dinero', color: '#9B7B54' },
    { id: 'habitos', name: 'Hábitos', color: '#5F6F7E' }
  ];

  function todayIso() {
    const d = new Date();
    const p = n => (n < 10 ? '0' + n : '' + n);
    return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())}`;
  }

  function importDay1FromTest() {
    const fallback = { mente: 2.5, tiempo: 2.5, energia: 2.5, dinero: 2.5, habitos: 2.5 };
    try {
      const raw = localStorage.getItem(TEST_STORAGE_KEY);
      if (!raw) return fallback;
      const parsed = JSON.parse(raw);
      if (!parsed || !parsed.answers) return fallback;
      const prefixMap = { mente: 'm', tiempo: 't', energia: 'e', dinero: 'd', habitos: 'h' };
      const out = {};
      DIMS.forEach(dim => {
        const pre = prefixMap[dim.id];
        const vals = [1, 2, 3, 4].map(i => Number(parsed.answers[pre + i]) || 0).filter(v => v > 0);
        out[dim.id] = vals.length ? Number((vals.reduce((a, b) => a + b, 0) / vals.length).toFixed(1)) : 2.5;
      });
      return out;
    } catch (e) {
      return fallback;
    }
  }

  function defaultState() {
    const d1 = importDay1FromTest();
    return {
      tier: 'demo', // 'demo' | 'esencial' | 'completa'
      seenWelcome: false,
      activeWeek: 1,
      selectedDay: 1,
      days: {}, // { "1": { done, microDone, expenseDone, tpuText, tpuDone, notes, completedAt } }
      sos: {
        goodThing: '',
        rescues: 0,
        lastRescueDate: null
      },
      dump: {
        text: '',
        top1: '',
        top2: ''
      },
      tripleAncla: {
        a1: '',
        a2: '',
        a3: '',
        checksByDate: {} // { "2026-11-27": [false, false, false] }
      },
      diaBase: {
        tpu: '',
        care: '',
        center: '',
        budget: '',
        vida: ''
      },
      expenses: [], // [{ id, date, desc, amount, cat: 'N'|'U'|'I' }]
      compare: {
        day1: d1,
        day30: { ...d1 }
      }
    };
  }

  function loadState() {
    const def = defaultState();
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (!raw) return def;
      const parsed = JSON.parse(raw);
      return {
        ...def,
        ...parsed,
        days: parsed.days || {},
        sos: { ...def.sos, ...(parsed.sos || {}) },
        dump: { ...def.dump, ...(parsed.dump || {}) },
        tripleAncla: {
          ...def.tripleAncla,
          ...(parsed.tripleAncla || {}),
          checksByDate: (parsed.tripleAncla && parsed.tripleAncla.checksByDate) || {}
        },
        diaBase: { ...def.diaBase, ...(parsed.diaBase || {}) },
        expenses: Array.isArray(parsed.expenses) ? parsed.expenses : [],
        compare: {
          day1: { ...def.compare.day1, ...((parsed.compare && parsed.compare.day1) || {}) },
          day30: { ...def.compare.day30, ...((parsed.compare && parsed.compare.day30) || {}) }
        }
      };
    } catch (e) {
      return def;
    }
  }

  let state = loadState();
  let contentData = null;
  let allDays = [];
  let selectedExpCat = 'N';

  function saveState() {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
    } catch (e) {
      // Ignorar si almacenamiento privado está bloqueado
    }
  }

  function esc(str) {
    return String(str || '')
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  // Toast
  const toastEl = document.getElementById('toast');
  let toastTimer = null;
  function showToast(msg) {
    toastEl.textContent = msg;
    toastEl.hidden = false;
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => { toastEl.hidden = true; }, 2800);
  }

  // Permisos según nivel
  function canAccessDay(dayNum) {
    if (state.tier === 'completa') return true;
    if (state.tier === 'esencial') return dayNum <= 7;
    return dayNum === 1;
  }

  function canAccessSos() {
    return state.tier === 'esencial' || state.tier === 'completa';
  }

  function canAccessFullTools() {
    return state.tier === 'completa';
  }

  function resolveKey(rawKey) {
    const clean = String(rawKey || '').trim().toUpperCase().replace(/\s+/g, '');
    if (ACCESS_KEYS.completa.includes(clean)) return 'completa';
    if (ACCESS_KEYS.esencial.includes(clean)) return 'esencial';
    return null;
  }

  function checkUrlKey() {
    try {
      const params = new URLSearchParams(window.location.search);
      const urlKey = params.get('clave') || params.get('key');
      if (urlKey) {
        const tier = resolveKey(urlKey);
        if (tier) {
          state.tier = tier;
          saveState();
          params.delete('clave');
          params.delete('key');
          const cleanUrl = window.location.pathname + (params.toString() ? '?' + params.toString() : '');
          history.replaceState(null, '', cleanUrl);
          showToast(tier === 'completa' ? '✓ Edición Completa (30 Días) activada' : '✓ Edición Esencial (Semana 1 + SOS) activada');
        }
      }
    } catch (e) {
      // Ignorar
    }
  }

  // Lock card reusable
  function buildLockHtml(title, desc, requiredTier) {
    const badge = requiredTier === 'esencial'
      ? 'Disponible desde Edición Esencial ($99 MXN)'
      : 'Exclusivo de Edición Completa ($199 MXN)';
    return `
      <div class="lock-card">
        <div class="lock-icon">🔒</div>
        <p class="eyebrow" style="color: var(--accent);">${badge}</p>
        <h3>${esc(title)}</h3>
        <p>${esc(desc)}</p>
        <div class="btn-row" style="justify-content: center;">
          <button type="button" class="btn btn-primary js-open-modal">Ingresar clave de acceso</button>
          <a href="../index.html#bridge-heading" class="btn btn-secondary">Ver ediciones ($99 / $199)</a>
        </div>
      </div>
    `;
  }

  // Modal de acceso
  const modal = document.getElementById('access-modal');
  const keyInput = document.getElementById('access-key-input');
  const keyError = document.getElementById('access-key-error');

  function openAccessModal() {
    keyInput.value = '';
    keyError.hidden = true;
    modal.hidden = false;
    setTimeout(() => keyInput.focus(), 60);
  }

  function closeAccessModal() {
    modal.hidden = true;
  }

  document.getElementById('btn-open-access').addEventListener('click', openAccessModal);
  document.getElementById('btn-banner-unlock').addEventListener('click', openAccessModal);
  document.getElementById('btn-manage-key').addEventListener('click', openAccessModal);
  document.getElementById('btn-close-modal').addEventListener('click', closeAccessModal);
  modal.addEventListener('click', e => {
    if (e.target === modal) closeAccessModal();
  });

  document.getElementById('btn-submit-key').addEventListener('click', () => {
    const tier = resolveKey(keyInput.value);
    if (!tier) {
      keyError.textContent = 'Clave no reconocida. Revisa el código de tu compra (ej. ESENCIAL-2026 o COMPLETA-2026).';
      keyError.hidden = false;
      return;
    }
    state.tier = tier;
    saveState();
    closeAccessModal();
    renderAll();
    showToast(tier === 'completa' ? '🎉 Edición Completa activada (30 días)' : '✓ Edición Esencial activada (Semana 1 + SOS)');
  });

  document.addEventListener('click', e => {
    if (e.target.closest('.js-open-modal')) {
      openAccessModal();
    }
  });

  // Navegación inferior + Pantalla inicial de 4 Fases
  const welcomeEl = document.getElementById('view-welcome');
  const appViewsEl = document.getElementById('app-views');
  let welcomeVisible = false;

  function setWelcomeVisible(show) {
    welcomeVisible = Boolean(show);
    welcomeEl.hidden = !welcomeVisible;
    appViewsEl.hidden = welcomeVisible;
    const banner = document.getElementById('access-banner');
    if (welcomeVisible) {
      banner.hidden = true;
    } else {
      renderAccessUI();
    }
    try { window.scrollTo({ top: 0, behavior: 'smooth' }); } catch (e) { window.scrollTo(0, 0); }
  }

  function renderWelcome() {
    if (!contentData) return;
    const list = document.getElementById('welcome-phases-list');
    list.innerHTML = '';
    const colors = { 1: '#4A5D4E', 2: '#C67D5B', 3: '#9B7B54', 4: '#5F6F7E' };

    contentData.weeks.forEach(w => {
      const accent = colors[w.number] || '#4A5D4E';
      const isEsencial = w.number === 1;
      const planLabel = isEsencial ? 'Desde Esencial ($99)' : 'Completa ($199)';
      const gains = (w.expectedOutcome || []).slice(0, 2).join(' ');
      const card = document.createElement('div');
      card.className = 'phase-card';
      card.style.borderLeft = `5px solid ${accent}`;
      card.innerHTML = `
        <div class="phase-head">
          <span class="phase-num" style="color:${accent};">Fase ${w.number} · ${esc(w.daysRange)}</span>
          <span class="phase-plan-tag ${isEsencial ? 'tag-esencial' : ''}">${planLabel}</span>
        </div>
        <h3>${esc(w.title)}</h3>
        <p class="phase-why"><strong>Para qué sirve:</strong> ${esc(w.focus)}</p>
        <p class="phase-gain"><strong>Qué te llevas:</strong> ${esc(gains)}</p>
      `;
      list.appendChild(card);
    });

    const startBtn = document.getElementById('btn-welcome-start');
    const keyBtn = document.getElementById('btn-welcome-key');
    if (state.tier === 'completa') {
      startBtn.textContent = 'Ir a mi recorrido de 30 días →';
      keyBtn.hidden = true;
    } else if (state.tier === 'esencial') {
      startBtn.textContent = 'Ir a mi Semana 1 y Hoja SOS →';
      keyBtn.hidden = false;
      keyBtn.textContent = 'Subir a Edición Completa (tengo clave)';
    } else {
      startBtn.textContent = 'Probar el Día 1 gratis ahora →';
      keyBtn.hidden = false;
      keyBtn.textContent = 'Ya tengo mi clave de acceso';
    }
  }

  document.getElementById('btn-open-welcome').addEventListener('click', () => {
    renderWelcome();
    setWelcomeVisible(!welcomeVisible);
  });

  document.getElementById('btn-banner-phases').addEventListener('click', () => {
    renderWelcome();
    setWelcomeVisible(true);
  });

  document.getElementById('btn-welcome-start').addEventListener('click', () => {
    state.seenWelcome = true;
    saveState();
    setWelcomeVisible(false);
    switchTab('dias');
  });

  document.getElementById('btn-welcome-key').addEventListener('click', openAccessModal);

  function switchTab(tabId) {
    if (welcomeVisible) {
      state.seenWelcome = true;
      saveState();
      setWelcomeVisible(false);
    }
    document.querySelectorAll('.nav-btn').forEach(b => b.classList.toggle('active', b.dataset.tab === tabId));
    document.querySelectorAll('.tab-panel').forEach(p => { p.hidden = p.id !== `tab-${tabId}`; });
    try { window.scrollTo({ top: 0, behavior: 'smooth' }); } catch (e) { window.scrollTo(0, 0); }
  }

  document.querySelectorAll('.nav-btn').forEach(btn => {
    btn.addEventListener('click', () => switchTab(btn.dataset.tab));
  });

  // Cabecera y banner de plan
  function renderAccessUI() {
    const badge = document.getElementById('btn-open-access');
    const banner = document.getElementById('access-banner');
    const bTitle = document.getElementById('access-banner-title');
    const bBody = document.getElementById('access-banner-body');
    const planH = document.getElementById('plan-heading');
    const planD = document.getElementById('plan-desc');

    badge.classList.remove('tier-completa', 'tier-esencial');

    if (state.tier === 'completa') {
      badge.textContent = 'Completa · 30 Días ✓';
      badge.classList.add('tier-completa');
      banner.hidden = true;
      planH.textContent = 'Edición Completa (30 Días) ✓';
      planD.textContent = 'Tienes acceso ilimitado a las 4 semanas, Hoja SOS, Descarga Mental, Triple Ancla, Día Base, Dinero 3–2–1 y Comparativa Día 1 vs. Día 30.';
    } else if (state.tier === 'esencial') {
      badge.textContent = 'Esencial · Sem. 1';
      badge.classList.add('tier-esencial');
      banner.hidden = welcomeVisible;
      bTitle.textContent = 'Edición Esencial activa (Fase 1 · Semana 1 + Hoja SOS)';
      bBody.textContent = 'Ya tienes los Días 1 al 7, la Descarga Mental y tu Hoja SOS listos. Cuando quieras desbloquear las Fases 2, 3 y 4 (Días 8–30 + Día Base + Dinero 3–2–1), activa tu clave Completa.';
      planH.textContent = 'Edición Esencial ($99) ✓';
      planD.textContent = 'Incluye Fase 1 (Días 1–7), Descarga Mental y Hoja SOS interactiva. Puedes subir a Edición Completa ($199) cuando gustes ingresando tu nueva clave.';
    } else {
      badge.textContent = 'Muestra · Clave';
      banner.hidden = welcomeVisible;
      bTitle.textContent = 'Modo muestra gratis (Día 1)';
      bBody.textContent = 'Prueba el Día 1 completo sin costo. Si ya adquiriste tu edición Esencial ($99) o Completa ($199), toca el botón para activar tu clave.';
      planH.textContent = 'Modo Muestra (Día 1 gratis)';
      planD.textContent = 'Estás explorando el Día 1 de muestra. Activa tu clave de Edición Esencial ($99) o Edición Completa ($199) para abrir tu sistema.';
    }
  }

  // TAB 1: 30 DÍAS
  function getDayState(dayNum) {
    const key = String(dayNum);
    if (!state.days[key]) {
      state.days[key] = {
        done: false,
        microDone: false,
        expenseDone: false,
        tpuText: '',
        tpuDone: false,
        notes: '',
        completedAt: null
      };
    }
    return state.days[key];
  }

  function computeStreak() {
    let streak = 0;
    for (let i = 1; i <= 30; i++) {
      if (state.days[String(i)] && state.days[String(i)].done) {
        streak++;
      } else if (streak > 0) {
        break;
      }
    }
    return streak;
  }

  function renderDaysTab() {
    if (!contentData) return;

    const doneCount = Object.values(state.days).filter(d => d && d.done).length;
    const pct = Math.round((doneCount / 30) * 100);
    document.getElementById('progress-label').textContent = `${doneCount} de 30 días completados (${pct}%)`;
    document.getElementById('overall-progress-fill').style.width = `${pct}%`;
    document.getElementById('streak-pill').textContent = `Racha: ${computeStreak()} días`;

    // Tabs de semanas
    const wWrap = document.getElementById('week-tabs');
    wWrap.innerHTML = '';
    contentData.weeks.forEach(w => {
      const isLockedWeek = (w.number > 1 && state.tier !== 'completa');
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'week-tab' + (state.activeWeek === w.number ? ' active' : '') + (isLockedWeek ? ' locked' : '');
      btn.innerHTML = `Fase ${w.number} ${isLockedWeek ? '🔒' : ''}<span>${w.daysRange.replace('Días ', 'D')}</span>`;
      btn.addEventListener('click', () => {
        state.activeWeek = w.number;
        const firstDayOfWeek = w.days[0].day;
        state.selectedDay = firstDayOfWeek;
        saveState();
        renderDaysTab();
      });
      wWrap.appendChild(btn);
    });

    const weekObj = contentData.weeks.find(w => w.number === state.activeWeek) || contentData.weeks[0];
    const firstOutcome = (weekObj.expectedOutcome && weekObj.expectedOutcome[0]) ? weekObj.expectedOutcome[0] : '';
    document.getElementById('week-motto').innerHTML = `
      <strong>Fase ${weekObj.number} · ${esc(weekObj.title)}:</strong> ${esc(weekObj.focus)}<br/>
      <span><em>Resultado esperado:</em> ${esc(firstOutcome)}</span>
    `;

    // Grid de días de la semana
    const dGrid = document.getElementById('days-grid');
    dGrid.innerHTML = '';
    weekObj.days.forEach(d => {
      const ds = state.days[String(d.day)];
      const locked = !canAccessDay(d.day);
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'day-pill'
        + (state.selectedDay === d.day ? ' active' : '')
        + (ds && ds.done ? ' done' : '')
        + (locked ? ' locked' : '');
      btn.innerHTML = `
        <span>Día ${d.day}</span>
        <span class="day-status">${locked ? '🔒' : (ds && ds.done ? '✓ Listo' : 'Pendiente')}</span>
      `;
      btn.addEventListener('click', () => {
        state.selectedDay = d.day;
        saveState();
        renderDaysTab();
      });
      dGrid.appendChild(btn);
    });

    renderSelectedDayCard();
  }

  function renderSelectedDayCard() {
    const area = document.getElementById('day-content-area');
    const dayObj = allDays.find(d => d.day === state.selectedDay) || allDays[0];
    const weekObj = contentData.weeks.find(w => w.days.some(x => x.day === dayObj.day));

    if (!canAccessDay(dayObj.day)) {
      const req = dayObj.day <= 7 ? 'esencial' : 'completa';
      const title = dayObj.day <= 7
        ? `Día ${dayObj.day}: ${dayObj.title}`
        : `Semana ${weekObj.number} · Día ${dayObj.day}: ${dayObj.title}`;
      const desc = dayObj.day <= 7
        ? 'Desbloquea toda la Semana 1 (Días 1 al 7) + la Hoja SOS y Descarga Mental con tu Edición Esencial ($99) o Completa ($199).'
        : 'Este día forma parte de las Semanas 2, 3 y 4 del sistema completo (Días 8 al 30 + Día Base + Dinero 3–2–1). Activa tu clave de Edición Completa ($199) para abrirlo.';
      area.innerHTML = buildLockHtml(title, desc, req);
      return;
    }

    const ds = getDayState(dayObj.day);
    area.innerHTML = `
      <article class="card card-primary">
        <p class="eyebrow">Semana ${weekObj.number} · Día ${dayObj.day} de 30</p>
        <h2 class="serif-title">${esc(dayObj.title)}</h2>
        <p class="copy">${esc(dayObj.idea)}</p>
        <p class="quote-box">“${esc(dayObj.quote)}”</p>

        <label class="check-row ${ds.microDone ? 'checked' : ''}">
          <input type="checkbox" id="day-micro-check" ${ds.microDone ? 'checked' : ''} />
          <div>
            <strong>Tu microacción de hoy (5–10 min)</strong>
            <span>${esc(dayObj.microaction)}</span>
          </div>
        </label>

        <div class="field" style="margin-top: 14px;">
          <label for="day-tpu-input">Tu TPU (Tarea Prioritaria Única) de hoy</label>
          <input id="day-tpu-input" type="text" class="input" value="${esc(ds.tpuText)}" placeholder="La única acción que define tu día hoy..." />
        </div>

        <label class="check-row ${ds.tpuDone ? 'checked' : ''}">
          <input type="checkbox" id="day-tpu-check" ${ds.tpuDone ? 'checked' : ''} />
          <div>
            <strong>Cumplí mi TPU de hoy</strong>
            <span>Si logras tu TPU, ya ganaste el día.</span>
          </div>
        </label>

        <label class="check-row ${ds.expenseDone ? 'checked' : ''}">
          <input type="checkbox" id="day-exp-check" ${ds.expenseDone ? 'checked' : ''} />
          <div>
            <strong>Orden del dinero hoy</strong>
            <span>${esc(dayObj.expense)}</span>
          </div>
        </label>

        <div class="field" style="margin-top: 12px;">
          <label for="day-notes">Notas o descarga de hoy (guardado automático)</label>
          <textarea id="day-notes" class="textarea" rows="3" placeholder="Escribe aquí lo que soltaste, aprendiste o decidiste hoy...">${esc(ds.notes)}</textarea>
        </div>

        <div class="btn-row" style="margin-top: 14px;">
          <button type="button" id="btn-toggle-day-done" class="btn ${ds.done ? 'btn-secondary' : 'btn-primary'} btn-full">
            ${ds.done ? '✓ Día ' + dayObj.day + ' completado (toca para desmarcar)' : 'Marcar Día ' + dayObj.day + ' como completado ✓'}
          </button>
        </div>
        <div class="btn-row" style="justify-content: space-between; margin-top: 10px;">
          <button type="button" id="btn-day-prev" class="btn btn-ghost btn-sm" ${dayObj.day <= 1 ? 'disabled' : ''}>← Día anterior</button>
          <button type="button" id="btn-day-next" class="btn btn-ghost btn-sm" ${dayObj.day >= 30 ? 'disabled' : ''}>Día siguiente →</button>
        </div>
      </article>
    `;

    // Bind events del día
    const microCb = document.getElementById('day-micro-check');
    microCb.addEventListener('change', e => {
      ds.microDone = e.target.checked;
      e.target.closest('.check-row').classList.toggle('checked', ds.microDone);
      saveState();
    });

    const tpuInput = document.getElementById('day-tpu-input');
    tpuInput.addEventListener('input', e => {
      ds.tpuText = e.target.value;
      saveState();
      syncSosTpu();
    });

    const tpuCb = document.getElementById('day-tpu-check');
    tpuCb.addEventListener('change', e => {
      ds.tpuDone = e.target.checked;
      e.target.closest('.check-row').classList.toggle('checked', ds.tpuDone);
      saveState();
    });

    const expCb = document.getElementById('day-exp-check');
    expCb.addEventListener('change', e => {
      ds.expenseDone = e.target.checked;
      e.target.closest('.check-row').classList.toggle('checked', ds.expenseDone);
      saveState();
    });

    const notesEl = document.getElementById('day-notes');
    notesEl.addEventListener('input', e => {
      ds.notes = e.target.value;
      saveState();
    });

    document.getElementById('btn-toggle-day-done').addEventListener('click', () => {
      ds.done = !ds.done;
      ds.completedAt = ds.done ? new Date().toISOString() : null;
      saveState();
      renderDaysTab();
      showToast(ds.done ? `¡Día ${dayObj.day} completado! Un paso más en orden.` : `Día ${dayObj.day} marcado como pendiente`);
    });

    document.getElementById('btn-day-prev').addEventListener('click', () => {
      if (dayObj.day > 1) {
        const target = dayObj.day - 1;
        state.selectedDay = target;
        const tw = contentData.weeks.find(w => w.days.some(x => x.day === target));
        if (tw) state.activeWeek = tw.number;
        saveState();
        renderDaysTab();
      }
    });

    document.getElementById('btn-day-next').addEventListener('click', () => {
      if (dayObj.day < 30) {
        const target = dayObj.day + 1;
        state.selectedDay = target;
        const tw = contentData.weeks.find(w => w.days.some(x => x.day === target));
        if (tw) state.activeWeek = tw.number;
        saveState();
        renderDaysTab();
      }
    });
  }

  // TAB 2: HOJA SOS + DESCARGA MENTAL
  let breathInterval = null;
  let breathSeconds = 60;
  let dumpInterval = null;
  let dumpSeconds = 180;

  function fmtClock(sec) {
    const m = Math.floor(sec / 60);
    const s = sec % 60;
    return `${m < 10 ? '0' + m : m}:${s < 10 ? '0' + s : s}`;
  }

  function updateBreathPhase(elapsed) {
    const cycle = elapsed % 12; // 4s inhala + 2s retén + 6s exhala
    if (cycle < 4) return 'Inhala suave por la nariz… (4s)';
    if (cycle < 6) return 'Retén con calma… (2s)';
    return 'Exhala despacio soltando los hombros… (6s)';
  }

  function syncSosTpu() {
    const ds = state.days[String(state.selectedDay)];
    const tpu = (ds && ds.tpuText && ds.tpuText.trim()) || (state.dump.top1 && state.dump.top1.trim()) || 'Define tu TPU en tu día de hoy';
    const el = document.getElementById('sos-current-tpu');
    if (el) el.textContent = tpu;
  }

  function renderSosTab() {
    const lockWrap = document.getElementById('sos-lock-wrap');
    const contentWrap = document.getElementById('sos-content-wrap');

    if (!canAccessSos()) {
      lockWrap.hidden = false;
      contentWrap.hidden = true;
      lockWrap.innerHTML = buildLockHtml(
        'Hoja SOS y Descarga Mental de 3 minutos',
        'Tu botón de rescate con temporizador guiado de respiración 4–2–6, protocolo de 6 pasos y descarga mental está incluido desde la Edición Esencial ($99 MXN).',
        'esencial'
      );
      return;
    }

    lockWrap.hidden = true;
    contentWrap.hidden = false;
    syncSosTpu();
    document.getElementById('sos-good-thing').value = state.sos.goodThing || '';
    document.getElementById('sos-count-note').textContent = state.sos.rescues > 0
      ? `Días rescatados con Hoja SOS: ${state.sos.rescues}`
      : 'Usa este protocolo cada vez que el día se sienta cuesta arriba.';

    document.getElementById('dump-text').value = state.dump.text || '';
    document.getElementById('dump-top1').value = state.dump.top1 || '';
    document.getElementById('dump-top2').value = state.dump.top2 || '';
  }

  document.getElementById('btn-breath-start').addEventListener('click', () => {
    const btn = document.getElementById('btn-breath-start');
    if (breathInterval) {
      clearInterval(breathInterval);
      breathInterval = null;
      btn.textContent = 'Continuar';
      return;
    }
    if (breathSeconds <= 0) breathSeconds = 60;
    btn.textContent = 'Pausar';
    document.getElementById('breath-phase').textContent = updateBreathPhase(60 - breathSeconds);
    breathInterval = setInterval(() => {
      breathSeconds--;
      document.getElementById('breath-clock').textContent = fmtClock(Math.max(0, breathSeconds));
      if (breathSeconds <= 0) {
        clearInterval(breathInterval);
        breathInterval = null;
        btn.textContent = 'Iniciar 60 segundos';
        document.getElementById('breath-phase').textContent = '✓ ¡60 segundos completos! Sigue al Paso 2.';
        showToast('Respiración completada');
      } else {
        document.getElementById('breath-phase').textContent = updateBreathPhase(60 - breathSeconds);
      }
    }, 1000);
  });

  document.getElementById('btn-breath-reset').addEventListener('click', () => {
    clearInterval(breathInterval);
    breathInterval = null;
    breathSeconds = 60;
    document.getElementById('breath-clock').textContent = '01:00';
    document.getElementById('breath-phase').textContent = 'Paso 1 · Inhala 4s · Retén 2s · Exhala 6s';
    document.getElementById('btn-breath-start').textContent = 'Iniciar 60 segundos';
  });

  document.getElementById('sos-good-thing').addEventListener('input', e => {
    state.sos.goodThing = e.target.value;
    saveState();
  });

  document.getElementById('btn-save-sos').addEventListener('click', () => {
    state.sos.rescues = (state.sos.rescues || 0) + 1;
    state.sos.lastRescueDate = todayIso();
    saveState();
    renderSosTab();
    showToast('✓ Día rescatado. Regresaste a tu centro.');
  });

  document.getElementById('btn-dump-start').addEventListener('click', () => {
    const btn = document.getElementById('btn-dump-start');
    if (dumpInterval) {
      clearInterval(dumpInterval);
      dumpInterval = null;
      btn.textContent = 'Continuar';
      return;
    }
    if (dumpSeconds <= 0) dumpSeconds = 180;
    btn.textContent = 'Pausar';
    dumpInterval = setInterval(() => {
      dumpSeconds--;
      document.getElementById('dump-clock').textContent = fmtClock(Math.max(0, dumpSeconds));
      if (dumpSeconds <= 0) {
        clearInterval(dumpInterval);
        dumpInterval = null;
        btn.textContent = 'Iniciar 3 minutos';
        showToast('¡3 minutos completos! Ahora elige tus 2 prioridades.');
      }
    }, 1000);
  });

  document.getElementById('btn-dump-reset').addEventListener('click', () => {
    clearInterval(dumpInterval);
    dumpInterval = null;
    dumpSeconds = 180;
    document.getElementById('dump-clock').textContent = '03:00';
    document.getElementById('btn-dump-start').textContent = 'Iniciar 3 minutos';
  });

  document.getElementById('dump-text').addEventListener('input', e => {
    state.dump.text = e.target.value;
    saveState();
  });
  document.getElementById('dump-top1').addEventListener('input', e => {
    state.dump.top1 = e.target.value;
    saveState();
    syncSosTpu();
  });
  document.getElementById('dump-top2').addEventListener('input', e => {
    state.dump.top2 = e.target.value;
    saveState();
  });

  // TAB 3: TRIPLE ANCLA + DÍA BASE
  function renderBaseTab() {
    const lockWrap = document.getElementById('base-lock-wrap');
    const contentWrap = document.getElementById('base-content-wrap');

    if (!canAccessFullTools()) {
      lockWrap.hidden = false;
      contentWrap.hidden = true;
      lockWrap.innerHTML = buildLockHtml(
        'Mi Triple Ancla + Mi Día Base',
        'Configura tus 3 hábitos no negociables para días difíciles y tu estructura mínima de estabilidad en la Edición Completa ($199 MXN).',
        'completa'
      );
      return;
    }

    lockWrap.hidden = true;
    contentWrap.hidden = false;

    // Chips del libro
    const chipsWrap = document.getElementById('ancla-chips');
    chipsWrap.innerHTML = '';
    const examples = (contentData && contentData.tripleAnclaExamples) || [];
    examples.forEach((ex, idx) => {
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'chip';
      btn.textContent = ex.title;
      btn.addEventListener('click', () => {
        const slot = idx === 0 || idx === 1 ? 'a1' : (idx === 2 ? 'a2' : 'a3');
        state.tripleAncla[slot] = ex.title;
        saveState();
        renderBaseTab();
        showToast('Ancla agregada');
      });
      chipsWrap.appendChild(btn);
    });

    document.getElementById('ancla-1').value = state.tripleAncla.a1 || '';
    document.getElementById('ancla-2').value = state.tripleAncla.a2 || '';
    document.getElementById('ancla-3').value = state.tripleAncla.a3 || '';

    const today = todayIso();
    if (!state.tripleAncla.checksByDate[today]) {
      state.tripleAncla.checksByDate[today] = [false, false, false];
    }
    const checks = state.tripleAncla.checksByDate[today];
    const labels = [
      state.tripleAncla.a1 || 'Ancla 1 · Mente',
      state.tripleAncla.a2 || 'Ancla 2 · Día',
      state.tripleAncla.a3 || 'Ancla 3 · Orden / Dinero'
    ];
    const checksWrap = document.getElementById('ancla-checks');
    checksWrap.innerHTML = '';
    labels.forEach((lbl, i) => {
      const row = document.createElement('label');
      row.className = 'check-row' + (checks[i] ? ' checked' : '');
      row.innerHTML = `
        <input type="checkbox" ${checks[i] ? 'checked' : ''} />
        <div><strong>${esc(lbl)}</strong><span>Ancla ${i + 1} de hoy</span></div>
      `;
      row.querySelector('input').addEventListener('change', e => {
        checks[i] = e.target.checked;
        row.classList.toggle('checked', checks[i]);
        saveState();
        if (checks.every(Boolean)) showToast('🎉 ¡Triple Ancla completa hoy!');
      });
      checksWrap.appendChild(row);
    });

    document.getElementById('db-tpu').value = state.diaBase.tpu || '';
    document.getElementById('db-care').value = state.diaBase.care || '';
    document.getElementById('db-center').value = state.diaBase.center || '';
    document.getElementById('db-budget').value = state.diaBase.budget || '';
    document.getElementById('db-vida').value = state.diaBase.vida || '';
  }

  ['a1', 'a2', 'a3'].forEach((k, idx) => {
    document.getElementById(`ancla-${idx + 1}`).addEventListener('input', e => {
      state.tripleAncla[k] = e.target.value;
      saveState();
    });
  });

  [
    ['db-tpu', 'tpu'],
    ['db-care', 'care'],
    ['db-center', 'center'],
    ['db-budget', 'budget'],
    ['db-vida', 'vida']
  ].forEach(([elId, field]) => {
    document.getElementById(elId).addEventListener('input', e => {
      state.diaBase[field] = e.target.value;
      saveState();
    });
  });

  // TAB 4: DINERO REGLA 3-2-1
  document.getElementById('exp-cat-row').addEventListener('click', e => {
    const btn = e.target.closest('.cat-btn');
    if (!btn) return;
    selectedExpCat = btn.dataset.cat;
    document.querySelectorAll('#exp-cat-row .cat-btn').forEach(b => b.classList.toggle('active', b === btn));
  });

  document.getElementById('btn-add-expense').addEventListener('click', () => {
    const descEl = document.getElementById('exp-desc');
    const amtEl = document.getElementById('exp-amount');
    const desc = descEl.value.trim();
    const amount = parseFloat(amtEl.value);
    if (!desc || isNaN(amount) || amount <= 0) {
      showToast('Escribe concepto y monto válido');
      return;
    }
    state.expenses.unshift({
      id: 'exp_' + Date.now(),
      date: todayIso(),
      desc,
      amount: Number(amount.toFixed(2)),
      cat: selectedExpCat
    });
    saveState();
    descEl.value = '';
    amtEl.value = '';
    renderDineroTab();
    showToast('Gasto registrado');
  });

  function fmtMoney(n) {
    return '$' + Number(n || 0).toLocaleString('es-MX', { maximumFractionDigits: 0 });
  }

  function renderDineroTab() {
    const lockWrap = document.getElementById('dinero-lock-wrap');
    const contentWrap = document.getElementById('dinero-content-wrap');

    if (!canAccessFullTools()) {
      lockWrap.hidden = false;
      contentWrap.hidden = true;
      lockWrap.innerHTML = buildLockHtml(
        'Mi Dinero en Orden (Regla 3–2–1)',
        'Registra tus gastos en 10 segundos como Necesario, Útil o Impulso y detecta fugas al instante en la Edición Completa ($199 MXN).',
        'completa'
      );
      return;
    }

    lockWrap.hidden = true;
    contentWrap.hidden = false;

    const sums = { N: 0, U: 0, I: 0 };
    state.expenses.forEach(item => {
      if (sums[item.cat] !== undefined) sums[item.cat] += Number(item.amount || 0);
    });
    const total = sums.N + sums.U + sums.I;
    document.getElementById('sum-N').textContent = fmtMoney(sums.N);
    document.getElementById('sum-U').textContent = fmtMoney(sums.U);
    document.getElementById('sum-I').textContent = fmtMoney(sums.I);

    const impPct = total > 0 ? Math.round((sums.I / total) * 100) : 0;
    document.getElementById('exp-total-line').textContent = total > 0
      ? `Total registrado: ${fmtMoney(total)} MXN · Impulso representa ${impPct}%`
      : 'Aún no registras gastos. Empieza anotando 1 gasto hoy.';

    const listEl = document.getElementById('expense-list');
    listEl.innerHTML = '';
    const catNames = { N: 'Necesario', U: 'Útil', I: 'Impulso' };
    state.expenses.slice(0, 40).forEach(item => {
      const row = document.createElement('div');
      row.className = 'exp-item';
      row.innerHTML = `
        <div class="exp-meta">
          <strong>${esc(item.desc)}</strong>
          <span>${esc(item.date)}</span>
        </div>
        <div class="exp-right">
          <span class="exp-tag ${item.cat}">${catNames[item.cat] || item.cat}</span>
          <strong>${fmtMoney(item.amount)}</strong>
          <button type="button" class="del-btn" aria-label="Eliminar">×</button>
        </div>
      `;
      row.querySelector('.del-btn').addEventListener('click', () => {
        state.expenses = state.expenses.filter(x => x.id !== item.id);
        saveState();
        renderDineroTab();
      });
      listEl.appendChild(row);
    });
  }

  // TAB 5: AVANCE (COMPARATIVA DÍA 1 VS 30 + RESPALDO)
  function renderCompareRadar() {
    const svgEl = document.getElementById('compare-radar');
    const cx = 170;
    const cy = 170;
    const maxR = 104;
    const count = DIMS.length;
    const pt = (idx, ratio) => {
      const angle = (-Math.PI / 2) + (idx * 2 * Math.PI / count);
      return { x: cx + Math.cos(angle) * maxR * ratio, y: cy + Math.sin(angle) * maxR * ratio };
    };

    let svg = '';
    for (let lvl = 1; lvl <= 5; lvl++) {
      const pts = DIMS.map((_, i) => {
        const p = pt(i, lvl / 5);
        return `${p.x.toFixed(1)},${p.y.toFixed(1)}`;
      }).join(' ');
      svg += `<polygon points="${pts}" fill="${lvl % 2 === 0 ? 'rgba(242,236,225,0.45)' : 'none'}" stroke="#DFD7C8" stroke-width="1" />`;
    }
    DIMS.forEach((d, i) => {
      const outer = pt(i, 1);
      svg += `<line x1="${cx}" y1="${cy}" x2="${outer.x.toFixed(1)}" y2="${outer.y.toFixed(1)}" stroke="#DFD7C8" stroke-width="1" />`;
      const lbl = pt(i, 1.28);
      const anchor = Math.abs(lbl.x - cx) < 12 ? 'middle' : (lbl.x > cx ? 'start' : 'end');
      svg += `<text x="${lbl.x.toFixed(1)}" y="${(lbl.y + 5).toFixed(1)}" text-anchor="${anchor}" fill="#1F1F1C" font-size="14" font-weight="700" font-family="Plus Jakarta Sans, sans-serif">${d.name}</text>`;
    });

    const d1Pts = DIMS.map((d, i) => {
      const v = Math.max(0.15, (Number(state.compare.day1[d.id]) || 1) / 5);
      const p = pt(i, v);
      return `${p.x.toFixed(1)},${p.y.toFixed(1)}`;
    }).join(' ');

    const d30Pts = DIMS.map((d, i) => {
      const v = Math.max(0.15, (Number(state.compare.day30[d.id]) || 1) / 5);
      const p = pt(i, v);
      return `${p.x.toFixed(1)},${p.y.toFixed(1)}`;
    }).join(' ');

    svg += `<polygon points="${d1Pts}" fill="rgba(198,125,91,0.14)" stroke="#C67D5B" stroke-width="2.4" stroke-dasharray="6 4" stroke-linejoin="round" />`;
    svg += `<polygon points="${d30Pts}" fill="rgba(74,93,78,0.24)" stroke="#4A5D4E" stroke-width="2.8" stroke-linejoin="round" />`;
    svgEl.innerHTML = svg;

    const avg1 = DIMS.reduce((a, d) => a + Number(state.compare.day1[d.id] || 0), 0) / DIMS.length;
    const avg30 = DIMS.reduce((a, d) => a + Number(state.compare.day30[d.id] || 0), 0) / DIMS.length;
    const diff = Number((avg30 - avg1).toFixed(1));
    const deltaEl = document.getElementById('compare-delta-summary');
    if (diff > 0) {
      deltaEl.textContent = `Promedio Día 1: ${avg1.toFixed(1)}/5 → Día 30: ${avg30.toFixed(1)}/5 (+${diff.toFixed(1)} pts de mayor orden y calma).`;
    } else if (diff === 0) {
      deltaEl.textContent = `Promedio actual: ${avg1.toFixed(1)}/5. Al llegar al Día 30 ajusta los controles de abajo para ver tu evolución.`;
    } else {
      deltaEl.textContent = `Promedio Día 1: ${avg1.toFixed(1)}/5 → Día 30: ${avg30.toFixed(1)}/5. Identificar qué bajó te muestra justo dónde volver a tu Día Base.`;
    }
  }

  function renderAvanceTab() {
    const lockWrap = document.getElementById('compare-lock-wrap');
    const compareCard = document.getElementById('compare-card');

    if (!canAccessFullTools()) {
      lockWrap.hidden = false;
      compareCard.hidden = true;
      lockWrap.innerHTML = buildLockHtml(
        'Comparativa Día 1 vs. Día 30',
        'Visualiza tu gráfica doble de avance entre el Día 1 y el Día 30 en la Edición Completa ($199 MXN).',
        'completa'
      );
      return;
    }

    lockWrap.hidden = true;
    compareCard.hidden = false;

    const buildSliders = (containerId, keyName) => {
      const wrap = document.getElementById(containerId);
      wrap.innerHTML = '';
      DIMS.forEach(d => {
        const val = Number(state.compare[keyName][d.id] || 2.5);
        const row = document.createElement('div');
        row.className = 'slider-row';
        row.innerHTML = `
          <label>${d.name}</label>
          <input type="range" min="1" max="5" step="0.5" value="${val}" />
          <span class="slider-val">${val.toFixed(1)}</span>
        `;
        const inp = row.querySelector('input');
        const out = row.querySelector('.slider-val');
        inp.addEventListener('input', e => {
          const v = Number(e.target.value);
          state.compare[keyName][d.id] = v;
          out.textContent = v.toFixed(1);
          saveState();
          renderCompareRadar();
        });
        wrap.appendChild(row);
      });
    };

    buildSliders('sliders-d1', 'day1');
    buildSliders('sliders-d30', 'day30');
    renderCompareRadar();
  }

  // Respaldo JSON
  document.getElementById('btn-export-json').addEventListener('click', () => {
    const blob = new Blob([JSON.stringify(state, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `vida-en-orden-respaldo-${todayIso()}.json`;
    a.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
    showToast('Respaldo descargado');
  });

  document.getElementById('btn-copy-backup').addEventListener('click', async () => {
    const text = JSON.stringify(state);
    try {
      await navigator.clipboard.writeText(text);
      showToast('Código de respaldo copiado');
    } catch (e) {
      showToast('Usa “Descargar respaldo (.json)” en este navegador');
    }
  });

  document.getElementById('input-import-json').addEventListener('change', e => {
    const file = e.target.files && e.target.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => {
      try {
        const imported = JSON.parse(String(reader.result));
        if (!imported || typeof imported !== 'object') throw new Error('inválido');
        state = { ...defaultState(), ...imported };
        saveState();
        renderAll();
        showToast('✓ Progreso restaurado con éxito');
      } catch (err) {
        showToast('El archivo de respaldo no es válido');
      }
    };
    reader.readAsText(file);
    e.target.value = '';
  });

  function renderAll() {
    renderAccessUI();
    renderWelcome();
    renderDaysTab();
    renderSosTab();
    renderBaseTab();
    renderDineroTab();
    renderAvanceTab();
  }

  // Inicialización
  checkUrlKey();
  fetch(CONTENT_URL)
    .then(r => r.json())
    .then(data => {
      contentData = data;
      allDays = [];
      data.weeks.forEach(w => w.days.forEach(d => allDays.push(d)));
      renderAll();
      if (!state.seenWelcome) {
        setWelcomeVisible(true);
      }
    })
    .catch(() => {
      document.getElementById('day-content-area').innerHTML =
        '<div class="card"><p class="copy">No se pudo cargar el contenido de los 30 días. Recarga la página.</p></div>';
    });
})();
