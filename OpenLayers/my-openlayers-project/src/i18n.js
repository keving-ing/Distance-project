let translations = {};
let currentLang = "it";

export async function loadTranslations(path = "/translations.json") {
    const res = await fetch(path);
    translations = await res.json();
    currentLang = localStorage.getItem("selectedLanguage") || "it";
    applyStaticTranslations(); // Per label, pulsanti, titoli ecc.
    applySelectTranslations(currentLang, translations); // Per le option dei select
}

export function setLanguage(lang) {
    currentLang = lang;
    localStorage.setItem("selectedLanguage", lang);
    applyStaticTranslations(); // Per label, pulsanti, titoli ecc.
    applySelectTranslations(currentLang, translations); // Per le option dei select
}

export function t(key, vars = {}) {
    let str = translations[currentLang]?.[key] || key;
    for (const [k, v] of Object.entries(vars)) {
        str = str.replace(`{${k}}`, v);
    }
    return str;
}


export function applyStaticTranslations() {
    const staticElements = {
    // 🔹 Top bar
    btnDistance: "btnDistance",
    btnDistanceSalud: "btnDistanceSalud",
    btnTransport: "btnTransport",

    // 🔧 Pannello impostazioni
    languageSelectLabel: "languageSelectLabel",
    settingsInfoTitle: "settingsInfoTitle",
    settingsInfoText1: "settingsInfoText1",
    settingsInfoText2: "settingsInfoText2",
    settingsInfoText3: "settingsInfoText3",
    settingsInfoText4: "settingsInfoText4",
    settingsUsageTitle: "settingsUsageTitle",
    settingsUsageText: "settingsUsageText",
    settingsLanguageTitle: "settingsLanguageTitle",

    settingsUsageSection1Title: "settingsUsageSection1Title",
    settingsUsageSection1Text: "settingsUsageSection1Text",
    settingsUsageSection1List: "settingsUsageSection1List",
    
    settingsUsageSection2Title: "settingsUsageSection2Title",
    settingsUsageSection2Text: "settingsUsageSection2Text",
    
    settingsUsageSection3Title: "settingsUsageSection3Title",
    settingsUsageSection3Text: "settingsUsageSection3Text",

    settingsUsageSection4Title: "settingsUsageSection4Title",
    settingsUsageSection4Text: "settingsUsageSection4Text",

    settingsUsageSection5Title: "settingsUsageSection5Title",
    settingsUsageSection5Text: "settingsUsageSection5Text",

    settingsUsageSection6Title: "settingsUsageSection6Title",
    settingsUsageSection6Text: "settingsUsageSection6Text",


    // 🔧 Pannello impostazioni
    languageSelectLabel: "languageSelectLabel",

    // 🔹 Sezione EDUCAZIONE
    labelSearchComune: "labelSearchComune",
    searchComune: "searchComune",
    labelEducationFilter: "labelEducationFilter",
    educationFilter: "educationFilter",
    labelModeFilter: "labelModeFilter",
    modeFilter: "modeFilter",
    labelExtraFilter: "labelExtraFilter",
    extraFilter: "extraFilter",
    resetFilters: "resetFilters",

    // 🔹 Sezione SALUTE
    labelSearchComuneSalute: "labelSearchComuneSalute",
    searchComuneSalute: "searchComuneSalute",
    labelHealthFilter: "labelHealthFilter",
    healthFilter: "healthFilter",
    labelHealthModeFilter: "labelHealthModeFilter",
    healthModeFilter: "healthModeFilter",
    labelExtraHealthFilter: "labelExtraHealthFilter",
    extraHealthFilter: "extraHealthFilter",
    resetHealthFilters: "resetHealthFilters",

    // 🔹 Sezione TRASPORTO PUBBLICO
    labelSearchComune1: "labelSearchComune1",
    searchComune1: "searchComune1",
    labelTipo: "labelTipo",
    tipo: "tipo",
    labelEducationFilter1: "labelEducationFilter1",
    educationFilter1: "educationFilter1",
    labelHealthFilter1: "labelHealthFilter1",
    healthFilter1: "healthFilter1",
    labelModalita: "labelModalita",
    modalita: "modalita",
    labelExtraFilter1: "labelExtraFilter1",
    extraFilter1: "extraFilter1",
    outliers: "outliers",
    resetFilters1: "resetFilters1",

    // 🔹 Layer radio buttons
    layerBoxComuni: "layerBoxComunia",
    layerBoxNuclei: "layerBoxNucleia",

    // 🔹 Legenda
    colorBarTitle: "colorBarTitle",

    info_comune: "info_comune"
};

    for (const [key, id] of Object.entries(staticElements)) {
        const el = document.getElementById(id);
        if (el && translations[currentLang][key]) {
            if (el.tagName === "INPUT" || el.tagName === "SELECT") {
                el.placeholder = translations[currentLang][key];
            } else if (el.tagName === "LABEL" && el.querySelector("input")) {
                // Se il label contiene un input, aggiorna solo il testo, non l’intero innerHTML
                const input = el.querySelector("input");
                const textNode = el.childNodes[el.childNodes.length - 1];
                if (textNode.nodeType === Node.TEXT_NODE) {
                    textNode.nodeValue = " " + translations[currentLang][key];
                } else {
                    el.appendChild(document.createTextNode(" " + translations[currentLang][key]));
                }
            } else {
                el.innerHTML = translations[currentLang][key];
            }
        }
    }
}

export function applySelectTranslations(currentLang, translations) {
    document.querySelectorAll("select").forEach(select => {
        select.querySelectorAll("option").forEach(option => {
            const key = option.value;
            if (translations[currentLang][key]) {
                option.textContent = translations[currentLang][key];
            } else if (key === "") {
                // Placeholder "-- Seleziona --"
                option.textContent = translations[currentLang]["select_placeholder"] || "-- Seleziona --";
            }
        });
    });
}


export function getCurrentLanguage() {
    return currentLang;
}