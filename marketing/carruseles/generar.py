#!/usr/bin/env python3
"""
Máquina de Carruseles — VIDA EN ORDEN
Genera diapositivas PNG 1080x1350 conectadas a marca/design-tokens.json.
Funciona igual en Linux (nube) y macOS.
"""

import html
import json
import os
import shutil
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_DIR = Path(__file__).resolve().parent
REPO_ROOT = BASE_DIR.parent.parent
TOKENS_PATH = REPO_ROOT / "marca" / "design-tokens.json"
DATA_PATH = BASE_DIR / "carruseles.json"
OUT_DIR = BASE_DIR / "output"

RADAR_SVG = """
<svg viewBox="-50 0 460 310" width="420" height="283" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
  <polygon points="180,46 286,123 245,248 115,248 74,123" fill="rgba(242,236,225,0.45)" stroke="#DDD4C5" stroke-width="1.5"/>
  <polygon points="180,73 260,131 229,225 131,225 100,131" fill="none" stroke="#DDD4C5" stroke-width="1.2"/>
  <polygon points="180,100 233,139 213,202 147,202 127,139" fill="rgba(242,236,225,0.45)" stroke="#DDD4C5" stroke-width="1.2"/>
  <polygon points="180,127 207,147 196,179 164,179 153,147" fill="none" stroke="#DDD4C5" stroke-width="1.2"/>
  <line x1="180" y1="158" x2="180" y2="46" stroke="#DDD4C5" stroke-width="1.2"/>
  <line x1="180" y1="158" x2="286" y2="123" stroke="#DDD4C5" stroke-width="1.2"/>
  <line x1="180" y1="158" x2="245" y2="248" stroke="#DDD4C5" stroke-width="1.2"/>
  <line x1="180" y1="158" x2="115" y2="248" stroke="#DDD4C5" stroke-width="1.2"/>
  <line x1="180" y1="158" x2="74" y2="123" stroke="#DDD4C5" stroke-width="1.2"/>
  <polygon points="180,76 268,129 224,220 132,226 98,132" fill="rgba(74,93,78,0.22)" stroke="#4A5D4E" stroke-width="3.2" stroke-linejoin="round"/>
  <circle cx="180" cy="76" r="6.5" fill="#4A5D4E" stroke="#FFFFFF" stroke-width="2.5"/>
  <circle cx="268" cy="129" r="6.5" fill="#C67D5B" stroke="#FFFFFF" stroke-width="2.5"/>
  <circle cx="224" cy="220" r="6.5" fill="#6E8572" stroke="#FFFFFF" stroke-width="2.5"/>
  <circle cx="132" cy="226" r="6.5" fill="#9B7B54" stroke="#FFFFFF" stroke-width="2.5"/>
  <circle cx="98" cy="132" r="6.5" fill="#5F6F7E" stroke="#FFFFFF" stroke-width="2.5"/>
  <text x="180" y="29" text-anchor="middle" fill="#232320" font-size="18" font-weight="700" font-family="Plus Jakarta Sans, sans-serif">Mente</text>
  <text x="298" y="128" text-anchor="start" fill="#232320" font-size="18" font-weight="700" font-family="Plus Jakarta Sans, sans-serif">Tiempo</text>
  <text x="255" y="274" text-anchor="middle" fill="#232320" font-size="18" font-weight="700" font-family="Plus Jakarta Sans, sans-serif">Energía</text>
  <text x="105" y="274" text-anchor="middle" fill="#232320" font-size="18" font-weight="700" font-family="Plus Jakarta Sans, sans-serif">Dinero</text>
  <text x="62" y="128" text-anchor="end" fill="#232320" font-size="18" font-weight="700" font-family="Plus Jakarta Sans, sans-serif">Hábitos</text>
</svg>
"""


def esc(text: str) -> str:
    return html.escape(str(text or ""))


def render_body(slide: dict, accent: str) -> str:
    stype = slide["type"]

    if stype == "cover":
        return f"""
        <div class="cover-wrap">
          <div class="accent-bar" style="background: {accent};"></div>
          <p class="eyebrow" style="color: {accent};">{esc(slide['eyebrow'])}</p>
          <h1 class="cover-title">
            {esc(slide['headline'])}
            <span class="cover-highlight" style="color: {accent};">{esc(slide['highlight'])}</span>
          </h1>
          <p class="cover-subtitle">{esc(slide['subtitle'])}</p>
          <div class="cover-footer-chip">
            <span class="chip-dot" style="background: {accent};"></span>
            <span>Método V.I.D.A. · Orden simple en 10 min/día</span>
          </div>
        </div>
        """

    if stype == "contrast":
        bad_li = "".join(f'<li><span class="mark mark-bad">✕</span><span>{esc(x)}</span></li>' for x in slide["badItems"])
        good_li = "".join(f'<li><span class="mark mark-good">✓</span><span>{esc(x)}</span></li>' for x in slide["goodItems"])
        return f"""
        <div class="content-wrap">
          <p class="eyebrow" style="color: {accent};">{esc(slide['eyebrow'])}</p>
          <h2 class="slide-title">{esc(slide['headline'])}</h2>
          <div class="contrast-stack">
            <div class="paper-card card-muted">
              <div class="card-tag card-tag-muted">{esc(slide['badTitle'])}</div>
              <ul class="bullet-list">{bad_li}</ul>
            </div>
            <div class="paper-card card-featured" style="border-left: 8px solid {accent};">
              <div class="card-tag" style="color: {accent};">{esc(slide['goodTitle'])}</div>
              <ul class="bullet-list">{good_li}</ul>
            </div>
          </div>
        </div>
        """

    if stype == "concept":
        return f"""
        <div class="content-wrap">
          <p class="eyebrow" style="color: {accent};">{esc(slide['eyebrow'])}</p>
          <h2 class="slide-title">{esc(slide['headline'])}</h2>
          <div class="paper-card concept-main">
            <p class="body-lg">{esc(slide['body'])}</p>
          </div>
          <div class="callout-card" style="border-left: 7px solid {accent};">
            <p class="callout-label" style="color: {accent};">{esc(slide['calloutLabel'])}</p>
            <p class="callout-text">{esc(slide['calloutText'])}</p>
          </div>
        </div>
        """

    if stype == "steps":
        cards = []
        for item in slide["items"]:
            cards.append(f"""
            <div class="paper-card step-card">
              <div class="step-num" style="background: {accent};">{esc(item['num'])}</div>
              <div class="step-copy">
                <h3>{esc(item['title'])}</h3>
                <p>{esc(item['desc'])}</p>
              </div>
            </div>
            """)
        return f"""
        <div class="content-wrap">
          <p class="eyebrow" style="color: {accent};">{esc(slide['eyebrow'])}</p>
          <h2 class="slide-title">{esc(slide['headline'])}</h2>
          <div class="steps-stack">
            {''.join(cards)}
          </div>
        </div>
        """

    if stype == "quote":
        return f"""
        <div class="quote-wrap">
          <div class="quote-rule"></div>
          <p class="quote-eyebrow">{esc(slide['eyebrow'])}</p>
          <blockquote class="quote-text">{esc(slide['quote'])}</blockquote>
          <p class="quote-subnote">{esc(slide['subnote'])}</p>
        </div>
        """

    if stype == "cta":
        return f"""
        <div class="cta-wrap">
          <p class="eyebrow" style="color: {accent};">{esc(slide['eyebrow'])}</p>
          <h2 class="cta-title">{esc(slide['headline'])}</h2>
          <div class="cta-radar-card">
            {RADAR_SVG}
          </div>
          <p class="cta-body">{esc(slide['body'])}</p>
          <div class="cta-pill" style="background: #4A5D4E;">
            <span>{esc(slide['badge'])}</span>
          </div>
        </div>
        """

    raise ValueError(f"Tipo de slide no soportado: {stype}")


def build_slide_html(tokens: dict, carousel: dict, slide: dict, idx: int, total: int) -> str:
    colors = tokens["colors"]
    accent = colors["dimensions"].get(carousel.get("accentDim", "mente"), colors["primary"])
    stype = slide["type"]
    quote_theme = slide.get("theme", "sage") if stype == "quote" else ""
    is_dark = stype == "quote" and quote_theme == "sage"
    is_warm = stype == "quote" and quote_theme == "warm"

    dots = "".join(
        f'<span class="dot {"active" if i == idx else ""}"></span>'
        for i in range(total)
    )
    footer_right = "Guarda este post ↗" if idx == total - 1 else "Desliza →"
    body_html = render_body(slide, accent)

    bg_class = "theme-sage" if is_dark else ("theme-warm" if is_warm else "theme-paper")

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8" />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Lora:ital,wght@0,500;0,600;1,400;1,500&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap" rel="stylesheet" />
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    html, body {{
      width: 1080px;
      height: 1350px;
      overflow: hidden;
      font-family: {tokens['typography']['fontBody']};
      -webkit-font-smoothing: antialiased;
    }}
    .canvas {{
      width: 1080px;
      height: 1350px;
      padding: 72px 84px 66px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      position: relative;
    }}
    .theme-paper {{
      background-color: {colors['bgPrimary']};
      background-image:
        radial-gradient(circle at 12% 6%, rgba(239, 231, 218, 0.9) 0%, transparent 44%),
        radial-gradient(circle at 90% 92%, rgba(231, 236, 232, 0.78) 0%, transparent 46%);
      color: {colors['textPrimary']};
    }}
    .theme-sage {{
      background: linear-gradient(155deg, #4A5D4E 0%, #3A4B3E 100%);
      color: #FAF7F2;
    }}
    .theme-warm {{
      background: linear-gradient(160deg, #F3EBDD 0%, #EAE0CE 100%);
      color: {colors['textPrimary']};
    }}

    /* TOP & FOOTER */
    .slide-top {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding-bottom: 26px;
      border-bottom: 1.5px solid rgba(35, 35, 32, 0.12);
    }}
    .theme-sage .slide-top {{
      border-bottom-color: rgba(250, 247, 242, 0.22);
    }}
    .brand-lockup {{
      display: flex;
      align-items: center;
      gap: 18px;
    }}
    .brand-name {{
      font-size: 20px;
      font-weight: 700;
      letter-spacing: 0.2em;
      color: {colors['primary']};
    }}
    .theme-sage .brand-name {{
      color: #FAF7F2;
    }}
    .brand-sep {{
      width: 1.5px;
      height: 20px;
      background: rgba(35, 35, 32, 0.2);
    }}
    .theme-sage .brand-sep {{
      background: rgba(250, 247, 242, 0.35);
    }}
    .brand-pilar {{
      font-size: 20px;
      font-weight: 500;
      color: {colors['textSecondary']};
    }}
    .theme-sage .brand-pilar {{
      color: rgba(250, 247, 242, 0.82);
    }}
    .slide-counter {{
      font-size: 20px;
      font-weight: 700;
      font-variant-numeric: tabular-nums;
      color: {colors['textSecondary']};
      background: rgba(35, 35, 32, 0.06);
      padding: 8px 20px;
      border-radius: 999px;
    }}
    .theme-sage .slide-counter {{
      background: rgba(250, 247, 242, 0.14);
      color: #FAF7F2;
    }}

    .slide-main {{
      flex: 1;
      display: flex;
      flex-direction: column;
      justify-content: center;
      padding: 28px 0;
    }}

    .slide-footer {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding-top: 24px;
      border-top: 1.5px solid rgba(35, 35, 32, 0.12);
    }}
    .theme-sage .slide-footer {{
      border-top-color: rgba(250, 247, 242, 0.22);
    }}
    .slogan {{
      font-family: {tokens['typography']['fontHeading']};
      font-style: italic;
      font-size: 23px;
      color: {colors['textSecondary']};
    }}
    .theme-sage .slogan {{
      color: rgba(250, 247, 242, 0.82);
    }}
    .footer-right {{
      display: flex;
      align-items: center;
      gap: 24px;
    }}
    .dots {{
      display: flex;
      gap: 8px;
      align-items: center;
    }}
    .dot {{
      width: 9px;
      height: 9px;
      border-radius: 999px;
      background: rgba(35, 35, 32, 0.2);
    }}
    .dot.active {{
      width: 28px;
      background: {colors['primary']};
    }}
    .theme-sage .dot {{
      background: rgba(250, 247, 242, 0.3);
    }}
    .theme-sage .dot.active {{
      background: #FAF7F2;
    }}
    .swipe-cue {{
      font-size: 21px;
      font-weight: 700;
      color: {colors['textPrimary']};
    }}
    .theme-sage .swipe-cue {{
      color: #FAF7F2;
    }}

    /* SHARED TYPOGRAPHY */
    .eyebrow {{
      font-size: 22px;
      font-weight: 700;
      letter-spacing: 0.14em;
      text-transform: uppercase;
      margin-bottom: 20px;
    }}
    .slide-title {{
      font-family: {tokens['typography']['fontHeading']};
      font-size: 56px;
      font-weight: 500;
      line-height: 1.18;
      letter-spacing: -0.015em;
      margin-bottom: 42px;
      color: {colors['textPrimary']};
    }}

    /* COVER */
    .cover-wrap {{
      display: flex;
      flex-direction: column;
      justify-content: center;
    }}
    .accent-bar {{
      width: 92px;
      height: 6px;
      border-radius: 999px;
      margin-bottom: 34px;
    }}
    .cover-title {{
      font-family: {tokens['typography']['fontHeading']};
      font-size: 74px;
      font-weight: 500;
      line-height: 1.14;
      letter-spacing: -0.02em;
      color: {colors['textPrimary']};
      margin-bottom: 36px;
    }}
    .cover-highlight {{
      display: block;
      margin-top: 10px;
      font-style: italic;
      font-weight: 600;
    }}
    .cover-subtitle {{
      font-size: 32px;
      line-height: 1.48;
      color: {colors['textSecondary']};
      max-width: 820px;
      margin-bottom: 48px;
    }}
    .cover-footer-chip {{
      display: inline-flex;
      align-items: center;
      gap: 14px;
      align-self: flex-start;
      background: #FFFFFF;
      border: 1.5px solid {colors['border']};
      padding: 16px 26px;
      border-radius: 999px;
      font-size: 23px;
      font-weight: 600;
      color: {colors['textPrimary']};
      box-shadow: 0 8px 24px rgba(35, 35, 32, 0.05);
    }}
    .chip-dot {{
      width: 12px;
      height: 12px;
      border-radius: 50%;
    }}

    /* PAPER CARDS */
    .paper-card {{
      background: #FFFFFF;
      border: 1.5px solid {colors['border']};
      border-radius: 26px;
      padding: 36px 40px;
      box-shadow: 0 12px 30px rgba(35, 35, 32, 0.05);
    }}

    /* CONTRAST */
    .contrast-stack {{
      display: flex;
      flex-direction: column;
      gap: 28px;
    }}
    .card-muted {{
      background: #F4EFE6;
      border-color: #E0D7C8;
      box-shadow: none;
    }}
    .card-tag {{
      font-size: 21px;
      font-weight: 700;
      letter-spacing: 0.1em;
      text-transform: uppercase;
      margin-bottom: 22px;
    }}
    .card-tag-muted {{
      color: #7A746B;
    }}
    .bullet-list {{
      list-style: none;
      display: flex;
      flex-direction: column;
      gap: 18px;
    }}
    .bullet-list li {{
      display: flex;
      align-items: flex-start;
      gap: 18px;
      font-size: 29px;
      line-height: 1.38;
      color: {colors['textPrimary']};
    }}
    .card-muted .bullet-list li {{
      color: #544F48;
    }}
    .mark {{
      width: 38px;
      height: 38px;
      border-radius: 50%;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      font-size: 20px;
      font-weight: 700;
      flex-shrink: 0;
      margin-top: 2px;
    }}
    .mark-bad {{
      background: rgba(132, 127, 118, 0.2);
      color: #6B655D;
    }}
    .mark-good {{
      background: #E7ECE8;
      color: #3B4B3E;
    }}

    /* CONCEPT */
    .concept-main {{
      margin-bottom: 30px;
      padding: 44px 46px;
    }}
    .body-lg {{
      font-size: 34px;
      line-height: 1.52;
      color: {colors['textPrimary']};
    }}
    .callout-card {{
      background: #F2ECE1;
      border-radius: 0 24px 24px 0;
      padding: 36px 42px;
    }}
    .callout-label {{
      font-size: 20px;
      font-weight: 700;
      letter-spacing: 0.12em;
      text-transform: uppercase;
      margin-bottom: 14px;
    }}
    .callout-text {{
      font-family: {tokens['typography']['fontHeading']};
      font-style: italic;
      font-size: 33px;
      line-height: 1.44;
      color: {colors['textPrimary']};
    }}

    /* STEPS */
    .steps-stack {{
      display: flex;
      flex-direction: column;
      gap: 24px;
    }}
    .step-card {{
      display: flex;
      align-items: flex-start;
      gap: 28px;
      padding: 32px 36px;
    }}
    .step-num {{
      width: 64px;
      height: 64px;
      border-radius: 18px;
      color: #FFFFFF;
      font-size: 26px;
      font-weight: 700;
      display: flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
      margin-top: 2px;
    }}
    .step-copy h3 {{
      font-size: 32px;
      font-weight: 700;
      line-height: 1.26;
      color: {colors['textPrimary']};
      margin-bottom: 10px;
    }}
    .step-copy p {{
      font-size: 26px;
      line-height: 1.44;
      color: {colors['textSecondary']};
    }}

    /* QUOTE */
    .quote-wrap {{
      display: flex;
      flex-direction: column;
      align-items: flex-start;
      justify-content: center;
      padding: 0 10px;
    }}
    .quote-rule {{
      width: 84px;
      height: 5px;
      border-radius: 999px;
      background: {colors['accent']};
      margin-bottom: 34px;
    }}
    .theme-sage .quote-rule {{
      background: #E2A98C;
    }}
    .quote-eyebrow {{
      font-size: 22px;
      font-weight: 700;
      letter-spacing: 0.16em;
      text-transform: uppercase;
      opacity: 0.82;
      margin-bottom: 28px;
    }}
    .quote-text {{
      font-family: {tokens['typography']['fontHeading']};
      font-size: 66px;
      font-weight: 500;
      line-height: 1.24;
      letter-spacing: -0.015em;
      margin-bottom: 42px;
    }}
    .quote-subnote {{
      font-size: 30px;
      line-height: 1.48;
      opacity: 0.88;
      max-width: 780px;
    }}

    /* CTA */
    .cta-wrap {{
      display: flex;
      flex-direction: column;
      align-items: center;
      text-align: center;
    }}
    .cta-title {{
      font-family: {tokens['typography']['fontHeading']};
      font-size: 54px;
      font-weight: 500;
      line-height: 1.18;
      margin-bottom: 30px;
      max-width: 860px;
      color: {colors['textPrimary']};
    }}
    .cta-radar-card {{
      background: #FFFFFF;
      border: 1.5px solid {colors['border']};
      border-radius: 30px;
      padding: 24px 44px;
      margin-bottom: 32px;
      box-shadow: 0 14px 34px rgba(35, 35, 32, 0.06);
      display: flex;
      align-items: center;
      justify-content: center;
    }}
    .cta-body {{
      font-size: 28px;
      line-height: 1.46;
      color: {colors['textSecondary']};
      max-width: 820px;
      margin-bottom: 34px;
    }}
    .cta-pill {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      padding: 22px 42px;
      border-radius: 999px;
      color: #FFFFFF;
      font-size: 26px;
      font-weight: 700;
      letter-spacing: 0.01em;
      box-shadow: 0 12px 28px rgba(74, 93, 78, 0.25);
    }}
  </style>
</head>
<body>
  <div class="canvas {bg_class}">
    <header class="slide-top">
      <div class="brand-lockup">
        <span class="brand-name">{esc(tokens['brand']['name'])}</span>
        <span class="brand-sep"></span>
        <span class="brand-pilar">{esc(carousel['pilar'])}</span>
      </div>
      <div class="slide-counter">{idx + 1:02d} / {total:02d}</div>
    </header>

    <main class="slide-main">
      {body_html}
    </main>

    <footer class="slide-footer">
      <span class="slogan">{esc(tokens['brand']['slogan'])}</span>
      <div class="footer-right">
        <div class="dots">{dots}</div>
        <span class="swipe-cue">{footer_right}</span>
      </div>
    </footer>
  </div>
</body>
</html>
"""


def main():
    tokens = json.loads(TOKENS_PATH.read_text(encoding="utf-8"))
    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    chrome_path = shutil.which("google-chrome") or shutil.which("chromium") or shutil.which("chromium-browser")
    launch_kwargs = {"headless": True}
    if chrome_path:
        launch_kwargs["executable_path"] = chrome_path

    manifest = {"carruseles": []}

    with sync_playwright() as p:
        browser = p.chromium.launch(**launch_kwargs)
        page = browser.new_page(viewport={"width": 1080, "height": 1350}, device_scale_factor=1)

        for carousel in data["carruseles"]:
            cdir = OUT_DIR / carousel["id"]
            cdir.mkdir(parents=True, exist_ok=True)
            slides = carousel["slides"]
            slide_paths = []

            for i, slide in enumerate(slides):
                html_doc = build_slide_html(tokens, carousel, slide, i, len(slides))
                page.set_content(html_doc, wait_until="networkidle")
                page.evaluate("() => document.fonts.ready")
                out_file = cdir / f"slide-{i + 1:02d}.png"
                page.screenshot(path=str(out_file), full_page=False)
                slide_paths.append(f"output/{carousel['id']}/slide-{i + 1:02d}.png")
                print(f"✓ {out_file.relative_to(REPO_ROOT)}")

            manifest["carruseles"].append({
                "id": carousel["id"],
                "numero": carousel["numero"],
                "pilar": carousel["pilar"],
                "titulo": carousel["titulo"],
                "captionIG": carousel["captionIG"],
                "hashtags": carousel["hashtags"],
                "slides": slide_paths
            })

        browser.close()

    manifest_path = OUT_DIR / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nListo: {len(manifest['carruseles'])} carruseles generados en {OUT_DIR.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
