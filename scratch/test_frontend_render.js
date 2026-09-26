// scratch/test_frontend_render.js
// Simulate the browser environment to test renderDocumentResult and all tab rendering functions
const fs = require('fs');
const path = require('path');

// 1. Create a minimal mock DOM
function createElementMock(tag) {
    const el = {
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
        appendChild: function(child) {
            this.children.push(child);
            return child;
        },
        querySelectorAll: function(sel) { return []; },
        querySelector: function(sel) { return null; },
        innerHTML: '',
        textContent: '',
        value: '',
        options: [],
        scrollIntoView: function() {},
        onclick: null
    };
    return el;
}

const elements = {};
function getOrCreateElement(id) {
    if (!elements[id]) {
        elements[id] = createElementMock('div');
        elements[id].id = id;
    }
    return elements[id];
}

// Pre-create elements referenced in app.js
const elementIds = [
    "result-doc-type-title", "page-indicator", "btn-prev-page", "btn-next-page",
    "page-jump-select", "viewer-empty-state", "all-pages-container",
    "processing-loader", "processing-status-text", "step-2-completion-banner",
    "workspace", "ec-analysis-content", "fields-content", "owners-content",
    "property-filter-content", "checklist-content", "ocr-text-content", "table-content",
    "tab-ec-analysis", "tab-fields", "tab-owners", "tab-property-filter",
    "tab-checklist", "tab-ocr-text", "tab-table", "btn-toggle-bbox",
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
        frag.appendChild = function(child) {
            this.children.push(child);
            return child;
        };
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

console.log("Mock DOM initialized successfully.");

// 2. Load the 22-page test EC response
const testResponsePath = path.join(__dirname, 'test_ec_response.json');
if (!fs.existsSync(testResponsePath)) {
    console.error("test_ec_response.json not found!");
    process.exit(1);
}

const data = JSON.parse(fs.readFileSync(testResponsePath, 'utf8'));
console.log(`Loaded EC response: ${data.pages ? data.pages.length : 0} pages, doc_type=${data.document_type_id}`);

// 3. Test app.js functions in isolated context
const appJsCode = fs.readFileSync(path.join(__dirname, '..', 'static', 'app.js'), 'utf8');

// Test that script can evaluate in context
try {
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
        decodeURIComponent,
        state: {
            currentResult: null,
            currentPageIndex: 0,
            showBBoxes: true,
            selectedCategoryId: "ec",
            categories: [{ id: "ec", name: "4. EC (Encumbrance Certificate)" }]
        }
    });

    vm.runInContext(appJsCode, context);
    console.log("static/app.js evaluated cleanly in VM context!");

    // Set state.currentResult
    context.state.currentResult = data;
    context.state.currentPageIndex = 0;

    // Test renderDocumentResult
    console.log("Executing renderDocumentResult()...");
    context.renderDocumentResult();
    console.log("SUCCESS: renderDocumentResult() executed without throwing any errors!");

    // Test showStep2CompletionNotice
    console.log("Executing showStep2CompletionNotice()...");
    context.showStep2CompletionNotice(data);
    const banner = elements["step-2-completion-banner"];
    console.log("Banner HTML content length:", banner.innerHTML.length);
    console.log("Banner classes:", Array.from(banner.classList.classes).join(", "));
    console.log("SUCCESS: showStep2CompletionNotice() executed perfectly!");

    // Test jumpToPage
    console.log("Executing jumpToPage(5)...");
    context.jumpToPage(5);
    console.log("SUCCESS: jumpToPage(5) executed perfectly! Current page:", context.state.currentPageIndex);

} catch (err) {
    console.error("FATAL ERROR during test:", err);
    process.exit(1);
}
