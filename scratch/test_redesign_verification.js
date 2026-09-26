const fs = require('fs');
const html = fs.readFileSync('static/index.html', 'utf8');

console.log('=== HTML STATIC VALIDATION ===');
const checks = [
    ['Brand lockup "PlotChoice Legal App"', html.includes('PlotChoice') && html.includes('Legal App')],
    ['Tamil Nadu Platform subtitle', html.includes('Tamil Nadu Legal Document Intelligence Platform')],
    ['Segmented track switcher bar', html.includes('segmented-track-bar')],
    ['Demo quick links pill group', html.includes('loadBundle(\'standard_sale_bundle\')') && html.includes('loadBundle(\'rural_patta_bundle\')')],
    ['Connected process stepper container', html.includes('stepper-container')],
    ['Step 1 badge & rail 1', html.includes('step-badge-1') && html.includes('step-rail-1')],
    ['Step 2 badge & rail 2', html.includes('step-badge-2') && html.includes('step-rail-2')],
    ['Step 3 badge', html.includes('step-badge-3')],
    ['Category grid (#category-grid)', html.includes('id="category-grid"')],
    ['Active category info summary drawer', html.includes('id="active-category-info"')],
    ['6-column property grid container (#selected-cat-tags)', html.includes('id="selected-cat-tags"') && html.includes('lg:grid-cols-6')],
    ['7 Category Cards present in HTML', [
        'cat-card-sale_deed', 'cat-card-patta', 'cat-card-parent_docs', 
        'cat-card-ec', 'cat-card-tslr', 'cat-card-rera', 'cat-card-loan_docs'
    ].every(id => html.includes(id))],
    ['"Ares -> Sq.Ft" removed from category cards', !html.substring(html.indexOf('id="category-grid"'), html.indexOf('id="active-category-info"')).includes('Ares')],
    ['"5-Yr Trace" removed from category cards', !html.substring(html.indexOf('id="category-grid"'), html.indexOf('id="active-category-info"')).includes('5-Yr')],
    ['"8 Fields" removed from category cards', !html.substring(html.indexOf('id="category-grid"'), html.indexOf('id="active-category-info"')).includes('8 Fields')]
];

let allPassed = true;
checks.forEach(([desc, ok]) => {
    console.log(`${ok ? '✓ PASS' : '✗ FAIL'}: ${desc}`);
    if (!ok) allPassed = false;
});

console.log('\n=== CSS VALIDATION ===');
const css = fs.readFileSync('static/style.css', 'utf8');
const cssChecks = [
    ['Segmented track bar CSS', css.includes('.segmented-track-bar') && css.includes('.track-tab-btn')],
    ['Connected stepper CSS', css.includes('.stepper-container') && css.includes('.stepper-rail') && css.includes('.stepper-badge-active')],
    ['Refined cat-card CSS with category colors', css.includes('.cat-card') && css.includes('.cat-card.cat-card-active') && css.includes('data-category="sale_deed"')],
    ['Property field card CSS', css.includes('.property-field-card')]
];
cssChecks.forEach(([desc, ok]) => {
    console.log(`${ok ? '✓ PASS' : '✗ FAIL'}: ${desc}`);
    if (!ok) allPassed = false;
});

console.log('\n=== JS LOGIC VALIDATION ===');
const appJs = fs.readFileSync('static/app.js', 'utf8');
const jsChecks = [
    ['updateStepPills handles rails and badges', appJs.includes('step-badge-1') && appJs.includes('step-rail-1') && appJs.includes('stepper-badge-completed')],
    ['updateCategoryInfo generates property-field-card', appJs.includes('property-field-card')],
    ['renderCategoriesGrid renders clean category cards without tick marks', !appJs.includes('cat-card-check')],
    ['resetWorkspace resets stepper to step 1', appJs.includes('updateStepPills(1)')]
];
jsChecks.forEach(([desc, ok]) => {
    console.log(`${ok ? '✓ PASS' : '✗ FAIL'}: ${desc}`);
    if (!ok) allPassed = false;
});

console.log(`\nOVERALL STATUS: ${allPassed ? 'ALL CHECKS PASSED!' : 'SOME CHECKS FAILED'}`);
