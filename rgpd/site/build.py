#!/usr/bin/env python3
"""Construit le site public COTOMA (dossier site/) à partir de page/index.html.

    python3 build.py

- remplace les polices Google par les polices hébergées dans site/fonts/
- ajoute le squelette HTML complet, la description, l'icône, le robots.txt, le sitemap
- écrit le .htaccess (HTTPS forcé, en-têtes de sécurité, cache)
Le contenu reste identique à la page publiée sur claude.ai : modifie page/index.html, relance build.py, envoie site/ sur OVH.
"""
import os, re, datetime as dt
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(HERE)
src=open(os.path.join(ROOT,'page','index.html'),encoding='utf-8').read()
fonts=open(os.path.join(HERE,'fonts','fonts.css'),encoding='utf-8').read()
src=re.sub(r'<link rel="stylesheet" href="https://fonts\.googleapis\.com[^"]*">', '<style>'+fonts+'</style>', src)
assert 'googleapis' not in src, 'il reste une référence à Google Fonts'
head='''<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="description" content="COTOMA : mise en conformité RGPD à prix fixe pour TPE et PME en Seine-et-Marne. Registre, politiques, cookies, réponses EcoVadis et CyberVadis.">
<meta name="robots" content="index,follow">
<meta name="referrer" content="no-referrer">
<link rel="canonical" href="https://cotoma.fr/">
<script type="application/ld+json">{"@context":"https://schema.org","@type":"ProfessionalService","name":"COTOMA","description":"Mise en conformité RGPD à prix fixe pour TPE et PME : audit, registre des traitements, politiques, cookies, réponses EcoVadis et CyberVadis.","url":"https://cotoma.fr/","email":"contact@cotoma.fr","telephone":"+33788403495","founder":{"@type":"Person","name":"Mattis Maupin"},"address":{"@type":"PostalAddress","streetAddress":"52 bis rue de Montgelard","postalCode":"77130","addressLocality":"La Grande-Paroisse","addressCountry":"FR"},"areaServed":["Seine-et-Marne","Yonne","France"],"priceRange":"290 € - 1990 €","knowsAbout":["RGPD","protection des données personnelles","registre des traitements","EcoVadis","CyberVadis"]}</script>
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' fill='%2315233b'/%3E%3Ctext x='16' y='22' font-size='18' font-family='Arial' font-weight='bold' fill='%23fff' text-anchor='middle'%3EC%3C/text%3E%3C/svg%3E">
<style>:root{color-scheme:light}body{margin:0;font-family:system-ui,sans-serif}img{max-width:100%}[hidden]{display:none!important}</style>
'''
i=src.index('<div class="wrap">')
out=head+src[:i]+'</head>\n<body>\n'+src[i:]+'\n</body>\n</html>\n'
open(os.path.join(HERE,'index.html'),'w',encoding='utf-8').write(out)
open(os.path.join(HERE,'robots.txt'),'w').write('User-agent: *\nAllow: /\nSitemap: https://cotoma.fr/sitemap.xml\n')
open(os.path.join(HERE,'sitemap.xml'),'w').write(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>https://cotoma.fr/</loc><lastmod>{dt.date.today()}</lastmod></url></urlset>\n')
open(os.path.join(HERE,'.htaccess'),'w').write('''# COTOMA — hébergement OVH (Apache)
# HTTPS obligatoire
RewriteEngine On
# Redirection HTTPS (le certificat Let's Encrypt cotoma.fr est actif). Double condition pour ne pas boucler derrière le répartiteur OVH.
RewriteCond %{HTTPS} !=on
RewriteCond %{HTTP:X-Forwarded-Proto} !=https
RewriteRule ^ https://%{HTTP_HOST}%{REQUEST_URI} [L,R=301]
# www -> sans www
RewriteCond %{HTTP_HOST} ^www\\.(.+)$ [NC]
RewriteRule ^ https://%1%{REQUEST_URI} [L,R=301]
# En-têtes de sécurité : rien ne se charge depuis un tiers
<IfModule mod_headers.c>
Header always set Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; font-src 'self'; img-src 'self' data:; connect-src 'none'; frame-ancestors 'none'; form-action 'none'; base-uri 'self'; object-src 'none'"
Header always set X-Content-Type-Options "nosniff"
Header always set Referrer-Policy "no-referrer"
Header always set Permissions-Policy "camera=(), microphone=(), geolocation=(), interest-cohort=()"
Header always set Strict-Transport-Security "max-age=31536000"
Header always set X-Frame-Options "DENY"
</IfModule>
# Cache : polices un an, page une heure
<IfModule mod_expires.c>
ExpiresActive On
ExpiresByType font/woff2 "access plus 1 year"
ExpiresByType text/html "access plus 1 hour"
</IfModule>
AddType font/woff2 .woff2
AddDefaultCharset UTF-8
ErrorDocument 404 /index.html
''')
print('site construit :', os.path.join(HERE,'index.html'), len(out), 'octets')
