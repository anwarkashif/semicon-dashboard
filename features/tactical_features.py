import streamlit as st
import pandas as pd
import json
import re
import urllib.parse
import os
import time
import glob
import plotly.express as px
import streamlit.components.v1 as components
from utils.constants import COUNTRY_INFO, INFRASTRUCTURE_DATA
from utils.engines import parse_rss_txt_file, get_active_live_alert

def render_decision_support_engine(all_text="", show_intel_note=False, is_home=False):
    st.markdown("""
    <h3 style='color:#00ffaa;
    margin-top: 5px;
    margin-bottom: 5px;'>
    🧠 Strategic Decision Support Engine
    </h3>
    """, unsafe_allow_html=True)
    
    if is_home:
        st.markdown("**INTELLIGENCE NOTE:** Live Geopolitics-OSINT Evaluation and Intelligence")
        st.markdown("<div style='margin-bottom: 15px;'></div>", unsafe_allow_html=True)
    else:
        st.markdown("<div style='margin-bottom: 15px;'></div>", unsafe_allow_html=True)
        
    decision_signals = []
    
    # ==========================================
    # DYNAMIC LIVE STRATEGIC SIGNAL DETECTION
    # ==========================================
    live_data_path = 'data/executive_home/tactical_events_24h.json'
    
    if os.path.exists(live_data_path):
        try:
            with open(live_data_path, 'r') as f:
                live_events = json.load(f)
            
            for event in live_events:
                risk_val = str(event.get('Risk', 'ELEVATED')).upper()
                
                # Dynamic priority routing & weights for execution sequence sorting
                if 'CRITICAL' in risk_val:
                    priority = "🔴 CRITICAL"
                    border_color = "#ef4444"
                    severity_weight = 3
                elif 'HIGH' in risk_val:
                    priority = "🟠 HIGH"
                    border_color = "#f97316"
                    severity_weight = 2
                else:
                    priority = "🟡 WATCH"
                    border_color = "#facc15"
                    severity_weight = 1
                    
                actor = event.get('Actor', 'Strategic Actor')
                location = event.get('Location', 'Global Domain')
                action = event.get('Action', 'Geopolitical shift detected')
                headline = event.get('Headline', action) 
                
                # Extract the execution timestamp / event date
                timestamp = event.get('Date', time.strftime('%Y-%m-%d'))
                
                # Generate dynamic recommendations based on live context
                action_context = (action + " " + location + " " + headline).lower()
                
                if any(k in action_context for k in ['mineral', 'rare earth', 'mining', 'lithium']):
                    rec = "Verify strategic mineral reserves and activate secondary sourcing protocols."
                elif any(k in action_context for k in ['taiwan', 'tsmc', 'semiconductor', 'fab', 'chip']):
                    rec = "Review advanced node inventory buffers and assess immediate regional exposure."
                elif any(k in action_context for k in ['military', 'strike', 'missile', 'war', 'navy']):
                    rec = "Initiate maritime rerouting protocols and monitor kinetic spillover."
                elif any(k in action_context for k in ['sanction', 'export', 'tariff', 'ban']):
                    rec = "Engage compliance teams to verify cross-border component legality and entity lists."
                elif any(k in action_context for k in ['ship', 'maritime', 'sea', 'strait', 'port']):
                    rec = "Monitor freight insurance premiums and immediate logistics bottlenecks."
                elif any(k in action_context for k in ['ai', 'quantum', 'cyber', 'drone']):
                    rec = "Audit IP security protocols and monitor competitive technological advancements."
                else:
                    rec = "Escalate to executive risk committee for continuous tracking."

                decision_signals.append({
                    "risk": f"{actor} ➔ {location}",
                    "impact": headline,
                    "recommendation": rec,
                    "priority": priority,
                    "border": border_color,
                    "weight": severity_weight,
                    "timestamp": timestamp
                })
        except Exception:
            pass

    # ==========================================
    # COMBO SORTING LAYER (CRITICAL -> HIGH -> WATCH)
    # ==========================================
    if decision_signals:
        decision_signals.sort(key=lambda x: x['weight'], reverse=True)

    # ==========================================
    # RENDER ENGINE
    # ==========================================
    if decision_signals:
        for signal in decision_signals:
            border_color = signal.get("border", "#facc15")
    
            st.markdown(f"""
            <div style="
                background-color:#0a0a0a;
                border-left:5px solid {border_color};
                padding:16px;
                border-radius:10px;
                margin-bottom:15px;
                box-shadow:0 0 12px rgba(0,0,0,0.5);
                position: relative;
            ">
            
            <div style="
                position: absolute;
                top: 16px;
                right: 16px;
                font-size: 11px;
                font-family: monospace;
                color: #888888;
                background: #111111;
                padding: 4px 8px;
                border-radius: 4px;
                border: 1px solid #222222;
            ">
                🕒 INTEL SYNC: {signal['timestamp']}
            </div>
    
            <div style="
                font-size:18px;
                font-weight:bold;
                margin-bottom:10px;
                color:white;
                padding-right: 120px;
            ">
            {signal['priority']} — {signal['risk']}
            </div>
    
            <div style="
                color:#cbd5e1;
                margin-bottom:8px;
                font-size:14px;
            ">
            <b>Live Tactical Impact:</b> {signal['impact']}
            </div>
    
            <div style="
                color:#93c5fd;
                font-size:14px;
            ">
            <b>Recommended Action:</b> {signal['recommendation']}
            </div>
    
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Awaiting live tactical pipeline sync. Engine nominal.")
    
    st.markdown("---")

def render_tactical_maps(df_actions, selected_actor, mapbox_token):
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
            px.set_mapbox_access_token(mapbox_token)
            
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
    # NEW FEATURE: 2D LIVE SUPPLY CHAIN MAP
    # ==========================================
    st.markdown("##### 🌍 Global Semiconductor Infrastructure Map")
    infra_list = []
    for category, locations in INFRASTRUCTURE_DATA.items():
        for loc in locations:
            infra_list.append({"Facility": loc["name"], "Lat": loc["lat"], "Lon": loc["lon"], "Category": category})
    
    if infra_list:
        df_infra = pd.DataFrame(infra_list)
        px.set_mapbox_access_token(mapbox_token)
        fig_infra = px.scatter_mapbox(
            df_infra, lat="Lat", lon="Lon", color="Category", hover_name="Facility",
            mapbox_style="carto-darkmatter", zoom=1.2, height=500,
            color_discrete_sequence=["#00ffff", "#ff00ff", "#ffff00", "#39ff14", "#ff4500", "#ffffff"]
        )
        fig_infra.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, paper_bgcolor="rgba(0,0,0,0)", legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01, font=dict(color="white")))
        st.plotly_chart(fig_infra, use_container_width=True)
    st.markdown("<br>", unsafe_allow_html=True)

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

def render_live_telemetry():
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
    st.markdown(f"<p style='font-size: 14px; font-weight: bold; color: #00ff00; margin-top: -10px;'>🟢 LIVE Geopolitical and SemicoN Dashboard SYNC: <span style='color: #888; font-weight: normal;'>Last updated {last_updated_str}</span></p>", unsafe_allow_html=True)
    
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
                
            alert_query = urllib.parse.quote_plus(alert_headline)
            
            live_rss[target_reg].append({
                "title": f"🔴 LIVE WARNING: {alert_headline}",
                "published": "JUST IN - ACTIVE ALERT",
                "link": f"https://news.google.com/search?q={alert_query}"
            })
    
    if live_rss and isinstance(live_rss, dict):
        regions = ["Asia", "West Asia/Middle East", "Americas", "Africa", "Europe", "Oceania"]
        region_colors = {
            "Asia": "#00bfff",                
            "West Asia/Middle East": "#00ff00",
            "Americas": "#ff4b4b",            
            "Africa": "#ffd166",                
            "Europe": "#ff69b4",                
            "Oceania": "#ffa500"                
        }
        
        cols_r1 = st.columns(3)
        for i in range(3):
            reg = regions[i]
            color = region_colors.get(reg, "#ffffff")
            articles = live_rss.get(reg, [])
            
            with cols_r1[i]:
                st.markdown(f"<h4 style='color: {color}; border-bottom: 2px solid {color}; padding-bottom: 5px;'>{reg}</h4>", unsafe_allow_html=True)
                if articles:
                    scroll_box = st.container(height=300)
                    for art in list(reversed(articles))[:8]: 
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

def render_verified_sources(sources_list):
    if sources_list:
        st.markdown("---")
        st.markdown("<h3 style='color:#00bfff; font-size:22px; margin-top: 20px; margin-bottom: 15px;'>Verified Intelligence Sources</h3>", unsafe_allow_html=True)
        
        themes = {
            "AI Chip Demand": {"keywords": ["ai", "nvidia", "gpu", "tpu", "compute", "openai", "data center", "server", "algorithm"], "color": "#ff00ff", "icon": "🧠", "sources": []},
            "Critical Minerals (REE)": {"keywords": ["rare earth", "mineral", "lithium", "cobalt", "graphite", "gallium", "germanium", "mining", "supply chain"], "color": "#00ff00", "icon": "⛏️", "sources": []},
            "Export Controls & Geopolitics": {"keywords": ["export", "control", "sanction", "ban", "tariff", "entity list", "bis", "geopolitics", "war", "tension", "blockade", "trade"], "color": "#ff4b4b", "icon": "⚖️", "sources": []},
            "General Strategic Intelligence": {"keywords": [], "color": "#888888", "icon": "📡", "sources": []}, 
            "Global Foundry Market": {"keywords": ["foundry", "tsmc", "samsung", "intel", "smic", "fab", "manufacturing", "yield", "semiconductor", "chipmaker"], "color": "#00bfff", "icon": "🏭", "sources": []},
            "Military & Outer Space": {"keywords": ["military", "defense", "weapon", "missile", "space", "satellite", "darpa", "dod", "navy", "army", "air force", "pentagon"], "color": "#ffd166", "icon": "🚀", "sources": []},
            "Regional (India & West Asia)": {"keywords": ["india", "modi", "dholera", "tata", "west asia", "middle east", "uae", "saudi", "israel", "gulf", "cg power"], "color": "#ff8c00", "icon": "🌍", "sources": []}
        }

        for src in sources_list:
            # 🛑 THE FIX: Bulletproof parsing to handle Pandas NaNs and Legacy Strings
            if isinstance(src, dict):
                raw_title = src.get('title', 'Verified Source')
                raw_url = src.get('url', '#')
                
                # If Pandas injected 'nan' because a headline was missing, fall back to URL
                if pd.isna(raw_title) or str(raw_title).strip().lower() == 'nan':
                    raw_title = raw_url if raw_url != '#' else 'Verified Source'
                    
                title_lower = str(raw_title).lower()
                clean_title = str(raw_title).replace('"', '&quot;').replace("'", "&#39;")
                src_url = str(raw_url)
                
            elif isinstance(src, str):
                if pd.isna(src) or str(src).strip().lower() == 'nan':
                    continue
                title_lower = str(src).lower()
                clean_title = (str(src)[:50] + "...") if len(str(src)) > 50 else str(src)
                src_url = str(src)
            else:
                continue

            placed = False
            for t_name, t_data in themes.items():
                if t_name == "General Strategic Intelligence":
                    continue
                if any(kw in title_lower for kw in t_data["keywords"]):
                    t_data["sources"].append({"title": clean_title, "url": src_url})
                    placed = True
                    break
            
            if not placed:
                themes["General Strategic Intelligence"]["sources"].append({"title": clean_title, "url": src_url})

        src_cols = st.columns(2)
        col_idx = 0
        
        for t_name in sorted(themes.keys()):
            t_data = themes[t_name]
            if t_data["sources"]:
                with src_cols[col_idx % 2]:
                    theme_html = f"""
                    <div style="background-color: rgba(255,255,255,0.03); border-left: 4px solid {t_data['color']}; padding: 15px; margin-bottom: 15px; border-radius: 6px; height: 100%;">
                        <h5 style="color: {t_data['color']}; margin-top: 0; margin-bottom: 10px; font-size: 14px; text-transform: uppercase; letter-spacing: 0.5px;">{t_data['icon']} {t_name}</h5>
                        <ul style="margin: 0; padding-left: 20px; font-size: 13px; color: #d1d5db; line-height: 1.6;">
                    """
                    for formatted_src in t_data["sources"]:
                        theme_html += f"<li style='margin-bottom: 5px;'><a href='{formatted_src['url']}' target='_blank' style='color: #e0e0e0; text-decoration: none; transition: 0.3s;' onmouseover=\"this.style.color='{t_data['color']}'\" onmouseout=\"this.style.color='#e0e0e0'\">{formatted_src['title']}</a></li>"
                    
                    theme_html += "</ul></div>"
                    st.markdown(theme_html, unsafe_allow_html=True)
                col_idx += 1