import 'ol/ol.css';
import { loadCsvData, updateMapColors } from './comuniProcessor.js';
import { loadCsvData_diff, updateMapDifferenceColors } from './differenceProcessor.js';
import { loadNucleiData, updateMapColorsNuclei} from './nucleiProcessor.js';
import { map, comuniLayer, nucleiLayer } from './map.js';
import { setupClickInteraction, setupPointerMoveInteraction, setupTooltip } from './interactions_map.js';
import { setupUIEvents,setupMenuNavigation } from './uiEvents.js';

const csvPath = "/data/aggregati_municipio.csv"; 
let comuneData = {}; // Qui salveremo i dati del CSV

const csvTransitPath = "/data/aggregati_municipio_transit.csv"; 
let comune_transit_Data = {}; // Qui salveremo i dati del CSV

const nucleiCsvPath = "/data/aggregated_school_distances_weighted.csv";
let nucleiData = {}; // Qui salveremo i dati del CSV

const diffCsvPath = "/data/differenze_municipio.csv";
let diffComuneData = {}; // Qui salveremo i dati del CSV


setupClickInteraction(map);
setupPointerMoveInteraction(map, document.getElementById("infoBox"),comuneData);
setupTooltip(map);

const layerRadios = document.querySelectorAll('input[name="layer"]');
nucleiLayer.setVisible(false); // ❌ Nuclei inizialmente nascosti
comuniLayer.setVisible(true);  // 🔥 Mostrati di default

// Evento per il cambio layer
layerRadios.forEach(radio => {
    radio.addEventListener('change', function () {
        if (this.value === "comuni") {
            comuniLayer.setVisible(true);  // 🔥 Mostra i comuni
            nucleiLayer.setVisible(false); // ❌ Nasconde i nuclei
        } else {
            comuniLayer.setVisible(true); // ❌ Nasconde i comuni
            nucleiLayer.setVisible(true);  // 🔥 Mostra i nuclei
        }
    });
});

setupMenuNavigation();
setupUIEvents(comuneData, nucleiData);

document.getElementById('extraFilter').addEventListener('change', function () {
    const schoolType = document.getElementById('educationFilter').value;
    const modeType = document.getElementById('modeFilter').value; // 🔥 Aggiunto il tipo di trasporto
    const metric = this.value === "distanza" ? "km" : "min";

    if (schoolType && metric && modeType) { // 🔥 Controllo per evitare errori
        const selectedData = modeType === 'DR' ? comuneData : comune_transit_Data;
        updateMapColors(schoolType, modeType, metric, comuniLayer, selectedData);
    } else {
        console.warn("⚠️ Uno dei parametri è mancante, impossibile aggiornare la mappa.");
    }
});

document.getElementById('extraFilter1').addEventListener('change', function () {
    const schoolType = document.getElementById('educationFilter1').value;
    const metric = this.value === "distanza" ? "km" : "min";

    if (schoolType && metric) { // 🔥 Controllo per evitare errori
        updateMapDifferenceColors(schoolType, metric, comuniLayer, diffComuneData);
    } else {
        console.warn("⚠️ Uno dei parametri è mancante, impossibile aggiornare la mappa.");
    }
});

// Aggiungiamo un listener per il cambio di layer (Comuni <-> Nuclei)
document.querySelectorAll('input[name="layer"]').forEach(radio => {
    radio.addEventListener('change', function () {
        if (this.value === "nuclei") {
            const schoolType = document.getElementById('educationFilter').value;
            const metric = document.getElementById('extraFilter').value === "distanza" ? "km" : "min";
            updateMapColorsNuclei(schoolType, metric, nucleiLayer, nucleiData);
        } else {
            const schoolType = document.getElementById('educationFilter').value;
            const metric = document.getElementById('extraFilter').value === "distanza" ? "km" : "min";
            updateMapColors(schoolType, metric, comuniLayer, comuneData);
        }
    });
});

// Dopo aver caricato i dati CSV
loadCsvData(csvPath).then(data => {
    comuneData = data;
    console.log("📊 Dati CSV caricati:", comuneData);

    // Avvia le interazioni dopo aver caricato i dati
    setupPointerMoveInteraction(map, document.getElementById("infoBox"), comuneData);
});

// Dopo aver caricato i dati CSV
loadCsvData(csvTransitPath).then(data => {
    comune_transit_Data = data;
    console.log("📊 Dati CSV caricati:", comune_transit_Data);

    // Avvia le interazioni dopo aver caricato i dati
    setupPointerMoveInteraction(map, document.getElementById("infoBox"), comune_transit_Data);
});

loadNucleiData(nucleiCsvPath).then(data => {
    nucleiData = data;
    console.log("📊 Dati nuclei caricati:", nucleiData);
});

loadCsvData_diff(diffCsvPath).then(data => {
    diffComuneData = data;
    console.log("📊 Dati CSV caricati:", diffComuneData);

    // Avvia le interazioni dopo aver caricato i dati
    setupPointerMoveInteraction(map, document.getElementById("infoBox"), diffComuneData);
});

updateMapColors(schoolType, metric, comuniLayer, comuneData);
updateMapColorsNuclei(schoolType, metric, nucleiLayer, nucleiData);