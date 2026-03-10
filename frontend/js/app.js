/**
 * Hash-based SPA router with view rendering for Mermaid Create & Play.
 *
 * Routes: #/home (default), #/dressup, #/coloring
 */

import { initTouch } from "./touch.js";
import { initDressUp, resetState } from "./dressup.js";
import {
  COLORING_PAGES,
  COLORS,
  initColoringCanvas,
  handleCanvasTap,
  strokeStart,
  strokeMove,
  strokeEnd,
  undo as coloringUndo,
  canUndo,
  releaseCanvas,
  setSelectedColor,
  getSelectedColor,
} from "./coloring.js";

const appEl = () => document.getElementById("app");

// -- View renderers ----------------------------------------------------------

function renderHome() {
  const el = appEl();
  el.innerHTML = `
    <div class="home-grid">
      <a href="#/dressup" class="activity-btn activity-btn--dressup" aria-label="Dress Up">
        <svg width="80" height="80" viewBox="0 0 80 80" fill="none" xmlns="http://www.w3.org/2000/svg">
          <circle cx="40" cy="40" r="36" fill="#f0d4f5" stroke="#c47ed0" stroke-width="2"/>
          <path d="M40 12L44 28L56 28L46 38L50 54L40 44L30 54L34 38L24 28L36 28Z"
                fill="#c47ed0" opacity="0.8"/>
          <path d="M28 58Q34 52 40 56Q46 52 52 58" stroke="#c47ed0" stroke-width="2.5"
                stroke-linecap="round" fill="none"/>
        </svg>
      </a>
      <a href="#/coloring" class="activity-btn activity-btn--coloring" aria-label="Coloring">
        <svg width="80" height="80" viewBox="0 0 80 80" fill="none" xmlns="http://www.w3.org/2000/svg">
          <circle cx="40" cy="40" r="36" fill="#fce0d0" stroke="#e8976b" stroke-width="2"/>
          <path d="M24 56L28 42L50 20L58 28L36 50L24 56Z" fill="#e8976b" opacity="0.8"/>
          <path d="M48 22L56 30" stroke="#d07850" stroke-width="2.5"/>
          <circle cx="26" cy="54" r="3" fill="#e8976b"/>
        </svg>
      </a>
    </div>
  `;
}

async function renderDressUp() {
  const el = appEl();
  el.innerHTML = '<div class="loading">Loading...</div>';
  try {
    const resp = await fetch("assets/svg/mermaid.svg");
    const svgText = await resp.text();
    el.innerHTML = `
      <div class="dressup-view">
        <div class="mermaid-container" id="mermaid-container">
          ${svgText}
        </div>
        <div class="selection-panel">
          <div class="category-tabs">
            <button class="cat-tab active" data-category="tail" aria-label="Tails">
              <svg width="24" height="24" viewBox="0 0 24 24">
                <path d="M12,2 Q8,10 6,16 Q10,20 12,18 Q14,20 18,16 Q16,10 12,2Z"
                      fill="#7ec8c8" />
              </svg>
            </button>
            <button class="cat-tab" data-category="hair" aria-label="Hair">
              <svg width="24" height="24" viewBox="0 0 24 24">
                <path d="M6,12 Q6,4 12,3 Q18,4 18,12 Q16,8 12,7 Q8,8 6,12Z"
                      fill="#c4a7d7" />
              </svg>
            </button>
            <button class="cat-tab" data-category="acc" aria-label="Accessories">
              <svg width="24" height="24" viewBox="0 0 24 24">
                <path d="M12,2 L14,8 L20,8 L15,12 L17,18 L12,14 L7,18 L9,12 L4,8 L10,8Z"
                      fill="#ffd700" />
              </svg>
            </button>
            <button class="cat-tab" data-category="color" aria-label="Colors">
              <svg width="24" height="24" viewBox="0 0 24 24">
                <circle cx="12" cy="12" r="10" fill="none" stroke="#999" stroke-width="2" />
                <circle cx="8" cy="10" r="3" fill="#ff69b4" />
                <circle cx="16" cy="10" r="3" fill="#87ceeb" />
                <circle cx="12" cy="16" r="3" fill="#98fb98" />
              </svg>
            </button>
            <button class="undo-btn" aria-label="Undo">
              <svg width="24" height="24" viewBox="0 0 24 24">
                <path d="M7,12 L3,8 L7,4 M3,8 L15,8 Q20,8 20,14 Q20,20 15,20 L10,20"
                      fill="none" stroke="#888" stroke-width="2.5" stroke-linecap="round" />
              </svg>
            </button>
          </div>
          <div class="options-row" id="options-row">
          </div>
        </div>
      </div>
    `;
    // Ensure the SVG has the expected id
    const svg = el.querySelector("svg");
    if (svg && !svg.id) {
      svg.id = "mermaid-svg";
    }
    // Reset state in case user navigated away and back
    resetState();
    // Wire touch sparkle feedback on the mermaid itself
    initTouch("#mermaid-svg");
    // Wire dress-up interaction (tabs, options, undo)
    await initDressUp();
  } catch (err) {
    el.innerHTML = '<div class="error">Could not load mermaid.</div>';
  }
}

function renderColoring() {
  const el = appEl();
  releaseCanvas();
  el.innerHTML = `
    <div class="coloring-gallery">
      ${COLORING_PAGES.map(
        (page) => `
        <button class="gallery-thumb" data-page="${page.id}" aria-label="${page.label}">
          <img src="${page.file}" alt="${page.label}" />
        </button>
      `
      ).join("")}
    </div>
  `;
  // Wire thumbnail clicks
  el.querySelectorAll(".gallery-thumb").forEach((btn) => {
    btn.addEventListener("click", () => openColoringPage(btn.dataset.page));
  });
}

/**
 * Update the undo button disabled state based on the undo stack.
 */
function _updateUndoBtn(undoBtn) {
  if (!undoBtn) return;
  if (canUndo()) {
    undoBtn.classList.remove("disabled");
  } else {
    undoBtn.classList.add("disabled");
  }
}

async function openColoringPage(pageId) {
  const el = appEl();
  const page = COLORING_PAGES.find((p) => p.id === pageId);
  if (!page) return;

  el.innerHTML = '<div class="loading">Loading...</div>';

  try {
    // Build the coloring view structure
    el.innerHTML = `
      <div class="coloring-view">
        <div class="coloring-page-container" id="coloring-container">
        </div>
        <div class="coloring-panel">
          <div class="coloring-toolbar">
            <button class="back-btn" aria-label="Back to gallery">
              <svg width="24" height="24" viewBox="0 0 24 24">
                <path d="M15,4 L7,12 L15,20" fill="none" stroke="#888" stroke-width="2.5" stroke-linecap="round" />
              </svg>
            </button>
            <button class="tool-btn selected" data-tool="fill" aria-label="Fill tool">
              <svg width="24" height="24" viewBox="0 0 100 100" fill="none" stroke="#888" stroke-width="7" stroke-linecap="round" stroke-linejoin="round">
                <path d="M20 42 A30 30 0 0 1 80 42"/>
                <path d="M15 42 L85 42 L85 88 Q85 95 78 95 L22 95 Q15 95 15 88 Z"/>
                <path d="M72 42 C80 52 68 60 76 72" stroke-width="6"/>
              </svg>
            </button>
            <button class="tool-btn" data-tool="brush" aria-label="Brush tool">
              <svg width="24" height="24" viewBox="0 0 100 100" fill="none" stroke="#888" stroke-width="6" stroke-linecap="round" stroke-linejoin="round">
                <path d="M8 94 C0 82 2 68 12 60 C20 54 30 56 32 66 C34 76 22 92 8 94Z"/>
                <line x1="24" y1="54" x2="36" y2="66"/>
                <line x1="30" y1="48" x2="42" y2="60"/>
                <path d="M34 50 C46 38 62 22 78 10 Q84 6 86 8 Q88 10 84 16 C70 30 54 46 42 58"/>
              </svg>
            </button>
            <button class="undo-btn disabled" aria-label="Undo">
              <svg width="24" height="24" viewBox="0 0 24 24">
                <path d="M7,12 L3,8 L7,4 M3,8 L15,8 Q20,8 20,14 Q20,20 15,20 L10,20"
                      fill="none" stroke="#888" stroke-width="2.5" stroke-linecap="round" />
              </svg>
            </button>
          </div>
          <div class="options-row" id="color-swatches">
            ${COLORS.map(
              (color, i) => `
              <button class="color-swatch${i === 2 ? " selected" : ""}"
                      data-color="${color}"
                      aria-label="Color ${color}"
                      style="background: ${color};">
              </button>
            `
            ).join("")}
          </div>
        </div>
      </div>
    `;

    const container = el.querySelector("#coloring-container");
    const undoBtn = el.querySelector(".coloring-toolbar .undo-btn");
    let activeTool = "fill"; // "fill" or "brush"

    // Wire tool toggle buttons
    el.querySelectorAll(".tool-btn").forEach((btn) => {
      btn.addEventListener("click", () => {
        activeTool = btn.dataset.tool;
        el.querySelectorAll(".tool-btn").forEach((b) => b.classList.remove("selected"));
        btn.classList.add("selected");
      });
    });

    // Set default selected color (hot pink, COLORS[2])
    setSelectedColor(COLORS[2]);

    // Initialize canvas with the SVG rasterized onto it
    const { canvas } = await initColoringCanvas(page.file, container);
    canvas.id = "coloring-canvas";

    // Fetch the SVG text and create an overlay for crisp line art
    const svgResp = await fetch(page.file);
    const svgText = await svgResp.text();
    const parser = new DOMParser();
    const svgDoc = parser.parseFromString(svgText, "image/svg+xml");
    const svgOverlay = svgDoc.documentElement;
    svgOverlay.classList.add("coloring-svg-overlay");
    svgOverlay.style.pointerEvents = "none";
    // Add viewBox for scalability, then remove explicit width/height so CSS
    // can size the SVG to match the canvas (inline SVGs with explicit w/h
    // don't maintain aspect ratio under CSS max-width constraints).
    if (!svgOverlay.getAttribute("viewBox")) {
      const w = svgOverlay.getAttribute("width") || "1024";
      const h = svgOverlay.getAttribute("height") || "1024";
      svgOverlay.setAttribute("viewBox", `0 0 ${w} ${h}`);
    }
    svgOverlay.removeAttribute("width");
    svgOverlay.removeAttribute("height");
    container.appendChild(svgOverlay);

    // Map pointer CSS coordinates to canvas pixel coordinates
    function _toCanvas(e) {
      const rect = canvas.getBoundingClientRect();
      const scaleX = canvas.width / rect.width;
      const scaleY = canvas.height / rect.height;
      return [
        Math.floor((e.clientX - rect.left) * scaleX),
        Math.floor((e.clientY - rect.top) * scaleY),
      ];
    }

    // Wire canvas pointer events based on active tool
    canvas.addEventListener("pointerdown", (e) => {
      canvas.setPointerCapture(e.pointerId);
      const [cx, cy] = _toCanvas(e);
      if (activeTool === "fill") {
        handleCanvasTap(cx, cy);
        _updateUndoBtn(undoBtn);
      } else {
        strokeStart(cx, cy);
      }
    });
    canvas.addEventListener("pointermove", (e) => {
      if (activeTool === "brush") {
        strokeMove(..._toCanvas(e));
      }
    });
    canvas.addEventListener("pointerup", () => {
      if (activeTool === "brush") {
        strokeEnd();
      }
      _updateUndoBtn(undoBtn);
    });
    canvas.addEventListener("pointercancel", () => {
      if (activeTool === "brush") {
        strokeEnd();
      }
      _updateUndoBtn(undoBtn);
    });

    // Wire undo button
    undoBtn.addEventListener("click", () => {
      coloringUndo();
      _updateUndoBtn(undoBtn);
    });

    // Wire back button: release canvas then go to gallery
    el.querySelector(".back-btn").addEventListener("click", () => {
      releaseCanvas();
      renderColoring();
    });

    // Wire color swatch selection
    el.querySelectorAll(".color-swatch").forEach((swatch) => {
      swatch.addEventListener("click", () => {
        setSelectedColor(swatch.dataset.color);
        el.querySelectorAll(".color-swatch").forEach((s) =>
          s.classList.remove("selected")
        );
        swatch.classList.add("selected");
      });
    });
  } catch (err) {
    el.innerHTML = '<div class="error">Could not load coloring page.</div>';
  }
}

// -- Router ------------------------------------------------------------------

const routes = {
  "": renderHome,
  home: renderHome,
  dressup: renderDressUp,
  coloring: renderColoring,
};

function updateNavHighlight(hash) {
  document.querySelectorAll(".nav-icon").forEach((icon) => {
    icon.classList.toggle("active", icon.dataset.view === hash);
  });
}

function router() {
  // Release any active coloring canvas before rendering a new route (CLRV-04)
  releaseCanvas();

  const hash = window.location.hash.slice(2) || "home";
  const render = routes[hash];
  if (render) {
    render();
  } else {
    renderHome();
  }
  updateNavHighlight(hash);
}

// -- Bootstrap ---------------------------------------------------------------

window.addEventListener("hashchange", router);
window.addEventListener("DOMContentLoaded", () => {
  if (!window.location.hash) {
    window.location.hash = "#/home";
  } else {
    router();
  }
});
