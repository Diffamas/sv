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
    if (($_SERVER['HTTP_X_COTOMA'] ?? '') !== '1') fail('Requête refusée.', 403);
    $body = json_decode((string)file_get_contents('php://input'), true) ?: [];
}
$action = $body['action'] ?? $_GET['action'] ?? 'status';
// Derrière le répartiteur de charge OVH, l'adresse du visiteur est dans X-Forwarded-For.
$ip = trim(explode(',', (string)($_SERVER['HTTP_X_FORWARDED_FOR'] ?? ''))[0]) ?: ($_SERVER['REMOTE_ADDR'] ?? '0');
$COLLS = ['prospects', 'clients', 'factures', 'parametres'];

function coll(string $c, array $COLLS): string { if (!in_array($c, $COLLS, true)) fail('Collection inconnue.'); return $c; }
function docid(string $id): string { if (!preg_match('/^[A-Za-z0-9_.~:@+-]{1,200}$/', $id)) fail('Identifiant invalide.'); return $id; }

switch ($action) {
    case 'ping':
        // Diagnostic sans données : un compteur qui doit augmenter à chaque appel si les écritures sont bien partagées.
        $pdo->exec('CREATE TABLE IF NOT EXISTS meta (k TEXT PRIMARY KEY, v TEXT)');
        $pdo->exec("INSERT INTO meta (k, v) VALUES ('ping', '0') ON CONFLICT(k) DO UPDATE SET v = CAST(CAST(v AS INTEGER) + 1 AS TEXT)");
        out(['ping' => (int)$pdo->query("SELECT v FROM meta WHERE k = 'ping'")->fetchColumn(), 'node' => substr(hash('sha256', (string)gethostname()), 0, 8)]);
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
    default:
        fail('Action inconnue.', 404);
}
