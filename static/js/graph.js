/**
 * LegacyLens Knowledge Graph — D3.js Force-Directed Visualization
 * Fetches /api/knowledge/graph/data/ and renders an interactive node-link diagram.
 */

(function () {
  "use strict";

  const CATEGORY_COLORS = {
    architecture: "#3b82f6",
    process:      "#8b5cf6",
    tooling:      "#10b981",
    domain:       "#f59e0b",
    decision:     "#ef4444",
    ownership:    "#06b6d4",
    onboarding:   "#a855f7",
    tribal:       "#ec4899",
  };

  const EDGE_COLORS = {
    supersedes:    "#f59e0b",
    contradicts:   "#ef4444",
    depends_on:    "#3b82f6",
    related:       "#334155",
    derived_from:  "#8b5cf6",
    owned_by:      "#06b6d4",
  };

  let allNodes = [], allEdges = [], simulation;

  async function loadGraph() {
    const container = document.getElementById("knowledge-graph");
    if (!container) return;

    // Show loading state
    container.innerHTML = '<div style="display:flex;align-items:center;justify-content:center;height:600px;color:var(--text-muted);gap:12px;"><span class="spinner"></span> Loading knowledge graph...</div>';

    try {
      const resp = await fetch("/api/knowledge/graph/data/");
      const data = await resp.json();

      if (data.status !== "ok" || !data.data) {
        showEmpty(container);
        return;
      }

      allNodes = data.data.nodes || [];
      allEdges = data.data.edges || [];

      document.getElementById("graph-stats").textContent =
        `${allNodes.length} facts · ${allEdges.length} relationships`;

      if (allNodes.length === 0) {
        showEmpty(container);
        return;
      }

      renderGraph(container, allNodes, allEdges);
    } catch (err) {
      container.innerHTML = `<div style="display:flex;align-items:center;justify-content:center;height:600px;color:var(--accent-red);">Failed to load graph: ${err.message}</div>`;
    }
  }

  function showEmpty(container) {
    container.innerHTML = '<div style="display:flex;flex-direction:column;align-items:center;justify-content:center;height:600px;color:var(--text-muted);gap:12px;"><svg xmlns=\'http://www.w3.org/2000/svg\' width=\'48\' height=\'48\' viewBox=\'0 0 24 24\' fill=\'none\' stroke=\'currentColor\' stroke-width=\'1.5\' stroke-linecap=\'round\' stroke-linejoin=\'round\'><circle cx=\'12\' cy=\'12\' r=\'10\'/><path d=\'M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3\'/><path d=\'M12 17h.01\'/></svg><p>No knowledge facts yet. Upload a document to populate the graph.</p></div>';
    document.getElementById("graph-stats").textContent = "0 facts · 0 relationships";
  }

  function renderGraph(container, nodes, edges) {
    container.innerHTML = "";
    const width  = container.clientWidth  || 900;
    const height = container.clientHeight || 600;

    const svg = d3.select(container)
      .append("svg")
      .attr("width",  "100%")
      .attr("height", height)
      .style("background", "transparent");

    // Zoom behaviour
    const g = svg.append("g");
    svg.call(
      d3.zoom()
        .scaleExtent([0.1, 4])
        .on("zoom", (event) => g.attr("transform", event.transform))
    );

    // Build edge data (link by index)
    const nodeMap = Object.fromEntries(nodes.map((n, i) => [n.id, i]));
    const links = edges
      .filter(e => nodeMap[e.source] !== undefined && nodeMap[e.target] !== undefined)
      .map(e => ({ ...e, source: nodeMap[e.source], target: nodeMap[e.target] }));

    // Simulation
    simulation = d3.forceSimulation(nodes)
      .force("link",   d3.forceLink(links).distance(100).strength(0.8))
      .force("charge", d3.forceManyBody().strength(-300))
      .force("center", d3.forceCenter(width / 2, height / 2))
      .force("collide", d3.forceCollide().radius(20));

    // Edges
    const link = g.append("g")
      .selectAll("line")
      .data(links)
      .enter().append("line")
      .attr("stroke", d => EDGE_COLORS[d.type] || "#334155")
      .attr("stroke-width", 1.5)
      .attr("stroke-opacity", 0.6)
      .attr("stroke-dasharray", d => d.type === "supersedes" ? "5,4" : null);

    // Nodes group
    const node = g.append("g")
      .selectAll("g")
      .data(nodes)
      .enter().append("g")
      .attr("class", "graph-node")
      .style("cursor", "pointer")
      .call(
        d3.drag()
          .on("start", (event, d) => {
            if (!event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x; d.fy = d.y;
          })
          .on("drag",  (event, d) => { d.fx = event.x; d.fy = event.y; })
          .on("end",   (event, d) => {
            if (!event.active) simulation.alphaTarget(0);
            d.fx = null; d.fy = null;
          })
      );

    // Node circles
    node.append("circle")
      .attr("r", d => 8 + (d.confidence || 0.5) * 12)
      .attr("fill",   d => CATEGORY_COLORS[d.category] || "#94a3b8")
      .attr("stroke", "#0a0e17")
      .attr("stroke-width", 2)
      .attr("fill-opacity", 0.85);

    // Node labels
    node.append("text")
      .text(d => (d.label || d.id || "").substring(0, 30))
      .attr("text-anchor", "middle")
      .attr("dy", d => 10 + (d.confidence || 0.5) * 12 + 12)
      .attr("font-size", "10px")
      .attr("fill", "#94a3b8")
      .attr("pointer-events", "none");

    // Hover highlight
    node.on("mouseover", function (event, d) {
      d3.select(this).select("circle")
        .attr("stroke", "#e2e8f0")
        .attr("stroke-width", 3)
        .attr("fill-opacity", 1);
    }).on("mouseout", function () {
      d3.select(this).select("circle")
        .attr("stroke", "#0a0e17")
        .attr("stroke-width", 2)
        .attr("fill-opacity", 0.85);
    });

    // Click — show detail panel
    node.on("click", (event, d) => {
      event.stopPropagation();
      const panel = document.getElementById("detail-panel");
      const body  = document.getElementById("detail-panel-body");
      if (panel && body) {
        body.innerHTML = `
          <div class="detail-row">
            <div class="detail-label">Summary</div>
            <div class="detail-value">${d.label || d.id}</div>
          </div>
          <div class="detail-row">
            <div class="detail-label">Category</div>
            <div class="detail-value"><span class="badge badge-${d.category}">${d.category}</span></div>
          </div>
          <div class="detail-row">
            <div class="detail-label">Status</div>
            <div class="detail-value"><span class="badge badge-${d.status}">${d.status}</span></div>
          </div>
          <div class="detail-row">
            <div class="detail-label">Confidence</div>
            <div class="detail-value">${Math.round((d.confidence || 0) * 100)}%</div>
          </div>
          ${d.content ? `<div class="detail-row"><div class="detail-label">Content</div><div class="detail-value" style="font-size:0.8rem;line-height:1.6;">${d.content.substring(0, 500)}</div></div>` : ""}
        `;
        panel.classList.add("open");
        lucide.createIcons();
      }
    });

    // Tick simulation
    simulation.on("tick", () => {
      link
        .attr("x1", d => d.source.x)
        .attr("y1", d => d.source.y)
        .attr("x2", d => d.target.x)
        .attr("y2", d => d.target.y);
      node.attr("transform", d => `translate(${d.x},${d.y})`);
    });

    // Reset button
    document.getElementById("reset-graph")?.addEventListener("click", () => {
      svg.transition().duration(500).call(
        d3.zoom().transform, d3.zoomIdentity
      );
    });

    // Filter handlers
    function applyFilters() {
      const cat = document.getElementById("filter-category")?.value || "";
      const sta = document.getElementById("filter-status")?.value || "";
      node.style("display", d => {
        if (cat && d.category !== cat) return "none";
        if (sta && d.status    !== sta) return "none";
        return null;
      });
    }

    document.getElementById("filter-category")?.addEventListener("change", applyFilters);
    document.getElementById("filter-status")?.addEventListener("change", applyFilters);

    // Responsive resize
    window.addEventListener("resize", () => {
      const w = container.clientWidth;
      svg.attr("width", w);
      simulation.force("center", d3.forceCenter(w / 2, height / 2)).alpha(0.3).restart();
    });
  }

  // Boot
  document.addEventListener("DOMContentLoaded", loadGraph);
})();
