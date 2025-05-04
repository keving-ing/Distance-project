import { getCenter } from 'ol/extent';
import Map from 'ol/Map';
import View from 'ol/View';
import TileLayer from 'ol/layer/Tile';
import VectorLayer from 'ol/layer/Vector';
import VectorSource from 'ol/source/Vector';
import OSM from 'ol/source/OSM';
import Style from 'ol/style/Style';
import Stroke from 'ol/style/Stroke';
import Fill from 'ol/style/Fill';
import { comuniLayer, nucleiLayer } from './map.js';

/**
 * 🔥 Funzione per gestire il click sui comuni
 */
export function setupClickInteraction(map, overlay) {
  map.on('click', function (event) {
    const feature = map.forEachFeatureAtPixel(event.pixel, f => f, {
      layerFilter: layer => layer === comuniLayer
    });

    if (feature) {
      const nomeComune = feature.get('COMUNE');
      const codiceComune = feature.get('PRO_COM');
      console.log(`🟢 Comune cliccato: ${nomeComune} (${codiceComune})`);

      // Mostra popup
      const popup = document.getElementById('popup');
      popup.style.display = 'block';

      // Imposta contenuto testo
      const content = document.getElementById('popup-content');
      content.innerHTML = `<strong>Comune:</strong> ${nomeComune}<br><div id="popup-map" style="width:100%;height:200px;margin-top:8px;"></div>`;

      // Ottieni i nuclei corrispondenti
      const source = nucleiLayer.getSource();
      console.log("📦 Source oggetto:", source);
      console.log("🔍 Stato della sorgente:", source.getState());
      console.log("📦 Feature caricate finora:", source.getFeatures());
      console.log("📦 URL sorgente:", source.getUrl && source.getUrl());

      const filteredFeatures = source.getFeatures().filter(f => f.get('PRO_COM') === codiceComune);
      console.log(`📌 Trovati ${filteredFeatures.length} nuclei per il comune selezionato.`);

      if (filteredFeatures.length === 0) return;

      // Costruisci nuova mini-mappa
      const miniMap = new Map({
        target: 'popup-map',
        layers: [
          new TileLayer({
            source: new OSM({
              crossOrigin: 'anonymous'
            }),
            maxZoom: 18
          }),
          new VectorLayer({
            source: new VectorSource({
              features: filteredFeatures
            }),
            style: new Style({
                stroke: new Stroke({ color: 'black', width: 2 }),
                fill: new Fill({ color: 'rgba(0, 0, 0, 0)' }) // trasparente
              })
          })
        ],
        view: new View({
          center: getCenter(new VectorSource({ features: filteredFeatures }).getExtent()),
          zoom: 13,
          maxZoom: 18
        }),
        controls: []
      });

      console.log("🔁 Mini-mappa aggiornata.");
    }
  });
}
/**
 * 🔥 Funzione per evidenziare il bordo dei comuni quando il mouse passa sopra
 */
export function setupPointerMoveInteraction(map, infoBox, comuneData, selectedMetric) {
    let highlightedFeature = null;

    map.on('pointermove', function (event) {
        const comuneDataReady = comuneData && Object.keys(comuneData).length > 0;
    
        const feature = map.forEachFeatureAtPixel(event.pixel, feature => feature, {
            layerFilter: layer => layer === comuniLayer
        });
    
        if (!feature) {
            if (highlightedFeature) {
                highlightedFeature.setStyle(new Style({
                    fill: new Fill({
                        color: highlightedFeature.get('originalFillColor') || 'rgba(255, 255, 255, 0.001)'
                    }),
                    stroke: new Stroke({
                        color: 'black',
                        width: 1
                    })
                }));
                highlightedFeature = null;
            }
            infoBox.style.display = "none";
            return;
        }
    
        if (feature !== highlightedFeature) {
            // Ripristina la precedente
            if (highlightedFeature) {
                highlightedFeature.setStyle(new Style({
                    fill: new Fill({
                        color: highlightedFeature.get('originalFillColor') || 'rgba(255, 255, 255, 0.001)'
                    }),
                    stroke: new Stroke({
                        color: 'black',
                        width: 1
                    })
                }));
            }
    
            highlightedFeature = feature;
    
            // Salva il colore originale di riempimento se non già salvato
            if (!feature.get('originalFillColor')) {
                const currentStyle = feature.getStyle();
                if (currentStyle && currentStyle.getFill()) {
                    feature.set('originalFillColor', currentStyle.getFill().getColor());
                } else {
                    feature.set('originalFillColor', 'rgba(255, 255, 255, 0.001)');
                }
            }
    
            // Evidenzia con bordo giallo
            feature.setStyle(new Style({
                fill: new Fill({
                    color: feature.get('originalFillColor')
                }),
                stroke: new Stroke({
                    color: 'yellow',
                    width: 3
                })
            }));
    
            // Mostra il nome del comune sempre
            const comuneName = feature.get('COMUNE')?.trim().toUpperCase();
    
            // Mostra infoBox solo se i dati sono pronti
            const comuneInfo = comuneDataReady ? comuneData[comuneName] : null;
    
            if (!comuneDataReady || !comuneInfo) {
                infoBox.style.display = "none";
            } else {
                const selectedSchoolType = document.getElementById('educationFilter').value || document.getElementById('educationFilter1').value;
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
