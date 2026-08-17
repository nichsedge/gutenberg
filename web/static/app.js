// Ebook Analysis Platform Frontend Application Logic
let currentBookId = "1998";
let currentCatalog = [];
let chartInstances = {};
let networkInstance = null;

// Initialize on DOM Ready
document.addEventListener("DOMContentLoaded", () => {
    initNavigation();
    loadCatalog();
    setupEventListeners();
});

// Setup Tab Navigation
function initNavigation() {
    const navItems = document.querySelectorAll(".nav-item");
    navItems.forEach(item => {
        item.addEventListener("click", () => {
            navItems.forEach(n => n.classList.remove("active"));
            item.classList.add("active");
            const targetTab = item.getAttribute("data-tab");
            switchTab(targetTab);
        });
    });
}

function switchTab(tabId) {
    document.querySelectorAll(".tab-content").forEach(tc => tc.classList.remove("active"));
    const activeTab = document.getElementById(tabId);
    if (activeTab) {
        activeTab.classList.add("active");
        loadTabContent(tabId);
    }
}

// Load Catalog
async function loadCatalog() {
    try {
        const resp = await fetch("/api/catalog");
        const data = await resp.json();
        currentCatalog = data.catalog;
        const selector = document.getElementById("book-selector");
        selector.innerHTML = "";
        currentCatalog.forEach(b => {
            const opt = document.createElement("option");
            opt.value = b.id;
            opt.textContent = `${b.title} (${b.author})`;
            if (b.id === currentBookId) opt.selected = true;
            selector.appendChild(opt);
        });
        loadTabContent("tab-basic-stats");
    } catch (e) {
        console.error("Error loading catalog:", e);
    }
}

// Event Listeners
function setupEventListeners() {
    document.getElementById("book-selector").addEventListener("change", (e) => {
        currentBookId = e.target.value;
        const activeTab = document.querySelector(".nav-item.active").getAttribute("data-tab");
        loadTabContent(activeTab);
    });

    document.getElementById("btn-load-custom-id").addEventListener("click", async () => {
        const idInput = prompt("Enter Project Gutenberg Ebook ID (e.g. 51710 for Birth of Tragedy):");
        if (idInput && idInput.trim()) {
            const btn = document.getElementById("btn-load-custom-id");
            btn.innerHTML = `<span class="loading-spinner"></span> Loading...`;
            try {
                const formData = new FormData();
                formData.append("book_id", idInput.trim());
                const res = await fetch("/api/load-book", { method: "POST", body: formData });
                const json = await res.json();
                if (res.ok) {
                    await loadCatalog();
                    currentBookId = json.book.id;
                    document.getElementById("book-selector").value = currentBookId;
                    const activeTab = document.querySelector(".nav-item.active").getAttribute("data-tab");
                    loadTabContent(activeTab);
                } else {
                    alert("Error loading book: " + (json.detail || "Unknown error"));
                }
            } catch (err) {
                alert("Failed to load book: " + err.message);
            } finally {
                btn.innerHTML = `<span>📥</span> Load Gutenberg ID`;
            }
        }
    });

    // Concordance Search
    document.getElementById("btn-concordance-search")?.addEventListener("click", () => loadConcordance());
    document.getElementById("kwic-search-input")?.addEventListener("keyup", (e) => {
        if (e.key === "Enter") loadConcordance();
    });

    // PoS Query Search
    document.getElementById("btn-pos-query")?.addEventListener("click", () => loadPosQuery());
    document.getElementById("pos-query-input")?.addEventListener("keyup", (e) => {
        if (e.key === "Enter") loadPosQuery();
    });

    // Similarity Search
    document.getElementById("btn-sim-search")?.addEventListener("click", () => loadWordSimilarity());
    
    // Word Info Search
    document.getElementById("btn-word-info-search")?.addEventListener("click", () => {
        const query = document.getElementById("word-info-input").value;
        if (query) loadWordInfo(query);
    });

    // Frequency Filters
    document.getElementById("freq-pos-filter")?.addEventListener("change", () => loadFrequency());
    document.getElementById("freq-stopwords-toggle")?.addEventListener("change", () => loadFrequency());
    document.getElementById("freq-search-input")?.addEventListener("input", debounce(() => loadFrequency(), 300));
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Router to load specific tab content
function loadTabContent(tabId) {
    switch (tabId) {
        case "tab-basic-stats":
            loadBasicStats();
            break;
        case "tab-frequency":
            loadFrequency();
            break;
        case "tab-wordcloud":
            loadWordCloud();
            break;
        case "tab-charts":
            loadCharts();
            break;
        case "tab-ngrams":
            loadNgrams();
            break;
        case "tab-pos-patterns":
            loadPosPatterns();
            break;
        case "tab-pos-query":
            loadPosQuery();
            break;
        case "tab-repeated-verses":
            loadRepeatedVerses();
            break;
        case "tab-repeated-phrases":
            loadRepeatedPhrases();
            break;
        case "tab-ontology":
            loadOntology();
            break;
        case "tab-word-info":
            loadWordInfo();
            break;
        case "tab-collocation":
            loadCollocation();
            break;
        case "tab-concordance":
            loadConcordance();
            break;
        case "tab-pause-marks":
            loadPauseMarks();
            break;
        case "tab-similarity":
            loadWordSimilarity();
            break;
        case "tab-dataset":
            loadDatasetView();
            break;
    }
}

// 1. Basic Statistics
async function loadBasicStats() {
    const container = document.getElementById("stats-container");
    container.innerHTML = `<div style="text-align:center; padding: 2rem;"><span class="loading-spinner"></span> Loading statistics...</div>`;
    
    try {
        const res = await fetch(`/api/stats?book_id=${currentBookId}`);
        const data = await res.json();
        
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
                    <div class="stat-label">Verses & Aphorisms</div>
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

            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(450px, 1fr)); gap: 1.5rem;">
                <div class="card">
                    <div class="card-header"><div class="card-title">Word Length Distribution</div></div>
                    <div style="height: 260px;"><canvas id="wordLengthChart"></canvas></div>
                </div>
                <div class="card">
                    <div class="card-header"><div class="card-title">Chapter Progression & Density</div></div>
                    <div style="height: 260px;"><canvas id="chapterProgressionChart"></canvas></div>
                </div>
            </div>
        `;

        // Render Word Length Chart
        const wlCtx = document.getElementById("wordLengthChart").getContext("2d");
        if (chartInstances.wordLength) chartInstances.wordLength.destroy();
        chartInstances.wordLength = new Chart(wlCtx, {
            type: "bar",
            data: {
                labels: data.word_length_distribution.map(d => `${d.length} chars`),
                datasets: [{
                    label: "Word Count",
                    data: data.word_length_distribution.map(d => d.count),
                    backgroundColor: "#f59e0b",
                    borderRadius: 4
                }]
            },
            options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } }
        });

        // Render Chapter Progression Chart
        const cpCtx = document.getElementById("chapterProgressionChart").getContext("2d");
        if (chartInstances.chapterProgression) chartInstances.chapterProgression.destroy();
        chartInstances.chapterProgression = new Chart(cpCtx, {
            type: "line",
            data: {
                labels: data.chapter_stats.slice(0, 30).map(c => `Sec ${c.id}`),
                datasets: [{
                    label: "Words per Section",
                    data: data.chapter_stats.slice(0, 30).map(c => c.word_count),
                    borderColor: "#3b82f6",
                    backgroundColor: "rgba(59, 130, 246, 0.1)",
                    fill: true,
                    tension: 0.3
                }]
            },
            options: { responsive: true, maintainAspectRatio: false }
        });

    } catch (e) {
        container.innerHTML = `<div style="color: var(--accent-rose); padding: 1rem;">Failed to load statistics: ${e.message}</div>`;
    }
}

// 2. Word Frequency & TF-IDF
async function loadFrequency() {
    const tableBody = document.getElementById("freq-table-body");
    tableBody.innerHTML = `<tr><td colspan="9" style="text-align:center; padding: 2rem;"><span class="loading-spinner"></span> Loading frequencies...</td></tr>`;

    const filterStopwords = document.getElementById("freq-stopwords-toggle")?.checked ?? true;
    const posFilter = document.getElementById("freq-pos-filter")?.value ?? "ALL";
    const searchQuery = document.getElementById("freq-search-input")?.value ?? "";

    try {
        const url = `/api/frequency?book_id=${currentBookId}&filter_stopwords=${filterStopwords}&pos_filter=${posFilter}&search_query=${encodeURIComponent(searchQuery)}&limit=300`;
        const res = await fetch(url);
        const data = await res.json();

        document.getElementById("freq-total-count").textContent = `${data.unique_filtered_words.toLocaleString()} words found`;

        if (data.frequencies.length === 0) {
            tableBody.innerHTML = `<tr><td colspan="9" style="text-align:center; padding: 2rem; color: var(--text-muted);">No matching words found.</td></tr>`;
            return;
        }

        tableBody.innerHTML = data.frequencies.map(f => `
            <tr>
                <td style="font-weight: 600; color: var(--text-muted);">${f.rank}</td>
                <td>
                    <a href="javascript:void(0)" onclick="openWordProfile('${f.word}')" style="color: var(--accent-gold); font-weight: 600; text-decoration: none;">
                        ${f.word}
                    </a>
                </td>
                <td style="color: var(--text-secondary);">${f.lemma}</td>
                <td><span class="badge badge-${f.pos.toLowerCase()}">${f.pos}</span></td>
                <td style="font-weight: 700;">${f.count.toLocaleString()}</td>
                <td>${f.tf_percentage}%</td>
                <td>${f.relative_frequency}</td>
                <td>${f.document_frequency} / ${data.total_chapters}</td>
                <td style="color: var(--accent-emerald); font-weight: 600;">${f.tfidf}</td>
            </tr>
        `).join("");
    } catch (e) {
        tableBody.innerHTML = `<tr><td colspan="9" style="color: var(--accent-rose); padding: 1rem;">Error: ${e.message}</td></tr>`;
    }
}

// 3. Word Cloud
async function loadWordCloud() {
    const container = document.getElementById("wordcloud-display");
    container.innerHTML = `<div style="text-align:center; padding: 3rem;"><span class="loading-spinner"></span> Generating Word Cloud...</div>`;

    try {
        const res = await fetch(`/api/wordcloud?book_id=${currentBookId}&max_words=120`);
        const data = await res.json();

        if (data.image_base64) {
            container.innerHTML = `
                <div style="text-align: center;">
                    <img src="${data.image_base64}" alt="Word Cloud" style="max-width: 100%; border-radius: 8px; box-shadow: 0 8px 24px rgba(0,0,0,0.5);" />
                </div>
            `;
        } else {
            // HTML Word Cloud tags
            container.innerHTML = `
                <div style="display: flex; flex-wrap: wrap; gap: 0.75rem; align-items: center; justify-content: center; padding: 2rem;">
                    ${data.words.map(w => `
                        <span onclick="openWordProfile('${w.text}')" style="font-size: ${w.size}px; color: hsl(${Math.random() * 40 + 35}, 90%, 65%); cursor: pointer; transition: transform 0.2s;" title="${w.text}: ${w.count} times">
                            ${w.text}
                        </span>
                    `).join("")}
                </div>
            `;
        }
    } catch (e) {
        container.innerHTML = `<div style="color: var(--accent-rose); padding: 1rem;">Failed to generate word cloud: ${e.message}</div>`;
    }
}

// 4. Charts & Trends
async function loadCharts() {
    try {
        const [statsRes, freqRes, pausesRes] = await Promise.all([
            fetch(`/api/stats?book_id=${currentBookId}`),
            fetch(`/api/frequency?book_id=${currentBookId}&filter_stopwords=true&limit=15`),
            fetch(`/api/pause-marks?book_id=${currentBookId}`)
        ]);

        const stats = await statsRes.json();
        const freq = await freqRes.json();
        const pauses = await pausesRes.json();

        // Top Words Bar Chart
        const topWordsCtx = document.getElementById("chart-top-words").getContext("2d");
        if (chartInstances.topWords) chartInstances.topWords.destroy();
        chartInstances.topWords = new Chart(topWordsCtx, {
            type: "bar",
            data: {
                labels: freq.frequencies.map(f => f.word),
                datasets: [{
                    label: "Occurrences",
                    data: freq.frequencies.map(f => f.count),
                    backgroundColor: "#f59e0b"
                }]
            },
            options: { responsive: true, maintainAspectRatio: false }
        });

        // POS Distribution Pie Chart
        const posCtx = document.getElementById("chart-pos-dist").getContext("2d");
        if (chartInstances.posDist) chartInstances.posDist.destroy();
        chartInstances.posDist = new Chart(posCtx, {
            type: "doughnut",
            data: {
                labels: freq.pos_distribution.map(p => p.pos),
                datasets: [{
                    data: freq.pos_distribution.map(p => p.count),
                    backgroundColor: ["#3b82f6", "#10b981", "#f59e0b", "#8b5cf6", "#ec4899", "#64748b"]
                }]
            },
            options: { responsive: true, maintainAspectRatio: false }
        });

        // Rhetorical Punctuation Radar Chart
        const radarCtx = document.getElementById("chart-rhetoric").getContext("2d");
        if (chartInstances.rhetoric) chartInstances.rhetoric.destroy();
        chartInstances.rhetoric = new Chart(radarCtx, {
            type: "radar",
            data: {
                labels: pauses.marks_breakdown.map(m => m.mark.split(" ")[0]),
                datasets: [{
                    label: "Marks Density (per 1k words)",
                    data: pauses.marks_breakdown.map(m => m.density_per_1000_words),
                    borderColor: "#ec4899",
                    backgroundColor: "rgba(236, 72, 153, 0.2)"
                }]
            },
            options: { responsive: true, maintainAspectRatio: false }
        });

    } catch (e) {
        console.error("Charts loading error:", e);
    }
}

// 5. N-Grams
async function loadNgrams() {
    const container = document.getElementById("ngrams-results");
    container.innerHTML = `<tr><td colspan="4" style="text-align:center; padding: 2rem;"><span class="loading-spinner"></span> Loading N-Grams...</td></tr>`;

    const n = document.getElementById("ngram-n-select")?.value || 2;
    const filterStop = document.getElementById("ngram-stop-toggle")?.checked ?? false;
    const minCount = document.getElementById("ngram-min-count")?.value || 2;
    const search = document.getElementById("ngram-search")?.value || "";

    try {
        const res = await fetch(`/api/ngrams?book_id=${currentBookId}&n=${n}&filter_stopwords=${filterStop}&min_count=${minCount}&search_query=${encodeURIComponent(search)}&limit=150`);
        const data = await res.json();

        if (data.results.length === 0) {
            container.innerHTML = `<tr><td colspan="4" style="text-align:center; padding: 2rem; color: var(--text-muted);">No n-grams matched.</td></tr>`;
            return;
        }

        container.innerHTML = data.results.map((item, idx) => `
            <tr>
                <td style="font-weight: 600; color: var(--text-muted);">${idx + 1}</td>
                <td style="font-weight: 700; color: var(--accent-gold);">${item.ngram}</td>
                <td><strong style="color: var(--text-primary);">${item.count}</strong></td>
                <td style="color: var(--text-secondary); font-size: 0.8rem;">
                    ${item.sample_contexts.map(ctx => `<div style="margin-bottom: 2px;">• ...${ctx}...</div>`).join("")}
                </td>
            </tr>
        `).join("");
    } catch (e) {
        container.innerHTML = `<tr><td colspan="4" style="color: var(--accent-rose);">Error: ${e.message}</td></tr>`;
    }
}

// 6. PoS Patterns
async function loadPosPatterns() {
    const container = document.getElementById("pos-patterns-results");
    container.innerHTML = `<tr><td colspan="4" style="text-align:center; padding: 2rem;"><span class="loading-spinner"></span> Loading PoS Patterns...</td></tr>`;

    const patLen = document.getElementById("pos-pattern-length")?.value || 2;

    try {
        const res = await fetch(`/api/pos-patterns?book_id=${currentBookId}&pattern_length=${patLen}&limit=50`);
        const data = await res.json();

        container.innerHTML = data.results.map((r, idx) => `
            <tr>
                <td style="font-weight: 600; color: var(--text-muted);">${idx + 1}</td>
                <td>
                    <span style="background: rgba(59, 130, 246, 0.2); color: #60a5fa; padding: 3px 8px; border-radius: 4px; font-weight: 700; font-family: monospace;">
                        ${r.pattern}
                    </span>
                </td>
                <td style="font-weight: 700;">${r.count.toLocaleString()} (${r.percentage}%)</td>
                <td style="color: var(--text-secondary); font-family: monospace; font-size: 0.8rem;">${r.example}</td>
            </tr>
        `).join("");
    } catch (e) {
        container.innerHTML = `<tr><td colspan="4" style="color: var(--accent-rose);">Error: ${e.message}</td></tr>`;
    }
}

// 7. PoS Query
async function loadPosQuery() {
    const container = document.getElementById("pos-query-results");
    const query = document.getElementById("pos-query-input")?.value || "ADJ NOUN";
    container.innerHTML = `<div style="text-align:center; padding: 2rem;"><span class="loading-spinner"></span> Searching PoS pattern "${query}"...</div>`;

    try {
        const res = await fetch(`/api/pos-query?book_id=${currentBookId}&query=${encodeURIComponent(query)}&limit=80`);
        const data = await res.json();

        if (data.matches.length === 0) {
            container.innerHTML = `<div style="text-align:center; padding: 2rem; color: var(--text-muted);">No verses matching POS query "${data.query}". Try a pattern like "ADJ NOUN" or "PRON VERB ADV".</div>`;
            return;
        }

        container.innerHTML = `
            <div style="margin-bottom: 1rem; color: var(--text-secondary);">Found <strong>${data.matches_count}</strong> matching passages for sequence <code>${data.query}</code>:</div>
            <div style="display: flex; flex-direction: column; gap: 0.75rem;">
                ${data.matches.map(m => `
                    <div class="card" style="margin-bottom: 0;">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                            <span style="font-size: 0.75rem; color: var(--accent-gold); font-weight: 600;">${m.chapter_title} (Verse ${m.verse_id})</span>
                            <span style="font-size: 0.75rem; color: var(--text-muted); font-family: monospace;">Match: ${m.matched_words}</span>
                        </div>
                        <div style="font-size: 0.95rem; color: var(--text-primary); line-height: 1.6;">${m.full_verse}</div>
                    </div>
                `).join("")}
            </div>
        `;
    } catch (e) {
        container.innerHTML = `<div style="color: var(--accent-rose);">Error: ${e.message}</div>`;
    }
}

// 8. Repeated Verses
async function loadRepeatedVerses() {
    const exactContainer = document.getElementById("exact-repeats-container");
    const nearContainer = document.getElementById("near-repeats-container");

    exactContainer.innerHTML = `<div style="text-align:center; padding: 2rem;"><span class="loading-spinner"></span> Searching repeated verses...</div>`;

    try {
        const res = await fetch(`/api/repeated-verses?book_id=${currentBookId}&min_similarity=0.8&limit=50`);
        const data = await res.json();

        // Exact repeats
        if (data.exact_repeats.length === 0) {
            exactContainer.innerHTML = `<div style="color: var(--text-muted); padding: 1rem;">No exact multi-occurrence verses found.</div>`;
        } else {
            exactContainer.innerHTML = data.exact_repeats.map(r => `
                <div class="card" style="border-left: 3px solid var(--accent-gold);">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                        <span class="badge" style="background: rgba(245, 158, 11, 0.2); color: var(--accent-gold);">Repeated ${r.repetition_count} times</span>
                    </div>
                    <p style="font-size: 0.95rem; margin-bottom: 0.5rem; color: var(--text-primary);">${r.text}</p>
                    <div style="font-size: 0.75rem; color: var(--text-muted);">Occurs in: ${r.occurrences.map(o => `${o.chapter} (#${o.verse_id})`).join(", ")}</div>
                </div>
            `).join("");
        }

        // Near repeats
        if (data.near_repeats.length === 0) {
            nearContainer.innerHTML = `<div style="color: var(--text-muted); padding: 1rem;">No near-duplicate verses found.</div>`;
        } else {
            nearContainer.innerHTML = data.near_repeats.map(nr => `
                <div class="card" style="border-left: 3px solid var(--accent-purple);">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                        <span class="badge" style="background: rgba(139, 92, 246, 0.2); color: #a78bfa;">${nr.similarity}% Jaccard Similarity</span>
                    </div>
                    <div style="font-size: 0.875rem; margin-bottom: 0.4rem;"><strong>A (${nr.verse_a.chapter}):</strong> ${nr.verse_a.text}</div>
                    <div style="font-size: 0.875rem; color: var(--text-secondary);"><strong>B (${nr.verse_b.chapter}):</strong> ${nr.verse_b.text}</div>
                </div>
            `).join("");
        }
    } catch (e) {
        exactContainer.innerHTML = `<div style="color: var(--accent-rose);">Error: ${e.message}</div>`;
    }
}

// 9. Repeated Phrases
async function loadRepeatedPhrases() {
    const container = document.getElementById("repeated-phrases-results");
    container.innerHTML = `<tr><td colspan="4" style="text-align:center; padding: 2rem;"><span class="loading-spinner"></span> Extracting common substrings...</td></tr>`;

    try {
        const res = await fetch(`/api/repeated-phrases?book_id=${currentBookId}&min_phrase_len=3&max_phrase_len=10&min_occurrences=3&limit=100`);
        const data = await res.json();

        if (data.phrases.length === 0) {
            container.innerHTML = `<tr><td colspan="4" style="text-align:center; padding: 2rem; color: var(--text-muted);">No repeating phrases found.</td></tr>`;
            return;
        }

        container.innerHTML = data.phrases.map((p, idx) => `
            <tr>
                <td style="font-weight: 600; color: var(--text-muted);">${idx + 1}</td>
                <td style="font-weight: 700; color: var(--accent-gold);">${p.phrase}</td>
                <td><span class="badge" style="background: rgba(16, 185, 129, 0.2); color: #34d399;">${p.word_count} words</span></td>
                <td><strong style="color: var(--text-primary);">${p.occurrences}</strong> times (${p.relative_freq} per 10k)</td>
            </tr>
        `).join("");
    } catch (e) {
        container.innerHTML = `<tr><td colspan="4" style="color: var(--accent-rose);">Error: ${e.message}</td></tr>`;
    }
}

// 10. Ontology Data & Graphs
async function loadOntology() {
    const conceptCards = document.getElementById("ontology-concept-cards");
    conceptCards.innerHTML = `<div style="text-align:center; padding: 2rem;"><span class="loading-spinner"></span> Loading Philosophical Ontology...</div>`;

    try {
        const res = await fetch(`/api/ontology?book_id=${currentBookId}`);
        const data = await res.json();

        conceptCards.innerHTML = data.concepts.map(c => `
            <div class="card" style="border-top: 3px solid ${c.color};">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                    <div style="font-weight: 700; font-size: 1.1rem; color: var(--text-primary);">${c.name}</div>
                    <span class="badge" style="background-color: ${c.color}22; color: ${c.color};">${c.frequency} mentions</span>
                </div>
                <div style="font-size: 0.75rem; color: var(--text-muted); margin-bottom: 0.5rem; text-transform: uppercase; letter-spacing: 0.05em;">${c.category}</div>
                <p style="font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 0.75rem;">${c.description}</p>
                ${c.sample_passages.length > 0 ? `
                    <div style="background: var(--bg-card); padding: 0.5rem 0.75rem; border-radius: 6px; font-size: 0.75rem; color: var(--text-muted);">
                        <em>"${c.sample_passages[0].text.slice(0, 140)}..."</em>
                    </div>
                ` : ""}
            </div>
        `).join("");

        // Render Vis Network Graph
        const graphContainer = document.getElementById("network-graph-container");
        if (typeof vis !== "undefined" && graphContainer) {
            const visNodes = new vis.DataSet(data.graph.nodes.map(n => ({
                id: n.id,
                label: n.label,
                value: n.value,
                color: { background: n.color, border: "#ffffff", highlight: { background: "#fbbf24", border: "#ffffff" } },
                font: { color: "#ffffff", size: 14, face: "Inter" }
            })));

            const visEdges = new vis.DataSet(data.graph.edges.map(e => ({
                from: e.from,
                to: e.to,
                value: e.value,
                color: { color: "rgba(148, 163, 184, 0.4)", highlight: "#fbbf24" }
            })));

            const visData = { nodes: visNodes, edges: visEdges };
            const visOptions = {
                nodes: { shape: "dot", scaling: { min: 14, max: 36 } },
                edges: { smooth: true },
                physics: { stabilization: true, barnesHut: { gravitationalConstant: -3000, springLength: 120 } }
            };

            networkInstance = new vis.Network(graphContainer, visData, visOptions);
        }
    } catch (e) {
        conceptCards.innerHTML = `<div style="color: var(--accent-rose);">Error loading ontology: ${e.message}</div>`;
    }
}

// 11. Word Information (Lexicon)
async function loadWordInfo(targetWord) {
    const word = targetWord || document.getElementById("word-info-input")?.value || "power";
    const container = document.getElementById("word-info-profile-container");
    container.innerHTML = `<div style="text-align:center; padding: 2rem;"><span class="loading-spinner"></span> Loading Lexicon profile for "${word}"...</div>`;

    try {
        const res = await fetch(`/api/word-info?book_id=${currentBookId}&word=${encodeURIComponent(word)}`);
        const data = await res.json();

        if (!data.found) {
            container.innerHTML = `<div class="card" style="color: var(--accent-rose);">${data.message}</div>`;
            return;
        }

        container.innerHTML = `
            <div class="stat-grid">
                <div class="stat-card">
                    <div class="stat-label">Word & Lemma</div>
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

            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 1.5rem; margin-bottom: 1.5rem;">
                <div class="card">
                    <div class="card-header"><div class="card-title">Top Collocates (±4 words)</div></div>
                    <div style="display: flex; flex-wrap: wrap; gap: 0.5rem;">
                        ${data.top_collocates.map(c => `
                            <span class="badge" onclick="openWordProfile('${c.word}')" style="background: var(--bg-card); color: var(--text-primary); border: 1px solid var(--border-color); padding: 0.35rem 0.6rem; cursor: pointer;">
                                ${c.word} (${c.co_occurrences})
                            </span>
                        `).join("")}
                    </div>
                </div>
                <div class="card">
                    <div class="card-header"><div class="card-title">POS Tag Instances</div></div>
                    <div style="display: flex; gap: 0.5rem; flex-wrap: wrap;">
                        ${data.pos_breakdown.map(p => `
                            <span class="badge badge-${p.pos.toLowerCase()}" style="padding: 0.4rem 0.75rem; font-size: 0.8rem;">
                                ${p.pos}: ${p.count}
                            </span>
                        `).join("")}
                    </div>
                </div>
            </div>

            <div class="card">
                <div class="card-header"><div class="card-title">Sample Context Passages</div></div>
                <div style="display: flex; flex-direction: column; gap: 0.75rem;">
                    ${data.sample_verses.map(v => `
                        <div style="background: var(--bg-card); padding: 0.75rem 1rem; border-radius: 6px; border-left: 3px solid var(--accent-gold);">
                            <div style="font-size: 0.75rem; color: var(--accent-gold); font-weight: 600; margin-bottom: 0.25rem;">${v.chapter} (Verse #${v.verse_id})</div>
                            <div style="font-size: 0.9rem; color: var(--text-primary); line-height: 1.5;">${v.highlighted_html}</div>
                        </div>
                    `).join("")}
                </div>
            </div>
        `;
    } catch (e) {
        container.innerHTML = `<div style="color: var(--accent-rose);">Error: ${e.message}</div>`;
    }
}

function openWordProfile(word) {
    document.getElementById("word-info-input").value = word;
    const navItems = document.querySelectorAll(".nav-item");
    navItems.forEach(n => n.classList.remove("active"));
    const targetNav = document.querySelector('[data-tab="tab-word-info"]');
    if (targetNav) targetNav.classList.add("active");
    switchTab("tab-word-info");
    loadWordInfo(word);
}

// 12. Collocations
async function loadCollocation() {
    const tableBody = document.getElementById("collocation-table-body");
    tableBody.innerHTML = `<tr><td colspan="7" style="text-align:center; padding: 2rem;"><span class="loading-spinner"></span> Calculating collocations & PMI...</td></tr>`;

    const windowSize = document.getElementById("colloc-window-select")?.value || 4;
    const minCount = document.getElementById("colloc-min-count")?.value || 3;
    const targetWord = document.getElementById("colloc-target-word")?.value || "";

    try {
        const res = await fetch(`/api/collocation?book_id=${currentBookId}&window_size=${windowSize}&min_cooccurrences=${minCount}&target_word=${encodeURIComponent(targetWord)}&limit=150`);
        const data = await res.json();

        if (data.results.length === 0) {
            tableBody.innerHTML = `<tr><td colspan="7" style="text-align:center; padding: 2rem; color: var(--text-muted);">No collocations found.</td></tr>`;
            return;
        }

        tableBody.innerHTML = data.results.map((c, idx) => `
            <tr>
                <td style="font-weight: 600; color: var(--text-muted);">${idx + 1}</td>
                <td style="font-weight: 700; color: var(--accent-gold);">${c.pair}</td>
                <td><strong style="color: var(--text-primary);">${c.cooccurrences}</strong></td>
                <td>${c.freq_w1}</td>
                <td>${c.freq_w2}</td>
                <td style="color: var(--accent-emerald); font-weight: 700;">${c.pmi}</td>
                <td style="color: var(--accent-blue);">${c.t_score}</td>
            </tr>
        `).join("");
    } catch (e) {
        tableBody.innerHTML = `<tr><td colspan="7" style="color: var(--accent-rose);">Error: ${e.message}</td></tr>`;
    }
}

// 13. Concordance (KWIC)
async function loadConcordance() {
    const container = document.getElementById("kwic-results-container");
    const keyword = document.getElementById("kwic-search-input")?.value || "zarathustra";
    const sortBy = document.getElementById("kwic-sort-select")?.value || "order";
    const contextWords = document.getElementById("kwic-context-words")?.value || 7;

    container.innerHTML = `<div style="text-align:center; padding: 2rem;"><span class="loading-spinner"></span> Generating KWIC concordance for "${keyword}"...</div>`;

    try {
        const res = await fetch(`/api/concordance?book_id=${currentBookId}&keyword=${encodeURIComponent(keyword)}&context_words=${contextWords}&sort_by=${sortBy}&limit=250`);
        const data = await res.json();

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
            </div>
        `).join("");
    } catch (e) {
        container.innerHTML = `<div style="color: var(--accent-rose);">Error: ${e.message}</div>`;
    }
}

// 14. Pause Marks & Rhetorical Cadence
async function loadPauseMarks() {
    const container = document.getElementById("pause-marks-container");
    container.innerHTML = `<div style="text-align:center; padding: 2rem;"><span class="loading-spinner"></span> Analyzing pause marks...</div>`;

    try {
        const res = await fetch(`/api/pause-marks?book_id=${currentBookId}`);
        const data = await res.json();

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
                    <div class="stat-sub">Density of Em-Dashes & Exclamations</div>
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
                <div class="card-header"><div class="card-title">Punctuation & Pause Marks Breakdown</div></div>
                <div class="table-responsive">
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>Pause / Rhetorical Mark</th>
                                <th>Total Count</th>
                                <th>Density (per 1,000 words)</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${data.marks_breakdown.map(m => `
                                <tr>
                                    <td style="font-weight: 700; color: var(--text-primary);">${m.mark}</td>
                                    <td>${m.count.toLocaleString()}</td>
                                    <td style="font-weight: 600; color: var(--accent-gold);">${m.density_per_1000_words}</td>
                                </tr>
                            `).join("")}
                        </tbody>
                    </table>
                </div>
            </div>
        `;
    } catch (e) {
        container.innerHTML = `<div style="color: var(--accent-rose);">Error: ${e.message}</div>`;
    }
}

// 15. Word Similarity & Embeddings
async function loadWordSimilarity() {
    const container = document.getElementById("sim-results-container");
    const word1 = document.getElementById("sim-word1-input")?.value || "power";
    const word2 = document.getElementById("sim-word2-input")?.value || "";

    container.innerHTML = `<div style="text-align:center; padding: 2rem;"><span class="loading-spinner"></span> Computing semantic vector similarities...</div>`;

    try {
        let url = `/api/similarity?book_id=${currentBookId}&word1=${encodeURIComponent(word1)}&top_k=15`;
        if (word2.trim()) {
            url += `&word2=${encodeURIComponent(word2.trim())}`;
        }
        const res = await fetch(url);
        const data = await res.json();

        if (data.error) {
            container.innerHTML = `<div class="card" style="color: var(--accent-rose);">${data.error}</div>`;
            return;
        }

        if (data.mode === "pairwise") {
            container.innerHTML = `
                <div class="card" style="text-align: center; padding: 2rem;">
                    <div style="font-size: 1.1rem; color: var(--text-secondary); margin-bottom: 0.5rem;">Semantic Cosine Similarity between:</div>
                    <div style="font-size: 1.5rem; font-weight: 700; color: var(--text-primary); margin-bottom: 1rem;">
                        <span style="color: var(--accent-gold);">${data.word1}</span> ↔ <span style="color: var(--accent-blue);">${data.word2}</span>
                    </div>
                    <div style="font-size: 3rem; font-weight: 800; color: var(--accent-emerald);">${data.percentage_similarity}%</div>
                    <div style="font-size: 0.85rem; color: var(--text-muted);">Cosine Score: ${data.cosine_similarity}</div>
                </div>
            `;
        } else {
            container.innerHTML = `
                <div style="margin-bottom: 1rem; color: var(--text-secondary);">Top semantically related words for <strong style="color: var(--accent-gold);">"${data.target_word}"</strong>:</div>
                <div class="table-responsive">
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>#</th>
                                <th>Semantically Related Word</th>
                                <th>Similarity Score</th>
                                <th>Cosine Metric</th>
                                <th>Occurrences</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${data.similar_words.map((sw, idx) => `
                                <tr>
                                    <td style="color: var(--text-muted);">${idx + 1}</td>
                                    <td><a href="javascript:void(0)" onclick="openWordProfile('${sw.word}')" style="color: var(--accent-gold); font-weight: 700; text-decoration: none;">${sw.word}</a></td>
                                    <td>
                                        <div style="display: flex; align-items: center; gap: 0.5rem;">
                                            <div style="background: rgba(16, 185, 129, 0.2); height: 8px; border-radius: 4px; width: ${sw.similarity_score * 2}px; max-width: 120px;">
                                                <div style="background: #10b981; height: 8px; border-radius: 4px; width: 100%;"></div>
                                            </div>
                                            <span style="font-weight: 700; color: #10b981;">${sw.similarity_score}%</span>
                                        </div>
                                    </td>
                                    <td style="font-family: monospace;">${sw.similarity}</td>
                                    <td>${sw.frequency}</td>
                                </tr>
                            `).join("")}
                        </tbody>
                    </table>
                </div>
            `;
        }
    } catch (e) {
        container.innerHTML = `<div style="color: var(--accent-rose);">Error: ${e.message}</div>`;
    }
}

// 16. Dataset View & Export
function loadDatasetView() {
    // Already static markup with buttons
}

function exportDataset(format) {
    window.location.href = `/api/export?book_id=${currentBookId}&format_type=${format}`;
}
