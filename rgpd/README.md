# Activité RGPD : tout est dans ce dossier

| Fichier | Rôle |
|---|---|
| `OFFRE.md` | La décision, les trois packs et leurs prix, l'usage des 25 €, l'ordre des opérations, le seuil de rentabilité |
| `prospection.md` | Profil Malt, post LinkedIn, trois emails, script téléphonique, relances, où trouver les prospects |
| `page/index.html` | Page de présentation de l'offre (publiée, lien dans la conversation). Remplacer [Prénom Nom], [email pro], [téléphone], SIRET |
| `outil-audit/audit_site.py` | Audit express d'une liste de sites : score et accroche de prospection par site |
| `outil-audit/prospects-sud77.txt` | Liste de départ de sites locaux, à enrichir |
| `outil-audit/resultats-sud77.csv` | Résultat de l'audit sur cette liste |
| `outil-audit/prospects-montereau.csv` | Entreprises et commerces de Montereau relevés dans l'annuaire de la mairie, avec adresse et téléphone, pour la prospection téléphonique |
| `kit-rgpd-tpe/` | Les 8 documents du kit : base de travail pour chaque mission, et produit numérique à vendre 49 € |

## Lancer l'audit

```
cd rgpd/outil-audit
python3 audit_site.py prospects-sud77.txt -o resultats-sud77.csv
```

Dépendances : `pip install requests beautifulsoup4`.

## Regénérer le kit après modification

```
cd rgpd/kit-rgpd-tpe
python3 generer_kit.py
```
