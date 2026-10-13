#!/usr/bin/env python3
"""Audit RGPD express d'une liste de sites web (prospection).

Usage :
    python3 audit_site.py sites.txt                # un domaine ou une URL par ligne
    python3 audit_site.py sites.txt -o resultats.csv

Pour chaque site, le script vérifie ce qui se voit depuis l'extérieur :
HTTPS, mentions légales, politique de confidentialité, politique cookies,
bannière de consentement (CMP), traceurs chargés (Google Analytics, Meta pixel,
Google Tag Manager, Google Fonts, YouTube, reCAPTCHA), formulaire de contact,
case de consentement dans le formulaire. Il attribue un score sur 10 et rédige
une accroche de prospection personnalisée.

Ce n'est pas un audit juridique : c'est un détecteur de manques visibles,
suffisant pour décrocher un rendez-vous.
"""
import argparse
import csv
import re
import sys
import time
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")
TIMEOUT = 15

LEGAL_PATTERNS = {
    "mentions": re.compile(r"mentions?\s*l[ée]gales?|legal", re.I),
    "confidentialite": re.compile(r"confidentialit|donn[ée]es\s*personnelles|vie\s*priv[ée]e|privacy|rgpd|gdpr", re.I),
    "cookies": re.compile(r"cookies?|traceurs?", re.I),
    "cgv": re.compile(r"\bcgv\b|conditions\s*g[ée]n[ée]rales", re.I),
}

CMP_SIGNATURES = {
    "tarteaucitron": r"tarteaucitron",
    "Axeptio": r"axept\.io|axeptio",
    "Cookiebot": r"cookiebot",
    "Didomi": r"didomi",
    "OneTrust": r"onetrust|optanon",
    "Complianz": r"complianz|cmplz",
    "CookieYes": r"cookieyes|cookie-law-info",
    "Orejime": r"orejime",
    "Klaro": r"klaro",
    "Iubenda": r"iubenda",
    "Usercentrics": r"usercentrics",
    "Quantcast": r"quantcast",
    "Wix/Shopify natif": r"consent-?banner|cookie-?consent|cookieconsent|cookie-?notice|cookie-?bar",
}

TRACKER_SIGNATURES = {
    "Google Analytics": r"google-analytics\.com|googletagmanager\.com/gtag|gtag\(|_gaq|UA-\d{4,}|G-[A-Z0-9]{6,}",
    "Google Tag Manager": r"googletagmanager\.com/gtm\.js|GTM-[A-Z0-9]{4,}",
    "Meta Pixel": r"connect\.facebook\.net|fbq\(",
    "Google Fonts": r"fonts\.googleapis\.com|fonts\.gstatic\.com",
    "YouTube embarqué": r"youtube\.com/embed|youtube-nocookie\.com",
    "Google Maps": r"maps\.googleapis\.com|google\.com/maps/embed",
    "reCAPTCHA": r"recaptcha",
    "Hotjar / Clarity": r"hotjar|clarity\.ms",
    "LinkedIn Insight": r"snap\.licdn\.com",
    "TikTok Pixel": r"analytics\.tiktok\.com",
}


def normalize(url):
    url = url.strip()
    if not url or url.startswith("#"):
        return None
    if not url.startswith("http"):
        url = "https://" + url
    return url


def fetch(url):
    try:
        r = requests.get(url, headers={"User-Agent": UA, "Accept-Language": "fr-FR,fr;q=0.9"},
                         timeout=TIMEOUT, allow_redirects=True)
        return r, None
    except requests.exceptions.SSLError:
        try:
            r = requests.get(url.replace("https://", "http://"), headers={"User-Agent": UA},
                             timeout=TIMEOUT, allow_redirects=True)
            return r, "ssl"
        except Exception as e:  # noqa: BLE001
            return None, f"erreur: {e.__class__.__name__}"
    except Exception as e:  # noqa: BLE001
        return None, f"erreur: {e.__class__.__name__}"


def find_links(soup, base):
    found = {}
    for a in soup.find_all("a", href=True):
        text = f"{a.get_text(' ', strip=True)} {a['href']}"
        for key, pat in LEGAL_PATTERNS.items():
            if key not in found and pat.search(text):
                found[key] = urljoin(base, a["href"])
    return found


def check_contact_form(soup):
    forms = soup.find_all("form")
    has_form = False
    has_consent = False
    for f in forms:
        inputs = f.find_all(["input", "textarea"])
        types = {i.get("type", "text") for i in inputs}
        names = " ".join((i.get("name") or "") + " " + (i.get("id") or "") for i in inputs).lower()
        if "email" in types or "email" in names or f.find("textarea"):
            if "search" in names or "recherche" in names or "newsletter" in names:
                continue
            has_form = True
            ftxt = f.get_text(" ", strip=True).lower()
            if "checkbox" in types and re.search(r"accepte|consens|confidentialit|donn[ée]es", ftxt):
                has_consent = True
    return has_form, has_consent


def audit(url):
    res = {"url": url, "statut": "", "https": "", "mentions_legales": "", "politique_confidentialite": "",
           "politique_cookies": "", "cgv": "", "cmp": "", "traceurs": "", "formulaire_contact": "",
           "consentement_formulaire": "", "score": "", "accroche": ""}
    r, err = fetch(url)
    if r is None:
        res["statut"] = err
        res["accroche"] = "Site injoignable : vérifier l'adresse avant de prospecter."
        return res
    res["statut"] = str(r.status_code)
    final = r.url
    res["https"] = "oui" if final.startswith("https://") and err != "ssl" else "NON"
    html = r.text or ""
    soup = BeautifulSoup(html, "html.parser")
    links = find_links(soup, final)
    res["mentions_legales"] = "oui" if "mentions" in links else "NON"
    res["politique_confidentialite"] = "oui" if "confidentialite" in links else "NON"
    res["politique_cookies"] = "oui" if "cookies" in links else "non"
    res["cgv"] = "oui" if "cgv" in links else "non"

    low = html.lower()
    cmps = [name for name, pat in CMP_SIGNATURES.items() if re.search(pat, low)]
    res["cmp"] = ", ".join(cmps) if cmps else "aucune détectée"
    trackers = [name for name, pat in TRACKER_SIGNATURES.items() if re.search(pat, html)]
    res["traceurs"] = ", ".join(trackers) if trackers else "aucun détecté"
    has_form, has_consent = check_contact_form(soup)
    res["formulaire_contact"] = "oui" if has_form else "non"
    res["consentement_formulaire"] = ("oui" if has_consent else "NON") if has_form else "-"

    # Score sur 10 : chaque manque visible retire des points.
    score = 10
    issues = []
    if res["https"] == "NON":
        score -= 2
        issues.append("le site n'est pas en HTTPS")
    if res["mentions_legales"] == "NON":
        score -= 2
        issues.append("aucune page de mentions légales (obligation LCEN, amende jusqu'à 75 000 €)")
    if res["politique_confidentialite"] == "NON":
        score -= 2
        issues.append("aucune politique de confidentialité (article 13 RGPD)")
    needs_consent = [t for t in trackers if t in ("Google Analytics", "Google Tag Manager", "Meta Pixel",
                                                   "YouTube embarqué", "Hotjar / Clarity", "LinkedIn Insight",
                                                   "TikTok Pixel")]
    if needs_consent and not cmps:
        score -= 3
        issues.append("des traceurs se chargent sans bannière de consentement (" + ", ".join(needs_consent)
                      + ") : c'est le motif n°1 des sanctions CNIL en procédure simplifiée")
    elif needs_consent and cmps:
        issues.append("bannière présente : vérifier que le bouton Refuser est aussi visible qu'Accepter")
    if "Google Fonts" in trackers:
        score -= 0.5
        issues.append("Google Fonts chargé depuis les serveurs Google (adresse IP transmise aux États-Unis)")
    if has_form and not has_consent:
        score -= 1
        issues.append("formulaire de contact sans mention d'information ni case de consentement")
    if "reCAPTCHA" in trackers and not cmps:
        score -= 0.5
        issues.append("reCAPTCHA sans consentement préalable")
    res["score"] = f"{max(score, 0):g}/10"

    if issues:
        res["accroche"] = ("En regardant votre site, j'ai noté que " + " ; ".join(issues[:3]) +
                           ". Ce sont des points simples à corriger, je peux vous envoyer le détail.")
    else:
        res["accroche"] = ("Votre site est propre en apparence. Reste la partie invisible : registre des "
                           "traitements, contrats sous-traitants, durées de conservation. C'est ce que "
                           "demandent vos clients donneurs d'ordre et la CNIL en cas de contrôle.")
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("liste", help="fichier texte, un site par ligne")
    ap.add_argument("-o", "--out", default="resultats.csv")
    ap.add_argument("--pause", type=float, default=1.0, help="pause entre deux sites (secondes)")
    args = ap.parse_args()
    with open(args.liste, encoding="utf-8") as f:
        urls = [u for u in (normalize(line) for line in f) if u]
    rows = []
    for i, u in enumerate(urls, 1):
        print(f"[{i}/{len(urls)}] {u}", file=sys.stderr)
        rows.append(audit(u))
        time.sleep(args.pause)
    with open(args.out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()) if rows else ["url"])
        w.writeheader()
        w.writerows(rows)
    rows.sort(key=lambda r: float(r["score"].split("/")[0]) if r["score"] else 99)
    print(f"\n{len(rows)} sites audités -> {args.out}\n")
    for r in rows:
        print(f"{r['score']:>6}  {r['url']}\n        {r['accroche'][:160]}")


if __name__ == "__main__":
    main()
