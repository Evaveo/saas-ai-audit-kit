# Grille d'audit SaaS + IA — générique

> Cadre réutilisable pour auditer n'importe quel SaaS (B2C, B2B, marketplace, vertical) qui intègre de l'IA générative (LLM, vision, embedding, classification…) avant un lancement ou pour un état des lieux.
>
> **Volontairement agnostique** : aucune dépendance à un cloud (AWS / GCP / Azure / OVH / Scaleway), à un framework (Node, Python, Go, Rails…), ou à une juridiction (les contrôles légaux indiquent "selon juridiction").
>
> **Légende criticité :** 🔴 bloquant launch — 🟡 à corriger sous 30 jours — 🟢 amélioration continue
>
> **Méthode** : 1 point = OK / 0 point = KO / N/A si non applicable. Score d'un thème = points obtenus / points applicables × 100. Sous 80% → plan d'action.
>
> **Adapter selon le contexte** : un SaaS B2B enterprise n'a pas les mêmes priorités qu'un B2C grand public. Marquer N/A est légitime ; documenter pourquoi.

---

## 1. Produit & UX

| # | Point de contrôle | Comment tester | Crit. |
|---|---|---|---|
| 1.1 | First-time user voit la valeur en < 60 sec | Inscription incognito → chrono jusqu'au "wow moment" | 🔴 |
| 1.2 | Empty state du dashboard guide l'action (pas un trou) | Compte vierge → présence de cards onboarding ou CTA primaire | 🟡 |
| 1.3 | Tous les CTA disent ce qu'ils font (pas de "Valider" ambigu) | Parcours tous les boutons → label = action backend ? | 🟡 |
| 1.4 | Erreurs réseau/API toastent un message utilisable (pas "Error generic") | Couper le réseau → tester save/upload/login | 🟡 |
| 1.5 | Loading states partout (skeletons, spinners) — pas de freeze visuel | Throttle réseau à Slow 3G → vérifier feedback | 🟢 |
| 1.6 | Mobile responsive testé sur le plus petit viewport ciblé | DevTools mode iPhone SE (375px) ou équivalent | 🔴 |
| 1.7 | Tab navigation (clavier seul) fonctionne sur tous les formulaires | Tab/Shift+Tab → focus visible et logique | 🟡 |
| 1.8 | Pas de "Lorem ipsum", placeholders TODO, ou textes oubliés dans une autre langue | grep recherche `lorem`, `todo`, `tbd`, `xxx` dans le code | 🔴 |
| 1.9 | i18n cohérent : tous les libellés visibles sont traduits dans toutes les langues annoncées | Switch toutes les langues → screen audit | 🟡 |
| 1.10 | Confirmation pour actions destructives (suppression, paiement, opt-out) | Tester chaque suppression — modal de confirmation présent ? | 🔴 |
| 1.11 | Contraste WCAG AA minimum sur les textes (4.5:1 normal, 3:1 large) | Lighthouse accessibility audit | 🟡 |

---

## 2. Sécurité & Authentification

| # | Point de contrôle | Comment tester | Crit. |
|---|---|---|---|
| 2.1 | Sessions via cookie `httpOnly` + `Secure` + `SameSite=Lax/Strict` (pas token en localStorage seul) | DevTools → Application → Cookies | 🔴 |
| 2.2 | CSP en production avec script-src/connect-src restreints (pas de `'unsafe-inline'` sur script-src) | Inspecter le header `Content-Security-Policy` | 🔴 |
| 2.3 | 2FA disponible pour tous, obligatoire pour les comptes admin / privilégiés | Désactiver 2FA admin → l'app doit refuser l'accès aux endpoints sensibles | 🔴 |
| 2.4 | Rate limit sur les endpoints d'auth (`/login`, `/register`, `/password/reset`) | Stresser avec curl → 429 doit apparaître après N tentatives | 🔴 |
| 2.5 | Hash mot de passe `bcrypt` (cost ≥ 10) ou `argon2` ou `scrypt` | Inspecter le code de signup/auth | 🔴 |
| 2.6 | Anti-énumération sur login (même message d'erreur pour "email inexistant" et "mot de passe faux") | Tenter login email connu vs inconnu | 🟡 |
| 2.7 | Email verification obligatoire avant accès aux features sensibles (paiement, données externes) | Compte non vérifié → essayer payer, exporter | 🟡 |
| 2.8 | Authorization vérifie le rôle contre la DB (pas seulement le claim JWT/session) | Demoter un admin en DB → son token doit perdre accès dans la minute | 🟡 |
| 2.9 | Aucun secret en clair dans le repo (clés API, mots de passe, tokens) | `git log -p` + scan secrets (GitGuardian, Trufflehog) | 🔴 |
| 2.10 | Headers de sécurité : `X-Frame-Options`, `Strict-Transport-Security`, `Referrer-Policy`, `Permissions-Policy` | Tester via securityheaders.com → grade ≥ A | 🟡 |
| 2.11 | Validation côté serveur (Zod / Joi / Pydantic / schémas équivalents) sur toutes les routes mutantes | Auditer chaque route POST/PUT/PATCH/DELETE | 🔴 |
| 2.12 | Protection CSRF active sur les requêtes mutantes en cookie-auth (SameSite + token CSRF si cross-origin) | Tester soumission cross-origin sans token | 🟡 |
| 2.13 | Logs d'audit pour actions admin sensibles (création/suppression user, changement de rôle, payout) | Existence d'une table d'audit + accessibilité | 🟡 |
| 2.14 | Dépendances scannées (npm audit / Snyk / Dependabot) — pas de CVE critique en prod | Dernier rapport scan ≤ 7 jours | 🟡 |

---

## 3. Données & Confidentialité

| # | Point de contrôle | Comment tester | Crit. |
|---|---|---|---|
| 3.1 | Export des données personnelles (droit d'accès) — format machine-readable (JSON/CSV) | Endpoint `/account/export` ou équivalent fonctionnel | 🔴 |
| 3.2 | Suppression compte respecte le droit à l'oubli (anonymisation, pas hard delete si données financières à conserver) | Tester delete → User row anonymisée, transactions intactes pour la compta | 🔴 |
| 3.3 | Registre des traitements documenté (qui traite quoi, finalité, base légale, durée) | Document accessible et à jour | 🔴 |
| 3.4 | DPA / contrats sous-traitance signés avec tous les fournisseurs traitant des données perso (paiement, email, IA, hébergeur, analytics) | Liste des sous-traitants + statut contractuel | 🔴 |
| 3.5 | Analyse d'impact (DPIA / PIA) si traitement à risque (tracking, scoring, IA décisionnelle, données sensibles) | Document présent et à jour | 🟡 |
| 3.6 | Hébergement aligné avec les exigences de la juridiction des utilisateurs (UE / US / autres) | Vérifier la région des bases, buckets, providers IA | 🟡 |
| 3.7 | Politique de rétention écrite (combien de temps conserve-t-on quoi, par catégorie) | Document de rétention + job automatique de purge | 🔴 |
| 3.8 | Bannière cookie / tracking conforme au régime applicable (refus = même clic qu'accepter) | Inspecter en visiteur — pas de pré-cochage | 🔴 |
| 3.9 | Trackers / analytics chargés UNIQUEMENT après consentement valable | DevTools Network avant accept → aucun call à GA/Meta/autre | 🔴 |
| 3.10 | Logs d'identification (IP + UA + horodatage) si la juridiction l'exige pour les hébergeurs de contenu | Vérifier la table de logs + durée de rétention conforme | 🟡 |
| 3.11 | DPO / Privacy Officer désigné (interne ou externe) si la juridiction l'exige | Coordonnées affichées dans les mentions | 🟡 |
| 3.12 | Chiffrement at-rest activé sur la DB et les buckets de stockage | Vérifier la config cloud / fournisseur | 🟡 |
| 3.13 | TLS 1.2 minimum sur tous les endpoints publics (idéalement TLS 1.3) | SSL Labs test → grade A | 🔴 |
| 3.14 | Pas de PII dans les URLs (email, ID dans query string indexable par moteur) | Audit des routes — IDs en path OK, données en query problématique | 🟡 |

---

## 4. IA — Pertinence & Qualité

| # | Point de contrôle | Comment tester | Crit. |
|---|---|---|---|
| 4.1 | Set d'évaluation (eval set) figé pour tester les prompts à chaque changement de modèle ou prompt | Existence d'un dossier `evals/` ou framework type Promptfoo / Braintrust / DeepEval / Ragas | 🟡 |
| 4.2 | Score de pertinence mesuré sur les sorties IA (golden answers + similarity / LLM-as-judge) | Process documenté + dashboard ou rapports | 🟢 |
| 4.3 | Détection des hallucinations (output contredit input, faits inventés, citations falsifiées) | Sample de 50 sorties prod → manual review % erreurs | 🟡 |
| 4.4 | Prompt injection testé (user input contient "ignore instructions above", role play) | Soumettre 10 inputs hostiles → mesurer escape rate | 🔴 |
| 4.5 | Output filtré pour contenu prohibé (NSFW, instructions dangereuses, contenu illégal selon juridiction) | Tester prompts adversariaux → contenu bloqué ? | 🔴 |
| 4.6 | Versioning des prompts (commit dans le code, pas hardcodé inline non versionné) | grep — les prompts sont-ils dans des fichiers dédiés versionnés ? | 🟡 |
| 4.7 | Versioning du modèle (référence explicite à une version pinnée, pas "latest") | Inspecter l'appel SDK | 🟡 |
| 4.8 | Fallback déterministe quand l'IA échoue (rate limit, model down, output unparseable) | Couper la clé API → l'app a-t-elle un mode dégradé propre ? | 🔴 |
| 4.9 | Validation des outputs structurés (JSON schema / Pydantic / Zod) avec retry si malformé | Inspecter le post-traitement IA | 🟡 |
| 4.10 | Disclaimer visible "Généré par IA, peut contenir des erreurs" sur chaque sortie | Audit visuel sur les écrans contenant des outputs IA | 🟡 |
| 4.11 | Citation/source affichée si l'IA fait du RAG sur des documents internes | UI montre les passages utilisés ? | 🟢 |

---

## 5. IA — Coûts & Limites opérationnelles

| # | Point de contrôle | Comment tester | Crit. |
|---|---|---|---|
| 5.1 | Quota par utilisateur (crédits IA, calls/mois) avec compteur en DB | Tester épuisement → 402 / blocage propre | 🔴 |
| 5.2 | Coût par appel suivi et journalisé (tokens in/out × tarif modèle) | Existence d'une table d'usage IA ou métriques équivalentes | 🟡 |
| 5.3 | Budget global plateforme avec alerte automatique (seuil quotidien et mensuel) | Budget configuré côté fournisseur cloud + IA | 🔴 |
| 5.4 | Limite max de tokens par requête (anti coût explosif via prompt énorme) | Tester input de 100 000 caractères → refusé avant l'appel IA ? | 🔴 |
| 5.5 | Rate limit / file d'attente sur les calls IA (anti-DDoS coûteux) | Burst 100 calls/sec → 429 ou queue ? | 🟡 |
| 5.6 | Cache des prompts répétés (même input → même sortie servie depuis cache) | Tester 2× la même requête → temps de réponse < 100ms au 2nd appel | 🟢 |
| 5.7 | Modèle moins cher en fallback automatique sur les tâches simples (routing modèles) | Documentation du routing | 🟢 |
| 5.8 | Timeout sur l'appel modèle (≤ 30s) pour ne pas bloquer indéfiniment | Inspecter le code SDK + tester sur prompt lent | 🟡 |
| 5.9 | Free tier limité : signup bonus, pas un quota infini | Compte free → quota visible et opposable | 🟡 |
| 5.10 | Idempotency sur les calls IA payés (un retry réseau ne re-débite pas) | Tester double-call avec idem-key | 🟡 |
| 5.11 | Streaming activé pour les réponses longues (réduit perceived latency) | Inspecter — les calls retournent-ils en SSE / chunks ? | 🟢 |

---

## 6. IA — Gouvernance, transparence & cadre légal

| # | Point de contrôle | Comment tester | Crit. |
|---|---|---|---|
| 6.1 | Modèle(s) utilisé(s) + finalité divulgué(s) dans les CGU et la politique de confidentialité | Mentions légales + CGU — section IA explicite ? | 🔴 |
| 6.2 | Consentement explicite si l'IA prend une décision impactante (scoring, recommandation, modération) | UI de consentement présent avant feature IA-décisionnelle | 🟡 |
| 6.3 | Classification du système IA selon le cadre applicable (par ex. EU AI Act : minimal / limité / haut risque / interdit) | Classification documentée + actions selon catégorie | 🟡 |
| 6.4 | Opt-out fourniture de données pour entraînement (utilisateur ou par défaut) | Setting utilisateur "Ne pas utiliser mes données pour entraîner" | 🟡 |
| 6.5 | Watermarking ou disclosure obligatoire si l'output est susceptible d'être confondu avec un contenu humain (deepfake, image générée) | UI / metadata signalent l'origine IA | 🟢 |
| 6.6 | Provider IA déclaré comme sous-traitant dans le registre (et DPA signé) | Registre des sous-traitants à jour | 🔴 |
| 6.7 | "Model card" disponible pour les usages business (description, biais connus, limitations, données d'entraînement si publique) | Document accessible aux utilisateurs avancés | 🟢 |
| 6.8 | Pas de prise de décision purement automatisée à effet significatif sans humain dans la boucle | Audit des features IA → identifier décisions auto à fort impact | 🔴 |
| 6.9 | Logs d'inférence IA conservés (audit-trail) pour traçabilité (au moins prompt + timestamp + user, output si nécessaire) | Table de logs des prompts/outputs | 🟡 |
| 6.10 | Documentation interne du flux IA (data lineage : input → prompt → output → action métier) | Diagramme + doc d'architecture IA | 🟢 |
| 6.11 | Process documenté pour traiter une plainte sur une décision IA (rectification, recours humain) | Endpoint d'appel + email dédié | 🟡 |

---

## 7. Architecture & Scalabilité

| # | Point de contrôle | Comment tester | Crit. |
|---|---|---|---|
| 7.1 | Backend stateless (instances interchangeables, pas de session ni de cache critique en mémoire) | Tuer une instance pendant une opération longue → reprise propre ? | 🔴 |
| 7.2 | Pool de connexions DB borné avec timeout court (éviter saturation) | Inspecter la config de la couche d'accès aux données | 🔴 |
| 7.3 | Rate-limiter persistant (store partagé) si multi-instance, pas en mémoire d'une instance | Vérifier que le compteur est centralisé | 🟡 |
| 7.4 | Idempotency sur webhooks externes (paiement, IA async, etc.) via table dédiée | Re-jouer le même webhook → pas de double traitement | 🔴 |
| 7.5 | Job queue pour les tâches lourdes (encodage, IA longue, emails en masse) — pas tout en synchrone | Existence d'un worker / queue / task system | 🟡 |
| 7.6 | CDN devant les assets statiques | Cache-Control headers sur les `/assets/` | 🟢 |
| 7.7 | Health checks sur tous les services externes (DB, stockage, paiement, IA, email) | Endpoint `/health` retourne le statut de chaque dépendance | 🟡 |
| 7.8 | Migration DB testée sur staging avant prod, idempotente, réversible | Process de release documenté | 🔴 |
| 7.9 | Backup DB automatique + retention ≥ 7 jours + restore testé au moins 1 fois | Plan DR + dernier test de restore daté | 🔴 |
| 7.10 | Pas de single point of failure critique (DB répliquée, service critique multi-zones) | Diagramme d'archi + plan DR documenté | 🟡 |
| 7.11 | Capacité à scaler horizontalement (charge × 10 sans refactor) | Test de montée en charge ou audit d'archi | 🟡 |
| 7.12 | Environnements séparés (dev / staging / prod) avec secrets distincts | Variables d'env propres à chaque environnement | 🔴 |

---

## 8. Paiement, monétisation & financier

| # | Point de contrôle | Comment tester | Crit. |
|---|---|---|---|
| 8.1 | Webhooks paiement avec idempotency stockée (event ID en DB) | Re-jouer un webhook 2× → pas de double traitement | 🔴 |
| 8.2 | Webhooks paiement vérifient la signature du provider | Inspecter le code webhook | 🔴 |
| 8.3 | Subscription / état facturation synchronisé DB ↔ provider (cron de réconciliation) | Job de réconciliation existe ? Documenter divergences trouvées | 🟡 |
| 8.4 | Past-due / dunning : grace period documentée puis blocage features payantes | Tester invoice failed → comportement attendu | 🟡 |
| 8.5 | Process refund documenté (conditions, délai, qui peut le faire) | Mécanisme self-service ou support clair | 🟡 |
| 8.6 | Taxes (TVA, sales tax) calculées correctement selon pays acheteur | Test commande dans 3 juridictions différentes | 🔴 |
| 8.7 | Affichage TTC / HT explicite sur la page pricing selon les obligations locales | Audit visuel page pricing | 🔴 |
| 8.8 | Marketplace / payouts : KYC validé avant tout versement, vérification AML conforme | Tester payout impossible si KYC pending | 🟡 |
| 8.9 | Facturation automatique (PDF) + archivage selon obligations comptables locales | Facture envoyée par email + accessible dans le compte | 🔴 |
| 8.10 | Dashboard MRR / churn / LTV / cohortes pour le founder (pas juste le brut provider) | Dashboard analytics produit existe ? | 🟢 |
| 8.11 | Gestion des essais (trial) : conversion automatique ou manuelle annoncée clairement | Tester fin de trial → comportement et notif | 🟡 |
| 8.12 | Politique de proration claire en cas d'upgrade / downgrade en milieu de cycle | Tester upgrade Pro → Business → calcul cohérent | 🟡 |

---

## 9. Observabilité & Opérations

| # | Point de contrôle | Comment tester | Crit. |
|---|---|---|---|
| 9.1 | Logs structurés (JSON ou équivalent) avec severity et requestId/traceId | Inspecter les logs prod — exploitables par filtre ? | 🟡 |
| 9.2 | Aucune PII dans les logs (email, mot de passe, CB, token, prompt sensible) | grep sur les logs des 24h passées | 🔴 |
| 9.3 | Alertes automatiques sur erreurs 5xx > seuil | Alerte configurée et testée | 🔴 |
| 9.4 | Alerte budget (cloud, paiement provider, IA) en cas de dépassement seuil | Configuration vérifiée | 🟡 |
| 9.5 | Uptime monitoring externe (indépendant du cloud du SaaS lui-même) | Test : couper le service → alerte arrive en < 5 min | 🟡 |
| 9.6 | Playbook incident documenté (qui appeler, comment rollback, communication client) | Document type `RUNBOOK.md` ou équivalent | 🟡 |
| 9.7 | Status page publique pour les incidents | URL accessible publiquement | 🟢 |
| 9.8 | Métrique de latence p50/p95/p99 sur les endpoints critiques | Tracing distribué ou métriques applicatives | 🟢 |
| 9.9 | Capacité à rollback en < 5 min sur production | Versions précédentes accessibles, process documenté | 🔴 |
| 9.10 | Changelog visible utilisateurs (release notes) | URL `/changelog` ou widget "Quoi de neuf" | 🟢 |
| 9.11 | Process de gestion des erreurs côté client (Sentry / Rollbar / équivalent) | Tableau de bord des erreurs JS en prod | 🟡 |
| 9.12 | Métriques business clés (signup, conversion, activation) instrumentées | Dashboard avec ces 3 chiffres au moins | 🟡 |

---

## 10. Légal & Conformité

> **⚠️ Adapter selon la juridiction.** Cette section liste les contrôles courants ; certains sont obligatoires en UE et facultatifs ailleurs, ou inversement. Vérifier avec un juriste local.

| # | Point de contrôle | Comment tester | Crit. |
|---|---|---|---|
| 10.1 | Conditions Générales d'Utilisation (Terms of Service) acceptées explicitement à l'inscription (checkbox non pré-cochée) | Tester signup → blocage si non cochée | 🔴 |
| 10.2 | Conditions de vente / abonnement (Terms of Sale) disponibles avant le paiement | Audit du flow checkout — lien visible et fonctionnel | 🔴 |
| 10.3 | Politique de confidentialité (Privacy Policy) accessible depuis chaque page | Lien dans le footer présent partout | 🔴 |
| 10.4 | Mentions / informations légales obligatoires selon juridiction (éditeur, hébergeur, contact) | Audit mentions légales | 🔴 |
| 10.5 | Médiateur / mécanisme de résolution des litiges désigné si la juridiction l'impose pour le B2C | Mentions légales — coordonnées + URL | 🟡 |
| 10.6 | Droit de rétractation / cooling-off documenté si requis (UE : 14 jours B2C) | CGV — clause de rétractation présente ? | 🟡 |
| 10.7 | Hébergement de contenu utilisateur : régime de responsabilité documenté + procédure de notification/retrait | Endpoint de signalement ou équivalent | 🟡 |
| 10.8 | Cookies "non essentiels" listés avec finalité et possibilité de refus catégoriel | Bannière de cookies — détail par catégorie | 🔴 |
| 10.9 | Email de contact officiel répondant en délai imposé par la juridiction (UE RGPD : 30 jours pour demande d'accès) | Test : envoyer demande sur l'email officiel | 🟡 |
| 10.10 | Stockage durable des CGU acceptées (timestamp + version) par utilisateur | Champ `acceptedTermsAt` + version en DB | 🟡 |
| 10.11 | Process d'appel / recours si suspension de compte ou retrait de contenu | Endpoint d'appel ou email dédié | 🟡 |
| 10.12 | Accessibilité web (selon juridiction : WCAG AA pour services publics en UE ; ADA aux US, etc.) | Lighthouse a11y audit ≥ 90 | 🟡 |
| 10.13 | Mention du recours aux outils IA dans la politique de confidentialité et CGU | Section dédiée présente | 🔴 |

---

## 11. UX/UI — Qualité de design

> Au-delà de l'UX surface (thème 1), audit du **système de design** et de la cohérence visuelle.

| # | Point de contrôle | Comment tester | Crit. |
|---|---|---|---|
| 11.1 | Design system documenté (couleurs, typo, spacing, composants) avec règles d'usage | Existence d'un Storybook / Figma library / fichier `tokens.css` partagé | 🟡 |
| 11.2 | Palette de couleurs avec contraste WCAG AA validé sur tous les usages (texte sur fond, état hover, désactivé) | Audit avec contrast-checker sur les combinaisons utilisées | 🟡 |
| 11.3 | Hiérarchie typographique claire (max 3-4 niveaux), polices web-safe ou self-hosted (pas dépendance CDN tiers en SPOF) | Inspecter les `font-family` + Network tab → pas de blocking call externe | 🟡 |
| 11.4 | Spacing / grid system cohérent (échelle mathématique type 4/8/16/24/32) | Audit visuel — éléments alignés sur une grille ? | 🟢 |
| 11.5 | Composants UI réutilisables (boutons, inputs, modales) — pas 7 variations ad-hoc | `grep` ou Storybook : combien de Button différents dans le code ? | 🟡 |
| 11.6 | États visuels couverts pour chaque composant interactif : default / hover / focus / active / disabled / loading / error | Interagir avec chaque composant via souris ET clavier | 🟡 |
| 11.7 | Focus rings visibles (accessibilité clavier) sans être intrusifs visuellement | Tab à travers la page sur fond clair ET fond sombre | 🟡 |
| 11.8 | Touch targets ≥ 44×44 px sur mobile (reco Apple / Google) | Mode DevTools mobile + mesurer les zones tappables | 🟡 |
| 11.9 | Animations purposeful (transition ≤ 300 ms, pas gratuit) + respect de `prefers-reduced-motion` | Activer `prefers-reduced-motion: reduce` dans DevTools → animations stoppées ? | 🟢 |
| 11.10 | Empty states designés (pas un blanc) — chaque liste vide a un message + action | Tester chaque liste/tableau à vide | 🟡 |
| 11.11 | Error states informatifs (qu'est-ce qui s'est passé, comment corriger) | Provoquer chaque erreur — message actionable affiché ? | 🟡 |
| 11.12 | Loading states adaptés (skeletons pour listes, spinners pour actions, progress pour upload) | Throttler le réseau → feedback visuel cohérent | 🟢 |
| 11.13 | Iconographie cohérente (un seul set : Lucide / Heroicons / Material…) | Audit visuel — pas de mélange de styles | 🟢 |
| 11.14 | Branding complet : logo, favicons (multiple tailles), OG images, splash screen PWA, email templates harmonisés | Audit visuel des touchpoints non-app (emails, partage social, install PWA) | 🟡 |
| 11.15 | Breakpoints responsive documentés et appliqués (mobile-first idéalement) | Tester desktop / tablet / mobile / petit mobile (375px) | 🔴 |
| 11.16 | Progressive disclosure : ne pas tout montrer d'un coup (accordions, tabs, "Voir plus") | Audit cognitif des écrans denses | 🟢 |
| 11.17 | Undo > confirm modal sur les actions réversibles (un toast "Annuler" vaut mieux qu'une modale) | Comparer suppression légère vs suppression définitive | 🟢 |
| 11.18 | Notifications (toasts) cohérents : positionnement fixe, durée standardisée, dismissable | Déclencher plusieurs toasts en parallèle | 🟡 |
| 11.19 | Pas de "dark patterns" anti-utilisateur (croix introuvable, désabonnement caché, opt-in pré-coché, urgence factice) | Audit éthique — un tiers neutre repère-t-il un pattern manipulatoire ? | 🔴 |
| 11.20 | Cohérence multi-écrans : si on revient à un écran, l'état est préservé (scroll, filtres, sélection) | Tester nav avant/arrière dans le navigateur | 🟢 |

---

## 12. Cohérence Frontend ↔ Backend (contrats API)

> Beaucoup de bugs production viennent d'un décalage entre ce que le frontend attend et ce que le backend renvoie. Cette section audit le **contrat** entre les deux.

| # | Point de contrôle | Comment tester | Crit. |
|---|---|---|---|
| 12.1 | Types partagés frontend ↔ backend (OpenAPI, GraphQL, Zod monorepo, tRPC…) — pas de re-définition manuelle | Changer un champ backend → erreur TypeScript côté frontend ? | 🟡 |
| 12.2 | Format d'erreur API uniforme partout (par ex. `{ error: string, code?: string, fields?: {...} }`) | Inspecter 10 endpoints différents en erreur → même structure ? | 🔴 |
| 12.3 | HTTP status codes sémantiquement corrects (201 sur create, 204 sur delete, 400 invalid, 401 auth, 403 forbidden, 404 not found, 422 validation, 429 rate limit, 5xx serveur) | Tester chaque cas → bon code retourné ? | 🟡 |
| 12.4 | Verbes HTTP respectés (GET idempotent et sans effet de bord, POST create, PUT replace, PATCH partial, DELETE) | Audit route par route | 🟡 |
| 12.5 | Naming des champs cohérent dans toute la stack (camelCase OU snake_case partout, pas mélangé) | Inspecter 10 endpoints + frontend usage | 🟡 |
| 12.6 | Format de dates uniforme (ISO 8601 dans les réponses, parsing identique côté frontend) | Audit des champs `*At` / `*Date` | 🟡 |
| 12.7 | Pagination uniforme (offset/limit OU cursor partout, pas mélangé selon endpoint) | Inspecter 3-5 endpoints paginés | 🟡 |
| 12.8 | Validation frontend mirror exactement la validation backend (longueur min/max, regex, format email) | Bypass frontend → erreur backend ≡ erreur frontend ? | 🟡 |
| 12.9 | Frontend cache les boutons / features non autorisés (mais backend ne se repose pas sur ça — re-vérifie) | Inspecter token avec rôle limité → UI adaptée ET endpoint refuse | 🟡 |
| 12.10 | Optimistic UI avec rollback sur erreur (si utilisé) — pas de flash UI puis revert silencieux | Couper le réseau pendant une action optimiste → état revient ? | 🟢 |
| 12.11 | Cache invalidation après mutation (React Query / SWR refetch automatique, ou invalidation manuelle) | Modifier une ressource → la liste se rafraîchit sans reload page ? | 🟡 |
| 12.12 | WebSocket / SSE / polling : reconnexion automatique, état UI synchronisé après reconnexion | Couper le wifi 30s puis le rétablir → état cohérent ? | 🟢 |
| 12.13 | Timeout frontend (~30 s typique) cohérent avec timeout backend (pas frontend 5 s alors que backend prend 20 s) | Tester avec un endpoint lent | 🟡 |
| 12.14 | Messages traduits côté serveur OU côté frontend (mais pas mix : back en EN, front en FR) | Vérifier que les erreurs backend remontent avec les bonnes langues OU des codes que le frontend traduit | 🟡 |
| 12.15 | Versioning API : changement breaking → nouveau endpoint OU header `Accept-Version` (pas écraser silencieusement) | Audit changelog backend | 🟡 |
| 12.16 | Feature flags cohérents : si flag OFF côté backend, frontend ne propose pas la feature (pas de bouton mort) | Désactiver un flag → audit UI | 🟡 |
| 12.17 | Compatibilité descendante : un user avec ancien frontend en cache ne casse pas (déploiement progressif, backend supporte N-1) | Tester avec un build frontend de la semaine dernière | 🟡 |
| 12.18 | Assets / chunk hashing : nouvelles versions invalident le cache navigateur (Vite/Webpack hash dans le nom de fichier) | Inspecter le nom des chunks dans `/dist` | 🔴 |
| 12.19 | Auth via cookies : `credentials: 'include'` côté fetch + `Access-Control-Allow-Credentials: true` + origin spécifique côté CORS | Inspecter une requête authentifiée cross-origin | 🔴 |
| 12.20 | CORS configuré strictement (pas `Access-Control-Allow-Origin: *` si credentials, allowlist explicite) | Inspecter le header CORS sur l'API | 🔴 |
| 12.21 | Endpoint pour vérifier la santé / version (`/health`, `/version`) — le frontend peut alerter si version obsolète | Coller `/health` en URL → réponse exploitable ? | 🟢 |
| 12.22 | Idempotency-Key supporté sur les mutations critiques (paiement, IA payée, envoi email) | Tester double-call avec même idem-key → un seul effet ? | 🟡 |
| 12.23 | Cohérence des limites de taille (upload max côté frontend ≤ max côté backend ≤ max côté reverse-proxy / load balancer) | Tester upload juste au-dessus de la limite annoncée | 🟡 |
| 12.24 | Erreurs réseau gérées proprement côté frontend (retry exponentiel sur 5xx, abandon clair sur 4xx) | Couper le réseau → comportement attendu | 🟡 |

---

## Synthèse — Scoring & plan d'action

### Tableau de bord recommandé

| Thème | Points 🔴 | Points 🟡 | Points 🟢 | Score |
|---|---|---|---|---|
| 1. Produit & UX | 3 | 5 | 1 | / 11 |
| 2. Sécurité & Auth | 6 | 7 | 0 | / 14 |
| 3. Données & Confidentialité | 7 | 7 | 0 | / 14 |
| 4. IA Qualité | 3 | 6 | 2 | / 11 |
| 5. IA Coûts | 3 | 5 | 3 | / 11 |
| 6. IA Gouvernance | 3 | 6 | 2 | / 11 |
| 7. Architecture | 4 | 7 | 1 | / 12 |
| 8. Paiement | 4 | 7 | 1 | / 12 |
| 9. Observabilité | 3 | 6 | 3 | / 12 |
| 10. Légal | 5 | 7 | 0 | / 13 |
| 11. UX/UI Design | 2 | 9 | 9 | / 20 |
| 12. Frontend ↔ Backend | 4 | 16 | 3 | / 24 |
| 13. (Bonus contexte) | — | — | — | — |
| **TOTAL** | **47** | **88** | **30** | **/ 165** |

### Seuils de décision

- **> 90%** : Ready to scale — focus growth.
- **80-90%** : Ready to launch — fix les 🟡 sous 30 jours.
- **65-80%** : Ready bêta privée — fix tous les 🔴 avant ouverture publique.
- **< 65%** : Pas prêt pour la prod — chantier en cours.

### Ordre d'attaque suggéré

1. **Tous les 🔴** d'abord (bloquants launch)
2. **Légal + Données** ensuite (risque pénal / régulateur)
3. **Sécurité** ensuite (risque incident sécurité)
4. **IA Coûts + Gouvernance** ensuite (risque facture / risque image)
5. **Le reste** : amélioration continue

---

## Adapter à un contexte spécifique

Quelques exemples d'ajustements selon le type de SaaS :

- **SaaS B2B enterprise** : ajouter SOC 2 / ISO 27001, SLA contractuels, SSO/SAML, isolation tenant, DPA standard.
- **SaaS B2C grand public** : renforcer les sections Légal, Cookies, accessibilité, support multilingue, recours.
- **Marketplace / plateforme** : renforcer KYC/AML, modération de contenu, payouts, signalement, régime responsabilité hébergeur.
- **SaaS santé / médical** : ajouter HDS (FR) / HIPAA (US) / équivalent, audit-trail médical, niveau de sécurité supérieur.
- **SaaS finance / paiement** : PCI-DSS, AML, KYC, surveillance transactions, lutte fraude.
- **SaaS données critiques (RH, juridique, assurance)** : chiffrement renforcé, journalisation accès, droit d'audit client, exit clause.

---

## Annexe — Outils recommandés (par domaine)

| Domaine | Outils (gratuit · payant) |
|---|---|
| Security headers | securityheaders.com · Mozilla Observatory · SSL Labs |
| Web perf | Lighthouse · WebPageTest · PageSpeed Insights · k6 (load test) |
| Code quality | Sonar Cloud · CodeQL · Semgrep · ESLint security plugins |
| Secret scanning | GitGuardian · Trufflehog · `git secrets` · Gitleaks |
| Privacy / Cookies | Cookiebot · Axeptio · Didomi · Klaro |
| Eval IA | Promptfoo · Braintrust · LangSmith · DeepEval · Ragas (RAG) |
| Monitoring uptime | UptimeRobot · BetterStack · Datadog Synthetics |
| Status page | Instatus · BetterStack · Statuspage (Atlassian) · OhDear |
| Compliance docs (SOC 2 / ISO) | Vanta · Drata · Secureframe · Sprinto |
| Error tracking | Sentry · Rollbar · Bugsnag · Honeybadger |
| Accessibility | axe DevTools · Wave · Pa11y · Lighthouse a11y |
| Load testing | k6 · Artillery · Locust · Gatling |
| Design system | Storybook · Figma · Penpot · Chromatic (visual regression) |
| Contrast / WCAG | WebAIM Contrast Checker · Stark · Polypane |
| Design audit | Maze · Hotjar · FullStory · Microsoft Clarity |
| API contracts | OpenAPI Generator · Stoplight · Hoppscotch · Postman · Bruno |
| API typing | tRPC · GraphQL Codegen · `openapi-typescript` · Zod |
| Visual regression | Chromatic · Percy · BackstopJS · Playwright (snapshots) |
| End-to-end testing | Playwright · Cypress · WebdriverIO |
| Contract testing | Pact · Spring Cloud Contract · Schemathesis |

---

_Cette grille évolue avec la réglementation (AI Act, DSA en UE ; AI Bills d'États aux US ; etc.) et les bonnes pratiques du secteur. À relire et adapter tous les 6 mois._
