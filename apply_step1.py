#!/usr/bin/env python3
"""Apply step 1 clean redesign. Reads index.html, writes index-step1.html."""
import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
INDEX = BASE / "index.html"
OUT = BASE / "index-step1.html"
CSS = BASE / "step1.css"

STICKY = """
<div id="stickyBar" class="sticky-bar">
    <div class="sticky-bar-inner">
        <div class="sticky-total">
            <div class="sticky-total-label">Total</div>
            <div class="sticky-total-value" id="stickyTotal">R$ 0</div>
        </div>
        <button class="btn btn-generar" id="generarBtn">Generar WhatsApp</button>
    </div>
</div>
"""

SYNC_FN = """
function syncStickyTotal(id) {
  const active = document.querySelector('.tab.active');
  if (!active || parseInt(active.getAttribute('data-option'), 10) !== id) return;
  const tot = document.getElementById('total-prev-' + id);
  const sticky = document.getElementById('stickyTotal');
  if (tot && sticky) sticky.textContent = tot.textContent;
}
"""

CREAR_OPCION = r'''function crearContenidoOpcion(id) {
  const hc = ['c1','c2','c3','c4','c5'][(id - 1) % 5];
  return `
  <div class="option-card">
    <div class="option-card-header ${hc}">Opción ${id}</div>
    <div class="option-card-body">
      <div class="form-section">
        <div class="section-title">Temporada & Pago</div>
        <div class="form-group">
          <label>Temporada</label>
          <div class="radio-group-4">
            <div class="radio-option"><input type="radio" name="temp-${id}" value="LOW" id="t-low-${id}"><label for="t-low-${id}">LOW<br><small>Feb–Mar</small></label></div>
            <div class="radio-option"><input type="radio" name="temp-${id}" value="MID" id="t-mid-${id}"><label for="t-mid-${id}">MID<br><small>May–Jun, Dic</small></label></div>
            <div class="radio-option"><input type="radio" name="temp-${id}" value="HIGH" id="t-high-${id}"><label for="t-high-${id}">HIGH<br><small>Jul–Nov</small></label></div>
            <div class="radio-option"><input type="radio" name="temp-${id}" value="AÑONUEVO" id="t-an-${id}"><label for="t-an-${id}">AÑO NUEVO</label></div>
          </div>
        </div>
        <div class="form-group">
          <label>Forma de pago</label>
          <div class="radio-group">
            <div class="radio-option"><input type="radio" name="pago-${id}" value="tarjeta" id="pago-t-${id}" checked><label for="pago-t-${id}">💳 Tarjeta</label></div>
            <div class="radio-option pago-efectivo"><input type="radio" name="pago-${id}" value="efectivo" id="pago-e-${id}"><label for="pago-e-${id}">💵 Efectivo / Pix<br><small>(-10%)</small></label></div>
          </div>
        </div>
        <div class="form-group"><label>Personas (1–3)</label><input type="number" id="pers-${id}" min="1" max="3" value="1"></div>
      </div>
      <div class="form-section">
        <div class="section-title">Hospedaje</div>
        <div class="form-group">
          <label>Habitación</label>
          <div class="radio-group-5">
            <div class="radio-option"><input type="radio" name="hab-${id}" value="Compartida 8 (Aire)" id="h-c8-${id}"><label for="h-c8-${id}">Comp. 8 · Aire</label></div>
            <div class="radio-option"><input type="radio" name="hab-${id}" value="Compartida Vent." id="h-cv-${id}"><label for="h-cv-${id}">Comp. Ventilador</label></div>
            <div class="radio-option"><input type="radio" name="hab-${id}" value="Compartida Aire (Fem)" id="h-ca-${id}"><label for="h-ca-${id}">Comp. Fem · Aire</label></div>
            <div class="radio-option"><input type="radio" name="hab-${id}" value="Privada s/Aire" id="h-psa-${id}"><label for="h-psa-${id}">Privada s/Aire</label></div>
            <div class="radio-option"><input type="radio" name="hab-${id}" value="Privada c/Aire" id="h-pca-${id}"><label for="h-pca-${id}">Privada c/Aire Suite</label></div>
          </div>
        </div>
        <div class="form-group"><label>Noches</label><input type="number" id="noches-${id}" min="1" value="1"></div>
        <div class="form-group">
          <label>¿Desayuno?</label>
          <div class="radio-group">
            <div class="radio-option"><input type="radio" name="des-${id}" value="si" id="des-si-${id}"><label for="des-si-${id}">Sí (+R$ ${precios.lodging.desayuno}/p)</label></div>
            <div class="radio-option"><input type="radio" name="des-${id}" value="no" id="des-no-${id}" checked><label for="des-no-${id}">No</label></div>
          </div>
        </div>
      </div>
      <div class="form-section">
        <div class="section-title">Clases</div>
        <div class="form-group">
          <label>¿Clases?</label>
          <div class="radio-group">
            <div class="radio-option"><input type="radio" name="clases-${id}" value="si" id="cl-si-${id}"><label for="cl-si-${id}">Sí</label></div>
            <div class="radio-option"><input type="radio" name="clases-${id}" value="no" id="cl-no-${id}" checked><label for="cl-no-${id}">No</label></div>
          </div>
        </div>
        <div id="clasesOpc-${id}" class="hidden">
          <div class="form-group">
            <label>Deporte</label>
            <select id="dep-${id}"><option value="">Seleccionar</option><option value="Kite">Kite</option><option value="Wing">Wing</option></select>
          </div>
          <div class="form-group">
            <label>Producto</label>
            <div class="radio-group" style="grid-template-columns:repeat(3,1fr)">
              <div class="radio-option"><input type="radio" name="prod-${id}" value="Hora suelta" id="pr-h-${id}"><label for="pr-h-${id}">Hora</label></div>
              <div class="radio-option"><input type="radio" name="prod-${id}" value="Pack 10h" id="pr-p-${id}"><label for="pr-p-${id}">Pack 10h</label></div>
              <div class="radio-option"><input type="radio" name="prod-${id}" value="Avanzadas" id="pr-a-${id}"><label for="pr-a-${id}">Avanzada</label></div>
            </div>
          </div>
          <div class="form-group" id="hrsClaseC-${id}" style="display:none">
            <label>Horas</label><input type="number" id="hrs-${id}" min="1" value="2" style="width:100px">
          </div>
          <div class="info-text green" id="huesp-note-${id}" style="display:none">Precio huésped aplicado (con hospedaje incluido)</div>
        </div>
      </div>
      <div class="form-section">
        <div class="section-title">Rental</div>
        <div class="form-group">
          <label>¿Rental?</label>
          <div class="radio-group">
            <div class="radio-option"><input type="radio" name="rental-${id}" value="si" id="ren-si-${id}"><label for="ren-si-${id}">Sí</label></div>
            <div class="radio-option"><input type="radio" name="rental-${id}" value="no" id="ren-no-${id}" checked><label for="ren-no-${id}">No</label></div>
          </div>
        </div>
        <div id="rentalOpc-${id}" class="hidden">
          <div class="form-group">
            <label>Deporte</label>
            <select id="depR-${id}"><option value="">Seleccionar</option><option value="Kite">Kite</option><option value="Wing">Wing</option></select>
          </div>
          <div id="renKite-${id}" class="hidden">
            <div class="form-group">
              <label>Equipo</label>
              <div class="rental-checkboxes">
                <div class="checkbox-container"><input type="checkbox" id="rk-comp-${id}" value="completo"><label for="rk-comp-${id}">Eq. Completo</label></div>
                <div class="checkbox-container"><input type="checkbox" id="rk-kite-${id}" value="soloKite"><label for="rk-kite-${id}">Solo Kite</label></div>
                <div class="checkbox-container"><input type="checkbox" id="rk-tabla-${id}" value="soloTabla"><label for="rk-tabla-${id}">Solo Tabla</label></div>
                <div class="checkbox-container"><input type="checkbox" id="rk-arnes-${id}" value="soloArnes"><label for="rk-arnes-${id}">Solo Arnés</label></div>
              </div>
            </div>
            <div class="rental-grid">
              <div class="form-group">
                <label>Duración</label>
                <select id="durK-${id}">
                  <option value="">Seleccionar</option>
                  <option value="sesion">Sesión (≤3h)</option>
                  <option value="dia1">1 Día</option>
                  <option value="dias3">3+ Días / día</option>
                  <option value="dias5">5+ Días / día</option>
                </select>
              </div>
              <div class="form-group"><label>Días</label><input type="number" id="diasK-${id}" min="1" value="1"></div>
            </div>
          </div>
          <div id="renWing-${id}" class="hidden">
            <div class="form-group">
              <label>Equipo</label>
              <div class="rental-checkboxes">
                <div class="checkbox-container"><input type="checkbox" id="rw-comp-${id}" value="completo"><label for="rw-comp-${id}">Eq. Completo</label></div>
                <div class="checkbox-container"><input type="checkbox" id="rw-wing-${id}" value="soloWing"><label for="rw-wing-${id}">Solo Wing</label></div>
                <div class="checkbox-container"><input type="checkbox" id="rw-foil-${id}" value="tablaFoil"><label for="rw-foil-${id}">Tabla + Foil</label></div>
              </div>
            </div>
            <div class="rental-grid">
              <div class="form-group">
                <label>Duración</label>
                <select id="durW-${id}">
                  <option value="">Seleccionar</option>
                  <option value="hora">Por Hora</option>
                  <option value="dia">Día Completo (3h)</option>
                </select>
              </div>
              <div class="form-group"><label>Días</label><input type="number" id="diasW-${id}" min="1" value="1"></div>
            </div>
          </div>
        </div>
      </div>
      <div class="form-section">
        <div class="section-title">Extras</div>
        <div class="extras-list">
          <div class="checkbox-container"><input type="checkbox" id="prot-${id}"><label for="prot-${id}" id="label-prot-${id}">Protector Solar (R$ ${precios.extras.protectorSolar})</label></div>
          <div class="checkbox-container"><input type="checkbox" id="lyc-${id}"><label for="lyc-${id}" id="label-lyc-${id}">Lycras (R$ ${precios.extras.lycras})</label></div>
          <div class="checkbox-container"><input type="checkbox" id="cuipe-${id}"><label for="cuipe-${id}" id="label-cuipe-${id}">Tarde en Cuipe (R$ ${precios.extras.cuipe})</label></div>
        </div>
      </div>
    </div>
  </div>
  <div class="result-box">
    <div class="result-box-header">Opción ${id}</div>
    <div class="result-box-body">
      <div class="result-item"><span>Subtotal</span><span id="subtotal-prev-${id}">R$ 0</span></div>
      <div class="result-item descuento" id="desc-row-${id}" style="display:none"><span>Desc. Efectivo/Pix</span><span id="desc-prev-${id}">-R$ 0</span></div>
      <div class="result-item total"><span>Total</span><span id="total-prev-${id}">R$ 0</span></div>
    </div>
  </div>
  `;
}
'''


def apply(html: str, css: str) -> str:
    html = re.sub(
        r"<style>\s*.*?\s*</style>",
        f"<style>\n{css.strip()}\n    </style>",
        html,
        count=1,
        flags=re.DOTALL,
    )

    html = re.sub(
        r'<div class="bento-card bento-card-split nombre-lead-box">\s*'
        r'<div class="card-accent">Lead</div>\s*'
        r'<div class="bento-card-body">\s*'
        r'(<input type="text" id="nombreLeadGlobal"[^>]*>)\s*'
        r"</div>\s*</div>",
        r'<div class="bento-card lead-card">\n            \1\n        </div>',
        html,
        count=1,
        flags=re.DOTALL,
    )

    html = re.sub(
        r'\n\s*<button class="btn btn-generar" id="generarBtn">[^<]*</button>\s*',
        "\n",
        html,
        count=1,
    )

    if 'id="stickyBar"' not in html:
        html = html.replace("\n<script>", STICKY + "\n<script>", 1)

    html = re.sub(
        r"function crearContenidoOpcion\(id\)\s*\{[\s\S]*?\n\}",
        CREAR_OPCION.strip(),
        html,
        count=1,
    )

    if "function syncStickyTotal" not in html:
        html = html.replace("function cambiarOpcion(id) {", SYNC_FN + "\nfunction cambiarOpcion(id) {", 1)

    html = html.replace(
        "document.getElementById('generarBtn').classList.toggle('hidden', !isCot);",
        "document.getElementById('stickyBar').classList.toggle('hidden', !isCot);",
    )

    html = html.replace(
        "  if (tc) tc.classList.add('active');\n}",
        "  if (tc) tc.classList.add('active');\n  syncStickyTotal(id);\n}",
        1,
    )

    html = html.replace(
        "    tot.textContent = `R$ ${d.grandTotal}`;\n  }\n}",
        "    tot.textContent = `R$ ${d.grandTotal}`;\n  }\n  syncStickyTotal(id);\n}",
        1,
    )

    html = html.replace(
        "  if (document.querySelectorAll('.tab').length > 1) cambiarOpcion(id);\n}",
        "  if (document.querySelectorAll('.tab').length > 1) cambiarOpcion(id);\n  else syncStickyTotal(id);\n}",
        1,
    )

    return html


def main():
    src = INDEX
    if len(sys.argv) > 1:
        src = Path(sys.argv[1])
    out = OUT
    if len(sys.argv) > 2:
        out = Path(sys.argv[2])

    try:
        html = src.read_text(encoding="utf-8")
    except OSError as e:
        print(f"ERROR reading {src}: {e}", file=sys.stderr)
        sys.exit(1)

    css = CSS.read_text(encoding="utf-8")
    result = apply(html, css)

    try:
        out.write_text(result, encoding="utf-8")
    except OSError as e:
        print(f"ERROR writing {out}: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"OK → {out} ({len(result)} bytes)")


if __name__ == "__main__":
    main()
