# Departamento de Marketing — Máquina de Carruseles y Reels

Diseñada para funcionar **igual en la nube (Linux) y localmente en tu Mac**, alimentándose directamente de `../marca/design-tokens.json` para garantizar estética consistente con **\$0 de inversión**.

## Arquitectura de Producción (Marca Anónima)

### 1. Máquina de Carruseles (`marketing/carruseles/`)
- **Formato:** PNG 1080×1350 (Instagram y TikTok) y 1000×1500 (Pinterest).
- **Flujo:** Guion en `carruseles.json` + fotografías editoriales en `assets/` + tokens de `marca/design-tokens.json` → `python3 marketing/carruseles/generar.py` → Exportación automática de todas las diapositivas en PNG (Playwright / Chromium headless).
- **Galería móvil (iPhone):** `marketing/carruseles/index.html` permite previsualizar, descargar los PNG 1080×1350 y copiar el texto + hashtags con un toque.
- **Ventaja:** Cero edición manual en Canva; si ajustamos tipografía, fotos o colores, todos los carruseles se actualizan al instante.

### 2. Máquina de Reels *Faceless* (`marketing/reels/`)
- **Formato:** MP4 vertical 1080×1920 (9:16), 20–35 segundos.
- **Formatos ganadores sin mostrar rostro:**
  1. **Demo real de la Webapp:** Grabación limpia de alguien haciendo el Test V.I.D.A. o armando su *Día Base* con texto editorial encima.
  2. **Tipografía animada sobre fondo crema/salvia:** Una idea fuerte del método (*"Un día ordenado no es perfecto. Es un día donde tú llevas el volante"*) + microacción de 10 segundos.
  3. **Comparativa visual:** "Día en piloto automático vs. Día con Triple Ancla".
- **Motor:** `FFmpeg` + plantillas HTML/Canvas (mismo comando en Linux y macOS).

## Regla del Embudo Orgánico
Toda pieza termina con una llamada clara y sin presión hacia el **Test V.I.D.A. gratuito** ("Evalúa tus 5 dimensiones en 3 minutos — enlace en bio").
