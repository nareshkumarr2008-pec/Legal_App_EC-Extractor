const fs = require('fs');

function escapeHtml(str) {
    if (!str) return '';
    return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

function parseOwnersList(rawVal) {
    if (!rawVal || rawVal === 'Not Detected' || rawVal === '-') return [];

    let cleanStr = rawVal.split(/\(Represented by POA:/i)[0].replace(/^[,\s]+|[,\s]+$/g, '').trim();
    cleanStr = cleanStr
        .replace(/\b([A-Z])\.8\./g, '$1.B.')
        .replace(/\b([A-Z])\.8\b/g, '$1.B')
        .replace(/\bBALAKRI[~-]HNAN\b/gi, 'BALAKRISHNAN');

    let owners = [];
    const numRegex = /(?:(?:\((\d+)\)|\[(\d+)\]|\b(\d+)[\)\.:-]))\s*([\s\S]+?)(?=(?:[,\s;]+(?:and\s+|&\s+)?(?:\(\d+\)|\[\d+\]|\b\d+[\)\.:-]))|$)/gi;
    const numMatches = [...cleanStr.matchAll(numRegex)];

    if (numMatches.length >= 2) {
        owners = numMatches.map((m, idx) => {
            const rawNum = m[1] || m[2] || m[3];
            let name = (m[4] || '')
                .replace(/^(?:and|&)\s+/i, '')
                .replace(/\s+(?:and|&)$/i, '')
                .replace(/^[,\s;]+|[,\s;]+$/g, '')
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
            const looksLikeNames = parts.every(p => /^[A-Z]/.test(p) && p.length > 2 && !p.includes('Village') && !p.includes('Taluk'));
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
        return owners.length + ' owners: ' + owners.map(o => o.num + ': ' + o.name).join(' | ');
    }
    const singleClean = rawVal.split(/\(Represented by POA:/i)[0].replace(/^[\(\[\d\)\.\:\-\s]+/, '').trim() || rawVal;
    return 'Single: ' + singleClean;
}

const tests = [
    '1) A.D.Balakrishnan, 2) D.B.Gopinath, 3) D.B.Balaji (Represented by POA: Mr.Jamal Asan Aliyar)',
    'Mrs. RENUKA ANURADHAN, W/o. Anuradhan',
    'Mr. R. MAHALINGAM, S/o. Sri S. Raju',
    '(1) A.D.BALAKRISHNAN (2) D.B.GOPINATH and (3) D.B.BALAJI',
    '(1) A.D.BALAKRISHNAN, (2) D.B.GOPINATH, (3) D.B.BALAJI, (4) D.B.SURESH, (5) D.B.RAMESH'
];

tests.forEach(t => console.log(formatOwnersListHtml(t)));
