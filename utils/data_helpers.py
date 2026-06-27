import glob
import json
import re
import os
import pandas as pd
import streamlit as st
import datetime 

def get_brief_mappings(directory):
    files = glob.glob(f'{directory}/*.json')
    
    # 🛑 THE FIX: The absolute truth. Sort the files by the exact millisecond they were created/modified on the server. Newest first.
    files.sort(key=os.path.getmtime, reverse=True)
    
    mapping = {}
    exclude_files = [
        'live_alert.json', 'flash_alert.json', 'psyopoly_alerts.json', 
        'sitrep_history.json', 'geopolitical_memory.json'
    ]
    
    # Because 'files' is perfectly sorted by time, inserting them into the dictionary in order guarantees the dropdown is perfectly chronological.
    for f in files:
        filename = os.path.basename(f)
        
        if filename in exclude_files or filename.startswith('tactical_events') or filename.startswith('weekly_tactical_live'):
            continue
            
        try:
            with open(f, 'r', encoding='utf-8') as file:
                d = json.load(file)
                if not isinstance(d, dict): continue
                    
                b_date = 'Unknown Date'
                if 'title' in d and ' - ' in d['title']:
                    extracted_date = str(d['title']).split(' - ')[-1].strip()
                    if len(extracted_date) > 5: b_date = extracted_date
                
                if b_date == 'Unknown Date':
                    b_date = d.get('date', 'Unknown Date')
                
                if b_date == 'Unknown Date':
                    date_match = re.search(r'\d{4}-\d{2}-\d{2}', filename)
                    if date_match: b_date = date_match.group(0)
                    else:
                        mtime = os.path.getmtime(f)
                        b_date = datetime.datetime.fromtimestamp(mtime).strftime('%Y-%m-%d')
                
                # 🏷️ Labeling Logic
                if 'weekly_tactical' in filename:
                    display_name = f"Tactical Weekly Brief: Strategic Intelligence Synthesis - {b_date}"
                elif 'brief_flash' in filename or 'flash_brief' in filename or 'flash' in filename:  
                    display_name = f"Executive Flash Brief - {b_date}"
                elif 'flush_brief' in filename:
                    display_name = f"Executive Flash Brief (Live Temporary) - {b_date}"
                elif 'shift_brief' in filename:
                    display_name = f"Today's Shift Snippet - {b_date}"
                elif 'brief_' in filename:
                    display_name = f"Weekly Intelligence Brief - {b_date}"
                else:
                    display_name = f"Intelligence Document - {b_date} ({filename})"
                    
                if display_name in mapping:
                    clean_filename = filename.replace('.json', '')
                    display_name = f"{display_name} (File: {clean_filename})"
                    
                mapping[display_name] = f
        except Exception: pass
            
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