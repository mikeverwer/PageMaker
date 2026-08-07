let animationTimer = null;
let lineAnimationId = null;

// ── Math utilities ───────────────────────────────────────────────────

function logFactorial(n) {
    let result = 0;
    for (let i = 2; i <= n; i++) {
        result += Math.log(i);
    }
    return result;
}

function coinProbability(n, k, p) {
    if (p === 0) return k === 0 ? 1 : 0;
    if (p === 1) return k === n ? 1 : 0;
    const logPMF = logFactorial(n) - logFactorial(k) - logFactorial(n - k)
                 + k * Math.log(p)
                 + (n - k) * Math.log(1 - p);
    return Math.exp(logPMF);
}

function flipOnce(numCoins, probHeads) {
    let heads = 0;
    for (let j = 0; j < numCoins; j++) {
        if (Math.random() < probHeads) heads++;
    }
    return heads;
}

// Each dot represents `binSize` trials; auto-scale so we never draw more
// than ~200 dots in a single column (preserves readability for large n).
function getBinSize(numTrials) {
    return Math.max(1, Math.ceil(numTrials / 200));
}

// ── Tick generation ──────────────────────────────────────────────────

function niceStep(maxValue, targetTickCount) {
    const roughStep = maxValue / targetTickCount;
    const magnitude = Math.pow(10, Math.floor(Math.log10(roughStep)));
    const normalized = roughStep / magnitude;
    let niceNormalized;
    if (normalized < 1.5) niceNormalized = 1;
    else if (normalized < 3.5) niceNormalized = 2;
    else if (normalized < 7) niceNormalized = 5;
    else niceNormalized = 10;
    return niceNormalized * magnitude;
}

function generateTicks(maxValue, targetTickCount = 6) {
    const step = niceStep(maxValue, targetTickCount);
    const ticks = [];
    for (let v = 0; v <= maxValue + 1e-9; v += step) {
        ticks.push(parseFloat(v.toFixed(10)));
    }
    return ticks;
}

function probDecimals(step) {
    if (step >= 1) return 0;
    return Math.ceil(-Math.log10(step) - 1e-9);
}

// ── Theoretical line: path access and reveal animation ──────────────

// Plotly renders scatter line traces as <path class="js-line">. We filter
// for non-empty `d` so that placeholder traces (empty data) don't match.
function getTheoreticalPath() {
    const plot = document.getElementById('flip-plot');
    if (!plot) return null;
    const candidates = plot.querySelectorAll('.scatterlayer .js-line');
    for (const path of candidates) {
        const d = path.getAttribute('d');
        if (d && d.length > 0) {
            return path;
        }
    }
    return null;
}

function cancelLineAnimation() {
    if (lineAnimationId !== null) {
        cancelAnimationFrame(lineAnimationId);
        lineAnimationId = null;
    }
}

// Hide the line by setting both stroke-dasharray and stroke-dashoffset to
// the path's full length: every painted segment is followed by an equal-
// length gap, and the gap is offset to start at the path's beginning.
// Idempotent and safe to call repeatedly. Plotly.extendTraces frequently
// rebuilds this path element, so we re-call this after each extend.
function hideTheoreticalLine() {
    const path = getTheoreticalPath();
    if (!path) return;
    const length = path.getTotalLength();
    if (length === 0) return;
    path.style.strokeDasharray = length + 'px';
    path.style.strokeDashoffset = length + 'px';
}

function showTheoreticalLine() {
    const path = getTheoreticalPath();
    if (path) {
        path.style.strokeDasharray = '';
        path.style.strokeDashoffset = '';
    }
}

// Animate stroke-dashoffset from `length` to 0, revealing the path L→R.
// Re-grabs the current live path element rather than trusting any reference
// captured before extendTraces calls (which may have rebuilt the DOM).
function animateLineDraw(duration = 1500) {
    const path = getTheoreticalPath();
    if (!path) return;
    const length = path.getTotalLength();
    if (length === 0) return;

    // Ensure the starting state is fully hidden, in case a redraw between
    // last hideTheoreticalLine() and now reset the styles.
    path.style.strokeDasharray = length + 'px';
    path.style.strokeDashoffset = length + 'px';

    const startTime = performance.now();
    function frame(now) {
        const t = Math.min((now - startTime) / duration, 1);
        const eased = t * t * (3 - 2 * t);  // smoothstep
        path.style.strokeDashoffset = (length * (1 - eased)) + 'px';
        if (t < 1) {
            lineAnimationId = requestAnimationFrame(frame);
        } else {
            lineAnimationId = null;
        }
    }
    lineAnimationId = requestAnimationFrame(frame);
}

// ── Plot construction ────────────────────────────────────────────────

function buildPlot() {
    clearTimeout(animationTimer);
    cancelLineAnimation();

    const n = parseInt(document.getElementById('num-coins').value);
    const p = parseFloat(document.getElementById('prob-heads').value);
    const trials = parseInt(document.getElementById('num-trials').value);
    const binSize = getBinSize(trials);

    // Theoretical: P(X = k) for k = 0..n
    const lineX = [];
    const lineY = [];
    let maxProb = 0;
    for (let k = 0; k <= n; k++) {
        const pk = coinProbability(n, k, p);
        lineX.push(k);
        lineY.push(pk);
        if (pk > maxProb) maxProb = pk;
    }

    const yMaxProb = Math.min(1.0, maxProb * 1.5);
    const yMaxFreq = yMaxProb * trials;

    const probTicks = generateTicks(yMaxProb);
    const step = probTicks[1] - probTicks[0];
    const decimals = probDecimals(step);
    const probLabels = probTicks.map(v => v.toFixed(decimals));
    const freqTicks = probTicks.map(v => v * trials);
    const freqLabels = freqTicks.map(f => Math.round(f).toString());

    const ev = n * p;
    const evLabel = Number.isInteger(ev) ? ev.toString() : ev.toFixed(1);
    const evProb = coinProbability(n, Math.round(ev), p);
    const evIsLeftHalf = ev < n / 2;

    const theoreticalTrace = {
        x: lineX,
        y: lineY,
        type: 'scatter',
        mode: 'lines',
        line: { color: '#888', width: 1.5 },
        name: 'Theoretical',
        hoverinfo: 'x+y'
    };

    const dotTrace = {
        x: [],
        y: [],
        customdata: [],
        type: 'scatter',
        mode: 'markers',
        marker: { color: '#0047ab', size: 6 },
        name: 'Simulated',
        hovertemplate: 'Heads: %{x}<br>Count: %{customdata}<extra></extra>'
    };

    const placeholderTrace = {
        x: [],
        y: [],
        type: 'scatter',
        yaxis: 'y2',
        showlegend: false,
        hoverinfo: 'skip'
    };

    const layout = {
        xaxis: {
            title: {
            text: 'Number of heads<br><span style="font-size: 0.8em; color: #888">Each dot represents '
                + binSize + ' trial' + (binSize === 1 ? '' : 's') + '</span>'
            },
            range: [-0.5, n + 0.5]
        },
        yaxis: {
            title: { text: 'Probability' },
            range: [0, yMaxProb],
            tickmode: 'array',
            tickvals: probTicks,
            ticktext: probLabels
        },
        yaxis2: {
            title: { text: 'Frequency' },
            side: 'right',
            overlaying: 'y',
            range: [0.5, yMaxFreq + 0.5],
            tickmode: 'array',
            tickvals: freqTicks,
            ticktext: freqLabels,
            showgrid: false
        },
        shapes: [{
            type: 'line',
            xref: 'x',
            yref: 'y',
            x0: ev, x1: ev,
            y0: 0,  y1: yMaxProb,
            line: { color: '#666', width: 1, dash: 'dash' }
        }],
        annotations: [
            {
                text: 'E[X] = ' + evLabel + '<br>P = ' + evProb.toFixed(3),
                x: ev,
                y: yMaxProb,
                xref: 'x', yref: 'y',
                xanchor: evIsLeftHalf ? 'left' : 'right',
                yanchor: 'top',
                xshift: evIsLeftHalf ? 4 : -4,
                showarrow: false,
                font: { size: 11, color: '#666' }
            }
        ],
        showlegend: true,
        margin: { t: 20, r: 60, b: 70 },
        paper_bgcolor: '#eaeaea',
        plot_bgcolor: '#eaeaea'
    };

    Plotly.react(
        'flip-plot',
        [theoreticalTrace, dotTrace, placeholderTrace],
        layout,
        { responsive: true }
    );
    showTheoreticalLine();  // clear any stale stroke-dash from prior animation
}

// ── Simulation ───────────────────────────────────────────────────────

function runSimulation() {
    clearTimeout(animationTimer);
    cancelLineAnimation();

    const coins = parseInt(document.getElementById('num-coins').value);
    const trials = parseInt(document.getElementById('num-trials').value);
    const prob = parseFloat(document.getElementById('prob-heads').value);

    const binSize = getBinSize(trials);
    const pUnit = binSize / trials;

    // Reset the dot trace; theoretical line trace remains populated.
    Plotly.restyle('flip-plot', { x: [[]], y: [[]], customdata: [[]] }, [1]);

    // Initial hide for the post-simulation reveal.
    hideTheoreticalLine();

    const counts     = new Array(coins + 1).fill(0);
    const dotsDrawn  = new Array(coins + 1).fill(0);
    let currentTrial = 0;

    function tick() {
        if (currentTrial >= trials) {
            animateLineDraw();
            return;
        }

        const trialsThisTick = Math.min(binSize, trials - currentTrial);
        const newX = [];
        const newY = [];
        const newCustom = [];

        for (let i = 0; i < trialsThisTick; i++) {
            const k = flipOnce(coins, prob);
            counts[k]++;

            const dotsForK = Math.ceil(counts[k] / binSize);
            if (dotsForK > dotsDrawn[k]) {
                dotsDrawn[k] = dotsForK;
                newX.push(k);
                newY.push((dotsForK - 0.5) * pUnit);
                newCustom.push(dotsForK * binSize);
            }
            currentTrial++;
        }

        if (newX.length > 0) {
            Plotly.extendTraces('flip-plot',
                { x: [newX], y: [newY], customdata: [newCustom] },
                [1]
            );
            // extendTraces typically rebuilds the SVG path for trace 0 too,
            // wiping our inline stroke-dash styles. Re-apply synchronously
            // before the browser paints so the line never flashes visible.
            hideTheoreticalLine();
        }

        animationTimer = setTimeout(tick, 50);
    }

    tick();
}

// ── Event wiring ─────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('prob-heads').addEventListener('input', () => {
        const p = parseFloat(document.getElementById('prob-heads').value);
        document.getElementById('prob-display').textContent = p.toFixed(2);
        buildPlot();
    });
    document.getElementById('num-coins').addEventListener('input', buildPlot);
    document.getElementById('num-trials').addEventListener('input', buildPlot);
    document.getElementById('run-btn').addEventListener('click', runSimulation);
    window.addEventListener("keydown", (e) => {
        if (e.code.includes("Enter")) {
            runSimulation();
        }
    })
    
    const plotResizeObserver = new ResizeObserver(() => {
        Plotly.Plots.resize('flip-plot');
    });
    plotResizeObserver.observe(document.getElementById('flip-plot'));

    buildPlot();
});
