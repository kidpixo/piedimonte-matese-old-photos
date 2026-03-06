# Il Cotonificio Egg di Piedimonte Matese

A historical photo documentation website exploring the industrial and social history of the Egg Cotton Mill in Piedimonte Matese, Italy, through interactive maps and archival photographs.

## About the Project

This Jekyll-based static website documents the history of the Cotonificio Egg, a cotton mill that profoundly shaped the economic and social life of Piedimonte Matese for over a century (1812-1943). The site combines historical research, archival photographs, and interactive mapping to tell the story of this significant chapter in Southern Italy's industrial history.

Founded by Swiss entrepreneur Gian Giacomo Egg during the Napoleonic era, the mill became the first mechanical spinning facility in the Kingdom of Naples and one of the largest industries in Southern Italy, at its peak employing over 1,300 workers.

## Features

- **Historical Photo Collection**: Curated archival photographs with detailed metadata including dates, locations, and historical context
- **Interactive Mapping**: Leaflet-based interactive maps displaying photo locations and historical geographic data
- **GeoJSON Integration**: Geographic visualization of historical sites and photo origins
- **Thematic Topics**: Research essays connecting multiple photographs and historical themes
- **Responsive Design**: Built on the Lanyon theme for Jekyll, optimized for desktop and mobile viewing

## Technology Stack

- **Static Site Generator**: Jekyll 4.x
- **Theme**: Lanyon (Poole-based)
- **Mapping**: Leaflet.js with plugins for georaster layers and Bing maps
- **Data Processing**: Python scripts for image optimization and GeoJSON generation
- **Deployment**: Docker-based containerization for reproducible builds
- **Hosting**: GitHub Pages compatible

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

## Data Workflow

1. **Archive Layer**: `archive/` - Private raw scans and notes
2. **Source Layer**: `raw_data/` - Master Markdown files with frontmatter
3. **Generated Layer**: `_photos/` - Auto-generated Jekyll collection
4. **Editorial Layer**: `_topics/` - Manual research essays
5. **Assets**: Optimized images, thumbnails, and GeoJSON data

## CDN Libraries

All external dependencies are loaded via pinned CDN URLs (configured in `_config.yml`):
- Leaflet 1.9.4 for mapping
- jQuery 3.6.0 for DOM manipulation
- Bootstrap 5.2.2 for UI components
- Leaflet plugins for advanced mapping features

## License

See [LICENSE.md](LICENSE.md) for details.

## Author

**Mario D'Amore**  
Email: kidpixo@gmail.com

---

*"La nostra Liverpool"* - As Piedimonte Matese was sometimes called for its modern industrial organization comparable to the best European factories.
