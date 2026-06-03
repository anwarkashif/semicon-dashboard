import streamlit as st
import requests

def render_shadowbroker():
    st.markdown("### 🛰️ Global Threat Intercept (ShadowBroker)")
    st.caption("Live external geospatial intelligence telemetry. Rendered securely via local node.")
    
    st.info("🔒 **SYSTEM ARCHITECTURE NOTE:** ShadowBroker utilizes strict Content-Security-Policy (CSP) headers to protect your local API keys. To maintain zero-trust security, the map runs in an isolated environment outside of the SemicoN iframe.")
    
    st.markdown("<hr style='border: 1px solid #333;'>", unsafe_allow_html=True)

    # ==========================================
    # 📡 PRE-LAUNCH DATA INTERCEPTOR (PORT 3000)
    # ==========================================
    st.markdown("#### 📡 Pre-Launch Threat Intercept")
    
    node_base_url = "http://localhost:3000"
    node_online = False
    
    try:
        # Pinging the active port 3000 to verify application status
        verify_response = requests.get(node_base_url, timeout=2)
        if verify_response.status_code == 200:
            node_online = True
    except requests.exceptions.RequestException:
        pass

    if node_online:
        st.success("🟢 **LOCAL NODE CONNECTED:** ShadowBroker telemetry pipeline is active on Port 3000.")
        
        try:
            target_api_endpoint = "http://localhost:3000/api/bootstrap/critical"
            api_response = requests.get(target_api_endpoint, timeout=3)
            
            if api_response.status_code == 200:
                data = api_response.json()
                st.markdown("##### 🚨 Critical Alert Feed")
                
                # --- TARGETED PARSER based on network inspection ---
                items = []
                
                # 1. Try the "news" array first (usually the most readable alerts)
                if 'news' in data and isinstance(data['news'], list) and len(data['news']) > 0:
                    items = data['news']
                # 2. Fallback to GDELT (GeoJSON features)
                elif 'gdelt' in data and isinstance(data['gdelt'], list) and len(data['gdelt']) > 0:
                    items = [f.get('properties', {}) for f in data['gdelt']]
                
                if items:
                    # Display the top 5 most recent alerts
                    for item in items[:5]:
                        # Extracting exactly based on the screenshot provided
                        title = item.get('title') or item.get('name') or "Critical Intercept"
                        desc = item.get('description') or item.get('summary') or ""
                        url = item.get('url') or item.get('link') or ""
                        source = item.get('source') or item.get('provider') or "OSINT Intercept"
                        
                        # Handle cases where description might be missing but we want to show the alert
                        if desc:
                            desc_html = f"<span style='color: #a0a0a0; font-size: 14px;'>{desc[:200]}{'...' if len(desc) > 200 else ''}</span>"
                        elif url:
                            desc_html = f"<span style='color: #a0a0a0; font-size: 13px; font-style: italic;'>Source: {source} — Click 'Initialize Console' to view full report.</span>"
                        else:
                            desc_html = f"<span style='color: #555; font-size: 13px; font-style: italic;'>[ Tactical Headline Only — Awaiting Full Telemetry ]</span>"
                        
                        st.markdown(f"""
                        <div style='background-color: #0e1117; padding: 15px; border-left: 4px solid #ff4b4b; border-radius: 5px; margin-bottom: 10px;'>
                            <span style='color: #ff4b4b; font-weight: bold; font-family: monospace;'>!! CRITICAL ALERT !!</span><br>
                            <span style='font-weight: bold;'>{title}</span><br>
                            {desc_html}
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.caption("Data stream connected, but no alerts found in the current timeframe.")
            else:
                st.caption(f"Waiting for valid data from endpoint (Status Code: {api_response.status_code}).")
                
        except Exception as e:
            st.warning("Telemetry stream verified, waiting for API route definition.")
    else:
        st.error("🔴 **LOCAL NODE OFFLINE:** Cannot reach Port 3000. Ensure the container is active in Docker Desktop.")

    # ==========================================
    # 🚀 LAUNCHPAD COMMAND CENTER
    # ==========================================
    st.markdown("""
    <div style="background-color: rgba(255, 255, 255, 0.05); padding: 40px; border-radius: 12px; border: 1px solid rgba(255, 255, 255, 0.1); text-align: center; margin-top: 25px; box-shadow: 0 4px 15px rgba(0,0,0,0.5);">
        <h3 style="color: #ffffff; margin-bottom: 10px; font-family: 'Courier New', monospace;">SHADOWBROKER NODE <span style="color: #00ff00;">[ ONLINE ]</span></h3>
        <p style="color: #a0a0a0; font-size: 15px; margin-bottom: 30px;">
            Decentralized threat feeds, ADS-B flight telemetry, and maritime AIS streams are actively being ingested on Port 3000.
        </p>
        <a href="http://localhost:3000" target="_blank" style="background-color: #00bfff; color: #000000; padding: 14px 30px; text-decoration: none; font-weight: bold; border-radius: 30px; font-size: 15px; transition: all 0.3s ease; display: inline-block; letter-spacing: 1px;">
            🚀 INITIALIZE SECURE CONSOLE ➔
        </a>
    </div>
    
    <style>
        a:hover {
            opacity: 0.8;
            box-shadow: 0 0 15px rgba(0, 191, 255, 0.5);
        }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("<div style='margin-top: 40px;'></div>", unsafe_allow_html=True)
    
    with st.expander("📊 **Active Telemetry Streams (Reference)**", expanded=False):
        st.markdown("""
        * **Aviation:** Commercial, private, and military flights (ADS-B).
        * **Maritime:** 25,000+ vessels via AIS, including Carrier Strike Groups.
        * **Space & Satellites:** Orbital tracking and mission-type classification.
        * **Geopolitics:** Global incidents (GDELT) and live warfront mapping.
        * **Infrastructure:** CCTV Mesh, Data Centers, and Internet Outage monitors.
        """)