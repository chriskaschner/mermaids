/**
 * Hash-based SPA router with view rendering for Mermaid Create & Play.
 *
 * Routes: #/home (default), #/dressup, #/coloring
 */

import { initTouch } from "./touch.js";
import { initDressUp, resetState } from "./dressup.js";

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
    const resp = await fetch("/assets/svg/mermaid.svg");
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
    initDressUp();
  } catch (err) {
    el.innerHTML = '<div class="error">Could not load mermaid.</div>';
  }
}

function renderColoring() {
  const el = appEl();
  el.innerHTML = `
    <div class="coloring-placeholder">
      <p>Coming soon!</p>
    </div>
  `;
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
