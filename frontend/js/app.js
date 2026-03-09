/**
 * Hash-based SPA router with view rendering for Mermaid Create & Play.
 *
 * Routes: #/home (default), #/dressup, #/coloring
 */

import { initTouch } from "./touch.js";

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
    el.innerHTML = `<div class="dressup-view">${svgText}</div>`;
    // Ensure the SVG has the expected id
    const svg = el.querySelector("svg");
    if (svg && !svg.id) {
      svg.id = "mermaid-svg";
    }
    initTouch("#mermaid-svg");
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
