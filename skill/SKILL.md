---
name: saas-ai-audit
description: Inspecte un repo SaaS (de préférence intégrant de l'IA), exécute en parallèle 13 sous-agents d'audit (un par thème — UX, sécurité, données/RGPD, IA qualité/coûts/gouvernance, archi, paiement, observabilité, légal, UX/UI, frontend↔backend, doc/maintenance), et produit un fichier Excel rempli avec scores et commentaires. À utiliser via `/saas-ai-audit` quand on veut auditer un SaaS de façon systématique.
---

# Skill : Audit SaaS + IA automatisé (v2)

## Quoi

Spawne 13 sous-agents `Explore` **en parallèle**, un par thème de la grille d'audit (UX, sécurité, données, IA qualité, IA coûts, IA gouvernance, architecture, paiement, observabilité, légal, UX/UI design, frontend↔backend, doc/maintenance). Chaque sous-agent inspecte le repo et remplit son thème. Le résultat global est écrit dans un fichier Excel généré à la racine du repo.

## Nouveautés v2

- **5 statuts** au lieu de 3 : `OK`, `PARTIAL`, `KO`, `TODO`, `N/A`
  - `PARTIAL` : critère partiellement respecté — compte 0.5 dans le score
  - `TODO` : prévu/planifié mais pas encore implémenté — exclu du score
- **Score pondéré** : 🔴 compte 3×, 🟡 compte 2×, 🟢 compte 1×
- **Profils** : `--profile early-stage|launch-ready|scale` skip les items prématurés
- **--scope** : ne lancer que certains thèmes (gagne tokens + temps)
- **--summary-json** : output machine-readable pour CI/CD

## Quand

L'utilisateur tape `/saas-ai-audit` ou demande "audite ce SaaS" / "fais un audit complet" / "remplis la grille d'audit".

## Pré-requis

- Le repo cible est le working directory courant (sauf si l'utilisateur précise un chemin).
- Python 3 + `openpyxl` installés.
- Les fichiers du skill : `themes.json` (définition des 13 thèmes) et `audit_xlsx.py` sont dans le même dossier que ce SKILL.md.

## Procédure

### Étape 1 — Préparer

1. Identifier le repo cible. Par défaut : `cwd`. Si l'utilisateur précise un chemin, l'utiliser.
2. Demander confirmation rapide :
   > "Je vais auditer `<nom-repo>` sur les 13 thèmes (UX, sécurité, données, IA qualité/coûts/gouvernance, archi, paiement, observabilité, légal, UX/UI, frontend↔backend, doc/maintenance). 13 sous-agents en parallèle, ~5-10 min. Profil : `<all>` (par défaut). OK ?"
3. Si OK, charger `themes.json` (chemin : `{skill_dir}/themes.json`) avec Read.

### Étape 2 — Dispatcher 13 sous-agents en parallèle

**Important : 1 seul message avec 13 appels `Agent` simultanés** (parallélisme).

Pour chaque thème, lancer un agent `Explore` avec un prompt construit ainsi :

```
Tu audites le thème "{theme_name}" du repo {repo_path}.

Description : {theme_description}

Pour chaque point ci-dessous, inspecte le repo et retourne ton verdict.

POINTS À AUDITER :
{liste des items du thème — id, label, comment tester, criticité}

OUTPUT : retourne UNIQUEMENT un JSON valide structuré comme :
{
  "1.1": {"status": "OK"|"PARTIAL"|"KO"|"TODO"|"N/A", "evidence": "file:line ou null", "notes": "1-2 phrases max"},
  "1.2": {...},
  ...
}

Choix du statut :
- "OK" : preuve que le point est respecté.
- "PARTIAL" : partiellement respecté (ex : feature existe mais sans tests, ou config présente mais incomplète). Compte 0.5 dans le score.
- "KO" : preuve du contraire OU absence clairement constatée après recherche.
- "TODO" : la feature est prévue/planifiée (TODO comment, issue ouverte, ticket, scaffolding partiel) mais pas encore implémentée. NE compte PAS dans le score — utile pour distinguer "mal fait" de "pas encore fait".
- "N/A" : ne s'applique pas à ce repo (ex : pas de marketplace si pas de payouts, pas d'IA si purement SaaS sans modèle).

Conseils :
- Préfère PARTIAL à KO si tu trouves une implémentation à moitié faite.
- Préfère TODO à KO si tu vois un commentaire/issue qui indique "à faire" sans malice.
- "evidence" : un file:line concret quand possible.
- "notes" : très court, factuel.

Ne fais PAS de recommandations. Audit pur. Pas de prose en dehors du JSON.
```

### Étape 3 — Collecter les résultats

Chaque sous-agent retourne son JSON. Assembler en un seul objet :

```json
{
  "audited_repo": "<absolute path>",
  "audit_date": "<YYYY-MM-DD>",
  "themes": {
    "01_Produit_UX": { "1.1": {...}, "1.2": {...}, ... },
    "02_Securite_Auth": { "2.1": {...}, ... },
    ...
  }
}
```

Sauvegarder en `{repo}/audit_results.json` via Write.

### Étape 4 — Générer l'Excel rempli

Exécuter via Bash :

```bash
python "{skill_dir}/audit_xlsx.py" --results "{repo}/audit_results.json" --output "{repo}/DOCS/AUDIT_{repo_name}_{YYYY-MM-DD}.xlsx"
```

Options utiles :
- `--profile early-stage` (skip items prématurés pour un MVP)
- `--scope 02_Securite_Auth,10_Legal` (ne garder que ces thèmes dans le rapport)
- `--summary-json {repo}/DOCS/audit_summary.json` (output machine-readable)

Si le dossier `DOCS/` n'existe pas dans le repo, mettre le fichier à la racine du repo.

### Étape 5 — Rapporter à l'utilisateur

Synthèse courte :
- Chemin du fichier Excel généré
- **Score brut** (OK + PARTIAL/2) / (OK + PARTIAL + KO)
- **Score pondéré** (poids 🔴=3, 🟡=2, 🟢=1)
- Top 5 des 🔴 KO (bloquants)
- Nombre de TODOs (features prévues mais pas faites)
- Suggestion : ouvrir l'xlsx dans Excel pour exploration

## Notes pour les sous-agents

- Ils utilisent l'outil **Explore** (read-only, rapide), pas de mutations.
- Eux NE doivent PAS dispatcher d'autres agents.
- Eux doivent retourner uniquement le JSON demandé — pas de prose autour.
- Si un point demande de tester quelque chose qui exige le serveur en cours d'exécution (ex : tester un endpoint live), ils marquent N/A avec note "Test runtime nécessaire".

### Comment exploiter le champ `automation` (schema v1+)

Chaque item du `themes.json` porte un champ `automation` :
- `"🤖"` (automatisable) → audit complet attendu via inspection du code
- `"🔁"` (semi-automatisable) → inspection + best effort, signaler ce qui reste manuel
- `"👤"` (manuel) → marquer N/A par défaut avec note "Manuel — voir notes" et reporter le `manual_caveat` de l'item si présent

### Comment exploiter le champ `profile` (schema v2)

Chaque item peut porter un champ `profile` :
- absent ou `"all"` → toujours audité
- `"launch+"` → skippé si l'utilisateur a passé `--profile early-stage`
- `"scale-only"` → skippé si l'utilisateur a passé `--profile early-stage` OU `--profile launch-ready`

Le script `audit_xlsx.py` se charge automatiquement de filtrer les items selon le `--profile`. Les sous-agents n'ont pas à s'en préoccuper.

## Variantes utiles

- `/saas-ai-audit thème:7` → ne lance qu'un seul agent sur le thème 7
- `/saas-ai-audit themes:1,2,3` → ne lance que ces 3 thèmes
- `/saas-ai-audit path:../autre-repo` → audite un autre dossier
- `/saas-ai-audit profile:early-stage` → adapté MVP/early-stage SaaS
- `/saas-ai-audit profile:launch-ready` → adapté SaaS prêt à lancer

## Anti-patterns à éviter

- **Ne pas** générer une nouvelle grille si `themes.json` existe — c'est le fichier source de vérité.
- **Ne pas** demander à un seul agent de tout faire — la parallélisation des 13 thèmes est l'objet du skill.
- **Ne pas** écrire de prose en dehors du JSON dans les sous-agents — le main agent doit pouvoir parser directement.
- **Ne pas** modifier le repo audité — read-only.
- **Ne pas** utiliser KO quand PARTIAL ou TODO sont plus juste — KO doit refléter une vraie défaillance, pas une feature non-prioritaire.
