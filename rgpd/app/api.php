<?php
// COTOMA — API du tableau de bord : une base SQLite, un mot de passe, des documents JSON par collection.
declare(strict_types=1);
require __DIR__ . '/config.php';
header('Content-Type: application/json; charset=utf-8');
header('Cache-Control: no-store');
header('X-Content-Type-Options: nosniff');

$secure = (!empty($_SERVER['HTTPS']) && $_SERVER['HTTPS'] !== 'off') || (($_SERVER['HTTP_X_FORWARDED_PROTO'] ?? '') === 'https');
$cookiePath = rtrim(dirname($_SERVER['SCRIPT_NAME']), '/') ?: '/';
// Les sessions sont stockées dans la base SQLite, pas dans les sessions PHP : sur un hébergement mutualisé
// à plusieurs serveurs, une session PHP peut ne pas être partagée d'une requête à l'autre.
function cookie_set(string $token, int $exp, bool $secure, string $path): void {
    setcookie('cotoma', $token, ['expires' => $exp, 'path' => $path, 'secure' => $secure, 'httponly' => true, 'samesite' => 'Strict']);
}

function out(array $o, int $code = 200): void { http_response_code($code); echo json_encode($o, JSON_UNESCAPED_UNICODE); exit; }
function fail(string $m, int $code = 400): void { out(['error' => $m], $code); }

if (!is_dir($COTOMA_DATA_DIR)) { @mkdir($COTOMA_DATA_DIR, 0750, true); }
if (!is_writable($COTOMA_DATA_DIR)) fail('Le dossier data/ n\'est pas accessible en écriture.', 500);
// Base v2 : journal classique (pas de WAL) pour rester cohérente sur le stockage partagé entre les serveurs OVH.
$pdo = new PDO('sqlite:' . $COTOMA_DATA_DIR . '/cotoma-v2.sqlite');
$pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
$pdo->exec('PRAGMA journal_mode=DELETE');
$pdo->exec('PRAGMA synchronous=FULL');
$pdo->exec('PRAGMA busy_timeout=5000');
$pdo->exec('CREATE TABLE IF NOT EXISTS docs (collection TEXT NOT NULL, id TEXT NOT NULL, data TEXT NOT NULL, version INTEGER NOT NULL DEFAULT 1, updated_at TEXT NOT NULL, PRIMARY KEY (collection, id))');
$pdo->exec('CREATE TABLE IF NOT EXISTS attempts (ip TEXT NOT NULL, ts INTEGER NOT NULL)');
$pdo->exec('CREATE TABLE IF NOT EXISTS journal (ts TEXT NOT NULL, action TEXT NOT NULL, collection TEXT, id TEXT)');
$pdo->exec('CREATE TABLE IF NOT EXISTS sessions (token TEXT PRIMARY KEY, expires INTEGER NOT NULL, created TEXT NOT NULL)');
// Visites du site public : uniquement des totaux par jour, sans adresse IP, sans cookie, sans identifiant de visiteur.
$pdo->exec('CREATE TABLE IF NOT EXISTS visites (jour TEXT NOT NULL, page TEXT NOT NULL, source TEXT NOT NULL, appareil TEXT NOT NULL, n INTEGER NOT NULL, PRIMARY KEY (jour, page, source, appareil))');
$pdo->prepare('DELETE FROM sessions WHERE expires < ?')->execute([time()]);
$SESSION_TTL = 43200; // 12 heures, prolongées à chaque requête
$token = (string)($_COOKIE['cotoma'] ?? '');
$auth = false;
if (preg_match('/^[a-f0-9]{64}$/', $token)) {
    $st = $pdo->prepare('SELECT expires FROM sessions WHERE token = ?'); $st->execute([$token]);
    if ($st->fetchColumn() !== false) { $auth = true; $pdo->prepare('UPDATE sessions SET expires = ? WHERE token = ?')->execute([time() + $SESSION_TTL, $token]); cookie_set($token, time() + $SESSION_TTL, $secure, $cookiePath); }
}

// Premier démarrage : importe data/seed.json si la base est vide.
$count = (int)$pdo->query('SELECT COUNT(*) FROM docs')->fetchColumn();
$seed = $COTOMA_DATA_DIR . '/seed-v2.json';
if ($count === 0 && is_file($seed)) {
    $s = json_decode((string)file_get_contents($seed), true);
    if (is_array($s)) {
        $ins = $pdo->prepare('INSERT OR IGNORE INTO docs (collection, id, data, version, updated_at) VALUES (?,?,?,1,?)');
        $pdo->beginTransaction();
        foreach ($s as $coll => $docs) foreach ($docs as $id => $data) $ins->execute([$coll, $id, json_encode($data, JSON_UNESCAPED_UNICODE), gmdate('c')]);
        $pdo->commit();
        @rename($seed, $seed . '.importe');
    }
}

// Coordonnées ajoutées après le premier import : complète les champs encore vides des paramètres (une seule fois).
$cfgRow = $pdo->query("SELECT data, version FROM docs WHERE collection = 'parametres' AND id = 'config'")->fetch(PDO::FETCH_ASSOC);
if ($cfgRow) {
    $cfg = json_decode($cfgRow['data'], true) ?: [];
    $fixVille = !empty($cfg['adresse']) && str_ends_with($cfg['adresse'], '77130 Montereau-Fault-Yonne');
    if (empty($cfg['nom']) || $fixVille) {
        $src = is_file($seed) ? $seed : (is_file($seed . '.importe') ? $seed . '.importe' : null);
        $s = $src ? json_decode((string)file_get_contents($src), true) : null;
        $def = $s['parametres']['config'] ?? [];
        $changed = false;
        foreach (['nom', 'adresse', 'telephone', 'email', 'forme'] as $k) {
            if (empty($cfg[$k]) && !empty($def[$k])) { $cfg[$k] = $def[$k]; $changed = true; }
        }
        if (!empty($cfg['adresse']) && str_ends_with($cfg['adresse'], '77130 Montereau-Fault-Yonne')) { $cfg['adresse'] = str_replace('77130 Montereau-Fault-Yonne', '77130 La Grande-Paroisse', $cfg['adresse']); $changed = true; }
        if ($changed) $pdo->prepare("UPDATE docs SET data = ?, version = version + 1, updated_at = ? WHERE collection = 'parametres' AND id = 'config'")->execute([json_encode($cfg, JSON_UNESCAPED_UNICODE), gmdate('c')]);
    }
}

$method = $_SERVER['REQUEST_METHOD'];
$body = [];
if ($method === 'POST') {
    $body = json_decode((string)file_get_contents('php://input'), true) ?: [];
    // Le compteur de visites et le formulaire de contact du site public sont les seules écritures acceptées sans l'en-tête du tableau de bord.
    if (!in_array($body['action'] ?? '', ['visite', 'contact'], true) && ($_SERVER['HTTP_X_COTOMA'] ?? '') !== '1') fail('Requête refusée.', 403);
}
$action = $body['action'] ?? $_GET['action'] ?? 'status';
// Derrière le répartiteur de charge OVH, l'adresse du visiteur est dans X-Forwarded-For.
$ip = trim(explode(',', (string)($_SERVER['HTTP_X_FORWARDED_FOR'] ?? ''))[0]) ?: ($_SERVER['REMOTE_ADDR'] ?? '0');
$COLLS = ['prospects', 'clients', 'factures', 'parametres'];

$JOUR = (new DateTimeImmutable('now', new DateTimeZone('Europe/Paris')))->format('Y-m-d');

// Provenance d'une visite : le nom du site d'origine seulement (jamais l'adresse complète), ou la campagne (?src=).
function visite_source(string $ref, string $src): string {
    $src = strtolower(trim($src));
    if ($src !== '' && preg_match('/^[a-z0-9_-]{1,40}$/', $src)) return 'campagne : ' . $src;
    $h = strtolower(trim($ref));
    if ($h === '' || !preg_match('/^[a-z0-9.-]{1,253}$/', $h)) return 'Accès direct';
    $h = preg_replace('/^(www|m|l|lm)\./', '', $h);
    if ($h === 'cotoma.fr') return 'Accès direct';
    $connus = ['/(^|\.)google\./' => 'Google', '/(^|\.)bing\.com$/' => 'Bing', '/duckduckgo\.com$/' => 'DuckDuckGo', '/qwant\.com$/' => 'Qwant', '/ecosia\.org$/' => 'Ecosia', '/(^|\.)yahoo\./' => 'Yahoo',
        '/(linkedin\.com|lnkd\.in)$/' => 'LinkedIn', '/(facebook\.com|fb\.com|fb\.me)$/' => 'Facebook', '/instagram\.com$/' => 'Instagram', '/(^t\.co|twitter\.com|^x\.com)$/' => 'X (Twitter)',
        '/malt\.(fr|com)$/' => 'Malt', '/pagesjaunes\.fr$/' => 'PagesJaunes', '/(chatgpt\.com|openai\.com|perplexity\.ai|claude\.ai)$/' => 'Assistant IA'];
    foreach ($connus as $re => $nom) if (preg_match($re, $h)) return $nom;
    return substr($h, 0, 60);
}

function coll(string $c, array $COLLS): string { if (!in_array($c, $COLLS, true)) fail('Collection inconnue.'); return $c; }
function docid(string $id): string { if (!preg_match('/^[A-Za-z0-9_.~:@+-]{1,200}$/', $id)) fail('Identifiant invalide.'); return $id; }

switch ($action) {
    case 'ping':
        // Diagnostic sans données : un compteur qui doit augmenter à chaque appel si les écritures sont bien partagées.
        $pdo->exec('CREATE TABLE IF NOT EXISTS meta (k TEXT PRIMARY KEY, v TEXT)');
        $pdo->exec("INSERT INTO meta (k, v) VALUES ('ping', '0') ON CONFLICT(k) DO UPDATE SET v = CAST(CAST(v AS INTEGER) + 1 AS TEXT)");
        out(['ping' => (int)$pdo->query("SELECT v FROM meta WHERE k = 'ping'")->fetchColumn(), 'node' => substr(hash('sha256', (string)gethostname()), 0, 8)]);
    case 'visite':
        if ($method !== 'POST') fail('Méthode.', 405);
        if ($auth) out(['ok' => true]); // tes propres visites, connecté au tableau de bord, ne comptent pas
        $ua = (string)($_SERVER['HTTP_USER_AGENT'] ?? ''); // lu pour écarter les robots, jamais enregistré
        if ($ua === '' || preg_match('/bot|crawl|spider|slurp|headless|preview|lighthouse|monitor|curl|wget|python/i', $ua)) out(['ok' => true]);
        $page = (string)($body['page'] ?? '/'); if (!preg_match('#^/[A-Za-z0-9/_.-]{0,80}$#', $page)) $page = '/';
        $source = visite_source((string)($body['ref'] ?? ''), (string)($body['src'] ?? ''));
        $appareil = ($body['appareil'] ?? '') === 'mobile' ? 'mobile' : 'ordinateur';
        // Garde-fous contre le remplissage : 20 000 vues et 300 lignes par jour au plus.
        $st = $pdo->prepare('SELECT COALESCE(SUM(n), 0), COUNT(*) FROM visites WHERE jour = ?'); $st->execute([$JOUR]); [$tot, $lignes] = $st->fetch(PDO::FETCH_NUM);
        if ((int)$tot >= 20000) out(['ok' => true]);
        if ((int)$lignes >= 300) { $st = $pdo->prepare('SELECT 1 FROM visites WHERE jour = ? AND page = ? AND source = ? AND appareil = ?'); $st->execute([$JOUR, $page, $source, $appareil]); if (!$st->fetchColumn()) { $page = '/'; $source = 'autre'; } }
        $pdo->prepare('INSERT INTO visites (jour, page, source, appareil, n) VALUES (?,?,?,?,1) ON CONFLICT(jour, page, source, appareil) DO UPDATE SET n = n + 1')->execute([$JOUR, $page, $source, $appareil]);
        // Durée de conservation : 25 mois, comme le recommande la CNIL pour la mesure d'audience.
        $pdo->prepare('DELETE FROM visites WHERE jour < ?')->execute([(new DateTimeImmutable($JOUR))->modify('-25 months')->format('Y-m-d')]);
        out(['ok' => true]);
    case 'contact':
        // Formulaire de contact du site : la demande devient un prospect « À contacter », priorité 1, et un email t'avertit.
        // Ni adresse IP, ni cookie, ni navigateur enregistrés : uniquement ce que la personne a écrit.
        if ($method !== 'POST') fail('Méthode.', 405);
        $origin = (string)($_SERVER['HTTP_ORIGIN'] ?? '');
        if ($origin !== '' && !preg_match('#^https?://(www\.)?cotoma\.fr$#', $origin)) fail('Requête refusée.', 403);
        if (trim((string)($body['web'] ?? '')) !== '') out(['ok' => true]); // champ piège invisible : rempli par un robot, ignoré en silence
        if ((int)($body['t'] ?? 0) < 3000) fail('Envoi trop rapide : réessayez dans quelques secondes.', 429);
        $clean = fn($v, int $max) => mb_substr(trim(preg_replace('/[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]/u', '', (string)$v) ?? ''), 0, $max);
        $nom = preg_replace('/\s+/u', ' ', $clean($body['nom'] ?? '', 120));
        $email = $clean($body['email'] ?? '', 160);
        $site = preg_replace('/\s+/u', '', $clean($body['site'] ?? '', 200));
        $message = $clean($body['message'] ?? '', 3000);
        if ($nom === '') fail('Indiquez votre nom ou celui de votre entreprise.');
        if (!filter_var($email, FILTER_VALIDATE_EMAIL)) fail('Adresse email invalide.');
        if ($site === '' && $message === '') fail('Indiquez l\'adresse de votre site ou écrivez un message.');
        // Garde-fou contre le remplissage : 30 demandes par jour au plus, compteur sans donnée personnelle.
        $pdo->exec('CREATE TABLE IF NOT EXISTS meta (k TEXT PRIMARY KEY, v TEXT)');
        $st = $pdo->prepare('SELECT v FROM meta WHERE k = ?'); $st->execute(['contact:' . $JOUR]);
        if ((int)$st->fetchColumn() >= 30) fail('Trop de demandes aujourd\'hui : écrivez directement à contact@cotoma.fr.', 429);
        $pdo->prepare("INSERT INTO meta (k, v) VALUES (?, '1') ON CONFLICT(k) DO UPDATE SET v = CAST(CAST(v AS INTEGER) + 1 AS TEXT)")->execute(['contact:' . $JOUR]);
        $pdo->prepare("DELETE FROM meta WHERE k LIKE 'contact:%' AND k < ?")->execute(['contact:' . $JOUR]);
        $id = 'site-' . str_replace('-', '', $JOUR) . '-' . bin2hex(random_bytes(3));
        $doc = ['nom' => $nom, 'email' => $email, 'site' => $site, 'telephone' => '', 'adresse' => '', 'categorie' => 'Demande via le site', 'secteur' => '', 'quartier' => '',
            'statut' => 'a_contacter', 'priorite' => 1, 'pack_vise' => '', 'montant_potentiel' => 0, 'score' => '', 'accroche' => '', 'raison' => 'A écrit via le formulaire du site : demande entrante, à rappeler en premier.',
            'source' => 'Formulaire du site', 'cree' => $JOUR, 'maj' => '', 'relance' => '', 'note' => $message,
            'historique' => [['date' => $JOUR, 'action' => 'Message reçu via le site', 'note' => mb_substr($message, 0, 300)]]];
        $pdo->prepare('INSERT INTO docs (collection, id, data, version, updated_at) VALUES (?,?,?,1,?)')->execute(['prospects', $id, json_encode($doc, JSON_UNESCAPED_UNICODE), gmdate('c')]);
        $pdo->prepare('INSERT INTO journal (ts, action, collection, id) VALUES (?,?,?,?)')->execute([gmdate('c'), 'contact', 'prospects', $id]);
        // Avertissement par email (OVH). Si l'envoi échoue, la demande reste dans le tableau de bord.
        $txt = "Nouvelle demande depuis cotoma.fr\n\nNom ou entreprise : $nom\nEmail : $email\nSite : " . ($site ?: '(non indiqué)') . "\n\nMessage :\n" . ($message ?: '(aucun)') . "\n\nElle est aussi dans le tableau de bord, onglet À contacter : https://cotoma.fr/app/\n";
        $headers = "From: COTOMA site <contact@cotoma.fr>\r\nReply-To: $email\r\nContent-Type: text/plain; charset=utf-8\r\nContent-Transfer-Encoding: 8bit\r\nMIME-Version: 1.0";
        @mail('contact@cotoma.fr', '=?UTF-8?B?' . base64_encode('Demande site : ' . mb_substr($nom, 0, 60)) . '?=', $txt, $headers, '-fcontact@cotoma.fr');
        out(['ok' => true]);
    case 'status':
        out(['auth' => $auth, 'setup' => $COTOMA_PASSWORD === 'change-moi', 'v' => 3]);
    case 'login':
        if ($method !== 'POST') fail('Méthode.', 405);
        if ($COTOMA_PASSWORD === 'change-moi' || strlen($COTOMA_PASSWORD) < 12) fail('Définis d\'abord un mot de passe d\'au moins 12 caractères dans config.php.', 503);
        $pdo->prepare('DELETE FROM attempts WHERE ts < ?')->execute([time() - 900]);
        $n = (int)$pdo->query("SELECT COUNT(*) FROM attempts WHERE ip = " . $pdo->quote($ip))->fetchColumn();
        if ($n >= 10) fail('Trop de tentatives. Réessaie dans 15 minutes.', 429);
        usleep(400000);
        if (!hash_equals($COTOMA_PASSWORD, (string)($body['password'] ?? ''))) {
            $pdo->prepare('INSERT INTO attempts (ip, ts) VALUES (?,?)')->execute([$ip, time()]);
            fail('Mot de passe incorrect.', 401);
        }
        $token = bin2hex(random_bytes(32));
        $pdo->prepare('INSERT INTO sessions (token, expires, created) VALUES (?,?,?)')->execute([$token, time() + $SESSION_TTL, gmdate('c')]);
        cookie_set($token, time() + $SESSION_TTL, $secure, $cookiePath);
        $pdo->prepare('DELETE FROM attempts WHERE ip = ?')->execute([$ip]);
        out(['auth' => true]);
    case 'logout':
        if ($token !== '') $pdo->prepare('DELETE FROM sessions WHERE token = ?')->execute([$token]);
        cookie_set('', time() - 3600, $secure, $cookiePath); out(['auth' => false]);
    case 'export':
        $tok = (string)($_GET['token'] ?? '');
        if (!$auth && !($COTOMA_EXPORT_TOKEN !== '' && hash_equals($COTOMA_EXPORT_TOKEN, $tok))) fail('Non autorisé.', 401);
        $outp = [];
        foreach ($pdo->query('SELECT collection, id, data, version, updated_at FROM docs ORDER BY collection, id') as $r)
            $outp[$r['collection']][$r['id']] = ['data' => json_decode($r['data'], true), 'version' => (int)$r['version'], 'updated_at' => $r['updated_at']];
        header('Content-Disposition: attachment; filename="cotoma-export-' . gmdate('Y-m-d') . '.json"');
        out(['exported_at' => gmdate('c'), 'collections' => $outp]);
}

if (!$auth) fail('Connexion requise.', 401);

switch ($action) {
    case 'all':
        $res = array_fill_keys($COLLS, []);
        foreach ($pdo->query('SELECT collection, id, data, version FROM docs') as $r)
            $res[$r['collection']][] = ['id' => $r['id'], 'data' => json_decode($r['data'], true), 'version' => (int)$r['version']];
        out(['collections' => $res, 'at' => gmdate('c')]);
    case 'list':
        $c = coll((string)($body['collection'] ?? $_GET['collection'] ?? ''), $COLLS);
        $st = $pdo->prepare('SELECT id, data, version FROM docs WHERE collection = ? ORDER BY id'); $st->execute([$c]);
        $rows = []; foreach ($st as $r) $rows[] = ['id' => $r['id'], 'data' => json_decode($r['data'], true), 'version' => (int)$r['version']];
        out(['docs' => $rows]);
    case 'set':
    case 'update':
        if ($method !== 'POST') fail('Méthode.', 405);
        $c = coll((string)($body['collection'] ?? ''), $COLLS); $id = docid((string)($body['id'] ?? ''));
        $data = $body['data'] ?? null; if (!is_array($data)) fail('Données invalides.');
        unset($data['id']);
        $st = $pdo->prepare('SELECT data, version FROM docs WHERE collection = ? AND id = ?'); $st->execute([$c, $id]); $cur = $st->fetch(PDO::FETCH_ASSOC);
        if ($action === 'update') { if (!$cur) fail('Document introuvable.', 404); $data = array_replace(json_decode($cur['data'], true) ?: [], $data); }
        $json = json_encode($data, JSON_UNESCAPED_UNICODE); if (strlen($json) > 262144) fail('Document trop volumineux.');
        if ($cur) $pdo->prepare('UPDATE docs SET data = ?, version = version + 1, updated_at = ? WHERE collection = ? AND id = ?')->execute([$json, gmdate('c'), $c, $id]);
        else $pdo->prepare('INSERT INTO docs (collection, id, data, version, updated_at) VALUES (?,?,?,1,?)')->execute([$c, $id, $json, gmdate('c')]);
        $pdo->prepare('INSERT INTO journal (ts, action, collection, id) VALUES (?,?,?,?)')->execute([gmdate('c'), $action, $c, $id]);
        out(['ok' => true, 'version' => $cur ? (int)$cur['version'] + 1 : 1]);
    case 'delete':
        if ($method !== 'POST') fail('Méthode.', 405);
        $c = coll((string)($body['collection'] ?? ''), $COLLS); $id = docid((string)($body['id'] ?? ''));
        if ($c === 'factures') { $st = $pdo->prepare('SELECT data FROM docs WHERE collection = ? AND id = ?'); $st->execute([$c, $id]); $d = $st->fetchColumn();
            if ($d) { $f = json_decode($d, true); if (($f['statut'] ?? '') !== 'brouillon') fail('Un document émis ne se supprime pas : annule-le par un avoir.', 409); } }
        $pdo->prepare('DELETE FROM docs WHERE collection = ? AND id = ?')->execute([$c, $id]);
        $pdo->prepare('INSERT INTO journal (ts, action, collection, id) VALUES (?,?,?,?)')->execute([gmdate('c'), 'delete', $c, $id]);
        out(['ok' => true]);
    case 'visites':
        $jours = max(1, min(800, (int)($body['jours'] ?? $_GET['jours'] ?? 400)));
        $depuis = (new DateTimeImmutable($JOUR))->modify('-' . ($jours - 1) . ' days')->format('Y-m-d');
        $st = $pdo->prepare('SELECT jour, page, source, appareil, n FROM visites WHERE jour >= ? ORDER BY jour'); $st->execute([$depuis]);
        $rows = []; foreach ($st as $r) $rows[] = [$r['jour'], $r['page'], $r['source'], $r['appareil'], (int)$r['n']];
        out(['jour' => $JOUR, 'depuis' => $depuis, 'lignes' => $rows]);
    default:
        fail('Action inconnue.', 404);
}
