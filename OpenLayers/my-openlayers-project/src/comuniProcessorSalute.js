import * as d3 from "d3";
import { updateLegend } from './utilities.js';
import Style from 'ol/style/Style';
import Stroke from 'ol/style/Stroke';
import Fill from 'ol/style/Fill';

/**
 * 📥 Carica i dati CSV per la salute
 */
export async function loadHealthCsvData(csvPath) {
    const response = await fetch(csvPath);
    const text = await response.text();
    const data = d3.csvParse(text);

    console.log("📊 Colonne disponibili nel CSV Salute:", Object.keys(data[0]));

    let healthData = {};
    data.forEach(row => {
        let comune = row.Comune.trim().toUpperCase();
        healthData[comune] = {
            km: parseFloat(row.mean_km) || null,
            min: parseFloat(row.mean_min) || null
        };
    });

    return healthData;
}

/**
 * 🎨 Aggiorna la mappa con i colori per i dati di salute
 */
export function updateMapColorsHealth(metric, comuniLayer, healthData, type) {
    console.log(`🎨 Aggiornamento colori salute per: ${metric}`);

    let min = Infinity;
    let max = -Infinity;
    let sum = 0;
    let count = 0;
    console.log(`🧪 metric: ${metric}`);
    // Prima passata: trovo min, max, media
    comuniLayer.getSource().getFeatures().forEach(feature => {
        const comuneName = feature.get("COMUNE")?.trim().toUpperCase();
        const comuneInfo = healthData[comuneName];

        if (comuneInfo) {
            const value = comuneInfo[metric];
            if (!isNaN(value) && value !== null) {
                min = Math.min(min, value);
                max = Math.max(max, value);
                sum += value;
                count++;
            }
        }
    });

    let media = count > 0 ? (sum / count) : 0;
    console.log(`📊 Min: ${min}, Max: ${max}, Media: ${media.toFixed(2)}`);

    // Seconda passata: colora
    comuniLayer.getSource().getFeatures().forEach(feature => {
        const comuneName = feature.get("COMUNE")?.trim().toUpperCase();
        const comuneInfo = healthData[comuneName];

        if (!comuneInfo) {
            feature.setStyle(new Style({
                stroke: new Stroke({ color: 'black', width: 1 })
            }));
            return;
        }

        const value = comuneInfo[metric];
        if (isNaN(value) || value === null) {
            feature.setStyle(new Style({
                fill: new Fill({ color: 'rgba(255, 255, 255, 0.7)' }),
                stroke: new Stroke({ color: 'black', width: 1 })
            }));
            return;
        }

        let ratio, color;
        if (value <= media) {
            ratio = (value - min) / (media - min);
            const r = Math.max(0, Math.min(1, ratio));
            color = `rgb(${Math.floor(0 + 80 * r)}, ${Math.floor(50 + 130 * r)}, ${Math.floor(200 + 55 * r)})`;
        } else {
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

    updateLegend(min, max, type, metric, media);
    document.getElementById('extraHealthFilter').value = "";
    console.log("✅ Mappa salute aggiornata!");
}