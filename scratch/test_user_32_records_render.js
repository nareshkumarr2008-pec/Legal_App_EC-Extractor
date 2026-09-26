// scratch/test_user_32_records_render.js
// Universal verification of EC Status tab for the 32-record EC document
const fs = require('fs');
const path = require('path');
const vm = require('vm');

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

// Build mock 32-record extraction representing the user's data
const mockTransactions = [
    { sr: 1, doc_no: "3558/1986", date: "17-Dec-1986", nature: "Sale Deed", executants: "Srivasi Mangapuram Mahathani", claimants: "Subha Anantharaman", consideration: "-", page_index: 0 },
    { sr: 2, doc_no: "3559/1986", date: "17-Dec-1986", nature: "Sale Deed", executants: "Srivasi Mangapuram Mahadani", claimants: "D. Raghunath", consideration: "-", page_index: 0 },
    { sr: 3, doc_no: "3560/1986", date: "17-Dec-1986", nature: "Sale Deed", executants: "Srivasi Mangapuram Mahadani", claimants: "Fatima Moghama Worajee", consideration: "-", page_index: 1 },
    { sr: 4, doc_no: "506/1987", date: "26-Feb-1987", nature: "விற்பைன ஆவணம்", executants: "Vashi Mangaram Mehdani (Principal)", claimants: "V. Ramasamy", consideration: "-", page_index: 1 },
    { sr: 5, doc_no: "507/1987", date: "26-Feb-1987", nature: "Sale Deed", executants: "Vashi Mangaram Mehdani (Principal)", claimants: "Meenashi Krishnamurthy", consideration: "-", page_index: 2 },
    { sr: 6, doc_no: "508/1987", date: "26-Feb-1987", nature: "Sale Deed", executants: "Vashi Mangaram Mehdani (Principal)", claimants: "Lycans In Romolam", consideration: "-", page_index: 2 },
    { sr: 7, doc_no: "660/1987", date: "13-Mar-1987", nature: "Sale Deed", executants: "Vashi Mangaram Mehdani (Principal)", claimants: "S. Ramasa Chandran", consideration: "-", page_index: 3 },
    { sr: 8, doc_no: "1220/1987", date: "13-May-1987", nature: "Sale Deed", executants: "Srivashi Mangaram Meghdani (Principal)", claimants: "C. Visveswar Rao", consideration: "-", page_index: 3 },
    { sr: 9, doc_no: "1221/1987", date: "13-May-1987", nature: "Sale Deed", executants: "Srivashi Mangaram Meghdani (Principal)", claimants: "S. V. Padmanabhan", consideration: "-", page_index: 4 },
    { sr: 10, doc_no: "1400/1987", date: "28-May-1987", nature: "Sale Deed", executants: "Vashi Mangaram Meghdani (Principal)", claimants: "V. E. Muthiah", consideration: "-", page_index: 4 },
    { sr: 11, doc_no: "189/1988", date: "28-Jan-1988", nature: "விற்பைன ஆவணம்", executants: "Vashimangaram", claimants: "A. Venugopalan Mahadani", consideration: "-", page_index: 5 },
    { sr: 12, doc_no: "190/1988", date: "28-Jan-1988", nature: "Sale Deed", executants: "Vashimangaram Mahadani", claimants: "Rabia Ismail Dadabai", consideration: "-", page_index: 5 },
    { sr: 13, doc_no: "2416/1989", date: "25-Jul-1989", nature: "Sale Deed", executants: "Visveswar Rao", claimants: "Jagankeergaard", consideration: "-", page_index: 6 },
    { sr: 14, doc_no: "2192/1995", date: "15-May-1995", nature: "Sale Deed", executants: "V. E. Muthiah", claimants: "R. Periya Sami", consideration: "-", page_index: 6 },
    { sr: 15, doc_no: "971/1999", date: "17-Jun-1999", nature: "Sale Deed", executants: "S. Jahangir", claimants: "Tamil Mani Panneer Selvam", consideration: "-", page_index: 7 },
    { sr: 16, doc_no: "885/2002", date: "26-Apr-2002", nature: "விடுதைல", executants: "D. Jayalakshmi", claimants: "Prashanth Raghunath", consideration: "-", page_index: 7 },
    { sr: 17, doc_no: "1636/2002", date: "26-Jul-2002", nature: "Sale Deed", executants: "Subeda M. Jetved", claimants: "R. Periasamy", consideration: "-", page_index: 8 },
    { sr: 18, doc_no: "15/2003", date: "03-Jan-2003", nature: "பிழைத்திருத்தல் ஆவணம்", executants: "Fatima E. Jetved", claimants: "R. Periasamy", consideration: "-", page_index: 8 },
    { sr: 19, doc_no: "1908/2007", date: "18-Oct-2007", nature: "Sale Deed", executants: "Value Rs.1,75,000/-.", claimants: "R. Periasamy", consideration: "-", page_index: 9 },
    { sr: 20, doc_no: "556/2009", date: "31-Mar-2009", nature: "உரிமை மாற்றம் - பெருநகர்", executants: "Rabindranath Ganesh", claimants: "A. Amala Anban", consideration: "-", page_index: 9 },
    { sr: 21, doc_no: "1611/2009", date: "09-Oct-2009", nature: "உரிமை மாற்றம் - பெருநகர்", executants: "Rabia I. Dadabai", claimants: "Sugadev Narayana Singh", consideration: "-", page_index: 10 },
    { sr: 22, doc_no: "1726/2009", date: "27-Oct-2009", nature: "உரிமை வைப்பு ஆவணம் வேண்டும் போது கடன் திரும்ப செலுத்த", executants: "A. Amala Anban (Amala Anban) : 12/part", claimants: "Corporation Bank", consideration: "-", page_index: 10 },
    { sr: 23, doc_no: "1840/2009", date: "13-Nov-2009", nature: "ஏற்பாடு- குடும்ப உறுப்பினர்கள்", executants: "Meenakshi Krishnamurthy", claimants: "Ganesh Krishnamurthy", consideration: "-", page_index: 11 },
    { sr: 24, doc_no: "233/2011", date: "07-Feb-2011", nature: "உரிமை மாற்றம் - பெருநகர்", executants: "Ganesh Krishnamurthy", claimants: "G. Annaprasadam", consideration: "-", page_index: 11 },
    { sr: 25, doc_no: "1471/2011", date: "14-Jul-2011", nature: "உரிமை மாற்றம் - பெருநகர்", executants: "Tamarind", claimants: "Lawrence Innazimuthu", consideration: "-", page_index: 12 },
    { sr: 26, doc_no: "1722/2012", date: "23-Aug-2012", nature: "ஏற்பாடு- குடும்ப உறுப்பினர்கள்", executants: "S.V. Padmanabhan", claimants: "Sarayu Padmanabhan", consideration: "-", page_index: 12 },
    { sr: 27, doc_no: "573/2018", date: "15-Mar-2018", nature: "விடுதைல ஆவணம்", executants: "S. V. Padmanabhan", claimants: "Sarayu Padmanabhan", consideration: "-", page_index: 13 },
    { sr: 28, doc_no: "610/2018", date: "21-Mar-2018", nature: "Sale Deed", executants: "Sarayu Padmanabhan Site No: Second", claimants: "D.V. Vishwapriya", consideration: "-", page_index: 13 },
    { sr: 29, doc_no: "1234/2018", date: "28-May-2018", nature: "உரிமை ஆவணங்களின் ஒப்பைடப்பு ஆவணம்", executants: "D. V. Vishwapriya", claimants: "Indian Bank", consideration: "-", page_index: 14 },
    { sr: 30, doc_no: "1445/2020", date: "19-Sep-2020", nature: "Receipt", executants: "Indian Bank", claimants: "Vishwapriya", consideration: "-", page_index: 14 },
    { sr: 31, doc_no: "2251/2021", date: "27-Aug-2021", nature: "ஏற்பாடு", executants: "Subha Anantharaman Floor No: First Floor", claimants: "Akila Anantharaman", consideration: "-", page_index: 15 },
    { sr: 32, doc_no: "3691/2024", date: "21-Nov-2024", nature: "ஏற்பாடு", executants: "Annapakyam Floor No: Third Floo", claimants: "Villichami Indrani", consideration: "-", page_index: 16 }
];

const mockExtraction = {
    document_type_id: "ec",
    document_type_name: "Encumbrance Certificate (EC)",
    fields: {
        search_period: { value: "-" },
        survey_searched: { value: "12/PART, 26" },
        property_extent: { value: "3.2 Grounds | 265 Grounds | 1986 Grounds | 279 Grounds | 267 Grounds | 275 Grounds | 283 Grounds | 413 Grounds" },
        active_mortgages: { value: "1 Open/Unreleased Mortgages | 1 Closed Mortgage(s)", open_count: 1 },
        court_attachments: { value: "1 Found", count: 1 },
        transactions_table: { value: mockTransactions }
    }
};

const appJsCode = fs.readFileSync(path.join(__dirname, '..', 'static', 'app.js'), 'utf8');
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
    filename: 'Test_32_ec.pdf',
    total_pages: 17,
    pages: new Array(17).fill({}),
    aggregated_text: "Mock 32 records text",
    extraction: mockExtraction
};
context.window.state.selectedCategoryId = "ec";

// Trigger render
context.renderDocumentResult();

const ecContainer = elements["ec-status-container"];
const html = ecContainer.innerHTML;

console.log("Rendered EC Status HTML length:", html.length);

// Assertions:
// 1. Search Period
if (html.includes("17-Dec-1986 to 21-Nov-2024")) {
    console.log("PASS: Search Period date range correctly derived: 17-Dec-1986 to 21-Nov-2024");
} else {
    console.error("FAIL: Search Period date range missing!");
    process.exit(1);
}

if (html.includes("38 years of records analyzed")) {
    console.log("PASS: 38 years of records analyzed correctly calculated");
} else {
    console.error("FAIL: 38 years calculation missing!");
    process.exit(1);
}

// 2. Mortgages pill with cleared count
if (html.includes("1 Active (1 Cleared)")) {
    console.log("PASS: Mortgage status shows 1 Active (1 Cleared)");
} else {
    console.error("FAIL: Mortgage pill display mismatch!");
    process.exit(1);
}

// 3. Row 19 Consideration Value
if (html.includes("₹1,75,000")) {
    console.log("PASS: Row 19 consideration value correctly extracted: ₹1,75,000");
} else {
    console.error("FAIL: Row 19 consideration ₹1,75,000 missing!");
    process.exit(1);
}

// 4. Row 22 party clean (no : 12/part in name)
if (html.includes("A. Amala Anban") && !html.includes("A. Amala Anban (Amala Anban) : 12/part")) {
    console.log("PASS: Row 22 executant name cleanly sanitized without : 12/part");
} else {
    console.error("FAIL: Row 22 party sanitation failed!");
    process.exit(1);
}

// 5. Row 28 property unit and party clean
if (html.includes("Sarayu Padmanabhan") && !html.includes("Sarayu Padmanabhan Site No: Second")) {
    console.log("PASS: Row 28 executant name cleanly sanitized");
} else {
    console.error("FAIL: Row 28 party sanitation failed!");
    process.exit(1);
}

// 6. Patta Owner on Row 32 (NOT Row 28)
if (html.includes("Villichami Indrani</span>") && html.includes("PATTA OWNER")) {
    console.log("PASS: Row 32 contains PATTA OWNER badge");
} else {
    console.error("FAIL: Row 32 missing PATTA OWNER badge!");
    process.exit(1);
}

// Verify Row 28 does NOT have the PATTA OWNER badge, while Row 32 does
const rows = html.split("<tbody")[1].split("<tr").slice(1);
const row28Html = rows[27]; // 28th body row (0-indexed 27)
const row32Html = rows[31]; // 32nd body row (0-indexed 31)

if (!row28Html.includes("PATTA OWNER")) {
    console.log("PASS: Row 28 correctly does NOT have PATTA OWNER badge");
} else {
    console.error("FAIL: Row 28 incorrectly has PATTA OWNER badge!");
    process.exit(1);
}

if (row32Html.includes("PATTA OWNER")) {
    console.log("PASS: Row 32 (Villichami Indrani) is the recognized PATTA OWNER");
} else {
    console.error("FAIL: Row 32 does not have PATTA OWNER badge!");
    process.exit(1);
}

// 7. Property Extent should NOT contain the 8-ground list
if (!html.includes("3.2 Grounds | 265 Grounds | 1986 Grounds")) {
    console.log("PASS: Spurious 1986 Grounds / 265 Grounds concatenated list eliminated from property cells");
} else {
    console.error("FAIL: Spurious grounds still present in property cells!");
    process.exit(1);
}

// 8. Nature display with clean Tamil subtitles
if (html.includes("Settlement Deed") && html.includes("ஏற்பாடு ஆவணம்")) {
    console.log("PASS: Nature displays bilingual English Deed + Tamil Subtitle");
} else {
    console.error("FAIL: Bilingual nature display missing!");
    process.exit(1);
}

console.log("\nALL 8 TESTS PASSED SUCCESSFULLY! Universal EC Status rendering verified.");
