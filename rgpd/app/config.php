<?php
// COTOMA — configuration du tableau de bord. Ce fichier n'est jamais servi tel quel : PHP l'exécute.
// 1. Mets ici un mot de passe long (12 caractères ou plus). C'est le seul accès au tableau de bord.
$COTOMA_PASSWORD = 'change-moi';
// 2. Jeton d'export pour les sauvegardes (lecture seule). Laisse vide pour désactiver.
//    Exemple d'usage : https://cotoma.fr/app/api.php?action=export&token=TON_JETON
$COTOMA_EXPORT_TOKEN = '';
// 3. Dossier des données (base SQLite). Doit être accessible en écriture par PHP.
$COTOMA_DATA_DIR = __DIR__ . '/data';
