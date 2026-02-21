# Project Architecture Map

**Last Updated**: [Date]  
**Primary Context Source**: This file  
**Update Frequency**: After major architectural decisions

---

## Project Summary

**Name**: [Project Name]  
**Type**: Jekyll Static Site (GitHub Pages)  
**Purpose**: [One-line project mission]  
**Hosting**: GitHub Pages (CDN-only, no backend)

---

## Core Stack

| Component | Technology | Notes |
|-----------|-----------|-------|
| Site Gen | Jekyll (Ruby) | No build pipeline, direct HTML output |
| Frontend | HTML/CSS/JavaScript | No frameworks, CDN libs only |
| Styling | [CSS/SASS] | [location] |
| Maps/GIS | [e.g., Leaflet.js] | [CDN URL + version] |
| Data Format | [GeoJSON/CSV/JSON] | [sourcing] |
| Deployment | GitHub Pages | Static only, no functions |

---

## Architecture Layers

### Layer 1: Static Content
- **Files**: `_layouts/`, `_posts/`, `_includes/`
- **Config**: `_config.yml`
- **Output**: HTML served as-is

### Layer 2: Frontend Logic
- **Files**: `public/js/`
- **CDN Dependencies**: [List with pinned URLs]
- **Constraints**: No npm, no build step

### Layer 3: Data Pipeline
- **Source**: [CSV/GeoJSON files location]
- **Processing**: [Python/bash scripts, if any]
- **Output**: [Format and location]

### Layer 4: External APIs
- **Services Used**: [OSM, Bing, etc.]
- **API Keys**: [Environment variables, never hardcoded]
- **Fallbacks**: [Graceful degradation plan]

---

## Configuration Single Source of Truth

### Key Settings (Central in `_config.yml`)

```yaml
site_name: [Project Name]
base_url: https://[username].github.io/[repo]/
cdn_libs:
  leaflet: https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js
  leaflet_css: https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css
api_keys:
  bing: <%= ENV['BING_API_KEY'] || '' %>
  stadia: <%= ENV['STADIA_KEY'] || '' %>
```

### Shared Constants

**Document all magic numbers and constants in one place:**

```javascript
// public/js/config.js - Generated from _config.yml at build time
const APP_CONFIG = {
  siteUrl: "{{ site.base_url }}",
  version: "{{ site.version }}",
  defaultZoom: 18,
  centerLat: 41.355946,
  centerLng: 14.370868,
  apiKeys: {
    bing: "{{ site.api_keys.bing }}"
  }
};
```

---

## Data Sources

| Data | Source | Format | Location | Ownership |
|------|--------|--------|----------|-----------|
| [e.g., Photos] | [CSV] | GeoJSON | `public/data/` | [Internal/External] |
| [e.g., Base Map] | [Tile Server] | Tiles | CDN | [Attribution] |

---

## External Dependencies (CDN-Only)

| Library | URL | Version | SRI Hash | Usage |
|---------|-----|---------|----------|-------|
| Leaflet.js | `https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js` | 1.9.4 | [Hash] | Maps |
| [Add more] | | | | |

**Rule**: Every external URL must have a pinned version and SRI hash.

---

## Key Decision Log

### Decision 1: CDN-Only Approach
**When**: [Date]  
**Why**: GitHub Pages cannot run npm or build pipelines  
**Impact**: All external libs pinned via CDN URLs with SRI hashes  
**Revisit**: [Date or condition]

### Decision 2: [Title]
**When**: [Date]  
**Why**: [Rationale]  
**Impact**: [Side effects]  
**Revisit**: [Date or condition]

---

## Known Limitations & Tech Debt

| Issue | Severity | Notes | Workaround |
|-------|----------|-------|-----------|
| [e.g., No backend] | High | Cannot serve dynamic content | Use GitHub API or static JSON |
| [e.g., CORS for tiles] | Medium | Cross-origin requests limited | CORS-friendly tile servers only |
| [e.g., File size] | Low | Large GeoJSON can slow load | Consider tiling or pagination |

---

## Deployment Checklist

- [ ] All CDN URLs tested and responding
- [ ] SRI hashes validated
- [ ] Environment variables set in GitHub Secrets (if used)
- [ ] CORS headers verified for external requests
- [ ] Error logging enabled in console
- [ ] Loading states shown to user
- [ ] Fallbacks tested (offline, slow network)

---

## Related Files to Update After Changes

- `.ai/IMPLEMENTATION_STEPS.md` - If tasks change
- `.ai/MEMORY/LEARNINGS.md` - If lessons learned
- `_config.yml` - If settings change
- `public/js/config.js` - If constants change
- `.github/copilot-instructions.md` - If global rules change
