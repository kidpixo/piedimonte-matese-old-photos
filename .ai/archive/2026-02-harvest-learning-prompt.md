# Harvest Learnings Prompt

**When to Use**: End of every session before closing  
**Duration**: 5-10 minutes  
**Owner**: AI agent or developer  
**Output**: Entries appended to [.ai/MEMORY/LEARNINGS.md](.ai/MEMORY/LEARNINGS.md)

---

## Instructions

At the end of your session, reflect on the work completed and capture insights using this structure.

### Step 1: Review What Was Done

```
## [Today's Date] - [Session Theme]

**Duration**: [Start time] - [End time] ([X hours])  
**Tasks Completed**:
- [ ] Task 1 from IMPLEMENTATION_STEPS.md
- [ ] Task 2 from IMPLEMENTATION_STEPS.md

**Files Modified**:
- .ai/PROJECT_MAP.md - [What changed?]
- public/js/myscript.js - [What changed?]
```

### Step 2: Identify Surprises & Lessons

For each item below, ask: "Did we learn something new or confirm something known?"

```markdown
### Discoveries

**Browser Issue Found?**
- Issue: [Describe the browser bug or quirk]
- Reproduced: [Browser/version]
- Workaround: [CSS/JS fix]

**Configuration Pattern**?
- Pattern: [Repeated mistake or success]
- Applies to: [Which files or components?]
- Rule: [One-sentence takeaway]

**Data or GIS Gotcha?**
- Problem: [Coordinate system? Encoding? Validation?]
- Impact: [How many hours did this cost?]
- Solution: [What did we do?]

**Performance or Deployment**?
- Observation: [What was slow or broke?]
- Root Cause: [Why?]
- Fix: [How did we resolve it?]
```

### Step 3: Log to LEARNINGS.md

For each significant discovery, format as:

```markdown
## [Date] - [Issue Title]

**Problem**: [What surprised us?]  
**Context**: [Where? Doing what?]  
**Root Cause**: [Why did it happen?]  
**Solution**: [How did we fix it?]  
**Lesson**: [One-sentence rule]  
**Impact**: High | Medium | Low  
**Tags**: `#tag1`, `#tag2`  
**Related Task**: [Link to IMPLEMENTATION_STEPS.md]  
**Code Example** (if applicable):
\`\`\`javascript
// Snippet showing the fix
\`\`\`
```

### Step 4: Update IMPLEMENTATION_STEPS.md

- [ ] Mark completed tasks as "completed"
- [ ] Move blockers to "blocked" with reason
- [ ] Add "Notes for Next Session" section
- [ ] Update task status if mid-sprint

### Step 5: Confirm PROJECT_MAP.md

- [ ] Did architecture change? Update it.
- [ ] Did we add a new CDN library? Add to list with version.
- [ ] Did we discover a new limitation? Add to Known Tech Debt.

---

## Sample Harvest Output

### Example 1: Browser Compatibility Issue

```
## 2026-02-18 - iOS Safari Marker Tap Issue

**Problem**: Map markers not opening popups on iOS Safari; works on desktop Safari.  
**Context**: User reported on iPhone 13, iOS 15. Reproduced with tap event.  
**Root Cause**: Safari mobile doesn't fire 'click' event on Leaflet layer; requires 'tap' event.  
**Solution**: Added `L.Browser.touch` check in myscript.js to bind both 'click' and 'tap'.  
**Lesson**: Always test on multiple iOS versions; desktop Safari != mobile Safari.  
**Impact**: High (affects all users on iOS)  
**Tags**: `#browser-compat`, `#leaflet`, `#mobile`  
**Related Task**: 3 (Implement Frontend Map)  
**Code Example**:
\`\`\`javascript
// Original (broken on iOS)
layer.on('click', showPopup);

// Fixed
layer.on('click', showPopup);
if (L.Browser.touch) {
  layer.on('tap', showPopup);  // iOS Safari fallback
}
\`\`\`
```

### Example 2: Configuration Pattern

```
## 2026-02-18 - Hardcoded URLs Lead to Stale Data

**Problem**: GeoJSON URL hardcoded in myscript.js; when we moved file to new path, map broke silently.  
**Context**: Refactored public/data/ folder structure; forgot to update one URL.  
**Root Cause**: Configuration scattered across multiple files instead of centralized.  
**Solution**: Moved all data URLs to _config.yml, injected into window.config in map.html.  
**Lesson**: All external URLs (data, tiles, APIs) belong in _config.yml, never in JS.  
**Impact**: High (prevents silent failures on deploy)  
**Tags**: `#config`, `#architecture`, `#refactor`  
**Related Task**: 1 (Bootstrap Jekyll)  
**Code Example**:
\`\`\`yaml
# _config.yml
data_urls:
  photos_origin: /public/data/photos_origin.geojson
  photos_fov: /public/data/photos_fov.geojson
\`\`\`

\`\`\`javascript
// myscript.js (no hardcoding)
fetch(window.config.dataUrls.photosOrigin)
  .then(...)
  .catch(err => console.error('Failed to load photos', err));
\`\`\`
```

---

## Quick Harvest Checklist

- [ ] Completed tasks marked in IMPLEMENTATION_STEPS.md
- [ ] Blockers documented with workaround
- [ ] Each discovery logged with Problem/Solution/Lesson format
- [ ] Tags added for future search (#config, #browser-compat, etc.)
- [ ] PROJECT_MAP.md updated if architecture changed
- [ ] Code examples included for tricky fixes
- [ ] Impact level assigned (High/Medium/Low)
- [ ] Related IMPLEMENTATION_STEPS.md task linked

---

## Why This Matters

- **Prevents Recurrence**: Next time you face a similar issue, LEARNINGS.md has the answer.
- **Onboards New Developers**: Learnings explain *why* choices were made, not just *what* was decided.
- **Informs Refactoring**: Patterns show which parts violate architecture and need cleanup.
- **Improves Estimates**: Past lessons help predict how long tasks take.

---

## Session Handoff

After harvest, your output should be appended to `.ai/MEMORY/LEARNINGS.md` automatically.

**Before closing the session**:
1. Run through checklist above
2. Copy formatted learnings
3. Open [.ai/MEMORY/LEARNINGS.md](.ai/MEMORY/LEARNINGS.md)
4. Paste under "Session Learnings" section with today's date
5. Commit to repo with message: `chore: harvest learnings [Date]`

---

## No Session? No Problem.

If you didn't discover anything surprising, log a single entry:

```markdown
## [Date] - Routine Maintenance
**Summary**: Completed [task] without new discoveries.  
**Impact**: Low  
**Tags**: `#routine`
```

This keeps LEARNINGS.md active and confirms no regressions occurred.
