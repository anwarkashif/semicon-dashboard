import streamlit as st
import pandas as pd
from datetime import datetime

# ==========================================
# 🔍 GEOPOLITICAL VARIABLE CLASSIFICATION ENGINE
# ==========================================
def classify_geopolitical_variable(summary_text):
    # Fallback if the data pipeline injects a null/missing summary
    if not isinstance(summary_text, str):
        return "Strategic Intelligence Log"
        
    text = summary_text.lower()
    
    if any(keyword in text for keyword in ['irgc', 'iran', 'tehran', 'persian']):
        return "Irano-Centric Network Axis"
    elif any(keyword in text for keyword in ['us ', 'u.s.', 'united states', 'washington', 'trump', 'centcom', 'treasury']):
        return "United States Transatlantic Policy"
    elif any(keyword in text for keyword in ['lebanon', 'beirut', 'hezbollah', 'aoun']):
        return "Levantine Operational Front"
    elif any(keyword in text for keyword in ['gaza', 'israel', 'netanyahu', 'flotilla', 'smotrich', 'ben-gvir', 'west bank']):
        return "Israeli Multi-Theater Strategy"
    elif any(keyword in text for keyword in ['syria', 'rojava', 'shahba', 'damascus']):
        return "Syrian Arena Dynamics"
    elif any(keyword in text for keyword in ['ukraine', 'russia', 'putin', 'dmitriev', 'moscow']):
        return "Eastern European Pivot"
    elif any(keyword in text for keyword in ['oil', 'petroleum', 'lpg', 'barrels', 'fuel', 'energy security']):
        return "Global Energy Security Grid"
    
    return "Strategic Intelligence Log"


# ==========================================
# 📅 DATE CONVERSION MATRIX ENGINE
# ==========================================
def format_intel_date(date_str):
    try:
        return datetime.strptime(str(date_str).strip(), "%Y-%m-%d").strftime("%B %d, %Y")
    except Exception:
        return str(date_str)


# ==========================================
# 🚀 CORE INTEL GRID MATRIX RENDERER
# ==========================================
def render_tactical_grid_matrix(df_target_segment):
    """
    Renders the exact 6-column professional tactical card matrix layout.
    Shared by both the Live Interceptor and the Historical Archive views.
    """
    unique_days = df_target_segment['FormattedDate'].unique()
    
    for current_day in unique_days:
        st.markdown(
            f"""
            <div class="dateline-axis-separator">
                📅 MISSION DATELINE INDEX // {current_day.upper()}
            </div>
            """,
            unsafe_allow_html=True
        )
        
        df_day_pool = df_target_segment[df_target_segment['FormattedDate'] == current_day]
        day_variables = df_day_pool['GeoTag'].unique()
        
        for current_var in day_variables:
            st.markdown(f'<div class="variable-sub-banner">▶ {current_var.upper()}</div>', unsafe_allow_html=True)
            
            df_target_cluster = df_day_pool[df_day_pool['GeoTag'] == current_var]
            row_count = len(df_target_cluster)
            
            for i in range(0, row_count, 6):
                cols = st.columns(6)
                
                for j in range(6):
                    if i + j < row_count:
                        idx = df_target_cluster.index[i + j]
                        row = df_target_cluster.loc[idx]
                        
                        event_type = str(row.get('Event', 'TACTICAL LOG')).upper()
                        summary_str = str(row.get('Summary', ''))
                        source_link = str(row.get('Source', 'https://www.psyopoly.pro/middle-east'))
                        
                        with cols[j]:
                            st.markdown(
                                f"""
                                <div class="tactical-grid-card">
                                    <div class="card-content-wrapper">
                                        <div class="card-tag-header">{event_type}</div>
                                        <div class="card-body-text">{summary_str}</div>
                                    </div>
                                    <a href="{source_link}" target="_blank" class="intercept-btn">INTERCEPT RECORD</a>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )


# ==========================================
# 📡 GEOPOLITICS-OSINT CONSOLE RENDERER
# ==========================================
def render_psyopoly_viewer(df_actions):
    st.markdown(
        """
        <style>
        /* Cyber Metallic Outbound Link Asset */
        .psyopoly-outbound-link {
            color: #facc15;
            text-decoration: none;
            font-family: 'Courier New', monospace;
            font-size: 13px;
            font-weight: bold;
            letter-spacing: 1.5px;
            display: inline-block;
            margin-top: 15px;
            margin-bottom: 30px;
            padding: 8px 20px;
            border: 1px solid rgba(250, 204, 21, 0.4);
            border-radius: 4px;
            background: linear-gradient(135deg, rgba(250, 204, 21, 0.1) 0%, rgba(15, 23, 42, 0.8) 100%);
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2), inset 0 1px 0 rgba(250, 204, 21, 0.2);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        .psyopoly-outbound-link:hover {
            background: linear-gradient(135deg, #facc15 0%, #eab308 100%);
            color: #0f172a;
            border-color: #facc15;
            box-shadow: 0 0 15px rgba(250, 204, 21, 0.5);
            transform: translateY(-2px);
        }
        
        /* Command Console Terminal Strip */
        .intel-terminal-banner {
            background: linear-gradient(90deg, #1e293b 0%, #0f172a 50%, #1e293b 100%);
            border: 1px solid rgba(59, 130, 246, 0.3);
            border-left: 4px solid #3b82f6;
            padding: 14px 20px;
            margin-bottom: 10px;
            margin-top: 10px;
            border-radius: 4px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-family: monospace;
            font-size: 13px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
            transition: all 0.3s ease;
        }
        .intel-terminal-banner:hover {
            background: linear-gradient(90deg, #2563eb 0%, #1e293b 50%, #2563eb 100%);
            box-shadow: 0 6px 20px rgba(59, 130, 246, 0.3);
            transform: translateY(-2px);
            border-color: #60a5fa;
        }
        .terminal-tag {
            color: #60a5fa;
            font-weight: bold;
        }
        .intel-terminal-banner:hover .terminal-tag {
            color: #ffffff;
            text-shadow: 0 0 8px rgba(255, 255, 255, 0.5);
        }
        
        /* Deep Spectrum Chronological Master Axis Splitter */
        .dateline-axis-separator {
            background: linear-gradient(90deg, #312e81 0%, #4c1d95 40%, #1e1b4b 100%);
            border-left: 4px solid #c084fc;
            padding: 12px 18px;
            margin: 25px 0 15px 0;
            border-radius: 4px;
            font-family: 'Courier New', monospace;
            font-size: 13px;
            font-weight: bold;
            color: #f3e8ff;
            letter-spacing: 1.5px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
            transition: all 0.3s ease;
        }
        .dateline-axis-separator:hover {
            background: linear-gradient(90deg, #4338ca 0%, #5b21b6 40%, #2e1065 100%);
            box-shadow: 0 6px 18px rgba(168, 85, 247, 0.4);
            transform: translateX(4px);
            border-left: 6px solid #d8b4fe;
        }
        
        /* Low-Profile Variable Anchor Header */
        .variable-sub-banner {
            color: #38bdf8;
            font-family: 'Courier New', monospace;
            font-size: 11px;
            font-weight: bold;
            margin: 20px 0 12px 0;
            padding: 6px 14px;
            background: linear-gradient(90deg, #1e3a8a 0%, rgba(30, 58, 138, 0.1) 100%);
            border-radius: 4px;
            border: 1px solid rgba(56, 189, 248, 0.3);
            border-left: 3px solid #38bdf8;
            display: inline-block;
            letter-spacing: 1px;
            transition: all 0.3s ease;
        }
        .variable-sub-banner:hover {
            background: linear-gradient(90deg, #2563eb 0%, rgba(37, 99, 235, 0.2) 100%);
            color: #ffffff;
            transform: translateX(4px);
            box-shadow: 0 2px 10px rgba(56, 189, 248, 0.3);
        }
        
        /* High-Density Tactical Grid Card Wrapper */
        .tactical-grid-card {
            background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
            border: 1px solid rgba(148, 163, 184, 0.2);
            border-radius: 6px;
            padding: 14px 12px 12px 12px;
            height: 245px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            margin-bottom: 15px;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        .tactical-grid-card:hover {
            border-color: rgba(168, 85, 247, 0.6);
            background: linear-gradient(135deg, #334155 0%, #1e293b 100%);
            box-shadow: 0 8px 25px rgba(168, 85, 247, 0.25);
            transform: translateY(-3px);
        }
        .card-content-wrapper {
            flex-grow: 1;
            display: flex;
            flex-direction: column;
        }
        .card-tag-header {
            font-family: 'Courier New', monospace;
            font-size: 9px;
            font-weight: bold;
            color: #60a5fa;
            background: linear-gradient(90deg, rgba(59, 130, 246, 0.2) 0%, rgba(59, 130, 246, 0.05) 100%);
            border: 1px solid rgba(96, 165, 250, 0.4);
            padding: 3px 8px;
            border-radius: 3px;
            align-self: flex-start;
            margin-bottom: 12px;
            letter-spacing: 0.5px;
            transition: all 0.3s ease;
        }
        .tactical-grid-card:hover .card-tag-header {
            color: #d8b4fe;
            background: linear-gradient(90deg, rgba(168, 85, 247, 0.2) 0%, rgba(168, 85, 247, 0.05) 100%);
            border-color: rgba(216, 180, 254, 0.5);
        }
        .card-body-text {
            font-size: 13px;
            color: #f1f5f9;
            line-height: 1.5;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            overflow: hidden;
            text-overflow: ellipsis;
            display: -webkit-box;
            -webkit-line-clamp: 6;
            -webkit-box-orient: vertical;
        }
        
        /* Direct Action Intercept Control */
        .intercept-btn {
            display: block;
            width: 100%;
            text-align: center;
            background: linear-gradient(180deg, #334155 0%, #1e293b 100%);
            color: #cbd5e1;
            padding: 8px 0;
            margin-top: 12px;
            border-radius: 4px;
            text-decoration: none;
            font-family: 'Courier New', monospace;
            font-size: 10px;
            font-weight: bold;
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
            border: 1px solid rgba(148, 163, 184, 0.4);
            letter-spacing: 0.5px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        .intercept-btn:hover {
            background: linear-gradient(90deg, #3b82f6 0%, #8b5cf6 100%);
            color: #ffffff;
            border-color: transparent;
            box-shadow: 0 4px 12px rgba(139, 92, 246, 0.4);
            text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    # Isolate Psyopoly variables
    df_psy = df_actions[df_actions['Actor'] == 'Psyopoly/West Asia'].copy()
    
    if not df_psy.empty:
        # Pre-process time matrix safely
        df_psy['DateTime'] = pd.to_datetime(df_psy['Date'], errors='coerce')
        df_psy = df_psy.sort_values(by='DateTime', ascending=False)
        df_psy['GeoTag'] = df_psy['Summary'].apply(classify_geopolitical_variable)
        df_psy['FormattedDate'] = df_psy['Date'].apply(format_intel_date)
        
        # Pull Year and Month integers for our logical archive buckets
        df_psy['Year'] = df_psy['DateTime'].dt.year
        df_psy['Month_Num'] = df_psy['DateTime'].dt.month
        
        # ------------------------------------------
        # 🚨 MAIN TERMINAL BANNER & OUTBOUND LINK
        # ------------------------------------------
        st.markdown(
            f"""
            <div class="intel-terminal-banner">
                <div><span class="terminal-tag">ORCHESTRATOR:</span> LIVE GRID INTERCEPTOR</div>
                <div><span class="terminal-tag">MONITORED PAYLOADS:</span> {len(df_psy)} ACTIVE CORES</div>
            </div>
            
            <div style="text-align: center;">
                <a href="https://www.psyopoly.pro/middle-east" target="_blank" class="psyopoly-outbound-link">
                    [PSYOPOLY - MIDDLE EAST MONITOR]
                </a>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # ------------------------------------------
        # 📁 CHRONOLOGICAL ARCHIVE ENGINE (Moved to Top)
        # ------------------------------------------
        st.markdown("### 📁 Strategic Intelligence Archives")
        st.caption("Access non-active multi-theater intelligence payloads segregated by calendar lifecycle.")
        
        # Set up absolute core year tracking structure (2026 - 2030)
        archive_years = ["2026", "2027", "2028", "2029", "2030"]
        year_tabs = st.tabs([f"📂 {yr}" for yr in archive_years])
        
        # Calendar map array
        all_months_map = {
            1: "January", 2: "February", 3: "March", 4: "April", 5: "May", 6: "June",
            7: "July", 8: "August", 9: "September", 10: "October", 11: "November", 12: "December"
        }
        
        for idx, year_str in enumerate(archive_years):
            target_year = int(year_str)
            
            with year_tabs[idx]:
                # Enforce rule: 2026 starts directly from June, others use a standard calendar year
                if target_year == 2026:
                    visible_months = {k: v for k, v in all_months_map.items() if k >= 6}
                else:
                    visible_months = all_months_map
                
                # Render clean row of month sub-tabs when the year folder is accessed
                month_tabs = st.tabs([f"📅 {name}" for name in visible_months.values()])
                
                for m_idx, (month_num, month_name) in enumerate(visible_months.items()):
                    with month_tabs[m_idx]:
                        # Filter rows matching this exact year and month frame
                        df_archive_segment = df_psy[(df_psy['Year'] == target_year) & (df_psy['Month_Num'] == month_num)]
                        
                        if not df_archive_segment.empty:
                            st.markdown(
                                f"""
                                <div class="intel-terminal-banner" style="border-left-color: #a855f7; border-color: rgba(168, 85, 247, 0.3);">
                                    <div><span class="terminal-tag" style="color: #c084fc;">ARCHIVE RETRIEVAL:</span> {month_name.upper()} {target_year}</div>
                                    <div><span class="terminal-tag" style="color: #c084fc;">RECOVERED RECORDINGS:</span> {len(df_archive_segment)} LOGS</div>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )
                            # Render the matching segments utilizing the exact structural format styles
                            render_tactical_grid_matrix(df_archive_segment)
                        else:
                            st.info(f"No intelligence payloads recorded for {month_name} {target_year}.")
        
        # ------------------------------------------
        # 📡 LIVE INTERCEPTOR VIEW (Recent Feed)
        # ------------------------------------------
        st.markdown("<br><hr style='border: 1px solid #1e293b;'><br>", unsafe_allow_html=True)
        st.markdown("### 🔴 Latest Active Intelligence Logs")
        st.caption("Chronological stream of all recently intercepted payloads.")
        
        # Render the standard dynamic live view feed below the archives
        render_tactical_grid_matrix(df_psy)
        
    else:
        st.warning("⚠️ Zero intelligence logs fetched for tracking segment inside the data pool.")