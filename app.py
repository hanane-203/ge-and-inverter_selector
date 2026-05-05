import streamlit as st
import pandas as pd
from fpdf import FPDF
import tempfile
import base64
import re
from datetime import datetime

# =========================================================
# CONFIG PAGE
# =========================================================
st.set_page_config(
    page_title="Plateforme intelligente de sélection GE & inverseur de source",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# SESSION STATE
# =========================================================
if "resultat_final" not in st.session_state:
    st.session_state.resultat_final = None
if "choix_confirme" not in st.session_state:
    st.session_state.choix_confirme = False
if "groupe_confirme" not in st.session_state:
    st.session_state.groupe_confirme = None
if "inverseur_confirme" not in st.session_state:
    st.session_state.inverseur_confirme = False
if "inverseur_final" not in st.session_state:
    st.session_state.inverseur_final = None
if "choix_inverseur_resultat" not in st.session_state:
    st.session_state.choix_inverseur_resultat = None

# =========================================================
# CSS (version complète)
# =========================================================
st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #f4f7fb 0%, #eaf1fb 100%); }
    .top-hero { background: linear-gradient(135deg, #ffffff 0%, #f7fbff 100%); border: 1px solid #dbe7f3; border-radius: 22px; padding: 26px 28px; margin-bottom: 22px; box-shadow: 0 6px 18px rgba(0,0,0,0.05); }
    .brand-wrap { display: flex; align-items: center; gap: 16px; margin-bottom: 12px; }
    .brand-logo { width: 68px; height: 68px; border-radius: 18px; background: linear-gradient(135deg, #123d6a 0%, #1f6fb2 100%); display: flex; align-items: center; justify-content: center; color: white; font-size: 30px; font-weight: 800; box-shadow: 0 8px 20px rgba(18,61,106,0.22); }
    .brand-name { font-size: 15px; font-weight: 800; color: #1a4f85; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 3px; }
    .main-title { font-size: 36px; font-weight: 900; color: #0f2747; margin-bottom: 0.4rem; line-height: 1.2; }
    .subtitle { font-size: 16px; color: #4b6280; margin-bottom: 0; line-height: 1.7; }
    .section-title { font-size: 28px; font-weight: 800; color: #10345c; margin-top: 10px; margin-bottom: 14px; }
    .info-box { background: linear-gradient(135deg, #eef4fb 0%, #f8fbff 100%); padding: 20px; border-radius: 16px; border: 1px solid #d4e1f2; margin-bottom: 20px; box-shadow: 0 4px 14px rgba(0,0,0,0.04); }
    .card { background: white; padding: 20px; border-radius: 16px; border: 1px solid #e4ebf5; box-shadow: 0 4px 14px rgba(0,0,0,0.06); margin-bottom: 18px; }
    .metric-card { background: white; border-radius: 16px; padding: 18px; text-align: center; border: 1px solid #e4ebf5; box-shadow: 0 4px 14px rgba(0,0,0,0.05); }
    .metric-label { font-size: 13px; color: #6b7b93; font-weight: 600; margin-bottom: 8px; text-transform: uppercase; }
    .metric-value { font-size: 26px; font-weight: 800; color: #0f2747; }
    .metric-sub { font-size: 13px; color: #70839c; margin-top: 4px; }
    .badge { display: inline-block; padding: 8px 14px; border-radius: 999px; font-weight: 700; font-size: 14px; margin-top: 6px; margin-bottom: 10px; }
    .badge-securite { background-color: #fff4db; color: #b26a00; border: 1px solid #f2cf75; }
    .badge-secours { background-color: #eaf4ff; color: #0d63b8; border: 1px solid #8ec2f5; }
    .badge-tempszero { background-color: #ffe9e9; color: #c62828; border: 1px solid #f2a4a4; }
    .badge-aucun { background-color: #f3f4f6; color: #4b5563; border: 1px solid #d1d5db; }
    .result-box-securite { background: linear-gradient(135deg, #fffaf0 0%, #fff4db 100%); border: 1px solid #f2cf75; border-left: 8px solid #e0a100; padding: 22px; border-radius: 18px; margin-top: 10px; }
    .result-box-secours { background: linear-gradient(135deg, #f4f9ff 0%, #eaf4ff 100%); border: 1px solid #8ec2f5; border-left: 8px solid #0d63b8; padding: 22px; border-radius: 18px; margin-top: 10px; }
    .result-box-tempszero { background: linear-gradient(135deg, #fff5f5 0%, #ffe9e9 100%); border: 1px solid #f2a4a4; border-left: 8px solid #d32f2f; padding: 22px; border-radius: 18px; margin-top: 10px; }
    .result-box-aucun { background: linear-gradient(135deg, #f9fafb 0%, #f3f4f6 100%); border: 1px solid #d1d5db; border-left: 8px solid #6b7280; padding: 22px; border-radius: 18px; margin-top: 10px; }
    .warning-box { background: #fff7e6; border: 1px solid #f4cf7a; border-left: 8px solid #d9a300; padding: 18px; border-radius: 16px; margin-top: 10px; margin-bottom: 16px; }
    .success-box { background: linear-gradient(135deg, #eef8f1 0%, #f8fffb 100%); border: 2px solid #78c69b; border-left: 10px solid #2e8b57; padding: 24px; border-radius: 18px; margin-top: 20px; margin-bottom: 20px; }
    .ups-box { background: linear-gradient(135deg, #eef6ff 0%, #f8fbff 100%); border: 2px solid #8ec2f5; border-left: 10px solid #0d63b8; padding: 24px; border-radius: 18px; margin-top: 20px; margin-bottom: 20px; }
    .confirm-box { background: linear-gradient(135deg, #eef8f1 0%, #f8fffb 100%); border: 2px solid #78c69b; border-left: 10px solid #2e8b57; padding: 24px; border-radius: 18px; margin-top: 20px; margin-bottom: 20px; }
    .lock-box { background: linear-gradient(135deg, #fff8e8 0%, #fffdf6 100%); border: 2px solid #f1d28b; border-left: 10px solid #d9a300; padding: 24px; border-radius: 18px; margin-top: 20px; margin-bottom: 20px; }
    .small-note { font-size: 13px; color: #6b7280; margin-top: 8px; }
    .tse-card { background: white; padding: 22px; border-radius: 18px; border: 1px solid #e4ebf5; box-shadow: 0 4px 14px rgba(0,0,0,0.06); margin-bottom: 18px; }
    .tse-title { font-size: 24px; font-weight: 800; color: #10345c; margin-bottom: 8px; }
    .tse-subtitle { color: #5f738c; font-size: 14px; margin-bottom: 14px; }
    .mini-badge { display: inline-block; padding: 6px 12px; border-radius: 999px; font-size: 12px; font-weight: 700; margin-right: 8px; margin-bottom: 8px; background: #eef4fb; color: #123d6a; border: 1px solid #cfe0f2; }
    .good-box { background: linear-gradient(135deg, #eef8f1 0%, #f8fffb 100%); border: 1px solid #9bd0b0; border-left: 8px solid #2e8b57; border-radius: 16px; padding: 18px; margin-top: 12px; margin-bottom: 12px; }
    .warn-box { background: #fff8e8; border: 1px solid #f1d28b; border-left: 8px solid #d9a300; border-radius: 16px; padding: 18px; margin-top: 12px; margin-bottom: 12px; }
    .danger-box { background: #fff2f2; border: 1px solid #efb1b1; border-left: 8px solid #cf2e2e; border-radius: 16px; padding: 18px; margin-top: 12px; margin-bottom: 12px; }
    .impossible-box { background: linear-gradient(135deg, #fff0f0 0%, #ffe5e5 100%); border: 2px solid #f5a0a0; border-left: 10px solid #c62828; padding: 24px; border-radius: 18px; margin-top: 10px; margin-bottom: 16px; }
    .seuil-info-box { background: linear-gradient(135deg, #f0f6ff 0%, #e8f2ff 100%); border: 1px solid #b0ccf0; border-left: 6px solid #1a6fc4; padding: 14px 18px; border-radius: 14px; margin-top: 8px; margin-bottom: 10px; font-size: 13px; color: #1a3a5c; }
    .schema-box { background: #1e2f3c; color: white; border-radius: 18px; padding: 18px; margin-top: 14px; }
    .schema-bar { display: flex; height: 34px; border-radius: 14px; overflow: hidden; margin: 10px 0; background: #dbe5ec; }
    .schema-src1 { background: #2a7f6e; text-align: center; line-height: 34px; font-weight: 700; }
    .schema-off { background: #e9a23b; text-align: center; line-height: 34px; font-weight: 700; }
    .schema-src2 { background: #2a7f6e; text-align: center; line-height: 34px; font-weight: 700; }
    .schema-sync { background: #2c6e9e; text-align: center; line-height: 34px; font-weight: 700; }
</style>
""", unsafe_allow_html=True)

# =========================================================
# EN-TETE
# =========================================================
st.markdown("""
<div class="top-hero">
    <div class="brand-wrap">
        <div class="brand-logo">⚡</div>
        <div>
            <div class="brand-name">PowerSwitch Decision</div>
            <div class="main-title">Plateforme intelligente de sélection du groupe électrogène et de l'inverseur de source</div>
        </div>
    </div>
    <div class="subtitle">
        Cette interface d'aide à la décision s'appuie sur une logique issue des normes techniques applicables
        et du règlement des ERP, afin d'orienter le choix du niveau de groupe électrogène ainsi que la configuration
        d'inversion de sources la plus cohérente avec les exigences de sécurité, de continuité de service,
        de criticité des charges et de tenue de l'installation.
    </div>
</div>
""", unsafe_allow_html=True)

# =========================================================
# BOUTON DE RÉINITIALISATION EN HAUT À DROITE
# =========================================================
col_reset1, col_reset2 = st.columns([6, 1])
with col_reset2:
    if st.button("🔄 Réinitialiser", use_container_width=True):
        st.session_state.resultat_final = None
        st.session_state.choix_confirme = False
        st.session_state.groupe_confirme = None
        st.session_state.inverseur_confirme = False
        st.session_state.inverseur_final = None
        st.session_state.choix_inverseur_resultat = None
        st.rerun()

# =========================================================
# FONCTION DE GÉNÉRATION PDF (CORRIGÉE)
# =========================================================
def generer_pdf(entrees, resultats_groupe, resultats_inverseur):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "PowerSwitch Decision - Rapport d'etude", ln=True, align="C")
    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, f"Date : {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True)
    pdf.ln(10)

    def clean_html(text):
        if not isinstance(text, str):
            return str(text)
        text = re.sub(r'<b>|</b>', '', text)
        text = re.sub(r'<br\s*/?>', ' ', text)
        text = re.sub(r'<[^>]+>', '', text)
        # Replace multiple spaces
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "1. Parametres d'entree", ln=True)
    pdf.set_font("Arial", "", 11)
    for k, v in entrees.items():
        pdf.cell(0, 8, f"{k} : {clean_html(v)}", ln=True)
    pdf.ln(5)

    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "2. Resultats - Groupe electrogene", ln=True)
    pdf.set_font("Arial", "", 11)
    for k, v in resultats_groupe.items():
        pdf.cell(0, 8, f"{k} : {clean_html(v)}", ln=True)
    pdf.ln(5)

    if resultats_inverseur:
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "3. Resultats - Inverseur de source", ln=True)
        pdf.set_font("Arial", "", 11)
        for k, v in resultats_inverseur.items():
            pdf.cell(0, 8, f"{k} : {clean_html(v)}", ln=True)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        pdf.output(tmp.name)
        tmp_path = tmp.name

    with open(tmp_path, "rb") as f:
        data = f.read()
    b64 = base64.b64encode(data).decode()
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="rapport_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf">📄 Télécharger le rapport PDF</a>'
    return href

# =========================================================
# DONNEES
# =========================================================
NIVEAU_SCORE = {"Aucun":0, "Secours":1, "Sécurité":2, "Temps Zéro":3}
SCORE_NIVEAU = {v:k for k,v in NIVEAU_SCORE.items()}

erp_types = {
    "U - Santé (Hôpitaux)": "U", "J - Structures pour personnes âgées / handicapées": "J",
    "O - Hôtels / Pensions": "O", "Rh - Internats": "Rh", "OA - Hôtels d'altitude": "OA",
    "L - Salles de spectacles / auditions / conférences": "L", "P - Salles de danse / jeux": "P",
    "Y - Musées": "Y", "X - Établissements sportifs": "X", "V - Lieux de culte": "V",
    "M - Magasins / centres commerciaux": "M", "N - Restaurants / Cafés": "N", "W - Bureaux / banques": "W",
    "S - Bibliothèques / archives": "S", "T - Salles d'exposition": "T", "GA - Gares": "GA",
    "PS - Parkings couverts": "PS", "EF - Établissements flottants": "EF", "SG - Structures gonflables": "SG",
    "BM - Bains maures": "BM", "IGH - Immeubles de grande hauteur": "IGH",
    "MIL - Défense / installations sensibles": "MIL", "AER - Aéroports": "AER",
}
TYPES_SPECIAUX = {"IGH", "MIL", "AER"}
TYPES_TEMPS_ZERO_GLOBAL = {"MIL", "AER"}

SEUILS = {
    "U":20, "J":25, "O":100, "Rh":100, "OA":20, "L":50, "P":120,
    "Y":200, "X":200, "V":300, "M":200, "N":200, "W":200, "S":200,
    "T":200, "GA":200, "PS":300, "EF":100, "SG":50, "BM":100,
}
EFFECTIF_MIN_VALABLE = SEUILS.copy()

BASE_ERP = [
    ["U","Santé (Hôpitaux)","Sécurité","Les fonctions de sécurité des personnes imposent au minimum une alimentation de sécurité. Les charges vitales non interruptibles doivent être traitées par UPS / ASI locale."],
    ["J","Personnes âgées / handicapées","Sécurité","Protection du public vulnérable et continuité des fonctions de sécurité."],
    ["O","Hôtels / Pensions","Sécurité","Public endormi : fonctions de sécurité à maintenir."],
    ["Rh","Internats","Sécurité","Public endormi et sécurité incendie."],
    ["OA","Hôtels d'altitude","Sécurité","Isolement et protection des occupants."],
    ["L","Salles de spectacles","Sécurité","Évacuation, balisage, SSI, désenfumage."],
    ["P","Salles de danse / jeux","Sécurité","Évacuation et protection des personnes."],
    ["Y","Musées","Secours","Continuité d'exploitation possible ; fonctions sécurité à vérifier séparément."],
    ["X","Établissements sportifs","Secours","Continuité fonctionnelle ; sécurité à préciser selon équipements."],
    ["V","Lieux de culte","Aucun","Pas de besoin systématique global ; analyser les fonctions réelles."],
    ["M","Magasins / centres commerciaux","Sécurité","Dès qu'il existe désenfumage / SSI / éclairage de sécurité, la sécurité domine."],
    ["N","Restaurants / Cafés","Secours","Continuité d'exploitation avant tout, sauf fonctions de sécurité spécifiques."],
    ["W","Bureaux / banques","Secours","Continuité d'exploitation ; les charges non interruptibles se traitent localement par UPS / ASI."],
    ["S","Bibliothèques / archives","Secours","Conservation / sûreté / exploitation ; sécurité selon fonctions présentes."],
    ["T","Salles d'exposition","Sécurité","Présence du public et fonctions sécurité fréquentes."],
    ["GA","Gares","Sécurité","Signalisation, évacuation, désenfumage, sécurité publique."],
    ["PS","Parkings couverts","Sécurité","Extraction, détection gaz, désenfumage."],
    ["EF","Établissements flottants","Sécurité","Fonctions vitales de sécurité."],
    ["SG","Structures gonflables","Sécurité","Maintien des équipements de sécurité structurelle."],
    ["BM","Bains maures","Secours","Continuité utile, sécurité à vérifier selon installations."],
    ["IGH","Immeubles de grande hauteur","Sécurité","Le niveau minimal est élevé ; analyser aussi la redondance et les fonctions critiques."],
    ["MIL","Défense / installations sensibles","Temps Zéro","Hypothèse haute retenue dans cette version : continuité maximale globale."],
    ["AER","Aéroports","Temps Zéro","Hypothèse haute retenue dans cette version : continuité maximale globale pour fonctions critiques."],
]
df_erp = pd.DataFrame(BASE_ERP, columns=["Code_type","Designation","Niveau_Min_Indicatif","Justification"])

FONCTIONS = [
    {"Famille":"Sécurité des personnes","Fonction":"Éclairage de sécurité","Niveau":"Sécurité","Reglementaire":"Oui","Commentaire":"Fonction directement liée à l'évacuation et à la sécurité des personnes.","Critique_TZ_Local":False},
    {"Famille":"Sécurité des personnes","Fonction":"SSI / alarme incendie / CMSI / sonorisation d'évacuation","Niveau":"Sécurité","Reglementaire":"Oui","Commentaire":"Fonction de sécurité incendie.","Critique_TZ_Local":False},
    {"Famille":"Sécurité des personnes","Fonction":"Désenfumage / extraction de fumées","Niveau":"Sécurité","Reglementaire":"Oui","Commentaire":"Équipement participant directement à la sécurité.","Critique_TZ_Local":False},
    {"Famille":"Sécurité des personnes","Fonction":"Pompes incendie / surpresseurs incendie","Niveau":"Sécurité","Reglementaire":"Oui","Commentaire":"Fonctions de lutte incendie.","Critique_TZ_Local":False},
    {"Famille":"Charges médicales / vitales","Fonction":"Bloc opératoire / réanimation / respirateurs / monitoring vital","Niveau":"Temps Zéro","Reglementaire":"Oui / très critique","Commentaire":"Charge critique nécessitant une continuité sans coupure. Pour un hôpital, cela implique une UPS locale en complément du GE de sécurité.","Critique_TZ_Local":True},
    {"Famille":"Charges critiques exploitation","Fonction":"Serveurs critiques / contrôle-commande / supervision centrale","Niveau":"Temps Zéro","Reglementaire":"Selon usage","Commentaire":"Continuité sans interruption parfois nécessaire ; UPS locale recommandée hors MIL / AER.","Critique_TZ_Local":True},
    {"Famille":"Charges critiques exploitation","Fonction":"Tour de contrôle / balisage / fonctions aéroportuaires critiques","Niveau":"Temps Zéro","Reglementaire":"Oui selon fonction","Commentaire":"Très forte criticité fonctionnelle.","Critique_TZ_Local":True},
    {"Famille":"Exploitation","Fonction":"Froid / chambres froides / conservation","Niveau":"Secours","Reglementaire":"Non en général","Commentaire":"Continuité d'exploitation, mais pas forcément sécurité des personnes.","Critique_TZ_Local":False},
    {"Famille":"Exploitation","Fonction":"Ventilation utile / climatisation utile / process","Niveau":"Secours","Reglementaire":"Non en général","Commentaire":"Important pour exploitation ou confort technique.","Critique_TZ_Local":False},
    {"Famille":"Exploitation","Fonction":"Encaissement / informatique non vitale / exploitation bureautique","Niveau":"Secours","Reglementaire":"Non","Commentaire":"Continuité souhaitée sans être une fonction de sécurité.","Critique_TZ_Local":False},
    {"Famille":"Exploitation","Fonction":"Vidéosurveillance / sûreté / anti-intrusion","Niveau":"Secours","Reglementaire":"Selon site","Commentaire":"Peut être important sans relever systématiquement de la sécurité incendie.","Critique_TZ_Local":False},
]
df_fonctions = pd.DataFrame(FONCTIONS)

# =========================================================
# FONCTIONS D'AFFICHAGE ET DE LOGIQUE
# =========================================================
def get_badge_html(type_groupe):
    tg = str(type_groupe).lower()
    if "temps zéro" in tg or "temps zero" in tg:
        return f'<span class="badge badge-tempszero">⚡ {type_groupe}</span>'
    elif "sécurité" in tg or "securite" in tg:
        return f'<span class="badge badge-securite">🛡️ {type_groupe}</span>'
    elif "secours" in tg:
        return f'<span class="badge badge-secours">🔋 {type_groupe}</span>'
    return f'<span class="badge badge-aucun">ℹ️ {type_groupe}</span>'

def get_result_box_class(type_groupe):
    tg = str(type_groupe).lower()
    if "temps zéro" in tg or "temps zero" in tg:
        return "result-box-tempszero"
    elif "sécurité" in tg or "securite" in tg:
        return "result-box-securite"
    elif "secours" in tg:
        return "result-box-secours"
    return "result-box-aucun"

def expliquer_groupe(type_groupe):
    if type_groupe == "Temps Zéro":
        return "<b>Temps Zéro</b> : aucune coupure n'est admissible pour la charge concernée. Ce niveau correspond aux cas où la continuité doit être assurée sans interruption au niveau global."
    elif type_groupe == "Sécurité":
        return "<b>Sécurité</b> : ce niveau concerne les installations participant directement à la protection des personnes et à l'évacuation."
    elif type_groupe == "Secours":
        return "<b>Secours</b> : ce niveau vise la continuité d'exploitation pour des usages importants, sans exiger une continuité instantanée de l'ensemble du site."
    return "<b>Aucun</b> : aucune exigence globale explicite n'a été retenue à ce stade. Une analyse complémentaire reste possible selon le projet."

def avantages_groupe(type_groupe):
    if type_groupe == "Temps Zéro":
        return "• Maintien sans coupure des charges ultra-critiques globales.<br>• Réduction maximale du risque fonctionnel.<br>• Réservé aux cas les plus exigeants."
    elif type_groupe == "Sécurité":
        return "• Réponse aux fonctions liées à la sécurité des personnes.<br>• Maintien des équipements réglementaires de sécurité.<br>• Cohérence avec les besoins d'évacuation et de protection."
    elif type_groupe == "Secours":
        return "• Continuité d'exploitation des usages importants.<br>• Réduction des pertes d'activité.<br>• Bon compromis entre besoin fonctionnel et coût."
    return "• Liberté de choix à ce stade.<br>• Possibilité d'affiner ensuite selon les contraintes réelles."

def render_inverseur_badges(inv):
    return f"""
    <span class="mini-badge">Transition : {inv['transition']}</span>
    <span class="mini-badge">Classe : {inv['classe']}</span>
    <span class="mini-badge">Commande : {inv['mode_commande']}</span>
    <span class="mini-badge">Bypass : {"Oui" if inv["bypass"] else "Non"}</span>
    <span class="mini-badge">UPS locale : {"Oui" if inv["besoin_ups"] else "Non"}</span>
    <span class="mini-badge">STS : {"Oui" if inv["besoin_sts"] else "Non"}</span>
    """

def afficher_bloc_resultat(titre, type_groupe, details_erp, details_fonctions):
    badge_html = get_badge_html(type_groupe)
    result_class = get_result_box_class(type_groupe)
    explication = expliquer_groupe(type_groupe)
    avantages = avantages_groupe(type_groupe)
    st.markdown(f"""
    <div class="{result_class}">
        <h3>{titre}</h3>
        {badge_html}
        <p><b>Type de groupe retenu :</b> {type_groupe}</p>
        <p><b>Équipements concernés :</b> {equipements_selon_niveau(type_groupe)}</p>
        <h4>Pourquoi ?</h4>
        <p>{explication}</p>
        <h4>Avantages</h4>
        <p>{avantages}</p>
        <h4>Analyse ERP</h4>
        <p>{details_erp}</p>
        <h4>Analyse des fonctions</h4>
        <p>{details_fonctions}</p>
    </div>
    """, unsafe_allow_html=True)

def equipements_selon_niveau(type_groupe):
    if type_groupe == "Temps Zéro":
        return "Charges vitales ou ultra-critiques globales : installations MIL, AER ou autres cas explicitement retenus comme non interruptibles au niveau global."
    elif type_groupe == "Sécurité":
        return "Éclairage de sécurité, SSI, désenfumage, pompes incendie, fonctions liées à la protection des personnes."
    elif type_groupe == "Secours":
        return "Froid, ventilation utile, exploitation, sûreté, informatique non vitale, continuité d'activité."
    return "Aucune exigence explicite globale à ce stade."

def afficher_synthese_finale(groupe_choisi, inverseur_choisi):
    st.markdown(f"""
    <div class="confirm-box">
        <h3>📋 Synthèse finale de l'étude</h3>
        <p><b>Groupe électrogène retenu :</b> {groupe_choisi}</p>
        <p><b>Inverseur de source retenu :</b> {inverseur_choisi['type_inverseur']}</p>
        <p><b>Classe :</b> {inverseur_choisi['classe']} &nbsp;|&nbsp; <b>Commande :</b> {inverseur_choisi['mode_commande']}</p>
        <p><b>Transition :</b> {inverseur_choisi['transition']} &nbsp;|&nbsp; <b>Bypass :</b> {"Oui" if inverseur_choisi['bypass'] else "Non"}</p>
        <p><b>Compléments :</b> {'UPS locale requise' if inverseur_choisi['besoin_ups'] else ''}{' + STS' if inverseur_choisi['besoin_sts'] else ''}</p>
        <hr>
        <p><i>Cette configuration répond aux exigences réglementaires et fonctionnelles identifiées.</i></p>
    </div>
    """, unsafe_allow_html=True)

# =========================================================
# REGLES METIER
# =========================================================
def determiner_categorie_erp(code, effectif_total):
    if code in TYPES_SPECIAUX:
        return None, "Pour ce type, la catégorie n'est pas utilisée comme critère principal dans cette version."
    seuil = SEUILS.get(code, 100)
    if effectif_total > 1500:
        return 1, "Effectif total > 1500."
    elif effectif_total > 700:
        return 2, "Effectif total entre 701 et 1500."
    elif effectif_total > 300:
        return 3, "Effectif total entre 301 et 700."
    elif effectif_total >= seuil:
        return 4, f"Effectif total ({effectif_total}) ≥ seuil 5e catégorie ({seuil})."
    return 5, f"Effectif total ({effectif_total}) < seuil 5e catégorie ({seuil})."

def niveau_min_erp(code):
    row = df_erp[df_erp["Code_type"] == code]
    if row.empty:
        return "Aucun", "Aucune base ERP trouvée."
    return row.iloc[0]["Niveau_Min_Indicatif"], row.iloc[0]["Justification"]

def niveau_fonctions_selectionnees(fonctions_selectionnees, code):
    if not fonctions_selectionnees:
        return "Aucun", "Aucune fonction particulière sélectionnée.", False, []
    max_score = 0
    justifs = []
    ups_local_necessaire = False
    for fonction in fonctions_selectionnees:
        ligne = df_fonctions[df_fonctions["Fonction"] == fonction]
        if not ligne.empty:
            niveau = ligne.iloc[0]["Niveau"]
            score = NIVEAU_SCORE[niveau]
            critique_tz_local = bool(ligne.iloc[0]["Critique_TZ_Local"])
            if critique_tz_local:
                if code in TYPES_TEMPS_ZERO_GLOBAL:
                    score = NIVEAU_SCORE["Temps Zéro"]
                    justifs.append(f"• {fonction} → Temps Zéro")
                else:
                    score = NIVEAU_SCORE["Sécurité"]
                    ups_local_necessaire = True
                    justifs.append(f"• {fonction} → charge critique : GE global = Sécurité + UPS locale requise")
            else:
                justifs.append(f"• {fonction} → {niveau}")
            if score > max_score:
                max_score = score
    fonctions_list = "<br>".join([f"• {f}" for f in fonctions_selectionnees])
    justifs.append(f"<br><b>Fonctions sélectionnées :</b><br>{fonctions_list}")
    return SCORE_NIVEAU[max_score], "<br>".join(justifs), ups_local_necessaire, []

def ajuster_par_temps_coupure(niveau_actuel, temps_coupure, code):
    score = NIVEAU_SCORE[niveau_actuel]
    justification = "Aucun ajustement par le temps de coupure."
    ups_local_temps = False
    if temps_coupure == "Aucune coupure admissible (0 s)":
        if code in TYPES_TEMPS_ZERO_GLOBAL:
            score = max(score, NIVEAU_SCORE["Temps Zéro"])
            justification = "Aucune coupure admissible (0 s) : pour ce type d'établissement, le niveau global est porté à Temps Zéro."
        else:
            score = max(score, NIVEAU_SCORE["Sécurité"])
            justification = "Aucune coupure admissible (0 s) : le niveau global retenu est Sécurité, avec UPS / ASI séparée pour les charges non interruptibles."
            ups_local_temps = True
    elif temps_coupure == "Coupure très courte admissible (comprise entre 10 s et 15 s)":
        score = max(score, NIVEAU_SCORE["Sécurité"])
        justification = "Une coupure très courte admissible impose au minimum un niveau Sécurité."
    elif temps_coupure == "Coupure courte admissible (≤ 15 s)":
        score = max(score, NIVEAU_SCORE["Secours"])
        justification = "Une coupure courte admissible impose au minimum un niveau Secours."
    else:
        justification = "Une coupure longue admissible (> 15 s) n'impose pas de relèvement particulier."
    return SCORE_NIVEAU[score], justification, ups_local_temps

def niveau_final_automatique(code, fonctions_selectionnees, temps_coupure):
    niveau_erp, justif_erp = niveau_min_erp(code)
    niveau_fct, justif_fct, ups_local_fct, _ = niveau_fonctions_selectionnees(fonctions_selectionnees, code)
    score_base = max(NIVEAU_SCORE[niveau_erp], NIVEAU_SCORE[niveau_fct])
    niveau_base = SCORE_NIVEAU[score_base]
    niveau_apres_temps, justif_temps, ups_local_temps = ajuster_par_temps_coupure(niveau_base, temps_coupure, code)
    if code not in TYPES_TEMPS_ZERO_GLOBAL and niveau_apres_temps == "Temps Zéro":
        niveau_apres_temps = "Sécurité"
    ups_local_requis = ups_local_fct or ups_local_temps
    remarque_ups = ""
    if ups_local_requis:
        remarque_ups = """
        <b>Remarque importante :</b><br>
        Pour cet établissement, le <b>niveau global retenu reste Sécurité</b>.<br>
        La présence de charges critiques ou d'un besoin sans coupure ne conduit pas à classer tout le site en <b>Temps Zéro</b>.<br><br>
        <b>Solution recommandée :</b><br>
        • prévoir un <b>groupe électrogène de Sécurité</b> pour l'installation générale,<br>
        • ajouter des <b>UPS locales</b> au niveau des charges critiques ou non interruptibles.
        """
    justification_globale = {
        "erp": f"Niveau minimal indicatif lié au type ERP : <b>{niveau_erp}</b><br>{justif_erp}",
        "fonctions": f"Niveau issu des fonctions sélectionnées : <b>{niveau_fct}</b><br>{justif_fct}",
        "temps": f"Ajustement selon la continuité admissible : <b>{niveau_apres_temps}</b><br>{justif_temps}",
        "remarque_ups": remarque_ups
    }
    return niveau_apres_temps, justification_globale, niveau_erp, niveau_fct, ups_local_requis

def niveau_minimal_mode_manuel(code, temps_coupure):
    niveau_erp, justif_erp = niveau_min_erp(code)
    remarque_ups = ""
    if temps_coupure == "Coupure longue admissible (> 15 s)":
        niveau_recommande = "Aucun"
        justif_temps = "Une coupure longue admissible (> 15 s) n'impose pas de niveau minimal particulier."
    elif temps_coupure == "Coupure courte admissible (≤ 15 s)":
        niveau_recommande = "Secours"
        justif_temps = "Une coupure courte admissible (≤ 15 s) conduit à recommander un groupe de Secours."
    elif temps_coupure == "Coupure très courte admissible (comprise entre 10 s et 15 s)":
        niveau_recommande = "Sécurité"
        justif_temps = "Une coupure très courte admissible (comprise entre 10 s et 15 s) conduit à recommander un groupe de Sécurité."
    elif temps_coupure == "Aucune coupure admissible (0 s)":
        if code in TYPES_TEMPS_ZERO_GLOBAL:
            niveau_recommande = "Temps Zéro"
            justif_temps = "Aucune coupure admissible (0 s) : pour ce type d'établissement, la recommandation est Temps Zéro."
        else:
            niveau_recommande = "Sécurité"
            justif_temps = "Aucune coupure admissible (0 s) : la recommandation est Sécurité avec UPS / ASI séparée pour les charges non interruptibles."
            remarque_ups = """
            <b>Remarque importante :</b><br>
            Le niveau global retenu reste <b>Sécurité</b>.<br>
            Les charges sans coupure doivent être traitées par <b>UPS / ASI séparée</b>.
            """
    else:
        niveau_recommande = "Aucun"
        justif_temps = "Aucun critère de temps reconnu."
    justification_globale = {
        "erp": f"Type ERP sélectionné : <b>{code}</b><br>{justif_erp}",
        "fonctions": "Analyse interne non affichée en mode manuel.",
        "temps": f"Référence minimale pilotée par le temps de coupure : <b>{niveau_recommande}</b><br>{justif_temps}",
        "remarque_ups": remarque_ups
    }
    return niveau_recommande, justification_globale, niveau_erp, "Non affiché", False

def verifier_choix_manuel(niveau_manuel, niveau_minimal):
    return NIVEAU_SCORE[niveau_manuel] >= NIVEAU_SCORE[niveau_minimal]

# =========================================================
# RECOMMANDATION INVERSEUR
# =========================================================
CRITICITE_SCORE = {"Vie humaine":3, "Dommages techniques / données":2, "Pertes financières / exploitation":1}
def criticite_dominante(criticites_selectionnees):
    if not criticites_selectionnees:
        return "Pertes financières / exploitation"
    max_score = 0
    dominante = "Pertes financières / exploitation"
    for c in criticites_selectionnees:
        score = CRITICITE_SCORE.get(c,0)
        if score > max_score:
            max_score = score
            dominante = c
    return dominante

def recommander_inverseur(groupe_ge, coupure, transition, maintenance_sans_coupure, criticites_selectionnees, mode_choix_inv, inverseur_force=None, classe_force=None):
    notes = []
    architecture = []
    besoin_ups = False
    besoin_sts = False
    criticite = criticite_dominante(criticites_selectionnees)
    if len(criticites_selectionnees) > 1:
        notes.append(f"Plusieurs niveaux de criticité sélectionnés : {', '.join(criticites_selectionnees)}. Niveau dominant retenu : <b>{criticite}</b>.")

    if groupe_ge == "Temps Zéro":
        type_recommande = "ATSE"
        commande = "Automatique"
        classe = "PC"
        notes.append("Le niveau global confirmé est Temps Zéro : l'architecture doit viser une très haute continuité.")
        architecture.append("ATSE prioritaire")
        architecture.append("Bypass fortement recommandé")
        besoin_ups = True
    elif groupe_ge == "Sécurité":
        type_recommande = "ATSE"
        commande = "Automatique"
        classe = "CB"
        notes.append("Le niveau global confirmé est Sécurité : le basculement automatique est à privilégier.")
        architecture.append("ATSE recommandé")
    elif groupe_ge == "Secours":
        type_recommande = "RTSE"
        commande = "Télécommandée / automatique selon besoin"
        classe = "CB"
        notes.append("Le niveau global confirmé est Secours : la continuité d'exploitation est recherchée sans exigence maximale systématique.")
        architecture.append("RTSE ou ATSE selon criticité")
    else:
        type_recommande = "MTSE"
        commande = "Manuelle"
        classe = "CC"
        notes.append("Aucune exigence forte globale n'est retenue à ce stade.")
        architecture.append("MTSE possible")

    if coupure == "< 50 ms":
        besoin_ups = True
        besoin_sts = True
        type_recommande = "ATSE"
        commande = "Automatique"
        classe = "PC"
        notes.append("Une coupure < 50 ms ne peut pas être garantie par un inverseur mécanique seul. Une architecture complémentaire de type UPS / STS est nécessaire.")
    elif coupure == "50 ms à 2 s":
        if groupe_ge in ["Sécurité","Temps Zéro"]:
            type_recommande = "ATSE"
            commande = "Automatique"
        elif groupe_ge == "Secours":
            type_recommande = "ATSE" if criticite in ["Vie humaine","Dommages techniques / données"] else "RTSE"
        else:
            type_recommande = "RTSE"
    else:
        if groupe_ge == "Temps Zéro":
            besoin_ups = True
            type_recommande = "ATSE"
            commande = "Automatique"
            notes.append("Même si l'utilisateur saisit > 2 s, le niveau Temps Zéro implique une architecture plus exigeante.")
        elif groupe_ge == "Sécurité":
            type_recommande = "ATSE"
            commande = "Automatique"
        elif groupe_ge == "Secours":
            type_recommande = "RTSE"
            commande = "Télécommandée"
        else:
            type_recommande = "MTSE"
            commande = "Manuelle"

    transition_reelle = transition
    if transition == "Fermée (sans coupure)":
        type_recommande = "ATSE"
        commande = "Automatique"
        classe = "PC"
        notes.append("La transition fermée nécessite une synchronisation des sources. Elle doit être réservée à des sources compatibles et à des appareillages adaptés.")
    elif transition == "Statique":
        type_recommande = "ATSE"
        commande = "Automatique"
        classe = "PC"
        besoin_sts = True
        besoin_ups = True
        notes.append("Le transfert statique relève d'une architecture STS / UPS, pas d'un simple inverseur mécanique.")
    elif transition == "Retardée (I-O-II)":
        notes.append("La transition retardée correspond au cas le plus courant en groupe électrogène.")
    else:
        notes.append("La transition ouverte implique une coupure franche lors du transfert.")

    bypass = False
    if maintenance_sans_coupure == "Oui":
        bypass = True
        if type_recommande != "ATSE":
            type_recommande = "ATSE"
            commande = "Automatique"
            notes.append("Le besoin de maintenance sans coupure pousse vers un ATSE avec bypass.")
        architecture.append("Bypass de maintenance recommandé")

    if criticite == "Vie humaine":
        type_recommande = "ATSE"
        commande = "Automatique"
        if transition in ["Fermée (sans coupure)","Statique"] or coupure == "< 50 ms":
            classe = "PC"
        notes.append("La criticité humaine impose une architecture de haute disponibilité.")
    elif criticite == "Dommages techniques / données":
        if coupure == "< 50 ms":
            besoin_ups = True
            besoin_sts = True
        if type_recommande == "MTSE":
            type_recommande = "RTSE"

    if transition in ["Fermée (sans coupure)","Statique"] or groupe_ge == "Temps Zéro":
        classe = "PC"
    elif type_recommande == "ATSE" and "PC" not in classe:
        classe = "CB"
    elif type_recommande == "RTSE" and "CB" not in classe and "PC" not in classe:
        classe = "CB"
    if classe not in ["CC","CB","PC"]:
        classe = "CB"

    alerte_manuel = ""
    if mode_choix_inv == "Choix manuel contrôlé" and inverseur_force and classe_force:
        type_recommande = inverseur_force
        classe = classe_force
        incoherences = []
        if coupure == "< 50 ms" and inverseur_force in ["MTSE","RTSE"]:
            incoherences.append("Un MTSE ou RTSE seul ne convient pas pour une exigence < 50 ms.")
        if transition == "Fermée (sans coupure)" and inverseur_force != "ATSE":
            incoherences.append("La transition fermée exige un ATSE avec logique de synchronisation.")
        if maintenance_sans_coupure == "Oui" and inverseur_force != "ATSE":
            incoherences.append("Le bypass de maintenance est cohérent surtout avec un ATSE.")
        if groupe_ge == "Sécurité" and inverseur_force == "MTSE":
            incoherences.append("Pour un groupe de Sécurité, un inverseur manuel est généralement insuffisant.")
        if groupe_ge == "Temps Zéro" and inverseur_force != "ATSE":
            incoherences.append("Pour un niveau Temps Zéro, un ATSE reste la base minimale de l'architecture globale.")
        if incoherences:
            alerte_manuel = " ".join(incoherences)

    if type_recommande == "MTSE":
        description = "Inverseur manuel simple, adapté aux besoins peu critiques et aux coupures admissibles longues."
    elif type_recommande == "RTSE":
        description = "Inverseur télécommandé, adapté aux besoins intermédiaires avec pilotage à distance."
    else:
        description = "Inverseur automatique, adapté aux besoins de sécurité, de disponibilité et aux architectures critiques."
    if bypass:
        description += " Version avec bypass de maintenance recommandée."
    if besoin_sts:
        description += " Une architecture complémentaire STS / UPS est nécessaire pour les charges ultra-sensibles."

    if transition_reelle == "Ouverte":
        schema_html = '<div class="schema-bar"><div class="schema-src1" style="width:40%">Source I</div><div class="schema-off" style="width:20%">OFF</div><div class="schema-src2" style="width:40%">Source II</div></div><div>Ouverture source I → temps mort → fermeture source II</div>'
    elif transition_reelle == "Retardée (I-O-II)":
        schema_html = '<div class="schema-bar"><div class="schema-src1" style="width:35%">Source I</div><div class="schema-off" style="width:30%">OFF réglable</div><div class="schema-src2" style="width:35%">Source II</div></div><div>Détection → temporisation → ouverture → temps mort → fermeture</div>'
    elif transition_reelle == "Fermée (sans coupure)":
        schema_html = '<div class="schema-bar"><div class="schema-src1" style="width:45%">Source I</div><div class="schema-sync" style="width:10%">SYNC</div><div class="schema-src2" style="width:45%">Source II</div></div><div>Synchronisation des sources avant transfert</div>'
    else:
        schema_html = '<div class="schema-bar"><div class="schema-src1" style="width:48%">Source I</div><div class="schema-sync" style="width:4%">STS</div><div class="schema-src2" style="width:48%">Source II</div></div><div>Commutation statique ultra-rapide, associée à une architecture UPS / STS</div>'

    return {
        "type_inverseur": type_recommande,
        "mode_commande": commande,
        "classe": classe,
        "transition": transition_reelle,
        "bypass": bypass,
        "besoin_ups": besoin_ups,
        "besoin_sts": besoin_sts,
        "description": description,
        "notes": notes,
        "architecture": architecture,
        "alerte_manuel": alerte_manuel,
        "schema_html": schema_html,
        "criticites_selectionnees": criticites_selectionnees,
        "criticite_dominante": criticite,
    }

# =========================================================
# PARTIE 1 : CHOIX DU GROUPE ELECTROGENE
# =========================================================
st.markdown("""
<div class="info-box">
    <b>Objectif :</b> guider le choix du niveau de groupe électrogène puis de l'inverseur de source
    en tenant compte du type d'établissement, du niveau de continuité attendu, de la criticité des usages
    et des contraintes de disponibilité de l'installation.
    <br><br>
    <b>Références prises en compte :</b> exigences normatives, règlement ERP, continuité de service, sécurité des personnes.
</div>
""", unsafe_allow_html=True)

mode_choix = st.radio("Mode de choix du groupe électrogène", ["Détermination automatique améliorée", "Choix manuel contrôlé"], horizontal=True)

if mode_choix == "Détermination automatique améliorée":
    st.markdown("## 1️⃣ Détermination automatique améliorée")
    col1, col2 = st.columns(2)
    with col1:
        erp_choice = st.selectbox("Type d'établissement", list(erp_types.keys()))
        code = erp_types[erp_choice]
    with col2:
        if code in TYPES_SPECIAUX:
            st.info("Pour ce type, la catégorie est affichée comme non déterminante dans cette version.")
            effectif_total = 0
        else:
            effectif_min = EFFECTIF_MIN_VALABLE.get(code, 1)
            st.markdown(f'<div class="seuil-info-box">ℹ️ <b>Effectif minimal valable pour ce type ERP ({code}) :</b> {effectif_min} personnes<br>En dessous de ce seuil, l\'établissement est classé en 5e catégorie mais reste soumis aux règles ERP.</div>', unsafe_allow_html=True)
            effectif_total = st.number_input("Effectif total admissible", min_value=0, step=1, value=0)
    effectif_invalide = (code not in TYPES_SPECIAUX) and (effectif_total == 0)
    if effectif_invalide:
        st.markdown('<div class="impossible-box"><h3>🚫 Effectif invalide — Analyse impossible</h3><p>Un effectif de <b>0</b> ne permet pas de réaliser une analyse réglementaire ERP.</p><p>Veuillez saisir l\'effectif total admissible de l\'établissement (nombre de personnes) pour que l\'outil puisse déterminer la catégorie ERP et le niveau de groupe adapté.</p></div>', unsafe_allow_html=True)
    else:
        categorie, justification_categorie = determiner_categorie_erp(code, effectif_total)
        st.markdown("### 2️⃣ Fonctions réellement à alimenter")
        fonctions_selectionnees = st.multiselect("Sélectionnez les fonctions / charges concernées", options=df_fonctions["Fonction"].tolist(), help="Plusieurs fonctions peuvent être retenues. Le niveau final suit la criticité la plus forte autorisée par la logique globale du site.")
        st.markdown("### 3️⃣ Continuité admissible")
        temps_coupure = st.radio("Temps de coupure maximal admissible pour les charges considérées", ["Coupure longue admissible (> 15 s)", "Coupure courte admissible (≤ 15 s)", "Coupure très courte admissible (comprise entre 10 s et 15 s)", "Aucune coupure admissible (0 s)"], horizontal=False)
        if st.button("Lancer la détermination", use_container_width=True):
            niveau_final, justifs, niveau_erp_indicatif, niveau_fct, ups_local_requis = niveau_final_automatique(code, fonctions_selectionnees, temps_coupure)
            st.session_state.resultat_final = {
                "mode": "Détermination automatique améliorée",
                "code": code, "erp_choice": erp_choice, "categorie": categorie,
                "justification_categorie": justification_categorie,
                "fonctions_selectionnees": fonctions_selectionnees,
                "temps_coupure": temps_coupure,
                "niveau_erp_indicatif": niveau_erp_indicatif,
                "niveau_fonctions": niveau_fct,
                "niveau_final": niveau_final,
                "details": justifs,
                "justification_libre": "",
                "ups_local_requis": ups_local_requis,
                "effectif_total": effectif_total   # <-- AJOUT
            }
            st.session_state.choix_confirme = False
            st.session_state.groupe_confirme = None
            st.session_state.inverseur_confirme = False
            st.session_state.inverseur_final = None
            st.session_state.choix_inverseur_resultat = None

else:  # Mode manuel
    st.markdown("## 1️⃣ Choix manuel contrôlé")
    col1, col2 = st.columns(2)
    with col1:
        erp_choice = st.selectbox("Type d'établissement", list(erp_types.keys()), key="manual_erp")
        code = erp_types[erp_choice]
    with col2:
        if code in TYPES_SPECIAUX:
            st.info("Pour ce type, la catégorie n'est pas utilisée comme pivot principal dans cette version.")
            effectif_total = 0
        else:
            effectif_min = EFFECTIF_MIN_VALABLE.get(code, 1)
            st.markdown(f'<div class="seuil-info-box">ℹ️ <b>Effectif minimal valable pour ce type ERP ({code}) :</b> {effectif_min} personnes<br>En dessous de ce seuil, l\'établissement est classé en 5e catégorie mais reste soumis aux règles ERP.</div>', unsafe_allow_html=True)
            effectif_total = st.number_input("Effectif total admissible", min_value=0, step=1, value=0, key="manual_eff")
    effectif_invalide = (code not in TYPES_SPECIAUX) and (effectif_total == 0)
    if effectif_invalide:
        st.markdown('<div class="impossible-box"><h3>🚫 Effectif invalide — Analyse impossible</h3><p>Un effectif de <b>0</b> ne permet pas de réaliser une analyse réglementaire ERP.</p><p>Veuillez saisir l\'effectif total admissible de l\'établissement (nombre de personnes) pour que l\'outil puisse déterminer la catégorie ERP et le niveau de groupe adapté.</p></div>', unsafe_allow_html=True)
    else:
        categorie, justification_categorie = determiner_categorie_erp(code, effectif_total)
        fonctions_selectionnees = []
        temps_coupure = st.radio("Temps de coupure maximal admissible", ["Coupure longue admissible (> 15 s)", "Coupure courte admissible (≤ 15 s)", "Coupure très courte admissible (comprise entre 10 s et 15 s)", "Aucune coupure admissible (0 s)"], key="manual_time")
        niveau_minimal, justifs, niveau_erp_indicatif, niveau_fct, ups_local_requis = niveau_minimal_mode_manuel(code, temps_coupure)
        st.markdown(f'<div class="card"><h3>Référence minimale issue de l\'analyse</h3><p><b>Niveau minimal recommandé :</b> {niveau_minimal}</p><p class="small-note">Le choix manuel peut être égal ou supérieur à ce niveau. S\'il est inférieur, l\'outil génère une alerte.</p></div>', unsafe_allow_html=True)
        groupe_manuel = st.selectbox("Choisissez directement le niveau de groupe électrogène", ["Aucun", "Secours", "Sécurité", "Temps Zéro"])
        justification_client = st.text_area("Justification / remarque du client", placeholder="Exemple : le client impose un niveau supérieur pour des raisons d'exploitation critique.")
        if groupe_manuel == "Aucun":
            st.error("⚠️ Vous devez sélectionner un groupe (Secours, Sécurité ou Temps Zéro) pour pouvoir valider.")
            valider_desactive = True
        else:
            conforme = verifier_choix_manuel(groupe_manuel, niveau_minimal)
            if conforme:
                st.success("Le choix manuel est cohérent avec le niveau minimal issu de l'analyse.")
            else:
                st.warning("Le choix manuel est inférieur au niveau minimal déduit de l'analyse. Vérification réglementaire / fonctionnelle recommandée.")
            valider_desactive = False
        if st.button("Valider le choix manuel", use_container_width=True, disabled=valider_desactive):
            st.session_state.resultat_final = {
                "mode": "Choix manuel contrôlé",
                "code": code, "erp_choice": erp_choice, "categorie": categorie,
                "justification_categorie": justification_categorie,
                "fonctions_selectionnees": fonctions_selectionnees,
                "temps_coupure": temps_coupure,
                "niveau_erp_indicatif": niveau_erp_indicatif,
                "niveau_fonctions": niveau_fct,
                "niveau_final": groupe_manuel,
                "niveau_minimal": niveau_minimal,
                "choix_conforme": conforme,
                "details": justifs,
                "justification_libre": justification_client,
                "ups_local_requis": ups_local_requis,
                "effectif_total": effectif_total   # <-- AJOUT
            }
            st.session_state.choix_confirme = False
            st.session_state.groupe_confirme = None
            st.session_state.inverseur_confirme = False
            st.session_state.inverseur_final = None
            st.session_state.choix_inverseur_resultat = None

# =========================================================
# AFFICHAGE RESULTAT (GROUPE)
# =========================================================
if st.session_state.resultat_final is not None:
    r = st.session_state.resultat_final
    st.markdown("## ✅ Résultat final")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f'<div class="metric-card"><div class="metric-label">Code ERP</div><div class="metric-value">{r["code"]}</div><div class="metric-sub">{r["erp_choice"]}</div></div>', unsafe_allow_html=True)
    with c2:
        val_cat = "N/A" if r["categorie"] is None else r["categorie"]
        st.markdown(f'<div class="metric-card"><div class="metric-label">Catégorie ERP</div><div class="metric-value">{val_cat}</div><div class="metric-sub">Calcul indicatif</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="metric-card"><div class="metric-label">Niveau ERP indicatif</div><div class="metric-value">{r["niveau_erp_indicatif"]}</div><div class="metric-sub">Plancher type ERP</div></div>', unsafe_allow_html=True)
    with c4:
        st.markdown(f'<div class="metric-card"><div class="metric-label">Niveau final retenu</div><div class="metric-value">{r["niveau_final"]}</div><div class="metric-sub">{r["mode"]}</div></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="card"><h3>Justification catégorie ERP</h3><p>{r["justification_categorie"]}</p></div>', unsafe_allow_html=True)

    if r["mode"] == "Choix manuel contrôlé":
        afficher_bloc_resultat("⚡ Groupe retenu", r["niveau_final"], r['details']['erp'], r['details']['temps'])
    else:
        afficher_bloc_resultat("⚡ Groupe retenu", r["niveau_final"], r['details']['erp'], r['details']['fonctions'])

    if r["details"].get("remarque_ups"):
        st.markdown(f'<div class="ups-box"><h3>🔌 Remarque sur les charges critiques</h3><p>{r["details"]["remarque_ups"]}</p></div>', unsafe_allow_html=True)

    st.markdown("### 🔓 Confirmation de la partie 1")
    st.info("Cliquez sur le bouton ci-dessous pour confirmer définitivement le groupe retenu et déverrouiller la partie 2.")
    if st.button("✅ Confirmer le choix du groupe et déverrouiller la partie 2", use_container_width=True):
        st.session_state.choix_confirme = True
        st.session_state.groupe_confirme = r["niveau_final"]
        st.session_state.inverseur_confirme = False
        st.session_state.inverseur_final = None
        st.session_state.choix_inverseur_resultat = None

    if st.session_state.choix_confirme and st.session_state.groupe_confirme is not None:
        st.markdown(f'<div class="confirm-box"><h3>Partie 1 confirmée</h3><p><b>Groupe confirmé :</b> {st.session_state.groupe_confirme}</p><p>La partie 2 est maintenant déverrouillée.</p></div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="lock-box"><h3>Partie 2 encore verrouillée</h3><p>Veuillez confirmer le groupe retenu pour activer le choix de l\'inverseur.</p></div>', unsafe_allow_html=True)

# =========================================================
# PARTIE 2 : CHOIX DE L'INVERSEUR DE SOURCES
# =========================================================
if st.session_state.get("choix_confirme", False) and st.session_state.get("groupe_confirme") is not None:
    st.markdown("---")
    st.markdown('<div class="section-title">2️⃣ Choix de l\'inverseur de sources</div>', unsafe_allow_html=True)
    groupe_partie_1 = st.session_state.groupe_confirme
    col_a, col_b = st.columns(2)
    with col_a:
        mode_inverseur = st.radio("Mode de choix de l'inverseur", ["Détermination automatique", "Choix manuel contrôlé"], horizontal=True, key="mode_inverseur")
        coupure_inv = st.selectbox("Temps de coupure admissible", ["< 50 ms", "50 ms à 2 s", "> 2 s"], index=1, key="coupure_inv")
        transition_inv = st.selectbox("Type de transition souhaité", ["Ouverte", "Retardée (I-O-II)", "Fermée (sans coupure)", "Statique"], index=1, key="transition_inv")
        maintenance_inv = st.radio("Maintenance sans coupure requise ?", ["Non", "Oui"], horizontal=True, key="maintenance_inv")
    with col_b:
        criticites_inv = st.multiselect("Niveau de criticité (choix multiple possible)", options=["Vie humaine", "Dommages techniques / données", "Pertes financières / exploitation"], default=["Pertes financières / exploitation"], key="criticite_inv", help="Sélectionnez un ou plusieurs niveaux de criticité. Le niveau le plus élevé sera retenu pour la recommandation.")
        if len(criticites_inv) > 1:
            dominant = criticite_dominante(criticites_inv)
            st.markdown(f'<div class="seuil-info-box">ℹ️ Plusieurs criticités sélectionnées. Niveau dominant retenu : <b>{dominant}</b></div>', unsafe_allow_html=True)
        inverseur_force = None
        classe_force = None
        if mode_inverseur == "Choix manuel contrôlé":
            inverseur_force = st.selectbox("Forcer le type d'inverseur", ["MTSE", "RTSE", "ATSE"], key="inverseur_force")
            classe_force = st.selectbox("Forcer la classe", ["CC", "CB", "PC"], index=2, key="classe_force")
    if st.button("Lancer le choix de l'inverseur", use_container_width=True):
        if not criticites_inv:
            st.warning("Veuillez sélectionner au moins un niveau de criticité.")
        else:
            st.session_state.choix_inverseur_resultat = recommander_inverseur(
                groupe_ge=groupe_partie_1,
                coupure=coupure_inv,
                transition=transition_inv,
                maintenance_sans_coupure=maintenance_inv,
                criticites_selectionnees=criticites_inv,
                mode_choix_inv=mode_inverseur,
                inverseur_force=inverseur_force,
                classe_force=classe_force
            )
            st.session_state.inverseur_confirme = False
            st.session_state.inverseur_final = None

    if st.session_state.get("choix_inverseur_resultat") is not None:
        inv = st.session_state.choix_inverseur_resultat
        st.markdown("## ✅ Résultat partie 2")
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.markdown(f'<div class="metric-card"><div class="metric-label">Type d\'inverseur</div><div class="metric-value">{inv["type_inverseur"]}</div><div class="metric-sub">Recommandation</div></div>', unsafe_allow_html=True)
        with m2:
            st.markdown(f'<div class="metric-card"><div class="metric-label">Mode de commande</div><div class="metric-value">{inv["mode_commande"]}</div><div class="metric-sub">Pilotage retenu</div></div>', unsafe_allow_html=True)
        with m3:
            st.markdown(f'<div class="metric-card"><div class="metric-label">Classe</div><div class="metric-value">{inv["classe"]}</div><div class="metric-sub">Aide à la décision</div></div>', unsafe_allow_html=True)
        with m4:
            bypass_txt = "Oui" if inv["bypass"] else "Non"
            st.markdown(f'<div class="metric-card"><div class="metric-label">Bypass</div><div class="metric-value">{bypass_txt}</div><div class="metric-sub">Maintenance</div></div>', unsafe_allow_html=True)
        badges_html = render_inverseur_badges(inv)
        criticites_html = " ".join([f'<span class="mini-badge">⚠️ {c}</span>' for c in inv.get("criticites_selectionnees", [])])
        if len(inv.get("criticites_selectionnees", [])) > 1:
            criticites_html += f'<br><span class="mini-badge" style="background:#fff4db;color:#b26a00;">Dominant : {inv.get("criticite_dominante","")}</span>'
        st.markdown(f'<div class="tse-card"><div class="tse-title">{inv["type_inverseur"]}</div><div class="tse-subtitle">{inv["description"]}</div>{badges_html}<div style="margin-top:10px;"><b>Criticité(s) :</b> {criticites_html}</div></div>', unsafe_allow_html=True)
        if inv["notes"]:
            st.markdown('<div class="good-box"><h3>Pourquoi ce choix ?</h3><ul>' + "".join([f"<li>{n}</li>" for n in inv["notes"]]) + "</ul></div>", unsafe_allow_html=True)
        if inv["architecture"]:
            st.markdown('<div class="card"><h3>Architecture conseillée</h3><ul>' + "".join([f"<li>{a}</li>" for a in inv["architecture"]]) + "</ul></div>", unsafe_allow_html=True)
        st.markdown(f'<div class="schema-box"><h3>Schéma simplifié de transfert</h3>{inv["schema_html"]}</div>', unsafe_allow_html=True)
        if inv["besoin_ups"] or inv["besoin_sts"]:
            texte_archi = []
            if inv["besoin_ups"]:
                texte_archi.append("ajouter une UPS / ASI locale pour les charges non interruptibles")
            if inv["besoin_sts"]:
                texte_archi.append("prévoir une architecture STS pour les charges ultra-sensibles")
            st.markdown(f'<div class="warn-box"><h3>Remarque importante</h3><p><b>Complément recommandé :</b> {" ; ".join(texte_archi)}.</p></div>', unsafe_allow_html=True)
        if inv["alerte_manuel"]:
            st.markdown(f'<div class="danger-box"><h3>⚠️ Alerte sur le choix manuel</h3><p>{inv["alerte_manuel"]}</p></div>', unsafe_allow_html=True)

        if st.button("✅ Confirmer le choix de l'inverseur", use_container_width=True):
            st.session_state.inverseur_confirme = True
            st.session_state.inverseur_final = inv

        if st.session_state.get("inverseur_confirme", False) and st.session_state.get("inverseur_final") is not None:
            afficher_synthese_finale(st.session_state.groupe_confirme, st.session_state.inverseur_final)

            # Bouton d'export PDF après la synthèse
            col_pdf1, col_pdf2, col_pdf3 = st.columns([1,2,1])
            with col_pdf2:
                if st.button("📄 Exporter les résultats en PDF", use_container_width=True):
                    r = st.session_state.resultat_final
                    inv = st.session_state.inverseur_final
                    entrees = {
                        "Type ERP": r["erp_choice"],
                        "Effectif total": r.get("effectif_total", "Non renseigné"),
                        "Fonctions sélectionnées": ", ".join(r["fonctions_selectionnees"]) if r["fonctions_selectionnees"] else "Aucune",
                        "Temps de coupure": r["temps_coupure"]
                    }
                    resultats_groupe = {
                        "Niveau retenu": r["niveau_final"],
                        "Justification ERP": r["details"]["erp"],
                        "Analyse des fonctions": r["details"]["fonctions"] if r["mode"] != "Choix manuel contrôlé" else r["details"]["temps"]
                    }
                    resultats_inverseur = {
                        "Type d'inverseur": inv["type_inverseur"],
                        "Classe": inv["classe"],
                        "Mode de commande": inv["mode_commande"],
                        "Transition": inv["transition"],
                        "Bypass": "Oui" if inv["bypass"] else "Non",
                        "UPS locale": "Oui" if inv["besoin_ups"] else "Non",
                        "STS": "Oui" if inv["besoin_sts"] else "Non"
                    }
                    href = generer_pdf(entrees, resultats_groupe, resultats_inverseur)
                    st.markdown(href, unsafe_allow_html=True)
                    st.success("Rapport PDF généré avec succès ! Cliquez sur le lien ci-dessus pour le télécharger.")

else:
    st.markdown("---")
    st.markdown('<div class="warning-box"><h3>Partie 2 verrouillée</h3><p>Veuillez d\'abord confirmer le choix du groupe électrogène dans la partie 1 pour activer le choix de l\'inverseur.</p></div>', unsafe_allow_html=True)

# =========================================================
# NOTE IMPORTANTE
# =========================================================
st.markdown("""
<div class="info-box">
    <b>Note importante :</b> cette interface constitue une <b>aide à la décision</b> fondée sur une logique construite
    dans le respect des normes techniques applicables et du règlement des ERP.
    La validation finale doit rester cohérente avec l'étude détaillée du projet, les schémas retenus,
    les charges réellement secourues et les exigences spécifiques de l'installation.
</div>
""", unsafe_allow_html=True)
