import streamlit as st
import pandas as pd
import os
import glob
import json
import re
import time
import sys
import math
import streamlit.components.v1 as components
from io import BytesIO
from PIL import Image, ImageDraw
from datetime import datetime, timezone
import plotly.express as px
import plotly.graph_objects as go
import pydeck as pdk
from google import genai
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.section import WD_ORIENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.opc.constants import RELATIONSHIP_TYPE

# --- App Configuration ---
st.set_page_config(page_title="SemicoN Dashboard", page_icon="logo.jpg", layout="wide", initial_sidebar_state="expanded")

MAINTENANCE_MODE = False
if MAINTENANCE_MODE:
    st.markdown("""<style>[data-testid="collapsedControl"], [data-testid="stSidebar"] { display: none; }</style>""", unsafe_allow_html=True)
    st.markdown("<div style='margin-top: 15vh;'></div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        try:
            st.image("logo.jpg", width=300)
        except:
            pass
        st.warning("⚠️ **Warning: Work in Progress.** Please wait, the Dashboard will be live soon.")
    st.stop()

# --- App Initialization & Folder Setup ---
os.makedirs('data', exist_ok=True)
os.makedirs('trash', exist_ok=True)

# ==========================================
# Consider moving this to an environment variable in the future: os.environ.get("MAPBOX_TOKEN")
MAPBOX_PUBLIC_TOKEN = "pk.eyJ1Ijoia2FzaGlmYW53YXIiLCJhIjoiY21td2loemd2Mm10MzJycXh4aTd1YjZtdCJ9.EN4o_kXPmA8ScOimJyf53A"
# ==========================================

# --- API Setup ---
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None
model_name = 'gemini-2.5-flash'

# --- Comprehensive Global ISO-3 & Regional Dictionary ---
COUNTRY_INFO = {
    "United States": ("USA", "Americas"), "USA": ("USA", "Americas"), "US": ("USA", "Americas"), "U.S.": ("USA", "Americas"),
    "Canada": ("CAN", "Americas"), "Mexico": ("MEX", "Americas"), "Brazil": ("BRA", "Americas"), "Argentina": ("ARG", "Americas"),
    "Chile": ("CHL", "Americas"), "Colombia": ("COL", "Americas"), "Peru": ("PER", "Americas"), "Venezuela": ("VEN", "Americas"), "Cuba": ("CUB", "Americas"),
    "United Kingdom": ("GBR", "Europe"), "UK": ("GBR", "Europe"), "U.K.": ("GBR", "Europe"), "Britain": ("GBR", "Europe"),
    "Germany": ("DEU", "Europe"), "France": ("FRA", "Europe"), "Italy": ("ITA", "Europe"), "Spain": ("ESP", "Europe"),
    "Netherlands": ("NLD", "Europe"), "Belgium": ("BEL", "Europe"), "Switzerland": ("CHE", "Europe"), "Poland": ("POL", "Europe"),
    "Sweden": ("SWE", "Europe"), "Norway": ("NOR", "Europe"), "Denmark": ("DNK", "Europe"), "Finland": ("FIN", "Europe"),
    "Ireland": ("IRL", "Europe"), "Russia": ("RUS", "Europe"), "Ukraine": ("UKR", "Europe"), "European Union": ("EU", "Europe"), "EU": ("EU", "Europe"),
    "Iran": ("IRN", "West Asia/Middle East"), "Israel": ("ISR", "West Asia/Middle East"), "Saudi Arabia": ("SAU", "West Asia/Middle East"),
    "United Arab Emirates": ("ARE", "West Asia/Middle East"), "UAE": ("ARE", "West Asia/Middle East"), "Qatar": ("QAT", "West Asia/Middle East"),
    "Oman": ("OMN", "West Asia/Middle East"), "Kuwait": ("KWT", "West Asia/Middle East"), "Bahrain": ("BHR", "West Asia/Middle East"),
    "Syria": ("SYR", "West Asia/Middle East"), "Iraq": ("IRQ", "West Asia/Middle East"), "Jordan": ("JOR", "West Asia/Middle East"),
    "Lebanon": ("LBN", "West Asia/Middle East"), "Yemen": ("YEM", "West Asia/Middle East"), "Turkey": ("TUR", "West Asia/Middle East"),
    "China": ("CHN", "Asia"), "Taiwan": ("TWN", "Asia"), "Japan": ("JPN", "Asia"), "South Korea": ("KOR", "Asia"), "North Korea": ("PRK", "Asia"),
    "India": ("IND", "Asia"), "Pakistan": ("PAK", "Asia"), "Bangladesh": ("BGD", "Asia"), "Sri Lanka": ("LKA", "Asia"),
    "Vietnam": ("VNM", "Asia"), "Malaysia": ("MYS", "Asia"), "Singapore": ("SGP", "Asia"), "Indonesia": ("IDN", "Asia"),
    "Philippines": ("PHL", "Asia"), "Thailand": ("THA", "Asia"), "Myanmar": ("MMR", "Asia"), "Cambodia": ("KHM", "Asia"),
    "South Africa": ("ZAF", "Africa"), "Egypt": ("EGY", "Africa"), "Nigeria": ("NGA", "Africa"), "Kenya": ("KEN", "Africa"),
    "Ethiopia": ("ETH", "Africa"), "Morocco": ("MAR", "Africa"), "Algeria": ("DZA", "Africa"), "Sudan": ("SDN", "Africa"),
    "Congo": ("COD", "Africa"), "Democratic Republic of the Congo": ("COD", "Africa"), "Angola": ("AGO", "Africa"), "Ghana": ("GHA", "Africa"),
    "Mali": ("MLI", "Africa"), "Niger": ("NER", "Africa"), "Chad": ("TCD", "Africa"), "Somalia": ("SOM", "Africa"),
    "Australia": ("AUS", "Oceania"), "New Zealand": ("NZL", "Oceania"), "Fiji": ("FJI", "Oceania"), "Papua New Guinea": ("PNG", "Oceania")
}

INFRASTRUCTURE_DATA = {
    "Semiconductor Fabs": [
        {"name": "TSMC - Gigafab 12 (Hsinchu, Taiwan)", "lat": 24.773, "lon": 121.011},
        {"name": "TSMC - Gigafab 18 (Tainan, Taiwan)", "lat": 23.113, "lon": 120.273},
        {"name": "TSMC - JASM (Kumamoto, Japan)", "lat": 32.883, "lon": 130.866},
        {"name": "TSMC - Fab 21 (Phoenix, USA)", "lat": 33.805, "lon": -112.148},
        {"name": "Samsung - Pyeongtaek Campus (South Korea)", "lat": 37.036, "lon": 127.042},
        {"name": "Samsung - Austin Fab (USA)", "lat": 30.368, "lon": -97.625},
        {"name": "Samsung - Taylor Fab [Under Construction] (USA)", "lat": 30.565, "lon": -97.409},
        {"name": "Intel - Ocotillo Campus (Chandler, USA)", "lat": 33.262, "lon": -111.862},
        {"name": "Intel - Ronler Acres (Hillsboro, USA)", "lat": 45.542, "lon": -122.923},
        {"name": "Intel - Fab 34 (Leixlip, Ireland)", "lat": 53.374, "lon": -6.502},
        {"name": "Intel - Magdeburg [Planned] (Germany)", "lat": 52.120, "lon": 11.627},
        {"name": "SMIC - SN1/SN2 (Shanghai, China)", "lat": 31.205, "lon": 121.597},
        {"name": "SMIC - B1/B2 (Beijing, China)", "lat": 39.805, "lon": 116.505},
        {"name": "GlobalFoundries - Fab 8 (Malta, USA)", "lat": 42.970, "lon": -73.754},
        {"name": "GlobalFoundries - Fab 1 (Dresden, Germany)", "lat": 51.125, "lon": 13.714},
        {"name": "GlobalFoundries - Singapore Campus", "lat": 1.436, "lon": 103.768},
        {"name": "UMC - Fab 12A (Tainan, Taiwan)", "lat": 23.115, "lon": 120.275},
        {"name": "Micron - Boise HQ & Fab (USA)", "lat": 43.535, "lon": -116.140},
        {"name": "Micron - Hiroshima Fab (Japan)", "lat": 34.238, "lon": 132.654},
        {"name": "Texas Instruments - Sherman Campus (USA)", "lat": 33.606, "lon": -96.611},
        {"name": "Tata & PSMC (Dholera)", "lat": 22.245, "lon": 72.195},
        {"name": "CG Power (Sanand) - ACTIVE", "lat": 23.005, "lon": 72.385},
        {"name": "Micron (Sanand) - ACTIVE", "lat": 22.956, "lon": 72.338},
        {"name": "Tower Semi (Panvel) - PLANNED", "lat": 18.989, "lon": 73.117},
        {"name": "ASML HQ (Netherlands)", "lat": 51.405, "lon": 5.405}
    ],
    "Critical Mineral Sites": [
        {"name": "Bayan Obo Mine [Largest REE] (China)", "lat": 41.796, "lon": 109.972},
        {"name": "Mountain Pass Mine [REE] (USA)", "lat": 35.473, "lon": -115.527},
        {"name": "Mount Weld Mine [REE] (Australia)", "lat": -28.775, "lon": 122.569},
        {"name": "Salar de Atacama [Lithium Triangle] (Chile)", "lat": -23.500, "lon": -68.250},
        {"name": "Mutanda Mine [Cobalt/Copper] (DRC)", "lat": -10.835, "lon": 25.795},
        {"name": "Kola Peninsula [Nickel/REE] (Russia)", "lat": 67.883, "lon": 33.000},
        {"name": "Manavalakurichi [Monazite (REEs)] (India)", "lat": 8.13, "lon": 77.30},
        {"name": "Chavara (Kollam) [REEs, Titanium] (India)", "lat": 9.01, "lon": 76.53}
    ],
    "Maritime Chokepoints": [
        {"name": "Strait of Malacca", "lat": 1.430, "lon": 103.264},
        {"name": "Strait of Hormuz", "lat": 26.566, "lon": 56.250},
        {"name": "Bab el-Mandeb (Red Sea)", "lat": 12.583, "lon": 43.333},
        {"name": "Suez Canal", "lat": 30.583, "lon": 32.333},
        {"name": "Panama Canal", "lat": 9.116, "lon": -79.750},
        {"name": "Taiwan Strait", "lat": 24.800, "lon": 119.900},
        {"name": "Bosphorus Strait", "lat": 41.221, "lon": 29.113}
    ],
    "Gulf FDI & Capital Diplomacy": [
        {"name": "Manara Minerals (Riyadh)", "lat": 24.7136, "lon": 46.6753},
        {"name": "ADQ Global Headquarters (Abu Dhabi)", "lat": 24.4539, "lon": 54.3773},
        {"name": "International Resources Holding (IRH)", "lat": 25.2048, "lon": 55.2708}
    ],
    "Naval Order of Battle & Strategic Bases": [
        {"name": "Naval Station Norfolk (USA)", "lat": 36.936, "lon": -76.326},
        {"name": "Naval Base San Diego (USA)", "lat": 32.673, "lon": -117.122},
        {"name": "Severomorsk (Russia) - Northern Fleet HQ", "lat": 69.070, "lon": 33.416},
        {"name": "US 7th Fleet HQ (Yokosuka, Japan)", "lat": 35.293, "lon": 139.661},
        {"name": "PLAN Southern Theater Command HQ (Zhanjiang, China)", "lat": 21.206, "lon": 110.402},
        {"name": "Andaman & Nicobar Command (India)", "lat": 11.666, "lon": 92.735},
        {"name": "INS Kadamba (Karwar, India)", "lat": 14.760, "lon": 74.137}
    ],
    "Aerospace & Space Force Installations": [
        {"name": "Cape Canaveral SFS / KSC (USA)", "lat": 28.488, "lon": -80.577},
        {"name": "Jiuquan Satellite Launch Center (China)", "lat": 40.960, "lon": 100.298},
        {"name": "Baikonur Cosmodrome (Kazakhstan)", "lat": 45.964, "lon": 63.305},
        {"name": "Satish Dhawan Space Centre (Sriharikota, India)", "lat": 13.719, "lon": 80.230}
    ]
}

# --- PURE PITCH BLACK CSS FIXES & MOBILE RESPONSIVENESS ---
st.markdown("""
<style>
    /* Force main app background to pure black */
    .stApp, .stAppViewContainer, .main .block-container { 
        background-color: #000000 !important; 
    }
    
    /* Ensure Header is transparent so Mobile Hamburger remains visible on black */
    header[data-testid="stHeader"] { 
        background-color: transparent !important; 
    }
    /* Force Hamburger icon to be white */
    [data-testid="collapsedControl"] svg { 
        color: #ffffff !important; 
    }
    
    /* NEW: Hide the Streamlit Running/Stop execution indicator */
    [data-testid="stStatusWidget"] {
        display: none !important;
    }

    /* NEW: Automatically handle iOS Notches and Android Punch Holes */
    .block-container {
        padding-top: max(1rem, env(safe-area-inset-top)) !important;
        padding-left: max(1rem, env(safe-area-inset-left)) !important;
        padding-right: max(1rem, env(safe-area-inset-right)) !important;
        margin-top: 0rem !important;
    }

    /* NEW: Make text adapt to small mobile screens (under 768px wide) */
    @media (max-width: 768px) {
        [data-testid="stMetricValue"] { font-size: 1.4rem !important; }
        h3 { font-size: 18px !important; }
    }
    
    [data-testid="stSidebar"] > div:first-child { padding-top: 0rem !important; }
    [data-testid="stSidebar"] { background-color: #000000 !important; border-right: 1px solid #222222 !important; } 
    [data-testid="stMetricValue"] { font-size: 1.8rem !important; font-weight: bold !important; color: #ffffff !important; }
    [data-testid="stMetricLabel"] { font-size: 1.0rem !important; white-space: normal !important; overflow: visible !important; height: auto !important; color: #aaaaaa !important; }
    footer { visibility: hidden; height: 0%; }
    h3 { margin-bottom: 0px !important; padding-bottom: 0px !important; }
    h4, h5 { margin-top: 0em !important; margin-bottom: 0.5em !important; }
    .stMarkdown p { margin-top: 5px !important; }
</style>
""", unsafe_allow_html=True)

def get_brief_mappings(directory):
    files = glob.glob(f'{directory}/brief_*.json')
    files.sort(reverse=True)
    mapping = {}
    for f in files:
        try:
            with open(f, 'r') as file:
                d = json.load(file)
                b_date = d.get('date', f.split('_')[1].split('.json')[0])
                display_name = f"SemicoN Weekly Brief - {b_date}"
                if display_name in mapping:
                    display_name = f"{display_name} (File: {f.split('_')[1].split('.json')[0]})"
                mapping[display_name] = f
        except: pass
    return mapping

def clean_dataframe(df):
    if df.empty: return df
    if 0 in df.columns: df = df.rename(columns={0: "Extracted Information"})
    if "0" in df.columns: df = df.rename(columns={"0": "Extracted Information"})
        
    cols_to_drop = [c for c in df.columns if "Unavailable" in str(c) or "None" in str(c)]
    df = df.drop(columns=cols_to_drop, errors='ignore')
    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].astype(str).str.strip()
            df[col] = df[col].replace({"None": "", "N/A": "", "NA": "", "N/a": "", "n/a": "", "none": "", "nan": "", "null": ""})
    return df

def render_highlighted_text(text, keyword):
    if not text: return ""
    clean_text = text.replace('$', r'\$') 
    if keyword and keyword != "All":
        sub_keywords = [k.strip() for k in re.split(r'&|/| and |,|;', keyword) if k.strip()]
        for sub_k in sub_keywords:
            pattern = re.compile(rf'\b({re.escape(sub_k)})\b', re.IGNORECASE)
            clean_text = pattern.sub(r'<span style="background-color: #ffeb3b; color: #000000; font-weight: bold; padding: 2px 4px; border-radius: 3px;">\1</span>', clean_text)
        st.markdown(clean_text, unsafe_allow_html=True)
    else:
        st.markdown(clean_text)

def add_hyperlink(paragraph, url, text):
    part = paragraph.part
    r_id = part.relate_to(url, RELATIONSHIP_TYPE.HYPERLINK, is_external=True)
    hyperlink = OxmlElement('w:hyperlink')
    hyperlink.set(qn('r:id'), r_id)
    new_run = OxmlElement('w:r')
    rPr = OxmlElement('w:rPr')
    c = OxmlElement('w:color')
    c.set(qn('w:val'), '0000EE')
    rPr.append(c)
    u = OxmlElement('w:u')
    u.set(qn('w:val'), 'single')
    rPr.append(u)
    new_run.append(rPr)
    text_node = OxmlElement('w:t')
    text_node.text = text
    new_run.append(text_node)
    hyperlink.append(new_run)
    paragraph._p.append(hyperlink)
    return hyperlink

def set_table_borders(table):
    tbl = table._tbl
    tblPr = tbl.tblPr
    tblBorders = tblPr.first_child_found_in("w:tblBorders")
    if tblBorders is not None: tblPr.remove(tblBorders)
    new_borders = OxmlElement('w:tblBorders')
    for border_name in ['top', 'left', 'bottom', 'right', 'insideH', 'insideV']:
        border = OxmlElement(f'w:{border_name}')
        border.set(qn('w:val'), 'single')
        border.set(qn('w:sz'), '24')
        border.set(qn('w:space'), '0')
        border.set(qn('w:color'), 'auto')
        new_borders.append(border)
    tblPr.append(new_borders)

def add_word_data_table(doc, heading_text, data_list):
    if not data_list: return
    safe_list = []
    for item in data_list:
        if isinstance(item, dict):
            safe_list.append(item)
        else:
            safe_list.append({"Extracted Information": str(item)})
            
    if not safe_list: return
    if len(safe_list) == 1 and "No " in str(list(safe_list[0].values())[0]): return
    
    p_heading = doc.add_paragraph()
    p_heading.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_heading.paragraph_format.line_spacing = 1.5
    p_heading.paragraph_format.space_before = Pt(6) 
    p_heading.paragraph_format.space_after = Pt(0) 
    r_head = p_heading.add_run(heading_text)
    r_head.bold = True
    r_head.font.name = 'Times New Roman'
    r_head.font.size = Pt(12)

    headers = list(safe_list[0].keys())
    table = doc.add_table(rows=1, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER 
    table.style = 'Table Grid'
    set_table_borders(table) 
    
    hdr_cells = table.rows[0].cells
    for i, h in enumerate(headers):
        hdr_cells[i].text = str(h)
        for p in hdr_cells[i].paragraphs:
            p.paragraph_format.space_after = Pt(0)
            for r in p.runs:
                r.font.name = 'Times New Roman'
                r.font.size = Pt(12)
                r.bold = True
                
    for item in safe_list:
        row_cells = table.add_row().cells
        for i, h in enumerate(headers):
            row_cells[i].text = str(item.get(h, ''))
            for p in row_cells[i].paragraphs:
                p.paragraph_format.space_after = Pt(0)
                for r in p.runs:
                    r.font.name = 'Times New Roman'
                    r.font.size = Pt(12)
    doc.add_paragraph() 

@st.cache_data
def create_landscape_word(text_sections, final_text, actions_data, brief_date, fund_data, market_data, risk_data, sources_data, text_ews):
    doc = Document()
    style = doc.styles['Normal']
    style.font.name = 'Times New Roman'
    style.font.size = Pt(12)
    style.paragraph_format.line_spacing = 1.5
    style.paragraph_format.space_after = Pt(0)
    style.paragraph_format.space_before = Pt(0)

    section = doc.sections[-1]
    section.orientation = WD_ORIENT.LANDSCAPE
    new_width, new_height = section.page_height, section.page_width
    section.page_width = new_width
    section.page_height = new_height
    
    header = section.header
    header.paragraphs[0].text = "" 
    r_head = header.paragraphs[0].add_run("Kashif Anwar, SemicoN Dashboard Brief")
    r_head.font.name = 'Times New Roman'
    r_head.font.size = Pt(11)
    header.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    footer = section.footer
    footer.paragraphs[0].text = ""
    r_foot = footer.paragraphs[0].add_run("Kashif Anwar, SemicoN Dashboard Brief")
    r_foot.font.name = 'Times New Roman'
    r_foot.font.size = Pt(11)
    footer.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER

    mast_table = doc.add_table(rows=1, cols=2)
    mast_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell_logo = mast_table.cell(0, 0)
    cell_logo.width = Inches(2.0)
    cell_text = mast_table.cell(0, 1)
    cell_text.width = Inches(6.0)
    cell_text.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
    
    p_logo = cell_logo.paragraphs[0]
    p_logo.alignment = WD_ALIGN_PARAGRAPH.CENTER
    try:
        img = Image.open("logo.jpg").convert("RGBA")
        min_dim = min(img.size)
        img = img.crop((0, 0, min_dim, min_dim))
        mask = Image.new('L', img.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, min_dim, min_dim), fill=255)
        result = Image.new('RGBA', img.size, (255, 255, 255, 0))
        result.paste(img, mask=mask)
        buf = BytesIO()
        result.save(buf, format="PNG")
        buf.seek(0)
        p_logo.add_run().add_picture(buf, width=Inches(1.5))
    except Exception: pass 
        
    p_text = cell_text.paragraphs[0]
    p_text.alignment = WD_ALIGN_PARAGRAPH.LEFT
    run_text = p_text.add_run("SemicoN Dashboard – A Semicon News Dashboard")
    run_text.font.name = 'Times New Roman'
    run_text.font.size = Pt(20)
    run_text.bold = True
    run_text.font.color.rgb = RGBColor(255, 0, 0) 
    doc.add_paragraph() 
    
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.line_spacing = 1.5
    p_title.paragraph_format.space_before = Pt(0)
    p_title.paragraph_format.space_after = Pt(12) 
    run_title = p_title.add_run(f'SemicoN Weekly Brief - {brief_date}')
    run_title.bold = True
    run_title.font.size = Pt(20)
    run_title.font.name = 'Times New Roman'
    
    p_author = doc.add_paragraph()
    p_author.paragraph_format.line_spacing = 1.5
    p_author.paragraph_format.space_before = Pt(0)
    p_author.paragraph_format.space_after = Pt(12)
    run_author = p_author.add_run("Prepared By: Kashif Anwar")
    run_author.bold = True
    run_author.font.size = Pt(12)
    run_author.font.name = 'Times New Roman'
    
    section_titles = [
        "Executive Summary",
        "Global Foundry Market & Geopolitical Positioning",
        "AI Chip Demand, Manufacturing & Processing",
        "Critical Minerals: Rare Earth Reserves & Supply Chains",
        "Export Controls & Geopolitical Impact",
        "AI, Chips and Rare Earth in Military and Outer Space Domain",
        "Lithography Chokepoints & State Actions",
        "India: Domestic & Strategic Developments",
        "West Asia/Middle East: Domestic & Strategic Developments"
    ]

    for i, text_data in enumerate(text_sections):
        
        if i == 0 and text_ews and text_ews.strip() != "":
            p_ews_head = doc.add_paragraph()
            p_ews_head.paragraph_format.space_before = Pt(12)
            r_ews_head = p_ews_head.add_run("🚨 Early Warning & Red Flags")
            r_ews_head.bold = True
            r_ews_head.font.color.rgb = RGBColor(255, 0, 0)
            r_ews_head.font.name = 'Times New Roman'
            r_ews_head.font.size = Pt(14)
            
            p_ews = doc.add_paragraph()
            r_ews = p_ews.add_run(text_ews)
            r_ews.font.name = 'Times New Roman'
            r_ews.font.size = Pt(12)
            
        if not text_data or text_data.strip() == "": continue

        p_head = doc.add_paragraph()
        p_head.paragraph_format.space_before = Pt(18)
        r_head = p_head.add_run(section_titles[i])
        r_head.bold = True
        r_head.font.name = 'Times New Roman'
        r_head.font.size = Pt(14)
        r_head.font.color.rgb = RGBColor(0, 102, 204)

        for line in text_data.split('\n'):
            line = line.strip()
            if not line: continue
            p = doc.add_paragraph()
            p.paragraph_format.line_spacing = 1.5
            p.paragraph_format.space_before = Pt(0)
            
            if line.startswith('**') and line.endswith('**'):
                p.paragraph_format.space_after = Pt(0)
                run = p.add_run(line.replace('**', ''))
                run.bold = True
                run.font.name = 'Times New Roman'
                run.font.size = Pt(12)
            elif line.startswith('* '):
                p.style = 'List Bullet'
                p.paragraph_format.space_after = Pt(12)
                run = p.add_run(line[2:].replace('**', ''))
                run.font.name = 'Times New Roman'
                run.font.size = Pt(12)
            else:
                p.paragraph_format.space_after = Pt(12)
                run = p.add_run(line.replace('**', ''))
                run.font.name = 'Times New Roman'
                run.font.size = Pt(12)
        
        if i == 1: add_word_data_table(doc, "Strategic Investments & Funding", fund_data)
        if i == 3: add_word_data_table(doc, "Market & Geopolitical Impact", market_data)
        if i == 4: add_word_data_table(doc, "Supply Chain Risk Analysis", risk_data)
                
    add_word_data_table(doc, 'Recent State Actions', actions_data)

    if final_text and final_text.strip() != "":
        p_head = doc.add_paragraph()
        p_head.paragraph_format.space_before = Pt(18)
        r_head = p_head.add_run("Strategic Conclusion")
        r_head.bold = True
        r_head.font.name = 'Times New Roman'
        r_head.font.size = Pt(14)
        r_head.font.color.rgb = RGBColor(0, 102, 204)

        for line in final_text.split('\n'):
            line = line.strip()
            if not line: continue
            p = doc.add_paragraph()
            p.paragraph_format.line_spacing = 1.5
            p.paragraph_format.space_before = Pt(0)
            
            if line.startswith('**') and line.endswith('**'):
                p.paragraph_format.space_after = Pt(0)
                run = p.add_run(line.replace('**', ''))
                run.bold = True
                run.font.name = 'Times New Roman'
                run.font.size = Pt(12)
            elif line.startswith('* '):
                p.style = 'List Bullet'
                p.paragraph_format.space_after = Pt(12)
                run = p.add_run(line[2:].replace('**', ''))
                run.font.name = 'Times New Roman'
                run.font.size = Pt(12)
            else:
                p.paragraph_format.space_after = Pt(12)
                run = p.add_run(line.replace('**', ''))
                run.font.name = 'Times New Roman'
                run.font.size = Pt(12)
                
    if sources_data:
        doc.add_paragraph() 
        p_source_head = doc.add_paragraph()
        p_source_head.paragraph_format.line_spacing = 1.5
        p_source_head.paragraph_format.space_before = Pt(12)
        r_source = p_source_head.add_run("Verified Intelligence Sources")
        r_source.bold = True
        r_source.font.name = 'Times New Roman'
        r_source.font.size = Pt(14)
        
        for src in sources_data:
            p_src = doc.add_paragraph()
            p_src.style = 'List Bullet'
            p_src.paragraph_format.space_after = Pt(6)
            p_src.paragraph_format.line_spacing = 1.0
            add_hyperlink(p_src, src['url'], src['title'])
            
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

def get_latest_file():
    if not os.path.exists('data'): return None
    files = glob.glob('data/brief_*.json')
    if not files: return None
    files.sort() 
    return files[-1]

latest_filepath = get_latest_file()

@st.cache_data(ttl=30) 
def load_data(filepath):
    if not filepath: return None
    with open(filepath, 'r') as f: return json.load(f)

dashboard_data = load_data(latest_filepath)

# ==========================================
# TEXT PARSER FOR RSS ACCUMULATOR FIX
# ==========================================
def parse_rss_txt_file():
    rss_dict = {}
    filepath = 'data/rss_accumulator.txt'
    if not os.path.exists(filepath): return rss_dict
    
    current_reg = None
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line.startswith("---") and "DOMAIN-FORCED NEWS" in line:
                reg = line.replace("---", "").replace("DOMAIN-FORCED NEWS", "").strip()
                if "Middle East" in reg: reg = "West Asia/Middle East"
                current_reg = reg
                if current_reg not in rss_dict:
                    rss_dict[current_reg] = []
            elif line.startswith("- [") and current_reg:
                try:
                    d_end = line.find("]")
                    date_str = line[3:d_end]
                    title_str = line[d_end+1:].strip()
                    
                    if not any(x['title'] == title_str for x in rss_dict[current_reg]):
                        rss_dict[current_reg].append({"title": title_str, "published": date_str, "link": "#"})
                except Exception: pass
    return rss_dict

def extract_tag(tag, text):
    match = re.search(rf'<{tag}>(.*?)</{tag}>', text, re.DOTALL | re.IGNORECASE)
    if match:
        clean_text = match.group(1).strip()
        clean_text = re.sub(r'</?[A-Z_]+>', '', clean_text)
        return clean_text
    return None

if dashboard_data:
    brief_date = dashboard_data.get('date', 'Latest Integration')
    raw_text = dashboard_data.get('brief_raw', '')
    t_sum = extract_tag('SUMMARY', raw_text)
    t_ews = extract_tag('EWS', raw_text)
    t1 = extract_tag('EXEC', raw_text)
    t2 = extract_tag('LITHO', raw_text)
    t3 = extract_tag('REE', raw_text)
    t4 = extract_tag('GEO', raw_text)
    t_mil = extract_tag('MILITARY', raw_text)
    t5 = extract_tag('CONCLUSION', raw_text)
    t_india = extract_tag('INDIA', raw_text)
    t_wa = extract_tag('WEST_ASIA', raw_text)
    t_fin = extract_tag('FINAL_CONCLUSION', raw_text)
    
    text_summary = t_sum or ""
    text_ews = t_ews or ""
    text_section_1 = t1 or ""
    text_section_2 = t2 or ""
    text_section_3 = t3 or ""
    text_section_4 = t4 or ""
    text_military = t_mil or ""
    text_section_5 = t5 or ""
    text_india = t_india or ""
    text_wa = t_wa or ""
    text_final = t_fin or ""
else:
    brief_date = "System Offline"
    raw_text = ""
    text_summary = text_ews = text_section_1 = text_section_2 = text_section_3 = text_section_4 = text_military = text_section_5 = text_india = text_wa = text_final = "Awaiting deployment of new intelligence brief."
    dashboard_data = {"supply_chain_risk": [{"Risk Factor": "No data"}], "recent_actions": [], "funding_data": [{"Entity": "No data"}], "market_impact": [{"Entity": "No data"}]}

# ==========================================
# NEW ALGORITHMIC THREAT SCORING FUNCTION
# ==========================================
def calculate_domain_threat(domain_name, text_content, dash_data):
    """
    Dynamically calculates a threat score (0-100) based on textual severity 
    and cross-referencing json data (risks & actions) without hardcoding values.
    """
    if not text_content or len(text_content.strip()) < 20:
        return 0
    
    score = 35 

    text_lower = text_content.lower()
    critical_keywords = ['ban', 'sanction', 'shortage', 'escalation', 'military', 'war', 'blockade', 'strike', 'chokepoint', 'threat', 'breach', 'crisis']
    high_keywords = ['tariff', 'control', 'restrict', 'vulnerability', 'disrupt', 'tension', 'export control', 'embargo', 'risk']
    medium_keywords = ['delay', 'subsidy', 'compete', 'invest', 'shift', 'policy', 'regulate', 'pressure', 'concern', 'geopolitical']

    score += sum(text_lower.count(kw) for kw in critical_keywords) * 8
    score += sum(text_lower.count(kw) for kw in high_keywords) * 5
    score += sum(text_lower.count(kw) for kw in medium_keywords) * 2

    domain_parts = [p.lower() for p in domain_name.replace(" / ", " ").split() if len(p) > 3]

    risks = dash_data.get('supply_chain_risk', [])
    for risk in risks:
        risk_text = str(risk).lower()
        if any(part in risk_text for part in domain_parts):
            score += 10 
    
    actions = dash_data.get('recent_actions', [])
    for action in actions:
        action_text = str(action).lower()
        if any(part in action_text for part in domain_parts):
            score += 5 

    return min(100, max(20, score))


# --- NEW CENTRALIZED LIVE ALERT FETCH FUNCTION ---
def get_active_live_alert():
    if not os.path.exists('data/live_alert.json'): 
        return None
    try:
        with open('data/live_alert.json', 'r') as f:
            alert = json.load(f)
        alert_time = datetime.fromisoformat(alert['timestamp'].replace("Z", "+00:00"))
        time_diff = datetime.now(timezone.utc) - alert_time
        
        if time_diff.total_seconds() < 7200: 
            return alert
    except Exception:
        pass 
    return None

def check_early_warnings():
    try:
        if st.session_state.get('role') == 'admin' and os.path.exists('data/live_alert.json'):
            if st.button("🛠️ Admin: Force Clear Live Alert (Resolve Stuck EWS)", type="primary"):
                try:
                    os.remove('data/live_alert.json')
                    st.success("Alert cleared! Refreshing...")
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to clear: {e}")

        alert = get_active_live_alert()
        
        box_bg_color = "#000000"
        nominal_text_color = "#d1d5db"
        
        if alert:  
            try:
                dt = datetime.fromisoformat(alert.get('timestamp', datetime.now(timezone.utc).isoformat()).replace("Z", "+00:00"))
                start_timestamp_ms = int(dt.timestamp() * 1000)
            except:
                start_timestamp_ms = int(time.time() * 1000)
            
            # --- RESPONSIVE DEFCON CSS FIX ---
            html_code = f"""
            <style>
                body {{ font-family: 'Courier New', Courier, monospace; margin: 0; padding: 0; background-color: {box_bg_color}; overflow: hidden; }}
                .defcon-box {{
                    background: linear-gradient(90deg, #8b0000 0%, #ff0000 50%, #8b0000 100%); 
                    background-size: 200% 200%; 
                    animation: pulseBackground 2s infinite; 
                    border: 2px solid #ff4b4b; 
                    padding: 15px; 
                    border-radius: 8px; 
                    box-shadow: 0 0 15px rgba(255, 0, 0, 0.5);
                    color: #ffffff;
                    min-height: 185px;
                    height: auto;
                    box-sizing: border-box;
                    overflow-y: auto; 
                }}
                :fullscreen {{
                    background-color: rgba(20, 20, 20, 0.95);
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }}
                :fullscreen .defcon-box {{ width: 90vw; max-height: 90vh; height: auto; padding: 40px; border-width: 4px; }}
                :fullscreen .title {{ font-size: 2.5em; }}
                :fullscreen .timer {{ font-size: 1.5em; }}
                :fullscreen .headline {{ font-size: 2em; line-height: 1.2; margin-top: 20px; }}
                :fullscreen .summary {{ font-size: 1.5em; line-height: 1.4; margin-top: 20px; }}
                
                @keyframes pulseBackground {{ 0% {{ background-position: 0% 50%; }} 50% {{ background-position: 100% 50%; }} 100% {{ background-position: 0% 50%; }} }}
                @keyframes blinkText {{ 0%, 100% {{ opacity: 1; }} 50% {{ opacity: 0; }} }}
                
                /* Responsive Flex Wrap Fix */
                .header-flex {{ display: flex; justify-content: space-between; align-items: center; margin-top: 0px; margin-bottom: 8px; flex-wrap: wrap; gap: 10px; }}
                .title {{ font-size: 1.17em; font-weight: bold; letter-spacing: 2px; text-transform: uppercase; margin:0; display:flex; align-items:center; flex: 1 1 100%; }}
                .timer-container {{ display: flex; align-items: center; flex: 1 1 100%; justify-content: flex-start; margin-bottom: 5px; }}
                
                @media (min-width: 600px) {{
                    .title {{ flex: 1; }}
                    .timer-container {{ flex: 1; justify-content: flex-end; margin-bottom: 0px; }}
                }}
                
                .timer {{ font-size: 15px; font-weight: bold; background: rgba(0,0,0,0.5); padding: 5px 10px; border-radius: 5px; border: 1px solid rgba(255,255,255,0.4); }}
                .headline {{ font-weight: 800; font-size: 16px; margin-bottom: 8px; margin-top:0; }}
                .summary {{ font-size: 14px; color: #f8f8f8; margin-bottom: 0px; border-top: 1px solid rgba(255,255,255,0.3); padding-top: 10px; }}
                
                .magnify-btn {{ background: rgba(0,0,0,0.6); color: white; border: 1px solid white; padding: 4px 8px; border-radius: 4px; cursor: pointer; font-size: 12px; font-weight: bold; margin-left: 10px; }}
                .magnify-btn:hover {{ background: rgba(255,255,255,0.2); }}
                :fullscreen .magnify-btn {{ display: none; }} 
                .close-btn {{ display: none; }}
                :fullscreen .close-btn {{ display: inline-block; background: transparent; color: white; border: 1px solid white; padding: 8px 16px; border-radius: 4px; cursor: pointer; font-size: 18px; margin-top: 20px; }}
            </style>
            
            <div class="defcon-box" id="defcon-container">
                <div class="header-flex">
                    <h3 class="title">
                        <span style="animation: blinkText 1s infinite; margin-right: 15px;">⚠️ DEFCON-LEVEL THREAT</span> 
                    </h3>
                    <div class="timer-container">
                        <div class="timer">Live Since: <span id="clock">00:00:00</span></div>
                        <button class="magnify-btn" onclick="toggleFullscreen()">🔍 MAGNIFY</button>
                    </div>
                </div>
                <p class="headline">{alert.get('headline', '')}</p>
                <p class="summary">{alert.get('summary', '')}</p>
                <button class="close-btn" onclick="document.exitFullscreen()">✖ CLOSE VIEW</button>
            </div>
            
            <script>
                function toggleFullscreen() {{
                    let elem = document.documentElement;
                    if (!document.fullscreenElement) {{
                        elem.requestFullscreen().catch(err => {{ alert(`Error: ${{err.message}}`); }});
                    }} else {{ document.exitFullscreen(); }}
                }}
                const start = {start_timestamp_ms};
                function update() {{
                    const now = new Date().getTime();
                    let diff = now - start;
                    if(diff < 0) diff = 0;
                    let h = Math.floor(diff / (1000 * 60 * 60));
                    let m = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
                    let s = Math.floor((diff % (1000 * 60)) / 1000);
                    document.getElementById('clock').innerText = String(h).padStart(2, '0') + ':' + String(m).padStart(2, '0') + ':' + String(s).padStart(2, '0');
                }}
                setInterval(update, 1000); update();
            </script>
            """
            components.html(html_code, height=260) 
            
        else:
            try:
                latest_time = os.path.getmtime("data/rss_accumulator.txt")
            except:
                latest_time = time.time()
                
            if latest_time < 1000000000: 
                latest_time = time.time()
                
            start_timestamp_ms = int(latest_time * 1000)

            # --- RESPONSIVE NOMINAL CSS FIX ---
            html_code = f"""
            <style>
                body {{ font-family: system-ui, -apple-system, sans-serif; margin: 0; padding: 0; background-color: {box_bg_color}; overflow: hidden; }}
                .nominal-box {{ background-color: rgba(0, 191, 255, 0.05); border-left: 5px solid #00bfff; padding: 15px; border-radius: 5px; min-height: 90px; height: auto; }}
                .header-flex {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; flex-wrap: wrap; gap: 8px; }}
                .title {{ color: #00bfff; margin: 0; font-size: 1.1em; font-weight: bold; display: flex; align-items: center; }}
                .timer {{ font-size: 13px; font-weight: bold; color: #00bfff; background: rgba(0, 191, 255, 0.1); padding: 5px 10px; border-radius: 4px; border: 1px solid rgba(0, 191, 255, 0.3); font-family: monospace; }}
                .desc {{ font-size: 14px; margin: 0; color: {nominal_text_color}; }}
            </style>
            <div class="nominal-box">
                <div class="header-flex">
                    <h4 class="title"><span>🟢 System Nominal</span></h4>
                    <div class="timer">Status Verified: <span id="clock">00:00:00</span> ago</div>
                </div>
                <p class="desc">Current Warning System doesn't see an early warning situation. Watch out for further updates.</p>
            </div>
            <script>
                const start = {start_timestamp_ms};
                function update() {{
                    const now = new Date().getTime();
                    let diff = now - start;
                    if(diff < 0) diff = 0;
                    let h = Math.floor(diff / (1000 * 60 * 60));
                    let m = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
                    let s = Math.floor((diff % (1000 * 60)) / 1000);
                    document.getElementById('clock').innerText = String(h).padStart(2, '0') + ':' + String(m).padStart(2, '0') + ':' + String(s).padStart(2, '0');
                }}
                setInterval(update, 1000); update();
            </script>
            """
            components.html(html_code, height=130)
    except Exception as e:
        pass 

# ==========================================
# LOGIN SCREEN 
# ==========================================
if 'role' not in st.session_state: st.session_state['role'] = None

if st.session_state['role'] is None:
    # --- BULLETPROOF RESPONSIVE SPLIT-SCREEN CSS ---
    st.markdown("""
    <style>
        /* Hide default Streamlit navigation */
        [data-testid="collapsedControl"], [data-testid="stSidebar"], header { display: none !important; }
        
        /* Widen the container for the split view on desktop */
        .block-container {
            padding-top: 5vh !important;
            max-width: 1000px !important;
        }

        /* Left Panel Styling */
        .left-panel-wrapper {
            background: linear-gradient(135deg, #0f172a, #1e293b, #020617);
            padding: 40px;
            border-radius: 12px;
            color: white;
            height: 100%;
            min-height: 480px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        }
        .left-panel-wrapper h1 { font-size: 2.8rem; font-weight: 300; line-height: 1.2; margin-bottom: 10px; }
        .left-panel-wrapper span { font-weight: 700; color: #facc15; }
        .left-panel-wrapper p { color: #94a3b8; font-size: 1.1rem; }

        /* Style the login button to match the yellow theme */
        .stButton>button[kind="primary"] { 
            width: 100%; 
            background-color: #facc15; 
            color: black; 
            font-weight: bold; 
            border: none; 
            margin-top: 10px;
            height: 45px;
        }
        .stButton>button[kind="primary"]:hover { background-color: #eab308; color: black; }
        .stButton>button[kind="secondary"] { width: 100%; font-weight: bold; height: 45px; }

        /* Desktop Fix: Vertically center the login form to balance the 50/50 split */
        div[data-testid="stColumn"]:nth-child(2) {
            display: flex;
            flex-direction: column;
            justify-content: center;
        }

        /* Mobile Rules: Aggressively override Streamlit's inline JS styles */
        @media screen and (max-width: 900px) {
            div[data-testid="stColumn"]:nth-child(1) {
                display: none !important;
                width: 0 !important;
                flex: 0 !important;
                height: 0 !important;
                opacity: 0 !important;
                overflow: hidden !important;
            }
            div[data-testid="stColumn"]:nth-child(2) {
                width: 100% !important;
                min-width: 100% !important;
            }
            .block-container { 
                max-width: 450px !important; 
                padding-top: 10vh !important; 
            }
            .left-panel-wrapper {
                display: none !important;
            }
        }
    </style>
    """, unsafe_allow_html=True)

    # Use a pure integer 2 for a mathematically perfect 50/50 split
    col_left, col_right = st.columns(2, gap="large")

    with col_left:
        # The visual gradient panel
        st.markdown("""
        <div class="left-panel-wrapper">
            <h1>Be a Part of<br>Something <span>Beautiful</span></h1>
            <p>Access the geopolitical and semiconductor geopolitical intelligence dashboard.</p>
        </div>
        """, unsafe_allow_html=True)

    with col_right:
        # The secure Python-backed login form
        st.markdown("<h2 style='margin-bottom: 5px; margin-top: 0px;'>Login</h2>", unsafe_allow_html=True)
        st.markdown("<p style='color: #aaa; font-size: 14px; margin-bottom: 20px;'>Enter your credentials</p>", unsafe_allow_html=True)
        
        with st.form("split_login_form"):
            email_input = st.text_input("Email", placeholder="analyst@agency.gov")
            password_input = st.text_input("Password", type="password", placeholder="Enter Secure Key")
            submit_login = st.form_submit_button("Login", type="primary")

            if submit_login:
                if email_input == "anwarkashif@outlook.com" and password_input == "NeverEstimateTheRahmat0fAllahSWT":
                    st.session_state['role'] = 'admin'
                    st.rerun()
                else: 
                    st.error("Invalid credentials.")
        
        if st.button("View as Guest", type="secondary"):
            st.session_state['role'] = 'guest'
            st.rerun()

# ==========================================
# MAIN DASHBOARD 
# ==========================================
else:
    # --- MOBILE SIDEBAR RESTORE FIX ---
    st.markdown("""<style>[data-testid="collapsedControl"] { display: block !important; } [data-testid="stSidebar"] { display: block !important; }</style>""", unsafe_allow_html=True)

    st.sidebar.image("logo.jpg", use_container_width=True)
    st.sidebar.markdown("""
    <div style='text-align: center; margin-top: -10px;'>
        <p style='font-size: 16px; font-weight: bold; margin-bottom: 5px;'>A Semicon News Dashboard.</p>
        <p style='font-size: 14px; margin-bottom: 5px;'>Prepared by: Kashif Anwar</p>
        <p style='font-size: 13px; color: #00bfff; font-weight: bold; font-style: italic; margin-bottom: 0px;'>A Human-AI Vetted Dashboard</p>
    </div>
    """, unsafe_allow_html=True)
    st.sidebar.markdown("---")
    
    st.sidebar.markdown("<p style='font-size: 16px; font-weight: bold; margin-bottom: 5px;'>Global Filter</p>", unsafe_allow_html=True)
    actor_list = []
    
    df_actions = clean_dataframe(pd.DataFrame(dashboard_data.get('recent_actions', [])))
    
    if not df_actions.empty and 'Actor' in df_actions.columns:
        actor_list = [a for a in df_actions['Actor'].dropna().unique().tolist() if str(a).strip()]
    
    selected_actor = st.sidebar.selectbox("🔍 Highlight & Filter by Actor:", ["All"] + sorted(actor_list))
    st.sidebar.markdown("---")

    st.sidebar.markdown("<p style='font-size: 16px; font-weight: bold; margin-bottom: 5px;'>Advanced Threat Tools</p>", unsafe_allow_html=True)
    advanced_tool = st.sidebar.radio(
        "Launch Sandbox Module:", 
        ["None (View Main Dashboard)", "Quantitative Threat Scoring", "Intelligence Interrogation (RAG)"], 
        index=0
    )
    st.sidebar.markdown("---")

    st.sidebar.markdown("<p style='font-size: 16px; font-weight: bold; margin-bottom: 5px;'>Regions Covered</p>", unsafe_allow_html=True)
    
    region_checks = {
        "Asia": ["**Asia:**", text_india], 
        "Middle East/West Asia": ["**Middle East/West Asia:**", text_wa],
        "Africa": ["**Africa:**"],
        "Europe": ["**Europe:**"],
        "Americas": ["**Americas:**"],
        "Oceania": ["**Oceania:**"]
    }
    
    for r, indicators in region_checks.items():
        is_covered = False
        for ind in indicators:
            if ind and len(ind.strip()) > 5: 
                is_covered = True
            elif ind in raw_text: 
                is_covered = True
                
        if is_covered:
            st.sidebar.markdown(f"✅ {r}")
        else:
            st.sidebar.markdown(f"➖ <span style='color:grey'>{r}</span>", unsafe_allow_html=True)
            
    st.sidebar.markdown("---")
    with st.sidebar.expander("🧠 Key Concepts Explained"):
        st.markdown("""
        **EUV Lithography:** Extreme Ultraviolet Lithography. The cutting-edge tech used to print the most advanced microchips.  
        **Tape-out:** The final design phase for integrated circuits before manufacturing begins.  
        **Foundry:** A specialized factory where semiconductor chips are manufactured (e.g., TSMC).  
        **Rare Earth Elements (REEs):** 17 metallic elements crucial for high-tech, defense, and green energy products.  
        **Fabless:** Companies that design chips but outsource manufacturing (e.g., Nvidia, Apple, AMD).
        """)

    st.sidebar.markdown("---")
    st.sidebar.title("SemicoN Access")

    if st.session_state['role'] == 'admin':
        st.sidebar.info("Access Level: **Administrator**")
        if st.sidebar.button("Logout"):
            st.session_state['role'] = None
            st.rerun()
        view_options = ["Weekly Intelligence Brief", "Trend Timelines", "Archives", "Clean Archives", "Trash"]
    else:
        st.sidebar.info("Access Level: **Guest Viewer**")
        st.sidebar.caption("*(System Access Restricted)*")
        view_options = ["Weekly Intelligence Brief", "Trend Timelines", "Archives"]

    st.sidebar.markdown("---")
    view_selection = st.sidebar.radio("Select View:", view_options)

    if advanced_tool == "Quantitative Threat Scoring":
        st.title("Quantitative Threat Scoring")
        st.markdown("Algorithmic ranking of regional supply chain vulnerability based on historical archive data.")
        
        archive_mapping = get_brief_mappings('data')
        if archive_mapping:
            scoring_data = {}
            for f_path in archive_mapping.values():
                try:
                    with open(f_path, 'r') as file:
                        d = json.load(file)
                        actions = d.get('recent_actions', [])
                        
                        for action in actions:
                            loc = str(action.get('Location', '')).strip()
                            if loc and loc != "Global":
                                for country, data_tuple in COUNTRY_INFO.items():
                                    if country.lower() in loc.lower():
                                        region = data_tuple[1]
                                        scoring_data[region] = scoring_data.get(region, 0) + 1
                                        break
                except: pass
            
            if scoring_data:
                score_df = pd.DataFrame(list(scoring_data.items()), columns=["Region", "Instability Actions Logged"])
                score_df = score_df.sort_values(by="Instability Actions Logged", ascending=False).reset_index(drop=True)
                
                def assign_threat(score):
                    if score > 10: return "🔴 Critical"
                    elif score > 5: return "🟠 High"
                    elif score > 2: return "🟡 Elevated"
                    else: return "🟢 Standard"
                    
                score_df["Calculated Threat Level"] = score_df["Instability Actions Logged"].apply(assign_threat)
                
                st.table(score_df.set_index(score_df.columns[0]))
            else:
                st.warning("Not enough historical data to generate scores yet.")
        else:
            st.warning("No archives available.")
            
        st.stop() 
        
    elif advanced_tool == "Intelligence Interrogation (RAG)":
        st.title("Intelligence Interrogation (RAG)")
        st.markdown("Query the historical SemicoN database. Responses are generated strictly from your vetted archives.")

        if not client:
            st.error("⚠️ GEMINI_API_KEY is missing from Koyeb Environment Variables. Please add it to unlock this feature.")
            st.stop()

        if "rag_messages" not in st.session_state:
            st.session_state.rag_messages = []

        for message in st.session_state.rag_messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if prompt := st.chat_input("Ask a strategic question (e.g., 'What were the major export controls on China last month?'):"):
            st.session_state.rag_messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                message_placeholder.markdown("Scanning intelligence archives & calculating threat models... 🕵️‍♂️")

                archive_mapping = get_brief_mappings('data')
                context_data = ""
                
                # --- RAG 2.0 CONTEXT BUILDER (OPTIMIZED FOR SPEED & ACCURACY) ---
                user_keywords = [w.lower() for w in re.findall(r'\b\w+\b', prompt) if len(w) > 2 and w.lower() not in ['what', 'when', 'where', 'which', 'who', 'why', 'how', 'were', 'was', 'this', 'that', 'with', 'from', 'about', 'the', 'and', 'for', 'are', 'did', 'have', 'has']]

                file_scores = []
                for f_path in archive_mapping.values():
                    try:
                        with open(f_path, 'r') as file:
                            d = json.load(file)
                            content = d.get('brief_raw', '').lower() + json.dumps(d.get('recent_actions', [])).lower()
                            score = sum(content.count(kw) for kw in user_keywords)
                            file_scores.append((score, f_path))
                    except: pass

                # Sort files by relevance score
                file_scores.sort(key=lambda x: x[0], reverse=True)

                # Pick top 3 most relevant files, fallback to latest 2 if no keywords match
                top_files = [fs[1] for fs in file_scores if fs[0] > 0][:3]
                if not top_files:
                    top_files = list(archive_mapping.values())[:2]
                
                for f_path in top_files:
                    try:
                        with open(f_path, 'r') as file:
                            d = json.load(file)
                            r_text = d.get('brief_raw', '')
                            
                            categories = [
                                ("Global Foundry Market", extract_tag('EXEC', r_text) or ""),
                                ("AI Chip Demand", extract_tag('LITHO', r_text) or ""),
                                ("Critical Minerals (REE)", extract_tag('REE', r_text) or ""),
                                ("Export Controls", extract_tag('GEO', r_text) or ""),
                                ("Military & Outer Space", extract_tag('MILITARY', r_text) or ""),
                                ("India Developments", extract_tag('INDIA', r_text) or ""),
                                ("West Asia / Middle East", extract_tag('WEST_ASIA', r_text) or "")
                            ]
                            
                            context_data += f"\n\n--- INTELLIGENCE BRIEF DATE: {d.get('date', 'Unknown')} ---\n"
                            context_data += "ALGORITHMIC THREAT SCORES:\n"
                            
                            for name, txt in categories:
                                if len(txt.strip()) > 20:
                                    score = calculate_domain_threat(name, txt, d)
                                    context_data += f"- {name}: {score}%\n"
                                    
                            context_data += "\nRAW INTELLIGENCE TEXT:\n"
                            context_data += r_text
                            context_data += f"\nLOGGED STATE ACTIONS:\n{json.dumps(d.get('recent_actions', []))}"
                    except: pass

                # --- RAG 2.0 SYSTEM PROMPT ---
                sys_prompt = f"""
                You are an elite geopolitical intelligence AI assistant for the SemicoN Dashboard.
                Your primary directive is to answer the user's question using ONLY the provided historical intelligence archives below.
                
                CRITICAL RAG 2.0 DIRECTIVE: You now have access to the "Algorithmic Threat Scores" (0-100%) calculated for each domain.
                - Scores > 60% indicate High Volatility/Threat environments.
                - Scores < 40% indicate standard baseline risk.
                When analyzing threats, vulnerabilities, or risks, explicitly cite these Algorithmic Threat Scores to ground your reasoning in the quantitative data model.
                
                If the answer is not present in the context, explicitly state: "I cannot find this information in the vetted intelligence archives."
                Format your responses in a structured, highly analytical style. Use structured comparative tables if you are summarizing multiple actors, dates, or data points. Do NOT invent or hallucinate external information.
                
                ARCHIVES CONTEXT:
                {context_data}
                """
                
                try:
                    full_response = ""
                    response = client.models.generate_content_stream(
                        model=model_name,
                        contents=[sys_prompt, prompt]
                    )
                    for chunk in response:
                        if chunk.text:
                            full_response += chunk.text
                            message_placeholder.markdown(full_response + "▌") 
                            
                    message_placeholder.markdown(full_response)
                except Exception as e:
                    full_response = f"⚠️ Error querying the intelligence database: {e}"
                    message_placeholder.markdown(full_response)
            st.session_state.rag_messages.append({"role": "assistant", "content": full_response})
            
        st.stop() 

    if view_selection == "Weekly Intelligence Brief":
        is_editing = st.session_state.get('vetting_toggle', False)
            
        if is_editing and st.session_state['role'] == 'admin':
            st.warning("You are currently in Edit Mode. Changes made here will be permanently written to the intelligence database.")
            with st.form("editor_form"):
                st.markdown("### Edit Intelligence Text")
                new_sum = st.text_area("Executive Summary", text_summary, height=150)
                new_ews = st.text_area("Early Warning & Red Flags", text_ews, height=100)
                new_s1 = st.text_area("Global Foundry Market", text_section_1, height=150)
                new_s2 = st.text_area("AI Chip Demand", text_section_2, height=100)
                new_s3 = st.text_area("Critical Minerals", text_section_3, height=100)
                new_s4 = st.text_area("Export Controls", text_section_4, height=100)
                new_mil = st.text_area("Military & Outer Space", text_military, height=100)
                new_s5 = st.text_area("Lithography Chokepoints", text_section_5, height=150)
                new_india = st.text_area("India: Domestic & Strategic Developments", text_india, height=150)
                new_wa = st.text_area("West Asia: Domestic & Strategic Developments", text_wa, height=150)
                new_fin = st.text_area("Strategic Conclusion", text_final, height=150)
                
                st.markdown("### Edit Data Tables & KPIs")
                
                edited_kpi_df = st.data_editor(clean_dataframe(pd.DataFrame(dashboard_data.get('kpi_metrics', []))), num_rows="dynamic", use_container_width=True)
                edited_funding_df = st.data_editor(clean_dataframe(pd.DataFrame(dashboard_data.get('funding_data', []))), num_rows="dynamic", use_container_width=True)
                edited_market_df = st.data_editor(clean_dataframe(pd.DataFrame(dashboard_data.get('market_impact', []))), num_rows="dynamic", use_container_width=True)
                edited_risk_df = st.data_editor(clean_dataframe(pd.DataFrame(dashboard_data.get('supply_chain_risk', []))), num_rows="dynamic", use_container_width=True)
                edited_actions_df = st.data_editor(clean_dataframe(pd.DataFrame(dashboard_data.get('recent_actions', []))), num_rows="dynamic", use_container_width=True)
                
                if st.form_submit_button("💾 Save Vetted Intelligence"):
                    
                    clean_kpi = edited_kpi_df.fillna("")
                    clean_actions = edited_actions_df.fillna("")
                    clean_fund = edited_funding_df.fillna("")
                    clean_market = edited_market_df.fillna("")
                    clean_risk = edited_risk_df.fillna("")
                    
                    kpi_json = clean_kpi.to_json(orient='records')
                    matrix_json = clean_actions.to_json(orient='records')
                    fund_json = clean_fund.to_json(orient='records')
                    market_json = clean_market.to_json(orient='records')
                    risk_json = clean_risk.to_json(orient='records')
                    
                    new_raw = f"<SUMMARY>\n{new_sum}\n</SUMMARY>\n\n<EWS>\n{new_ews}\n</EWS>\n\n<EXEC>\n{new_s1}\n</EXEC>\n\n<LITHO>\n{new_s2}\n</LITHO>\n\n<REE>\n{new_s3}\n</REE>\n\n<GEO>\n{new_s4}\n</GEO>\n\n<MILITARY>\n{new_mil}\n</MILITARY>\n\n<CONCLUSION>\n{new_s5}\n</CONCLUSION>\n\n<INDIA>\n{new_india}\n</INDIA>\n\n<WEST_ASIA>\n{new_wa}\n</WEST_ASIA>\n\n<FINAL_CONCLUSION>\n{new_fin}\n</FINAL_CONCLUSION>\n\n<KPI_METRICS>{kpi_json}</KPI_METRICS>\n<FUNDING_DATA>{fund_json}</FUNDING_DATA>\n<MARKET_IMPACT>{market_json}</MARKET_IMPACT>\n<RISK_INDEX>{risk_json}</RISK_INDEX>\n<ACTION_MATRIX>{matrix_json}</ACTION_MATRIX>"
                    
                    dashboard_data['brief_raw'] = new_raw
                    dashboard_data['kpi_metrics'] = clean_kpi.to_dict(orient='records')
                    dashboard_data['recent_actions'] = clean_actions.to_dict(orient='records')
                    dashboard_data['funding_data'] = clean_fund.to_dict(orient='records')
                    dashboard_data['market_impact'] = clean_market.to_dict(orient='records')
                    dashboard_data['supply_chain_risk'] = clean_risk.to_dict(orient='records')
                    
                    if latest_filepath:
                        with open(latest_filepath, 'w') as f:
                            json.dump(dashboard_data, f)
                        
                    st.cache_data.clear() 
                    st.success("Changes permanently saved! Refreshing system...")
                    time.sleep(1)
                    st.rerun() 
            
            st.markdown("<br>", unsafe_allow_html=True)
            st.toggle("✏️ Enable Human-AI Vetting Mode (Edit Text & Data)", key="vetting_toggle")

        else:
            st.title(f"SemicoN Weekly Brief - {brief_date}") 
            st.markdown("---")
            
            current_day = datetime.now(timezone.utc).astimezone().strftime('%B %d, %Y')
            st.markdown(f"<h3 style='color:#ff4b4b; margin-top: 10px; margin-bottom: 10px;'>🛡️ Strategic Threat Monitor ({current_day})</h3>", unsafe_allow_html=True)
            
            check_early_warnings()

            # --- PLOTLY CONCENTRIC RING WHEEL IMPLEMENTATION ---
            st.markdown("<h3 style='color:#00bfff; font-size:22px; margin-top: 30px; margin-bottom: 10px;'>Semicon, Rare Earth and AI Geopolitical Outlook</h3>", unsafe_allow_html=True)

            scv_categories = [
                ("Global Foundry Market", text_section_1, "#00bfff"),
                ("AI Chip Demand", text_section_2, "#ff00ff"),
                ("Critical Minerals (REE)", text_section_3, "#00ff00"),
                ("Export Controls", text_section_4, "#ff4b4b"),
                ("Military & Outer Space", text_military, "#ffd166"),
                ("India Developments", text_india, "#ff8c00"),
                ("West Asia / Middle East", text_wa, "#9400d3")
            ]

            active_cats = []
            for name, txt, col in scv_categories:
                if len(txt.strip()) > 20:
                    dynamic_score = calculate_domain_threat(name, txt, dashboard_data)
                    active_cats.append({"name": name, "score": dynamic_score, "color": col})

            active_cats = sorted(active_cats, key=lambda x: x["score"], reverse=True)

            scv_cols = st.columns([1.2, 1])

            with scv_cols[0]:
                st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
                st.markdown("<p style='color: #888; font-size: 14px; font-weight: bold; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 0px; text-align: center;'>Supply Chain Vulnerability (SCV) Wheel</p>", unsafe_allow_html=True)

                if active_cats:
                    fig = go.Figure()

                    base_hole = 0.35      
                    ring_width = 0.015    
                    gap = 0.075           

                    for i, cat in enumerate(active_cats):
                        val = cat["score"]
                        color = cat["color"]

                        data_hole = base_hole + i * (ring_width + gap)
                        fig.add_trace(go.Pie(
                            values=[val, 100 - val],
                            hole=data_hole,
                            domain=dict(x=[0, 1], y=[0, 1]),
                            marker=dict(
                                colors=[color, "#000000"],
                                line=dict(width=0) 
                            ),
                            textinfo='none',
                            sort=False,
                            direction='clockwise',
                            hoverinfo='text',
                            hovertext=[f"{cat['name']}: {val}%", ""],
                            showlegend=False
                        ))

                        gap_hole = data_hole + ring_width
                        fig.add_trace(go.Pie(
                            values=[100], 
                            hole=gap_hole,
                            domain=dict(x=[0, 1], y=[0, 1]),
                            marker=dict(
                                colors=["#000000"], 
                                line=dict(width=2, color="#000000")
                            ), 
                            textinfo='none',
                            sort=False,
                            hoverinfo='none',
                            showlegend=False
                        ))
                    
                    fig.add_trace(go.Pie(
                        values=[100],
                        hole=0.98,
                        domain=dict(x=[0, 1], y=[0, 1]),
                        marker=dict(colors=["#000000"], line=dict(width=4, color="#000000")),
                        textinfo='none',
                        hoverinfo='none',
                        showlegend=False
                    ))

                    overall_score = int(sum(c["score"] for c in active_cats) / len(active_cats)) if active_cats else 0

                    fig.update_layout(
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        margin=dict(t=20, b=20, l=20, r=20),
                        height=400,
                        annotations=[dict(
                            text=f"<b style='font-size:42px; color:white;'>{overall_score}</b><br><span style='color:#aaaaaa; font-size:12px; font-weight:bold;'>AVG SCV SCORE</span>",
                            x=0.5, y=0.5,
                            showarrow=False
                        )]
                    )

                    st.plotly_chart(fig, use_container_width=True)
                    
                    legend_html = "<div style='display:flex; flex-wrap:wrap; justify-content:center; gap:12px; margin-top:-30px; margin-bottom:20px;'>"
                    for cat in active_cats:
                        legend_html += f"<div style='font-size:10px; font-weight:bold; color:#a3a3a3;'><span style='color:{cat['color']};'>●</span> {cat['name'].upper()}</div>"
                    legend_html += "</div>"
                    st.markdown(legend_html, unsafe_allow_html=True)
                else:
                    st.warning("Not enough data to render the wheel.")

            with scv_cols[1]:
                st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
                st.markdown("<p style='color: #888; font-size: 14px; font-weight: bold; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 20px;'>SCV Threat Matrix (Active Domains)</p>", unsafe_allow_html=True)
                
                if active_cats:
                    for cat in active_cats:
                        label = cat["name"].upper()
                        value = cat["score"]
                        color = cat["color"]
                        
                        st.markdown(f"""
                        <div style="margin-bottom: 15px;">
                            <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                                <span style="font-size: 12px; font-weight: 600; color: #d1d5db; letter-spacing: 0.5px;">{label}</span>
                                <span style="font-size: 13px; font-weight: bold; color: {color};">{value}%</span>
                            </div>
                            <div style="width: 100%; background-color: #1f2937; border-radius: 4px; height: 6px;">
                                <div style="width: {value}%; background-color: {color}; height: 6px; border-radius: 4px; box-shadow: 0 0 8px {color}80;"></div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("No domain data available to calculate threat matrix.")
            
            # ==========================================
            # AI GEOPOLITICAL SYNTHESIS
            # ==========================================
            st.markdown("<p style='color: #888; font-size: 14px; font-weight: bold; text-transform: uppercase; letter-spacing: 1px; margin-top: 20px; margin-bottom: 10px;'>AI Geopolitical Synthesis</p>", unsafe_allow_html=True)
            if text_summary and text_summary.strip() != "":
                with st.container(height=160):
                    render_highlighted_text(text_summary, selected_actor)
            else:
                st.info("No synthesis data available.")
                
            st.markdown("---")

            if text_ews and text_ews.strip() != "":
                st.markdown("<h5 style='color:#ff4b4b; margin-top: 0px; margin-bottom: 5px;'>🚨 Weekly EWS Synthesis</h5>", unsafe_allow_html=True)
                render_highlighted_text(text_ews, selected_actor)
                st.markdown("<br>", unsafe_allow_html=True)
            
            st.markdown("---")

            if latest_filepath:
                df_kpi = clean_dataframe(pd.DataFrame(dashboard_data.get('kpi_metrics', [])))
                df_fund = clean_dataframe(pd.DataFrame(dashboard_data.get('funding_data', [])))
                df_market = clean_dataframe(pd.DataFrame(dashboard_data.get('market_impact', [])))
                df_risk = clean_dataframe(pd.DataFrame(dashboard_data.get('supply_chain_risk', [])))
                
                if not df_kpi.empty and 'Metric' in df_kpi.columns:
                    st.markdown("##### Executive Snapshot")
                    cols_per_row = 3
                    for i in range(0, len(df_kpi), cols_per_row):
                        kpi_cols = st.columns(cols_per_row)
                        for j in range(cols_per_row):
                            if i + j < len(df_kpi):
                                with kpi_cols[j]:
                                    row = df_kpi.iloc[i + j]
                                    label_val = str(row.get('Metric', ''))
                                    metric_val = str(row.get('Value', ''))
                                    st.markdown(f"""
                                        <div style="margin-bottom: 20px; border-left: 4px solid #00bfff; padding-left: 15px;">
                                            <p style="font-size: 13px; font-weight: 600; color: #888; margin-bottom: 0px; line-height: 1.2;">{label_val}</p>
                                            <p style="font-size: 26px; font-weight: bold; margin-top: 0px; line-height: 1.2; color: white;">{metric_val}</p>
                                        </div>
                                    """, unsafe_allow_html=True)
                    st.markdown("---")
                
                st.markdown("<h3 style='color:#00bfff; font-size:22px; margin-top: 20px; margin-bottom: 0px;'>Executive Summary</h3>", unsafe_allow_html=True)
                if text_summary: render_highlighted_text(text_summary, selected_actor)

                st.markdown("<h3 style='color:#00bfff; font-size:22px; margin-top: 20px; margin-bottom: 0px;'>Global Foundry Market & Geopolitical Positioning</h3>", unsafe_allow_html=True)
                if text_section_1: render_highlighted_text(text_section_1, selected_actor)
                
                if not df_fund.empty and not (len(df_fund) == 1 and "No " in str(df_fund.iloc[0].values[0])):
                    st.markdown("##### Strategic Investments & Funding")
                    st.table(df_fund.set_index(df_fund.columns[0]))

                st.markdown("<h3 style='color:#00bfff; font-size:22px; margin-top: 20px; margin-bottom: 0px;'>AI Chip Demand, Manufacturing & Processing</h3>", unsafe_allow_html=True)
                if text_section_2: render_highlighted_text(text_section_2, selected_actor)
                
                st.markdown("<h3 style='color:#00bfff; font-size:22px; margin-top: 20px; margin-bottom: 0px;'>Critical Minerals: Rare Earth Reserves & Supply Chains</h3>", unsafe_allow_html=True)
                if text_section_3: render_highlighted_text(text_section_3, selected_actor)
                
                if not df_market.empty and not (len(df_market) == 1 and "Data Unavailable" in str(df_market.iloc[0].values[0])):
                    st.markdown("##### Market & Geopolitical Impact")
                    st.table(df_market.set_index(df_market.columns[0]))

                st.markdown("<h3 style='color:#00bfff; font-size:22px; margin-top: 20px; margin-bottom: 0px;'>Export Controls & Geopolitical Impact</h3>", unsafe_allow_html=True)
                if text_section_4: render_highlighted_text(text_section_4, selected_actor)
                
                if not df_risk.empty and not (len(df_risk) == 1 and "Data Unavailable" in str(df_risk.iloc[0].values[0])):
                    st.markdown("##### Supply Chain Risk Analysis")
                    st.table(df_risk.set_index(df_risk.columns[0]))
                    
                st.markdown("<h3 style='color:#00bfff; font-size:22px; margin-top: 20px; margin-bottom: 0px;'>AI, Chips and Rare Earth in Military and Outer Space Domain</h3>", unsafe_allow_html=True)
                if text_military: render_highlighted_text(text_military, selected_actor)
                
                st.markdown("<h3 style='color:#00bfff; font-size:22px; margin-top: 20px; margin-bottom: 0px;'>Lithography Chokepoints & State Actions</h3>", unsafe_allow_html=True)
                if text_section_5: render_highlighted_text(text_section_5, selected_actor)

                if text_india and text_india.strip() != "": 
                    st.markdown("<h3 style='color:#00bfff; font-size:22px; margin-top: 20px; margin-bottom: 0px;'>India: Domestic & Strategic Developments</h3>", unsafe_allow_html=True)
                    render_highlighted_text(text_india, selected_actor)
                    
                if text_wa and text_wa.strip() != "": 
                    st.markdown("<h3 style='color:#00bfff; font-size:22px; margin-top: 20px; margin-bottom: 0px;'>West Asia/Middle East: Domestic & Strategic Developments</h3>", unsafe_allow_html=True)
                    render_highlighted_text(text_wa, selected_actor)

                region_colors = {
                    "Asia": "#00bfff",                
                    "West Asia/Middle East": "#00ff00",
                    "Americas": "#ff4b4b",            
                    "Africa": "#ffd166",               
                    "Europe": "#ff69b4",               
                    "Oceania": "#ffa500"               
                }

                if not df_actions.empty:
                    map_data = []
                    for _, row in df_actions.iterrows():
                        if selected_actor != "All" and selected_actor != str(row.get('Actor', '')):
                            continue
                            
                        loc_val = str(row.get('Location', '')).strip()
                        actor_val = str(row.get('Actor', ''))
                        action_val = str(row.get('Action', '')).strip()
                        
                        search_string = f"{loc_val} {actor_val}".lower()

                        added_iso = set()
                        
                        for country, data_tuple in COUNTRY_INFO.items():
                            iso_code = data_tuple[0]
                            region_name = data_tuple[1]
                            c_low = country.lower()
                            
                            if re.search(rf'(?<![a-z]){re.escape(c_low)}(?![a-z])', search_string):
                                if iso_code not in added_iso:
                                    map_data.append({"iso_alpha": iso_code, "country": country, "actor": actor_val, "action": action_val, "region": region_name})
                                    added_iso.add(iso_code)
                    
                    if map_data:
                        st.markdown("##### Geopolitical Threat Actions (2D Heatmap)")
                        df_map = pd.DataFrame(map_data)
                        px.set_mapbox_access_token(MAPBOX_PUBLIC_TOKEN)
                        
                        fig = px.choropleth_mapbox(
                            df_map, 
                            geojson="https://raw.githubusercontent.com/johan/world.geo.json/master/countries.geo.json", 
                            locations="iso_alpha", 
                            featureidkey="id", 
                            color="region", 
                            color_discrete_map=region_colors,
                            hover_name="country", 
                            hover_data={"action": True, "actor": True, "region": False, "iso_alpha": False}, 
                            mapbox_style="carto-darkmatter", 
                            zoom=1.0, 
                            center={"lat": 20.0, "lon": 0.0}, 
                            opacity=0.6 
                        )
                        fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, paper_bgcolor="rgba(0,0,0,0)", showlegend=False)
                        st.plotly_chart(fig, use_container_width=True)

                    # ==========================================
                    # NEW FEATURE: TRUE 3D MAPBOX GLOBE
                    # ==========================================
                    st.markdown("##### 3D Tactical Infrastructure Globe")
                    st.markdown("<p style='font-size: 13px; color: #888;'>Use <b>Right-Click + Drag</b> to rotate the 3D globe. Scroll to zoom.</p>", unsafe_allow_html=True)
                    
                    selected_infra = st.multiselect(
                        "📍 Toggle Physical Infrastructure Layers:", 
                        [
                            "Semiconductor Fabs", 
                            "Critical Mineral Sites", 
                            "Maritime Chokepoints", 
                            "Gulf FDI & Capital Diplomacy", 
                            "Naval Order of Battle & Strategic Bases",
                            "Aerospace & Space Force Installations" 
                        ], 
                        default=["Semiconductor Fabs", "Maritime Chokepoints"]
                    )
                    
                    infra_colors_hex = {
                        "Semiconductor Fabs": "#00ffff", 
                        "Critical Mineral Sites": "#ff00ff", 
                        "Maritime Chokepoints": "#ffff00",
                        "Gulf FDI & Capital Diplomacy": "#39ff14",
                        "Naval Order of Battle & Strategic Bases": "#ff4500", 
                        "Aerospace & Space Force Installations": "#ffffff" 
                    }

                    # Prepare data to send to JavaScript
                    map_features = []
                    for infra_type in selected_infra:
                        sites = INFRASTRUCTURE_DATA.get(infra_type, [])
                        color = infra_colors_hex[infra_type]
                        for site in sites:
                            map_features.append({
                                "name": site["name"],
                                "lat": site["lat"],
                                "lon": site["lon"],
                                "color": color
                            })

                    map_data_json = json.dumps(map_features)
                    mapbox_token = MAPBOX_PUBLIC_TOKEN
                    map_bg_color = "#000000"
                    
                    html_code = f"""
                    <!DOCTYPE html>
                    <html>
                    <head>
                    <meta charset="utf-8" />
                    <script src="https://api.mapbox.com/mapbox-gl-js/v2.15.0/mapbox-gl.js"></script>
                    <link href="https://api.mapbox.com/mapbox-gl-js/v2.15.0/mapbox-gl.css" rel="stylesheet" />
                    <style>
                    html, body {{ height: 100%; width: 100%; margin: 0; padding: 0; background-color: {map_bg_color}; overflow: hidden; }}
                    #map {{ position: absolute; top: 0; left: 0; width: 100%; height: 100%; border-radius: 8px; }}
                    .mapboxgl-popup-content {{ background-color: #1e1e1e; color: #ffffff; border: 1px solid #00bfff; border-radius: 5px; font-family: monospace; padding: 10px; box-shadow: 0 0 10px rgba(0, 191, 255, 0.5); }}
                    .mapboxgl-popup-close-button {{ color: #ffffff; }}
                    </style>
                    </head>
                    <body>
                    <div id="map"></div>
                    <script>
                    mapboxgl.accessToken = '{mapbox_token}';

                    if (!mapboxgl.accessToken.startsWith('pk.')) {{
                        document.getElementById('map').innerHTML = '<div style="display:flex; justify-content:center; align-items:center; height:100%; color:#00bfff; font-family:monospace; text-align:center; background:#1e1e1e; border:1px solid #00bfff; border-radius:8px; padding:20px;"><div><h2>⚠️ Mapbox Token Required</h2></div></div>';
                    }} else {{
                        const map = new mapboxgl.Map({{
                            container: 'map',
                            style: 'mapbox://styles/mapbox/dark-v11',
                            projection: 'globe', 
                            zoom: 1.2,
                            center: [30, 20],
                            pitch: 45
                        }});

                        map.on('style.load', () => {{
                            map.setFog({{ 'color': 'rgb(10, 20, 30)', 'high-color': 'rgb(0, 0, 0)', 'horizon-blend': 0.1, 'space-color': 'rgb(5, 5, 5)', 'star-intensity': 0.8 }});
                        }});

                        map.addControl(new mapboxgl.NavigationControl());

                        const rawData = {map_data_json};

                        function createPolygon(lon, lat, radiusDegrees = 1.0) {{
                            const pts = [];
                            const sides = 16;
                            for (let i = 0; i < sides; i++) {{
                                const angle = (i / sides) * 2 * Math.PI;
                                const lonOffset = (radiusDegrees / Math.cos(lat * Math.PI / 180)) * Math.cos(angle);
                                const latOffset = radiusDegrees * Math.sin(angle);
                                pts.push([lon + lonOffset, lat + latOffset]);
                            }}
                            pts.push(pts[0]); 
                            return [pts];
                        }}

                        map.on('load', () => {{
                            map.resize();
                            
                            const features = rawData.map(item => ({{
                                type: 'Feature',
                                geometry: {{ type: 'Polygon', coordinates: createPolygon(item.lon, item.lat, 0.8) }},
                                properties: {{ name: item.name, color: item.color, height: 500000 }}
                            }}));

                            map.addSource('infrastructure', {{ type: 'geojson', data: {{ type: 'FeatureCollection', features: features }} }});
                            map.addLayer({{
                                'id': 'infrastructure-pillars',
                                'type': 'fill-extrusion',
                                'source': 'infrastructure',
                                'paint': {{ 'fill-extrusion-color': ['get', 'color'], 'fill-extrusion-height': ['get', 'height'], 'fill-extrusion-base': 0, 'fill-extrusion-opacity': 0.8 }}
                            }});

                            map.on('click', 'infrastructure-pillars', (e) => {{
                                const props = e.features[0].properties;
                                new mapboxgl.Popup().setLngLat(e.lngLat).setHTML('<strong>' + props.name + '</strong>').addTo(map);
                            }});

                            map.on('mouseenter', 'infrastructure-pillars', () => {{ map.getCanvas().style.cursor = 'pointer'; }});
                            map.on('mouseleave', 'infrastructure-pillars', () => {{ map.getCanvas().style.cursor = ''; }});
                        }});
                    }}
                    </script>
                    </body>
                    </html>
                    """

                    components.html(html_code, height=850, scrolling=False) 

                if not df_actions.empty:
                    st.markdown("##### Recent State Actions")
                    if selected_actor != "All":
                        display_actions = df_actions[df_actions['Actor'] == selected_actor]
                    else:
                        display_actions = df_actions
                        
                    st.table(display_actions.set_index(display_actions.columns[0]))

                st.markdown("<h3 style='color:#00bfff; font-size:22px; margin-top: 20px; margin-bottom: 0px;'>Strategic Conclusion</h3>", unsafe_allow_html=True)
                if text_final: render_highlighted_text(text_final, selected_actor)

                # ==========================================
                # LIVE GLOBAL TELEMETRY 
                # ==========================================
                st.markdown("<h2 style='text-align: center; color: #00bfff; margin-top: 50px; margin-bottom: 10px;'>Live Global Telemetry</h2>", unsafe_allow_html=True)
                st.markdown("---")
                
                last_updated_str = "Unknown"
                latest_time = 0
                
                for f in glob.glob("data/*"):
                    try:
                        mtime = os.path.getmtime(f)
                        if mtime > latest_time:
                            latest_time = mtime
                    except: pass
                
                if latest_time > 0:
                    diff_minutes = int(time.time() - latest_time) // 60
                    if diff_minutes < 0 or diff_minutes > 100000:
                        last_updated_str = "Awaiting fresh sync"
                    elif diff_minutes < 1:
                        last_updated_str = "Just now"
                    elif diff_minutes < 60:
                        last_updated_str = f"{diff_minutes} minutes ago"
                    else:
                        hours = diff_minutes // 60
                        mins = diff_minutes % 60
                        last_updated_str = f"{hours}h {mins}m ago"

                st.markdown("##### Think Tank Radar")
                st.markdown(f"<p style='font-size: 14px; font-weight: bold; color: #00ff00; margin-top: -10px;'>🟢 LIVE Geopolitical and OSINT SYNC: <span style='color: #888; font-weight: normal;'>Last updated {last_updated_str}</span></p>", unsafe_allow_html=True)
                
                live_rss = parse_rss_txt_file()

                active_alert = get_active_live_alert()
                if active_alert and isinstance(live_rss, dict):
                    alert_headline = active_alert.get('headline', '')
                    
                    is_duplicate = False
                    for reg, articles in live_rss.items():
                        if any(alert_headline.lower() in art.get('title', '').lower() for art in articles):
                            is_duplicate = True
                            break
                    
                    if not is_duplicate:
                        target_reg = "Asia"
                        summary_text = active_alert.get('summary', '').lower()
                        regions_to_check = ["Asia", "West Asia/Middle East", "Americas", "Africa", "Europe", "Oceania"]
                        
                        for r in regions_to_check:
                            if r.split('/')[0].lower() in summary_text:
                                target_reg = r
                                break
                                
                        if target_reg not in live_rss:
                            live_rss[target_reg] = []
                            
                        live_rss[target_reg].append({
                            "title": f"🔴 LIVE WARNING: {alert_headline}",
                            "published": "JUST IN - ACTIVE ALERT",
                            "link": "#"
                        })
                
                if live_rss and isinstance(live_rss, dict):
                    regions = ["Asia", "West Asia/Middle East", "Americas", "Africa", "Europe", "Oceania"]
                    
                    cols_r1 = st.columns(3)
                    for i in range(3):
                        reg = regions[i]
                        color = region_colors.get(reg, "#ffffff")
                        articles = live_rss.get(reg, [])
                        
                        with cols_r1[i]:
                            st.markdown(f"<h4 style='color: {color}; border-bottom: 2px solid {color}; padding-bottom: 5px;'>{reg}</h4>", unsafe_allow_html=True)
                            if articles:
                                scroll_box = st.container(height=300)
                                for art in reversed(articles): 
                                    clean_title = art['title'].replace('"', '&quot;').replace("'", "&#39;")
                                    html_str = f'<div style="margin-bottom:10px; padding:10px; background-color:rgba(255,255,255,0.05); border-left:3px solid {color}; border-radius:4px;"><a href="{art["link"]}" target="_blank" style="color:#e0e0e0; font-weight:600; text-decoration:none; font-size:13px; display:block; margin-bottom:5px;">{clean_title}</a><span style="font-size:11px; color:#888;">{art["published"][:25]}</span></div>'
                                    scroll_box.markdown(html_str, unsafe_allow_html=True)
                            else:
                                st.info("No data available.")
                                
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    cols_r2 = st.columns(3)
                    for i in range(3, 6):
                        reg = regions[i]
                        color = region_colors.get(reg, "#ffffff")
                        articles = live_rss.get(reg, [])
                        
                        with cols_r2[i-3]:
                            st.markdown(f"<h4 style='color: {color}; border-bottom: 2px solid {color}; padding-bottom: 5px;'>{reg}</h4>", unsafe_allow_html=True)
                            if articles:
                                scroll_box = st.container(height=300)
                                for art in reversed(articles):
                                    clean_title = art['title'].replace('"', '&quot;').replace("'", "&#39;")
                                    html_str = f'<div style="margin-bottom:10px; padding:10px; background-color:rgba(255,255,255,0.05); border-left:3px solid {color}; border-radius:4px;"><a href="{art["link"]}" target="_blank" style="color:#e0e0e0; font-weight:600; text-decoration:none; font-size:13px; display:block; margin-bottom:5px;">{clean_title}</a><span style="font-size:11px; color:#888;">{art["published"][:25]}</span></div>'
                                    scroll_box.markdown(html_str, unsafe_allow_html=True)
                            else:
                                st.info("No data available.")
                else:
                    st.info("Live feed currently unavailable. (Awaiting next GitHub Action run to initialize new structure).")

                sources_list = dashboard_data.get('sources', [])
                if sources_list:
                    st.markdown("---")
                    st.markdown("<h3 style='color:#00bfff; font-size:20px; margin-top: 20px; margin-bottom: 0px;'>Verified Intelligence Sources</h3>", unsafe_allow_html=True)
                    sources_markdown = ""
                    for src in sources_list:
                        sources_markdown += f"- [{src['title']}]({src['url']})\n"
                    st.markdown(sources_markdown)

            # --- SHARE & EXPORT ---
            st.markdown("---")
            st.markdown("### Document Controls")
            
            if st.session_state['role'] == 'admin':
                bot_col1, bot_col2 = st.columns(2)
                with bot_col1:
                    st.markdown("**🔗 Share Dashboard Link:**")
                    st.code("https://www.semirare.in/", language="text")
                with bot_col2:
                    st.markdown("**📄 Export Full Document:**")
                    if latest_filepath:
                        text_list = [text_summary, text_section_1, text_section_2, text_section_3, text_section_4, text_military, text_section_5, text_india, text_wa]
                        word_file = create_landscape_word(
                            text_list, text_final, 
                            dashboard_data.get('recent_actions', []), 
                            brief_date, 
                            dashboard_data.get('funding_data', []), 
                            dashboard_data.get('market_impact', []), 
                            dashboard_data.get('supply_chain_risk', []),
                            dashboard_data.get('sources', []),
                            text_ews
                        )
                        
                        st.download_button(
                            label="⬇️ Download Authentic Word Doc", data=word_file,
                            file_name=f"SemicoN Weekly Brief - {brief_date}.docx",
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                        )

                if latest_filepath:
                    st.markdown("---")
                    st.markdown("### System Administration")
                    st.toggle("✏️ Enable Human-AI Vetting Mode (Edit Text & Data)", key="vetting_toggle")
            
            else:
                st.markdown("**🔗 Share Dashboard Link:**")
                st.code("https://www.semirare.in/", language="text")

    elif view_selection == "Trend Timelines":
        st.title("Macro Trends & Timelines")
        st.markdown("Tracking the volume of Geopolitical Actions and Supply Chain Risks across historical briefs.")
        
        archive_mapping = get_brief_mappings('data')
        if archive_mapping:
            sorted_brief_paths = list(archive_mapping.values())
            sorted_brief_paths.reverse() 
            
            trend_data = []
            for f_path in sorted_brief_paths:
                try:
                    with open(f_path, 'r') as file:
                        d = json.load(file)
                        b_date = d.get('date', 'Unknown')
                        
                        actions = d.get('recent_actions', [])
                        risks = d.get('supply_chain_risk', [])
                        
                        actions_count = len([a for a in actions if "System" not in str(a.values())])
                        risks_count = len([r for r in risks if "Data Unavailable" not in str(r.values())])
                        
                        trend_data.append({
                            "Date": b_date,
                            "Geopolitical Actions": actions_count,
                            "Supply Chain Risks": risks_count
                        })
                except: pass
            
            if trend_data:
                df_trends = pd.DataFrame(trend_data).set_index("Date")
                st.line_chart(df_trends)
            else:
                st.warning("Not enough valid data points to plot a trend.")
        else:
            st.warning("No archives available to generate trend timelines.")

    elif view_selection == "Archives":
        st.title("Archives")
        archive_mapping = get_brief_mappings('data')
        
        if archive_mapping:
            selected_brief = st.selectbox("Select Past Brief:", list(archive_mapping.keys()))
            st.info(f"Displaying: {selected_brief}")
            with open(archive_mapping[selected_brief], 'r') as f:
                archived_data = json.load(f)
            
            arch_raw = archived_data.get('brief_raw', '')
            t1 = extract_tag('EXEC', arch_raw) or arch_raw
            st.markdown(t1.replace('$', r'\$'))
        else:
            st.warning("No active archives found.")

    elif view_selection == "Clean Archives" and st.session_state['role'] == 'admin':
        st.title("Clean Archives")
        st.info("Move outdated or incorrect briefs to the Trash. Guests cannot see this tool.")
        archive_mapping = get_brief_mappings('data')
        
        if archive_mapping:
            archive_to_clean = st.selectbox("Select Brief to Clean:", list(archive_mapping.keys()))
            if st.button("🗑️ Move to Trash", type="primary"):
                old_path = archive_mapping[archive_to_clean]
                filename = os.path.basename(old_path)
                new_path = os.path.join('trash', filename)
                os.rename(old_path, new_path)
                st.success(f"Successfully moved to Trash: {archive_to_clean}")
                st.rerun()
        else:
            st.warning("No active archives found to clean.")
            
    elif view_selection == "Trash" and st.session_state['role'] == 'admin':
        st.title("Trash Bin")
        st.warning("Items here are completely hidden from the public dashboard.")
        trash_mapping = get_brief_mappings('trash')
        
        if trash_mapping:
            archive_to_manage = st.selectbox("Select Brief in Trash:", list(trash_mapping.keys()))
            old_path = trash_mapping[archive_to_manage]
            filename = os.path.basename(old_path)
            
            col_rev, col_del = st.columns(2)
            with col_rev:
                if st.button("♻️ Revert to Archives"):
                    new_path = os.path.join('data', filename)
                    os.rename(old_path, new_path)
                    st.success(f"Completely restored: {archive_to_manage}")
                    st.rerun()
            with col_del:
                if st.button("⚠️ Permanently Delete", type="primary"):
                    os.remove(old_path)
                    st.success(f"Permanently destroyed: {archive_to_manage}")
                    st.rerun()
        else:
            st.info("Trash is currently empty.")