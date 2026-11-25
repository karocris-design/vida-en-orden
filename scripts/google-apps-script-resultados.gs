const SHEET_NAME = 'Resultados';
const HEADERS = [
  'ID',
  'Fecha',
  'Estado',
  'Promedio',
  'Mente',
  'Tiempo',
  'Energía',
  'Dinero',
  'Hábitos',
  'Fortaleza',
  'Prioridad',
  'Frase de llegada',
  'Reflexión',
  'Perfil prueba',
  'Claridad (1-5)',
  '¿Algo confuso?',
  '¿Qué gustó más?'
];

function getOrSetupSheet() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let sheet = ss.getSheetByName(SHEET_NAME);
  if (!sheet) {
    sheet = ss.getSheets()[0];
    sheet.setName(SHEET_NAME);
  }
  if (sheet.getLastRow() === 0) {
    sheet.appendRow(HEADERS);
    sheet.getRange(1, 1, 1, HEADERS.length).setFontWeight('bold');
    sheet.setFrozenRows(1);
  }
  return sheet;
}

function doGet() {
  getOrSetupSheet();
  return ContentService
    .createTextOutput(JSON.stringify({ ok: true, message: 'VIDA EN ORDEN — Webhook activo' }))
    .setMimeType(ContentService.MimeType.JSON);
}

function doPost(e) {
  const lock = LockService.getScriptLock();
  lock.waitLock(10000);
  try {
    const raw = (e && e.postData && e.postData.contents) ? e.postData.contents : '{}';
    const data = JSON.parse(raw);
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    const sheet = getOrSetupSheet();
    const fecha = Utilities.formatDate(new Date(), ss.getSpreadsheetTimeZone(), 'yyyy-MM-dd HH:mm:ss');

    const rowValues = [
      data.submissionId || ('vida_' + Date.now()),
      fecha,
      data.event || 'test_completado',
      data.overall !== undefined ? data.overall : '',
      data.mente !== undefined ? data.mente : '',
      data.tiempo !== undefined ? data.tiempo : '',
      data.energia !== undefined ? data.energia : '',
      data.dinero !== undefined ? data.dinero : '',
      data.habitos !== undefined ? data.habitos : '',
      data.strongest || '',
      data.priority || '',
      data.arrivalPhrase || '',
      data.reflection || '',
      data.feedbackProfile || '',
      data.feedbackClarity !== undefined ? data.feedbackClarity : '',
      data.feedbackConfusing || '',
      data.feedbackLiked || ''
    ];

    let updated = false;
    if (data.submissionId && sheet.getLastRow() > 1) {
      const ids = sheet.getRange(2, 1, sheet.getLastRow() - 1, 1).getValues();
      for (let i = ids.length - 1; i >= 0; i--) {
        if (String(ids[i][0]) === String(data.submissionId)) {
          sheet.getRange(i + 2, 1, 1, rowValues.length).setValues([rowValues]);
          updated = true;
          break;
        }
      }
    }

    if (!updated) {
      sheet.appendRow(rowValues);
    }

    return ContentService
      .createTextOutput(JSON.stringify({ ok: true, updated: updated }))
      .setMimeType(ContentService.MimeType.JSON);
  } catch (err) {
    return ContentService
      .createTextOutput(JSON.stringify({ ok: false, error: String(err) }))
      .setMimeType(ContentService.MimeType.JSON);
  } finally {
    lock.releaseLock();
  }
}
