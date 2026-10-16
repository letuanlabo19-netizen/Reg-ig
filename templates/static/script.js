const socket = io();
const state = {};

function $(sel, root = document) { return root.querySelector(sel); }
function $$(sel, root = document) { return [...root.querySelectorAll(sel)]; }
function now() { return new Date().toLocaleTimeString('vi-VN', { hour12: false }); }
function escapeHtml(s) { return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;'); }

// ================== HIỆU ỨNG TRONG PANEL ==================
function createEffectForPanel(canvas) {
    if (!canvas) return null;
    const ctx = canvas.getContext('2d');
    let W = 0, H = 0;
    let ACTIVE = false;

    function resize() {
        const rect = canvas.getBoundingClientRect();
        W = canvas.width = Math.max(1, rect.width);
        H = canvas.height = Math.max(1, rect.height);
    }
    const ro = new ResizeObserver(resize);
    ro.observe(canvas);
    setTimeout(resize, 100);

    let ACCENT = '#ec4899';
    function getAccent() {
        const panel = canvas.closest('.tool-panel');
        const c = panel ? getComputedStyle(panel).getPropertyValue('--panel-color').trim() : '#ec4899';
        return c || '#ec4899';
    }

    const flowers = [];
    const FLOWER_COLORS = ['#ff6b9d', '#ffd93d', '#a78bfa', '#ff8fab', '#f9a8d4'];
    function newFlower() {
        return {
            x: Math.random() * W, y: -20,
            size: 6 + Math.random() * 8,
            speedY: 0.4 + Math.random() * 0.8,
            speedX: (Math.random() - 0.5) * 0.6,
            rot: Math.random() * Math.PI * 2,
            rotSpeed: (Math.random() - 0.5) * 0.05,
            color: FLOWER_COLORS[Math.floor(Math.random() * FLOWER_COLORS.length)],
            type: Math.random() < 0.5 ? 'flower' : 'petal'
        };
    }
    for (let i = 0; i < 8; i++) {
        const f = newFlower();
        f.y = Math.random() * H;
        flowers.push(f);
    }

    const hearts = [];
    function newHeart() {
        return {
            x: Math.random() * W, y: -20,
            size: 6 + Math.random() * 7,
            speedY: 0.6 + Math.random() * 1,
            speedX: (Math.random() - 0.5) * 0.5,
            color: ['#ef4444', '#ec4899', '#f43f5e', '#fb7185'][Math.floor(Math.random() * 4)],
            alpha: 0.6 + Math.random() * 0.4,
            pulse: Math.random() * Math.PI * 2
        };
    }
    for (let i = 0; i < 6; i++) {
        const h = newHeart();
        h.y = Math.random() * H;
        hearts.push(h);
    }

    const bolts = [];
    function newBolt() {
        const sx = Math.random() * W;
        const segs = [];
        let x = sx, y = 0;
        const endY = H * (0.4 + Math.random() * 0.5);
        while (y < endY) {
            segs.push({ x, y });
            x += (Math.random() - 0.5) * 60;
            y += 10 + Math.random() * 20;
        }
        return { segments: segs, life: 1, fadeSpeed: 0.03 + Math.random() * 0.02, width: 1 + Math.random() * 1.5 };
    }
    function triggerLightning() {
        for (let i = 0; i < 3; i++) setTimeout(() => bolts.push(newBolt()), i * 120);
    }

    function drawLightning(bolt, color) {
        if (bolt.segments.length < 2) return;
        ctx.save();
        ctx.globalAlpha = bolt.life;
        ctx.strokeStyle = color;
        ctx.lineWidth = bolt.width;
        ctx.shadowBlur = 15;
        ctx.shadowColor = color;
        ctx.lineCap = 'round';
        ctx.lineJoin = 'round';
        ctx.beginPath();
        ctx.moveTo(bolt.segments[0].x, bolt.segments[0].y);
        for (let i = 1; i < bolt.segments.length; i++) ctx.lineTo(bolt.segments[i].x, bolt.segments[i].y);
        ctx.stroke();
        ctx.strokeStyle = 'rgba(255,255,255,' + bolt.life + ')';
        ctx.lineWidth = bolt.width * 0.4;
        ctx.shadowBlur = 0;
        ctx.beginPath();
        ctx.moveTo(bolt.segments[0].x, bolt.segments[0].y);
        for (let i = 1; i < bolt.segments.length; i++) ctx.lineTo(bolt.segments[i].x, bolt.segments[i].y);
        ctx.stroke();
        ctx.restore();
    }

    function drawFlower(f) {
        ctx.save();
        ctx.translate(f.x, f.y);
        ctx.rotate(f.rot);
        ctx.globalAlpha = 0.85;
        ctx.fillStyle = f.color;
        ctx.shadowBlur = 8;
        ctx.shadowColor = f.color;
        if (f.type === 'petal') {
            ctx.beginPath();
            ctx.ellipse(0, 0, f.size, f.size * 0.5, 0, 0, Math.PI * 2);
            ctx.fill();
        } else {
            for (let i = 0; i < 5; i++) {
                ctx.save();
                ctx.rotate((Math.PI * 2 / 5) * i);
                ctx.beginPath();
                ctx.ellipse(0, -f.size * 0.5, f.size * 0.4, f.size * 0.7, 0, 0, Math.PI * 2);
                ctx.fill();
                ctx.restore();
            }
            ctx.fillStyle = '#ffd93d';
            ctx.beginPath();
            ctx.arc(0, 0, f.size * 0.25, 0, Math.PI * 2);
            ctx.fill();
        }
        ctx.restore();
    }

    function drawHeart(h) {
        ctx.save();
        ctx.translate(h.x, h.y);
        const s = h.size + Math.sin(h.pulse) * 1.2;
        ctx.globalAlpha = h.alpha;
        ctx.fillStyle = h.color;
        ctx.shadowBlur = 10;
        ctx.shadowColor = h.color;
        ctx.beginPath();
        ctx.moveTo(0, s * 0.3);
        ctx.bezierCurveTo(0, 0, -s * 0.5, 0, -s * 0.5, s * 0.3);
        ctx.bezierCurveTo(-s * 0.5, s * 0.7, 0, s * 1.1, 0, s * 1.3);
        ctx.bezierCurveTo(0, s * 1.1, s * 0.5, s * 0.7, s * 0.5, s * 0.3);
        ctx.bezierCurveTo(s * 0.5, 0, 0, 0, 0, s * 0.3);
        ctx.fill();
        ctx.restore();
    }

    function loop() {
        ctx.clearRect(0, 0, W, H);
        if (ACTIVE && W > 0 && H > 0) {
            ACCENT = getAccent();
            for (const f of flowers) {
                f.y += f.speedY;
                f.x += f.speedX + Math.sin(f.y * 0.02) * 0.3;
                f.rot += f.rotSpeed;
                if (f.y > H + 30) Object.assign(f, newFlower());
                drawFlower(f);
            }
            for (const h of hearts) {
                h.y += h.speedY;
                h.x += h.speedX + Math.sin(h.y * 0.02) * 0.3;
                h.pulse += 0.08;
                if (h.y > H + 30) Object.assign(h, newHeart());
                drawHeart(h);
            }
            for (let i = bolts.length - 1; i >= 0; i--) {
                bolts[i].life -= bolts[i].fadeSpeed;
                if (bolts[i].life <= 0) { bolts.splice(i, 1); continue; }
                drawLightning(bolts[i], ACCENT);
            }
            if (Math.random() < 0.02 && bolts.length < 2) bolts.push(newBolt());
        }
        requestAnimationFrame(loop);
    }
    loop();

    return {
        start: () => { ACTIVE = true; canvas.classList.add('active'); resize(); triggerLightning(); },
        stop: () => { ACTIVE = false; canvas.classList.remove('active'); bolts.length = 0; ctx.clearRect(0, 0, W, H); }
    };
}

const fxInstances = {};
$$('.tool-panel').forEach(panel => {
    const tool = panel.dataset.tool;
    const cForm = panel.querySelector('.fx-canvas-form');
    const cTerm = panel.querySelector('.fx-canvas-term');
    fxInstances[tool] = {
        form: createEffectForPanel(cForm),
        term: createEffectForPanel(cTerm)
    };
});

function fxStart(tool) {
    const fx = fxInstances[tool];
    if (fx) { if (fx.form) fx.form.start(); if (fx.term) fx.term.start(); }
}
function fxStop(tool) {
    const fx = fxInstances[tool];
    if (fx) { if (fx.form) fx.form.stop(); if (fx.term) fx.term.stop(); }
}

// ================== COLOR PICKER ==================
(function initColorPicker() {
    const picker = document.getElementById('theme-color');
    if (!picker) return;
    const saved = localStorage.getItem('theme_accent');
    if (saved) {
        document.documentElement.style.setProperty('--accent', saved);
        picker.value = saved;
    }
    picker.addEventListener('input', (e) => {
        document.documentElement.style.setProperty('--accent', e.target.value);
        localStorage.setItem('theme_accent', e.target.value);
    });
})();

// ================== LINE CLASSIFY ==================
function classifyLine(line) {
    if (/\b(traceback|exception|error|lỗi|die|fail|thất bại)\b/i.test(line)) return 'err';
    if (/\b(warn|cảnh báo|retry|timeout|chậm)\b/i.test(line)) return 'warn';
    if (/\b(success|thành công|✔|✅|ok|done|hoàn thành)\b/i.test(line)) return 'ok';
    if (/\b(info|đang|bắt đầu|nick|job|task|reg)\b/i.test(line)) return 'info';
    return '';
}

function appendLine(termEl, line, ts = null) {
    const div = document.createElement('div');
    div.className = 'term-line ' + classifyLine(line);
    div.innerHTML = `<span class="ts">[${ts || now()}]</span>${escapeHtml(line)}`;
    termEl.appendChild(div);
    termEl.scrollTop = termEl.scrollHeight;
}

setInterval(() => { const el = $('#clock'); if (el) el.textContent = now(); }, 1000);

// ================== TAB SWITCH ==================
$$('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        const tool = btn.dataset.tool;
        $$('.tab-btn').forEach(b => b.classList.toggle('active', b === btn));
        $$('.tool-panel').forEach(p => p.classList.toggle('active', p.dataset.tool === tool));
        setTimeout(() => {
            const fx = fxInstances[tool];
            if (fx) { if (fx.form) { const r = fx.form; } }
        }, 100);
    });
});
$$('.tab-btn')[0]?.click();

// ================== HELPERS ==================
function getPanel(tool) { return $(`.tool-panel[data-tool="${tool}"]`); }
function getTerm(tool) { const p = getPanel(tool); return p ? p.querySelector('.terminal') : null; }
function getStatusBadge(tool) { return $(`.session-info[data-tool="${tool}"] .status-badge`); }
function getSessionIdEl(tool) { return $(`.session-info[data-tool="${tool}"] .session-id`); }
function getOutputCount(tool) { return $(`.session-info[data-tool="${tool}"] .output-count`); }
function getBtn(tool, cls) { return $(`.btn-${cls}[data-tool="${tool}"]`); }
function getCfg(tool, cls) { const p = getPanel(tool); return p ? p.querySelector('.' + cls) : null; }

function setStatus(tool, status, sessionId = null) {
    const badge = getStatusBadge(tool);
    if (!badge) return;
    badge.className = 'status-badge ' + (status === 'running' ? 'running' : status === 'stopped' ? 'stopped' : 'idle');
    badge.textContent = status === 'running' ? '● RUNNING' : status === 'stopped' ? '● STOPPED' : '● IDLE';
    if (sessionId !== null) getSessionIdEl(tool).textContent = sessionId ? `Session: ${sessionId}` : '';
    const isRunning = status === 'running';
    getBtn(tool, 'start').disabled = isRunning;
    getBtn(tool, 'stop').disabled = !isRunning;
    getBtn(tool, 'clear').disabled = false;
    getBtn(tool, 'save').disabled = false;
    const stdin = $(`.stdin-input[data-tool="${tool}"]`);
    const sendBtn = $(`.btn-send[data-tool="${tool}"]`);
    if (stdin) stdin.disabled = !isRunning;
    if (sendBtn) sendBtn.disabled = !isRunning;
    const form = $(`#form-${tool.replace('.', '_')}`);
    if (form) form.querySelectorAll('input, textarea, select').forEach(el => el.disabled = isRunning);
}

// ================== BUILD CONFIG JSON ==================
function buildConfig(tool) {
    const smsToken = (getCfg(tool, 'cfg-sms-token')?.value || '').trim();
    const countryId = (getCfg(tool, 'cfg-country-id')?.value || '0').trim();
    const appId = (getCfg(tool, 'cfg-app-id')?.value || '12').trim();
    const use1sec = getCfg(tool, 'cfg-email-1secmail')?.checked;
    const useMailtm = getCfg(tool, 'cfg-email-mailtm')?.checked;
    let emailProvider = 'both';
    if (use1sec && !useMailtm) emailProvider = '1secmail';
    else if (!use1sec && useMailtm) emailProvider = 'mailtm';
    else if (!use1sec && !useMailtm) emailProvider = '1secmail';

    const proxiesRaw = (getCfg(tool, 'cfg-proxies')?.value || '').trim();
    const proxies = proxiesRaw.split('\n').map(s => s.trim()).filter(Boolean);
    const proxy = proxies.length > 0 ? proxies[0] : '';

    const avatarsRaw = (getCfg(tool, 'cfg-avatars')?.value || '').trim();
    const avatars = avatarsRaw.split('\n').map(s => s.trim()).filter(Boolean);

    const captionsRaw = (getCfg(tool, 'cfg-captions')?.value || '').trim();
    const captions = captionsRaw.split('\n').map(s => s.trim()).filter(Boolean);

    const usernamePattern = (getCfg(tool, 'cfg-username-pattern')?.value || 'user{rand}').trim();
    const passwordPattern = (getCfg(tool, 'cfg-password-pattern')?.value || 'Pass{rand}!').trim();
    const count = parseInt(getCfg(tool, 'cfg-count')?.value || '1');
    const threads = parseInt(getCfg(tool, 'cfg-threads')?.value || '1');
    const delay = parseInt(getCfg(tool, 'cfg-delay')?.value || '15');

    return {
        email_provider: emailProvider,
        sms_man_token: smsToken,
        country_id: countryId,
        app_id: appId,
        proxy: proxy,
        proxies: proxies,
        avatar_urls: avatars,
        captions: captions,
        username_pattern: usernamePattern,
        password_pattern: passwordPattern,
        count: count,
        threads: threads,
        delay: delay,
    };
}

// ================== START ==================
$$('.btn-start').forEach(btn => {
    btn.addEventListener('click', async () => {
        const tool = btn.dataset.tool;
        const config = buildConfig(tool);

        // Validate
        if (config.count < 1) { alert('⚠️ Số nick phải >= 1'); return; }
        if (config.avatar_urls.length === 0) {
            if (!confirm('⚠️ Chưa nhập URL avatar — nick reg ra sẽ không có ảnh. Vẫn tiếp tục?')) return;
        }
        if (config.captions.length === 0) {
            if (!confirm('⚠️ Chưa nhập caption — tool sẽ dùng caption mặc định. Vẫn tiếp tục?')) return;
        }
        if (config.proxies.length === 0) {
            if (!confirm('⚠️ Chưa nhập proxy — tỉ lệ sống sẽ ~0%. Vẫn tiếp tục?')) return;
        }

        btn.disabled = true;
        try {
            const res = await fetch(`/api/start/${tool}`, { method: 'POST' });
            const data = await res.json();
            if (!data.ok) { alert('Lỗi: ' + (data.error || '')); btn.disabled = false; return; }

            state[tool] = { sessionId: data.session_id, status: 'running' };
            setStatus(tool, 'running', data.session_id);
            socket.emit('join', { session_id: data.session_id });

            fxStart(tool);

            const term = getTerm(tool);
            if (term) {
                term.innerHTML = '';
                appendLine(term, `▶ Bắt đầu chạy [${tool}] — Session: ${data.session_id}`);
                appendLine(term, `📋 Config: ${config.count} nick | ${config.threads} luồng | proxy: ${config.proxies.length}`);
            }

            // Đợi 500ms cho process khởi động rồi gửi config JSON
            await new Promise(r => setTimeout(r, 500));
            const configJson = JSON.stringify(config);
            await fetch(`/api/input/${data.session_id}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text: configJson })
            });
            if (term) appendLine(term, `> [auto] Đã gửi config (${configJson.length} ký tự)`, now());

            $(`.tab-btn[data-tool="${tool}"]`).click();
        } catch (e) {
            alert('Lỗi kết nối: ' + e.message);
            btn.disabled = false;
        }
    });
});

// ================== TEST PROXY ==================
$$('.btn-test-proxy').forEach(btn => {
    btn.addEventListener('click', async () => {
        const panel = btn.closest('.tool-panel');
        const input = panel.querySelector('.cfg-test-proxy');
        const proxy = (input?.value || '').trim();
        if (!proxy) { alert('⚠️ Nhập proxy để test'); return; }
        btn.disabled = true;
        btn.textContent = 'Đang test...';
        try {
            const res = await fetch('/api/test-proxy', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ proxy })
            });
            const data = await res.json();
            if (data.ok) alert('✅ Proxy OK!\nIP: ' + data.ip);
            else alert('❌ Proxy die!\n' + (data.error || ''));
        } catch (e) {
            alert('Lỗi: ' + e.message);
        }
        btn.disabled = false;
        btn.textContent = 'Test Proxy';
    });
});

// ================== STOP ==================
$$('.btn-stop').forEach(btn => {
    btn.addEventListener('click', async () => {
        const tool = btn.dataset.tool;
        const s = state[tool]; if (!s) return;
        if (!confirm('Dừng tool này?')) return;
        await fetch(`/api/stop/${s.sessionId}`, { method: 'POST' });
        setStatus(tool, 'stopped');
        fxStop(tool);
    });
});

// ================== CLEAR ==================
$$('.btn-clear').forEach(btn => {
    btn.addEventListener('click', () => {
        const tool = btn.dataset.tool;
        const t = getTerm(tool); if (t) t.innerHTML = '';
        const c = getOutputCount(tool); if (c) c.textContent = '0 dòng';
        const s = state[tool]; if (s) fetch(`/api/clear/${s.sessionId}`, { method: 'POST' });
    });
});

// ================== SAVE ==================
$$('.btn-save').forEach(btn => {
    btn.addEventListener('click', async () => {
        const tool = btn.dataset.tool; const s = state[tool];
        if (!s) { alert('Chưa có session!'); return; }
        const res = await fetch(`/api/save/${s.sessionId}`, { method: 'POST' });
        const data = await res.json();
        if (data.ok) alert('Đã lưu: ' + data.filename); else alert('Lỗi: ' + (data.error || ''));
    });
});

// ================== STDIN ==================
function sendStdin(tool) {
    const input = $(`.stdin-input[data-tool="${tool}"]`); if (!input) return;
    const text = input.value; const s = state[tool]; if (!s || !s.sessionId) return;
    fetch(`/api/input/${s.sessionId}`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text })
    });
    const term = getTerm(tool); if (term) appendLine(term, `> ${text}`, now());
    input.value = '';
}
$$('.btn-send').forEach(btn => btn.addEventListener('click', () => sendStdin(btn.dataset.tool)));
$$('.stdin-input').forEach(inp => inp.addEventListener('keydown', e => {
    if (e.key === 'Enter') sendStdin(inp.dataset.tool);
}));

// ================== SOCKET ==================
socket.on('output', data => {
    const { session_id, line, ts } = data;
    const tool = Object.keys(state).find(k => state[k].sessionId === session_id);
    if (!tool) return;
    const term = getTerm(tool); if (!term) return;
    appendLine(term, line, ts);
    const oc = getOutputCount(tool); if (oc) oc.textContent = term.children.length + ' dòng';
});

socket.on('status', data => {
    const { session_id, status, message, return_code } = data;
    const tool = Object.keys(state).find(k => state[k].sessionId === session_id);
    if (!tool) return;
    if (status === 'stopped') {
        state[tool].status = 'stopped';
        setStatus(tool, 'stopped');
        const term = getTerm(tool);
        if (term) appendLine(term, `■ ${message || 'Đã dừng'} (exit: ${return_code ?? '?'})`);
        fxStop(tool);
    }
});

socket.on('cleared', data => {
    const tool = Object.keys(state).find(k => state[k].sessionId === data.session_id);
    if (tool) { const t = getTerm(tool); if (t) t.innerHTML = ''; }
});

// ================== AUTO SAVE CONFIG ==================
const CFG_FIELDS = ['cfg-sms-token', 'cfg-country-id', 'cfg-app-id', 'cfg-proxies', 'cfg-avatars',
                    'cfg-captions', 'cfg-username-pattern', 'cfg-password-pattern', 'cfg-count',
                    'cfg-threads', 'cfg-delay'];
CFG_FIELDS.forEach(cls => {
    $$('.' + cls).forEach(input => {
        const tool = input.closest('.tool-panel')?.dataset.tool;
        if (!tool) return;
        const key = `ta_cfg_${tool}_${cls}`;
        const saved = localStorage.getItem(key);
        if (saved !== null) input.value = saved;
        input.addEventListener('input', () => localStorage.setItem(key, input.value));
    });
});
['cfg-email-1secmail', 'cfg-email-mailtm'].forEach(cls => {
    $$('.' + cls).forEach(cb => {
        const tool = cb.closest('.tool-panel')?.dataset.tool;
        if (!tool) return;
        const key = `ta_cfg_${tool}_${cls}`;
        const saved = localStorage.getItem(key);
        if (saved !== null) cb.checked = saved === 'true';
        cb.addEventListener('change', () => localStorage.setItem(key, cb.checked));
    });
});

fetch('/api/sessions').then(r => r.json()).then(list => {
    const el = $('#sessions-count'); if (el) el.textContent = list.length + ' sessions';
});
