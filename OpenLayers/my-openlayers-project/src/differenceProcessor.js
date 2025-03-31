import * as d3 from "d3";
import { updateLegend } from './utilities.js';
import Style from 'ol/style/Style';
import Stroke from 'ol/style/Stroke';
import Fill from 'ol/style/Fill';

export async function loadCsvData_diff(csvPath) {
    const response = await fetch(csvPath);
    const text = await response.text();
    const data = d3.csvParse(text);

    console.log("📊 Colonne disponibili nel CSV:", Object.keys(data[0])); // Stampiamo i nomi delle colonne!

    let comuneData = {}; // Qui salviamo solo i dati di differenza

    data.forEach(row => {
        let comune = row.Comune.trim().toUpperCase();

        comuneData[comune] = {
            SI_km: row.SI_diff_km !== "" ? parseFloat(row.SI_diff_km) : null,
            SP_km: row.SP_diff_km !== "" ? parseFloat(row.SP_diff_km) : null,
            SS_km: row.SS_diff_km !== "" ? parseFloat(row.SS_diff_km) : null,
            IC_km: row.IC_diff_km !== "" ? parseFloat(row.IC_diff_km) : null,
            SI_min: row.SI_diff_min !== "" ? parseFloat(row.SI_diff_min) : null,
            SP_min: row.SP_diff_min !== "" ? parseFloat(row.SP_diff_min) : null,
            SS_min: row.SS_diff_min !== "" ? parseFloat(row.SS_diff_min) : null,
            IC_min: row.IC_diff_min !== "" ? parseFloat(row.IC_diff_min) : null,
        };
    });

    console.log("✅ Dati differenze caricati:", comuneData);
    return comuneData;
}

/**
 * Funzione per aggiornare la colorazione dei comuni in base alla distanza selezionata
 * @param {string} schoolType - Tipologia di scuola ("SI", "SP", "SS")
 * @param {string} metric - Unità di misura ("km" o "min")
 */
export function updateMapDifferenceColors(schoolType, metric, comuniLayer, comuneData) {
    console.log(`🎨 Aggiornamento colori per: ${schoolType}_${metric}`);

    let min = Infinity;
    let max = -Infinity;

    // Prima passata: trovare i valori minimi e massimi per la scala dei colori
    comuniLayer.getSource().getFeatures().forEach(feature => {
        const comuneName = feature.get('COMUNE')?.trim().toUpperCase();
        const comuneInfo = comuneData[comuneName];

        //console.log(`🔍 [DEBUG] Comune analizzato: ${comuneName}`);
        //console.log(`🔍 [DEBUG] Chiavi disponibili per ${comuneName}:`, comuneInfo ? Object.keys(comuneInfo) : "Nessun dato");

        if (comuneInfo) {
            let keyToSearch = `${schoolType}_${metric}`.trim();
            let value = comuneInfo[keyToSearch];

            //console.log(`🔍 [DEBUG] Cerco chiave: ${keyToSearch}, Valore trovato: ${value}`);
            console.log(`🔍 Tipo valore:`, typeof value, ' - Valore:', value, ' - comune: ', comuneName);

            if (value !== null && !isNaN(value)) {
                min = Math.min(min, value);
                max = Math.max(max, value);
            }
        }
    });

    // Se i valori min e max non sono cambiati, interrompiamo qui
    if (min === Infinity || max === -Infinity) {
        console.warn("⚠️ Nessun valore valido trovato! Controlla il CSV.");
        return;
    }

    // Seconda passata: applicare il colore
    comuniLayer.getSource().getFeatures().forEach(feature => {
        const comuneName = feature.get('COMUNE')?.trim().toUpperCase();
        const comuneInfo = comuneData[comuneName];

        if (!comuneInfo) {
            feature.setStyle(new Style({
                stroke: new Stroke({ color: 'black', width: 2 })
            }));
            return;
        }

        let keyToSearch = `${schoolType}_${metric}`.trim();
        let value = comuneInfo[keyToSearch];

        if (value === null || isNaN(value)) {
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

    updateLegend(min, max, schoolType, metric);
    console.log("✅ Colorazione aggiornata!");
}
