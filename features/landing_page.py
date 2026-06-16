import streamlit as st
import json
import os
import streamlit.components.v1 as components

def calculate_regional_threats(df_actions):
    threats = {
        "Asia": "ELEVATED", "West Asia": "ELEVATED", "Africa": "WATCH",
        "Europe": "WATCH", "Eurasia": "WATCH", "North America": "NOMINAL",
        "South America": "NOMINAL", "Oceanic": "NOMINAL"
    }
    
    region_mapping = {
        "Asia": ['china', 'taiwan', 'japan', 'korea', 'india', 'philippines', 'indo-pacific', 'asia'],
        "West Asia": ['iran', 'israel', 'red sea', 'yemen', 'saudi', 'uae', 'middle east', 'gaza'],
        "Africa": ['africa', 'sudan', 'congo', 'niger'],
        "Europe": ['europe', 'uk', 'germany', 'france', 'eu'],
        "Eurasia": ['russia', 'ukraine', 'black sea', 'eurasia'],
        "North America": ['us', 'usa', 'united states', 'canada', 'mexico'],
        "South America": ['brazil', 'argentina', 'venezuela', 'south america'],
        "Oceanic": ['australia', 'new zealand', 'oceanic']
    }

    # 1. Update based on df_actions
    if df_actions is not None and not df_actions.empty:
        for _, row in df_actions.iterrows():
            text = str(row.get('Action', '')) + " " + str(row.get('Location', ''))
            text = text.lower()
            risk = str(row.get('Risk', '')).upper()
            
            for region, keywords in region_mapping.items():
                if any(kw in text for kw in keywords):
                    if risk == 'CRITICAL': threats[region] = "CRITICAL"
                    elif risk == 'HIGH' and threats[region] != "CRITICAL": threats[region] = "HIGH"

    # 2. Update based on Flash Alerts to directly boost Command Centre Threat Matrix
    flash_path = 'data/flash_alert.json'
    if os.path.exists(flash_path):
        try:
            with open(flash_path, 'r') as f:
                flash_alerts = json.load(f)
                if isinstance(flash_alerts, list):
                    for alert in flash_alerts:
                        text = str(alert.get('title', '')).lower()
                        risk = str(alert.get('threat_level', '')).upper()
                        
                        for region, keywords in region_mapping.items():
                            if any(kw in text for kw in keywords):
                                if risk == 'CRITICAL': threats[region] = "CRITICAL"
                                elif risk == 'HIGH' and threats[region] != "CRITICAL": threats[region] = "HIGH"
                                elif risk == 'ELEVATED' and threats[region] not in ["CRITICAL", "HIGH"]: threats[region] = "ELEVATED"
        except Exception:
            pass

    return threats

def render_redroom_landing(df_actions):
    st.markdown("""
        <style>
        [data-testid="stAppViewContainer"], .stApp {
            background-color: #000000 !important;
            background-image: none !important;
        }
        [data-testid="stHeader"] { display: none !important; }
        [data-testid="stSidebar"] { display: none !important; }
        
        .landing-title {
            color: #ff0000; 
            font-size: 2.8rem;
            font-weight: 900;
            text-align: center;
            letter-spacing: 4px;
            text-transform: uppercase;
            text-shadow: 0 0 20px rgba(255, 0, 0, 0.8);
            margin-top: 10px;
            margin-bottom: 40px;
            font-family: system-ui, -apple-system, sans-serif;
        }
        
        .glass-panel {
            background: rgba(5, 5, 10, 0.95);
            border: 1px solid #2d0000;
            border-radius: 12px;
            padding: 20px;
            height: 550px;
            overflow-y: auto;
            box-shadow: 0 0 30px rgba(0, 0, 0, 1);
        }
        .glass-panel::-webkit-scrollbar { width: 5px; }
        .glass-panel::-webkit-scrollbar-thumb { background: #441111; border-radius: 5px; }
        
        .panel-header { 
            font-size: 1.2rem; 
            font-weight: 800; 
            background: linear-gradient(90deg, #ff3333 0%, #ff9999 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            border-bottom: 1px solid #441111; 
            padding-bottom: 10px; 
            margin-bottom: 15px; 
            letter-spacing: 1px; 
        }
        
        .tag-critical { color: #ff0000; font-weight: bold; }
        .tag-high { color: #f97316; font-weight: bold; }
        .tag-elevated { color: #eab308; font-weight: bold; }
        .tag-watch { color: #3b82f6; font-weight: bold; }
        .tag-nominal { color: #22c55e; font-weight: bold; }
        
        .flash-link { display: block; text-decoration: none; color: #cbd5e1; font-size: 0.9rem; padding: 12px 10px; border-bottom: 1px solid #1e0505; transition: all 0.2s; line-height: 1.4; }
        .flash-link:hover { background: rgba(255, 0, 0, 0.12); color: #ffffff; padding-left: 15px; border-left: 3px solid #ff0000; }
        
        .region-row { display: flex; justify-content: space-between; align-items: center; padding: 15px 10px; border-bottom: 1px dashed #2d0000; font-size: 1rem; color: #e2e8f0; }
        
        @keyframes defconPulse {
            0% { box-shadow: 0 0 15px rgba(255, 0, 0, 0.5); transform: scale(1); }
            50% { box-shadow: 0 0 40px rgba(255, 0, 0, 1); transform: scale(1.02); }
            100% { box-shadow: 0 0 15px rgba(255, 0, 0, 0.5); transform: scale(1); }
        }
        [data-testid="stButton"] button {
            background: linear-gradient(90deg, #660000, #ff0000, #660000);
            background-size: 200% auto;
            color: #ffffff !important;
            border: 2px solid #ff0000;
            padding: 15px 40px;
            font-size: 1.2rem;
            font-weight: bold;
            letter-spacing: 2px;
            border-radius: 30px;
            transition: all 0.3s ease;
            animation: defconPulse 2s infinite;
        }
        [data-testid="stButton"] button:hover {
            background-position: right center;
            border-color: #ffffff;
            color: #ffffff !important;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<div class='landing-title'>SemicoN Dashboard</div>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1.2, 1.6, 1.2])

    with col1:
        flash_path = 'data/flash_alert.json'
        alerts = []
        if os.path.exists(flash_path):
            try:
                with open(flash_path, 'r') as f: alerts = json.load(f)
            except: pass
        
        html_str = "<div class='glass-panel'><div class='panel-header'>MUST WATCH</div>"
        if alerts and isinstance(alerts, list):
            for alert in alerts[:10]:
                src = alert.get('source', 'INTEL')
                tit = alert.get('title', 'Encrypted Telemetry')
                url = alert.get('url', '#')
                thr = alert.get('threat_level', 'WATCH').upper()
                tc = f"tag-{thr.lower()}"
                html_str += f"<a href='{url}' target='_blank' class='flash-link'><span style='font-size: 0.75rem; color: #8a7373; font-family: monospace;'>{src}</span><br><span class='{tc}'>[{thr}]</span> {tit}</a>"
        else:
            html_str += "<p style='color: #64748b; text-align: center; margin-top: 50px;'>No active flashes in current cycle.</p>"
        html_str += "</div>"
        st.markdown(html_str, unsafe_allow_html=True)

    with col2:
        globe_html = """
        <style> body { margin: 0; background: transparent; overflow: hidden; display: flex; justify-content: center; align-items: center; height: 100%; } </style>
        <script src="https://unpkg.com/three"></script>
        <script src="https://unpkg.com/globe.gl"></script>
        <div id="globeViz" style="width: 100%; height: 550px; display: flex; justify-content: center;"></div>
        <script>
            const globe = Globe()(document.getElementById('globeViz'))
                // Upgraded to standard high-fidelity Blue Marble color texture topology map
                .globeImageUrl('https://unpkg.com/three-globe/example/img/earth-blue-marble.jpg')
                .backgroundColor('rgba(0,0,0,0)')
                .pointOfView({ altitude: 2.0 });
            
            // Retaining full tactical auto-rotation logic across the color profiles
            globe.controls().autoRotate = true;
            globe.controls().autoRotateSpeed = 1.5;
            globe.atmosphereColor('#ff0000');
            globe.atmosphereAltitude(0.25);

            // Removing dark color override masks so natural geography colors pop out cleanly
            const globeMaterial = globe.globeMaterial();
            globeMaterial.emissive = new THREE.Color('#110000');
            globeMaterial.emissiveIntensity = 0.4;
        </script>
        """
        components.html(globe_html, height=550)

    with col3:
        regional_threats = calculate_regional_threats(df_actions)
        mat_str = "<div class='glass-panel'><div class='panel-header'>REGIONAL THREAT MATRIX</div>"
        regions = ["Asia", "West Asia", "Africa", "Europe", "Eurasia", "North America", "South America", "Oceanic"]
        for region in regions:
            lvl = regional_threats.get(region, "NOMINAL")
            tc = f"tag-{lvl.lower()}"
            mat_str += f"<div class='region-row'><span>{region}</span><span class='{tc}'>{lvl}</span></div>"
        mat_str += "</div>"
        st.markdown(mat_str, unsafe_allow_html=True)

    st.markdown("<div style='display: flex; justify-content: center; margin-top: 40px;'>", unsafe_allow_html=True)
    
    col_btn1, col_btn2, col_btn3 = st.columns([1, 1.5, 1])
    with col_btn2:
        if st.button("ENTER DASHBOARD", use_container_width=True):
            st.session_state['dashboard_entered'] = True
            st.session_state['just_entered'] = True  
            st.rerun() 
            
    st.markdown("</div>", unsafe_allow_html=True)