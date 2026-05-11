import streamlit as st
import streamlit.components.v1 as components
import os
import time
from datetime import datetime
from utils.engines import get_active_live_alert, get_deployment_timestamp

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
        
        # Guarantee the fallback time never shifts during navigation or refresh
        fallback_time_ms = get_deployment_timestamp()
        
        if alert:   
            try:
                # Safely check for timestamp without triggering datetime.now() execution
                if 'timestamp' in alert:
                    dt = datetime.fromisoformat(alert['timestamp'].replace("Z", "+00:00"))
                    start_timestamp_ms = int(dt.timestamp() * 1000)
                else:
                    start_timestamp_ms = fallback_time_ms
            except:
                start_timestamp_ms = fallback_time_ms
            
            # Pre-calculate the elapsed time in Python to eliminate the 00:00:00 visual flash
            elapsed_ms = max(0, int(time.time() * 1000) - start_timestamp_ms)
            h, m, s = elapsed_ms // 3600000, (elapsed_ms % 3600000) // 60000, (elapsed_ms % 60000) // 1000
            initial_clock = f"{h:02d}:{m:02d}:{s:02d}"
            
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
                    max-height: 240px; /* NEW: Forces the box to stop expanding and trigger the scrollbar */
                    height: auto;
                    box-sizing: border-box;
                    overflow-y: auto; 
                    -webkit-overflow-scrolling: touch; /* NEW: Forces smooth scroll support on Android/iOS non-Safari browsers */
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
                        <div class="timer">Live Since: <span id="clock">{initial_clock}</span></div>
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
            components.html(html_code, height=245) # <-- TIGHTENED HEIGHT 
            
        else:
            start_timestamp_ms = fallback_time_ms
            
            # Pre-calculate to eliminate 00:00:00 flash
            elapsed_ms = max(0, int(time.time() * 1000) - start_timestamp_ms)
            h, m, s = elapsed_ms // 3600000, (elapsed_ms % 3600000) // 60000, (elapsed_ms % 60000) // 1000
            initial_clock = f"{h:02d}:{m:02d}:{s:02d}"

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
                    <div class="timer">Status Verified: <span id="clock">{initial_clock}</span> ago</div>
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
        pass  # <--- THIS CLOSES THE TRY BLOCK AT THE TOP OF THE FUNCTION