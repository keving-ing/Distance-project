import * as d3 from "d3";
import { updateLegend } from './utilities.js';
import Style from 'ol/style/Style';
import Stroke from 'ol/style/Stroke';
import Fill from 'ol/style/Fill';

import Papa from 'papaparse'; // se usi Papaparse (consigliato)
// Mappa per salvare: { "056059": 66188 }
export const popolazioneMap = {};

fetch('/DCIS_POPRES1_12022025124521891.csv')
  .then(response => response.text())
  .then(csv => {
    Papa.parse(csv, {
      header: true,
      skipEmptyLines: true,
      complete: (results) => {
        results.data.forEach(row => {
          const codice = row['ITTER107'];
          const valore = parseInt(row['Value']);
          if (!isNaN(valore)) {
            popolazioneMap[codice] = valore;
          }
        });
        console.log("✅ Popolazione caricata:", popolazioneMap);
        console.log("📄 CSV grezzo:", csv.slice(0, 300)); // stampa le prime righe
        Papa.parse(csv, {
            header: true,
            complete: results => {
            console.log("✅ Dati PapaParse:", results.data); // deve stampare array
            }
        });
      }
    });
    
  });


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
export function updateMapColorsHealth(metric, comuniLayer, healthData, type, selectedProvinces = [], maxPop = 40000) {
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

        const codiceProvincia = feature.get('COD_PROV');
        const codiceComune = String(feature.get('PRO_COM_T'));
        const popolazioneComune = popolazioneMap[codiceComune] || 0;

        if (
            isNaN(value) ||
            value === null ||
            popolazioneComune > maxPop ||
            (selectedProvinces.length > 0 && !selectedProvinces.includes(String(codiceProvincia)))
        ) {
            feature.setStyle(new Style({
                fill: new Fill({ color: 'rgba(255, 255, 255, 0.7)' }),
                stroke: new Stroke({ color: 'black', width: 1 })
            }));
            feature.set('originalColor', 'rgba(255, 255, 255, 0.7)');
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
    document.getElementById('extraFilter1').value = "";
    console.log("✅ Mappa salute aggiornata!");
}