const purchaserVal = 'Mr.M.G.NAAGESH, Son of Late.M.N.Gopal, Hindu, aged about 42 years, residing at No.6/2, Sri Ramar Street, Devaraj N (Represented by POA: Mrs.V.M.BHUWANEESVARI - POA Doc: Doc No. 1698 of 2010, SRO Virugambakkam)';

let cleanPresName = purchaserVal;
let presSubtitle = "";
if (purchaserVal) {
    const mainPart = purchaserVal.split(/\(Represented by POA:/i)[0].trim();
    const parts = mainPart.split(',').map(p => p.trim()).filter(Boolean);
    if (parts.length > 0) {
        cleanPresName = parts[0].replace(/^(Mr\.|Mrs\.|Dr\.|Miss|Smt\.)([A-Za-z])/i, "$1 $2");
        const parentage = parts.find(p => /^(?:Son|Wife|Daughter)\s+of/i.test(p)) || "";
        const cityPinMatch = mainPart.match(/(?:Saligramam|Chennai|Madras)[^,\(\)]*(?:\d{6})?/i);
        const cityPin = cityPinMatch ? cityPinMatch[0].trim() : "";
        presSubtitle = [parentage, cityPin].filter(Boolean).join(" • ");
    }
}
console.log('cleanPresName:', cleanPresName);
console.log('presSubtitle:', presSubtitle);
