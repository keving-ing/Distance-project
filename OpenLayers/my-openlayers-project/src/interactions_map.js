import { defaultStyle } from './map.js';
import Stroke from 'ol/style/Stroke';
import Style from 'ol/style/Style';
import Fill from 'ol/style/Fill';

/**
 * 🔥 Funzione per gestire il click sui comuni
 */
export function setupClickInteraction(map) {
    map.on('click', function (event) {
        const feature = map.forEachFeatureAtPixel(event.pixel, function (feature) {
            return feature;
        });

        if (feature) {
            const nomeComune = feature.get('COMUNE');  // Cambia con il campo corretto nel GeoJSON
            alert(`Comune: ${nomeComune}`);
        }
    });
}


let highlightedFeature = null;

/**
 * 🔥 Funzione per evidenziare il bordo dei comuni quando il mouse passa sopra
 */
export function setupPointerMoveInteraction(map, infoBox, comuneData) {
    let highlightedFeature = null;

    map.on('pointermove', function (event) {
        // **✅ Controlla se `comuneData` è caricato**
        if (!comuneData || Object.keys(comuneData).length === 0) {
            console.warn("⚠️ comuneData non è ancora caricato, saltando interazione...");
            return;
        }

        const feature = map.forEachFeatureAtPixel(event.pixel, feature => feature);

        // **🔴 Se il mouse non è su nessun comune, ripristina l'evidenziazione**
        if (!feature) {
            if (highlightedFeature) {
                highlightedFeature.setStyle(new Style({
                    fill: new Fill({ color: highlightedFeature.get('originalColor') || 'rgba(255, 255, 255, 0)' }), 
                    stroke: new Stroke({ color: 'black', width: 2 })  // 🔥 Bordo nero di default
                }));
                highlightedFeature = null;
            }
            infoBox.style.display = "none";
            return;
        }

        // **🟡 Se la feature è diversa da quella già evidenziata, aggiorniamo**
        if (feature !== highlightedFeature) {
            if (highlightedFeature) {
                highlightedFeature.setStyle(new Style({
                    fill: new Fill({ color: highlightedFeature.get('originalColor') || 'rgba(255, 255, 255, 0)' }),
                    stroke: new Stroke({ color: 'black', width: 2 })  
                }));
            }
            highlightedFeature = feature;

            feature.setStyle(new Style({
                fill: new Fill({ color: feature.get('originalColor') || 'rgba(255, 255, 255, 0)' }), 
                stroke: new Stroke({ color: 'yellow', width: 3 })  // 🔥 Evidenziamo solo il bordo
            }));

            // **🟢 Recupera il nome del comune**
            const comuneName = feature.get('COMUNE')?.trim().toUpperCase();
            const comuneInfo = comuneData[comuneName];

            if (!comuneInfo) {
                infoBox.style.display = "none";
                return;
            }

            // **📊 Prendi il filtro selezionato dall'utente**
            const selectedSchoolType = document.getElementById('educationFilter').value || document.getElementById('educationFilter1').value;
            const selectedMetric = document.getElementById('extraFilter').value ? 
                (document.getElementById('extraFilter').value === "distanza" ? "km" : "min") :
                (document.getElementById('extraFilter1').value === "distanza" ? "km" : "min");

            // Ottieni il valore corretto in base alla selezione
            const value = comuneInfo[`${selectedSchoolType}_${selectedMetric}`];

            if (selectedSchoolType && selectedMetric) { 
                infoBox.innerHTML = `
                    <strong>COMUNE:</strong> ${comuneName}<br>
                    <strong>Distanza:</strong> ${value ? value.toFixed(2) : "N/A"} ${selectedMetric}
                `;
                infoBox.style.display = "block";
            } else {
                infoBox.style.display = "none";
            }
        }
    });
}

/**
 * 🔥 Funzione per creare un tooltip con il nome del comune
 */
export function setupTooltip(map) {
    const tooltipElement = document.createElement('div');
    tooltipElement.style.position = 'absolute';
    tooltipElement.style.background = 'rgba(0, 0, 0, 0.7)';
    tooltipElement.style.color = 'white';
    tooltipElement.style.padding = '5px 10px';
    tooltipElement.style.borderRadius = '4px';
    tooltipElement.style.display = 'none';
    document.body.appendChild(tooltipElement);

    map.on('pointermove', function (event) {
        const feature = map.forEachFeatureAtPixel(event.pixel, function (feature) {
            return feature;
        });

        if (feature) {
            const nomeComune = feature.get('COMUNE'); 
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
}
