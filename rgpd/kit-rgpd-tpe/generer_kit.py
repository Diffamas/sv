#!/usr/bin/env python3
"""Génère le Kit RGPD TPE (8 documents) dans le dossier courant."""
from docx import Document
from docx.shared import Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

INK = RGBColor(0x15, 0x23, 0x3B)
RED = RGBColor(0xB8, 0x23, 0x2F)
DATE = "13 octobre 2026"


def doc_base(title, subtitle):
    d = Document()
    for s in d.sections:
        s.left_margin = s.right_margin = Cm(2.2)
        s.top_margin = s.bottom_margin = Cm(2)
    st = d.styles["Normal"]
    st.font.name = "Calibri"
    st.font.size = Pt(11)
    p = d.add_paragraph()
    r = p.add_run("KIT RGPD TPE")
    r.font.size = Pt(9); r.font.bold = True; r.font.color.rgb = RED
    h = d.add_paragraph()
    r = h.add_run(title); r.font.size = Pt(22); r.font.bold = True; r.font.color.rgb = INK
    s = d.add_paragraph()
    r = s.add_run(subtitle); r.font.size = Pt(11); r.italic = True
    d.add_paragraph(f"Modèle version 1.0, {DATE}. Les champs entre [crochets] sont à remplacer. "
                    "Supprimez cette ligne avant publication.").runs[0].font.size = Pt(9)
    return d


def H(d, text, lvl=1):
    p = d.add_paragraph()
    r = p.add_run(text)
    r.font.bold = True
    r.font.size = Pt(14 if lvl == 1 else 12)
    r.font.color.rgb = INK
    p.paragraph_format.space_before = Pt(12)
    return p


def P(d, text):
    return d.add_paragraph(text)


def UL(d, items):
    for i in items:
        d.add_paragraph(i, style="List Bullet")


def table(d, header, rows):
    t = d.add_table(rows=1, cols=len(header))
    t.style = "Light Grid Accent 1"
    for i, h in enumerate(header):
        c = t.rows[0].cells[i]; c.text = h
        c.paragraphs[0].runs[0].font.bold = True
    for row in rows:
        cells = t.add_row().cells
        for i, v in enumerate(row):
            cells[i].text = v
    d.add_paragraph()


# ---------------------------------------------------------------- 00 Guide
d = doc_base("Guide d'utilisation du kit", "Par où commencer, dans quel ordre, et ce que la CNIL demande en premier.")
H(d, "Ce que contient le kit")
table(d, ["Fichier", "Usage", "Obligatoire ?"], [
    ["01-Registre-des-traitements.xlsx", "Inventaire de vos traitements, sous-traitants, durées, incidents, demandes", "Oui (art. 30 RGPD)"],
    ["02-Politique-de-confidentialite.docx", "Information des clients, prospects, visiteurs du site", "Oui (art. 13)"],
    ["03-Politique-cookies.docx", "Information et consentement sur les traceurs du site", "Oui si traceurs non essentiels"],
    ["04-Mentions-legales.docx", "Identification de l'éditeur du site", "Oui (loi LCEN)"],
    ["05-Procedure-violation-de-donnees.docx", "Quoi faire en cas de fuite, perte, piratage", "Oui (art. 33 et 34)"],
    ["06-Clause-RGPD-sous-traitant.docx", "Clause à faire signer à vos prestataires qui touchent des données", "Oui (art. 28)"],
    ["07-Checklist-conformite-TPE.docx", "Auto-évaluation en 30 questions", "Conseillé"],
])
H(d, "Dans quel ordre")
UL(d, [
    "Jour 1 : remplissez l'onglet Registre du fichier Excel. Listez chaque activité qui utilise des données de personnes : clients, salariés, candidats, visiteurs du site, caméras. La plupart des TPE ont 5 à 10 traitements.",
    "Jour 1 : remplissez l'onglet Sous-traitants. Hébergeur, logiciel de facturation, expert-comptable, agence web, messagerie, solution de paie. Vérifiez que chacun a une clause RGPD (souvent déjà dans ses CGV) ; sinon envoyez le document 06.",
    "Jour 2 : adaptez les documents 02, 03 et 04 et publiez-les sur votre site, dans le pied de page.",
    "Jour 2 : réglez votre bannière cookies : bouton Refuser aussi visible qu'Accepter, aucun traceur chargé avant le clic. Si vous n'avez que des statistiques exemptées (Matomo configuré selon la CNIL) ou aucun traceur, pas de bannière nécessaire.",
    "Jour 3 : lisez et signez la procédure 05, affichez-la à l'endroit où l'équipe la trouvera. Notez le contact de votre prestataire informatique dedans.",
    "Jour 3 : passez la checklist 07. Ce qui reste en rouge devient votre plan d'action.",
    "Chaque année : relisez le registre, mettez les dates à jour. En cas de contrôle, c'est ce qui prouve une démarche.",
])
H(d, "Les 5 erreurs qui coûtent le plus cher aux petites entreprises")
UL(d, [
    "Google Analytics, pixel Meta ou vidéo YouTube chargés avant tout consentement : motif principal des sanctions simplifiées de la CNIL en 2025 et 2026.",
    "Caméras sans affichage, ou qui filment les postes de travail en continu, ou images gardées plus de 30 jours.",
    "Ne pas répondre dans le mois à une personne qui demande l'accès ou la suppression de ses données.",
    "Aucun registre : c'est le premier document demandé lors d'un contrôle.",
    "Envoyer des emails commerciaux à des particuliers sans consentement préalable.",
])
H(d, "Durées de conservation de référence (recommandations CNIL)")
table(d, ["Données", "Durée"], [
    ["Clients : factures et pièces comptables", "10 ans"],
    ["Clients : coordonnées et échanges commerciaux", "3 ans après la fin de la relation"],
    ["Prospects", "3 ans après le dernier contact"],
    ["Candidats non retenus", "2 ans après le dernier contact"],
    ["Dossier salarié", "Durée du contrat + 5 ans"],
    ["Bulletins de paie", "5 ans (doubles employeur)"],
    ["Vidéosurveillance", "30 jours maximum"],
    ["Journaux de connexion", "6 mois à 1 an"],
    ["Badges et accès", "3 mois (sauf obligation particulière)"],
])
d.save("00-Guide-d-utilisation.docx")

# ---------------------------------------------------------------- 01 Registre xlsx
wb = Workbook()
hdr_fill = PatternFill("solid", fgColor="15233B")
hdr_font = Font(bold=True, color="FFFFFF")
thin = Side(style="thin", color="C9CED6")
border = Border(left=thin, right=thin, top=thin, bottom=thin)


def sheet(ws, header, rows, widths=None):
    ws.append(header)
    for c in ws[1]:
        c.fill = hdr_fill; c.font = hdr_font; c.alignment = Alignment(wrap_text=True, vertical="center")
    for r in rows:
        ws.append(r)
    for row in ws.iter_rows(min_row=1, max_row=ws.max_row, max_col=len(header)):
        for c in row:
            c.border = border
            c.alignment = Alignment(wrap_text=True, vertical="top")
    for i, w in enumerate(widths or [22] * len(header), 1):
        ws.column_dimensions[get_column_letter(i)].width = w
    ws.freeze_panes = "A2"


ws = wb.active; ws.title = "Lisez-moi"
ws["A1"] = "Registre des activités de traitement (article 30 RGPD)"; ws["A1"].font = Font(bold=True, size=14)
for i, t in enumerate([
    "Responsable du traitement : [Raison sociale], [adresse], SIRET [numéro]. Représentant : [prénom nom, fonction].",
    "Référent RGPD / contact : [prénom nom, email]. Un DPO n'est obligatoire que pour les organismes publics ou le suivi régulier à grande échelle.",
    "Date de création : [date]. Dernière mise à jour : [date]. Version : 1.0.",
    "Les lignes pré-remplies de l'onglet Registre décrivent une TPE type : gardez celles qui vous concernent, supprimez les autres, ajoutez les vôtres.",
    "Onglets : Registre, Sous-traitants, Durées de conservation, Mesures de sécurité, Demandes de droits, Incidents.",
    "Ce registre est tenu à disposition de la CNIL sur demande. Il n'a pas à être publié.",
], start=3):
    ws[f"A{i}"] = t
ws.column_dimensions["A"].width = 120

ws = wb.create_sheet("Registre")
cols = ["Réf.", "Nom du traitement", "Finalité principale", "Sous-finalités", "Base légale", "Personnes concernées",
        "Catégories de données", "Données sensibles ?", "Destinataires internes", "Sous-traitants / destinataires externes",
        "Durée de conservation", "Transfert hors UE", "Mesures de sécurité", "Outil / logiciel", "Date création", "Dernière MàJ"]
rows = [
    ["CLI-001", "Gestion des clients, devis et facturation", "Exécution des contrats et obligations comptables", "Devis, commandes, livraison, facturation, SAV", "Exécution du contrat ; obligation légale (comptabilité)", "Clients professionnels et particuliers", "Identité, coordonnées, adresse, historique de commandes, données de facturation", "Non", "Gérant, administratif", "[Logiciel de facturation], expert-comptable, banque", "Factures 10 ans ; coordonnées 3 ans après fin de relation", "Non", "Mots de passe individuels, sauvegarde, accès limité", "[logiciel]", "[date]", "[date]"],
    ["PRO-001", "Prospection commerciale", "Développement commercial", "Envoi d'offres, relances, newsletter", "Intérêt légitime (B2B) ; consentement (B2C)", "Prospects", "Identité, email, téléphone, société, fonction", "Non", "Gérant, commercial", "[Outil emailing], [CRM]", "3 ans après le dernier contact", "[Oui si outil américain : clauses contractuelles types]", "Désinscription dans chaque email, accès limité", "[outil]", "[date]", "[date]"],
    ["RH-001", "Gestion du personnel et de la paie", "Administration RH et obligations sociales", "Contrats, paie, absences, formation, médecine du travail", "Exécution du contrat de travail ; obligation légale", "Salariés, stagiaires, intérimaires", "État civil, NIR, RIB, situation familiale, arrêts de travail", "Oui (NIR, santé)", "Gérant, RH", "Expert-comptable / prestataire paie, mutuelle, organismes sociaux", "Dossier : contrat + 5 ans ; paie 5 ans", "Non", "Dossiers verrouillés, accès RH uniquement", "[logiciel paie]", "[date]", "[date]"],
    ["REC-001", "Recrutement", "Sélection des candidats", "Réception et tri des candidatures, entretiens", "Mesures précontractuelles ; intérêt légitime", "Candidats", "CV, lettre, diplômes, échanges", "Non", "Gérant, RH", "[Site d'emploi]", "2 ans après le dernier contact (candidats non retenus)", "Non", "Suppression à échéance, accès limité", "Email", "[date]", "[date]"],
    ["WEB-001", "Site internet et formulaire de contact", "Réponse aux demandes, sécurité du site", "Formulaire, statistiques, journaux techniques", "Consentement (cookies) ; intérêt légitime (sécurité)", "Visiteurs du site", "Nom, email, message, adresse IP, cookies", "Non", "Gérant", "[Hébergeur], [agence web], [outil statistiques]", "Messages 1 an ; journaux 1 an ; cookies 13 mois max", "[Selon l'outil de statistiques]", "HTTPS, bannière de consentement, mises à jour", "[CMS]", "[date]", "[date]"],
    ["FOU-001", "Gestion des fournisseurs", "Achats et règlement des fournisseurs", "Commandes, factures, paiements", "Exécution du contrat ; obligation légale", "Contacts chez les fournisseurs", "Identité, coordonnées professionnelles, RIB", "Non", "Gérant, administratif", "Expert-comptable, banque", "10 ans (pièces comptables)", "Non", "Accès limité, sauvegarde", "[logiciel]", "[date]", "[date]"],
    ["SEC-001", "Vidéosurveillance des locaux", "Sécurité des biens et des personnes", "Prévention des vols et intrusions", "Intérêt légitime", "Salariés, clients, visiteurs", "Images", "Non", "Gérant", "[Installateur / télésurveillance]", "30 jours maximum", "Non", "Affichage à l'entrée, accès aux images limité et journalisé, pas de caméra sur les postes de travail ni les zones de pause", "[Enregistreur]", "[date]", "[date]"],
    ["COM-001", "Comptabilité", "Tenue des comptes et obligations fiscales", "Écritures, déclarations", "Obligation légale", "Clients, fournisseurs, salariés", "Données de facturation et de paie", "Non", "Gérant", "Expert-comptable", "10 ans", "Non", "Accès limité, sauvegarde", "[logiciel]", "[date]", "[date]"],
]
sheet(ws, cols, rows, [9, 28, 28, 28, 26, 22, 34, 12, 20, 30, 28, 18, 34, 16, 12, 12])

ws = wb.create_sheet("Sous-traitants")
sheet(ws, ["Réf.", "Prestataire", "Service", "Données confiées", "Localisation des données", "Transfert hors UE", "Clause RGPD (art. 28)", "Statut", "Dernière vérification"], [
    ["ST-01", "[Hébergeur du site, ex. OVH, o2switch]", "Hébergement du site", "Journaux, formulaires", "France / UE", "Non", "Incluse dans les CGV (vérifier)", "Actif", "[date]"],
    ["ST-02", "[Messagerie, ex. Google Workspace, Microsoft 365]", "Emails professionnels", "Emails, contacts, pièces jointes", "UE / États-Unis", "Possible : clauses contractuelles types + Data Privacy Framework", "DPA en ligne de l'éditeur", "Actif", "[date]"],
    ["ST-03", "[Expert-comptable]", "Comptabilité, paie", "Factures, données salariés", "France", "Non", "Lettre de mission : vérifier la clause", "Actif", "[date]"],
    ["ST-04", "[Logiciel de facturation / caisse]", "Facturation", "Clients, factures", "[pays]", "[oui/non]", "CGV / DPA", "Actif", "[date]"],
    ["ST-05", "[Agence web / webmaster]", "Maintenance du site", "Accès au site et aux formulaires", "France", "Non", "À faire signer (document 06)", "À vérifier", "[date]"],
    ["ST-06", "[Télésurveillance / installateur caméras]", "Vidéosurveillance", "Images", "France", "Non", "À faire signer (document 06)", "À vérifier", "[date]"],
], [8, 34, 22, 28, 20, 28, 30, 12, 16])

ws = wb.create_sheet("Durées de conservation")
sheet(ws, ["Traitement", "Données", "Durée", "Justification", "Sort à l'échéance"], [
    ["Clients", "Factures, pièces comptables", "10 ans", "Code de commerce L123-22", "Archivage puis destruction"],
    ["Clients", "Coordonnées, échanges", "3 ans après la fin de la relation", "Recommandation CNIL", "Suppression"],
    ["Prospects", "Coordonnées", "3 ans après le dernier contact", "Recommandation CNIL", "Suppression"],
    ["Recrutement", "Candidatures non retenues", "2 ans après le dernier contact", "Recommandation CNIL", "Suppression"],
    ["RH", "Dossier salarié", "Durée du contrat + 5 ans", "Prescription", "Archivage puis destruction"],
    ["RH", "Bulletins de paie", "5 ans", "Code du travail L3243-4", "Archivage"],
    ["Site web", "Journaux de connexion", "1 an", "LCEN, décret 2021", "Suppression automatique"],
    ["Site web", "Cookies", "13 mois maximum ; consentement renouvelé", "Lignes directrices CNIL", "Expiration"],
    ["Sécurité", "Vidéosurveillance", "30 jours maximum", "Recommandation CNIL", "Écrasement automatique"],
], [18, 30, 30, 30, 26])

ws = wb.create_sheet("Mesures de sécurité")
sheet(ws, ["Domaine", "Mesure", "En place ?", "Commentaire"], [
    ["Accès", "Un identifiant et un mot de passe par personne, jamais partagés", "[oui/non]", ""],
    ["Accès", "Mots de passe de 12 caractères minimum ou gestionnaire de mots de passe", "[oui/non]", ""],
    ["Accès", "Double authentification sur la messagerie et la banque", "[oui/non]", ""],
    ["Accès", "Retrait des accès le jour du départ d'un salarié ou prestataire", "[oui/non]", ""],
    ["Postes", "Antivirus actif et mises à jour automatiques", "[oui/non]", ""],
    ["Postes", "Verrouillage automatique des sessions", "[oui/non]", ""],
    ["Sauvegardes", "Sauvegarde automatique, au moins une copie hors site, test de restauration annuel", "[oui/non]", ""],
    ["Site web", "HTTPS, CMS et extensions à jour", "[oui/non]", ""],
    ["Papier", "Dossiers RH et clients dans un meuble fermé", "[oui/non]", ""],
    ["Organisation", "Charte informatique signée par les salariés", "[oui/non]", ""],
    ["Organisation", "Procédure de violation de données connue de l'équipe", "[oui/non]", ""],
], [16, 70, 12, 30])

ws = wb.create_sheet("Demandes de droits")
sheet(ws, ["Date de réception", "Demandeur", "Droit exercé (accès, rectification, effacement, opposition, portabilité)", "Canal", "Identité vérifiée ?", "Réponse envoyée le", "Délai (max 1 mois)", "Commentaire"], [
    ["[date]", "[nom]", "[droit]", "[email / courrier]", "[oui/non]", "[date]", "[jours]", ""],
], [16, 20, 40, 16, 14, 16, 14, 30])

ws = wb.create_sheet("Incidents")
sheet(ws, ["Date", "Incident", "Données concernées", "Personnes concernées (nombre)", "Gravité", "Actions réalisées", "Notification CNIL (72 h) ?", "Information des personnes ?", "Responsable", "Statut"], [
    ["[date]", "[ex. email envoyé au mauvais destinataire]", "[données]", "[nombre]", "[faible / moyenne / élevée]", "[actions]", "[oui/non + date]", "[oui/non + date]", "[nom]", "[ouvert / clos]"],
], [12, 34, 24, 16, 14, 34, 18, 18, 14, 12])
wb.save("01-Registre-des-traitements.xlsx")

# ---------------------------------------------------------------- 02 Politique de confidentialité
d = doc_base("Politique de confidentialité", "À publier sur le site, lien dans le pied de page. Adaptée à une TPE avec site vitrine, formulaire de contact et fichier clients.")
H(d, "1. Qui est responsable de vos données")
P(d, "[Raison sociale], [forme juridique], [adresse], SIRET [numéro], représentée par [prénom nom]. Contact pour toute question sur vos données : [email].")
H(d, "2. Quelles données nous collectons, pourquoi, et sur quelle base")
table(d, ["Situation", "Données", "Pourquoi", "Base légale", "Durée"], [
    ["Vous nous contactez (formulaire, email, téléphone)", "Nom, email, téléphone, contenu du message", "Vous répondre", "Intérêt légitime, mesures précontractuelles", "1 an après le dernier échange"],
    ["Vous devenez client", "Identité, adresse, données de facturation, historique", "Exécuter le contrat, facturer, assurer le suivi", "Contrat, obligation légale", "Factures 10 ans ; coordonnées 3 ans après la fin de la relation"],
    ["Vous recevez nos offres", "Email, nom", "Vous informer de nos services", "Consentement (particuliers) ; intérêt légitime (professionnels)", "3 ans après le dernier contact"],
    ["Vous visitez notre site", "Adresse IP, journaux techniques, cookies", "Sécurité, statistiques", "Intérêt légitime (sécurité) ; consentement (statistiques et traceurs tiers)", "Journaux 1 an ; cookies 13 mois max"],
    ["Vous entrez dans nos locaux", "Images de vidéosurveillance", "Sécurité des biens et des personnes", "Intérêt légitime", "30 jours"],
])
H(d, "3. Qui a accès à vos données")
P(d, "Les personnes de [raison sociale] qui en ont besoin pour leur travail, et nos prestataires qui agissent sur nos instructions : [hébergeur], [messagerie], [expert-comptable], [logiciel de facturation], [agence web]. Chacun est tenu par un contrat conforme à l'article 28 du RGPD. Nous ne vendons ni ne louons vos données.")
H(d, "4. Transferts hors de l'Union européenne")
P(d, "[Aucun transfert. / Certains prestataires, comme [outil], sont situés aux États-Unis : le transfert est encadré par les clauses contractuelles types de la Commission européenne et, le cas échéant, par leur certification au Data Privacy Framework.]")
H(d, "5. Vos droits")
P(d, "Vous pouvez demander l'accès à vos données, leur rectification, leur effacement, la limitation de leur traitement, vous opposer à leur utilisation, demander leur portabilité, retirer votre consentement à tout moment, et définir des directives sur leur sort après votre décès. Écrivez à [email] ou à [adresse postale]. Nous répondons sous un mois. Une pièce d'identité peut vous être demandée en cas de doute raisonnable sur votre identité.")
P(d, "Si vous estimez que vos droits ne sont pas respectés, vous pouvez saisir la CNIL : www.cnil.fr/fr/plaintes, 3 place de Fontenoy, TSA 80715, 75334 Paris Cedex 07.")
H(d, "6. Sécurité")
P(d, "Accès par identifiants individuels, sauvegardes régulières, site en HTTPS, locaux fermés, prestataires sélectionnés pour leurs garanties de sécurité.")
H(d, "7. Cookies")
P(d, "Voir notre politique cookies : [lien].")
H(d, "8. Mise à jour")
P(d, "Version du [date]. Nous la modifierons si nos pratiques changent ; la version en ligne fait foi.")
d.save("02-Politique-de-confidentialite.docx")

# ---------------------------------------------------------------- 03 Cookies
d = doc_base("Politique cookies", "À publier avec un lien depuis la bannière et le pied de page.")
H(d, "Ce qu'est un cookie")
P(d, "Un cookie est un petit fichier déposé sur votre appareil lorsque vous consultez un site. Certains sont indispensables au fonctionnement du site ; d'autres servent à mesurer l'audience ou à afficher des contenus de services tiers. La loi impose votre accord préalable pour ces derniers.")
H(d, "Les cookies utilisés sur ce site")
table(d, ["Nom / service", "Finalité", "Consentement requis", "Durée"], [
    ["Cookies de session, choix de consentement", "Fonctionnement du site, mémoriser votre choix", "Non (nécessaires)", "Session / 6 mois"],
    ["[Google Analytics / Matomo]", "Mesure d'audience", "[Oui / Non si Matomo configuré en exemption CNIL]", "13 mois max"],
    ["[YouTube, Google Maps]", "Affichage de vidéos ou de cartes", "Oui", "Selon le tiers"],
    ["[Pixel Meta, LinkedIn]", "Mesure de nos campagnes publicitaires", "Oui", "Selon le tiers"],
])
H(d, "Votre choix")
P(d, "À votre première visite, une bannière vous propose d'accepter ou de refuser, avec la même facilité. Rien n'est déposé avant votre choix, hormis les cookies nécessaires. Vous pouvez changer d'avis à tout moment via le lien « Gérer mes cookies » en pied de page. Votre choix est conservé 6 mois.")
H(d, "Réglages du navigateur")
P(d, "Vous pouvez aussi configurer votre navigateur pour refuser les cookies. Certaines fonctions du site peuvent alors ne plus fonctionner.")
P(d, f"Version du [date].")
d.save("03-Politique-cookies.docx")

# ---------------------------------------------------------------- 04 Mentions légales
d = doc_base("Mentions légales", "Obligatoires pour tout site (loi pour la confiance dans l'économie numérique). Amende jusqu'à 75 000 € pour une personne physique.")
H(d, "Éditeur du site")
UL(d, [
    "Dénomination : [raison sociale ou nom et prénom pour une entreprise individuelle]",
    "Forme juridique et capital : [SARL au capital de X € / entreprise individuelle]",
    "Siège : [adresse complète]",
    "Immatriculation : [RCS ville + numéro, ou SIREN pour les entreprises individuelles ; numéro au répertoire des métiers pour les artisans]",
    "TVA intracommunautaire : [numéro] ou « TVA non applicable, article 293 B du CGI »",
    "Contact : [email], [téléphone]",
    "Directeur de la publication : [prénom nom]",
    "Activité réglementée : [autorité, titre professionnel, règles applicables, le cas échéant]",
])
H(d, "Hébergeur")
P(d, "[Nom de l'hébergeur], [adresse], [téléphone].")
H(d, "Propriété intellectuelle")
P(d, "L'ensemble du site (textes, images, logo, structure) est protégé par le droit d'auteur. Toute reproduction sans autorisation écrite est interdite.")
H(d, "Données personnelles et cookies")
P(d, "Voir la politique de confidentialité et la politique cookies : [liens].")
H(d, "Médiation de la consommation (si vous vendez à des particuliers)")
P(d, "En cas de litige, le consommateur peut recourir gratuitement au médiateur [nom du médiateur], [site], ou à la plateforme européenne de règlement en ligne des litiges : ec.europa.eu/consumers/odr.")
d.save("04-Mentions-legales.docx")

# ---------------------------------------------------------------- 05 Procédure violation
d = doc_base("Procédure de gestion des violations de données", "Articles 33 et 34 du RGPD. À signer par le gérant et à garder accessible à toute l'équipe.")
table(d, ["Élément", "Information"], [
    ["Référence", "PROC-INC-01"], ["Version", "1.0"], ["Date", "[date]"],
    ["Responsable", "[gérant]"], ["Prestataire informatique", "[nom, téléphone, email]"], ["Référent RGPD", "[nom, email]"],
])
H(d, "1. Ce qu'est une violation de données")
P(d, "Tout événement qui entraîne la destruction, la perte, l'altération, la divulgation ou l'accès non autorisé à des données personnelles. Exemples : rançongiciel, email envoyé au mauvais destinataire, ordinateur ou téléphone perdu, mot de passe partagé utilisé par un ancien salarié, dossiers papier jetés sans destruction, site piraté.")
H(d, "2. Les quatre étapes")
table(d, ["Étape", "Qui", "Quand", "Quoi"], [
    ["Signaler", "Toute personne qui constate", "Immédiatement", "Prévenir le gérant et le prestataire informatique. Ne rien effacer. Noter l'heure, ce qui a été vu."],
    ["Contenir", "Gérant + informatique", "Dans l'heure", "Couper les accès concernés, isoler le poste, changer les mots de passe, restaurer depuis une sauvegarde saine."],
    ["Évaluer", "Gérant", "Dans les 24 h", "Quelles données, combien de personnes, quel risque pour elles (usurpation, fraude, atteinte à la vie privée). Remplir l'onglet Incidents du registre."],
    ["Notifier", "Gérant", "Sous 72 h", "Si risque pour les personnes : notification à la CNIL sur notifications.cnil.fr. Si risque élevé : informer aussi les personnes concernées en termes clairs. Si aucun risque : documenter la décision dans le registre."],
])
H(d, "3. Contenu de la notification CNIL")
UL(d, ["Nature de la violation, catégories et nombre approximatif de personnes et d'enregistrements concernés",
       "Conséquences probables", "Mesures prises ou envisagées", "Coordonnées du contact"])
H(d, "4. Après l'incident")
UL(d, ["Réunion de retour d'expérience sous 15 jours", "Mise à jour des mesures de sécurité dans le registre", "Dépôt de plainte en cas d'acte malveillant"])
P(d, "Signature du gérant : ____________________   Date : __________")
d.save("05-Procedure-violation-de-donnees.docx")

# ---------------------------------------------------------------- 06 Clause sous-traitant
d = doc_base("Clause de protection des données à insérer dans les contrats avec vos prestataires", "Article 28 du RGPD. À annexer au devis ou au contrat de tout prestataire qui accède à des données personnelles pour votre compte.")
P(d, "Entre [raison sociale], responsable du traitement, et [prestataire], sous-traitant, au titre de [prestation].")
H(d, "Article 1. Objet")
P(d, "Le sous-traitant traite, pour le compte du responsable du traitement, les données suivantes : [catégories de données], concernant [catégories de personnes], pour la finalité suivante : [finalité], pendant la durée du contrat.")
H(d, "Article 2. Obligations du sous-traitant")
UL(d, [
    "Ne traiter les données que sur instruction documentée du responsable du traitement.",
    "Garantir la confidentialité des personnes autorisées à traiter les données.",
    "Mettre en œuvre les mesures de sécurité appropriées (article 32) : [chiffrement, contrôle d'accès, sauvegardes, journalisation].",
    "Ne recruter aucun autre sous-traitant sans autorisation écrite préalable, et lui imposer les mêmes obligations.",
    "Aider le responsable du traitement à répondre aux demandes d'exercice de droits et à respecter ses obligations (sécurité, notification des violations, analyse d'impact).",
    "Notifier toute violation de données au responsable du traitement dans les 48 heures suivant sa découverte, avec les informations nécessaires à la notification CNIL.",
    "Ne transférer aucune donnée hors de l'Union européenne sans encadrement conforme au chapitre V du RGPD.",
    "À la fin du contrat, au choix du responsable du traitement, supprimer ou restituer toutes les données, et détruire les copies existantes, sous 30 jours, avec attestation.",
    "Mettre à disposition toute information nécessaire pour démontrer le respect de ces obligations et permettre des audits.",
])
H(d, "Article 3. Registre et contact")
P(d, "Le sous-traitant tient le registre des catégories d'activités de traitement effectuées pour le compte du responsable. Contact du sous-traitant pour la protection des données : [nom, email].")
P(d, "Fait à [ville], le [date], en deux exemplaires.\n\nPour le responsable du traitement : ____________________\n\nPour le sous-traitant : ____________________")
d.save("06-Clause-RGPD-sous-traitant.docx")

# ---------------------------------------------------------------- 07 Checklist
d = doc_base("Checklist conformité TPE", "30 questions. Trois réponses « non » dans une même section = priorité.")
sections = {
    "Documentation": [
        "Nous avons un registre des traitements à jour (moins d'un an).",
        "Chaque traitement a une finalité, une base légale et une durée de conservation écrites.",
        "Nous savons qui est le référent RGPD dans l'entreprise.",
        "Nos sous-traitants sont listés, avec une clause RGPD pour chacun.",
        "Nous savons si des données partent hors de l'Union européenne et comment c'est encadré.",
    ],
    "Information des personnes": [
        "Le site a des mentions légales complètes.",
        "Le site a une politique de confidentialité accessible depuis chaque page.",
        "Chaque formulaire indique pourquoi les données sont collectées et renvoie vers la politique.",
        "Les salariés ont reçu une information sur l'utilisation de leurs données (note ou charte).",
        "La vidéosurveillance est signalée par un panneau avec finalité, durée, contact.",
    ],
    "Cookies et site web": [
        "Une bannière propose Accepter et Refuser avec la même visibilité.",
        "Aucun traceur non essentiel n'est chargé avant le consentement.",
        "Le choix est modifiable à tout moment via un lien en pied de page.",
        "Le site est en HTTPS et son CMS est à jour.",
        "Les polices, cartes et vidéos tierces sont chargées avec consentement ou hébergées localement.",
    ],
    "Droits des personnes": [
        "Une adresse email est dédiée aux demandes et consultée chaque semaine.",
        "Nous savons répondre à une demande d'accès ou d'effacement en moins d'un mois.",
        "Chaque demande est notée dans le registre des demandes.",
        "Chaque email commercial contient un lien de désinscription qui fonctionne.",
        "Nous ne prospectons pas de particuliers sans leur consentement.",
    ],
    "Sécurité": [
        "Un identifiant par personne, aucun mot de passe partagé.",
        "Double authentification sur la messagerie et les outils critiques.",
        "Sauvegarde automatique testée dans l'année.",
        "Antivirus et mises à jour automatiques sur tous les postes.",
        "Les accès d'un salarié parti sont coupés le jour même.",
    ],
    "Incidents et conservation": [
        "La procédure de violation de données est écrite et connue de l'équipe.",
        "Nous savons notifier la CNIL sous 72 heures.",
        "Les données périmées sont supprimées au moins une fois par an.",
        "Les images de vidéosurveillance sont écrasées sous 30 jours.",
        "Les dossiers papier sensibles (RH, santé) sont sous clé.",
    ],
}
for sec, qs in sections.items():
    H(d, sec)
    table(d, ["Question", "Oui", "Non", "Action"], [[q, "☐", "☐", ""] for q in qs])
d.save("07-Checklist-conformite-TPE.docx")
print("kit généré")
