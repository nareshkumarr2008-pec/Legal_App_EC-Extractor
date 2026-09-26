const fs = require('fs');

const html = fs.readFileSync('static/index.html', 'utf8');

const checks = [
    ['active-category-info id removed', !html.includes('id="active-category-info"')],
    ['selected-cat-title id removed', !html.includes('id="selected-cat-title"')],
    ['selected-cat-tamil id removed', !html.includes('id="selected-cat-tamil"')],
    ['selected-cat-tags id removed', !html.includes('id="selected-cat-tags"')],
    ['Target Verification Scope text removed', !html.includes('Target Verification Scope')],
    ['Verified Legal Entities text removed', !html.includes('Verified Legal Entities')],
    ['Category grid intact', html.includes('id="category-grid"')],
    ['Category cards #01 to #07 intact', html.includes('id="cat-card-sale_deed"') && html.includes('id="cat-card-loan_docs"')]
];

let allPassed = true;
checks.forEach(([name, passed]) => {
    console.log(`${passed ? '✓ PASS' : '✗ FAIL'}: ${name}`);
    if (!passed) allPassed = false;
});

if (!allPassed) {
    process.exit(1);
}
console.log('\nAll checks passed successfully.');
