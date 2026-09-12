import os
import base64
import requests
import pandas as pd
import streamlit as st
from datetime import datetime
API_URL = os.getenv("API_URL", "https://saveaserving.onrender.com")
st.set_page_config(
    page_title="ChefEngine | AI Restaurant Operations",
    page_icon="🍳",
    layout="wide"
)

# --- INITIALIZE SESSION STATE FOR VIEW TOGGLE ---
if "show_copilot" not in st.session_state:
    st.session_state.show_copilot = False

# --- LOAD DATASET DYNAMICALLY ---
@st.cache_data
def load_item_catalog():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    possible_paths = [
        os.path.join(base_dir, "data", "raw", "restaurant_synthetic_data.csv"),
        os.path.join(base_dir, "data", "raw", "raw_restaurant_demand.csv"),
        os.path.join(base_dir, "data", "restaurant_synthetic_data.csv"),
        os.path.join(base_dir, "restaurant_synthetic_data.csv"),
        "data/raw/restaurant_synthetic_data.csv",
        "data/raw/raw_restaurant_demand.csv"
    ]
    
    file_path = None
    for p in possible_paths:
        if os.path.exists(p):
            file_path = p
            break
            
    if not file_path:
        raise FileNotFoundError("Could not locate CSV dataset in 'data/raw/'.")

    df = pd.read_csv(file_path)
    catalog = df.groupby('item_name').agg({
        'selling_price': 'mean',
        'ingredient_cost': 'mean',
        'ingredient_stock': 'mean',
        'quantity_sold': 'mean'
    }).reset_index()
    
    catalog_dict = {}
    for _, row in catalog.iterrows():
        catalog_dict[row['item_name']] = {
            "price": round(float(row['selling_price']), 2),
            "cost": round(float(row['ingredient_cost']), 2),
            "stock": int(round(row['ingredient_stock'])),
            "base_demand": round(float(row['quantity_sold']), 1)
        }
    return catalog_dict

ITEM_CATALOG = load_item_catalog()

# --- FETCH LIVE WEATHER & TIME AUTOMATICALLY ---
@st.cache_data(ttl=600)
def get_live_weather_and_time(lat=12.9716, lon=77.5946):
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,rain,is_day,weather_code"
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            data = res.json()["current"]
            temp = float(data["temperature_2m"])
            is_rainy = 1 if float(data["rain"]) > 0.0 else 0
            is_night = 0 if int(data["is_day"]) == 1 else 1
            return temp, is_rainy, is_night
    except Exception:
        pass
    return 24.0, 0, 0

live_temp, live_rainy, live_night = get_live_weather_and_time()

# --- HELPER TO CONVERT LOCAL IMAGE TO BASE64 ---
def get_image_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return ""

bg_css_url = "https://images.unsplash.com/photo-1504674900247-0877df9cc836?auto=format&fit=crop&w=1600&q=80"

# --- VIBRANT WARM CULINARY PRODUCTION THEME CSS WITH ENLARGED HERO BANNER ---
st.markdown(f"""
<style>
    .stApp {{
        background-color: #fffaf5 !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        color: #2d1810;
    }}
    
    /* Enlarged Production Hero Banner with Blurred Background & Dark Gradient Overlay */
    .hero-banner {{
        position: relative;
        width: 100%;
        min-height: 220px;
        border-radius: 16px;
        overflow: hidden;
        padding: 60px 40px;
        margin-bottom: 24px;
        box-shadow: 0 14px 40px rgba(0, 0, 0, 0.3);
        display: flex;
        justify-content: space-between;
        align-items: center;
    }}
    .hero-banner::before {{
        content: "";
        position: absolute;
        top: 0; left: 0; right: 0; bottom: 0;
        background-image: url("{bg_css_url}");
        background-size: cover;
        background-position: center;
        filter: blur(6px) brightness(0.6);
        transform: scale(1.1);
        z-index: 1;
    }}
    .hero-content {{
        position: relative;
        z-index: 2;
        display: flex;
        justify-content: space-between;
        align-items: center;
        width: 100%;
    }}

    div.stButton > button {{
        border-radius: 10px !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        padding: 0.6rem 1.2rem !important;
        transition: all 0.2s ease-in-out !important;
        border: 1px solid #ea580c !important;
        background: linear-gradient(135deg, #f97316 0%, #ea580c 100%) !important;
        color: #ffffff !important;
        box-shadow: 0 4px 12px rgba(234, 88, 12, 0.3);
        width: 100%;
    }}
    div.stButton > button:hover {{
        transform: translateY(-1px);
        background: linear-gradient(135deg, #ea580c 0%, #c2410c 100%) !important;
        box-shadow: 0 6px 16px rgba(234, 88, 12, 0.4) !important;
        color: #ffffff !important;
    }}
    div.stButton > button p, div.stButton > button span {{
        color: #ffffff !important;
    }}
    .metric-card {{
        background-color: #ffffff; 
        border: 1px solid #fed7aa; 
        border-radius: 12px;
        padding: 20px; 
        text-align: center; 
        box-shadow: 0 4px 6px -1px rgba(234, 88, 12, 0.05);
        transition: all 0.2s ease;
    }}
    .metric-card:hover {{ 
        border-color: #ea580c;
        box-shadow: 0 8px 12px -2px rgba(234, 88, 12, 0.15); 
    }}
    .metric-title {{ color: #9a3412; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; }}
    .metric-value {{ font-size: 2.2rem; font-weight: 800; color: #7c2d12; margin-top: 6px; }}
    .badge-warning {{ background-color: #ffedd5; color: #c2410c; padding: 14px 18px; border-radius: 10px; font-weight: 600; border: 1px solid #fed7aa; display: flex; align-items: center; gap: 10px; }}
    .badge-ok {{ background-color: #d1fae5; color: #065f46; padding: 14px 18px; border-radius: 10px; font-weight: 600; border: 1px solid #a7f3d0; display: flex; align-items: center; gap: 10px; }}
    section[data-testid="stSidebar"] {{
        background-color: #fff3ec !important;
        border-right: 1px solid #ffd6b3;
    }}
    section[data-testid="stSidebar"] .stMarkdown h3, 
    section[data-testid="stSidebar"] .stMarkdown h4,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] .stCheckbox span {{
        color: #431407 !important;
    }}
    section[data-testid="stSidebar"] hr {{
        border-color: #fed7aa;
    }}
    
    /* Enhanced Textarea Styling */
    .stTextArea textarea {{
        background-color: #ffffff !important;
        border: 1px solid #fed7aa !important;
        border-radius: 12px !important;
        padding: 12px !important;
        font-size: 0.95rem !important;
        color: #2d1810 !important;
        box-shadow: 0 2px 4px rgba(234, 88, 12, 0.04) !important;
    }}
    .stTextArea textarea:focus {{
        border-color: #ea580c !important;
        box-shadow: 0 0 0 2px rgba(234, 88, 12, 0.2) !important;
    }}
</style>
""", unsafe_allow_html=True)

# --- REFINED SIDEBAR WITH FOOD THUMBNAIL ---
with st.sidebar:
    st.markdown("### 📋 Operations Control")
    st.image(
        "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?auto=format&fit=crop&w=600&q=80",
        caption="Professional Kitchen Operations",
        use_container_width=True
    )
    
    selected_item = st.selectbox("Select Menu Item", sorted(list(ITEM_CATALOG.keys())))
    item_defaults = ITEM_CATALOG[selected_item]

    st.markdown("---")
    st.markdown("#### 💰 Financial Parameters")
    selling_price = st.number_input("Selling Price (₹)", value=item_defaults["price"], step=5.0)
    ingredient_cost = st.number_input("Ingredient Cost (₹)", value=item_defaults["cost"], step=5.0)

    st.markdown("---")
    st.markdown("#### 🌦️ Live Environmental Telemetry")
    weather_desc = "🌧️ Rainy & Wet" if live_rainy else ("☀️ Hot & Clear" if live_temp > 28 else "🌤️ Pleasant")
    time_desc = "🌙 Night Service" if live_night else "☀️ Daytime Service"
    st.info(f"**Temp:** {live_temp}°C\n\n**Condition:** {weather_desc}\n\n**Period:** {time_desc}")

    st.markdown("---")
    available_stock = st.number_input("Current Stock (Portions)", value=item_defaults["stock"], step=5)

    st.markdown("---")
    event_today = st.checkbox("Special Event / Holiday", value=True)
    promo_today = st.checkbox("Promotional Discount Active", value=False)
    override_demand = st.checkbox("Manual Demand Override")

    manual_demand = st.number_input("Set Custom Demand", value=item_defaults["base_demand"]) if override_demand else None

# --- ENLARGED PRODUCTION HERO BANNER ---
btn_label = "🔙 Dashboard" if st.session_state.show_copilot else "🤖 Chef Copilot"

st.markdown(f"""
<div class="hero-banner">
    <div class="hero-content">
        <div>
            <h1 style="margin: 0; font-size: 2.5rem; color: #ffffff; font-weight: 800; letter-spacing: -0.025em; text-shadow: 0 3px 12px rgba(0,0,0,0.7);">🍳 ChefEngine AI Ops</h1>
            <p style="margin: 8px 0 0 0; color: #fed7aa; font-size: 1.2rem; font-weight: 600; text-shadow: 0 2px 8px rgba(0,0,0,0.7);">Dynamic Demand Forecasting & Newsvendor Inventory Suite</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

col_spacer, col_btn = [st.columns([5, 1])[0], st.columns([5, 1])[1]]
with col_btn:
    if st.button(btn_label, use_container_width=True):
        st.session_state.show_copilot = not st.session_state.show_copilot
        st.rerun()

st.markdown("<div style='margin: 16px 0; border-bottom: 1px solid #fed7aa;'></div>", unsafe_allow_html=True)

# --- CONDITIONAL VIEW ROUTING ---
if not st.session_state.show_copilot:
    st.markdown("###  Operational Recommendation & Executive Summary")
    
    if st.button(" Calculate Optimal Prep Target", use_container_width=True):
        payload = {
            "item_id": "ITEM001",
            "item_name": selected_item,
            "selling_price": selling_price,
            "ingredient_cost": ingredient_cost,
            "available_stock": available_stock,
            "predicted_demand": manual_demand if override_demand else None,
            "day_of_week": datetime.now().weekday(),
            "event": 1 if event_today else 0,
            "promotion": 1 if promo_today else 0,
            "temperature": live_temp,
            "is_rainy": live_rainy,
            "is_night": live_night
        }
        
        try:
            res = requests.post(f"{API_URL}/predict-and-optimize", json=payload)
            
            if res.status_code == 200:
                data = res.json()
                opt = data["optimization_details"]
                gross_profit = round(selling_price - ingredient_cost, 2)
                gross_margin = round((gross_profit / selling_price) * 100, 1) if selling_price > 0 else 0.0
                
                st.markdown("<div style='margin: 12px 0;'></div>", unsafe_allow_html=True)
                m1, m2, m3 = st.columns(3)
                
                with m1:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-title">ML Forecast</div>
                        <div class="metric-value">{data['calculated_demand']}</div>
                        <small style="color:#9a3412;">Auto: {live_temp}°C | {weather_desc}</small>
                    </div>
                    """, unsafe_allow_html=True)
                    
                with m2:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-title">Optimal Q*</div>
                        <div class="metric-value" style="color:#ea580c;">{opt['unconstrained_prep_qty']}</div>
                        <small style="color:#9a3412;">Unconstrained Target</small>
                    </div>
                    """, unsafe_allow_html=True)
                    
                with m3:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-title">Final Prep Limit</div>
                        <div class="metric-value" style="color:#059669;">{opt['final_recommended_prep']}</div>
                        <small style="color:#9a3412;">Stock Cap</small>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("<div style='margin: 20px 0;'></div>", unsafe_allow_html=True)
                
                if opt['stock_status'] == "INSUFFICIENT_STOCK":
                    st.markdown(f"""
                    <div class="badge-warning">
                        <span>⚠️</span> <span><strong>INVENTORY SHORTAGE:</strong> Need {opt['shortage_qty']} more units to cover expected target!</span>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div class="badge-ok">
                        <span>✅</span> <span><strong>INVENTORY ADEQUATE:</strong> Available stock covers target recommendation.</span>
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown("<div style='margin: 24px 0;'></div>", unsafe_allow_html=True)
                
                # --- STRUCTURED EXECUTIVE SUMMARY CONTAINER ---
                st.markdown(f"""
                <div style="background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 14px; padding: 28px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);">
                    <h2 style="margin-top: 0; color: #1e3a8a; font-size: 1.5rem; font-weight: 700;">Executive Summary – {selected_item}</h2>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
                
                col_table, col_insights = st.columns([1, 1])
                
                with col_table:
                    summary_df = pd.DataFrame({
                        "Metric": [
                            "Selling Price",
                            "Cost per Unit",
                            "Gross Profit per Unit",
                            "Baseline Forecast Demand",
                            "Target Optimal Prep (Q*)",
                            "Final Constrained Prep",
                            "Inventory Status"
                        ],
                        "Value": [
                            f"₹{selling_price:.1f}",
                            f"₹{ingredient_cost:.1f}",
                            f"₹{gross_profit:.2f}",
                            f"{data['calculated_demand']} units",
                            f"{opt['unconstrained_prep_qty']} units",
                            f"{opt['final_recommended_prep']} units",
                            f"{opt['stock_status']}"
                        ]
                    })
                    st.dataframe(summary_df, use_container_width=True, hide_index=True)
                    
                with col_insights:
                    st.markdown(f"""
                    <div style="background: #ffffff; border: 1px solid #e2e8f0; padding: 20px; border-radius: 12px;">
                        <h4 style="margin-top:0; color: #1e3a8a; font-size: 1.1rem;">Key Insights</h4>
                        <ul style="margin: 0; padding-left: 20px; color: #334155; font-size: 0.92rem; line-height: 1.6;">
                            <li><strong>Profitability:</strong> Each {selected_item} plate contributes a healthy ₹{gross_profit:.2f} gross profit, representing a <strong>{gross_margin}% margin</strong> over cost.</li>
                            <li><strong>Demand Gap:</strong> The constrained preparation ({opt['final_recommended_prep']} units) falls short of the forecasted demand ({data['calculated_demand']} units).</li>
                            <li><strong>Stock Issue:</strong> The <code>{opt['stock_status']}</code> flag indicates raw-material constraints are limiting production.</li>
                        </ul>
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown("<div style='margin: 24px 0;'></div>", unsafe_allow_html=True)

                # --- CLEAN RECOMMENDATIONS SECTION ---
                st.markdown("""
                <div style="background: #ffffff; border: 1px solid #e2e8f0; padding: 24px; border-radius: 14px;">
                    <h3 style="margin-top:0; color: #1e3a8a; font-size: 1.3rem;">Recommendations</h3>
                    <ol style="margin: 0; padding-left: 20px; color: #334155; font-size: 0.95rem; line-height: 1.7;">
                        <li><strong>Increase Inventory Allocation:</strong> Prioritize procurement of key ingredients to meet at least the baseline forecast demand.</li>
                        <li><strong>Adjust Prep Schedule:</strong> Stagger batch preparation throughout peak operational windows to minimize waste under stock constraints.</li>
                    </ol>
                </div>
                """, unsafe_allow_html=True)

            else:
                st.error("Backend model error.")
                
        except Exception as e:
            st.error(f"Cannot reach FastAPI backend. Error: {e}")
else:
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 14px; margin-bottom: 20px; background: #ffffff; padding: 20px; border-radius: 12px; border: 1px solid #fed7aa;">
        <div style="font-size: 2.2rem;">🤖</div>
        <div>
            <h2 style="margin:0; font-size: 1.5rem; color: #431407;">Head Chef Copilot Workspace</h2>
            <p style="margin:2px 0 0 0; color: #9a3412; font-size: 0.9rem;">Ask natural language what-if scenario questions regarding pricing, discounts, and inventory for <strong>%s</strong></p>
        </div>
    </div>
    """ % selected_item, unsafe_allow_html=True)
    
    # Enhanced Text Area for Manager Prompt
    user_query = st.text_area(
        "Manager Query", 
        value="What if we run a 15% discount tomorrow?",
        height=90,
        placeholder="Type your what-if scenario here (e.g., What if we increase prices by 10% on rainy days?)...",
        key="copilot_full_input"
    )
    
    st.markdown("<div style='margin: 8px 0;'></div>", unsafe_allow_html=True)
    
    if st.button("🤖 Ask Copilot", use_container_width=True):
        payload = {
            "query": user_query,
            "item_name": selected_item,
            "predicted_demand": item_defaults["base_demand"],
            "available_stock": available_stock
        }
        try:
            res = requests.post(f"{API_URL}/copilot/query", json=payload)
            if res.status_code == 200:
                ans = res.json()
                response_text = ans.get('response') or ans.get('answer') or ans.get('result')
                if not response_text:
                    response_text = f"Analysis generated for {selected_item}. Baseline demand is {item_defaults['base_demand']} units."

                st.markdown("""
                <div style="background-color: #ffffff; border: 1px solid #fed7aa; border-left: 4px solid #ea580c; padding: 20px; border-radius: 12px; margin-top: 20px; box-shadow: 0 4px 6px -1px rgba(234,88,12,0.05);">
                    <strong style="color: #ea580c; font-size: 1rem;">🤖 Copilot Insights:</strong>
                </div>
                """, unsafe_allow_html=True)
                st.markdown(response_text)
            else:
                st.error(f"Server returned status {res.status_code}: {res.text}")
        except Exception as e:
            st.error(f"Connection error: {e}")