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
    page_title="PowerSwitch Decision",
    layout="wide",
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
# CSS — Cegelec / VINCI Energies Design System
# =========================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@300;400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap');

    :root {
        --blue:       #005BAC;
        --blue-dark:  #003B70;
        --blue-light: #EAF3FB;
        --cyan:       #00A3E0;
        --white:      #FFFFFF;
        --bg:         #F4F6F8;
        --border:     #D9E1E8;
        --text:       #1F2937;
        --muted:      #6B7280;
        --success:    #16A34A;
        --warning:    #D97706;
        --danger:     #DC2626;
        --radius:     6px;
        --radius-lg:  10px;
    }

    html, body, .stApp {
        background: var(--bg) !important;
        font-family: 'IBM Plex Sans', -apple-system, sans-serif !important;
        color: var(--text) !important;
    }
    h1,h2,h3,h4,h5,h6,p,span,div,label,button,input,select,textarea {
        font-family: 'IBM Plex Sans', -apple-system, sans-serif !important;
    }

    /* Hide Streamlit chrome */
    #MainMenu, footer, header[data-testid="stHeader"] { display: none !important; }
    .block-container {
        padding-top: 76px !important;
        padding-bottom: 56px !important;
        max-width: 1080px !important;
    }

    /* ===== STICKY HEADER ===== */
    .ps-header {
        position: fixed;
        top: 0; left: 0; right: 0;
        z-index: 9999;
        background: var(--blue);
        height: 56px;
        display: flex;
        align-items: center;
        padding: 0 36px;
        box-shadow: 0 2px 10px rgba(0,59,112,0.22);
        border-bottom: 2px solid var(--blue-dark);
        gap: 14px;
    }
    .ps-header-accent {
        width: 5px; height: 28px;
        background: var(--cyan);
        border-radius: 3px;
        flex-shrink: 0;
    }
    .ps-header-name {
        font-size: 14px;
        font-weight: 700;
        color: #FFFFFF;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin: 0;
    }

    /* ===== INTRO ===== */
    .ps-intro {
        background: var(--white);
        border: 1px solid var(--border);
        border-top: 3px solid var(--blue);
        border-radius: var(--radius-lg);
        padding: 36px 40px 30px;
        margin-bottom: 24px;
    }
    .ps-intro-title {
        font-size: 21px;
        font-weight: 700;
        color: var(--blue-dark);
        line-height: 1.4;
        margin: 0 0 18px 0;
        max-width: 780px;
    }
    .ps-intro-body {
        font-size: 13.5px;
        color: var(--muted);
        line-height: 1.8;
        max-width: 760px;
        border-top: 1px solid var(--border);
        padding-top: 16px;
        margin: 0;
    }
    .ps-intro-body b { color: var(--text); font-weight: 600; }

    /* ===== FORM CONTAINER ===== */
    .ps-form-wrap {
        background: var(--white);
        border: 1px solid var(--border);
        border-radius: var(--radius-lg);
        padding: 28px 32px 32px;
        margin-bottom: 24px;
    }
    .ps-form-title {
        font-size: 11px;
        font-weight: 700;
        color: var(--blue);
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin: 0;
        padding: 0;
    }
    .ps-divider {
        border: none;
        border-top: 1px solid var(--border);
        margin: 16px 0 22px 0;
    }

    /* ===== SECTION LABEL ===== */
    .ps-label {
        font-size: 10px;
        font-weight: 700;
        color: var(--blue);
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin: 22px 0 10px 0;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .ps-label::after {
        content: '';
        flex: 1;
        height: 1px;
        background: var(--border);
    }

    /* ===== RESULTS TITLE ===== */
    .ps-results-title {
        font-size: 11px;
        font-weight: 700;
        color: var(--blue);
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin: 30px 0 16px 0;
        padding-bottom: 10px;
        border-bottom: 2px solid var(--blue-light);
    }

    /* ===== STREAMLIT OVERRIDES ===== */
    .stRadio label { font-size: 13px !important; }
    .stSelectbox label, .stMultiSelect label,
    .stNumberInput label, .stTextArea label {
        font-size: 11px !important; font-weight: 700 !important;
        color: var(--muted) !important; text-transform: uppercase !important;
        letter-spacing: 0.06em !important;
    }
    .stSelectbox > div > div,
    .stMultiSelect > div > div {
        border: 1px solid var(--border) !important;
        border-radius: var(--radius) !important;
        font-size: 13px !important;
    }
    .stSelectbox > div > div:focus-within,
    .stMultiSelect > div > div:focus-within {
        border-color: var(--blue) !important;
        box-shadow: 0 0 0 2px rgba(0,91,172,0.12) !important;
    }

    /* ===== BUTTONS ===== */
    .stButton > button {
        font-family: 'IBM Plex Sans', sans-serif !important;
        font-weight: 600 !important;
        font-size: 13px !important;
        border-radius: var(--radius) !important;
        padding: 10px 22px !important;
        cursor: pointer !important;
        transition: all 0.15s ease !important;
        letter-spacing: 0.02em !important;
        background: var(--blue) !important;
        color: #FFFFFF !important;
        border: 1px solid var(--blue-dark) !important;
    }
    .stButton > button:hover {
        background: var(--blue-dark) !important;
        box-shadow: 0 3px 10px rgba(0,59,112,0.25) !important;
        transform: translateY(-1px) !important;
    }
    .stButton > button:active {
        transform: translateY(0) !important;
        box-shadow: none !important;
    }

    /* ===== METRIC CARD ===== */
    .metric-card {
        background: var(--white);
        border: 1px solid var(--border);
        border-radius: var(--radius);
        padding: 14px 16px;
    }
    .metric-card .metric-label {
        font-size: 10px; font-weight: 700;
        color: var(--muted); text-transform: uppercase;
        letter-spacing: 0.07em; margin-bottom: 5px;
    }
    .metric-card .metric-value {
        font-size: 18px; font-weight: 700;
        color: var(--blue-dark);
        font-family: 'IBM Plex Mono', monospace !important;
    }
    .metric-card .metric-sub {
        font-size: 10px; color: var(--muted); margin-top: 3px;
    }

    /* ===== SEUIL INFO ===== */
    .seuil-info-box {
        background: var(--blue-light);
        border: 1px solid #C2D9EF;
        border-left: 3px solid var(--blue);
        padding: 8px 12px;
        border-radius: var(--radius);
        margin: 4px 0 10px 0;
        font-size: 12px; color: var(--blue-dark); font-weight: 500;
    }

    /* ===== CARD ===== */
    .card {
        background: var(--bg); border: 1px solid var(--border);
        border-radius: var(--radius); padding: 16px 18px; margin-bottom: 12px;
    }
    .card h3 {
        font-size: 11px; font-weight: 700; color: var(--text);
        margin: 0 0 6px 0; text-transform: uppercase; letter-spacing: 0.05em;
    }
    .card p { font-size: 13px; color: var(--muted); line-height: 1.6; margin: 0; }

    /* ===== RESULT BOXES ===== */
    .result-box-securite  { background:#FFFBEB; border:1px solid #FCD34D; border-left:4px solid #D97706; padding:20px 22px; border-radius:var(--radius); margin-top:12px; }
    .result-box-secours   { background:var(--blue-light); border:1px solid #C2D9EF; border-left:4px solid var(--blue); padding:20px 22px; border-radius:var(--radius); margin-top:12px; }
    .result-box-tempszero { background:#FEF2F2; border:1px solid #FCA5A5; border-left:4px solid var(--danger); padding:20px 22px; border-radius:var(--radius); margin-top:12px; }
    .result-box-aucun     { background:var(--bg); border:1px solid var(--border); border-left:4px solid var(--muted); padding:20px 22px; border-radius:var(--radius); margin-top:12px; }
    .result-box-securite h3,.result-box-secours h3,.result-box-tempszero h3,.result-box-aucun h3 { font-size:14px; font-weight:700; color:var(--text); margin:0 0 10px 0; }
    .result-box-securite h4,.result-box-secours h4,.result-box-tempszero h4,.result-box-aucun h4 { font-size:10px; font-weight:700; color:var(--muted); margin:14px 0 5px 0; text-transform:uppercase; letter-spacing:0.07em; }
    .result-box-securite p,.result-box-secours p,.result-box-tempszero p,.result-box-aucun p { font-size:13px; color:var(--muted); line-height:1.65; margin:0 0 5px 0; }

    /* ===== BADGES ===== */
    .badge { display:inline-flex; align-items:center; padding:3px 10px; border-radius:4px; font-weight:700; font-size:10px; margin:0 5px 7px 0; letter-spacing:0.05em; text-transform:uppercase; }
    .badge-securite  { background:#FEF3C7; color:#92400E; border:1px solid #FCD34D; }
    .badge-secours   { background:var(--blue-light); color:var(--blue-dark); border:1px solid #C2D9EF; }
    .badge-tempszero { background:#FEE2E2; color:#991B1B; border:1px solid #FCA5A5; }
    .badge-aucun     { background:var(--bg); color:var(--muted); border:1px solid var(--border); }

    /* ===== MINI BADGES ===== */
    .mini-badge { display:inline-flex; align-items:center; padding:2px 9px; border-radius:4px; font-size:11px; font-weight:600; margin:2px 3px 3px 0; background:var(--bg); color:var(--muted); border:1px solid var(--border); font-family:'IBM Plex Mono',monospace !important; }

    /* ===== STATUS BOXES ===== */
    .warning-box  { background:#FFFBEB; border:1px solid #FCD34D; border-left:4px solid #D97706; padding:14px 18px; border-radius:var(--radius); margin:10px 0; }
    .warning-box h3 { font-size:13px; font-weight:700; color:#92400E; margin:0 0 5px 0; }
    .warning-box p  { font-size:13px; color:#78350F; margin:0; line-height:1.55; }

    .ups-box  { background:var(--blue-light); border:1px solid #C2D9EF; border-left:4px solid var(--cyan); padding:14px 18px; border-radius:var(--radius); margin:12px 0; }
    .ups-box h3 { font-size:13px; font-weight:700; color:var(--blue-dark); margin:0 0 5px 0; }
    .ups-box p  { font-size:13px; color:var(--blue-dark); margin:0; line-height:1.55; }

    .confirm-box { background:#F0FDF4; border:1px solid #86EFAC; border-left:4px solid var(--success); padding:16px 20px; border-radius:var(--radius); margin:12px 0; }
    .confirm-box h3 { font-size:13px; font-weight:700; color:#166534; margin:0 0 7px 0; }
    .confirm-box p  { font-size:13px; color:#15803D; margin:0 0 4px 0; line-height:1.55; }
    .confirm-box hr { border:none; border-top:1px solid #BBF7D0; margin:10px 0; }

    .lock-box { background:var(--bg); border:1px solid var(--border); border-left:4px solid var(--muted); padding:14px 18px; border-radius:var(--radius); margin:12px 0; }
    .lock-box h3 { font-size:13px; font-weight:700; color:var(--muted); margin:0 0 5px 0; }
    .lock-box p  { font-size:13px; color:var(--muted); margin:0; line-height:1.55; }

    .good-box { background:#F0FDF4; border:1px solid #86EFAC; border-left:4px solid var(--success); border-radius:var(--radius); padding:14px 18px; margin:10px 0; }
    .good-box h3 { font-size:13px; font-weight:700; color:#166534; margin:0 0 7px 0; }
    .good-box ul { margin:0; padding-left:18px; font-size:13px; color:#15803D; line-height:1.65; }

    .warn-box { background:#FFFBEB; border:1px solid #FCD34D; border-left:4px solid #D97706; border-radius:var(--radius); padding:14px 18px; margin:10px 0; }
    .warn-box h3 { font-size:13px; font-weight:700; color:#92400E; margin:0 0 5px 0; }
    .warn-box p  { font-size:13px; color:#78350F; margin:0; line-height:1.55; }

    .danger-box { background:#FEF2F2; border:1px solid #FCA5A5; border-left:4px solid var(--danger); border-radius:var(--radius); padding:14px 18px; margin:10px 0; }
    .danger-box h3 { font-size:13px; font-weight:700; color:#991B1B; margin:0 0 5px 0; }
    .danger-box p  { font-size:13px; color:#7F1D1D; margin:0; line-height:1.55; }

    .impossible-box { background:#FEF2F2; border:1px solid #FCA5A5; border-left:4px solid var(--danger); padding:14px 18px; border-radius:var(--radius); margin:10px 0; }
    .impossible-box h3 { font-size:13px; font-weight:700; color:#991B1B; margin:0 0 5px 0; }
    .impossible-box p  { font-size:13px; color:#7F1D1D; margin:0 0 4px 0; line-height:1.55; }

    .info-box { background:var(--blue-light); border:1px solid #C2D9EF; border-radius:var(--radius); padding:14px 18px; margin:14px 0; font-size:13px; color:var(--blue-dark); line-height:1.65; }
    .info-box b { color:var(--blue-dark); font-weight:700; }

    /* ===== TSE CARD ===== */
    .tse-card { background:var(--white); border:1px solid var(--border); border-top:3px solid var(--cyan); border-radius:var(--radius); padding:18px 20px; margin-bottom:12px; }
    .tse-title { font-size:20px; font-weight:700; color:var(--blue-dark); margin-bottom:3px; font-family:'IBM Plex Mono',monospace !important; }
    .tse-subtitle { font-size:13px; color:var(--muted); margin-bottom:10px; line-height:1.6; }

    /* ===== SCHEMA ===== */
    .schema-box { background:var(--blue-dark); color:#F8FAFC; border-radius:var(--radius); padding:16px 18px; margin-top:12px; }
    .schema-box h3 { font-size:11px; font-weight:700; color:#93C5FD; margin:0 0 10px 0; text-transform:uppercase; letter-spacing:0.07em; }
    .schema-bar { display:flex; height:28px; border-radius:4px; overflow:hidden; margin:6px 0; }
    .schema-src1 { background:#059669; text-align:center; line-height:28px; font-weight:700; font-size:11px; color:white; }
    .schema-off  { background:#D97706; text-align:center; line-height:28px; font-weight:700; font-size:11px; color:white; }
    .schema-src2 { background:#059669; text-align:center; line-height:28px; font-weight:700; font-size:11px; color:white; }
    .schema-sync { background:var(--cyan); text-align:center; line-height:28px; font-weight:700; font-size:11px; color:white; }
    .schema-box > div:last-child { font-size:11px; color:#93C5FD; margin-top:5px; }

    hr { border:none !important; border-top:1px solid var(--border) !important; margin:26px 0 !important; }
    .stAlert { border-radius:var(--radius) !important; font-size:13px !important; }
    div[data-testid="stMarkdownContainer"] h2 { font-size:14px !important; font-weight:700 !important; color:var(--blue) !important; margin:24px 0 12px 0 !important; padding-bottom:7px !important; border-bottom:1px solid var(--border) !important; text-transform:uppercase !important; letter-spacing:0.06em !important; }
    div[data-testid="stMarkdownContainer"] h3 { font-size:13px !important; font-weight:700 !important; color:var(--text) !important; margin:14px 0 7px 0 !important; }
    .small-note { font-size:11px; color:var(--muted); margin-top:4px; }
</style>
""", unsafe_allow_html=True)

# =========================================================
# STICKY HEADER
# =========================================================
st.markdown("""
<div class="ps-header">
    <div class="ps-header-accent"></div>
    <span class="ps-header-name">PowerSwitch Decision</span>
</div>
""", unsafe_allow_html=True)

# =========================================================
# INTRODUCTION
# =========================================================
st.markdown("""
<div class="ps-intro">
    <h1 class="ps-intro-title">Plateforme intelligente de sélection du groupe électrogène et de l'inverseur de source</h1>
    <p class="ps-intro-body">
        Aide à la décision conforme aux normes techniques et au règlement ERP pour le dimensionnement
        des systèmes de continuité électrique et la configuration optimale des transferts de sources.<br><br>
        <b>Objectif :</b> guider le choix du niveau de groupe électrogène puis de l'inverseur de source en tenant
        compte du type d'établissement, du niveau de continuité attendu, de la criticité des usages
        et des contraintes de disponibilité de l'installation.<br><br>
        <b>Références prises en compte :</b> exigences normatives, règlement ERP, continuité de service, sécurité des personnes.
    </p>
</div>
""", unsafe_allow_html=True)

# =========================================================
# FONCTION PDF — 100% Français, sans débordement
# =========================================================
def generer_pdf(entrees, resultats_groupe, resultats_inverseur):
    pdf = FPDF()
    pdf.set_margins(18, 18, 18)
    pdf.add_page()
    eff_w = pdf.w - 36  # effective width

    def safe(text):
        if not isinstance(text, str):
            text = str(text)
        text = re.sub(r'<b>|</b>|<br\s*/?>', ' ', text)
        text = re.sub(r'<[^>]+>', '', text)
        text = re.sub(r'\s+', ' ', text)
        replacements = {
            '\u2264': '<=', '\u2265': '>=', '\u00b2': '2', '\u00b3': '3',
            '\u2019': "'", '\u2018': "'", '\u201c': '"', '\u201d': '"',
            '\u2013': '-', '\u2014': '--', '\u2022': '-',
            '\u00e9': 'e', '\u00e8': 'e', '\u00ea': 'e', '\u00eb': 'e',
            '\u00e0': 'a', '\u00e2': 'a', '\u00e4': 'a',
            '\u00f4': 'o', '\u00f6': 'o', '\u00fb': 'u',
            '\u00fc': 'u', '\u00f9': 'u', '\u00ee': 'i', '\u00ef': 'i',
            '\u00e7': 'c', '\u00c9': 'E', '\u00c8': 'E', '\u00ca': 'E',
            '\u00c0': 'A', '\u00c2': 'A', '\u00d4': 'O', '\u00db': 'U',
            '\u00ce': 'I', '\u00c7': 'C',
        }
        for ch, rep in replacements.items():
            text = text.replace(ch, rep)
        return text.encode('latin-1', errors='replace').decode('latin-1').strip()

    def section_title(title):
        pdf.ln(5)
        pdf.set_fill_color(0, 91, 172)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Arial", "B", 10)
        pdf.cell(eff_w, 8, safe(title), ln=True, fill=True)
        pdf.set_text_color(31, 41, 55)
        pdf.ln(2)

    def field_row(label, value):
        pdf.set_font("Arial", "B", 8)
        pdf.set_text_color(107, 114, 128)
        pdf.cell(eff_w, 5, safe(label), ln=True)
        pdf.set_font("Arial", "", 10)
        pdf.set_text_color(31, 41, 55)
        pdf.multi_cell(eff_w, 5.5, safe(str(value)), 0, 'L')
        pdf.ln(2)

    # En-tete
    pdf.set_fill_color(0, 59, 112)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", "B", 15)
    pdf.cell(eff_w, 11, "PowerSwitch Decision", ln=True, fill=True, align="C")
    pdf.set_font("Arial", "", 9)
    pdf.cell(eff_w, 7, "Rapport d'etude de dimensionnement electrique", ln=True, fill=True, align="C")
    pdf.set_text_color(31, 41, 55)
    pdf.ln(2)
    pdf.set_font("Arial", "", 8)
    pdf.set_text_color(107, 114, 128)
    pdf.cell(eff_w, 5, safe(f"Genere le : {datetime.now().strftime('%d/%m/%Y a %H:%M')}"), ln=True, align="R")
    pdf.set_text_color(31, 41, 55)
    pdf.ln(4)

    section_title("1. Parametres d'entree")
    for k, v in entrees.items():
        field_row(k, v)

    section_title("2. Resultats — Groupe electrogene")
    for k, v in resultats_groupe.items():
        field_row(k, v)

    if resultats_inverseur:
        section_title("3. Resultats — Inverseur de source")
        for k, v in resultats_inverseur.items():
            field_row(k, v)

    pdf.ln(8)
    pdf.set_draw_color(217, 225, 232)
    pdf.line(pdf.l_margin, pdf.get_y(), pdf.w - pdf.r_margin, pdf.get_y())
    pdf.ln(4)
    pdf.set_font("Arial", "I", 8)
    pdf.set_text_color(107, 114, 128)
    note = (
        "Ce rapport constitue une aide a la decision fondee sur les normes techniques applicables "
        "et le reglement des ERP. La validation finale doit rester coherente avec l'etude detaillee "
        "du projet, les schemas retenus, les charges reellement secourues et les exigences specifiques de l'installation."
    )
    pdf.multi_cell(eff_w, 4.5, note, 0, 'L')

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        pdf.output(tmp.name)
        tmp_path = tmp.name
    with open(tmp_path, "rb") as f:
        data = f.read()
    b64 = base64.b64encode(data).decode()
    fname = f"rapport_powerswitch_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    href = (
        f'<a href="data:application/octet-stream;base64,{b64}" download="{fname}" '
        f'style="display:inline-flex;align-items:center;gap:8px;padding:10px 22px;'
        f'background:#005BAC;color:white;text-decoration:none;border-radius:6px;'
        f'font-weight:600;font-size:13px;font-family:IBM Plex Sans,sans-serif;">'
        f'Telecharger le rapport PDF</a>'
    )
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
    {"Famille":"Sécurité des personnes","Fonction":"Éclairage de sécurité","Niveau":"Sécurité","Reglementaire":"Oui","Commentaire":"","Critique_TZ_Local":False},
    {"Famille":"Sécurité des personnes","Fonction":"SSI / alarme incendie / CMSI / sonorisation d'évacuation","Niveau":"Sécurité","Reglementaire":"Oui","Commentaire":"","Critique_TZ_Local":False},
    {"Famille":"Sécurité des personnes","Fonction":"Désenfumage / extraction de fumées","Niveau":"Sécurité","Reglementaire":"Oui","Commentaire":"","Critique_TZ_Local":False},
    {"Famille":"Sécurité des personnes","Fonction":"Pompes incendie / surpresseurs incendie","Niveau":"Sécurité","Reglementaire":"Oui","Commentaire":"","Critique_TZ_Local":False},
    {"Famille":"Charges médicales / vitales","Fonction":"Bloc opératoire / réanimation / respirateurs / monitoring vital","Niveau":"Temps Zéro","Reglementaire":"Oui / très critique","Commentaire":"Charge critique nécessitant une continuité sans coupure.","Critique_TZ_Local":True},
    {"Famille":"Charges critiques exploitation","Fonction":"Serveurs critiques / contrôle-commande / supervision centrale","Niveau":"Temps Zéro","Reglementaire":"Selon usage","Commentaire":"Continuité sans interruption parfois nécessaire ; UPS locale recommandée hors MIL / AER.","Critique_TZ_Local":True},
    {"Famille":"Charges critiques exploitation","Fonction":"Tour de contrôle / balisage / fonctions aéroportuaires critiques","Niveau":"Temps Zéro","Reglementaire":"Oui selon fonction","Commentaire":"Très forte criticité fonctionnelle.","Critique_TZ_Local":True},
    {"Famille":"Exploitation","Fonction":"Froid / chambres froides / conservation","Niveau":"Secours","Reglementaire":"Non en général","Commentaire":"Continuité d'exploitation.","Critique_TZ_Local":False},
    {"Famille":"Exploitation","Fonction":"Ventilation utile / climatisation utile / process","Niveau":"Secours","Reglementaire":"Non en général","Commentaire":"Important pour exploitation ou confort technique.","Critique_TZ_Local":False},
    {"Famille":"Exploitation","Fonction":"Encaissement / informatique non vitale / exploitation bureautique","Niveau":"Secours","Reglementaire":"Non","Commentaire":"Continuité souhaitée sans être une fonction de sécurité.","Critique_TZ_Local":False},
    {"Famille":"Exploitation","Fonction":"Vidéosurveillance / sûreté / anti-intrusion","Niveau":"Secours","Reglementaire":"Selon site","Commentaire":"Peut être important sans relever systématiquement de la sécurité incendie.","Critique_TZ_Local":False},
]
df_fonctions = pd.DataFrame(FONCTIONS)

# =========================================================
# HELPERS
# =========================================================
def get_badge_html(type_groupe):
    tg = str(type_groupe).lower()
    if "temps zéro" in tg or "temps zero" in tg:
        return f'<span class="badge badge-tempszero">{type_groupe}</span>'
    elif "sécurité" in tg or "securite" in tg:
        return f'<span class="badge badge-securite">{type_groupe}</span>'
    elif "secours" in tg:
        return f'<span class="badge badge-secours">{type_groupe}</span>'
    return f'<span class="badge badge-aucun">{type_groupe}</span>'

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

def afficher_bloc_resultat(titre, type_groupe, details_erp, details_fonctions_sans_liste):
    badge_html = get_badge_html(type_groupe)
    result_class = get_result_box_class(type_groupe)
    explication = expliquer_groupe(type_groupe)
    avantages = avantages_groupe(type_groupe)
    titre_clean = titre.replace("⚡ ", "").replace("⚡", "")
    st.markdown(f"""
    <div class="{result_class}">
        <h3>{titre_clean}</h3>
        {badge_html}
        <p><b>Type de groupe retenu :</b> {type_groupe}</p>
        <p><b>Équipements concernés :</b> {equipements_selon_niveau(type_groupe)}</p>
        <h4>Justification</h4>
        <p>{explication}</p>
        <h4>Avantages</h4>
        <p>{avantages}</p>
        <h4>Analyse ERP</h4>
        <p>{details_erp}</p>
        <h4>Analyse des fonctions</h4>
        <p>{details_fonctions_sans_liste}</p>
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
    complements = []
    if inverseur_choisi['besoin_ups']:
        complements.append("UPS locale requise")
    if inverseur_choisi['besoin_sts']:
        complements.append("STS")
    complements_text = " + ".join(complements) if complements else "Aucun"
    st.markdown(f"""
    <div class="confirm-box">
        <h3>Synthèse finale de l'étude</h3>
        <p><b>Groupe électrogène retenu :</b> {groupe_choisi}</p>
        <p><b>Inverseur de source retenu :</b> {inverseur_choisi['type_inverseur']}</p>
        <p><b>Classe :</b> {inverseur_choisi['classe']} &nbsp;|&nbsp; <b>Commande :</b> {inverseur_choisi['mode_commande']}</p>
        <p><b>Transition :</b> {inverseur_choisi['transition']} &nbsp;|&nbsp; <b>Bypass :</b> {"Oui" if inverseur_choisi['bypass'] else "Non"}</p>
        <p><b>Compléments :</b> {complements_text}</p>
        <hr>
        <p>Cette configuration répond aux exigences réglementaires et fonctionnelles identifiées.</p>
    </div>
    """, unsafe_allow_html=True)

# =========================================================
# LOGIQUE METIER
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
        return 4, f"Effectif total ({effectif_total}) >= seuil 5e catégorie ({seuil})."
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
    elif "0 s < t" in temps_coupure and "10 s" in temps_coupure:
        score = max(score, NIVEAU_SCORE["Sécurité"])
        justification = "Une coupure très courte (0 s < t <= 10 s) impose au minimum un niveau Sécurité."
    elif "10 s < t" in temps_coupure and "15 s" in temps_coupure:
        score = max(score, NIVEAU_SCORE["Secours"])
        justification = "Une coupure courte (10 s < t <= 15 s) impose au minimum un niveau Secours."
    else:
        justification = "Une coupure longue (> 15 s) n'impose pas de niveau minimal particulier."
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
        remarque_ups = (
            "<b>Remarque importante :</b><br>"
            "Pour cet établissement, le <b>niveau global retenu reste Sécurité</b>.<br>"
            "La présence de charges critiques ou d'un besoin sans coupure ne conduit pas à classer tout le site en <b>Temps Zéro</b>.<br><br>"
            "<b>Solution recommandée :</b><br>"
            "• prévoir un <b>groupe électrogène de Sécurité</b> pour l'installation générale,<br>"
            "• ajouter des <b>UPS locales</b> au niveau des charges critiques ou non interruptibles."
        )
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
    if "> 15 s" in temps_coupure:
        niveau_recommande = "Aucun"
        justif_temps = "Une coupure longue admissible (> 15 s) n'impose pas de niveau minimal particulier."
    elif "10 s < t" in temps_coupure and "15 s" in temps_coupure:
        niveau_recommande = "Secours"
        justif_temps = "Une coupure courte admissible (10 s < t <= 15 s) conduit à recommander un groupe de Secours."
    elif "0 s < t" in temps_coupure and "10 s" in temps_coupure:
        niveau_recommande = "Sécurité"
        justif_temps = "Une coupure très courte admissible (0 s < t <= 10 s) conduit à recommander un groupe de Sécurité."
    elif "0 s" in temps_coupure:
        if code in TYPES_TEMPS_ZERO_GLOBAL:
            niveau_recommande = "Temps Zéro"
            justif_temps = "Aucune coupure admissible (0 s) : pour ce type d'établissement, la recommandation est Temps Zéro."
        else:
            niveau_recommande = "Sécurité"
            justif_temps = "Aucune coupure admissible (0 s) : la recommandation est Sécurité avec UPS / ASI séparée pour les charges non interruptibles."
            remarque_ups = "<b>Remarque :</b> le niveau global retenu reste <b>Sécurité</b>. Les charges sans coupure doivent être traitées par <b>UPS / ASI séparée</b>."
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
# INVERSEUR
# =========================================================
CRITICITE_SCORE = {"Vie humaine":3, "Dommages techniques / données":2, "Pertes financières / exploitation":1}

def criticite_dominante(criticites_selectionnees):
    if not criticites_selectionnees:
        return "Pertes financières / exploitation"
    max_score = 0
    dominante = "Pertes financières / exploitation"
    for c in criticites_selectionnees:
        score = CRITICITE_SCORE.get(c, 0)
        if score > max_score:
            max_score = score
            dominante = c
    return dominante

def recommander_inverseur(groupe_ge, coupure, transition, maintenance_sans_coupure,
                           criticites_selectionnees, mode_choix_inv,
                           inverseur_force=None, classe_force=None):
    notes = []
    architecture = []
    besoin_ups = False
    besoin_sts = False
    criticite = criticite_dominante(criticites_selectionnees)
    if len(criticites_selectionnees) > 1:
        notes.append(f"Plusieurs niveaux de criticité sélectionnés : {', '.join(criticites_selectionnees)}. Niveau dominant retenu : <b>{criticite}</b>.")

    if groupe_ge == "Temps Zéro":
        type_recommande = "ATSE"; commande = "Automatique"; classe = "PC"
        notes.append("Le niveau global confirmé est Temps Zéro : l'architecture doit viser une très haute continuité.")
        architecture.append("ATSE prioritaire"); architecture.append("Bypass fortement recommandé")
        besoin_ups = True
    elif groupe_ge == "Sécurité":
        type_recommande = "ATSE"; commande = "Automatique"; classe = "CB"
        notes.append("Le niveau global confirmé est Sécurité : le basculement automatique est à privilégier.")
        architecture.append("ATSE recommandé")
    elif groupe_ge == "Secours":
        type_recommande = "RTSE"; commande = "Télécommandée / automatique selon besoin"; classe = "CB"
        notes.append("Le niveau global confirmé est Secours : la continuité d'exploitation est recherchée sans exigence maximale systématique.")
        architecture.append("RTSE ou ATSE selon criticité")
    else:
        type_recommande = "MTSE"; commande = "Manuelle"; classe = "CC"
        notes.append("Aucune exigence forte globale n'est retenue à ce stade.")
        architecture.append("MTSE possible")

    if coupure == "< 50 ms":
        besoin_ups = True; besoin_sts = True
        type_recommande = "ATSE"; commande = "Automatique"; classe = "PC"
        notes.append("Une coupure < 50 ms ne peut pas être garantie par un inverseur mécanique seul. Une architecture complémentaire UPS / STS est nécessaire.")
    elif coupure == "50 ms à 2 s":
        if groupe_ge in ["Sécurité","Temps Zéro"]:
            type_recommande = "ATSE"; commande = "Automatique"
        elif groupe_ge == "Secours":
            type_recommande = "ATSE" if criticite in ["Vie humaine","Dommages techniques / données"] else "RTSE"
        else:
            type_recommande = "RTSE"
    else:
        if groupe_ge == "Temps Zéro":
            besoin_ups = True; type_recommande = "ATSE"; commande = "Automatique"
            notes.append("Même si la valeur saisie est > 2 s, le niveau Temps Zéro implique une architecture plus exigeante.")
        elif groupe_ge == "Sécurité":
            type_recommande = "ATSE"; commande = "Automatique"
        elif groupe_ge == "Secours":
            type_recommande = "RTSE"; commande = "Télécommandée"
        else:
            type_recommande = "MTSE"; commande = "Manuelle"

    transition_reelle = transition
    if transition == "Fermée (sans coupure)":
        type_recommande = "ATSE"; commande = "Automatique"; classe = "PC"
        notes.append("La transition fermée nécessite une synchronisation des sources. Réservée à des sources compatibles et des appareillages adaptés.")
    elif transition == "Statique":
        type_recommande = "ATSE"; commande = "Automatique"; classe = "PC"
        besoin_sts = True; besoin_ups = True
        notes.append("Le transfert statique relève d'une architecture STS / UPS, pas d'un simple inverseur mécanique.")
    elif transition == "Retardée (I-O-II)":
        notes.append("La transition retardée correspond au cas le plus courant en groupe électrogène.")
    else:
        notes.append("La transition ouverte implique une coupure franche lors du transfert.")

    bypass = False
    if maintenance_sans_coupure == "Oui":
        bypass = True
        if type_recommande != "ATSE":
            type_recommande = "ATSE"; commande = "Automatique"
            notes.append("Le besoin de maintenance sans coupure pousse vers un ATSE avec bypass.")
        architecture.append("Bypass de maintenance recommandé")

    if criticite == "Vie humaine":
        type_recommande = "ATSE"; commande = "Automatique"
        if transition in ["Fermée (sans coupure)","Statique"] or coupure == "< 50 ms":
            classe = "PC"
        notes.append("La criticité humaine impose une architecture de haute disponibilité.")
    elif criticite == "Dommages techniques / données":
        if coupure == "< 50 ms":
            besoin_ups = True; besoin_sts = True
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
        type_recommande = inverseur_force; classe = classe_force
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
        "type_inverseur": type_recommande, "mode_commande": commande,
        "classe": classe, "transition": transition_reelle, "bypass": bypass,
        "besoin_ups": besoin_ups, "besoin_sts": besoin_sts, "description": description,
        "notes": notes, "architecture": architecture, "alerte_manuel": alerte_manuel,
        "schema_html": schema_html, "criticites_selectionnees": criticites_selectionnees,
        "criticite_dominante": criticite,
    }

# =========================================================
# PARTIE 1 — FORMULAIRE (conteneur unifié)
# =========================================================
st.markdown('<div class="ps-form-wrap">', unsafe_allow_html=True)

# Titre du formulaire + bouton Réinitialiser en haut à droite
col_ftitle, col_freset = st.columns([8, 2])
with col_ftitle:
    st.markdown('<p class="ps-form-title">Étape 1 — Sélection du groupe électrogène</p>', unsafe_allow_html=True)
with col_freset:
    if st.button("↺ Réinitialiser", key="btn_reset"):
        for k in ["resultat_final","choix_confirme","groupe_confirme",
                  "inverseur_confirme","inverseur_final","choix_inverseur_resultat"]:
            st.session_state[k] = None if k not in ["choix_confirme","inverseur_confirme"] else False
        st.rerun()

st.markdown('<hr class="ps-divider">', unsafe_allow_html=True)

# Mode d'analyse
st.markdown('<p class="ps-label">Mode d\'analyse</p>', unsafe_allow_html=True)
mode_choix = st.radio(
    "mode", ["Détermination automatique améliorée", "Choix manuel contrôlé"],
    horizontal=True, label_visibility="collapsed"
)

if mode_choix == "Détermination automatique améliorée":
    st.markdown('<p class="ps-label">Identification de l\'établissement</p>', unsafe_allow_html=True)
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
            st.markdown(f'<div class="seuil-info-box">Effectif minimal valable pour ce type : <b>{effectif_min} personnes</b></div>', unsafe_allow_html=True)
            effectif_total = st.number_input("Effectif total admissible", min_value=0, step=1, value=0)

    effectif_invalide = (code not in TYPES_SPECIAUX) and (effectif_total == 0)
    if effectif_invalide:
        st.markdown('<div class="impossible-box"><h3>Effectif invalide — Analyse impossible</h3><p>Un effectif de <b>0</b> ne permet pas de réaliser une analyse réglementaire ERP. Veuillez saisir un effectif valable.</p></div>', unsafe_allow_html=True)
    else:
        categorie, justification_categorie = determiner_categorie_erp(code, effectif_total)
        st.markdown('<p class="ps-label">Fonctions à alimenter</p>', unsafe_allow_html=True)
        fonctions_selectionnees = st.multiselect(
            "Sélectionnez les fonctions / charges concernées",
            options=df_fonctions["Fonction"].tolist(),
            help="Plusieurs fonctions peuvent être retenues."
        )
        st.markdown('<p class="ps-label">Continuité admissible</p>', unsafe_allow_html=True)
        temps_coupure = st.radio(
            "Temps de coupure maximal admissible",
            ["Coupure longue admissible (> 15 s)",
             "Coupure courte admissible (10 s < t <= 15 s)",
             "Coupure très courte admissible (0 s < t <= 10 s)",
             "Aucune coupure admissible (0 s)"],
            label_visibility="collapsed"
        )
        st.markdown('<div style="margin-top:24px;"></div>', unsafe_allow_html=True)
        if st.button("Lancer la détermination automatique", use_container_width=True):
            niveau_final, justifs, niveau_erp_indicatif, niveau_fct, ups_local_requis = \
                niveau_final_automatique(code, fonctions_selectionnees, temps_coupure)
            st.session_state.resultat_final = {
                "mode": "Détermination automatique améliorée",
                "code": code, "erp_choice": erp_choice, "categorie": categorie,
                "justification_categorie": justification_categorie,
                "fonctions_selectionnees": fonctions_selectionnees,
                "temps_coupure": temps_coupure,
                "niveau_erp_indicatif": niveau_erp_indicatif,
                "niveau_fonctions": niveau_fct,
                "niveau_final": niveau_final,
                "details": justifs, "justification_libre": "",
                "ups_local_requis": ups_local_requis, "effectif_total": effectif_total
            }
            for k in ["choix_confirme","inverseur_confirme"]:
                st.session_state[k] = False
            for k in ["groupe_confirme","inverseur_final","choix_inverseur_resultat"]:
                st.session_state[k] = None

else:  # Manuel
    st.markdown('<p class="ps-label">Identification de l\'établissement</p>', unsafe_allow_html=True)
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
            st.markdown(f'<div class="seuil-info-box">Effectif minimal valable pour ce type : <b>{effectif_min} personnes</b></div>', unsafe_allow_html=True)
            effectif_total = st.number_input("Effectif total admissible", min_value=0, step=1, value=0, key="manual_eff")

    effectif_invalide = (code not in TYPES_SPECIAUX) and (effectif_total == 0)
    if effectif_invalide:
        st.markdown('<div class="impossible-box"><h3>Effectif invalide — Analyse impossible</h3><p>Un effectif de <b>0</b> ne permet pas de réaliser une analyse réglementaire ERP. Veuillez saisir un effectif valable.</p></div>', unsafe_allow_html=True)
    else:
        categorie, justification_categorie = determiner_categorie_erp(code, effectif_total)
        fonctions_selectionnees = []
        st.markdown('<p class="ps-label">Continuité admissible</p>', unsafe_allow_html=True)
        temps_coupure = st.radio(
            "Temps de coupure",
            ["Coupure longue admissible (> 15 s)",
             "Coupure courte admissible (10 s < t <= 15 s)",
             "Coupure très courte admissible (0 s < t <= 10 s)",
             "Aucune coupure admissible (0 s)"],
            key="manual_time", label_visibility="collapsed"
        )
        niveau_minimal, justifs, niveau_erp_indicatif, niveau_fct, ups_local_requis = \
            niveau_minimal_mode_manuel(code, temps_coupure)
        st.markdown(f'<div class="card"><h3>Référence minimale issue de l\'analyse</h3><p><b>Niveau minimal recommandé :</b> {niveau_minimal}</p><p class="small-note">Le choix manuel peut être égal ou supérieur à ce niveau.</p></div>', unsafe_allow_html=True)

        st.markdown('<p class="ps-label">Choix du niveau</p>', unsafe_allow_html=True)
        groupe_manuel = st.selectbox("Choisissez directement le niveau de groupe électrogène",
                                     ["Aucun", "Secours", "Sécurité", "Temps Zéro"])
        justification_client = st.text_area("Justification / remarque du client",
                                             placeholder="Exemple : le client impose un niveau supérieur pour des raisons d'exploitation critique.")

        if groupe_manuel == "Aucun":
            st.error("Vous devez sélectionner un groupe (Secours, Sécurité ou Temps Zéro) pour pouvoir valider.")
            valider_desactive = True
        else:
            conforme = verifier_choix_manuel(groupe_manuel, niveau_minimal)
            if conforme:
                st.success("Le choix manuel est cohérent avec le niveau minimal issu de l'analyse.")
            else:
                st.warning("Le choix manuel est inférieur au niveau minimal déduit de l'analyse.")
            valider_desactive = False

        st.markdown('<div style="margin-top:24px;"></div>', unsafe_allow_html=True)
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
                "details": justifs, "justification_libre": justification_client,
                "ups_local_requis": ups_local_requis, "effectif_total": effectif_total
            }
            for k in ["choix_confirme","inverseur_confirme"]:
                st.session_state[k] = False
            for k in ["groupe_confirme","inverseur_final","choix_inverseur_resultat"]:
                st.session_state[k] = None

st.markdown('</div>', unsafe_allow_html=True)  # ferme ps-form-wrap

# =========================================================
# RÉSULTATS — GROUPE
# =========================================================
if st.session_state.resultat_final is not None:
    r = st.session_state.resultat_final
    st.markdown('<p class="ps-results-title">Résultat — Groupe électrogène</p>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f'<div class="metric-card"><div class="metric-label">Code ERP</div><div class="metric-value">{r["code"]}</div><div class="metric-sub">{r["erp_choice"][:28]}</div></div>', unsafe_allow_html=True)
    with c2:
        val_cat = "N/A" if r["categorie"] is None else r["categorie"]
        st.markdown(f'<div class="metric-card"><div class="metric-label">Catégorie ERP</div><div class="metric-value">{val_cat}</div><div class="metric-sub">Calcul indicatif</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="metric-card"><div class="metric-label">Niveau ERP indicatif</div><div class="metric-value">{r["niveau_erp_indicatif"]}</div><div class="metric-sub">Plancher type ERP</div></div>', unsafe_allow_html=True)
    with c4:
        st.markdown(f'<div class="metric-card"><div class="metric-label">Niveau final retenu</div><div class="metric-value">{r["niveau_final"]}</div><div class="metric-sub">{r["mode"][:22]}</div></div>', unsafe_allow_html=True)

    st.markdown(f'<div class="card" style="margin-top:12px;"><h3>Justification catégorie ERP</h3><p>{r["justification_categorie"]}</p></div>', unsafe_allow_html=True)

    if r["mode"] == "Choix manuel contrôlé":
        afficher_bloc_resultat("Groupe retenu", r["niveau_final"], r['details']['erp'], r['details']['temps'])
    else:
        afficher_bloc_resultat("Groupe retenu", r["niveau_final"], r['details']['erp'], r['details']['fonctions'])

    if r["details"].get("remarque_ups"):
        st.markdown(f'<div class="ups-box"><h3>Remarque sur les charges critiques</h3><p>{r["details"]["remarque_ups"]}</p></div>', unsafe_allow_html=True)

    st.markdown('<p class="ps-label" style="margin-top:28px;">Confirmation de la partie 1</p>', unsafe_allow_html=True)
    st.info("Cliquez ci-dessous pour confirmer définitivement le groupe retenu et déverrouiller la partie 2.")

    if st.button("Confirmer le groupe et déverrouiller la partie 2", use_container_width=True):
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
# PARTIE 2 — INVERSEUR
# =========================================================
if st.session_state.get("choix_confirme", False) and st.session_state.get("groupe_confirme") is not None:
    st.markdown("---")
    st.markdown('<div class="ps-form-wrap">', unsafe_allow_html=True)
    st.markdown('<p class="ps-form-title">Étape 2 — Choix de l\'inverseur de source</p>', unsafe_allow_html=True)
    st.markdown('<hr class="ps-divider">', unsafe_allow_html=True)

    groupe_partie_1 = st.session_state.groupe_confirme

    st.markdown('<p class="ps-label">Mode et paramètres de l\'inverseur</p>', unsafe_allow_html=True)
    col_a, col_b = st.columns(2)
    with col_a:
        mode_inverseur = st.radio("Mode de choix de l'inverseur", ["Détermination automatique", "Choix manuel contrôlé"],
                                   horizontal=True, key="mode_inverseur")
        coupure_inv = st.selectbox("Temps de coupure admissible", ["< 50 ms", "50 ms à 2 s", "> 2 s"], index=1, key="coupure_inv")
        transition_inv = st.selectbox("Type de transition souhaité",
                                       ["Ouverte", "Retardée (I-O-II)", "Fermée (sans coupure)", "Statique"],
                                       index=1, key="transition_inv")
        maintenance_inv = st.radio("Maintenance sans coupure requise ?", ["Non", "Oui"], horizontal=True, key="maintenance_inv")
    with col_b:
        criticites_inv = st.multiselect(
            "Niveau de criticité (choix multiple possible)",
            options=["Vie humaine", "Dommages techniques / données", "Pertes financières / exploitation"],
            default=["Pertes financières / exploitation"],
            key="criticite_inv"
        )
        if len(criticites_inv) > 1:
            dominant = criticite_dominante(criticites_inv)
            st.markdown(f'<div class="seuil-info-box">Plusieurs criticités sélectionnées. Dominant : <b>{dominant}</b></div>', unsafe_allow_html=True)
        inverseur_force = None
        classe_force = None
        if mode_inverseur == "Choix manuel contrôlé":
            inverseur_force = st.selectbox("Forcer le type d'inverseur", ["MTSE", "RTSE", "ATSE"], key="inverseur_force")
            classe_force = st.selectbox("Forcer la classe", ["CC", "CB", "PC"], index=2, key="classe_force")

    st.markdown('<div style="margin-top:24px;"></div>', unsafe_allow_html=True)
    if st.button("Lancer la recommandation inverseur", use_container_width=True):
        if not criticites_inv:
            st.warning("Veuillez sélectionner au moins un niveau de criticité.")
        else:
            st.session_state.choix_inverseur_resultat = recommander_inverseur(
                groupe_ge=groupe_partie_1, coupure=coupure_inv, transition=transition_inv,
                maintenance_sans_coupure=maintenance_inv, criticites_selectionnees=criticites_inv,
                mode_choix_inv=mode_inverseur, inverseur_force=inverseur_force, classe_force=classe_force
            )
            st.session_state.inverseur_confirme = False
            st.session_state.inverseur_final = None

    st.markdown('</div>', unsafe_allow_html=True)

    if st.session_state.get("choix_inverseur_resultat") is not None:
        inv = st.session_state.choix_inverseur_resultat
        st.markdown('<p class="ps-results-title">Résultat — Inverseur de source</p>', unsafe_allow_html=True)

        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.markdown(f'<div class="metric-card"><div class="metric-label">Type d\'inverseur</div><div class="metric-value">{inv["type_inverseur"]}</div><div class="metric-sub">Recommandation</div></div>', unsafe_allow_html=True)
        with m2:
            cmd_short = inv["mode_commande"].split("/")[0].strip()[:14]
            st.markdown(f'<div class="metric-card"><div class="metric-label">Commande</div><div class="metric-value">{cmd_short}</div><div class="metric-sub">Mode de pilotage</div></div>', unsafe_allow_html=True)
        with m3:
            st.markdown(f'<div class="metric-card"><div class="metric-label">Classe</div><div class="metric-value">{inv["classe"]}</div><div class="metric-sub">Aide à la décision</div></div>', unsafe_allow_html=True)
        with m4:
            bypass_txt = "Oui" if inv["bypass"] else "Non"
            st.markdown(f'<div class="metric-card"><div class="metric-label">Bypass</div><div class="metric-value">{bypass_txt}</div><div class="metric-sub">Maintenance</div></div>', unsafe_allow_html=True)

        badges_html = render_inverseur_badges(inv)
        criticites_html = " ".join([f'<span class="mini-badge">{c}</span>' for c in inv.get("criticites_selectionnees", [])])
        if len(inv.get("criticites_selectionnees", [])) > 1:
            criticites_html += f'<br><span class="mini-badge" style="background:#FEF3C7;color:#92400E;border-color:#FCD34D;">Dominant : {inv.get("criticite_dominante","")}</span>'
        st.markdown(f'<div class="tse-card"><div class="tse-title">{inv["type_inverseur"]}</div><div class="tse-subtitle">{inv["description"]}</div>{badges_html}<div style="margin-top:8px;font-size:12px;"><b>Criticité(s) :</b> {criticites_html}</div></div>', unsafe_allow_html=True)

        if inv["notes"]:
            st.markdown('<div class="good-box"><h3>Pourquoi ce choix ?</h3><ul>' + "".join([f"<li>{n}</li>" for n in inv["notes"]]) + "</ul></div>", unsafe_allow_html=True)
        if inv["architecture"]:
            st.markdown('<div class="card"><h3>Architecture conseillée</h3><ul style="margin:0;padding-left:18px;font-size:13px;color:var(--muted);line-height:1.65;">' + "".join([f"<li>{a}</li>" for a in inv["architecture"]]) + "</ul></div>", unsafe_allow_html=True)

        st.markdown(f'<div class="schema-box"><h3>Schéma simplifié de transfert</h3>{inv["schema_html"]}</div>', unsafe_allow_html=True)

        if inv["besoin_ups"] or inv["besoin_sts"]:
            texte_archi = []
            if inv["besoin_ups"]: texte_archi.append("ajouter une UPS / ASI locale pour les charges non interruptibles")
            if inv["besoin_sts"]: texte_archi.append("prévoir une architecture STS pour les charges ultra-sensibles")
            st.markdown(f'<div class="warn-box"><h3>Complément d\'architecture requis</h3><p>{" ; ".join(texte_archi)}.</p></div>', unsafe_allow_html=True)

        if inv["alerte_manuel"]:
            st.markdown(f'<div class="danger-box"><h3>Alerte — Choix manuel</h3><p>{inv["alerte_manuel"]}</p></div>', unsafe_allow_html=True)

        st.markdown('<div style="margin-top:20px;"></div>', unsafe_allow_html=True)
        if st.button("Confirmer le choix de l'inverseur", use_container_width=True):
            st.session_state.inverseur_confirme = True
            st.session_state.inverseur_final = inv

        if st.session_state.get("inverseur_confirme", False) and st.session_state.get("inverseur_final") is not None:
            afficher_synthese_finale(st.session_state.groupe_confirme, st.session_state.inverseur_final)

            col_pdf1, col_pdf2, col_pdf3 = st.columns([1, 2, 1])
            with col_pdf2:
                if st.button("Exporter le rapport en PDF", use_container_width=True):
                    r = st.session_state.resultat_final
                    inv_f = st.session_state.inverseur_final
                    entrees = {
                        "Type ERP": r["erp_choice"],
                        "Effectif total": r.get("effectif_total", "Non renseigné"),
                        "Fonctions sélectionnées": ", ".join(r["fonctions_selectionnees"]) if r["fonctions_selectionnees"] else "Aucune",
                        "Temps de coupure": r["temps_coupure"],
                        "Mode d'analyse": r["mode"],
                    }
                    resultats_groupe = {
                        "Niveau retenu": r["niveau_final"],
                        "Justification ERP": r["details"]["erp"],
                        "Analyse": r["details"]["fonctions"] if r["mode"] != "Choix manuel contrôlé" else r["details"]["temps"],
                    }
                    resultats_inverseur = {
                        "Type d'inverseur": inv_f["type_inverseur"],
                        "Classe": inv_f["classe"],
                        "Mode de commande": inv_f["mode_commande"],
                        "Type de transition": inv_f["transition"],
                        "Bypass de maintenance": "Oui" if inv_f["bypass"] else "Non",
                        "UPS locale requise": "Oui" if inv_f["besoin_ups"] else "Non",
                        "Architecture STS": "Oui" if inv_f["besoin_sts"] else "Non",
                    }
                    href = generer_pdf(entrees, resultats_groupe, resultats_inverseur)
                    st.markdown(href, unsafe_allow_html=True)
                    st.success("Rapport PDF généré. Cliquez sur le lien ci-dessus pour le télécharger.")

else:
    st.markdown("---")
    st.markdown('<div class="warning-box"><h3>Partie 2 verrouillée</h3><p>Confirmez d\'abord le groupe électrogène en partie 1 pour activer le choix de l\'inverseur.</p></div>', unsafe_allow_html=True)

# =========================================================
# NOTE DE BAS DE PAGE
# =========================================================
st.markdown("""
<div class="info-box" style="margin-top:36px;">
    <b>Note importante :</b> cette interface constitue une <b>aide à la décision</b> fondée sur une logique construite
    dans le respect des normes techniques applicables et du règlement des ERP.
    La validation finale doit rester cohérente avec l'étude détaillée du projet, les schémas retenus,
    les charges réellement secourues et les exigences spécifiques de l'installation.
</div>
""", unsafe_allow_html=True)
