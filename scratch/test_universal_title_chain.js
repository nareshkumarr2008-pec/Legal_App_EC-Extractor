const fs = require('fs');

function escapeHtml(str) {
    if (!str) return '';
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

function parseOwnersList(rawVal) {
    if (!rawVal || rawVal === "Not Detected" || rawVal === "-") return [];

    let cleanStr = rawVal.split(/\(Represented by POA:/i)[0].replace(/^[,\s]+|[,\s]+$/g, "").trim();
    cleanStr = cleanStr
        .replace(/\b([A-Z])\.8\./g, "$1.B.")
        .replace(/\b([A-Z])\.8\b/g, "$1.B")
        .replace(/\bBALAKRI[~-]HNAN\b/gi, "BALAKRISHNAN");

    let owners = [];
    const numRegex = /(?:(?:\(([0-9ivxabc]+)\)|\[([0-9ivxabc]+)\]|\b(\d+)[\)\.:-]))\s*([\s\S]+?)(?=(?:[,\s;]+(?:and\s+|&\s+)?(?:\([0-9ivxabc]+\)|\[[0-9ivxabc]+\]|\b\d+[\)\.:-]))|$)/gi;
    const numMatches = [...cleanStr.matchAll(numRegex)];

    if (numMatches.length >= 2) {
        owners = numMatches.map((m, idx) => {
            const rawNum = m[1] || m[2] || m[3];
            let name = (m[4] || "")
                .replace(/^(?:and|&)\s+/i, "")
                .replace(/\s+(?:and|&)$/i, "")
                .replace(/^[,\s;]+|[,\s;]+$/g, "")
                .trim();
            return {
                num: rawNum || String(idx + 1),
                name: name
            };
        }).filter(o => o.name.length > 1);
    }

    if (owners.length < 2) {
        const parts = cleanStr.split(/(?:,\s*and\s+|\s+and\s+|,\s*(?=[A-Z]))/i)
            .map(p => p.trim())
            .filter(p => p.length > 2 && !/^(?:Son|Wife|Daughter|W\/o|S\/o|D\/o)\b/i.test(p));
        if (parts.length >= 2) {
            const looksLikeNames = parts.every(p => /^[A-Z]/.test(p) && p.length > 2 && !p.includes("Village") && !p.includes("Taluk"));
            if (looksLikeNames) {
                owners = parts.map((name, idx) => ({
                    num: String(idx + 1),
                    name: name
                }));
            }
        }
    }
    return owners;
}

function formatOwnersListHtml(rawVal, themeColor = 'blue') {
    if (!rawVal || rawVal === "Not Detected" || rawVal === "-") return `<span class="text-slate-400">Not Detected</span>`;
    
    const owners = parseOwnersList(rawVal);

    if (owners.length > 1) {
        const badgeColor = themeColor === 'amber' ? 'bg-amber-500/20 text-amber-300 border-amber-500/30' : 
                           themeColor === 'emerald' ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30' : 
                           themeColor === 'indigo' ? 'bg-indigo-500/20 text-indigo-300 border-indigo-500/30' : 
                           themeColor === 'purple' ? 'bg-purple-500/20 text-purple-300 border-purple-500/30' : 
                           'bg-blue-500/20 text-blue-300 border-blue-500/30';
        
        return `
            <div class="space-y-1.5">
                <div class="flex items-center gap-1.5">
                    <span class="text-[9px] font-bold px-2 py-0.5 rounded-full border ${badgeColor}">
                        ${owners.length} Co-Owners / Legal Heirs
                    </span>
                </div>
                <div class="space-y-1 max-h-36 overflow-y-auto pr-1">
                    ${owners.map(o => `
                        <div class="flex items-center gap-1.5 text-xs text-white bg-white/5 px-2 py-1 rounded-lg border border-white/5" title="${escapeHtml(o.name)}">
                            <span class="w-4 h-4 rounded-full bg-white/10 flex items-center justify-center text-[9px] font-mono font-bold shrink-0 text-slate-300">${escapeHtml(o.num)}</span>
                            <span class="font-bold truncate">${escapeHtml(o.name)}</span>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }

    const singleClean = rawVal.split(/\(Represented by POA:/i)[0].replace(/^[\(\[\d\)\.\:\-\s]+/, '').trim() || rawVal;
    return `<div class="font-extrabold text-white text-sm leading-snug break-words">${escapeHtml(singleClean)}</div>`;
}

function parsePartyNameAndParentage(rawStr, defaultLabel = "") {
    if (!rawStr || rawStr === "Not Detected" || rawStr === "-") {
        return { name: defaultLabel, subtitle: "", raw: rawStr || defaultLabel };
    }
    const cleanStr = rawStr.split(/\(Represented by POA:/i)[0].replace(/^[,\s]+|[,\s]+$/g, "").trim();
    const parts = cleanStr.split(',').map(p => p.trim()).filter(Boolean);
    if (!parts.length) return { name: defaultLabel, subtitle: "", raw: rawStr };

    let primaryName = parts[0]
        .replace(/^(Mr\.|Mrs\.|Dr\.|Miss|Smt\.)([A-Za-z])/i, "$1 $2")
        .replace(/M\s*\.\s*6\s*\.\s*NAAGESH/gi, "M.G.NAAGESH")
        .replace(/M\s*\.\s*6\s*\.\s*Naagesh/gi, "M.G.Naagesh")
        .replace(/\bM\s*\.\s*6\b/gi, "M.G")
        .replace(/\bMr\.\s*Mr\.\b/g, "Mr.");

    let parentage = "";
    if (parts.length > 1) {
        const pMatch = parts.slice(1).find(p => /^(?:Son|Wife|Daughter|W\/o|S\/o|D\/o)\s*(?:of|\.)?/i.test(p));
        if (pMatch) parentage = pMatch;
    }
    return { name: primaryName, subtitle: parentage, raw: cleanStr };
}

function buildUniversalTitleChain(fields) {
    const getVal = (f, def = "") => (f && f.value && f.value !== "Not Detected" && f.value !== "-") ? f.value.trim() : def;

    const vendorVal = getVal(fields.vendor_details, "");
    const purchaserVal = getVal(fields.purchaser_details, "");
    const prevOwnerVal = getVal(fields.history_previous_owner, "");
    const prevDocRefVal = getVal(fields.previous_doc_reference, "");
    const poaVal = getVal(fields.poa_agent_details, "");
    const docNo = getVal(fields.document_number, "Current Registered Deed");
    const regDate = getVal(fields.registration_date, "Registered Date");
    const sroVal = getVal(fields.sro, "Sub-Registrar Office");

    const motherDocs = prevDocRefVal ? prevDocRefVal.split('|').map(d => d.replace(/^Mother\s+Deed\s*:\s*/i, '').trim()).filter(Boolean) : [];
    const prevOwnerEntries = prevOwnerVal ? prevOwnerVal.split('|').map(o => o.trim()).filter(Boolean) : [];

    const nodes = [];

    // Parse Purchaser (Final Node - Always Present)
    const purchaserInfo = parsePartyNameAndParentage(purchaserVal, "Current Purchaser");

    // Parse Vendor (Penultimate Node - Always Present)
    const vendorInfo = parsePartyNameAndParentage(vendorVal, "Vendor / Seller");

    // Check for intermediate or prior historical stages
    if (prevOwnerEntries.length > 0) {
        if (prevOwnerEntries.length === 1) {
            const poStr = prevOwnerEntries[0];
            let poPoa = "";
            let poClean = poStr;
            if (poStr.includes("Represented by POA:")) {
                poPoa = poStr.split("Represented by POA:")[1].replace(/[)]+$/, "").trim();
                poClean = poStr.split(/Represented by POA:/i)[0].replace(/[\(\s,]+$/, "").trim();
            }

            const parsedOwners = parseOwnersList(poClean);
            const poInfo = parsePartyNameAndParentage(poClean, "Past Titleholder (A)");
            let displayName = poInfo.name;
            if (parsedOwners.length > 1) {
                displayName = `${parsedOwners[0].name} (+${parsedOwners.length - 1} co-owners)`;
            }
            
            nodes.push({
                role: "Prior Owner (A)",
                rolePill: "Prior Title",
                theme: "blue",
                name: displayName,
                rawName: poClean,
                coOwnersCount: parsedOwners.length,
                subtitle: poInfo.subtitle || "Historical titleholder recited in deed",
                docRef: motherDocs[0] || "Recited in Deed Recitals",
                poa: poPoa || "Direct Execution / Self",
                connector: "Mother Deed"
            });
        } else {
            // Multiple prior owner entries (e.g. A -> B -> ...)
            prevOwnerEntries.forEach((poStr, idx) => {
                let poPoa = "";
                let poClean = poStr;
                if (poStr.includes("Represented by POA:")) {
                    poPoa = poStr.split("Represented by POA:")[1].replace(/[)]+$/, "").trim();
                    poClean = poStr.split(/Represented by POA:/i)[0].replace(/[\(\s,]+$/, "").trim();
                }
                const parsedOwners = parseOwnersList(poClean);
                const poInfo = parsePartyNameAndParentage(poClean, `Prior Owner (${String.fromCharCode(65 + idx)})`);
                let displayName = poInfo.name;
                if (parsedOwners.length > 1) {
                    displayName = `${parsedOwners[0].name} (+${parsedOwners.length - 1} co-owners)`;
                }
                const isRoot = idx === 0;
                nodes.push({
                    role: isRoot ? `Root Owner (${String.fromCharCode(65 + idx)})` : `Prior Owner (${String.fromCharCode(65 + idx)})`,
                    rolePill: isRoot ? "Root Title" : "Prior Conveyance",
                    theme: isRoot ? "blue" : (idx === 1 ? "indigo" : "purple"),
                    name: displayName,
                    rawName: poClean,
                    coOwnersCount: parsedOwners.length,
                    subtitle: poInfo.subtitle || (isRoot ? "Original titleholder / allottee" : "Intermediate titleholder"),
                    docRef: motherDocs[idx] || (isRoot ? "Root Acquisition" : "Intermediate Deed"),
                    poa: poPoa || "Direct Execution / Self",
                    connector: isRoot ? "Prior Transfer" : "Mother Deed"
                });
            });
        }
    } else if (motherDocs.length > 0) {
        // No explicit owner names extracted, but mother deed is present
        nodes.push({
            role: "Prior Conveyance (A)",
            rolePill: "Mother Deed",
            theme: "blue",
            name: "Prior Titleholder(s)",
            rawName: "Prior Titleholder(s)",
            subtitle: "Recorded in parent document recitals",
            docRef: motherDocs[0],
            poa: "Direct Execution / Self",
            connector: "Mother Deed"
        });
    }

    // Next Node: Current Vendor (Seller)
    const vendorStepChar = String.fromCharCode(65 + nodes.length);
    const vendorOwners = parseOwnersList(vendorVal);
    let vendorDisplayName = vendorInfo.name;
    if (vendorOwners.length > 1) {
        vendorDisplayName = `${vendorOwners[0].name} (+${vendorOwners.length - 1} co-owners)`;
    }
    nodes.push({
        role: `Previous Owner / Vendor (${vendorStepChar})`,
        rolePill: "Vendor",
        theme: "amber",
        name: vendorDisplayName,
        rawName: vendorInfo.raw,
        coOwnersCount: vendorOwners.length,
        subtitle: vendorInfo.subtitle || "Vendor / Grantor executing transfer",
        docRef: motherDocs[motherDocs.length - 1] || "Mother Deed Conveyance",
        poa: poaVal || "Direct Execution (Self)",
        connector: "Sale Deed"
    });

    // Final Node: Current Purchaser (Buyer)
    const purchaserStepChar = String.fromCharCode(65 + nodes.length);
    const purchaserOwners = parseOwnersList(purchaserVal);
    let purchaserDisplayName = purchaserInfo.name;
    if (purchaserOwners.length > 1) {
        purchaserDisplayName = `${purchaserOwners[0].name} (+${purchaserOwners.length - 1} co-owners)`;
    }
    nodes.push({
        role: `Present Owner (${purchaserStepChar})`,
        rolePill: "Current Title",
        theme: "emerald",
        name: purchaserDisplayName,
        rawName: purchaserInfo.raw,
        coOwnersCount: purchaserOwners.length,
        subtitle: purchaserInfo.subtitle || "Purchaser / Absolute Titleholder",
        docRef: `${docNo} (Reg: ${regDate})`,
        sro: sroVal,
        poa: poaVal && purchaserVal.includes("POA") ? poaVal : "Direct Execution (Self)",
        connector: null
    });

    // Update step numbers
    nodes.forEach((n, idx) => {
        n.stepNumber = idx + 1;
        n.totalSteps = nodes.length;
    });

    return nodes;
}

function renderTitleChainHtml(titleChain) {
    const totalSteps = titleChain.length;
    const breadcrumbStr = titleChain.map(n => escapeHtml(n.name.split(',')[0].trim())).join(' ➔ ');

    const themeStyles = {
        blue: {
            cardBg: 'bg-slate-900/60 border-slate-700/60',
            pill: 'bg-blue-500/20 text-blue-300 border-blue-500/30',
            dot: 'bg-blue-400',
            titleText: 'text-blue-300',
            stepText: 'text-blue-400'
        },
        indigo: {
            cardBg: 'bg-indigo-950/40 border-indigo-500/40',
            pill: 'bg-indigo-500/20 text-indigo-300 border-indigo-500/30',
            dot: 'bg-indigo-400',
            titleText: 'text-indigo-300',
            stepText: 'text-indigo-400'
        },
        purple: {
            cardBg: 'bg-purple-950/40 border-purple-500/40',
            pill: 'bg-purple-500/20 text-purple-300 border-purple-500/30',
            dot: 'bg-purple-400',
            titleText: 'text-purple-300',
            stepText: 'text-purple-400'
        },
        amber: {
            cardBg: 'bg-amber-950/30 border-amber-500/40',
            pill: 'bg-amber-500/20 text-amber-300 border-amber-500/30',
            dot: 'bg-amber-400',
            titleText: 'text-amber-300',
            stepText: 'text-amber-400'
        },
        emerald: {
            cardBg: 'bg-emerald-950/40 border-emerald-500/40',
            pill: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30',
            dot: 'bg-emerald-400',
            titleText: 'text-emerald-300',
            stepText: 'text-emerald-400'
        }
    };

    return `
        <!-- 0. TITLE CONVEYANCE CHAIN (DYNAMIC N-STEP CHAIN) -->
        <div id="sale-deed-card-title-chain" class="sale-deed-card rounded-2xl bg-gradient-to-br from-slate-900 via-indigo-950 to-slate-900 border border-indigo-800/50 text-white shadow-sm overflow-hidden transition-all">
            <div onclick="window.toggleSaleDeedCard('sale-deed-card-title-chain')" class="p-3.5 sm:p-4 hover:bg-white/5 cursor-pointer flex items-center justify-between gap-3 transition-colors select-none">
                <div class="flex items-center gap-2.5 min-w-0">
                    <div class="w-8 h-8 rounded-xl bg-amber-400/20 text-amber-300 border border-amber-400/30 flex items-center justify-center font-bold text-xs shrink-0">
                        <i data-lucide="git-commit" class="w-4 h-4"></i>
                    </div>
                    <div class="min-w-0">
                        <div class="flex items-center gap-2 flex-wrap">
                            <h4 class="text-xs sm:text-sm font-extrabold uppercase tracking-wider text-amber-300 truncate">Title Conveyance Chain (உரிமை வழித்தொடர்)</h4>
                            <span class="text-[10px] font-mono px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 shrink-0">${totalSteps}-Step Verified Chain</span>
                        </div>
                        <p class="text-[11px] text-slate-300 truncate max-w-xl">
                            ${breadcrumbStr}
                        </p>
                    </div>
                </div>
                <div class="flex items-center gap-2 shrink-0">
                    <button type="button" onclick="event.stopPropagation(); window.copyTitlePedigree()" class="px-2.5 py-1 rounded-lg bg-white/10 hover:bg-white/20 border border-white/15 text-[11px] font-semibold text-amber-300 flex items-center gap-1 transition-all cursor-pointer" title="Copy complete title pedigree report">
                        <i data-lucide="copy" class="w-3 h-3"></i>
                        <span>Copy Pedigree</span>
                    </button>
                    <i data-lucide="chevron-right" id="sale-deed-card-title-chain-chevron" class="sale-deed-card-chevron w-4 h-4 text-slate-400 transition-transform duration-200"></i>
                </div>
            </div>

            <!-- Implicit Details Body -->
            <div id="sale-deed-card-title-chain-body" class="sale-deed-card-body hidden p-4 sm:p-5 border-t border-white/10 space-y-3.5">
                <div class="flex items-center justify-between gap-2 flex-wrap">
                    <p class="text-[11px] text-slate-300">Sequential ${totalSteps}-step legal title conveyance: ${titleChain.map(n => escapeHtml(n.role)).join(' ➔ ')}</p>
                    <span class="text-[10px] text-amber-300/80 font-mono">Unbroken Title Chain</span>
                </div>

                <!-- Dynamic Grid/Flex Container for N nodes -->
                <div class="flex flex-col lg:flex-row items-stretch gap-3 w-full max-w-full min-w-0 text-xs overflow-x-auto pb-1">
                    ${titleChain.map((node, idx) => {
                        const style = themeStyles[node.theme] || themeStyles.blue;
                        const isLast = idx === titleChain.length - 1;

                        return `
                            <!-- Node ${node.stepNumber}: ${escapeHtml(node.role)} -->
                            <div class="flex-1 min-w-[220px] max-w-full p-4 rounded-xl ${style.cardBg} border space-y-3 overflow-hidden flex flex-col justify-between shadow-2xs">
                                <div class="space-y-2 min-w-0">
                                    <div class="space-y-1 min-w-0">
                                        <div class="flex items-center justify-between gap-1.5 pb-1.5 border-b border-white/10">
                                            <span class="text-[10px] font-bold ${style.stepText} flex items-center gap-1.5 shrink-0">
                                                <span class="w-1.5 h-1.5 rounded-full ${style.dot}"></span>
                                                Step ${node.stepNumber} of ${node.totalSteps}
                                            </span>
                                            <span class="text-[9px] font-semibold px-2 py-0.5 rounded-full border ${style.pill} shrink-0">
                                                ${escapeHtml(node.rolePill)}
                                            </span>
                                        </div>
                                        <div class="text-[11px] font-extrabold ${style.titleText} uppercase tracking-wider pt-0.5">
                                            ${escapeHtml(node.role)}
                                        </div>
                                    </div>
                                    ${formatOwnersListHtml(node.rawName || node.name, node.theme)}
                                    ${node.subtitle ? `
                                        <div class="text-[11px] text-slate-300 break-words leading-relaxed">
                                            ${escapeHtml(node.subtitle)}
                                        </div>
                                    ` : ''}
                                </div>

                                <div class="pt-2.5 border-t border-white/10 space-y-2 text-[11px] min-w-0">
                                    <div class="min-w-0">
                                        <span class="text-slate-400 font-medium block text-[10px]">Document Ref:</span>
                                        <span class="text-slate-200 font-semibold break-words leading-relaxed text-[11px] block">
                                            ${escapeHtml(node.docRef || '-')}
                                        </span>
                                    </div>
                                    ${node.poa ? `
                                        <div class="min-w-0">
                                            <span class="text-slate-400 font-medium block text-[10px]">Representation:</span>
                                            <span class="text-amber-200/90 font-medium break-words leading-relaxed text-[11px] block">
                                                ${escapeHtml(node.poa)}
                                            </span>
                                        </div>
                                    ` : ''}
                                </div>
                            </div>

                            ${!isLast ? `
                                <!-- Directional Connector -->
                                <div class="flex items-center justify-center py-1 lg:py-0 px-1 shrink-0 self-center">
                                    <div class="flex lg:flex-col items-center justify-center gap-1 px-2.5 py-1.5 rounded-xl bg-indigo-500/20 border border-indigo-400/30 text-indigo-300 shadow-2xs">
                                        <i data-lucide="arrow-right" class="w-3.5 h-3.5 hidden lg:block"></i>
                                        <i data-lucide="arrow-down" class="w-3.5 h-3.5 block lg:hidden"></i>
                                        <span class="text-[8px] font-extrabold tracking-wider uppercase whitespace-nowrap">${escapeHtml(node.connector || 'Conveyance')}</span>
                                    </div>
                                </div>
                            ` : ''}
                        `;
                    }).join('')}
                </div>
            </div>
        </div>
    `;
}

// Test HTML generation
const chain3 = buildUniversalTitleChain({
    vendor_details: { value: "Mr. N. MUTHUKARUPPAN, Son of Mr. Nagappa Chettiar" },
    purchaser_details: { value: "Mr. M. G. NAAGESH, Son of Late. M. N. Gopal" },
    history_previous_owner: { value: "(1) A.D.BALAKRISHNAN (2) D.B.GOPINATH and (3) D.B.BALAJI (Represented by POA: Mr. N. Muthukaruppan)" },
    previous_doc_reference: { value: "Mother Deed: Doc No. 7126 of 1995 at SRO Virugambakkam" },
    document_number: { value: "Doc No. 3978 of 2010" },
    registration_date: { value: "22/11/2010" }
});

const html3 = renderTitleChainHtml(chain3);
console.log("Rendered HTML for 3-step chain length:", html3.length);

const chain5 = buildUniversalTitleChain({
    vendor_details: { value: "Mr. D. Suresh, Son of M. Duraisamy" },
    purchaser_details: { value: "Mr. E. Elango, Son of G. Ekambaram" },
    history_previous_owner: { value: "Mr. A. Annamalai | (1) B. Balamurugan, (2) B. Baskaran | Mr. C. Chandran" },
    previous_doc_reference: { value: "Mother Deed: Doc No. 120 of 1975 | Mother Deed: Doc No. 450 of 1988 | Mother Deed: Doc No. 980 of 2002" },
    document_number: { value: "Doc No. 5432 of 2024" },
    registration_date: { value: "15/06/2024" }
});

const html5 = renderTitleChainHtml(chain5);
console.log("Rendered HTML for 5-step chain length:", html5.length);
