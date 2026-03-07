<a name="top"></a>

[🇬🇧 ENG](#english) | [🇮🇹 ITA](#italiano)

---

<a name="english"></a>
# Il Cotonificio Egg di Piedimonte Matese

A historical photo documentation website exploring the industrial and social history of the Egg Cotton Mill in Piedimonte Matese, Italy, through interactive maps and archival photographs.

## About the Project

This Jekyll-based static website documents the history of the Cotonificio Egg, a cotton mill that profoundly shaped the economic and social life of Piedimonte Matese for over a century (1812-1943). The site combines historical research, archival photographs, and interactive mapping to tell the story of this significant chapter in Southern Italy's industrial history.

Founded by Swiss entrepreneur Gian Giacomo Egg during the Napoleonic era, the mill became the first mechanical spinning facility in the Kingdom of Naples and one of the largest industries in Southern Italy, at its peak employing over 1,300 workers.

[^top](#top)

## Features

- **Historical Photo Collection**: Curated archival photographs with detailed metadata including dates, locations, and historical context
- **Interactive Mapping**: Leaflet-based interactive maps displaying photo locations and historical geographic data
- **GeoJSON Integration**: Geographic visualization of historical sites and photo origins
- **Thematic Topics**: Research essays connecting multiple photographs and historical themes
- **Responsive Design**: Built on the Lanyon theme for Jekyll, optimized for desktop and mobile viewing

[^top](#top)

## Technology Stack

- **Static Site Generator**: Jekyll 4.x
- **Theme**: Lanyon (Poole-based)
- **Mapping**: Leaflet.js with plugins for georaster layers and Bing maps
- **Data Processing**: Python scripts for image optimization and GeoJSON generation
- **Deployment**: Docker-based containerization for reproducible builds
- **Hosting**: GitHub Pages compatible

[^top](#top)

## Project Structure

```
.
├── _photos/          # Photo collection (Jekyll collection)
├── _topics/          # Thematic research essays (Jekyll collection)
├── raw_data/         # Source data files with frontmatter
├── assets/
│   ├── photos/       # Optimized photo assets
│   ├── thumbs/       # Generated thumbnails
│   ├── data/         # GeoJSON and geographic data
│   ├── css/          # Stylesheets
│   └── js/           # JavaScript for maps and interactions
├── _layouts/         # Jekyll layout templates
├── _includes/        # Reusable template components
└── scripts/          # Python processing scripts
```

[^top](#top)

## Collections

### Photos
Each photo entry contains:
- Historical context and description
- Geographic coordinates for mapping
- Date and location information
- Labels/tags for categorization
- Image variants (original, restored, detail crops)

### Topics
Thematic essays that connect multiple photographs and explore specific aspects of the mill's history, such as architecture, social conditions, or industrial processes.

[^top](#top)

## Development

### Local Setup

```bash
# Install dependencies
bundle install

# Serve locally
bundle exec jekyll serve

# Or using Docker
docker-compose up
```

### Processing Photos

Python scripts handle image optimization and metadata generation:

```bash
# Process raw data into Jekyll collections
python scripts/process_research.py
```

[^top](#top)

## Data Workflow

1. **Archive Layer**: `archive/` - Private raw scans and notes
2. **Source Layer**: `raw_data/` - Master Markdown files with frontmatter
3. **Generated Layer**: `_photos/` - Auto-generated Jekyll collection
4. **Editorial Layer**: `_topics/` - Manual research essays
5. **Assets**: Optimized images, thumbnails, and GeoJSON data

[^top](#top)

## CDN Libraries

All external dependencies are loaded via pinned CDN URLs (configured in `_config.yml`):
- Leaflet 1.9.4 for mapping
- jQuery 3.6.0 for DOM manipulation
- Bootstrap 5.2.2 for UI components
- Leaflet plugins for advanced mapping features

[^top](#top)

## License

See [LICENSE.md](LICENSE.md) for details.

[^top](#top)

## Author

**Mario D'Amore**  
Email: kidpixo@gmail.com

[^top](#top)

---

*"La nostra Liverpool"* - As Piedimonte Matese was sometimes called for its modern industrial organization comparable to the best European factories.

---

<a name="italiano"></a>
# Il Cotonificio Egg di Piedimonte Matese

Un sito web di documentazione storica fotografica che esplora la storia industriale e sociale del Cotonificio Egg a Piedimonte Matese, Italia, attraverso mappe interattive e fotografie d'archivio.

## Il Progetto

Questo sito statico basato su Jekyll documenta la storia del Cotonificio Egg, una fabbrica tessile che ha profondamente segnato la vita economica e sociale di Piedimonte Matese per oltre un secolo (1812-1943). Il sito combina ricerca storica, fotografie d'archivio e mappe interattive per raccontare questo capitolo significativo della storia industriale del Sud Italia.

Fondato dall'imprenditore svizzero Gian Giacomo Egg durante l'epoca napoleonica, il cotonificio divenne il primo stabilimento di filatura meccanica del Regno di Napoli e una delle più grandi industrie del Sud Italia, arrivando ad impiegare oltre 1.300 operai nel periodo di massima attività.

[^top](#top)

## Caratteristiche

- **Collezione Fotografica Storica**: Fotografie d'archivio curate con metadati dettagliati inclusi date, luoghi e contesto storico
- **Mappe Interattive**: Mappe interattive basate su Leaflet che mostrano le posizioni delle foto e dati geografici storici
- **Integrazione GeoJSON**: Visualizzazione geografica di siti storici e origini delle fotografie
- **Temi di Ricerca**: Saggi di ricerca che collegano più fotografie e temi storici
- **Design Responsivo**: Costruito sul tema Lanyon per Jekyll, ottimizzato per la visualizzazione desktop e mobile

[^top](#top)

## Stack Tecnologico

- **Generatore Sito Statico**: Jekyll 4.x
- **Tema**: Lanyon (basato su Poole)
- **Mappe**: Leaflet.js con plugin per layer georaster e mappe Bing
- **Elaborazione Dati**: Script Python per l'ottimizzazione delle immagini e la generazione di GeoJSON
- **Deployment**: Containerizzazione basata su Docker per build riproducibili
- **Hosting**: Compatibile con GitHub Pages

[^top](#top)

## Struttura del Progetto

```
.
├── _photos/          # Collezione fotografie (collezione Jekyll)
├── _topics/          # Saggi di ricerca tematici (collezione Jekyll)
├── raw_data/         # File di dati sorgente con frontmatter
├── assets/
│   ├── photos/       # Risorse fotografiche ottimizzate
│   ├── thumbs/       # Miniature generate
│   ├── data/         # GeoJSON e dati geografici
│   ├── css/          # Fogli di stile
│   └── js/           # JavaScript per mappe e interazioni
├── _layouts/         # Template di layout Jekyll
├── _includes/        # Componenti template riutilizzabili
└── scripts/          # Script Python di elaborazione
```

[^top](#top)

## Collezioni

### Fotografie
Ogni voce fotografica contiene:
- Contesto storico e descrizione
- Coordinate geografiche per la mappatura
- Informazioni su data e luogo
- Etichette/tag per la categorizzazione
- Varianti dell'immagine (originale, restaurata, ritagli di dettaglio)

### Temi
Saggi tematici che collegano più fotografie ed esplorano aspetti specifici della storia del cotonificio, come architettura, condizioni sociali o processi industriali.

[^top](#top)

## Sviluppo

### Configurazione Locale

```bash
# Installa le dipendenze
bundle install

# Avvia il server locale
bundle exec jekyll serve

# Oppure usando Docker
docker-compose up
```

### Elaborazione delle Fotografie

Gli script Python gestiscono l'ottimizzazione delle immagini e la generazione dei metadati:

```bash
# Elabora i dati grezzi nelle collezioni Jekyll
python scripts/process_research.py
```

[^top](#top)

## Flusso di Lavoro dei Dati

1. **Livello Archivio**: `archive/` - Scansioni grezze private e note
2. **Livello Sorgente**: `raw_data/` - File Markdown master con frontmatter
3. **Livello Generato**: `_photos/` - Collezione Jekyll auto-generata
4. **Livello Editoriale**: `_topics/` - Saggi di ricerca manuali
5. **Risorse**: Immagini ottimizzate, miniature e dati GeoJSON

[^top](#top)

## Librerie CDN

Tutte le dipendenze esterne sono caricate tramite URL CDN con versioni fissate (configurate in `_config.yml`):
- Leaflet 1.9.4 per le mappe
- jQuery 3.6.0 per la manipolazione del DOM
- Bootstrap 5.2.2 per i componenti UI
- Plugin Leaflet per funzionalità avanzate di mappatura

[^top](#top)

## Licenza

Vedi [LICENSE.md](LICENSE.md) per i dettagli.

[^top](#top)

## Autore

**Mario D'Amore**  
Email: kidpixo@gmail.com

[^top](#top)

---

*"La nostra Liverpool"* - Come Piedimonte Matese era talvolta chiamata per la sua moderna organizzazione industriale paragonabile alle migliori fabbriche europee.
