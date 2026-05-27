---
name: saas-ai-audit
description: Inspecte un repo SaaS (de préférence intégrant de l'IA), exécute en parallèle 12 sous-agents d'audit (un par thème — UX, sécurité, données/RGPD, IA qualité/coûts/gouvernance, archi, paiement, observabilité, légal, UX/UI, frontend↔backend), et produit un fichier Excel rempli avec scores et commentaires. À utiliser via `/saas-ai-audit` quand on veut auditer un SaaS de façon systématique.
---

# Skill : Audit SaaS + IA automatisé

## Quoi

Spawne 12 sous-agents `Explore` **en parallèle**, un par thème de la grille d'audit (UX, sécurité, données, IA qualité, IA coûts, IA gouvernance, architecture, paiement, observabilité, légal, UX/UI design, frontend↔backend). Chaque sous-agent inspecte le repo et remplit son thème (OK / KO / N/A + commentaire par point). Le résultat global est écrit dans un fichier Excel généré à la racine du repo.

## Quand

L'utilisateur tape `/saas-ai-audit` ou demande "audite ce SaaS" / "fais un audit complet" / "remplis la grille d'audit".

## Pré-requis

- Le repo cible est le working directory courant (sauf si l'utilisateur précise un chemin).
- Python 3 + `openpyxl` installés (déjà OK sur cette machine).
- Les fichiers du skill : `themes.json` (définition des 12 thèmes) et `audit_xlsx.py` (générateur Excel) sont dans le même dossier que ce SKILL.md.

## Procédure

### Étape 1 — Préparer

1. Identifier le repo cible. Par défaut : `cwd`. Si l'utilisateur précise un chemin, l'utiliser.
2. Demander confirmation rapide à l'utilisateur : "Je vais auditer `<nom-repo>` sur les 12 thèmes (UX, sécurité, données, IA qualité/coûts/gouvernance, archi, paiement, observabilité, légal, UX/UI, frontend↔backend). ~12 sous-agents en parallèle, ~5-10 min. OK ?"
3. Si OK, charger `themes.json` (chemin : `{skill_dir}/themes.json`) avec Read.

### Étape 2 — Dispatcher 12 sous-agents en parallèle

**Important : 1 seul message avec 12 appels `Agent` simultanés** (parallélisme).

Pour chaque thème, lancer un agent `Explore` avec un prompt construit ainsi :

```
Tu audites le thème "{theme_name}" du repo {repo_path}.

Description : {theme_description}

Pour chaque point ci-dessous, inspecte le repo et retourne ton verdict.

POINTS À AUDITER :
{liste des items du thème — id, label, comment tester, criticité}

OUTPUT : retourne UNIQUEMENT un JSON valide structuré comme :
{
  "1.1": {"status": "OK"|"KO"|"N/A", "evidence": "file:line ou null", "notes": "1-2 phrases max"},
  "1.2": {...},
  ...
}

- "OK" si tu trouves la preuve que le point est respecté.
- "KO" si tu trouves la preuve du contraire OU si l'absence est clairement constatée après recherche.
- "N/A" si le point ne s'applique pas à ce repo (ex : pas de paiement, pas d'IA).
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

Si le dossier `DOCS/` n'existe pas dans le repo, mettre le fichier à la racine du repo.

### Étape 5 — Rapporter à l'utilisateur

Synthèse courte :
- Chemin du fichier Excel généré
- Score global (% OK / (OK+KO))
- Top 5 des 🔴 KO (bloquants)
- Suggestion : ouvrir l'xlsx dans Excel pour exploration

## Notes pour les sous-agents

- Ils utilisent l'outil **Explore** (read-only, rapide), pas de mutations.
- Eux NE doivent PAS dispatcher d'autres agents.
- Eux doivent retourner uniquement le JSON demandé — pas de prose autour.
- Si un point demande de tester quelque chose qui exige le serveur en cours d'exécution (ex : tester un endpoint live), ils marquent N/A avec note "Test runtime nécessaire".

### Comment exploiter le champ `automation` (schema v2)

Chaque item du `themes.json` porte un champ `automation` :
- `"🤖"` (automatisable) → audit complet attendu via inspection du code
- `"🔁"` (semi-automatisable) → inspection + best effort, signaler ce qui reste manuel
- `"👤"` (manuel) → marquer N/A par défaut avec note "Manuel — voir notes" et reporter le `manual_caveat` de l'item si présent

Cela permet aux sous-agents de ne pas perdre de temps à essayer d'auditer des choses qui ne peuvent pas l'être par lecture du code (validation juridique, décision métier, test utilisateur réel).

## Variantes utiles

- `/saas-ai-audit thème:7` → ne lance qu'un seul agent sur le thème 7
- `/saas-ai-audit themes:1,2,3` → ne lance que ces 3 thèmes
- `/saas-ai-audit path:../autre-repo` → audite un autre dossier

## Anti-patterns à éviter

- **Ne pas** générer une nouvelle grille si `themes.json` existe — c'est le fichier source de vérité.
- **Ne pas** demander à un seul agent de tout faire — la parallélisation des 12 thèmes est l'objet du skill.
- **Ne pas** écrire de prose en dehors du JSON dans les sous-agents — le main agent doit pouvoir parser directement.
- **Ne pas** modifier le repo audité — read-only.
