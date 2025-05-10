import 'ol/ol.css';
import VectorLayer from 'ol/layer/Vector';
import VectorSource from 'ol/source/Vector';
import GeoJSON from 'ol/format/GeoJSON';
import Stroke from 'ol/style/Stroke';
import Style from 'ol/style/Style';
import Fill from 'ol/style/Fill';

// ✅ Layer dei MUNICIPI di ROMA
export const romaLayer = new VectorLayer({
    source: new VectorSource({
        url: '/comuniRoma.geojson',
        format: new GeoJSON()
    }),
    style: new Style({
        stroke: new Stroke({
            color: 'black',
            width: 1
        }),
        fill: new Fill({
            color: 'rgba(255, 255, 255, 0.001)' // Trasparente ma interattivo
        })
    }),
    visible: false // nascosto di default
});

// ✅ Layer del PERIMETRO ESTERNO di ROMA
export const perimetroRomaLayer = new VectorLayer({
    source: new VectorSource({
        url: '/perimetroRoma.geojson',
        format: new GeoJSON()
    }),
    style: new Style({
        stroke: new Stroke({
            color: 'black',
            width: 4
        }),
        fill: new Fill({
            color: 'rgba(255, 0, 0, 0.05)' // Leggero riempimento rosso chiaro
        })
    }),
    visible: false // nascosto di default
});
