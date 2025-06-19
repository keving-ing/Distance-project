import 'ol/ol.css';
import { loadCsvData, updateMapColors } from './comuniProcessor.js';
import { loadHealthCsvData, updateMapColorsHealth } from './comuniProcessorSalute.js';
import { loadCsvData_diff, updateMapDifferenceColors } from './differenceProcessor.js';
import { loadNucleiData, updateMapColorsNuclei} from './nucleiProcessor.js';
import { map, comuniLayer, nucleiLayer, defaultStyle } from './map.js';
import { setupClickInteraction, setupPointerMoveInteraction, setupTooltip } from './interactions_map.js';
import { setupUIEvents,setupMenuNavigation } from './uiEvents.js';
import { updateMapColorsNucleiSalute } from './nucleiProcessorSalute.js';
import { loadTranslations, setLanguage, t } from './i18n.js';
import { romaLayer } from './mapRoma.js';
import Overlay from 'ol/Overlay';


await loadTranslations();

const csvPath = "/data/aggregati_municipio.csv"; 
let comuneData = {};

const csvPath_density = "/data/aggregati_municipio_density.csv"; 
let comuneData_density = {};

const nucleiCsvPath = "/data/aggregated_school_distances_weighted.csv";
let nucleiData = {}; 

const hospitalCsvPath = "/data/aggregated_hospital_by_municipality.csv";
let hospitalData = {};

const healthMGPath = "/data/aggregated_medici_by_municipality.csv";
let healthMG = {};

const healthEMPath = "/data/aggregated_ps_by_municipality.csv";
let healthEM = {};

const healthMGPath_nucleo = "/data/aggregated_medici_distances_weighted.csv";
let healthMG_nuclei = {};

const healthOSPath_nucleo = "/data/aggregated_hospital_distances_weighted.csv";
let healthOS_nuclei = {};

const healthEMPath_nucleo = "/data/aggregated_ps_distances_weighted.csv";
let healthEM_nuclei = {};


const healthMGPath_roma = "/data/aggregated_medici_by_municipality_roma.csv";
let healthMG_roma = {};

const healthOSPath_roma = "/data/aggregated_hospital_by_municipality_roma.csv";
let healthOS_roma = {};

const transitRomaPath = "/data/aggregati_municipio_transit_ROMA.csv";
let comuneData_roma = {};







// 🎯 Seleziona gli elementi HTML del popup
const closer = document.getElementById('popup-closer');

closer.onclick = function () {
  document.getElementById('popup').style.display = 'none';
  closer.blur();
  return false;
};
  

//setupClickInteraction(map);
setupPointerMoveInteraction(map, document.getElementById("infoBox"),comuneData);
setupTooltip(map);

const layerRadios = document.querySelectorAll('input[name="layer"]');
comuniLayer.setVisible(true);  // 🔥 Mostrati di default
//nucleiLayer.setVisible(true);

// Evento per il cambio layer
layerRadios.forEach(radio => {
    radio.addEventListener('change', function () {
        if (this.value === "comuni") {
            comuniLayer.setVisible(true);  // 🔥 Mostra i comuni
            nucleiLayer.setVisible(false); // ❌ Nasconde i nuclei
        } else {
            comuniLayer.setVisible(false); // ❌ Nasconde i comuni
            nucleiLayer.setVisible(true);  // 🔥 Mostra i nuclei
        }
    });
});

setupMenuNavigation();
setupUIEvents(comuneData, nucleiData);

let selectedSchoolType = "";
let selectedMetric = "";
let selectedMode = ""; // per DR / TP
let selectedComuneData = null;         // usato da updateMapColors
let selectedHealthComuneData = null;   // usato da updateMapColorsHealth
let currentContext = "";    


document.getElementById('extraFilter').addEventListener('change', function () {

    comuniLayer.getSource().getFeatures().forEach(feature => {
                feature.setStyle(defaultStyle);
                let color = 'rgba(255, 255, 255, 0)';
                feature.set('originalColor', color);
            });

    const schoolType = document.getElementById('educationFilter').value;
    selectedSchoolType = document.getElementById('educationFilter').value;
    const modeType = document.getElementById('modeFilter').value; // 🔥 Aggiunto il tipo di trasporto
    selectedMode = document.getElementById('modeFilter').value;
    const metric = this.value === "distanza" ? "km" : "min";
    selectedMetric = this.value === "distanza" ? "km" : "min";
    if (schoolType && metric && modeType) {
        const selectedData = modeType === 'DR' ? comuneData : comuneData_density;
        selectedComuneData = selectedData;
        currentContext = "EDUCAZIONE";

        // 🔵 Colora layer dei comuni
        updateMapColors(schoolType, modeType, metric, comuniLayer, selectedData);

        // 🔵 Colora layer dei nuclei anche se non visibile
        updateMapColorsNuclei(schoolType, metric, nucleiLayer, nucleiData);
        nucleiLayer.setVisible(false); // 👈 Mantieni invisibile

        document.getElementById("filterToggleContainer").style.display = "block";

        console.log(`🧪 metric: ${metric}`);
        console.log("🧪 Comuni presenti in comuneData:", Object.keys(selectedData));
        setupPointerMoveInteraction(map, document.getElementById("infoBox"), selectedData, metric);
    }
 else {
        console.warn("⚠️ Uno dei parametri è mancante, impossibile aggiornare la mappa.");
    }
    Array.from(document.getElementById("provinceFilter").options).forEach(opt => opt.selected = false);
    document.getElementById("popFilter").value = 40000; // Ripristina il valore di default

});


document.getElementById('extraHealthFilter').addEventListener('change', function () {

    // 🔄 Reset stili
    comuniLayer.getSource().getFeatures().forEach(feature => {
        feature.setStyle(defaultStyle);
        let color = 'rgba(255, 255, 255, 0)';
        feature.set('originalColor', color);
    });

    const metric = this.value === "distanza" ? "km" : "min";
    selectedMetric = metric
    const healthType = document.getElementById('healthFilter').value;
    const mode = document.getElementById('healthModeFilter').value;

    // 🔁 Mappa tra tipi di dato e dataset caricati
    const healthDataMap = {
        MG: healthMG,
        OS: hospitalData,
        UR: healthEM
    };

    const healthNucleiDataMap = {
    MG: healthMG_nuclei,
    OS: healthOS_nuclei,
    UR: healthEM_nuclei
    };

    const selectedData = healthDataMap[healthType];
    const selectedNucleiData = healthNucleiDataMap[healthType];

    selectedHealthComuneData = selectedData;
    currentContext = "SALUTE";

    if (healthType && metric && selectedData) {
        console.log(`🎨 Applicazione colori salute: tipo=${healthType}, unità=${metric}`);
        updateMapColorsHealth(metric, comuniLayer, selectedData, healthType);
        updateMapColorsNucleiSalute(metric, nucleiLayer, selectedNucleiData);
        document.getElementById("filterToggleContainer").style.display = "block";
        console.log(`🧪 metric: ${metric}`);
        console.log("🧪 Comuni presenti in comuneData:", Object.keys(selectedData));
        setupPointerMoveInteraction(map, document.getElementById("infoBox"), selectedData, metric);
    } else {
        console.warn("⚠️ Parametri mancanti o dati non caricati:", { healthType, metric });
    }
    Array.from(document.getElementById("provinceFilter").options).forEach(opt => opt.selected = false);
    document.getElementById("popFilter").value = 40000; // Ripristina il valore di default
});



document.getElementById('extraFilter1').addEventListener('change', function () {

    
    const modalitaSelect = document.getElementById('modFilterContainer1');
    const educationSelect = document.getElementById('educationFilterContainer1');
    const healthSelect = document.getElementById('healthFilterContainer1');
    const extraFilterContainer = document.getElementById('extraFilterContainer1');

    romaLayer.getSource().getFeatures().forEach(feature => {
        feature.setStyle(defaultStyle);
        let color = 'rgba(255, 255, 255, 0)';
        feature.set('originalColor', color);
    });

    const tipo = document.getElementById('tipo').value;              // SA o ED
    const modalita = document.getElementById('modalita').value;      // DR, PT, DI
    const criterio = this.value === "distanza" ? "km" : "min";       // distanza o tempo
    selectedMetric = criterio;
    selectedMode = modalita;

    // EDUCAZIONE
    if (tipo === "SA") {
        const schoolType = document.getElementById('educationFilter1').value;
        selectedSchoolType = schoolType;

        const selectedData = modalita === 'DR'
            ? comuneData
            : modalita === 'PT'
            ? comuneData_roma
            : comuneData_roma_diff;  // differenze DR - PT

        selectedComuneData = selectedData;
        currentContext = "EDUCAZIONE";

        if (schoolType && criterio && modalita) {
            updateMapColors(schoolType, modalita, criterio, romaLayer, selectedData,["58"]); // Solo Roma]"]);

            setupPointerMoveInteraction(map, document.getElementById("infoBox"), selectedData, criterio);
        } else {
            console.warn("⚠️ Parametri mancanti per EDUCAZIONE TRASPORTO PUBBLICO.");
        }

    // SALUTE
    } else if (tipo === "ED") {
        const healthType = document.getElementById('healthFilter1').value; // MG o OS
        selectedMetric = criterio;

        let selectedData = null;

        if (healthType === "MG") {
            selectedData = modalita === 'DR'
                ? healthMG
                : modalita === 'PT'
                ? healthMG_roma
                : healthMG_roma_diff;
        } else if (healthType === "OS") {
            selectedData = modalita === 'DR'
                ? hospitalData
                : modalita === 'PT'
                ? healthOS_roma
                : hospitalData_roma_diff;
        }

        selectedHealthComuneData = selectedData;
        currentContext = "SALUTE";

        if (healthType && criterio && modalita && selectedData) {
            updateMapColorsHealth(criterio, romaLayer, selectedData, healthType, ["58"]); // Solo Roma]"]);
            setupPointerMoveInteraction(map, document.getElementById("infoBox"), selectedData, criterio);
        } else {
            console.warn("⚠️ Parametri mancanti o dati non caricati per SALUTE TRASPORTO PUBBLICO.");
        }
    }

    
    educationSelect.style.display = "none";
    modalitaSelect.style.display = "none";
    extraFilterContainer.style.display = "none";
    healthSelect.style.display = "none";
    modalitaSelect.style.display = "none";
    extraFilterContainer.style.display = "none";
    document.getElementById('tipo').value = "";
});



document.getElementById("applyFiltersBtn").addEventListener("click", () => {
    const selectedOptions = Array.from(document.getElementById("provinceFilter").selectedOptions);
    const selectedProvinces = selectedOptions.map(opt => {
        switch (opt.value) {
            case "VITERBO": return "56";
            case "RIETI": return "57";
            case "ROMA": return "58";
            case "LATINA": return "59";
            case "FROSINONE": return "60";
            default: return null;
        }
    }).filter(Boolean);

    const maxPop = parseInt(document.getElementById("popFilter").value) || 40000;

    if (currentContext === "EDUCAZIONE") {
        if (selectedSchoolType && selectedMetric && selectedMode && selectedComuneData) {
            updateMapColors(selectedSchoolType, selectedMode, selectedMetric, comuniLayer, selectedComuneData, selectedProvinces, maxPop);
            setupPointerMoveInteraction(map, document.getElementById("infoBox"), selectedComuneData, selectedMetric);
        } else {
            console.warn("⚠️ Variabili mancanti per EDUCAZIONE");
        }
    } else if (currentContext === "SALUTE") {
        if (selectedHealthComuneData && selectedMetric) {
            updateMapColorsHealth(selectedMetric, comuniLayer, selectedHealthComuneData, document.getElementById('healthFilter').value, selectedProvinces, maxPop);
            setupPointerMoveInteraction(map, document.getElementById("infoBox"), selectedHealthComuneData, selectedMetric);
        } else {
            console.warn("⚠️ Variabili mancanti per SALUTE");
        }
    } else {
        console.warn("⚠️ Contesto corrente sconosciuto:", currentContext);
    }
});

let nucleiDataReady = false;
// Aggiungiamo un listener per il cambio di layer (Comuni <-> Nuclei)
document.querySelectorAll('input[name="layer"]').forEach(radio => {
    radio.addEventListener('change', function () {
        if (this.value === "nuclei") {
            nucleiLayer.setVisible(true);
            comuniLayer.setVisible(false);
        } else {
            comuniLayer.setVisible(true);
            nucleiLayer.setVisible(false);
        }
    });
});


loadCsvData(csvPath).then(data => {
    comuneData = data;
    console.log("📊 Dati CSV caricati:", comuneData);

    // Avvia le interazioni dopo aver caricato i dati
    //setupPointerMoveInteraction(map, document.getElementById("infoBox"), comuneData);
});

loadCsvData(csvPath_density).then(data => {
    comuneData_density = data;
    console.log("📊 Dati CSV caricati:", comuneData_density);

    // Avvia le interazioni dopo aver caricato i dati
    //setupPointerMoveInteraction(map, document.getElementById("infoBox"), comuneData);
});


loadNucleiData(nucleiCsvPath).then(data => {
    nucleiData = data;
    nucleiDataReady = true;
    console.log("📊 Dati nuclei caricati:", nucleiData);
    
});

loadHealthCsvData(hospitalCsvPath).then(data => {
    hospitalData = data;
    console.log("📊 Dati CSV caricati:", hospitalData);

    // Avvia le interazioni dopo aver caricato i dati
    //setupPointerMoveInteraction(map, document.getElementById("infoBox"), outliersTransport);
});

loadHealthCsvData(healthMGPath).then(data => {
    healthMG = data;
    console.log("📊 Dati CSV caricati:", healthMG);

    // Avvia le interazioni dopo aver caricato i dati
    //setupPointerMoveInteraction(map, document.getElementById("infoBox"), outliersTransport)
});

loadHealthCsvData(healthMGPath_roma).then(data => {
    healthMG_roma = data;
    console.log("📊 Dati CSV caricati:", healthMG_roma);
});

loadHealthCsvData(healthOSPath_roma).then(data => { 
    healthOS_roma = data;
    console.log("📊 Dati CSV caricati:", healthOS_roma);
});

loadCsvData(transitRomaPath).then(data => {
    comuneData_roma = data;
    console.log("📊 Dati CSV caricati:", comuneData_roma);
});

loadHealthCsvData(healthEMPath).then(data => {
    healthEM = data;
    console.log("📊 Dati CSV caricati:", healthEM);

    // Avvia le interazioni dopo aver caricato i dati
    //setupPointerMoveInteraction(map, document.getElementById("infoBox"), outliersTransport);
});


loadNucleiData(healthMGPath_nucleo).then(data => {
    healthMG_nuclei = data;
    nucleiDataReady = true;
    console.log("📊 Dati nuclei medici caricati:", healthMG_nuclei);
    
});

loadNucleiData(healthOSPath_nucleo).then(data => {
    healthOS_nuclei = data;
    nucleiDataReady = true;
    console.log("📊 Dati nuclei ospedali caricati:", healthOS_nuclei);
    
});

loadNucleiData(healthEMPath_nucleo).then(data => {
    healthEM_nuclei = data;
    nucleiDataReady = true;
    console.log("📊 Dati nuclei ps caricati:", healthEM_nuclei);
    
});

setupClickInteraction(map);