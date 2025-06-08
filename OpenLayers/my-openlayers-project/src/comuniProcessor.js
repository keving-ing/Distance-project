import * as d3 from "d3";
import { updateLegend } from './utilities.js';
import Style from 'ol/style/Style';
import Stroke from 'ol/style/Stroke';
import Fill from 'ol/style/Fill';
import Papa from 'papaparse'; // se usi Papaparse (consigliato)
// Mappa per salvare: { "056059": 66188 }
const popolazioneMap = {};

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
      }
    });
  });


export async function loadCsvData(csvPath) {
    const response = await fetch(csvPath);
    const text = await response.text();
    const data = d3.csvParse(text);

    console.log("📊 Colonne disponibili nel CSV:", Object.keys(data[0])); // Stampiamo i nomi delle colonne!

    let comuneData = {};
    data.forEach(row => {
        let comune = row.Comune.trim().toUpperCase();
        comuneData[comune] = {
            SI_km: parseFloat(row.SI_mean_km) || null,
            SP_km: parseFloat(row.SP_mean_km) || null,
            SS_km: parseFloat(row.SS_mean_km) || null,
            IC_km: parseFloat(row.IC_mean_km) || null,
            SI_min: parseFloat(row.SI_mean_min) || null,
            SP_min: parseFloat(row.SP_mean_min) || null,
            SS_min: parseFloat(row.SS_mean_min) || null,
            IC_min: parseFloat(row.IC_mean_min) || null
        };
    });

    return comuneData;
}

/**
 * Funzione per aggiornare la colorazione dei comuni in base alla distanza selezionata
 * @param {string} schoolType - Tipologia di scuola ("SI", "SP", "SS")
 * @param {string} metric - Unità di misura ("km" o "min")
 */
export function updateMapColors(schoolType, modeType, metric, comuniLayer, comuneData, selectedProvinces = [], maxPop = 40000) {
    console.log(`🎨 Aggiornamento colori per: ${schoolType}_${metric}`);

    let min = Infinity;
    let max = -Infinity;
    let sum = 0;          
    let count = 0;        

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
                sum += value;
                count++;
            }
        }
    });

    let media = count > 0 ? (sum / count) : 0;
    console.log(`📊 Min: ${min}, Max: ${max}, Media: ${media.toFixed(2)}`);


    // Seconda passata: applicare il colore
    comuniLayer.getSource().getFeatures().forEach(feature => {
        const comuneName = feature.get('COMUNE')?.trim().toUpperCase();
        const comuneNameFormatted = comuneName.trim().toUpperCase();
        const comuneInfo = comuneData[comuneNameFormatted];

        if (!comuneInfo) {


            feature.setStyle(new Style({
                stroke: new Stroke({ color: 'black', width: 1 })
            }));
            return;
        }

        

        let keyToSearch = `${schoolType}_${metric}`;


        let value = comuneInfo[`${schoolType}_${metric}`];

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

        // Scala colori da Blu (min) → Rosso (max)
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
        
        // ✅ Salva anche il colore originale nel feature
        feature.set('originalColor', color);
    });

    updateLegend(min, max, schoolType, metric, modeType);
    document.getElementById('extraFilter').value = "";
    document.getElementById('extraFilter1').value = "";
    console.log("✅ Colorazione aggiornata!");
}
