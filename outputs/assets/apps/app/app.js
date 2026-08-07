// This file contains any javascript that the app requires

(function () {
  function init() {
    const svg = document.getElementById('gr-svg');
    const resetBtn = document.getElementById('gr-reset');
    const countLabel = document.getElementById('gr-count');
    if (!svg || !resetBtn || !countLabel) return;

    const svgNS = 'http://www.w3.org/2000/svg';
    const PHI = (1 + Math.sqrt(5)) / 2;
    const PAD = 3;
    const FALLBACK_WIDTH = 600;
    const MIN_SIDE = 2; // stop once the next square would be smaller than this
    const EDGES = ['left', 'top', 'right', 'bottom']; // cycling this order is what makes it spiral
    const PALETTE = [
        '#fb7b77', '#fdc170', '#f3f87f', '#98f786', '#69ebfc',
        '#6d9efc', '#937df8', '#f78ef0', '#bc5090'
    ];

    // Sized once from the container's rendered width at load time.
    // Deliberately doesn't re-measure on resize -- reload to pick up a new width.
    const measuredWidth = svg.parentElement.clientWidth;
    const outerW = Math.round(measuredWidth > 0 ? measuredWidth : FALLBACK_WIDTH);

    // The interior rectangle's height is derived from its own width via phi
    // (kept as an exact float) rather than from independently-rounded outer
    // W/H shrunk by a flat pad -- that would distort the ratio and drift
    // further from golden with every cut. PAD only offsets position and
    // pads the outer viewBox; it never touches the interior ratio.
    const contentW = outerW - 2 * PAD;
    const contentH = contentW / PHI;
    const outerH = Math.round(contentH + 2 * PAD);

    svg.setAttribute('width', outerW);
    svg.setAttribute('height', outerH);
    svg.setAttribute('viewBox', `0 0 ${outerW} ${outerH}`);

    let rect, edgeIndex, count, done;

    function reset() {
      rect = { x: PAD, y: PAD, w: contentW, h: contentH };
      edgeIndex = 0;
      count = 0;
      done = false;
      svg.classList.remove('gr-done');
      svg.innerHTML = '';
      drawOutline();
      updateCount();
    }

    function drawOutline() {
      const outline = document.createElementNS(svgNS, 'rect');
      outline.setAttribute('x', rect.x);
      outline.setAttribute('y', rect.y);
      outline.setAttribute('width', rect.w);
      outline.setAttribute('height', rect.h);
      outline.setAttribute('fill', 'none');
      outline.setAttribute('stroke', 'currentColor');
      outline.setAttribute('stroke-width', '1');
      svg.appendChild(outline);
    }

    function updateCount() {
      countLabel.textContent = 'Subdivisions: ' + count;
    }

    // Cuts a square (side = shorter dimension) off the given edge of r.
    // Returns the square that was cut, the remaining rectangle, and the dividing line.
    function cut(r, edge) {
      const side = Math.min(r.w, r.h);
      let square, remaining, line;
      if (edge === 'left') {
        square = { x: r.x, y: r.y, w: side, h: side };
        remaining = { x: r.x + side, y: r.y, w: r.w - side, h: r.h };
        line = [r.x + side, r.y, r.x + side, r.y + r.h];
      } else if (edge === 'right') {
        square = { x: r.x + r.w - side, y: r.y, w: side, h: side };
        remaining = { x: r.x, y: r.y, w: r.w - side, h: r.h };
        line = [r.x + r.w - side, r.y, r.x + r.w - side, r.y + r.h];
      } else if (edge === 'top') {
        square = { x: r.x, y: r.y, w: side, h: side };
        remaining = { x: r.x, y: r.y + side, w: r.w, h: r.h - side };
        line = [r.x, r.y + side, r.x + r.w, r.y + side];
      } else {
        square = { x: r.x, y: r.y + r.h - side, w: side, h: side };
        remaining = { x: r.x, y: r.y, w: r.w, h: r.h - side };
        line = [r.x, r.y + r.h - side, r.x + r.w, r.y + r.h - side];
      }
      return { square, remaining, line };
    }

    function subdivide() {
      if (done) return;

      const edge = EDGES[edgeIndex % EDGES.length];
      const { square, remaining, line } = cut(rect, edge);

      const squareEl = document.createElementNS(svgNS, 'rect');
      squareEl.setAttribute('class', 'gr-square');
      squareEl.setAttribute('x', square.x);
      squareEl.setAttribute('y', square.y);
      squareEl.setAttribute('width', square.w);
      squareEl.setAttribute('height', square.h);
      squareEl.setAttribute('fill', PALETTE[count % PALETTE.length]);
      squareEl.setAttribute('fill-opacity', '0.55');
      squareEl.setAttribute('stroke', 'currentColor');
      squareEl.setAttribute('stroke-width', '1');
      svg.appendChild(squareEl);

      const lineEl = document.createElementNS(svgNS, 'line');
      lineEl.setAttribute('x1', line[0]);
      lineEl.setAttribute('y1', line[1]);
      lineEl.setAttribute('x2', line[2]);
      lineEl.setAttribute('y2', line[3]);
      lineEl.setAttribute('stroke', 'currentColor');
      lineEl.setAttribute('stroke-width', '1');
      svg.appendChild(lineEl);

      rect = remaining;
      edgeIndex++;
      count++;
      updateCount();

      if (Math.min(rect.w, rect.h) < MIN_SIDE) {
        done = true;
        svg.classList.add('gr-done');
      }
    }

    svg.addEventListener('click', subdivide);
    resetBtn.addEventListener('click', reset);

    reset();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();