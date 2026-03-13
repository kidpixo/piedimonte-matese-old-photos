// Constants and configuration for the map and layers
// Use window.location.origin for local dev to avoid CORS issues with 0.0.0.0 vs localhost
// Use base_url from template for production
const BASE_URL = (window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1")
  ? window.location.origin + "/assets/maps_data/"
  : base_url + "/assets/maps_data/";

// Layer configuration: defines all options for each layer
const LAYER_CONFIG = {
    OSM: {
        id: "osm",
        type: "basemap",
        name: "OpenStreetMap",
        url: "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
        attribution: "Mixed by Kidpixo",
        opacity: 1,
        visible: true,
        layerType: "tile",
        showInControl: false,
        extraOptions: { 
            maxNativeZoom: 19, 
            maxZoom: 23 
        }
    },
    // BING: {
    //     id: "bing",
    //     type: "overlay",
    //     name: "Bing",
    //     url: "BING_API_KEY_HERE", // Replace with your Bing API key or comment out to disable
    //     opacity: 0.4,
    //     slider: true,
    //     visible: true,
    //     layerType: "bing"
    // },
    ESRI: {
        id: "esri",
        type: "overlay",
        name: "Esri",
        url: "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attribution: 'Powered by [Esri](https://www.esri.com)',
        opacity: 1.0,
        slider: true,
        visible: true,
        layerType: "tile",
        showInControl: true,
        extraOptions: { 
            maxNativeZoom: 20, 
            maxZoom: 23 
        }
        },
    RASTER_1884: {
        id: "1884",
        type: "overlay",
        name: "1884",
        year: "1884",
        url: BASE_URL + "COG_1884.jpeg-band.tif",
        opacity: 0.7,
        slider: true,
        visible: true,
        layerType: "georaster",
        extraOptions: { resolution: 256 },
        showInControl: true
    },
    RASTER_1940: {
        id: "1940",
        type: "overlay",
        name: "1940",
        year: "1940",
        url: BASE_URL + "COG_1940.tif",
        opacity: 0.7,
        slider: true,
        visible: true,
        layerType: "georaster",
        extraOptions: { resolution: 256},
        showInControl: true,
        grayscale: true
    },
    RASTER_1964: {
        id: "1964",
        type: "overlay",
        name: "1964",
        year: "1964",
        url: BASE_URL + "COG_1964.tif",
        opacity: 0.7,
        slider: true,
        visible: true,
        layerType: "georaster",
        extraOptions: { resolution: 256},
        showInControl: true
    },
       RASTER_1970: {
        id: "1970",
        type: "overlay",
        name: "1970",
        year: "1970",
        url: BASE_URL + "COG_1970.jpeg-band.tif",
        opacity: 0.7,
        slider: true,
        visible: true,
        layerType: "georaster",
        extraOptions: { resolution: 256},
        showInControl: true,
        grayscale: true
    },
   SOTTERRANEO: {
        id: "sotterraneo",
        type: "overlay",
        name: "sotterraneo",
        url: BASE_URL + 'Mappa_cut_modified.png',
        opacity: 0.8,
        slider: true,
        visible: true,
        layerType: "image",
        imageBounds: [
            [41.35386391721536, 14.371526891622073],
            [41.354430965215357, 14.371859023622073]
        ],
        showInControl: true
    },
    FOTO: {
        id: "foto",
        type: "overlay",
        name: "foto",
        url: BASE_URL + 'photos_origin.geojson',
        slider: false,
        visible: true,
        layerType: "geojson",
        showInControl: true,
        style: {
            pointToLayer: function(feature, latlng) {
                return L.circleMarker(latlng, {
                    radius: 8,
                    fillColor: "#e74c3c", // Red fill
                    color: "#c0392b",     // Dark red border
                    weight: 2,
                    opacity: 1,
                    fillOpacity: 0.9
                });
            }
        }
    },
    FOTO_FOV: {
        id: "foto_fov",
        type: "overlay",
        name: "foto_fov",
        url: BASE_URL + 'photos_fov.geojson',
        opacity: 0.8,
        slider: true,
        visible: true,
        layerType: "geojson",
        showInControl: true,
        style: {
            style: {
                fillColor: "hsl(190, 80%, 50%)", // light blue fill
                fillOpacity: 0.5,
                stroke: false,        // No border
                weight: 0
            }
        }
    },
    FOTO_LINE: {
        id: "foto_line",
        type: "overlay",
        name: "foto_line",
        url: BASE_URL + 'photos_lov.geojson',
        slider: true,
        visible: true,
        layerType: "geojson",
        showInControl: true,
        style: {
            style: {
                color: "#e74c3c", // Red line
                weight: 4,
                opacity: 1
            },            
            // Usage in onEachFeature:
            onEachFeature: function(feature, layer) {
                if (layer instanceof L.Polyline) {
                    layer.on("add", function() {
                        requestAnimationFrame(() => addArrowhead(layer, { color: "#e74c3c", size: 10 }));
                    });
                    layers.map.on("zoomend moveend", () => addArrowhead(layer, { color: "#e74c3c", size: 10 }));
                }
                }
            }
    },
    // Add more as needed, or comment out to disable
    PHOTO_ORIGIN: {
        id: "photo_origin",
        type: "overlay",
        name: "Photo Origin",
        visible: false,
        layerType: "geojson",
        showInControl: true,
        style: {
            pointToLayer: function(feature, latlng) {
                return L.circleMarker(latlng, {
                    radius: 8,
                    fillColor: "#e74c3c",
                    color: "#c0392b",
                    weight: 2,
                    opacity: 1,
                    fillOpacity: 0.9
                });
            }
        }
    },
    PHOTO_FOV: {
        id: "photo_fov",
        type: "overlay",
        name: "Photo FOV",
        visible: false,
        layerType: "geojson",
        showInControl: true,
        style: {
            style: {
                fillColor: "hsl(190, 80%, 50%)", // light blue fill
                fillOpacity: 0.5,
                stroke: false,        // No border
                weight: 0
            }
        }
     },
    PHOTO_LINE: {
        id: "photo_line",
        type: "overlay",
        name: "Photo Line",
        visible: false,
        layerType: "geojson",
        showInControl: true,
        style: {
            style: {
                color: "#e74c3c", // Red line
                weight: 4,
                opacity: 1
            },            
            // Usage in onEachFeature:
            onEachFeature: function(feature, layer) {
                if (layer instanceof L.Polyline) {
                    layer.on("add", function() {
                        requestAnimationFrame(() => addArrowhead(layer, { color: "#e74c3c", size: 10 }));
                    });
                    layers.map.on("zoomend moveend", () => addArrowhead(layer, { color: "#e74c3c", size: 10 }));
                }
                }
            }    }
};

// Global object to store all map layers for easy access
let layers = {};

// Main initialization function: sets up the map and all layers/controls
async function initMap() {
    createMap(); // Create the Leaflet map instance
    addBasemaps(); // Add base map layers (OSM, Bing, Esri)
    await addRasterLayers(); // Wait for rasters to load
    await addPhotoLayers(); // Add photo origin points as GeoJSON (now awaited)
    addImageOverlays(); // Add PNG image overlay (underground)
    await addIndividualGeoJsonLayers(); // Add individual photo layers if present
    addLayerControls(); // Add layer switcher and overlay controls (after all layers are added)
    setupOpacityControls(); // Add opacity sliders for layers
    setupCustomControls(); // Add custom controls (e.g., reset zoom)
}

// --- URL PARAMS HANDLING ---
(function handleUrlParams() {
    const params = new URLSearchParams(window.location.search);
    const layersParam = params.get('layers');
    let layersFromFrontmatter = Array.isArray(window.activeLayers) ? window.activeLayers : [];
        // Set all overlays (except basemaps) to not visible
        for (const key in LAYER_CONFIG) {
            const cfg = LAYER_CONFIG[key];
            if (cfg.type === 'overlay') {
                cfg.visible = false;
            }
        }
        // Activate overlays from URL or frontmatter
        let activeList = [];
        if (layersParam) {
            activeList = layersParam.split(',').map(x => x.trim());
        } else if (layersFromFrontmatter.length > 0) {
            activeList = layersFromFrontmatter.map(x => String(x).trim());
        }
        activeList.forEach(name => {
            for (const key in LAYER_CONFIG) {
                if (LAYER_CONFIG[key].type === 'overlay' && LAYER_CONFIG[key].name.toLowerCase() === name.toLowerCase()) {
                    LAYER_CONFIG[key].visible = true;
                }
            }
        });
    // Center: ?center=lat,lng
    const centerParam = params.get('center');
    if (centerParam) {
        const [lat, lng] = centerParam.split(',').map(Number);
        if (!isNaN(lat) && !isNaN(lng)) {
            window._mapCenterOverride = [lat, lng];
        }
    }
    // Zoom: ?zoom=18
    const zoomParam = params.get('zoom');
    if (zoomParam && !isNaN(parseInt(zoomParam))) {
        window._mapZoomOverride = parseInt(zoomParam);
    }
})();

// Create the Leaflet map and add geolocation control
function createMap() {
    layers.map = L.map("map", {
        center: window._mapCenterOverride || [centerLat || 41.35512154669242, centerLng || 14.372210047410501],
        zoom: window._mapZoomOverride || zoomLevel || 17,        maxZoom: 23,
        zoomControl: true,
        preferCanvas: false,
    });
    L.control.locate().addTo(layers.map); // Add geolocate user button

    // Add right-click context menu to show coordinates in a popup
    layers.map.on("contextmenu", function (event) {
        L.popup()
            .setLatLng(event.latlng)
            .setContent("Coordinates:<br>" + event.latlng.lat.toFixed(6) + ", " + event.latlng.lng.toFixed(6))
            .openOn(layers.map);
    });
}

// Add base map layers: OSM, Bing, Esri
function addBasemaps() {
    for (const key in LAYER_CONFIG) {
        const cfg = LAYER_CONFIG[key];
        if (!cfg.visible || cfg.type !== 'basemap') continue;
        if (cfg.layerType === 'tile') {
            layers[cfg.id] = L.tileLayer(cfg.url, {
                attribution: cfg.attribution,
                opacity: cfg.opacity ?? 1,
                maxZoom: layers.map.options.maxZoom,
                ...cfg.extraOptions
            }).addTo(layers.map);
            layers[cfg.id].options['layer_id'] = cfg.id;
        }
        // Add more basemap types as needed
    }
    // Add overlays that are actually basemap-like (e.g. Bing, Esri) as overlays but not as basemaps
    for (const key in LAYER_CONFIG) {
        const cfg = LAYER_CONFIG[key];
        if (!cfg.visible || cfg.type !== 'overlay') continue;
        if (cfg.layerType === 'tile' || cfg.layerType === 'bing') {
            if (cfg.layerType === 'bing') {
                if (typeof L.TileLayer.Bing !== 'undefined') {
                    layers[cfg.id] = new L.TileLayer.Bing(cfg.url, {
                        type: 'AerialWithLabels',
                        opacity: cfg.opacity ?? 1,
                        maxZoom: layers.map.options.maxZoom,
                        ...cfg.extraOptions
                    }).addTo(layers.map);
                    layers[cfg.id].setOpacity(cfg.opacity ?? 1);
                    layers[cfg.id].options['layer_id'] = cfg.id;
                }
            } else {
                layers[cfg.id] = L.tileLayer(cfg.url, {
                    attribution: cfg.attribution,
                    opacity: cfg.opacity ?? 1,
                    maxZoom: layers.map.options.maxZoom,
                    ...cfg.extraOptions
                }).addTo(layers.map);
                layers[cfg.id].options['layer_id'] = cfg.id;
            }
        }
    }
}

async function addRasterLayers() {
    for (const key in LAYER_CONFIG) {
        const cfg = LAYER_CONFIG[key];
        if (!cfg.visible || cfg.layerType !== 'georaster') continue;
        const georaster = await parseGeoraster(cfg.url, {'resampleMethod':'nearest'});
        let options = {
            debugLevel: 0,
            georaster: georaster,
            opacity: cfg.opacity ?? 1,
            ...cfg.extraOptions
        };
        if (cfg.grayscale) {
            options.pixelValuesToColorFn = values => {
                const v = values[0];
                if (v === 0 || v === undefined) return null;
                return `rgb(${v},${v},${v})`;
            };
        }
        layers[cfg.id] = new GeoRasterLayer(options).addTo(layers.map);
        layers[cfg.id].options['layer_id'] = cfg.id;
    }
}

// Add PNG image overlay (underground map)
function addImageOverlays() {
    for (const key in LAYER_CONFIG) {
        const cfg = LAYER_CONFIG[key];
        if (!cfg.visible || cfg.layerType !== 'image') continue;
        try {
            layers[cfg.id] = L.imageOverlay(cfg.url, cfg.imageBounds, { opacity: cfg.opacity ?? 1 });
            layers[cfg.id].options['layer_id'] = cfg.id;
            layers[cfg.id].addTo(layers.map);
        } catch (error) {
            console.error(`Error adding image overlay for ${cfg.id}:`, error);
        }
    }
}

// Add layer switcher and overlay controls
function addLayerControls() {
    setTimeout(() => {
        let baseMaps = {};
        let overlayMaps = {};
        for (const key in LAYER_CONFIG) {
            const cfg = LAYER_CONFIG[key];
            const layer = layers[cfg.id];
            if (!layer) continue;
            if (cfg.showInControl === false) continue;
            if (cfg.type === 'basemap') {
                baseMaps[cfg.name] = layer;
            } else if (cfg.type === 'overlay') {
                if (cfg.slider) {
                    overlayMaps[`${cfg.name}<input type=\"range\" id=\"opacity-slider-${cfg.id}\" class=\"opacity-slider\" min=\"0\" max=\"1\" step=\"0.1\" value=\"${cfg.opacity ?? 1}\" />`] = layer;
                } else {
                    overlayMaps[cfg.name] = layer;
                }
            }
        }
        if (layers.layerControl) {
            layers.map.removeControl(layers.layerControl);
        }
        layers.layerControl = L.control.layers(baseMaps, overlayMaps, {"autoZIndex": true, "collapsed": true, "position": "topright"}).addTo(layers.map);
    }, 500);
}

// Add event listeners for opacity sliders for each layer
function setupOpacityControls() {
    setTimeout(() => {
        for (const key in LAYER_CONFIG) {
            const cfg = LAYER_CONFIG[key];
            if (!cfg.slider) continue;
            const el = document.querySelector(`#opacity-slider-${cfg.id}`);
            const layer = layers[cfg.id];
            if (el && layer) {
                el.addEventListener('input', debounce((e) => {
                    const opacity = e.target.value;
                    // Use method detection for opacity change
                    if (typeof layer.setStyle === "function") {
                        layer.setStyle({ fillOpacity: opacity, opacity: opacity });
                    } else if (typeof layer.setOpacity === "function") {
                        layer.setOpacity(opacity);
                    }
                }, 50));
            }
        }
    }, 700);
}

// Add a custom control (reset zoom button)
function setupCustomControls() {
    const control = new L.Control({ position: 'topleft' });
    control.onAdd = function(map) {
        const azoom = L.DomUtil.create('a', 'mt-0');
        azoom.innerHTML = `<div class="leaflet-control-zoom leaflet-bar leaflet-control mt-0 ms-0"><a class="leaflet-control-reset-zoom" title="Reset zoom" role="button" aria-label="Reset zoom">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-house" viewBox="0 0 16 16">
            <path fill-rule="evenodd" d="M2 13.5V7h1v6.5a.5.5 0 0 0 .5.5h9a.5.5 0 0 0 .5-.5V7h1v6.5a1.5 1.5 0 0 1-1.5 1.5h-9A1.5 1.5 0 0 1 2 13.5zm11-11V6l-2-2V2.5a.5.5 0 0 1 .5-.5h1a.5.5 0 0 1 .5.5z"/>
            <path fill-rule="evenodd" d="M7.293 1.5a1 1 0 0 1 1.414 0l6.647 6.646a.5.5 0 0 1-.708.708L8 2.207 1.354 8.854a.5.5 0 1 1-.708-.708L7.293 1.5z"/>
            </svg></a></div>`;
        L.DomEvent
            .disableClickPropagation(azoom)
            .on(azoom, 'click', () => {
                layers.map.setView(layers.map.options.center, layers.map.options.zoom);
            });
        return azoom;
    };
    control.addTo(layers.map);
}

// Add photo origin points as a GeoJSON layer : use layer style config if present, and bind popups with photo thumbnails
async function addPhotoLayers() {
    const promises = [];
    for (const key in LAYER_CONFIG) {
        const cfg = LAYER_CONFIG[key];
        if (!cfg.visible || cfg.layerType !== 'geojson') continue;

        const promise = new Promise((resolve, reject) => {
            getJSON(cfg.url, (geojson) => {
                try {
                    const geoJsonOptions = cfg.style ? { ...cfg.style } : {};
                    const configOnEachFeature = geoJsonOptions.onEachFeature;

                    geoJsonOptions.onEachFeature = (feature, layer) => {
                        // keep layer-specific behavior (e.g. arrowheads)
                        if (typeof configOnEachFeature === "function") {
                            configOnEachFeature(feature, layer);
                        }

                        // add popup only when properties exist
                        const props = feature?.properties || {};
                        if (props.text && props.filename) {
                            const text = String(props.text).replace(/['"]+/g, "");
                            const filename = String(props.filename);
                            const popupContent = `<div><h2>${text}</h2><a href="${BASE_URL}photos/${filename}" target="_blank" rel="noopener noreferrer">original` +
                                (filename.includes(".webm")
                                    ? `<video controls id="markers_popup_photos" src="${BASE_URL}assets/thumbs/${filename}" alt="${filename}"></video>`
                                    : `<img id="markers_popup_photos" src="${BASE_URL}assets/thumbs/${filename}" alt="${filename}">`) +
                                "</a></div>";
                            layer.bindPopup(popupContent, { maxWidth: "auto" });
                        }
                    };

                    layers[cfg.id] = L.geoJSON(geojson, geoJsonOptions).addTo(layers.map);
                    layers[cfg.id].options["layer_id"] = cfg.id;
                    resolve();
                } catch (error) {
                    console.error(`Error adding photo layer for ${cfg.id}:`, error);
                    reject(error);
                }
            });
        });

        promises.push(promise);
    }

    return Promise.all(promises);
}

/// --- Timeline Slider ---
function createTimelineSlider() {
    // Only use overlays that are currently visible and have a year
    const years = Object.values(LAYER_CONFIG)
        .filter(cfg => cfg.type === 'overlay' && cfg.year && cfg.visible)
        .map(cfg => parseInt(cfg.year))
        .filter(y => !isNaN(y))
        .sort((a, b) => a - b);
    if (years.length < 2) return; // Need at least 2 visible layers with year

    if (layers.timelineControl) {
        layers.map.removeControl(layers.timelineControl);
        layers.timelineControl = null;
    }

    const TimelineControl = L.Control.extend({
        options: {
            position: 'bottomleft'
        },

        onAdd: function(map) {
            const expandedWidth = '90%';

            const bottomLeftCorner = map._controlCorners && map._controlCorners.bottomleft;
            if (bottomLeftCorner) {
                this._previousBottomLeftStyle = {
                    width: bottomLeftCorner.style.width,
                    display: bottomLeftCorner.style.display,
                    justifyContent: bottomLeftCorner.style.justifyContent,
                    pointerEvents: bottomLeftCorner.style.pointerEvents
                };
                bottomLeftCorner.style.width = '100%';
                bottomLeftCorner.style.display = 'flex';
                bottomLeftCorner.style.justifyContent = 'flex-start';
                bottomLeftCorner.style.pointerEvents = 'none';
            }

            // Main control wrapper
            const collapsibleControl = L.DomUtil.create('div', 'leaflet-control leaflet-bar');
            collapsibleControl.style.pointerEvents = 'auto';
            collapsibleControl.style.width = expandedWidth;
            collapsibleControl.style.border = '1px solid #bbb';
            collapsibleControl.style.borderRadius = '8px';
            collapsibleControl.style.background = 'rgba(255,255,255,0.3)';
            collapsibleControl.style.display = 'flex';
            collapsibleControl.style.flexDirection = 'row';
            collapsibleControl.style.alignItems = 'stretch';
            collapsibleControl.style.textAlign = 'center';
            collapsibleControl.style.marginBottom = '12px'; // more gap from map bottom

            // Slider content container
            const sliderContainer = L.DomUtil.create('div', 'w-100 px-4 pb-2', collapsibleControl);
            sliderContainer.id = 'timeline-slider-container';
            sliderContainer.style.display = 'flex';
            sliderContainer.style.flexDirection = 'column';
            sliderContainer.style.justifyContent = 'center';
            sliderContainer.style.alignItems = 'center';
            sliderContainer.style.background = 'none';
            sliderContainer.style.borderRadius = '8px';

            // Create year labels
            const labelRow = L.DomUtil.create('div', 'px-3 pb-1 d-flex justify-content-between mx-auto', sliderContainer);
            labelRow.style.position = 'relative';
            labelRow.style.marginBottom = '4px';
            labelRow.style.width = '100%';
            labelRow.style.maxWidth = '100%';
            labelRow.style.marginBottom = '2px';

            years.forEach((year) => {
                const lbl = L.DomUtil.create('span', '', labelRow);
                lbl.innerText = year;
                lbl.style.fontSize = '1.25em';
                lbl.style.color = '#222';
                lbl.style.fontWeight = 'bold';
                lbl.style.textShadow = '0 0 8px #fff, 0 0 2px #fff, 0 0 1px #fff';
                lbl.style.padding = '2px 6px';
                lbl.style.borderRadius = '4px';
                lbl.style.padding = '1px 4px';
            });

            // Create slider input
            const slider = L.DomUtil.create('input', 'form-range', sliderContainer);
            slider.type = 'range';
            slider.id = 'timeline-slider';
            slider.min = 0;
            slider.max = years.length - 1;
            slider.step = '0.01';
            slider.value = 0;
            slider.style.margin = '0 auto';
            slider.style.width = '100%';

            // Create timeline controls as native Leaflet-style bar buttons
            const transportBar = L.DomUtil.create('div', 'leaflet-bar');
            transportBar.style.display = 'flex';

            const playBtn = L.DomUtil.create('a', 'leaflet-bar-part', transportBar);
            playBtn.id = 'timeline-play-btn';
            playBtn.href = '#';
            playBtn.setAttribute('role', 'button');
            playBtn.setAttribute('aria-label', 'Play timeline');
            playBtn.innerHTML = '&#9654;';
            playBtn.title = 'Play timeline';
            playBtn.style.width = '32px';
            playBtn.style.textAlign = 'center';

            const loopBtn = L.DomUtil.create('a', 'leaflet-bar-part', transportBar);
            loopBtn.href = '#';
            loopBtn.setAttribute('role', 'button');
            loopBtn.setAttribute('aria-label', 'Toggle loop playback');
            loopBtn.title = 'Loop playback';
            loopBtn.textContent = '∞';
            loopBtn.style.width = '32px';
            loopBtn.style.textAlign = 'center';

            const speedBtn = L.DomUtil.create('a', 'leaflet-bar-part', transportBar);
            speedBtn.href = '#';
            speedBtn.setAttribute('role', 'button');
            speedBtn.setAttribute('aria-label', 'Toggle playback speed');
            speedBtn.title = 'Fast playback';
            speedBtn.textContent = '1x';
            speedBtn.style.minWidth = '36px';
            speedBtn.style.textAlign = 'center';

            const reverseBtn = L.DomUtil.create('a', 'leaflet-bar-part', transportBar);
            reverseBtn.href = '#';
            reverseBtn.setAttribute('role', 'button');
            reverseBtn.setAttribute('aria-label', 'Toggle reverse playback');
            reverseBtn.title = 'Reverse playback';
            reverseBtn.textContent = '⇄';
            reverseBtn.style.width = '32px';
            reverseBtn.style.textAlign = 'center';

            // Controls row
            const controlsRow = L.DomUtil.create('div', '', sliderContainer);
            controlsRow.style.display = 'flex';
            controlsRow.style.flexDirection = 'row';
            controlsRow.style.justifyContent = 'center';
            controlsRow.style.alignItems = 'center';
            controlsRow.style.width = '60%';
            controlsRow.style.margin = '8px auto 0 auto';
            controlsRow.appendChild(transportBar);

            // Toggle button (collapse)
            const toggleBtn = L.DomUtil.create('a', 'leaflet-bar-part leaflet-bar-part-single timeline-toggle-btn', collapsibleControl);
            toggleBtn.href = '#';
            toggleBtn.setAttribute('role', 'button');
            toggleBtn.setAttribute('aria-label', 'Toggle timeline controls');
            toggleBtn.title = 'Collapse timeline controls';
            toggleBtn.innerHTML = '«'; // fixed icon, state via title/aria
;
            collapsibleControl.insertBefore(toggleBtn, sliderContainer);

            function applyTimelineOpacity(val) {
                const i = Math.floor(val);
                const frac = val - i;
                years.forEach((year, idx) => {
                    const layerKey = Object.keys(LAYER_CONFIG).find(k => LAYER_CONFIG[k].year && parseInt(LAYER_CONFIG[k].year) === year);
                    if (!layerKey) return;
                    const layerObj = layers[LAYER_CONFIG[layerKey].id];
                    if (!layerObj) return;
                    let opacity = 0;
                    if (idx === i) {
                        opacity = 1 - frac;
                    } else if (idx === i + 1) {
                        opacity = frac;
                    }
                    layerObj.setOpacity(opacity);
                    LAYER_CONFIG[layerKey].opacity = opacity;
                    const sliderEl = document.querySelector(`#opacity-slider-${LAYER_CONFIG[layerKey].id}`);
                    if (sliderEl) sliderEl.value = opacity;
                    const checkbox = document.querySelector(`input.leaflet-control-layers-selector[type='checkbox'][data-layerid='${LAYER_CONFIG[layerKey].id}']`);
                    if (checkbox && !checkbox.checked) checkbox.checked = true;
                });
            }

            // Timeline slider movement
            slider.addEventListener('input', function(e) {
                const val = parseFloat(e.target.value);
                applyTimelineOpacity(val);
            });

            // Play logic
            let playing = false;
            let playInterval = null;
            let currentStep = 0;
            let loopEnabled = true;
            let fastEnabled = false;
            let reverseEnabled = false;
            const stepsPerLabel = 20;
            const totalSteps = (years.length - 1) * stepsPerLabel;
            const baseStepTime = 3000 / stepsPerLabel;
            const fastStepTime = baseStepTime / 4;

            function setModeButtonState(button, enabled) {
                button.style.backgroundColor = enabled ? '#e9f2ff' : '';
                button.style.fontWeight = enabled ? 'bold' : 'normal';
            }

            setModeButtonState(loopBtn, loopEnabled);
            setModeButtonState(speedBtn, fastEnabled);
            setModeButtonState(reverseBtn, reverseEnabled);

            function getDirection() {
                return reverseEnabled ? -1 : 1;
            }
            function getLoop() {
                return loopEnabled;
            }
            function getSpeed() {
                return fastEnabled ? fastStepTime : baseStepTime;
            }
            function setPlaying(state) {
                playing = state;
                playBtn.innerHTML = state ? '&#9632;' : '&#9654;';
                playBtn.title = state ? 'Stop timeline' : 'Play timeline';
            }
            function stopTimeline() {
                setPlaying(false);
                if (playInterval) clearTimeout(playInterval);
                playInterval = null;
            }
            function playTimeline() {
                if (playing) return;
                setPlaying(true);
                let direction = getDirection();
                let loop = getLoop();
                let speed = getSpeed();
                const min = 0;
                const max = totalSteps;
                currentStep = Math.round(parseFloat(slider.value) * stepsPerLabel);

                function step() {
                    direction = getDirection();
                    loop = getLoop();
                    speed = getSpeed();

                    if (currentStep < min) currentStep = min;
                    if (currentStep > max) currentStep = max;

                    const sliderValue = (currentStep / stepsPerLabel).toFixed(2);
                    slider.value = sliderValue;
                    applyTimelineOpacity(parseFloat(sliderValue));
                    currentStep += direction;

                    if (currentStep < min || currentStep > max) {
                        if (loop) {
                            currentStep = direction === -1 ? max : min;
                        } else {
                            stopTimeline();
                            return;
                        }
                    }
                    playInterval = setTimeout(step, speed);
                }

                playInterval = setTimeout(step, speed);
            }

            L.DomEvent.on(playBtn, 'click', function(e) {
                L.DomEvent.preventDefault(e);
                if (playing) {
                    stopTimeline();
                } else {
                    playTimeline();
                }
            });

            [
                {
                    button: loopBtn,
                    toggle: () => {
                        loopEnabled = !loopEnabled;
                        setModeButtonState(loopBtn, loopEnabled);
                    }
                },
                {
                    button: speedBtn,
                    toggle: () => {
                        fastEnabled = !fastEnabled;
                        speedBtn.textContent = fastEnabled ? '2x' : '1x';
                        setModeButtonState(speedBtn, fastEnabled);
                    }
                },
                {
                    button: reverseBtn,
                    toggle: () => {
                        reverseEnabled = !reverseEnabled;
                        setModeButtonState(reverseBtn, reverseEnabled);
                    }
                }
            ].forEach(ctrl => {
                L.DomEvent.on(ctrl.button, 'click', function(e) {
                    L.DomEvent.preventDefault(e);
                    ctrl.toggle();
                    if (playing) {
                        stopTimeline();
                        playTimeline();
                    }
                });
            });

            // Toggle collapse/expand state
            let collapsed = false;
            L.DomEvent.on(toggleBtn, 'click', function(e) {
                L.DomEvent.preventDefault(e);
                collapsed = !collapsed;
                if (collapsed) {
                    sliderContainer.style.display = 'none';
                    collapsibleControl.style.width = 'auto';
                    collapsibleControl.style.justifyContent = 'flex-start';
                } else {
                    sliderContainer.style.display = 'flex';
                    collapsibleControl.style.width = expandedWidth;
                    collapsibleControl.style.justifyContent = '';
                }
                toggleBtn.innerHTML = collapsed ? '◷' : '«';
                toggleBtn.title = collapsed ? 'Expand timeline controls' : 'Collapse timeline controls';
            });

            // Keep map interactions isolated from control interactions
            L.DomEvent.disableClickPropagation(collapsibleControl);
            L.DomEvent.disableScrollPropagation(collapsibleControl);

            this._stopTimeline = stopTimeline;
            return collapsibleControl;
        },

        onRemove: function() {
            if (typeof this._stopTimeline === 'function') {
                this._stopTimeline();
            }
            const bottomLeftCorner = layers.map && layers.map._controlCorners && layers.map._controlCorners.bottomleft;
            if (bottomLeftCorner && this._previousBottomLeftStyle) {
                bottomLeftCorner.style.width = this._previousBottomLeftStyle.width;
                bottomLeftCorner.style.display = this._previousBottomLeftStyle.display;
                bottomLeftCorner.style.justifyContent = this._previousBottomLeftStyle.justifyContent;
                bottomLeftCorner.style.pointerEvents = this._previousBottomLeftStyle.pointerEvents;
            }
        }
    });

    layers.timelineControl = new TimelineControl();
    layers.timelineControl.addTo(layers.map);
}

// Patch: add data-layerid to checkboxes after layer control is created
function patchLayerControlCheckboxes() {
    setTimeout(() => {
        const selectors = document.querySelectorAll('.leaflet-control-layers-selector[type="checkbox"]');
        selectors.forEach(cb => {
            const label = cb.parentElement.textContent;
            for (const key in LAYER_CONFIG) {
                if (label.includes(LAYER_CONFIG[key].name)) {
                    cb.setAttribute('data-layerid', LAYER_CONFIG[key].id);
                }
            }
        });
    }, 1000);
}

// Utility: debounce function for performance
const debounce = (func, wait) => {
    let timeout;
    return (...args) => {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), wait);
    };
};

// Utility: fetch JSON data from a URL
const getJSON = (url, cb) => {
    fetch(url)
        .then(response => response.json())
        .then(result => cb(result))
        .catch(error => console.error(error));
}

// Utility: return a style object with custom fill opacity
const new_style = (opacity) => ({ "fillOpacity": opacity });

// Utility: find a layer by its custom layer_id
function filter_layer_id(layer_id) {
    for (let key in layers.map._layers) {
        if (layers.map._layers[key].options.layer_id == layer_id) {
            return layers.map._layers[key];
        }
    }
}

// Utility: log all layer IDs in the map (for debugging)
function return_all_layer_id() {
    for (let key in layers.map._layers) {
        if (layers.map._layers[key].options.hasOwnProperty('layer_id')) {
            console.log(key, layers.map._layers[key].options.layer_id);
        }
    }
}

// Add individual photo GeoJSON layers if variables are present
async function addIndividualGeoJsonLayers() {
    // Origin Point
    if (typeof window.photoOriginGeoJson === 'object' && window.photoOriginGeoJson) {
        try {
            layers.photo_origin = L.geoJSON(window.photoOriginGeoJson, {
                pointToLayer: LAYER_CONFIG.PHOTO_ORIGIN.style.pointToLayer,
                onEachFeature: function(feature, layer) {
                    layer.bindPopup('<b>Photo Origin</b>');
                }
            }).addTo(layers.map);
            layers.photo_origin.options['layer_id'] = 'photo_origin';
            LAYER_CONFIG.PHOTO_ORIGIN.visible = true;
        } catch (err) {
            console.error('Error adding photo origin layer:', err);
        }
    }
    // FOV Polygon
    if (typeof window.photoFovGeoJson === 'object' && window.photoFovGeoJson) {
        try {
            layers.photo_fov = L.geoJSON(window.photoFovGeoJson, LAYER_CONFIG.PHOTO_FOV.style).addTo(layers.map);
            layers.photo_fov.options['layer_id'] = 'photo_fov';
            LAYER_CONFIG.PHOTO_FOV.visible = true;
        } catch (err) {
            console.error('Error adding photo FOV layer:', err);
        }
    }
    // Line of Sight
    if (typeof window.photoLineGeoJson === 'object' && window.photoLineGeoJson) {
        try {
            layers.photo_line = L.geoJSON(window.photoLineGeoJson, LAYER_CONFIG.PHOTO_LINE.style).addTo(layers.map);
            layers.photo_line.options['layer_id'] = 'photo_line';
            LAYER_CONFIG.PHOTO_LINE.visible = true;
        } catch (err) {
            console.error('Error adding photo line layer:', err);
        }
    }
}

// Utility: Add arrowhead to a Leaflet polyline
function addArrowhead(layer, options = {}) {
    const color = options.color || "#e74c3c";
    const size = options.size || 15;
    const map = layer._map;
    if (!map) return;

    const latlngsRaw = layer.getLatLngs();
    const latlngs = Array.isArray(latlngsRaw[0]) ? latlngsRaw[0] : latlngsRaw;
    if (!latlngs || latlngs.length < 2) return;

    const prev = latlngs[latlngs.length - 2];
    const last = latlngs[latlngs.length - 1];

    const p1 = map.latLngToLayerPoint(prev);
    const p2 = map.latLngToLayerPoint(last);
    const angle = Math.atan2(p2.y - p1.y, p2.x - p1.x);

    const arrowLength = size;
    const arrowWidth = size / 2;

    const left = L.point(
        p2.x - arrowLength * Math.cos(angle) + arrowWidth * Math.sin(angle),
        p2.y - arrowLength * Math.sin(angle) - arrowWidth * Math.cos(angle)
    );
    const right = L.point(
        p2.x - arrowLength * Math.cos(angle) - arrowWidth * Math.sin(angle),
        p2.y - arrowLength * Math.sin(angle) + arrowWidth * Math.cos(angle)
    );

    const path = layer._path;
    const svg = path?.ownerSVGElement;
    if (!svg) {
        console.warn("Arrowhead not drawn: SVG path not ready.");
        return;
    }

    svg.querySelectorAll(`[data-arrowhead="${layer._leaflet_id}"]`).forEach((el) => el.remove());

    const arrow = document.createElementNS("http://www.w3.org/2000/svg", "polygon");
    arrow.setAttribute("points", `${p2.x},${p2.y} ${left.x},${left.y} ${right.x},${right.y}`);
    arrow.setAttribute("fill", color);
    arrow.setAttribute("stroke", color);
    arrow.setAttribute("stroke-width", "1");
    arrow.setAttribute("data-arrowhead", String(layer._leaflet_id));
    svg.appendChild(arrow);
}

// Start everything: initialize map and add raster layers (async)
(async () => {
    await initMap();
    patchLayerControlCheckboxes();
    createTimelineSlider();
})();
