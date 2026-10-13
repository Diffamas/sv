# Questionnaire client (entretien d'une heure)

Chaque réponse remplit une clé du fichier `client.yaml`. Pose les questions dans l'ordre, note les réponses, lance le générateur : le dossier sort en une minute.

## 1. Identité (5 min)
| Question | Clé |
|---|---|
| Nom exact de l'entreprise tel qu'il figure sur le Kbis ? | raison_sociale |
| Forme juridique et capital ? | forme_juridique, forme_capital |
| Adresse du siège ? Ville ? | adresse, ville |
| SIRET ? Numéro RCS ou SIREN ? | siret, immatriculation |
| Numéro de TVA, ou franchise en base ? | tva |
| Qui signe : prénom, nom, fonction ? | representant, fonction |
| Email et téléphone à publier ? | email, telephone |
| Combien de salariés, intérimaires, stagiaires ? | effectif |

## 2. Site web (10 min)
| Question | Clé |
|---|---|
| Adresse du site ? | site |
| Qui l'héberge ? (regarder la facture ou demander à l'agence) | hebergeur, hebergeur_mentions |
| Qui l'a fait, qui le maintient ? | agence_web |
| Statistiques : Google Analytics, Matomo, rien ? | analytics, analytics_consentement |
| Vidéos YouTube, carte Google Maps intégrées ? | embeds |
| Publicité Meta, LinkedIn, TikTok ? | pixels |
| Formulaire de contact, prise de rendez-vous, boutique ? | traitements (WEB) |

## 3. Clients et prospection (10 min)
| Question | Clé |
|---|---|
| Où sont les clients : logiciel de facturation, caisse, tableur, CRM ? | logiciel_facturation |
| Particuliers, professionnels, les deux ? | traitements (CLI) |
| Envoi d'emails ou SMS commerciaux ? Avec quel outil ? Consentement recueilli ? | traitements (PRO) |
| Combien de temps gardez-vous les coordonnées d'un ancien client ? | (à comparer aux durées du kit) |

## 4. Salariés (10 min)
| Question | Clé |
|---|---|
| Qui fait la paie : vous, un logiciel, l'expert-comptable ? | comptable |
| Où sont les dossiers du personnel : papier, informatique, les deux ? Sous clé ? | (mesures de sécurité) |
| Recevez-vous des candidatures ? Combien de temps les gardez-vous ? | traitements (REC) |
| Badges, pointeuse, géolocalisation des véhicules ? | traitements (ACC, GEO : à ajouter à la main) |
| Charte informatique signée ? | (mesures de sécurité) |

## 5. Locaux et sécurité (10 min)
| Question | Clé |
|---|---|
| Caméras ? Combien, où, qui installe, qui a accès aux images, combien de jours ? Panneau d'affichage ? | videosurveillance, videosurveillance_prestataire |
| Messagerie : Gmail, Outlook, OVH, autre ? | messagerie |
| Qui dépanne l'informatique ? | prestataire_it |
| Sauvegardes ? Antivirus ? Mots de passe partagés ? | (mesures de sécurité) |
| Un outil américain ? (Google, Microsoft, Meta, Mailchimp, Canva…) | transfert_hors_ue |

## 6. Incidents et droits (5 min)
| Question | Clé |
|---|---|
| Déjà eu un piratage, une perte de données, un email envoyé au mauvais destinataire ? | (onglet Incidents) |
| Déjà reçu une demande de suppression ou d'accès ? Comment avez-vous répondu ? | (onglet Demandes de droits) |

## 7. Clôture (5 min)
- Rappeler ce qui sera livré et quand.
- Demander les contrats des prestataires (hébergeur, agence, comptable, caméras) par email.
- Fixer la date de la formation d'une heure.
