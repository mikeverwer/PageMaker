// Builds a floating table-of-contents from the headings in #markdown-content.
// Runs only if the page clears a heading threshold; otherwise adds nothing.

(function () {
    const HEADING_SELECTOR = 'h2, h3';
    const MIN_HEADINGS = 3;

    // Turn heading text into a URL-safe id.
    function slugify(text, used) {
        let base = text
            .toLowerCase()
            .trim()
            .replace(/[^\w\s-]/g, '')
            .replace(/\s+/g, '-')
            .replace(/-+/g, '-')
            || 'section';
        let slug = base;
        let n = 2;
        while (used.has(slug)) {
            slug = base + '-' + n++;
        }
        used.add(slug);
        return slug;
    }

    function buildToc() {
        const content = document.getElementById('markdown-content');
        if (!content) return;

        const headings = Array.from(content.querySelectorAll(HEADING_SELECTOR));
        if (headings.length < MIN_HEADINGS) return;

        // Ensure every heading has an id to jump to.
        const used = new Set();
        headings.forEach(h => {
            if (!h.id) h.id = slugify(h.textContent, used);
            else used.add(h.id);
        });

        // Toggle button — mirrors #toggle-sidebars styling via shared class.
        const toggle = document.createElement('button');
        toggle.id = 'toggle-toc';
        toggle.title = 'Table of contents';
        toggle.setAttribute('aria-expanded', 'false');
        toggle.textContent = '§';

        // The panel that lists the headings.
        const panel = document.createElement('nav');
        panel.id = 'toc-panel';
        panel.className = 'toc-hidden';
        panel.setAttribute('aria-label', 'Table of contents');

        const list = document.createElement('ul');
        const topLi = document.createElement('li');
        topLi.className = 'toc-h2';
        const topA = document.createElement('a');
        topA.href = '#';
        topA.textContent = '(Top)';
        topLi.appendChild(topA);
        list.appendChild(topLi);
        headings.forEach(h => {
            const li = document.createElement('li');
            li.className = 'toc-' + h.tagName.toLowerCase(); // toc-h2 / toc-h3
            const a = document.createElement('a');
            a.href = '#' + h.id;
            a.textContent = h.textContent;
            li.appendChild(a);
            list.appendChild(li);
        });
        panel.appendChild(list);

        document.body.appendChild(toggle);
        document.body.appendChild(panel);

        function openPanel() {
            panel.classList.remove('toc-hidden');
            toggle.setAttribute('aria-expanded', 'true');
        }
        function closePanel() {
            panel.classList.add('toc-hidden');
            toggle.setAttribute('aria-expanded', 'false');
        }
        function togglePanel() {
            if (panel.classList.contains('toc-hidden')) openPanel();
            else closePanel();
        }

        toggle.addEventListener('click', function (e) {
            e.stopPropagation();
            togglePanel();
        });

        // Clicking a link jumps and closes.
        panel.addEventListener('click', function (e) {
            if (e.target.tagName === 'A') closePanel();
        });

        // Click outside closes.
        document.addEventListener('click', function (e) {
            if (panel.classList.contains('toc-hidden')) return;
            if (!panel.contains(e.target) && e.target !== toggle) closePanel();
        });

        // Escape closes.
        document.addEventListener('keydown', function (e) {
            if (e.key === 'Escape') closePanel();
        });
    }

    // The markdown renders asynchronously, so wait for #markdown-content to be
    // populated rather than firing on DOMContentLoaded (when it's still empty).
    function waitForContent() {
        const content = document.getElementById('markdown-content');
        if (content && content.querySelector(HEADING_SELECTOR)) {
            buildToc();
            return;
        }
        const observer = new MutationObserver(function (mutations, obs) {
            const el = document.getElementById('markdown-content');
            if (el && el.querySelector(HEADING_SELECTOR)) {
                obs.disconnect();
                buildToc();
            }
        });
        observer.observe(document.body, { childList: true, subtree: true });
        // Safety timeout so the observer can't run forever.
        setTimeout(function () { observer.disconnect(); }, 10000);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', waitForContent);
    } else {
        waitForContent();
    }
})();
