import glob
import json
import re
import os
import pandas as pd
import streamlit as st

def get_brief_mappings(directory):
    files = glob.glob(f'{directory}/brief_*.json')
    files.sort(reverse=True)
    mapping = {}
    for f in files:
        try:
            with open(f, 'r', encoding='utf-8') as file:
                d = json.load(file)
                # Ensure we pull a clean date, falling back to a safe string if missing
                b_date = d.get('date', 'Unknown Date')
                filename = os.path.basename(f)
                
                # 🛑 THE FIX: Dynamically label the brief based on its filename
                if 'weekly_tactical' in filename:
                    display_name = f"Weekly Tactical Brief - {b_date}"
                else:
                    display_name = f"Weekly Intelligence Brief - {b_date}"
                    
                # Prevent dictionary overwriting if multiple briefs trigger on the exact same date
                if display_name in mapping:
                    clean_filename = filename.replace('.json', '')
                    display_name = f"{display_name} (File: {clean_filename})"
                    
                mapping[display_name] = f
        except Exception: 
            pass
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

def extract_tag(tag, text):
    match = re.search(rf'<{tag}>(.*?)</{tag}>', text, re.DOTALL | re.IGNORECASE)
    if match:
        clean_text = match.group(1).strip()
        clean_text = re.sub(r'</?[A-Z_]+>', '', clean_text)
        return clean_text
    return None