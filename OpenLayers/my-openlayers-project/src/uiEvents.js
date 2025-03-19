import { searchComune } from './filters.js';
import { updateMapColors } from './comuniProcessor.js';
import { updateMapColorsNuclei } from './nucleiProcessor.js';
import { comuniLayer, nucleiLayer, defaultStyle } from './map.js';


export function setupMenuNavigation() {
    document.getElementById("btnDistance").addEventListener("click", function () {
        document.getElementById("controls").style.display = "block";  // Mostra il menu distanza
        document.getElementById("transportAnalysisControls").style.display = "none"; // Nasconde l'altro menu
    });

    document.getElementById("btnTransport").addEventListener("click", function () {
        document.getElementById("controls").style.display = "none"; // Nasconde il menu distanza
        document.getElementById("transportAnalysisControls").style.display = "block"; // Mostra il menu trasporto pubblico
    });
}

/**
 * 🔥 Inizializza gli eventi della UI
 */
export function setupUIEvents(comuneData, nucleiData) {
    
    document.getElementById('searchComune').addEventListener('keypress', function (event) {
        if (event.key === 'Enter') {  // Se l'utente preme Invio
            searchComune(map, comuniLayer, this.value);
        }
    });

    function checkFilters() {
        const educationFilter = document.getElementById('educationFilter').value;
        const modeFilter = document.getElementById('modeFilter').value;
        const extraFilterContainer = document.getElementById('extraFilterContainer');

        if (educationFilter && modeFilter) {  
            extraFilterContainer.style.display = "block";  // 🔥 Mostra il secondo menu solo se entrambi i filtri sono selezionati
        } else {
            extraFilterContainer.style.display = "none";   // ❌ Nasconde il secondo menu se manca uno dei due
        }
    }

    function checkFilters1() {
        const educationFilter = document.getElementById('educationFilter1').value;
        const extraFilterContainer = document.getElementById('extraFilterContainer1');

        if (educationFilter) {  
            extraFilterContainer.style.display = "block";  // 🔥 Mostra il secondo menu solo se entrambi i filtri sono selezionati
        } else {
            extraFilterContainer.style.display = "none";   // ❌ Nasconde il secondo menu se manca uno dei due
        }
    }

    document.getElementById('educationFilter').addEventListener('change', checkFilters);
    document.getElementById('modeFilter').addEventListener('change', checkFilters);
    document.getElementById('educationFilter1').addEventListener('change', checkFilters1);

    document.getElementById('resetFilters').addEventListener('click', function () {
        document.getElementById('educationFilter').value = "";
        document.getElementById('modeFilter').value = "";
        document.getElementById('extraFilter').value = "";
        document.getElementById('extraFilterContainer').style.display = "none";
        infoBox.style.display = "none";
        document.getElementById('color-bar-container').style.display = "none"; // 🔥 Nasconde la legenda
    
        comuniLayer.getSource().getFeatures().forEach(feature => {
            feature.setStyle(defaultStyle);
            let color = 'rgba(255, 255, 255, 0)';
            feature.set('originalColor', color);
        });
    
        
         // Imposta i layer iniziali
        nucleiLayer.setVisible(false); // ❌ Nuclei inizialmente nascosti
        comuniLayer.setVisible(true);  // 🔥 Mostrati di default
        document.querySelector('input[name="layer"][value="comuni"]').checked = true;
    
        console.log("🔄 Filtri resettati e mappa ripristinata!");
    });


    window.addEventListener('load', function () {
        console.log("🔄 Reset della mappa e dei filtri all'avvio!");
    
        // Resetta i filtri a "-- Seleziona --"
        document.getElementById('educationFilter').value = "";
        document.getElementById('modeFilter').value = "";
        document.getElementById('extraFilter').value = "";
    
        // Nasconde la seconda selezione e la legenda
        document.getElementById('extraFilterContainer').style.display = "none";
        document.getElementById('color-bar-container').style.display = "none";
    
        // Reset delle checkbox dei layer
        document.querySelector('input[name="layer"][value="comuni"]').checked = true;
    
        // Nasconde i nuclei, mostra i comuni
        nucleiLayer.setVisible(false);
        comuniLayer.setVisible(true);
    
        // Resetta i colori dei comuni
        comuniLayer.getSource().getFeatures().forEach(feature => {
            feature.setStyle(defaultStyle);
            let color = 'rgba(255, 255, 255, 0)'; // Colore originale
            feature.set('originalColor', color);
        });
    
        console.log("✅ Reset completato!");
    });
}
