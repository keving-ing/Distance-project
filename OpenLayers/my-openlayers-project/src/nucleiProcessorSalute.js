import { cleanID } from './utilities.js';
import Style from 'ol/style/Style';
import Stroke from 'ol/style/Stroke';
import Fill from 'ol/style/Fill';


/**
 * Funzione per aggiornare la colorazione dei nuclei urbani (accessibilità SALUTE)
 */
export function updateMapColorsNucleiSalute(metric, nucleiLayer, nucleiData) {
    console.log("🎨 Visualizzazione nuclei (SALUTE)");

    let min = Infinity;
    let max = -Infinity;
    let sum = 0;          
    let count = 0; 

    // 🔍 PRIMA PASSATA: trova min e max
    nucleiLayer.getSource().getFeatures().forEach((feature, index) => {
        let nucleoID = feature.get('LOC21_ID');
        if (!nucleoID) {
            console.warn(`❌ Feature senza LOC21_ID (feature #${index})`);
            return;
        }

        //nucleoID = cleanID(nucleoID);

        const nucleoData = nucleiData[nucleoID];

        if (!nucleoData) {
            return;
        }

        const value = nucleoData[`mean_${metric}`];
        //console.log(`🔍 ${nucleoID} → mean_${metric} =`, value);

        if (!isNaN(value) && value !== null) {
            min = Math.min(min, value);
            max = Math.max(max, value);
            sum += value;
            count++;
        } else {
            console.warn(`⚠️ Valore non valido per ${nucleoID}:`, value);
        }
    });

    let media = count > 0 ? (sum / count) : 0;
    console.log(`📊 Min: ${min}, Max: ${max}`);

    // 🎨 SECONDA PASSATA: applica colorazione
    nucleiLayer.getSource().getFeatures().forEach(feature => {
        let nucleoID = feature.get('LOC21_ID');
        if (!nucleoID) return;

        //nucleoID = cleanID(nucleoID);
        const nucleoData = nucleiData[nucleoID];
        if (!nucleoData) return;

        const value = nucleoData[`mean_${metric}`];
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
            fill: new Fill({ color }),
            stroke: new Stroke({ color: 'black', width: 1 })
        }));

        feature.set('originalColor', color);
    });

    console.log("✅ Nuclei (salute) aggiornati!");
}
