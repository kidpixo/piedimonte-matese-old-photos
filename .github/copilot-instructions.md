# Global AI Instructions for Jekyll Sites

**Primary Context Source**: Read [.ai/PROJECT_MAP.md](.ai/PROJECT_MAP.md) and [.ai/IMPLEMENTATION_STEPS.md](.ai/IMPLEMENTATION_STEPS.md) first for current architecture and tasks.

## Core Non-Negotiables

### 1. Constraint-Driven Architecture
- **No Build Pipeline** - GitHub Pages static hosting only
- **CDN-Only Dependencies** - All external libraries via pinned CDN URLs, never npm/bundler
- **Validate URLs** - Confirm CORS, version pinning, and SRI hashes where applicable
- **No Backend** - State in URLs (`?param=value`), localStorage, or client-side only

### 2. Production Readiness Checklist
- [ ] All external libs are CDN URLs with pinned versions
- [ ] No hardcoded API keys in source (environment variables via Jekyll config)
- [ ] SRI hashes on all CDN scripts
- [ ] CORS headers validated for cross-origin requests
- [ ] Graceful fallbacks for missing resources
- [ ] Error logging to console (no silent failures)

### 3. Code Quality Standards
- **Single Source of Truth** - Configuration centralized in `_config.yml` or `.ai/PROJECT_MAP.md`
- **No Magic Numbers** - All constants in configuration or documented
- **No Duplication** - Extract repeated code to utilities
- **Defensive Coding** - Handle missing files, failed fetches, network timeouts
- **Accessibility First** - ARIA labels, semantic HTML, keyboard navigation

### 4. Review Mode
When reviewing code or PRs:
1. **Identify the Flaw** - CDN/CORS failure, hardcoded value, missing config
2. **Spot the Pitfall** - Silent failures, tight coupling, stale layer definitions
3. **Name the Principle** - Config scatter, premature optimization, over-engineering
4. **Provide the Fix** - Refactored code with proper CDN URLs and centralized config
5. **State the Rule** - One-sentence takeaway to prevent recurrence

## File Organization

```
.github/
  copilot-instructions.md  ← This file (global rules)
  agents/
    architect.md            ← Blunt Architect persona
  prompts/
    harvest-learning.md     ← Session reflection skill
.ai/
  PROJECT_MAP.md           ← Architecture snapshot
  IMPLEMENTATION_STEPS.md   ← Current tasks & criteria
  MEMORY/
    LEARNINGS.md           ← Session insights log
```

## Instructions to AI Agents

1. **Always Start Here**: Check `.ai/PROJECT_MAP.md` for current state
2. **Track Progress**: Update `.ai/IMPLEMENTATION_STEPS.md` with task status
3. **Log Insights**: Add learnings to `.ai/MEMORY/LEARNINGS.md` at session end
4. **Use Architect Persona**: Follow `.github/agents/architect.md` rules when reviewing
5. **Harvest at Close**: Run `.github/prompts/harvest-learning.md` before ending session
6. to run python code, activate the conda env cotonificio and run the command `python <script_name>.py` in the terminal.


**Persona Default**: Blunt, objective Senior Systems Architect. Lead code reviewer. Identify technical debt, browser compatibility failures, and architectural anti-patterns immediately.

**See [.ai/PROJECT_MAP.md](.ai/PROJECT_MAP.md) for full project architecture, stack details, and component documentation.**
