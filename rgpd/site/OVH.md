# Mettre COTOMA en ligne chez OVH

Le dossier `site/` est prêt : une page, les polices hébergées localement, aucun appel vers un tiers, mentions légales et politique de confidentialité intégrées, `.htaccess` qui force le HTTPS et pose les en-têtes de sécurité.

## 1. Commander (15 minutes, environ 50 € TTC la première année)

1. ovhcloud.com → Hébergement web → offre **Perso**. Vérifie le prix affiché au moment de la commande : OVH a annoncé une hausse pour les renouvellements à partir de juin 2026. L'offre inclut un nom de domaine la première année et le certificat SSL.
2. Pendant la commande, ajoute le domaine **cotoma.fr** (disponible au 13 octobre 2026). Choisis la durée d'un an.
3. Coordonnées du titulaire : ton nom, ton adresse. Pour un .fr, un particulier ou une entreprise établie dans l'UE suffit.
4. Après paiement, tu reçois un email « Installation terminée » avec les identifiants FTP. Compte une à deux heures.

## 2. Envoyer les fichiers (10 minutes)

Option A, sans logiciel : espace client OVH → Hébergements → ton hébergement → onglet FTP-SSH → « Explorateur FTP ». Entre dans le dossier `www`, supprime le fichier `index.html` d'exemple, puis envoie :

- `index.html`
- `.htaccess` (fichier caché : active l'affichage des fichiers cachés dans l'explorateur)
- `robots.txt`
- `sitemap.xml`
- le dossier `fonts/` avec ses 10 fichiers

Option B, avec FileZilla (gratuit) : hôte `ftp.cluster0XX.hosting.ovh.net` (indiqué dans l'email), identifiant et mot de passe FTP, port 21. Glisse les mêmes fichiers dans `www`.

## 3. Activer le HTTPS (2 minutes)

Espace client → ton hébergement → Informations générales → bloc « Certificat SSL » → « Commander un certificat SSL » → Let's Encrypt, gratuit. Le certificat est posé sous une heure. Le `.htaccess` redirige ensuite tout le trafic vers https://cotoma.fr.

## 4. Vérifier (5 minutes)

- https://cotoma.fr s'ouvre avec le cadenas, http:// et www. redirigent.
- Dans le navigateur, F12 → onglet Réseau : toutes les requêtes doivent partir de cotoma.fr. Aucune vers Google ou un autre domaine.
- Sur securityheaders.com, entre cotoma.fr : les en-têtes posés par le `.htaccess` doivent apparaître.
- Remplace les cinq champs entre crochets dans `page/index.html` (nom, adresse, SIRET, email, téléphone, et le médiateur si tu factures des particuliers), relance `python3 build.py`, renvoie `index.html`.

## 5. Email professionnel

L'offre Perso inclut des adresses email sur ton domaine : espace client → Emails → créer `contact@cotoma.fr`. Hébergé en France, c'est ce qu'il faut écrire dans la politique de confidentialité comme « hébergeur de messagerie : OVH, France ». Mets cette adresse dans la page de présentation et sur les factures.

## Mettre à jour le site plus tard

Modifie `rgpd/page/index.html` (ou demande-moi), lance `python3 rgpd/site/build.py`, renvoie `site/index.html` dans `www` par FTP. Rien d'autre ne change.

## Ce que le site respecte

| Règle | Comment |
|---|---|
| Mentions légales (LCEN art. 6-III) | Section « Mentions légales » : éditeur, SIRET, contact, directeur de publication, hébergeur OVH |
| Information des personnes (RGPD art. 13) | Section « Confidentialité » : données, finalités, bases légales, durées, destinataires, droits, CNIL |
| Cookies et traceurs (loi Informatique et Libertés art. 82) | Aucun cookie, aucun traceur, aucune mesure d'audience. Le thème choisi est une préférence stockée localement, exemptée de consentement |
| Transferts hors UE | Aucun : polices hébergées sur le site, hébergeur et messagerie en France |
| Sécurité (RGPD art. 32) | HTTPS forcé, HSTS, politique de sécurité du contenu stricte, pas de formulaire, pas de script tiers |
| Médiation de la consommation (C. conso L616-1) | Champ prévu dans les mentions légales, à remplir si tu factures des particuliers |
