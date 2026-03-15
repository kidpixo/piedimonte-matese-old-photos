# Implementation Steps & Task Tracker

**Primary Context**: Read [PROJECT_MAP.md](PROJECT_MAP.md) first  
**Instructions**: Follow [.github/copilot-instructions.md](../.github/copilot-instructions.md)  
**Update Frequency**: After each task completed

---

## Current Status

**Project Phase**: Layout Templates (Phase 3) DONE → Docker Build (Phase 4) NEXT  
**Last Updated**: 2026-03-10 (Phase 3 fully complete—variants + GeoJSON overlays implemented)  
**Blocker**: None

### Update Log — 2026-03-14 (`scripts/process_research.py` hardening)

**What changed**
- Refactored execution into explicit modes:
  - `geo` (default): GeoJSON-only build from all `raw_data/*.md`
  - `all`: full `_photos` + image processing + GeoJSON
  - `changed`: git-scoped incremental `_photos` build (`--prune` optional)
- Decoupled GeoJSON metadata collection from `_photos` generation to avoid mode-coupling.
- Added `photo_post_rel_url` in generated `photos_origin.geojson` properties.
- Added defensive location normalization (`dict` or list-of-dicts) before validation and geometry extraction.
- Improved typo diagnostics for location keys (missing/unknown keys + close-match suggestions).

**Observability additions**
- Added `--check` audit mode:
  - enumerates all `raw_data/*.md`
  - validates geo presence and image references
  - reports missing generated `_photos/*.md`
  - reports orphaned files in `raw_data/`, `_photos/`, `assets/images/`, `assets/thumbs/`
- Added `--json` for machine-readable check output (CI-friendly).
- Added `--strict-warnings` for CI failure on warnings.
- Added `--clean` (requires `--check`) to remove orphan files only after check output and interactive confirmation.

**Exit code contract**
- `--check`: `0` (clean), `1` (errors), `2` (internal failure)
- `--check --strict-warnings`: returns `-1` when warnings exist (shell observes `255`)

**Validation executed**
- Syntax validation: `python3 -m py_compile scripts/process_research.py`
- Runtime validation:
  - `python3 scripts/process_research.py --check`
  - `python3 scripts/process_research.py --check --json`
  - `python3 scripts/process_research.py --check --strict-warnings` (confirmed CI-fail behavior)

### Update Log — 2026-03-14 (`scripts/process_research.py` cleanup UX + short flags)

**What changed (this chat)**
- Added `--yes` to skip confirmation only in `--check --clean` flow.
- Added short options for faster CLI use:
  - `-l/-c/-C/-y/-j/-w` and `changed -p`.

**How we implemented it**
- Extended `run_check_mode(...)` with `auto_yes` and kept cleanup execution strictly after report generation.
- Preserved safe behavior: interactive confirmation remains default for `--check --clean`.
- Added argument guards to avoid unsafe or ambiguous combinations:
  - `--clean` requires `--check`
  - `--yes` requires both `--check` and `--clean`

**Validation executed**
- `python3 -m py_compile scripts/process_research.py`
- `python3 scripts/process_research.py -h`
- `python3 scripts/process_research.py -c -C -y`
- `python3 scripts/process_research.py --check --yes` (expected guard error)

### Update Log — 2026-03-15 (`_layouts/photos_index.html` table/grid hybrid)

**What changed**
- Added a view switch on `/photos/` to toggle between DataTable rows and image-only Bootstrap grid.
- Kept DataTables as the single data engine (search, pagination, ordering, page length, info).
- Implemented grid rendering from current DataTables state (`page + search + order`) so controls keep working in grid mode.
- Added URL state sync for deep-linking view mode (`?view=grid`), preserving existing query params.

**Technical notes**
- Works with both DataTables constructor styles already used in project:
  - `new DataTable(...)`
  - jQuery plugin fallback `jQuery(...).DataTable(...)`
- Added defensive fallback with explicit console error when DataTables scripts are unavailable.
- Grid cards clone the linked thumbnail from table rows and preserve accessible labels.

**Validation executed**
- Editor diagnostics check on `_layouts/photos_index.html`: no errors reported.

### Update Log — 2026-03-15 (`assets/js/photos-index.js` extraction)

**What changed**
- Moved custom `/photos/` page behavior out of inline `<script>` into dedicated asset file: `assets/js/photos-index.js`.
- Replaced inline script in `_layouts/photos_index.html` with one external include:
  - `<script src="{{ '/assets/js/photos-index.js' | relative_url }}"></script>`

**Why**
- Keeps layout template focused on markup/Liquid and centralizes custom logic in reusable static assets.
- Improves maintainability while preserving current CDN-only architecture and client-side behavior.

**Validation executed**
- Editor diagnostics check on `_layouts/photos_index.html` and `assets/js/photos-index.js`: no errors reported.

### Chat refinements — 2026-03-15 (final)

- Replaced hover overlay with persistent single-line captions under thumbnails to improve scanability and avoid duplicated information.
- Added keyboard focus styling and ensured anchors remain accessible; included visually-hidden map hint for screen readers.
- Introduced compact top-right badges with year + map icon for tiles that have coordinates; badges styled to match icon height.
- Kept DataTables toolbar and pagination visible in grid mode by hiding only the `tbody`; added `#clear-filters` button and live counts (`#photos-count`).
- Externalized JS to `assets/js/photos-index.js` and added CSS rules in `assets/css/overwrite_bootstrap.css`.

Status: all changes implemented and validated locally (editor diagnostics). See files changed section above for file list.

### Short Summary — 2026-03-15 (photos grid + assetization)

What we changed:
- Added a client-side grid toggle to `/photos/` that mirrors DataTables results into a responsive Bootstrap grid.
- Implemented a map badge overlay for images with map coordinates (reuses the same SVG used in the sidebar).
- Extracted the inline page script into `assets/js/photos-index.js` and replaced inline code with a single script include in `_layouts/photos_index.html`.

How we implemented it:
1. Kept DataTables as the canonical data engine; initialized it from `assets/js/photos-index.js` (supports both `new DataTable(...)` and `jQuery(...).DataTable(...)` patterns).
2. On every DataTables `draw` event we rebuild the grid from the current result set (`page: 'current', search: 'applied', order: 'applied'`).
3. The grid cards clone the table thumbnail and add a `position-absolute` SVG badge when the row's Map column contains a marker (✓).
4. The view toggle state is synchronized to the URL via `?view=grid` for deep-linking and preserved alongside existing params like `label`.
5. Added defensive checks and console errors when DataTables or required DOM elements are unavailable.

Files touched:
- `_layouts/photos_index.html` (add toggle/grid container + include of `assets/js/photos-index.js`)
- `assets/js/photos-index.js` (new file)

Why:
- Keeps DataTables controls (filtering/pagination) while offering a visual grid. Externalizing JS improves maintainability and aligns with the project's CDN-only/static asset constraints.

---

## Phase Checklist

- [x] **Phase 1**: Python data pipeline (`scripts/process_research.py`) ← **DONE**
- [x] **Phase 2**: Jekyll config (collections + paths) ← **DONE**
- [x] **Phase 3**: Layout templates (photo.html + topic.html + label.html) ← **DONE**
- [ ] **Phase 4**: Docker multi-stage build
- [ ] **Phase 5**: Asset migration (public/ → assets/)

---

## Phase 1: Data Pipeline (scripts/process_research.py)

**Status**: ✅ COMPLETED (production-ready)  
**Owner**: Completed  
**Priority**: P0 (blocks all downstream work)  
**Goal**: Process `raw_data/*.md` → `_photos/` transformation with image optimization (Parent-Variant pattern)

### Current Data Structure (Real)

Your raw_data already has this format:
```yaml
---
layout: photo
title: "Via Carmine ponte torano verso piazza Carmine circa 1900"
primary_image: "ViaCarmine-ponte_torano_verso_piazza_carmine_1900.jpg"
date: 1900-01-01
labels: ["piazza carmine", ciminera, "via carmine"]
location:
  - latitude_origin: 41.35528481
    longitude_origin: 14.37159419
  - latitude_vertex_left: 41.35534475
    longitude_vertex_left: 14.37221629
  - latitude_vertex_right: 41.35519581
    longitude_vertex_right: 14.37199924
# Additional fields (keep for future use):
# - variants: [{file: "...", type: "...", note: "..."}, ...]
---

Via Carmine ponte torano verso piazza Carmine circa 1900.
```

**Existing Infrastructure**:
- ✅ `scripts/convert_photos_coords.py` - Already processes location data → GeoJSON
- ✅ `raw_data/` - Has real examples with images
- ✅ `primary_image` field - Ready for optimization
- 🔄 `variants` array - To be added for Parent-Variant pattern

### Description
Create `scripts/process_research.py` that:

1. **Scans** `raw_data/*.md` files
2. **Validates** frontmatter: `title`, `date`, `location`, `labels`, `primary_image`
3. **Processes images** (primary + optional variants):
   - Primary → `assets/images/[slug]-main.jpg` + thumbnail 150×150 → `assets/thumbs/[slug].jpg`
   - Each variant (if present) → `assets/images/variants/[slug]/[file].jpg` + thumbnail
4. **Reuses location data**: Call/adapt `convert_photos_coords.py` logic for GeoJSON generation
5. **Generates** `assets/data/geojson.geojson` with photo locations
6. **Creates** `.md` file in `_photos/[slug].md` with processed image paths + original location data

### Acceptance Criteria
- [ ] Script reads all `raw_data/*.md` files
- [ ] Validates YAML frontmatter (logs errors, skips invalid entries)
- [ ] **Processes primary image**:
  - [ ] Optimize and save → `assets/images/[slug]-main.jpg`
  - [ ] Create 150×150 thumbnail → `assets/thumbs/[slug].jpg`
- [ ] **Handles variants array** (if `variants:` key exists):
  - [ ] Iterates each variant in `variants: [{file, type, note}, ...]`
  - [ ] Optimize each → `assets/images/variants/[slug]/[filename].jpg`
  - [ ] Create thumbnail → `assets/thumbs/variants/[slug]/[filename].jpg`
  - [ ] Preserve metadata: `type`, `note` fields
- [ ] **Processes location data**:
  - [ ] Extracts `origin` point: `{latitude_origin, longitude_origin}`
  - [ ] Extracts FOV polygon: vertex_left + vertex_right (use existing `convert_photos_coords.py` logic)
  - [ ] Generates GeoJSON with both: `assets/data/geojson.geojson`
- [ ] **Writes `.md`** to `_photos/[slug].md`:
  - [ ] Copies body text from raw_data
  - [ ] Frontmatter includes primary image + variants array with all processed paths
  - [ ] Frontmatter preserves location data (for photo.html to use)
- [ ] No hardcoded paths (use config or constants)
- [ ] Error handling + logging (no silent failures per copilot-instructions.md)

### Dependencies
- [ ] Python 3.11+ environment configured
- [ ] Pillow library for image processing
- [ ] python-frontmatter for YAML parsing
- [ ] geopandas + shapely (from existing convert_photos_coords.py)
- [ ] pandas (optional, for data handling)

### Parent-Variant Anti-Patterns to Avoid
❌ Do NOT create separate `_photos/` entries for each variant  
❌ Do NOT hardcode paths (variant folder structure must match slug)  
❌ Do NOT lose variant metadata (`type`, `note`)  
❌ Do NOT skip location data (convert_photos_coords.py has the logic)

### Notes
**Key decision**: One-way pipeline—never hand-edit `_photos/` (autogenerated)  
**Existing script**: `scripts/convert_photos_coords.py` already handles location → GeoJSON (shapely Polygon for FOV, Point for origin)  
**Adapt, don't rewrite**: Extract the location processing logic from `convert_photos_coords.py` into new script  
**Testing**: Use existing raw_data examples:
- Try: `viaCarmine-ponte_torano_verso_piazza_carmine_1900.md` (has primary_image)
- Add: variant image to test Parent-Variant logic

### Implementation Strategy
1. Create `scripts/process_research.py` with main flow
2. Extract location → GeoJSON logic from `convert_photos_coords.py` into helper function
3. Image processing: Pillow for optimization + thumbnails
4. Output: Jekyll-ready `.md` files in `_photos/`

### Definition of Done
- [x] `scripts/process_research.py` created and tested with real data
- [x] Processes `viaCarmine-ponte_torano_verso_piazza_carmine_1900.md` without errors
- [x] Output folder structure correct:
  - [x] `assets/images/via-carmine-ponte_torano_verso_piazza_carmine_1900-main.jpg` (232K optimized)
  - [x] `assets/thumbs/via-carmine-ponte_torano_verso_piazza_carmine_1900.jpg` (5.6K thumbnail)
  - [x] `assets/data/photos_origin.geojson` + `photos_fov.geojson` (both files created, 9 features each)
- [x] Generated `_photos/via-carmine-ponte_torano_verso_piazza_carmine_1900.md` created and ready
- [x] GeoJSON validates (proper GeoJSON FeatureCollection format)
- [x] No hardcoded values (all paths computed from slug)
- [x] Added notes to MEMORY/LEARNINGS.md

### Related Files
- [scripts/convert_photos_coords.py](scripts/convert_photos_coords.py) - Existing location processing (reference/reuse logic)
- [raw_data/viaCarmine-ponte_torano_verso_piazza_carmine_1900.md](raw_data/viaCarmine-ponte_torano_verso_piazza_carmine_1900.md) - Real test data
- [.ai/PROJECT_MAP.md](PROJECT_MAP.md#layer-2-master-source) - Source format spec
- [.ai/PROJECT_MAP.md](PROJECT_MAP.md#layer-3-generated-collection) - Output structure

---

## Phase 2: Jekyll Configuration (Collections & Paths)

**Status**: ✅ COMPLETED (production-ready)  
**Owner**: Completed  
**Priority**: P1  
**Goal**: Validate & finalize `_config.yml` collections and permalink structure

### Description
Verify and update `_config.yml`:
1. Collections (`photos`, `topics`) are already registered—verify paths match PROJECT_MAP.md Layer 3
2. Confirm permalinks are correct
3. Validate exclude list includes `archive/`, `raw_data/`, `scripts/`, etc.
4. Add CDN configuration for Leaflet.js (if using maps)

### Acceptance Criteria
- [x] `collections.photos` exists with `output: true` and permalink `/photos/:slug/`
- [x] `collections.topics` exists with `output: true` and permalink `/topics/:slug/`
- [x] `exclude:` includes: `archive/`, `raw_data/`, `scripts/`, `Dockerfile`, `docker-compose.yml`
- [x] CDN libs documented: Leaflet.js URL + version (SRI hashes noted for future)
- [ ] Site builds without warnings: `jekyll build` (requires running Docker/podman)
- [ ] Collections accessible via Liquid: `site.photos`, `site.topics` (verify in Phase 3)
- [x] No path conflicts between collections and static content

### Dependencies
- [ ] Phase 1 complete (process_research.py generates _photos/)

### Current State
✅ Collections already defined in _config.yml  
✅ Permalinks fixed to match `/photos/:slug/` and `/topics/:slug/`  
✅ CDN configuration centralized in `cdn_libs` section

### Task 2.1: Verify Collection Configuration ✅ COMPLETED

- [x] Open `_config.yml`
- [x] Confirm `collections.photos.output: true`
- [x] Check `collections.photos.permalink` matches `/photos/:slug/`
- [x] Fixed: Changed from `/archive/:name/` to `/photos/:slug/`
- [x] Fixed: Changed topics from `:name` to `:slug` variable
- [ ] Run `jekyll build --trace` and check for warnings (deferred to Phase 3)
- [ ] Verify `_site/photos/` contains generated HTML (deferred to Phase 3)

### Task 2.2: Add CDN Configuration ✅ COMPLETED

Added to `_config.yml`:
```yaml
cdn_libs:
  leaflet_css: "https://cdn.jsdelivr.net/npm/leaflet@1.9.4/dist/leaflet.css"
  leaflet_js: "https://cdn.jsdelivr.net/npm/leaflet@1.9.4/dist/leaflet.min.js"
  jquery: "https://code.jquery.com/jquery-3.6.0.min.js"
  bootstrap_css: "https://cdn.jsdelivr.net/npm/bootstrap@5.2.2/dist/css/bootstrap.min.css"
  bootstrap_js: "https://cdn.jsdelivr.net/npm/bootstrap@5.2.2/dist/js/bootstrap.bundle.min.js"
  georaster: "https://cdn.jsdelivr.net/npm/georaster@1.6.0/dist/georaster.browser.bundle.min.js"
  georaster_layer: "https://cdn.jsdelivr.net/npm/georaster-layer-for-leaflet@3.10.0/dist/v3/webpack/bundle/georaster-layer-for-leaflet.min.js"
  leaflet_bing: "https://cdn.jsdelivr.net/npm/leaflet-bing-layer@3.3.1/leaflet-bing-layer.min.js"
  leaflet_locate_css: "https://cdnjs.cloudflare.com/ajax/libs/leaflet-locatecontrol/0.83.1/L.Control.Locate.css"
  leaflet_locate_js: "https://cdnjs.cloudflare.com/ajax/libs/leaflet-locatecontrol/0.83.1/L.Control.Locate.min.js"
```

### Definition of Done
- [x] `_config.yml` updated with correct collection permalinks
- [x] Collections use `:slug` variable for consistency
- [x] CDN libraries centralized (Single Source of Truth principle)
- [x] PROJECT_MAP.md Collection structure matches actual _config.yml
- [ ] `jekyll build` succeeds without warnings (requires Docker/podman container)
- [ ] Collections accessible in Liquid templates (to be verified in Phase 3)
- [ ] Added notes to MEMORY/LEARNINGS.md

### Notes Added
- **Permalink Fix**: Changed `/archive/:name/` to `/photos/:slug/` for proper URL structure
- **CDN Centralization**: Following "Single Source of Truth" principle from copilot-instructions.md
- **SRI Hashes**: Noted for future implementation (use https://www.srihash.org/)
- **Next Step**: Refactor layouts to use `{{ site.cdn_libs.leaflet_js }}` instead of hardcoded URLs
- **Sidebar Fix**: Replaced Bootstrap collapse with HTML5 `<details>/<summary>`, fixed collection references (`site.pages` → `site.photos`), added Topics menu

### Related Files
- [_config.yml](_config.yml) - Actual file to verify/update
- [.ai/PROJECT_MAP.md](PROJECT_MAP.md#configuration) - _config.yml section

---

## Phase 3: Layout Templates (photo.html + topic.html + label.html Enhancements)

**Status**: ✅ COMPLETED (production-ready)  
**Priority**: P1  
**Goal**: Display research photos with image variants + editorial essays linked to photos + label browsing

### Task 3.1: Enhance `_layouts/photo.html` (Primary Image + Map)

**Status**: ✅ COMPLETED (primary image + conditional map)

**Acceptance Criteria**:
- [x] Displays primary image thumbnail from `processed_primary_thumb`
- [x] Thumbnail links to full-size image (`processed_primary_image`)
- [x] Map renders only if `latitude_origin` and `longitude_origin` present in `location` array
- [x] Map variables adapted to new location structure (extracts lat/lon from frontmatter array)
- [x] CDN scripts (Leaflet, etc.) conditionally loaded only when map needed
- [x] Shows all variant images with proper metadata:
  - [x] Iterates `all_images` array, skips `is_primary: true` entry for variants section
  - [x] Displays thumbnail for each variant
  - [x] Shows variant `type` and `note` fields in `<figcaption>`
  - [x] Links to full-size variant image
- [x] Research notes rendered from page markdown body
- [x] Responsive image layout (lazy loading: `loading="lazy"` on variants)
- [x] No hardcoded paths—all image URLs from frontmatter

**Completed**:
- [x] Primary image thumbnail with fallback chain
- [x] Thumbnail link to full image
- [x] Conditional map based on location data
- [x] Map center/zoom from location array
- [x] Bootstrap + Leaflet libs conditionally loaded

**Pending**: none — all items complete

**Implementation Notes**:
```liquid
{%- for variant in page.variants -%}
  <figure class="variant variant--{{ forloop.index }}">
    <img src="{{ variant.thumb }}" alt="{{ page.title }} - {{ variant.type }}" loading="lazy">
    <figcaption>{{ variant.type }}: {{ variant.note }}</figcaption>
  </figure>
{%- endfor -%}
```

### Task 3.2: Create/Enhance `_layouts/topic.html` (Editorial Essays)

**Status**: ✅ COMPLETED (functional, styling optional)

**Acceptance Criteria**:
- [x] Renders manual essay markdown (`{{ content }}`)
- [x] Reads `featured_photos: [{id: photo_slug, commentary: "..."}]` from frontmatter
- [x] Uses Liquid to join with photos collection by slug
- [x] Displays photo thumbnail + commentary inline within article
- [x] Links from thumbnail to full photo page
- [x] No hardcoded paths (uses relative_url filter)
- [x] Shows "Documentazione Collegata" section with thumbnails
- [x] Includes error handling for missing photos

**Completed**:
- [x] Created `_layouts/topic.html` with featured_photos loop
- [x] Collection join: `site.photos | where: "slug", item.id | first`
- [x] Photo thumbnails with border/styling
- [x] "Visualizza scheda tecnica" links to photo detail pages
- [x] Created test topic: `_topics/test-topic-ciminiera-e-ponte.md`
- [x] Test topic successfully references both photo collection items

**Notes**: This is the "editorial layer" where researchers annotate and contextualize source materials. Fully functional.

### Task 3.3: Add Label/Tag Browsing System

**Status**: ✅ COMPLETED (functional tag filtering)

**Acceptance Criteria**:
- [x] Extract unique labels from all photos in collection
- [x] Show label counts
- [x] Display as submenu in sidebar
- [x] Create label.html layout for single-label view
- [x] Filter photos by label via URL query parameter (`?tag=...`)
- [x] Show all photos with matching label
- [x] Client-side toggle between index and filtered views

**Completed**:
- [x] Updated `_includes/sidebar.html` with Labels submenu
- [x] Computed unique labels from `page.labels` across all photos
- [x] Shows label count: "piazza carmine (2)", "ciminiera (1)", etc.
- [x] Created `_layouts/label.html` with dual views:
  - Index: all labels with counts
  - Filtered: photos matching selected label (client-side filter)
- [x] Created `labels.md` index page at `/labels/`
- [x] JavaScript parses `?tag=...` query param and toggles filtered view
- [x] Photo grid cards in filtered view with thumbnails + links

**Notes**: Labels are extracted at build-time; filtering happens client-side for zero-server overhead.

### Definition of Done (Phase 3)
- [x] photo.html: primary image + conditional map ✅
- [x] photo.html: variant images with thumbnail, type, note, lazy loading ✅
- [x] photo.html: GeoJSON overlays (origin/fov/line) passed to JS window vars ✅
- [x] topic.html: editorial essays with featured_photos ✅
- [x] label.html: tag browsing + filtering ✅
- [x] Sidebar: updated with Photos, Topics, Labels submenu ✅
- [x] No hardcoded paths or magic values (all from frontmatter/config) ✅
- [ ] `jekyll build` succeeds without errors (⏳ pending Docker test — Phase 4 prerequisite)
- [ ] Added implementation notes to MEMORY/LEARNINGS.md (⏳ at session end)

### Related Files
- [_layouts/photo.html](_layouts/photo.html) - Enhanced with primary image + conditional map ✅
- [_layouts/topic.html](_layouts/topic.html) - Created for editorial essays ✅
- [_layouts/label.html](_layouts/label.html) - Created for tag browsing ✅
- [_includes/sidebar.html](_includes/sidebar.html) - Updated with all 3 collections + labels ✅
- [labels.md](labels.md) - New index page for tag browsing ✅
- [_topics/test-topic-ciminiera-e-ponte.md](_topics/test-topic-ciminiera-e-ponte.md) - Test topic ✅

---

## Phase 3.5: Sidebar Collapsible Collection Navigation

**Status**: ✅ COMPLETED  
**Priority**: P1  
**Goal**: Split each collection sidebar entry into a standalone index link + independent collapsible toggle for individual items; auto-expand when viewing that collection.

### Design Decisions

**Collection index pages** — Use standalone root `.md` files (same pattern as `labels.md`):
- `photos.md` at root with `permalink: /photos/` and a new `collection_index` layout (or reuse `page`)
- `topics.md` at root with `permalink: /topics/` and the same layout
- Rationale: placing index inside `_photos/` would pollute `site.photos` iteration; root files are Jekyll-idiomatic and consistent with existing `labels.md`

**Toggle mechanism** — Bootstrap `collapse` (not `<details>`):
- `<details>/<summary>` is a single hit target — impossible to split link + toggle without JS hacks
- Bootstrap `collapse` cleanly separates `<a>` link and `<button data-bs-toggle>` in the same row
- Bootstrap is already a declared CDN dep in `_config.yml` → move global load to `head.html`

**Active state** — Jekyll's `page.collection` variable:
- `page.collection == 'photos'` is true on any `_photos/*.md` page
- `page.url == '/photos/'` catches the index page itself
- Combined: `{% if page.collection == 'photos' or page.url == '/photos/' %}show{% endif %}`

### Task 3.5.1: Load Bootstrap Globally in head.html

- [x] Add `<link>` for `{{ site.cdn_libs.bootstrap_css }}` to `_includes/head.html`
- [x] Add `<script>` for `{{ site.cdn_libs.bootstrap_js }}` to `_includes/head.html`
- [x] Remove duplicate Bootstrap `<link>`/`<script>` tags from `_layouts/photo.html`
- [x] jQuery removed (Bootstrap 5 doesn't need it)

### Task 3.5.2: Create Collection Index Pages

- [x] Created `photos.md` at root with `permalink: /photos/` and `exclude_from_nav: true`
  - Bootstrap grid of all `site.photos` with thumbnails, title, year, labels
- [x] Created `topics.md` at root with `permalink: /topics/` and `exclude_from_nav: true`
  - List of all `site.topics` with title and excerpt
- [x] Neither page pollutes `site.photos`/`site.topics` (root files, not in collection folder)
- [x] Pages loop in sidebar has `{% unless node.exclude_from_nav %}` guard

### Task 3.5.3: Refactor sidebar.html — Photos Block

- [x] `<details>` replaced with `.sidebar-collection-header` + Bootstrap collapse
- [x] `<a>` link to `/photos/` independent of toggle button
- [x] `active` on parent link: `page.collection == 'photos' or page.url == '/photos/'`
- [x] Collapse auto-opens (`show`) on same condition
- [x] Chevron button with `aria-expanded` and `aria-label`
- [x] Map icon preserved on photos with location data

### Task 3.5.4: Refactor sidebar.html — Topics Block

- [x] Same Bootstrap collapse pattern as Photos
- [x] Active state: `page.collection == 'topics' or page.url == '/topics/'`
- [x] Collapse ID: `#sidebar-topics-list` / Journal icon added

### Task 3.5.5: Refactor sidebar.html — Labels Block

- [x] Same Bootstrap collapse pattern as Photos/Topics
- [x] Active state: `page.url == '/labels/'`
- [x] Collapse ID: `#sidebar-labels-list` / Tag icon preserved

### Task 3.5.6: Add CSS for sidebar-collection-header row

- [x] Added to `assets/css/lanyon.css`:
  - `.sidebar-collection-header` — flex row, space-between
  - `.sidebar-collapse-toggle` — borderless button, Lanyon color palette
  - `.sidebar-collapse-toggle::before { content: "+" }` — collapsed indicator (CSS only, no JS)
  - `.sidebar-collapse-toggle[aria-expanded="true"]::before { content: "\\2212" }` — expanded indicator (`−` minus sign), Bootstrap auto-updates `aria-expanded`
  - `.sidebar-nav-sublist` — consistent sublist styling with subtle separators
  - **Note**: No SVG used. Toggle is pure CSS `::before` text chars driven by Bootstrap's automatic `aria-expanded` attribute management.

### Acceptance Criteria
- [x] `/photos/` index page exists and lists all photos with thumbnail grid
- [x] `/topics/` index page exists and lists all topics
- [x] Sidebar: "Photos" label is a standalone `<a>` link to `/photos/`
- [x] Sidebar: Separate toggle button expands/collapses individual photo list
- [x] Photos section auto-expands when viewing any `/photos/*` page or `/photos/`
- [x] Topics section auto-expands when viewing any `/topics/*` page or `/topics/`
- [x] No Bootstrap loaded twice (removed from `photo.html`, global in `head.html`)
- [x] No `<details>` elements remain in sidebar (all converted)
- [x] Toggle icon switches `+` (collapsed) / `−` (expanded) via CSS `::before` — no JS required
- [x] Keyboard accessible (`aria-label`, `aria-expanded` on all buttons)
- [ ] Jekyll build succeeds without warnings (⏳ pending Docker test)

### Definition of Done
- [x] All 6 tasks ✅
- [ ] Tested in browser: expand/collapse works, active state correct (⏳ pending Docker/local build)

### Related Files
- [_includes/sidebar.html](_includes/sidebar.html) — refactored ✅
- [_includes/head.html](_includes/head.html) — Bootstrap added globally ✅
- [_layouts/photo.html](_layouts/photo.html) — duplicate Bootstrap removed ✅
- [photos.md](photos.md) — new collection index ✅
- [topics.md](topics.md) — new collection index ✅
- [assets/css/lanyon.css](assets/css/lanyon.css) — sidebar CSS added ✅
- [_config.yml](_config.yml) — `cdn_libs` already had Bootstrap URLs

---

## Phase 3.6: Photos Index with DataTables + Label Filtering

**Status**: ✅ COMPLETED (production-ready, fully tested)  
**Priority**: P1  
**Goal**: Implement sortable, searchable DataTables in `/photos/` and `/labels/` pages with URL pre-filtering and visual enhancements

### Design Decisions

**Dual-layout architecture**:
- `_layouts/photos_index.html` — All photos, searchable by title across all fields
- `_layouts/label.html` — Photos filtered by label, with slug-based pre-filtering in DOM before DataTables init

**jQuery discovery**:
- CDN variant of DataTables 2.2.2 is jQuery plugin, not ESM
- Initial assumption of "no jQuery" was incorrect; had to add jQuery 3.6.0 before DataTables scripts
- Implemented dual-API initialization for compatibility (tries `new DataTable()` first, falls back to jQuery plugin)

**Slug-based pre-filtering**:
- Label filtering builds `data-label-slugs="slug1|slug2|..."` on each row
- Removes non-matching rows from DOM **before** DataTables initialization for reliable filtering
- Slug construction: `label | downcase | replace: " ", "-" | replace: "_", "-"`

**URL parameters**:
- `/photos/?label=slug` triggers text search via DataTables API
- `/labels/?tag=slug` triggers DOM pre-filtering by removing rows first, then initializing DataTables

### Task 3.6.1: Add DataTables & jQuery CDN to _config.yml

- [x] Added entries to `cdn_libs` in `_config.yml`:
  - `jquery: "https://code.jquery.com/jquery-3.6.0.min.js"`
  - `datatables_css: "https://cdn.datatables.net/2.2.2/css/dataTables.bootstrap5.min.css"`
  - `datatables_js: "https://cdn.datatables.net/2.2.2/js/dataTables.min.js"`
  - `datatables_bs5_js: "https://cdn.datatables.net/2.2.2/js/dataTables.bootstrap5.min.js"`

### Task 3.6.2: Create _layouts/photos_index.html

- [x] Created `_layouts/photos_index.html` with:
  - jQuery loaded before DataTables scripts
  - Dual-API DataTable initialization (new DataTable + jQuery fallback)
  - Table columns: Foto (40×40px thumbnail, non-sortable), Titolo, Anno (default sort desc), Etichette, Mappa
  - Thumbnail lazy loading with fallback chain: `photo.processed_primary_thumb` → `photo.processed_primary_image` → `photo.primary_image`
  - "Mappa" column shows ✓ indicator when photo has location data (sortable)
  - Default sort: Year descending, 25 rows/page
  - Italian language localization
  - URL pre-filter: `?label=slug` → `table.search(slug.replace(/-/g, ' ')).draw()`
  - Error logging to console if DataTables fails to load

### Task 3.6.3: Enhance _layouts/label.html

- [x] Added jQuery loaded before DataTables scripts
- [x] Implemented slug-based pre-filtering:
  - Builds `data-label-slugs` attribute on each row with pipe-separated label slugs
  - Removes rows not containing the selected tag **before** DataTables init
  - Highlights active label badge with `text-bg-primary` class
- [x] Updated table columns to match photos_index: Foto (40×40px, non-sortable), Titolo, Anno (default sort desc), Etichette, Mappa (sortable)
- [x] Dual-API DataTable initialization with error logging
- [x] Italian language localization matching photos_index

### Task 3.6.4: Remove Bootstrap duplicates

- [x] Removed inline `<link rel="stylesheet">` Bootstrap CSS from `_layouts/label.html` (now global in `head.html`)
- [x] Removed inline `<script src>` Bootstrap JS from `_layouts/label.html`

### Task 3.6.5: Enable Mappa column sorting

- [x] Removed Mappa column (index 4) from non-sortable targets in both layouts
- [x] Updated `columnDefs` to: `{ orderable: false, searchable: false, targets: [0] }` (Foto column only)
- [x] Mappa column now sortable by indicating presence of location data

### Acceptance Criteria

- [x] `/photos/` renders sortable, searchable DataTable of all photos
- [x] `/labels/` renders sortable, searchable DataTable filtered by label with slug pre-filtering
- [x] Thumbnail column shows 40×40px image (non-sortable, non-searchable)
- [x] Title column links to individual photo page, searchable
- [x] Year column is sortable with default sort descending
- [x] Labels column shows clickable badge links to `/labels/?tag=...`, non-sortable, non-searchable
- [x] Mappa column shows ✓ indicator when location data present, **sortable**, non-searchable
- [x] `?label=slug` pre-filters photos_index table on load via text search
- [x] `?tag=slug` pre-filters label.html table on load via DOM row removal
- [x] DataTables controls render correctly: search, pagination, page length, info
- [x] jQuery loads before DataTables without dependency errors
- [x] Dual-API initialization provides graceful fallback and error logging
- [x] No Bootstrap loaded twice (duplicates removed from label.html)
- [x] DataTables CDN pinned at 2.2.2 in `_config.yml` (Single Source of Truth)
- [x] Browser test: sort, filter, paginate all work correctly ✅

### Bug Fixes Completed

1. **jQuery Dependency Error**: CDN DataTables v2.2.2 was jQuery plugin variant
   - Symptom: Browser console `ReferenceError: jQuery is not defined`
   - Fix: Added jQuery 3.6.0 load before DataTables scripts
   - Applied to: both `photos_index.html` and `label.html`

2. **Label Filtering Not Working**: `/labels/?tag=via-carmine` showed all photos instead of filtered
   - Symptom: Text search method was unreliable for matching label slugs
   - Root cause: Global search doesn't match specific label slug patterns reliably
   - Fix: Pre-filter rows in DOM by building `data-label-slugs` attribute, remove non-matching rows before DataTables init
   - Result: Filtering now deterministic (verified: 3 photos have "via-carmine" label)

3. **DataTables Controls Not Rendering**: Search box, pagination, entries-per-page dropdown were invisible
   - Root cause: jQuery dependency error prevented initialization
   - Fix: Resolved jQuery issue above
   - Result: Controls now render correctly with hard page refresh

### Definition of Done
- [x] All 5 tasks completed ✅
- [x] Both layout files tested in browser ✅
- [x] Sorting works on all non-disabled columns including Mappa ✅
- [x] Filtering works via URL parameters and text search ✅
- [x] Pagination and entries-per-page selector functional ✅
- [x] No console errors, graceful error logging in place ✅

### Related Files
- [_layouts/photos_index.html](_layouts/photos_index.html) — new layout ✅
- [photos.md](photos.md) — updated to use photos_index layout ✅
- [_config.yml](_config.yml) — DataTables CDN added to cdn_libs ✅
- [_layouts/label.html](_layouts/label.html) — Bootstrap duplicate removed ✅

---

## Phase 4: Docker Multi-Stage Build

**Status**: not-started  
**Owner**: [Assign]  
**Priority**: P2  
**Goal**: Create production-ready Docker pipeline: Python → Jekyll → Nginx

### Description
Multi-stage Dockerfile:
- **Stage 1**: Python 3.11 + process_research.py (generates _photos/)
- **Stage 2**: Ruby 3.2 + Jekyll build (generates _site/)
- **Stage 3**: Minimal Nginx (serves _site/)

Plus `.dockerignore` to exclude `archive/` (private data)

### Acceptance Criteria
- [ ] Stage 1 runs Python script, outputs to `_photos/` + `assets/`
- [ ] Stage 2 reads generated _photos/, builds site
- [ ] Stage 3 serves only `_site/` on port 80
- [ ] Image size optimized (no unused layers)
- [ ] `.dockerignore` excludes `archive/`
- [ ] `docker compose up` starts correctly
- [ ] No build warnings about missing files

### Dependencies
- [ ] Phase 1 complete (process_research.py exists)
- [ ] Phase 2 complete (_config.yml configured)

### Related Files
- [Dockerfile](Dockerfile) - Update to multi-stage
- [docker-compose.yml](docker-compose.yml)
- [.dockerignore](.dockerignore) - Create if not exists
- [Makefile](Makefile) - Already has `make build`, `make serve`

---

## Phase 5: Asset Refactor (public/ → assets/)

**Status**: not-started  
**Owner**: [Assign]  
**Priority**: P3  
**Goal**: Consolidate CSS/JS from Lanyon theme under `assets/` structure

### Description
Move theme resources to follow Jekyll standards:
- CSS: `public/css/` → `assets/css/`
- JS: `public/js/` → `assets/js/`
- Update references in `_includes/head.html` + `_includes/sidebar.html`

### Acceptance Criteria
- [ ] All CSS files moved to `assets/css/`
- [ ] All JS files moved to `assets/js/`
- [ ] `_includes/head.html` updated with new paths
- [ ] `_includes/sidebar.html` updated with new paths
- [ ] No broken links in built _site/
- [ ] Page loads correctly locally
- [ ] Git commit reflects move (no content changes)

### Dependencies
- [ ] Phases 1-4 working

### Notes
Low priority—visual polish phase. Only after core pipeline works.

---

## Key Principles (from copilot-instructions.md)

✅ **Single Source of Truth**: Configuration in `_config.yml` or PROJECT_MAP.md  
✅ **No Magic Numbers**: All constants documented  
✅ **No Silent Failures**: Log all errors to console  
✅ **Validate All URLs**: CDN + SRI hashes  
✅ **One-Way Pipeline**: `raw_data/` → `_photos/` → `_site/` (never hand-edit generated)  
✅ **Parent-Variant Pattern**: One object = one `.md` file with primary + variants array (no duplicate entries)

---

## Notes for Next Session

---

## Active TODO List (as of 2026-02-27)

### Map & Photo Frontmatter Integration

- [x] Extract GeoJSON from frontmatter in photo.html (`origin_geojson`, `fov_geojson`, `line_of_sight_geojson`)
- [x] Pass GeoJSON variables to JavaScript in photo.html (`window.photoOriginGeoJson`, `window.photoFovGeoJson`, `window.photoLineGeoJson`)
- [x] Add GeoJSON layer config to LAYER_CONFIG in myscript.js (`PHOTO_ORIGIN`, `PHOTO_FOV`, `PHOTO_LINE`)
- [x] Created `addIndividualGeoJsonLayers()` function in myscript.js (line 801)
- [x] Layer styling for origin/fov/line layers defined in LAYER_CONFIG entries
- [x] `initMap()` calls `addIndividualGeoJsonLayers()` (line 190)
- [ ] End-to-end test with Piazza_Carmine-anni-1940-1950.md (requires Docker build + real frontmatter GeoJSON fields)

**Status:** ✅ Fully implemented. Only remaining item is end-to-end integration test via Docker.
