// scratch/test_sample_ec_status.js
// Test sample EC rendering through EC status tab
const fs = require('fs');
const path = require('path');

function createElementMock(tag) {
    return {
        tagName: tag.toUpperCase(),
        classList: {
            classes: new Set(),
            add: function(...cls) { cls.forEach(c => this.classes.add(c)); },
            remove: function(...cls) { cls.forEach(c => this.classes.delete(c)); },
            contains: function(c) { return this.classes.has(c); },
            toggle: function(c) { if (this.classes.has(c)) this.classes.delete(c); else this.classes.add(c); }
        },
        style: {},
        dataset: {},
        children: [],
        appendChild: function(child) { this.children.push(child); return child; },
        querySelectorAll: function(sel) { return []; },
        querySelector: function(sel) { return null; },
        innerHTML: '',
        textContent: '',
        value: '',
        options: [],
        scrollIntoView: function() {},
        onclick: null,
        setAttribute: function(k, v) { this[k] = v; },
        getAttribute: function(k) { return this[k] || null; }
    };
}

const elements = {};
function getOrCreateElement(id) {
    if (!elements[id]) {
        elements[id] = createElementMock('div');
        elements[id].id = id;
    }
    return elements[id];
}

const elementIds = [
    "result-doc-type-title", "page-indicator", "btn-prev-page", "btn-next-page",
    "page-jump-select", "viewer-empty-state", "all-pages-container",
    "processing-loader", "processing-status-text", "step-2-completion-banner",
    "workspace", "ec-status-content", "ec-analysis-content", "fields-content", "owners-content",
    "property-filter-content", "checklist-content", "ocr-text-content", "table-content",
    "tab-ec-status", "tab-btn-ec-status", "tab-content-ec-status", "ec-status-container",
    "tab-ec-analysis", "tab-btn-ec-analysis", "tab-content-ec-analysis", "ec-analysis-container",
    "tab-fields", "tab-btn-fields", "tab-content-fields", "tab-owners", "tab-btn-owners", "tab-content-owners",
    "tab-property-filter", "tab-btn-property-filter", "tab-content-property-filter",
    "tab-checklist", "tab-ocr-text", "tab-ocr", "tab-btn-ocr", "tab-content-ocr",
    "tab-table", "tab-btn-table", "tab-content-table", "btn-toggle-bbox",
    "prop-in-survey", "prop-in-taluk", "prop-in-city", "prop-in-district",
    "prop-in-extent", "prop-in-boundary", "prop-in-flat", "prop-in-door", "prop-in-owner",
    "property-filter-results", "checklist-items-container", "checklist-badge-count",
    "raw-ocr-text-view", "fields-grid-container", "fields-badge-count",
    "ec-summary-card", "ec-table-body", "table-transactions-body"
];
elementIds.forEach(id => getOrCreateElement(id));

global.document = {
    getElementById: (id) => elements[id] || getOrCreateElement(id),
    createElement: (tag) => createElementMock(tag),
    createDocumentFragment: () => {
        const frag = createElementMock('fragment');
        frag.appendChild = function(child) { this.children.push(child); return child; };
        return frag;
    },
    querySelectorAll: (sel) => [],
    querySelector: (sel) => null,
    addEventListener: (evt, cb) => {},
    removeEventListener: (evt, cb) => {}
};

global.window = {
    document: global.document,
    addEventListener: (evt, cb) => {},
    removeEventListener: (evt, cb) => {},
    IntersectionObserver: null,
    setTimeout: (fn, ms) => {},
    clearTimeout: (id) => {},
    scrollTo: () => {}
};

global.lucide = {
    createIcons: () => {}
};

async function testSampleEC() {
    const res = await fetch('http://127.0.0.1:8000/api/sample/ec');
    const data = await res.json();
    console.log("Fetched sample EC from backend, status:", data.status);

    const appJsCode = fs.readFileSync(path.join(__dirname, '..', 'static', 'app.js'), 'utf8');
    const vm = require('vm');
    const context = vm.createContext({
        console,
        document: global.document,
        window: global.window,
        lucide: global.lucide,
        fetch: () => Promise.resolve({ json: () => Promise.resolve({}) }),
        parseInt,
        parseFloat,
        Math,
        JSON,
        String,
        Array,
        Object,
        Set,
        Date,
        isNaN,
        encodeURIComponent,
        decodeURIComponent
    });

    vm.runInContext(appJsCode, context);

    context.window.state.currentResult = {
        filename: 'Sample_ec.pdf',
        total_pages: 1,
        pages: [data.simulated_page],
        aggregated_text: data.raw_text,
        extraction: data.extracted_data
    };
    context.window.state.selectedCategoryId = "ec";

    context.renderDocumentResult();

    console.log("Sample EC activeTab:", context.window.state.activeTab);
    if (context.window.state.activeTab !== "ec-status") {
        throw new Error(`Expected activeTab to be 'ec-status', but got '${context.window.state.activeTab}'`);
    }

    const ecContainer = elements["ec-status-container"];
    console.log("Sample EC container HTML length:", ecContainer.innerHTML.length);

    // Print key sections
    const checks = [
        "ENCUMBRANCE STATUS",
        "Mortgages",
        "None",
        "Liens/Attachments",
        "4", // 4 transactions
        "TRANSACTIONS",
        "EC Search Period",
        "01-Jan-1990 to 17-Oct-2023",
        "33 years of records analyzed",
        "Transaction History",
        "4 records",
        "PATTA OWNER",
        "Classic Foundations",
        "K. Rajendran",
        "S. Lakshmi Priya"
    ];
    checks.forEach(c => {
        if (!ecContainer.innerHTML.includes(c)) {
            throw new Error(`Sample EC output missing expected element: '${c}'`);
        }
    });

    console.log("ALL CHECKS PASSED FOR SAMPLE EC STATUS TAB RENDERING!");
}

testSampleEC().catch(e => {
    console.error("FAIL:", e);
    process.exit(1);
});
