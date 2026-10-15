"""Fiches pratiques du site COTOMA (section Ressources), utilisé par build.py.

Une fiche = un fichier HTML dans page/ressources/, qui commence par un en-tête :
    <!--
    ordre: 1
    titre: titre complet de la page (balise <title> et <h1>)
    carte: titre court affiché sur la carte de la page d'accueil
    resume: une phrase sous le titre de la carte
    description: résumé pour Google (balise meta description)
    date: 2026-10-15
    lecture: 4 min
    -->
suivi du texte de la fiche en HTML (h2, p, ul, ol, table).
Pour ajouter une fiche : copier un fichier existant, changer l'en-tête et le texte, relancer build.py.
"""
import os, re, json, shutil, datetime as dt

MOIS = ['janvier', 'février', 'mars', 'avril', 'mai', 'juin', 'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre']


def esc(t):
    return t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')


def lire(path):
    txt = open(path, encoding='utf-8').read()
    m = re.match(r'\s*<!--(.*?)-->\s*', txt, re.S)
    meta = {k.strip(): v.strip() for k, v in (l.split(':', 1) for l in m.group(1).strip().splitlines() if ':' in l)}
    # Espace insécable avant : ; ? ! pour que la ponctuation ne passe jamais seule à la ligne.
    for k in ('titre', 'carte', 'resume', 'description'):
        meta[k] = re.sub(r' ([:;?!])', '\u00a0\\1', meta[k])
    meta['nom'] = os.path.splitext(os.path.basename(path))[0]
    meta['corps'] = re.sub(r' ([:;?!])(?=[\s<])', '\u00a0\\1', txt[m.end():])
    d = dt.date.fromisoformat(meta['date'])
    meta['date_fr'] = f"{d.day} {MOIS[d.month - 1]} {d.year}"
    meta['num'] = '%02d' % int(meta['ordre'])
    return meta


def charger(root):
    dossier = os.path.join(root, 'page', 'ressources')
    return sorted((lire(os.path.join(dossier, f)) for f in os.listdir(dossier) if f.endswith('.html')), key=lambda f: int(f['ordre']))


def remplir(src, fiches):
    """Regénère les cartes entre les repères ressources:debut et ressources:fin de la page d'accueil."""
    cartes = '\n'.join(
        '    <a class="fiche" href="ressources/%s/"><span class="ref">FICHE-%s · %s de lecture</span><h3>%s</h3><p>%s</p><span class="lire">Lire la fiche →</span></a>'
        % (f['nom'], f['num'], esc(f['lecture']), esc(f['carte']), esc(f['resume'])) for f in fiches)
    bloc = '  <div class="fiches">\n' + cartes + '\n  </div>\n'
    return re.sub(r'(<!-- ressources:debut[^>]*-->\n).*?(  <!-- ressources:fin -->)', lambda m: m.group(1) + bloc + m.group(2), src, count=1, flags=re.S)


STYLE_FICHE = """<style>
.fiche-page{max-width:44em;padding-block:36px 8px}
.fil{font-family:var(--mono);font-size:.78rem;color:var(--muted);letter-spacing:.04em;margin:0 0 18px}
.fil a{color:inherit}
.fiche-page h1{font-size:clamp(1.6rem,4vw,2.3rem);line-height:1.12}
.signature{font-size:.92rem;color:var(--muted);margin:14px 0 0}
.bref{background:var(--paper);border:1px solid var(--line);border-left:4px solid var(--accent);padding:16px 20px;margin:26px 0 8px}
.bref-title{font-family:var(--mono);font-size:.74rem;letter-spacing:.1em;text-transform:uppercase;color:var(--accent);margin:0 0 8px}
.bref ul{margin:0;padding-left:18px}.bref li{margin:4px 0}
.fiche-page h2{font-size:1.25rem;margin:34px 0 10px}
.fiche-page p{margin:0 0 14px}
.fiche-page ul,.fiche-page ol{padding-left:22px;margin:0 0 14px}.fiche-page li{margin:6px 0}
.fiche-page .tablewrap{margin:4px 0 14px}
.fiche-page code{font-family:var(--mono);font-size:.88em;background:var(--tint);padding:1px 5px}
.fiche-cta{background:var(--paper);border:1px solid var(--accent);box-shadow:0 0 0 1px var(--accent) inset;padding:20px 22px;margin:34px 0 0}
.fiche-cta h2{margin:0 0 8px}.fiche-cta p{color:var(--muted)}
.avert{font-size:.85rem;color:var(--muted);margin-top:22px}
.autres{border-top:1px solid var(--line);margin-top:34px;padding-top:22px}
.autres ul{list-style:none;padding:0;margin:0}.autres li{margin:0;border-top:1px solid var(--line)}.autres li:first-child{border-top:0}
.autres a{display:block;padding:10px 0;color:var(--fg);font-weight:600;text-decoration:none}
.autres a:hover,.autres a:focus-visible{color:var(--accent);text-decoration:underline;text-underline-offset:3px}
</style>"""

# Thème choisi par le visiteur sur la page d'accueil, et le même compteur de visites anonyme (voir Confidentialité).
SCRIPT = """<script>
(function(){var r=document.documentElement,s=null;try{s=JSON.parse(localStorage.getItem('cotoma-theme')||'null');}catch(e){}
if(s&&s.p&&s.p!=='encre')r.setAttribute('data-palette',s.p);if(s&&(s.m==='light'||s.m==='dark'))r.setAttribute('data-theme',s.m);
var a=document.querySelector('.top nav a[aria-current]');if(a&&a.parentNode.scrollWidth>a.parentNode.clientWidth)a.parentNode.scrollLeft=a.offsetLeft-16;})();
(function(){
  if(location.hostname!=='cotoma.fr'||navigator.globalPrivacyControl||navigator.doNotTrack==='1'||!window.fetch)return;
  var ref='';try{ref=document.referrer?new URL(document.referrer).hostname:'';}catch(e){}
  var src='';try{var q=new URLSearchParams(location.search);src=q.get('src')||q.get('utm_source')||'';}catch(e){}
  var body=JSON.stringify({action:'visite',page:location.pathname,ref:ref,src:src,appareil:matchMedia('(max-width:720px)').matches?'mobile':'ordinateur'});
  try{fetch('/app/api.php',{method:'POST',body:body,keepalive:true,credentials:'same-origin',headers:{'Content-Type':'text/plain'}}).catch(function(){});}catch(e){}
})();
</script>"""

PAGE = """<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{titre} · COTOMA</title>
<meta name="description" content="{description}">
<meta name="robots" content="index,follow">
<meta name="referrer" content="no-referrer">
<link rel="canonical" href="{url}">
<script type="application/ld+json">{ld}</script>
{icone}
{style}
{style_fiche}
</head>
<body>
<div class="wrap">
<header class="top">
  <a class="brand" href="/" style="color:inherit;text-decoration:none">COTOMA<small>Conformité RGPD · TPE et PME · Seine-et-Marne</small></a>
  {nav}
</header>
<article class="fiche-page">
  <p class="fil"><a href="/">Accueil</a> › <a href="/#ressources">Ressources</a> › Fiche {num}</p>
  <p class="eyebrow">Fiche pratique · {lecture} de lecture</p>
  <h1>{titre}</h1>
  <p class="signature">Par Mattis Maupin, COTOMA · {date_fr}</p>
{corps}
  <aside class="fiche-cta">
    <h2>Vous voulez savoir où en est votre entreprise ?</h2>
    <p>Envoyez-moi l'adresse de votre site : audit express gratuit sous 48 h, avec les trois premiers points à corriger.</p>
    <a class="btn" href="/#contact">Demander l'audit express gratuit</a>
  </aside>
  <p class="avert">Fiche d'information générale, à jour au {date_fr}. Elle ne remplace pas un avis juridique adapté à votre situation.</p>
  <nav class="autres" aria-label="Autres fiches"><p class="eyebrow">Autres fiches pratiques</p><ul>{autres}</ul></nav>
</article>
<footer>
  <p>COTOMA, nom commercial de Mattis Maupin, entrepreneur individuel, 52 bis rue de Montgelard, 77130 La Grande-Paroisse. <a href="/#mentions" style="color:inherit">Mentions légales</a> · <a href="/#confidentialite" style="color:inherit">Confidentialité</a></p>
  <p>Ce site ne dépose aucun cookie et ne contient aucun traceur.</p>
</footer>
</div>
{script}
</body>
</html>
"""


def construire(here, fiches, src, icone):
    """Écrit site/ressources/<nom>/index.html pour chaque fiche. src : page d'accueil avec les polices déjà intégrées."""
    # Les fiches sont un dossier plus bas : les polices sont appelées depuis la racine du site.
    style = '\n'.join(re.findall(r'<style>.*?</style>', src, re.S)).replace('url(fonts/', 'url(/fonts/')
    nav = re.search(r'<nav aria-label="Sections">.*?</nav>', src, re.S).group(0).replace('href="#', 'href="/#')
    nav = nav.replace('<a href="/#ressources">', '<a href="/#ressources" aria-current="true">')
    sortie = os.path.join(here, 'ressources')
    shutil.rmtree(sortie, ignore_errors=True)
    for f in fiches:
        url = 'https://cotoma.fr/ressources/%s/' % f['nom']
        ld = json.dumps({'@context': 'https://schema.org', '@type': 'Article', 'headline': f['titre'], 'description': f['description'],
                         'datePublished': f['date'], 'dateModified': f['date'], 'inLanguage': 'fr', 'mainEntityOfPage': url,
                         'author': {'@type': 'Person', 'name': 'Mattis Maupin'},
                         'publisher': {'@type': 'Organization', 'name': 'COTOMA', 'url': 'https://cotoma.fr/'}}, ensure_ascii=False)
        autres = ''.join('<li><a href="/ressources/%s/">%s</a></li>' % (o['nom'], esc(o['carte'])) for o in fiches if o is not f)
        page = PAGE.format(titre=esc(f['titre']), description=esc(f['description']), url=url, ld=ld.replace('</', '<\\/'), icone=icone,
                           style=style, style_fiche=STYLE_FICHE, nav=nav, num=f['num'], lecture=esc(f['lecture']), date_fr=f['date_fr'],
                           corps=f['corps'], autres=autres, script=SCRIPT)
        os.makedirs(os.path.join(sortie, f['nom']), exist_ok=True)
        open(os.path.join(sortie, f['nom'], 'index.html'), 'w', encoding='utf-8').write(page)
    return sortie


def sitemap(fiches):
    return ''.join('<url><loc>https://cotoma.fr/ressources/%s/</loc><lastmod>%s</lastmod></url>' % (f['nom'], f['date']) for f in fiches)
