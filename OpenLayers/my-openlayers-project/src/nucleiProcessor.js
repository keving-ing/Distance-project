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
    let sum = 0;          
    let count = 0; 

   
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
                sum += value;
                count++;
            }
        } else {
            
        }
    });

    let media = count > 0 ? (sum / count) : 0;
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

        let ratio
        let color;

        if(value <= media){
            ratio = (value - min) / (media - min); // Normalizzazione tra 0 e 1
            const r = Math.max(0, Math.min(1, ratio));
            color = `rgb(${Math.floor(0 + 80 * r)}, ${Math.floor(50 + 130 * r)}, ${ Math.floor(200 + 55 * r)})`;
        }else{
            ratio = (value - media) / (max - media);
            const r = Math.max(0, Math.min(1, ratio));
            color = `rgb(${Math.floor(80 + 140 * r)}, ${Math.floor(180 - 140 * r)}, ${Math.floor(255 - 215 * r)})`;
        }


        feature.setStyle(new Style({
            fill: new Fill({ color: color }),
            stroke: new Stroke({ color: 'black', width: 1 })
        }));

        feature.set('originalColor', color);
    });
    
    //updateLegend(min, max);
    console.log("✅ Nuclei aggiornati!");
}

