# Implementation Steps & Task Tracker

**Primary Context**: Read [PROJECT_MAP.md](PROJECT_MAP.md) first

**Update this file**: After each task or session, mark status and move to next item

---

## Current Sprint

**Sprint Number**: 1  
**Sprint Goal**: [Define what this sprint accomplishes]  
**Start Date**: [Date]  
**Target End Date**: [Date]

---

## Task Template

```
## [Task ID]. [Task Title]

**Status**: not-started | in-progress | blocked | completed  
**Owner**: [Person or agent]  
**Priority**: P0 (critical) | P1 (high) | P2 (medium) | P3 (low)  

### Description
[What needs to be built?]

### Acceptance Criteria (Ideal State)
- [ ] Criterion 1 - How do we know this is done?
- [ ] Criterion 2 - Testable, objective measure
- [ ] Criterion 3 - Aligns with architecture in PROJECT_MAP.md

### Definition of Done
- [ ] Code reviewed (see .github/agents/architect.md)
- [ ] All CDN URLs validated
- [ ] Error handling implemented (no silent failures)
- [ ] Updated PROJECT_MAP.md if architecture changed
- [ ] Added learning to .ai/MEMORY/LEARNINGS.md if new pattern
- [ ] Deployed to GitHub Pages and tested

### Dependencies
- [ ] [Task B] - Must complete before this
- [ ] [External resource] - Needed

### Notes
[Any learnings, blockers, or context from past work]

### Related Files
- [PROJECT_MAP.md](PROJECT_MAP.md) - Confirm architecture alignment
- [LEARNINGS.md](MEMORY/LEARNINGS.md) - Check if solved before

---
```

---

## Active Tasks

### 1. Bootstrap Jekyll Site Structure

**Status**: not-started  
**Owner**: AI  
**Priority**: P0

### Description
Set up base Jekyll directory structure with _layouts/, _includes/, _posts/, public/ folders and initial _config.yml

### Acceptance Criteria (Ideal State)
- [ ] `_config.yml` created with site metadata and CDN libs defined
- [ ] `_layouts/default.html` created with base template
- [ ] `_layouts/page.html` and `_layouts/post.html` extend default
- [ ] `_includes/head.html` loads all CDN dependencies with SRI hashes
- [ ] `_includes/sidebar.html` for navigation
- [ ] `public/css/`, `public/js/` created and linked
- [ ] `public/js/config.js` generated from _config.yml variables
- [ ] Jekyll serves locally without errors
- [ ] Deployment to GitHub Pages tested

### Definition of Done
- [ ] Code reviewed against .github/agents/architect.md
- [ ] All CDN URLs pinned and validated
- [ ] Error handling in place (console logs for missing libs)
- [ ] PROJECT_MAP.md updated with actual CDN URLs and stack
- [ ] Learning logged in .ai/MEMORY/LEARNINGS.md
- [ ] Site accessible at https://[user].github.io/[repo]/

### Dependencies
- None (this is bootstrap)

### Notes
Refer to PROJECT_MAP.md for CDN library versions and SRI hashes. Keep _config.yml DRY—build all URLs there, inject into JS.

### Related Files
- [PROJECT_MAP.md](PROJECT_MAP.md) - Update Technology stack
- [LEARNINGS.md](MEMORY/LEARNINGS.md) - Log Jekyll quirks if found

---

### 2. Set Up Data Pipeline

**Status**: not-started  
**Owner**: AI  
**Priority**: P1

### Description
Create data processing scripts (if needed) to transform source data to GeoJSON or JSON for frontend consumption.

### Acceptance Criteria (Ideal State)
- [ ] Source data identified (CSV, GeoJSON, API, etc.)
- [ ] Processing script written (Python, bash, or Jekyll plugin)
- [ ] Output saved to `public/data/` with clear naming
- [ ] Error handling for missing/malformed source data
- [ ] Script documented in PROJECT_MAP.md
- [ ] Processed data validated (schema check)
- [ ] Output committed to repo (immutable reference)

### Definition of Done
- [ ] Script runs without hardcoded paths (uses environment or config)
- [ ] Output tested for correctness
- [ ] PROJECT_MAP.md updated with Data Sources section
- [ ] LEARNINGS.md documents any gotchas (encoding, coordinate systems, etc.)
- [ ] Script can be re-run safely without data loss

### Dependencies
- Task 1: Bootstrap Jekyll Site Structure

### Notes
Decide: commit processed data to repo or generate on demand? For GitHub Pages, commit is safer (no build step). Log coordinate system and assumptions in LEARNINGS.md.

### Related Files
- [PROJECT_MAP.md](PROJECT_MAP.md) - Data Sources section
- [LEARNINGS.md](MEMORY/LEARNINGS.md) - Encoding, CRS, validation lessons

---

### 3. Implement Frontend Map/Visualization

**Status**: not-started  
**Owner**: AI  
**Priority**: P1

### Description
Build interactive frontend using Leaflet.js (or similar), load processed data, display markers/overlays/controls.

### Acceptance Criteria (Ideal State)
- [ ] Map loads on page with correct center/zoom from config
- [ ] Base layer (OSM or configured tile) renders
- [ ] Data layers load from `public/data/` via fetch
- [ ] Markers/popups display correctly with no console errors
- [ ] Error handling: graceful fallback if data or tiles fail to load
- [ ] Mobile-responsive (touch controls, readable on small screens)
- [ ] Accessibility: ARIA labels, keyboard navigation for controls
- [ ] Layer control shows/hides overlays without reload
- [ ] URL state preserved (if bookmarking implemented)

### Definition of Done
- [ ] No hardcoded coordinates or API URLs (all from config)
- [ ] Network errors logged to console, not silent
- [ ] Tested in Chrome, Firefox, Safari, Edge
- [ ] PDO tested on mobile (iPhone, Android)
- [ ] PROJECT_MAP.md updated with Frontend stack details
- [ ] LEARNINGS.md documents browser compatibility issues
- [ ] Deployed and working on GitHub Pages

### Dependencies
- Task 1: Bootstrap Jekyll Site Structure
- Task 2: Set Up Data Pipeline

### Notes
Use config.js injected from _config.yml. Load data asynchronously with error handling. Test slow networks with browser DevTools throttling.

### Related Files
- [PROJECT_MAP.md](PROJECT_MAP.md) - External CDN dependencies, API keys
- [LEARNINGS.md](MEMORY/LEARNINGS.md) - Browser quirks, CORS issues

---

### 4. Add Static Content & Navigation

**Status**: not-started  
**Owner**: AI  
**Priority**: P2

### Description
Create about page, blog posts, footer, and navigation structure. Use Jekyll frontmatter for metadata.

### Acceptance Criteria (Ideal State)
- [ ] Home page (index.md) with project overview
- [ ] About page (about.md) with project context
- [ ] Blog post template (_layouts/post.html) functional
- [ ] Navigation menu in sidebar (_includes/sidebar.html)
- [ ] Footer with links and attribution
- [ ] All pages styled consistently with main CSS
- [ ] No broken links or 404s
- [ ] Mobile navigation works on small screens

### Definition of Done
- [ ] HTML validates (no console warnings)
- [ ] Accessibility: All text has sufficient contrast, semantic HTML used
- [ ] PROJECT_MAP.md updated if new pages change architecture
- [ ] LEARNINGS.md documents Jekyll template quirks if found

### Dependencies
- Task 1: Bootstrap Jekyll Site Structure

### Notes
Keep navigation DRY—pull menu from _data/nav.yml or _config.yml, iterate in _includes/.

---

### 5. Testing & Validation

**Status**: not-started  
**Owner**: AI  
**Priority**: P1

### Description
Test site across browsers, devices, network conditions, and validate performance.

### Acceptance Criteria (Ideal State)
- [ ] Automated: Links checker passes (no 404s)
- [ ] Chrome, Firefox, Safari, Edge all render correctly
- [ ] Mobile: iPhone 12, Android responsive and touch-friendly
- [ ] Network: Tested with 3G throttling, works without hanging
- [ ] Performance: Lighthouse score >90
- [ ] Accessibility: WAVE scan passes, keyboard navigation works
- [ ] Offline: Loading states shown, no silent failures
- [ ] GitHub Pages: Deployed and public URL working

### Definition of Done
- [ ] Automated tests run on push (GitHub Actions, if applicable)
- [ ] Known browser issues documented in LEARNINGS.md
- [ ] CLIENT_MAP.md updated with test results
- [ ] No console errors or warnings in production

### Dependencies
- All prior tasks

### Notes
Use GitHub Actions matrix for multi-browser testing. Document any browser-specific CSS/JS patches in LEARNINGS.md for future reference.

---

## Backlog (Future Sprints)

### [ ] Optimize asset loading (lazy load images, minify CSS/JS)
### [ ] Add analytics (Plausible, or no tracking if privacy-first)
### [ ] Set up CI/CD pipeline (GitHub Actions on push)
### [ ] Deploy to custom domain (DNS setup)
### [ ] Add multi-language support (if needed)
### [ ] Implement search (static or external)

---

## Completed Tasks

(Move tasks here with completion date and summary)

---

## Notes for Next Session

- [Item 1]: What did we discover?
- [Item 2]: What should we try next?
- [Item 3]: What got blocked?

(This section rolls forward to LEARNINGS.md at session end via harvest-learning.md)
