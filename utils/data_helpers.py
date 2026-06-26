import glob
import json
import re
import os
import pandas as pd
import streamlit as st

def get_brief_mappings(directory):
    # 🛑 THE FIX: Expand the search scope to catch all your generated JSON formats
    files = []
    files.extend(glob.glob(f'{directory}/brief_*.json'))
    files.extend(glob.glob(f'{directory}/flush_brief_*.json'))
    files.extend(glob.glob(f'{directory}/shift_brief*.json'))
    files.extend(glob.glob(f'{directory}/tactical_events_*.json'))
    
    # Sort files by modification time so the newest are at the top
    files.sort(key=os.path.getmtime, reverse=True)
    
    mapping = {}
    for f in files:
        try:
            with open(f, 'r', encoding='utf-8') as file:
                d = json.load(file)
                
                # Handle both Dictionary returns and List returns (for tactical_events)
                if isinstance(d, dict):
                    b_date = d.get('date', 'Unknown Date')
                elif isinstance(d, list) and len(d) > 0 and isinstance(d[0], dict):
                    b_date = d[0].get('Date', 'Unknown Date')
                else:
                    b_date = 'Unknown Date'
                
                filename = os.path.basename(f)
                
                # If the JSON doesn't have a date key, try to extract it from the filename
                if b_date == 'Unknown Date':
                    date_match = re.search(r'\d{4}-\d{2}-\d{2}', filename)
                    b_date = date_match.group(0) if date_match else "Unknown Date"
                
                # 🏷️ Intelligent Labeling based on the filename structure
                if 'weekly_tactical' in filename or 'tactical_events' in filename:
                    display_name = f"Weekly Tactical Brief - {b_date}"
                elif 'flush_brief' in filename:
                    display_name = f"Executive Flash Brief - {b_date}"
                elif 'shift_brief' in filename:
                    display_name = f"Today's Shift Snippet - {b_date}"
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