import 'ol/ol.css';
import { loadCsvData, updateMapColors } from './comuniProcessor.js';
import { loadCsvData_diff, updateMapDifferenceColors } from './differenceProcessor.js';
import { loadNucleiData, updateMapColorsNuclei} from './nucleiProcessor.js';
import { map, comuniLayer, nucleiLayer, defaultStyle } from './map.js';
import { setupClickInteraction, setupPointerMoveInteraction, setupTooltip } from './interactions_map.js';
import { setupUIEvents,setupMenuNavigation } from './uiEvents.js';
import Overlay from 'ol/Overlay';

const csvPath = "/data/aggregati_municipio.csv"; 
let comuneData = {}; // Qui salveremo i dati del CSV

const csvTransitPath = "/data/aggregati_municipio_transit.csv"; 
let comune_transit_Data = {}; // Qui salveremo i dati del CSV

const nucleiCsvPath = "/data/aggregated_school_distances_weighted.csv";
let nucleiData = {}; // Qui salveremo i dati del CSV

const diffCsvPath = "/data/differenze_municipio.csv";
let diffComuneData = {}; // Qui salveremo i dati del CSV

const outCsvPath = "/data/outliers_comuni.csv";
let outliersTransport = {}; // Qui salveremo i dati del CSV

outliersTransport

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
nucleiLayer.setVisible(false); // ❌ Nuclei inizialmente nascosti
comuniLayer.setVisible(true);  // 🔥 Mostrati di default

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
    if (schoolType && metric && modeType) { // 🔥 Controllo per evitare errori
        const selectedData = modeType === 'DR' ? comuneData : comune_transit_Data;
        updateMapColors(schoolType, modeType, metric, comuniLayer, selectedData);
        setupPointerMoveInteraction(map, document.getElementById("infoBox"), selectedData, metric);
    } else {
        console.warn("⚠️ Uno dei parametri è mancante, impossibile aggiornare la mappa.");
    }
});

document.getElementById('extraFilter1').addEventListener('change', function () {

    comuniLayer.getSource().getFeatures().forEach(feature => {
                feature.setStyle(defaultStyle);
                let color = 'rgba(255, 255, 255, 0)';
                feature.set('originalColor', color);
            });


    const schoolType = document.getElementById('educationFilter1').value;
    selectedSchoolType = document.getElementById('educationFilter1').value;
    const metric = this.value === "distanza" ? "km" : "min";
    selectedMetric = this.value === "distanza" ? "km" : "min";

    if (schoolType && metric) { // 🔥 Controllo per evitare errori
        updateMapDifferenceColors(schoolType, metric, comuniLayer, diffComuneData);
        setupPointerMoveInteraction(map, document.getElementById("infoBox"), diffComuneData, metric);
    } else {
        console.warn("⚠️ Uno dei parametri è mancante, impossibile aggiornare la mappa.");
    }
});

document.getElementById('outliers').addEventListener('click', function () {

    comuniLayer.getSource().getFeatures().forEach(feature => {
                feature.setStyle(defaultStyle);
                let color = 'rgba(255, 255, 255, 0)';
                feature.set('originalColor', color);
            });

    const schoolType = document.getElementById('educationFilter').value || document.getElementById('educationFilter1').value;
    const metric = document.getElementById('extraFilter').value ? 
        (document.getElementById('extraFilter').value === "distanza" ? "km" : "min") :
        (document.getElementById('extraFilter1').value === "distanza" ? "km" : "min");

    if (schoolType && metric) {
        console.log(`🔍 Visualizzazione outliers per: ${schoolType}_${metric}`);
        updateMapDifferenceColors(schoolType, metric, comuniLayer, outliersTransport);
    } else {
        console.warn("⚠️ Seleziona un tipo di scuola e un'unità di misura prima di visualizzare gli outliers.");
        alert("Seleziona un tipo di scuola e un'unità di misura prima di visualizzare gli outliers.");
    }
});

let nucleiDataReady = false;
// Aggiungiamo un listener per il cambio di layer (Comuni <-> Nuclei)
document.querySelectorAll('input[name="layer"]').forEach(radio => {
    radio.addEventListener('change', function () {
        if (this.value === "nuclei") {
            const schoolType = document.getElementById('educationFilter').value;
            const metric = document.getElementById('extraFilter').value === "distanza" ? "km" : "min";
            const modeType = document.getElementById('modeFilter').value;
            
            console.log("📌 Cambio layer: nuclei");
            console.log("🎓 School type:", schoolType);
            console.log("🕓 Metric:", metric);
            console.log("🚗 Mode:", modeType);
            
            if (schoolType && metric) {
                console.log("🎨 Applico colorazione nuclei...");
                updateMapColorsNuclei(schoolType, metric, nucleiLayer, nucleiData);
            } else {
                console.warn("⚠️ Filtro non selezionato, nessuna colorazione nuclei.");
            }

            nucleiLayer.setVisible(true);
            comuniLayer.setVisible(false);
        } else {
            comuniLayer.setVisible(true);
            nucleiLayer.setVisible(false);
        }
    });
});

// Dopo aver caricato i dati CSV
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
    map.addLayer(nucleiLayer); // ✅ aggiunto ma invisibile
    nucleiLayer.setVisible(false);
    setupClickInteraction(map);
});

loadCsvData_diff(diffCsvPath).then(data => {
    diffComuneData = data;
    console.log("📊 Dati CSV caricati:", diffComuneData);

    // Avvia le interazioni dopo aver caricato i dati
    //setupPointerMoveInteraction(map, document.getElementById("infoBox"), diffComuneData);
});

loadCsvData_diff(outCsvPath).then(data => {
    outliersTransport = data;
    console.log("📊 Dati CSV caricati:", outliersTransport);

    // Avvia le interazioni dopo aver caricato i dati
    //setupPointerMoveInteraction(map, document.getElementById("infoBox"), outliersTransport);
});