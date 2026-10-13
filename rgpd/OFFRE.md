# COTOMA — vendre ta compétence RGPD, pas des vêtements

Nom commercial : COTOMA. À déclarer comme nom commercial de l'entreprise individuelle au guichet unique (champ « nom commercial »), pour pouvoir l'utiliser sur les factures et la page.

Décision prise le 13 octobre 2026, hors Shopify, sans stock, sans pub.

## Pourquoi celle-là et pas une autre

J'ai regardé ce que tu as déjà produit. Dans ton Drive, il y a un dossier RGPD complet livré en mai-juin 2026 pour un groupe industriel multi-sites (registre, PIA sur l'outil CNIL, politiques, procédure de violation de données, durées de conservation, sous-traitants, gouvernance, réponses à un questionnaire sécurité client). C'est exactement le livrable qu'un consultant facture entre 450 et 850 € la journée sur Malt ou via la CCI.

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
| PME / questionnaire client | à partir de 1 990 € ou 500 €/jour | PME à qui un client impose EcoVadis, CyberVadis, un appel d'offres ou un audit | Tout le pack TPE + PIA sur l'outil CNIL, gouvernance, mesures de sécurité documentées, réponses au questionnaire, preuves | 2 à 4 semaines |
| Suivi | 89 €/mois | Clients des packs TPE et PME | Mise à jour annuelle du registre, veille, réponse aux demandes de droits et aux incidents | continu |

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
2. Le client ne sera pas cité : la référence reste « groupe industriel multi-sites, 2026 », sans nom, sans secteur, sans nombre de sites. Une recommandation LinkedIn de ton contact, si elle vient de lui, reste possible.
3. Créer le profil Malt avec le texte de prospection.md, TJM 500 €.
4. Lancer l'outil d'audit sur 50 sites locaux, envoyer 20 emails ciblés avec l'accroche générée. Taux de réponse réaliste : 5 à 10 %, donc 1 à 2 rendez-vous, 1 client sur 3 rendez-vous.
5. Publier le kit sur Gumroad à 49 €.
6. Poster sur LinkedIn une fois par semaine : un manquement courant, comment le corriger.

## Seuil de rentabilité

- Dépenses : 0 à 10 €.
- Premier pack Site conforme : 290 € encaissés, 219 € nets après charges.
- Objectif réaliste à 60 jours : 2 packs Site + 1 pack TPE = 1 370 € encaissés.

## Conformité de la facturation (vérifiée le 13 octobre 2026)

Ce que le tableau de bord applique sur chaque devis, facture et avoir :

| Obligation | Texte | Comment c'est appliqué |
|---|---|---|
| Numéro unique, chronologique, sans trou | art. 242 nonies A ann. II CGI | Numéro attribué à l'émission, une séquence par type et par année (F-, D-, AV-). Un brouillon n'a pas de numéro et peut être supprimé ; un document émis ne se modifie plus. |
| Identité de l'émetteur avec « EI » ou « entrepreneur individuel », adresse, SIRET | art. L526-22 C. com., L441-9 C. com. | Paramètres obligatoires avant émission. |
| Identité et adresse du client, SIREN du client entre professionnels | décret 2022-1299, en vigueur depuis le 1er septembre 2026 | Émission refusée sans SIREN sauf client particulier. |
| Nature de l'opération, adresse de livraison | décret 2022-1299 | Ligne « prestation de services, lieu d'exécution : adresse du client ». |
| Date d'émission, date de la prestation | art. L441-9 | Contrôle : la prestation ne peut pas être postérieure à l'émission. |
| Désignation, quantité, prix unitaire HT, total | art. L441-9 | Lignes détaillées. |
| TVA : mention « TVA non applicable, art. 293 B du CGI » | art. 293 B CGI | Imprimée sur chaque document tant que tu es en franchise. |
| Échéance, pénalités de retard à 3 fois le taux légal, indemnité de 40 €, pas d'escompte | art. L441-10 et D441-5 C. com. | Imprimées entre professionnels. Délai plafonné à 60 jours. |
| Particuliers : médiateur de la consommation, droit de rétractation | art. L616-1 et L221-18 C. conso | Émission refusée sans médiateur renseigné. |
| Avoir pour corriger une facture émise | art. 242 nonies A | Bouton « Annuler par un avoir », référence croisée. |
| Conservation 10 ans | art. L123-22 C. com. | PDF à archiver chez toi, export CSV depuis Bilan. |

Ce qui reste à ta charge :

1. **Médiateur de la consommation** : si tu factures des particuliers, tu dois adhérer à un médiateur agréé avant la première vente (CM2C, Médicys, AME, environ 50 à 100 € par an). Pour des clients professionnels uniquement, pas besoin.
2. **Facturation électronique** : depuis le 1er septembre 2026, obligation de pouvoir recevoir des factures électroniques via une plateforme agréée, même en franchise de TVA. Choisis-en une maintenant sur la liste d'impots.gouv.fr ; plusieurs ont une offre gratuite pour les micro-entreprises. À partir du 1er septembre 2027, tes factures aux professionnels devront partir par cette plateforme et tes ventes aux particuliers être déclarées en e-reporting. Le tableau de bord devra alors exporter vers la plateforme : je l'ajouterai quand tu l'auras choisie.
3. **Logiciel de caisse certifié** : l'obligation de certification (art. 286 I 3° bis CGI) ne s'applique pas tant que tu es en franchise en base. Si tu dépasses les seuils et deviens redevable de la TVA, il faudra un outil attesté par son éditeur.
4. **Archivage** : la base du tableau de bord est en ligne. Télécharge chaque PDF émis et fais un export CSV par trimestre dans un dossier de sauvegarde.
5. **Une seule personne émet** : la numérotation se calcule dans la page ; n'émets pas deux factures en même temps depuis deux appareils.
