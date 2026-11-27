(() => {
  const STORAGE_KEY = 'vida_en_orden_test_v1';
  const SHEETS_WEBHOOK_URL = 'https://script.google.com/macros/s/AKfycbwsTRMTmWNc2rkkG23_FRq99kihGzq71zZ2w1ZRE5VojAMROPKSz9RXsJLhkVR055yEgQ/exec';

  const DIMENSIONS = [
    {
      id: 'mente',
      name: 'Mente',
      color: '#4A5D4E',
      short: 'Claridad y ruido mental',
      vidaLetter: 'V — Vida (Reconocer tu estado y bajar el ruido)',
      weekLabel: 'Semana 1 · Orden mental y calma',
      toolName: 'Descarga mental de 3 minutos',
      strengthCopy: 'Tu mente tiene espacio para pensar con calma. Cuando hay claridad arriba, las decisiones diarias pesan mucho menos y no te saturas con facilidad.',
      strengthTip: 'Aprovecha esta claridad para ponerle orden primero a las áreas que hoy te cuestan más, sin exigirte perfección.',
      priorityCopy: 'Hoy tu cabeza está cargando demasiados pendientes y preocupaciones al mismo tiempo. Antes de intentar hacer más cosas, necesitas vaciar el ruido mental.',
      priorityWhy: 'Cuando la mente está saturada, todo se siente el doble de pesado: te cuesta concentrarte, duermes peor y cualquier imprevisto te drena.',
      microAction: 'Toma una hoja o nota del teléfono y escribe durante 3 minutos todo lo que tienes dando vueltas en la cabeza, sin ordenarlo ni filtrarlo. Luego subraya solo 2 cosas que sí importan hoy.',
      microActionWhy: 'Al pasar tus pendientes al papel, tu cerebro deja de repetirlos en círculo para “no olvidarlos” y baja la tensión casi de inmediato.',
      quote: '“Lo que escribo dejo de cargarlo.”',
      bandCopy: {
        low: 'Tu mente trae mucho ruido y pendientes acumulados; vaciarla en papel te dará alivio rápido.',
        mid: 'Alternas ratos de claridad con momentos de saturación o distracciones con el celular.',
        high: 'Mantienes buena calma mental, enfoque y capacidad para poner límites.'
      }
    },
    {
      id: 'tiempo',
      name: 'Tiempo',
      color: '#C67D5B',
      short: 'Estructura y ritmo diario',
      vidaLetter: 'D — Dirección (Ordenar prioridades sin saturarte)',
      weekLabel: 'Semana 2 · Productividad simple',
      toolName: 'Tu Día Base',
      strengthCopy: 'Tienes una buena noción de tus prioridades y logras darle forma a tu día sin vivir apagando incendios a cada hora.',
      strengthTip: 'Usa este buen sentido de orden para reservar un pequeño bloque fijo a tu área prioritaria cada semana.',
      priorityCopy: 'Sientes que el día se te escapa entre urgencias, prisas o improvisación. No necesitas una agenda rígida ni perfecta; necesitas un esqueleto simple que te sostenga.',
      priorityWhy: 'Sin 2 o 3 prioridades claras al arrancar, terminas muy ocupado al final del día pero con la sensación frustrante de no haber avanzado en lo importante.',
      microAction: 'Define hoy solo 3 momentos ancla para mañana: qué haces los primeros 10 minutos al despertar, cuál será tu prioridad número 1 y a qué hora cierras tus pendientes.',
      microActionWhy: 'Tener 3 puntos fijos en el día elimina la sensación de caos y te devuelve el control sin sentirte encerrado en un horario estricto.',
      quote: '“Un día ordenado no es perfecto. Es un día donde tú llevas el volante.”',
      bandCopy: {
        low: 'El día te está llevando con prisas e improvisación; necesitas 2 o 3 prioridades simples.',
        mid: 'Algunos días fluyen bien, pero en otros pierdes el ritmo entre urgencias.',
        high: 'Llevas buen control de tus mañanas, tus prioridades y el ritmo de tu semana.'
      }
    },
    {
      id: 'energia',
      name: 'Energía',
      color: '#6E8572',
      short: 'Descanso y cuidado personal',
      vidaLetter: 'I — Intención (Cuidar lo que te sostiene)',
      weekLabel: 'Semana 1 y 4 · Descanso real y Hoja SOS',
      toolName: 'Descanso real de 10 minutos',
      strengthCopy: 'Cuidas tu descanso y sabes reconocer cuándo parar. Esa energía estable es el combustible que te permite rendir sin agotarte.',
      strengthTip: 'Protege tus horas de sueño y pausas sin pantalla: son la base que sostiene todo lo demás en tu semana.',
      priorityCopy: 'Tu cansancio no siempre viene de hacer demasiado, sino de no darte pausas verdaderas, dormir poco o descansar pegado a las pantallas.',
      priorityWhy: 'Cuando la pila está baja, incluso las tareas fáciles se sienten cuesta arriba y cuesta el triple sostener cualquier buen hábito.',
      microAction: 'Regálate hoy 10 minutos de descanso verdadero: sin celular, sin televisión y sin hacer dos cosas a la vez. Respira profundo, camina despacio o quédate en silencio.',
      microActionWhy: 'Diez minutos reales sin estímulos ni pantallas le permiten a tu sistema nervioso bajar revoluciones y recuperar claridad.',
      quote: '“Descansar no es dejar de trabajar; es recuperar claridad.”',
      bandCopy: {
        low: 'Tu batería está baja y tu cuerpo pide pausas reales sin pantallas ni apuros.',
        mid: 'Tu energía alcanza para sacar el día, pero sueles terminar cansado y sin reserva.',
        high: 'Cuidas bien tu descanso, tu cuerpo y tu espacio cercano.'
      }
    },
    {
      id: 'dinero',
      name: 'Dinero',
      color: '#9B7B54',
      short: 'Claridad y control de gastos',
      vidaLetter: 'D — Dirección (Control básico sin drama)',
      weekLabel: 'Semana 3 · Orden del dinero',
      toolName: 'Mapa simple del dinero',
      strengthCopy: 'Sabes en qué se va tu dinero y tomas decisiones de gasto con calma. Esa claridad quita muchísimo estrés silencioso.',
      strengthTip: 'Sigue con ese hábito de revisar tus gastos: esa misma constancia te servirá para ordenar cualquier otra área de tu vida.',
      priorityCopy: 'La tensión con el dinero suele nacer de no mirarlo con calma o de pequeños gastos por impulso que se van acumulando sin darte cuenta.',
      priorityWhy: 'No saber exactamente en qué se va el dinero genera preocupación constante en el fondo de la mente, aunque no lo notes todo el día.',
      microAction: 'Anota hoy 1 solo gasto del día (grande o pequeño) y clasifícalo con una palabra: Necesario, Útil o Impulso. Sin culpa, solo para observar con claridad.',
      microActionWhy: 'Empezar con un solo gasto rompe el miedo a mirar tus números y activa decisiones mucho más conscientes desde el primer día.',
      quote: '“El dinero no se arregla pensando, se arregla registrando.”',
      bandCopy: {
        low: 'Hay incertidumbre o tensión con tus gastos; empezar a anotarlos de forma simple te dará mucha paz.',
        mid: 'Tienes una idea general de tus gastos, pero aún hay fugas pequeñas o compras por impulso.',
        high: 'Tienes claridad sobre en qué se va tu dinero y decides tus gastos con tranquilidad.'
      }
    },
    {
      id: 'habitos',
      name: 'Hábitos',
      color: '#5F6F7E',
      short: 'Pequeñas acciones sostenibles',
      vidaLetter: 'A — Acción (Lo pequeño sostenido cada día)',
      weekLabel: 'Semana 4 · Integración y Triple Ancla',
      toolName: 'Tu Triple Ancla',
      strengthCopy: 'Logras sostener pequeñas rutinas que mantienen tu día en pie incluso cuando no tienes ganas o la semana se complica.',
      strengthTip: 'Esa constancia es oro puro: agrega una sola acción mini en tu área más baja y verás cambios rápidos sin esfuerzo extremo.',
      priorityCopy: 'Intentar cambiar diez cosas a la vez agota y frustra. Cuando un día sale mal, es fácil sentir que “ya fallaste” y soltar todo.',
      priorityWhy: 'Sin una versión mínima para los días difíciles, cada tropiezo se vuelve un reinicio desde cero y te hace dudar de tu propia palabra.',
      microAction: 'Elige tu Triple Ancla para mañana: 1 acción pequeñísima para tu mente, 1 para tu día y 1 para tu orden/dinero. Que las tres juntas tomen menos de 10 minutos.',
      microActionWhy: 'Cumplir acciones tan pequeñas que casi no puedes fallar reconstruye tu confianza y crea impulso real día tras día.',
      quote: '“Lo pequeño, sostenido, sostiene todo.”',
      bandCopy: {
        low: 'Te cuesta sostener rutinas; necesitas bajar el tamaño de tus metas a versiones mínimas de 5 minutos.',
        mid: 'Sostienes algunos hábitos buenos, pero en días pesados se te rompen con facilidad.',
        high: 'Tienes constancia real y sabes retomar tu ritmo rápido cuando un día se desacomoda.'
      }
    }
  ];

  const SCALE_PRESETS = {
    estadoMente: [
      { v: 1, t: 'Muy saturada', d: 'Mil cosas a la vez y me cuesta pensar claro' },
      { v: 2, t: 'Inquieta', d: 'Con ruido y pendientes dando vueltas' },
      { v: 3, t: 'Neutra', d: 'A veces clara, a veces revuelta' },
      { v: 4, t: 'Enfocada', d: 'Casi siempre sé qué sigue' },
      { v: 5, t: 'Clara', d: 'En calma y con espacio para pensar' }
    ],
    frecuenciaPositiva: [
      { v: 1, t: 'Casi nunca', d: 'Me pasa muy rara vez' },
      { v: 2, t: 'Pocas veces', d: 'Solo de vez en cuando' },
      { v: 3, t: 'A veces', d: 'Unos días sí y otros no' },
      { v: 4, t: 'Casi siempre', d: 'La mayoría de los días' },
      { v: 5, t: 'Siempre', d: 'Es parte natural de mi semana' }
    ],
    ordenDia: [
      { v: 1, t: 'En caos', d: 'Voy apagando incendios todo el día' },
      { v: 2, t: 'Desordenado', d: 'Improviso la mayor parte del tiempo' },
      { v: 3, t: 'Estable a ratos', d: 'Algunos días fluyen y otros se rompen' },
      { v: 4, t: 'Casi estructurado', d: 'Tengo una rutina que suele funcionar' },
      { v: 5, t: 'Claro y estable', d: 'Sé qué importa y llevo el ritmo' }
    ],
    energiaNivel: [
      { v: 1, t: 'Muy baja', d: 'Me siento agotado casi todo el día' },
      { v: 2, t: 'Baja', d: 'Me cuesta arrancar o sostener el ritmo' },
      { v: 3, t: 'Normal', d: 'Alcanza, pero termino sin pila' },
      { v: 4, t: 'Buena', d: 'Me siento bien la mayor parte del día' },
      { v: 5, t: 'Alta y estable', d: 'Descanso bien y rindo sin agotarme' }
    ],
    dineroCalma: [
      { v: 1, t: 'Perdido o tenso', d: 'Prefiero ni mirar en qué se va el dinero' },
      { v: 2, t: 'Inquieto', d: 'Me genera estrés o gasto por impulso' },
      { v: 3, t: 'Más o menos', d: 'Llevo una idea general, pero sin orden claro' },
      { v: 4, t: 'Estable', d: 'Sé mis gastos principales y cuido lo básico' },
      { v: 5, t: 'Claro y tranquilo', d: 'Llevo control simple y decido con calma' }
    ],
    habitosCantidad: [
      { v: 1, t: 'Ninguno constante', d: 'Empiezo cosas pero me cuesta seguirlas' },
      { v: 2, t: '1 hábito irregular', d: 'Lo hago solo cuando tengo tiempo o ganas' },
      { v: 3, t: '1 a 2 hábitos', d: 'Los sostengo la mayoría de los días' },
      { v: 4, t: '3 a 4 hábitos', d: 'Tengo una base estable cada semana' },
      { v: 5, t: 'Muy consistente', d: 'Mis hábitos clave me sostienen diario' }
    ]
  };

  // 20 preguntas (4 por dimensión) fieles al PDF original y comprensibles para adultos y jóvenes
  const QUESTIONS = [
    // MENTE (1-4)
    {
      id: 'm1', dim: 'mente', context: 'Mente · Claridad general',
      text: '¿Cómo se siente tu mente en un día normal últimamente?',
      hint: 'Piensa en tu nivel de ruido mental, preocupaciones o pendientes.',
      scale: SCALE_PRESETS.estadoMente
    },
    {
      id: 'm2', dim: 'mente', context: 'Mente · Descarga mental',
      text: 'Cuando tienes muchos pendientes o preocupaciones, ¿los bajas a papel o a una lista en vez de cargarlos en la cabeza?',
      hint: 'Sacar las cosas de la mente reduce la ansiedad inmediata.',
      scale: SCALE_PRESETS.frecuenciaPositiva
    },
    {
      id: 'm3', dim: 'mente', context: 'Mente · Enfoque',
      text: '¿Logras concentrarte en una sola tarea sin brincar cada pocos minutos al celular o a otras cosas?',
      hint: 'Piensa en las notificaciones y distracciones diarias.',
      scale: SCALE_PRESETS.frecuenciaPositiva
    },
    {
      id: 'm4', dim: 'mente', context: 'Mente · Límites',
      text: '¿Te sientes capaz de decir “no” o dejar algo para después sin sentir culpa?',
      hint: 'Poner límites protege tu paz mental.',
      scale: SCALE_PRESETS.frecuenciaPositiva
    },

    // TIEMPO (5-8)
    {
      id: 't1', dim: 'tiempo', context: 'Tiempo · Estructura diaria',
      text: '¿Qué tan ordenados están tus días actualmente?',
      hint: 'Evalúa si sientes que llevas el volante o que el día te arrastra.',
      scale: SCALE_PRESETS.ordenDia
    },
    {
      id: 't2', dim: 'tiempo', context: 'Tiempo · Prioridades',
      text: 'Al empezar el día, ¿tienes claras las 2 o 3 cosas que de verdad importan hoy?',
      hint: 'No una lista interminable, solo lo esencial.',
      scale: SCALE_PRESETS.frecuenciaPositiva
    },
    {
      id: 't3', dim: 'tiempo', context: 'Tiempo · Mañanas',
      text: '¿Tus mañanas arrancan con calma en lugar de con prisas y apuros?',
      hint: 'Los primeros 15 minutos suelen marcar el tono del día.',
      scale: SCALE_PRESETS.frecuenciaPositiva
    },
    {
      id: 't4', dim: 'tiempo', context: 'Tiempo · Cierre del día',
      text: 'Al llegar la noche, ¿sientes que avanzaste en lo importante en vez de solo estar ocupado?',
      hint: 'Estar ocupado no siempre es avanzar.',
      scale: SCALE_PRESETS.frecuenciaPositiva
    },

    // ENERGÍA (9-12)
    {
      id: 'e1', dim: 'energia', context: 'Energía · Nivel general',
      text: '¿Cómo está tu nivel de energía durante la mayor parte del día?',
      hint: 'Considera tanto tu energía física como tus ganas.',
      scale: SCALE_PRESETS.energiaNivel
    },
    {
      id: 'e2', dim: 'energia', context: 'Energía · Descanso real',
      text: '¿Te das pausas de descanso verdadero (sin pantallas ni redes sociales) durante tu semana?',
      hint: 'Ver el teléfono cansa la mente aunque el cuerpo esté sentado.',
      scale: SCALE_PRESETS.frecuenciaPositiva
    },
    {
      id: 'e3', dim: 'energia', context: 'Energía · Sueño y cuerpo',
      text: '¿Duermes lo suficiente y cuidas lo básico de tu cuerpo (agua, movimiento o comida sin prisas)?',
      hint: 'Lo básico diario sostiene todo lo demás.',
      scale: SCALE_PRESETS.frecuenciaPositiva
    },
    {
      id: 'e4', dim: 'energia', context: 'Energía · Entorno',
      text: '¿Tu espacio cercano (escritorio, cuarto o mesa) te transmite calma en lugar de desorden?',
      hint: 'El desorden visual también consume energía mental.',
      scale: SCALE_PRESETS.frecuenciaPositiva
    },

    // DINERO (13-16)
    {
      id: 'd1', dim: 'dinero', context: 'Dinero · Sensación actual',
      text: '¿Cómo te sientes hoy respecto al manejo de tu dinero o tus gastos diarios?',
      hint: 'Si todavía no manejas ingresos propios, piensa en tus gastos, ahorros o dinero de la semana.',
      scale: SCALE_PRESETS.dineroCalma
    },
    {
      id: 'd2', dim: 'dinero', context: 'Dinero · Registro simple',
      text: '¿Sabes con claridad en qué se te va el dinero cada semana?',
      hint: 'No hace falta un Excel complejo; basta con tenerlo visible.',
      scale: SCALE_PRESETS.frecuenciaPositiva
    },
    {
      id: 'd3', dim: 'dinero', context: 'Dinero · Compras conscientes',
      text: 'Antes de comprar algo por antojo o prisa, ¿te detienes un momento a pensar si realmente lo necesitas?',
      hint: 'Distinguir entre necesario, útil y capricho.',
      scale: SCALE_PRESETS.frecuenciaPositiva
    },
    {
      id: 'd4', dim: 'dinero', context: 'Dinero · Tranquilidad',
      text: '¿Sientes que tus decisiones de gasto te acercan a estar más tranquilo el próximo mes?',
      hint: 'Ahorrar o evitar pequeños gastos innecesarios cuenta mucho.',
      scale: SCALE_PRESETS.frecuenciaPositiva
    },

    // HÁBITOS (17-20)
    {
      id: 'h1', dim: 'habitos', context: 'Hábitos · Constancia',
      text: '¿Cuántos hábitos positivos sostienes de forma constante hoy?',
      hint: 'Cuenta acciones simples que haces casi diario (leer, caminar, ordenar, anotar, descansar bien).',
      scale: SCALE_PRESETS.habitosCantidad
    },
    {
      id: 'h2', dim: 'habitos', context: 'Hábitos · Días difíciles',
      text: 'Cuando tienes un día malo o muy ocupado, ¿tienes una versión mínima de tus hábitos para no abandonar todo?',
      hint: 'Por ejemplo: hacer 5 minutos en vez de cero.',
      scale: SCALE_PRESETS.frecuenciaPositiva
    },
    {
      id: 'h3', dim: 'habitos', context: 'Hábitos · Regreso rápido',
      text: 'Si un día te sales de tu rutina, ¿logras retomarla al día siguiente sin regañarte ni rendirte?',
      hint: 'Volver rápido importa más que no fallar nunca.',
      scale: SCALE_PRESETS.frecuenciaPositiva
    },
    {
      id: 'h4', dim: 'habitos', context: 'Hábitos · Palabra contigo',
      text: 'Cuando te propones una acción pequeña para hoy, ¿sueles cumplirla?',
      hint: 'Recuperar tu palabra contigo mismo construye confianza.',
      scale: SCALE_PRESETS.frecuenciaPositiva
    }
  ];

  // Estado
  let state = loadState();
  let currentIndex = 0;
  let autoAdvanceTimer = null;
  let reflectionSyncTimer = null;

  function defaultState() {
    return {
      submissionId: null,
      answers: {},
      arrivalPhrase: '',
      completed: false,
      completedAt: null,
      microActionDone: false,
      reflection: '',
      feedbackSent: false,
      interest: {
        tier: 'Completa $199',
        contact: '',
        submitted: false
      },
      feedback: {
        profile: 'Adulto',
        clarity: 5,
        confusing: '',
        liked: ''
      }
    };
  }

  function loadState() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (!raw) return defaultState();
      const parsed = JSON.parse(raw);
      return {
        ...defaultState(),
        ...parsed,
        interest: { ...defaultState().interest, ...(parsed.interest || {}) },
        feedback: { ...defaultState().feedback, ...(parsed.feedback || {}) }
      };
    } catch (e) {
      return defaultState();
    }
  }

  function saveState() {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
    } catch (e) {
      // Ignorar si almacenamiento privado está bloqueado
    }
  }

  function ensureSubmissionId() {
    if (!state.submissionId) {
      state.submissionId = 'vida_' + Date.now() + '_' + Math.random().toString(36).slice(2, 7);
      saveState();
    }
    return state.submissionId;
  }

  function buildSheetsPayload(eventName) {
    const r = computeScores();
    const byDim = {};
    r.scores.forEach(s => {
      byDim[s.id] = s.score;
    });
    const baseReflection = (state.reflection || '').trim();
    const interestTag = state.interest && state.interest.submitted
      ? `[Interés 30D: ${state.interest.tier}${state.interest.contact.trim() ? ' · ' + state.interest.contact.trim() : ''}]`
      : '';
    const combinedReflection = [baseReflection, interestTag].filter(Boolean).join(' | ');
    return {
      submissionId: ensureSubmissionId(),
      event: eventName,
      overall: r.overall,
      mente: byDim.mente,
      tiempo: byDim.tiempo,
      energia: byDim.energia,
      dinero: byDim.dinero,
      habitos: byDim.habitos,
      strongest: r.strongest.name,
      priority: r.priority.name,
      arrivalPhrase: (state.arrivalPhrase || '').trim(),
      reflection: combinedReflection,
      feedbackProfile: state.feedback ? state.feedback.profile : '',
      feedbackClarity: state.feedback ? state.feedback.clarity : '',
      feedbackConfusing: state.feedback ? (state.feedback.confusing || '').trim() : '',
      feedbackLiked: state.feedback ? (state.feedback.liked || '').trim() : ''
    };
  }

  function syncToSheets(eventName) {
    if (!SHEETS_WEBHOOK_URL) return Promise.resolve(false);
    try {
      const payload = buildSheetsPayload(eventName);
      return fetch(SHEETS_WEBHOOK_URL, {
        method: 'POST',
        mode: 'no-cors',
        keepalive: true,
        headers: { 'Content-Type': 'text/plain;charset=utf-8' },
        body: JSON.stringify(payload)
      })
        .then(() => true)
        .catch(() => false);
    } catch (e) {
      return Promise.resolve(false);
    }
  }

  function scrollPageTop() {
    try {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } catch (e) {
      window.scrollTo(0, 0);
    }
  }

  function clearAutoAdvance() {
    if (autoAdvanceTimer) {
      clearTimeout(autoAdvanceTimer);
      autoAdvanceTimer = null;
    }
  }

  // Referencias DOM
  const els = {
    brandHomeBtn: document.getElementById('brand-home-btn'),
    headerPill: document.getElementById('header-progress-pill'),
    headerStepText: document.getElementById('header-step-text'),

    viewIntro: document.getElementById('view-intro'),
    viewQuiz: document.getElementById('view-quiz'),
    viewCheckin: document.getElementById('view-checkin'),
    viewResults: document.getElementById('view-results'),

    btnStart: document.getElementById('btn-start-test'),
    btnResume: document.getElementById('btn-resume-test'),
    btnViewSaved: document.getElementById('btn-view-saved-result'),

    quizDimBadge: document.getElementById('quiz-dim-badge'),
    quizCounter: document.getElementById('quiz-counter'),
    quizProgressbar: document.getElementById('quiz-progressbar'),
    quizProgressFill: document.getElementById('quiz-progress-fill'),
    questionSheet: document.getElementById('question-sheet'),
    questionContext: document.getElementById('question-context'),
    questionText: document.getElementById('question-text'),
    questionHint: document.getElementById('question-hint'),
    optionsList: document.getElementById('options-list'),
    btnPrevQ: document.getElementById('btn-prev-q'),
    btnNextQ: document.getElementById('btn-next-q'),

    checkinPhrase: document.getElementById('checkin-phrase'),
    btnBackToLastQ: document.getElementById('btn-back-to-last-q'),
    btnFinishTest: document.getElementById('btn-finish-test'),

    resultHeadline: document.getElementById('result-headline'),
    resultSubtitle: document.getElementById('result-subtitle'),
    savedPhraseBox: document.getElementById('saved-phrase-box'),
    savedPhraseText: document.getElementById('saved-phrase-text'),
    radarSvg: document.getElementById('radar-svg'),
    overallScoreValue: document.getElementById('overall-score-value'),
    overallScoreTag: document.getElementById('overall-score-tag'),
    overallDiagnosisText: document.getElementById('overall-diagnosis-text'),
    barsList: document.getElementById('bars-list'),

    strengthTitle: document.getElementById('strength-title'),
    strengthBody: document.getElementById('strength-body'),
    strengthTip: document.getElementById('strength-tip'),
    priorityTitle: document.getElementById('priority-title'),
    priorityBody: document.getElementById('priority-body'),
    priorityWhy: document.getElementById('priority-why'),
    priorityVidaLink: document.getElementById('priority-vida-link'),

    microactionToolTag: document.getElementById('microaction-tool-tag'),
    microactionText: document.getElementById('microaction-text'),
    microactionWhy: document.getElementById('microaction-why'),
    microactionQuote: document.getElementById('microaction-quote'),
    microactionDoneCheck: document.getElementById('microaction-done-check'),
    microactionDoneLabel: document.getElementById('microaction-done-label'),

    reflectionInput: document.getElementById('reflection-input'),
    reflectionStatus: document.getElementById('reflection-status'),
    btnCopySummary: document.getElementById('btn-copy-summary'),
    btnRetakeTest: document.getElementById('btn-retake-test'),

    fbProfileGroup: document.getElementById('fb-profile-group'),
    fbClarityGroup: document.getElementById('fb-clarity-group'),
    fbConfusing: document.getElementById('fb-confusing'),
    fbLiked: document.getElementById('fb-liked'),
    btnSendFeedback: document.getElementById('btn-send-feedback'),
    feedbackSendStatus: document.getElementById('feedback-send-status'),
    btnCopyWhatsapp: document.getElementById('btn-copy-whatsapp'),

    waitlistTierGroup: document.getElementById('waitlist-tier-group'),
    waitlistContact: document.getElementById('waitlist-contact'),
    btnWaitlistSubmit: document.getElementById('btn-waitlist-submit'),
    waitlistStatus: document.getElementById('waitlist-status'),

    toast: document.getElementById('toast')
  };

  let toastTimer = null;
  function showToast(msg) {
    els.toast.textContent = msg;
    els.toast.hidden = false;
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => {
      els.toast.hidden = true;
    }, 2800);
  }

  function showView(viewName) {
    clearAutoAdvance();
    els.viewIntro.hidden = viewName !== 'intro';
    els.viewQuiz.hidden = viewName !== 'quiz';
    els.viewCheckin.hidden = viewName !== 'checkin';
    els.viewResults.hidden = viewName !== 'results';
    els.headerPill.hidden = viewName !== 'quiz';
    scrollPageTop();
  }

  function refreshIntroButtons() {
    const answeredCount = Object.keys(state.answers).length;
    els.btnResume.hidden = !(answeredCount > 0 && !state.completed);
    els.btnViewSaved.hidden = !state.completed;
    if (answeredCount > 0 && !state.completed) {
      els.btnResume.textContent = `Continuar (${answeredCount}/${QUESTIONS.length})`;
    }
  }

  function renderQuestion(idx) {
    clearAutoAdvance();
    currentIndex = idx;
    const q = QUESTIONS[idx];
    const dim = DIMENSIONS.find(d => d.id === q.dim);
    const pct = Math.round(((idx + 1) / QUESTIONS.length) * 100);

    els.headerStepText.textContent = `${idx + 1} / ${QUESTIONS.length}`;
    els.quizDimBadge.textContent = dim.name;
    els.quizDimBadge.style.color = dim.color;
    els.quizCounter.textContent = `Pregunta ${idx + 1} de ${QUESTIONS.length}`;
    els.quizProgressFill.style.width = `${pct}%`;
    els.quizProgressFill.style.backgroundColor = dim.color;
    els.quizProgressbar.setAttribute('aria-valuenow', String(pct));

    els.questionContext.textContent = q.context;
    els.questionText.textContent = q.text;
    els.questionHint.textContent = q.hint;

    const currentVal = state.answers[q.id];
    els.optionsList.innerHTML = '';

    q.scale.forEach(opt => {
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'option-btn' + (currentVal === opt.v ? ' selected' : '');
      btn.setAttribute('role', 'radio');
      btn.setAttribute('aria-checked', currentVal === opt.v ? 'true' : 'false');
      btn.innerHTML = `
        <span class="option-num">${opt.v}</span>
        <span class="option-copy">
          <span class="option-title">${opt.t}</span>
          <span class="option-desc">${opt.d}</span>
        </span>
      `;
      btn.addEventListener('click', () => {
        clearAutoAdvance();
        state.answers[q.id] = opt.v;
        saveState();
        els.optionsList.querySelectorAll('.option-btn').forEach(b => {
          b.classList.remove('selected');
          b.setAttribute('aria-checked', 'false');
        });
        btn.classList.add('selected');
        btn.setAttribute('aria-checked', 'true');
        btn.blur();
        els.btnNextQ.disabled = false;

        // Avance fluido con breve pausa para confirmar la selección
        autoAdvanceTimer = setTimeout(() => {
          autoAdvanceTimer = null;
          if (currentIndex === idx) {
            goNextQuestion();
          }
        }, 240);
      });
      els.optionsList.appendChild(btn);
    });

    els.btnPrevQ.textContent = idx === 0 ? '← Inicio' : '← Anterior';
    els.btnNextQ.textContent = idx === QUESTIONS.length - 1 ? 'Último paso →' : 'Siguiente →';
    els.btnNextQ.disabled = !currentVal;

    // Transición clara y volver arriba para que en móvil siempre se vea la nueva pregunta
    if (els.questionSheet) {
      els.questionSheet.classList.remove('question-enter');
      void els.questionSheet.offsetWidth;
      els.questionSheet.classList.add('question-enter');
    }
    scrollPageTop();
  }

  function goNextQuestion() {
    clearAutoAdvance();
    const q = QUESTIONS[currentIndex];
    if (!state.answers[q.id]) return;
    if (currentIndex < QUESTIONS.length - 1) {
      renderQuestion(currentIndex + 1);
    } else {
      els.checkinPhrase.value = state.arrivalPhrase || '';
      showView('checkin');
    }
  }

  function computeScores() {
    const scores = DIMENSIONS.map(dim => {
      const dimQs = QUESTIONS.filter(q => q.dim === dim.id);
      const sum = dimQs.reduce((acc, q) => acc + (Number(state.answers[q.id]) || 0), 0);
      const avg = dimQs.length ? sum / dimQs.length : 0;
      return { ...dim, score: Number(avg.toFixed(1)) };
    });

    const overall = Number((scores.reduce((a, b) => a + b.score, 0) / scores.length).toFixed(1));
    const sorted = [...scores].sort((a, b) => b.score - a.score);
    return {
      scores,
      overall,
      strongest: sorted[0],
      priority: sorted[sorted.length - 1]
    };
  }

  function scoreLabel(val) {
    if (val < 2.2) return 'Mucho ruido';
    if (val < 3.1) return 'Pide orden pronto';
    if (val < 4.0) return 'En construcción';
    return 'Base sólida';
  }

  function overallLabel(val) {
    if (val < 2.3) return 'Momento de pausar y simplificar';
    if (val < 3.3) return 'Buen punto de reinicio';
    if (val < 4.2) return 'Estructura en marcha';
    return 'Vida con buena claridad';
  }

  function overallDiagnosis(val, strongest, priority) {
    if (val < 2.3) {
      return `Hoy sientes bastante ruido acumulado en tu día a día. No significa que estés haciendo todo mal, sino que necesitas parar un momento y simplificar. Tu mejor apoyo actual es ${strongest.name} (${strongest.score}/5), y el alivio más rápido vendrá al ordenar poco a poco ${priority.name} (${priority.score}/5).`;
    }
    if (val < 3.3) {
      return `Estás en un buen punto de reinicio: ya tienes bases que te sostienen —especialmente en ${strongest.name} (${strongest.score}/5)—, pero ${priority.name} (${priority.score}/5) te está quitando calma y energía. Con un ajuste pequeño ahí notarás la diferencia en toda tu semana.`;
    }
    if (val < 4.2) {
      return `Ya llevas una estructura saludable en marcha. Tu fortaleza hoy está en ${strongest.name} (${strongest.score}/5), y si le das un poco de atención a ${priority.name} (${priority.score}/5), tus días se sentirán mucho más ligeros y estables.`;
    }
    return `Tienes una vida con muy buena claridad y equilibrio general. Destacas especialmente en ${strongest.name} (${strongest.score}/5). Tu oportunidad de mejora fina está en ${priority.name} (${priority.score}/5) para sostener ese ritmo sin desgaste.`;
  }

  function dimensionBandNote(dim) {
    if (!dim.bandCopy) return dim.short;
    if (dim.score < 2.6) return dim.bandCopy.low;
    if (dim.score < 3.8) return dim.bandCopy.mid;
    return dim.bandCopy.high;
  }

  function renderRadar(scores) {
    const size = 360;
    const cx = size / 2;
    const cy = size / 2;
    const maxR = 112;
    const levels = 5;
    const count = scores.length;

    const pt = (index, ratio) => {
      const angle = (-Math.PI / 2) + (index * 2 * Math.PI / count);
      return {
        x: cx + Math.cos(angle) * maxR * ratio,
        y: cy + Math.sin(angle) * maxR * ratio
      };
    };

    let svg = '';
    // Rejilla concéntrica
    for (let lvl = 1; lvl <= levels; lvl++) {
      const ratio = lvl / levels;
      const points = scores.map((_, i) => {
        const p = pt(i, ratio);
        return `${p.x.toFixed(1)},${p.y.toFixed(1)}`;
      }).join(' ');
      svg += `<polygon points="${points}" fill="${lvl % 2 === 0 ? 'rgba(242,236,225,0.45)' : 'none'}" stroke="#DFD7C8" stroke-width="1" />`;
    }

    // Ejes radiales y etiquetas más grandes para lectura cómoda en móvil
    scores.forEach((s, i) => {
      const outer = pt(i, 1);
      svg += `<line x1="${cx}" y1="${cy}" x2="${outer.x.toFixed(1)}" y2="${outer.y.toFixed(1)}" stroke="#DFD7C8" stroke-width="1" />`;
      const lbl = pt(i, 1.25);
      const anchor = Math.abs(lbl.x - cx) < 12 ? 'middle' : (lbl.x > cx ? 'start' : 'end');
      svg += `<text x="${lbl.x.toFixed(1)}" y="${(lbl.y + 5).toFixed(1)}" text-anchor="${anchor}" fill="#1F1F1C" font-size="14.5" font-weight="700" font-family="Plus Jakarta Sans, sans-serif">${s.name}</text>`;
    });

    // Polígono del usuario
    const dataPoints = scores.map((s, i) => {
      const p = pt(i, Math.max(0.12, s.score / 5));
      return `${p.x.toFixed(1)},${p.y.toFixed(1)}`;
    }).join(' ');

    svg += `<polygon points="${dataPoints}" fill="rgba(74, 93, 78, 0.22)" stroke="#4A5D4E" stroke-width="2.8" stroke-linejoin="round" />`;

    // Puntos de cada dimensión
    scores.forEach((s, i) => {
      const p = pt(i, Math.max(0.12, s.score / 5));
      svg += `<circle cx="${p.x.toFixed(1)}" cy="${p.y.toFixed(1)}" r="5.5" fill="${s.color}" stroke="#FFFFFF" stroke-width="2" />`;
    });

    els.radarSvg.innerHTML = svg;
  }

  function renderResults() {
    const result = computeScores();

    els.resultHeadline.textContent = `Hoy tu mayor palanca de orden es ${result.priority.name}`;
    els.resultSubtitle.textContent = `Lo mejor de tu resultado está en ${result.strongest.name} (${result.strongest.score}/5) y tu punto más bajo está en ${result.priority.name} (${result.priority.score}/5). Empezar por ahí te devolverá calma con menos esfuerzo.`;

    if (state.arrivalPhrase && state.arrivalPhrase.trim()) {
      els.savedPhraseBox.hidden = false;
      els.savedPhraseText.textContent = `“${state.arrivalPhrase.trim()}”`;
    } else {
      els.savedPhraseBox.hidden = true;
    }

    renderRadar(result.scores);
    els.overallScoreValue.textContent = `${result.overall.toFixed(1)} / 5.0`;
    els.overallScoreTag.textContent = overallLabel(result.overall);
    if (els.overallDiagnosisText) {
      els.overallDiagnosisText.textContent = overallDiagnosis(result.overall, result.strongest, result.priority);
    }

    // Barras con lectura clara por dimensión
    els.barsList.innerHTML = '';
    result.scores.forEach(s => {
      const pct = Math.round((s.score / 5) * 100);
      const row = document.createElement('div');
      row.innerHTML = `
        <div class="bar-row-head">
          <span class="bar-name">${s.name}</span>
          <span class="bar-score"><strong>${s.score.toFixed(1)}</strong>/5 · ${scoreLabel(s.score)}</span>
        </div>
        <div class="bar-track">
          <div class="bar-fill" style="width: ${pct}%; background-color: ${s.color};"></div>
        </div>
        <p class="bar-note">${dimensionBandNote(s)}</p>
      `;
      els.barsList.appendChild(row);
    });

    // Lectura V.I.D.A.: Lo mejor y lo más bajo
    els.strengthTitle.textContent = `${result.strongest.name} (${result.strongest.score.toFixed(1)} / 5)`;
    els.strengthBody.textContent = result.strongest.strengthCopy;
    if (els.strengthTip) {
      els.strengthTip.innerHTML = `<strong>Cómo aprovecharlo:</strong> ${result.strongest.strengthTip}`;
    }

    els.priorityTitle.textContent = `${result.priority.name} (${result.priority.score.toFixed(1)} / 5)`;
    els.priorityBody.textContent = result.priority.priorityCopy;
    if (els.priorityWhy) {
      els.priorityWhy.innerHTML = `<strong>Por qué te pesa tanto:</strong> ${result.priority.priorityWhy}`;
    }
    els.priorityVidaLink.innerHTML = `<strong>En el método:</strong> ${result.priority.vidaLetter}<br/><span>${result.priority.weekLabel}</span>`;

    // Tip práctico de hoy (Micro-acción)
    els.microactionToolTag.textContent = result.priority.toolName;
    els.microactionText.textContent = result.priority.microAction;
    if (els.microactionWhy) {
      els.microactionWhy.innerHTML = `<strong>Por qué funciona este tip:</strong> ${result.priority.microActionWhy}`;
    }
    els.microactionQuote.textContent = result.priority.quote;
    els.microactionDoneCheck.checked = Boolean(state.microActionDone);
    updateMicroActionLabel();

    // Reflexión y feedback
    els.reflectionInput.value = state.reflection || '';
    syncFeedbackInputs();
    showView('results');
  }

  function updateMicroActionLabel() {
    els.microactionDoneLabel.textContent = state.microActionDone
      ? '¡Hecho! Hoy ya avanzaste 1% hacia tu orden'
      : 'Marcar este tip como hecho hoy';
  }

  function syncFeedbackInputs() {
    els.fbProfileGroup.querySelectorAll('.seg-btn').forEach(btn => {
      btn.classList.toggle('active', btn.dataset.profile === state.feedback.profile);
    });
    els.fbClarityGroup.querySelectorAll('.rate-btn').forEach(btn => {
      btn.classList.toggle('active', Number(btn.dataset.rate) === Number(state.feedback.clarity));
    });
    els.fbConfusing.value = state.feedback.confusing || '';
    els.fbLiked.value = state.feedback.liked || '';
    if (els.btnSendFeedback) {
      els.btnSendFeedback.textContent = state.feedbackSent ? 'Actualizar mi opinión' : 'Enviar mi opinión';
    }
    if (els.feedbackSendStatus) {
      els.feedbackSendStatus.hidden = !state.feedbackSent;
      if (state.feedbackSent) {
        els.feedbackSendStatus.textContent = '✓ ¡Gracias! Tu opinión y resultado ya quedaron guardados.';
      }
    }
    if (els.waitlistTierGroup && state.interest) {
      els.waitlistTierGroup.querySelectorAll('.tier-pick').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.tier === state.interest.tier);
      });
    }
    if (els.waitlistContact && state.interest) {
      els.waitlistContact.value = state.interest.contact || '';
    }
    if (els.btnWaitlistSubmit && state.interest) {
      els.btnWaitlistSubmit.textContent = state.interest.submitted
        ? '✓ ¡Anotado! Actualizar mi aviso'
        : 'Quiero que me avisen cuando salga';
    }
    if (els.waitlistStatus && state.interest) {
      els.waitlistStatus.hidden = !state.interest.submitted;
      if (state.interest.submitted) {
        els.waitlistStatus.textContent = `✓ Registramos tu interés (${state.interest.tier}). ¡Te avisaremos en cuanto salga!`;
      }
    }
  }

  async function copyText(text, okMsg) {
    try {
      await navigator.clipboard.writeText(text);
      showToast(okMsg);
    } catch (e) {
      const ta = document.createElement('textarea');
      ta.value = text;
      document.body.appendChild(ta);
      ta.select();
      document.execCommand('copy');
      ta.remove();
      showToast(okMsg);
    }
  }

  // EVENTOS
  els.brandHomeBtn.addEventListener('click', () => {
    refreshIntroButtons();
    showView('intro');
  });

  els.btnStart.addEventListener('click', () => {
    if (state.completed || Object.keys(state.answers).length > 0) {
      state = defaultState();
      saveState();
    }
    showView('quiz');
    renderQuestion(0);
  });

  els.btnResume.addEventListener('click', () => {
    const firstUnanswered = QUESTIONS.findIndex(q => !state.answers[q.id]);
    showView('quiz');
    renderQuestion(firstUnanswered === -1 ? QUESTIONS.length - 1 : firstUnanswered);
  });

  els.btnViewSaved.addEventListener('click', () => {
    renderResults();
  });

  els.btnPrevQ.addEventListener('click', () => {
    if (currentIndex === 0) {
      refreshIntroButtons();
      showView('intro');
    } else {
      renderQuestion(currentIndex - 1);
    }
  });

  els.btnNextQ.addEventListener('click', goNextQuestion);

  document.querySelectorAll('.quick-chip').forEach(chip => {
    chip.addEventListener('click', () => {
      els.checkinPhrase.value = chip.dataset.phrase;
      state.arrivalPhrase = chip.dataset.phrase;
      saveState();
    });
  });

  els.checkinPhrase.addEventListener('input', e => {
    state.arrivalPhrase = e.target.value;
    saveState();
  });

  els.btnBackToLastQ.addEventListener('click', () => {
    showView('quiz');
    renderQuestion(QUESTIONS.length - 1);
  });

  els.btnFinishTest.addEventListener('click', () => {
    state.arrivalPhrase = els.checkinPhrase.value.trim();
    state.completed = true;
    state.completedAt = new Date().toISOString();
    ensureSubmissionId();
    saveState();
    renderResults();
    syncToSheets('test_completado');
  });

  els.microactionDoneCheck.addEventListener('change', e => {
    state.microActionDone = e.target.checked;
    saveState();
    updateMicroActionLabel();
    if (state.microActionDone) {
      showToast('Micro-acción registrada para hoy');
    }
  });

  els.reflectionInput.addEventListener('input', e => {
    state.reflection = e.target.value;
    saveState();
    els.reflectionStatus.textContent = 'Guardado automáticamente';
    if (state.completed) {
      clearTimeout(reflectionSyncTimer);
      reflectionSyncTimer = setTimeout(() => {
        syncToSheets('reflexion_actualizada');
      }, 1500);
    }
  });

  els.btnCopySummary.addEventListener('click', () => {
    const r = computeScores();
    const lines = [
      'VIDA EN ORDEN — Mi resultado Test V.I.D.A.',
      `Nivel general: ${r.overall.toFixed(1)}/5.0 (${overallLabel(r.overall)})`,
      '',
      ...r.scores.map(s => `• ${s.name}: ${s.score.toFixed(1)}/5 (${scoreLabel(s.score)})`),
      '',
      `Base firme: ${r.strongest.name}`,
      `Prioridad hoy: ${r.priority.name} (${r.priority.toolName})`,
      state.reflection.trim() ? `Mi nota: ${state.reflection.trim()}` : ''
    ].filter(Boolean);
    copyText(lines.join('\n'), 'Resumen copiado al portapapeles');
  });

  els.btnRetakeTest.addEventListener('click', () => {
    state = defaultState();
    saveState();
    showView('quiz');
    renderQuestion(0);
  });

  els.fbProfileGroup.addEventListener('click', e => {
    const btn = e.target.closest('.seg-btn');
    if (!btn) return;
    state.feedback.profile = btn.dataset.profile;
    saveState();
    syncFeedbackInputs();
  });

  els.fbClarityGroup.addEventListener('click', e => {
    const btn = e.target.closest('.rate-btn');
    if (!btn) return;
    state.feedback.clarity = Number(btn.dataset.rate);
    saveState();
    syncFeedbackInputs();
  });

  els.fbConfusing.addEventListener('input', e => {
    state.feedback.confusing = e.target.value;
    saveState();
  });

  els.fbLiked.addEventListener('input', e => {
    state.feedback.liked = e.target.value;
    saveState();
  });

  if (els.btnSendFeedback) {
    els.btnSendFeedback.addEventListener('click', async () => {
      els.btnSendFeedback.disabled = true;
      els.btnSendFeedback.textContent = 'Enviando...';
      await syncToSheets('feedback_enviado');
      state.feedbackSent = true;
      saveState();
      els.btnSendFeedback.disabled = false;
      els.btnSendFeedback.textContent = 'Actualizar mi opinión';
      if (els.feedbackSendStatus) {
        els.feedbackSendStatus.hidden = false;
        els.feedbackSendStatus.textContent = '✓ ¡Gracias! Tu opinión y resultado ya quedaron guardados.';
      }
      showToast('¡Gracias! Tu opinión se guardó automáticamente');
    });
  }

  els.btnCopyWhatsapp.addEventListener('click', () => {
    const r = computeScores();
    const fb = state.feedback;
    syncToSheets('feedback_enviado');
    state.feedbackSent = true;
    saveState();
    syncFeedbackInputs();
    const msg = [
      '📋 *Feedback Prueba — Test V.I.D.A.*',
      `• Perfil: ${fb.profile}`,
      `• Claridad (1-5): ${fb.clarity}/5`,
      `• Nivel general test: ${r.overall.toFixed(1)}/5 (Prioridad: ${r.priority.name})`,
      `• ¿Algo confuso?: ${fb.confusing.trim() || 'Ninguna palabra o pregunta confusa'}`,
      `• ¿Qué gustó más?: ${fb.liked.trim() || 'Sin comentario adicional'}`
    ].join('\n');
    copyText(msg, 'Feedback copiado y guardado — listo para WhatsApp');
  });

  if (els.waitlistTierGroup) {
    els.waitlistTierGroup.addEventListener('click', e => {
      const btn = e.target.closest('.tier-pick');
      if (!btn) return;
      state.interest.tier = btn.dataset.tier;
      saveState();
      syncFeedbackInputs();
    });
  }

  if (els.waitlistContact) {
    els.waitlistContact.addEventListener('input', e => {
      state.interest.contact = e.target.value;
      saveState();
    });
  }

  if (els.btnWaitlistSubmit) {
    els.btnWaitlistSubmit.addEventListener('click', async () => {
      els.btnWaitlistSubmit.disabled = true;
      els.btnWaitlistSubmit.textContent = 'Guardando...';
      state.interest.submitted = true;
      state.interest.contact = els.waitlistContact ? els.waitlistContact.value.trim() : '';
      saveState();
      const evt = state.interest.tier.includes('99') && !state.interest.tier.includes('199')
        ? 'interes_30d_99'
        : 'interes_30d_199';
      await syncToSheets(evt);
      els.btnWaitlistSubmit.disabled = false;
      syncFeedbackInputs();
      showToast('¡Listo! Te avisaremos en cuanto salga');
    });
  }

  // Inicialización
  refreshIntroButtons();
  showView('intro');
})();
