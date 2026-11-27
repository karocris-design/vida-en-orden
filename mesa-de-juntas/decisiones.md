# Bitácora de Decisiones — VIDA EN ORDEN

Registro vivo de acuerdos tomados en la Mesa de Juntas.

## 2026-11-25 — Sesión de Arranque (`/grill-me`)

1. **Arquitectura del negocio:** Monorepo Git con 4 módulos (`marca`, `producto`, `marketing`, `mesa-de-juntas`) diseñado en la nube y portable a macOS (`scripts/setup-mac.sh`).
2. **Orden de ataque:** Construir primero el **Test V.I.D.A.** (Etapa 1) para pruebas de claridad con esposa e hijas (15 y 9 años), manteniendo lista la base de Mesa de Juntas y Marketing.
3. **Embudo y modelo de acceso (\$0, sin cuentas):**
   - Test V.I.D.A. (5 dimensiones) **gratis** como imán orgánico en redes.
   - Programa de 30 días desbloqueado con clave/enlace local al comprar (\$99 PDF / \$199 PDF+Webapp), con persistencia en `localStorage` y respaldo exportable.
4. **Identidad visual unificada:** Minimalista cálida tipo cuaderno editorial (`#FAF7F2` crema, `#4A5D4E` salvia, `#C67D5B` terracota, `#232320` carbón; *Lora* + *Plus Jakarta Sans*).
5. **Mesa de Juntas (2 capas):** Directores + bitácora en Git + panel web móvil optimizado para iPhone.
6. **Máquina de Marketing (próxima fase):** Carruseles `HTML → PNG 1080×1350` + Reels *faceless* con demos de webapp y `FFmpeg`.
7. **Fuente editorial incorporada:** Se descargó `Orden y crecimiento personal.pdf` (89 páginas) desde Google Drive y se extrajo su texto base para alinear el Test V.I.D.A. y preparar la auditoría editorial de Etapa 2.

## 2026-11-27 — Cierre de Etapa 2 (PDF Editorial Coherente v2)

1. **Reconstrucción en pipeline propio (Opción A):** Se generó el sistema completo desde `producto/sistema-30-dias/contenido.json` + `generar_pdf.py` usando los tokens exactos de `marca/design-tokens.json` (*Lora* + *Plus Jakarta Sans*, paleta crema/salvia/terracota), produciendo **2 ediciones de 87 páginas** (Digital Editorial + Imprimible ahorro de tinta) con metadatos 100% anónimos y 0 desbordes verificados.
2. **Terminología unificada en todo el ecosistema:** Regla 3–2–1 oficial = **Necesario (3) / Útil (2) / Impulso (1)** en PDF, Webapp y Carruseles; TPU integrada desde Semana 2; Día 20 redactado nuevo (*La regla de pausa de 24 horas*); 30 hojas exactas de Diario numeradas con frase guía; tabla comparativa Día 1 vs. Día 30 y hoja rellenable de Mi Día Base agregadas.
3. **Redes oficiales confirmadas:** Instagram `@vida.orden` y enlace `linktr.ee/VidaOrden` unificados en portada, contraportada, Test Inicial y `marca/identidad.md`.
4. **Protección del producto de pago:** Los archivos `.pdf` compilados en `producto/sistema-30-dias/output/` quedan excluidos de Git (`.gitignore`) para no exponerse públicamente en GitHub Pages.
