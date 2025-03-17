/**
 * Cerca un comune e zooma su di esso.
 * @param {ol.Map} map - La mappa di OpenLayers
 * @param {ol.layer.Vector} comuniLayer - Il layer dei comuni
 * @param {string} searchText - Il testo cercato dall'utente
 */
export function searchComune(map, comuniLayer, searchText) {
    searchText = searchText.trim().toLowerCase();

    let foundFeature = null;

    comuniLayer.getSource().getFeatures().forEach(feature => {
        const nomeComune = feature.get('COMUNE').trim().toLowerCase(); 

        if (nomeComune === searchText) {  // Verifica corrispondenza esatta
            foundFeature = feature;
        }
    });

    if (foundFeature) {
        const extent = foundFeature.getGeometry().getExtent();
        map.getView().fit(extent, { duration: 1000, padding: [50, 50, 50, 50] });
    } else {
        alert("Comune non trovato! Assicurati di scrivere il nome esatto.");
    }
}


