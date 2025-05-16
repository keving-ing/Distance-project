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
import Overlay from 'ol/Overlay';

await loadTranslations();

const csvPath = "/data/aggregati_municipio.csv"; 
let comuneData = {}; // Qui salveremo i dati del CSV

const csvTransitPath = "/data/aggregati_municipio_transit.csv"; 
let comune_transit_Data = {}; // Qui salveremo i dati del CSV

const nucleiCsvPath = "/data/aggregated_school_distances_weighted.csv";
let nucleiData = {}; // Qui salveremo i dati del CSV

const hospitalCsvPath = "/data/aggregated_hospital_by_municipality.csv";
let hospitalData = {}; // Qui salveremo i dati del CSV

const healthMGPath = "/data/aggregated_medici_by_municipality.csv";
let healthMG = {};

const healthMGPath_nucleo = "/data/aggregated_medici_distances_weighted.csv";
let healthMG_nuclei = {};

const healthOSPath_nucleo = "/data/aggregated_hospital_distances_weighted.csv";
let healthOS_nuclei = {};


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
        const selectedData = modeType === 'DR' ? comuneData : comune_transit_Data;

        // 🔵 Colora layer dei comuni
        updateMapColors(schoolType, modeType, metric, comuniLayer, selectedData);

        // 🔵 Colora layer dei nuclei anche se non visibile
        updateMapColorsNuclei(schoolType, metric, nucleiLayer, nucleiData);
        nucleiLayer.setVisible(false); // 👈 Mantieni invisibile

        console.log(`🧪 metric: ${metric}`);
        console.log("🧪 Comuni presenti in comuneData:", Object.keys(selectedData));
        setupPointerMoveInteraction(map, document.getElementById("infoBox"), selectedData, metric);
    }
 else {
        console.warn("⚠️ Uno dei parametri è mancante, impossibile aggiornare la mappa.");
    }
});


document.getElementById('extraHealthFilter').addEventListener('change', function () {

    // 🔄 Reset stili
    comuniLayer.getSource().getFeatures().forEach(feature => {
        feature.setStyle(defaultStyle);
        let color = 'rgba(255, 255, 255, 0)';
        feature.set('originalColor', color);
    });

    const metric = this.value === "distanza" ? "km" : "min";
    const healthType = document.getElementById('healthFilter').value;
    const mode = document.getElementById('healthModeFilter').value;

    // 🔁 Mappa tra tipi di dato e dataset caricati
    const healthDataMap = {
        MG: healthMG,
        OS: hospitalData
        //UR: healthUR
    };

    const healthNucleiDataMap = {
    MG: healthMG_nuclei,
    OS: healthOS_nuclei,
    //UR: urgenza_nuclei
    };

    const selectedData = healthDataMap[healthType];
    const selectedNucleiData = healthNucleiDataMap[healthType];

    if (healthType && metric && selectedData) {
        console.log(`🎨 Applicazione colori salute: tipo=${healthType}, unità=${metric}`);
        updateMapColorsHealth(metric, comuniLayer, selectedData, healthType);
        updateMapColorsNucleiSalute(metric, nucleiLayer, selectedNucleiData);
        console.log(`🧪 metric: ${metric}`);
        console.log("🧪 Comuni presenti in comuneData:", Object.keys(selectedData));
        setupPointerMoveInteraction(map, document.getElementById("infoBox"), selectedData, metric);
    } else {
        console.warn("⚠️ Parametri mancanti o dati non caricati:", { healthType, metric });
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

// Dopo aver caricato i dati CSV
loadCsvData(csvTransitPath).then(data => {
    comune_transit_Data = data;
    console.log("📊 Dati CSV caricati:", comune_transit_Data);

    // Avvia le interazioni dopo aver caricato i dati
    //setupPointerMoveInteraction(map, document.getElementById("infoBox"), comune_transit_Data);
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

setupClickInteraction(map);