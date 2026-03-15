# Project Architecture Map

**Project**: Lanyon Research Database  
**Purpose**: Refactor scattered research documentation into a high-integrity Jekyll site with Python-driven data pipeline  
**Stack**: Python (data pipeline) + Jekyll (site gen) + Docker (deployment)  
**Hosting**: VPS (Docker) + GitHub Pages option

---

## Project Goal

Migrate from manual file management to an automated research database with:
- Structured data storage (YAML frontmatter + images)
- Image optimization (web + thumbnails)
- Geospatial indexing (GeoJSON)
- Editorial essays linked to source materials

---

## Data Architecture (Data Retrieval Structure)

### Layer 1: Archive (Private)
- **Location**: `archive/`
- **Content**: Raw scans, original notes (NOT deployed)
- **Purpose**: Permanent backup, source truth

### Layer 2: Master Source
- **Location**: `raw_data/`
- **Format**: `[slug].md` (YAML frontmatter + research notes) + images
- **Parent-Variant Structure** (Historical Object Pattern):
  - Each `.md` file represents ONE research object/event
  - Stores ONE primary image + optional array of variant images
  - Variants capture different views/states of the same object

**Example: `raw_data/monastery-facade.md`**
```yaml
---
title: "Main Facade - San Pasquale Monastery"
date: 2024-01-15
labels: [architecture, restoration, monastery]
location:
  lat: 41.376
  lng: 14.372
primary_image: "monastery-facade-original.jpg"
variants:
  - file: "monastery-facade-restored-2024.jpg"
    type: "Digital Restoration"
    note: "Color corrected and noise reduced by MDA."
  - file: "monastery-facade-crop-detail.jpg"
    type: "Detail Crop"
    note: "Focus on the stone carving above the main portal."
---
This monastery facade was... (Research text here)
```

- **Required Fields**: `title`, `labels`
- **Optional Fields**: `date`, `location: {lat, lng}`, `variants` array with `{file, type, note}`
- **Owner**: Human (manual curation)

### Layer 3: Generated Collection
- **Location**: `_photos/` (Jekyll collection, auto-generated)
- **Source**: Python script processes `raw_data/` files with Parent-Variant pattern
- **Output Format**: `.md` files with frontmatter + body text
- **Frontmatter Structure**:
  ```yaml
  title: "..."
  date: "..."
  location: {lat: X, lng: Y}
  labels: [...]
  primary_image: "assets/images/[slug]-main.jpg"
  primary_thumb: "assets/thumbs/[slug].jpg"
  variants:
    - file: "assets/images/variants/[slug]/monastery-facade-restored-2024.jpg"
      thumb: "assets/thumbs/variants/[slug]/monastery-facade-restored-2024.jpg"
      type: "Digital Restoration"
      note: "Color corrected and noise reduced by MDA."
    - file: "assets/images/variants/[slug]/monastery-facade-crop-detail.jpg"
      thumb: "assets/thumbs/variants/[slug]/monastery-facade-crop-detail.jpg"
      type: "Detail Crop"
      note: "Focus on the stone carving above the main portal."
  ```
- **Auto-Generated Assets**:
  - Primary image → `assets/images/[slug]-main.jpg`
  - Primary thumbnail (150×150) → `assets/thumbs/[slug].jpg`
  - Variant images → `assets/images/variants/[slug]/[variant-filename].jpg`
  - Variant thumbnails → `assets/thumbs/variants/[slug]/[variant-filename].jpg`
  - GeoJSON index → `assets/data/geojson.geojson`

### Layer 4: Editorial Essays
- **Location**: `_topics/` (Jekyll collection, manual)
- **Format**: Markdown with `featured_photos` frontmatter array
- **Each entry**: `{id: photo_slug, commentary: "..."}`
- **Rendering**: Liquid joins photos collection to display inline

### Output Layer
- **Location**: `_site/` (Jekyll build output)
- **Served by**: Docker + Nginx or GitHub Pages

---

## Processing Pipeline

### Stage 1: Python Data Processing (`scripts/process_research.py`)

**Input**: `raw_data/*.md` + images  
**Output**: `_photos/`, `assets/`, `assets/data/geojson.geojson`

**Execution Modes (2026-03 update)**:
- `python3 scripts/process_research.py` or `python3 scripts/process_research.py geo`
  - GeoJSON only from full `raw_data/*.md` frontmatter scan
- `python3 scripts/process_research.py all`
  - Full pipeline: `_photos` generation + image processing + GeoJSON
- `python3 scripts/process_research.py changed [--prune]`
  - Incremental `_photos` generation from git-changed `raw_data/*.md`
  - `--prune`/`-p` removes stale `_photos/*.md` entries for deleted source files

**Observability / Integrity Mode (2026-03 update)**:
- `python3 scripts/process_research.py --check`
  - Audits source/generated consistency and reports errors/warnings
- `python3 scripts/process_research.py --check --json`
  - Machine-readable audit output for CI pipelines
- `python3 scripts/process_research.py --check --strict-warnings`
  - Fails when warnings exist (Python returns `-1`; shell sees exit `255`)
- `python3 scripts/process_research.py --check --clean`
  - Runs integrity check first, then asks confirmation before deleting orphan files
- `python3 scripts/process_research.py --check --clean --yes`
  - Runs integrity check first, then deletes orphan files without confirmation

**CLI Short Switches (2026-03 update)**:
- `-l` (`--log`), `-c` (`--check`), `-C` (`--clean`), `-y` (`--yes`), `-j` (`--json`), `-w` (`--strict-warnings`), `-p` (`changed --prune`)

**Location Normalization Rule (2026-03 update)**:
- `location` is normalized to a single dict (supports list-of-dicts input)
- Geo key typo diagnostics include expected vs found keys and likely matches

**Tasks**:
1. Scan all `raw_data/*.md` files
2. Validate YAML frontmatter (required fields + variants array if present)
3. Process primary image:
   - Optimize and save to `assets/images/[slug]-main.jpg`
   - Create 150×150 thumbnail → `assets/thumbs/[slug].jpg`
4. Process variant images (if `variants` array exists):
   - Loop through each variant in the array
   - Optimize each and save to `assets/images/variants/[slug]/[variant-filename].jpg`
   - Create 150×150 thumbnail → `assets/thumbs/variants/[slug]/[variant-filename].jpg`
   - Preserve metadata: `type`, `note` fields
5. Generate GeoJSON → `assets/data/geojson.geojson`
6. Create `.md` file in `_photos/[slug].md` for each entry:
   - Copy body text from raw_data
   - Add frontmatter with links to all processed images (primary + variants)

### Stage 2: Jekyll Build
- Reads `_photos/` + `_topics/` collections
- Uses `_layouts/photo.html` and `_layouts/topic.html`
- Outputs static HTML → `_site/`

### Stage 3: Nginx Serve
- Hosts `_site/` on VPS (production)

---

## Core Stack

| Component | Technology | Notes |
|-----------|-----------|-------|
| Data Processing | Python 3.11+ | Pillow (images), python-frontmatter (YAML) |
| Site Generator | Jekyll 4.x | Ruby 3.2 (github-pages compatible) |
| Frontend | HTML/CSS/JavaScript | Leaflet.js (CDN) for maps |
| Styling | CSS (Lanyon theme) | Moving from `public/` to `assets/` |
| UI Components | Bootstrap 5.2.2 | Loaded globally in `head.html`; collapse for sidebar, badges for labels |
| Tables | DataTables 2.2.2 | Bootstrap 5 integration with jQuery plugin; sortable/searchable tables in `/photos/` and `/labels/` |
| JavaScript Runtime | jQuery 3.6.0 | Required by DataTables CDN variant; loaded before DataTables |
| Container | Docker multi-stage | Python → Jekyll → Nginx |
| Deployment | VPS + optional GH Pages | Docker Compose on VPS |

## Features

### Photo Browsing
- **`/photos/`** - All photos in sortable, filterable DataTable (columns: Thumbnail, Title, Year, Labels, Map)  
- **`/labels/`** - Photos filtered by label with label selector badges and slug-based pre-filtering  
- **URL parameters** - `?label=slug` on `/photos/` and `?tag=slug` on `/labels/` for deep linking

Additional UI: `/photos/` now provides a user-controlled toggle between the classic DataTables row view and a responsive Bootstrap image grid. The grid is rendered client-side from the current DataTables result set (page + search + order) so DataTables controls (search, pagination, ordering, page-length) continue to apply. The behavior is implemented in `assets/js/photos-index.js` and the grid view state is deep-linkable via `?view=grid`.

### DataTables Controls (All Layouts)
- Sortable columns (Mappa column now sortable)
- Global text search across photo titles and descriptions
- Entries-per-page selector (10, 25, 50, 100)
- Pagination with page info
- Italian language localization
- Bootstrap 5 responsive styling

---

## Configuration

### `_config.yml` Collections

```yaml
collections:
  photos:
    output: true
    permalink: /photos/:slug/
  topics:
    output: true
    permalink: /topics/:slug/

exclude:
  - archive/
  - raw_data/
  - scripts/
  - Dockerfile
  - docker-compose.yml
```

---

## File Manifest

| Path | Type | Purpose |
|------|------|---------|
| `archive/` | Folder | Private backups (excluded from build) |
| `raw_data/` | Folder | Master YAML + images (source of truth) |
| `_photos/` | Jekyll Collection | Auto-generated from raw_data |
| `_topics/` | Jekyll Collection | Manual editorial essays |
| `assets/images/` | Folder | Optimized photos |
| `assets/thumbs/` | Folder | 150×150 thumbnails |
| `assets/data/` | Folder | GeoJSON and metadata |
| `_site/` | Output | Final HTML (deployment target) |
| `scripts/process_research.py` | Script | Python ETL pipeline |
| `_layouts/photo.html` | Layout | Individual photo detail page (variants, GeoJSON map) |
| `_layouts/topic.html` | Layout | Editorial topic page (linked photos) |
| `_layouts/label.html` | Layout | Label index + `?tag=` filtered view (client-side SPA) |
| `_layouts/photos_index.html` | Layout | `/photos/` index with DataTables (sortable, filterable) |
| `photos.md` | Page | Collection index at `/photos/`; uses `photos_index` layout; `exclude_from_nav: true` |
| `topics.md` | Page | Collection index at `/topics/`; uses `page` layout; `exclude_from_nav: true` |
| `labels.md` | Page | Label index at `/labels/` |
| `_includes/head.html` | Include | Global `<head>`; loads Bootstrap CSS+JS globally via `cdn_libs` |
| `_includes/sidebar.html` | Include | Collapsible collection nav (Bootstrap collapse, CSS `+`/`−` toggle) |

---

## Constraints & Decisions

### Parent-Variant Pattern (Historical Object)
- **Why**: One research object (e.g., facade) may have multiple visual representations (original, restored, detail crop)
- **Design**: Each `raw_data/*.md` file is ONE object with a primary image + optional variants array
- **Benefit**: Single source of truth—update object metadata once, all variants inherit location/date/labels
- **Implementation**: Python script respects this structure; generates folder hierarchy `assets/images/variants/[slug]/`
- **Anti-pattern**: Don't create separate entries for each variant (causes data drift)

### No site_source/ folder
- **Why**: Jekyll's default workflow is `root → _site/`
- **You currently**: Source files in `root/`, output to `_site/`
- **No change needed**: Keep this structure

### One-way pipeline
- Human edits `raw_data/` → Python runs → `_photos/` generated → Jekyll builds → `_site/`
- Never hand-edit `_photos/` (regenerated each build)

---

### Sidebar Collapsible Collection Navigation

- **Pattern**: Each collection entry in the sidebar has two independent elements:
  1. A clickable `<a>` link → collection index page (`/photos/`, `/topics/`, `/labels/`)
  2. A Bootstrap `collapse` toggle button (chevron icon) → expands/collapses individual item list
- **Why Bootstrap collapse over `<details>`**: `<details>/<summary>` is a single hit target — the entire `<summary>` toggles, making it impossible to have a separate link + separate toggle in the same row without JS hacks.
- **Bootstrap global load**: Bootstrap CSS+JS moved from `photo.html` inline to `_includes/head.html` using `site.cdn_libs.*` values (Single Source of Truth already in `_config.yml`).
- **Active state**: Use Jekyll's `page.collection` variable (equals `"photos"` for any `_photos/*.md`) to auto-expand the relevant section and add `active` class to the parent link.
- **Collection index pages**: Standalone root markdown files (`photos.md`, `topics.md`) with explicit `permalink` override. **Not** inside `_photos/` or `_topics/` to avoid polluting `site.photos`/`site.topics` iteration.
  - `photos.md` → `permalink: /photos/` — renders a grid/list of all `site.photos`
  - `topics.md` → `permalink: /topics/` — renders a list of all `site.topics`
  - `labels.md` already exists at `/labels/` (same pattern)

**Sidebar HTML pattern:**
```html
<!-- Photos -->
<div class="sidebar-collection-header">
  <a href="/photos/" class="sidebar-nav-item{% if page.url == '/photos/' or page.collection == 'photos' %} active{% endif %}">
    Photos ({{ site.photos.size }})
  </a>
  <button class="sidebar-collapse-toggle"
          data-bs-toggle="collapse"
          data-bs-target="#photos-list"
          aria-expanded="{% if page.collection == 'photos' or page.url == '/photos/' %}true{% else %}false{% endif %}">
    <!-- empty: CSS ::before renders + or − based on aria-expanded -->
  </button>
</div>

**Toggle CSS pattern** (in `assets/css/lanyon.css`):
```css
.sidebar-collapse-toggle::before { content: "+"; }
.sidebar-collapse-toggle[aria-expanded="true"]::before { content: "\2212"; } /* − minus sign */
```
Bootstrap automatically updates `aria-expanded` on the button — no custom JS required.
<div class="collapse {% if page.collection == 'photos' or page.url == '/photos/' %}show{% endif %}" id="photos-list">
  <ul>...items...</ul>
</div>
```

---

## Known Issues & Tech Debt

| Issue | Status | Notes |
|-------|--------|-------|
| Ruby 3.3 incompatible | ✅ Fixed | Downgraded to 3.2 for jekyll compatibility |
| Bootstrap duplication | ✅ Fixed | Moved to global `head.html`; removed inline copies from `photo.html`, `label.html` |
| Multi-stage Docker | Planned | Need Stage 1: Python, Stage 2: Jekyll, Stage 3: Nginx |
| Asset migration | Pending | Move `public/` CSS/JS to `assets/` |

---

## Next Steps (From README.md Tasks)

- [x] **Phase 1**: Create `scripts/process_research.py` (data pipeline) ← **DONE**
- [x] **Phase 2**: Update `_config.yml` (Jekyll collections) ← **DONE**
- [x] **Phase 3**: Create `_layouts/photo.html` and `_layouts/topic.html` ← **DONE** (variants + GeoJSON overlays included)
- [x] **Phase 3.5**: Sidebar collapsible collection navigation ← **DONE**
- [x] **Phase 3.5**: Sidebar collapsible collection navigation ← **DONE**
- [x] **Phase 3.6**: `/photos/` index with DataTables (`_layouts/photos_index.html`) ← **DONE**
- [ ] **Phase 4**: Update Docker (multi-stage build) ← **NEXT**
- [ ] **Phase 5**: Asset refactor (public/ → assets/)

**Active backlog**: End-to-end test of per-photo GeoJSON overlay pipeline (`photoOriginGeoJson`/`Fov`/`Line` → `addIndividualGeoJsonLayers()`) via Docker build with real frontmatter data.

---

## Related Files

- `.ai/IMPLEMENTATION_STEPS.md` - Task tracking
- `.ai/MEMORY/LEARNINGS.md` - Session notes
- `_config.yml` - Jekyll configuration
- `README.md` - Project overview
