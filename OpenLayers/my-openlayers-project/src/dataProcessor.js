import * as d3 from "d3";

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
