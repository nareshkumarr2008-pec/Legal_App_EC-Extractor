const fs = require('fs');

console.log('=== VERIFYING CATEGORY CARD COLOR THEMES & REMOVAL OF TICKS ===\n');

const html = fs.readFileSync('static/index.html', 'utf8');
const css = fs.readFileSync('static/style.css', 'utf8');
const js = fs.readFileSync('static/app.js', 'utf8');

const categories = [
    { id: 'sale_deed', name: 'Sale deed', color: '#2563EB' },
    { id: 'patta', name: 'Patta document', color: '#059669' },
    { id: 'parent_docs', name: 'Parent docs', color: '#4F46E5' },
    { id: 'ec', name: 'EC', color: '#7C3AED' },
    { id: 'tslr', name: 'TSLR document', color: '#0284C7' },
    { id: 'rera', name: 'Rera certificate', color: '#0D9488' },
    { id: 'loan_docs', name: 'Loan documents', color: '#D97706' }
];

const checks = [
    // 1. Tick mark removal
    ['No cat-card-check elements in static/index.html', !html.includes('cat-card-check')],
    ['No cat-card-check element in static/app.js dynamic template', !js.includes('cat-card-check')],
    ['CSS has display: none !important for .cat-card-check', css.includes('.cat-card-check') && css.includes('display: none !important;')],

    // 2. Individual Category Active Highlighting
    ...categories.map(cat => [
        `Category '${cat.id}' has individual active border color (${cat.color}) in CSS`,
        css.includes(`.cat-card[data-category="${cat.id}"].cat-card-active`) &&
        css.includes(cat.color)
    ]),

    // 3. Active Elevation
    ['Active cards have elevated translateY(-3px)', css.includes('.cat-card.cat-card-active') && css.includes('transform: translateY(-3px) !important;')],

    // 4. Cache buster
    ['Cache busters updated to v=73.0 in index.html', html.includes('style.css?v=73.0') && html.includes('app.js?v=73.0')]
];

let allPassed = true;
checks.forEach(([desc, ok], i) => {
    console.log(`[${String(i + 1).padStart(2, '0')}] ${ok ? '✓ PASS' : '✗ FAIL'}: ${desc}`);
    if (!ok) allPassed = false;
});

console.log(`\n======================================================`);
console.log(`CATEGORY HIGHLIGHT TEST RESULT: ${allPassed ? 'ALL CHECKS PASSED SUCCESSFULLY!' : 'FAILURES DETECTED'}`);
console.log(`======================================================\n`);

process.exit(allPassed ? 0 : 1);
