// Heart Surface — homepage interactive element
//
// (2x² + y² + z² − 1)³ − (x²z³)/10 − y²z³ = 0,   for  −3 ≤ x, y, z ≤ 3
//
// Renders lazily on first click via Plotly's `isosurface` trace, so the
// homepage never pays the grid-build cost unless someone actually clicks.

(function () {
    // Grid points per axis. 16 cubes/axis (~17 pts/axis) was the figure
    // that verified renderable in Desmos 3D / CalcPlot3D; Plotly's own
    // marching-cubes implementation isn't identical, so this is a starting
    // point, not a proven-good value — tune for smoothness vs. perf once
    // this is actually running in a browser.
    const GRID_N = 60;
    const RANGE = 1.5;
    const PLOT_BG = '#eaeaea'; // keep in sync with heart_surface.css 

    function heartSurfaceValue(x, y, z) {
        const a = 2 * x * x + y * y + z * z - 1;
        return a * a * a - (x * x * z * z * z) / 10 - y * y * z * z * z;
    }

    // Flat grid arrays for Plotly's isosurface trace. Plotly infers the
    // rectilinear grid shape itself from which coordinate changes first as
    // the array is walked (see traces/streamtube/calc.js processGrid, which
    // isosurface reuses) — so any consistent, complete x/y/z nesting works,
    // this doesn't need to match a specific row/column-major convention.
    function buildGrid(n) {
        const xs = [];
        const ys = [];
        const zs = [];
        const values = [];
        const step = (2 * RANGE) / (n - 1);

        for (let i = 0; i < n; i++) {
            const x = -RANGE + i * step;
            for (let j = 0; j < n; j++) {
                const y = -RANGE + j * step;
                for (let k = 0; k < n; k++) {
                    const z = -RANGE + k * step;
                    xs.push(x);
                    ys.push(y);
                    zs.push(z);
                    values.push(heartSurfaceValue(x, y, z));
                }
            }
        }
        return { xs, ys, zs, values };
    }

    let plotted = false;
    let resizeObserver = null;

    function renderPlot() {
        if (plotted) return;
        plotted = true;

        const { xs, ys, zs, values } = buildGrid(GRID_N);

        const trace = {
            type: 'isosurface',
            x: xs,
            y: ys,
            z: zs,
            value: values,
            isomin: 0,
            isomax: 0,
            surface: { show: true, count: 1 },
            caps: {
                x: { show: false },
                y: { show: false },
                z: { show: false }
            },
            colorscale: [
                [0, '#5b8fd6'],
                [1, '#0047ab'] // site accent
            ],
            showscale: false,
            lighting: {
                ambient: 0.55,
                diffuse: 0.8,
                specular: 0.4,
                roughness: 0.5,
                fresnel: 0.2
            },
            lightposition: { x: 200, y: 200, z: 200 },
            flatshading: false
        };

        const layout = {
            paper_bgcolor: PLOT_BG,
            scene: {
                bgcolor: PLOT_BG,
                xaxis: { visible: false },
                yaxis: { visible: false },
                zaxis: { visible: false },
                aspectmode: 'cube',
                camera: { eye: { x: 1.6, y: 1, z: 0.8 } }
            },
            margin: { t: 0, r: 0, b: 0, l: 0 }
        };

        Plotly.newPlot('heart-surface-plot', [trace], layout, {
            responsive: true,
            displayModeBar: false
        });

        const container = document.getElementById('heart-surface-plot');
        resizeObserver = new ResizeObserver(() => {
            Plotly.Plots.resize('heart-surface-plot');
        });
        resizeObserver.observe(container);
    }

    document.addEventListener('DOMContentLoaded', () => {
        const app = document.getElementById('heart-surface-app');
        const toggle = document.getElementById('heart-surface-toggle');
        const back = document.getElementById('heart-surface-back');
        if (!app || !toggle) return;

        function showGraph() {
            app.dataset.state = 'graph';
            toggle.setAttribute('aria-expanded', 'true');
            renderPlot();
            // The plot container is display:none right up until the line
            // above; give layout a tick to settle before Plotly re-measures.
            requestAnimationFrame(() => Plotly.Plots.resize('heart-surface-plot'));
        }

        function showEquation() {
            app.dataset.state = 'equation';
            toggle.setAttribute('aria-expanded', 'false');
        }

        toggle.addEventListener('click', showGraph);
        if (back) {
            back.addEventListener('click', (e) => {
                e.stopPropagation();
                showEquation();
            });
        }
     
        // One-time "this is clickable" hint: briefly replays the hover
        // treatment unprompted, since touch devices never trigger a real
        // :hover state and the equation alone doesn't obviously read as a
        // button. Skipped under prefers-reduced-motion, and cancelled if
        // the person clicks before it would have fired.
        const HINT_DELAY = 1400; // ms after DOMContentLoaded
 
        if (!window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
            const hintTimer = setTimeout(() => {
                if (app.dataset.state !== 'equation') return; // already clicked, skip
                toggle.classList.add('heart-surface-hint');
                toggle.addEventListener(
                    'animationend',
                    () => toggle.classList.remove('heart-surface-hint'),
                    { once: true }
                );
            }, HINT_DELAY);
 
            toggle.addEventListener('click', () => clearTimeout(hintTimer), { once: true });
        }

    });
})();
