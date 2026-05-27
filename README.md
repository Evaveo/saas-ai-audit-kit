# saas-ai-audit-kit

> A 12-theme, ~145-point pre-launch audit grid for any SaaS that integrates AI — usable as a standalone spreadsheet **or** as an automated Claude Code skill that fills it for you.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Made by Evaveo](https://img.shields.io/badge/made_by-Evaveo-7c3aed)](https://evaveo.com)

## Why

Most pre-launch checklists are either too generic ("ship it!") or too specific to one stack. This kit is the missing middle:

- **Stack-agnostic** — works on any SaaS, any language, any cloud, any juridiction.
- **AI-aware** — three dedicated themes for AI quality, costs, and governance (EU AI Act ready).
- **Actionable** — every point has a concrete way to test it, not abstract platitudes.
- **Automatable** — a Claude Code skill that dispatches 12 parallel agents to inspect your repo and fill the grid for you.

## The 12 themes

| # | Theme | # of checks | Focus |
|---|---|---|---|
| 1 | Product & UX | 11 | First-run, empty states, mobile, a11y |
| 2 | Security & Auth | 14 | Cookies, CSP, 2FA, rate-limit, secrets |
| 3 | Data & Privacy | 14 | GDPR rights, DPA, retention, encryption |
| 4 | AI — Quality | 11 | Eval set, hallucinations, prompt injection |
| 5 | AI — Costs | 11 | Quotas, budget alerts, token limits |
| 6 | AI — Governance | 11 | AI Act, model cards, audit-trail |
| 7 | Architecture | 12 | Stateless, queue, idempotency, backup |
| 8 | Payments | 12 | Webhooks, taxes, dunning, refunds |
| 9 | Observability | 12 | Logs, alerts, runbook, rollback |
| 10 | Legal & Compliance | 13 | ToS, Privacy, cookies, rétractation |
| 11 | UX/UI Design quality | 20 | Design system, states, branding, dark patterns |
| 12 | Frontend ↔ Backend | 24 | API contracts, HTTP semantics, CORS, idempotency |

**Each point** is tagged with a criticality:
- 🔴 **Blocker** — fix before public launch
- 🟡 **Important** — fix within 30 days
- 🟢 **Polish** — continuous improvement

## Two ways to use

### Option A — Just the spreadsheet (no AI required)

1. Download [`examples/empty_template.xlsx`](examples/empty_template.xlsx)
2. Open in Excel / Google Sheets / LibreOffice
3. For each theme tab, fill the **Score** column (OK / KO / N/A dropdown) + a **Comment**
4. The **Synthèse** tab auto-calculates your score per theme + global score

Decision thresholds (built-in):

| Score | Verdict |
|---|---|
| **> 90%** | Ready to scale — focus growth |
| **80-90%** | Ready to launch — fix 🟡 within 30 days |
| **65-80%** | Ready for private beta — fix all 🔴 before opening |
| **< 65%** | Not production-ready — work in progress |

### Option B — Automated audit via Claude Code skill

The skill spawns 12 parallel agents that inspect a repository and fill the grid automatically.

**Requirements :**
- [Claude Code](https://claude.com/claude-code) installed
- Python 3.10+
- `pip install openpyxl`

**Install the skill :**

```bash
# Unix / macOS
./install/install.sh

# Windows (PowerShell)
.\install\install.ps1
```

Or manually : copy `skill/` to `~/.claude/skills/saas-ai-audit/`.

**Use it :**

```bash
cd /path/to/your-saas-repo
claude
> /saas-ai-audit
```

The skill will :
1. Confirm the target repository
2. Dispatch 12 `Explore` sub-agents **in parallel** (~5-10 min)
3. Compile their findings into `audit_results.json`
4. Generate a filled `AUDIT_{repo}_{date}.xlsx` with scores and comments
5. Report the global score + top 5 blockers

### Option C — Run the Python script directly

```bash
# Empty template
python skill/audit_xlsx.py --output audit.xlsx

# Or fill from your own JSON
python skill/audit_xlsx.py --results audit_results.json --output AUDIT.xlsx
```

JSON format expected :

```json
{
  "audited_repo": "/path/to/repo",
  "audit_date": "2026-01-15",
  "themes": {
    "01_Produit_UX": {
      "1.1": { "status": "OK", "evidence": "components/Onboarding.tsx:42", "notes": "First-run wizard..." }
    }
  }
}
```

## Adapting to your context

The grid is opinionated but not prescriptive. Different SaaS types have different priorities :

| Context | What to emphasize |
|---|---|
| **B2B enterprise** | Add SOC 2 / ISO 27001, SSO/SAML, SLA, tenant isolation |
| **B2C consumer** | Reinforce Legal, cookies, accessibility, multilingual |
| **Marketplace / platform** | KYC/AML, moderation, payouts, abuse reporting |
| **Health / medical** | HDS (FR) / HIPAA (US), medical audit-trail, higher security |
| **Finance / payments** | PCI-DSS, AML, fraud detection, transaction monitoring |
| **Critical-data (HR, legal, insurance)** | Enhanced encryption, access logs, customer right-to-audit |

Mark items **N/A** when they don't apply to your context — document why in the comment column.

## Repo structure

```
saas-ai-audit-kit/
├── README.md              ← you are here
├── LICENSE                ← MIT
├── CONTRIBUTING.md        ← how to contribute new checks
├── grid/
│   └── SAAS_AI_AUDIT_GRID.md   ← human-readable markdown version
├── skill/                 ← Claude Code skill (copy to ~/.claude/skills/)
│   ├── SKILL.md
│   ├── themes.json        ← all 12 themes & 145 checks (source of truth)
│   └── audit_xlsx.py      ← generates / fills the Excel
├── examples/
│   ├── empty_template.xlsx
│   └── sample_results.json
├── install/
│   ├── install.sh         ← Unix / macOS installer
│   └── install.ps1        ← Windows installer
└── .github/
    └── ISSUE_TEMPLATE/
```

## Contributing

New checks, sector-specific extensions, or translations are very welcome. See [CONTRIBUTING.md](CONTRIBUTING.md).

Quick guideline : every check must have
- A clear pass/fail outcome (no "is it good?")
- A concrete way to test it (`grep`, DevTools, curl, etc.)
- A criticality rating (🔴 / 🟡 / 🟢)

## License

[MIT](LICENSE) — use it, fork it, adapt it, sell consulting based on it. Just keep the copyright notice.

## Credits

Created and maintained by **Evaveo** ([evaveo.com](https://evaveo.com)) — built from the lessons learned shipping [Formaveo](https://formaveo.com), an interactive video SaaS with integrated AI.

© 2026 Evaveo — all rights reserved.

---

_Built with Claude Code. The Claude Code skill is itself the kit's auto-audit reference implementation._
