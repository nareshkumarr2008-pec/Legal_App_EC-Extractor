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
    if (!rawVal || rawVal === 'Not Detected' || rawVal === '-') return '<span class="text-slate-400">Not Detected</span>';
    
    const owners = parseOwnersList(rawVal);

    if (owners.length > 1) {
        const badgeColor = themeColor === 'amber' ? 'bg-amber-500/20 text-amber-300 border-amber-500/30' : 
                           themeColor === 'emerald' ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30' : 
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
                        <div class="flex items-center gap-1.5 text-xs text-white bg-white/5 px-2 py-1 rounded-lg border border-white/5" title="${o.name}">
                            <span class="w-4 h-4 rounded-full bg-white/10 flex items-center justify-center text-[9px] font-mono font-bold shrink-0 text-slate-300">${o.num}</span>
                            <span class="font-bold truncate">${o.name}</span>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }

    const singleClean = rawVal.split(/\(Represented by POA:/i)[0].replace(/^[\(\[\d\)\.\:\-\s]+/, '').trim() || rawVal;
    return `<div class="font-extrabold text-white text-sm leading-snug break-words">${singleClean}</div>`;
}

const s3_1 = '1) A.D.Balakrishnan, 2) D.B.Gopinath, 3) D.B.Balaji (Represented by POA: Mr.Jamal Asan Aliyar)';
console.log('HTML for 2004 Deed owners:\n', formatOwnersListHtml(s3_1));

const s5 = '(1) A.D.BALAKRISHNAN, (2) D.B.GOPINATH, (3) D.B.BALAJI, (4) D.B.SURESH, (5) D.B.RAMESH';
console.log('HTML for 5 owners:\n', formatOwnersListHtml(s5));
