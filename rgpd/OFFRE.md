# Plan B : vendre ta compétence RGPD, pas des vêtements

Décision prise le 13 octobre 2026, hors Shopify, sans stock, sans pub.

## Pourquoi celle-là et pas une autre

J'ai regardé ce que tu as déjà produit. Dans ton Drive, il y a un dossier RGPD complet livré en mai-juin 2026 pour un groupe industriel multi-sites (registre de 8 traitements, PIA sur l'outil CNIL, politiques confidentialité et cookies, procédure de violation de données, tableau des durées de conservation, cartographie des sous-traitants, gouvernance, pack CyberVadis). C'est exactement le livrable qu'un consultant facture entre 450 et 850 € la journée sur Malt ou via la CCI.

Les autres pistes à 25 € tiennent moins bien :
- Print-on-demand Seven Starz (Printful + Etsy) : zéro stock mais 8 à 12 € de marge par pièce et aucun trafic. Il faudrait 200 ventes pour que ça compte.
- Revente Vinted / Leboncoin : 25 € d'achat, 10 à 20 € de gain par cycle, beaucoup de temps.
- Trading, paris, crypto : non.

La compétence RGPD a trois avantages : capital zéro, marge 100 %, et une demande qui monte. La CNIL a prononcé 23 sanctions en procédure simplifiée depuis janvier 2026 (133 750 € d'amendes cumulées), surtout sur les cookies et la vidéosurveillance, et ce sont des petites structures qui sont visées par cette procédure. En parallèle, les grands donneurs d'ordre imposent EcoVadis et CyberVadis à leurs fournisseurs, qui ne savent pas répondre.

## L'offre (prix fixes, TTC car micro-entreprise en franchise de TVA)

| Pack | Prix | Pour qui | Contenu | Durée |
|---|---|---|---|---|
| Site conforme | 290 € | Artisan, commerce, indépendant avec un site | Audit du site, mentions légales, politique de confidentialité, politique cookies, réglage de la bannière, mention d'information sur le formulaire | 2 jours |
| Conformité TPE | 790 € | TPE de 1 à 20 salariés | Tout le pack Site + registre des traitements, durées de conservation, cartographie des sous-traitants et clauses, procédure violation de données, registre des demandes de droits, 1 h de formation du gérant | 1 semaine |
| PME / questionnaire client | à partir de 1 490 € ou 400 €/jour | PME à qui un client impose EcoVadis, CyberVadis, un appel d'offres ou un audit | Tout le pack TPE + PIA sur l'outil CNIL, gouvernance, mesures de sécurité documentées, réponses au questionnaire, preuves | 2 à 4 semaines |
| Suivi | 49 €/mois | Clients des packs TPE et PME | Mise à jour annuelle du registre, veille, réponse aux demandes de droits et aux incidents | continu |

Un seul pack Site conforme couvre 11 fois les 25 €. Un pack TPE couvre un mois de vie.

## Ce que je t'ai construit (dossier rgpd/)

1. `outil-audit/audit_site.py` : tu lui donnes une liste de sites, il te sort un score sur 10 et une accroche de prospection personnalisée par site (HTTPS, mentions légales, politique de confidentialité, bannière cookies, traceurs Google/Meta chargés sans consentement, Google Fonts, formulaire sans case de consentement). Testé : il fonctionne.
2. `outil-audit/prospects-sud77.txt` : première liste de sites locaux à auditer, et `resultats-sud77.csv` avec les résultats.
3. `prospection.md` : profil Malt, post LinkedIn, 3 emails de prospection, script téléphonique, relances.
4. `kit-rgpd-tpe/` : un kit de 8 documents (registre Excel pré-rempli pour une TPE type, politiques, mentions légales, procédure violation, clause sous-traitant, checklist, guide). Deux usages : c'est ta base de travail pour chaque mission, et c'est un produit numérique à vendre 49 € sur Gumroad ou ComeUp pour un revenu sans temps passé.
5. Page de présentation publiée (lien dans mon message) : à partager avec les prospects.

## Comment dépenser les 25 €

| Poste | Montant |
|---|---|
| Rien avant le premier client | 0 € |
| Domaine .fr pour une adresse email pro (OVH, Gandi, Ionos) : prenom-nom.fr ou rgpd-sud77.fr | 7 à 10 € l'année |
| Reste | garde-le : Malt, ComeUp, LinkedIn, Gumroad et la CCI sont gratuits à l'inscription |

Malt prend 10 % sur les missions trouvées via la plateforme, Gumroad 10 % + frais sur les ventes du kit. Les clients trouvés par email ou téléphone ne coûtent rien.

## Ordre des opérations (cette semaine)

1. Micro-entreprise : activité « conseil pour les affaires » (code NAF 70.22Z), gratuit sur autoentrepreneur.urssaf.fr. Charges : 24,6 % du chiffre encaissé, pas de TVA en dessous de 37 500 € de prestations.
2. Demander à ton contact chez le client industriel l'autorisation de le citer en référence, ou au minimum une recommandation LinkedIn. Sans nom, la référence « groupe industriel multi-sites, 9 sites, 2026 » suffit.
3. Créer le profil Malt avec le texte de prospection.md, TJM 400 €.
4. Lancer l'outil d'audit sur 50 sites locaux, envoyer 20 emails ciblés avec l'accroche générée. Taux de réponse réaliste : 5 à 10 %, donc 1 à 2 rendez-vous, 1 client sur 3 rendez-vous.
5. Publier le kit sur Gumroad à 49 €.
6. Poster sur LinkedIn une fois par semaine : un manquement courant, comment le corriger.

## Seuil de rentabilité

- Dépenses : 0 à 10 €.
- Premier pack Site conforme : 290 € encaissés, 219 € nets après charges.
- Objectif réaliste à 60 jours : 2 packs Site + 1 pack TPE = 1 370 € encaissés.
