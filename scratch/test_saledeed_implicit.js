// Node script to test Sale Deed implicit details & arrow toggles
const fs = require('fs');

const appJsCode = fs.readFileSync('static/app.js', 'utf-8');

class ClassList {
    constructor() {
        this.classes = new Set();
    }
    add(...cls) { cls.forEach(c => this.classes.add(c)); }
    remove(...cls) { cls.forEach(c => this.classes.delete(c)); }
    contains(c) { return this.classes.has(c); }
    toString() { return Array.from(this.classes).join(' '); }
}

class MockElement {
    constructor(tag = 'div') {
        this.tagName = tag.toUpperCase();
        this.id = '';
        this.className = '';
        this.classList = new ClassList();
        this.children = [];
        this._innerHTML = '';
        this.textContent = '';
    }

    set innerHTML(html) {
        this._innerHTML = html;
        const idMatches = html.matchAll(/id="([^"]+)"/g);
        for (const m of idMatches) {
            const el = new MockElement();
            el.id = m[1];
            const regex = new RegExp(`id="${m[1]}"[^>]*class="([^"]*)"`);
            const classMatch = html.match(regex);
            if (classMatch) {
                el.className = classMatch[1];
                classMatch[1].split(/\s+/).filter(Boolean).forEach(c => el.classList.add(c));
            }
            mockElementsById[m[1]] = el;
        }
    }
    get innerHTML() { return this._innerHTML; }
    appendChild(child) { this.children.push(child); }
}

const mockElementsById = {};

global.document = {
    createElement: (tag) => new MockElement(tag),
    getElementById: (id) => mockElementsById[id] || null,
    addEventListener: () => {},
    querySelectorAll: (selector) => {
        if (selector === '.sale-deed-card-body') return Object.values(mockElementsById).filter(el => el.id.endsWith('-body'));
        if (selector === '.sale-deed-card-chevron') return Object.values(mockElementsById).filter(el => el.id.endsWith('-chevron'));
        if (selector === '.sale-deed-card') return Object.values(mockElementsById).filter(el => el.id.startsWith('sale-deed-card-') && !el.id.includes('-body') && !el.id.includes('-chevron'));
        return [];
    }
};
global.window = global;
global.state = { currentResult: { extraction: { fields: {} } } };
global.escapeHtml = (s) => s ? String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;') : '';
global.lucide = { createIcons: () => {} };

eval(appJsCode);

const container = new MockElement('div');
const sampleFields = {
    document_number: { value: "Doc No. 3978 of 2010 (Book 1)" },
    registration_date: { value: "22-11-2010" },
    sro_details: { value: "SRO Kodambakkam" },
    purchaser_details: { value: "Mr. M.G. NAAGESH, Son of Late M.N. Gopal, residing at No.6/2, Sri Ramar St" },
    history_previous_owner: { value: "Mr. R. Parthasarathy, Represented by POA: Mr. V. Saravanan" },
    previous_doc_reference: { value: "Doc No. 7126 of 1995" },
    survey_number: { value: "New Survey No. 78 of Block No. 1" },
    village_taluk_district: { value: "No. 109 Puliyur Village / Egmore Nungambakkam Taluk / Chennai District" },
    land_extent: { value: "Two Grounds and 2130 sq.ft" },
    apartment_uds_floor: { value: "UDS: 768 sq.ft | Built-up Area: 907 sq.ft" },
    flat_details: { value: "Flat No. A-2, Ground Floor, Apollo Twins" },
    land_classification: { value: "House Site / Residential" },
    boundaries: { north: "40 Feet Road", south: "Plot No. 12", east: "Remaining Land", west: "Passage" }
};

renderSaleDeedFieldsLayout(sampleFields, container);

console.log("=== CHECKING ALL 8 DETAIL CARDS (INCLUDING TITLE CHAIN) ARE IMPLICIT (HIDDEN) BY DEFAULT ===");
const expected8Cards = [
    'sale-deed-card-title-chain',
    'sale-deed-card-purchaser',
    'sale-deed-card-prev-owner',
    'sale-deed-card-survey',
    'sale-deed-card-extent',
    'sale-deed-card-flat',
    'sale-deed-card-boundaries',
    'sale-deed-card-sro'
];

let allImplicitOnLoad = true;
expected8Cards.forEach(id => {
    const cardEl = mockElementsById[id];
    const bodyEl = mockElementsById[`${id}-body`];
    const chevronEl = mockElementsById[`${id}-chevron`];
    if (!cardEl) console.error(`Missing card: ${id}`);
    if (!bodyEl) console.error(`Missing body: ${id}-body`);
    if (!chevronEl) console.error(`Missing chevron: ${id}-chevron`);

    const isHidden = bodyEl && bodyEl.classList.contains('hidden');
    console.log(`Card: ${id.padEnd(28)} | Body implicit (hidden): ${isHidden}`);
    if (!isHidden) allImplicitOnLoad = false;
});

console.log(`\nAll 8 detail cards implicit on load: ${allImplicitOnLoad}`);

// Test individual toggle on Title Conveyance Chain
console.log("\n=== TEST 1: TOGGLE ARROW ON TITLE CONVEYANCE CHAIN CARD ===");
window.toggleSaleDeedCard('sale-deed-card-title-chain');
const chainOpen = !mockElementsById['sale-deed-card-title-chain-body'].classList.contains('hidden');
const chainChevronRotated = mockElementsById['sale-deed-card-title-chain-chevron'].classList.contains('rotate-90');
console.log(`Title Chain card body opened: ${chainOpen} | Chevron rotated 90°: ${chainChevronRotated}`);

// Test toggle back
console.log("\n=== TEST 2: TOGGLE TITLE CONVEYANCE CHAIN BACK TO IMPLICIT ===");
window.toggleSaleDeedCard('sale-deed-card-title-chain');
const chainClosed = mockElementsById['sale-deed-card-title-chain-body'].classList.contains('hidden');
const chainChevronReset = !mockElementsById['sale-deed-card-title-chain-chevron'].classList.contains('rotate-90');
console.log(`Title Chain card body closed: ${chainClosed} | Chevron reset: ${chainChevronReset}`);

// Test Expand All Details
console.log("\n=== TEST 3: EXPAND ALL DETAILS VIA MASTER ARROW ===");
window.toggleAllSaleDeedCards();
const allOpen = expected8Cards.every(id => !mockElementsById[`${id}-body`].classList.contains('hidden'));
const allChevronsRotated = expected8Cards.every(id => mockElementsById[`${id}-chevron`].classList.contains('rotate-90'));
const masterTextCollapse = mockElementsById['sale-deed-toggle-all-text'].textContent === 'Collapse All Details';
const masterChevron180 = mockElementsById['sale-deed-toggle-all-chevron'].classList.contains('rotate-180');
console.log(`All 8 card bodies open: ${allOpen}`);
console.log(`All 8 chevrons rotated: ${allChevronsRotated}`);
console.log(`Master text is "Collapse All Details": ${masterTextCollapse}`);
console.log(`Master chevron rotated 180°: ${masterChevron180}`);

// Test Collapse All Details
console.log("\n=== TEST 4: COLLAPSE ALL DETAILS BACK TO IMPLICIT ===");
window.toggleAllSaleDeedCards();
const allClosedAgain = expected8Cards.every(id => mockElementsById[`${id}-body`].classList.contains('hidden'));
const allChevronsResetAgain = expected8Cards.every(id => !mockElementsById[`${id}-chevron`].classList.contains('rotate-90'));
const masterTextExpand = mockElementsById['sale-deed-toggle-all-text'].textContent === 'Expand All Details';
const masterChevronReset = !mockElementsById['sale-deed-toggle-all-chevron'].classList.contains('rotate-180');
console.log(`All 8 card bodies closed again: ${allClosedAgain}`);
console.log(`All 8 chevrons reset again: ${allChevronsResetAgain}`);
console.log(`Master text is "Expand All Details": ${masterTextExpand}`);
console.log(`Master chevron reset: ${masterChevronReset}`);

if (allImplicitOnLoad && chainOpen && chainClosed && allOpen && allClosedAgain) {
    console.log("\n>>> ALL TESTS PASSED SUCCESSFULLY! Title chain and all details are implicit by default, arrow toggles show details! <<<\n");
} else {
    console.error("\n>>> TEST FAILED! <<<");
    process.exit(1);
}
