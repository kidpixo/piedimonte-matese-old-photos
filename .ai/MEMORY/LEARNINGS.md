# Session Learnings & Pattern Log

**Purpose**: Capture architectural lessons, gotchas, and patterns to avoid repetition  
**Owner**: Development team / AI agents  
**Update Frequency**: End of each session (via .github/prompts/harvest-learning.md)

---

## How to Log a Learning

```markdown
## [Date] - [Issue Title]

**Problem**: What was the issue or surprise?  
**Context**: Where did it occur? What were we trying to do?  
**Root Cause**: Why did it happen?  
**Solution**: How did we fix it?  
**Lesson**: One-sentence rule to avoid recurrence  
**Impact**: High | Medium | Low (how often will this matter?)  
**Tags**: `#CORS`, `#config`, `#browser-compat`, `#jekyll`, `#gis`, etc.  
**Related Task**: Link to IMPLEMENTATION_STEPS.md task if applicable  
**Code Example** (optional):
```language
// Insert code snippet showing the fix
```

---

## Learning Categories

### Configuration & Secrets
Issues with .yml files, environment variables, hardcoded values

### Browser Compatibility
CSS/JavaScript issues across Chrome, Firefox, Safari, Edge

### Performance
Slow load times, large assets, network bottlenecks

### Geographic / GIS
Coordinate systems, projections, tile servers, CORS with CDN

### Jekyll / Static Site Gen
Build quirks, template inheritance, frontmatter, plugins

### Data Pipeline
Encoding, CSV parsing, JSON validation

### Accessibility
ARIA, keyboard navigation, screen readers

### Deployment
GitHub Pages, DNS, certificate issues

---

## Session Learnings (Start Here)

(Learnings logged here will be rolled forward to this permanent log)

### Session 2 - Phase 1 Data Pipeline Complete (2026-02-22)

#### GeoJSON Generation: Manual JSON vs geopandas
**Problem**: `generate_geojson()` created empty FeatureCollection despite successful image processing.  
**Context**: Script processed 9 photos, optimized images, created thumbnails, but GeoJSON had `features: []`.  
**Root Cause**: Manual JSON generation from Shapely geometries loses serialization; `Point`/`Polygon` objects aren't directly JSON-serializable.  
**Solution**: Switched to geopandas GeoDataFrame with `.to_file(driver="GeoJSON")`. Matches proven pattern from existing `convert_photos_coords.py`.  
**Lesson**: Always use framework serializers (geopandas, sqlalchemy, etc.) for complex objects; avoid manual JSON construction for geometries.  
**Impact**: High (geospatial data is irreplaceable; silent failures are critical)  
**Tags**: `#gis`, `#json`, `#geopandas`, `#data-pipeline`

#### Two-File GeoJSON Pattern for Photography
**Problem**: Initial implementation tried single `geojson.geojson` file.  
**Context**: Photo metadata has dual representation: origin point (camera) + field-of-view polygon (triangle).  
**Solution**: Generate two separate files: `photos_origin.geojson` (Points) + `photos_fov.geojson` (Polygons).  
**Lesson**: Separate GeoJSON by geometry type and semantic meaning. Enables richer map visualization and flexible downstream consumption.  
**Impact**: High (enables richer map rendering)  
**Tags**: `#gis`, `#design-patterns`, `#data-architecture`

#### GeoJSON Generation: Manual JSON vs geopandas
**Problem**: `generate_geojson()` created empty FeatureCollection despite successful image processing.  
**Context**: Script processed 9 photos, optimized images, created thumbnails, but GeoJSON had `features: []`.  
**Root Cause**: Manual JSON generation from Shapely geometries loses serialization; `Point`/`Polygon` objects aren't directly JSON-serializable.  
**Solution**: Switched to geopandas GeoDataFrame with `.to_file(driver="GeoJSON")`. Matches proven pattern from existing `convert_photos_coords.py`.  
**Lesson**: Always use framework serializers (geopandas, sqlalchemy, etc.) for complex objects; avoid manual JSON construction for geometries.  
**Impact**: High (geospatial data is irreplaceable; silent failures are critical)  
**Tags**: `#gis`, `#json`, `#geopandas`, `#data-pipeline`

#### Two-File GeoJSON Pattern for Photography
**Problem**: Initial implementation tried single `geojson.geojson` file.  
**Context**: Photo metadata has dual representation: origin point (camera) + field-of-view polygon (triangle).  
**Solution**: Generate two separate files: `photos_origin.geojson` (Points) + `photos_fov.geojson` (Polygons).  
**Lesson**: Separate GeoJSON by geometry type and semantic meaning. Enables richer map visualization and flexible downstream consumption.  
**Impact**: High (enables richer map rendering)  
**Tags**: `#gis`, `#design-patterns`, `#data-architecture`

#### Parent-Variant Pattern Successfully Implemented
**Problem**: Unclear how to represent multiple image variants per photo object.  
**Context**: Photos have primary image + optional variants (file/type/note metadata).  
**Solution**: One `.md` file per research object = parent; variants as array in frontmatter. Prevents data drift (update once, all variants inherit).  
**Lesson**: Single source of truth at object level, not per-image. Variants are object properties, not separate entities.  
**Impact**: Medium (architectural; prevents future refactoring)  
**Tags**: `#data-architecture`, `#jekyll`, `#design-patterns`

### Session 1 - Bootstrap (Prior)

#### Ruby/Jekyll Version Incompatibility
**Problem**: Dockerfile used `ruby:3.3-slim` with Jekyll 3.9.3, caused `undefined method '[]' for nil (NoMethodError)` in Logger.  
**Solution**: Downgraded to `ruby:3.2-slim` (Jekyll 3.9.3 incompatible with Ruby 3.3 Logger API).  
**Lesson**: Match Ruby/Jekyll/gem-pages versions carefully; check CHANGELOG for compatibility.  
**Impact**: High (blocks all Docker builds)  
**Tags**: `#ruby`, `#jekyll`, `#docker`

#### Docker Layer Caching Optimization
**Problem**: Copying entire source before dependencies invalidated cache on every source change.  
**Solution**: Reordered Dockerfile: Gemfile → bundle install → then copy source.  
**Lesson**: Layer order matters; dependencies before source changes.  
**Impact**: Medium (development velocity)  
**Tags**: `#docker`, `#optimization`

---

## Permanent Pattern Library

(Archive of lessons that influenced major decisions or prevented recurrence)

### GitHub Pages Constraints
**Lesson**: GitHub Pages has no backend, no build pipeline, no environment variables in JavaScript at runtime.  
**Fix**: Inject secrets via Jekyll config at build time, inject into `window.config` in HTML template.  
**Tags**: `#github-pages`, `#config`, `#secrets`  
**Impact**: High (affects all external API usage)

### CDN URL Validation
**Lesson**: CDN URL changes break silently; end users never know until they complain.  
**Fix**: Validate all CDN URLs in IMPLEMENTATION_STEPS.md checkpoint. Pin versions. Use SRI hashes to detect tampering.  
**Tags**: `#cdn`, `#security`, `#release`  
**Impact**: High (prevents outages)

### CORS Headers Missing
**Lesson**: Tiles and GeoJSON loaded from external service fail silently if CORS headers absent.  
**Fix**: Test fetch in browser DevTools before deploying. Use `mode: 'cors'` in fetch options. Choose CORS-friendly tile servers.  
**Tags**: `#CORS`, `#gis`, `#browser`  
**Impact**: Medium (affects map rendering)

### Coordinate System Confusion
**Lesson**: Easy to confuse WGS84 (lat/lng) with projected coordinates (meters). Causes markers to appear in wrong locations.  
**Fix**: Document projection in PROJECT_MAP.md Data Sources section. Validate coordinates visually on map before commit.  
**Tags**: `#gis`, `#data`, `#validation`  
**Impact**: Medium (affects all geographic work)

---

## Quick Reference Tags

Search by tag to find related learnings:

- `#config` - Configuration and constants
- `#CORS` - Cross-origin resource sharing
- `#browser-compat` - Browser-specific issues
- `#jekyll` - Jekyll/static site generator quirks
- `#gis` - Geographic / mapping work
- `#data` - Data processing and validation
- `#security` - Security and secret management
- `#performance` - Load time and optimization
- `#accessibility` - ARIA and accessibility
- `#github-pages` - GitHub Pages specific limits
- `#release` - Deployment and production issues

---

## Decision Replay

When in doubt, check if this decision tree has already been decided:

- [ ] Should library come from CDN or npm? → **Always CDN for GitHub Pages**
- [ ] Where to store config values? → **_config.yml, never hardcoded in JS**
- [ ] How to handle missing data? → **Log error, show fallback UI, don't fail silently**
- [ ] Which tile server? → **OSM (free, CORS-friendly), not Bing (keys needed)**
- [ ] How to share state? → **URL params for reproducible links, localStorage for session**

---

## 2026-02-25 - Phase 2: Jekyll Configuration Complete

**Problem**: Collection permalinks used wrong pattern and CDN libraries were scattered across layout files  
**Context**: `_config.yml` had `/archive/:name/` instead of `/photos/:slug/`, violating PROJECT_MAP.md spec. CDN URLs hardcoded in map.html and photo.html layouts.  
**Root Cause**: Initial Jekyll setup didn't follow the "Single Source of Truth" principle from copilot-instructions.md  
**Solution**: 
1. Fixed permalinks: `/archive/:name/` → `/photos/:slug/`, `:name` → `:slug` for topics
2. Centralized all CDN URLs in `_config.yml` under `cdn_libs` section
3. Documented 9 CDN libraries with pinned versions (Leaflet, jQuery, Bootstrap, georaster, etc.)

**Lesson**: Always centralize configuration in `_config.yml`—never hardcode paths or CDN URLs in layouts  
**Impact**: High (affects all future CDN updates and URL consistency)  
**Tags**: `#config`, `#jekyll`, `#cdn`, `#single-source-of-truth`  
**Related Task**: [IMPLEMENTATION_STEPS.md Phase 2](../IMPLEMENTATION_STEPS.md#phase-2-jekyll-configuration-collections--paths)  

**Next Step**: Refactor `_layouts/map.html` and `_layouts/photo.html` to use `{{ site.cdn_libs.leaflet_js }}` instead of hardcoded URLs (deferred to Phase 3)

**Code Example**:
```yaml
# _config.yml centralized CDN configuration
cdn_libs:
  leaflet_css: "https://cdn.jsdelivr.net/npm/leaflet@1.9.4/dist/leaflet.css"
  leaflet_js: "https://cdn.jsdelivr.net/npm/leaflet@1.9.4/dist/leaflet.min.js"
  # ... 7 more libs
```

---

## 2026-02-25 - Sidebar Bootstrap Dependency Violation

**Problem**: Sidebar used Bootstrap collapse component but Bootstrap wasn't loaded globally  
**Context**: `_includes/sidebar.html` had collapsible Photos menu using `data-bs-toggle="collapse"`, but Bootstrap CSS/JS only loads in photo.html and map.html layouts, not in default.html  
**Root Cause**: 
1. Sidebar incorrectly queried `site.pages | where_exp: "item", "item.layout == 'photo'"` instead of using `site.photos` collection
2. Bootstrap dependency violated "No Build Pipeline" constraint—external dependencies should work everywhere or not be used
3. No Topics section at all (missing collection menu)

**Solution**: 
1. Replaced Bootstrap collapse with HTML5 `<details>/<summary>` (native, zero dependencies)
2. Fixed collection query: `site.pages` → `site.photos` and added `site.topics`
3. Added item counts: "Photos (2)", "Topics (0)" for user visibility
4. Sorted photos by date (newest first), topics by title

**Lesson**: Never use framework components (Bootstrap/jQuery) unless loaded globally—prefer native HTML5 features for core UI  
**Impact**: High (sidebar is on every page)  
**Tags**: `#bootstrap`, `#dependencies`, `#collections`, `#html5`, `#accessibility`  
**Related Task**: [IMPLEMENTATION_STEPS.md Phase 2](../IMPLEMENTATION_STEPS.md#phase-2-jekyll-configuration-collections--paths)  

**Code Example**:
```liquid
<!-- Before: Bootstrap-dependent (broken) -->
<button data-bs-toggle="collapse" data-bs-target="#photosMenu">Photos</button>
{% assign photos_list = site.pages | where_exp: "item", "item.layout == 'photo'" %}

<!-- After: Native HTML5 (works everywhere) -->
<details class="sidebar-nav-item">
  <summary style="cursor:pointer;">Photos ({{ site.photos.size }})</summary>
  {% for photo in site.photos %}...{% endfor %}
</details>
```

---

## 2026-02-25 - Phase 3: Layout Templates Complete (Photo, Topic, Label)

**Problem**: Photos were bare (no thumbnail display), topics & labels had no dedicated UI, sidebar Bootstrap dependency was broken  
**Context**: Implementing Layer 4 & 5 from PROJECT_MAP.md (editorial essays + tag browsing)  
**Root Cause**: Initial layouts were placeholders; sidebar tried to use Bootstrap without loading it globally

**Solution**:
1. **photo.html enhancements**:
   - Extract `latitude_origin`/`longitude_origin` from location array (both old `lat`/`lon` and new structure)
   - Render primary image thumbnail as clickable link to full-size
   - Gate map rendering on presence of location coordinates
   - Conditionally load Leaflet/map scripts only when needed

2. **topic.html created**:
   - Reads `featured_photos` array from frontmatter
   - Joins photo data via `site.photos | where: "slug", item.id | first`
   - Displays thumbnail + commentary for each featured photo
   - Links to full photo detail pages

3. **Label system added**:
   - Extract unique labels from all photos at build-time
   - Compute counts per label (via nested Liquid loop)
   - Added submenu to sidebar with sorted labels + counts
   - Created `label.html` layout with dual views:
     - Index: all labels as clickable cards
     - Filtered: photos matching selected label (client-side JS)
   - URL query param `?tag=...` toggles between views

4. **Sidebar refactor**:
   - Fixed order: Pages → Photos → Topics → Labels (logical hierarchy)
   - All collections use HTML5 `<details>/<summary>` (no Bootstrap)
   - Removed hardcoded `site.pages` query; now uses proper collections

**Lesson**: Use native HTML5 features (`<details>`) for progressive enhancements—avoid framework dependencies for core UI

**Impact**: High (photos now visible, editorial layer working, label discovery enabled)  
**Tags**: `#layouts`, `#collections`, `#jekyll`, `#liquid`, `#progressive-enhancement`, `#client-side-filtering`  
**Related Tasks**: [IMPLEMENTATION_STEPS.md Phase 3](../IMPLEMENTATION_STEPS.md#phase-3-layout-templates-phothtml--topichtml--labelhtml-enhancements)

**What remains**: 
- Variant image support in photo.html (Parent-Variant pattern)
- jekyll build validation (Docker/podman required)
- Lazy loading optimization (`loading="lazy"`)

**Code Example** (extracting labels with counts):
```liquid
{% assign all_labels = "" | split: "" %}
{% for photo in site.photos %}
  {% for label in photo.labels %}
    {% unless all_labels contains label %}
      {% assign all_labels = all_labels | push: label %}
    {% endunless %}
  {% endfor %}
{% endfor %}
{% for label in all_labels | sort %}
  {% assign count = 0 %}
  {% for photo in site.photos %}
    {% if photo.labels contains label %}
      {% assign count = count | plus: 1 %}
    {% endif %}
  {% endfor %}
  <!-- Render: {{ label }} ({{ count }}) -->
{% endfor %}
```

---

## Session Handoff Template

(Copy this to next session's notes section at end of session)

### End-of-Session Summary

**Date**: [Date]  
**Duration**: [Hours]  
**Tasks Completed**:
- [ ] Task 1
- [ ] Task 2

**Blockers Encountered**:
- [Blocker 1]: [Status]

**Learnings Captured**:
- [Learning 1 title] (see section above)

**Next Session Should**:
- [ ] [Action 1]

---

**Legend**: This file grows with each session. Never delete entries; they form the institutional memory of the project.
