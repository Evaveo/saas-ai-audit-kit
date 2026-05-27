# Contributing to saas-ai-audit-kit

Thanks for considering a contribution. This kit gets better when real practitioners share what they've found bites them in production.

## Three types of contributions

### 1. New checks

Suggest a check that's missing. Open a pull request that edits `skill/themes.json`.

Every check must have:
- An **id** following the theme's numbering (e.g. `4.12` for the 12th item of theme 4)
- A **label** that is a single declarative sentence ("Foo is bar.")
- A **how** that is a concrete test (a grep, a curl, a DevTools step) — not "review the code"
- A **crit** rating: 🔴 / 🟡 / 🟢

Avoid:
- Subjective checks ("the UX is good")
- Stack-specific assumptions (e.g. "React Query is set up")
- Jurisdiction-specific items in the generic themes — propose a new sector-specific section instead

### 2. Sector extensions

Have a vertical that doesn't fit (defense, fintech regulated, healthcare HDS, edtech FERPA…)? Open an issue describing the sector and propose 10-15 sector-specific checks. We'll add them as a `13_<sector>` theme so users can opt in.

### 3. Translations

The grid is currently French + English mixed. If you want to localize fully into one language, open a PR creating `skill/themes.<lang>.json` and we'll wire the skill to accept a `--lang` flag.

## Code style

- Python: PEP 8, type hints where it helps readability.
- JSON: 2-space indent. Keep emoji criticality markers as-is.
- Markdown: keep lines wrapping at sentence boundaries, not at column 80.

## Releasing a new version

Maintainers only:

1. Update `skill/themes.json` (the source of truth)
2. Regenerate the example template:
   ```bash
   python skill/audit_xlsx.py --output examples/empty_template.xlsx
   ```
3. Tag the release: `git tag vX.Y.Z && git push --tags`

## Code of conduct

Be kind. Critique the work, not the person. Disagreements are fine; condescension isn't.

## License of contributions

By contributing, you agree your work is licensed under MIT, same as the rest of the kit.
