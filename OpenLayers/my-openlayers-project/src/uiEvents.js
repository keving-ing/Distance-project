import { searchComune } from './filters.js';
import { updateMapColors } from './comuniProcessor.js';
import { updateMapColorsNuclei } from './nucleiProcessor.js';
import { map, comuniLayer, nucleiLayer, defaultStyle, regioneLayer } from './map.js';
import { romaLayer, perimetroRomaLayer } from './mapRoma.js';
import { resetAll } from './utilities.js';
import { fromLonLat } from 'ol/proj';
import { loadTranslations, setLanguage, t } from './i18n.js';


export function setupMenuNavigation() {

    // Gestione pulsanti nella barra superiore
    document.getElementById("btnDistance").addEventListener("click", function () {
        resetAll();
        romaLayer.setVisible(false);
        perimetroRomaLayer.setVisible(false);
        comuniLayer.setVisible(true);
        regioneLayer.setVisible(true);
        map.getView().setCenter(fromLonLat([12.5, 42.1]));
        map.getView().setZoom(8.5)
        document.getElementById("controls").style.display = "block"; // ✅ Mostra EDUCAZIONE
    });

    document.getElementById("btnDistanceSalud").addEventListener("click", function () {
        resetAll();
        romaLayer.setVisible(false);
        perimetroRomaLayer.setVisible(false);
        comuniLayer.setVisible(true);
        regioneLayer.setVisible(true)
        map.getView().setCenter(fromLonLat([12.5, 42.1]));
        map.getView().setZoom(8.5)
        document.getElementById("healthAnalysisControls").style.display = "block"; // ✅ Mostra SALUTE
    });

    document.getElementById("btnTransport").addEventListener("click", function () {
        resetAll();
        document.getElementById("transportAnalysisControls").style.display = "block"; // ✅ Mostra TRASPORTI
        comuniLayer.setVisible(false);
        nucleiLayer.setVisible(false);
        regioneLayer.setVisible(false)
        romaLayer.setVisible(true);
        perimetroRomaLayer.setVisible(true);
        document.getElementById('transportAnalysisControls').style.display = "block";
        document.getElementById('controls').style.display = "none";
        document.getElementById('healthAnalysisControls').style.display = "none";

        // 🔍 Zoom sulla provincia di Roma
        romaLayer.getSource().on('change', function () {
    if (romaLayer.getSource().getState() === 'ready') {
        const extent = romaLayer.getSource().getExtent();
        if (!extent || extent.every(isNaN)) return;

       map.getView().fit(extent, {
            duration: 800,
            padding: [100, 50, 30, 50],  // TOP, RIGHT, BOTTOM, LEFT
            maxZoom: 11
        });
    }
});
    });
}


/**
 * 🔥 Inizializza gli eventi della UI
 */
export function setupUIEvents(comuneData, nucleiData) {

    document.getElementById("languageSelect").addEventListener("change", (e) => {
        setLanguage(e.target.value);
    });


    const settingsBtn = document.getElementById("settingsBtn");
    const settingsPanel = document.getElementById("settingsPanel");

    // Mostra/nasconde il pannello e chiude le sezioni
    settingsBtn.addEventListener("click", (event) => {
        event.stopPropagation();
        const isVisible = settingsPanel.style.display === "block";
        
        if (!isVisible) {
            // Chiude tutte le sezioni interne
            document.querySelectorAll(".accordion-content, .settings-section-content").forEach(section => {
                section.style.display = "none";
            });
        }

        settingsPanel.style.display = isVisible ? "none" : "block";
    });

    // Chiude il pannello cliccando fuori
    document.addEventListener("click", (event) => {
        const isClickInside = settingsPanel.contains(event.target) || settingsBtn.contains(event.target);
        if (!isClickInside) {
            settingsPanel.style.display = "none";
        }
    });

    // Toggle apertura/chiusura sezioni
    document.querySelectorAll(".accordion-header").forEach(header => {
        header.addEventListener("click", () => {
            const content = header.nextElementSibling;
            const isOpen = content.style.display === "block";

            // 🔁 Chiude tutte le sezioni
            document.querySelectorAll(".accordion-content, .settings-section-content").forEach(section => {
                section.style.display = "none";
            });

            // ✅ Se la sezione era chiusa, la riapre
            if (!isOpen) {
                content.style.display = "block";
            }
        });
    });

        
    document.getElementById('searchComune').addEventListener('keypress', function (event) {
        if (event.key === 'Enter') {  // Se l'utente preme Invio
            searchComune(map, comuniLayer, this.value);
        }
    });

    document.getElementById('searchComune1').addEventListener('keypress', function (event) {
        if (event.key === 'Enter') {  // Se l'utente preme Invio
            searchComune(map, comuniLayer, this.value);
        }
    });

    document.getElementById('searchComuneSalute').addEventListener('keypress', function (event) {
        if (event.key === 'Enter') {
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
        const tipoFilter = document.getElementById('tipo').value;
        const modalitaSelect = document.getElementById('modFilterContainer1');
        const educationSelect = document.getElementById('educationFilterContainer1');
        const education = document.getElementById('educationFilter1');
        const health = document.getElementById('healthFilter1');
        const mode = document.getElementById('modalita');
        const healthSelect = document.getElementById('healthFilterContainer1');
        const extraFilterContainer = document.getElementById('extraFilterContainer1');


        if (tipoFilter === "SA") {
            // EDUCAZIONE
            educationSelect.style.display = "block";

            if (education.value) {
                modalitaSelect.style.display = "block";

                if(mode.value){
                    extraFilterContainer.style.display = "block";
                }
            }

        } else if (tipoFilter === "ED") {
            
            healthSelect.style.display = "block";

            if (health.value) {
                modalitaSelect.style.display = "block";

                if(mode.value){
                    extraFilterContainer.style.display = "block";
                }
            }
    }
    }

    function checkHealthFilters() {
        const healthFilter = document.getElementById('healthFilter').value;
        const modeFilter = document.getElementById('healthModeFilter').value;
        const container = document.getElementById('extraHealthFilterContainer');
    
        if (healthFilter && modeFilter) {
            container.style.display = "block";
        } else {
            container.style.display = "none";
        }
    }

    document.getElementById('educationFilter').addEventListener('change', checkFilters);
    document.getElementById('modeFilter').addEventListener('change', checkFilters);
    document.getElementById('educationFilter1').addEventListener('change', checkFilters1);
    document.getElementById('healthFilter').addEventListener('change', checkHealthFilters);
    document.getElementById('healthModeFilter').addEventListener('change', checkHealthFilters);
    document.getElementById('healthFilter1').addEventListener('change', checkFilters1);
    document.getElementById('tipo').addEventListener('change', checkFilters1);
    document.getElementById('modalita').addEventListener('change', checkFilters1);

    document.getElementById('resetFilters').addEventListener('click', function () {
        document.getElementById('searchComune').value = "";
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

    document.getElementById('resetFilters1').addEventListener('click', function () {
        document.getElementById('searchComune1').value = "";
        document.getElementById('educationFilter1').value = "";
        document.getElementById('extraFilter1').value = "";
        document.getElementById('extraFilterContainer1').style.display = "none";
        infoBox.style.display = "none";
        document.getElementById('color-bar-container').style.display = "none"; // 🔥 Nasconde la legenda
    
        comuniLayer.getSource().getFeatures().forEach(feature => {
            feature.setStyle(defaultStyle);
            let color = 'rgba(255, 255, 255, 0)';
            feature.set('originalColor', color);
        });
   });

        document.getElementById('resetHealthFilters').addEventListener('click', function () {
            document.getElementById('searchComuneSalute').value = "";
            document.getElementById('healthFilter').value = "";
            document.getElementById('healthModeFilter').value = "";
            document.getElementById('extraHealthFilter').value = "";
            document.getElementById('extraHealthFilterContainer').style.display = "none";
            infoBox.style.display = "none";
            document.getElementById('color-bar-container').style.display = "none";

            comuniLayer.getSource().getFeatures().forEach(feature => {
                feature.setStyle(defaultStyle);
                let color = 'rgba(255, 255, 255, 0)';
                feature.set('originalColor', color);
            });

            nucleiLayer.setVisible(false);
            comuniLayer.setVisible(true);
            document.querySelector('input[name="layer"][value="comuni"]').checked = true;

            console.log("🔄 Filtri SALUTE resettati e mappa ripristinata!");
        });

    window.addEventListener('load', function () {
        console.log("🔄 Reset della mappa e dei filtri all'avvio!");
    
        // Resetta i filtri a "-- Seleziona --"
        document.getElementById('educationFilter').value = "";
        document.getElementById('educationFilter1').value = "";
        document.getElementById('modeFilter').value = "";
        document.getElementById('extraFilter').value = "";
        document.getElementById('extraFilter1').value = "";
    
        // Nasconde la seconda selezione e la legenda
        document.getElementById('extraFilterContainer').style.display = "none";
        document.getElementById('extraFilterContainer1').style.display = "none";
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

        document.getElementById('healthFilter').value = "";
        document.getElementById('healthModeFilter').value = "";
        document.getElementById('extraHealthFilter').value = "";
        document.getElementById('extraHealthFilterContainer').style.display = "none";
    
        console.log("✅ Reset completato!");
    });
}
