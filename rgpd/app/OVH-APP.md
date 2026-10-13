# Mettre le tableau de bord sur cotoma.fr/app

Le dossier `app/` est le tableau de bord complet, autonome : une page, une API PHP (`api.php`), une base SQLite créée toute seule dans `data/`, un mot de passe. Il fonctionne sur l'offre Perso d'OVH sans rien installer. Testé de bout en bout : connexion, actions de prospection, paramètres, devis brouillon, PDF, émission numérotée.

## 1. Avant l'envoi : le mot de passe (1 minute)

Ouvre `config.php` et remplace `change-moi` par un mot de passe long, 12 caractères au moins, que tu es seul à connaître. Sans ça, l'API refuse toute connexion. Optionnel : mets aussi un jeton dans `COTOMA_EXPORT_TOKEN` pour pouvoir télécharger une sauvegarde complète par une simple adresse.

## 2. Envoyer (5 minutes)

Par l'explorateur FTP d'OVH ou FileZilla, crée le dossier `www/app` et envoie dedans, en gardant la structure :

- `index.html`, `api.php`, `config.php`, `remote.js`, `.htaccess`
- `data/` avec `seed.json` et `.htaccess` (tes 363 prospects et tes paramètres : importés automatiquement au premier accès, puis le fichier est renommé `.importe`)
- `fonts/` (10 fichiers) et `lib/` (jsPDF)

Ne pas envoyer `build.py` ni ce fichier.

## 3. Droits sur `data/` (1 minute)

Dans l'explorateur FTP, clic droit sur le dossier `data` → permissions → écriture pour le propriétaire (755 ou 750 suffit chez OVH, PHP tourne avec ton compte). Si la page affiche « data/ n'est pas accessible en écriture », c'est ici que ça se règle.

## 4. Ouvrir (1 minute)

https://cotoma.fr/app/ → écran de connexion → ton mot de passe. Le tableau de bord s'ouvre avec les 363 entreprises à contacter.

## Sécurité, ce qui est en place

- Mot de passe obligatoire, session en cookie sécurisé, 10 essais ratés par quart d'heure maximum.
- La base, la configuration et les sauvegardes ne sont jamais servies par le web (`.htaccess`), même en tapant l'adresse.
- Aucun script ni police chargés depuis un tiers ; en-têtes de sécurité stricts ; page exclue des moteurs de recherche.
- Une facture émise ne peut pas être supprimée, même par l'API.
- Journal des écritures dans la base (table `journal`).

## Sauvegarde

Une fois par semaine : https://cotoma.fr/app/api.php?action=export&token=TON_JETON télécharge toutes les données en JSON. Garde-les dans un dossier à toi. OVH fait aussi ses propres sauvegardes de l'hébergement.

## Mettre à jour

Je modifie `dashboard/index.html` ou `app/remote.js`, je lance `python3 app/build.py`, tu renvoies `index.html` et `remote.js` par FTP. La base n'est pas touchée.

## Le tableau de bord claude.ai

Il reste en ligne mais ne se synchronise pas avec OVH. Dès que cotoma.fr/app fonctionne, travaille uniquement dessus. Si tu veux que je lise ou corrige tes données depuis une conversation, donne-moi l'adresse d'export avec le jeton : je pourrai lire, pas écrire.
