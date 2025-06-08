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
import { romaLayer } from './mapRoma.js';
import { t } from './i18n.js';


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

      const tooltip = document.createElement('div');
        tooltip.className = 'popup-tooltip';
        tooltip.style.cssText = `
        position: absolute;
        background: rgba(0, 0, 0, 0.7);
        color: white;
        padding: 4px 6px;
        border-radius: 4px;
        font-size: 12px;
        pointer-events: none;
        display: none;
        `;
        document.getElementById('popup-map').appendChild(tooltip);

        miniMap.on('pointermove', function (evt) {
        const pixel = miniMap.getEventPixel(evt.originalEvent);
        const hit = miniMap.hasFeatureAtPixel(pixel);
        if (hit) {
            const feature = miniMap.forEachFeatureAtPixel(pixel, f => f);
            const nome = feature.get('NOME') || 'Nucleo sconosciuto';
            tooltip.innerText = nome;
            tooltip.style.left = `${evt.originalEvent.offsetX + 10}px`;
            tooltip.style.top = `${evt.originalEvent.offsetY + 10}px`;
            tooltip.style.display = 'block';
        } else {
            tooltip.style.display = 'none';
        }
        });

      console.log("🔁 Mini-mappa aggiornata.");
    }
  });
}
/**
 * 🔥 Funzione per evidenziare il bordo dei comuni quando il mouse passa sopra
 */
let currentPointerMoveHandler = null;

export function setupPointerMoveInteraction(map, infoBox, comuneData, selectedMetric) {

    console.log("🧪 Comuni presenti in comuneData:", Object.keys(comuneData));
    
    // 🔄 Rimuovi il precedente listener se esistente
    if (currentPointerMoveHandler) {
        map.un('pointermove', currentPointerMoveHandler);
    }

    let highlightedFeature = null;

    // 🔁 Nuovo handler da salvare
    currentPointerMoveHandler = function (event) {
        const comuneDataReady = comuneData && Object.keys(comuneData).length > 0;

       

        const feature = map.forEachFeatureAtPixel(event.pixel, f => f, {
            layerFilter: layer => layer === comuniLayer || layer === romaLayer
        });

        if (!feature) {
            if (highlightedFeature) {
                highlightedFeature.setStyle(new Style({
                    fill: new Fill({
                        color: highlightedFeature.get('originalColor') || 'rgba(255, 255, 255, 0.001)'
                    }),
                    stroke: new Stroke({ color: 'black', width: 1 })
                }));
                highlightedFeature = null;
            }
            infoBox.style.display = "none";
            return;
        }

        if (feature !== highlightedFeature) {
            if (highlightedFeature) {
                highlightedFeature.setStyle(new Style({
                    fill: new Fill({
                        color: highlightedFeature.get('originalColor') || 'rgba(255, 255, 255, 0.001)'
                    }),
                    stroke: new Stroke({ color: 'black', width: 1 })
                }));
            }

            highlightedFeature = feature;

            feature.setStyle(new Style({
                fill: new Fill({
                    color: feature.get('originalColor') || 'rgba(255,255,255,0)'
                }),
                stroke: new Stroke({
                    color: 'yellow',
                    width: 3
                })
            }));

            const comuneName = feature.get('COMUNE')?.trim().toUpperCase();
            console.log(`🧪 comuneName: ${comuneName}`);

            const comuneInfo = comuneDataReady ? comuneData[comuneName] : null;
            console.log(`🧪 comuneInfo per ${comuneName}:`, comuneInfo);

            if (!comuneDataReady || !comuneInfo) {
                console.warn(`⚠️ Nessuna info per: ${comuneName}`);
                infoBox.style.display = "none";
                return;
            }

            let value = null;
            let label = null;

            // EDUCAZIONE
            const schoolType = document.getElementById('educationFilter').value || document.getElementById('educationFilter1').value;
            if (schoolType && `${schoolType}_${selectedMetric}` in comuneInfo) {
                value = comuneInfo[`${schoolType}_${selectedMetric}`];
                label = `Educazione (${schoolType})`;
            }
            // SALUTE
            else if (`km` in comuneInfo || `min` in comuneInfo) {
                value = comuneInfo[selectedMetric];
                const healthType = document.getElementById('healthFilter').value;
                label = `Salute (${healthType})`;
            }

            if (label && selectedMetric && value !== undefined) {
                const translatedComune = t("info_comune");
                const translatedValore = t("info_valore", {
                    label: label,
                    value: value ? value.toFixed(2) : "N/A",
                    unit: selectedMetric
                });

                infoBox.innerHTML = `
                    <strong>${translatedComune}:</strong> ${comuneName}<br>
                    <strong>${translatedValore}</strong>
                `;
                infoBox.style.display = "block";
            } else {
                console.warn(`❌ Dati incompleti per ${comuneName} → label:${label}, metric:${selectedMetric}, value:${value}`);
                infoBox.style.display = "none";
            }
        }
    };

    // ✅ Registra il nuovo listener
    map.on('pointermove', currentPointerMoveHandler);
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
    tooltipElement.style.pointerEvents = 'none';
    tooltipElement.style.zIndex = 9999;
    document.body.appendChild(tooltipElement);

    map.on('pointermove', function (event) {
        const feature = map.forEachFeatureAtPixel(event.pixel, f => f);

        if (feature) {
            const nomeComune = feature.get('COMUNE');
            if (nomeComune) {
                const labelComune = t("info_comune");
                tooltipElement.innerHTML = `<strong>${labelComune}:</strong> ${nomeComune}`;
                tooltipElement.style.left = event.pixel[0] + 10 + 'px';
                tooltipElement.style.top = event.pixel[1] + 10 + 'px';
                tooltipElement.style.display = 'block';
            }
        } else {
            tooltipElement.style.display = 'none';
        }
    });
}
