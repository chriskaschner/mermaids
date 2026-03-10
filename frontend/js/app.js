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
              <svg width="24" height="24" viewBox="0 0 24 24">
                <path d="M6 3Q6 3 18 3Q19 3 19 4L19 7" fill="none" stroke="#888" stroke-width="2" stroke-linecap="round"/>
                <path d="M12 1A7 7 0 0 1 19 7" fill="none" stroke="#888" stroke-width="2" stroke-linecap="round"/>
                <rect x="5" y="7" width="14" height="14" rx="2" fill="none" stroke="#888" stroke-width="2"/>
                <path d="M14 7Q15 10 14 12Q13 14 14 16" fill="none" stroke="#888" stroke-width="2" stroke-linecap="round"/>
              </svg>
            </button>
            <button class="tool-btn" data-tool="brush" aria-label="Brush tool">
              <svg width="24" height="24" viewBox="0 0 512 512">
                <path d="M.7 389.87C3.16 369.41 18.77 352.38 38.23 346.22c11.93-3.77 24.72-3.1 37.1-2.87 5.26.1 10.63.34 15.54 2.16 10.17 3.77 17.05 13.14 22.3 22.63l45.08 81.45c1.93 3.49 3.89 7.09 4.48 11.05 1.13 7.59-3.08 14.89-8.56 20.37S141.6 490 134.02 491.16c-6.7 1.02-13.6-.46-20.07-2.33-22.46-6.49-42.87-18.85-60.22-34.26C37.37 439.92 23.2 423 12.63 404.16c-3.53-6.29-7.79-14.24-11.93-14.29z"
                      fill="none" stroke="#888" stroke-width="30" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M108.81 367.56L218.6 257.77M148.58 407.33L258.37 297.54"
                      fill="none" stroke="#888" stroke-width="30" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M178.63 337.51c17.68-17.68 17.68-46.34 0-64.03l-2.11-2.11c-17.68-17.68-46.34-17.68-64.03 0"
                      fill="none" stroke="#888" stroke-width="30" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M238.49 277.66c90.01-90.01 148.74-171.93 199.87-220.2 12.46-11.76 33.87-14.52 46.98-1.41 13.11 13.11 10.35 34.52-1.41 46.98-48.27 51.13-130.19 109.86-220.2 199.87"
                      fill="none" stroke="#888" stroke-width="30" stroke-linecap="round" stroke-linejoin="round"/>
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
