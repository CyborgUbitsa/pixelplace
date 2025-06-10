
const intToHex = i => "#" + i.toString(16).padStart(6, "0");

document.addEventListener("DOMContentLoaded", () => {
  const q = id => document.getElementById(id);
  const inpX = q("input-x"), inpY = q("input-y");
  const inpHex = q("input-hex"), inpR = q("input-r"), inpG = q("input-g"), inpB = q("input-b");
  const inpScale = q("input-scale");
  const btnSet = q("btn-set");
  const canvas = q("pixel-canvas"), ctx = canvas.getContext("2d");

  let SCALE = +inpScale.value || 4;
  function applyScale() {
    canvas.style.width  = canvas.width  * SCALE + "px";
    canvas.style.height = canvas.height * SCALE + "px";
  }
  inpScale.addEventListener("change", () => {
    SCALE = Math.max(1, Math.min(40, +inpScale.value || 4));
    inpScale.value = SCALE;
    applyScale();
  });
  applyScale();

  const logicalY = y => canvas.height - 1 - y;
  const drawPixel = (x, y, hex) => {
    ctx.fillStyle = hex;
    ctx.fillRect(x, logicalY(y), 1, 1);
  };

  /* ---- валидаторы ---- */
  function parseCoords() {
    const x = +inpX.value, y = +inpY.value;
    const ok = v => Number.isInteger(v) && v >= 0;
    if (!ok(x) || !ok(y) || x >= CANVAS_W || y >= CANVAS_H) return null;
    return { x, y };
  }
  function parseColor() {
    if (inpHex.value.trim()) {
      const hex = inpHex.value.trim();
      return /^#[0-9a-fA-F]{6}$/.test(hex)
        ? { int: parseInt(hex.slice(1), 16), hex }
        : null;
    }
    const r = +inpR.value, g = +inpG.value, b = +inpB.value;
    const ok = v => Number.isInteger(v) && v >= 0 && v <= 255;
    if (!ok(r) || !ok(g) || !ok(b)) return null;
    const int = (r << 16) | (g << 8) | b;
    return { int, hex: intToHex(int) };
  }

  async function loadSnapshot() {
    const img = new Image();
    img.src = `/api/canvas/${CANVAS_ID}/snapshot/png/?t=${Date.now()}`;
    await img.decode();
    ctx.drawImage(img, 0, 0);
  }

  let socket;
  function connectWs() {
    socket = new WebSocket(WS_URL);
    socket.onopen = () => console.info("WS open");
    socket.onclose = e => {
      console.warn("WS closed", e.code);
      setTimeout(connectWs, 1500);
    };
    socket.onmessage = e => {
  const m = JSON.parse(e.data);
  if ("x" in m && "y" in m && "color" in m) {
      drawPixel(m.x, m.y, intToHex(m.color));
      appendAuditRow(m);
  }
};

}

  if (btnSet) {
  btnSet.addEventListener("click", () => {
    const coords = parseCoords();
    const col    = parseColor();
    if (!coords || !col) {
      console.warn("not-sent: invalid coords or color", { coords, col });
      return;
    }
    if (socket.readyState !== 1) {
      console.warn("WebSocket not ready", socket.readyState);
      return;
    }

    drawPixel(coords.x, coords.y, col.hex);
    socket.send(JSON.stringify({ x: coords.x, y: coords.y, color: col.int }));
    console.log("outgoing", coords, col.int);
  });
}

function appendAuditRow(m) {
  const table = document.getElementById("audit-body");  
  if (!table) return;
  const row = document.createElement("tr");
  row.innerHTML = `
     <td>${m.ts}</td>
     <td>${m.user}</td>
     <td>${m.x}</td>
     <td>${m.y}</td>
     <td>
        <span style="display:inline-block;width:14px;height:14px;
                     background:${intToHex(m.color)};
                     border:1px solid #0003;margin-right:.3rem"></span>
        ${intToHex(m.color)}
     </td>`;
  table.prepend(row);
  if (table.rows.length > 500) table.deleteRow(-1);
}


  (async () => {
    await loadSnapshot();
    connectWs();
  })();
});
