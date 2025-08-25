mermaid.initialize({ startOnLoad: true, theme: 'dark' });

function addCopyButtonsToCodeBlocks() {
    const copySVG = '<svg class="copy-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24"><path d="M7.024 3.75c0-.966.784-1.75 1.75-1.75H20.25c.966 0 1.75.784 1.75 1.75v11.498a1.75 1.75 0 0 1-1.75 1.75H8.774a1.75 1.75 0 0 1-1.75-1.75Zm1.75-.25a.25.25 0 0 0-.25.25v11.498c0 .139.112.25.25.25H20.25a.25.25 0 0 0 .25-.25V3.75a.25.25 0 0 0-.25-.25Z"></path><path d="M1.995 10.749a1.75 1.75 0 0 1 1.75-1.751H5.25a.75.75 0 1 1 0 1.5H3.745a.25.25 0 0 0-.25.25L3.5 20.25c0 .138.111.25.25.25h9.5a.25.25 0 0 0 .25-.25v-1.51a.75.75 0 1 1 1.5 0v1.51A1.75 1.75 0 0 1 13.25 22h-9.5A1.75 1.75 0 0 1 2 20.25l-.005-9.501Z"></path></svg>';
    const checkSVG = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24"><path d="M21.03 5.72a.75.75 0 0 1 0 1.06l-11.5 11.5a.747.747 0 0 1-1.072-.012l-5.5-5.75a.75.75 0 1 1 1.084-1.036l4.97 5.195L19.97 5.72a.75.75 0 0 1 1.06 0Z"></path></svg>';
    const failSVG = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24"><path d="M5.72 5.72a.75.75 0 0 1 1.06 0L12 10.94l5.22-5.22a.749.749 0 0 1 1.275.326.749.749 0 0 1-.215.734L13.06 12l5.22 5.22a.749.749 0 0 1-.326 1.275.749.749 0 0 1-.734-.215L12 13.06l-5.22 5.22a.751.751 0 0 1-1.042-.018.751.751 0 0 1-.018-1.042L10.94 12 5.72 6.78a.75.75 0 0 1 0-1.06Z"></path></svg>';
    const codeBlocks = document.querySelectorAll('code[class^="language-"]');

    codeBlocks.forEach(codeBlock => {
        const container = codeBlock.closest('pre') || codeBlock.parentElement;
        // if (container.querySelector('.copy-button')) continue;
        
        const copyButton = document.createElement('button');
        copyButton.type = 'button';
        copyButton.className = 'copy-button';
        copyButton.innerHTML = copySVG;
        copyButton.title = 'Copy to clipboard';
        
        container.style.position = 'relative';
        container.appendChild(copyButton);
        
        copyButton.addEventListener('click', async () => {
            try {
                await navigator.clipboard.writeText(codeBlock.textContent);
                
                // Change to check icon
                copyButton.innerHTML = checkSVG;
                copyButton.classList.add('copied');
                
                setTimeout(() => {
                copyButton.innerHTML = copySVG;
                copyButton.classList.remove('copied');
                }, 1000);
                
            } catch (err) {
                console.error('Failed to copy: ', err);
                copyButton.innerHTML = failSVG;
                setTimeout(() => {
                copyButton.innerHTML = copySVG;
                }, 1000);
            }
        });
    });
}

async function renderMarkdown(element) {
    try {
        const MarkdownIt = (await import('https://cdn.jsdelivr.net/npm/markdown-it@14.1.0/+esm')).default;
        const footnoteModule = await import('https://cdn.jsdelivr.net/npm/markdown-it-footnote@4.0.0/+esm');
        const deflistModule = await import('https://cdn.jsdelivr.net/npm/markdown-it-deflist@3.0.0/+esm');
        const hljsModule = await import('https://cdn.jsdelivr.net/npm/highlight.js@11.11.0/+esm');
        
        // Initialize plugins
        const footnotePlugin = footnoteModule.default || footnoteModule;
        const deflistPlugin = deflistModule.default || deflistModule;
        const hljs = hljsModule.default || hljsModule;

        const md = new MarkdownIt({
            html: true, // Allow HTML tags
            linkify: true, // Autoconvert URL-like text to links
            typographer: true, // Enable some language-neutral replacement + quotes beautification

            highlight: function (str, lang) {
                if (lang && hljs.getLanguage(lang)) {
                    try {
                        return hljs.highlight(str, { language: lang }).value;
                    } catch (__) {}
                }

                return ''; // use external default escaping
            }
        });
        md.use(footnotePlugin); // Use footnotes plugin
        md.use(deflistPlugin);

        const src = element.getAttribute('src');
        const response = await fetch(src);
        const markdownText = await response.text();
        const htmlContent = md.render(markdownText);
        element.innerHTML = htmlContent;

        MathJax.typeset();

        // Find any mermaid code blocks and tell Mermaid to render them
        element.querySelectorAll('code.language-mermaid').forEach(el => {
            // Insert a dedicated div for mermaid to render into
            const graphDiv = document.createElement('div');
            const codeDetails = document.createElement('details');
            const codeSummary = document.createElement('summary');

            graphDiv.className = 'mermaid';
            graphDiv.textContent = el.textContent;

            codeSummary.textContent = "Mermaid Code";
            codeDetails.textContent = "\n" + el.textContent + "\n";
            el.textContent = "";

            codeDetails.insertAdjacentElement('beforeend', codeSummary);
            el.insertAdjacentElement('beforeend', codeDetails);
            el.insertAdjacentElement('afterend', graphDiv);
        });
        mermaid.run();

        // Add copy-to-clipboard button

        // element.querySelectorAll('code[class^="language-"]').forEach(el => {
        //     const copyButton = document.createElement('button');
        //     el.insertAdjacentElement('afterbegin', copyButton);
        // });
        addCopyButtonsToCodeBlocks();
        
    } catch (error) {
        console.error('Error loading or rendering markdown:', error);
        element.innerHTML = `<p style="color: red;">Error loading content: ${error.message}</p>`;
    }
}


// Render all elements with the class 'markdown-content'
document.addEventListener('DOMContentLoaded', function() {
    const markdownContent = document.getElementById('markdown-content');
    if (markdownContent) {
        renderMarkdown(markdownContent);
    }
});
