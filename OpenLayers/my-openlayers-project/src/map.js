import 'ol/ol.css';
import Map from 'ol/Map';
import View from 'ol/View';
import TileLayer from 'ol/layer/Tile';
import XYZ from 'ol/source/XYZ';
import VectorLayer from 'ol/layer/Vector';
import VectorSource from 'ol/source/Vector';
import GeoJSON from 'ol/format/GeoJSON';
import Stroke from 'ol/style/Stroke';
import Style from 'ol/style/Style';
import { fromLonLat } from 'ol/proj';
import Fill from 'ol/style/Fill';
import { romaLayer, perimetroRomaLayer } from './mapRoma.js';


// Creazione della mappa OpenLayers
export const map = new Map({
    target: 'map',
    layers: [
        new TileLayer({
            source: new XYZ({
                url: 'https://{a-c}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png'
            })
        })
    ],
    view: new View({
        center: fromLonLat([12.5, 42.1]),
        zoom: 8.5 
    })
});

// Aggiungi layer con i confini dei comuni del Lazio
export const comuniLayer = new VectorLayer({
    source: new VectorSource({
        url: '/comuniLazio.geojson', // Percorso corretto
        format: new GeoJSON()
    }),
    style: new Style({
        stroke: new Stroke({
            color: 'black', // Contorno nero per i comuni
            width: 1
        })
    })
});

// Aggiungi layer con i confini dei nuclei
export const nucleiLayer = new VectorLayer({
    source: new VectorSource({
        url: '/nucleos_Lazio.geojson',
        format: new GeoJSON()
    }),
    style: new Style({
        stroke: new Stroke({
            color: 'black',
            width: 1
        })
    }),
    visible: false // di default nascosto
});

const comuneStyle = new Style({
    stroke: new Stroke({
        color: 'black',
        width: 1
    }),
    fill: new Fill({
        color: 'rgba(255, 255, 255, 0.001)'  // quasi trasparente, ma interattivo!
    })
});

const nucleiStyle = new Style({
    stroke: new Stroke({
        color: 'black',
        width: 1
    }),
});

export const defaultStyle = new Style({
    stroke: new Stroke({
        color: 'black',
        width: 1
    }),
});

export const regioneLayer = new VectorLayer({
    source: new VectorSource({
        url: '/perimetroLazio.geojson',
        format: new GeoJSON()
    }),
    style: new Style({
        stroke: new Stroke({
            color: 'black',
            width: 4
        })
    })
});



// Applica gli stili ai layer
comuniLayer.setStyle(comuneStyle);
nucleiLayer.setStyle(nucleiStyle);

// Aggiungi i layer alla mappa
map.addLayer(comuniLayer);
//map.addLayer(nucleiLayer);
map.addLayer(regioneLayer);

map.addLayer(romaLayer);
map.addLayer(perimetroRomaLayer);
