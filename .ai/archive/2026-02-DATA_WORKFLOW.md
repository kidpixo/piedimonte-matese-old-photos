# Data Workflow: Photo Discovery to Map Display

**Status**: Exploratory / In Discussion  
**Last Updated**: 2026-02-20  
**Related**: [PROJECT_MAP.md](PROJECT_MAP.md) (Layer 3: Data Pipeline)

---

## Overview

This document describes the end-to-end workflow for adding a historical photo to the site, from discovery through map display.

**Two sources of truth, each owning different concerns:**

| Concern | Owner | Format | Why |
|---------|-------|--------|-----|
| **Geo data** (coordinates, FOV, boresight) | `public/photos/Photos.csv` | CSV | QGIS exports CSV natively; manual coord entry in YAML is impractical |
| **Narrative data** (title, description, subjects, tags) | `photos/<name>.md` front-matter | YAML + Markdown | Jekyll consumes it directly; rich text lives here |
| **Map layers** (points, FOV polygons) | `public/data/*.geojson` | GeoJSON | **Derived** from CSV, consumed by Leaflet |

```
┌─────────────────────────────────────────────────────────────────────┐
│                        DATA FLOW DIAGRAM                            │
│                                                                     │
│  ┌──────────┐     ┌──────────┐     ┌──────────────────┐            │
│  │ Facebook │     │ Internet │     │ Physical Archive  │            │
│  │ groups   │     │ sources  │     │ (scans, prints)   │            │
│  └────┬─────┘     └────┬─────┘     └────────┬─────────┘            │
│       │                │                     │                      │
│       └────────────────┼─────────────────────┘                      │
│                        │                                            │
│                        ▼                                            │
│              ┌─────────────────┐                                    │
│              │  STEP 1: SAVE   │                                    │
│              │  Save image to  │                                    │
│              │  public/photos/ │                                    │
│              └────────┬────────┘                                    │
│                       │                                             │
│          ┌────────────┼────────────┐                                │
│          ▼                         ▼                                │
│  ┌───────────────┐       ┌─────────────────┐                       │
│  │ STEP 2a: GEO  │       │ STEP 2b: PAGE   │                       │
│  │ Open QGIS     │       │ Create .md with │                       │
│  │ Pinpoint on   │       │ front-matter    │                       │
│  │ map → update  │       │ (title, desc,   │                       │
│  │ Photos.csv    │       │ subjects, tags) │                       │
│  └───────┬───────┘       └─────────────────┘                       │
│          │                                                          │
│          ▼                                                          │
│  ┌───────────────────┐                                              │
│  │ STEP 3: EXPORT    │                                              │
│  │ Run Python script │                                              │
│  │ CSV → GeoJSON     │                                              │
│  │ (points + FOV)    │                                              │
│  └───────┬───────────┘                                              │
│          │                                                          │
│          ▼                                                          │
│  ┌───────────────────┐                                              │
│  │ STEP 4: COMMIT    │                                              │
│  │ git add + push    │                                              │
│  │ GitHub Pages      │                                              │
│  │ serves static     │                                              │
│  └───────┬───────────┘                                              │
│          │                                                          │
│          ▼                                                          │
│  ┌───────────────────┐                                              │
│  │ STEP 5: DISPLAY   │                                              │
│  │ Leaflet loads     │                                              │
│  │ GeoJSON (map)     │                                              │
│  │ Liquid renders    │                                              │
│  │ photo page (site) │                                              │
│  └───────────────────┘                                              │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Step 1: Save the Image

**Input**: Photo found on Facebook, internet, or scanned from physical archive  
**Output**: Image file in `public/photos/`

### What to capture at discovery time

- [ ] Image file saved (JPG, PNG, or WEBM for video)
- [ ] Source URL (Facebook post, archive link)
- [ ] Any caption/description from the source
- [ ] Approximate date (from post, comments, visual cues)
- [ ] Names of people/places mentioned in comments

### Naming convention

```
<subject>_<location>_<approx_year>.jpg
# Examples:
OrologiaioCarnevale_PiazzaCarmine_fianco-BarCarletto-1900.jpg
abatttimento_ciminiera_1972.jpg
ponte_torano_verso_piazza_carmine_anni70.jpg
```

### Open questions

- [ ] Should we store original resolution or resize?
- [ ] Do we keep the Facebook URL as attribution?
- [ ] Copyright/license status of each photo?

---

## Step 2a: Geo-Reference in QGIS

**Input**: Image + local knowledge of the location  
**Output**: Updated row in `public/photos/Photos.csv`

### What QGIS captures

For each photo, the operator manually places **3 points** on the map:

| Point | CSV Columns | Meaning |
|-------|------------|---------|
| **Origin** | `latitude_origin`, `longitude_origin` | Where the photographer stood |
| **Left vertex** | `latitude_vertex_left`, `longitude_vertex_left` | Left edge of frame |
| **Right vertex** | `latitude_vertex_right`, `longitude_vertex_right` | Right edge of frame |

These 3 points define a **field-of-view (FOV) triangle**.

### CSV schema (current)

```csv
filename,width,height,latitude_origin,longitude_origin,latitude_vertex_left,longitude_vertex_left,latitude_vertex_right,longitude_vertex_right,text,time
```

### Partially filled rows are OK

Not every photo can be geo-referenced (unknown location, indoor shots, etc.).  
Rows with empty coordinates are **skipped** during GeoJSON export.

### Open questions

- [ ] Should we add a `confidence` column? (exact / approximate / unknown)
- [ ] Should we add a `source_note` column? (how location was determined)
- [ ] Is the FOV triangle always needed, or just origin point sometimes?

---

## Step 2b: Create Photo Page

**Input**: Image file + discovery notes  
**Output**: `photos/<name>.md` with front-matter

### Front-matter template

```yaml
---
layout: photo
title: "Piazza Carmine con Ciminiera"
date: 1970              # approximate year
image: piazzacarmine_con_ciminiera.jpg
facebook_url: "https://www.facebook.com/photo/?fbid=..."

# Display settings for per-photo map (if coordinates exist in CSV)
center_lat: 41.355946   # can be derived from CSV origin
center_lng: 14.370868   # can be derived from CSV origin
zoom: 18
map_height: "500px"

# Narrative metadata (not in CSV)
tags:
  - piazza-carmine
  - ciminiera
  - cotonificio
subject:
  name: ""
  description: ""
---

Foto di Piazza Carmine con Ciminiera, prima del 1972.
Narrative content, historical context, identification notes...
```

### What lives HERE vs CSV

| Data | In front-matter | In CSV | Why |
|------|----------------|--------|-----|
| Title / description | ✅ | ❌ | Rich text, Jekyll needs it |
| Tags / subjects | ✅ | ❌ | Jekyll collections, Liquid filters |
| Facebook URL | ✅ | ❌ | Attribution, not geo data |
| Coordinates | ✅ (derived) | ✅ (source) | CSV is source; front-matter gets injected |
| FOV vertices | ❌ | ✅ | Only map needs this (GeoJSON) |
| Boresight | ❌ | ✅ (derived) | Calculated by export script |
| Image dimensions | ❌ | ✅ | Used for FOV scaling |

### Open questions

- [ ] Should `center_lat`/`center_lng` be injected from CSV automatically?
- [ ] Or should the photo page just link to the main map with `?photo=filename`?
- [ ] Do we need a per-photo mini-map, or just a link to the overview map?

---

## Step 3: Export GeoJSON

**Input**: `public/photos/Photos.csv`  
**Output**: 
- `public/data/photos_origin.geojson` (Point layer — photographer locations)
- `public/data/photos_fov.geojson` (Polygon layer — field-of-view triangles)

### Current script

`public/scripts/convert_photos_coords.py` (Jupyter notebook, uses pandas + geopandas + shapely)

### What it does

1. Reads `Photos.csv`, drops rows with empty coordinates
2. Creates Point geometry from `(longitude_origin, latitude_origin)`
3. Creates Polygon geometry from origin + left vertex + right vertex (FOV triangle)
4. Calculates boresight vector (camera direction, midpoint of FOV angle)
5. Exports two GeoJSON files:
   - `photos_origin.geojson` — point per photo (for markers on map)
   - `photos_fov.geojson` — triangle per photo (for FOV overlay on map)

### Derived fields added by script

| Field | Source | Purpose |
|-------|--------|---------|
| `x_boresight` | Calculated from vertex vectors | Camera direction (x component) |
| `y_boresight` | Calculated from vertex vectors | Camera direction (y component) |
| Scaled `width`/`height` | From CSV, normalized to 2m | A-Frame display sizing (legacy?) |

### When to run

```bash
cd public/scripts
python convert_photos_coords.py
# or: make geojson (if added to Makefile)
```

**Run after**: Any update to Photos.csv  
**Run before**: `git commit` and `jekyll build`

### Open questions

- [ ] Should we add a Makefile target for this? (`make geojson`)
- [ ] Should we validate the GeoJSON output? (schema check)
- [ ] Should we add the export to a pre-commit hook?
- [ ] The boresight calculation looks buggy — it uses `photos_df` (all rows) instead of `row` per-row. Investigate.
- [ ] The A-Frame width/height scaling — is this still needed or legacy from a VR prototype?
- [ ] Should we also generate a combined `photos_all.geojson` with both points and FOV?

---

## Step 4: Commit and Deploy

**Input**: Updated CSV + GeoJSON + photo pages  
**Output**: Static site on GitHub Pages

### Commit workflow

```bash
# After adding/updating a photo:
git add public/photos/<new_image>.jpg           # image file
git add public/photos/Photos.csv                # updated CSV
git add photos/<name>.md                        # photo page
git add public/data/photos_origin.geojson       # regenerated
git add public/data/photos_fov.geojson          # regenerated
git commit -m "Add photo: <description>"
git push
```

### No build step needed on GitHub Pages

- Jekyll handles `.md` → HTML via Liquid templates (standard GitHub Pages)
- GeoJSON files are static assets served as-is
- No custom plugins required

### Optional: GitHub Actions automation

Could automate Step 3 (CSV → GeoJSON export) on push:
- Trigger on changes to `public/photos/Photos.csv`
- Run `convert_photos_coords.py`
- Auto-commit regenerated GeoJSON
- See `.github/workflows/` for implementation

**Decision needed**: Manual local export vs. automated CI export?

---

## Step 5: Display

### Overview map (all photos)

- Leaflet.js loads `photos_origin.geojson` → markers for all photos
- Leaflet.js loads `photos_fov.geojson` → FOV triangles overlay
- Layer control toggles points / FOV / historical maps
- Popup on marker click → thumbnail + link to photo page

### Per-photo page

- Liquid template checks if `center_lat` / `center_lng` exist in front-matter
- If yes → render mini-map centered on photo location
- If no → skip map section (graceful degradation)
- Narrative content rendered below

### Open questions

- [ ] Should the overview map link to individual photo pages?
- [ ] Should clicking a photo page marker open the photo overlay on the main map?
- [ ] URL scheme: `/photos/name/` or `/photos/?id=name`?

---

## Summary: What Runs Where

| Step | Where | Automated? | Output |
|------|-------|-----------|--------|
| 1. Save image | Local machine | No (manual) | `public/photos/*.jpg` |
| 2a. Geo-reference | QGIS (local) | No (manual) | `Photos.csv` row updated |
| 2b. Create page | Text editor (local) | No (manual) | `photos/*.md` |
| 3. Export GeoJSON | Python (local) | **Could automate** | `public/data/*.geojson` |
| 4. Deploy | `git push` → GitHub Pages | Yes (auto) | Live site |
| 5. Display | Browser (Leaflet + Liquid) | Yes (auto) | Map + photo pages |

---

## Decisions Log

| Decision | Status | Notes |
|----------|--------|-------|
| CSV as geo source of truth | ✅ Decided | QGIS workflow requires it |
| Front-matter as narrative source | ✅ Decided | Jekyll needs it |
| GeoJSON is derived (not manually edited) | ✅ Decided | Always regenerated from CSV |
| Per-photo mini-map | ❓ Open | Depends on `center_lat` in front-matter |
| Inject CSV coords → front-matter | ❓ Open | Automation TBD |
| GitHub Actions for GeoJSON export | ❓ Open | Could replace local export step |
| Makefile target for export | ❓ Open | Convenience vs. complexity |
| Boresight/A-Frame fields | ❓ Open | Legacy? Still needed? |

---

## Next Steps

1. **Fix the export script** — boresight calculation may be buggy (uses global df instead of per-row)
2. **Decide on per-photo maps** — mini-map vs. link to overview map
3. **Add Makefile target** — `make geojson` to standardize the export step
4. **Validate with a new photo** — walk through the full workflow end-to-end
5. **Update PROJECT_MAP.md** — once decisions are locked
