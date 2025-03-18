import { cleanID, updateLegend } from './utilities.js';
import Style from 'ol/style/Style';
import Stroke from 'ol/style/Stroke';
import Fill from 'ol/style/Fill';

export async function loadNucleiData(csvPath) {
    try {
        const response = await fetch(csvPath);
        const text = await response.text();
        
        const rows = text.split("\n").map(row => row.split(","));
        const headers = rows[0].map(h => h.trim());

        let nucleiData = {};
        for (let i = 1; i < rows.length; i++) {
            let obj = {};
            let nucleoID = rows[i][1]?.trim(); // 🔥 Usiamo il Nucleo_ID come chiave

            if (!nucleoID) continue; // Salta righe senza Nucleo_ID

            obj["Nucleo_ID"] = nucleoID;
            headers.forEach((h, index) => {
                if (index > 1) { // Ignora Comune e Nucleo_ID
                    obj[h] = parseFloat(rows[i][index]) || null;
                }
            });

            nucleiData[nucleoID] = obj; // 🔥 Ora la chiave è l'ID del nucleo
        }

        console.log("📊 Dati Nuclei caricati:", nucleiData);
        return nucleiData;
    } catch (error) {
        console.error("❌ Errore nel caricamento del CSV dei nuclei:", error);
        return {};
    }
}

/**
 * Funzione per aggiornare la colorazione dei nuclei urbani
 */
export function updateMapColorsNuclei(schoolType, metric, nucleiLayer, nucleiData) {
    console.log("🎨 Cambio layer: visualizzazione nuclei");

    let min = Infinity;
    let max = -Infinity;

   
    // 🔥 PRIMA PASSATA: Trova Min/Max
    nucleiLayer.getSource().getFeatures().forEach(feature => {
        let nucleoID = feature.get('LOC21_ID');  // ID dal GeoJSON
        

        if (!nucleoID) {
            console.warn(`⚠️ Feature senza LOC21_ID, impossibile associare i dati.`);
            return;
        }

        nucleoID = cleanID(nucleoID);  // 🔥 Normalizziamo l'ID


        const nucleoData = nucleiData[nucleoID];


        if (nucleoData) {
            let value = nucleoData[`${schoolType}_mean_${metric}`];


            if (!isNaN(value) && value !== null) {
                min = Math.min(min, value);
                max = Math.max(max, value);
            }
        } else {
            
        }
    });

    console.log(`📊 Min: ${min}, Max: ${max}`);

    // 🔥 SECONDA PASSATA: Applica colori normalizzati
    nucleiLayer.getSource().getFeatures().forEach(feature => {
        let nucleoID = feature.get('LOC21_ID');  
        if (!nucleoID) return;

        nucleoID = cleanID(nucleoID);

        const nucleoData = nucleiData[nucleoID];

        if (!nucleoData) {
            return;
        }

        let value = nucleoData[`${schoolType}_mean_${metric}`];

        if (isNaN(value) || value === null) return;

        let ratio = (value - min) / (max - min);
        let color = `rgba(${Math.floor(255 * ratio)}, 50, ${Math.floor(255 * (1 - ratio))}, 1)`;


        feature.setStyle(new Style({
            fill: new Fill({ color: color }),
            stroke: new Stroke({ color: 'black', width: 1 })
        }));

        feature.set('originalColor', color);
    });
    
    updateLegend(min, max);
    console.log("✅ Nuclei aggiornati!");
}

