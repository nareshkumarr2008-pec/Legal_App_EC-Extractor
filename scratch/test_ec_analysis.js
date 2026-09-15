const fs = require('fs');
const js = fs.readFileSync('static/app.js', 'utf8');

// Mock browser DOM
let innerHTML = '';
const elements = {
    'ec-analysis-container': {
        set innerHTML(val) { innerHTML = val; },
        get innerHTML() { return innerHTML; }
    },
    'tab-btn-ec-analysis': {
        classList: {
            add: () => {},
            remove: () => {}
        }
    }
};

const document = {
    getElementById: (id) => elements[id] || null
};

const state = {
    selectedCategoryId: 'ec',
    currentResult: null
};
global.window = global;
global.lucide = { createIcons: () => {} };

function escapeHtml(str) {
    if (!str) return '';
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
}

// Extract function renderECAnalysisTab
const start = js.indexOf('function renderECAnalysisTab(');
const end = js.indexOf('function renderOwnersTab(');
const funcCode = js.substring(start, end);

eval(funcCode);

const payload = JSON.parse(fs.readFileSync('scratch_test_payload.json', 'utf8'));
console.log('Testing renderECAnalysisTab with scratch_test_payload.json...');
try {
    renderECAnalysisTab(payload);
    console.log('Populated test Success! Length of innerHTML:', innerHTML.length);
} catch (e) {
    console.error('Error in populated renderECAnalysisTab:', e);
}

try {
    renderECAnalysisTab(null);
    console.log('Null payload test Success! Length of innerHTML:', innerHTML.length);
    console.log('Null preview:', innerHTML.trim().substring(0, 150));
} catch (e) {
    console.error('Error in null renderECAnalysisTab:', e);
}
