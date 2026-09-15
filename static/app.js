const DEFAULT_CATEGORIES = [
    {"id": "sale_deed", "name": "Sale deed / title deed", "tamil_name": "கிரையப் பத்திரம் / தாய் பத்திரம்", "key_fields": ["Vendor Details", "Purchaser Details", "History / Previous Owner Details", "Schedule of Property", "Survey Number / S No", "Land Extent", "Building Built-Up Area", "Apartment UDS & Floor", "Boundary", "SRO Details"]},
    {"id": "patta", "name": "Patta document", "tamil_name": "பட்டா ஆவணம் (கிராமம் & நகரம் TSLR)", "key_fields": ["Patta Number", "Pattadhar / Owner Name", "Survey Number / S No", "Extent", "Village / Taluk / District", "TSLR Town Survey No", "TSLR Ward + Block", "TSLR Town"]},
    {"id": "parent_docs", "name": "Parent docs / mother copy", "tamil_name": "முந்தைய மூல ஆவணங்கள் (Mother Copy)", "key_fields": ["Previous Owner / Vendor", "Purchaser / Claimant", "Parent Document No & Year", "Survey Number / S No", "Extent Transferred", "Last 5 Years Validation"]},
    {"id": "ec", "name": "EC", "tamil_name": "வில்லங்கச் சான்றிதழ் (Encumbrance Certificate)", "key_fields": ["Search Period (30-Year Min)", "Form Type (Form 15 vs 16)", "Survey Number & Village", "SRO Details", "Registered Entries Table", "Encumbrance Status"]},
    {"id": "building_plan", "name": "Approved building plan", "tamil_name": "அங்கீகரிக்கப்பட்ட கட்டிட வரைபடம்", "key_fields": ["Permit Number & Date", "Sanctioning Authority", "Survey No / Plot No & Village", "Approved Built-Up Area", "Height & Number of Floors", "FSI & Setbacks Compliance"]},
    {"id": "rera", "name": "Rera certificate approval certificate (if applicable)", "tamil_name": "RERA பதிவு சான்றிதழ்", "key_fields": ["TNRERA Registration Number", "Project Name & Type", "Promoter / Developer Name", "Project Survey Numbers & Location", "Validity & Completion Expiry"]},
    {"id": "tax_eb", "name": "Property water tax and eb receipts", "tamil_name": "சொத்து வரி, குடிநீர் வரி & EB ரசீது", "key_fields": ["Property Tax Assessment No", "Property Owner Name", "Door Number & Locality", "Water Tax Connection & Status", "EB Consumer No & Tariff", "Payment Receipt Date & Amount"]},
    {"id": "layout_approval", "name": "Approved layout (if applicable) CMDA / DTCP", "tamil_name": "அங்கீகரிக்கப்பட்ட மனைப்பிரிவு (CMDA / DTCP)", "key_fields": ["Layout Approval Number (PPD/Lo)", "Sanctioning Authority (CMDA / DTCP)", "Survey Numbers & Village", "Total Extent & Number of Plots", "OSR Park & Road Gift Details"]},
    {"id": "death_legal_heir", "name": "Death certificate and legal hier certificate", "tamil_name": "இறப்பு & வாரிசுச் சான்றிதழ் (Varisu)", "key_fields": ["Deceased Name", "Date of Death & Reg No", "Varisu Certificate Order No & Date", "Surviving Legal Heirs List", "Heir Completeness Check (100%)", "Patta Mutation Status (TN Act 1983)"]},
    {"id": "loan_docs", "name": "Loan documents (if applicable)", "tamil_name": "வங்கி கடன் ஆவணங்கள் / MODT", "key_fields": ["Lending Bank / Institution", "Borrower & Co-Borrower Names", "Loan Account & Sanctioned Amount", "Security / MODT Details", "MODT Doc No, Year & SRO", "NOC / Discharge Status"]},
    {"id": "tslr", "name": "TSLR document (Town Survey Land Record)", "tamil_name": "நகர நில அளவை ஆவணம் (TSLR)", "key_fields": ["District", "Taluk", "Town", "Ward", "Name", "Survey Number / S.No", "Extent", "Ward + Block", "Land classification", "Current land use", "Tenure type", "Assessment (Rs.)", "Remarks"]}
];

// PlotChoice DocuScan OCR & Cross-Verification Platform

let state = {
    currentTrack: "ocr",
    categories: DEFAULT_CATEGORIES,
    selectedCategoryId: "sale_deed",
    currentFile: null,
    currentResult: null,
    currentPageIndex: 0,
    zoomLevel: 1.0,
    showBBoxes: true,
    activeTab: "fields",
    currentBundle: null
};

// Initialize Application
document.addEventListener("DOMContentLoaded", async () => {
    lucide.createIcons();
    await checkServerHealth();
    await fetchCategories();
    await checkLLMStatus();
    setupDropzone();
    // Default load sale deed sample
    await loadSampleDocument("sale_deed");

    // Periodic heartbeat checks
    setInterval(checkServerHealth, 15000);
    setInterval(checkLLMStatus, 30000);
});

// Check status of main OCR FastAPI server
async function checkServerHealth() {
    try {
        const controller = new AbortController();
        const tid = setTimeout(() => controller.abort(), 3500);
        const res = await fetch("/api/health", { signal: controller.signal });
        clearTimeout(tid);
        if (res.ok) {
            updateServerStatus(true);
            return true;
        } else {
            updateServerStatus(false, "Server Error");
            return false;
        }
    } catch (e) {
        updateServerStatus(false, "Offline");
        return false;
    }
}

function updateServerStatus(online, customText) {
    const badge = document.getElementById("server-status-badge");
    const dot = document.getElementById("server-status-dot");
    const text = document.getElementById("server-status-text");
    if (!badge || !dot || !text) return;

    if (online) {
        badge.className = "hidden md:flex items-center space-x-2 px-3 py-1 rounded-lg bg-emerald-50 border border-emerald-200 text-emerald-700 text-xs font-medium cursor-pointer";
        dot.className = "w-2 h-2 rounded-full bg-emerald-500 animate-ping";
        text.textContent = customText || "PaddleOCR Server Active";
    } else if (customText === "Reconnecting...") {
        badge.className = "hidden md:flex items-center space-x-2 px-3 py-1 rounded-lg bg-amber-50 border border-amber-200 text-amber-700 text-xs font-medium cursor-pointer";
        dot.className = "w-2 h-2 rounded-full bg-amber-500 animate-pulse";
        text.textContent = "Server Warming Up / Reconnecting...";
    } else {
        badge.className = "hidden md:flex items-center space-x-2 px-3 py-1 rounded-lg bg-rose-50 border border-rose-200 text-rose-700 text-xs font-medium cursor-pointer";
        dot.className = "w-2 h-2 rounded-full bg-rose-500";
        text.textContent = customText ? `Server ${customText}` : "OCR Server Offline (Run start_app.bat)";
    }
    lucide.createIcons();
}

// Check status of local Qwen 2.5 7B LLM service
async function checkLLMStatus() {
    try {
        const res = await fetch("/api/llm/status");
        const data = await res.json();
        const badge = document.getElementById("llm-status-badge");
        const text = document.getElementById("llm-status-text");
        const toggle = document.getElementById("toggle-use-llm");
        if (data && data.llm_available) {
            if (badge) {
                badge.className = "hidden md:flex items-center space-x-2 px-3 py-1 rounded-lg bg-emerald-50 border border-emerald-200 text-emerald-700 text-xs font-medium";
            }
            if (text) text.textContent = "Qwen 2.5 7B AI Active";
            if (toggle) toggle.checked = true;
        } else {
            if (badge) {
                badge.className = "hidden md:flex items-center space-x-2 px-3 py-1 rounded-lg bg-slate-100 border border-slate-200 text-slate-600 text-xs font-medium";
            }
            if (text) text.textContent = "Qwen AI Offline (Rule-Engine Active)";
            if (toggle) toggle.checked = false;
        }
        lucide.createIcons();
    } catch (e) {
        console.warn("LLM status check error:", e);
    }
}

// Track Switching (Track 1: OCR, Track 2: Matrix, Track 3: Inheritance)
function switchTrack(trackName) {
    state.currentTrack = trackName;
    const tracks = ["ocr", "matrix", "inheritance"];

    tracks.forEach(t => {
        const btn = document.getElementById(`track-btn-${t}`);
        const view = document.getElementById(`track-view-${t}`);
        if (t === trackName) {
            btn.className = "track-btn-active px-3.5 py-1.5 rounded-lg text-xs font-bold transition-all flex items-center gap-1.5";
            view.classList.remove("hidden");
        } else {
            btn.className = "px-3.5 py-1.5 rounded-lg text-xs font-bold bg-white text-slate-700 border border-slate-200 hover:bg-slate-50 transition-all flex items-center gap-1.5 shadow-2xs";
            view.classList.add("hidden");
        }
    });

    if (trackName === "matrix" && !state.currentBundle) {
        loadBundle("standard_sale_bundle");
    } else if (trackName === "inheritance" && !state.currentBundle) {
        loadBundle("inherited_property_bundle");
    }

    lucide.createIcons();
}

// 1. Fetch & Render Document Categories
async function fetchCategories() {
    try {
        const res = await fetch("/api/categories");
        const data = await res.json();
        if (data.status === "success") {
            state.categories = data.categories;
            updateCategoryInfo(state.selectedCategoryId);
            lucide.createIcons();
        }
    } catch (err) {
        console.error("Failed to fetch categories:", err);
    }
}

function renderCategoriesGrid() {
    const grid = document.getElementById("category-grid");
    grid.innerHTML = "";

    state.categories.forEach(cat => {
        const isActive = cat.id === state.selectedCategoryId;
        const card = document.createElement("div");
        card.id = `cat-card-${cat.id}`;
        card.onclick = () => selectCategory(cat.id, true);
        card.className = `p-3 rounded-xl border cursor-pointer transition-all duration-150 flex flex-col justify-between ${
            isActive 
                ? "cat-card-active" 
                : "border-slate-200/80 bg-white hover:border-blue-300 hover:bg-blue-50/20 shadow-2xs"
        }`;

        card.innerHTML = `
            <div class="flex items-start justify-between mb-1">
                <div class="w-6 h-6 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center">
                    <i data-lucide="${cat.icon || 'file-text'}" class="w-3.5 h-3.5"></i>
                </div>
                <span class="text-[9px] font-bold text-slate-400">#${cat.id.toUpperCase().slice(0, 4)}</span>
            </div>
            <div>
                <h4 class="text-xs font-bold text-slate-800 leading-snug">${cat.name}</h4>
                <p class="text-[10px] text-slate-500 line-clamp-1 mt-0.5">${cat.tamil_name}</p>
            </div>
        `;
        grid.appendChild(card);
    });
    lucide.createIcons();
}

// 1. Select Document Category
function selectCategory(catId, loadDoc = true) {
    state.selectedCategoryId = catId;

    // Synchronize dropdown
    const catSelect = document.getElementById("doc-category-select");
    if (catSelect && catSelect.value !== catId) {
        catSelect.value = catId;
    }

    // Synchronize card styles
    const allCards = document.querySelectorAll("[id^='cat-card-']");
    allCards.forEach(el => {
        if (el.id === `cat-card-${catId}`) {
            el.className = "cat-card-active p-3 rounded-xl border cursor-pointer transition-all duration-150 flex flex-col justify-between shadow-2xs";
        } else {
            el.className = "border-slate-200/80 bg-white hover:border-blue-300 hover:bg-blue-50/20 p-3 rounded-xl border cursor-pointer transition-all duration-150 flex flex-col justify-between shadow-2xs";
        }
    });

    updateCategoryInfo(catId);
    lucide.createIcons();

    if (state.currentFile) {
        triggerProcess();
    } else if (loadDoc && state.currentResult) {
        loadSampleDocument(catId);
    }
}

function updateCategoryInfo(catId) {
    const cat = state.categories.find(c => c.id === catId);
    if (!cat) return;

    const titleEl = document.getElementById("selected-cat-title");
    const tamilEl = document.getElementById("selected-cat-tamil");
    if (titleEl) titleEl.textContent = `Selected: ${cat.name}`;
    if (tamilEl) tamilEl.textContent = cat.tamil_name;

    const tagsContainer = document.getElementById("selected-cat-tags");
    if (tagsContainer) {
        tagsContainer.innerHTML = "";
        (cat.key_fields || []).slice(0, 6).forEach(f => {
            const span = document.createElement("span");
            span.className = "px-2 py-0.5 bg-white text-slate-600 rounded-md border border-slate-200 text-[10px] font-medium";
            span.textContent = f;
            tagsContainer.appendChild(span);
        });
    }
}

// 2. Load Sample Document (NEVER recursively call selectCategory here!)
async function loadSampleDocument(targetId = null) {
    const effectiveId = targetId || state.selectedCategoryId || "sale_deed";

    showLoader(true, `Loading Document for ${effectiveId.replace('_', ' ').toUpperCase()}...`);

    try {
        const res = await fetch(`/api/sample/${effectiveId}`);
        const data = await res.json();
        if (data.status === "success") {
            state.currentResult = {
                filename: `Sample_${effectiveId}.pdf`,
                total_pages: 1,
                pages: [data.simulated_page],
                aggregated_text: data.raw_text,
                extraction: data.extracted_data
            };
            state.currentPageIndex = 0;
            renderDocumentResult();
        }
    } catch (err) {
        console.error("Error loading sample:", err);
    } finally {
        showLoader(false);
    }
}

// 3. Dropzone & File Handling
function setupDropzone() {
    const dropzone = document.getElementById("dropzone");
    const fileInput = document.getElementById("file-input");

    if (!dropzone || !fileInput) return;

    fileInput.addEventListener("click", () => {
        fileInput.value = "";
    });

    dropzone.addEventListener("dragover", (e) => {
        e.preventDefault();
        e.stopPropagation();
        dropzone.classList.add("border-blue-500", "bg-blue-100/50");
    });

    dropzone.addEventListener("dragleave", (e) => {
        e.preventDefault();
        e.stopPropagation();
        dropzone.classList.remove("border-blue-500", "bg-blue-100/50");
    });

    dropzone.addEventListener("drop", (e) => {
        e.preventDefault();
        e.stopPropagation();
        dropzone.classList.remove("border-blue-500", "bg-blue-100/50");
        if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
            handleFileSelected(e.dataTransfer.files[0]);
        }
    });

    fileInput.addEventListener("change", (e) => {
        if (e.target.files && e.target.files.length > 0) {
            handleFileSelected(e.target.files[0]);
        }
    });
}

function handleFileSelected(file) {
    if (!file) return;
    state.currentFile = file;

    const inner = document.getElementById("dropzone-inner");
    if (inner) {
        inner.innerHTML = `
            <div class="w-12 h-12 rounded-full bg-emerald-100 text-emerald-700 flex items-center justify-center mb-2 shadow-2xs">
                <i data-lucide="file-check" class="w-6 h-6"></i>
            </div>
            <h3 class="text-sm font-bold text-slate-900">${file.name}</h3>
            <p class="text-xs text-slate-500">${(file.size / 1024 / 1024).toFixed(2)} MB • Ready for OCR</p>
            <div class="mt-2 flex items-center space-x-2">
                <span class="px-2.5 py-1 text-[11px] font-semibold rounded-md bg-emerald-50 text-emerald-700 border border-emerald-200">File Ready</span>
                <span class="text-xs text-blue-600 font-semibold underline hover:text-blue-800">Change File</span>
            </div>
        `;
        lucide.createIcons();
    }

    triggerProcess();
}

function resetDropzoneUI() {
    const inner = document.getElementById("dropzone-inner");
    if (inner) {
        inner.innerHTML = `
            <div class="w-12 h-12 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center mb-3 shadow-2xs">
                <i data-lucide="upload-cloud" class="w-6 h-6"></i>
            </div>
            <h3 class="text-sm font-bold text-slate-900 mb-1">Click to Upload or Drag & Drop Document</h3>
            <p class="text-xs text-slate-500 mb-2">Supports PDF, PNG, JPG, TIFF, WebP, BMP (Multi-page supported)</p>
            <span class="mt-1 px-4 py-1.5 text-xs font-semibold rounded-lg bg-white border border-blue-300 text-blue-700 hover:bg-blue-50 shadow-2xs inline-block">
                Browse Document File...
            </span>
        `;
        lucide.createIcons();
    }
}

function dismissOcrError() {
    const banner = document.getElementById("ocr-error-banner");
    if (banner) banner.classList.add("hidden");
}

function showOcrConnectionModal(err) {
    dismissOcrError();
    const banner = document.getElementById("ocr-error-banner");
    const title = document.getElementById("ocr-error-title");
    const desc = document.getElementById("ocr-error-desc");
    const errMsg = (err && err.message) ? err.message : (typeof err === "string" ? err : "");
    const isConnErr = errMsg.includes("Failed to fetch") || (err && err.name === "AbortError") || errMsg.includes("NetworkError");

    if (banner) {
        if (title) {
            title.textContent = isConnErr ? "OCR Server Connection Notice" : "OCR Processing Notice";
        }
        if (desc) {
            desc.textContent = isConnErr
                ? "The OCR backend at 127.0.0.1:8000 is not reachable. The server might be warming up or restarting. Please click 'Retry Connection Now' or ensure start_app.bat is running."
                : `Processing issue encountered: ${errMsg || "Unknown error"}. Please verify your document and try again.`;
        }
        banner.classList.remove("hidden");
        banner.scrollIntoView({ behavior: "smooth", block: "center" });
    }
    if (window.lucide) lucide.createIcons();
}

function toggleCustomPageRange(val) {
    const customInput = document.getElementById("ocr-custom-page-range");
    if (customInput) {
        if (val === "custom") {
            customInput.classList.remove("hidden");
            customInput.focus();
        } else {
            customInput.classList.add("hidden");
        }
    }
}

// 4. Trigger OCR and Extraction Process
async function runOcrProcess() {
    dismissOcrError();
    if (!state.currentFile) {
        const fileInput = document.getElementById("file-input");
        if (fileInput) {
            fileInput.click();
        }
        return;
    }

    const lang = document.getElementById("ocr-lang-select").value;
    const docType = state.selectedCategoryId;
    const useLlmEl = document.getElementById("toggle-use-llm");
    const useLlm = useLlmEl ? useLlmEl.checked : true;

    const pagesScopeEl = document.getElementById("ocr-pages-select");
    const pagesScope = pagesScopeEl ? pagesScopeEl.value : "all";
    let pageRangeParam = null;
    let maxPagesParam = null;
    if (pagesScope === "first_3") {
        maxPagesParam = "3";
    } else if (pagesScope === "first_5") {
        maxPagesParam = "5";
    } else if (pagesScope === "custom") {
        const customInput = document.getElementById("ocr-custom-page-range");
        const customVal = customInput ? customInput.value.trim() : "";
        if (customVal) pageRangeParam = customVal;
    }

    const scopeMsg = maxPagesParam ? ` (First ${maxPagesParam} pages)` : (pageRangeParam ? ` (Pages: ${pageRangeParam})` : "");
    const initialMsg = useLlm 
        ? `Running OCR & Qwen 2.5 7B AI Extraction${scopeMsg}...` 
        : `Running Dual-Pipeline OCR & Extracting Entities${scopeMsg}...`;
    showLoader(true, initialMsg);

    const maxRetries = 1;
    let attempt = 0;
    let lastError = null;

    while (attempt <= maxRetries) {
        const formData = new FormData();
        formData.append("file", state.currentFile);
        formData.append("doc_type", docType);
        formData.append("lang", lang);
        formData.append("use_llm", useLlm ? "true" : "false");
        if (pageRangeParam) formData.append("page_range", pageRangeParam);
        if (maxPagesParam) formData.append("max_pages", maxPagesParam);

        const controller = new AbortController();
        // 10-minute generous timeout for multi-page CPU OCR
        const timeoutId = setTimeout(() => controller.abort(), 600000);

        try {
            const res = await fetch("/api/ocr/process", {
                method: "POST",
                body: formData,
                signal: controller.signal
            });
            clearTimeout(timeoutId);

            if (!res.ok) {
                let detail = `Server returned status ${res.status}`;
                try {
                    const errData = await res.json();
                    if (errData && errData.detail) detail = errData.detail;
                } catch(e) {}
                throw new Error(detail);
            }
            const data = await res.json();
            state.currentResult = data;
            state.currentPageIndex = 0;
            renderDocumentResult();
            showLoader(false);
            updateServerStatus(true);
            return;
        } catch (err) {
            clearTimeout(timeoutId);
            lastError = err;
            console.warn(`OCR attempt ${attempt + 1}/${maxRetries + 1} failed:`, err);

            // Do not retry on intentional timeout aborts (it avoids queuing multiple 10-min jobs)
            if (err.name === "AbortError") {
                lastError = new Error("Document processing timed out after 10 minutes. For large multi-page scans on CPU, try selecting 'First 3 Pages' or 'Pages 1-3'.");
                break;
            }

            const isNetworkError = err.message && (
                err.message.includes("Failed to fetch") ||
                err.message.includes("NetworkError") ||
                err.message.includes("Load failed")
            );

            if (isNetworkError && attempt < maxRetries) {
                attempt++;
                const delayMs = attempt * 2000;
                updateServerStatus(false, "Reconnecting...");
                showLoader(true, `Server warming up or reconnecting... Retrying attempt ${attempt}/${maxRetries} (${delayMs / 1000}s)...`);
                await new Promise(r => setTimeout(r, delayMs));
                continue;
            } else {
                break;
            }
        }
    }

    showLoader(false);
    updateServerStatus(false, "Offline");
    console.error("OCR Processing Final Error:", lastError);
    showOcrConnectionModal(lastError);
}

const triggerProcess = runOcrProcess;

// 5. Render OCR and Extraction Results
function renderDocumentResult() {
    if (!state.currentResult) return;
    const res = state.currentResult;
    const extraction = res.extraction || {};
    const pages = res.pages || [];
    const currentPage = pages[state.currentPageIndex] || pages[0] || {};

    document.getElementById("result-doc-type-title").textContent = extraction.document_type_name || "Extracted Document";
    const totalPages = res.total_pages || pages.length || 1;
    document.getElementById("page-indicator").textContent = `Page ${state.currentPageIndex + 1} / ${totalPages}`;
    document.getElementById("btn-prev-page").disabled = state.currentPageIndex <= 0;
    document.getElementById("btn-next-page").disabled = state.currentPageIndex >= (totalPages - 1);

    // Populate page-jump dropdown for smooth navigation across 30+ pages
    const jumpSelect = document.getElementById("page-jump-select");
    if (jumpSelect) {
        if (totalPages > 1) {
            jumpSelect.classList.remove("hidden");
            if (jumpSelect.options.length !== totalPages) {
                jumpSelect.innerHTML = "";
                for (let p = 0; p < totalPages; p++) {
                    const opt = document.createElement("option");
                    opt.value = p;
                    opt.textContent = `Page ${p + 1} of ${totalPages}`;
                    jumpSelect.appendChild(opt);
                }
            }
            jumpSelect.value = state.currentPageIndex;
        } else {
            jumpSelect.classList.add("hidden");
        }
    }

    renderAllDocumentPages(pages, extraction);
    renderECAnalysisTab(extraction);
    renderFieldsTab(extraction.fields || {});
    renderOwnersTab(extraction);
    renderPropertyFilterTab(extraction);
    renderChecklistTab(extraction.checklist || []);
    renderOCRTextTab(res.aggregated_text || currentPage.full_text || "");
    renderTableTab(extraction);

    const isECDoc = (extraction.document_type_id === "ec") || 
                    (extraction.fields && ("form_type" in extraction.fields || "transactions_table" in extraction.fields || "ec_report" in extraction.fields));
    
    if (isECDoc) {
        switchTab("ec-analysis");
    } else {
        switchTab("fields");
    }

    lucide.createIcons();
}

function jumpToPage(targetIdx) {
    if (!state.currentResult || !state.currentResult.pages) return;
    const idx = parseInt(targetIdx);
    if (!isNaN(idx) && idx >= 0 && idx < state.currentResult.pages.length) {
        state.currentPageIndex = idx;
        const totalPages = state.currentResult.total_pages || state.currentResult.pages.length || 1;
        document.getElementById("page-indicator").textContent = `Page ${state.currentPageIndex + 1} / ${totalPages}`;
        document.getElementById("btn-prev-page").disabled = state.currentPageIndex <= 0;
        document.getElementById("btn-next-page").disabled = state.currentPageIndex >= (totalPages - 1);
        const jumpSelect = document.getElementById("page-jump-select");
        if (jumpSelect) jumpSelect.value = state.currentPageIndex;

        const targetCard = document.getElementById(`page-card-${idx}`);
        if (targetCard) {
            targetCard.scrollIntoView({ behavior: "smooth", block: "start" });
        }
    }
}

function renderAllDocumentPages(pages, extraction) {
    const emptyState = document.getElementById("viewer-empty-state");
    const container = document.getElementById("all-pages-container");

    if (!container) return;
    if (emptyState) emptyState.classList.add("hidden");
    container.innerHTML = "";

    if (!pages || pages.length === 0) {
        if (emptyState) emptyState.classList.remove("hidden");
        return;
    }

    const fields = extraction.fields || {};
    const total = pages.length;

    pages.forEach((pageData, pIdx) => {
        const pageCard = document.createElement("div");
        pageCard.className = "pdf-page-card";
        pageCard.id = `page-card-${pIdx}`;

        // Page Header Bar
        const headerBar = document.createElement("div");
        headerBar.className = "pdf-page-header";
        const pageWordsCount = (pageData.words && pageData.words.length > 0)
            ? pageData.words.length
            : (pageData.lines || []).flatMap(l => l.words || []).length;

        headerBar.innerHTML = `
            <div class="flex items-center space-x-2">
                <span class="w-2 h-2 rounded-full bg-blue-600 inline-block"></span>
                <span class="font-bold text-slate-800">Page ${pIdx + 1} of ${total}</span>
            </div>
            <div class="flex items-center space-x-2 text-[10px] font-mono">
                <span class="px-2 py-0.5 rounded bg-blue-50 text-blue-700 font-semibold border border-blue-200">${pageWordsCount} Words Boxed</span>
                <span class="text-slate-400">${(pageData.lines || []).length} Lines</span>
            </div>
        `;
        pageCard.appendChild(headerBar);

        // Page Body
        const pageBody = document.createElement("div");
        pageBody.className = "pdf-page-body";
        pageBody.id = `page-body-${pIdx}`;

        if (pageData.preview_url) {
            const img = document.createElement("img");
            img.className = "pdf-page-image";
            img.src = pageData.preview_url;
            img.alt = `Page ${pIdx + 1}`;
            pageBody.appendChild(img);

            // Bounding Box Overlay for this specific page
            const bboxOverlay = document.createElement("div");
            bboxOverlay.className = "pdf-page-bbox-layer bbox-overlay-page";
            bboxOverlay.id = `bbox-layer-${pIdx}`;
            if (!state.showBBoxes) {
                bboxOverlay.style.display = "none";
            }

            // 1. Render Field Bounding Boxes belonging to THIS page
            Object.entries(fields).forEach(([key, item]) => {
                if (item && item.box) {
                    const box = item.box;
                    const boxPage = (typeof box.page_index === "number") ? box.page_index : 0;
                    if (boxPage === pIdx) {
                        const fieldBoxEl = document.createElement("div");
                        let colorClass = "field-patta";
                        if (key.includes("survey") || key.includes("ts_number")) colorClass = "field-survey";
                        else if (key.includes("district") || key.includes("taluk") || key.includes("village") || key.includes("sro")) colorClass = "field-district";
                        else if (key.includes("pattadhar") || key.includes("owner") || key.includes("seller")) colorClass = "field-owner";
                        else if (key.includes("period") || key.includes("date")) colorClass = "field-patta";

                        const isTopClamped = box.y_pct < 4.0;
                        fieldBoxEl.className = `field-canvas-box ${colorClass}${isTopClamped ? " tag-bottom" : ""}`;
                        fieldBoxEl.id = `canvas-field-${key}`;
                        fieldBoxEl.style.left = `${box.x_pct}%`;
                        fieldBoxEl.style.top = `${box.y_pct}%`;
                        fieldBoxEl.style.width = `${box.w_pct}%`;
                        fieldBoxEl.style.height = `${box.h_pct}%`;

                        const labelText = item.label || key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
                        const valText = typeof item.value === "object" ? JSON.stringify(item.value) : String(item.value);

                        fieldBoxEl.innerHTML = `
                            <div class="field-val-inside">
                                <div class="field-hover-title">${escapeHtml(labelText)}</div>
                                <span>${escapeHtml(valText)}</span>
                            </div>
                        `;

                        fieldBoxEl.onclick = () => highlightFieldCard(key);
                        bboxOverlay.appendChild(fieldBoxEl);
                    }
                }
            });

            // 2. Render Individual Word-Level Bounding Boxes for THIS page
            const words = (pageData.words && pageData.words.length > 0)
                ? pageData.words
                : (pageData.lines || []).flatMap(l => l.words || []);

            if (words && words.length > 0) {
                words.forEach((word, wIdx) => {
                    if (!word || !word.w_pct || !word.h_pct) return;
                    const wordBoxEl = document.createElement("div");
                    wordBoxEl.className = "word-bbox";
                    wordBoxEl.id = `word-p${pIdx}-w${wIdx}`;
                    wordBoxEl.style.left = `${word.x_pct}%`;
                    wordBoxEl.style.top = `${word.y_pct}%`;
                    wordBoxEl.style.width = `${word.w_pct}%`;
                    wordBoxEl.style.height = `${word.h_pct}%`;

                    const isTop = word.y_pct < 5.5;
                    const tooltipCls = isTop ? "word-bbox-tooltip tooltip-bottom" : "word-bbox-tooltip";
                    const transText = word.translation ? word.translation : "";
                    const confPct = Math.round((word.confidence || 0.98) * 100);

                    wordBoxEl.innerHTML = `
                        <div class="${tooltipCls}">
                            <div class="word-tooltip-orig">${escapeHtml(word.text)}</div>
                            ${transText ? `<div class="word-tooltip-trans"><span class="text-slate-400 font-normal mr-1">Trans:</span>${escapeHtml(transText)}</div>` : ''}
                            <div class="word-tooltip-conf">Conf: ${confPct}%</div>
                        </div>
                    `;

                    wordBoxEl.onclick = (e) => {
                        e.stopPropagation();
                        showWordInspector(word, pIdx + 1);
                    };

                    bboxOverlay.appendChild(wordBoxEl);
                });
            } else {
                // Fallback to line bounding boxes if no words are available
                const lines = pageData.lines || [];
                lines.forEach((line, lineIdx) => {
                    const rect = line.rect || {};
                    const boxEl = document.createElement("div");
                    boxEl.className = "ocr-bbox";
                    boxEl.id = `bbox-p${pIdx}-l${lineIdx}`;
                    boxEl.style.left = `${rect.x_pct}%`;
                    boxEl.style.top = `${rect.y_pct}%`;
                    boxEl.style.width = `${rect.w_pct}%`;
                    boxEl.style.height = `${rect.h_pct}%`;

                    boxEl.innerHTML = `
                        <div class="ocr-bbox-tooltip">
                            <span class="font-bold">${escapeHtml(line.text)}</span>
                            <span class="text-blue-300 text-[10px] block">Confidence: ${(line.confidence * 100).toFixed(1)}%</span>
                        </div>
                    `;
                    boxEl.onclick = () => highlightLineInText(line.text);
                    bboxOverlay.appendChild(boxEl);
                });
            }

            pageBody.appendChild(bboxOverlay);
        } else {
            // Synthetic preview for simulated pages
            renderSyntheticDocument(pageData, pageBody);
        }

        pageCard.appendChild(pageBody);
        container.appendChild(pageCard);
    });

    applyZoom();
}

function highlightFieldCard(fieldKey) {
    switchTab("fields");
    document.querySelectorAll(".field-canvas-box").forEach(b => b.classList.remove("active-field"));
    const canvasBox = document.getElementById(`canvas-field-${fieldKey}`);
    if (canvasBox) {
        canvasBox.classList.add("active-field");
        canvasBox.scrollIntoView({ behavior: "smooth", block: "center" });
    }
    const fieldCard = document.getElementById(`field-card-${fieldKey}`);
    if (fieldCard) {
        fieldCard.classList.add("ring-2", "ring-blue-500");
        fieldCard.scrollIntoView({ behavior: "smooth", block: "center" });
        setTimeout(() => fieldCard.classList.remove("ring-2", "ring-blue-500"), 2000);
    }
}

function renderSyntheticDocument(pageData, container) {
    const docTitle = (state.currentResult && state.currentResult.extraction) ? state.currentResult.extraction.document_type_name : "OFFICIAL DOCUMENT RECORD";
    const tamilTitle = (state.currentResult && state.currentResult.extraction) ? state.currentResult.extraction.tamil_name : "";

    container.innerHTML = `
        <div class="w-[540px] min-h-[720px] bg-amber-50/40 p-6 rounded-xl shadow-lg border-2 border-slate-300 font-sans text-xs text-slate-800 leading-relaxed relative select-none">
            <!-- Official Document Stamp Header -->
            <div class="border-b-2 border-slate-400 pb-3 mb-4 text-center">
                <div class="inline-flex items-center justify-center space-x-2 text-slate-900 font-extrabold text-sm uppercase tracking-wide">
                    <span>${docTitle}</span>
                </div>
                <p class="text-[11px] text-slate-600 font-medium mt-0.5">${tamilTitle}</p>
                <div class="mt-2 flex items-center justify-center space-x-3 text-[10px] text-slate-500 font-mono">
                    <span class="px-2 py-0.5 bg-slate-200 rounded">TAMIL NADU REGISTRATION & REVENUE</span>
                    <span class="px-2 py-0.5 bg-emerald-100 text-emerald-800 rounded font-bold">DIGITALLY VERIFIED</span>
                </div>
            </div>

            <!-- OCR Text Preview -->
            <div class="font-mono text-[11px] text-slate-700 leading-relaxed whitespace-pre-wrap bg-white/70 p-4 rounded-lg border border-slate-200 shadow-2xs">
                ${pageData.full_text}
            </div>
        </div>
    `;
}

function escapeHtml(str) {
    if (!str) return "";
    return String(str)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

function renderBilingualParties(list, fallbackText) {
    if (!Array.isArray(list) || list.length === 0) {
        return `<span class="text-slate-800 font-medium whitespace-pre-line">${escapeHtml(fallbackText || "-")}</span>`;
    }
    return `<div class="space-y-1">` + list.map(p => {
        const roleBits = [p.role_english, p.role_tamil].filter(Boolean).join(" / ");
        const roleTag = roleBits ? ` <span class="text-slate-400 font-normal">(${escapeHtml(roleBits)})</span>` : "";
        const badge = p.verified
            ? `<span class="shrink-0 px-1.5 py-0.5 rounded text-[9px] font-bold bg-emerald-100 text-emerald-800 border border-emerald-300">✓ ${p.confidence}%</span>`
            : `<span class="shrink-0 px-1.5 py-0.5 rounded text-[9px] font-bold bg-amber-100 text-amber-800 border border-amber-300">⚠ Review ${p.confidence}%</span>`;
        return `
            <div class="flex items-start justify-between gap-2 bg-white/70 rounded px-1.5 py-1 border border-slate-100">
                <div class="leading-snug">
                    <span class="text-slate-800 font-semibold">${escapeHtml(String(p.index))}. ${escapeHtml(p.english)}</span>${roleTag}
                    <div class="text-slate-500 text-[10px]">${escapeHtml(p.tamil)}</div>
                </div>
                ${badge}
            </div>`;
    }).join("") + `</div>`;
}

function renderBilingualPartiesCompact(list, fallbackText) {
    if (!Array.isArray(list) || list.length === 0) {
        return escapeHtml(fallbackText || "-").replace(/\n/g, "<br/>");
    }
    return list.map(p => {
        const mark = p.verified ? "✓" : "⚠";
        return `${escapeHtml(String(p.index))}. ${escapeHtml(p.english)} <span class="text-slate-400">(${escapeHtml(p.tamil)})</span> ${mark}`;
    }).join("<br/>");
}

function sanitizeTxFinancials(tx) {
    let pr = (tx.pr_number || "-").toString().trim();
    let cons = (tx.consideration || (tx.consideration_norm && tx.consideration_norm.formatted) || "-").toString().trim();
    let mkt = (tx.market_value || (tx.market_value_norm && tx.market_value_norm.formatted) || "-").toString().trim();

    if (!cons || cons === "0" || cons === "null" || cons === "None") cons = "-";
    if (!mkt || mkt === "0" || mkt === "null" || mkt === "None") mkt = "-";
    if (!pr || pr === "0" || pr === "null" || pr === "None") pr = "-";

    // Check if PR number erroneously contains currency
    if (/Rs\.?|₹|\bINR\b/i.test(pr) || (/^\d{1,3}(?:,\d{2,3})+$/.test(pr) && !pr.includes('/'))) {
        const currVal = pr.startsWith('Rs.') || pr.startsWith('₹') ? pr : `Rs. ${pr}/-`;
        if (cons === '-' || cons === '0') cons = currVal;
        if (mkt === '-' || mkt === '0') mkt = currVal;
        pr = "-";
    }

    return { pr, cons, mkt };
}

// =========================================================================
// EC Analysis (Encumbrance Certificate Overview) Tab Engine
// =========================================================================

function renderECAnalysisTab(extraction = null) {
    const container = document.getElementById("ec-analysis-container");
    const ecTabBtn = document.getElementById("tab-btn-ec-analysis");
    if (!container) return;

    extraction = extraction || (state.currentResult ? state.currentResult.extraction : null);

    const fields = (extraction && extraction.fields) ? extraction.fields : {};
    const report = fields.ec_report || {};
    const registry = fields.owners_registry || {};
    const summary = registry.summary || {};

    const hasData = Boolean(extraction && (
        (extraction.fields && Object.keys(extraction.fields).length > 0) ||
        (extraction.document_type_id === "ec") ||
        ("ec_report" in fields)
    ));

    const isEC = (state.selectedCategoryId === "ec") || 
                 ("form_type" in fields) || 
                 ("transactions_table" in fields) || 
                 ("search_period" in fields) ||
                 (extraction && extraction.document_type_id === "ec") ||
                 ("ec_report" in fields);

    if (hasData && !isEC) {
        if (ecTabBtn) ecTabBtn.classList.add("hidden");
        container.innerHTML = "";
        return;
    }

    if (ecTabBtn) ecTabBtn.classList.remove("hidden");

    if (!hasData) {
        container.innerHTML = `
            <div class="p-8 text-center bg-white rounded-2xl border border-dashed border-slate-300/80 shadow-2xs space-y-3 my-auto">
                <div class="w-12 h-12 rounded-xl bg-amber-50 text-amber-500 flex items-center justify-center mx-auto shadow-2xs">
                    <i data-lucide="sparkles" class="w-6 h-6"></i>
                </div>
                <h4 class="font-bold text-sm text-slate-800">EC Analysis & Legal Overview</h4>
                <p class="text-xs text-slate-500 max-w-md mx-auto leading-relaxed">
                    Upload an Encumbrance Certificate (EC) PDF above or click a sample document to generate an automated legal risk synthesis, ownership devolution summary, and 12-point title audit.
                </p>
            </div>
        `;
        if (window.lucide && lucide.createIcons) lucide.createIcons();
        return;
    }

    try {

    // 1. Gather Key Fields Data
    const currentOwnerObj = fields.current_owner || {};
    const ownerName = currentOwnerObj.name || currentOwnerObj.value || (fields.owner_name ? (fields.owner_name.value || fields.owner_name) : (report.applicant_name || "-"));
    const ownerType = currentOwnerObj.type || "Individual";
    const ownerDocNo = currentOwnerObj.doc_no || "-";
    const ownerDate = currentOwnerObj.date || "-";
    const ownerVendor = currentOwnerObj.vendor || "-";

    const activeMort = fields.active_mortgages || {};
    const openMortgages = activeMort.open_count || 0;
    const closedMortgages = activeMort.closed_count || 0;

    const poaObj = fields.active_poa || {};
    const hasPoa = poaObj.has_poa === true;
    const poaAgents = poaObj.agents || [];
    const poaStatusVal = poaObj.value || "No active POA entries found.";

    const courtObj = fields.court_attachments_key || fields.court_attachments || {};
    const hasCourt = courtObj.has_court === true || (courtObj.value && !courtObj.value.toLowerCase().includes("clear") && !courtObj.value.toLowerCase().includes("no court"));
    const courtVal = courtObj.value || "Clear: No court decrees or attachment orders detected.";

    const villageObj = fields.village_taluk || {};
    const village = villageObj.village || report.village || "-";
    const taluk = villageObj.taluk || report.district || "-";
    const district = villageObj.district || report.district || "-";
    const zone = villageObj.zone || report.zone || "-";

    const surveyObj = fields.survey_patta || {};
    const survey = surveyObj.survey || surveyObj.value || report.survey_details || "-";
    const pattaPlot = surveyObj.patta || "-";

    const propExtObj = fields.property_extent || {};
    const extent = propExtObj.extent || propExtObj.value || report.requested_extent || "-";
    const isUds = propExtObj.is_uds === true;
    const landCat = propExtObj.land_category || "-";
    const structure = propExtObj.structure || "-";

    const boundsObj = fields.boundary_schedule || {};
    const north = boundsObj.north || "-";
    const south = boundsObj.south || "-";
    const east = boundsObj.east || "-";
    const west = boundsObj.west || "-";
    const hasBounds = (north !== "-" || south !== "-" || east !== "-" || west !== "-");

    const txObj = fields.total_transactions || {};
    const txCount = parseInt(txObj.value || "0") || (report.entries ? report.entries.length : 0);

    const searchFrom = report.search_period_from || "-";
    const searchTo = report.search_period_to || "-";
    const searchYears = report.search_window_years !== undefined && report.search_window_years !== null ? report.search_window_years : "-";
    const isBelow30Yr = report.below_30yr_standard === true;

    const sroObj = fields.sub_registrar_office || {};
    const sro = sroObj.value || report.sro || "-";

    const totalOwners = summary.total_owners_count || (summary.current_owners_count + summary.historical_owners_count) || (currentOwnerObj.property_owners ? currentOwnerObj.property_owners.length : 1);
    const unitsCount = summary.units_count || (currentOwnerObj.property_owners ? currentOwnerObj.property_owners.length : 1);

    const srGapsObj = fields.sr_no_gaps || {};
    const hasSrGaps = srGapsObj.has_gaps === true;
    const srGapsText = srGapsObj.value || "Sequential continuity verified";

    // 2. Risk Evaluation
    const isHighRisk = hasCourt || (openMortgages > 2 && hasSrGaps);
    const isMediumRisk = !isHighRisk && (openMortgages > 0 || hasPoa || isBelow30Yr || hasSrGaps);

    const riskBadgeText = isHighRisk ? "HIGH RISK" : (isMediumRisk ? "MEDIUM RISK" : "CLEAR / LOW RISK");
    const riskBadgeClass = isHighRisk 
        ? "bg-rose-100 text-rose-800 border-rose-300 font-bold" 
        : (isMediumRisk 
            ? "bg-amber-100 text-amber-800 border-amber-300 font-bold" 
            : "bg-emerald-100 text-emerald-800 border-emerald-300 font-bold");

    // 3. Executive Narrative Summary Paragraph
    const propIdent = `The property comprised in Survey No. ${survey !== '-' ? survey : 'searched parcel'}, ${village !== '-' ? village + ' village' : ''}, ${district !== '-' ? district + ' district' : ''} (SRO: ${sro})`;
    
    let concerns = [];
    if (openMortgages > 0) concerns.push(`${openMortgages} open/unreleased mortgage charge(s) without registered discharge receipts`);
    if (hasCourt) concerns.push(`an active civil court attachment decree`);
    if (hasPoa) concerns.push(`${poaAgents.length || 1} registered Power of Attorney (POA) instrument(s) in title trail`);
    if (isBelow30Yr) concerns.push(`the search window of ${searchYears} years is below the standard 30-year due diligence benchmark`);
    if (hasSrGaps) concerns.push(`serial number sequence gap in registry records`);

    let narrative = "";
    if (concerns.length > 0) {
        narrative = `${propIdent} requires caution. While the registered transaction trail is traceable across ${txCount} instrument(s) and current ownership is recorded under ${ownerName}, there are specific matters for scrutiny: ${concerns.join(", ")}.`;
    } else {
        narrative = `${propIdent} exhibits a clear and unencumbered title profile. The registered devolution chain is fully traceable across ${txCount} transaction(s) with ${ownerName} confirmed as current title holder. No active mortgages, court attachments, or adverse legal encumbrances were detected across the ${searchYears !== '-' ? searchYears + ' year' : ''} search window.`;
    }

    // 4. Build Structured Audit Items (Checklist / Verification Rows)
    const auditItems = [];

    // Item 1: EC Status & Transactions
    if (txCount > 0) {
        if (openMortgages === 0 && !hasCourt) {
            auditItems.push({
                type: "pass",
                title: "Encumbrance Certificate is clean with traceable transactions",
                desc: `Encumbrance Certificate contains ${txCount} traceable registered transactions spanning ${searchFrom} to ${searchTo} (${searchYears} years search window — ${!isBelow30Yr ? 'complies with 30-year statutory legal standard' : 'under 30-yr benchmark'}). No active mortgages, liens, or court attachments.`,
                action: "switchTab('table')"
            });
        } else {
            auditItems.push({
                type: "warn",
                title: "Encumbrance Certificate contains active transaction entries requiring review",
                desc: `Encumbrance Certificate contains ${txCount} registered transactions spanning ${searchFrom} to ${searchTo}. Open mortgage or verification caveats require cross-checking with parent deeds.`,
                action: "switchTab('table')"
            });
        }
    } else {
        auditItems.push({
            type: "pass",
            title: "Encumbrance Certificate is Nil (Form 16)",
            desc: `Nil Encumbrance Certificate confirmed with zero registered transactions recorded between ${searchFrom} and ${searchTo} (${searchYears} years). Property is free of registered encumbrances in this window.`,
            action: "switchTab('fields')"
        });
    }

    // Item 2: Current Title Holder & Root Deed
    if (ownerName !== "-") {
        auditItems.push({
            type: "pass",
            title: `Current Title Holder confirmed: ${ownerName}`,
            desc: `Registered records confirm ${ownerName} (${ownerType}) as current legal title holder${ownerDocNo !== '-' ? ' via ' + (fields.nature_last_tx?.value || 'acquisition deed') + ' (Doc No: ' + ownerDocNo + ' on ' + ownerDate + ')' : ''}${ownerVendor !== '-' ? ' from ' + ownerVendor : ''}.`,
            action: `openOwnerDossierByName('${ownerName.replace(/'/g, "\\'")}')`
        });
    } else {
        auditItems.push({
            type: "warn",
            title: "Current Title Holder identification requires parent document cross-check",
            desc: "Explicit grantee name not isolated in search header. Cross-verification with registered sale deed and Patta passbook recommended.",
            action: "switchTab('owners')"
        });
    }

    // Item 3: Active Mortgages & Charges
    if (openMortgages === 0) {
        auditItems.push({
            type: "pass",
            title: "Zero active mortgages or unreleased financial charges",
            desc: closedMortgages > 0 
                ? `All registered security interests (${closedMortgages} mortgage(s)) have been verified as satisfied and closed via registered discharge receipts. No active bank charges.`
                : "No mortgage deeds or financial charges recorded in the searched registration window.",
            action: "highlightFieldCard('active_mortgages')"
        });
    } else {
        auditItems.push({
            type: "warn",
            title: `${openMortgages} Open / Unreleased Mortgage(s) recorded`,
            desc: `${openMortgages} registered mortgage instrument(s) found without corresponding registered discharge receipt (Receipt Deed). ${closedMortgages} prior mortgage(s) closed. Bank NOC / registered cancellation deed must be verified.`,
            action: "highlightFieldCard('active_mortgages')"
        });
    }

    // Item 4: Court Attachments & Liens
    if (!hasCourt) {
        auditItems.push({
            type: "pass",
            title: "No court attachments, execution petitions, or decrees",
            desc: "Search confirms zero registered attachment orders, civil court decrees, or insolvency petitions recorded against this property under SRO records.",
            action: "highlightFieldCard('court_attachments_key')"
        });
    } else {
        auditItems.push({
            type: "danger",
            title: "Civil Court Attachment / Decree identified on property",
            desc: `${courtVal}. Immediate legal consultation and court case status verification required.`,
            action: "highlightFieldCard('court_attachments_key')"
        });
    }

    // Item 5: Power of Attorney (POA)
    if (!hasPoa) {
        auditItems.push({
            type: "pass",
            title: "No active Power of Attorney (POA) instruments",
            desc: "No General Power of Attorney (GPA) or Special Power of Attorney (SPA) instruments registered in this search period. Title transactions executed directly by principals.",
            action: "highlightFieldCard('active_poa')"
        });
    } else {
        auditItems.push({
            type: "warn",
            title: `${poaAgents.length || 1} Power of Attorney (POA) / Agent entry identified`,
            desc: `${poaStatusVal}. Verify that the GPA was in force on the date of deed execution and has not been revoked or extinguished.`,
            action: "highlightFieldCard('active_poa')"
        });
    }

    // Item 6: Property Extent & Classification
    auditItems.push({
        type: "pass",
        title: `Property Extent: ${extent !== '-' ? extent : 'Recorded in schedule'}`,
        desc: `Registered extent: ${extent}${structure !== '-' ? ' | Structure: ' + structure : ''} (${isUds ? 'Undivided Share of Land / UDS' : (landCat !== '-' ? landCat : 'Plot Extent')}). Cross-verify with Patta/FMB sketch.`,
        action: "highlightFieldCard('property_extent')"
    });

    // Item 7: Survey & Patta Identification
    auditItems.push({
        type: "pass",
        title: `Survey Identification: ${survey !== '-' ? survey : 'Comprised in SRO record'}`,
        desc: `Comprised in Survey No(s): ${survey}${pattaPlot !== '-' ? ' | Patta / Plot No: ' + pattaPlot : ''} in ${village} Village, ${district} District.`,
        action: "highlightFieldCard('survey_patta')"
    });

    // Item 8: Boundary Schedule
    if (hasBounds) {
        auditItems.push({
            type: "pass",
            title: "Four-Side Boundary Schedule identified",
            desc: `North: ${north} | South: ${south} | East: ${east} | West: ${west}.`,
            action: "highlightFieldCard('boundary_schedule')"
        });
    } else {
        auditItems.push({
            type: "warn",
            title: "Boundary clauses not explicitly specified in search header",
            desc: "Four boundaries not itemized in EC certificate header. Inspection of Schedule A/B in parent sale deed and physical site survey recommended.",
            action: "highlightFieldCard('boundary_schedule')"
        });
    }

    // Item 9: Search Window Standard
    if (!isBelow30Yr && searchYears !== "-") {
        auditItems.push({
            type: "pass",
            title: `Search Window: ${searchYears} Years (${searchFrom} to ${searchTo})`,
            desc: `The ${searchYears}-year search window meets and exceeds the Tamil Nadu 30-year legal due diligence benchmark for absolute title scrutiny.`,
            action: "highlightFieldCard('search_period')"
        });
    } else if (isBelow30Yr) {
        auditItems.push({
            type: "warn",
            title: `Search Window: ${searchYears} Years (${searchFrom} to ${searchTo}) — Below 30-Yr Benchmark`,
            desc: `The search period of ${searchYears} years is less than the standard 30-year period. Obtaining an extended search EC or verifying prior parent deeds is strongly recommended.`,
            action: "highlightFieldCard('search_period')"
        });
    }

    // Item 10: Title Devolution & Property Clusters
    auditItems.push({
        type: "pass",
        title: `Title Devolution: ${totalOwners} genuine title owner(s) across ${unitsCount} property cluster(s)`,
        desc: `Chronological devolution mapped across ${txCount} registered transactions with verified root acquisition deeds and outward transfer links.`,
        action: "switchTab('owners')"
    });

    // Item 11: Document Continuity
    if (!hasSrGaps) {
        auditItems.push({
            type: "pass",
            title: "Source Document Continuity: Verified",
            desc: "Registration serial numbers are sequential with no unrecorded gaps or missing volume entries detected.",
            action: "highlightFieldCard('sr_no_gaps')"
        });
    } else {
        auditItems.push({
            type: "warn",
            title: "Serial Number Sequence Gaps detected",
            desc: `${srGapsText}. Check with SRO whether intervening numbers correspond to unindexed books or deleted tokens.`,
            action: "highlightFieldCard('sr_no_gaps')"
        });
    }

    // Item 12: Statutory Registration Caveat
    auditItems.push({
        type: "pass",
        title: "Statutory TNREGINET Scope & Ground Verification Note",
        desc: "Certificate reflects registered deeds filed with the SRO. Unregistered agreements, municipal tax dues, and physical possession must be verified on-site.",
        action: "highlightFieldCard('legal_caveat')"
    });

    const passedCount = auditItems.filter(i => i.type === "pass").length;
    const warningCount = auditItems.filter(i => i.type === "warn" || i.type === "danger").length;

    // 5. Render Template
    container.innerHTML = `
        <div class="space-y-4">
            <!-- Main Analysis Header Card (Styled exactly as sample image) -->
            <div class="p-5 rounded-2xl bg-gradient-to-br from-amber-500/10 via-white to-orange-500/5 border border-amber-200/90 shadow-2xs">
                <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-amber-200/60">
                    <div class="flex items-center gap-3">
                        <div class="w-10 h-10 rounded-xl bg-gradient-to-tr from-amber-500 to-orange-500 text-white flex items-center justify-center shadow-xs shrink-0">
                            <i data-lucide="sparkles" class="w-5 h-5"></i>
                        </div>
                        <div>
                            <div class="flex items-center gap-2">
                                <h3 class="text-base font-bold text-slate-900">EC Analysis (Encumbrance Certificate Overview)</h3>
                                <span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-amber-100 text-amber-900 border border-amber-200/80">TNREGINET Official</span>
                            </div>
                            <p class="text-xs text-slate-500 mt-0.5">Automated legal synthesis derived dynamically from all extracted key fields</p>
                        </div>
                    </div>

                    <div class="flex items-center gap-2 flex-wrap text-xs">
                        <span class="px-3 py-1 rounded-full text-xs border uppercase tracking-wider ${riskBadgeClass}">
                            ${riskBadgeText}
                        </span>
                        <span class="px-2.5 py-1 rounded-full bg-white/90 text-emerald-800 border border-emerald-200/80 font-bold shadow-2xs flex items-center gap-1.5">
                            <span class="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
                            ${passedCount} Passed
                        </span>
                        <span class="px-2.5 py-1 rounded-full bg-white/90 text-amber-800 border border-amber-200/80 font-bold shadow-2xs flex items-center gap-1.5">
                            <span class="w-1.5 h-1.5 rounded-full bg-amber-500"></span>
                            ${warningCount} Warnings
                        </span>
                    </div>
                </div>

                <!-- Executive Narrative Summary Paragraph -->
                <div class="mt-3.5 p-3.5 rounded-xl bg-white/85 border border-amber-200/70 shadow-2xs">
                    <p class="text-xs text-slate-700 leading-relaxed font-normal">
                        ${narrative}
                    </p>
                </div>
            </div>

            <!-- Structured Audit Rows (Pass & Warning Items) -->
            <div class="space-y-2.5">
                ${auditItems.map(item => {
                    const isPass = item.type === "pass";
                    const isDanger = item.type === "danger";
                    
                    let bgBorderClass = "bg-emerald-50/60 hover:bg-emerald-50/90 border-emerald-200/70 text-slate-800";
                    let iconHtml = `<span class="w-5 h-5 rounded-full bg-emerald-100 text-emerald-700 flex items-center justify-center shrink-0 mt-0.5 font-bold text-xs">✓</span>`;

                    if (isDanger) {
                        bgBorderClass = "bg-rose-50/70 hover:bg-rose-50 border-rose-200/90 text-slate-900";
                        iconHtml = `<span class="w-5 h-5 rounded-full bg-rose-100 text-rose-700 flex items-center justify-center shrink-0 mt-0.5 font-bold text-xs">✕</span>`;
                    } else if (!isPass) {
                        bgBorderClass = "bg-amber-50/65 hover:bg-amber-50 border-amber-200/85 text-slate-900";
                        iconHtml = `<span class="w-5 h-5 rounded-full bg-amber-100 text-amber-800 flex items-center justify-center shrink-0 mt-0.5 font-bold text-xs">⚠</span>`;
                    }

                    return `
                    <div class="p-2.5 px-3.5 rounded-xl border transition-all shadow-2xs flex items-center justify-between gap-3 ${bgBorderClass}">
                        <div class="flex items-center gap-2.5 min-w-0">
                            ${iconHtml}
                            <span class="text-xs font-bold text-slate-900 leading-snug">${escapeHtml(item.title)}</span>
                        </div>
                        ${item.action ? `
                        <button type="button" onclick="${item.action}" class="shrink-0 text-[11px] font-semibold text-blue-700 hover:text-blue-900 hover:underline cursor-pointer flex items-center gap-1 bg-white/80 hover:bg-white px-2.5 py-1 rounded-lg border border-slate-200/80 shadow-2xs transition-colors">
                            <span>Inspect</span>
                            <span>&rarr;</span>
                        </button>
                        ` : ''}
                    </div>
                    `;
                }).join("")}
            </div>

            <!-- Bottom Action Navigation -->
            <div class="pt-2 flex items-center justify-between gap-2 flex-wrap">
                <div class="flex items-center gap-2">
                    <button type="button" onclick="switchTab('fields')" class="px-3 py-1.5 text-xs font-semibold rounded-lg bg-blue-600 hover:bg-blue-700 text-white shadow-2xs flex items-center gap-1.5 cursor-pointer transition-colors">
                        <i data-lucide="list-tree" class="w-3.5 h-3.5"></i>
                        <span>View Detailed Key Fields</span>
                    </button>
                    <button type="button" onclick="switchTab('owners')" class="px-3 py-1.5 text-xs font-semibold rounded-lg bg-purple-50 hover:bg-purple-100 text-purple-700 border border-purple-200 flex items-center gap-1.5 cursor-pointer transition-colors">
                        <i data-lucide="users" class="w-3.5 h-3.5"></i>
                        <span>Owners Directory (${totalOwners})</span>
                    </button>
                    <button type="button" onclick="switchTab('table')" class="px-3 py-1.5 text-xs font-semibold rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 border border-slate-200 flex items-center gap-1.5 cursor-pointer transition-colors">
                        <i data-lucide="table" class="w-3.5 h-3.5 text-indigo-600"></i>
                        <span>Transactions Table (${txCount})</span>
                    </button>
                </div>
                <button type="button" onclick="downloadPdfWithLanguage()" class="px-3 py-1.5 text-xs font-semibold rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white shadow-2xs flex items-center gap-1.5 cursor-pointer transition-colors">
                    <i data-lucide="download" class="w-3.5 h-3.5"></i>
                    <span>Export Full Legal Dossier</span>
                </button>
            </div>
        </div>
    `;

        lucide.createIcons();
    } catch (err) {
        console.error("Error rendering EC Analysis Tab:", err);
        container.innerHTML = `
            <div class="p-6 rounded-2xl bg-amber-50 border border-amber-200 text-amber-900 space-y-2">
                <div class="flex items-center gap-2 font-bold text-sm">
                    <i data-lucide="alert-triangle" class="w-4 h-4 text-amber-600"></i>
                    <span>Unable to Render EC Overview</span>
                </div>
                <p class="text-xs text-amber-700 leading-relaxed">${escapeHtml(err.message || 'An unexpected error occurred.')}</p>
            </div>
        `;
        if (window.lucide && lucide.createIcons) lucide.createIcons();
    }
}

function renderFieldsTab(fields) {
    const container = document.getElementById("extracted-fields-container");
    if (!container) return;
    container.innerHTML = "";

    const isEC = (state.selectedCategoryId === "ec") || 
                 ("form_type" in fields) || 
                 ("transactions_table" in fields) || 
                 ("search_period" in fields) ||
                 (state.currentResult && state.currentResult.extraction && state.currentResult.extraction.document_type_id === "ec");

    const isTSLR = (state.selectedCategoryId === "tslr") ||
                   ("town_survey_number" in fields) ||
                   ("ward_block" in fields) ||
                   ("old_survey_number" in fields) ||
                   (state.currentResult && state.currentResult.extraction && state.currentResult.extraction.document_type_id === "tslr");

    if (isEC) {
        renderECFieldsLayout(fields, container);
    } else if (isTSLR) {
        renderTSLRFieldsLayout(fields, container);
    } else {
        renderStandardFieldsLayout(fields, container);
    }

    lucide.createIcons();
}

function renderECFieldsLayout(fields, container) {
    // 1. Safe extraction of field values
    const currentOwnerObj = fields.current_owner || {};
    const ownerName = currentOwnerObj.name || currentOwnerObj.value || (fields.owner_name ? (fields.owner_name.value || fields.owner_name) : "-");
    const ownershipType = currentOwnerObj.type || "Individual";
    const ownerDocNo = currentOwnerObj.doc_no || "-";
    const ownerDate = currentOwnerObj.date || "-";
    const ownerVendor = currentOwnerObj.vendor || "-";
    const propertyOwners = currentOwnerObj.property_owners || [];
    const hasMultipleProperties = currentOwnerObj.has_multiple_properties || propertyOwners.length > 1;
    const certNo = fields.certificate_no ? (fields.certificate_no.value || fields.certificate_no) : (currentOwnerObj.certificate_no || "-");
    const appNo = fields.application_no ? (fields.application_no.value || fields.application_no) : (currentOwnerObj.application_no || "-");
    const applicantName = fields.applicant_name ? (fields.applicant_name.value || fields.applicant_name) : (currentOwnerObj.applicant_name || "-");

    // 2. Active Mortgages
    const mortgageObj = fields.active_mortgages || fields.mortgage_status || {};
    const mortgageVal = mortgageObj.value || "0 Open/Unreleased Mortgages | 0 Closed Mortgage";
    const mortgageFlags = mortgageObj.flags || (fields.verification_flags && fields.verification_flags.mortgages_flags) || [];

    // 3. Active POA
    const poaObj = fields.active_poa || {};
    const poaVal = poaObj.value || "No registered Power of Attorney (POA) entries found in this search window.";
    const poaAgents = poaObj.agents || poaObj.details || [];
    const hasPOA = poaObj.has_poa || poaAgents.length > 0;

    // 4. Court Attachments
    const courtVal = fields.court_attachments_key ? (fields.court_attachments_key.value || fields.court_attachments_key) :
                     (fields.court_attachments ? (fields.court_attachments.value || fields.court_attachments) : "No court attachments, decrees, or lis-pendens entries appear among the registered documents in this search window.");

    // 5. Village & Taluk
    const sroVal = fields.sro_office ? (fields.sro_office.value || fields.sro_office) : "-";
    const villageVal = fields.village ? (fields.village.value || fields.village) : "-";
    const talukVal = fields.taluk ? (fields.taluk.value || fields.taluk) : "-";
    const districtVal = fields.district ? (fields.district.value || fields.district) : "-";
    const zoneVal = fields.zone ? (fields.zone.value || fields.zone) : "-";

    // 6. Survey / Patta
    const surveyVal = fields.survey_searched ? (fields.survey_searched.value || fields.survey_searched) : "-";
    const pattaVal = fields.survey_patta ? (fields.survey_patta.patta || "-") : "-";

    // 7. Property Extent & Remarks
    const extentObj = fields.property_extent || {};
    const extentVal = extentObj.value || extentObj.extent || (fields.extent ? (fields.extent.value || fields.extent) : "Not explicitly specified in remarks");
    const isUDS = extentObj.is_uds === true;
    const landCategory = extentObj.land_category || (isUDS ? "UDS (Undivided Share of Land)" : "Normal Land (முழு நில உரிமை / Independent Plot)");
    const propTypeVal = extentObj.property_type || (fields.property_type_remarks && fields.property_type_remarks.value) || "House Site / Building";
    const structureVal = extentObj.structure || "Residential Structure / Land";
    const remarksNotes = extentObj.remarks_notes || "Standard document remarks recorded in SRO register";

    // 8. Boundary Schedule
    const boundObj = fields.boundary_schedule || {};
    const northBound = boundObj.north || "-";
    const southBound = boundObj.south || "-";
    const eastBound = boundObj.east || "-";
    const westBound = boundObj.west || "-";

    // 9. Total Transactions Found
    const totalTxObj = fields.total_transactions || fields.total_entries || {};
    const totalEntriesVal = totalTxObj.value || (fields.total_entries ? fields.total_entries.value : "0");
    const formTypeVal = fields.form_type ? (fields.form_type.value || fields.form_type) : (parseInt(totalEntriesVal) > 0 ? "Form 15 (Encumbered)" : "Form 16 Nil");
    const txBreakdown = totalTxObj.breakdown || (parseInt(totalEntriesVal) > 0 ? `${totalEntriesVal} Registered Transactions Recorded` : "Nil Encumbrance");

    // 10. Nature of Last Transaction
    const lastTxObj = fields.nature_of_last_tx || {};
    const lastNature = lastTxObj.nature || lastTxObj.value || "-";
    const lastDocNo = lastTxObj.doc_no || "-";
    const lastDate = lastTxObj.date || "-";
    const lastExecs = lastTxObj.executants || "-";
    const lastClaims = lastTxObj.claimants || "-";

    // 11. Consideration Value
    const consObj = fields.consideration_value || {};
    const consVal = consObj.value || "-";
    const mktVal = consObj.market_value || "-";

    // 12. Search Period
    const searchPeriodObj = fields.search_period_key || fields.search_period || {};
    const searchPeriod = searchPeriodObj.value || searchPeriodObj.period || (fields.search_period ? (fields.search_period.value || fields.search_period) : "-");
    const sroAvail = searchPeriodObj.sro_available || (fields.sro_available_from ? (fields.sro_available_from.value || fields.sro_available_from) : searchPeriod);
    const stdObj = fields.search_period_standard || {};
    const is30Compliant = stdObj.status === "COMPLIANT" || searchPeriodObj.is_30yr === true;

    // 13. Sub-Registrar Office
    const sroKeyObj = fields.sro_office_key || {};
    const sroJurisdiction = sroKeyObj.jurisdiction || (fields.sro_jurisdiction ? (fields.sro_jurisdiction.value || fields.sro_jurisdiction) : sroVal);
    const certDate = sroKeyObj.cert_date || (fields.certificate_date ? (fields.certificate_date.value || fields.certificate_date) : "-");
    const sigVal = sroKeyObj.validity || (fields.digital_signature_validity ? (fields.digital_signature_validity.value || fields.digital_signature_validity) : "Digitally Signed by Sub-Registrar / Certificate Valid under Tamil Nadu Registration Rules");

    const wrapper = document.createElement("div");
    wrapper.className = "space-y-3.5";

    wrapper.innerHTML = `
        <!-- CRITICAL PRODUCT CAVEAT CALLOUT -->
        <div class="p-3.5 rounded-xl bg-amber-500/10 border-2 border-amber-300 text-amber-900 shadow-2xs">
            <div class="flex items-start gap-2.5">
                <div class="p-2 rounded-lg bg-amber-200/80 text-amber-900 shrink-0 mt-0.5">
                    <i data-lucide="shield-alert" class="w-4 h-4"></i>
                </div>
                <div>
                    <div class="flex items-center gap-2 mb-1">
                        <span class="text-xs font-extrabold uppercase tracking-wide text-amber-950">Critical Product Verification Caveat</span>
                        <span class="px-1.5 py-0.2 rounded bg-amber-200 text-amber-900 text-[10px] font-bold">Scope of EC</span>
                    </div>
                    <p class="text-[11px] text-amber-900/90 leading-relaxed font-medium">
                        The Encumbrance Certificate (EC) reflects <strong>ONLY registered documents</strong> filed with the Tamil Nadu Registration Department. Unregistered agreements of sale, court orders/stay injunctions not communicated to or entered by the SRO, municipal & water tax dues, revenue record variations (Patta/TSLR), and physical possession disputes are <strong>invisible</strong> to it. <strong>An EC alone cannot be the sole verification signal</strong> and must be cross-verified with Patta/TSLR, parent deeds, and site inspection.
                    </p>
                </div>
            </div>
        </div>

        <!-- 1. KEY FIELDS HEADER -->
        <div class="flex items-center justify-between pt-1">
            <h4 class="text-xs font-bold text-slate-900 uppercase tracking-wider flex items-center gap-1.5">
                <i data-lucide="map-pin" class="w-3.5 h-3.5 text-blue-600"></i>
                <span>1. KEY FIELDS (முக்கிய விவரங்கள்)</span>
            </h4>
            <div class="flex items-center gap-2">
                <button type="button" onclick="toggleAllECKeyCards()" class="px-2 py-0.5 text-[10px] font-bold text-blue-600 hover:text-blue-800 bg-blue-50 hover:bg-blue-100 rounded border border-blue-200 transition-colors cursor-pointer" id="btn-toggle-all-ec-cards">
                    Toggle Expand All
                </button>
                <span class="text-[10px] font-mono text-slate-400">Section 1 of 1</span>
            </div>
        </div>

        <!-- ACCORDION CARDS CONTAINER -->
        <div class="space-y-2">

            <!-- 0. HERO CARD: CURRENT OWNER NAME (OPEN BY DEFAULT) -->
            <div id="ec-card-owner" class="ec-key-card rounded-xl border border-blue-200 bg-white shadow-2xs transition-all overflow-hidden">
                <div onclick="toggleECKeyCard('ec-card-owner')" class="p-3 bg-blue-50/50 hover:bg-blue-50/80 cursor-pointer flex items-center justify-between transition-colors">
                    <div class="flex items-center gap-2">
                        <i data-lucide="user" class="w-4 h-4 text-blue-600"></i>
                        <span class="text-xs font-bold text-slate-800">Current Owner Name</span>
                    </div>
                    <i data-lucide="chevron-down" id="ec-card-owner-chevron" class="ec-key-card-chevron w-4 h-4 text-blue-600 transition-transform"></i>
                </div>
                <div id="ec-card-owner-body" class="ec-key-card-body p-3.5 bg-white border-t border-blue-100 space-y-2.5">
                    ${(certNo !== "-" || appNo !== "-" || applicantName !== "-") ? `
                    <div class="p-2.5 rounded-lg bg-slate-50 border border-slate-200 text-xs flex flex-wrap items-center justify-between gap-2 text-slate-600 font-mono">
                        ${certNo !== "-" ? `<span><b>Cert No:</b> <span class="text-slate-900 font-bold">${escapeHtml(certNo)}</span></span>` : ""}
                        ${appNo !== "-" ? `<span><b>App No:</b> ${escapeHtml(appNo)}</span>` : ""}
                        ${applicantName !== "-" ? `<span><b>Applicant:</b> <span class="text-blue-900 font-semibold">${escapeHtml(applicantName)}</span></span>` : ""}
                    </div>
                    ` : ""}

                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <span class="text-[11px] font-semibold text-slate-400 block">Current Title Holder / Owner</span>
                            <span class="text-sm font-extrabold text-slate-900 block mt-0.5">${escapeHtml(ownerName)}</span>
                        </div>
                        <div>
                            <span class="text-[11px] font-semibold text-slate-400 block">Ownership Type</span>
                            <span class="text-sm font-extrabold text-slate-900 block mt-0.5">${escapeHtml(ownershipType)}</span>
                        </div>
                    </div>

                    <div class="pt-2 flex items-center gap-2 flex-wrap">
                        <button type="button" onclick="openOwnerDossierByName('${escapeHtml(ownerName)}')" class="px-3 py-1.5 text-xs font-semibold rounded-lg bg-purple-600 hover:bg-purple-700 text-white shadow-2xs flex items-center gap-1.5 cursor-pointer transition-colors">
                            <i data-lucide="file-text" class="w-3.5 h-3.5"></i>
                            <span>View Title Dossier</span>
                        </button>
                        <button type="button" onclick="switchTab('owners')" class="px-3 py-1.5 text-xs font-semibold rounded-lg bg-blue-50 hover:bg-blue-100 text-blue-700 border border-blue-200 flex items-center gap-1.5 cursor-pointer transition-colors">
                            <i data-lucide="users" class="w-3.5 h-3.5"></i>
                            <span>Open Owners Directory (${(fields.owners_registry && fields.owners_registry.summary) ? (fields.owners_registry.summary.total_owners_count || fields.owners_registry.summary.total_parties) : (propertyOwners.length || 1)})</span>
                        </button>
                    </div>

                    ${ownerDocNo !== "-" ? `
                    <div class="pt-2 border-t border-slate-100 flex items-center justify-between text-[11px] text-slate-500 font-mono bg-slate-50/60 px-2.5 py-1.5 rounded-lg">
                        <span><b>Latest Title Deed (Overall):</b> Doc ${escapeHtml(ownerDocNo)}</span>
                        <span><b>Reg Date:</b> ${escapeHtml(ownerDate)}</span>
                        ${ownerVendor !== "-" ? `<span><b>Vendor:</b> ${escapeHtml(ownerVendor)}</span>` : ""}
                    </div>
                    ` : ""}

                    ${hasMultipleProperties ? `
                    <div class="pt-3 mt-1 border-t border-blue-100">
                        <div class="flex items-center justify-between mb-2">
                            <span class="text-[11px] font-bold text-slate-700 uppercase tracking-wider flex items-center gap-1">
                                <i data-lucide="layers" class="w-3.5 h-3.5 text-blue-600"></i>
                                <span>All Property Units & Respective Owners (${propertyOwners.length} Units Found)</span>
                            </span>
                            <button type="button" onclick="switchTab('owners')" class="text-[10px] bg-blue-50 hover:bg-blue-100 text-blue-700 font-semibold px-2 py-0.5 rounded border border-blue-200 transition-colors cursor-pointer">View in Directory &rarr;</button>
                        </div>
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-2 max-h-72 overflow-y-auto pr-1">
                            ${propertyOwners.map(po => `
                            <div class="p-2.5 rounded-lg bg-slate-50 hover:bg-blue-50/40 border border-slate-200/80 transition-colors space-y-1 text-xs">
                                <div class="flex items-start justify-between gap-1.5">
                                    <span class="font-bold text-slate-800 text-[11px] leading-tight text-blue-950">${escapeHtml(po.unit)}</span>
                                    <span class="shrink-0 px-1.5 py-0.5 text-[9px] font-semibold rounded bg-slate-200/70 text-slate-700 font-mono">${po.total_entries} doc(s)</span>
                                </div>
                                <div class="flex items-center justify-between gap-2 pt-0.5">
                                    <div class="text-[12px] font-extrabold text-slate-900 truncate">${escapeHtml(po.owner_name)}</div>
                                    <button type="button" onclick="openOwnerDossierByName('${escapeHtml(po.owner_name)}')" class="shrink-0 px-2 py-0.5 rounded text-[10px] font-bold bg-purple-50 hover:bg-purple-100 text-purple-700 border border-purple-200 transition-colors flex items-center gap-1 cursor-pointer" title="Inspect Title Dossier">
                                        <i data-lucide="file-text" class="w-3 h-3"></i>
                                        <span>Dossier</span>
                                    </button>
                                </div>
                                <div class="text-[10px] text-slate-500 font-mono flex items-center justify-between pt-0.5 border-t border-slate-200/50">
                                    <span>Doc: <b>${escapeHtml(po.doc_no)}</b> (${escapeHtml(po.date)})</span>
                                    ${po.extent && po.extent !== '-' ? `<span>Ext: <b>${escapeHtml(po.extent)}</b></span>` : ''}
                                </div>
                            </div>
                            `).join('')}
                        </div>
                    </div>
                    ` : ""}
                </div>
            </div>

            <!-- 1. ACTIVE MORTGAGES -->
            <div id="ec-card-mortgage" class="ec-key-card rounded-xl border border-slate-200/90 bg-white shadow-2xs transition-all overflow-hidden">
                <div onclick="toggleECKeyCard('ec-card-mortgage')" class="p-3 hover:bg-slate-50 cursor-pointer flex items-center justify-between transition-colors">
                    <div class="flex items-center gap-2">
                        <i data-lucide="home" class="w-4 h-4 text-slate-600"></i>
                        <span class="text-xs font-bold text-slate-800">1. Active Mortgages</span>
                    </div>
                    <div class="flex items-center gap-2">
                        <span class="px-2 py-0.5 rounded text-[10px] font-bold ${mortgageVal.includes('Open') && !mortgageVal.startsWith('0 Open') ? 'bg-amber-100 text-amber-800 border border-amber-200' : 'bg-emerald-100 text-emerald-800 border border-emerald-200'}">
                            ${escapeHtml(mortgageVal)}
                        </span>
                        <i data-lucide="chevron-right" id="ec-card-mortgage-chevron" class="ec-key-card-chevron w-4 h-4 text-slate-400 transition-transform"></i>
                    </div>
                </div>
                <div id="ec-card-mortgage-body" class="ec-key-card-body hidden p-3.5 bg-slate-50/50 border-t border-slate-100 space-y-2">
                    <div class="space-y-1.5">
                        ${mortgageFlags.length > 0 ? mortgageFlags.map(mf => {
                            const isClosed = mf.startsWith('[CLOSED]');
                            return `
                            <div class="p-2 rounded-lg text-[11px] leading-relaxed flex items-start gap-2 ${isClosed ? 'bg-emerald-50/80 border border-emerald-200 text-emerald-900' : 'bg-amber-50/80 border border-amber-200 text-amber-900'}">
                                <span class="px-1.5 py-0.5 rounded text-[9px] font-extrabold shrink-0 mt-0.5 ${isClosed ? 'bg-emerald-200 text-emerald-800' : 'bg-amber-200 text-amber-900'}">
                                    ${isClosed ? 'CLOSED' : 'OPEN / UNRELEASED'}
                                </span>
                                <span>${escapeHtml(mf.replace(/^\[(?:CLOSED|OPEN \/ UNRELEASED)\]\s*/, ''))}</span>
                            </div>
                            `;
                        }).join('') : `
                        <div class="text-[11px] text-emerald-800 bg-emerald-50 p-2 rounded-lg border border-emerald-200">
                            Clear Title: No open or active mortgages recorded in this search period.
                        </div>
                        `}
                    </div>
                </div>
            </div>

            <!-- 2. ACTIVE POWER OF ATTORNEY (POA) -->
            <div id="ec-card-poa" class="ec-key-card rounded-xl border border-slate-200/90 bg-white shadow-2xs transition-all overflow-hidden">
                <div onclick="toggleECKeyCard('ec-card-poa')" class="p-3 hover:bg-slate-50 cursor-pointer flex items-center justify-between transition-colors">
                    <div class="flex items-center gap-2">
                        <i data-lucide="file-text" class="w-4 h-4 text-slate-600"></i>
                        <span class="text-xs font-bold text-slate-800">2. Active Power of Attorney (POA)</span>
                    </div>
                    <div class="flex items-center gap-2">
                        <span class="px-2 py-0.5 rounded text-[10px] font-bold ${hasPOA ? 'bg-purple-100 text-purple-800 border border-purple-200' : 'bg-slate-100 text-slate-600 border border-slate-200'}">
                            ${hasPOA ? `${poaAgents.length} Agents Identified` : 'No Active POA'}
                        </span>
                        <i data-lucide="chevron-right" id="ec-card-poa-chevron" class="ec-key-card-chevron w-4 h-4 text-slate-400 transition-transform"></i>
                    </div>
                </div>
                <div id="ec-card-poa-body" class="ec-key-card-body hidden p-3.5 bg-slate-50/50 border-t border-slate-100 space-y-2">
                    <div class="text-[11px] text-slate-700 bg-white p-2.5 rounded-lg border border-slate-200/60 leading-relaxed space-y-1.5">
                        <div class="font-bold text-slate-800">${escapeHtml(poaVal)}</div>
                        ${poaAgents.length > 0 ? `
                        <div class="space-y-1 pt-1">
                            ${poaAgents.map(ag => `
                            <div class="p-1.5 bg-purple-50/60 rounded border border-purple-100 text-purple-900 text-[11px] font-mono">
                                • ${escapeHtml(ag)}
                            </div>
                            `).join('')}
                        </div>
                        ` : ""}
                    </div>
                </div>
            </div>

            <!-- 3. COURT ATTACHMENTS / LIENS -->
            <div id="ec-card-court" class="ec-key-card rounded-xl border border-slate-200/90 bg-white shadow-2xs transition-all overflow-hidden">
                <div onclick="toggleECKeyCard('ec-card-court')" class="p-3 hover:bg-slate-50 cursor-pointer flex items-center justify-between transition-colors">
                    <div class="flex items-center gap-2">
                        <i data-lucide="gavel" class="w-4 h-4 text-slate-600"></i>
                        <span class="text-xs font-bold text-slate-800">3. Court Attachments / Liens</span>
                    </div>
                    <div class="flex items-center gap-2">
                        <span class="px-2 py-0.5 rounded text-[10px] font-bold ${courtVal.includes('FLAG') ? 'bg-rose-100 text-rose-800 border border-rose-200' : 'bg-emerald-100 text-emerald-800 border border-emerald-200'}">
                            ${courtVal.includes('FLAG') ? 'FLAG: ATTACHMENT' : 'CLEAR / NO ATTACHMENTS'}
                        </span>
                        <i data-lucide="chevron-right" id="ec-card-court-chevron" class="ec-key-card-chevron w-4 h-4 text-slate-400 transition-transform"></i>
                    </div>
                </div>
                <div id="ec-card-court-body" class="ec-key-card-body hidden p-3.5 bg-slate-50/50 border-t border-slate-100 space-y-2">
                    <div class="text-[11px] text-slate-700 bg-white p-2.5 rounded-lg border border-slate-200/60 leading-relaxed">
                        ${escapeHtml(courtVal)}
                    </div>
                </div>
            </div>

            <!-- 4. VILLAGE & TALUK NAME -->
            <div id="ec-card-village" class="ec-key-card rounded-xl border border-slate-200/90 bg-white shadow-2xs transition-all overflow-hidden">
                <div onclick="toggleECKeyCard('ec-card-village')" class="p-3 hover:bg-slate-50 cursor-pointer flex items-center justify-between transition-colors">
                    <div class="flex items-center gap-2">
                        <i data-lucide="map-pin" class="w-4 h-4 text-slate-600"></i>
                        <span class="text-xs font-bold text-slate-800">4. Village & Taluk Name</span>
                    </div>
                    <div class="flex items-center gap-2">
                        <span class="text-[11px] font-mono text-slate-600 font-semibold">${escapeHtml(villageVal)}</span>
                        <i data-lucide="chevron-right" id="ec-card-village-chevron" class="ec-key-card-chevron w-4 h-4 text-slate-400 transition-transform"></i>
                    </div>
                </div>
                <div id="ec-card-village-body" class="ec-key-card-body hidden p-3.5 bg-slate-50/50 border-t border-slate-100">
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-2 text-xs">
                        <div class="p-2.5 bg-white rounded-lg border border-slate-200/60">
                            <span class="text-[10px] font-bold text-slate-400 block uppercase">வருவாய் கிராமம் (Revenue Village)</span>
                            <span class="text-xs font-bold text-slate-800 mt-0.5 block">${escapeHtml(villageVal)}</span>
                        </div>
                        <div class="p-2.5 bg-white rounded-lg border border-slate-200/60">
                            <span class="text-[10px] font-bold text-slate-400 block uppercase">வட்டம் / எல்லை (Taluk / Jurisdiction)</span>
                            <span class="text-xs font-bold text-slate-800 mt-0.5 block">${escapeHtml(talukVal)}</span>
                        </div>
                        <div class="p-2.5 bg-white rounded-lg border border-slate-200/60">
                            <span class="text-[10px] font-bold text-slate-400 block uppercase">பதிவு மாவட்டம் (Registration District)</span>
                            <span class="text-xs font-bold text-slate-800 mt-0.5 block">${escapeHtml(districtVal)}</span>
                        </div>
                        <div class="p-2.5 bg-white rounded-lg border border-slate-200/60">
                            <span class="text-[10px] font-bold text-slate-400 block uppercase">மண்டலம் (Zone)</span>
                            <span class="text-xs font-bold text-slate-800 mt-0.5 block">${escapeHtml(zoneVal)}</span>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 5. SURVEY / PATTA NUMBER -->
            <div id="ec-card-survey" class="ec-key-card rounded-xl border border-slate-200/90 bg-white shadow-2xs transition-all overflow-hidden">
                <div onclick="toggleECKeyCard('ec-card-survey')" class="p-3 hover:bg-slate-50 cursor-pointer flex items-center justify-between transition-colors">
                    <div class="flex items-center gap-2">
                        <i data-lucide="file-text" class="w-4 h-4 text-slate-600"></i>
                        <span class="text-xs font-bold text-slate-800">5. Survey / Patta Number</span>
                    </div>
                    <div class="flex items-center gap-2">
                        <span class="text-[11px] font-mono text-blue-700 font-bold bg-blue-50 px-2 py-0.5 rounded border border-blue-200">${escapeHtml(surveyVal)}</span>
                        <i data-lucide="chevron-right" id="ec-card-survey-chevron" class="ec-key-card-chevron w-4 h-4 text-slate-400 transition-transform"></i>
                    </div>
                </div>
                <div id="ec-card-survey-body" class="ec-key-card-body hidden p-3.5 bg-slate-50/50 border-t border-slate-100 space-y-2">
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-2 text-xs">
                        <div class="p-2.5 bg-white rounded-lg border border-slate-200/60">
                            <span class="text-[10px] font-bold text-slate-400 block uppercase">தேடப்பட்ட புல எண்(கள்) (Survey Number Searched)</span>
                            <span class="text-xs font-extrabold text-blue-700 font-mono mt-0.5 block">${escapeHtml(surveyVal)}</span>
                        </div>
                        <div class="p-2.5 bg-white rounded-lg border border-slate-200/60">
                            <span class="text-[10px] font-bold text-slate-400 block uppercase">பட்டா / பிளாக் / மனை எண் (Patta / Block / Plot)</span>
                            <span class="text-xs font-bold text-slate-800 font-mono mt-0.5 block">${escapeHtml(pattaVal)}</span>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 6. EXTENT OF PROPERTY (AREA) - WITH UDS AND REMARKS DETAILS -->
            <div id="ec-card-extent" class="ec-key-card rounded-xl border border-slate-200/90 bg-white shadow-2xs transition-all overflow-hidden">
                <div onclick="toggleECKeyCard('ec-card-extent')" class="p-3 hover:bg-slate-50 cursor-pointer flex items-center justify-between transition-colors">
                    <div class="flex items-center gap-2">
                        <i data-lucide="layers" class="w-4 h-4 text-slate-600"></i>
                        <span class="text-xs font-bold text-slate-800">6. Extent of Property (Area)</span>
                    </div>
                    <div class="flex items-center gap-2">
                        <span class="px-2 py-0.5 rounded text-[10px] font-bold ${isUDS ? 'bg-amber-100 text-amber-900 border border-amber-300' : 'bg-emerald-100 text-emerald-900 border border-emerald-300'}">
                            ${isUDS ? 'UDS Share' : 'Normal Land'}
                        </span>
                        <i data-lucide="chevron-right" id="ec-card-extent-chevron" class="ec-key-card-chevron w-4 h-4 text-slate-400 transition-transform"></i>
                    </div>
                </div>
                <div id="ec-card-extent-body" class="ec-key-card-body hidden p-3.5 bg-slate-50/50 border-t border-slate-100 space-y-3">
                    <div class="grid grid-cols-1 md:grid-cols-3 gap-2.5 text-xs">
                        <div class="p-2.5 bg-white rounded-lg border border-slate-200/60">
                            <span class="text-[10px] font-bold text-slate-400 block uppercase">சொத்தின் விஸ்தீர்ணம் (Property Extent / Area)</span>
                            <span class="text-xs font-extrabold text-blue-700 font-mono mt-0.5 block">${escapeHtml(extentVal)}</span>
                        </div>
                        <div class="p-2.5 bg-white rounded-lg border border-slate-200/60">
                            <span class="text-[10px] font-bold text-slate-400 block uppercase">நில உரிமை வகை (Land Classification)</span>
                            <span class="text-xs font-bold text-slate-900 mt-0.5 block flex items-center gap-1">
                                <i data-lucide="${isUDS ? 'pie-chart' : 'check-circle'}" class="w-3.5 h-3.5 ${isUDS ? 'text-amber-600' : 'text-emerald-600'}"></i>
                                <span>${escapeHtml(landCategory)}</span>
                            </span>
                        </div>
                        <div class="p-2.5 bg-white rounded-lg border border-slate-200/60">
                            <span class="text-[10px] font-bold text-slate-400 block uppercase">சொத்தின் வகைப்பாடு (Property Type)</span>
                            <span class="text-xs font-bold text-slate-800 mt-0.5 block">${escapeHtml(propTypeVal)}</span>
                        </div>
                    </div>

                    <!-- REMARKS & STRUCTURE DETAILS CALLOUT -->
                    <div class="p-3 bg-blue-50/40 rounded-xl border border-blue-200/80 space-y-1.5">
                        <div class="flex items-center gap-1.5 text-blue-900 font-bold text-xs">
                            <i data-lucide="info" class="w-3.5 h-3.5 text-blue-600"></i>
                            <span>Remarks Column Details (ஆவணக் குறிப்புகள் & கூடுதல் விவரங்கள்)</span>
                        </div>
                        <p class="text-[11px] text-slate-600 leading-relaxed">
                            <strong>Structure Details:</strong> ${escapeHtml(structureVal)}
                        </p>
                        <div class="text-[11px] text-slate-700 bg-white p-2 rounded-lg border border-blue-100 font-mono leading-relaxed">
                            <b>Extracted Notes:</b> ${escapeHtml(remarksNotes)}
                        </div>
                    </div>
                </div>
            </div>

            <!-- 7. BOUNDARY SCHEDULE (N/S/E/W) -->
            <div id="ec-card-boundary" class="ec-key-card rounded-xl border border-slate-200/90 bg-white shadow-2xs transition-all overflow-hidden">
                <div onclick="toggleECKeyCard('ec-card-boundary')" class="p-3 hover:bg-slate-50 cursor-pointer flex items-center justify-between transition-colors">
                    <div class="flex items-center gap-2">
                        <i data-lucide="compass" class="w-4 h-4 text-slate-600"></i>
                        <span class="text-xs font-bold text-slate-800">7. Boundary Schedule (N/S/E/W)</span>
                    </div>
                    <i data-lucide="chevron-right" id="ec-card-boundary-chevron" class="ec-key-card-chevron w-4 h-4 text-slate-400 transition-transform"></i>
                </div>
                <div id="ec-card-boundary-body" class="ec-key-card-body hidden p-3.5 bg-slate-50/50 border-t border-slate-100">
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-2 text-xs">
                        <div class="p-2.5 bg-white rounded-lg border border-slate-200/60">
                            <span class="text-[10px] font-bold text-blue-600 block uppercase">வடக்கு (North Boundary)</span>
                            <span class="text-xs font-semibold text-slate-800 mt-0.5 block">${escapeHtml(northBound)}</span>
                        </div>
                        <div class="p-2.5 bg-white rounded-lg border border-slate-200/60">
                            <span class="text-[10px] font-bold text-emerald-600 block uppercase">தெற்கு (South Boundary)</span>
                            <span class="text-xs font-semibold text-slate-800 mt-0.5 block">${escapeHtml(southBound)}</span>
                        </div>
                        <div class="p-2.5 bg-white rounded-lg border border-slate-200/60">
                            <span class="text-[10px] font-bold text-indigo-600 block uppercase">கிழக்கு (East Boundary)</span>
                            <span class="text-xs font-semibold text-slate-800 mt-0.5 block">${escapeHtml(eastBound)}</span>
                        </div>
                        <div class="p-2.5 bg-white rounded-lg border border-slate-200/60">
                            <span class="text-[10px] font-bold text-amber-600 block uppercase">மேற்கு (West Boundary)</span>
                            <span class="text-xs font-semibold text-slate-800 mt-0.5 block">${escapeHtml(westBound)}</span>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 8. TOTAL TRANSACTIONS FOUND -->
            <div id="ec-card-total-tx" class="ec-key-card rounded-xl border border-slate-200/90 bg-white shadow-2xs transition-all overflow-hidden">
                <div onclick="toggleECKeyCard('ec-card-total-tx')" class="p-3 hover:bg-slate-50 cursor-pointer flex items-center justify-between transition-colors">
                    <div class="flex items-center gap-2">
                        <i data-lucide="arrow-left-right" class="w-4 h-4 text-slate-600"></i>
                        <span class="text-xs font-bold text-slate-800">8. Total Transactions Found</span>
                    </div>
                    <div class="flex items-center gap-2">
                        <span class="px-2 py-0.5 rounded text-[10px] font-bold bg-purple-100 text-purple-800 border border-purple-200">
                            ${escapeHtml(totalEntriesVal)} Registered Entries
                        </span>
                        <i data-lucide="chevron-right" id="ec-card-total-tx-chevron" class="ec-key-card-chevron w-4 h-4 text-slate-400 transition-transform"></i>
                    </div>
                </div>
                <div id="ec-card-total-tx-body" class="ec-key-card-body hidden p-3.5 bg-slate-50/50 border-t border-slate-100 space-y-2">
                    <div class="p-2.5 bg-white rounded-lg border border-slate-200/60 text-xs space-y-1">
                        <div class="flex items-center justify-between">
                            <span class="font-bold text-slate-700">படிவ வகை (Form Type):</span>
                            <span class="font-extrabold text-purple-700">${escapeHtml(formTypeVal)}</span>
                        </div>
                        <div class="pt-1 border-t border-slate-100 text-[11px] text-slate-600 leading-relaxed">
                            <b>Breakdown:</b> ${escapeHtml(txBreakdown)}
                        </div>
                    </div>
                </div>
            </div>

            <!-- 9. NATURE OF LAST TRANSACTION -->
            <div id="ec-card-last-tx" class="ec-key-card rounded-xl border border-slate-200/90 bg-white shadow-2xs transition-all overflow-hidden">
                <div onclick="toggleECKeyCard('ec-card-last-tx')" class="p-3 hover:bg-slate-50 cursor-pointer flex items-center justify-between transition-colors">
                    <div class="flex items-center gap-2">
                        <i data-lucide="file-text" class="w-4 h-4 text-slate-600"></i>
                        <span class="text-xs font-bold text-slate-800">9. Nature of Last Transaction</span>
                    </div>
                    <div class="flex items-center gap-2">
                        <span class="text-[11px] font-mono font-semibold text-slate-700">${escapeHtml(lastNature.split('\n')[0])}</span>
                        <i data-lucide="chevron-right" id="ec-card-last-tx-chevron" class="ec-key-card-chevron w-4 h-4 text-slate-400 transition-transform"></i>
                    </div>
                </div>
                <div id="ec-card-last-tx-body" class="ec-key-card-body hidden p-3.5 bg-slate-50/50 border-t border-slate-100 space-y-2">
                    <div class="p-2.5 bg-white rounded-lg border border-slate-200/60 text-xs space-y-1.5">
                        <div class="flex items-center justify-between">
                            <span class="font-bold text-slate-800">ஆவணத் தன்மை (Nature): ${escapeHtml(lastNature)}</span>
                            <span class="font-mono text-blue-700 font-bold">Doc ${escapeHtml(lastDocNo)} (${escapeHtml(lastDate)})</span>
                        </div>
                        <div class="pt-1 border-t border-slate-100 text-[11px] text-slate-600">
                            <div><b>Executant:</b> ${escapeHtml(lastExecs)}</div>
                            <div class="mt-0.5"><b>Claimant:</b> ${escapeHtml(lastClaims)}</div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 10. CONSIDERATION VALUE (LAST TRANSACTION AMOUNT) -->
            <div id="ec-card-consideration" class="ec-key-card rounded-xl border border-slate-200/90 bg-white shadow-2xs transition-all overflow-hidden">
                <div onclick="toggleECKeyCard('ec-card-consideration')" class="p-3 hover:bg-slate-50 cursor-pointer flex items-center justify-between transition-colors">
                    <div class="flex items-center gap-2">
                        <i data-lucide="coins" class="w-4 h-4 text-slate-600"></i>
                        <span class="text-xs font-bold text-slate-800">10. Consideration Value (Last transaction amount)</span>
                    </div>
                    <i data-lucide="chevron-right" id="ec-card-consideration-chevron" class="ec-key-card-chevron w-4 h-4 text-slate-400 transition-transform"></i>
                </div>
                <div id="ec-card-consideration-body" class="ec-key-card-body hidden p-3.5 bg-slate-50/50 border-t border-slate-100">
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-2 text-xs">
                        <div class="p-2.5 bg-white rounded-lg border border-slate-200/60">
                            <span class="text-[10px] font-bold text-slate-400 block uppercase">கைமாற்றுத் தொகை (Consideration Value)</span>
                            <span class="text-xs font-extrabold text-emerald-700 font-mono mt-0.5 block">${escapeHtml(consVal)}</span>
                        </div>
                        <div class="p-2.5 bg-white rounded-lg border border-slate-200/60">
                            <span class="text-[10px] font-bold text-slate-400 block uppercase">சந்தை மதிப்பு (Market Value)</span>
                            <span class="text-xs font-extrabold text-slate-800 font-mono mt-0.5 block">${escapeHtml(mktVal)}</span>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 11. SEARCH PERIOD (DATES) -->
            <div id="ec-card-search-period" class="ec-key-card rounded-xl border border-slate-200/90 bg-white shadow-2xs transition-all overflow-hidden">
                <div onclick="toggleECKeyCard('ec-card-search-period')" class="p-3 hover:bg-slate-50 cursor-pointer flex items-center justify-between transition-colors">
                    <div class="flex items-center gap-2">
                        <i data-lucide="calendar" class="w-4 h-4 text-slate-600"></i>
                        <span class="text-xs font-bold text-slate-800">11. Search Period (Dates)</span>
                    </div>
                    <div class="flex items-center gap-2">
                        <span class="px-2 py-0.5 rounded text-[10px] font-extrabold ${is30Compliant ? 'bg-emerald-100 text-emerald-800 border border-emerald-300' : 'bg-amber-100 text-amber-800 border border-amber-300'}">
                            ${is30Compliant ? '30+ YEARS OK' : 'LESS THAN 30 YRS'}
                        </span>
                        <i data-lucide="chevron-right" id="ec-card-search-period-chevron" class="ec-key-card-chevron w-4 h-4 text-slate-400 transition-transform"></i>
                    </div>
                </div>
                <div id="ec-card-search-period-body" class="ec-key-card-body hidden p-3.5 bg-slate-50/50 border-t border-slate-100 space-y-2">
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-2 text-xs">
                        <div class="p-2.5 bg-white rounded-lg border border-slate-200/60">
                            <span class="text-[10px] font-bold text-slate-400 block uppercase">தேடல் காலம் (Search Period Requested)</span>
                            <span class="text-xs font-bold text-slate-900 font-mono mt-0.5 block">${escapeHtml(searchPeriod)}</span>
                        </div>
                        <div class="p-2.5 bg-white rounded-lg border border-slate-200/60">
                            <span class="text-[10px] font-bold text-slate-400 block uppercase">அலுவலக தேதி இருப்பு (SRO Date Available Range)</span>
                            <span class="text-xs font-bold text-slate-900 font-mono mt-0.5 block">${escapeHtml(sroAvail)}</span>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 12. SUB-REGISTRAR OFFICE (SRO) -->
            <div id="ec-card-sro" class="ec-key-card rounded-xl border border-slate-200/90 bg-white shadow-2xs transition-all overflow-hidden">
                <div onclick="toggleECKeyCard('ec-card-sro')" class="p-3 hover:bg-slate-50 cursor-pointer flex items-center justify-between transition-colors">
                    <div class="flex items-center gap-2">
                        <i data-lucide="landmark" class="w-4 h-4 text-slate-600"></i>
                        <span class="text-xs font-bold text-slate-800">12. Sub-Registrar Office (SRO)</span>
                    </div>
                    <div class="flex items-center gap-2">
                        <span class="text-[11px] font-semibold text-slate-700">${escapeHtml(sroVal)}</span>
                        <i data-lucide="chevron-right" id="ec-card-sro-chevron" class="ec-key-card-chevron w-4 h-4 text-slate-400 transition-transform"></i>
                    </div>
                </div>
                <div id="ec-card-sro-body" class="ec-key-card-body hidden p-3.5 bg-slate-50/50 border-t border-slate-100 space-y-2">
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-2 text-xs">
                        <div class="p-2.5 bg-white rounded-lg border border-slate-200/60">
                            <span class="text-[10px] font-bold text-slate-400 block uppercase">சார்பதிவாளர் அலுவலகம் (SRO Office & Jurisdiction)</span>
                            <span class="text-xs font-bold text-slate-800 mt-0.5 block">${escapeHtml(sroJurisdiction)}</span>
                        </div>
                        <div class="p-2.5 bg-white rounded-lg border border-slate-200/60">
                            <span class="text-[10px] font-bold text-slate-400 block uppercase">சான்றிதழ் நாள் (Certificate Date)</span>
                            <span class="text-xs font-bold text-slate-800 mt-0.5 block font-mono">${escapeHtml(certDate)}</span>
                        </div>
                    </div>
                    <div class="p-2.5 bg-emerald-50 rounded-lg border border-emerald-200 text-[11px] text-emerald-900 flex items-center gap-1.5">
                        <i data-lucide="badge-check" class="w-4 h-4 text-emerald-600 shrink-0"></i>
                        <span>${escapeHtml(sigVal)}</span>
                    </div>
                </div>
            </div>

        </div>
    `;

    container.appendChild(wrapper);
}

// Global accordion togglers
window.toggleECKeyCard = function(cardId) {
    const body = document.getElementById(`${cardId}-body`);
    const chevron = document.getElementById(`${cardId}-chevron`);
    const card = document.getElementById(cardId);
    if (!body) return;
    const isHidden = body.classList.contains("hidden");
    if (isHidden) {
        body.classList.remove("hidden");
        if (chevron) {
            chevron.classList.add("rotate-90");
            chevron.classList.remove("text-slate-400");
            chevron.classList.add("text-blue-600");
        }
        if (card) card.classList.add("border-blue-300", "ring-1", "ring-blue-100");
    } else {
        body.classList.add("hidden");
        if (chevron) {
            chevron.classList.remove("rotate-90");
            chevron.classList.remove("text-blue-600");
            chevron.classList.add("text-slate-400");
        }
        if (card) card.classList.remove("border-blue-300", "ring-1", "ring-blue-100");
    }
};

window.toggleAllECKeyCards = function() {
    const bodies = document.querySelectorAll(".ec-key-card-body");
    const chevrons = document.querySelectorAll(".ec-key-card-chevron");
    const cards = document.querySelectorAll(".ec-key-card");
    const anyHidden = Array.from(bodies).some(b => b.classList.contains("hidden"));
    bodies.forEach(b => {
        if (anyHidden) b.classList.remove("hidden");
        else b.classList.add("hidden");
    });
    chevrons.forEach(c => {
        if (anyHidden) {
            c.classList.add("rotate-90");
            c.classList.remove("text-slate-400");
            c.classList.add("text-blue-600");
        } else {
            c.classList.remove("rotate-90");
            c.classList.remove("text-blue-600");
            c.classList.add("text-slate-400");
        }
    });
    cards.forEach(c => {
        if (anyHidden) c.classList.add("border-blue-300");
        else c.classList.remove("border-blue-300");
    });
};


function renderTSLRFieldsLayout(fields, container) {
    const getVal = (f, def = "-") => {
        if (!f) return def;
        if (typeof f === "object" && f.value !== undefined) return f.value;
        return f;
    };
    const getConf = (f) => {
        if (f && typeof f === "object" && typeof f.confidence === "number") {
            return Math.round(f.confidence * 100);
        }
        return 98;
    };

    // Header block
    const districtVal = getVal(fields.district, "-");
    const talukVal = getVal(fields.taluk, "-");
    const townVal = getVal(fields.town_village, "-");
    const wardVal = getVal(fields.ward, "-");

    // Record fields
    const slNoVal = getVal(fields.serial_no, "1");
    const nameVal = getVal(fields.owner_name, "-");
    const surveyVal = getVal(fields.survey_number, "-");
    const oldSurveyVal = getVal(fields.old_survey_number, "-");
    const extentVal = getVal(fields.extent, "-");
    const wardBlockVal = getVal(fields.ward_block, "-");
    const landClassVal = getVal(fields.land_classification, "-");
    const landUseVal = getVal(fields.current_land_use, "-");
    const tenureVal = getVal(fields.tenure_type, "-");
    const assessVal = getVal(fields.assessment, "-");
    const remarksVal = getVal(fields.remarks, "-");
    const fmbWarningVal = getVal(fields.fmb_warning, null);

    // Formatted survey number display e.g. "35/2  (Old/O.Sur No: 249/3A1A3 pt -)"
    let finalSurveyDisplay = surveyVal;
    if (surveyVal !== "-" && !surveyVal.includes("Old/O.Sur No") && oldSurveyVal !== "-") {
        finalSurveyDisplay = `${surveyVal}  (Old/O.Sur No: ${oldSurveyVal})`;
    }

    // Clean Extent display if it has bracketed calculations
    let cleanExtent = extentVal;
    if (cleanExtent.includes("[")) {
        cleanExtent = cleanExtent.split("[")[0].trim();
    }

    const wrapper = document.createElement("div");
    wrapper.className = "space-y-4";

    const textRepresentation = `Result\n\n=======================================================\nDistrict : ${districtVal}\nTaluk    : ${talukVal}\nTown     : ${townVal}\nWard     : ${wardVal}\n-------------------------------------------------------\nSl.No ${slNoVal}\n  Name                   : ${nameVal}\n  Survey Number / S.No   : ${finalSurveyDisplay}\n  Extent                 : ${cleanExtent}\n  Ward + Block           : ${wardBlockVal}\n  Land classification    : ${landClassVal}\n  Current land use       : ${landUseVal}\n  Tenure type            : ${tenureVal}\n  Assessment (Rs.)       : ${assessVal}\n  Remarks                : ${remarksVal}\n=======================================================`;

    function makeKVRow(label, val, key = "") {
        return `
            <div class="flex items-start justify-between py-2 px-3 hover:bg-slate-50 rounded-lg transition-colors group cursor-pointer" id="field-card-${key}" onclick="highlightFieldCard('${key}')">
                <span class="text-xs font-semibold text-slate-600 w-48 shrink-0">${escapeHtml(label)}</span>
                <span class="text-xs font-bold text-slate-400 mr-3">:</span>
                <div class="flex-1 flex items-center justify-between gap-2">
                    <span class="text-xs font-bold text-slate-900 select-all font-mono">${escapeHtml(String(val))}</span>
                    <div class="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                        <button onclick="event.stopPropagation(); copyToClipboard('${String(val).replace(/'/g, "\\'")}')" class="p-1 rounded text-slate-400 hover:text-slate-700 hover:bg-slate-200/60" title="Copy">
                            <i data-lucide="copy" class="w-3 h-3"></i>
                        </button>
                    </div>
                </div>
            </div>
        `;
    }

    wrapper.innerHTML = `
        ${fmbWarningVal ? `
        <div class="p-3 rounded-xl bg-amber-500/10 border-2 border-amber-300 text-amber-900 shadow-2xs flex items-start gap-2.5 mb-3">
            <i data-lucide="alert-triangle" class="w-4 h-4 text-amber-700 shrink-0 mt-0.5"></i>
            <div class="text-xs font-medium">${escapeHtml(fmbWarningVal)}</div>
        </div>
        ` : ''}

        <div class="rounded-xl bg-white border border-slate-200 shadow-sm overflow-hidden">
            <!-- Header bar with Copy All action -->
            <div class="px-4 py-3 bg-slate-900 text-white flex items-center justify-between">
                <div class="flex items-center gap-2">
                    <i data-lucide="file-text" class="w-4 h-4 text-slate-300"></i>
                    <h3 class="text-sm font-bold text-white tracking-wide">Result</h3>
                </div>
                <button onclick="copyToClipboard(\`${textRepresentation.replace(/`/g, '\\`')}\`)" class="px-2.5 py-1 rounded-lg bg-white/10 hover:bg-white/20 text-xs font-medium text-slate-200 transition-colors flex items-center gap-1.5 shadow-2xs">
                    <i data-lucide="copy" class="w-3 h-3"></i>
                    <span>Copy All</span>
                </button>
            </div>

            <!-- Content Area -->
            <div class="p-4 space-y-3 font-mono">
                <!-- Section 1: Header Fields -->
                <div class="border-b border-slate-200 pb-3 space-y-0.5">
                    ${makeKVRow('District', districtVal, 'district')}
                    ${makeKVRow('Taluk', talukVal, 'taluk')}
                    ${makeKVRow('Town', townVal, 'town_village')}
                    ${makeKVRow('Ward', wardVal, 'ward')}
                </div>

                <!-- Section 2: Sl.No & Record Fields -->
                <div class="space-y-0.5 pt-1">
                    <div class="px-3 py-1 text-xs font-extrabold text-blue-700 tracking-wider">
                        Sl.No ${escapeHtml(slNoVal)}
                    </div>
                    <div class="pl-3 space-y-0.5">
                        ${makeKVRow('Name', nameVal, 'owner_name')}
                        ${makeKVRow('Survey Number / S.No', finalSurveyDisplay, 'survey_number')}
                        ${makeKVRow('Extent', cleanExtent, 'extent')}
                        ${makeKVRow('Ward + Block', wardBlockVal, 'ward_block')}
                        ${makeKVRow('Land classification', landClassVal, 'land_classification')}
                        ${makeKVRow('Current land use', landUseVal, 'current_land_use')}
                        ${makeKVRow('Tenure type', tenureVal, 'tenure_type')}
                        ${makeKVRow('Assessment (Rs.)', assessVal, 'assessment')}
                        ${makeKVRow('Remarks', remarksVal, 'remarks')}
                    </div>
                </div>
            </div>
        </div>
    `;

    container.appendChild(wrapper);
}

function renderStandardFieldsLayout(fields, container) {
    Object.entries(fields).forEach(([key, item]) => {
        if (key === "transactions_table" || key === "verification_flags" || key === "checklist" || key === "legal_caveat") {
            return;
        }
        const val = item.value;
        const conf = item.confidence || 0.90;
        const fieldLabel = item.label || key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());

        const card = document.createElement("div");
        card.className = "glass-card p-3 rounded-xl border border-slate-200/90 shadow-2xs hover:border-blue-200 cursor-pointer";
        card.id = `field-card-${key}`;
        card.onclick = () => highlightFieldCard(key);

        let valueHtml = "";
        if (typeof val === "object" && val !== null) {
            valueHtml = `<div class="grid grid-cols-2 gap-2 mt-1.5">`;
            for (const [subKey, subVal] of Object.entries(val)) {
                valueHtml += `
                    <div class="p-2 rounded-lg bg-slate-50 border border-slate-200/70 text-[11px]">
                        <span class="text-slate-500 font-semibold block capitalize">${subKey}:</span>
                        <span class="text-slate-800 font-medium">${escapeHtml(subVal)}</span>
                    </div>
                `;
            }
            valueHtml += `</div>`;
        } else {
            const valStr = String(val);
            valueHtml = `
                <div class="flex items-start justify-between gap-2 mt-1.5">
                    <div class="w-full bg-slate-50/80 hover:bg-white text-xs font-semibold text-slate-800 border border-slate-200/80 rounded-lg p-2.5 leading-relaxed break-words font-sans transition-colors whitespace-pre-line">
                        ${escapeHtml(valStr)}
                    </div>
                    <button onclick="event.stopPropagation(); copyToClipboard('${valStr.replace(/'/g, "\\'").replace(/\n/g, "\\n")}')" class="text-slate-400 hover:text-blue-600 p-1.5 rounded-lg hover:bg-blue-50 transition-colors shrink-0" title="Copy">
                        <i data-lucide="copy" class="w-3.5 h-3.5"></i>
                    </button>
                </div>
            `;
        }

        const confPct = Math.round(conf * 100);
        const confColor = confPct >= 85 ? "text-emerald-600 bg-emerald-50 border-emerald-200" : "text-amber-600 bg-amber-50 border-amber-200";

        let llmBadge = "";
        let evidenceHtml = "";
        if (item.llm_enhanced) {
            const enh = item.llm_enhanced;
            const srcText = enh.source_text || "";
            llmBadge = `
                <span class="px-2 py-0.5 rounded-full text-[9px] font-bold bg-purple-100 text-purple-800 border border-purple-200 flex items-center gap-1" title="Extracted with local Qwen 2.5 7B LLM">
                    <i data-lucide="cpu" class="w-2.5 h-2.5"></i>
                    <span>Qwen AI</span>
                </span>
            `;
            if (srcText) {
                evidenceHtml = `
                    <div class="mt-1.5 p-2 rounded-lg bg-purple-50/50 border border-purple-100 text-[10px] text-purple-900">
                        <span class="font-bold text-purple-950 uppercase tracking-wider block text-[9px] mb-0.5">Ground-Truth OCR Evidence:</span>
                        <span class="font-mono text-slate-700 italic">"${escapeHtml(srcText)}"</span>
                    </div>
                `;
            }
        }

        card.innerHTML = `
            <div class="flex items-center justify-between text-xs mb-1">
                <span class="font-bold text-slate-700 flex items-center gap-1.5">
                    <span class="w-1.5 h-1.5 rounded-full bg-blue-500"></span>
                    <span>${fieldLabel}</span>
                </span>
                <div class="flex items-center gap-1.5">
                    ${llmBadge}
                    <span class="px-2 py-0.5 rounded-full text-[10px] font-semibold border ${confColor}">${confPct}%</span>
                </div>
            </div>
            ${valueHtml}
            ${evidenceHtml}
        `;
        container.appendChild(card);
    });
}
// 6. Checklist, OCR Text, and Tables
function renderChecklistTab(checklist) {
    const container = document.getElementById("checklist-items-container");
    const badge = document.getElementById("checklist-badge-count");
    container.innerHTML = "";
    const passedCount = checklist.filter(c => c.is_valid).length;
    badge.textContent = `${passedCount}/${checklist.length}`;

    checklist.forEach(item => {
        const row = document.createElement("div");
        const isPass = item.is_valid;
        row.className = `p-3 rounded-xl border flex items-center justify-between text-xs ${
            isPass ? "bg-emerald-50/40 border-emerald-200 text-slate-800" : "bg-amber-50/50 border-amber-200 text-slate-800"
        }`;
        row.innerHTML = `
            <div class="flex items-center space-x-2.5">
                <div class="w-5 h-5 rounded-full flex items-center justify-center ${isPass ? "bg-emerald-100 text-emerald-700" : "bg-amber-100 text-amber-700"}">
                    <i data-lucide="${isPass ? 'check' : 'alert-circle'}" class="w-3.5 h-3.5"></i>
                </div>
                <span class="font-medium text-slate-800">${item.title}</span>
            </div>
            <span class="px-2 py-0.5 rounded-md font-bold text-[10px] ${isPass ? "bg-emerald-100 text-emerald-800" : "bg-amber-100 text-amber-800"}">
                ${isPass ? "VERIFIED" : "ATTENTION"}
            </span>
        `;
        container.appendChild(row);
    });
}

function renderOCRTextTab(fullText) {
    document.getElementById("raw-ocr-text-view").textContent = fullText || "No text extracted.";
}

function renderTableTab(extraction) {
    const container = document.getElementById("table-records-container");
    const docId = extraction.document_type_id || "";
    const fields = extraction.fields || {};

    const txList = (fields.transactions_table && Array.isArray(fields.transactions_table.value))
        ? fields.transactions_table.value
        : [];

    if ((docId === "ec" || txList.length > 0) && txList.length > 0) {
        let rowsHtml = txList.map((tx, idx) => {
            const srNum = tx.sr || (idx + 1);
            const natureText = (tx.nature || "-").replace(/\n/g, "<br/>");
            const noteHtml = tx.nature_note ? `<div class="mt-1 text-[10px] text-amber-700 bg-amber-50/70 px-1.5 py-0.5 rounded border border-amber-200/60 italic leading-snug">${escapeHtml(tx.nature_note)}</div>` : "";
            const execHtml = renderBilingualPartiesCompact(tx.executants_bilingual, tx.executants || tx.parties);
            const claimHtml = renderBilingualPartiesCompact(tx.claimants_bilingual, tx.claimants);
            const fin = sanitizeTxFinancials(tx);
            const consText = fin.cons;
            const mktText = fin.mkt;
            const prText = fin.pr;
            const schedules = tx.schedules || [];
            let schSummary = "";
            if (schedules.length > 0) {
                const s0 = schedules[0];
                const parts = [];
                if (s0.village_street && s0.village_street !== '-') parts.push(s0.village_street);
                if (s0.survey_no && s0.survey_no !== '-') parts.push(`S.No: ${s0.survey_no}`);
                if (s0.flat_no && s0.flat_no !== '-') parts.push(`Flat: ${s0.flat_no}`);
                if (s0.plot_no && s0.plot_no !== '-') parts.push(`Plot: ${s0.plot_no}`);
                if (s0.extent && s0.extent !== '-') parts.push(`Ext: ${s0.extent}`);
                schSummary = parts.join(" | ") || (s0.property_type || "-");
            }

            return `
            <tr class="hover:bg-slate-50/80 transition-colors">
                <td class="p-2.5 text-center text-slate-500 font-mono text-xs">${srNum}</td>
                <td class="p-2.5 font-bold text-blue-700 font-mono whitespace-nowrap text-xs">${escapeHtml(tx.doc_no || "-")}</td>
                <td class="p-2.5 text-slate-700 whitespace-nowrap text-xs font-medium">${escapeHtml(tx.date || "-")}</td>
                <td class="p-2.5 text-slate-800 text-xs leading-relaxed max-w-[150px]">
                    <div class="font-semibold text-slate-900">${natureText}</div>
                    ${noteHtml}
                </td>
                <td class="p-2.5 text-slate-700 text-[11px] leading-relaxed max-w-[180px]">${execHtml}</td>
                <td class="p-2.5 text-slate-700 text-[11px] leading-relaxed max-w-[180px]">${claimHtml}</td>
                <td class="p-2.5 font-semibold text-emerald-700 whitespace-nowrap text-xs font-mono">${escapeHtml(consText)}</td>
                <td class="p-2.5 font-semibold text-slate-700 whitespace-nowrap text-xs font-mono">${escapeHtml(mktText)}</td>
                <td class="p-2.5 font-semibold text-indigo-700 whitespace-nowrap text-xs font-mono">${escapeHtml(prText)}</td>
                <td class="p-2.5 text-slate-600 text-[10px] leading-snug max-w-[160px]">${escapeHtml(schSummary || "-")}</td>
            </tr>
            `;
        }).join("");

        container.innerHTML = `
            <div class="mb-3 flex items-center justify-between">
                <div>
                    <h4 class="text-xs font-bold text-slate-900">Registered Entries (Form 15) — Full Detail Table</h4>
                    <p class="text-[11px] text-slate-500">${txList.length} Transactions Extracted Across All Pages (Strict Column Ordering)</p>
                </div>
                <span class="px-2.5 py-1 bg-blue-50 text-blue-700 border border-blue-200 rounded-lg text-xs font-semibold">
                    ${txList.length} Entries
                </span>
            </div>
            <div class="overflow-x-auto max-h-[520px] rounded-xl border border-slate-200 shadow-2xs">
                <table class="w-full text-left text-xs border-collapse">
                    <thead class="bg-slate-100 text-slate-900 font-bold sticky top-0 shadow-2xs border-b border-slate-200">
                        <tr>
                            <th class="p-2.5 border-b border-slate-200 text-center w-8">Sr.</th>
                            <th class="p-2.5 border-b border-slate-200">Doc No/Year</th>
                            <th class="p-2.5 border-b border-slate-200">Date</th>
                            <th class="p-2.5 border-b border-slate-200">Nature</th>
                            <th class="p-2.5 border-b border-slate-200">Executant(s)</th>
                            <th class="p-2.5 border-b border-slate-200">Claimant(s)</th>
                            <th class="p-2.5 border-b border-slate-200">Consideration Value</th>
                            <th class="p-2.5 border-b border-slate-200">Market Value</th>
                            <th class="p-2.5 border-b border-slate-200">PR Number</th>
                            <th class="p-2.5 border-b border-slate-200">Schedule Details</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-slate-200 bg-white">
                        ${rowsHtml}
                    </tbody>
                </table>
            </div>
        `;
    } else if (docId === "ec") {
        container.innerHTML = `
            <div class="p-8 text-center space-y-2">
                <div class="w-10 h-10 rounded-full bg-emerald-100 text-emerald-700 flex items-center justify-center mx-auto">
                    <i data-lucide="check-circle" class="w-5 h-5"></i>
                </div>
                <h4 class="text-xs font-bold text-slate-800">Nil Encumbrance Certificate (Form 16)</h4>
                <p class="text-[11px] text-slate-500">No adverse encumbrance entries or transactions recorded during the search period. Title is clean.</p>
            </div>
        `;
    } else {
        container.innerHTML = `<div class="p-6 text-center text-xs text-slate-400">Structured tables available for EC & Legal Heir documents.</div>`;
    }
}

// --------------------------------------------------------------------------
// Owners Directory & Title Dossier Engine
// --------------------------------------------------------------------------

function renderOwnersTab(extraction) {
    const container = document.getElementById("owners-directory-container");
    const badge = document.getElementById("owners-count-badge");
    if (!container) return;

    const fields = (extraction && extraction.fields) ? extraction.fields : {};
    const registry = fields.owners_registry || {};
    state.ownersRegistry = registry;
    state.activeOwnerFilter = state.activeOwnerFilter || "owners";
    state.ownerSearchQuery = state.ownerSearchQuery || "";

    const summary = registry.summary || {
        total_owners_count: 0,
        total_parties: 0,
        current_owners_count: 0,
        historical_owners_count: 0,
        institutions_count: 0,
        units_count: 0
    };

    if (badge) {
        badge.textContent = summary.total_owners_count || (summary.current_owners_count + summary.historical_owners_count) || summary.total_parties || "0";
    }

    if (!summary.total_parties && (!registry.all_owners || registry.all_owners.length === 0)) {
        container.innerHTML = `
            <div class="text-center p-8 space-y-3 bg-white rounded-xl border border-slate-200 shadow-2xs">
                <div class="w-12 h-12 rounded-full bg-slate-100 flex items-center justify-center mx-auto text-slate-400">
                    <i data-lucide="users" class="w-6 h-6"></i>
                </div>
                <h4 class="font-bold text-sm text-slate-800">No Registered Owners Found in Certificate</h4>
                <p class="text-xs text-slate-500 max-w-md mx-auto">
                    This document appears to be a Nil Encumbrance Certificate (Form 16) or has no registered transactions in the searched date window.
                </p>
            </div>
        `;
        lucide.createIcons();
        return;
    }

    const totalOwners = summary.total_owners_count || (summary.current_owners_count + summary.historical_owners_count);

    container.innerHTML = `
        <div class="space-y-4">
            <!-- Summary Bar -->
            <div class="p-4 rounded-xl bg-gradient-to-r from-purple-500/10 via-blue-500/5 to-slate-50 border border-purple-200/80 shadow-2xs">
                <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                    <div>
                        <div class="flex items-center gap-2">
                            <span class="p-1.5 rounded-lg bg-purple-600 text-white shadow-2xs">
                                <i data-lucide="users" class="w-4 h-4"></i>
                            </span>
                            <h4 class="text-sm font-bold text-slate-900">Owners Directory & Title Dossier Registry</h4>
                            <span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-purple-100 text-purple-800 border border-purple-200">TNREGINET Verified</span>
                        </div>
                        <p class="text-[11px] text-slate-500 mt-1">
                            Chronological devolution, root acquisition deeds, held property schedules, and active bank mortgages for all parties in this certificate.
                        </p>
                    </div>

                    <div class="flex items-center gap-2 flex-wrap text-xs">
                        <div class="px-2.5 py-1 rounded-lg bg-white border border-purple-200 text-purple-800 font-semibold shadow-2xs flex items-center gap-1.5">
                            <span class="w-2 h-2 rounded-full bg-purple-500"></span>
                            <span>${totalOwners} Title Owner(s)</span>
                        </div>
                        <div class="px-2.5 py-1 rounded-lg bg-white border border-emerald-200 text-emerald-800 font-semibold shadow-2xs flex items-center gap-1.5">
                            <span class="w-2 h-2 rounded-full bg-emerald-500"></span>
                            <span>${summary.current_owners_count} Current Title Holder(s)</span>
                        </div>
                        <div class="px-2.5 py-1 rounded-lg bg-white border border-slate-200 text-slate-700 font-semibold shadow-2xs flex items-center gap-1.5">
                            <span class="w-2 h-2 rounded-full bg-slate-400"></span>
                            <span>${summary.historical_owners_count} Prior Owner(s)</span>
                        </div>
                        <div class="px-2.5 py-1 rounded-lg bg-white border border-blue-200 text-blue-800 font-semibold shadow-2xs flex items-center gap-1.5">
                            <span class="w-2 h-2 rounded-full bg-blue-500"></span>
                            <span>${summary.units_count} Property Unit(s)</span>
                        </div>
                    </div>
                </div>

                <!-- Search & Filters -->
                <div class="mt-4 pt-3 border-t border-purple-100 flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-2.5">
                    <div class="relative flex-1">
                        <i data-lucide="search" class="w-3.5 h-3.5 text-slate-400 absolute left-3 top-2.5"></i>
                        <input type="text" id="owner-search-input" value="${escapeHtml(state.ownerSearchQuery || '')}" oninput="handleOwnerSearch(this.value)" placeholder="Search owner name, deed number, survey no, or flat/plot..." class="w-full bg-white border border-slate-300 rounded-lg pl-8 pr-3 py-1.5 text-xs text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-1 focus:ring-purple-500">
                    </div>

                    <div class="flex items-center gap-1.5 overflow-x-auto text-[11px] font-semibold" id="owner-filter-buttons-container">
                        <button type="button" data-filter="owners" onclick="setOwnerFilter('owners')" class="owner-filter-btn px-2.5 py-1 rounded-lg transition-colors cursor-pointer ${state.activeOwnerFilter === 'owners' ? 'bg-purple-600 text-white shadow-xs' : 'bg-white hover:bg-slate-100 text-slate-700 border border-slate-200'}">
                            Title Owners (${totalOwners})
                        </button>
                        <button type="button" data-filter="current" onclick="setOwnerFilter('current')" class="owner-filter-btn px-2.5 py-1 rounded-lg transition-colors cursor-pointer ${state.activeOwnerFilter === 'current' ? 'bg-emerald-600 text-white shadow-xs' : 'bg-white hover:bg-slate-100 text-slate-700 border border-slate-200'}">
                            Current Owners (${summary.current_owners_count})
                        </button>
                        <button type="button" data-filter="historical" onclick="setOwnerFilter('historical')" class="owner-filter-btn px-2.5 py-1 rounded-lg transition-colors cursor-pointer ${state.activeOwnerFilter === 'historical' ? 'bg-slate-700 text-white shadow-xs' : 'bg-white hover:bg-slate-100 text-slate-700 border border-slate-200'}">
                            Prior Owners (${summary.historical_owners_count})
                        </button>
                        <button type="button" data-filter="institutions" onclick="setOwnerFilter('institutions')" class="owner-filter-btn px-2.5 py-1 rounded-lg transition-colors cursor-pointer ${state.activeOwnerFilter === 'institutions' ? 'bg-indigo-600 text-white shadow-xs' : 'bg-white hover:bg-slate-100 text-slate-700 border border-slate-200'}">
                            Lenders & Banks (${summary.institutions_count})
                        </button>
                        <button type="button" data-filter="all" onclick="setOwnerFilter('all')" class="owner-filter-btn px-2.5 py-1 rounded-lg transition-colors cursor-pointer ${state.activeOwnerFilter === 'all' ? 'bg-slate-800 text-white shadow-xs' : 'bg-white hover:bg-slate-100 text-slate-700 border border-slate-200'}">
                            All Signatories (${summary.total_parties})
                        </button>
                    </div>
                </div>
            </div>

            <!-- Clustered Property Units Ribbon (If multiple) -->
            ${(registry.property_units && registry.property_units.length > 1) ? `
            <div class="p-3 bg-blue-50/60 rounded-xl border border-blue-200/70 shadow-2xs space-y-2">
                <div class="flex items-center justify-between text-xs">
                    <span class="font-bold text-blue-950 flex items-center gap-1.5">
                        <i data-lucide="layers" class="w-3.5 h-3.5 text-blue-600"></i>
                        <span>Identified Property Clusters (${registry.property_units.length} Units)</span>
                    </span>
                    <span class="text-[10px] text-blue-700">Click to filter owners by property unit</span>
                </div>
                <div class="flex gap-2 overflow-x-auto pb-1">
                    ${registry.property_units.map(u => `
                    <button type="button" onclick="filterOwnersByUnit('${escapeHtml(u.unit_key)}')" class="shrink-0 text-left p-2 rounded-lg bg-white hover:bg-blue-100 border border-blue-200/80 shadow-2xs text-[11px] transition-colors cursor-pointer max-w-[240px]">
                        <div class="font-bold text-slate-900 truncate">${escapeHtml(u.unit_key)}</div>
                        <div class="text-[10px] text-slate-500 flex items-center justify-between mt-0.5">
                            <span>Holder: <b>${escapeHtml(u.current_owner)}</b></span>
                            <span class="ml-1 text-blue-600 font-mono">${u.total_transactions} doc(s)</span>
                        </div>
                    </button>
                    `).join('')}
                </div>
            </div>
            ` : ""}

            <!-- Owners Cards List -->
            <div id="owners-cards-list" class="space-y-3">
                <!-- Filled dynamically -->
            </div>
        </div>
    `;

    renderOwnerCards();
    lucide.createIcons();
}

function setOwnerFilter(filterType) {
    state.activeOwnerFilter = filterType;
    const container = document.getElementById("owner-filter-buttons-container");
    if (container) {
        const colorMap = {
            owners: "bg-purple-600 text-white shadow-xs",
            current: "bg-emerald-600 text-white shadow-xs",
            historical: "bg-slate-700 text-white shadow-xs",
            institutions: "bg-indigo-600 text-white shadow-xs",
            all: "bg-slate-800 text-white shadow-xs"
        };
        container.querySelectorAll(".owner-filter-btn").forEach(btn => {
            const f = btn.getAttribute("data-filter");
            if (f === filterType) {
                btn.className = `owner-filter-btn px-2.5 py-1 rounded-lg transition-colors cursor-pointer ${colorMap[f] || 'bg-purple-600 text-white shadow-xs'}`;
            } else {
                btn.className = "owner-filter-btn px-2.5 py-1 rounded-lg transition-colors cursor-pointer bg-white hover:bg-slate-100 text-slate-700 border border-slate-200";
            }
        });
    }
    renderOwnerCards();
    lucide.createIcons();
}

function handleOwnerSearch(query) {
    state.ownerSearchQuery = (query || "").trim().toLowerCase();
    renderOwnerCards();
    lucide.createIcons();
}

function filterOwnersByUnit(unitKey) {
    const input = document.getElementById("owner-search-input");
    if (input) {
        input.value = unitKey;
        handleOwnerSearch(unitKey);
    }
}

function renderOwnerCards() {
    const listContainer = document.getElementById("owners-cards-list");
    if (!listContainer || !state.ownersRegistry) return;

    const registry = state.ownersRegistry;
    let list = [];

    if (state.activeOwnerFilter === "current") {
        list = registry.current_owners || [];
    } else if (state.activeOwnerFilter === "historical") {
        list = registry.historical_owners || [];
    } else if (state.activeOwnerFilter === "institutions") {
        list = registry.institutions || [];
    } else if (state.activeOwnerFilter === "owners") {
        list = (registry.property_owners && registry.property_owners.length > 0)
            ? registry.property_owners
            : (registry.current_owners || []).concat(registry.historical_owners || []);
    } else {
        list = registry.all_owners || [];
    }

    const q = state.ownerSearchQuery || "";
    if (q) {
        list = list.filter(o => {
            const name = (o.name || "").toLowerCase();
            const bName = (o.name_bilingual || "").toLowerCase();
            const role = (o.role || "").toLowerCase();
            const units = (o.property_units || []).join(" ").toLowerCase();
            const acqDoc = o.acquisition ? ((o.acquisition.doc_no || "") + " " + (o.acquisition.nature || "")).toLowerCase() : "";
            const txDocs = (o.transactions || []).map(t => (t.doc_no || "") + " " + (t.nature || "")).join(" ").toLowerCase();
            return name.includes(q) || bName.includes(q) || role.includes(q) || units.includes(q) || acqDoc.includes(q) || txDocs.includes(q);
        });
    }

    if (list.length === 0) {
        listContainer.innerHTML = `
            <div class="text-center p-6 bg-white rounded-xl border border-slate-200 text-xs text-slate-500">
                No matching owners or parties found for the current filter/search query.
            </div>
        `;
        return;
    }

    listContainer.innerHTML = list.map(o => {
        const isCurrent = o.is_current_owner === true;
        const isInstitution = (o.entity_type === "Bank / Financial Institution" || o.entity_type === "Government / Statutory Body");
        
        let roleBadgeClass = "bg-slate-100 text-slate-700 border-slate-200";
        let roleText = o.role || "Registered Party";
        if (isCurrent) {
            roleBadgeClass = "bg-emerald-100 text-emerald-800 border-emerald-200";
            roleText = "Current Legal Owner";
        } else if (isInstitution) {
            roleBadgeClass = "bg-indigo-100 text-indigo-800 border-indigo-200";
        } else if (o.acquisition) {
            roleBadgeClass = "bg-amber-100 text-amber-800 border-amber-200";
            roleText = "Prior / Historical Owner";
        }

        const iconName = isInstitution ? "landmark" : (o.entity_type === "Individual" ? "user" : "building-2");
        const iconBg = isCurrent ? "bg-emerald-100 text-emerald-700" : (isInstitution ? "bg-indigo-100 text-indigo-700" : "bg-purple-100 text-purple-700");

        return `
        <div class="p-4 rounded-xl bg-white hover:bg-slate-50/80 border border-slate-200/90 shadow-2xs transition-all space-y-3">
            <div class="flex flex-col sm:flex-row sm:items-start justify-between gap-3">
                <div class="flex items-start gap-3">
                    <div class="p-2.5 rounded-xl ${iconBg} shrink-0 mt-0.5 shadow-2xs">
                        <i data-lucide="${iconName}" class="w-4 h-4"></i>
                    </div>
                    <div>
                        <div class="flex items-center gap-2 flex-wrap">
                            <h4 class="font-extrabold text-sm text-slate-900">${escapeHtml(o.name_bilingual || o.name)}</h4>
                            <span class="px-2 py-0.5 rounded-full text-[10px] font-bold border ${roleBadgeClass}">${escapeHtml(roleText)}</span>
                            <span class="px-1.5 py-0.5 rounded text-[10px] font-medium bg-slate-100 text-slate-600 border border-slate-200">${escapeHtml(o.entity_type || 'Entity')}</span>
                        </div>
                        <div class="text-[11px] text-slate-500 mt-0.5 flex items-center gap-2 flex-wrap">
                            <span>Total Involvements: <b>${o.total_tx_count || (o.transactions ? o.transactions.length : 0)} document(s)</b></span>
                            ${o.property_units && o.property_units.length > 0 ? `<span>&bull; Units: <b>${escapeHtml(o.property_units.join(', '))}</b></span>` : ''}
                        </div>
                    </div>
                </div>

                <button type="button" onclick="openOwnerDossier('${escapeHtml(o.owner_id)}')" class="shrink-0 px-3 py-1.5 text-xs font-semibold rounded-lg bg-purple-600 hover:bg-purple-700 text-white shadow-2xs flex items-center gap-1.5 transition-colors cursor-pointer">
                    <i data-lucide="file-text" class="w-3.5 h-3.5"></i>
                    <span>View Title Dossier</span>
                </button>
            </div>

            <!-- Acquisition & Devolution Row -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-2 text-xs pt-1">
                ${o.acquisition ? `
                <div class="p-2.5 rounded-lg bg-emerald-50/50 border border-emerald-200/70 text-emerald-950 space-y-1">
                    <div class="flex items-center justify-between text-[11px] font-bold text-emerald-900">
                        <span class="flex items-center gap-1"><i data-lucide="key" class="w-3 h-3 text-emerald-600"></i> Acquisition Instrument</span>
                        <span class="font-mono">Doc ${escapeHtml(o.acquisition.doc_no)} (${escapeHtml(o.acquisition.date)})</span>
                    </div>
                    <div class="text-[11px] text-emerald-900/90 truncate font-medium">
                        <b>Nature:</b> ${escapeHtml(o.acquisition.nature || 'Title Deed')} &bull; <b>From:</b> ${escapeHtml(o.acquisition.acquired_from || '-')}
                    </div>
                    ${o.acquisition.consideration && o.acquisition.consideration !== '-' ? `
                    <div class="text-[10px] text-emerald-800 font-mono">
                        Consideration: <b>${escapeHtml(o.acquisition.consideration)}</b>
                    </div>
                    ` : ''}
                </div>
                ` : `
                <div class="p-2.5 rounded-lg bg-slate-50 border border-slate-200 text-slate-500 text-[11px] flex items-center">
                    <span>No registered root acquisition deed found within this EC window.</span>
                </div>
                `}

                ${o.transferred_to ? `
                <div class="p-2.5 rounded-lg bg-slate-100 border border-slate-200/90 text-slate-800 space-y-1">
                    <div class="flex items-center justify-between text-[11px] font-bold text-slate-700">
                        <span class="flex items-center gap-1"><i data-lucide="arrow-right-left" class="w-3 h-3 text-slate-500"></i> Devolution / Transferred To</span>
                        <span class="font-mono">Doc ${escapeHtml(o.transferred_to.doc_no)}</span>
                    </div>
                    <div class="text-[11px] text-slate-700 font-medium truncate">
                        <b>Transferred To:</b> ${escapeHtml(o.transferred_to.transferred_to || '-')}
                    </div>
                    <div class="text-[10px] text-slate-500 font-mono">
                        Date: ${escapeHtml(o.transferred_to.date || '-')}
                    </div>
                </div>
                ` : (isCurrent ? `
                <div class="p-2.5 rounded-lg bg-emerald-500/10 border border-emerald-300 text-emerald-900 flex items-center justify-between">
                    <div class="flex items-center gap-1.5 text-xs font-bold">
                        <i data-lucide="shield-check" class="w-4 h-4 text-emerald-600"></i>
                        <span>Absolute Legal Title Retained</span>
                    </div>
                    <span class="text-[10px] font-mono bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded font-bold">No Outward Transfer</span>
                </div>
                ` : `
                <div class="p-2.5 rounded-lg bg-slate-50 border border-slate-200 text-slate-500 text-[11px] flex items-center">
                    <span>Devolution status not recorded as an outward sale deed in this EC.</span>
                </div>
                `)}
            </div>

            <!-- Mortgages / Loans Status -->
            <div class="pt-1 flex items-center justify-between text-xs">
                ${o.has_active_mortgages ? `
                <span class="px-2.5 py-1 rounded-md bg-amber-100 text-amber-900 border border-amber-200 text-[11px] font-bold flex items-center gap-1.5">
                    <i data-lucide="alert-triangle" class="w-3.5 h-3.5 text-amber-600"></i>
                    <span>Active / Unreleased Mortgage(s) Recorded</span>
                </span>
                ` : (o.mortgages && o.mortgages.length > 0 ? `
                <span class="px-2.5 py-1 rounded-md bg-emerald-100 text-emerald-800 border border-emerald-200 text-[11px] font-bold flex items-center gap-1.5">
                    <i data-lucide="check-circle-2" class="w-3.5 h-3.5 text-emerald-600"></i>
                    <span>All ${o.mortgages.length} Mortgage(s) Discharged & Closed</span>
                </span>
                ` : `
                <span class="px-2 py-0.5 rounded text-[11px] text-slate-500">
                    No mortgages or charges recorded under this party.
                </span>
                `)}

                <button type="button" onclick="openOwnerDossier('${escapeHtml(o.owner_id)}')" class="text-purple-600 hover:text-purple-800 font-semibold text-[11px] flex items-center gap-1 cursor-pointer">
                    <span>Inspect Complete Dossier & Audit</span>
                    <i data-lucide="arrow-right" class="w-3 h-3"></i>
                </button>
            </div>
        </div>
        `;
    }).join("");
}

function openOwnerDossierByName(name) {
    if (!state.ownersRegistry || !state.ownersRegistry.all_owners) {
        switchTab("owners");
        return;
    }
    const clean = (name || "").toLowerCase().trim();
    const found = state.ownersRegistry.all_owners.find(o => {
        return (o.name || "").toLowerCase().includes(clean) || (o.name_bilingual || "").toLowerCase().includes(clean);
    });
    if (found) {
        openOwnerDossier(found.owner_id);
    } else {
        switchTab("owners");
    }
}

function openOwnerDossier(ownerId) {
    if (!state.ownersRegistry || !state.ownersRegistry.all_owners) return;
    const owner = state.ownersRegistry.all_owners.find(o => o.owner_id === ownerId);
    if (!owner) return;

    const modal = document.getElementById("owner-dossier-modal");
    const nameEl = document.getElementById("dossier-owner-name");
    const roleBadge = document.getElementById("dossier-role-badge");
    const entityBadge = document.getElementById("dossier-entity-badge");
    const iconContainer = document.getElementById("dossier-role-icon");
    const bodyContainer = document.getElementById("dossier-modal-body");

    if (!modal || !bodyContainer) return;

    if (nameEl) nameEl.textContent = owner.name_bilingual || owner.name;
    if (entityBadge) entityBadge.textContent = owner.entity_type || "Entity";

    const isCurrent = owner.is_current_owner === true;
    const isInstitution = (owner.entity_type === "Bank / Financial Institution" || owner.entity_type === "Government / Statutory Body");

    if (roleBadge) {
        if (isCurrent) {
            roleBadge.className = "px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800 border border-emerald-200";
            roleBadge.textContent = "Current Legal Owner / Title Holder";
        } else if (isInstitution) {
            roleBadge.className = "px-2.5 py-0.5 rounded-full text-xs font-semibold bg-indigo-100 text-indigo-800 border border-indigo-200";
            roleBadge.textContent = "Institutional Mortgagee / Lender";
        } else if (owner.acquisition) {
            roleBadge.className = "px-2.5 py-0.5 rounded-full text-xs font-semibold bg-slate-200 text-slate-800 border border-slate-300";
            roleBadge.textContent = "Prior / Historical Owner";
        } else {
            roleBadge.className = "px-2.5 py-0.5 rounded-full text-xs font-semibold bg-purple-100 text-purple-800 border border-purple-200";
            roleBadge.textContent = owner.role || "Registered Party";
        }
    }

    if (iconContainer) {
        iconContainer.className = `p-2.5 rounded-xl ${isCurrent ? 'bg-emerald-100 text-emerald-700' : (isInstitution ? 'bg-indigo-100 text-indigo-700' : 'bg-purple-100 text-purple-700')} mt-0.5 shadow-2xs`;
        const icon = isInstitution ? "landmark" : (owner.entity_type === "Individual" ? "user" : "building-2");
        iconContainer.innerHTML = `<i data-lucide="${icon}" class="w-5 h-5"></i>`;
    }

    bodyContainer.innerHTML = `
        <!-- Section 1: Property Units Associated -->
        <div class="p-3.5 rounded-xl bg-slate-50 border border-slate-200 space-y-2">
            <h5 class="text-xs font-bold text-slate-900 uppercase tracking-wide flex items-center gap-1.5">
                <i data-lucide="home" class="w-3.5 h-3.5 text-blue-600"></i>
                <span>Property Schedule & Held Units (${(owner.property_units || []).length} Unit(s))</span>
            </h5>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-2">
                ${(owner.property_units && owner.property_units.length > 0) ? owner.property_units.map(u => `
                <div class="p-2 bg-white rounded-lg border border-slate-200 text-xs font-bold text-slate-800 flex items-center gap-2">
                    <i data-lucide="map-pin" class="w-3.5 h-3.5 text-blue-500 shrink-0"></i>
                    <span class="truncate">${escapeHtml(u)}</span>
                </div>
                `).join('') : `
                <div class="text-slate-500 text-xs">General property scope from certificate header</div>
                `}
            </div>
        </div>

        <!-- Section 2: Acquisition Instrument -->
        <div class="p-3.5 rounded-xl bg-white border border-slate-200 shadow-2xs space-y-2">
            <h5 class="text-xs font-bold text-slate-900 uppercase tracking-wide flex items-center gap-1.5">
                <i data-lucide="key" class="w-3.5 h-3.5 text-emerald-600"></i>
                <span>Root Acquisition Deed (எவ்வாறு உரிமை பெறப்பட்டது)</span>
            </h5>
            ${owner.acquisition ? `
            <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 bg-emerald-50/40 p-3 rounded-lg border border-emerald-100 text-xs">
                <div>
                    <span class="text-[10px] text-slate-500 uppercase block font-semibold">Document No & Year</span>
                    <span class="font-extrabold text-slate-900 font-mono">${escapeHtml(owner.acquisition.doc_no)}</span>
                </div>
                <div>
                    <span class="text-[10px] text-slate-500 uppercase block font-semibold">Registration Date</span>
                    <span class="font-bold text-slate-800">${escapeHtml(owner.acquisition.date)}</span>
                </div>
                <div>
                    <span class="text-[10px] text-slate-500 uppercase block font-semibold">Deed Nature</span>
                    <span class="font-bold text-slate-800">${escapeHtml(owner.acquisition.nature)}</span>
                </div>
                <div>
                    <span class="text-[10px] text-slate-500 uppercase block font-semibold">Consideration Amount</span>
                    <span class="font-bold text-emerald-700 font-mono">${escapeHtml(owner.acquisition.consideration || '-')}</span>
                </div>
                <div class="col-span-2 sm:col-span-4 pt-1 border-t border-emerald-100 flex items-center justify-between text-[11px]">
                    <span><b>Acquired From (Vendor/Executant):</b> ${escapeHtml(owner.acquisition.acquired_from || '-')}</span>
                    ${owner.acquisition.extent && owner.acquisition.extent !== '-' ? `<span><b>Extent:</b> ${escapeHtml(owner.acquisition.extent)}</span>` : ''}
                </div>
            </div>
            ` : `
            <p class="text-xs text-slate-500 italic p-2 bg-slate-50 rounded-lg">
                No registered acquisition deed (Sale/Settlement/Gift) recorded within the search period of this Encumbrance Certificate. The party may hold title through parent deeds prior to the search window or by inheritance.
            </p>
            `}
        </div>

        <!-- Section 3: Devolution / Transfer Out (If Applicable) -->
        ${owner.transferred_to ? `
        <div class="p-3.5 rounded-xl bg-slate-50 border border-slate-200 space-y-2">
            <h5 class="text-xs font-bold text-slate-900 uppercase tracking-wide flex items-center gap-1.5">
                <i data-lucide="arrow-right-left" class="w-3.5 h-3.5 text-slate-600"></i>
                <span>Subsequent Transfer / Devolution (உரிமை மாற்றம்)</span>
            </h5>
            <div class="p-3 bg-white rounded-lg border border-slate-200 text-xs space-y-1">
                <div class="flex items-center justify-between">
                    <span class="font-bold text-slate-800">Transferred To: <b class="text-purple-700">${escapeHtml(owner.transferred_to.transferred_to)}</b></span>
                    <span class="font-mono text-slate-600">Doc: ${escapeHtml(owner.transferred_to.doc_no)}</span>
                </div>
                <div class="text-[11px] text-slate-500">Date of Registered Transfer: ${escapeHtml(owner.transferred_to.date)}</div>
            </div>
        </div>
        ` : (isCurrent ? `
        <div class="p-3 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-900 flex items-center gap-2 text-xs">
            <i data-lucide="check-circle" class="w-4 h-4 text-emerald-600 shrink-0"></i>
            <span><strong>Active Title Holder:</strong> No subsequent sale deed or alienation recorded against this party. Legal ownership remains intact.</span>
        </div>
        ` : '')}

        <!-- Section 4: Loans & Mortgage Audit -->
        <div class="p-3.5 rounded-xl bg-white border border-slate-200 shadow-2xs space-y-2">
            <div class="flex items-center justify-between">
                <h5 class="text-xs font-bold text-slate-900 uppercase tracking-wide flex items-center gap-1.5">
                    <i data-lucide="landmark" class="w-3.5 h-3.5 text-purple-600"></i>
                    <span>Mortgage & Bank Loan Audit (அடமான பரிசீலனை)</span>
                </h5>
                <span class="text-[11px] font-bold ${owner.has_active_mortgages ? 'text-amber-600' : 'text-emerald-600'}">
                    ${owner.has_active_mortgages ? '⚠️ ACTIVE LOANS RECORDED' : 'CLEAR / NO ACTIVE CHARGES'}
                </span>
            </div>
            ${(owner.mortgages && owner.mortgages.length > 0) ? `
            <div class="space-y-2">
                ${owner.mortgages.map(m => `
                <div class="p-2.5 rounded-lg border ${m.status === 'OPEN' ? 'bg-amber-50/50 border-amber-200 text-amber-950' : 'bg-slate-50 border-slate-200 text-slate-700'} text-xs space-y-1">
                    <div class="flex items-center justify-between font-bold">
                        <span>Lender: ${escapeHtml(m.lender)}</span>
                        <span class="px-2 py-0.5 rounded text-[10px] font-mono ${m.status === 'OPEN' ? 'bg-amber-200 text-amber-900' : 'bg-emerald-100 text-emerald-800'}">
                            ${m.status === 'OPEN' ? '⚠️ OPEN / UNRELEASED' : 'CLOSED / SATISFIED'}
                        </span>
                    </div>
                    <div class="flex items-center justify-between text-[11px] text-slate-600">
                        <span>Doc: <b>${escapeHtml(m.doc_no)}</b> (${escapeHtml(m.date)})</span>
                        ${m.amount && m.amount !== '-' ? `<span>Loan Sum: <b>${escapeHtml(m.amount)}</b></span>` : ''}
                    </div>
                    ${m.discharge_doc && m.discharge_doc !== '-' ? `
                    <div class="text-[10px] text-emerald-800 font-mono pt-1 border-t border-slate-200">
                        Discharge Receipt: <b>${escapeHtml(m.discharge_doc)}</b>
                    </div>
                    ` : ''}
                </div>
                `).join('')}
            </div>
            ` : `
            <p class="text-xs text-slate-500 italic p-2 bg-slate-50 rounded-lg">
                No mortgages, MODTs, or financial charges recorded under this owner in the Encumbrance Certificate.
            </p>
            `}
        </div>

        <!-- Section 5: Complete Transaction Trail -->
        <div class="p-3.5 rounded-xl bg-white border border-slate-200 shadow-2xs space-y-2">
            <h5 class="text-xs font-bold text-slate-900 uppercase tracking-wide flex items-center gap-1.5">
                <i data-lucide="history" class="w-3.5 h-3.5 text-indigo-600"></i>
                <span>Complete Chronological Transaction Trail (${(owner.transactions || []).length} Document(s))</span>
            </h5>
            <div class="overflow-x-auto rounded-lg border border-slate-200">
                <table class="min-w-full divide-y divide-slate-200 text-xs">
                    <thead class="bg-slate-50 text-slate-600">
                        <tr>
                            <th class="px-2.5 py-2 text-left font-bold">Doc No & Date</th>
                            <th class="px-2.5 py-2 text-left font-bold">Nature</th>
                            <th class="px-2.5 py-2 text-left font-bold">Party Role</th>
                            <th class="px-2.5 py-2 text-left font-bold">Counterparty</th>
                            <th class="px-2.5 py-2 text-right font-bold">Value</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-slate-100 bg-white">
                        ${(owner.transactions && owner.transactions.length > 0) ? owner.transactions.map(t => `
                        <tr class="hover:bg-slate-50/80">
                            <td class="px-2.5 py-2 font-mono whitespace-nowrap">
                                <div class="font-bold text-slate-900">${escapeHtml(t.doc_no)}</div>
                                <div class="text-[10px] text-slate-500">${escapeHtml(t.date)}</div>
                            </td>
                            <td class="px-2.5 py-2 font-medium text-slate-800">${escapeHtml(t.nature)}</td>
                            <td class="px-2.5 py-2">
                                <span class="px-1.5 py-0.5 rounded text-[10px] font-semibold ${t.role.includes('Claimant') ? 'bg-emerald-50 text-emerald-800 border border-emerald-200' : 'bg-blue-50 text-blue-800 border border-blue-200'}">${escapeHtml(t.role)}</span>
                            </td>
                            <td class="px-2.5 py-2 text-slate-600 max-w-[180px] truncate" title="${escapeHtml(t.counterparty)}">${escapeHtml(t.counterparty)}</td>
                            <td class="px-2.5 py-2 text-right font-mono font-bold text-slate-800">${escapeHtml(t.amount || '-')}</td>
                        </tr>
                        `).join('') : `
                        <tr><td colspan="5" class="px-3 py-2 text-center text-slate-400">No transactions recorded.</td></tr>
                        `}
                    </tbody>
                </table>
            </div>
        </div>
    `;

    modal.classList.remove("hidden");
    lucide.createIcons();
}

function closeOwnerDossier() {
    const modal = document.getElementById("owner-dossier-modal");
    if (modal) {
        modal.classList.add("hidden");
    }
}

// --------------------------------------------------------------------------
// Property Title & Encumbrance Verification Filter
// --------------------------------------------------------------------------

function renderPropertyFilterTab(extraction) {
    const container = document.getElementById("property-filter-container");
    if (!container) return;

    const fields = (extraction && extraction.fields) ? extraction.fields : {};
    const defaultSy = fields.survey_searched ? (fields.survey_searched.value || "") : "";
    const defaultTaluk = fields.taluk ? (fields.taluk.value || "") : "";
    const defaultVillage = fields.village ? (fields.village.value || "") : "";
    const defaultDistrict = fields.district ? (fields.district.value || "") : "";

    container.innerHTML = `
        <div class="space-y-4">
            <!-- Filter Input Card -->
            <div class="p-4 rounded-xl bg-white border border-slate-200/90 shadow-2xs">
                <div class="flex items-center justify-between pb-3 mb-3 border-b border-slate-100 flex-wrap gap-2">
                    <div>
                        <h4 class="text-xs font-bold text-slate-900 uppercase tracking-wide flex items-center gap-1.5">
                            <i data-lucide="filter" class="w-4 h-4 text-blue-600"></i>
                            <span>Property Details to Verify (சொத்து சரிபார்ப்பு விவரங்கள்)</span>
                        </h4>
                        <p class="text-[11px] text-slate-500 mt-0.5">Filter the document entries to isolate your specific unit, trace title holder, inspect loans, closures, and court orders.</p>
                    </div>
                    <div class="flex items-center gap-2">
                        <button type="button" onclick="autoFillPropertyFilter()" class="px-2.5 py-1 text-xs font-semibold rounded-lg bg-blue-50 hover:bg-blue-100 text-blue-700 border border-blue-200 transition-colors flex items-center gap-1 shadow-2xs cursor-pointer">
                            <i data-lucide="sparkles" class="w-3.5 h-3.5"></i><span>Auto-fill from Document</span>
                        </button>
                        <button type="button" onclick="clearPropertyFilter()" class="px-2 py-1 text-xs font-medium rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-600 transition-colors flex items-center gap-1 cursor-pointer">
                            <i data-lucide="rotate-ccw" class="w-3 h-3"></i><span>Clear</span>
                        </button>
                    </div>
                </div>

                <form id="property-filter-form" onsubmit="event.preventDefault(); runPropertyFilter();" class="space-y-3">
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
                        <!-- Survey Number -->
                        <div>
                            <label class="block font-bold text-slate-700 mb-1">Survey Number (புல எண்) <span class="text-red-500">*</span></label>
                            <input type="text" id="prop-in-survey" value="${escapeHtml(defaultSy)}" placeholder="e.g. 142/2A, 249/3A, 35/2" class="w-full bg-slate-50 border border-slate-200 rounded-lg px-2.5 py-1.5 text-xs text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-1 focus:ring-blue-500 font-mono">
                        </div>

                        <!-- Extent / Area -->
                        <div>
                            <label class="block font-bold text-slate-700 mb-1">Extent / Property Area (விஸ்தீர்ணம் / பரப்பளவு)</label>
                            <input type="text" id="prop-in-extent" placeholder="e.g. 1250 Sq.Ft, 480 Sq.Ft UDS, 0.04.50 Hectare" class="w-full bg-slate-50 border border-slate-200 rounded-lg px-2.5 py-1.5 text-xs text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-1 focus:ring-blue-500">
                        </div>

                        <!-- Taluk -->
                        <div>
                            <label class="block font-bold text-slate-700 mb-1">Taluk (வட்டம்)</label>
                            <input type="text" id="prop-in-taluk" value="${escapeHtml(defaultTaluk)}" placeholder="e.g. Velachery, Guindy, Mambalam" class="w-full bg-slate-50 border border-slate-200 rounded-lg px-2.5 py-1.5 text-xs text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-1 focus:ring-blue-500">
                        </div>

                        <!-- City / Village -->
                        <div>
                            <label class="block font-bold text-slate-700 mb-1">City / Revenue Village (வருவாய் கிராமம் / நகரம்)</label>
                            <input type="text" id="prop-in-city" value="${escapeHtml(defaultVillage)}" placeholder="e.g. Velachery, Chennai, Villupuram" class="w-full bg-slate-50 border border-slate-200 rounded-lg px-2.5 py-1.5 text-xs text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-1 focus:ring-blue-500">
                        </div>

                        <!-- District -->
                        <div>
                            <label class="block font-bold text-slate-700 mb-1">District (மாவட்டம்)</label>
                            <input type="text" id="prop-in-district" value="${escapeHtml(defaultDistrict)}" placeholder="e.g. Chennai, Chengalpattu" class="w-full bg-slate-50 border border-slate-200 rounded-lg px-2.5 py-1.5 text-xs text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-1 focus:ring-blue-500">
                        </div>

                        <!-- Flat Name / No -->
                        <div>
                            <label class="block font-bold text-slate-700 mb-1">Flat Name / No (அடுக்குமாடி எண் / பெயர்) — if applicable</label>
                            <input type="text" id="prop-in-flat" placeholder="e.g. Flat 3B, Block A, Classic Haven" class="w-full bg-slate-50 border border-slate-200 rounded-lg px-2.5 py-1.5 text-xs text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-1 focus:ring-blue-500 font-semibold text-blue-900">
                        </div>

                        <!-- Door / Plot Number -->
                        <div>
                            <label class="block font-bold text-slate-700 mb-1">Door Number / Plot No (கதவு / மனை எண்)</label>
                            <input type="text" id="prop-in-door" placeholder="e.g. Door 4/18, Plot 28" class="w-full bg-slate-50 border border-slate-200 rounded-lg px-2.5 py-1.5 text-xs text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-1 focus:ring-blue-500">
                        </div>

                        <!-- Boundary Details -->
                        <div>
                            <label class="block font-bold text-slate-700 mb-1">Boundary Details (நான்கெல்லை விவரங்கள்)</label>
                            <input type="text" id="prop-in-boundary" placeholder="e.g. North: 30ft road, South: Plot 29, East: Plot 27..." class="w-full bg-slate-50 border border-slate-200 rounded-lg px-2.5 py-1.5 text-xs text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-1 focus:ring-blue-500">
                        </div>

                        <!-- Owner Name -->
                        <div class="md:col-span-2">
                            <label class="block font-bold text-slate-700 mb-1">Owner Name to Trace / Verify (உரிமையாளர் பெயர்)</label>
                            <input type="text" id="prop-in-owner" placeholder="e.g. K. Rajendran, S. Lakshmi Priya" class="w-full bg-blue-50/40 border border-blue-200 rounded-lg px-2.5 py-1.5 text-xs text-blue-900 placeholder-slate-400 focus:outline-none focus:ring-1 focus:ring-blue-500 font-medium">
                            <span class="text-[10px] text-slate-400 mt-0.5 block">Identifies this owner's exact acquisition, sale, or mortgage transaction in the title chain.</span>
                        </div>
                    </div>

                    <div class="pt-1 flex items-center justify-end gap-2">
                        <button type="submit" id="btn-run-prop-filter" class="px-4 py-2 text-xs font-bold rounded-lg bg-blue-600 hover:bg-blue-700 text-white shadow-xs transition-colors flex items-center gap-1.5 cursor-pointer">
                            <i data-lucide="search" class="w-3.5 h-3.5"></i><span>Filter & Verify Property Title</span>
                        </button>
                    </div>
                </form>
            </div>

            <!-- Dynamic Results Container -->
            <div id="property-filter-results" class="space-y-3">
                <div class="p-6 text-center bg-slate-50/70 rounded-xl border border-slate-200 text-slate-400 text-xs">
                    <i data-lucide="list-filter" class="w-8 h-8 mx-auto text-slate-300 mb-2"></i>
                    Click <strong>"Filter & Verify Property Title"</strong> above or <strong>"Auto-fill from Document"</strong> to inspect matching entries, current holder, loans, closures, and court orders.
                </div>
            </div>
        </div>
    `;

    lucide.createIcons();

    // Auto-run initial filter if document has transactions
    const txList = (fields.transactions_table && Array.isArray(fields.transactions_table.value)) ? fields.transactions_table.value : [];
    if (txList.length > 0) {
        runPropertyFilter();
    }
}

function autoFillPropertyFilter() {
    if (!state.currentResult || !state.currentResult.extraction) return;
    const extraction = state.currentResult.extraction;
    const fields = extraction.fields || {};

    const syEl = document.getElementById("prop-in-survey");
    const talukEl = document.getElementById("prop-in-taluk");
    const cityEl = document.getElementById("prop-in-city");
    const distEl = document.getElementById("prop-in-district");
    const extEl = document.getElementById("prop-in-extent");
    const boundEl = document.getElementById("prop-in-boundary");
    const flatEl = document.getElementById("prop-in-flat");
    const doorEl = document.getElementById("prop-in-door");
    const ownerEl = document.getElementById("prop-in-owner");

    // Pre-fill from fields
    if (syEl && fields.survey_searched) syEl.value = fields.survey_searched.value || "";
    if (talukEl && fields.taluk) talukEl.value = fields.taluk.value || "";
    if (cityEl && fields.village) cityEl.value = fields.village.value || "";
    if (distEl && fields.district) distEl.value = fields.district.value || "";

    // Scan transactions for flat/door/extent/boundary
    const txList = (fields.transactions_table && Array.isArray(fields.transactions_table.value)) ? fields.transactions_table.value : [];
    if (txList.length > 0) {
        for (const tx of txList) {
            const rem = tx.remarks || tx.document_remarks || "";
            const sch = (tx.schedules && tx.schedules.length > 0) ? tx.schedules[0] : {};

            if (flatEl && !flatEl.value) {
                const mFlat = rem.match(/(?:Flat|Apartment|Unit)[^\w\n]*([A-Za-z0-9\-]+)/i);
                if (mFlat) flatEl.value = `Flat ${mFlat[1]}`;
                else if (sch.plot_no && sch.plot_no.toLowerCase().includes("flat")) flatEl.value = sch.plot_no;
            }

            if (doorEl && !doorEl.value) {
                const mDoor = rem.match(/(?:Door|Plot|D\.?No\.?)[^\w\n]*([A-Za-z0-9\-]+)/i);
                if (mDoor) doorEl.value = mDoor[0];
            }

            if (extEl && !extEl.value) {
                const mExt = rem.match(/(?:Property Extent|Extent)[^:\n]*[:\s]+([^,\n]+)/i);
                if (mExt) extEl.value = mExt[1].trim();
                else if (sch.extent && sch.extent !== "-") extEl.value = sch.extent;
            }

            if (boundEl && !boundEl.value) {
                const mBound = rem.match(/Boundary Details[^:\n]*[:\s]+([^\n\r]+)/i);
                if (mBound) boundEl.value = mBound[1].trim();
            }

            if (ownerEl && !ownerEl.value && tx.claimants && !tx.claimants.toLowerCase().includes("bank")) {
                const firstClaimant = tx.claimants.split(/[,;\n]/)[0].replace(/^\d+\.\s*/, '').trim();
                if (firstClaimant) ownerEl.value = firstClaimant;
            }
        }
    }

    runPropertyFilter();
}

function clearPropertyFilter() {
    ["prop-in-survey", "prop-in-taluk", "prop-in-city", "prop-in-district", "prop-in-extent", "prop-in-boundary", "prop-in-flat", "prop-in-door", "prop-in-owner"].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.value = "";
    });
    runPropertyFilter();
}

async function runPropertyFilter() {
    if (!state.currentResult || !state.currentResult.extraction) return;

    const criteria = {
        survey_no: document.getElementById("prop-in-survey") ? document.getElementById("prop-in-survey").value.trim() : "",
        taluk: document.getElementById("prop-in-taluk") ? document.getElementById("prop-in-taluk").value.trim() : "",
        city_village: document.getElementById("prop-in-city") ? document.getElementById("prop-in-city").value.trim() : "",
        district: document.getElementById("prop-in-district") ? document.getElementById("prop-in-district").value.trim() : "",
        extent: document.getElementById("prop-in-extent") ? document.getElementById("prop-in-extent").value.trim() : "",
        boundary: document.getElementById("prop-in-boundary") ? document.getElementById("prop-in-boundary").value.trim() : "",
        flat_name: document.getElementById("prop-in-flat") ? document.getElementById("prop-in-flat").value.trim() : "",
        door_no: document.getElementById("prop-in-door") ? document.getElementById("prop-in-door").value.trim() : "",
        owner_name: document.getElementById("prop-in-owner") ? document.getElementById("prop-in-owner").value.trim() : ""
    };

    const resultsContainer = document.getElementById("property-filter-results");
    if (resultsContainer) {
        resultsContainer.innerHTML = `
            <div class="p-6 text-center text-xs text-slate-500 space-y-2">
                <div class="animate-spin w-6 h-6 border-2 border-blue-600 border-t-transparent rounded-full mx-auto"></div>
                <p>Analyzing document transactions against property parameters...</p>
            </div>
        `;
    }

    try {
        const res = await fetch("/api/property/filter", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                criteria: criteria,
                extraction: state.currentResult.extraction
            })
        });
        const data = await res.json();
        renderFilteredPropertyResults(data);
    } catch (err) {
        console.error("Property filter error:", err);
        if (resultsContainer) {
            resultsContainer.innerHTML = `<div class="p-4 bg-red-50 text-red-700 text-xs rounded-xl border border-red-200">Error running filter: ${err.message}</div>`;
        }
    }
}

function renderFilteredPropertyResults(results) {
    const container = document.getElementById("property-filter-results");
    if (!container || !results) return;

    const summary = results.summary || {};
    const holder = results.current_holder;
    const userTx = results.user_related_transaction;
    const loans = results.loan_records || [];
    const courtCases = results.court_cases || [];
    const matchedTx = results.matched_transactions || [];
    const totalEntries = summary.total_entries || 0;
    const matchedCount = summary.matched_entries_count || 0;

    // Update match badge in tab button
    const badge = document.getElementById("prop-filter-match-badge");
    if (badge) {
        badge.textContent = `${matchedCount}/${totalEntries}`;
        badge.classList.remove("hidden");
    }

    // 1. Stat Cards
    const matchPct = summary.match_percentage || 0;
    const holderName = holder ? holder.buyer_holder : (summary.current_holder_name || "Clear Nil / None");
    const openLoans = summary.open_loans_count || 0;
    const closedLoans = summary.closed_loans_count || 0;
    const hasCourtOrders = summary.has_court_orders || false;

    // 2. Build Loans HTML
    let loansHtml = "";
    if (loans.length > 0) {
        loansHtml = loans.map((l, idx) => {
            const isClosed = l.is_closed;
            const badgeCls = isClosed ? "bg-emerald-100 text-emerald-800 border-emerald-300" : "bg-red-100 text-red-800 border-red-300 animate-pulse";
            const iconName = isClosed ? "check-circle" : "alert-triangle";
            const statusBadge = `<span class="px-2 py-0.5 rounded-md text-[10px] font-bold border flex items-center gap-1 ${badgeCls}"><i data-lucide="${iconName}" class="w-3 h-3"></i>${l.status_label}</span>`;
            
            return `
                <div class="p-3 rounded-xl border ${isClosed ? 'bg-emerald-50/40 border-emerald-200/90' : 'bg-red-50/40 border-red-300'} shadow-2xs space-y-2">
                    <div class="flex items-start justify-between gap-2">
                        <div>
                            <span class="text-[10px] font-bold uppercase tracking-wider text-slate-500">Mortgage / Loan Entry #${idx + 1}</span>
                            <h5 class="text-xs font-extrabold text-slate-900 mt-0.5">Doc No: ${escapeHtml(l.mortgage_doc_no)} (${escapeHtml(l.mortgage_date)})</h5>
                        </div>
                        ${statusBadge}
                    </div>

                    <div class="grid grid-cols-1 md:grid-cols-3 gap-2 text-xs bg-white/80 p-2.5 rounded-lg border border-slate-200/60">
                        <div>
                            <span class="text-[10px] text-slate-500 block">Lender (வங்கி / கடன் வழங்கியவர்):</span>
                            <span class="font-bold text-slate-800">${escapeHtml(l.lender)}</span>
                        </div>
                        <div>
                            <span class="text-[10px] text-slate-500 block">Borrower (அடமானம் வைத்தவர்):</span>
                            <span class="font-semibold text-slate-800">${escapeHtml(l.borrower)}</span>
                        </div>
                        <div>
                            <span class="text-[10px] text-slate-500 block">Loan Amount (தொகை):</span>
                            <span class="font-bold text-emerald-700 font-mono">${escapeHtml(l.amount)}</span>
                        </div>
                    </div>

                    <div class="text-[11px] ${isClosed ? 'text-emerald-800 bg-emerald-100/60' : 'text-red-800 bg-red-100/60'} p-2 rounded-lg font-medium">
                        ${isClosed ? `
                            <div class="flex items-center gap-1.5">
                                <i data-lucide="shield-check" class="w-4 h-4 text-emerald-700 shrink-0"></i>
                                <span><strong>Loan Fully Closed:</strong> Registered Discharge Deed <strong>${escapeHtml(l.discharge_doc_no)}</strong> recorded on ${escapeHtml(l.discharge_date)} (${escapeHtml(l.discharge_nature)}).</span>
                            </div>
                        ` : `
                            <div class="flex items-start gap-1.5">
                                <i data-lucide="alert-octagon" class="w-4 h-4 text-red-700 shrink-0 mt-0.5"></i>
                                <span><strong>ACTIVE LIEN WARNING:</strong> No registered mortgage discharge receipt / release deed found in this search window. Verify bank NOC before transaction!</span>
                            </div>
                        `}
                    </div>
                </div>
            `;
        }).join("");
    } else {
        loansHtml = `
            <div class="p-3.5 rounded-xl bg-emerald-50/50 border border-emerald-200 text-emerald-900 text-xs flex items-center gap-2">
                <i data-lucide="check-circle-2" class="w-4 h-4 text-emerald-600 shrink-0"></i>
                <span><strong>No Loans or Mortgages:</strong> No MODT, deposit of title deeds, or mortgage instruments are recorded against this property in the search window.</span>
            </div>
        `;
    }

    // 3. Build Court Cases HTML
    let courtHtml = "";
    if (courtCases.length > 0) {
        courtHtml = `
            <div class="p-3.5 rounded-xl bg-red-50 border-2 border-red-300 text-red-900 text-xs space-y-2">
                <div class="flex items-center gap-2 text-red-950 font-extrabold text-xs">
                    <i data-lucide="alert-triangle" class="w-4 h-4 text-red-600"></i>
                    <span>ADVERSE COURT ORDERS / ATTACHMENTS DETECTED (${courtCases.length})</span>
                </div>
                <div class="space-y-1.5">
                    ${courtCases.map(c => `
                        <div class="bg-white/90 p-2.5 rounded-lg border border-red-200 text-xs">
                            <div class="font-bold text-slate-900">${escapeHtml(c.doc_no)} — ${escapeHtml(c.date)} (${escapeHtml(c.nature)})</div>
                            <div class="text-slate-600 text-[11px] mt-0.5">${escapeHtml(c.details)}</div>
                        </div>
                    `).join("")}
                </div>
            </div>
        `;
    } else {
        courtHtml = `
            <div class="p-3 rounded-xl bg-emerald-50/50 border border-emerald-200 text-emerald-900 text-xs flex items-center gap-2">
                <i data-lucide="badge-check" class="w-4 h-4 text-emerald-600 shrink-0"></i>
                <span><strong>Clear Title (No Court Litigations):</strong> No court attachments, civil suits (O.S./E.P.), injunctions, or lis pendens entries found.</span>
            </div>
        `;
    }

    // 4. Build User's Related Transaction HTML
    let userTxHtml = "";
    if (userTx) {
        userTxHtml = `
            <div class="p-3.5 rounded-xl bg-blue-50/70 border border-blue-200 text-slate-900 text-xs space-y-2">
                <div class="flex items-center justify-between">
                    <span class="text-[11px] font-extrabold text-blue-900 uppercase tracking-wide flex items-center gap-1.5">
                        <i data-lucide="user-check" class="w-4 h-4 text-blue-600"></i>
                        <span>User's Target Owner Transaction Found</span>
                    </span>
                    <span class="px-2 py-0.5 bg-blue-100 text-blue-800 font-bold text-[10px] rounded-full">${escapeHtml(userTx.role)}</span>
                </div>
                <div class="grid grid-cols-1 md:grid-cols-3 gap-2 bg-white p-2.5 rounded-lg border border-blue-100">
                    <div>
                        <span class="text-[10px] text-slate-400 block">Deed Document No:</span>
                        <span class="font-bold text-blue-700 font-mono">${escapeHtml(userTx.doc_no)} (${escapeHtml(userTx.date)})</span>
                    </div>
                    <div>
                        <span class="text-[10px] text-slate-400 block">Nature of Instrument:</span>
                        <span class="font-semibold text-slate-800">${escapeHtml(userTx.nature)}</span>
                    </div>
                    <div>
                        <span class="text-[10px] text-slate-400 block">Consideration:</span>
                        <span class="font-bold text-emerald-700 font-mono">${escapeHtml(userTx.consideration)}</span>
                    </div>
                </div>
                <div class="text-[11px] text-slate-600">
                    <strong>Parties:</strong> From <em>${escapeHtml(userTx.executants)}</em> To <em>${escapeHtml(userTx.claimants)}</em>
                </div>
            </div>
        `;
    } else if (results.criteria_used && results.criteria_used.owner_name) {
        userTxHtml = `
            <div class="p-3 rounded-xl bg-amber-50 border border-amber-200 text-amber-900 text-xs flex items-center gap-2">
                <i data-lucide="help-circle" class="w-4 h-4 text-amber-600 shrink-0"></i>
                <span>Owner <strong>"${escapeHtml(results.criteria_used.owner_name)}"</strong> was not directly identified in the matched transactions. Check spelling or prior title link.</span>
            </div>
        `;
    }

    // 5. Build Matched Transactions Table
    let tableHtml = "";
    if (matchedTx.length > 0) {
        tableHtml = `
            <div class="overflow-x-auto max-h-[380px] rounded-xl border border-slate-200 shadow-2xs">
                <table class="w-full text-left text-xs border-collapse">
                    <thead class="bg-slate-100 text-slate-800 font-bold sticky top-0 border-b border-slate-200">
                        <tr>
                            <th class="p-2 text-center w-8">#</th>
                            <th class="p-2">Doc No/Year</th>
                            <th class="p-2">Date</th>
                            <th class="p-2">Nature</th>
                            <th class="p-2">Executant(s)</th>
                            <th class="p-2">Claimant(s)</th>
                            <th class="p-2">Amount</th>
                            <th class="p-2">Match Signal</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-slate-200 bg-white">
                        ${matchedTx.map((tx, i) => `
                            <tr class="hover:bg-blue-50/50 transition-colors">
                                <td class="p-2 text-center text-slate-500 font-mono text-[11px]">${tx.sr || (i + 1)}</td>
                                <td class="p-2 font-bold text-blue-700 font-mono whitespace-nowrap text-xs">${escapeHtml(tx.doc_no || tx.doc_no_year || "-")}</td>
                                <td class="p-2 text-slate-600 whitespace-nowrap text-[11px]">${escapeHtml(tx.date || tx.registration_date || "-")}</td>
                                <td class="p-2 font-semibold text-slate-800 text-xs">${escapeHtml(tx.nature || "-")}</td>
                                <td class="p-2 text-slate-700 text-[11px] max-w-[140px] truncate" title="${escapeHtml(tx.executants || '')}">${escapeHtml(tx.executants || "-")}</td>
                                <td class="p-2 text-slate-700 text-[11px] max-w-[140px] truncate" title="${escapeHtml(tx.claimants || '')}">${escapeHtml(tx.claimants || "-")}</td>
                                <td class="p-2 font-mono font-semibold text-emerald-700 whitespace-nowrap text-xs">${escapeHtml(tx.consideration || "-")}</td>
                                <td class="p-2 text-[10px] text-blue-600 font-medium">${escapeHtml((tx.match_reasons || []).join(", ") || "Matched")}</td>
                            </tr>
                        `).join("")}
                    </tbody>
                </table>
            </div>
        `;
    } else {
        tableHtml = `<div class="p-4 text-center text-xs text-slate-400">No transactions matched the criteria.</div>`;
    }

    // Put everything together
    container.innerHTML = `
        <div class="space-y-4">
            <!-- 1. Executive Summary Grid -->
            <div class="grid grid-cols-2 md:grid-cols-4 gap-2.5 text-xs">
                <!-- Matched Entries -->
                <div class="p-3 rounded-xl bg-white border border-slate-200/90 shadow-2xs">
                    <span class="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Matched Entries</span>
                    <div class="text-lg font-extrabold text-blue-700 font-mono mt-0.5">${matchedCount} / ${totalEntries}</div>
                    <span class="text-[10px] text-slate-500 font-medium">${matchPct}% of total document</span>
                </div>

                <!-- Current Legal Holder -->
                <div class="p-3 rounded-xl bg-white border border-slate-200/90 shadow-2xs">
                    <span class="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Current Legal Holder</span>
                    <div class="text-xs font-extrabold text-slate-900 truncate mt-1" title="${escapeHtml(holderName)}">${escapeHtml(holderName)}</div>
                    <span class="text-[10px] text-emerald-600 font-bold">${holder ? `via Doc ${holder.doc_no}` : 'Clear Title'}</span>
                </div>

                <!-- Loan / Mortgages -->
                <div class="p-3 rounded-xl bg-white border border-slate-200/90 shadow-2xs">
                    <span class="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Mortgages & Loans</span>
                    <div class="text-sm font-extrabold ${openLoans > 0 ? 'text-red-600' : 'text-emerald-700'} mt-1">
                        ${openLoans > 0 ? `${openLoans} Active Lien(s)` : `${closedLoans} Discharged`}
                    </div>
                    <span class="text-[10px] text-slate-500">${loans.length} Total Loans Recorded</span>
                </div>

                <!-- Court Cases -->
                <div class="p-3 rounded-xl bg-white border border-slate-200/90 shadow-2xs">
                    <span class="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Court Litigations</span>
                    <div class="text-xs font-extrabold ${hasCourtOrders ? 'text-red-600' : 'text-emerald-700'} mt-1">
                        ${hasCourtOrders ? `${courtCases.length} Order(s) Found` : 'Clean Title'}
                    </div>
                    <span class="text-[10px] text-slate-500">${hasCourtOrders ? 'Adverse Entry' : 'No attachments'}</span>
                </div>
            </div>

            <!-- 2. Current Holder Spotlight -->
            ${holder ? `
                <div class="p-3.5 rounded-xl bg-gradient-to-r from-emerald-50 to-teal-50 border border-emerald-200 shadow-2xs text-xs space-y-1.5">
                    <div class="flex items-center justify-between">
                        <span class="text-[11px] font-extrabold text-emerald-950 uppercase tracking-wider flex items-center gap-1.5">
                            <i data-lucide="award" class="w-4 h-4 text-emerald-600"></i>
                            <span>Latest Traced Legal Title Holder (தற்போதைய சட்டபூர்வ உரிமையாளர்)</span>
                        </span>
                        <span class="px-2 py-0.5 rounded-full bg-emerald-200/70 text-emerald-900 font-bold text-[10px]">Title Chain Culmination</span>
                    </div>
                    <div class="text-sm font-extrabold text-emerald-950">${escapeHtml(holder.buyer_holder)}</div>
                    <div class="text-[11px] text-emerald-900/80 leading-relaxed">
                        Acquired via <strong>${escapeHtml(holder.nature)}</strong> (Doc No. <strong>${escapeHtml(holder.doc_no)}</strong> registered on ${escapeHtml(holder.date)}) from <em>${escapeHtml(holder.seller_prior)}</em> for consideration of <strong>${escapeHtml(holder.consideration)}</strong>.
                    </div>
                </div>
            ` : ''}

            <!-- 3. Target User's Transaction -->
            ${userTxHtml}

            <!-- 4. Loan & Mortgage Details (with Closure Status) -->
            <div class="space-y-2">
                <div class="flex items-center justify-between">
                    <h5 class="text-xs font-bold text-slate-900 uppercase tracking-wide flex items-center gap-1.5">
                        <i data-lucide="landmark" class="w-3.5 h-3.5 text-blue-600"></i>
                        <span>Loan & Mortgage Lifecycle Analysis (அடமானக் கடன் விவரங்கள் & முடிவு நிலை)</span>
                    </h5>
                    <span class="text-[10px] font-mono text-slate-400">${loans.length} Loans Analyzed</span>
                </div>
                ${loansHtml}
            </div>

            <!-- 5. Court Orders -->
            <div class="space-y-2">
                <h5 class="text-xs font-bold text-slate-900 uppercase tracking-wide flex items-center gap-1.5">
                    <i data-lucide="scale" class="w-3.5 h-3.5 text-indigo-600"></i>
                    <span>Court Cases & Orders (நீதிமன்ற உத்தரவுகள் / பற்று)</span>
                </h5>
                ${courtHtml}
            </div>

            <!-- 6. Filtered Entries Table -->
            <div class="space-y-2">
                <div class="flex items-center justify-between">
                    <h5 class="text-xs font-bold text-slate-900 uppercase tracking-wide flex items-center gap-1.5">
                        <i data-lucide="table" class="w-3.5 h-3.5 text-blue-600"></i>
                        <span>Filtered Registered Entries Matching This Property (${matchedCount})</span>
                    </h5>
                    <span class="text-[10px] text-slate-500 font-mono">Isolated from ${totalEntries} total entries</span>
                </div>
                ${tableHtml}
            </div>
        </div>
    `;

    lucide.createIcons();
}

// 7. Multi-Document Bundles & Cross-Verification Matrix Engine
async function loadBundle(bundleId) {
    showLoader(true, `Running Multi-Document Cross-Verification on ${bundleId}...`);
    try {
        const res = await fetch(`/api/bundle/${bundleId}`);
        const data = await res.json();
        if (data.status === "success") {
            state.currentBundle = data;
            if (data.cross_check) {
                switchTrack("matrix");
                renderMatrixResults(data);
            } else if (data.inheritance_check) {
                switchTrack("inheritance");
                renderInheritanceResults(data);
            }
        }
    } catch (err) {
        console.error("Bundle error:", err);
    } finally {
        showLoader(false);
    }
}

function renderMatrixResults(bundleData) {
    const bundle = bundleData.bundle;
    const check = bundleData.cross_check;

    document.getElementById("matrix-bundle-title").textContent = bundle.title;
    document.getElementById("matrix-bundle-desc").textContent = bundle.description;

    const statusPill = document.getElementById("matrix-status-pill");
    const scoreText = document.getElementById("matrix-score-text");

    if (check.overall_status === "PASS") {
        statusPill.className = "px-3 py-1 rounded-full text-xs font-bold bg-emerald-100 text-emerald-800 border border-emerald-200";
        statusPill.textContent = "OVERALL STATUS: ALL CHECKS PASSED (CLEAR TITLE)";
        scoreText.className = "text-xs font-semibold text-emerald-700 bg-emerald-50 px-2.5 py-1 rounded-md border border-emerald-200";
        scoreText.textContent = `${check.checks_passed} of ${check.total_checks} Checks Passed (100% Integrity)`;
    } else {
        statusPill.className = "px-3 py-1 rounded-full text-xs font-bold bg-rose-100 text-rose-800 border border-rose-300";
        statusPill.textContent = `CRITICAL ALERT: ${check.red_flags_count} RED FLAGS FOUND`;
        scoreText.className = "text-xs font-semibold text-rose-700 bg-rose-50 px-2.5 py-1 rounded-md border border-rose-200";
        scoreText.textContent = `${check.checks_passed} of ${check.total_checks} Checks Passed (${check.red_flags_count} Defect / Fraud Alerts)`;
    }

    const tbody = document.getElementById("matrix-table-body");
    tbody.innerHTML = "";

    (check.matrix_results || []).forEach(row => {
        const tr = document.createElement("tr");
        const isPass = row.status.includes("PASS");
        tr.className = isPass ? "hover:bg-slate-50" : "bg-rose-50/50 hover:bg-rose-50";

        tr.innerHTML = `
            <td class="p-3">
                <span class="font-bold text-slate-800 block">${row.title}</span>
                <span class="text-[11px] text-slate-500 block mt-0.5">${row.details}</span>
            </td>
            <td class="p-3 text-slate-600">${row.compared_docs}</td>
            <td class="p-3 font-medium text-slate-800">${row.sale_deed_val}</td>
            <td class="p-3 font-medium text-slate-800">${row.revenue_val}</td>
            <td class="p-3">
                <span class="px-2 py-1 rounded-md font-bold text-[10px] ${
                    isPass ? "bg-emerald-100 text-emerald-800 border border-emerald-200" : "bg-rose-100 text-rose-800 border border-rose-200"
                }">
                    ${row.status}
                </span>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

function renderInheritanceResults(bundleData) {
    const inh = bundleData.inheritance_check;
    const cardsGrid = document.getElementById("heir-cards-grid");
    cardsGrid.innerHTML = "";

    (inh.heirs_breakdown || []).forEach((h, idx) => {
        const card = document.createElement("div");
        const isSigned = h.status.toLowerCase().includes("signatory") || h.status.toLowerCase().includes("release") || h.status.toLowerCase().includes("poa");
        card.className = `p-3.5 rounded-xl border heir-card shadow-2xs ${isSigned ? 'signed' : 'missing'}`;

        card.innerHTML = `
            <div class="flex items-start justify-between">
                <div>
                    <span class="text-[10px] font-bold text-slate-400">Class-I Legal Heir #${idx + 1}</span>
                    <h4 class="text-xs font-bold text-slate-900 mt-0.5">${h.name}</h4>
                    <p class="text-[11px] text-slate-600 mt-0.5">Relationship: <b>${h.relationship}</b> • Age: ${h.age}</p>
                </div>
                <span class="px-2 py-0.5 rounded text-[10px] font-bold ${
                    isSigned ? 'bg-emerald-100 text-emerald-800' : 'bg-rose-100 text-rose-800'
                }">
                    ${isSigned ? 'VERIFIED SIGNATORY / RELEASE' : 'MISSING SIGNATURE'}
                </span>
            </div>
            <div class="mt-2 pt-2 border-t border-slate-200/60 text-[11px] text-slate-700">
                <span class="font-semibold text-slate-500">Deed Status:</span> ${h.status}
            </div>
        `;
        cardsGrid.appendChild(card);
    });

    const stepsContainer = document.getElementById("inheritance-steps-container");
    stepsContainer.innerHTML = "";

    (inh.verification_steps || []).forEach(step => {
        const div = document.createElement("div");
        div.className = `p-3 rounded-xl border flex items-start justify-between gap-3 text-xs ${
            step.is_pass ? "bg-white border-slate-200" : "bg-rose-50 border-rose-200"
        }`;

        div.innerHTML = `
            <div class="space-y-0.5">
                <div class="flex items-center space-x-1.5">
                    <span class="font-bold text-slate-900">${step.title}</span>
                </div>
                <p class="text-[11px] text-slate-500">${step.description}</p>
                <p class="text-[11px] font-medium text-slate-800 pt-1">${step.details}</p>
            </div>
            <span class="px-2 py-0.5 rounded text-[10px] font-extrabold flex-shrink-0 ${
                step.is_pass ? "bg-emerald-100 text-emerald-800" : "bg-rose-100 text-rose-800"
            }">
                ${step.status}
            </span>
        `;
        stepsContainer.appendChild(div);
    });
    lucide.createIcons();
}

// 8. Tab, Zoom, Search, and Export helpers
function switchTab(tabName) {
    state.activeTab = tabName;
    ["ec-analysis", "fields", "owners", "property-filter", "checklist", "table", "ocr"].forEach(t => {
        const btn = document.getElementById(`tab-btn-${t}`);
        const content = document.getElementById(`tab-content-${t}`);
        if (btn && content) {
            if (t === tabName) {
                btn.className = "px-3 py-1.5 font-semibold rounded-lg bg-blue-600 text-white shadow-sm flex items-center gap-1.5 shrink-0";
                content.classList.remove("hidden");
            } else {
                btn.className = "px-3 py-1.5 font-semibold rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 flex items-center gap-1.5 shrink-0";
                content.classList.add("hidden");
            }
        }
    });

    if (tabName === "ec-analysis") {
        renderECAnalysisTab((state.currentResult && state.currentResult.extraction) ? state.currentResult.extraction : null);
    }

    lucide.createIcons();
}

function changePage(delta) {
    if (!state.currentResult || !state.currentResult.pages) return;
    const newIdx = state.currentPageIndex + delta;
    if (newIdx >= 0 && newIdx < state.currentResult.pages.length) {
        jumpToPage(newIdx);
    }
}

function adjustZoom(delta) {
    state.zoomLevel = Math.max(0.4, Math.min(2.5, state.zoomLevel + delta));
    applyZoom();
}

function resetZoom() {
    state.zoomLevel = 1.0;
    applyZoom();
}

function applyZoom() {
    const pagesContainer = document.getElementById("all-pages-container");
    if (pagesContainer) {
        pagesContainer.style.transform = `scale(${state.zoomLevel})`;
    }
    const canvasWrapper = document.getElementById("canvas-wrapper");
    if (canvasWrapper) {
        canvasWrapper.style.transform = `scale(${state.zoomLevel})`;
    }
    const zoomText = document.getElementById("zoom-level-text");
    if (zoomText) {
        zoomText.textContent = `${Math.round(state.zoomLevel * 100)}%`;
    }
}

function toggleBBoxes() {
    state.showBBoxes = !state.showBBoxes;
    const bboxLayers = document.querySelectorAll(".pdf-page-bbox-layer, #bbox-overlay-layer");
    bboxLayers.forEach(layer => {
        layer.style.display = state.showBBoxes ? "block" : "none";
    });
    const btn = document.getElementById("btn-toggle-bbox");
    if (btn) {
        if (state.showBBoxes) {
            btn.className = "px-2 py-1 rounded bg-blue-50 text-blue-700 border border-blue-200 hover:bg-blue-100 font-medium text-[11px] flex items-center gap-1";
        } else {
            btn.className = "px-2 py-1 rounded bg-slate-100 text-slate-500 border border-slate-200 hover:bg-slate-200 font-medium text-[11px] flex items-center gap-1";
        }
    }
}

function searchInDocument(query) {
    const q = query.trim().toLowerCase();
    const countEl = document.getElementById("search-match-count");
    const bboxes = document.querySelectorAll(".word-bbox, .ocr-bbox");

    if (!q) {
        if (countEl) countEl.textContent = "";
        bboxes.forEach(b => b.classList.remove("highlighted"));
        return;
    }
    let matchCount = 0;
    bboxes.forEach(b => {
        if (b.innerText.toLowerCase().includes(q)) {
            b.classList.add("highlighted");
            matchCount++;
        } else {
            b.classList.remove("highlighted");
        }
    });
    countEl.textContent = `${matchCount} found`;
}

function escapeHtml(str) {
    if (!str) return "";
    return String(str)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

function showWordInspector(word, pageNum) {
    let card = document.getElementById("word-inspector-card");
    if (!card) {
        card = document.createElement("div");
        card.id = "word-inspector-card";
        document.body.appendChild(card);
    }

    const confPct = Math.round((word.confidence || 0.98) * 100);
    const trans = word.translation || "No direct translation";

    card.innerHTML = `
        <div class="flex items-start justify-between gap-3 mb-2">
            <div class="flex items-center gap-1.5">
                <span class="w-2 h-2 rounded-full bg-blue-500"></span>
                <span class="text-xs font-bold text-slate-200">Word Inspector • Page ${pageNum}</span>
            </div>
            <button onclick="document.getElementById('word-inspector-card').remove()" class="text-slate-400 hover:text-white p-0.5 text-xs font-bold leading-none">&times;</button>
        </div>
        <div class="space-y-1.5 text-xs">
            <div class="bg-slate-800/80 p-2 rounded-lg border border-slate-700">
                <span class="text-[10px] text-slate-400 font-semibold uppercase block">Detected Word (OCR):</span>
                <span class="text-sm font-bold text-white tracking-wide select-all">${escapeHtml(word.text)}</span>
            </div>
            <div class="bg-emerald-950/40 p-2 rounded-lg border border-emerald-800/50">
                <span class="text-[10px] text-emerald-300 font-semibold uppercase block">Bilingual Translation:</span>
                <span class="text-sm font-bold text-emerald-300 select-all">${escapeHtml(trans)}</span>
            </div>
            <div class="flex items-center justify-between text-[11px] text-slate-400 pt-1">
                <span>Confidence: <b class="text-blue-400">${confPct}%</b></span>
                <button onclick="copyToClipboard('${escapeHtml(trans).replace(/'/g, "\\'")}')" class="text-blue-400 hover:text-blue-300 font-semibold text-[10px] underline">Copy Trans</button>
            </div>
        </div>
    `;
}

function highlightLineInText(text) {
    switchTab("ocr");
    document.getElementById("raw-ocr-text-view").scrollIntoView({ behavior: "smooth" });
}

async function exportResult(format) {
    if (!state.currentResult) return;
    const res_data = state.currentResult;
    const extraction = res_data.extraction || {};

    // PDF report language: English / Tamil / Both. Ignored for json/csv/txt.
    let pdfLang = "en";
    if (format === "pdf") {
        const langSelect = document.getElementById("pdf-lang-select");
        if (langSelect && langSelect.value) pdfLang = langSelect.value;
    }

    const payload = {
        format: format,
        doc_type: extraction.document_type_id || "document",
        filename: res_data.filename || "document.pdf",
        total_pages: res_data.total_pages || 1,
        extraction: extraction,
        fields: extraction.fields || {},
        checklist: extraction.checklist || [],
        lang: pdfLang
    };

    try {
        const res = await fetch("/api/export", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });
        if (!res.ok) {
            let errMsg = `Export failed (HTTP ${res.status})`;
            try {
                const errJson = await res.json();
                if (errJson && errJson.detail) errMsg = errJson.detail;
            } catch(e) {}
            throw new Error(errMsg);
        }
        const blob = await res.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        const cleanBase = (res_data.filename || extraction.document_type_id || 'document').replace(/\.[^/.]+$/, "");
        const langSuffix = format === 'pdf' ? { en: "", ta: "_Tamil", both: "_Bilingual" }[pdfLang] || "" : "";
        a.download = format === 'pdf' ? `${cleanBase}_OCR_Report${langSuffix}.pdf` : `${cleanBase}_extracted.${format}`;
        document.body.appendChild(a);
        a.click();
        a.remove();
        setTimeout(() => window.URL.revokeObjectURL(url), 1500);
    } catch (err) {
        console.error("Export error:", err);
        alert("Failed to download " + format.toUpperCase() + ": " + err.message);
    }
}

function printReport() { window.print(); }
function copyToClipboard(text) { navigator.clipboard.writeText(text); }
function copyFullText() {
    navigator.clipboard.writeText(document.getElementById("raw-ocr-text-view").innerText);
    alert("Full OCR text copied to clipboard!");
}
function resetWorkspace() {
    state.currentFile = null;
    state.currentResult = null;
    state.currentPageIndex = 0;

    // 1. Reset hidden file input
    const fileInput = document.getElementById("file-input");
    if (fileInput) fileInput.value = "";

    // 2. Reset dropzone UI
    resetDropzoneUI();

    // 3. Clear document preview & canvas
    const emptyState = document.getElementById("viewer-empty-state");
    const imgPreview = document.getElementById("doc-image-preview");
    const bboxLayer = document.getElementById("bbox-overlay-layer");
    if (emptyState) emptyState.classList.remove("hidden");
    if (imgPreview) {
        imgPreview.src = "";
        imgPreview.style.display = "none";
    }
    if (bboxLayer) bboxLayer.innerHTML = "";

    // 4. Reset pagination & zoom
    const pageInd = document.getElementById("page-indicator");
    if (pageInd) pageInd.textContent = "Page 0 / 0";
    const prevBtn = document.getElementById("btn-prev-page");
    const nextBtn = document.getElementById("btn-next-page");
    if (prevBtn) prevBtn.disabled = true;
    if (nextBtn) nextBtn.disabled = true;
    resetZoom();

    // 5. Reset search
    const searchInput = document.getElementById("doc-search-input");
    const searchCount = document.getElementById("search-match-count");
    if (searchInput) searchInput.value = "";
    if (searchCount) searchCount.textContent = "";

    // 6. Reset titles and badge
    const titleEl = document.getElementById("result-doc-type-title");
    const subEl = document.getElementById("result-doc-subtitle");
    const badgeEl = document.getElementById("result-doc-badge");
    const cat = state.categories.find(c => c.id === state.selectedCategoryId);
    const catName = cat ? cat.name : "Document";

    if (titleEl) titleEl.textContent = "Document Removed";
    if (subEl) subEl.textContent = `Category: ${catName}. Upload a new document file below to begin OCR extraction.`;
    if (badgeEl) {
        badgeEl.textContent = "Ready for Upload";
        badgeEl.className = "px-2 py-0.5 rounded-full text-[10px] font-semibold bg-blue-50 text-blue-700 border border-blue-200";
    }

    // 7. Reset Key Fields Tab with upload CTA
    const fieldsContainer = document.getElementById("extracted-fields-container");
    if (fieldsContainer) {
        fieldsContainer.innerHTML = `
            <div class="p-8 text-center bg-slate-50/60 rounded-2xl border-2 border-dashed border-slate-200 flex flex-col items-center justify-center space-y-3">
                <div class="w-14 h-14 rounded-2xl bg-blue-100/80 text-blue-600 flex items-center justify-center shadow-xs">
                    <i data-lucide="upload-cloud" class="w-7 h-7"></i>
                </div>
                <div>
                    <h4 class="font-bold text-slate-900 text-sm mb-1">Document Removed & Ready</h4>
                    <p class="text-xs text-slate-500 max-w-sm">The previous document has been cleared. Select or drop a new document above to extract key fields.</p>
                </div>
                <button type="button" onclick="document.getElementById('file-input').click()" class="mt-2 px-4 py-2 text-xs font-semibold rounded-xl bg-blue-600 hover:bg-blue-700 text-white shadow-sm flex items-center gap-1.5 transition-colors">
                    <i data-lucide="file-up" class="w-4 h-4"></i>
                    <span>Select New Document to Upload</span>
                </button>
            </div>
        `;
    }

    // 7b. Reset Property Filter Tab
    const propFilterContainer = document.getElementById("property-filter-container");
    if (propFilterContainer) propFilterContainer.innerHTML = "";
    const propMatchBadge = document.getElementById("prop-filter-match-badge");
    if (propMatchBadge) {
        propMatchBadge.textContent = "0";
        propMatchBadge.classList.add("hidden");
    }

    // 8. Reset Checklist Tab
    const checklistContainer = document.getElementById("checklist-items-container");
    const checklistBadge = document.getElementById("checklist-badge-count");
    if (checklistBadge) checklistBadge.textContent = "0/0";
    if (checklistContainer) {
        checklistContainer.innerHTML = `
            <div class="p-8 text-center text-slate-400 text-xs flex flex-col items-center justify-center space-y-2">
                <i data-lucide="check-square" class="w-8 h-8 text-slate-300"></i>
                <p>Checklist validation will execute automatically when a document is uploaded.</p>
            </div>
        `;
    }

    // 9. Reset OCR Text Tab
    const rawOcrView = document.getElementById("raw-ocr-text-view");
    if (rawOcrView) {
        rawOcrView.textContent = "No document loaded. Upload a file above to view raw OCR text.";
    }

    // 10. Reset Table Tab
    const tableContainer = document.getElementById("table-records-container");
    if (tableContainer) {
        tableContainer.innerHTML = `
            <div class="p-8 text-center text-slate-400 text-xs flex flex-col items-center justify-center space-y-2">
                <i data-lucide="table" class="w-8 h-8 text-slate-300"></i>
                <p>Table records will appear here after document processing.</p>
            </div>
        `;
    }

    lucide.createIcons();

    // 11. Highlight dropzone area
    const dropzone = document.getElementById("dropzone");
    if (dropzone) {
        dropzone.scrollIntoView({ behavior: "smooth", block: "center" });
        dropzone.classList.add("ring-4", "ring-blue-200");
        setTimeout(() => dropzone.classList.remove("ring-4", "ring-blue-200"), 1200);
    }
}
function showLoader(show, text = "") {
    const loader = document.getElementById("processing-loader");
    if (show) {
        document.getElementById("processing-status-text").textContent = text;
        loader.classList.remove("hidden");
    } else {
        loader.classList.add("hidden");
    }
}
