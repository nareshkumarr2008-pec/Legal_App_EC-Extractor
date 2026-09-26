const fs = require('fs');

// Simple DOM emulation to test selectCategory, updateCategoryInfo, updateStepPills
const elements = {};
function createEl(tag) {
    const el = {
        tagName: tag,
        id: '',
        className: '',
        innerHTML: '',
        textContent: '',
        classList: {
            classes: new Set(),
            add(c) { this.classes.add(c); el.className = Array.from(this.classes).join(' '); },
            remove(c) { this.classes.delete(c); el.className = Array.from(this.classes).join(' '); },
            contains(c) { return this.classes.has(c); }
        },
        children: [],
        appendChild(child) { this.children.push(child); },
        setAttribute(k, v) { this[k] = v; }
    };
    return el;
}

// Mock document
const document = {
    getElementById(id) {
        if (!elements[id]) elements[id] = createEl('div');
        return elements[id];
    },
    querySelectorAll(sel) {
        return Object.values(elements);
    }
};

const lucide = { createIcons: () => {} };

const DEFAULT_CATEGORIES = [
    {"id": "sale_deed", "name": "Sale deed / title deed", "tamil_name": "கிரையப் பத்திரம் / தாய் பத்திரம்", "key_fields": ["Vendor Details", "Purchaser Details", "History / Previous Owner Details", "Schedule of Property", "Survey Number / S No", "Land Extent"]},
    {"id": "patta", "name": "Patta document", "tamil_name": "பட்டா ஆவணம் (கிராமம் & நகரம் TSLR)", "key_fields": ["Patta Number", "Pattadhar / Owner Name", "Survey Number / S No", "Extent", "Village / Taluk / District", "TSLR Town Survey No"]}
];

let state = {
    categories: DEFAULT_CATEGORIES,
    selectedCategoryId: "sale_deed"
};

function updateCategoryInfo(catId) {
    const cat = state.categories.find(c => c.id === catId);
    if (!cat) return;

    const titleEl = document.getElementById("selected-cat-title");
    const tamilEl = document.getElementById("selected-cat-tamil");
    if (titleEl) titleEl.textContent = `Selected: ${cat.name}`;
    if (tamilEl) tamilEl.textContent = cat.tamil_name;

    const tagsContainer = document.getElementById("selected-cat-tags");
    if (tagsContainer) {
        tagsContainer.children = [];
        (cat.key_fields || []).slice(0, 6).forEach((f, idx) => {
            const card = createEl("div");
            card.className = "property-field-card";
            card.innerHTML = `<span class="idx">${idx + 1}</span><span>${f}</span>`;
            tagsContainer.appendChild(card);
        });
    }
}

function updateStepPills(step) {
    const b1 = document.getElementById("step-badge-1");
    const b2 = document.getElementById("step-badge-2");
    const b3 = document.getElementById("step-badge-3");
    const r1 = document.getElementById("step-rail-1");
    const r2 = document.getElementById("step-rail-2");

    if (step === 1) {
        b1.className = "stepper-badge stepper-badge-active";
        b2.className = "stepper-badge stepper-badge-pending";
        b3.className = "stepper-badge stepper-badge-pending";
        r1.className = "stepper-rail";
        r2.className = "stepper-rail";
    } else if (step === 2) {
        b1.className = "stepper-badge stepper-badge-completed";
        b2.className = "stepper-badge stepper-badge-active";
        b3.className = "stepper-badge stepper-badge-pending";
        r1.className = "stepper-rail completed";
        r2.className = "stepper-rail";
    } else if (step === 3) {
        b1.className = "stepper-badge stepper-badge-completed";
        b2.className = "stepper-badge stepper-badge-completed";
        b3.className = "stepper-badge stepper-badge-active";
        r1.className = "stepper-rail completed";
        r2.className = "stepper-rail completed";
    }
}

// Run tests
console.log('Testing initial category info for sale_deed...');
updateCategoryInfo('sale_deed');
console.log('Title:', document.getElementById('selected-cat-title').textContent);
console.log('Tags count:', document.getElementById('selected-cat-tags').children.length);

console.log('\nTesting switch to patta...');
updateCategoryInfo('patta');
console.log('Title:', document.getElementById('selected-cat-title').textContent);
console.log('Tags count:', document.getElementById('selected-cat-tags').children.length);

console.log('\nTesting stepper transitions...');
updateStepPills(1);
console.log('Step 1 -> b1:', elements['step-badge-1'].className, '| r1:', elements['step-rail-1'].className);
updateStepPills(2);
console.log('Step 2 -> b1:', elements['step-badge-1'].className, '| b2:', elements['step-badge-2'].className, '| r1:', elements['step-rail-1'].className);
updateStepPills(3);
console.log('Step 3 -> b1:', elements['step-badge-1'].className, '| b2:', elements['step-badge-2'].className, '| b3:', elements['step-badge-3'].className, '| r1:', elements['step-rail-1'].className, '| r2:', elements['step-rail-2'].className);

const allOk = elements['step-badge-3'].className === 'stepper-badge stepper-badge-active' && elements['step-rail-2'].className === 'stepper-rail completed';
console.log(`\nINTERACTION TEST RESULT: ${allOk ? 'PASSED' : 'FAILED'}`);
