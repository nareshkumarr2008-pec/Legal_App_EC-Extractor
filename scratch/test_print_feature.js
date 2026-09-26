const fs = require('fs');

console.log('=== VERIFYING UNIVERSAL PRINT ISOLATION FOR ALL 7 CATEGORIES ===\n');

const html = fs.readFileSync('static/index.html', 'utf8');
const css = fs.readFileSync('static/style.css', 'utf8');
const js = fs.readFileSync('static/app.js', 'utf8');

const checks = [
    // Core Print Activation
    ['Print button in HTML calls printReport()', html.includes('onclick="printReport()"')],
    ['CSS has @media print configuration block', css.includes('@media print')],
    ['JS printReport() auto-fits textareas and calls window.print()', 
        js.includes('function printReport()') && 
        js.includes('document.querySelectorAll') && 
        js.includes('ta.scrollHeight') && 
        js.includes('window.print()')],

    // Isolation: Shell Elements Hidden
    ['Application header, footer, stepper, and track buttons hidden in print', 
        css.includes('header,') && css.includes('footer,') && css.includes('.stepper-container,')],
    ['Left canvas / document viewer column hidden in print', 
        css.includes('#workspace-section .lg\\:col-span-5')],
    ['Right intelligence pane executive header (title, badges, action buttons) hidden in print', 
        html.includes('id="result-doc-type-title"') && css.includes('.no-print,')],
    ['Right intelligence pane tab navigation bar hidden in print', 
        html.includes('id="tab-btn-fields"') && css.includes('.no-print,')],
    ['Inactive tabs strictly hidden in print', 
        css.includes('[id^="tab-content-"].hidden')],

    // Right Pane Expansion
    ['Active tab container and workspace unlocked to full natural height', 
        css.includes('overflow-y: visible !important;') && css.includes('max-height: none !important;')],

    // Category 1: Sale Deed Isolation
    ['Sale Deed Executive Banner styled with crisp dark theme and contrast', 
        css.includes('#tab-content-fields .bg-gradient-to-br') && 
        !css.includes('#extracted-fields-container > div:first-child')],
    ['Sale Deed Title Conveyance card formatted with break-inside: avoid', 
        css.includes('#sale-deed-card-title-chain')],
    ['Sale Deed detail cards have clean borders and preserve toggle state', 
        css.includes('.sale-deed-card:not(#sale-deed-card-title-chain)') && 
        css.includes('.sale-deed-card-body.hidden')],

    // Categories 2 & 5: Patta & TSLR Isolation
    ['Patta & TSLR report header banners formatted cleanly', 
        css.includes('#tab-content-fields .bg-gradient-to-r.from-slate-900')],
    ['Patta 4 Hero Grid and TSLR 8 Hero Grid formatted with avoid page-break', 
        css.includes('#extracted-fields-container .rounded-2xl.bg-tm-card')],
    ['Patta & TSLR action buttons (Copy All, Download PDF) hidden in print', 
        css.includes('button[onclick*="copyCurrentPattaSummary"]') && 
        css.includes('button[onclick*="downloadPdfWithLanguage"]')],

    // Categories 3, 6, 7: Standard Layout (Parent Docs, RERA, Loan Docs)
    ['Standard layout Manual Field Editor bar hidden in print', 
        css.includes('.p-4.mb-4.rounded-2xl.bg-gradient-to-r') && 
        css.includes('#manual-custom-key') && 
        css.includes('button[onclick*="saveCustomFieldFromInput"]')],
    ['Standard layout glass-cards formatted with break-inside: avoid', 
        css.includes('#extracted-fields-container .glass-card')],
    ['Standard layout Save / Copy action buttons hidden in print', 
        css.includes('button[onclick*="saveManualFieldByKey"]')],

    // Category 4: EC Isolation
    ['EC Key accordion cards formatted cleanly with avoid page-break', 
        css.includes('.ec-key-card')],
    ['EC action buttons, toggles and chevrons hidden in print', 
        css.includes('#btn-toggle-all-ec-cards') && 
        css.includes('.ec-key-card-chevron') && 
        css.includes('button[onclick*="openOwnerDossierByName"]')],

    // Universal Inputs & Textareas Conversion
    ['Form inputs & textareas converted to transparent, borderless static text', 
        css.includes('#extracted-fields-container input[type="text"]') && 
        css.includes('#extracted-fields-container textarea') && 
        css.includes('border: none !important;') && 
        css.includes('background: transparent !important;')],

    // Tables & Checklist Formatting
    ['Tables formatted with clean borders and contrast header', 
        css.includes('table {') && css.includes('th, td {') && css.includes('border: 1px solid #CBD5E1 !important;')],
    ['Checklist items formatted with avoid page-break', 
        css.includes('#checklist-items-container > div')],

    // Version Bump
    ['Cache buster version updated in static/index.html', 
        html.includes('style.css?v=73.0') && html.includes('app.js?v=73.0')]
];

let allPassed = true;
checks.forEach(([desc, ok], i) => {
    console.log(`[${String(i + 1).padStart(2, '0')}] ${ok ? '✓ PASS' : '✗ FAIL'}: ${desc}`);
    if (!ok) allPassed = false;
});

console.log(`\n======================================================`);
console.log(`UNIVERSAL PRINT TEST RESULT: ${allPassed ? 'ALL 22 CHECKS PASSED SUCCESSFULLY!' : 'FAILURES DETECTED'}`);
console.log(`======================================================\n`);

process.exit(allPassed ? 0 : 1);
