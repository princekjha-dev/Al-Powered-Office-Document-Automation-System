/* ════════════════════════════════════════════════════════════
   DocAI — Frontend Logic v3
   Premium workspace with sidebar nav, chat toggle,
   multi-step loader, and keyboard shortcuts
   ════════════════════════════════════════════════════════════ */

const API = '';
let session = null;   // { session_id, filename }
let genFormat = 'docx';
let imgStyle = 'realistic';
let translateLang = 'en';

// ─── DOM Ready ──────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    initUpload();
    initChat();
    initSidebar();
    initChatToggle();
    initPills();
    initGenerate();
    initImage();
    initCompareWorkspace();
    initTools();
    initFeatureCards();
    initModal();
    initDocClose();
    initKeyboardShortcuts();
});

// ─── Upload ─────────────────────────────────────────────────
function initUpload() {
    const zone = document.getElementById('upload-zone');
    const input = document.getElementById('file-input');

    zone.addEventListener('click', () => input.click());
    zone.addEventListener('dragover', e => { e.preventDefault(); zone.classList.add('drag-over'); });
    zone.addEventListener('dragleave', () => zone.classList.remove('drag-over'));
    zone.addEventListener('drop', e => {
        e.preventDefault();
        zone.classList.remove('drag-over');
        if (e.dataTransfer.files.length) analyzeFile(e.dataTransfer.files[0]);
    });
    input.addEventListener('change', () => {
        if (input.files.length) analyzeFile(input.files[0]);
        input.value = '';
    });
}

async function analyzeFile(file) {
    const ext = '.' + file.name.split('.').pop().toLowerCase();
    if (!['.pdf', '.docx', '.xlsx'].includes(ext)) {
        toast('Unsupported file. Use PDF, DOCX, or XLSX.', 'error');
        return;
    }

    // Show loader
    hide('landing');
    hide('landing-bg');
    hide('workspace');
    show('full-loader');
    startLoaderSteps();

    const form = new FormData();
    form.append('file', file);

    try {
        const res = await fetch(API + '/api/analyze', { method: 'POST', body: form });
        const data = await res.json();
        if (!data.success) throw new Error(data.error || 'Analysis failed');

        session = { session_id: data.session_id, filename: data.filename };

        // Update header indicator
        document.getElementById('doc-name').textContent = data.filename;
        show('doc-indicator');

        // Complete loader steps
        completeLoaderSteps();

        // Small delay for UX polish
        await sleep(600);

        // Render workspace
        renderAnalysis(data);
        hide('full-loader');
        show('workspace');
        resetLoaderSteps();

        // Reset chat for new doc
        resetChat(data.filename);

        toast('Document analyzed successfully!', 'success');
    } catch (err) {
        toast(err.message, 'error');
        hide('full-loader');
        show('landing');
        show('landing-bg');
        resetLoaderSteps();
    }
}

// ─── Multi-step Loader ──────────────────────────────────────
function startLoaderSteps() {
    const steps = ['step-extract', 'step-score', 'step-ai'];
    steps.forEach(s => {
        const el = document.getElementById(s);
        el.classList.remove('active', 'done');
    });
    document.getElementById('step-extract').classList.add('active');

    // Simulate progress
    setTimeout(() => {
        document.getElementById('step-extract').classList.remove('active');
        document.getElementById('step-extract').classList.add('done');
        document.getElementById('step-score').classList.add('active');
    }, 1500);
    setTimeout(() => {
        document.getElementById('step-score').classList.remove('active');
        document.getElementById('step-score').classList.add('done');
        document.getElementById('step-ai').classList.add('active');
    }, 3000);
}

function completeLoaderSteps() {
    ['step-extract', 'step-score', 'step-ai'].forEach(s => {
        const el = document.getElementById(s);
        el.classList.remove('active');
        el.classList.add('done');
    });
}

function resetLoaderSteps() {
    ['step-extract', 'step-score', 'step-ai'].forEach(s => {
        const el = document.getElementById(s);
        el.classList.remove('active', 'done');
    });
    document.getElementById('step-extract').classList.add('active');
}

// ─── Render Analysis ────────────────────────────────────────
function renderAnalysis(d) {
    const sr = document.getElementById('stats-row');
    sr.innerHTML = `
        <div class="stat">
            <div class="stat-icon" style="background:var(--accent-bg);color:var(--accent-2);">🌐</div>
            <div class="stat-val grad">${d.language.name || 'Unknown'}</div>
            <div class="stat-lbl">Language ${Math.round((d.language.confidence||0)*100)}%</div>
        </div>
        <div class="stat">
            <div class="stat-icon" style="background:var(--purple-bg);color:var(--purple);">📂</div>
            <div class="stat-val grad">${(d.category.name||'—').toUpperCase()}</div>
            <div class="stat-lbl">Category ${Math.round((d.category.confidence||0)*100)}%</div>
        </div>
        <div class="stat">
            <div class="stat-icon" style="background:var(--blue-bg);color:var(--blue);">📝</div>
            <div class="stat-val grad">${(d.stats.words||0).toLocaleString()}</div>
            <div class="stat-lbl">Words</div>
        </div>
        <div class="stat">
            <div class="stat-icon" style="background:var(--green-bg);color:var(--green);">📄</div>
            <div class="stat-val grad">~${d.stats.pages||1}</div>
            <div class="stat-lbl">Pages</div>
        </div>
    `;

    // Quality
    const q = d.quality;
    const overall = q.overall || 0;
    const pct = overall / 10;
    const circumference = 2 * Math.PI * 46;
    const dash = circumference * pct;
    const gap = circumference - dash;
    let ringColor = overall >= 8 ? 'var(--green)' : overall >= 6 ? 'var(--accent-2)' : overall >= 4 ? 'var(--yellow)' : 'var(--red)';

    document.getElementById('quality-card').innerHTML = `
        <div class="card-head">
            <div class="card-icon" style="background:${overall >= 6 ? 'var(--green-bg)' : 'var(--yellow-bg)'};color:${overall >= 6 ? 'var(--green)' : 'var(--yellow)'};">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>
            </div>
            <h3>Quality Assessment</h3>
        </div>
        <div class="quality-layout">
            <div class="quality-ring">
                <svg viewBox="0 0 100 100">
                    <circle cx="50" cy="50" r="46" class="ring-bg"/>
                    <circle cx="50" cy="50" r="46" class="ring-fill" 
                        stroke="${ringColor}"
                        stroke-dasharray="${circumference}" 
                        stroke-dashoffset="${circumference}"
                        data-target="${gap}"/>
                </svg>
                <div class="quality-center">
                    <div class="qc-num" style="color:${ringColor}">${overall.toFixed(1)}</div>
                    <div class="qc-label">${q.label || 'Score'}</div>
                </div>
            </div>
            <div class="quality-bars">
                ${qBar('Clarity', q.clarity, '--accent-2')}
                ${qBar('Grammar', q.grammar, '--green')}
                ${qBar('Coherence', q.coherence, '--blue')}
                ${qBar('Completeness', q.completeness, '--purple')}
                ${qBar('Professional', q.professionalism, '--yellow')}
            </div>
        </div>
        <div class="tags">${(d.category.tags||[]).map(t=>`<span class="tag">${esc(t)}</span>`).join('')}</div>
    `;

    // Animate ring
    requestAnimationFrame(() => {
        const ring = document.querySelector('.ring-fill');
        if (ring) ring.style.strokeDashoffset = ring.dataset.target;
    });
    // Animate bars
    setTimeout(() => {
        document.querySelectorAll('.qb-fill').forEach(b => { b.style.width = b.dataset.w; });
    }, 200);

    // AI text
    document.getElementById('ai-text').textContent = d.ai_analysis || 'No AI analysis available.';
}

function qBar(name, val, colorVar) {
    val = val || 0;
    const pct = (val / 10 * 100).toFixed(0);
    return `<div class="qb-row">
        <span class="qb-name">${name}</span>
        <div class="qb-track"><div class="qb-fill" style="background:var(${colorVar}); width:0" data-w="${pct}%"></div></div>
        <span class="qb-val">${val.toFixed(1)}</span>
    </div>`;
}

// ─── Chat ───────────────────────────────────────────────────
function initChat() {
    const inp = document.getElementById('chat-input');
    const btn = document.getElementById('chat-send');
    btn.addEventListener('click', sendQ);
    inp.addEventListener('keydown', e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendQ(); } });

    // Quick prompts
    document.addEventListener('click', e => {
        if (e.target.classList.contains('qp')) {
            inp.value = e.target.dataset.q;
            sendQ();
        }
    });
}

function resetChat(filename) {
    const msgs = document.getElementById('chat-messages');
    msgs.innerHTML = `<div class="chat-welcome" id="chat-welcome">
        <p>👋 <strong>${esc(filename)}</strong> loaded! Ask me anything about it.</p>
        <div class="quick-prompts">
            <button class="qp" data-q="Summarize this document in 3 bullet points">📝 Summarize</button>
            <button class="qp" data-q="What are the key topics covered?">🔑 Key topics</button>
            <button class="qp" data-q="List all important facts and numbers">📊 Facts & numbers</button>
        </div>
    </div>`;
}

async function sendQ() {
    const inp = document.getElementById('chat-input');
    const q = inp.value.trim();
    if (!q || !session) return;

    // Hide welcome
    const wel = document.getElementById('chat-welcome');
    if (wel) wel.style.display = 'none';

    addMsg(q, 'user');
    inp.value = '';

    // Typing indicator
    const thinking = addTypingIndicator();

    try {
        const res = await fetch(API + '/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ session_id: session.session_id, question: q }),
        });
        const data = await res.json();
        thinking.remove();
        addMsg(data.success ? data.answer : ('Error: ' + (data.error||'Unknown')), 'bot');
    } catch (err) {
        thinking.remove();
        addMsg('Error: ' + err.message, 'bot');
    }
}

function addMsg(text, cls) {
    const msgs = document.getElementById('chat-messages');
    const div = document.createElement('div');
    div.className = 'chat-msg ' + cls;
    div.textContent = text;
    msgs.appendChild(div);
    msgs.scrollTop = msgs.scrollHeight;
    return div;
}

function addTypingIndicator() {
    const msgs = document.getElementById('chat-messages');
    const div = document.createElement('div');
    div.className = 'chat-msg bot thinking';
    div.innerHTML = '<div class="typing-dots"><span></span><span></span><span></span></div>';
    msgs.appendChild(div);
    msgs.scrollTop = msgs.scrollHeight;
    return div;
}

// ─── Chat Toggle ────────────────────────────────────────────
function initChatToggle() {
    const toggle = document.getElementById('chat-toggle');
    const chat = document.getElementById('ws-chat');
    if (!toggle || !chat) return;

    toggle.addEventListener('click', () => {
        chat.classList.toggle('collapsed');
        // Flip the arrow
        const svg = toggle.querySelector('svg');
        if (chat.classList.contains('collapsed')) {
            svg.innerHTML = '<polyline points="9 18 15 12 9 6"/>';
        } else {
            svg.innerHTML = '<polyline points="15 18 9 12 15 6"/>';
        }
    });
}

// ─── Sidebar Navigation ────────────────────────────────────
function initSidebar() {
    document.querySelectorAll('.sidebar-btn[data-panel]').forEach(btn => {
        btn.addEventListener('click', () => {
            // Update active sidebar button
            document.querySelectorAll('.sidebar-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            // Switch panel
            document.querySelectorAll('.ws-panel').forEach(p => p.classList.remove('active'));
            const panel = document.getElementById('ws-' + btn.dataset.panel);
            if (panel) {
                // Force re-trigger animation
                panel.classList.remove('active');
                void panel.offsetWidth;
                panel.classList.add('active');
            }
        });
    });
}

// ─── Pill Selectors ─────────────────────────────────────────
function initPills() {
    document.querySelectorAll('.pill-group').forEach(group => {
        group.querySelectorAll('.pill').forEach(pill => {
            pill.addEventListener('click', () => {
                group.querySelectorAll('.pill').forEach(p => p.classList.remove('active'));
                pill.classList.add('active');
                // Update vars
                if (pill.closest('#ws-generate')) genFormat = pill.dataset.val;
                if (pill.closest('#ws-image')) imgStyle = pill.dataset.val;
            });
        });
    });
}

// ─── Compare (Workspace) ────────────────────────────────────
function initCompareWorkspace() {
    document.getElementById('compare-btn').addEventListener('click', async () => {
        const text2 = document.getElementById('compare-text2').value.trim();
        if (!text2) { toast('Paste the second text to compare', 'error'); return; }

        const loader = document.getElementById('compare-loader');
        const result = document.getElementById('compare-result');
        show2(loader); hide2(result);

        try {
            const res = await fetch(API + '/api/compare', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ session_id: session?.session_id, text2 }),
            });
            const data = await res.json();
            if (data.error) throw new Error(data.error);

            result.innerHTML = `
                <div class="stats-row" style="margin-top:16px;">
                    <div class="stat"><div class="stat-val grad">${((data.similarity||0)*100).toFixed(1)}%</div><div class="stat-lbl">Similarity</div></div>
                    <div class="stat"><div class="stat-val" style="color:var(--green);">+${data.added||0}</div><div class="stat-lbl">Added</div></div>
                    <div class="stat"><div class="stat-val" style="color:var(--red);">−${data.removed||0}</div><div class="stat-lbl">Removed</div></div>
                    <div class="stat"><div class="stat-val">${data.unchanged||0}</div><div class="stat-lbl">Unchanged</div></div>
                </div>
                <div class="card" style="margin-top:14px;">
                    <div class="card-title">Changes</div>
                    ${(data.added_lines||[]).filter(l=>l.trim()).map(l=>`<span class="diff-add">+ ${esc(l.substring(0,150))}</span>`).join('')}
                    ${(data.removed_lines||[]).filter(l=>l.trim()).map(l=>`<span class="diff-rem">− ${esc(l.substring(0,150))}</span>`).join('')}
                    ${data.key_changes ? `<div style="margin-top:14px; font-size:0.85rem; color:var(--text-2); white-space:pre-wrap;">${esc(data.key_changes)}</div>` : ''}
                </div>
            `;
            show2(result);
        } catch (err) {
            toast(err.message, 'error');
        } finally {
            hide2(loader);
        }
    });
}

// ─── Generate ───────────────────────────────────────────────
function initGenerate() {
    document.getElementById('gen-btn').addEventListener('click', async () => {
        const topic = document.getElementById('gen-topic').value.trim();
        if (!topic) { toast('Enter a topic', 'error'); return; }

        const btn = document.getElementById('gen-btn');
        const loader = document.getElementById('gen-loader');
        const result = document.getElementById('gen-result');
        btn.disabled = true;
        show2(loader); hide2(result);

        try {
            const res = await fetch(API + '/api/generate/doc', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ topic, format: genFormat }),
            });
            if (!res.ok) {
                const err = await res.json().catch(()=>({}));
                throw new Error(err.error || 'Generation failed');
            }
            const blob = await res.blob();
            const fname = `${topic.replace(/[^a-zA-Z0-9 ]/g,'').replace(/ /g,'_').substring(0,40)}.${genFormat}`;
            downloadBlob(blob, fname);

            result.innerHTML = `<div class="card" style="text-align:center;margin-top:16px;">
                <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="var(--green)" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
                <p style="margin-top:12px;font-weight:700;font-size:1rem;">Document downloaded!</p>
                <p style="color:var(--text-3);font-size:0.82rem;margin-top:6px;">${esc(fname)}</p>
            </div>`;
            show2(result);
            toast('Document generated successfully!', 'success');
        } catch (err) {
            toast(err.message, 'error');
        } finally {
            btn.disabled = false;
            hide2(loader);
        }
    });
}

// ─── Image ──────────────────────────────────────────────────
function initImage() {
    document.getElementById('img-btn').addEventListener('click', async () => {
        const prompt = document.getElementById('img-prompt').value.trim();
        if (!prompt) { toast('Enter a prompt', 'error'); return; }

        const btn = document.getElementById('img-btn');
        const loader = document.getElementById('img-loader');
        const result = document.getElementById('img-result');
        btn.disabled = true;
        show2(loader); hide2(result);

        try {
            const res = await fetch(API + '/api/generate/image', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ prompt, style: imgStyle }),
            });
            if (!res.ok) {
                const err = await res.json().catch(()=>({}));
                throw new Error(err.error || 'Image generation failed');
            }
            const blob = await res.blob();
            const url = URL.createObjectURL(blob);

            result.innerHTML = `<div class="card" style="text-align:center;margin-top:16px;">
                <img src="${url}" class="img-preview" alt="Generated image">
                <div style="margin-top:16px;">
                    <a href="${url}" download="ai-image.png" class="btn btn-outline">⬇ Download Image</a>
                </div>
            </div>`;
            show2(result);
            toast('Image generated!', 'success');
        } catch (err) {
            toast(err.message, 'error');
        } finally {
            btn.disabled = false;
            hide2(loader);
        }
    });
}

// ─── Tools ──────────────────────────────────────────────────
function initTools() {
    document.getElementById('tool-lang').addEventListener('click', () => runTool('language'));
    document.getElementById('tool-cat').addEventListener('click', () => runTool('categorize'));
    document.getElementById('tool-qual').addEventListener('click', () => runTool('quality'));
    document.getElementById('tool-errors').addEventListener('click', () => runTool('errors'));
    document.getElementById('tool-translate').addEventListener('click', () => runTool('translate'));
    document.getElementById('tool-export').addEventListener('click', () => runTool('export'));
}

async function runTool(type) {
    const text = document.getElementById('tools-text').value.trim();
    if (!text) { toast('Paste some text first', 'error'); return; }

    const result = document.getElementById('tools-result');
    hide2(result);

    try {
        let res;
        if (type === 'errors') {
            res = await fetch(API + '/api/errors', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ session_id: session?.session_id || null }),
            });
        } else if (type === 'translate') {
            const lang = prompt('Target language code (example: en, hi, es):', translateLang) || translateLang;
            translateLang = lang.trim().toLowerCase() || 'en';
            res = await fetch(API + '/api/translate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text, target_language: translateLang }),
            });
        } else if (type === 'export') {
            res = await fetch(API + '/api/export', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ session_id: session?.session_id || null, format: 'json' }),
            });
        } else {
            res = await fetch(API + `/api/${type}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text }),
            });
        }
        const data = await res.json();

        let html = '';
        if (type === 'language') {
            html = `<div class="card" style="margin-top:14px;">
                <div class="card-title">Language Detection</div>
                <div class="stats-row"><div class="stat"><div class="stat-val grad">${esc(data.language_name||'Unknown')}</div><div class="stat-lbl">Language</div></div>
                <div class="stat"><div class="stat-val grad">${esc(data.language||'?')}</div><div class="stat-lbl">Code</div></div>
                <div class="stat"><div class="stat-val grad">${Math.round((data.confidence||0)*100)}%</div><div class="stat-lbl">Confidence</div></div></div>
            </div>`;
        } else if (type === 'categorize') {
            html = `<div class="card" style="margin-top:14px;">
                <div class="card-title">Categorization</div>
                <div class="stats-row"><div class="stat"><div class="stat-val grad">${(data.category||'—').toUpperCase()}</div><div class="stat-lbl">Category</div></div>
                <div class="stat"><div class="stat-val grad">${Math.round((data.confidence||0)*100)}%</div><div class="stat-lbl">Confidence</div></div></div>
                <div class="tags" style="margin-top:10px;">${(data.tags||[]).map(t=>`<span class="tag">${esc(t)}</span>`).join('')}</div>
            </div>`;
        } else if (type === 'quality') {
            const s = data.scores || {};
            html = `<div class="card" style="margin-top:14px;">
                <div class="card-title">Quality Score — ${(s.overall||0).toFixed(1)} / 10</div>
                <div class="quality-bars" style="margin-top:10px;">
                    ${qBar('Clarity', s.clarity, '--accent-2')}
                    ${qBar('Grammar', s.grammar, '--green')}
                    ${qBar('Coherence', s.coherence, '--blue')}
                    ${qBar('Completeness', s.completeness, '--purple')}
                    ${qBar('Professional', s.professionalism, '--yellow')}
                </div>
                ${data.suggestions?.length ? `<ul style="margin-top:14px;padding-left:18px;color:var(--text-2);font-size:0.82rem;line-height:1.7;">
                    ${data.suggestions.map(s=>`<li style="margin-bottom:6px;">${esc(s)}</li>`).join('')}
                </ul>` : ''}
            </div>`;
        } else if (type === 'errors') {
            const issues = data.issues || [];
            html = `<div class="card" style="margin-top:14px;">
                <div class="card-title">Error Detection Report</div>
                <p style="margin-bottom:10px;color:var(--text-2);">Detected issues: <strong>${issues.length}</strong></p>
                ${issues.length ? issues.map(i => `<div class="${i.severity === 'warning' ? 'diff-rem' : 'diff-add'}">${esc(i.message || 'Issue')}</div>`).join('') : '<div class="diff-add">No obvious issues found in quick checks.</div>'}
            </div>`;
        } else if (type === 'translate') {
            html = `<div class="card" style="margin-top:14px;">
                <div class="card-title">Translation (${esc(data.target_language || translateLang)})</div>
                <div class="ai-text">${esc(data.translated_text || 'No translation output')}</div>
            </div>`;
        } else if (type === 'export') {
            html = `<div class="card" style="margin-top:14px;">
                <div class="card-title">Session Export</div>
                <p style="color:var(--text-2);margin-bottom:10px;">Export generated successfully.</p>
                <button class="btn btn-outline" id="download-export-btn">⬇ Download JSON</button>
            </div>`;
        }
        result.innerHTML = html;
        show2(result);

        if (type === 'export') {
            const downloadBtn = document.getElementById('download-export-btn');
            if (downloadBtn) {
                downloadBtn.addEventListener('click', () => {
                    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
                    downloadBlob(blob, `session_export_${Date.now()}.json`);
                });
            }
        }

        // Animate bars if quality
        if (type === 'quality') {
            setTimeout(() => {
                result.querySelectorAll('.qb-fill').forEach(b => { b.style.width = b.dataset.w; });
            }, 100);
        }
    } catch (err) {
        toast(err.message, 'error');
    }
}

// ─── Feature Cards (Landing) ────────────────────────────────
function initFeatureCards() {
    document.querySelectorAll('.feature-card').forEach(card => {
        card.addEventListener('click', () => {
            openModal(card.dataset.tool);
        });
    });
}

function openModal(tool) {
    const overlay = document.getElementById('modal-overlay');
    const content = document.getElementById('modal-content');

    if (tool === 'generate') {
        content.innerHTML = `
            <h2 style="margin-bottom:18px;">✨ Generate Document</h2>
            <label class="label">Topic</label>
            <input type="text" id="m-gen-topic" class="input" placeholder='e.g. "Python Best Practices"'>
            <label class="label" style="margin-top:18px;">Format</label>
            <div class="pill-group" id="m-gen-pills">
                <button class="pill active" data-val="docx">Word (.docx)</button>
                <button class="pill" data-val="pdf">PDF</button>
            </div>
            <button class="btn btn-primary" style="margin-top:22px;width:100%;" id="m-gen-btn">Generate & Download</button>
            <div class="loader-inline" id="m-gen-loader" style="display:none;"><div class="spinner-sm"></div> Generating...</div>
        `;
        let mFmt = 'docx';
        content.querySelectorAll('#m-gen-pills .pill').forEach(p => {
            p.addEventListener('click', () => {
                content.querySelectorAll('#m-gen-pills .pill').forEach(pp => pp.classList.remove('active'));
                p.classList.add('active');
                mFmt = p.dataset.val;
            });
        });
        document.getElementById('m-gen-btn').addEventListener('click', async () => {
            const topic = document.getElementById('m-gen-topic').value.trim();
            if (!topic) return toast('Enter a topic', 'error');
            show2(document.getElementById('m-gen-loader'));
            document.getElementById('m-gen-btn').disabled = true;
            try {
                const res = await fetch(API + '/api/generate/doc', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ topic, format: mFmt }),
                });
                if (!res.ok) throw new Error((await res.json().catch(()=>({}))).error || 'Failed');
                downloadBlob(await res.blob(), `${topic.replace(/[^a-zA-Z0-9]/g,'_').substring(0,40)}.${mFmt}`);
                toast('Document downloaded!', 'success');
                closeModal();
            } catch (err) { toast(err.message, 'error'); }
            finally { hide2(document.getElementById('m-gen-loader')); document.getElementById('m-gen-btn').disabled = false; }
        });
    } else if (tool === 'image') {
        content.innerHTML = `
            <h2 style="margin-bottom:18px;">🎨 AI Image Generator</h2>
            <label class="label">Prompt</label>
            <input type="text" id="m-img-prompt" class="input" placeholder='e.g. "A sunset over mountains"'>
            <label class="label" style="margin-top:18px;">Style</label>
            <div class="pill-group" id="m-img-pills">
                <button class="pill active" data-val="realistic">Realistic</button>
                <button class="pill" data-val="artistic">Artistic</button>
                <button class="pill" data-val="abstract">Abstract</button>
            </div>
            <button class="btn btn-primary" style="margin-top:22px;width:100%;" id="m-img-btn">Generate Image</button>
            <div class="loader-inline" id="m-img-loader" style="display:none;"><div class="spinner-sm"></div> Generating...</div>
            <div id="m-img-result"></div>
        `;
        let mStyle = 'realistic';
        content.querySelectorAll('#m-img-pills .pill').forEach(p => {
            p.addEventListener('click', () => {
                content.querySelectorAll('#m-img-pills .pill').forEach(pp => pp.classList.remove('active'));
                p.classList.add('active');
                mStyle = p.dataset.val;
            });
        });
        document.getElementById('m-img-btn').addEventListener('click', async () => {
            const prompt = document.getElementById('m-img-prompt').value.trim();
            if (!prompt) return toast('Enter a prompt', 'error');
            show2(document.getElementById('m-img-loader'));
            document.getElementById('m-img-btn').disabled = true;
            try {
                const res = await fetch(API + '/api/generate/image', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ prompt, style: mStyle }),
                });
                if (!res.ok) throw new Error((await res.json().catch(()=>({}))).error || 'Failed');
                const url = URL.createObjectURL(await res.blob());
                document.getElementById('m-img-result').innerHTML = `
                    <img src="${url}" class="img-preview" style="margin-top:18px;">
                    <div style="margin-top:14px;text-align:center;"><a href="${url}" download="ai-image.png" class="btn btn-outline">⬇ Download</a></div>
                `;
            } catch (err) { toast(err.message, 'error'); }
            finally { hide2(document.getElementById('m-img-loader')); document.getElementById('m-img-btn').disabled = false; }
        });
    } else if (tool === 'compare') {
        content.innerHTML = `
            <h2 style="margin-bottom:18px;">📊 Compare Documents</h2>
            <p style="color:var(--text-3);font-size:0.85rem;margin-bottom:18px;">Paste two texts to compare them side by side.</p>
            <label class="label">Text 1</label>
            <textarea id="m-cmp1" class="textarea" rows="5" placeholder="First text..."></textarea>
            <label class="label" style="margin-top:14px;">Text 2</label>
            <textarea id="m-cmp2" class="textarea" rows="5" placeholder="Second text..."></textarea>
            <button class="btn btn-primary" style="margin-top:18px;width:100%;" id="m-cmp-btn">Compare</button>
            <div class="loader-inline" id="m-cmp-loader" style="display:none;"><div class="spinner-sm"></div> Comparing...</div>
            <div id="m-cmp-result"></div>
        `;
        document.getElementById('m-cmp-btn').addEventListener('click', async () => {
            const t1 = document.getElementById('m-cmp1').value.trim();
            const t2 = document.getElementById('m-cmp2').value.trim();
            if (!t1 || !t2) return toast('Paste both texts', 'error');
            show2(document.getElementById('m-cmp-loader'));
            try {
                const res = await fetch(API + '/api/compare', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ text1: t1, text2: t2 }),
                });
                const data = await res.json();
                if (data.error) throw new Error(data.error);
                document.getElementById('m-cmp-result').innerHTML = `
                    <div class="card" style="margin-top:18px;">
                        <p><strong>Similarity:</strong> ${((data.similarity||0)*100).toFixed(1)}%</p>
                        <p style="margin-top:8px;"><span style="color:var(--green);font-weight:700;">+${data.added||0} added</span> · <span style="color:var(--red);font-weight:700;">−${data.removed||0} removed</span></p>
                        ${data.key_changes ? `<div style="margin-top:12px;font-size:0.85rem;color:var(--text-2);white-space:pre-wrap;">${esc(data.key_changes)}</div>` : ''}
                    </div>
                `;
            } catch (err) { toast(err.message, 'error'); }
            finally { hide2(document.getElementById('m-cmp-loader')); }
        });
    } else if (tool === 'tools') {
        content.innerHTML = `
            <h2 style="margin-bottom:18px;">🛠️ Quick Tools</h2>
            <label class="label">Paste text to analyze</label>
            <textarea id="m-tools-text" class="textarea" rows="5" placeholder="Paste text here..."></textarea>
            <div class="tools-btns" style="margin-top:16px;">
                <button class="btn btn-outline" id="m-tool-lang">🌐 Language</button>
                <button class="btn btn-outline" id="m-tool-cat">📂 Category</button>
                <button class="btn btn-outline" id="m-tool-qual">📊 Quality</button>
            </div>
            <div id="m-tools-result" style="margin-top:14px;"></div>
        `;
        const runModalTool = async (type) => {
            const text = document.getElementById('m-tools-text').value.trim();
            if (!text) return toast('Paste some text', 'error');
            try {
                const res = await fetch(API + `/api/${type}`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ text }),
                });
                const data = await res.json();
                let html = '';
                if (type === 'language') html = `<div class="card"><p><strong>Language:</strong> ${esc(data.language_name||'Unknown')} (${esc(data.language||'?')}) — ${Math.round((data.confidence||0)*100)}% confidence</p></div>`;
                else if (type === 'categorize') html = `<div class="card"><p><strong>Category:</strong> ${esc((data.category||'?').toUpperCase())} — ${Math.round((data.confidence||0)*100)}%</p><div class="tags" style="margin-top:10px;">${(data.tags||[]).map(t=>`<span class="tag">${esc(t)}</span>`).join('')}</div></div>`;
                else if (type === 'quality') html = `<div class="card"><p><strong>Quality:</strong> ${(data.scores?.overall||0).toFixed(1)} / 10</p></div>`;
                document.getElementById('m-tools-result').innerHTML = html;
            } catch (err) { toast(err.message, 'error'); }
        };
        document.getElementById('m-tool-lang').addEventListener('click', () => runModalTool('language'));
        document.getElementById('m-tool-cat').addEventListener('click', () => runModalTool('categorize'));
        document.getElementById('m-tool-qual').addEventListener('click', () => runModalTool('quality'));
    }

    show('modal-overlay');
}

// ─── Modal ──────────────────────────────────────────────────
function initModal() {
    document.getElementById('modal-close').addEventListener('click', closeModal);
    document.getElementById('modal-overlay').addEventListener('click', e => {
        if (e.target.id === 'modal-overlay') closeModal();
    });
}
function closeModal() { hide('modal-overlay'); }

// ─── Doc Close (back to landing) ────────────────────────────
function initDocClose() {
    document.getElementById('doc-close').addEventListener('click', () => {
        session = null;
        hide('workspace');
        hide('doc-indicator');
        show('landing');
        show('landing-bg');
    });
}

// ─── Keyboard Shortcuts ─────────────────────────────────────
function initKeyboardShortcuts() {
    document.addEventListener('keydown', e => {
        // Ctrl+U → trigger upload
        if ((e.ctrlKey || e.metaKey) && e.key === 'u') {
            e.preventDefault();
            const input = document.getElementById('file-input');
            if (input) input.click();
        }
        // Escape → close modal
        if (e.key === 'Escape') {
            const modal = document.getElementById('modal-overlay');
            if (modal && modal.style.display !== 'none') {
                closeModal();
            }
        }
    });
}

// ─── Utility ────────────────────────────────────────────────
function show(id) {
    const el = document.getElementById(id);
    if (el) el.style.display = '';
}
function hide(id) {
    const el = document.getElementById(id);
    if (el) el.style.display = 'none';
}
function show2(el) { if (el) el.style.display = ''; }
function hide2(el) { if (el) el.style.display = 'none'; }

function esc(t) {
    if (!t) return '';
    const d = document.createElement('div');
    d.textContent = t;
    return d.innerHTML;
}

function downloadBlob(blob, name) {
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url; a.download = name;
    a.click();
    URL.revokeObjectURL(url);
}

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

function toast(msg, type = 'info') {
    const c = document.getElementById('toast-container');
    const t = document.createElement('div');
    t.className = 'toast-msg ' + type;

    // Icon
    let icon = '💡';
    if (type === 'error') icon = '❌';
    else if (type === 'success') icon = '✅';

    t.innerHTML = `<span class="toast-icon">${icon}</span><span>${esc(msg)}</span>`;
    c.appendChild(t);
    setTimeout(() => {
        t.style.opacity = '0';
        t.style.transform = 'translateX(20px)';
        t.style.transition = 'all 0.3s';
        setTimeout(() => t.remove(), 300);
    }, 4000);
}
