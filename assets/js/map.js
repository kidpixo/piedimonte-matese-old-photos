document.addEventListener("DOMContentLoaded", function () {
    // Initialize the map
    var map = L.map("map", {
        center: [centerLat, centerLng],
        zoom: zoomLevel,
        zoomControl: true,
        preferCanvas: false,
    });
    // Let's lay down the base map, the canvas where our map artwork will unfold
    var tile_layer = L.tileLayer(
        "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
        {
            attribution: "Mixed by Kidpixo",
            detectRetina: false,
            maxNativeZoom: 19,
            maxZoom: 20,
            minZoom: 2,
            noWrap: false,
            opacity: 1,
            subdomains: "abc",
            tms: false,
        }
    );
    // Drop it like it's hot on our map
    tile_layer.addTo(map);
    tile_layer.options['layer_id'] = 'osm'

    // Add optional layers or controls
    if (typeof locateControlEnabled !== "undefined" && locateControlEnabled) {
        L.control.locate().addTo(map);
    }


var other_layer = L.tileLayer('https://tileserver.memomaps.de/tilegen/{z}/{x}/{y}.png', {
	maxZoom: 22,
	attribution: 'Map <a href="https://memomaps.de/">memomaps.de</a> <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, map data &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
});

other_layer.setOpacity(0.4);

var Stadia_AlidadeSatellite = L.tileLayer('https://tiles.stadiamaps.com/tiles/alidade_satellite/{z}/{x}/{y}{r}.{ext}', {
	minZoom: 0,
	maxZoom: 20,
	attribution: '&copy; CNES, Distribution Airbus DS, © Airbus DS, © PlanetObserver (Contains Copernicus Data) | &copy; <a href="https://www.stadiamaps.com/" target="_blank">Stadia Maps</a> &copy; <a href="https://openmaptiles.org/" target="_blank">OpenMapTiles</a> &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
	ext: 'jpg'
});

Stadia_AlidadeSatellite.setOpacity(0.4);
Stadia_AlidadeSatellite.addTo(map);

    var bingLayer = new L.TileLayer.Bing('Ai2nLg63EqcX4-3ZTWHmKNQbUkcsnEYuVJGlD8V0GC83idoO0u8cu7AzD-UOz5KV', {
        type: 'AerialWithLabels', // You can change the type to 'AerialWithLabels' or 'Road'
        maxNativeZoom: 18,
        maxZoom: 20,
    });
    // digidem/leaflet-bing-layer bug: options are ignored
    // opacity in creation is not working!
    // Adding the Bing Photo Layer to our map
    bingLayer.addTo(map);
    bingLayer.setOpacity(0.4);
    bingLayer.options['maxNativeZoom'] = 18;
    bingLayer.options['maxZoom'] = map.getMaxZoom();
    bingLayer.options['layer_id'] = 'bing';

    // build layers group
    // basemaps
    var baseMaps = { "OpenStreetMap": tile_layer, };
    // overlays, insert input range as title with ad-hoc IDs
    var overlayMaps = { 
        'bing': bingLayer,
        'Stadia Alidade Satellite': Stadia_AlidadeSatellite,
        'other layer': other_layer,
    };

    // create global control
    var layerControl = L.control.layers(baseMaps,
        overlayMaps,
        { "autoZIndex": true, "collapsed": false, "position": "topright" }
    ).addTo(map);

    // debub

    function filter_layer_id(layer_id) {
        for (let key in map._layers) {
            if (map._layers[key].options.layer_id == layer_id) {
                return map._layers[key]
            }
        }
    }

    function return_all_layer_id() {
        for (let key in map._layers) {
            if (map._layers[key].options.hasOwnProperty('layer_id')) {
                console.log(key, map._layers[key].options.layer_id);
            }
        }
    }


});