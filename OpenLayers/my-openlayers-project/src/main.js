import 'ol/ol.css';
import { searchComune } from './filters.js';
import { loadCsvData, updateMapColors } from './comuniProcessor.js';
import { loadNucleiData, updateMapColorsNuclei} from './nucleiProcessor.js';
import { map, comuniLayer, nucleiLayer, defaultStyle } from './map.js';
import { setupClickInteraction, setupPointerMoveInteraction, setupTooltip } from './interactions_map.js';
import { setupUIEvents } from './uiEvents.js';

const csvPath = "/data/aggregati_municipio.csv"; 
let comuneData = {}; // Qui salveremo i dati del CSV

const nucleiCsvPath = "/data/aggregated_school_distances_weighted.csv";
let nucleiData = {}; // Qui salveremo i dati del CSV


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

setupUIEvents(comuneData, nucleiData);


document.getElementById('extraFilter').addEventListener('change', function () {
    const schoolType = document.getElementById('educationFilter').value;
    const metric = this.value === "distanza" ? "km" : "min";

    if (schoolType && metric) {
        updateMapColors(schoolType, metric,comuniLayer,comuneData);
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










loadNucleiData(nucleiCsvPath).then(data => {
    nucleiData = data;
    console.log("📊 Dati nuclei caricati:", nucleiData);
});



updateMapColors(schoolType, metric, comuniLayer, comuneData);
updateMapColorsNuclei(schoolType, metric, nucleiLayer, nucleiData);