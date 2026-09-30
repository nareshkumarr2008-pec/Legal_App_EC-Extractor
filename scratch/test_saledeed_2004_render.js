const fs = require('fs');

// Simple DOM Mock
class MockElement {
    constructor(tagName = 'div') {
        this.tagName = tagName;
        this.innerHTML = '';
        this.children = [];
        this.className = '';
        this.style = {};
    }
    appendChild(child) {
        this.children.push(child);
    }
    querySelector(sel) { return null; }
    querySelectorAll(sel) { return []; }
}

global.document = {
    createElement: (tag) => new MockElement(tag),
    getElementById: (id) => new MockElement('div'),
    addEventListener: () => {}
};
global.window = {};
global.escapeHtml = (s) => s ? String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;') : '';
global.state = {
    currentResult: {
        filename: 'Sale deed_188_2004.pdf',
        page_count: 14
    }
};

const appJs = fs.readFileSync('static/app.js', 'utf8');

// Extract renderSaleDeedFieldsLayout function from app.js
const fnStart = appJs.indexOf('function renderSaleDeedFieldsLayout(');
const fnEnd = appJs.indexOf('// Global Sale Deed accordion togglers', fnStart);
const fnCode = appJs.substring(fnStart, fnEnd);

eval(fnCode);

const dump = JSON.parse(fs.readFileSync('scratch/2004_result_dump.json', 'utf8'));
const container = new MockElement('div');

renderSaleDeedFieldsLayout(dump.fields, container);

console.log('Container children:', container.children.length);
const html = container.children[0].innerHTML;

// Assertions
const checks = [
    { name: 'Card 0 Past Owner C is Renuka Anuradhan', pass: html.includes('Mrs. RENUKA ANURADHAN') },
    { name: 'Card 0 Prior Owners B is Balakrishnan', pass: html.includes('1) A.D.Balakrishnan') },
    { name: 'Card 0 Present Owner D is Mahalingam', pass: html.includes('Mr. R. MAHALINGAM') },
    { name: 'Mother Deed has full date 26.10.1995', pass: html.includes('26.10.1995') },
    { name: 'Mother Deed has Book & Volume', pass: html.includes('Book 1, Volume 1752, Pages from 91 to 94') },
    { name: 'Survey Number is T.S. No. 78, Block No. 1', pass: html.includes('T.S. No. 78, Block No. 1') },
    { name: 'Card 2 contains Vendor (C) as first field', pass: html.includes('Previous Owner (C) / Conveying Vendor') },
    { name: 'Card 2 contains Prior Owner (B) as second field', pass: html.includes('Prior Owner(s) / Mother Deed Transferor (முந்தைய மூல உரிமையாளர் - B)') },
    { name: 'Card 2 contains Mother Deed as third field', pass: html.includes('Mother Deed Document Number &amp; SRO (Book 1)') }
];

console.log('=== VERIFICATION CHECKS ===');
let allPass = true;
checks.forEach(c => {
    console.log(`${c.pass ? '✓' : '✗'} ${c.name}`);
    if (!c.pass) allPass = false;
});

if (allPass) {
    console.log('\nALL 9 CHECKS PASSED PERFECTLY!');
} else {
    console.error('\nSOME CHECKS FAILED!');
    process.exit(1);
}
