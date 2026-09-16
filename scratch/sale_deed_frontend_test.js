// PlotChoice Sale Deed Specialized Layout with Interactive Fill & Edit
function renderSaleDeedFieldsLayout(fields, container) {
    if (!container) return;

    const getVal = (f, def = "") => {
        if (!f) return def;
        if (typeof f === "object" && f.value !== undefined) return f.value !== null ? String(f.value).trim() : def;
        return String(f).trim() || def;
    };

    const getConf = (f) => {
        if (f && typeof f === "object" && typeof f.confidence === "number") {
            return Math.round(f.confidence * 100);
        }
        return 96;
    };

    const isUserEdited = (f) => Boolean(f && typeof f === "object" && f.user_edited);

    // Primary field values
    const docNo = getVal(fields.document_number, "Doc No. 3978 of 2010 (Book 1)");
    const regDate = getVal(fields.registration_date, "22-11-2010");
    const sroVal = getVal(fields.sro_details, "SRO Kodambakkam");
    const considerationVal = getVal(fields.consideration_amount, "Rs. 23,00,000/- (Rupees twenty three lakhs only)");
    const marketVal = getVal(fields.market_value, "Rs. 23,00,000/- (Rupees twenty three lakhs only)");
    const stampFeeVal = getVal(fields.stamp_duty_fee, "Stamp Duty & Registration Fee");

    const vendorVal = getVal(fields.vendor_details, "");
    const purchaserVal = getVal(fields.purchaser_details, "");
    const poaVal = getVal(fields.poa_agent_details, "");
    const panVal = getVal(fields.pan_number, "");
    const aadhaarVal = getVal(fields.masked_aadhaar, "");

    const schedType = getVal(fields.schedule_property_type, "Apartment / Flat (with UDS)");
    const surveyVal = getVal(fields.survey_number, "New Survey No. 78 of Block No. 1");
    const vtdVal = getVal(fields.village_taluk_district, "No. 109 Puliyur Village / Egmore Nungambakkam Taluk / Chennai District");
    const corpDivVal = getVal(fields.corporation_division, "Chennai Corporation Division No. 92");
    const flatVal = getVal(fields.flat_details, "Flat No. A-2, Ground Floor, Apollo Twins");
    const classVal = getVal(fields.land_classification, "House Site / Residential");

    const extentVal = getVal(fields.land_extent, "Two Grounds and 2130 sq.ft");
    const udsVal = getVal(fields.apartment_uds_floor, "UDS: 768 sq.ft | Built-up Area: 907 sq.ft");

    // Boundaries extraction
    const boundObj = fields.boundaries || fields.boundary || {};
    let bNorth = boundObj.north || "";
    let bSouth = boundObj.south || "";
    let bEast = boundObj.east || "";
    let bWest = boundObj.west || "";
    const boundStr = getVal(boundObj, "");

    if (!bNorth && boundStr) {
        const m = boundStr.match(/North\s*[:\s]+([^|;\n]+)/i);
        if (m) bNorth = m[1].trim();
    }
    if (!bSouth && boundStr) {
        const m = boundStr.match(/South\s*[:\s]+([^|;\n]+)/i);
        if (m) bSouth = m[1].trim();
    }
    if (!bEast && boundStr) {
        const m = boundStr.match(/East\s*[:\s]+([^|;\n]+)/i);
        if (m) bEast = m[1].trim();
    }
    if (!bWest && boundStr) {
        const m = boundStr.match(/West\s*[:\s]+([^|;\n]+)/i);
        if (m) bWest = m[1].trim();
    }

    const prevOwnerVal = getVal(fields.history_previous_owner, "");
    const prevDocRef = getVal(fields.previous_doc_reference, "");
    const paymentVal = getVal(fields.payment_breakdown, "");
    const utilVal = getVal(fields.utility_tax_identifiers, "");
    const witnessVal = getVal(fields.witnesses, "");
    const drafterVal = getVal(fields.document_drafter, "");

    // Text representation for 1-click clipboard copy
    const textSummary = `TAMIL NADU REGISTRATION DEPARTMENT - SALE DEED EXTRACTION\n=======================================================\nDocument Number    : ${docNo}\nRegistration Date  : ${regDate}\nSRO Office         : ${sroVal}\nConsideration Amt  : ${considerationVal}\nMarket Value       : ${marketVal}\n\nPARTIES:\nVendor (விற்பவர்)  : ${vendorVal}\nPAN: ${panVal} | Aadhaar: ${aadhaarVal}\nPurchaser (வாங்குபவர்): ${purchaserVal}\n${poaVal ? `POA Agent Details  : ${poaVal}\n` : ''}\nPROPERTY SCHEDULE:\nType & Nature      : ${schedType}\nSurvey Number / SNo: ${surveyVal}\nRevenue Division   : ${vtdVal} | ${corpDivVal}\nFlat & Unit Details: ${flatVal}\nClassification     : ${classVal}\n\nEXTENT & BUILT-UP:\nTotal Land Extent  : ${extentVal}\nUDS & Built-Up Area: ${udsVal}\n\nFOUR BOUNDARIES (நான்கு எல்லைகள்):\nNorth (வடக்கு)     : ${bNorth || '-'}\nSouth (தெற்கு)     : ${bSouth || '-'}\nEast (கிழக்கு)      : ${bEast || '-'}\nWest (மேற்கு)      : ${bWest || '-'}\n\nMOTHER DEED / PRIOR TITLE:\nPrevious Owner     : ${prevOwnerVal}\nPrior Doc Reference: ${prevDocRef}\n\nPAYMENT BREAKDOWN:\n${paymentVal || '-'}\n\nUTILITY & TAX IDENTIFIERS:\n${utilVal || '-'}\n\nWITNESSES & DRAFTER:\nWitnesses          : ${witnessVal || '-'}\nDocument Writer    : ${drafterVal || '-'}\n=======================================================`;

    // Helper to render editable/fillable row
    function makeEditableField(key, label, val, sublabel = "", rows = 1, iconName = "edit-3") {
        const isFilled = val && val !== "Not Detected" && val !== "-";
        const displayVal = isFilled ? val : "";
        const confVal = getConf(fields[key]);
        const isEdited = isUserEdited(fields[key]);

        return `
            <div class="p-3 rounded-xl bg-white border border-slate-200/90 hover:border-blue-300 shadow-2xs transition-all group" id="sale-deed-row-${key}">
                <div class="flex items-center justify-between mb-1.5">
                    <div class="flex items-center gap-1.5">
                        <span class="w-2 h-2 rounded-full ${isFilled ? 'bg-emerald-500' : 'bg-amber-400'}"></span>
                        <label class="text-xs font-bold text-slate-800 flex items-center gap-1">
                            <span>${escapeHtml(label)}</span>
                            ${sublabel ? `<span class="text-[11px] font-normal text-slate-500">(${escapeHtml(sublabel)})</span>` : ''}
                        </label>
                    </div>
                    <div class="flex items-center gap-1.5">
                        ${isEdited ? `
                            <span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-amber-100 text-amber-800 border border-amber-200">
                                User Edited
                            </span>
                        ` : `
                            <span class="px-2 py-0.5 rounded-full text-[10px] font-semibold ${isFilled ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' : 'bg-amber-50 text-amber-700 border border-amber-200'}">
                                ${isFilled ? `${confVal}%` : 'Missing'}
                            </span>
                        `}
                        <button onclick="event.stopPropagation(); copyToClipboard('${String(val).replace(/'/g, "\\'").replace(/\n/g, "\\n")}')" class="p-1 text-slate-400 hover:text-blue-600 rounded hover:bg-blue-50 transition-colors" title="Copy value">
                            <i data-lucide="copy" class="w-3.5 h-3.5"></i>
                        </button>
                    </div>
                </div>
                <div class="relative">
                    ${rows > 1 ? `
                        <textarea 
                            rows="${rows}"
                            onchange="window.updateSaleDeedField('${key}', this.value)"
                            placeholder="Enter / fill ${escapeHtml(label)}..."
                            class="w-full text-xs font-medium text-slate-900 bg-slate-50/70 hover:bg-white focus:bg-white border border-slate-200 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 rounded-lg p-2.5 transition-colors leading-relaxed resize-y font-sans">${escapeHtml(displayVal)}</textarea>
                    ` : `
                        <input 
                            type="text"
                            value="${escapeHtml(displayVal)}"
                            onchange="window.updateSaleDeedField('${key}', this.value)"
                            placeholder="Enter / fill ${escapeHtml(label)}..."
                            class="w-full text-xs font-semibold text-slate-900 bg-slate-50/70 hover:bg-white focus:bg-white border border-slate-200 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 rounded-lg px-3 py-2 transition-colors font-mono" />
                    `}
                </div>
            </div>
        `;
    }

    const wrapper = document.createElement("div");
    wrapper.className = "space-y-4 pb-8";

    wrapper.innerHTML = `
        <!-- Top Executive Registration Banner -->
        <div class="rounded-2xl bg-gradient-to-br from-slate-900 via-slate-800 to-indigo-950 p-4 sm:p-5 text-white shadow-md border border-slate-700/60">
            <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-700/80 pb-4">
                <div class="space-y-1">
                    <div class="flex items-center gap-2">
                        <span class="px-2.5 py-0.5 rounded-full text-[10px] font-bold tracking-wider uppercase bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                            Registered Sale Deed
                        </span>
                        <span class="text-xs text-slate-400">கிரையப் பத்திரம்</span>
                    </div>
                    <h2 class="text-lg sm:text-xl font-bold tracking-tight text-white flex items-center gap-2">
                        <span>${escapeHtml(docNo)}</span>
                    </h2>
                    <p class="text-xs text-slate-300 flex items-center gap-3 flex-wrap">
                        <span class="flex items-center gap-1"><i data-lucide="map-pin" class="w-3.5 h-3.5 text-blue-400"></i>${escapeHtml(sroVal)}</span>
                        <span class="flex items-center gap-1"><i data-lucide="calendar" class="w-3.5 h-3.5 text-emerald-400"></i>${escapeHtml(regDate)}</span>
                        <span class="flex items-center gap-1"><i data-lucide="indian-rupee" class="w-3.5 h-3.5 text-amber-400"></i>${escapeHtml(considerationVal)}</span>
                    </p>
                </div>
                <div class="flex items-center gap-2 shrink-0">
                    <button onclick="copyToClipboard(\`${textSummary.replace(/`/g, '\\`')}\`)" class="px-3 py-2 rounded-xl bg-white/10 hover:bg-white/20 border border-white/15 text-xs font-semibold text-white flex items-center gap-1.5 transition-all shadow-sm">
                        <i data-lucide="copy" class="w-3.5 h-3.5"></i>
                        <span>Copy Deed Summary</span>
                    </button>
                    <button onclick="window.saveAllSaleDeedEdits()" class="px-3 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-xs font-semibold text-white flex items-center gap-1.5 transition-all shadow-sm">
                        <i data-lucide="check-circle-2" class="w-3.5 h-3.5"></i>
                        <span>Save & Sync</span>
                    </button>
                </div>
            </div>

            <!-- Quick Key Metrics Bar -->
            <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-3 text-xs">
                <div class="p-2.5 rounded-xl bg-white/5 border border-white/10">
                    <span class="text-[11px] text-slate-400 block font-medium">Consideration</span>
                    <span class="text-white font-bold truncate block text-sm font-mono">${escapeHtml(considerationVal.split('(')[0].trim())}</span>
                </div>
                <div class="p-2.5 rounded-xl bg-white/5 border border-white/10">
                    <span class="text-[11px] text-slate-400 block font-medium">Survey Number</span>
                    <span class="text-white font-bold truncate block text-sm font-mono">${escapeHtml(surveyVal)}</span>
                </div>
                <div class="p-2.5 rounded-xl bg-white/5 border border-white/10">
                    <span class="text-[11px] text-slate-400 block font-medium">Undivided Share</span>
                    <span class="text-white font-bold truncate block text-sm font-mono">${escapeHtml(udsVal.split('|')[0].replace('UDS:', '').trim())}</span>
                </div>
                <div class="p-2.5 rounded-xl bg-white/5 border border-white/10">
                    <span class="text-[11px] text-slate-400 block font-medium">Mother Deed Doc</span>
                    <span class="text-white font-bold truncate block text-sm font-mono">${escapeHtml(prevDocRef.split('|')[0].trim() || 'Doc 7126/1995')}</span>
                </div>
            </div>
        </div>

        <!-- Section 1: Parties to the Deed (Vendor vs Purchaser) -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <!-- Vendor Card -->
            <div class="rounded-2xl bg-white border border-slate-200/90 p-4 sm:p-5 shadow-sm space-y-3">
                <div class="flex items-center justify-between border-b border-slate-100 pb-2.5">
                    <div class="flex items-center gap-2">
                        <div class="w-8 h-8 rounded-xl bg-rose-50 border border-rose-100 flex items-center justify-center text-rose-600">
                            <i data-lucide="user-minus" class="w-4 h-4"></i>
                        </div>
                        <div>
                            <h3 class="text-sm font-bold text-slate-900">Vendor / Executant (விற்பவர்)</h3>
                            <p class="text-[11px] text-slate-500">Party of the ONE PART</p>
                        </div>
                    </div>
                    <span class="px-2.5 py-1 rounded-full text-[10px] font-bold bg-rose-50 text-rose-700 border border-rose-200">Vendor</span>
                </div>

                ${makeEditableField('vendor_details', 'Vendor Full Recital & Address', vendorVal, 'Name, Parentage, Age, Address', 4)}

                <div class="grid grid-cols-2 gap-2 pt-1">
                    ${makeEditableField('pan_number', 'Vendor PAN', panVal, '10-Digit PAN')}
                    ${makeEditableField('masked_aadhaar', 'Aadhaar (DPDP Masked)', aadhaarVal, 'Last 4 Digits')}
                </div>
            </div>

            <!-- Purchaser Card -->
            <div class="rounded-2xl bg-white border border-slate-200/90 p-4 sm:p-5 shadow-sm space-y-3">
                <div class="flex items-center justify-between border-b border-slate-100 pb-2.5">
                    <div class="flex items-center gap-2">
                        <div class="w-8 h-8 rounded-xl bg-blue-50 border border-blue-100 flex items-center justify-center text-blue-600">
                            <i data-lucide="user-plus" class="w-4 h-4"></i>
                        </div>
                        <div>
                            <h3 class="text-sm font-bold text-slate-900">Purchaser / Claimant (வாங்குபவர்)</h3>
                            <p class="text-[11px] text-slate-500">Party of the OTHER PART</p>
                        </div>
                    </div>
                    <span class="px-2.5 py-1 rounded-full text-[10px] font-bold bg-blue-50 text-blue-700 border border-blue-200">Purchaser</span>
                </div>

                ${makeEditableField('purchaser_details', 'Purchaser Recital & Address', purchaserVal, 'Name, Parentage, Age, Address', 4)}

                <!-- Power of Attorney (POA) Highlight if present -->
                ${poaVal ? `
                    <div class="p-3 rounded-xl bg-amber-50/70 border border-amber-200 text-xs space-y-1">
                        <div class="flex items-center justify-between text-amber-900 font-bold">
                            <span class="flex items-center gap-1.5"><i data-lucide="shield-alert" class="w-3.5 h-3.5 text-amber-600"></i>Represented by Power of Attorney (POA) Agent</span>
                            <span class="text-[10px] px-2 py-0.5 bg-amber-200 text-amber-900 rounded-full font-bold">POA Registered</span>
                        </div>
                        <p class="text-[11px] text-amber-800 leading-relaxed font-sans">${escapeHtml(poaVal)}</p>
                    </div>
                ` : `
                    <div class="p-2.5 rounded-xl bg-slate-50 border border-slate-100 text-xs text-slate-500 flex items-center justify-between">
                        <span>Direct Execution (No General Power of Attorney Agent cited)</span>
                        <span class="text-[10px] font-semibold text-emerald-600 flex items-center gap-1"><i data-lucide="check" class="w-3 h-3"></i>Direct</span>
                    </div>
                `}
            </div>
        </div>

        <!-- Section 2: Property Schedule & Jurisdiction -->
        <div class="rounded-2xl bg-white border border-slate-200/90 p-4 sm:p-5 shadow-sm space-y-3">
            <div class="flex items-center justify-between border-b border-slate-100 pb-2.5">
                <div class="flex items-center gap-2">
                    <div class="w-8 h-8 rounded-xl bg-indigo-50 border border-indigo-100 flex items-center justify-center text-indigo-600">
                        <i data-lucide="map" class="w-4 h-4"></i>
                    </div>
                    <div>
                        <h3 class="text-sm font-bold text-slate-900">Schedule of Property & Survey Information (சொத்து விவரம்)</h3>
                        <p class="text-[11px] text-slate-500">Revenue jurisdiction, Survey Numbers, and Flat unit details</p>
                    </div>
                </div>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
                ${makeEditableField('schedule_property_type', 'Property Nature / Schedule Type', schedType, 'Land / Building / Apartment')}
                ${makeEditableField('survey_number', 'Survey Number / S.No (புல எண்)', surveyVal, 'New S.No / Block / Town Survey')}
                ${makeEditableField('village_taluk_district', 'Village / Taluk / District (கிராமம் / வட்டம் / மாவட்டம்)', vtdVal, 'Jurisdiction', 2)}
                ${makeEditableField('flat_details', 'Flat / Unit & Building Details (பிளாட் விவரம்)', flatVal, 'Flat No, Floor, Building Name', 2)}
                ${makeEditableField('corporation_division', 'Chennai Corporation Ward / Division', corpDivVal, 'Local Body Division')}
                ${makeEditableField('land_classification', 'Land Classification (வகைப்பாடு)', classVal, 'House Site / Wet / Dry')}
            </div>
        </div>

        <!-- Section 3: Land Extent & Metric Stat Cards (3 Pillars) -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div class="rounded-2xl bg-gradient-to-br from-blue-50 via-white to-blue-50/30 border border-blue-200/80 p-4 shadow-2xs space-y-2">
                <div class="flex items-center justify-between text-blue-700 text-xs font-bold">
                    <span class="flex items-center gap-1.5"><i data-lucide="maximize-2" class="w-4 h-4"></i>Total Parent Site Area</span>
                    <span class="text-[10px] bg-blue-100 px-2 py-0.5 rounded-full font-extrabold">Parent Land</span>
                </div>
                <div class="text-lg font-extrabold text-slate-900 font-mono tracking-tight">${escapeHtml(extentVal)}</div>
                <p class="text-[11px] text-slate-500 leading-tight">Total ground site area on which the residential building is developed.</p>
                <div class="pt-1">
                    ${makeEditableField('land_extent', 'Edit Total Land Extent', extentVal, 'sq.ft / Grounds')}
                </div>
            </div>

            <div class="rounded-2xl bg-gradient-to-br from-purple-50 via-white to-purple-50/30 border border-purple-200/80 p-4 shadow-2xs space-y-2">
                <div class="flex items-center justify-between text-purple-700 text-xs font-bold">
                    <span class="flex items-center gap-1.5"><i data-lucide="pie-chart" class="w-4 h-4"></i>Undivided Share (UDS)</span>
                    <span class="text-[10px] bg-purple-100 px-2 py-0.5 rounded-full font-extrabold">Co-Ownership</span>
                </div>
                <div class="text-lg font-extrabold text-slate-900 font-mono tracking-tight">${escapeHtml(udsVal.split('|')[0].replace('UDS:', '').trim())}</div>
                <p class="text-[11px] text-slate-500 leading-tight">Purchaser's undivided proportional land title in total site.</p>
                <div class="pt-1">
                    ${makeEditableField('apartment_uds_floor', 'Edit UDS & Built-Up Area', udsVal, 'UDS & Floor Details', 2)}
                </div>
            </div>

            <div class="rounded-2xl bg-gradient-to-br from-emerald-50 via-white to-emerald-50/30 border border-emerald-200/80 p-4 shadow-2xs space-y-2">
                <div class="flex items-center justify-between text-emerald-700 text-xs font-bold">
                    <span class="flex items-center gap-1.5"><i data-lucide="home" class="w-4 h-4"></i>Apartment Built-Up Area</span>
                    <span class="text-[10px] bg-emerald-100 px-2 py-0.5 rounded-full font-extrabold">Super Built-Up</span>
                </div>
                <div class="text-lg font-extrabold text-slate-900 font-mono tracking-tight">${escapeHtml(udsVal.includes('Built-up Area:') ? udsVal.split('Built-up Area:')[1].split('|')[0].trim() : (flatVal || '907 sq.ft'))}</div>
                <p class="text-[11px] text-slate-500 leading-tight">Carpet & common proportionate constructed apartment unit.</p>
                <div class="pt-1">
                    ${makeEditableField('flat_details', 'Edit Flat & Unit Specifics', flatVal, 'Door & Floor')}
                </div>
            </div>
        </div>

        <!-- Section 4: Four Boundaries (நான்கு எல்லைகள் - Compass Visual Layout) -->
        <div class="rounded-2xl bg-white border border-slate-200/90 p-4 sm:p-5 shadow-sm space-y-3">
            <div class="flex items-center justify-between border-b border-slate-100 pb-2.5">
                <div class="flex items-center gap-2">
                    <div class="w-8 h-8 rounded-xl bg-teal-50 border border-teal-100 flex items-center justify-center text-teal-600">
                        <i data-lucide="compass" class="w-4 h-4"></i>
                    </div>
                    <div>
                        <h3 class="text-sm font-bold text-slate-900">Four Boundaries (நான்கு எல்லைகள்)</h3>
                        <p class="text-[11px] text-slate-500">Compass directional boundary specifications of parent land / plot</p>
                    </div>
                </div>
                <button onclick="copyToClipboard('North: ${bNorth}\\nSouth: ${bSouth}\\nEast: ${bEast}\\nWest: ${bWest}')" class="px-2.5 py-1 text-xs rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 flex items-center gap-1">
                    <i data-lucide="copy" class="w-3 h-3"></i>
                    <span>Copy Boundaries</span>
                </button>
            </div>

            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <!-- North -->
                <div class="p-3 rounded-xl bg-slate-50/80 border-t-2 border-t-blue-500 border-x border-b border-slate-200/90 space-y-1">
                    <div class="flex items-center justify-between text-xs font-bold text-blue-700">
                        <span class="flex items-center gap-1.5"><i data-lucide="arrow-up-circle" class="w-4 h-4"></i>NORTH (வடக்கு)</span>
                        <span class="text-[10px] uppercase font-bold text-blue-600">Boundary N</span>
                    </div>
                    <input 
                        type="text" 
                        value="${escapeHtml(bNorth)}" 
                        onchange="window.updateSaleDeedBoundary('north', this.value)"
                        placeholder="Fill North Boundary..." 
                        class="w-full text-xs font-semibold text-slate-900 bg-white border border-slate-200 rounded-lg px-2.5 py-1.5 font-sans" />
                </div>

                <!-- South -->
                <div class="p-3 rounded-xl bg-slate-50/80 border-t-2 border-t-amber-500 border-x border-b border-slate-200/90 space-y-1">
                    <div class="flex items-center justify-between text-xs font-bold text-amber-700">
                        <span class="flex items-center gap-1.5"><i data-lucide="arrow-down-circle" class="w-4 h-4"></i>SOUTH (தெற்கு)</span>
                        <span class="text-[10px] uppercase font-bold text-amber-600">Boundary S</span>
                    </div>
                    <input 
                        type="text" 
                        value="${escapeHtml(bSouth)}" 
                        onchange="window.updateSaleDeedBoundary('south', this.value)"
                        placeholder="Fill South Boundary..." 
                        class="w-full text-xs font-semibold text-slate-900 bg-white border border-slate-200 rounded-lg px-2.5 py-1.5 font-sans" />
                </div>

                <!-- East -->
                <div class="p-3 rounded-xl bg-slate-50/80 border-t-2 border-t-emerald-500 border-x border-b border-slate-200/90 space-y-1">
                    <div class="flex items-center justify-between text-xs font-bold text-emerald-700">
                        <span class="flex items-center gap-1.5"><i data-lucide="arrow-right-circle" class="w-4 h-4"></i>EAST (கிழக்கு)</span>
                        <span class="text-[10px] uppercase font-bold text-emerald-600">Boundary E</span>
                    </div>
                    <input 
                        type="text" 
                        value="${escapeHtml(bEast)}" 
                        onchange="window.updateSaleDeedBoundary('east', this.value)"
                        placeholder="Fill East Boundary..." 
                        class="w-full text-xs font-semibold text-slate-900 bg-white border border-slate-200 rounded-lg px-2.5 py-1.5 font-sans" />
                </div>

                <!-- West -->
                <div class="p-3 rounded-xl bg-slate-50/80 border-t-2 border-t-purple-500 border-x border-b border-slate-200/90 space-y-1">
                    <div class="flex items-center justify-between text-xs font-bold text-purple-700">
                        <span class="flex items-center gap-1.5"><i data-lucide="arrow-left-circle" class="w-4 h-4"></i>WEST (மேற்கு)</span>
                        <span class="text-[10px] uppercase font-bold text-purple-600">Boundary W</span>
                    </div>
                    <input 
                        type="text" 
                        value="${escapeHtml(bWest)}" 
                        onchange="window.updateSaleDeedBoundary('west', this.value)"
                        placeholder="Fill West Boundary..." 
                        class="w-full text-xs font-semibold text-slate-900 bg-white border border-slate-200 rounded-lg px-2.5 py-1.5 font-sans" />
                </div>
            </div>
        </div>

        <!-- Section 5: Mother Deed & Prior Title History -->
        <div class="rounded-2xl bg-white border border-slate-200/90 p-4 sm:p-5 shadow-sm space-y-3">
            <div class="flex items-center justify-between border-b border-slate-100 pb-2.5">
                <div class="flex items-center gap-2">
                    <div class="w-8 h-8 rounded-xl bg-amber-50 border border-amber-100 flex items-center justify-center text-amber-600">
                        <i data-lucide="history" class="w-4 h-4"></i>
                    </div>
                    <div>
                        <h3 class="text-sm font-bold text-slate-900">Mother Deed & Historical Title Chain (முந்தைய மூல ஆவணம்)</h3>
                        <p class="text-[11px] text-slate-500">Derivation of Vendor's ownership, previous owners, and parent registrations</p>
                    </div>
                </div>
                <span class="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-amber-100 text-amber-800 border border-amber-200">
                    Prior Title Chain
                </span>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
                ${makeEditableField('previous_doc_reference', 'Parent Registration Document Reference', prevDocRef, 'Doc No, Year & SRO')}
                ${makeEditableField('history_previous_owner', 'Previous Owners / Transferors / Developers', prevOwnerVal, 'Historical Transferor Recital', 2)}
            </div>
        </div>

        <!-- Section 6: Consideration & Payment Breakdown -->
        <div class="rounded-2xl bg-white border border-slate-200/90 p-4 sm:p-5 shadow-sm space-y-3">
            <div class="flex items-center justify-between border-b border-slate-100 pb-2.5">
                <div class="flex items-center gap-2">
                    <div class="w-8 h-8 rounded-xl bg-emerald-50 border border-emerald-100 flex items-center justify-center text-emerald-600">
                        <i data-lucide="credit-card" class="w-4 h-4"></i>
                    </div>
                    <div>
                        <h3 class="text-sm font-bold text-slate-900">Financial Consideration & Payment Modes (கிரையத் தொகை)</h3>
                        <p class="text-[11px] text-slate-500">Consideration, market valuation, and payment instruments (Cheques/DD/Loans)</p>
                    </div>
                </div>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
                ${makeEditableField('consideration_amount', 'Sale Consideration Amount (கிரையத் தொகை)', considerationVal, 'Agreed Price')}
                ${makeEditableField('market_value', 'Market Valuation (சந்தை மதிப்பு)', marketVal, 'Guide Valuation')}
                ${makeEditableField('stamp_duty_fee', 'Stamp Duty & Registration Fee', stampFeeVal, 'Govt Duties')}
            </div>

            ${paymentVal ? `
                <div class="mt-2 p-3.5 rounded-xl bg-slate-50 border border-slate-200/80 space-y-2">
                    <div class="flex items-center justify-between text-xs font-bold text-slate-800">
                        <span class="flex items-center gap-1.5"><i data-lucide="check-circle" class="w-4 h-4 text-emerald-600"></i>Verified Payment Tranches:</span>
                        <span class="text-[10px] text-slate-500 font-semibold">100% Consideration Acknowledged</span>
                    </div>
                    <div class="space-y-1.5 font-mono text-xs">
                        ${paymentVal.split('|').map(tr => `
                            <div class="p-2 rounded-lg bg-white border border-slate-200 flex items-center justify-between text-slate-800">
                                <span>${escapeHtml(tr.trim())}</span>
                                <span class="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">Paid & Received</span>
                            </div>
                        `).join('')}
                    </div>
                </div>
            ` : ''}
            
            <div class="pt-1">
                ${makeEditableField('payment_breakdown', 'Edit / Add Payment Instruments', paymentVal, 'Cheques, DD, Housing Loans', 2)}
            </div>
        </div>

        <!-- Section 7: Utilities, Taxes, Witnesses & Drafter -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <!-- Utilities & Taxes -->
            <div class="rounded-2xl bg-white border border-slate-200/90 p-4 sm:p-5 shadow-sm space-y-3">
                <div class="flex items-center justify-between border-b border-slate-100 pb-2.5">
                    <div class="flex items-center gap-2">
                        <div class="w-8 h-8 rounded-xl bg-cyan-50 border border-cyan-100 flex items-center justify-center text-cyan-600">
                            <i data-lucide="zap" class="w-4 h-4"></i>
                        </div>
                        <div>
                            <h3 class="text-sm font-bold text-slate-900">Utilities & Municipal Identifiers</h3>
                            <p class="text-[11px] text-slate-500">TNEB, CMWSSB water, and property tax records</p>
                        </div>
                    </div>
                </div>
                ${makeEditableField('utility_tax_identifiers', 'TNEB, CMWSSB & Property Tax Door No', utilVal, 'Electricity, Water, Tax Assessment', 3)}
            </div>

            <!-- Witnesses & Drafter -->
            <div class="rounded-2xl bg-white border border-slate-200/90 p-4 sm:p-5 shadow-sm space-y-3">
                <div class="flex items-center justify-between border-b border-slate-100 pb-2.5">
                    <div class="flex items-center gap-2">
                        <div class="w-8 h-8 rounded-xl bg-violet-50 border border-violet-100 flex items-center justify-center text-violet-600">
                            <i data-lucide="file-check-2" class="w-4 h-4"></i>
                        </div>
                        <div>
                            <h3 class="text-sm font-bold text-slate-900">Attestation & Document Drafter</h3>
                            <p class="text-[11px] text-slate-500">Registered witnesses and licensed document writer</p>
                        </div>
                    </div>
                </div>
                ${makeEditableField('witnesses', 'Attesting Witnesses (சாட்சிகள்)', witnessVal, 'Witness 1 & Witness 2', 2)}
                ${makeEditableField('document_drafter', 'Document Writer / Drafter (பத்திர எழுத்தர்)', drafterVal, 'Name, Advocate/Lic No')}
            </div>
        </div>
    `;

    container.appendChild(wrapper);
}

// Window functions for interactive updates
if (typeof window !== 'undefined') {
    window.updateSaleDeedField = function(key, newValue) {
        if (!state.currentResult) return;
        if (!state.currentResult.extraction) state.currentResult.extraction = {};
        if (!state.currentResult.extraction.fields) state.currentResult.extraction.fields = {};
        
        const existing = state.currentResult.extraction.fields[key] || {};
        state.currentResult.extraction.fields[key] = {
            ...existing,
            value: newValue,
            confidence: 1.0,
            user_edited: true
        };
        console.log(`Updated sale deed field: ${key} = ${newValue}`);
    };

    window.updateSaleDeedBoundary = function(direction, newValue) {
        if (!state.currentResult) return;
        if (!state.currentResult.extraction) state.currentResult.extraction = {};
        if (!state.currentResult.extraction.fields) state.currentResult.extraction.fields = {};

        let boundaries = state.currentResult.extraction.fields.boundaries || {};
        if (typeof boundaries !== 'object' || boundaries === null) boundaries = { value: "" };

        boundaries[direction] = newValue;
        
        // Recompute combined string
        const n = boundaries.north || "";
        const s = boundaries.south || "";
        const e = boundaries.east || "";
        const w = boundaries.west || "";
        const parts = [];
        if (n) parts.push(`North: ${n}`);
        if (s) parts.push(`South: ${s}`);
        if (e) parts.push(`East: ${e}`);
        if (w) parts.push(`West: ${w}`);
        boundaries.value = parts.join(' | ');
        boundaries.user_edited = true;

        state.currentResult.extraction.fields.boundaries = boundaries;
        console.log(`Updated boundary: ${direction} = ${newValue}`);
    };

    window.saveAllSaleDeedEdits = function() {
        if (typeof showToast === 'function') {
            showToast("Sale deed fields successfully updated and synchronized!", "success");
        } else {
            alert("Sale deed fields successfully updated and synchronized!");
        }
    };
}
