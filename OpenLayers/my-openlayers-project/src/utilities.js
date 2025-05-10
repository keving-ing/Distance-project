import { map, comuniLayer, nucleiLayer, defaultStyle } from './map.js';

/**
 * 🔥 Funzione per pulire gli ID e renderli confrontabili
 */
export function cleanID(id) {
    if (typeof id === 'number') {
        id = id.toString();  // Converti in stringa se è numero
    }
    
    if (id.includes('.')) {
        id = id.split('.')[0];  // 🔥 Rimuove tutto dopo il punto (6004026601.000001 → 6004026601)
    }

    return id.trim()+".0";  // 🔥 Rimuove spazi
}

/**
 * 🔥 Funzione per aggiornare la leggenda dei colori
 */
export function updateLegend(min, max, schoolType, metric, media) {

    
    const colorBarContainer = document.getElementById('color-bar-container');
    const colorBar = document.getElementById('color-bar');
    const minValue = document.getElementById('min-value');
    const maxValue = document.getElementById('max-value');
    const title = document.getElementById('color-bar-title');

    // **🔥 Mostra il contenitore della legenda**
    colorBarContainer.style.display = "block";

    if(schoolType == 'SI'){
        schoolType = 'EDUCAZIONE INFANZIA'
    }
    else if(schoolType == 'SP'){
        schoolType = 'EDUCAZIONE PRIMARIA'
    }
    else if(schoolType == 'SS'){
        schoolType = 'EDUCAZIONE SECONDARIA'
    }
    else if(schoolType == 'MG'){
        schoolType = 'MEDICI DI FAMIGLIA'
    }
    else if(schoolType == 'OS'){
        schoolType = 'STRUTTURE OSPEDALIERE'
    }


    // **🔥 Imposta il titolo (puoi modificarlo se necessario)**
    title.innerText = schoolType;

    console.log(`METRIC: ${metric}`);

    // **🔥 Imposta i valori min e max**
    minValue.innerText = min.toFixed(2) + " " + metric;
    maxValue.innerText = max.toFixed(2) + " " + metric;

    const steps = 50;
    colorBar.innerHTML = ""; // Pulisce la barra

    for (let i = 0; i <= steps; i++) {
        const ratio = i / steps;
        let color;

        if (ratio <= 0.5) {
            // 🔵 Sotto la media
            const localRatio = ratio / 0.5;
            color = `rgb(${Math.floor(0 + 80 * localRatio)}, ${Math.floor(50 + 130 * localRatio)}, ${Math.floor(200 + 55 * localRatio)})`;
        } else {
            // 🔴 Sopra la media
            const localRatio = (ratio - 0.5) / 0.5;
            color = `rgb(${Math.floor(80 + 140 * localRatio)}, ${Math.floor(180 - 140 * localRatio)}, ${Math.floor(255 - 215 * localRatio)})`;
        }

        const colorBlock = document.createElement("div");
        colorBlock.style.width = "25px";
        colorBlock.style.height = "10px";
        colorBlock.style.backgroundColor = color;

        colorBar.appendChild(colorBlock);
    }


    document.getElementById("color-bar-container").style.display = "block";
}

export function resetAll() {
    // Nasconde tutti i menu
    document.getElementById("controls").style.display = "none";
    document.getElementById("healthAnalysisControls").style.display = "none";
    document.getElementById("transportAnalysisControls").style.display = "none";

    // Resetta i valori dei filtri
    const allInputs = document.querySelectorAll(
        '#controls select, #controls input, ' +
        '#healthAnalysisControls select, #healthAnalysisControls input, ' +
        '#transportAnalysisControls select, #transportAnalysisControls input'
    );
    allInputs.forEach(input => input.value = "");

    // Nasconde i contenitori extra
    document.getElementById("extraFilterContainer").style.display = "none";
    document.getElementById("extraFilterContainer1").style.display = "none";
    document.getElementById("extraHealthFilterContainer").style.display = "none";

    // Nasconde la legenda e l'infobox
    document.getElementById('color-bar-container').style.display = "none";
    document.getElementById('infoBox').style.display = "none";

    // Ripristina la mappa
    comuniLayer.getSource().getFeatures().forEach(feature => {
        feature.setStyle(defaultStyle);
        feature.set('originalColor', 'rgba(255, 255, 255, 0)');
    });

    nucleiLayer.setVisible(false);
    comuniLayer.setVisible(true);
    document.querySelector('input[name="layer"][value="comuni"]').checked = true;

    console.log("🔄 Reset globale completato.");
}

