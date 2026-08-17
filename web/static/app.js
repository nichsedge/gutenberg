// ─────────────────────────────────────────────────────────────────────────────
// Gutenberg Ebook Analysis Platform — Frontend Application
// Features: caching, keyboard shortcuts, bookmarks, theme toggle, command palette,
// global loading bar, sentiment, compare, full-text search
// ─────────────────────────────────────────────────────────────────────────────

let currentBookId = "1998";
let currentCatalog = [];
let chartInstances = {};
let networkInstance = null;

// ── Tab definitions for command palette & keyboard shortcuts ─────────────────
const TABS = [
    { key: "tab-basic-stats",      icon: "📊", label: "Basic Statistics",             shortcut: "1" },
    { key: "tab-frequency",        icon: "🔤", label: "Word Frequency & TF-IDF",       shortcut: "2" },
    { key: "tab-wordcloud",        icon: "☁️", label: "Word Clouds",                  shortcut: "3" },
    { key: "tab-charts",           icon: "📈", label: "Charts & Distributions",        shortcut: "4" },
    { key: "tab-ngrams",           icon: "🧩", label: "N-Grams Explorer",              shortcut: "5" },
    { key: "tab-pos-patterns",     icon: "🏷️", label: "PoS Patterns"                              },
    { key: "tab-pos-query",        icon: "🔍", label: "PoS Query Engine"                           },
    { key: "tab-repeated-verses",  icon: "🔁", label: "Repeated Verses"                            },
    { key: "tab-repeated-phrases", icon: "✂️", label: "Repeated Phrases"                           },
    { key: "tab-pause-marks",      icon: "⏸️", label: "Pause Marks & Rhythm"                       },
    { key: "tab-ontology",         icon: "🕸️", label: "Ontology Data & Graphs"                     },
    { key: "tab-word-info",        icon: "📖", label: "Word Information"                            },
    { key: "tab-collocation",      icon: "🔗", label: "Collocation"                                },
    { key: "tab-concordance",      icon: "📑", label: "Concordance (KWIC)"                          },
    { key: "tab-similarity",       icon: "🧬", label: "Word Similarity"                             },
    { key: "tab-sentiment",        icon: "🎭", label: "Sentiment Analysis"                          },
    { key: "tab-compare",          icon: "⚖️", label: "Compare Books"                               },
    { key: "tab-search",           icon: "🔎", label: "Full-Text Search"                             },
    { key: "tab-dataset",          icon: "💾", label: "Dataset Export & API"                        },
];

// ── Init ──────────────────────────────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", () => {
    applyStoredTheme();
    initNavigation();
    loadCatalog();
    setupEventListeners();
    setupMobileSidebar();
    setupBookmarks();
    setupCommandPalette();
    setupKeyboardShortcuts();
    updateBookmarkBadge();
});

// ── Global Loading Bar ────────────────────────────────────────────────────────
const loadingBar = document.getElementById("global-loading-bar");
let loadingCount = 0;
function showLoading() {
    loadingCount++;
    loadingBar.style.width = "0%";
    loadingBar.classList.remove("done");
    loadingBar.classList.add("loading");
}
function hideLoading() {
    loadingCount = Math.max(0, loadingCount - 1);
    if (loadingCount === 0) {
        loadingBar.classList.remove("loading");
        loadingBar.style.width = "100%";
        loadingBar.classList.add("done");
        setTimeout(() => { loadingBar.style.width = "0%"; loadingBar.classList.remove("done"); }, 600);
    }
}

// ── API wrapper with loading bar ──────────────────────────────────────────────
async function apiFetch(url) {
    showLoading();
    try {
        const res = await fetch(url);
        if (!res.ok) {
            const err = await res.json().catch(() => ({}));
            throw new Error(err.detail || `HTTP ${res.status}`);
        }
        return await res.json();
    } finally {
        hideLoading();
    }
}

// ── Theme Toggle ──────────────────────────────────────────────────────────────
function applyStoredTheme() {
    const theme = localStorage.getItem("eba-theme") || "dark";
    if (theme === "light") document.body.classList.add("theme-light");
    updateThemeBtn();
}
function updateThemeBtn() {
    const btn = document.getElementById("btn-theme-toggle");
    if (btn) btn.textContent = document.body.classList.contains("theme-light") ? "🌙" : "☀️";
}
function toggleTheme() {
    document.body.classList.toggle("theme-light");
    localStorage.setItem("eba-theme", document.body.classList.contains("theme-light") ? "light" : "dark");
    updateThemeBtn();
}

// ── Mobile Sidebar ────────────────────────────────────────────────────────────
function setupMobileSidebar() {
    const sidebar = document.getElementById("sidebar");
    const overlay = document.getElementById("sidebar-overlay");
    const openBtn = document.getElementById("sidebar-open");
    const closeBtn = document.getElementById("sidebar-close");

    openBtn?.addEventListener("click", () => {
        sidebar.classList.add("mobile-open");
        overlay.classList.add("mobile-open");
    });
    const closeSidebar = () => {
        sidebar.classList.remove("mobile-open");
        overlay.classList.remove("mobile-open");
    };
    closeBtn?.addEventListener("click", closeSidebar);
    overlay?.addEventListener("click", closeSidebar);
}

// ── Keyboard Shortcuts ────────────────────────────────────────────────────────
function setupKeyboardShortcuts() {
    document.addEventListener("keydown", (e) => {
        // Ignore if typing in an input
        if (e.target.tagName === "INPUT" || e.target.tagName === "TEXTAREA" || e.target.tagName === "SELECT") return;

        // Ctrl+K — command palette
        if (e.key === "k" && (e.ctrlKey || e.metaKey)) {
            e.preventDefault();
            openCommandPalette();
            return;
        }
        // Ctrl+B — bookmarks
        if (e.key === "b" && (e.ctrlKey || e.metaKey)) {
            e.preventDefault();
            toggleBookmarksPanel();
            return;
        }
        // Escape — close palette/panel
        if (e.key === "Escape") {
            closeCommandPalette();
            closeBookmarksPanel();
            return;
        }
        // Number keys 1-5 → tabs
        if (/^[1-5]$/.test(e.key) && !e.ctrlKey && !e.metaKey && !e.altKey) {
            const idx = parseInt(e.key) - 1;
            const tab = TABS.find(t => t.shortcut === e.key);
            if (tab) activateTab(tab.key);
            return;
        }
    });
}

// ── Command Palette ───────────────────────────────────────────────────────────
function setupCommandPalette() {
    const backdrop = document.getElementById("cmd-palette-backdrop");
    const input = document.getElementById("cmd-palette-input");
    const results = document.getElementById("cmd-palette-results");

    backdrop?.addEventListener("click", (e) => { if (e.target === backdrop) closeCommandPalette(); });

    input?.addEventListener("input", () => {
        const q = input.value.toLowerCase();
        results.innerHTML = "";
        const filtered = q
            ? TABS.filter(t => t.label.toLowerCase().includes(q))
            : TABS;
        filtered.slice(0, 8).forEach((tab, i) => {
            const div = document.createElement("div");
            div.className = "cmd-palette-result" + (i === 0 ? " active" : "");
            div.innerHTML = `<span class="cmd-palette-result-icon">${tab.icon}</span>${tab.label}`;
            div.addEventListener("click", () => { activateTab(tab.key); closeCommandPalette(); });
            results.appendChild(div);
        });
    });
    // Trigger initial render
    input?.dispatchEvent(new Event("input"));
}

function openCommandPalette() {
    const backdrop = document.getElementById("cmd-palette-backdrop");
    backdrop?.classList.add("open");
    const input = document.getElementById("cmd-palette-input");
    input.value = "";
    input?.dispatchEvent(new Event("input"));
    setTimeout(() => input?.focus(), 50);
}
function closeCommandPalette() {
    document.getElementById("cmd-palette-backdrop")?.classList.remove("open");
}

// ── Bookmarks (localStorage) ──────────────────────────────────────────────────
function setupBookmarks() {
    document.getElementById("btn-bookmarks")?.addEventListener("click", toggleBookmarksPanel);
    document.getElementById("bookmarks-close")?.addEventListener("click", closeBookmarksPanel);
}
function toggleBookmarksPanel() {
    const panel = document.getElementById("bookmarks-panel");
    if (panel.classList.contains("open")) { closeBookmarksPanel(); }
    else { panel.classList.add("open"); renderBookmarks(); }
}
function closeBookmarksPanel() { document.getElementById("bookmarks-panel")?.classList.remove("open"); }

function getBookmarks() {
    try { return JSON.parse(localStorage.getItem("eba-bookmarks") || "[]"); } catch { return []; }
}
function saveBookmarks(bms) { localStorage.setItem("eba-bookmarks", JSON.stringify(bms)); }
function addBookmark(text, meta = "") {
    const bms = getBookmarks();
    if (bms.find(b => b.text === text && b.bookId === currentBookId)) return; // no dupes
    bms.unshift({ id: Date.now(), bookId: currentBookId, text: text.slice(0, 200), meta });
    saveBookmarks(bms);
    updateBookmarkBadge();
    renderBookmarks();
}
function deleteBookmark(id) {
    saveBookmarks(getBookmarks().filter(b => b.id !== id));
    updateBookmarkBadge();
    renderBookmarks();
}
function updateBookmarkBadge() {
    const badge = document.getElementById("bookmark-count-badge");
    const bms = getBookmarks().filter(b => b.bookId === currentBookId);
    if (badge) badge.textContent = bms.length > 0 ? ` ${bms.length}` : "";
}
function renderBookmarks() {
    const list = document.getElementById("bookmarks-list");
    if (!list) return;
    const bms = getBookmarks().filter(b => b.bookId === currentBookId);
    if (bms.length === 0) {
        list.innerHTML = `<div style="padding: 1.5rem; text-align:center; color: var(--text-muted); font-size:0.85rem;">No bookmarks yet.<br><br>Click the 🔖 icon on any verse or passage to save it here.</div>`;
        return;
    }
    list.innerHTML = bms.map(b => `
        <div class="bookmark-item">
            <button class="bookmark-del" onclick="deleteBookmark(${b.id})">✕ remove</button>
            <div style="color: var(--text-primary); line-height: 1.4;">${escapeHtml(b.text.slice(0, 120))}${b.text.length > 120 ? "…" : ""}</div>
            <div class="bookmark-meta">${escapeHtml(b.meta)}</div>
        </div>
    `).join("");
}

// ── Tab Navigation ────────────────────────────────────────────────────────────
function initNavigation() {
    document.querySelectorAll(".nav-item").forEach(item => {
        item.addEventListener("click", () => {
            const tabId = item.getAttribute("data-tab");
            activateTab(tabId);
            // Close mobile sidebar after nav
            if (window.innerWidth <= 768) {
                document.getElementById("sidebar")?.classList.remove("mobile-open");
                document.getElementById("sidebar-overlay")?.classList.remove("mobile-open");
            }
        });
    });
}

function activateTab(tabId) {
    document.querySelectorAll(".nav-item").forEach(n => n.classList.remove("active"));
    const navItem = document.querySelector(`[data-tab="${tabId}"]`);
    if (navItem) navItem.classList.add("active");

    document.querySelectorAll(".tab-content").forEach(tc => tc.classList.remove("active"));
    const activeTab = document.getElementById(tabId);
    if (activeTab) { activeTab.classList.add("active"); loadTabContent(tabId); }
}

// ── Catalog Loading ───────────────────────────────────────────────────────────
async function loadCatalog() {
    try {
        const data = await apiFetch("/api/catalog");
        currentCatalog = data.catalog;
        const selector = document.getElementById("book-selector");
        const cmpA = document.getElementById("compare-book-a");
        const cmpB = document.getElementById("compare-book-b");

        [selector, cmpA, cmpB].forEach((el, idx) => {
            if (!el) return;
            el.innerHTML = "";
            currentCatalog.forEach(b => {
                const opt = document.createElement("option");
                opt.value = b.id;
                opt.textContent = `${b.title} (${b.author})`;
                if (b.id === currentBookId) opt.selected = true;
                // For compare B, default to different book
                if (idx === 2 && b.id === "4363") opt.selected = true;
                el.appendChild(opt);
            });
        });
        loadTabContent("tab-basic-stats");
    } catch (e) { console.error("Error loading catalog:", e); }
}

// ── Event Listeners ───────────────────────────────────────────────────────────
function setupEventListeners() {
    document.getElementById("book-selector")?.addEventListener("change", (e) => {
        currentBookId = e.target.value;
        const activeTab = document.querySelector(".nav-item.active")?.getAttribute("data-tab");
        if (activeTab) loadTabContent(activeTab);
        updateBookmarkBadge();
    });

    document.getElementById("btn-theme-toggle")?.addEventListener("click", toggleTheme);

    document.getElementById("btn-load-custom-id")?.addEventListener("click", async () => {
        const idInput = prompt("Enter Project Gutenberg Ebook ID (e.g. 51710 for Birth of Tragedy):");
        if (idInput?.trim()) {
            const btn = document.getElementById("btn-load-custom-id");
            btn.innerHTML = `<span class="loading-spinner"></span> Loading...`;
            try {
                const formData = new FormData();
                formData.append("book_id", idInput.trim());
                showLoading();
                const res = await fetch("/api/load-book", { method: "POST", body: formData });
                const json = await res.json();
                if (res.ok) {
                    await loadCatalog();
                    currentBookId = json.book.id;
                    document.getElementById("book-selector").value = currentBookId;
                    const activeTab = document.querySelector(".nav-item.active")?.getAttribute("data-tab");
                    if (activeTab) loadTabContent(activeTab);
                } else { alert("Error loading book: " + (json.detail || "Unknown error")); }
            } catch (err) { alert("Failed to load book: " + err.message); }
            finally { btn.innerHTML = `<span>📥</span> Load Gutenberg ID`; hideLoading(); }
        }
    });

    // Concordance
    document.getElementById("btn-concordance-search")?.addEventListener("click", loadConcordance);
    document.getElementById("kwic-search-input")?.addEventListener("keyup", e => { if (e.key === "Enter") loadConcordance(); });

    // POS Query
    document.getElementById("btn-pos-query")?.addEventListener("click", loadPosQuery);
    document.getElementById("pos-query-input")?.addEventListener("keyup", e => { if (e.key === "Enter") loadPosQuery(); });

    // Similarity
    document.getElementById("btn-sim-search")?.addEventListener("click", loadWordSimilarity);
    document.getElementById("sim-word1-input")?.addEventListener("keyup", e => { if (e.key === "Enter") loadWordSimilarity(); });

    // Word Info
    document.getElementById("btn-word-info-search")?.addEventListener("click", () => {
        const q = document.getElementById("word-info-input").value;
        if (q) loadWordInfo(q);
    });
    document.getElementById("word-info-input")?.addEventListener("keyup", e => { if (e.key === "Enter") loadWordInfo(e.target.value); });

    // Frequency filters
    document.getElementById("freq-pos-filter")?.addEventListener("change", loadFrequency);
    document.getElementById("freq-stopwords-toggle")?.addEventListener("change", loadFrequency);
    document.getElementById("freq-search-input")?.addEventListener("input", debounce(loadFrequency, 300));

    // Compare
    document.getElementById("btn-compare")?.addEventListener("click", loadCompare);

    // Search
    document.getElementById("btn-search")?.addEventListener("click", loadFullTextSearch);
    document.getElementById("search-phrase-input")?.addEventListener("keyup", e => { if (e.key === "Enter") loadFullTextSearch(); });
}

function debounce(func, wait) {
    let timeout;
    return function(...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func(...args), wait);
    };
}

// ── Tab Router ────────────────────────────────────────────────────────────────
function loadTabContent(tabId) {
    const loaders = {
        "tab-basic-stats":      loadBasicStats,
        "tab-frequency":        loadFrequency,
        "tab-wordcloud":        loadWordCloud,
        "tab-charts":           loadCharts,
        "tab-ngrams":           loadNgrams,
        "tab-pos-patterns":     loadPosPatterns,
        "tab-pos-query":        () => {},
        "tab-repeated-verses":  loadRepeatedVerses,
        "tab-repeated-phrases": loadRepeatedPhrases,
        "tab-ontology":         loadOntology,
        "tab-word-info":        () => {},
        "tab-collocation":      loadCollocation,
        "tab-concordance":      loadConcordance,
        "tab-pause-marks":      loadPauseMarks,
        "tab-similarity":       () => {},
        "tab-sentiment":        loadSentiment,
        "tab-compare":          () => {},
        "tab-search":           () => {},
        "tab-dataset":          () => {},
    };
    loaders[tabId]?.();
}

// ── Helpers ───────────────────────────────────────────────────────────────────
function escapeHtml(str) {
    return str.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;");
}

function skeletonStats(n = 4) {
    return `<div class="stat-grid">${Array(n).fill('<div class="stat-card skeleton skeleton-stat"></div>').join("")}</div>`;
}

function bookmarkButton(text, meta) {
    const escapedText = escapeHtml(text).replace(/'/g, "\\'");
    const escapedMeta = escapeHtml(meta).replace(/'/g, "\\'");
    return `<button onclick="addBookmark('${escapedText}','${escapedMeta}')" style="background:none;border:none;cursor:pointer;color:var(--text-muted);font-size:0.8rem;" title="Bookmark this passage">🔖</button>`;
}

// ── 1. Basic Statistics ───────────────────────────────────────────────────────
async function loadBasicStats() {
    const container = document.getElementById("stats-container");
    container.innerHTML = skeletonStats(6) + `<div style="display:grid;grid-template-columns:1fr 1fr;gap:1.5rem;"><div class="card skeleton" style="height:280px;"></div><div class="card skeleton" style="height:280px;"></div></div>`;

    try {
        const data = await apiFetch(`/api/stats?book_id=${currentBookId}`);

        container.innerHTML = `
            <div class="stat-grid">
                <div class="stat-card">
                    <div class="stat-label">Total Words (Tokens)</div>
                    <div class="stat-value" style="color: var(--accent-gold);">${data.total_words.toLocaleString()}</div>
                    <div class="stat-sub">${data.total_characters.toLocaleString()} characters</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Unique Vocabulary</div>
                    <div class="stat-value" style="color: var(--accent-blue);">${data.unique_words.toLocaleString()}</div>
                    <div class="stat-sub">TTR: ${data.type_token_ratio}%</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Hapax Legomena</div>
                    <div class="stat-value" style="color: var(--accent-emerald);">${data.hapax_legomena.toLocaleString()}</div>
                    <div class="stat-sub">${data.hapax_percentage}% of vocabulary used once</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Verses &amp; Aphorisms</div>
                    <div class="stat-value" style="color: var(--accent-purple);">${data.total_verses.toLocaleString()}</div>
                    <div class="stat-sub">Across ${data.total_chapters} sections/chapters</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Flesch Reading Ease</div>
                    <div class="stat-value">${data.flesch_reading_ease}</div>
                    <div class="stat-sub">Grade Level: ${data.flesch_kincaid_grade} (Gunning Fog: ${data.gunning_fog_index})</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Estimated Reading Time</div>
                    <div class="stat-value">${Math.floor(data.estimated_reading_minutes / 60)}h ${data.estimated_reading_minutes % 60}m</div>
                    <div class="stat-sub">Avg Sentence: ${data.average_sentence_length} words</div>
                </div>
            </div>

            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(380px, 1fr)); gap: 1.5rem;">
                <div class="card">
                    <div class="card-header"><div class="card-title">Word Length Distribution</div></div>
                    <div style="height: 260px;"><canvas id="wordLengthChart"></canvas></div>
                </div>
                <div class="card">
                    <div class="card-header"><div class="card-title">Chapter Progression &amp; Density</div></div>
                    <div style="height: 260px;"><canvas id="chapterProgressionChart"></canvas></div>
                </div>
            </div>`;

        const chartDefaults = { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } };
        const darkTick = { color: "#94a3b8" };
        const darkGrid = { color: "rgba(51,65,85,0.6)" };

        const wlCtx = document.getElementById("wordLengthChart").getContext("2d");
        if (chartInstances.wordLength) chartInstances.wordLength.destroy();
        chartInstances.wordLength = new Chart(wlCtx, {
            type: "bar",
            data: {
                labels: data.word_length_distribution.map(d => `${d.length}`),
                datasets: [{ label: "Word Count", data: data.word_length_distribution.map(d => d.count), backgroundColor: "#f59e0b", borderRadius: 4 }]
            },
            options: { ...chartDefaults, scales: { x: { ticks: darkTick, grid: darkGrid }, y: { ticks: darkTick, grid: darkGrid } } }
        });

        const cpCtx = document.getElementById("chapterProgressionChart").getContext("2d");
        if (chartInstances.chapterProgression) chartInstances.chapterProgression.destroy();
        chartInstances.chapterProgression = new Chart(cpCtx, {
            type: "line",
            data: {
                labels: data.chapter_stats.slice(0, 30).map(c => `§${c.id}`),
                datasets: [{ label: "Words/Section", data: data.chapter_stats.slice(0, 30).map(c => c.word_count), borderColor: "#3b82f6", backgroundColor: "rgba(59,130,246,0.08)", fill: true, tension: 0.3, pointRadius: 2 }]
            },
            options: { ...chartDefaults, plugins: { legend: { display: true, labels: { color: "#94a3b8" } } }, scales: { x: { ticks: darkTick, grid: darkGrid }, y: { ticks: darkTick, grid: darkGrid } } }
        });

    } catch (e) {
        container.innerHTML = `<div style="color: var(--accent-rose); padding: 1rem;">Failed to load statistics: ${e.message}</div>`;
    }
}

// ── 2. Word Frequency & TF-IDF ────────────────────────────────────────────────
async function loadFrequency() {
    const tableBody = document.getElementById("freq-table-body");
    tableBody.innerHTML = `<tr><td colspan="9" style="text-align:center; padding: 2rem;"><span class="loading-spinner"></span> Loading frequencies...</td></tr>`;

    const filterStopwords = document.getElementById("freq-stopwords-toggle")?.checked ?? true;
    const posFilter = document.getElementById("freq-pos-filter")?.value ?? "ALL";
    const searchQuery = document.getElementById("freq-search-input")?.value ?? "";

    try {
        const data = await apiFetch(`/api/frequency?book_id=${currentBookId}&filter_stopwords=${filterStopwords}&pos_filter=${posFilter}&search_query=${encodeURIComponent(searchQuery)}&limit=300`);

        document.getElementById("freq-total-count").textContent = `${data.unique_filtered_words.toLocaleString()} words found`;

        if (data.frequencies.length === 0) {
            tableBody.innerHTML = `<tr><td colspan="9" style="text-align:center; padding: 2rem; color: var(--text-muted);">No matching words found.</td></tr>`;
            return;
        }

        tableBody.innerHTML = data.frequencies.map(f => `
            <tr>
                <td style="font-weight: 600; color: var(--text-muted);">${f.rank}</td>
                <td><a href="javascript:void(0)" onclick="openWordProfile('${f.word}')" style="color: var(--accent-gold); font-weight: 600; text-decoration: none;">${f.word}</a></td>
                <td style="color: var(--text-secondary);">${f.lemma}</td>
                <td><span class="badge badge-${f.pos.toLowerCase()}">${f.pos}</span></td>
                <td style="font-weight: 700;">${f.count.toLocaleString()}</td>
                <td>${f.tf_percentage}%</td>
                <td>${f.relative_frequency}</td>
                <td>${f.document_frequency} / ${data.total_chapters}</td>
                <td style="color: var(--accent-emerald); font-weight: 600;">${f.tfidf}</td>
            </tr>`).join("");
    } catch (e) {
        tableBody.innerHTML = `<tr><td colspan="9" style="color: var(--accent-rose); padding: 1rem;">Error: ${e.message}</td></tr>`;
    }
}

// ── 3. Word Cloud ─────────────────────────────────────────────────────────────
async function loadWordCloud() {
    const container = document.getElementById("wordcloud-display");
    container.innerHTML = `<div style="text-align:center; padding: 3rem;"><span class="loading-spinner"></span> Generating Word Cloud...</div>`;

    try {
        const data = await apiFetch(`/api/wordcloud?book_id=${currentBookId}&max_words=120`);
        if (data.image_base64) {
            container.innerHTML = `<div style="text-align: center;"><img src="${data.image_base64}" alt="Word Cloud" style="max-width: 100%; border-radius: 8px; box-shadow: 0 8px 24px rgba(0,0,0,0.5);" /></div>`;
        } else {
            container.innerHTML = `<div style="display: flex; flex-wrap: wrap; gap: 0.75rem; align-items: center; justify-content: center; padding: 2rem;">
                ${data.words.map(w => `<span onclick="openWordProfile('${w.text}')" style="font-size: ${w.size}px; color: hsl(${Math.random()*40+35}, 90%, 65%); cursor: pointer; transition: transform 0.2s;" title="${w.text}: ${w.count} times">${w.text}</span>`).join("")}</div>`;
        }
    } catch (e) {
        container.innerHTML = `<div style="color: var(--accent-rose); padding: 1rem;">Failed to generate word cloud: ${e.message}</div>`;
    }
}

// ── 4. Charts & Trends ────────────────────────────────────────────────────────
async function loadCharts() {
    try {
        const [freqData, pausesData] = await Promise.all([
            apiFetch(`/api/frequency?book_id=${currentBookId}&filter_stopwords=true&limit=15`),
            apiFetch(`/api/pause-marks?book_id=${currentBookId}`)
        ]);

        const darkTick = { color: "#94a3b8" };
        const darkGrid = { color: "rgba(51,65,85,0.6)" };

        const topWordsCtx = document.getElementById("chart-top-words").getContext("2d");
        if (chartInstances.topWords) chartInstances.topWords.destroy();
        chartInstances.topWords = new Chart(topWordsCtx, {
            type: "bar",
            data: { labels: freqData.frequencies.map(f => f.word), datasets: [{ label: "Occurrences", data: freqData.frequencies.map(f => f.count), backgroundColor: "rgba(245,158,11,0.8)", borderRadius: 4 }] },
            options: { responsive: true, maintainAspectRatio: false, scales: { x: { ticks: darkTick, grid: darkGrid }, y: { ticks: darkTick, grid: darkGrid } }, plugins: { legend: { labels: { color: "#94a3b8" } } } }
        });

        const posCtx = document.getElementById("chart-pos-dist").getContext("2d");
        if (chartInstances.posDist) chartInstances.posDist.destroy();
        chartInstances.posDist = new Chart(posCtx, {
            type: "doughnut",
            data: { labels: freqData.pos_distribution.map(p => p.pos), datasets: [{ data: freqData.pos_distribution.map(p => p.count), backgroundColor: ["#3b82f6","#10b981","#f59e0b","#8b5cf6","#ec4899","#64748b","#14b8a6"] }] },
            options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { labels: { color: "#94a3b8" } } } }
        });

        const radarCtx = document.getElementById("chart-rhetoric").getContext("2d");
        if (chartInstances.rhetoric) chartInstances.rhetoric.destroy();
        chartInstances.rhetoric = new Chart(radarCtx, {
            type: "radar",
            data: { labels: pausesData.marks_breakdown.map(m => m.mark.split(" ")[0]), datasets: [{ label: "Marks Density (per 1k words)", data: pausesData.marks_breakdown.map(m => m.density_per_1000_words), borderColor: "#ec4899", backgroundColor: "rgba(236,72,153,0.15)", pointBackgroundColor: "#ec4899" }] },
            options: { responsive: true, maintainAspectRatio: false, scales: { r: { ticks: { color: "#64748b", backdropColor: "transparent" }, grid: { color: "rgba(51,65,85,0.6)" }, pointLabels: { color: "#94a3b8" } } }, plugins: { legend: { labels: { color: "#94a3b8" } } } }
        });
    } catch (e) { console.error("Charts loading error:", e); }
}

// ── 5. N-Grams ────────────────────────────────────────────────────────────────
async function loadNgrams() {
    const container = document.getElementById("ngrams-results");
    container.innerHTML = `<tr><td colspan="4" style="text-align:center; padding: 2rem;"><span class="loading-spinner"></span></td></tr>`;

    const n = document.getElementById("ngram-n-select")?.value || 3;
    const filterStop = document.getElementById("ngram-stop-toggle")?.checked ?? false;
    const minCount = document.getElementById("ngram-min-count")?.value || 3;
    const search = document.getElementById("ngram-search")?.value || "";

    try {
        const data = await apiFetch(`/api/ngrams?book_id=${currentBookId}&n=${n}&filter_stopwords=${filterStop}&min_count=${minCount}&search_query=${encodeURIComponent(search)}&limit=150`);

        if (data.results.length === 0) {
            container.innerHTML = `<tr><td colspan="4" style="text-align:center; padding: 2rem; color: var(--text-muted);">No n-grams matched.</td></tr>`;
            return;
        }
        container.innerHTML = data.results.map((item, idx) => `
            <tr>
                <td style="font-weight: 600; color: var(--text-muted);">${idx + 1}</td>
                <td style="font-weight: 700; color: var(--accent-gold);">${item.ngram}</td>
                <td><strong style="color: var(--text-primary);">${item.count}</strong></td>
                <td style="color: var(--text-secondary); font-size: 0.8rem;">${item.sample_contexts.map(ctx => `<div style="margin-bottom: 2px;">•&nbsp;…${ctx}…</div>`).join("")}</td>
            </tr>`).join("");
    } catch (e) { container.innerHTML = `<tr><td colspan="4" style="color: var(--accent-rose);">Error: ${e.message}</td></tr>`; }
}

// ── 6. PoS Patterns ───────────────────────────────────────────────────────────
async function loadPosPatterns() {
    const container = document.getElementById("pos-patterns-results");
    container.innerHTML = `<tr><td colspan="4" style="text-align:center; padding: 2rem;"><span class="loading-spinner"></span></td></tr>`;
    const patLen = document.getElementById("pos-pattern-length")?.value || 2;

    try {
        const data = await apiFetch(`/api/pos-patterns?book_id=${currentBookId}&pattern_length=${patLen}&limit=50`);
        container.innerHTML = data.results.map((r, idx) => `
            <tr>
                <td style="font-weight: 600; color: var(--text-muted);">${idx + 1}</td>
                <td><span style="background: rgba(59,130,246,0.2); color: #60a5fa; padding: 3px 8px; border-radius: 4px; font-weight: 700; font-family: monospace;">${r.pattern}</span></td>
                <td style="font-weight: 700;">${r.count.toLocaleString()} (${r.percentage}%)</td>
                <td style="color: var(--text-secondary); font-family: monospace; font-size: 0.8rem;">${r.example}</td>
            </tr>`).join("");
    } catch (e) { container.innerHTML = `<tr><td colspan="4" style="color: var(--accent-rose);">Error: ${e.message}</td></tr>`; }
}

// ── 7. PoS Query ──────────────────────────────────────────────────────────────
async function loadPosQuery() {
    const container = document.getElementById("pos-query-results");
    const query = document.getElementById("pos-query-input")?.value || "ADJ NOUN";
    container.innerHTML = `<div style="text-align:center; padding: 2rem;"><span class="loading-spinner"></span></div>`;

    try {
        const data = await apiFetch(`/api/pos-query?book_id=${currentBookId}&query=${encodeURIComponent(query)}&limit=80`);
        if (data.matches.length === 0) {
            container.innerHTML = `<div style="text-align:center; padding: 2rem; color: var(--text-muted);">No verses matching POS query "${data.query}". Try "ADJ NOUN" or "PRON VERB ADV".</div>`;
            return;
        }
        container.innerHTML = `
            <div style="margin-bottom: 1rem; color: var(--text-secondary);">Found <strong>${data.matches_count}</strong> matching passages for sequence <code>${data.query}</code>:</div>
            <div style="display: flex; flex-direction: column; gap: 0.75rem;">
                ${data.matches.map(m => `
                    <div class="card" style="margin-bottom: 0;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                            <span style="font-size: 0.75rem; color: var(--accent-gold); font-weight: 600;">${m.chapter_title} (Verse ${m.verse_id})</span>
                            <span style="font-size: 0.75rem; color: var(--text-muted); font-family: monospace;">Match: ${m.matched_words}</span>
                        </div>
                        <div style="font-size: 0.9rem; line-height: 1.6;">${m.full_verse}</div>
                    </div>`).join("")}
            </div>`;
    } catch (e) { container.innerHTML = `<div style="color: var(--accent-rose);">Error: ${e.message}</div>`; }
}

// ── 8. Repeated Verses ────────────────────────────────────────────────────────
async function loadRepeatedVerses() {
    const exactC = document.getElementById("exact-repeats-container");
    const nearC = document.getElementById("near-repeats-container");
    exactC.innerHTML = nearC.innerHTML = `<div style="text-align:center; padding: 2rem;"><span class="loading-spinner"></span></div>`;

    try {
        const data = await apiFetch(`/api/repeated-verses?book_id=${currentBookId}&min_similarity=0.8&limit=50`);

        exactC.innerHTML = data.exact_repeats.length === 0
            ? `<div style="color: var(--text-muted); padding: 1rem;">No exact multi-occurrence verses found.</div>`
            : data.exact_repeats.map(r => `
                <div class="card" style="border-left: 3px solid var(--accent-gold);">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                        <span class="badge" style="background: rgba(245,158,11,0.2); color: var(--accent-gold);">Repeated ${r.repetition_count}×</span>
                        ${bookmarkButton(r.text, "Repeated verse")}
                    </div>
                    <p style="font-size: 0.95rem; margin-bottom: 0.5rem;">${r.text}</p>
                    <div style="font-size: 0.75rem; color: var(--text-muted);">Occurs in: ${r.occurrences.map(o => `${o.chapter} (#${o.verse_id})`).join(", ")}</div>
                </div>`).join("");

        nearC.innerHTML = data.near_repeats.length === 0
            ? `<div style="color: var(--text-muted); padding: 1rem;">No near-duplicate verses found.</div>`
            : data.near_repeats.map(nr => `
                <div class="card" style="border-left: 3px solid var(--accent-purple);">
                    <span class="badge" style="background: rgba(139,92,246,0.2); color: #a78bfa;">${nr.similarity}% Jaccard Similarity</span>
                    <div style="font-size: 0.875rem; margin: 0.5rem 0;"><strong>A (${nr.verse_a.chapter}):</strong> ${nr.verse_a.text}</div>
                    <div style="font-size: 0.875rem; color: var(--text-secondary);"><strong>B (${nr.verse_b.chapter}):</strong> ${nr.verse_b.text}</div>
                </div>`).join("");
    } catch (e) { exactC.innerHTML = `<div style="color: var(--accent-rose);">Error: ${e.message}</div>`; }
}

// ── 9. Repeated Phrases ───────────────────────────────────────────────────────
async function loadRepeatedPhrases() {
    const container = document.getElementById("repeated-phrases-results");
    container.innerHTML = `<tr><td colspan="4" style="text-align:center; padding: 2rem;"><span class="loading-spinner"></span></td></tr>`;

    try {
        const data = await apiFetch(`/api/repeated-phrases?book_id=${currentBookId}&min_phrase_len=3&max_phrase_len=10&min_occurrences=3&limit=100`);

        if (data.phrases.length === 0) {
            container.innerHTML = `<tr><td colspan="4" style="text-align:center; padding: 2rem; color: var(--text-muted);">No repeating phrases found.</td></tr>`;
            return;
        }
        container.innerHTML = data.phrases.map((p, idx) => `
            <tr>
                <td style="font-weight: 600; color: var(--text-muted);">${idx + 1}</td>
                <td style="font-weight: 700; color: var(--accent-gold);">${p.phrase}</td>
                <td><span class="badge" style="background: rgba(16,185,129,0.2); color: #34d399;">${p.word_count} words</span></td>
                <td><strong>${p.occurrences}</strong> times (${p.relative_freq} per 10k)</td>
            </tr>`).join("");
    } catch (e) { container.innerHTML = `<tr><td colspan="4" style="color: var(--accent-rose);">Error: ${e.message}</td></tr>`; }
}

// ── 10. Ontology Data & Graphs ────────────────────────────────────────────────
async function loadOntology() {
    const conceptCards = document.getElementById("ontology-concept-cards");
    conceptCards.innerHTML = `<div style="text-align:center; padding: 2rem;"><span class="loading-spinner"></span> Loading Philosophical Ontology...</div>`;

    try {
        const data = await apiFetch(`/api/ontology?book_id=${currentBookId}`);

        conceptCards.innerHTML = data.concepts.map(c => `
            <div class="card" style="border-top: 3px solid ${c.color}; margin-bottom: 0;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                    <div style="font-weight: 700; font-size: 1.05rem;">${c.name}</div>
                    <span class="badge" style="background-color: ${c.color}22; color: ${c.color};">${c.frequency} mentions</span>
                </div>
                <div style="font-size: 0.7rem; color: var(--text-muted); margin-bottom: 0.5rem; text-transform: uppercase; letter-spacing: 0.05em;">${c.category}</div>
                <p style="font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 0.75rem;">${c.description}</p>
                ${c.sample_passages.length > 0 ? `<div style="background: var(--bg-card); padding: 0.5rem 0.75rem; border-radius: 6px; font-size: 0.75rem; color: var(--text-muted);">
                    <em>"${c.sample_passages[0].text.slice(0, 140)}…"</em>
                    ${bookmarkButton(c.sample_passages[0].text, c.name + " concept passage")}
                </div>` : ""}
            </div>`).join("");

        const graphContainer = document.getElementById("network-graph-container");
        if (typeof vis !== "undefined" && graphContainer) {
            if (networkInstance) { networkInstance.destroy(); networkInstance = null; }
            const visNodes = new vis.DataSet(data.graph.nodes.map(n => ({
                id: n.id, label: n.label, value: n.value,
                color: { background: n.color, border: "#ffffff", highlight: { background: "#fbbf24", border: "#ffffff" } },
                font: { color: "#ffffff", size: 13, face: "Inter" }
            })));
            const visEdges = new vis.DataSet(data.graph.edges.map(e => ({
                from: e.from, to: e.to, value: e.value,
                color: { color: "rgba(148,163,184,0.35)", highlight: "#fbbf24" }
            })));
            networkInstance = new vis.Network(graphContainer, { nodes: visNodes, edges: visEdges }, {
                nodes: { shape: "dot", scaling: { min: 14, max: 38 } },
                edges: { smooth: true },
                physics: { stabilization: true, barnesHut: { gravitationalConstant: -3000, springLength: 120 } }
            });
        }
    } catch (e) { conceptCards.innerHTML = `<div style="color: var(--accent-rose);">Error loading ontology: ${e.message}</div>`; }
}

// ── 11. Word Information ──────────────────────────────────────────────────────
async function loadWordInfo(targetWord) {
    const word = targetWord || document.getElementById("word-info-input")?.value || "power";
    const container = document.getElementById("word-info-profile-container");
    container.innerHTML = `<div style="text-align:center; padding: 2rem;"><span class="loading-spinner"></span></div>`;

    try {
        const data = await apiFetch(`/api/word-info?book_id=${currentBookId}&word=${encodeURIComponent(word)}`);

        if (!data.found) {
            container.innerHTML = `<div class="card" style="color: var(--accent-rose);">${data.message}</div>`;
            return;
        }

        container.innerHTML = `
            <div class="stat-grid">
                <div class="stat-card">
                    <div class="stat-label">Word &amp; Lemma</div>
                    <div class="stat-value" style="color: var(--accent-gold); text-transform: capitalize;">${data.word}</div>
                    <div class="stat-sub">Lemma: ${data.lemma} | Syllables: ${data.syllables}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Corpus Rank</div>
                    <div class="stat-value">#${data.rank}</div>
                    <div class="stat-sub">${data.total_occurrences} total occurrences</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Relative Frequency</div>
                    <div class="stat-value" style="color: var(--accent-emerald);">${data.relative_frequency_per_10k}</div>
                    <div class="stat-sub">Per 10,000 words (${data.tf_percentage}%)</div>
                </div>
            </div>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); gap: 1.5rem; margin-bottom: 1.5rem;">
                <div class="card">
                    <div class="card-header"><div class="card-title">Top Collocates (±4 words)</div></div>
                    <div style="display: flex; flex-wrap: wrap; gap: 0.5rem;">
                        ${data.top_collocates.map(c => `<span class="badge" onclick="openWordProfile('${c.word}')" style="background: var(--bg-card); color: var(--text-primary); border: 1px solid var(--border-color); padding: 0.35rem 0.6rem; cursor: pointer;">${c.word} (${c.co_occurrences})</span>`).join("")}
                    </div>
                </div>
                <div class="card">
                    <div class="card-header"><div class="card-title">POS Tag Instances</div></div>
                    <div style="display: flex; gap: 0.5rem; flex-wrap: wrap;">
                        ${data.pos_breakdown.map(p => `<span class="badge badge-${p.pos.toLowerCase()}" style="padding: 0.4rem 0.75rem; font-size: 0.8rem;">${p.pos}: ${p.count}</span>`).join("")}
                    </div>
                </div>
            </div>
            <div class="card">
                <div class="card-header"><div class="card-title">Sample Context Passages</div></div>
                <div style="display: flex; flex-direction: column; gap: 0.75rem;">
                    ${data.sample_verses.map(v => `
                        <div style="background: var(--bg-card); padding: 0.75rem 1rem; border-radius: 6px; border-left: 3px solid var(--accent-gold);">
                            <div style="font-size: 0.75rem; color: var(--accent-gold); font-weight: 600; margin-bottom: 0.25rem;">
                                ${v.chapter} (Verse #${v.verse_id})
                                ${bookmarkButton(v.text, v.chapter)}
                            </div>
                            <div style="font-size: 0.9rem; line-height: 1.5;">${v.highlighted_html}</div>
                        </div>`).join("")}
                </div>
            </div>`;
    } catch (e) { container.innerHTML = `<div style="color: var(--accent-rose);">Error: ${e.message}</div>`; }
}

function openWordProfile(word) {
    document.getElementById("word-info-input").value = word;
    activateTab("tab-word-info");
    loadWordInfo(word);
}

// ── 12. Collocations ──────────────────────────────────────────────────────────
async function loadCollocation() {
    const tableBody = document.getElementById("collocation-table-body");
    tableBody.innerHTML = `<tr><td colspan="7" style="text-align:center; padding: 2rem;"><span class="loading-spinner"></span></td></tr>`;

    const windowSize = document.getElementById("colloc-window-select")?.value || 4;
    const minCount = document.getElementById("colloc-min-count")?.value || 3;
    const targetWord = document.getElementById("colloc-target-word")?.value || "";

    try {
        const data = await apiFetch(`/api/collocation?book_id=${currentBookId}&window_size=${windowSize}&min_cooccurrences=${minCount}&target_word=${encodeURIComponent(targetWord)}&limit=150`);

        if (data.results.length === 0) {
            tableBody.innerHTML = `<tr><td colspan="7" style="text-align:center; padding: 2rem; color: var(--text-muted);">No collocations found.</td></tr>`;
            return;
        }
        tableBody.innerHTML = data.results.map((c, idx) => `
            <tr>
                <td style="font-weight: 600; color: var(--text-muted);">${idx + 1}</td>
                <td style="font-weight: 700; color: var(--accent-gold);">${c.pair}</td>
                <td><strong>${c.cooccurrences}</strong></td>
                <td>${c.freq_w1}</td>
                <td>${c.freq_w2}</td>
                <td style="color: var(--accent-emerald); font-weight: 700;">${c.pmi}</td>
                <td style="color: var(--accent-blue);">${c.t_score}</td>
            </tr>`).join("");
    } catch (e) { tableBody.innerHTML = `<tr><td colspan="7" style="color: var(--accent-rose);">Error: ${e.message}</td></tr>`; }
}

// ── 13. Concordance (KWIC) ────────────────────────────────────────────────────
async function loadConcordance() {
    const container = document.getElementById("kwic-results-container");
    const keyword = document.getElementById("kwic-search-input")?.value || "zarathustra";
    const sortBy = document.getElementById("kwic-sort-select")?.value || "order";
    const contextWords = document.getElementById("kwic-context-words")?.value || 7;
    container.innerHTML = `<div style="text-align:center; padding: 2rem;"><span class="loading-spinner"></span></div>`;

    try {
        const data = await apiFetch(`/api/concordance?book_id=${currentBookId}&keyword=${encodeURIComponent(keyword)}&context_words=${contextWords}&sort_by=${sortBy}&limit=250`);
        document.getElementById("kwic-match-count").textContent = `${data.total_matches} matches found`;

        if (data.lines.length === 0) {
            container.innerHTML = `<div style="text-align:center; padding: 2rem; color: var(--text-muted);">No concordance lines found for "${keyword}".</div>`;
            return;
        }
        container.innerHTML = data.lines.map(line => `
            <div class="kwic-line">
                <div class="kwic-left">${line.left_context}</div>
                <div class="kwic-keyword">${line.keyword}</div>
                <div class="kwic-right">${line.right_context}</div>
                <div class="kwic-chap">${line.chapter_title}</div>
            </div>`).join("");
    } catch (e) { container.innerHTML = `<div style="color: var(--accent-rose); padding:1rem;">Error: ${e.message}</div>`; }
}

// ── 14. Pause Marks & Rhetorical Cadence ─────────────────────────────────────
async function loadPauseMarks() {
    const container = document.getElementById("pause-marks-container");
    container.innerHTML = `<div style="text-align:center; padding: 2rem;"><span class="loading-spinner"></span></div>`;

    try {
        const data = await apiFetch(`/api/pause-marks?book_id=${currentBookId}`);
        container.innerHTML = `
            <div class="stat-grid">
                <div class="stat-card">
                    <div class="stat-label">Total Punctuation Marks</div>
                    <div class="stat-value" style="color: var(--accent-rose);">${data.total_punctuation_marks.toLocaleString()}</div>
                    <div class="stat-sub">Across ${data.total_words.toLocaleString()} words</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Impassioned Proclamation Index</div>
                    <div class="stat-value" style="color: var(--accent-gold);">${data.rhetorical_indices.impassioned_proclamation_index}</div>
                    <div class="stat-sub">Density of Em-Dashes &amp; Exclamations</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Interrogative Index</div>
                    <div class="stat-value" style="color: var(--accent-blue);">${data.rhetorical_indices.dialectical_interrogation_index}</div>
                    <div class="stat-sub">Questions per 1,000 words</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Aphoristic Clause Linking</div>
                    <div class="stat-value" style="color: var(--accent-purple);">${data.rhetorical_indices.aphoristic_clause_linking_index}</div>
                    <div class="stat-sub">Semicolons per 1,000 words</div>
                </div>
            </div>
            <div class="card">
                <div class="card-header"><div class="card-title">Punctuation &amp; Pause Marks Breakdown</div></div>
                <div class="table-responsive">
                    <table class="data-table">
                        <thead><tr><th>Pause / Rhetorical Mark</th><th>Total Count</th><th>Density (per 1,000 words)</th></tr></thead>
                        <tbody>${data.marks_breakdown.map(m => `<tr><td style="font-weight: 700;">${m.mark}</td><td>${m.count.toLocaleString()}</td><td style="font-weight: 600; color: var(--accent-gold);">${m.density_per_1000_words}</td></tr>`).join("")}</tbody>
                    </table>
                </div>
            </div>`;
    } catch (e) { container.innerHTML = `<div style="color: var(--accent-rose);">Error: ${e.message}</div>`; }
}

// ── 15. Word Similarity ───────────────────────────────────────────────────────
async function loadWordSimilarity() {
    const container = document.getElementById("sim-results-container");
    const word1 = document.getElementById("sim-word1-input")?.value || "power";
    const word2 = document.getElementById("sim-word2-input")?.value || "";
    container.innerHTML = `<div style="text-align:center; padding: 2rem;"><span class="loading-spinner"></span> Computing semantic vector similarities...</div>`;

    try {
        let url = `/api/similarity?book_id=${currentBookId}&word1=${encodeURIComponent(word1)}&top_k=15`;
        if (word2.trim()) url += `&word2=${encodeURIComponent(word2.trim())}`;
        const data = await apiFetch(url);

        if (data.error) { container.innerHTML = `<div class="card" style="color: var(--accent-rose);">${data.error}</div>`; return; }

        if (data.mode === "pairwise") {
            container.innerHTML = `
                <div class="card" style="text-align: center; padding: 2rem;">
                    <div style="font-size: 1.1rem; color: var(--text-secondary); margin-bottom: 0.5rem;">Semantic Cosine Similarity between:</div>
                    <div style="font-size: 1.5rem; font-weight: 700; margin-bottom: 1rem;">
                        <span style="color: var(--accent-gold);">${data.word1}</span> ↔ <span style="color: var(--accent-blue);">${data.word2}</span>
                    </div>
                    <div style="font-size: 3rem; font-weight: 800; color: var(--accent-emerald);">${data.percentage_similarity}%</div>
                    <div style="font-size: 0.85rem; color: var(--text-muted);">Cosine Score: ${data.cosine_similarity}</div>
                </div>`;
        } else {
            container.innerHTML = `
                <div style="margin-bottom: 1rem; color: var(--text-secondary);">Top semantically related words for <strong style="color: var(--accent-gold);">"${data.target_word}"</strong>:</div>
                <div class="table-responsive">
                    <table class="data-table">
                        <thead><tr><th>#</th><th>Semantically Related Word</th><th>Similarity Score</th><th>Cosine Metric</th><th>Occurrences</th></tr></thead>
                        <tbody>${data.similar_words.map((sw, idx) => `
                            <tr>
                                <td style="color: var(--text-muted);">${idx + 1}</td>
                                <td><a href="javascript:void(0)" onclick="openWordProfile('${sw.word}')" style="color: var(--accent-gold); font-weight: 700; text-decoration: none;">${sw.word}</a></td>
                                <td>
                                    <div style="display: flex; align-items: center; gap: 0.5rem;">
                                        <div style="background: rgba(16,185,129,0.2); height: 8px; border-radius: 4px; width: ${sw.similarity_score * 1.5}px; max-width: 120px; overflow: hidden;">
                                            <div style="background: #10b981; height: 8px; border-radius: 4px; width: 100%;"></div>
                                        </div>
                                        <span style="font-weight: 700; color: #10b981;">${sw.similarity_score}%</span>
                                    </div>
                                </td>
                                <td style="font-family: monospace;">${sw.similarity}</td>
                                <td>${sw.frequency}</td>
                            </tr>`).join("")}
                        </tbody>
                    </table>
                </div>`;
        }
    } catch (e) { container.innerHTML = `<div style="color: var(--accent-rose);">Error: ${e.message}</div>`; }
}

// ── 16. Sentiment Analysis (NEW) ──────────────────────────────────────────────
async function loadSentiment() {
    const container = document.getElementById("sentiment-container");
    container.innerHTML = skeletonStats(4) + `<div class="card skeleton" style="height: 300px;"></div>`;

    try {
        const data = await apiFetch(`/api/sentiment?book_id=${currentBookId}`);
        if (data.error) { container.innerHTML = `<div class="card" style="color: var(--accent-rose);">${data.error}</div>`; return; }

        const sentColor = s => s === "positive" ? "var(--accent-emerald)" : s === "negative" ? "var(--accent-rose)" : "var(--text-muted)";
        const sentEmoji = s => s === "positive" ? "😊" : s === "negative" ? "😔" : "😐";

        container.innerHTML = `
            <div class="stat-grid">
                <div class="stat-card">
                    <div class="stat-label">Overall Sentiment</div>
                    <div class="stat-value" style="color: ${sentColor(data.overall_sentiment)};">${sentEmoji(data.overall_sentiment)} ${data.overall_sentiment}</div>
                    <div class="stat-sub">Average compound: ${data.average_compound}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Positive Chapters</div>
                    <div class="stat-value" style="color: var(--accent-emerald);">${data.positive_chapters}</div>
                    <div class="stat-sub">Out of ${data.total_chapters_analyzed} total</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Negative Chapters</div>
                    <div class="stat-value" style="color: var(--accent-rose);">${data.negative_chapters}</div>
                    <div class="stat-sub">${data.neutral_chapters} neutral chapters</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Most Positive Chapter</div>
                    <div class="stat-value" style="color: var(--accent-emerald); font-size: 1.1rem;">${data.most_positive_chapter?.compound?.toFixed(3)}</div>
                    <div class="stat-sub">${(data.most_positive_chapter?.title || "").slice(0, 40)}</div>
                </div>
            </div>

            <div class="card">
                <div class="card-header"><div class="card-title">😊↔😔 Emotional Trajectory Across Chapters</div></div>
                <div style="display: flex; flex-direction: column; gap: 0.4rem; padding: 0.5rem 0;">
                    ${data.chapter_arcs.map(arc => {
                        const pct = Math.max(0, Math.min(100, (arc.compound + 1) / 2 * 100));
                        return `<div class="sentiment-bar-container">
                            <div class="sentiment-bar-label" title="${arc.title}">${arc.title}</div>
                            <div class="sentiment-bar-track">
                                <div class="sentiment-bar-fill ${arc.sentiment}" style="width: ${pct}%;"></div>
                            </div>
                            <div class="sentiment-bar-value" style="color: ${sentColor(arc.sentiment)};">${arc.compound.toFixed(3)}</div>
                        </div>`;
                    }).join("")}
                </div>
            </div>

            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(380px, 1fr)); gap: 1.5rem;">
                <div class="card">
                    <div class="card-header"><div class="card-title">🔆 Most Positive Passages</div></div>
                    <div style="display: flex; flex-direction: column; gap: 0.5rem;">
                        ${(data.top_positive_verses || []).map(v => `
                            <div style="background: var(--bg-card); padding: 0.75rem; border-radius: 6px; border-left: 3px solid var(--accent-emerald);">
                                <div style="font-size: 0.7rem; color: var(--accent-emerald); font-weight: 600; margin-bottom: 0.25rem;">${v.chapter} — compound: ${v.compound}</div>
                                <div style="font-size: 0.85rem; line-height: 1.5;">${escapeHtml(v.text.slice(0, 180))}…</div>
                                ${bookmarkButton(v.text, v.chapter + " – positive")}
                            </div>`).join("")}
                    </div>
                </div>
                <div class="card">
                    <div class="card-header"><div class="card-title">🌑 Most Negative Passages</div></div>
                    <div style="display: flex; flex-direction: column; gap: 0.5rem;">
                        ${(data.top_negative_verses || []).map(v => `
                            <div style="background: var(--bg-card); padding: 0.75rem; border-radius: 6px; border-left: 3px solid var(--accent-rose);">
                                <div style="font-size: 0.7rem; color: var(--accent-rose); font-weight: 600; margin-bottom: 0.25rem;">${v.chapter} — compound: ${v.compound}</div>
                                <div style="font-size: 0.85rem; line-height: 1.5;">${escapeHtml(v.text.slice(0, 180))}…</div>
                                ${bookmarkButton(v.text, v.chapter + " – negative")}
                            </div>`).join("")}
                    </div>
                </div>
            </div>`;
    } catch (e) { container.innerHTML = `<div style="color: var(--accent-rose);">Error: ${e.message}</div>`; }
}

// ── 17. Compare Books (NEW) ───────────────────────────────────────────────────
async function loadCompare() {
    const container = document.getElementById("compare-results-container");
    const bookA = document.getElementById("compare-book-a")?.value;
    const bookB = document.getElementById("compare-book-b")?.value;
    if (bookA === bookB) { container.innerHTML = `<div class="card" style="color: var(--text-muted);">Please select two different books to compare.</div>`; return; }

    container.innerHTML = skeletonStats(3) + `<div class="card skeleton" style="height: 200px;"></div>`;

    try {
        const data = await apiFetch(`/api/compare?book_id_a=${bookA}&book_id_b=${bookB}`);
        const v = data.vocabulary;
        const r = data.readability;

        const titleA = data.book_a.title;
        const titleB = data.book_b.title;

        const compareRow = (label, a, b) => `
            <div class="compare-row">
                <div class="compare-label">${label}</div>
                <div class="compare-a">${a}</div>
                <div class="compare-b">${b}</div>
            </div>`;

        container.innerHTML = `
            <div class="stat-grid">
                <div class="stat-card">
                    <div class="stat-label">Vocabulary Similarity</div>
                    <div class="stat-value" style="color: var(--accent-purple);">${v.jaccard_similarity_pct}%</div>
                    <div class="stat-sub">Jaccard index on content words</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Shared Vocabulary</div>
                    <div class="stat-value">${v.shared_vocab_size.toLocaleString()}</div>
                    <div class="stat-sub">Words in both texts</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Unique to ${titleA.split(" ")[0]}</div>
                    <div class="stat-value" style="color: var(--accent-gold);">${v.unique_to_a.toLocaleString()}</div>
                    <div class="stat-sub">Content words exclusive to Book A</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Unique to ${titleB.split(" ")[0]}</div>
                    <div class="stat-value" style="color: var(--accent-blue);">${v.unique_to_b.toLocaleString()}</div>
                    <div class="stat-sub">Content words exclusive to Book B</div>
                </div>
            </div>

            <div class="card">
                <div class="card-header"><div class="card-title">📊 Readability &amp; Style Comparison</div></div>
                <div class="compare-row compare-header">
                    <div>Metric</div>
                    <div style="color: var(--accent-gold);">📖 ${titleA}</div>
                    <div style="color: var(--accent-blue);">📖 ${titleB}</div>
                </div>
                ${compareRow("Total Words", r.total_words_a?.toLocaleString(), r.total_words_b?.toLocaleString())}
                ${compareRow("Unique Words", r.unique_words_a?.toLocaleString(), r.unique_words_b?.toLocaleString())}
                ${compareRow("Type-Token Ratio", r.ttr_a + "%", r.ttr_b + "%")}
                ${compareRow("Flesch Reading Ease", r.flesch_ease_a, r.flesch_ease_b)}
                ${compareRow("Flesch-Kincaid Grade", r.fk_grade_a, r.fk_grade_b)}
                ${compareRow("Avg Sentence Length", r.avg_sentence_len_a + " words", r.avg_sentence_len_b + " words")}
                ${compareRow("Lexical Density", r.lexical_density_a + "%", r.lexical_density_b + "%")}
            </div>

            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(380px, 1fr)); gap: 1.5rem;">
                <div class="card">
                    <div class="card-header"><div class="card-title" style="color: var(--accent-gold);">🔤 Words Unique to "${titleA}"</div></div>
                    <div style="display: flex; flex-wrap: wrap; gap: 0.4rem;">
                        ${v.top_unique_a.map(w => `<span class="badge" style="background: rgba(245,158,11,0.15); color: var(--accent-gold); border: 1px solid rgba(245,158,11,0.3);" title="${w.freq_per_10k}/10k">${w.word}</span>`).join("")}
                    </div>
                </div>
                <div class="card">
                    <div class="card-header"><div class="card-title" style="color: var(--accent-blue);">🔤 Words Unique to "${titleB}"</div></div>
                    <div style="display: flex; flex-wrap: wrap; gap: 0.4rem;">
                        ${v.top_unique_b.map(w => `<span class="badge" style="background: rgba(59,130,246,0.15); color: var(--accent-blue); border: 1px solid rgba(59,130,246,0.3);" title="${w.freq_per_10k}/10k">${w.word}</span>`).join("")}
                    </div>
                </div>
            </div>

            <div class="card">
                <div class="card-header"><div class="card-title">🕸️ Philosophical Concept Density Comparison</div></div>
                <div style="display: flex; flex-direction: column; gap: 0.5rem;">
                    ${data.concepts.slice(0, 12).map(c => {
                        const maxVal = Math.max(c.density_a, c.density_b, 1);
                        return `<div style="display: grid; grid-template-columns: 180px 1fr 1fr; gap: 0.5rem; align-items: center; font-size: 0.82rem;">
                            <div style="color: var(--text-muted); white-space: nowrap; overflow: hidden; text-overflow: ellipsis;" title="${c.concept}">${c.concept}</div>
                            <div style="display: flex; align-items: center; gap: 0.4rem;">
                                <div style="flex: 1; background: var(--bg-card); height: 8px; border-radius: 4px; overflow: hidden;">
                                    <div style="background: var(--accent-gold); height: 100%; width: ${c.density_a / maxVal * 100}%; border-radius: 4px;"></div>
                                </div>
                                <span style="color: var(--accent-gold); width: 38px; text-align: right;">${c.density_a}</span>
                            </div>
                            <div style="display: flex; align-items: center; gap: 0.4rem;">
                                <div style="flex: 1; background: var(--bg-card); height: 8px; border-radius: 4px; overflow: hidden;">
                                    <div style="background: var(--accent-blue); height: 100%; width: ${c.density_b / maxVal * 100}%; border-radius: 4px;"></div>
                                </div>
                                <span style="color: var(--accent-blue); width: 38px; text-align: right;">${c.density_b}</span>
                            </div>
                        </div>`;
                    }).join("")}
                    <div style="display: grid; grid-template-columns: 180px 1fr 1fr; gap: 0.5rem; font-size: 0.7rem; color: var(--text-muted); margin-top: 0.5rem; padding-top: 0.5rem; border-top: 1px solid var(--border-color);">
                        <div></div>
                        <div style="color: var(--accent-gold);">📖 ${titleA} (per 10k)</div>
                        <div style="color: var(--accent-blue);">📖 ${titleB} (per 10k)</div>
                    </div>
                </div>
            </div>`;
    } catch (e) { container.innerHTML = `<div style="color: var(--accent-rose);">Error: ${e.message}</div>`; }
}

// ── 18. Full-Text Search (NEW) ────────────────────────────────────────────────
async function loadFullTextSearch() {
    const container = document.getElementById("search-results-container");
    const phrase = document.getElementById("search-phrase-input")?.value || "";
    if (!phrase.trim()) { container.innerHTML = `<div class="card" style="color: var(--text-muted);">Enter a phrase to search.</div>`; return; }

    container.innerHTML = `<div style="text-align:center; padding: 2rem;"><span class="loading-spinner"></span> Searching…</div>`;

    try {
        const data = await apiFetch(`/api/search?book_id=${currentBookId}&phrase=${encodeURIComponent(phrase)}&limit=200`);
        document.getElementById("search-match-count").textContent = `${data.total_matches} matches`;

        if (data.results.length === 0) {
            container.innerHTML = `<div style="text-align:center; padding: 2rem; color: var(--text-muted);">No results found for "${phrase}".</div>`;
            return;
        }
        container.innerHTML = `<div style="display: flex; flex-direction: column; gap: 0.75rem;">
            ${data.results.map(r => `
                <div class="card" style="margin-bottom: 0; border-left: 3px solid var(--accent-gold);">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.4rem;">
                        <span style="font-size: 0.75rem; color: var(--accent-gold); font-weight: 600;">${r.chapter_title} (Verse #${r.verse_id})</span>
                        ${bookmarkButton(r.text, r.chapter_title)}
                    </div>
                    <div style="font-size: 0.9rem; line-height: 1.6;">${r.highlighted_html}</div>
                </div>`).join("")}
        </div>`;
    } catch (e) { container.innerHTML = `<div style="color: var(--accent-rose);">Error: ${e.message}</div>`; }
}

// ── Dataset Export ────────────────────────────────────────────────────────────
function loadDatasetView() {}
function exportDataset(format) {
    window.location.href = `/api/export?book_id=${currentBookId}&format_type=${format}`;
}
