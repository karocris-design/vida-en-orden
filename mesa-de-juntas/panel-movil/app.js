(() => {
  const STORAGE_KEY = 'vida_en_orden_junta_v4';
  const REVENUE_GOAL = 10000;

  const ROADMAP_STAGES = [
    {
      stage: 'Etapa 1 · Validar el Test V.I.D.A. (Completada ✓)',
      tasks: [
        { id: 'e1_repo', label: 'Estructura del monorepo + tokens visuales unificados', defaultDone: true },
        { id: 'e1_pdf', label: 'Importar y analizar PDF original de 89 páginas desde Drive', defaultDone: true },
        { id: 'e1_test', label: 'Construir Test V.I.D.A. (20 preguntas + radar + diagnóstico + Google Sheets)', defaultDone: true },
        { id: 'e1_junta', label: 'Construir Panel Móvil de Mesa de Juntas para iPhone', defaultDone: true },
        { id: 'e1_deploy', label: 'Publicar en GitHub Pages gratis ($0) + guardado automático', defaultDone: true },
        { id: 'e1_family', label: 'Probar en familia, agrandar letra y validar cierre y diagnóstico', defaultDone: true }
      ]
    },
    {
      stage: 'Etapa 2 · Corregir y Pulir el PDF (Completada ✓)',
      tasks: [
        { id: 'e2_anon', label: 'Retirar firma personal, iniciales y metadatos de autor del PDF (@vida.orden)', defaultDone: true },
        { id: 'e2_esp', label: 'Hacer opcionales las referencias espirituales (16 menciones + ícono neutro)', defaultDone: true },
        { id: 'e2_fix', label: 'Reconstruir PDF editorial 87 págs. (Digital + Impresión), Día 20 nuevo y plantillas', defaultDone: true }
      ]
    },
    {
      stage: 'Etapa 3 · Webapp Completa de 30 Días (Completada ✓)',
      tasks: [
        { id: 'e3_days', label: 'Integrar los 30 días interactivos (10 min/día)', defaultDone: true },
        { id: 'e3_tools', label: 'Herramientas interactivas: Triple Ancla, Día Base, Hoja SOS y Dinero 3-2-1', defaultDone: true },
        { id: 'e3_key', label: 'Desbloqueo por clave local (Esencial $99 / Completa $199) + respaldo JSON', defaultDone: true }
      ]
    },
    {
      stage: 'Etapa 4 · Máquina de Marketing y Validación Comercial',
      tasks: [
        { id: 'e4_carousels', label: 'Generador automático de Carruseles (1080×1350) + 4 carruseles listos', defaultDone: true },
        { id: 'e4_reels', label: 'Activar pipeline de Reels faceless (demos webapp + FFmpeg)', defaultDone: false },
        { id: 'e4_mac', label: 'Replicar Máquina de Marketing en tu Mac (setup-mac.sh)', defaultDone: false },
        { id: 'e4_adults', label: 'Validar interés y oferta con adultos del público objetivo', defaultDone: false }
      ]
    },
    {
      stage: 'Etapa 5 · Lanzamiento y Meta ($10,000 MXN/mes)',
      tasks: [
        { id: 'e5_store', label: 'Configurar página de venta y entrega automática ($99 / $199)', defaultDone: false },
        { id: 'e5_organic', label: 'Publicación constante en Instagram, TikTok y Pinterest', defaultDone: false }
      ]
    }
  ];

  const MARKETING_PIECES = [
    {
      id: 'carrusel_01',
      format: 'Carrusel #01 · 6 PNG 1080×1350 (LISTO ✓)',
      title: 'No necesitas productividad extrema, necesitas un Día Base',
      slides: [
        'Portada: No estás atrasado. Solo estás intentando vivir sin un Día Base.',
        'Contraste: Rutina rígida vs. Tu Día Base flexible.',
        '3 piezas: Arranque limpio + 1 prioridad real + 1 hora de cierre.',
        'Cierre + CTA: Test V.I.D.A. gratis en 3 min (link en bio).'
      ]
    },
    {
      id: 'carrusel_02',
      format: 'Carrusel #02 · 6 PNG 1080×1350 (LISTO ✓)',
      title: 'La Triple Ancla para días caóticos',
      slides: [
        'Portada: Cuando el día se descontrola, no necesitas 20 hábitos. Necesitas 3.',
        'Fórmula: 1 para tu Mente · 1 para tu Día · 1 para tu Dinero/Orden.',
        'Frase del libro: “Lo pequeño, sostenido, sostiene todo.”',
        'Cierre + CTA: Descubre qué dimensión necesita orden primero en el Test V.I.D.A.'
      ]
    },
    {
      id: 'carrusel_03',
      format: 'Carrusel #03 · 6 PNG 1080×1350 (LISTO ✓)',
      title: '¿Por qué terminas el día agotado si sientes que casi no avanzaste?',
      slides: [
        'Portada: La trampa silenciosa de cargar 30 pendientes abiertos en la cabeza.',
        'Ejercicio 3 min: Escribe sin filtro → subraya 2 cosas → estaciona el resto.',
        'Frase del libro: “Lo que escribo dejo de cargarlo.”',
        'Cierre + CTA: Evalúa tus 5 dimensiones gratis en el Test V.I.D.A.'
      ]
    },
    {
      id: 'carrusel_04',
      format: 'Carrusel #04 · 6 PNG 1080×1350 (LISTO ✓)',
      title: 'El dinero no se arregla pensando. Se arregla registrando.',
      slides: [
        'Portada: Un método de 30 segundos al día sin Excels complicados.',
        'Regla de 3 etiquetas: Necesario · Útil · Impulso (sin culpa).',
        'Contraste: Prometer no gastar vs. anotar 1 gasto diario.',
        'Cierre + CTA: Revisa tu equilibrio en 5 áreas con el Test V.I.D.A. gratis.'
      ]
    },
    {
      id: 'reel_01',
      format: 'Reel Faceless · 9:16 · 22 seg (Próximo)',
      title: '¿Por qué terminas cansado si sientes que no avanzaste?',
      slides: [
        '0–3s: Grabación móvil abriendo el Test V.I.D.A. con titular editorial.',
        '3–16s: Demostración rápida marcando las 5 dimensiones → aparece el radar.',
        '16–22s: Micro-acción del día + CTA al Test gratis sin crear cuenta.'
      ]
    }
  ];

  function buildDefaultState() {
    const tasks = {};
    ROADMAP_STAGES.forEach(s => s.tasks.forEach(t => { tasks[t.id] = t.defaultDone; }));
    const pieces = {};
    MARKETING_PIECES.forEach(p => { pieces[p.id] = 'pendiente'; });
    return {
      sales: { esencial: 0, completo: 0 },
      tasks,
      pieces,
      notes: ''
    };
  }

  function loadState() {
    const def = buildDefaultState();
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (!raw) return def;
      const parsed = JSON.parse(raw);
      return {
        sales: { ...def.sales, ...(parsed.sales || {}) },
        tasks: { ...def.tasks, ...(parsed.tasks || {}) },
        pieces: { ...def.pieces, ...(parsed.pieces || {}) },
        notes: parsed.notes || ''
      };
    } catch {
      return def;
    }
  }

  let state = loadState();
  function saveState() {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
    } catch {}
  }

  const toastEl = document.getElementById('toast');
  let toastTimer = null;
  function showToast(msg) {
    toastEl.textContent = msg;
    toastEl.hidden = false;
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => { toastEl.hidden = true; }, 2600);
  }

  async function copyText(text, msg) {
    try {
      await navigator.clipboard.writeText(text);
      showToast(msg);
    } catch {
      const ta = document.createElement('textarea');
      ta.value = text;
      document.body.appendChild(ta);
      ta.select();
      document.execCommand('copy');
      ta.remove();
      showToast(msg);
    }
  }

  // TABS
  document.querySelectorAll('.nav-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const tab = btn.dataset.tab;
      document.querySelectorAll('.nav-btn').forEach(b => b.classList.toggle('active', b === btn));
      document.querySelectorAll('.tab-panel').forEach(panel => {
        panel.hidden = panel.id !== `tab-${tab}`;
      });
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  });

  // VENTAS / META
  function renderSales() {
    const e = state.sales.esencial;
    const c = state.sales.completo;
    const revenue = (e * 99) + (c * 199);
    const totalSales = e + c;
    const pct = Math.min(100, Math.round((revenue / REVENUE_GOAL) * 100));

    document.getElementById('count-esencial').textContent = e;
    document.getElementById('count-completo').textContent = c;
    document.getElementById('revenue-display').innerHTML = `$${revenue.toLocaleString('es-MX')} <span class="metric-goal">/ $10,000 MXN</span>`;
    document.getElementById('sales-count-pill').textContent = `${totalSales} / 51 ventas (${pct}%)`;
    document.getElementById('revenue-bar').style.width = `${pct}%`;
  }

  document.querySelectorAll('.step-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const tier = btn.dataset.tier;
      const delta = Number(btn.dataset.delta);
      state.sales[tier] = Math.max(0, (state.sales[tier] || 0) + delta);
      saveState();
      renderSales();
    });
  });

  // COMPARTIR MENSAJE DE PRUEBA FAMILIAR
  document.getElementById('btn-share-test').addEventListener('click', () => {
    const testUrl = new URL('../../producto/webapp/index.html', window.location.href).href;
    const msg = [
      'Hola! ¿Me ayudas probando este test corto de 3 minutos? Se llama Test V.I.D.A.',
      testUrl,
      'Al terminar trae una cajita al final para copiarme tu opinión y ver si todas las preguntas se entienden fácil.'
    ].join('\n\n');
    copyText(msg, 'Mensaje de prueba copiado para WhatsApp');
  });

  // ROADMAP
  function renderRoadmap() {
    const container = document.getElementById('roadmap-container');
    container.innerHTML = '';

    let total = 0;
    let done = 0;

    ROADMAP_STAGES.forEach(stageObj => {
      const card = document.createElement('article');
      card.className = 'card stage-card';
      const stageDone = stageObj.tasks.filter(t => state.tasks[t.id]).length;

      card.innerHTML = `
        <div class="stage-header">
          <h3 class="stage-title">${stageObj.stage}</h3>
          <span class="meta-muted">${stageDone}/${stageObj.tasks.length}</span>
        </div>
        <div class="task-list"></div>
      `;

      const list = card.querySelector('.task-list');
      stageObj.tasks.forEach(task => {
        total++;
        const isDone = Boolean(state.tasks[task.id]);
        if (isDone) done++;

        const label = document.createElement('label');
        label.className = 'task-row' + (isDone ? ' done' : '');
        label.innerHTML = `
          <input type="checkbox" ${isDone ? 'checked' : ''} />
          <span>${task.label}</span>
        `;
        label.querySelector('input').addEventListener('change', e => {
          state.tasks[task.id] = e.target.checked;
          saveState();
          renderRoadmap();
        });
        list.appendChild(label);
      });

      container.appendChild(card);
    });

    const pct = total ? Math.round((done / total) * 100) : 0;
    document.getElementById('roadmap-pct').textContent = `${pct}% (${done}/${total})`;
    document.getElementById('roadmap-bar').style.width = `${pct}%`;
  }

  // MARKETING
  function renderMarketing() {
    const container = document.getElementById('marketing-container');
    container.innerHTML = '';

    MARKETING_PIECES.forEach(piece => {
      const current = state.pieces[piece.id] || 'pendiente';
      const card = document.createElement('article');
      card.className = 'card piece-card';
      card.innerHTML = `
        <span class="piece-meta">${piece.format}</span>
        <h3 class="piece-hook">${piece.title}</h3>
        <ul class="piece-slides">
          ${piece.slides.map(s => `<li>${s}</li>`).join('')}
        </ul>
        <div class="status-row">
          <button type="button" class="status-btn ${current === 'aprobado' ? 'active' : ''}" data-status="aprobado">Aprobar</button>
          <button type="button" class="status-btn ${current === 'ajustar' ? 'active' : ''}" data-status="ajustar">Ajustar</button>
          <button type="button" class="status-btn ${current === 'pendiente' ? 'active' : ''}" data-status="pendiente">Pendiente</button>
        </div>
      `;

      card.querySelectorAll('.status-btn').forEach(btn => {
        btn.addEventListener('click', () => {
          state.pieces[piece.id] = btn.dataset.status;
          saveState();
          renderMarketing();
          showToast(`Estado actualizado: ${btn.textContent}`);
        });
      });

      container.appendChild(card);
    });
  }

  document.getElementById('btn-export-mkt').addEventListener('click', () => {
    const lines = [
      'Mesa de Juntas — Decisiones de Marketing (VIDA EN ORDEN)',
      ...MARKETING_PIECES.map(p => `• [${(state.pieces[p.id] || 'pendiente').toUpperCase()}] ${p.title}`)
    ];
    copyText(lines.join('\n'), 'Decisiones de marketing copiadas');
  });

  // NOTAS DE JUNTA
  const notesInput = document.getElementById('board-notes');
  notesInput.value = state.notes || '';
  notesInput.addEventListener('input', e => {
    state.notes = e.target.value;
    saveState();
    document.getElementById('notes-status').textContent = 'Guardado ahora';
  });

  document.getElementById('btn-copy-agenda').addEventListener('click', () => {
    const doneCount = Object.values(state.tasks).filter(Boolean).length;
    const totalCount = Object.keys(state.tasks).length;
    const msg = [
      '📋 Agenda — Mesa de Juntas VIDA EN ORDEN',
      `Avance roadmap: ${doneCount}/${totalCount} tareas`,
      `Ventas registradas: ${state.sales.esencial} Esencial + ${state.sales.completo} Completo`,
      '',
      'Notas desde iPhone:',
      state.notes.trim() || '(Sin notas nuevas todavía)'
    ].join('\n');
    copyText(msg, 'Agenda copiada para pegar en el chat');
  });

  renderSales();
  renderRoadmap();
  renderMarketing();
})();
