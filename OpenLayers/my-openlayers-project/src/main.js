import 'ol/ol.css';
import Map from 'ol/Map';
import View from 'ol/View';
import TileLayer from 'ol/layer/Tile';
import OSM from 'ol/source/OSM';
import XYZ from 'ol/source/XYZ';
import VectorLayer from 'ol/layer/Vector';
import VectorSource from 'ol/source/Vector';
import GeoJSON from 'ol/format/GeoJSON';
import Stroke from 'ol/style/Stroke';
import Style from 'ol/style/Style';
import { fromLonLat } from 'ol/proj';
import Overlay from 'ol/Overlay';
import { pointerMove } from 'ol/events/condition';
import Fill from 'ol/style/Fill';
import { searchComune } from './filters.js';
import { loadCsvData } from './dataProcessor.js';
import { loadNucleiData } from './nucleiProcessor.js';



// Creazione della mappa OpenLayers
const map = new Map({
    target: 'map',
    layers: [
        new TileLayer({
            source: new XYZ({
                url: 'https://{a-c}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png'
            })
        })
    ],
    view: new View({
        center: fromLonLat([12.5, 41.9]), // Lazio
        zoom: 8.5 
    })
});

// Aggiungi layer con i confini dei comuni del Lazio
const comuniLayer = new VectorLayer({
    source: new VectorSource({
        url: '/comuniLazio.geojson', // Percorso corretto
        format: new GeoJSON()
    }),
    style: new Style({
        stroke: new Stroke({
            color: 'black', // Contorno blu per i comuni
            width: 2
        })
    })
});

// Aggiungi layer con i confini dei comuni del Lazio
const nucleiLayer = new VectorLayer({
    source: new VectorSource({
        url: '/nucleos_Lazio.geojson', // Percorso corretto
        format: new GeoJSON()
    }),
    style: new Style({
        stroke: new Stroke({
            color: 'black', // Contorno blu per i comuni
            width: 1
        })
    })
});

const comuneStyle = new Style({
    stroke: new Stroke({
        color: 'black',  // Colore dei contorni
        width: 2
    }),
    
});

const nucleiStyle = new Style({
    stroke: new Stroke({
        color: 'black',  // Colore dei contorni
        width: 1
    }),
    
});



// Aggiungi il layer alla mappa
map.addLayer(comuniLayer);
comuniLayer.setStyle(comuneStyle);

// Aggiungi il layer alla mappa
map.addLayer(nucleiLayer);
nucleiLayer.setStyle(nucleiStyle)

const layerRadios = document.querySelectorAll('input[name="layer"]');

// Imposta i layer iniziali
nucleiLayer.setVisible(false); // ❌ Nuclei inizialmente nascosti
comuniLayer.setVisible(true);  // 🔥 Mostrati di default

// Aggiungi evento per il cambio layer
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



map.on('click', function (event) {
    const feature = map.forEachFeatureAtPixel(event.pixel, function (feature) {
        return feature;
    });

    if (feature) {
        const nomeComune = feature.get('COMUNE');  // Cambia con il campo corretto nel GeoJSON
        //const popolazione = feature.get('popolazione');  // Esempio di altro dato
        alert(`Comune: ${nomeComune}`);
    }
});


const defaultStyle = new Style({
    stroke: new Stroke({
        color: 'black',
        width: 2
    }),
});

const highlightStyle = new Style({
    stroke: new Stroke({
        color: 'red',
        width: 3
    }),
    fill: new Fill({
        color: 'rgba(247, 197, 169, 0.3)' // Giallo trasparente
    })
});

let highlightedFeature = null;

map.on('pointermove', function (event) {
    const feature = map.forEachFeatureAtPixel(event.pixel, function (feature) {
        return feature;
    });

    // Se il mouse non è su nessun comune, rimuovi l'evidenziazione
    if (!feature) {
        if (highlightedFeature) {
            highlightedFeature.setStyle(new Style({
                fill: new Fill({ color: highlightedFeature.get('originalColor') || 'rgba(255, 255, 255, 0)' }), // Nessun colore se non esiste
                stroke: new Stroke({ color: 'black', width: 2 })  // Bordo nero standard
            }));
            highlightedFeature = null;
        }
        infoBox.style.display = "none";
        return;
    }

    // Se è una nuova feature, aggiorna l'evidenziazione
    if (feature !== highlightedFeature) {
        if (highlightedFeature) {
            highlightedFeature.setStyle(new Style({
                fill: new Fill({ color: highlightedFeature.get('originalColor') || 'rgba(255, 255, 255, 0)' }),
                stroke: new Stroke({ color: 'black', width: 2 })
            }));
        }
        highlightedFeature = feature;

        // **Evidenziamo SOLO il bordo senza cambiare il riempimento**
        feature.setStyle(new Style({
            fill: new Fill({ color: feature.get('originalColor') || 'rgba(255, 255, 255, 0)' }), // Mantiene il colore originale o trasparente
            stroke: new Stroke({ color: 'yellow', width: 3 })  // Bordo giallo per evidenziare
        }));

        // Mostra le informazioni nel riquadro
        const comuneName = feature.get('COMUNE')?.trim().toUpperCase();
        const comuneNameFormatted = comuneName.trim().toUpperCase();
        const comuneInfo = comuneData[comuneNameFormatted];

        if (comuneInfo) {
            const schoolType = document.getElementById('educationFilter').value;
            const metric = document.getElementById('extraFilter').value === "distanza" ? "km" : "min";
            const value = comuneInfo[`${schoolType}_${metric}`];

            if (schoolType && metric) { // 🔥 Mostra il box solo se c'è un filtro attivo
                infoBox.innerHTML = `
                    <strong>COMUNE:</strong> ${comuneName}<br>
                    <strong>Distanza:</strong> ${value ? value.toFixed(2) : "N/A"} ${metric}
                `;
                infoBox.style.display = "block";
            } else {
                infoBox.style.display = "none";
            }
        } else {
            infoBox.style.display = "none";
        }
    }
});



// Crea un elemento HTML per il tooltip
const tooltipElement = document.createElement('div');
tooltipElement.style.position = 'absolute';
tooltipElement.style.background = 'rgba(0, 0, 0, 0.7)';
tooltipElement.style.color = 'white';
tooltipElement.style.padding = '5px 10px';
tooltipElement.style.borderRadius = '4px';
tooltipElement.style.display = 'none';
document.body.appendChild(tooltipElement);

// Aggiungi un evento per mostrare il nome del comune quando passi sopra
map.on('pointermove', function (event) {
    const feature = map.forEachFeatureAtPixel(event.pixel, function (feature) {
        return feature;
    });

    if (feature) {
        const nomeComune = feature.get('COMUNE'); // Assicurati che il campo si chiami "name"
        if (nomeComune) {
            tooltipElement.innerHTML = nomeComune;
            tooltipElement.style.left = event.pixel[0] + 10 + 'px';
            tooltipElement.style.top = event.pixel[1] + 10 + 'px';
            tooltipElement.style.display = 'block';
        }
    } else {
        tooltipElement.style.display = 'none';
    }
});



document.getElementById('searchComune').addEventListener('keypress', function (event) {
    if (event.key === 'Enter') {  // Se l'utente preme Invio
        searchComune(map, comuniLayer, this.value);
    }
});

document.getElementById('educationFilter').addEventListener('change', function () {
    const extraFilterContainer = document.getElementById('extraFilterContainer');

    if (this.value) {  
        extraFilterContainer.style.display = "block";  // Mostra il secondo menu
    } else {
        extraFilterContainer.style.display = "none";   // Nasconde il secondo menu se si deseleziona
    }
});


const csvPath = "/data/aggregati_municipio.csv"; 
let comuneData = {}; // Qui salveremo i dati del CSV

// Carica i dati CSV all'avvio
loadCsvData(csvPath).then(data => {
    comuneData = data;
    console.log("📊 Dati CSV caricati:", comuneData);
});

/**
 * Funzione per aggiornare la colorazione dei comuni in base alla distanza selezionata
 * @param {string} schoolType - Tipologia di scuola ("SI", "SP", "SS")
 * @param {string} metric - Unità di misura ("km" o "min")
 */
function updateMapColors(schoolType, metric) {
    console.log(`🎨 Aggiornamento colori per: ${schoolType}_${metric}`);

    let min = Infinity;
    let max = -Infinity;

    // Prima passata: trovare i valori minimi e massimi per la scala dei colori
    comuniLayer.getSource().getFeatures().forEach(feature => {

        const comuneName = feature.get('COMUNE')?.trim().toUpperCase();
        const comuneNameFormatted = comuneName.trim().toUpperCase();
        const comuneInfo = comuneData[comuneNameFormatted];

        if (comuneInfo) {
            let value = comuneInfo[`${schoolType}_${metric}`];
            if (!isNaN(value) && value !== null) {
                min = Math.min(min, value);
                max = Math.max(max, value);
            }
        }
    });


    // Seconda passata: applicare il colore
    comuniLayer.getSource().getFeatures().forEach(feature => {
        const comuneName = feature.get('COMUNE')?.trim().toUpperCase();
        const comuneNameFormatted = comuneName.trim().toUpperCase();
        const comuneInfo = comuneData[comuneNameFormatted];

        if (!comuneInfo) {


            feature.setStyle(new Style({
                stroke: new Stroke({ color: 'black', width: 2 })
            }));
            return;
        }

        

        let keyToSearch = `${schoolType}_${metric}`;


        let value = comuneInfo[`${schoolType}_${metric}`];

        if (isNaN(value) || value === null) {
            feature.setStyle(new Style({
                fill: new Fill({ color: 'rgba(255, 255, 255, 0.7)' }),
                stroke: new Stroke({ color: 'black', width: 2 })
            }));
            return;
        }

        // Scala colori da Blu (min) → Rosso (max)
        let ratio = (value - min) / (max - min); // Normalizzazione tra 0 e 1
        let color = `rgb(${Math.floor(255 * ratio)}, 50, ${Math.floor(255 * (1 - ratio))})`;

        feature.setStyle(new Style({
            fill: new Fill({ color: color }),
            stroke: new Stroke({ color: 'black', width: 2 })
        }));

        feature.set('originalColor', color); // Memorizziamo il colore originale
    });

    updateLegend(min, max);
    console.log("✅ Colorazione aggiornata!");
}


document.getElementById('extraFilter').addEventListener('change', function () {
    const schoolType = document.getElementById('educationFilter').value;
    const metric = this.value === "distanza" ? "km" : "min";

    if (schoolType && metric) {
        updateMapColors(schoolType, metric);
    }
});


const infoBox = document.getElementById("infoBox");



document.getElementById('resetFilters').addEventListener('click', function () {
    document.getElementById('educationFilter').value = "";
    document.getElementById('extraFilter').value = "";
    document.getElementById('extraFilterContainer').style.display = "none";
    infoBox.style.display = "none";

    // 🔥 Ripristina lo stile di tutti i comuni
    comuniLayer.getSource().getFeatures().forEach(feature => {
        feature.setStyle(defaultStyle);
    });

    console.log("🔄 Filtri resettati e mappa ripristinata!");
});

function updateLegend(min, max) {
    const legend = document.getElementById('legend');
    document.getElementById('legend-max').innerText = `${max.toFixed(2)}`;
    document.getElementById('legend-min').innerText = `${min.toFixed(2)}`;
    legend.style.display = "block"; // 🔥 Mostra la legenda
}


document.getElementById('resetFilters').addEventListener('click', function () {
    document.getElementById('educationFilter').value = "";
    document.getElementById('extraFilter').value = "";
    document.getElementById('extraFilterContainer').style.display = "none";
    infoBox.style.display = "none";
    document.getElementById('legend').style.display = "none"; // 🔥 Nasconde la legenda

    comuniLayer.getSource().getFeatures().forEach(feature => {
        feature.setStyle(defaultStyle);
    });

    console.log("🔄 Filtri resettati e mappa ripristinata!");
});


const nucleiCsvPath = "/data/aggregated_school_distances_weighted.csv";
let nucleiData = {};

loadNucleiData(nucleiCsvPath).then(data => {
    nucleiData = data;
    console.log("📊 Dati nuclei caricati:", nucleiData);
});

// Aggiungiamo un listener per il cambio di layer (Comuni <-> Nuclei)
document.querySelectorAll('input[name="layer"]').forEach(radio => {
    radio.addEventListener('change', function () {
        if (this.value === "nuclei") {
            updateMapColorsNuclei();
        } else {
            updateMapColors();
        }
    });
});

/**
 * Funzione per aggiornare la colorazione dei nuclei urbani
 */
function updateMapColorsNuclei() {
    console.log("🎨 Cambio layer: visualizzazione nuclei");

    let min = Infinity;
    let max = -Infinity;

    nucleiLayer.getSource().getFeatures().forEach(feature => {
        const comuneName = feature.get('COMUNE')?.trim().toUpperCase();
        const comuneInfo = nucleiData[comuneName];

        if (comuneInfo) {
            comuneInfo.forEach(nucleo => {
                let value = nucleo[`${schoolType}_${metric}`];
                if (!isNaN(value) && value !== null) {
                    min = Math.min(min, value);
                    max = Math.max(max, value);
                }
            });
        }
    });

    nucleiLayer.getSource().getFeatures().forEach(feature => {
        const comuneName = feature.get('COMUNE')?.trim().toUpperCase();
        const comuneInfo = nucleiData[comuneName];

        if (!comuneInfo) {
            feature.setStyle(defaultStyle);
            return;
        }

        let nucleoID = feature.get('Nucleo_ID');
        let nucleoData = comuneInfo.find(n => n["Nucleo_ID"] === nucleoID);

        if (!nucleoData) {
            feature.setStyle(defaultStyle);
            return;
        }

        let value = nucleoData[`${schoolType}_${metric}`];

        if (isNaN(value) || value === null) {
            feature.setStyle(new Style({
                fill: new Fill({ color: 'rgba(255, 255, 255, 0.7)' }),
                stroke: new Stroke({ color: 'black', width: 1 })
            }));
            return;
        }

        let ratio = (value - min) / (max - min);
        let color = `rgba(${Math.floor(255 * ratio)}, 50, ${Math.floor(255 * (1 - ratio))}, 1)`;

        feature.setStyle(new Style({
            fill: new Fill({ color: color }),
            stroke: new Stroke({ color: 'black', width: 1 })
        }));

        feature.set('originalColor', color);
    });

    console.log("✅ Nuclei aggiornati!");
}