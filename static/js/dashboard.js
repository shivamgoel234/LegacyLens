/**
 * LegacyLens Dashboard — Live stat updates
 */

(function () {
  "use strict";

  function animateCount(el, target) {
    const start = parseInt(el.textContent, 10) || 0;
    if (start === target) return;
    let current = start;
    const step = Math.ceil(Math.abs(target - start) / 20);
    const up = target > start;
    const interval = setInterval(() => {
      current = up ? Math.min(current + step, target) : Math.max(current - step, target);
      el.textContent = current;
      if (current === target) clearInterval(interval);
    }, 50);
  }

  async function refreshStats() {
    try {
      const [factsResp, gapsResp] = await Promise.all([
        fetch("/api/knowledge/facts/"),
        fetch("/api/knowledge/gaps/"),
      ]);
      const factsData = await factsResp.json();
      const gapsData  = await gapsResp.json();

      const factCount = factsData?.data?.length || 0;
      const gapCount  = gapsData?.data?.length  || 0;

      const factEl = document.getElementById("fact-count");
      const gapEl  = document.getElementById("gap-count");

      if (factEl) animateCount(factEl, factCount);
      if (gapEl)  animateCount(gapEl,  gapCount);
    } catch {
      // Silently fail — server-rendered counts are still shown
    }
  }

  document.addEventListener("DOMContentLoaded", () => {
    // Animate server-rendered numbers on page load
    document.querySelectorAll(".stat-value").forEach(el => {
      const val = parseInt(el.textContent, 10);
      if (!isNaN(val)) {
        el.textContent = 0;
        animateCount(el, val);
      }
    });

    // Refresh live stats after 2s
    setTimeout(refreshStats, 2000);
  });
})();
