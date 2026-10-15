export class PerformanceOverlay {
  constructor({ documentRef = globalThis.document, parent = null } = {}) {
    this.documentRef = documentRef;
    this.parent = parent || documentRef?.body || null;
    this.element = null;
    this.frameMs = 0;
    this.frames = 0;
    this.lastSecond = 0;
    this.fps = 0;
    if (this.documentRef && this.parent) {
      this.element = this.documentRef.createElement("pre");
      this.element.dataset.qa = "performance-overlay";
      this.element.style.cssText = [
        "position:fixed", "left:12px", "bottom:12px", "margin:0", "padding:10px",
        "z-index:10", "color:#dff8ff", "background:rgba(3,13,24,.78)",
        "border:1px solid rgba(137,225,255,.35)", "font:12px/1.45 ui-monospace,monospace",
        "pointer-events:none", "white-space:pre",
      ].join(";");
      this.parent.appendChild(this.element);
    }
  }

  update(renderer, { frameMs = 0, waveCount = 0, cameraMode = "orbit", boundaryVisible = true, foamVisible = true } = {}) {
    const safeFrameMs = Number.isFinite(frameMs) ? Math.max(0, frameMs) : 0;
    this.frameMs = this.frameMs === 0 ? safeFrameMs : this.frameMs * 0.9 + safeFrameMs * 0.1;
    this.frames += 1;
    const now = performance.now();
    if (this.lastSecond === 0) {
      this.lastSecond = now;
    }
    if (now - this.lastSecond >= 1000) {
      this.fps = this.frames * 1000 / (now - this.lastSecond);
      this.frames = 0;
      this.lastSecond = now;
    }
    if (!this.element) {
      return;
    }
    const info = renderer?.info?.render || {};
    const memory = renderer?.info?.memory || {};
    this.element.textContent = [
      "W1 THREE WATER QA",
      `frame ${this.frameMs.toFixed(2)} ms  fps ${this.fps.toFixed(1)}`,
      `drawCalls ${info.calls ?? 0}  triangles ${info.triangles ?? 0}`,
      `geometries ${memory.geometries ?? 0}  textures ${memory.textures ?? 0}`,
      `waves ${waveCount}  camera ${cameraMode}`,
      `boundary ${boundaryVisible ? "on" : "off"}  foam ${foamVisible ? "on" : "off"}`,
      "60 FPS is a target; this overlay reports measurements only",
    ].join("\n");
  }

  setVisible(visible) {
    if (this.element) {
      this.element.hidden = !visible;
    }
  }

  dispose() {
    this.element?.remove();
    this.element = null;
  }
}
