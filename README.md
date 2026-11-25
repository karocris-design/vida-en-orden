# VIDA EN ORDEN — *Menos ruido. Más vida.*

Monorepo operativo del proyecto **VIDA EN ORDEN**: producto digital híbrido (PDF + Webapp interactiva de 30 días), Departamento de Marketing (Máquina de Carruseles y Reels *faceless*) y Mesa de Juntas (roles ejecutivos + panel móvil para iPhone).

## Estructura del Proyecto

- `marca/` — Tokens visuales unificados (`design-tokens.json`) y guía editorial (`identidad.md`).
- `producto/`
  - `webapp/` — Webapp móvil gratuita/híbrida: **Test V.I.D.A.** (Etapa 1) + futuro sistema completo de 30 días (Etapa 3).
  - `pdf-fuente/` — Documento original de 89 páginas (`Orden y crecimiento personal.pdf`) y auditoría editorial (Etapa 2).
- `marketing/` — Arquitectura de la Máquina de Carruseles (`HTML → PNG 1080×1350`) y Reels (`FFmpeg` + demos *faceless*) replicable en Mac.
- `mesa-de-juntas/`
  - `directores/` — Perfiles operativos (Estrategia, Producto, Marketing, Finanzas) para sesiones de junta.
  - `panel-movil/` — Panel ligero *mobile-first* para consultar avances, meta mensual y aprobar piezas desde el iPhone.
  - `decisiones.md` y `roadmap.md` — Bitácora viva del negocio.
- `scripts/setup-mac.sh` — Script de instalación para replicar este entorno localmente en tu Mac.

## Uso Local (Nube o Mac)

```bash
# Clonar y preparar entorno en Mac
chmod +x scripts/setup-mac.sh
./scripts/setup-mac.sh

# Previsualizar sitio (Webapp + Panel de Mesa de Juntas)
npx serve -l 4173 .
```

## Despliegue Gratuito ($0)

El proyecto funciona como sitio estático sin backend obligatorio (`localStorage` + exportación de progreso), listo para publicarse gratis en **GitHub Pages** o **Vercel**:
- `/` → Test V.I.D.A. (y futuro portal de 30 días)
- `/mesa-de-juntas/panel-movil/` → Mesa de Juntas para iPhone
