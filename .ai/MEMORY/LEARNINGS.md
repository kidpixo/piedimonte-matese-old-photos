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

### [Session 1 - Bootstrap]

#### Blank (Start logging here)

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
