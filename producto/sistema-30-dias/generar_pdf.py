#!/usr/bin/env python3
"""
Generador Editorial de PDF — VIDA EN ORDEN (Sistema de 30 Días)
Produce dos ediciones limpias desde marca/design-tokens.json + contenido.json:
  1. Edición Digital Editorial (paleta crema/salvia/terracota)
  2. Edición Imprimible (fondo blanco, ahorro de tinta)

Limpia metadatos automáticamente con PyMuPDF para proteger el anonimato de la marca.
Funciona igual en Linux (nube) y macOS.
"""

import html
import json
import shutil
from pathlib import Path
import pymupdf
from playwright.sync_api import sync_playwright

BASE_DIR = Path(__file__).resolve().parent
REPO_ROOT = BASE_DIR.parent.parent
TOKENS_PATH = REPO_ROOT / "marca" / "design-tokens.json"
CONTENT_PATH = BASE_DIR / "contenido.json"
OUT_DIR = BASE_DIR / "output"


def esc(text: str) -> str:
    return html.escape(str(text or ""))


def logo_svg(size: int = 56, color: str = "#232320") -> str:
    """Emblema geométrico circular oficial de VIDA EN ORDEN (SVG vectorial)."""
    return f"""
    <svg width="{size}" height="{size}" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
      <circle cx="32" cy="32" r="30" fill="{color}"/>
      <circle cx="32" cy="32" r="20.5" stroke="#FAF7F2" stroke-width="2.4"/>
      <line x1="25.5" y1="12.5" x2="25.5" y2="51.5" stroke="#FAF7F2" stroke-width="2.1"/>
      <line x1="38.5" y1="12.5" x2="38.5" y2="51.5" stroke="#FAF7F2" stroke-width="2.1"/>
      <line x1="12.5" y1="25.5" x2="51.5" y2="25.5" stroke="#FAF7F2" stroke-width="2.1"/>
      <line x1="12.5" y1="38.5" x2="51.5" y2="38.5" stroke="#FAF7F2" stroke-width="2.1"/>
    </svg>
    """


ICONS = {
    "check": '<path d="M5 12.5l4.2 4.2L19 7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>',
    "heart": '<path d="M12 20s-7-4.5-8.5-8.8C2.4 8 4.4 5 7.6 5c1.9 0 3.4 1 4.4 2.4C13 6 14.5 5 16.4 5 19.6 5 21.6 8 20.5 11.2 19 15.5 12 20 12 20z" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/>',
    "compass": '<circle cx="12" cy="12" r="9" stroke="currentColor" stroke-width="1.8"/><polygon points="15.5,8.5 13.5,13.5 8.5,15.5 10.5,10.5" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round" fill="none"/>',
    "wallet": '<rect x="3" y="6" width="18" height="13" rx="2.5" stroke="currentColor" stroke-width="1.8"/><path d="M16 12.5h5" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/><circle cx="16.5" cy="12.5" r="1" fill="currentColor"/>',
    "play": '<circle cx="12" cy="12" r="9" stroke="currentColor" stroke-width="1.8"/><polygon points="10,8.5 16,12 10,15.5" fill="currentColor"/>',
    "leaf": '<path d="M5 19C5 11 11 5 19 5c0 8-6 14-14 14z" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/><path d="M5 19l7-7" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>',
    "clock": '<circle cx="12" cy="12" r="9" stroke="currentColor" stroke-width="1.8"/><path d="M12 7v5l3.5 2" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>',
    "anchor": '<circle cx="12" cy="6" r="2.2" stroke="currentColor" stroke-width="1.8"/><line x1="12" y1="8.2" x2="12" y2="19.5" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/><line x1="8" y1="11" x2="16" y2="11" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/><path d="M6 15.5a6 6 0 0 0 12 0" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>',
    "book": '<path d="M4 6.5A2.5 2.5 0 0 1 6.5 4H12v16H6.5A2.5 2.5 0 0 0 4 22V6.5zM20 6.5A2.5 2.5 0 0 0 17.5 4H12v16h5.5a2.5 2.5 0 0 1 2.5 2V6.5z" stroke="currentColor" stroke-width="1.7" stroke-linejoin="round"/>',
    "spark": '<path d="M12 3v18M3 12h18M6 6l12 12M18 6L6 18" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>',
}


def icon_svg(name: str, size: int = 20) -> str:
    body = ICONS.get(name, ICONS["check"])
    return f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">{body}</svg>'


def page_shell(page_num: int, running_section: str, body_html: str, extra_class: str = "", hide_chrome: bool = False) -> str:
    header = "" if hide_chrome else f"""
      <header class="p-header">
        <span class="p-brand">VIDA EN ORDEN</span>
        <span class="p-section">{esc(running_section)}</span>
      </header>
    """
    footer = "" if hide_chrome else f"""
      <footer class="p-footer">
        <span>Sistema de 30 Días · Menos ruido. Más vida.</span>
        <span class="p-num">{page_num:02d}</span>
      </footer>
    """
    return f"""
    <section class="page {extra_class}" data-page="{page_num}">
      {header}
      <div class="p-body">{body_html}</div>
      {footer}
    </section>
    """


def build_pages(tokens: dict, content: dict) -> tuple[list[str], dict]:
    """Construye las 87 páginas en orden exacto y devuelve (lista_html_paginas, mapa_indice)."""
    dim_colors = tokens["colors"]["dimensions"]
    meta = content["meta"]
    pages: list[str] = []
    toc_map: dict[str, int] = {}

    def add_page(running: str, body: str, extra_class: str = "", hide_chrome: bool = False, toc_key: str = "") -> int:
        pnum = len(pages) + 1
        if toc_key:
            toc_map[toc_key] = pnum
        pages.append(page_shell(pnum, running, body, extra_class=extra_class, hide_chrome=hide_chrome))
        return pnum

    # PÁG 1 — PORTADA
    add_page("", f"""
      <div class="cover-page">
        <div class="cover-top">
          <div class="cover-emblem">
            {logo_svg(64, "#4A5D4E")}
            <div>
              <div class="cover-brand-name">VIDA EN ORDEN</div>
              <div class="cover-edition">{esc(meta['edition'])} · {esc(meta['instagram'])}</div>
            </div>
          </div>
          <div class="cover-pill">Sistema práctico · 10 min/día</div>
        </div>

        <div class="cover-center">
          <div class="accent-rule"></div>
          <p class="eyebrow">CUADERNO DE TRABAJO Y MÉTODO</p>
          <h1 class="cover-h1">VIDA EN ORDEN</h1>
          <h2 class="cover-h2">Sistema de 30 Días</h2>
          <p class="cover-slogan">{esc(meta['subtitle'])}</p>

          <div class="cover-card">
            <div class="cover-card-kicker">{esc(meta['methodFull'])}</div>
            <p class="cover-card-copy">{esc(meta['tagline'])}</p>
            <div class="cover-pillars">
              <span><strong>V</strong> Vida</span>
              <span><strong>I</strong> Intención</span>
              <span><strong>D</strong> Dirección</span>
              <span><strong>A</strong> Acción</span>
            </div>
          </div>
        </div>

        <div class="cover-bottom">
          <div class="cover-dims">
            <span>Mente</span><i>·</i><span>Tiempo</span><i>·</i><span>Energía</span><i>·</i><span>Dinero</span><i>·</i><span>Hábitos</span>
          </div>
          <div class="cover-handle">{esc(meta['instagram'])} &nbsp;|&nbsp; {esc(meta['linktree'])}</div>
        </div>
      </div>
    """, extra_class="page-cover", hide_chrome=True)

    # PÁG 2 — MANIFIESTO
    m = content["manifesto"]
    m_paras = "".join(f"<p class='manifesto-p'>{esc(p)}</p>" for p in m["paragraphs"])
    add_page("Bienvenida", f"""
      <div class="manifesto-wrap">
        <p class="eyebrow">{esc(m['eyebrow'])}</p>
        <div class="short-rule"></div>
        <h1 class="manifesto-title">{esc(m['title'])}</h1>
        <p class="manifesto-lead">{esc(m['lead'])}</p>
        <div class="manifesto-body">{m_paras}</div>
        <div class="manifesto-close">{esc(m['closing'])}</div>
      </div>
    """)

    # PÁG 3 — ÍNDICE (placeholder que llenamos al final con números reales verificados)
    toc_index = len(pages)
    add_page("Índice", "__TOC_PLACEHOLDER__")

    # PÁG 4 — CÓMO FUNCIONA (CALMA... DAME 10 MINUTOS)
    intro = content["intro"]
    intro_blocks = ""
    for blk in intro["blocks"]:
        if "bullets" in blk:
            lis = "".join(f"<li>{esc(b)}</li>" for b in blk["bullets"])
            intro_blocks += f"""
              <div class="card card-tinted">
                <h3 class="card-h3">{esc(blk['title'])}</h3>
                <ul class="clean-list">{lis}</ul>
              </div>
            """
        else:
            intro_blocks += f"""
              <div class="card">
                <h3 class="card-h3">{esc(blk['title'])}</h3>
                <p class="card-p">{esc(blk['body'])}</p>
              </div>
            """
    add_page("Parte I · Fundamento", f"""
      <p class="eyebrow">{esc(intro['eyebrow'])}</p>
      <h1 class="h1">{esc(intro['title'])}</h1>
      <p class="lead">{esc(intro['lead'])}</p>
      <div class="stack-md">{intro_blocks}</div>
      <div class="callout-bar">{esc(intro['closing'])}</div>
    """, toc_key="parte1")

    # PÁG 5 — MÉTODO V.I.D.A.
    pillars_html = ""
    for p in content["vidaPillars"]:
        col = dim_colors[p["accent"]]
        qs = "".join(f"<li>{esc(q)}</li>" for q in p["questions"])
        pillars_html += f"""
          <div class="pillar-card" style="border-left: 4px solid {col};">
            <div class="pillar-head">
              <span class="pillar-letter" style="background:{col};">{esc(p['letter'])}</span>
              <div>
                <h3 class="pillar-name">{esc(p['name'])}</h3>
                <p class="pillar-tag">{esc(p['tagline'])}</p>
              </div>
            </div>
            <p class="pillar-body">{esc(p['body'])}</p>
            <ul class="pillar-qs">{qs}</ul>
          </div>
        """
    add_page("Parte I · Método V.I.D.A.", f"""
      <p class="eyebrow">Arquitectura del sistema</p>
      <h1 class="h1">El Método V.I.D.A.</h1>
      <p class="lead">Un sistema claro y aterrizado para ordenar tu vida desde adentro hacia afuera.</p>
      <div class="pillar-grid">{pillars_html}</div>
    """, toc_key="metodo_vida")

    # PÁG 6 — TEST INICIAL (5 DIMENSIONES HOMOLOGADO 1–5 + PUENTE A 3 BASES)
    dim_rows = ""
    for d in content["dimensions"]:
        col = dim_colors[d["id"]]
        opts = "".join(f"<span class='scale-chip'>{esc(s)}</span>" for s in d["scale"])
        dim_rows += f"""
          <div class="test-row">
            <div class="test-row-top">
              <div class="test-dim-label"><span class="dim-dot" style="background:{col};"></span><strong>{esc(d['name'])}</strong> — {esc(d['question'])}</div>
              <div class="score-box">Puntaje (1–5): ______</div>
            </div>
            <div class="scale-chips">{opts}</div>
          </div>
        """
    add_page("Parte I · Diagnóstico", f"""
      <p class="eyebrow">Punto de partida · 5 Dimensiones</p>
      <h1 class="h1">Test Inicial — ¿Dónde estás hoy?</h1>
      <p class="lead-sm">Responde con honestidad antes de empezar. No hay respuestas «buenas»: solo claridad para medir tu avance en el Día 30.</p>
      <div class="test-list">{dim_rows}</div>
      <div class="card card-compact mt-sm">
        <div class="two-col-tight">
          <div>
            <div class="field-label">Estado interior (describe en una frase cómo llegas hoy):</div>
            <div class="write-line"></div>
            <div class="write-line"></div>
          </div>
          <div class="total-score-box">
            <div class="total-label">PUNTAJE INICIAL</div>
            <div class="total-val">____ / 25</div>
            <div class="total-hint">Guarda este número para compararlo en la pág. 41.</div>
          </div>
        </div>
      </div>
      <div class="bridge-note">
        <strong>Cómo se conecta con tus 30 días:</strong> este test evalúa tus <strong>5 dimensiones</strong> (Mente, Tiempo, Energía, Dinero y Hábitos). Durante el mes las ordenarás a través de <strong>3 bases prácticas</strong> (Sem. 1: Mente y Energía · Sem. 2: Tiempo y Entorno · Sem. 3: Dinero) más <strong>1 semana de Integración y Hábitos</strong> (Sem. 4). También puedes hacer la versión interactiva con gráfica radar en <strong>{esc(meta['linktree'])}</strong>.
      </div>
    """, toc_key="test_inicial")

    # PÁG 7 — MINI-MANUAL (3 PASOS SIMPLES)
    add_page("Parte I · Guía rápida", f"""
      <p class="eyebrow">Cómo usar este cuaderno</p>
      <h1 class="h1">Mini-Manual en 3 pasos simples</h1>
      <p class="lead">No necesitas leer capítulos interminables. Solo sigue este ciclo de 10 minutos cada día.</p>

      <div class="step-flow">
        <div class="flow-card">
          <div class="flow-num">01</div>
          <div class="flow-content">
            <div class="flow-tag">20 segundos</div>
            <h3>Lee la Idea Clave del día</h3>
            <p>Una sola idea clara que da contexto a tu jornada. Sin teoría extra ni ruido innecesario.</p>
          </div>
        </div>
        <div class="flow-arrow">↓</div>
        <div class="flow-card">
          <div class="flow-num" style="background:#C67D5B;">02</div>
          <div class="flow-content">
            <div class="flow-tag" style="color:#C67D5B;">3 a 10 minutos</div>
            <h3>Haz tu Microacción</h3>
            <p>Pequeña, concreta y realizable incluso en un día pesado. Lo que se hace diario es lo que transforma.</p>
          </div>
        </div>
        <div class="flow-arrow">↓</div>
        <div class="flow-card">
          <div class="flow-num" style="background:#5F6F7E;">03</div>
          <div class="flow-content">
            <div class="flow-tag" style="color:#5F6F7E;">1 a 2 minutos</div>
            <h3>Registra en tu Cuaderno Diario</h3>
            <p>Anota tu estado mental (1–5), tu intención, tu gasto consciente y una reflexión breve (págs. 44–73).</p>
          </div>
        </div>
      </div>

      <div class="golden-rule">
        <div class="golden-kicker">REGLA DE ORO</div>
        <p class="golden-text">No busques un día perfecto. <strong>Busca un día ordenado.</strong></p>
      </div>
    """, toc_key="mini_manual")

    # PÁG 8 — HOJA MAESTRA (10 REGLAS)
    rule_icons = ["leaf", "play", "spark", "clock", "check", "anchor", "wallet", "heart", "book", "compass"]
    rules_html = ""
    for idx, rule in enumerate(content["tenRules"], 1):
        rules_html += f"""
          <div class="rule-item">
            <div class="rule-badge">{icon_svg(rule_icons[idx - 1], 18)}</div>
            <div>
              <div class="rule-num">REGLA {idx:02d}</div>
              <div class="rule-txt">{esc(rule)}</div>
            </div>
          </div>
        """
    add_page("Parte I · Hoja Maestra", f"""
      <p class="eyebrow">Principios del sistema</p>
      <h1 class="h1">Hoja Maestra — Las 10 Reglas</h1>
      <p class="lead">Vuelve a esta página cada vez que sientas prisa, saturación o ganas de complicar tu rutina.</p>
      <div class="rules-grid">{rules_html}</div>
      <div class="callout-bar mt-md">Lo simple se repite. Lo que se repite construye calma.</div>
    """, toc_key="hoja_maestra")

    # PÁGS 9–11 — LAS 3 BASES DEL MÉTODO
    for idx, base in enumerate(content["threeBases"]):
        col = dim_colors[base["accent"]]
        tools_li = "".join(f"<li>{esc(t)}</li>" for t in base["tools"])
        extra_note = ""
        if idx == 2:
            extra_note = """
              <div class="card card-tinted mt-md">
                <h3 class="card-h3">¿Y la cuarta semana? — Integración y Hábitos (Días 22 al 30)</h3>
                <p class="card-p">En la Semana 4 unirás las 3 bases dentro de tu <strong>Triple Ancla</strong> y tu <strong>Día Base</strong>, para que el orden deje de depender de fuerza de voluntad y se vuelva tu forma natural de vivir.</p>
              </div>
            """
        add_page(f"Parte I · Las 3 Bases ({idx + 1}/3)", f"""
          <div class="base-page">
            <p class="eyebrow" style="color:{col};">LAS 3 BASES DEL MÉTODO V.I.D.A. · BASE {esc(base['num'])}</p>
            <h1 class="h1">{esc(base['title'])}</h1>
            <div class="dim-pill" style="border-color:{col}; color:{col};">{esc(base['dimensionsLink'])}</div>

            <div class="statement-card" style="border-left: 5px solid {col};">
              <p class="statement-big">{esc(base['statement'])}</p>
              <p class="statement-sub">{esc(base['body'])}</p>
            </div>

            <div class="card mt-md">
              <h3 class="card-h3">Lo trabajarás con:</h3>
              <ul class="clean-list clean-list-lg">{tools_li}</ul>
            </div>

            {extra_note}

            <blockquote class="editorial-quote" style="border-top-color:{col};">
              «{esc(base['quote'])}»
            </blockquote>
          </div>
        """, toc_key="tres_bases" if idx == 0 else "")

    # PÁG 12 — MAPA DEL MÉTODO (VISTA GENERAL — 5 PASOS DIARIOS)
    steps_html = ""
    for st in content["methodSteps"]:
        steps_html += f"""
          <div class="map-row">
            <div class="map-num">{esc(st['num'])}</div>
            <div class="map-card">
              <h3>{esc(st['title'])}</h3>
              <p>{esc(st['desc'])}</p>
            </div>
          </div>
        """
    add_page("Parte I · Mapa del Método", f"""
      <p class="eyebrow">Vista general diaria</p>
      <h1 class="h1">Mapa del Método — Tu ciclo diario</h1>
      <p class="lead">Es simple a propósito: lo que puedes sostener todos los días es lo que de verdad transforma.</p>
      <div class="map-timeline">{steps_html}</div>
      <div class="golden-rule mt-md">
        <div class="golden-kicker">EL MÉTODO COMPLETO EN UNA FRASE</div>
        <p class="golden-text"><strong>Haz menos, pero hazlo cada día.</strong></p>
      </div>
    """, toc_key="mapa_metodo")

    # PÁG 13 — PREPARACIÓN ANTES DE EMPEZAR
    need_li = "".join(f"<li><span class='mk-good'>✓</span><span>{esc(x)}</span></li>" for x in content["preparation"]["need"])
    avoid_li = "".join(f"<li><span class='mk-bad'>✕</span><span>{esc(x)}</span></li>" for x in content["preparation"]["avoid"])
    add_page("Parte I · Preparación", f"""
      <p class="eyebrow">Antes del Día 1</p>
      <h1 class="h1">Preparación antes de empezar</h1>
      <p class="lead">El orden no nace del entusiasmo del lunes: <strong>nace de la intención bien puesta</strong>.</p>
      <div class="stack-md">
        <div class="card card-sage-border">
          <h3 class="card-h3" style="color:#4A5D4E;">Qué necesitas</h3>
          <ul class="icon-list">{need_li}</ul>
        </div>
        <div class="card card-terra-border">
          <h3 class="card-h3" style="color:#C67D5B;">Qué evitar</h3>
          <ul class="icon-list">{avoid_li}</ul>
        </div>
      </div>
    """)

    # PÁG 14 — CÓMO SE VE UN DÍA ORDENADO
    ord_li = "".join(f"<li><span class='ord-dot'></span><span>{esc(x)}</span></li>" for x in content["orderedDay"])
    add_page("Parte I · Horizonte", f"""
      <p class="eyebrow">Tu referencia cotidiana</p>
      <h1 class="h1">Cómo se ve un día ordenado</h1>
      <p class="lead">Un día ordenado no es un día lleno de pendientes tachados… <strong>es un día claro.</strong></p>
      <div class="card mt-md">
        <ul class="ordered-list">{ord_li}</ul>
      </div>
      <div class="hero-quote-box mt-lg">
        <p class="hero-quote">«Un día ordenado no es perfecto.<br/>Es un día donde tú llevas el volante.»</p>
      </div>
    """)

    # PARTE II — SEMANAS 1 A 4 (Págs 15 a 39)
    for w in content["weeks"]:
        wcol = dim_colors[w["accent"]]
        running = f"Semana {w['number']} · {w['title']} ({w['daysRange']})"

        # Portada de semana
        add_page(f"Parte II · Semana {w['number']}", f"""
          <div class="week-cover">
            <div class="week-badge" style="background:{wcol};">SEMANA {w['number']} · {esc(w['daysRange'].upper())}</div>
            <h1 class="week-cover-title">{esc(w['title'])}</h1>
            <div class="week-rule" style="background:{wcol};"></div>
            <p class="week-motto">«{esc(w['motto'])}»</p>
            <p class="week-focus">{esc(w['focus'])}</p>
            <div class="week-days-preview">
              {"".join(f"<div class='wdp-row'><span>Día {d['day']:02d}</span><strong>{esc(d['title'])}</strong></div>" for d in w['days'])}
            </div>
          </div>
        """, extra_class="page-week-cover", toc_key=f"semana_{w['number']}")

        # Días en pares (2 días por página; el último impar comparte página con Resultado Esperado)
        days = w["days"]
        i = 0
        while i < len(days):
            pair = days[i:i + 2]
            if len(pair) == 2:
                blocks = ""
                for d in pair:
                    blocks += f"""
                      <article class="day-card" style="border-top: 3px solid {wcol};">
                        <div class="day-head">
                          <span class="day-check">☐</span>
                          <span class="day-num" style="color:{wcol};">DÍA {d['day']:02d}</span>
                          <h2 class="day-title">{esc(d['title'])}</h2>
                        </div>
                        <p class="day-idea"><strong>Idea clave:</strong> {esc(d['idea'])}</p>
                        <div class="day-box">
                          <div class="day-box-label" style="color:{wcol};">MICROACCIÓN (3–10 MIN)</div>
                          <p>{esc(d['microaction'])}</p>
                        </div>
                        <p class="day-expense"><strong>Gasto consciente:</strong> {esc(d['expense'])}</p>
                        <div class="day-note-wrap">
                          <span class="day-note-label">Nota rápida:</span>
                          <div class="write-line-inline"></div>
                        </div>
                        <p class="day-quote">«{esc(d['quote'])}»</p>
                      </article>
                    """
                add_page(running, f'<div class="day-pair">{blocks}</div>')
            else:
                d = pair[0]
                outcomes_li = "".join(f"<li>{esc(o)}</li>" for o in w["expectedOutcome"])
                add_page(running, f"""
                  <div class="day-pair">
                    <article class="day-card" style="border-top: 3px solid {wcol};">
                      <div class="day-head">
                        <span class="day-check">☐</span>
                        <span class="day-num" style="color:{wcol};">DÍA {d['day']:02d}</span>
                        <h2 class="day-title">{esc(d['title'])}</h2>
                      </div>
                      <p class="day-idea"><strong>Idea clave:</strong> {esc(d['idea'])}</p>
                      <div class="day-box">
                        <div class="day-box-label" style="color:{wcol};">MICROACCIÓN (3–10 MIN)</div>
                        <p>{esc(d['microaction'])}</p>
                      </div>
                      <p class="day-expense"><strong>Gasto consciente:</strong> {esc(d['expense'])}</p>
                      <div class="day-note-wrap">
                        <span class="day-note-label">Nota rápida:</span>
                        <div class="write-line-inline"></div>
                      </div>
                      <p class="day-quote">«{esc(d['quote'])}»</p>
                    </article>

                    <div class="outcome-card" style="border-left: 5px solid {wcol};">
                      <div class="outcome-kicker" style="color:{wcol};">CIERRE DE SEMANA {w['number']} · {esc(w['title'].upper())}</div>
                      <h3 class="outcome-title">Resultado esperado de la Semana {w['number']}</h3>
                      <ul class="clean-list">{outcomes_li}</ul>
                    </div>
                  </div>
                """)
            i += 2

        # Checklist semanal
        chk_li = "".join(f"<li><span class='chk-box'>☐</span><span>{esc(item)}</span></li>" for item in content["weeklyChecklist"])
        add_page(f"Checklist · Semana {w['number']}", f"""
          <p class="eyebrow" style="color:{wcol};">Revisión semanal · Semana {w['number']} ({esc(w['daysRange'])})</p>
          <h1 class="h1">Checklist Semanal — ¿Cómo voy?</h1>
          <p class="lead-sm">Marca con honestidad lo que sostuviste esta semana. Recuerda: avanzar imperfecto vale más que no empezar.</p>
          <div class="card">
            <ul class="checklist">{chk_li}</ul>
          </div>
          <div class="card mt-md">
            <div class="field-label">Comentario final de la Semana {w['number']} (qué me funcionó mejor y qué ajustaré):</div>
            <div class="write-line"></div>
            <div class="write-line"></div>
            <div class="write-line"></div>
          </div>
        """)

    # PÁG 40 — MANTENIMIENTO MENSUAL (CORREGIDO: 3 LÍNEAS EN TRIPLE ANCLA + LÍNEA EN ESTADO INTERIOR)
    add_page("Cierre del Ciclo · Mantenimiento", f"""
      <p class="eyebrow">Reseteo mensual · 10 minutos</p>
      <h1 class="h1">Mantenimiento Mensual</h1>
      <p class="lead-sm">Repite esta hoja al cerrar cada mes para mantener tu sistema vivo, ligero y adaptado a tu realidad.</p>

      <div class="stack-sm">
        <div class="card card-compact">
          <h3 class="card-h3">1. Día Base</h3>
          <p class="inline-q">¿Lo tengo claro y vigente? &nbsp;&nbsp; ☐ Sí &nbsp;&nbsp;&nbsp; ☐ Necesita ajuste</p>
          <div class="field-label mt-xs">Ajustes para el próximo mes:</div>
          <div class="write-line"></div>
        </div>

        <div class="card card-compact">
          <h3 class="card-h3">2. Triple Ancla (tus 3 hábitos esenciales)</h3>
          <div class="num-line"><span>1.</span><div class="write-line-inline"></div></div>
          <div class="num-line"><span>2.</span><div class="write-line-inline"></div></div>
          <div class="num-line"><span>3.</span><div class="write-line-inline"></div></div>
        </div>

        <div class="card card-compact">
          <h3 class="card-h3">3. Dinero — Piloto Simple</h3>
          <div class="two-col-even">
            <div><div class="field-label">Límite semanal ($):</div><div class="write-line"></div></div>
            <div><div class="field-label">Impulsos permitidos (máx. 1–2):</div><div class="write-line"></div></div>
          </div>
        </div>

        <div class="card card-compact">
          <h3 class="card-h3">4. Microorden del Hogar</h3>
          <div class="field-label">Espacio clave a despejar o mantener este mes:</div>
          <div class="write-line"></div>
        </div>

        <div class="card card-compact">
          <h3 class="card-h3">5. Estado interior (en una palabra o frase corta)</h3>
          <div class="write-line"></div>
        </div>
      </div>
    """, toc_key="mantenimiento")

    # PÁG 41 — EVALUACIÓN FINAL: COMPARATIVA DÍA 1 VS. DÍA 30 + 10 LOGROS
    comp_rows = ""
    for d in content["dimensions"]:
        col = dim_colors[d["id"]]
        comp_rows += f"""
          <tr>
            <td><span class="dim-dot" style="background:{col};"></span><strong>{esc(d['name'])}</strong></td>
            <td class="td-center">____ / 5</td>
            <td class="td-center">____ / 5</td>
            <td class="td-center">______</td>
          </tr>
        """
    ach_li = "".join(f"<li><span class='chk-box'>☐</span><span>{esc(a)}</span></li>" for a in content["finalAchievements"])
    add_page("Cierre del Ciclo · Evaluación Final", f"""
      <p class="eyebrow">Día 1 vs. Día 30</p>
      <h1 class="h1">Evaluación Final — Tu avance real</h1>
      <p class="lead-sm">Después de 30 días no busques perfección: busca verdad. Traslada tus puntajes de la pág. 06 y evalúa cómo llegas hoy.</p>

      <table class="compare-table">
        <thead>
          <tr>
            <th>Dimensión V.I.D.A.</th>
            <th class="td-center">Día 1 (pág. 06)</th>
            <th class="td-center">Día 30 (hoy)</th>
            <th class="td-center">Cambio (+ / =)</th>
          </tr>
        </thead>
        <tbody>
          {comp_rows}
          <tr class="tr-total">
            <td><strong>Puntaje Total</strong></td>
            <td class="td-center"><strong>____ / 25</strong></td>
            <td class="td-center"><strong>____ / 25</strong></td>
            <td class="td-center"><strong>______</strong></td>
          </tr>
        </tbody>
      </table>

      <div class="card card-compact mt-md">
        <h3 class="card-h3">Marca lo que hoy forma parte de tu vida:</h3>
        <ul class="checklist checklist-tight">{ach_li}</ul>
      </div>
    """, toc_key="evaluacion_final")

    # PÁG 42 — CARTA DE CIERRE (REINVENCIÓN EN 30 DÍAS)
    cl = content["closingLetter"]
    cl_paras = "".join(f"<p class='letter-p'>{esc(p)}</p>" for p in cl["paragraphs"])
    cl_close = "".join(f"<p class='letter-close-line'>{esc(c)}</p>" for c in cl["closingLines"])
    add_page("Cierre del Ciclo", f"""
      <div class="letter-wrap">
        <p class="eyebrow">{esc(cl['eyebrow'])}</p>
        <h1 class="h1">{esc(cl['title'])}</h1>
        <div class="short-rule"></div>
        <div class="letter-body">{cl_paras}</div>
        <div class="letter-footer-box">{cl_close}</div>
      </div>
    """)

    # PARTE III — CUADERNO DIARIO (PORTADA + EXACTAMENTE 30 PÁGINAS NUMERADAS DÍA 01 A DÍA 30)
    add_page("Parte III · Cuaderno Diario", f"""
      <div class="section-cover">
        <div class="week-badge" style="background:#4A5D4E;">PARTE III · REGISTRO DIARIO</div>
        <h1 class="week-cover-title">Cuaderno Diario</h1>
        <h2 class="section-cover-sub">30 Días · 30 Frases</h2>
        <div class="week-rule" style="background:#4A5D4E;"></div>
        <p class="section-cover-copy">
          Este cuaderno es tu espacio diario para respirar, enfocarte y volver a lo esencial.
          Aquí no necesitas perfección, solo honestidad y una microacción que mantenga tu vida en orden, un día a la vez.
        </p>
        <p class="section-cover-copy">
          Cada hoja corresponde a un día exacto del sistema, con su frase guía y el registro rápido de tu estado mental, intención, microacción y gasto consciente.
        </p>
        <div class="section-cover-quote">«Lo pequeño que registres aquí… será lo grande que cambie allá afuera.»</div>
      </div>
    """, extra_class="page-week-cover", toc_key="cuaderno_diario")

    all_days = []
    for w in content["weeks"]:
        for d in w["days"]:
            all_days.append((w, d))

    assert len(all_days) == 30, f"Se esperaban 30 días exactos, hay {len(all_days)}"

    for w, d in all_days:
        wcol = dim_colors[w["accent"]]
        add_page(f"Cuaderno Diario · Semana {w['number']}", f"""
          <div class="diario-head" style="border-left: 4px solid {wcol};">
            <div class="diario-top-row">
              <span class="diario-day-tag" style="background:{wcol};">DÍA {d['day']:02d} / 30</span>
              <span class="diario-date">Fecha: _____ / _____ / _______</span>
            </div>
            <h2 class="diario-title">{esc(d['title'])}</h2>
            <p class="diario-quote">«{esc(d['quote'])}»</p>
          </div>

          <div class="diario-section">
            <div class="diario-label">1. Estado mental hoy <span class="diario-hint">(encierra cómo llegas)</span></div>
            <div class="mood-scale">
              <span><strong>1</strong> Saturada</span>
              <span><strong>2</strong> Inquieta</span>
              <span><strong>3</strong> Neutra</span>
              <span><strong>4</strong> Enfocada</span>
              <span><strong>5</strong> Clara</span>
            </div>
          </div>

          <div class="diario-section">
            <div class="diario-label">2. Intención del día <span class="diario-hint">(tu foco o TPU de hoy)</span></div>
            <div class="write-line"></div>
            <div class="write-line"></div>
          </div>

          <div class="diario-section">
            <div class="diario-label-row">
              <span class="diario-label">3. Microacción del día</span>
              <span class="diario-done">☐ Cumplida</span>
            </div>
            <div class="diario-micro-reminder">{esc(d['microaction'])}</div>
            <div class="write-line"></div>
            <div class="write-line"></div>
          </div>

          <div class="diario-section">
            <div class="diario-label">4. Gasto consciente <span class="diario-hint">(marca N = Necesario · U = Útil · I = Impulso)</span></div>
            <table class="expense-mini-table">
              <thead>
                <tr>
                  <th style="width:52%;">Concepto</th>
                  <th style="width:24%;">Monto ($)</th>
                  <th style="width:24%; text-align:center;">Regla 3–2–1</th>
                </tr>
              </thead>
              <tbody>
                <tr><td></td><td></td><td class="td-center">N &nbsp;·&nbsp; U &nbsp;·&nbsp; I</td></tr>
                <tr><td></td><td></td><td class="td-center">N &nbsp;·&nbsp; U &nbsp;·&nbsp; I</td></tr>
                <tr><td></td><td></td><td class="td-center">N &nbsp;·&nbsp; U &nbsp;·&nbsp; I</td></tr>
              </tbody>
            </table>
          </div>

          <div class="diario-section">
            <div class="diario-label">5. Reflexión breve del día <span class="diario-hint">(¿avancé 1% hoy? ¿qué aprendí?)</span></div>
            <div class="write-line"></div>
            <div class="write-line"></div>
            <div class="write-line"></div>
            <div class="write-line"></div>
          </div>
        """)

    # PARTE IV — KIT DE HERRAMIENTAS, TABLAS Y PLANTILLAS (Págs 74 a 85)
    add_page("Parte IV · Kit de Herramientas", f"""
      <div class="section-cover">
        <div class="week-badge" style="background:#C67D5B;">PARTE IV · ANEXOS Y PLANTILLAS</div>
        <h1 class="week-cover-title">Kit de Herramientas</h1>
        <h2 class="section-cover-sub">2 Tablas Semanales + 6 Plantillas Prácticas</h2>
        <div class="week-rule" style="background:#C67D5B;"></div>
        <p class="section-cover-copy">
          Herramientas simples para sostener tu semana, tu energía y tu dinero mucho más allá del Día 30.
        </p>
        <p class="section-cover-copy">
          Úsalas en tu tableta digital o imprímelas y pégalas en un lugar visible. Prácticas. Claras. Repetibles.
        </p>
        <div class="section-cover-quote">«Menos ruido. Más vida.»</div>
      </div>
    """, extra_class="page-week-cover", toc_key="kit_herramientas")

    # PÁG 75 — INTRODUCCIÓN AL KIT + TPU
    ki = content["kitIntro"]
    ki_items = "".join(f"<li><strong>{esc(it['label'])}:</strong> {esc(it['desc'])}</li>" for it in ki["items"])
    add_page("Parte IV · Introducción al Kit", f"""
      <p class="eyebrow">{esc(ki['eyebrow'])}</p>
      <h1 class="h1">{esc(ki['title'])}</h1>
      <p class="lead-sm">{esc(ki['lead'])}</p>

      <div class="card card-terra-border mt-sm">
        <h3 class="card-h3" style="color:#C67D5B;">{esc(ki['tpuBox']['title'])}</h3>
        <p class="card-p">{esc(ki['tpuBox']['body'])}</p>
      </div>

      <div class="card mt-md">
        <h3 class="card-h3">Qué incluye este Kit (8 recursos)</h3>
        <ul class="clean-list">{ki_items}</ul>
      </div>

      <div class="callout-bar mt-md">Úsalas sin perfeccionismo. Úsalas para sostenerte y afinar tu vida en orden.</div>
    """)

    # PÁG 76 — TABLA 1: REGISTRO SIMPLE DE LA SEMANA (CORREGIDA)
    add_page("Parte IV · Finanzas Semanales", f"""
      <p class="eyebrow" style="color:#9B7B54;">Anexo financiero · Semana 3 (Días 15 al 21) o cualquier semana</p>
      <h1 class="h1">Tabla 1 — Registro Simple de la Semana</h1>
      <p class="lead-sm">Marca solo lo esencial. Nada de adornos ni culpa: claridad en blanco y negro.</p>

      <div class="stack-sm">
        <div class="card card-compact">
          <div class="two-col-even">
            <div><div class="field-label">Semana del:</div><div class="write-line"></div></div>
            <div><div class="field-label">1. Gasto total de la semana ($):</div><div class="write-line"></div></div>
          </div>
        </div>

        <div class="card card-compact">
          <h3 class="card-h3">2. Fugas pequeñas detectadas (máx. 3)</h3>
          <div class="num-line"><span>•</span><div class="write-line-inline"></div></div>
          <div class="num-line"><span>•</span><div class="write-line-inline"></div></div>
          <div class="num-line"><span>•</span><div class="write-line-inline"></div></div>
        </div>

        <div class="card card-compact">
          <h3 class="card-h3">3. Clasificación según Regla 3–2–1</h3>
          <div class="three-col-box">
            <div>
              <div class="cat-badge cat-3">3 · Necesarios</div>
              <div class="write-line"></div>
              <div class="write-line"></div>
              <div class="write-line"></div>
            </div>
            <div>
              <div class="cat-badge cat-2">2 · Útiles</div>
              <div class="write-line"></div>
              <div class="write-line"></div>
              <div class="write-line"></div>
            </div>
            <div>
              <div class="cat-badge cat-1">1 · Impulsos</div>
              <div class="write-line"></div>
              <div class="write-line"></div>
              <div class="write-line"></div>
            </div>
          </div>
        </div>

        <div class="card card-compact">
          <h3 class="card-h3">4. Ajuste concreto elegido para la próxima semana</h3>
          <div class="write-line"></div>
          <div class="write-line"></div>
        </div>

        <div class="card card-compact">
          <h3 class="card-h3">5. Nota personal (cómo me sentí con mis decisiones)</h3>
          <div class="write-line"></div>
          <div class="write-line"></div>
        </div>
      </div>
    """, toc_key="tablas_finanzas")

    # PÁG 77 — TABLA 2: SEGUIMIENTO DE MINI-METAS (CORREGIDA)
    add_page("Parte IV · Finanzas Semanales", f"""
      <p class="eyebrow" style="color:#9B7B54;">Anexo financiero · Constancia semanal</p>
      <h1 class="h1">Tabla 2 — Seguimiento de Mini-Metas</h1>
      <p class="lead-sm">Pequeños acuerdos semanales que entrenan tu calma financiera sin sacrificios extremos.</p>

      <div class="stack-sm">
        <div class="card card-compact">
          <h3 class="card-h3">1. Mini-colchón semanal definido</h3>
          <div class="two-col-even mt-xs">
            <div><div class="field-label">Monto apartado ($):</div><div class="write-line"></div></div>
            <div><div class="field-label">¿Lo respeté hasta el domingo?</div><p class="inline-q">☐ Sí &nbsp;&nbsp;&nbsp;&nbsp; ☐ No (¿por qué?)</p></div>
          </div>
        </div>

        <div class="card card-compact">
          <h3 class="card-h3">2. Reducción de impulsos (Nivel 1 de la Regla 3–2–1)</h3>
          <div class="field-label">Impulso o fuga que reduje esta semana:</div>
          <div class="write-line"></div>
          <p class="inline-q mt-xs">¿Lo cumplí? &nbsp;&nbsp; ☐ Sí &nbsp;&nbsp;&nbsp;&nbsp; ☐ Parcialmente &nbsp;&nbsp;&nbsp;&nbsp; ☐ No</p>
        </div>

        <div class="card card-compact">
          <h3 class="card-h3">3. Día Cero (día sin gastos no esenciales)</h3>
          <div class="two-col-even mt-xs">
            <div><div class="field-label">Día seleccionado:</div><div class="write-line"></div></div>
            <div><div class="field-label">¿Se cumplió?</div><p class="inline-q">☐ Sí &nbsp;&nbsp;&nbsp;&nbsp; ☐ No</p></div>
          </div>
        </div>

        <div class="card card-compact">
          <h3 class="card-h3">4. Meta personal de dinero para la siguiente semana</h3>
          <div class="write-line"></div>
          <div class="write-line"></div>
        </div>

        <div class="card card-compact">
          <h3 class="card-h3">5. Reflexión breve (¿qué hice bien? ¿qué puedo mejorar?)</h3>
          <div class="write-line"></div>
          <div class="write-line"></div>
          <div class="write-line"></div>
        </div>
      </div>
    """)

    # PÁG 78 — PLANTILLA 1: MI RUTINA BASE
    add_page("Parte IV · Plantilla 1", f"""
      <p class="eyebrow">Plantilla 1 · Días normales</p>
      <h1 class="h1">Mi Rutina Base</h1>
      <p class="lead-sm">Tu esqueleto diario simple y repetible para días regulares. Imprime y pega esta hoja donde la puedas ver todos los días.</p>

      <div class="stack-sm">
        <div class="card">
          <div class="field-label-lg">1. Despertar con intención (primeros 10 minutos sin redes)</div>
          <div class="write-line"></div>
          <div class="write-line"></div>
        </div>
        <div class="card">
          <div class="field-label-lg">2. Primer cuidado del día (cuerpo / mente)</div>
          <div class="write-line"></div>
          <div class="write-line"></div>
        </div>
        <div class="card card-terra-border">
          <div class="field-label-lg" style="color:#C67D5B;">3. Tarea Prioritaria Única (TPU)</div>
          <div class="write-line"></div>
          <div class="write-line"></div>
        </div>
        <div class="card">
          <div class="field-label-lg">4. Movimiento breve / Orden mínimo</div>
          <div class="write-line"></div>
        </div>
        <div class="card">
          <div class="field-label-lg">5. Cierre del día (agradecimiento / evaluación breve / 1 gasto)</div>
          <div class="write-line"></div>
          <div class="write-line"></div>
        </div>
      </div>

      <div class="callout-bar mt-md">Frase guía: «Menos ruido. Más vida.»</div>
    """, toc_key="plantilla_rutina")

    # PÁG 79 — PLANTILLA 2: MI SEMANA ESTABLE
    weekdays = ["LUNES", "MARTES", "MIÉRCOLES", "JUEVES", "VIERNES"]
    wk_cards = ""
    for wd in weekdays:
        wk_cards += f"""
          <div class="day-plan-card">
            <div class="dp-title">{wd}</div>
            <div class="dp-line"><span>TPU:</span><i></i></div>
            <div class="dp-line"><span>Cuidado:</span><i></i></div>
            <div class="dp-line"><span>Fijos:</span><i></i></div>
            <div class="dp-line"><span>Gasto:</span><i></i></div>
          </div>
        """
    add_page("Parte IV · Plantilla 2", f"""
      <p class="eyebrow">Plantilla 2 · Menos es más</p>
      <h1 class="h1">Mi Semana Estable</h1>
      <p class="lead-sm">Una agenda semanal ligera para no reinventar tu vida cada lunes. Imprime y pega esta hoja donde la puedas ver todos los días.</p>

      <div class="week-plan-grid">
        <div class="week-plan-col">{wk_cards}</div>
        <div class="week-plan-col">
          <div class="day-plan-card">
            <div class="dp-title">SÁBADO</div>
            <div class="dp-line"><span>Enfoque:</span><i></i></div>
            <div class="dp-line"><span>Descanso / ocio:</span><i></i></div>
            <div class="dp-line"><span>Casa / orden:</span><i></i></div>
          </div>
          <div class="day-plan-card">
            <div class="dp-title">DOMINGO</div>
            <div class="field-label mt-xs">Reflexión / Pausa personal (opcional: espiritual):</div>
            <div class="write-line"></div>
            <div class="write-line"></div>
            <div class="write-line"></div>
            <div class="field-label mt-sm">Plan semanal rápido (5 minutos):</div>
            <div class="write-line"></div>
            <div class="write-line"></div>
            <div class="write-line"></div>
          </div>
          <div class="quote-mini-card">
            <div class="golden-kicker">FRASE GUÍA</div>
            <p>«Lo que repites, te sostiene.»</p>
          </div>
        </div>
      </div>
    """, toc_key="plantilla_semana")

    # PÁG 80 — PLANTILLA 3: MI DINERO EN ORDEN (COHERENTE: 6 NECESARIOS, 6 ÚTILES, 2 IMPULSOS)
    def numbered_two_col(count: int) -> str:
        half = count // 2
        left = "".join(f"<div class='num-line'><span>{n}.</span><div class='write-line-inline'></div></div>" for n in range(1, half + 1))
        right = "".join(f"<div class='num-line'><span>{n}.</span><div class='write-line-inline'></div></div>" for n in range(half + 1, count + 1))
        return f"<div class='two-col-even'><div>{left}</div><div>{right}</div></div>"

    add_page("Parte IV · Plantilla 3", f"""
      <p class="eyebrow" style="color:#9B7B54;">Plantilla 3 · Regla 3–2–1</p>
      <h1 class="h1">Mi Dinero en Orden</h1>
      <p class="lead-sm">Controla tus gastos semanales en menos de 2 minutos. Imprime y pega esta hoja donde la puedas ver todos los días.</p>

      <div class="card card-compact">
        <div class="two-col-even">
          <div><div class="field-label">Semana del:</div><div class="write-line"></div></div>
          <div><div class="field-label">Dinero que entra esta semana ($):</div><div class="write-line"></div></div>
        </div>
      </div>

      <div class="card card-compact mt-sm">
        <div class="cat-row"><span class="cat-badge cat-3">3 · Necesarios</span><span class="diario-hint">Indispensables de tu semana (hasta 6)</span></div>
        {numbered_two_col(6)}
      </div>

      <div class="card card-compact mt-sm">
        <div class="cat-row"><span class="cat-badge cat-2">2 · Útiles</span><span class="diario-hint">No indispensables, pero aportan valor real (hasta 6)</span></div>
        {numbered_two_col(6)}
      </div>

      <div class="card card-compact mt-sm">
        <div class="cat-row"><span class="cat-badge cat-1">1 · Impulsos permitidos</span><span class="diario-hint">Máximo 1 a 2 planeados y sin culpa</span></div>
        <div class="two-col-even">
          <div class="num-line"><span>1.</span><div class="write-line-inline"></div></div>
          <div class="num-line"><span>2.</span><div class="write-line-inline"></div></div>
        </div>
      </div>

      <div class="card card-tinted card-compact mt-sm">
        <div class="two-col-even">
          <div><div class="field-label">Límite semanal ($):</div><div class="write-line"></div></div>
          <div><div class="field-label">Total gastado ($):</div><div class="write-line"></div></div>
        </div>
      </div>

      <div class="callout-bar mt-sm">Frase guía: «El dinero fluye mejor cuando tú mandas.»</div>
    """, toc_key="plantilla_dinero")

    # PÁG 81 — HERRAMIENTA 4: HOJA SOS (INCLUSIVA + RESETEO FÍSICO)
    add_page("Parte IV · Herramienta 4", f"""
      <div class="sos-header">
        <div>
          <p class="eyebrow" style="color:#C67D5B;">Herramienta 4 · Días difíciles</p>
          <h1 class="h1">Hoja SOS — Botón de Rescate</h1>
        </div>
        <div class="sos-badge">SOS</div>
      </div>
      <p class="lead-sm"><strong>Cuando el día se caiga, no te caigas tú.</strong> Sigue estos 6 pasos en orden exacto:</p>

      <div class="sos-steps">
        <div class="sos-step">
          <div class="sos-num">1</div>
          <div>
            <h3>Respira 60 segundos</h3>
            <p>Inhala 4 segundos · retén 2 segundos · exhala lento en 6 segundos (repite 5 veces).</p>
          </div>
        </div>
        <div class="sos-step">
          <div class="sos-num">2</div>
          <div>
            <h3>Aplica el Reseteo Físico de 5 minutos</h3>
            <p>Lava tu cara con agua fresca · bebe un vaso de agua · despeja 1 microespacio · camina 3 minutos sin pantalla.</p>
          </div>
        </div>
        <div class="sos-step">
          <div class="sos-num">3</div>
          <div>
            <h3>Regresa a tu base</h3>
            <p>Suelta lo secundario por hoy. Haz únicamente tu <strong>TPU (Tarea Prioritaria Única)</strong>.</p>
          </div>
        </div>
        <div class="sos-step">
          <div class="sos-num">4</div>
          <div>
            <h3>Reduce el ruido</h3>
            <p>Silencia notificaciones y redes sociales durante 1 hora completa.</p>
          </div>
        </div>
        <div class="sos-step">
          <div class="sos-num">5</div>
          <div>
            <h3>Frase de anclaje o práctica personal (opcional)</h3>
            <p>Repite en calma —o haz una breve oración si forma parte de tu vida—: <em>«Hoy elijo claridad, calma y dirección.»</em></p>
          </div>
        </div>
        <div class="sos-step">
          <div class="sos-num">6</div>
          <div>
            <h3>Escribe una sola cosa buena de hoy</h3>
            <div class="write-line mt-xs"></div>
            <div class="write-line"></div>
          </div>
        </div>
      </div>
    """, toc_key="hoja_sos")

    # PÁG 82 — HERRAMIENTA 5: MI TRIPLE ANCLA (GUÍA — NUMERACIÓN 1–3 CORREGIDA)
    add_page("Parte IV · Herramienta 5", f"""
      <p class="eyebrow" style="color:#5F6F7E;">Herramienta 5 · Constancia real</p>
      <h1 class="h1">Mi Triple Ancla</h1>
      <p class="lead">Tres hábitos esenciales. Mínimo esfuerzo. Máximo impacto.</p>

      <div class="card">
        <p class="card-p">Tu vida no cambia por intentar hacer veinte cosas nuevas, sino por sostener lo que de verdad importa.</p>
        <p class="card-p mt-xs">La <strong>Triple Ancla</strong> es tu sistema mínimo de estabilidad diaria: tres hábitos tan pequeños que puedes cumplir incluso en tus peores días, pero tan estratégicos que mantienen tu mente, tu energía y tu rumbo en orden.</p>
        <div class="triple-mantra">
          <span>Son tus no negociables.</span>
          <span>Tu estructura interna.</span>
          <span>Tu «aunque sea esto, hoy lo cumplo».</span>
        </div>
      </div>

      <div class="card card-tinted mt-md">
        <h3 class="card-h3">¿Cómo elegir tu Triple Ancla? (3 reglas exactas)</h3>
        <div class="three-rules">
          <div class="tr-item">
            <div class="tr-num">1</div>
            <div>
              <strong>Que no dependan de motivación.</strong>
              <p>Si necesitas «tener ganas» para hacerlos, son demasiado grandes.</p>
            </div>
          </div>
          <div class="tr-item">
            <div class="tr-num">2</div>
            <div>
              <strong>Que tarden menos de 5 minutos cada uno.</strong>
              <p>Lo micro es lo sostenible. Las tres juntas toman menos de 10–15 minutos al día.</p>
            </div>
          </div>
          <div class="tr-item">
            <div class="tr-num">3</div>
            <div>
              <strong>Que impacten directamente tu claridad, tu energía o tu dirección.</strong>
              <p>Nada decorativo: solo acciones que sostienen tu día real.</p>
            </div>
          </div>
        </div>
      </div>

      <div class="callout-bar mt-md">Si estos tres hábitos suceden, tu día ya no se derrumba.</div>
    """, toc_key="triple_ancla")

    # PÁG 83 — HERRAMIENTA 5: EJEMPLOS Y PLANTILLA TRIPLE ANCLA (PARES LIMPIOS, NO 10 VIÑETAS)
    ex_html = ""
    for ex in content["tripleAnclaExamples"]:
        ex_html += f"""
          <div class="ex-item">
            <strong>{esc(ex['title'])}</strong>
            <p>{esc(ex['desc'])}</p>
          </div>
        """
    add_page("Parte IV · Herramienta 5", f"""
      <p class="eyebrow" style="color:#5F6F7E;">Herramienta 5 · Inspiración y definición</p>
      <h1 class="h1">Ejemplos y Tu Triple Ancla</h1>
      <p class="lead-sm">No copies por copiar: inspírate y escoge solo tres que encajen con tu vida real.</p>

      <div class="ex-list">{ex_html}</div>

      <div class="card card-sage-border mt-md">
        <h3 class="card-h3" style="color:#4A5D4E;">Define aquí tu Triple Ancla (tus 3 fundamentos diarios)</h3>
        <p class="diario-hint">Escoge los mismos tres todos los días durante al menos 30 días.</p>
        <div class="num-line mt-sm"><span>1.</span><div class="write-line-inline"></div></div>
        <div class="num-line mt-xs"><span>2.</span><div class="write-line-inline"></div></div>
        <div class="num-line mt-xs"><span>3.</span><div class="write-line-inline"></div></div>
      </div>
    """)

    # PÁG 84 — HERRAMIENTA 6: MI DÍA BASE (CONSOLIDADO SIN DUPLICACIÓN + ÍCONO NEUTRO)
    db_html = ""
    for el in content["diaBaseElements"]:
        db_html += f"""
          <div class="db-row">
            <div class="db-icon">{icon_svg(el['icon'], 20)}</div>
            <div>
              <h3>{esc(el['title'])}</h3>
              <p>{esc(el['desc'])}</p>
            </div>
          </div>
        """
    add_page("Parte IV · Herramienta 6", f"""
      <p class="eyebrow" style="color:#4A5D4E;">Herramienta 6 · Modo estabilidad</p>
      <h1 class="h1">Mi Día Base — Qué es y qué incluye</h1>
      <p class="lead-sm">Cuando la vida se complica —y se va a complicar— no necesitas planes perfectos: necesitas una estructura mínima para <strong>no retroceder</strong> y cuidar tu palabra contigo mismo.</p>

      <div class="db-list">{db_html}</div>

      <div class="golden-rule mt-md">
        <div class="golden-kicker">TU SUELO FIRME</div>
        <p class="golden-text">Un Día Base bien hecho hace que los días difíciles no te destruyan… y que los días buenos te encuentren preparado.</p>
      </div>
    """, toc_key="dia_base")

    # PÁG 85 — HERRAMIENTA 6: PLANTILLA RELLENABLE DE MI DÍA BASE (LA HOJA QUE FALTABA!)
    add_page("Parte IV · Herramienta 6", f"""
      <p class="eyebrow" style="color:#4A5D4E;">Herramienta 6 · Hoja rellenable</p>
      <h1 class="h1">Plantilla — Mi Día Base</h1>
      <p class="lead-sm">Tu plan mínimo de estabilidad para días pesados, cansados o con imprevistos. Guárdalo visible junto a tu Hoja SOS.</p>

      <div class="stack-sm">
        <div class="card card-compact card-terra-border">
          <h3 class="card-h3" style="color:#C67D5B;">1. Mis 3 tareas indispensables (la #1 es mi TPU)</h3>
          <div class="num-line"><span>1.</span><div class="write-line-inline"></div></div>
          <div class="num-line"><span>2.</span><div class="write-line-inline"></div></div>
          <div class="num-line"><span>3.</span><div class="write-line-inline"></div></div>
        </div>

        <div class="card card-compact">
          <h3 class="card-h3">2. Mi cuidado personal mínimo</h3>
          <div class="write-line"></div>
        </div>

        <div class="card card-compact">
          <h3 class="card-h3">3. Mi pausa de centro (silencio, gratitud, lectura u oración opcional)</h3>
          <div class="write-line"></div>
        </div>

        <div class="card card-compact">
          <h3 class="card-h3">4. Mi límite diario de gastos en días difíciles ($)</h3>
          <div class="write-line"></div>
        </div>

        <div class="card card-compact">
          <h3 class="card-h3">5. Mi microacción V.I.D.A. de respaldo</h3>
          <div class="write-line"></div>
        </div>
      </div>

      <div class="callout-bar mt-sm">Cuando todo falle, regreso a mi base.</div>
    """)

    # PÁG 86 — CIERRE INSTITUCIONAL (SIN FIRMA PERSONAL)
    add_page("Cierre", f"""
      <div class="goodbye-wrap">
        {logo_svg(68, "#4A5D4E")}
        <div class="goodbye-brand">VIDA EN ORDEN</div>
        <div class="short-rule" style="margin: 18px auto;"></div>
        <h1 class="goodbye-title">Gracias por darte esta oportunidad.</h1>
        <p class="goodbye-p">Te mereces la vida que estás construyendo: más clara, más firme y con más paz.</p>
        <p class="goodbye-p">Ojalá este método te acompañe muchos años. Ojalá sigas avanzando simple, constante, con intención y dirección.</p>
        <p class="goodbye-p"><strong>Lo mejor todavía viene.</strong></p>
        <div class="goodbye-sign">— VIDA EN ORDEN · Menos ruido. Más vida.</div>
      </div>
    """, hide_chrome=True)

    # PÁG 87 — CONTRAPORTADA INSTITUCIONAL (SIN INICIALES PERSONALES)
    add_page("", f"""
      <div class="back-cover">
        {logo_svg(84, "#232320")}
        <div class="back-brand">VIDA EN ORDEN</div>
        <div class="back-sub">Sistema de 30 Días · Método V.I.D.A.</div>
        <div class="back-slogan">{esc(meta['subtitle'])}</div>
        <div class="back-meta">
          <span>{esc(meta['edition'])}</span>
          <span>·</span>
          <span>{esc(meta['instagram'])}</span>
          <span>·</span>
          <span>{esc(meta['linktree'])}</span>
        </div>
      </div>
    """, extra_class="page-cover", hide_chrome=True)

    # RELLENAR ÍNDICE (PÁG 3) CON LOS NÚMEROS REALES VERIFICADOS
    toc_entries = [
        ("Parte I · Fundamento y Punto de Partida", [
            ("Bienvenido al Método V.I.D.A. (10 min/día)", toc_map["parte1"]),
            ("El Método V.I.D.A. (4 pilares)", toc_map["metodo_vida"]),
            ("Test Inicial — ¿Dónde estás hoy? (5 Dimensiones)", toc_map["test_inicial"]),
            ("Mini-Manual en 3 pasos + Hoja Maestra (10 Reglas)", toc_map["mini_manual"]),
            ("Las 3 Bases del Método (Mente, Día y Dinero)", toc_map["tres_bases"]),
            ("Mapa del Método, Preparación y Día Ordenado", toc_map["mapa_metodo"]),
        ]),
        ("Parte II · Los 30 Días del Sistema", [
            ("Semana 1 · Orden Mental y Calma (Días 1–7)", toc_map["semana_1"]),
            ("Semana 2 · Claridad y Estructura Diaria (Días 8–14)", toc_map["semana_2"]),
            ("Semana 3 · Orden del Dinero (Días 15–21)", toc_map["semana_3"]),
            ("Semana 4 · Integración y Hábitos (Días 22–30)", toc_map["semana_4"]),
            ("Mantenimiento Mensual y Evaluación Día 1 vs. Día 30", toc_map["mantenimiento"]),
        ]),
        ("Parte III · Cuaderno Diario", [
            ("Cuaderno Diario — 30 Días · 30 Frases (Día 01 al Día 30)", toc_map["cuaderno_diario"]),
        ]),
        ("Parte IV · Kit de Herramientas y Plantillas", [
            ("Introducción al Kit y qué es la TPU", toc_map["kit_herramientas"]),
            ("Tablas 1 y 2 — Registro Semanal y Mini-Metas de Dinero", toc_map["tablas_finanzas"]),
            ("Plantilla 1 — Mi Rutina Base", toc_map["plantilla_rutina"]),
            ("Plantilla 2 — Mi Semana Estable", toc_map["plantilla_semana"]),
            ("Plantilla 3 — Mi Dinero en Orden (Regla 3–2–1)", toc_map["plantilla_dinero"]),
            ("Herramienta 4 — Hoja SOS (Días Difíciles)", toc_map["hoja_sos"]),
            ("Herramienta 5 — Mi Triple Ancla (Guía + Plantilla)", toc_map["triple_ancla"]),
            ("Herramienta 6 — Mi Día Base (Guía + Plantilla)", toc_map["dia_base"]),
        ]),
    ]

    toc_html_groups = ""
    for group_title, rows in toc_entries:
        rows_html = "".join(
            f"<div class='toc-row'><span class='toc-label'>{esc(lbl)}</span><span class='toc-dots'></span><span class='toc-pg'>{pg:02d}</span></div>"
            for lbl, pg in rows
        )
        toc_html_groups += f"<div class='toc-group'><div class='toc-group-title'>{esc(group_title)}</div>{rows_html}</div>"

    toc_body = f"""
      <p class="eyebrow">Mapa del cuaderno</p>
      <h1 class="h1">Índice General</h1>
      <p class="lead-sm">Todo el sistema organizado para que encuentres cualquier día, tabla o plantilla en segundos.</p>
      <div class="toc-wrap">{toc_html_groups}</div>
    """
    pages[toc_index] = pages[toc_index].replace("__TOC_PLACEHOLDER__", toc_body)

    return pages, toc_map


def build_html_document(tokens: dict, pages: list[str], print_mode: bool = False) -> str:
    c = tokens["colors"]
    bg_page = "#FFFFFF" if print_mode else c["bgPrimary"]
    bg_card = "#FFFFFF"
    bg_tinted = "#F7F6F3" if print_mode else c["bgMuted"]
    bg_cover = "#FFFFFF" if print_mode else c["bgPrimary"]

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8" />
<title>VIDA EN ORDEN — Sistema de 30 Días</title>
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="https://fonts.googleapis.com/css2?family=Lora:ital,wght@0,500;0,600;0,700;1,400;1,500&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap" rel="stylesheet" />
<style>
  @page {{
    size: letter;
    margin: 0;
  }}
  * {{
    box-sizing: border-box;
    margin: 0;
    padding: 0;
  }}
  html, body {{
    background: {bg_page};
    color: {c['textPrimary']};
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    font-size: 13px;
    line-height: 1.5;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }}
  .page {{
    width: 8.5in;
    height: 11in;
    padding: 0.58in 0.68in 0.56in 0.68in;
    background: {bg_page};
    position: relative;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    break-after: page;
    page-break-after: always;
  }}
  .page:last-child {{
    break-after: auto;
    page-break-after: auto;
  }}
  .page-cover {{
    background: {bg_cover};
    padding: 0.72in 0.78in;
  }}
  .p-header {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-bottom: 9px;
    margin-bottom: 18px;
    border-bottom: 1px solid {c['border']};
    font-size: 9.5px;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: {c['textMuted']};
    flex-shrink: 0;
  }}
  .p-brand {{
    font-weight: 700;
    color: {c['primary']};
    letter-spacing: 0.14em;
  }}
  .p-body {{
    flex: 1;
    display: flex;
    flex-direction: column;
    min-height: 0;
  }}
  .p-footer {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-top: 9px;
    margin-top: 14px;
    border-top: 1px solid {c['border']};
    font-size: 9.5px;
    color: {c['textMuted']};
    flex-shrink: 0;
  }}
  .p-num {{
    font-weight: 700;
    color: {c['textPrimary']};
    font-variant-numeric: tabular-nums;
  }}

  /* Tipografía editorial */
  .eyebrow {{
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: {c['primary']};
    margin-bottom: 6px;
  }}
  .h1 {{
    font-family: 'Lora', Georgia, serif;
    font-size: 24px;
    font-weight: 600;
    line-height: 1.2;
    color: {c['textPrimary']};
    margin-bottom: 8px;
  }}
  .lead {{
    font-size: 13.5px;
    color: {c['textSecondary']};
    margin-bottom: 16px;
    line-height: 1.55;
  }}
  .lead-sm {{
    font-size: 12.2px;
    color: {c['textSecondary']};
    margin-bottom: 12px;
    line-height: 1.48;
  }}
  .short-rule {{
    width: 48px;
    height: 3px;
    background: {c['accent']};
    border-radius: 3px;
    margin: 12px 0 18px;
  }}
  .mt-xs {{ margin-top: 6px; }}
  .mt-sm {{ margin-top: 11px; }}
  .mt-md {{ margin-top: 16px; }}
  .mt-lg {{ margin-top: 24px; }}

  /* Tarjetas y contenedores */
  .stack-sm {{ display: flex; flex-direction: column; gap: 10px; }}
  .stack-md {{ display: flex; flex-direction: column; gap: 14px; }}
  .card {{
    background: {bg_card};
    border: 1px solid {c['border']};
    border-radius: 12px;
    padding: 15px 18px;
  }}
  .card-compact {{
    padding: 11px 15px;
  }}
  .card-tinted {{
    background: {bg_tinted};
    border-color: {c['border']};
  }}
  .card-sage-border {{
    border-left: 4px solid {c['primary']};
  }}
  .card-terra-border {{
    border-left: 4px solid {c['accent']};
  }}
  .card-h3 {{
    font-family: 'Lora', Georgia, serif;
    font-size: 14.5px;
    font-weight: 600;
    color: {c['textPrimary']};
    margin-bottom: 5px;
  }}
  .card-p {{
    font-size: 12.3px;
    color: {c['textSecondary']};
    line-height: 1.52;
  }}
  .callout-bar {{
    margin-top: auto;
    padding: 12px 16px;
    background: {c['primarySoft']};
    border-left: 4px solid {c['primary']};
    border-radius: 8px;
    font-family: 'Lora', Georgia, serif;
    font-style: italic;
    font-size: 13.5px;
    color: {c['textPrimary']};
    text-align: center;
  }}

  /* Portada */
  .cover-page {{
    height: 100%;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
  }}
  .cover-top {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-bottom: 18px;
    border-bottom: 1px solid {c['border']};
  }}
  .cover-emblem {{
    display: flex;
    align-items: center;
    gap: 14px;
  }}
  .cover-brand-name {{
    font-size: 15px;
    font-weight: 700;
    letter-spacing: 0.16em;
    color: {c['textPrimary']};
  }}
  .cover-edition {{
    font-size: 11px;
    color: {c['textMuted']};
    margin-top: 2px;
  }}
  .cover-pill {{
    padding: 7px 14px;
    border-radius: 999px;
    background: {c['primarySoft']};
    color: {c['primary']};
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.04em;
  }}
  .cover-center {{
    margin: auto 0;
  }}
  .accent-rule {{
    width: 64px;
    height: 4px;
    background: {c['accent']};
    border-radius: 4px;
    margin-bottom: 18px;
  }}
  .cover-h1 {{
    font-family: 'Lora', Georgia, serif;
    font-size: 46px;
    font-weight: 700;
    letter-spacing: 0.03em;
    line-height: 1.08;
    color: {c['textPrimary']};
  }}
  .cover-h2 {{
    font-family: 'Lora', Georgia, serif;
    font-size: 27px;
    font-weight: 500;
    color: {c['primary']};
    margin-top: 6px;
  }}
  .cover-slogan {{
    font-family: 'Lora', Georgia, serif;
    font-style: italic;
    font-size: 20px;
    color: {c['accent']};
    margin-top: 14px;
    margin-bottom: 34px;
  }}
  .cover-card {{
    background: {bg_card};
    border: 1px solid {c['border']};
    border-left: 5px solid {c['primary']};
    border-radius: 16px;
    padding: 24px 26px;
  }}
  .cover-card-kicker {{
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    color: {c['primary']};
    margin-bottom: 8px;
  }}
  .cover-card-copy {{
    font-size: 15px;
    color: {c['textPrimary']};
    line-height: 1.55;
    margin-bottom: 18px;
  }}
  .cover-pillars {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 10px;
    padding-top: 14px;
    border-top: 1px solid {c['border']};
    font-size: 12px;
    color: {c['textSecondary']};
  }}
  .cover-pillars strong {{
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 22px;
    height: 22px;
    border-radius: 6px;
    background: {c['primarySoft']};
    color: {c['primary']};
    margin-right: 6px;
    font-size: 11px;
  }}
  .cover-bottom {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-top: 16px;
    border-top: 1px solid {c['border']};
    font-size: 11px;
    color: {c['textMuted']};
  }}
  .cover-dims {{
    display: flex;
    gap: 8px;
    font-weight: 600;
    color: {c['textSecondary']};
  }}
  .cover-dims i {{ font-style: normal; color: {c['accent']}; }}

  /* Manifiesto */
  .manifesto-wrap {{
    margin: auto 0;
    padding: 0 18px;
  }}
  .manifesto-title {{
    font-family: 'Lora', Georgia, serif;
    font-size: 31px;
    line-height: 1.25;
    font-weight: 600;
    margin-bottom: 12px;
  }}
  .manifesto-lead {{
    font-family: 'Lora', Georgia, serif;
    font-style: italic;
    font-size: 22px;
    color: {c['accent']};
    margin-bottom: 24px;
  }}
  .manifesto-p {{
    font-size: 15.5px;
    line-height: 1.75;
    color: {c['textSecondary']};
    margin-bottom: 16px;
  }}
  .manifesto-close {{
    margin-top: 28px;
    padding-top: 18px;
    border-top: 1px solid {c['border']};
    font-family: 'Lora', Georgia, serif;
    font-size: 20px;
    font-weight: 600;
    color: {c['primary']};
  }}

  /* Índice */
  .toc-wrap {{ display: flex; flex-direction: column; gap: 15px; margin-top: 6px; }}
  .toc-group-title {{
    font-size: 10.5px;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: {c['primary']};
    margin-bottom: 6px;
    padding-bottom: 4px;
    border-bottom: 1px solid {c['border']};
  }}
  .toc-row {{
    display: flex;
    align-items: baseline;
    gap: 8px;
    font-size: 12px;
    padding: 3px 0;
  }}
  .toc-label {{ color: {c['textPrimary']}; }}
  .toc-dots {{ flex: 1; border-bottom: 1px dotted {c['borderStrong']}; transform: translateY(-3px); }}
  .toc-pg {{ font-weight: 700; color: {c['primary']}; font-variant-numeric: tabular-nums; }}

  /* Listas */
  .clean-list {{ list-style: none; display: flex; flex-direction: column; gap: 6px; }}
  .clean-list li {{
    position: relative;
    padding-left: 16px;
    font-size: 12.2px;
    color: {c['textSecondary']};
  }}
  .clean-list li::before {{
    content: "•";
    position: absolute;
    left: 2px;
    color: {c['accent']};
    font-weight: 700;
  }}
  .clean-list-lg li {{ font-size: 13.5px; padding-left: 18px; line-height: 1.55; }}

  /* Método VIDA */
  .pillar-grid {{ display: flex; flex-direction: column; gap: 11px; }}
  .pillar-card {{
    background: {bg_card};
    border: 1px solid {c['border']};
    border-radius: 12px;
    padding: 12px 16px;
  }}
  .pillar-head {{ display: flex; align-items: center; gap: 12px; margin-bottom: 6px; }}
  .pillar-letter {{
    width: 30px;
    height: 30px;
    border-radius: 8px;
    color: #FFFFFF;
    font-family: 'Lora', Georgia, serif;
    font-size: 16px;
    font-weight: 700;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
  }}
  .pillar-name {{ font-family: 'Lora', Georgia, serif; font-size: 15px; font-weight: 600; }}
  .pillar-tag {{ font-size: 11.5px; color: {c['textMuted']}; font-style: italic; }}
  .pillar-body {{ font-size: 12px; color: {c['textSecondary']}; margin-bottom: 6px; }}
  .pillar-qs {{
    display: flex;
    flex-wrap: wrap;
    gap: 5px 14px;
    list-style: none;
    font-size: 11px;
    color: {c['textPrimary']};
    padding-top: 6px;
    border-top: 1px dashed {c['border']};
  }}
  .pillar-qs li::before {{ content: "→ "; color: {c['accent']}; font-weight: 700; }}

  /* Test Inicial */
  .test-list {{ display: flex; flex-direction: column; gap: 9px; }}
  .test-row {{
    background: {bg_card};
    border: 1px solid {c['border']};
    border-radius: 10px;
    padding: 9px 13px;
  }}
  .test-row-top {{ display: flex; justify-content: space-between; align-items: center; gap: 10px; margin-bottom: 6px; }}
  .test-dim-label {{ font-size: 12px; color: {c['textPrimary']}; display: flex; align-items: center; gap: 6px; }}
  .dim-dot {{ width: 9px; height: 9px; border-radius: 50%; display: inline-block; flex-shrink: 0; }}
  .score-box {{ font-size: 11px; font-weight: 600; color: {c['textSecondary']}; white-space: nowrap; }}
  .scale-chips {{ display: grid; grid-template-columns: repeat(5, 1fr); gap: 5px; }}
  .scale-chip {{
    font-size: 9.8px;
    text-align: center;
    padding: 4px 4px;
    border-radius: 6px;
    background: {bg_tinted};
    color: {c['textSecondary']};
    border: 1px solid {c['border']};
  }}
  .two-col-tight {{ display: grid; grid-template-columns: 1.55fr 1fr; gap: 16px; align-items: center; }}
  .two-col-even {{ display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }}
  .total-score-box {{
    background: {c['primarySoft']};
    border-radius: 10px;
    padding: 10px 12px;
    text-align: center;
  }}
  .total-label {{ font-size: 9.5px; font-weight: 700; letter-spacing: 0.1em; color: {c['primary']}; }}
  .total-val {{ font-family: 'Lora', Georgia, serif; font-size: 20px; font-weight: 700; margin: 4px 0; }}
  .total-hint {{ font-size: 9.5px; color: {c['textSecondary']}; }}
  .bridge-note {{
    margin-top: 10px;
    padding: 10px 13px;
    border-radius: 10px;
    background: {bg_tinted};
    border: 1px solid {c['border']};
    font-size: 11px;
    color: {c['textSecondary']};
    line-height: 1.48;
  }}

  /* Líneas para escribir */
  .field-label {{ font-size: 11px; font-weight: 600; color: {c['textSecondary']}; margin-bottom: 4px; }}
  .field-label-lg {{ font-size: 13px; font-weight: 700; color: {c['textPrimary']}; margin-bottom: 8px; }}
  .write-line {{ height: 24px; border-bottom: 1px solid {c['borderStrong']}; }}
  .num-line {{ display: flex; align-items: flex-end; gap: 8px; height: 26px; font-size: 12px; font-weight: 600; color: {c['textSecondary']}; }}
  .write-line-inline {{ flex: 1; border-bottom: 1px solid {c['borderStrong']}; height: 18px; }}
  .inline-q {{ font-size: 12px; color: {c['textPrimary']}; margin-top: 4px; }}

  /* Mini-manual */
  .step-flow {{ display: flex; flex-direction: column; align-items: stretch; gap: 8px; margin-top: 8px; }}
  .flow-card {{
    display: flex;
    align-items: center;
    gap: 18px;
    background: {bg_card};
    border: 1px solid {c['border']};
    border-radius: 14px;
    padding: 20px 22px;
  }}
  .flow-num {{
    width: 48px;
    height: 48px;
    border-radius: 12px;
    background: {c['primary']};
    color: #FFFFFF;
    font-family: 'Lora', Georgia, serif;
    font-size: 20px;
    font-weight: 700;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
  }}
  .flow-tag {{ font-size: 10px; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; color: {c['primary']}; }}
  .flow-content h3 {{ font-family: 'Lora', Georgia, serif; font-size: 17px; margin: 2px 0 4px; }}
  .flow-content p {{ font-size: 12.8px; color: {c['textSecondary']}; }}
  .flow-arrow {{ text-align: center; font-size: 18px; color: {c['textMuted']}; line-height: 1; }}
  .golden-rule {{
    margin-top: auto;
    padding: 18px 22px;
    border-radius: 14px;
    background: {c['accentSoft']};
    border: 1px solid #E8CFC2;
    text-align: center;
  }}
  .golden-kicker {{ font-size: 10px; font-weight: 700; letter-spacing: 0.14em; color: {c['accent']}; margin-bottom: 5px; }}
  .golden-text {{ font-family: 'Lora', Georgia, serif; font-size: 16.5px; color: {c['textPrimary']}; }}

  /* Hoja maestra 10 reglas */
  .rules-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-top: 6px; }}
  .rule-item {{
    display: flex;
    align-items: flex-start;
    gap: 11px;
    background: {bg_card};
    border: 1px solid {c['border']};
    border-radius: 12px;
    padding: 13px 14px;
  }}
  .rule-badge {{
    width: 34px;
    height: 34px;
    border-radius: 9px;
    background: {c['primarySoft']};
    color: {c['primary']};
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
  }}
  .rule-num {{ font-size: 9.5px; font-weight: 700; letter-spacing: 0.1em; color: {c['textMuted']}; }}
  .rule-txt {{ font-size: 12.4px; font-weight: 600; color: {c['textPrimary']}; line-height: 1.4; margin-top: 2px; }}

  /* 3 Bases */
  .base-page {{ display: flex; flex-direction: column; height: 100%; }}
  .dim-pill {{
    display: inline-block;
    align-self: flex-start;
    padding: 5px 12px;
    border-radius: 999px;
    border: 1px solid;
    font-size: 11px;
    font-weight: 600;
    margin: 4px 0 18px;
  }}
  .statement-card {{
    background: {bg_card};
    border: 1px solid {c['border']};
    border-radius: 14px;
    padding: 20px 22px;
  }}
  .statement-big {{ font-family: 'Lora', Georgia, serif; font-size: 19px; font-weight: 600; line-height: 1.38; margin-bottom: 10px; }}
  .statement-sub {{ font-size: 13.5px; color: {c['textSecondary']}; line-height: 1.6; }}
  .editorial-quote {{
    margin-top: auto;
    padding-top: 18px;
    border-top: 2px solid;
    font-family: 'Lora', Georgia, serif;
    font-style: italic;
    font-size: 19px;
    color: {c['textPrimary']};
    text-align: center;
  }}

  /* Mapa 5 pasos */
  .map-timeline {{ display: flex; flex-direction: column; gap: 11px; margin-top: 6px; }}
  .map-row {{ display: flex; align-items: center; gap: 14px; }}
  .map-num {{
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background: {c['primary']};
    color: #FFFFFF;
    font-family: 'Lora', Georgia, serif;
    font-size: 15px;
    font-weight: 700;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
  }}
  .map-card {{
    flex: 1;
    background: {bg_card};
    border: 1px solid {c['border']};
    border-radius: 12px;
    padding: 12px 16px;
  }}
  .map-card h3 {{ font-family: 'Lora', Georgia, serif; font-size: 15px; margin-bottom: 3px; }}
  .map-card p {{ font-size: 12px; color: {c['textSecondary']}; }}

  /* Preparación y Día ordenado */
  .icon-list {{ list-style: none; display: flex; flex-direction: column; gap: 9px; margin-top: 8px; }}
  .icon-list li {{ display: flex; align-items: flex-start; gap: 10px; font-size: 12.8px; color: {c['textSecondary']}; }}
  .mk-good {{ color: {c['primary']}; font-weight: 700; }}
  .mk-bad {{ color: {c['accent']}; font-weight: 700; }}
  .ordered-list {{ list-style: none; display: flex; flex-direction: column; gap: 14px; }}
  .ordered-list li {{ display: flex; align-items: flex-start; gap: 12px; font-size: 14px; color: {c['textPrimary']}; line-height: 1.5; }}
  .ord-dot {{ width: 9px; height: 9px; border-radius: 50%; background: {c['primary']}; margin-top: 6px; flex-shrink: 0; }}
  .hero-quote-box {{
    margin-top: auto;
    padding: 28px 24px;
    border-radius: 16px;
    background: {c['primarySoft']};
    text-align: center;
  }}
  .hero-quote {{ font-family: 'Lora', Georgia, serif; font-size: 21px; font-style: italic; color: {c['textPrimary']}; line-height: 1.45; }}

  /* Portadas de Semana / Sección */
  .week-cover, .section-cover {{
    margin: auto 0;
    text-align: center;
    padding: 0 22px;
  }}
  .week-badge {{
    display: inline-block;
    padding: 7px 18px;
    border-radius: 999px;
    color: #FFFFFF;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.12em;
    margin-bottom: 18px;
  }}
  .week-cover-title {{
    font-family: 'Lora', Georgia, serif;
    font-size: 36px;
    font-weight: 700;
    line-height: 1.18;
    color: {c['textPrimary']};
  }}
  .section-cover-sub {{
    font-family: 'Lora', Georgia, serif;
    font-size: 20px;
    font-weight: 500;
    color: {c['accent']};
    margin-top: 6px;
  }}
  .week-rule {{ width: 64px; height: 4px; border-radius: 4px; margin: 18px auto; }}
  .week-motto {{
    font-family: 'Lora', Georgia, serif;
    font-style: italic;
    font-size: 19px;
    color: {c['textPrimary']};
    margin-bottom: 8px;
  }}
  .week-focus {{ font-size: 13px; color: {c['textSecondary']}; margin-bottom: 26px; }}
  .week-days-preview {{
    text-align: left;
    background: {bg_card};
    border: 1px solid {c['border']};
    border-radius: 14px;
    padding: 16px 20px;
    display: flex;
    flex-direction: column;
    gap: 8px;
  }}
  .wdp-row {{ display: flex; gap: 14px; font-size: 12.2px; padding-bottom: 6px; border-bottom: 1px dashed {c['border']}; }}
  .wdp-row:last-child {{ border-bottom: none; padding-bottom: 0; }}
  .wdp-row span {{ font-weight: 700; color: {c['textMuted']}; width: 52px; flex-shrink: 0; }}
  .section-cover-copy {{ font-size: 14.5px; color: {c['textSecondary']}; line-height: 1.68; margin-bottom: 14px; }}
  .section-cover-quote {{
    margin-top: 26px;
    padding: 16px 20px;
    border-radius: 12px;
    background: {bg_tinted};
    font-family: 'Lora', Georgia, serif;
    font-style: italic;
    font-size: 17px;
    color: {c['primary']};
  }}

  /* Tarjetas de Día (2 por página) */
  .day-pair {{ display: flex; flex-direction: column; gap: 22px; flex: 1; justify-content: flex-start; }}
  .day-card {{
    flex: 1;
    background: {bg_card};
    border: 1px solid {c['border']};
    border-radius: 14px;
    padding: 20px 22px;
    display: flex;
    flex-direction: column;
    gap: 11px;
  }}
  .day-head {{ display: flex; align-items: baseline; gap: 9px; }}
  .day-check {{ font-size: 17px; color: {c['textMuted']}; line-height: 1; }}
  .day-num {{ font-size: 11px; font-weight: 700; letter-spacing: 0.1em; flex-shrink: 0; }}
  .day-title {{ font-family: 'Lora', Georgia, serif; font-size: 18px; font-weight: 600; color: {c['textPrimary']}; line-height: 1.25; }}
  .day-idea {{ font-size: 12.8px; color: {c['textSecondary']}; line-height: 1.55; }}
  .day-idea strong {{ color: {c['textPrimary']}; }}
  .day-box {{
    background: {bg_tinted};
    border-radius: 10px;
    padding: 12px 15px;
  }}
  .day-box-label {{ font-size: 9.5px; font-weight: 700; letter-spacing: 0.12em; margin-bottom: 4px; }}
  .day-box p {{ font-size: 12.8px; color: {c['textPrimary']}; line-height: 1.52; }}
  .day-expense {{ font-size: 12.2px; color: {c['textSecondary']}; line-height: 1.48; }}
  .day-expense strong {{ color: {c['textPrimary']}; }}
  .day-note-wrap {{
    margin-top: auto;
    display: flex;
    align-items: flex-end;
    gap: 8px;
    padding-top: 6px;
  }}
  .day-note-label {{ font-size: 10.5px; font-weight: 600; color: {c['textMuted']}; white-space: nowrap; }}
  .day-quote {{
    padding-top: 9px;
    border-top: 1px dashed {c['border']};
    font-family: 'Lora', Georgia, serif;
    font-style: italic;
    font-size: 13.8px;
    color: {c['primary']};
  }}
  .outcome-card {{
    flex: 1;
    background: {bg_card};
    border: 1px solid {c['border']};
    border-radius: 14px;
    padding: 22px 24px;
    display: flex;
    flex-direction: column;
    justify-content: center;
  }}
  .outcome-kicker {{ font-size: 10px; font-weight: 700; letter-spacing: 0.12em; margin-bottom: 6px; }}
  .outcome-title {{ font-family: 'Lora', Georgia, serif; font-size: 19px; margin-bottom: 12px; }}

  /* Checklists */
  .checklist {{ list-style: none; display: flex; flex-direction: column; gap: 10px; }}
  .checklist-tight {{ gap: 6px; }}
  .checklist li {{ display: flex; align-items: flex-start; gap: 10px; font-size: 12.5px; color: {c['textPrimary']}; }}
  .checklist-tight li {{ font-size: 11.6px; }}
  .chk-box {{ font-size: 15px; color: {c['primary']}; line-height: 1.15; flex-shrink: 0; }}

  /* Tabla comparativa Día 1 vs 30 */
  .compare-table {{ width: 100%; border-collapse: collapse; background: {bg_card}; border-radius: 10px; overflow: hidden; border: 1px solid {c['border']}; }}
  .compare-table th, .compare-table td {{ padding: 8px 11px; border-bottom: 1px solid {c['border']}; font-size: 12px; text-align: left; }}
  .compare-table th {{ background: {bg_tinted}; font-size: 10.5px; text-transform: uppercase; letter-spacing: 0.06em; color: {c['textSecondary']}; }}
  .compare-table .dim-dot {{ margin-right: 7px; vertical-align: middle; }}
  .td-center {{ text-align: center !important; }}
  .tr-total td {{ background: {c['primarySoft']}; border-bottom: none; }}

  /* Carta de cierre */
  .letter-wrap {{ margin: auto 0; }}
  .letter-p {{ font-size: 14px; line-height: 1.72; color: {c['textSecondary']}; margin-bottom: 14px; }}
  .letter-footer-box {{
    margin-top: 22px;
    padding: 18px 22px;
    border-radius: 14px;
    background: {c['primarySoft']};
    border-left: 4px solid {c['primary']};
  }}
  .letter-close-line {{ font-family: 'Lora', Georgia, serif; font-size: 14.5px; color: {c['textPrimary']}; margin-bottom: 6px; }}
  .letter-close-line:last-child {{ margin-bottom: 0; font-weight: 600; color: {c['primary']}; }}

  /* Cuaderno Diario */
  .diario-head {{
    background: {bg_card};
    border: 1px solid {c['border']};
    border-radius: 12px;
    padding: 12px 16px;
    margin-bottom: 13px;
  }}
  .diario-top-row {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; }}
  .diario-day-tag {{ padding: 4px 10px; border-radius: 999px; color: #FFFFFF; font-size: 10px; font-weight: 700; letter-spacing: 0.1em; }}
  .diario-date {{ font-size: 11px; color: {c['textSecondary']}; font-weight: 600; }}
  .diario-title {{ font-family: 'Lora', Georgia, serif; font-size: 17px; font-weight: 600; }}
  .diario-quote {{ font-family: 'Lora', Georgia, serif; font-style: italic; font-size: 12px; color: {c['textSecondary']}; margin-top: 3px; }}
  .diario-section {{
    background: {bg_card};
    border: 1px solid {c['border']};
    border-radius: 11px;
    padding: 11px 14px;
    margin-bottom: 10px;
  }}
  .diario-label {{ font-size: 11.5px; font-weight: 700; color: {c['textPrimary']}; margin-bottom: 5px; }}
  .diario-label-row {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px; }}
  .diario-done {{ font-size: 11px; font-weight: 700; color: {c['primary']}; }}
  .diario-hint {{ font-weight: 400; color: {c['textMuted']}; font-size: 10.5px; }}
  .diario-micro-reminder {{
    font-size: 10.8px;
    color: {c['textSecondary']};
    background: {bg_tinted};
    padding: 6px 10px;
    border-radius: 7px;
    margin-bottom: 5px;
    line-height: 1.4;
  }}
  .mood-scale {{ display: grid; grid-template-columns: repeat(5, 1fr); gap: 6px; margin-top: 4px; }}
  .mood-scale span {{
    text-align: center;
    padding: 6px 4px;
    border-radius: 8px;
    border: 1px solid {c['borderStrong']};
    background: {bg_tinted};
    font-size: 10.8px;
    color: {c['textSecondary']};
  }}
  .mood-scale strong {{ color: {c['primary']}; margin-right: 3px; }}
  .expense-mini-table {{ width: 100%; border-collapse: collapse; margin-top: 4px; }}
  .expense-mini-table th {{ font-size: 10px; text-transform: uppercase; color: {c['textMuted']}; text-align: left; padding: 4px 6px; border-bottom: 1px solid {c['border']}; }}
  .expense-mini-table td {{ height: 24px; padding: 3px 6px; border-bottom: 1px solid {c['border']}; font-size: 10.5px; color: {c['textMuted']}; font-weight: 600; }}

  /* Tablas y Plantillas Parte IV */
  .three-col-box {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-top: 6px; }}
  .cat-row {{ display: flex; align-items: center; gap: 10px; margin-bottom: 6px; }}
  .cat-badge {{ display: inline-block; padding: 3px 9px; border-radius: 999px; font-size: 10.5px; font-weight: 700; }}
  .cat-3 {{ background: {c['primarySoft']}; color: {c['primary']}; }}
  .cat-2 {{ background: #F2ECE1; color: #7C6242; }}
  .cat-1 {{ background: {c['accentSoft']}; color: {c['accent']}; }}

  /* Semana estable */
  .week-plan-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px; flex: 1; }}
  .week-plan-col {{ display: flex; flex-direction: column; gap: 9px; }}
  .day-plan-card {{
    background: {bg_card};
    border: 1px solid {c['border']};
    border-radius: 10px;
    padding: 9px 12px;
  }}
  .dp-title {{ font-size: 10.5px; font-weight: 700; letter-spacing: 0.1em; color: {c['primary']}; margin-bottom: 5px; }}
  .dp-line {{ display: flex; align-items: flex-end; gap: 6px; height: 20px; font-size: 10.5px; color: {c['textSecondary']}; }}
  .dp-line span {{ flex-shrink: 0; font-weight: 600; }}
  .dp-line i {{ flex: 1; border-bottom: 1px solid {c['borderStrong']}; height: 14px; font-style: normal; }}
  .quote-mini-card {{
    margin-top: auto;
    background: {c['primarySoft']};
    border-radius: 12px;
    padding: 16px;
    text-align: center;
  }}
  .quote-mini-card p {{ font-family: 'Lora', Georgia, serif; font-style: italic; font-size: 16px; color: {c['textPrimary']}; }}

  /* Hoja SOS */
  .sos-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; }}
  .sos-badge {{
    padding: 8px 18px;
    border-radius: 12px;
    background: {c['accent']};
    color: #FFFFFF;
    font-family: 'Lora', Georgia, serif;
    font-size: 22px;
    font-weight: 700;
    letter-spacing: 0.1em;
  }}
  .sos-steps {{ display: flex; flex-direction: column; gap: 10px; margin-top: 6px; }}
  .sos-step {{
    display: flex;
    gap: 14px;
    align-items: flex-start;
    background: {bg_card};
    border: 1px solid {c['border']};
    border-radius: 12px;
    padding: 12px 15px;
  }}
  .sos-num {{
    width: 30px;
    height: 30px;
    border-radius: 50%;
    background: {c['accentSoft']};
    color: {c['accent']};
    font-weight: 700;
    font-size: 13px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
  }}
  .sos-step > div:last-child {{ flex: 1; }}
  .sos-step h3 {{ font-family: 'Lora', Georgia, serif; font-size: 14.5px; margin-bottom: 3px; }}
  .sos-step p {{ font-size: 12px; color: {c['textSecondary']}; line-height: 1.48; }}

  /* Triple Ancla */
  .triple-mantra {{
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 8px;
    margin-top: 14px;
    padding-top: 12px;
    border-top: 1px solid {c['border']};
    text-align: center;
    font-size: 11.5px;
    font-weight: 700;
    color: {c['primary']};
  }}
  .three-rules {{ display: flex; flex-direction: column; gap: 12px; margin-top: 10px; }}
  .tr-item {{ display: flex; gap: 12px; align-items: flex-start; }}
  .tr-num {{
    width: 26px;
    height: 26px;
    border-radius: 8px;
    background: {c['primary']};
    color: #FFFFFF;
    font-weight: 700;
    font-size: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
  }}
  .tr-item strong {{ display: block; font-size: 13px; color: {c['textPrimary']}; }}
  .tr-item p {{ font-size: 12px; color: {c['textSecondary']}; margin-top: 2px; }}
  .ex-list {{ display: flex; flex-direction: column; gap: 9px; }}
  .ex-item {{
    background: {bg_card};
    border: 1px solid {c['border']};
    border-left: 4px solid #5F6F7E;
    border-radius: 10px;
    padding: 10px 14px;
  }}
  .ex-item strong {{ display: block; font-size: 12.8px; color: {c['textPrimary']}; margin-bottom: 2px; }}
  .ex-item p {{ font-size: 11.6px; color: {c['textSecondary']}; }}

  /* Día Base */
  .db-list {{ display: flex; flex-direction: column; gap: 11px; margin-top: 6px; }}
  .db-row {{
    display: flex;
    gap: 14px;
    align-items: flex-start;
    background: {bg_card};
    border: 1px solid {c['border']};
    border-radius: 12px;
    padding: 13px 16px;
  }}
  .db-icon {{
    width: 38px;
    height: 38px;
    border-radius: 10px;
    background: {c['primarySoft']};
    color: {c['primary']};
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
  }}
  .db-row h3 {{ font-family: 'Lora', Georgia, serif; font-size: 14.5px; margin-bottom: 3px; }}
  .db-row p {{ font-size: 12px; color: {c['textSecondary']}; line-height: 1.48; }}

  /* Cierre y Contraportada */
  .goodbye-wrap {{
    margin: auto 0;
    text-align: center;
    padding: 0 36px;
  }}
  .goodbye-brand {{ font-size: 14px; font-weight: 700; letter-spacing: 0.2em; margin-top: 12px; color: {c['primary']}; }}
  .goodbye-title {{ font-family: 'Lora', Georgia, serif; font-size: 28px; font-weight: 600; margin-bottom: 18px; }}
  .goodbye-p {{ font-size: 15px; line-height: 1.75; color: {c['textSecondary']}; margin-bottom: 14px; }}
  .goodbye-sign {{ margin-top: 26px; font-family: 'Lora', Georgia, serif; font-style: italic; font-size: 15px; color: {c['primary']}; }}

  .back-cover {{
    margin: auto 0;
    text-align: center;
  }}
  .back-brand {{ font-size: 22px; font-weight: 700; letter-spacing: 0.24em; margin-top: 18px; color: {c['textPrimary']}; }}
  .back-sub {{ font-size: 13px; color: {c['textSecondary']}; margin-top: 6px; }}
  .back-slogan {{ font-family: 'Lora', Georgia, serif; font-style: italic; font-size: 18px; color: {c['accent']}; margin: 18px 0 36px; }}
  .back-meta {{ display: inline-flex; gap: 10px; padding: 10px 20px; border-radius: 999px; background: {bg_tinted}; font-size: 11.5px; color: {c['textSecondary']}; font-weight: 600; }}
</style>
</head>
<body>
  {"".join(pages)}
</body>
</html>
"""


def scrub_metadata(pdf_path: Path, meta: dict) -> None:
    """Limpia por completo metadatos del navegador y asigna metadatos institucionales anónimos."""
    tmp_path = pdf_path.with_suffix(".tmp.pdf")
    doc = pymupdf.open(pdf_path)
    doc.set_metadata({
        "title": meta["title"],
        "author": meta["author"],
        "subject": f"{meta['methodFull']} — {meta['subtitle']}",
        "keywords": f"VIDA EN ORDEN, Método VIDA, Sistema de 30 Días, {meta['instagram']}",
        "creator": meta["author"],
        "producer": meta["author"],
    })
    doc.save(tmp_path, garbage=4, deflate=True)
    doc.close()
    tmp_path.replace(pdf_path)


def render_pdf(html_str: str, out_path: Path, meta: dict, expected_pages: int) -> None:
    chrome_path = shutil.which("google-chrome") or shutil.which("chromium") or shutil.which("chromium-browser")
    launch_kwargs = {"headless": True}
    if chrome_path:
        launch_kwargs["executable_path"] = chrome_path

    with sync_playwright() as p:
        browser = p.chromium.launch(**launch_kwargs)
        page = browser.new_page(viewport={"width": 816, "height": 1056})
        page.set_content(html_str, wait_until="networkidle")
        page.evaluate("() => document.fonts.ready")
        page.pdf(
            path=str(out_path),
            format="Letter",
            print_background=True,
            margin={"top": "0", "right": "0", "bottom": "0", "left": "0"},
            prefer_css_page_size=True,
        )
        browser.close()

    scrub_metadata(out_path, meta)

    doc = pymupdf.open(out_path)
    actual = len(doc)
    md = doc.metadata
    doc.close()
    if actual != expected_pages:
        raise RuntimeError(f"{out_path.name}: se esperaban {expected_pages} páginas, pero se generaron {actual} (posible desborde CSS).")
    size_kb = out_path.stat().st_size / 1024
    print(f"✓ {out_path.relative_to(REPO_ROOT)} — {actual} págs · {size_kb:.0f} KB · Author={md.get('author')!r}")


def main() -> None:
    tokens = json.loads(TOKENS_PATH.read_text(encoding="utf-8"))
    content = json.loads(CONTENT_PATH.read_text(encoding="utf-8"))
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    pages, toc_map = build_pages(tokens, content)
    expected = len(pages)
    print(f"Generando sistema completo ({expected} páginas verificadas)...")
    print("Mapa de índice:", json.dumps(toc_map, ensure_ascii=False))

    # 1. Edición Digital Editorial
    html_digital = build_html_document(tokens, pages, print_mode=False)
    render_pdf(html_digital, OUT_DIR / "VIDA-EN-ORDEN-Sistema-30-Dias-Digital.pdf", content["meta"], expected)

    # 2. Edición Imprimible (ahorro de tinta)
    html_print = build_html_document(tokens, pages, print_mode=True)
    render_pdf(html_print, OUT_DIR / "VIDA-EN-ORDEN-Sistema-30-Dias-Impresion.pdf", content["meta"], expected)

    print("\nListo: ambas ediciones generadas sin metadatos personales y con 100% de coherencia.")


if __name__ == "__main__":
    main()
