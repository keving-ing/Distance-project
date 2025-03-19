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
export function updateLegend(min, max, schoolType, metric) {
    const colorBarContainer = document.getElementById('color-bar-container');
    const colorBar = document.getElementById('color-bar');
    const minValue = document.getElementById('min-value');
    const maxValue = document.getElementById('max-value');
    const title = document.getElementById('color-bar-title');

    // **🔥 Mostra il contenitore della legenda**
    colorBarContainer.style.display = "block";

    if(schoolType == 'SI'){
        schoolType = 'INFANZIA'
    }
    else if(schoolType == 'SP'){
        schoolType = 'PRIMARIA'
    }
    else{
        schoolType = 'SECONDARIA'
    }


    // **🔥 Imposta il titolo (puoi modificarlo se necessario)**
    title.innerText = "EDUCAZIONE " + schoolType;

    // **🔥 Imposta i valori min e max**
    minValue.innerText = min.toFixed(2) + " " + metric;
    maxValue.innerText = max.toFixed(2) + " " + metric;

    // **🔥 Genera la scala dei colori**
    colorBar.innerHTML = ""; // Svuota la barra prima di rigenerarla

    const steps = 50; // Numero di gradazioni da generare
    for (let i = 0; i <= steps; i++) {
        let ratio = i / steps;
        let color = `rgb(${Math.floor(255 * ratio)}, 50, ${Math.floor(255 * (1 - ratio))})`; // Scala dal rosso al blu

        const colorBlock = document.createElement("div");
        colorBlock.style.width = "25px";
        colorBlock.style.height = "10px";
        colorBlock.style.backgroundColor = color;

        colorBar.appendChild(colorBlock);
    }
}
