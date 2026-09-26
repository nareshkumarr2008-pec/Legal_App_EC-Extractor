const fs = require('fs');

const html = fs.readFileSync('static/index.html', 'utf8');

const requiredIds = [
    'file-input',
    'dropzone',
    'dropzone-inner',
    'doc-category-select',
    'ocr-lang-select',
    'ocr-pages-select',
    'ocr-custom-page-range',
    'btn-process',
    'processing-loader',
    'ocr-error-banner'
];

let allPassed = true;
console.log('--- Step 2 ID Presence Check ---');
requiredIds.forEach(id => {
    const hasId = html.includes(`id="${id}"`);
    console.log(`${hasId ? '✓ PASS' : '✗ FAIL'}: ID #${id} exists`);
    if (!hasId) allPassed = false;
});

// Check single line elements
const singleLineChecks = [
    ['Unified single line row container', html.includes('flex flex-col lg:flex-row items-stretch lg:items-center gap-2')],
    ['Dropzone single line height', html.includes('h-10 min-h-[40px]')],
    ['Target Document Type in line', html.includes('id="doc-category-select"')],
    ['OCR Model in line', html.includes('id="ocr-lang-select"')],
    ['Page Scope in line', html.includes('id="ocr-pages-select"')],
    ['Start OCR button in line', html.includes('id="btn-process"')],
    ['Streamlined header with ready badge', html.includes('Step 02 &bull; Ready')],
    ['Browse button with icon', html.includes('Browse') && html.includes('data-lucide="file-up"')],
    ['Category cards intact', html.includes('id="cat-card-sale_deed"') && html.includes('id="cat-card-loan_docs"')]
];

console.log('\n--- Single Line Layout Checks ---');
singleLineChecks.forEach(([name, passed]) => {
    console.log(`${passed ? '✓ PASS' : '✗ FAIL'}: ${name}`);
    if (!passed) allPassed = false;
});

if (!allPassed) {
    process.exit(1);
}
console.log('\nAll Step 2 Single-Line layout checks passed successfully.');
