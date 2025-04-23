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
        center: fromLonLat([12.5, 42.1]), // Lazio
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
            width: 2
        })
    })
});

// Aggiungi layer con i confini dei nuclei
export const nucleiLayer = new VectorLayer({
    source: new VectorSource({
        url: '/nucleos_Lazio.geojson', // Percorso corretto
        format: new GeoJSON()
    }),
    style: new Style({
        stroke: new Stroke({
            color: 'black', // Contorno nero per i nuclei
            width: 1
        })
    })
});

const comuneStyle = new Style({
    stroke: new Stroke({
        color: 'black',
        width: 2
    }),
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
        width: 2
    }),
});

// Applica gli stili ai layer
comuniLayer.setStyle(comuneStyle);
nucleiLayer.setStyle(nucleiStyle);

// Aggiungi i layer alla mappa
map.addLayer(comuniLayer);
map.addLayer(nucleiLayer);
