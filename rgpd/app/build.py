#!/usr/bin/env python3
"""Construit le tableau de bord auto-hébergé (app/index.html) à partir de dashboard/index.html.

    python3 build.py

Transformations : polices locales, jsPDF local, couche de données remote.js (api.php + mot de passe),
téléchargement direct des PDF, squelette HTML complet, noindex, écran de connexion.
"""
import os, re
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
src = open(os.path.join(ROOT, 'dashboard', 'index.html'), encoding='utf-8').read()
fonts = open(os.path.join(HERE, 'fonts', 'fonts.css'), encoding='utf-8').read()
src, n1 = re.subn(r'<link rel="stylesheet" href="https://fonts\.googleapis\.com[^"]*">', '<style>' + fonts + '</style>', src)
src, n2 = re.subn(r'<script src="https://cdnjs\.cloudflare\.com/ajax/libs/jspdf/[^"]+"></script>', '<script src="lib/jspdf.umd.min.js"></script>\n<script src="remote.js"></script>', src)
old = "const [db,user,dl]=await Promise.all([window.claude?.use?.('db'),window.claude?.use?.('user'),window.claude?.use?.('downloads')]);"
assert old in src, 'ligne de démarrage introuvable dans dashboard/index.html'
src = src.replace(old, "const [db,user,dl]=await window.remoteBoot();")
assert n1 == 1 and n2 == 1, (n1, n2)
assert 'googleapis' not in src and 'cdnjs' not in src and 'claude.use' not in src.replace('claude?.use', '')
login_css = '''<style>
#login{position:fixed;inset:0;background:var(--bg);display:flex;align-items:center;justify-content:center;z-index:50;padding:16px}
#login[hidden]{display:none}
.login-box{background:var(--paper);border:1px solid var(--line);padding:28px;width:100%;max-width:380px;display:flex;flex-direction:column;gap:10px}
.login-box h2{margin:0 0 6px}
.login-box label{font-family:var(--mono);font-size:.78rem;color:var(--muted)}
.login-box input{font:inherit;font-size:1rem;padding:10px;border:1px solid var(--line);background:var(--bg);color:var(--fg)}
.login-box .note{min-height:1.2em;margin:0}
</style>'''
src = src.replace('</style>\n\n<div class="wrap">', '</style>\n' + login_css + '\n<div class="wrap">', 1)
# bouton de déconnexion dans la navigation
src = src.replace('<button role="tab" aria-selected="false" data-tab="bilan">Bilan</button>\n  </nav>', '<button role="tab" aria-selected="false" data-tab="bilan">Bilan</button>\n    <button type="button" onclick="window.cotomaLogout()" title="Se déconnecter">Quitter</button>\n  </nav>', 1)
head = '''<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="robots" content="noindex, nofollow">
<meta name="referrer" content="no-referrer">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' fill='%2315233b'/%3E%3Ctext x='16' y='22' font-size='18' font-family='Arial' font-weight='bold' fill='%23fff' text-anchor='middle'%3EC%3C/text%3E%3C/svg%3E">
<style>:root{color-scheme:light}body{margin:0;font-family:system-ui,sans-serif}img{max-width:100%}[hidden]{display:none!important}</style>
'''
i = src.index('<div class="wrap">')
out = head + src[:i] + '</head>\n<body>\n' + src[i:] + '\n</body>\n</html>\n'
open(os.path.join(HERE, 'index.html'), 'w', encoding='utf-8').write(out)
print('app construit :', len(out), 'octets')
