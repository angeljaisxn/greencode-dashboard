import sys
import os
from io import BytesIO

# ---- FIX PROJECT PATH ----
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
import pandas as pd
import plotly.express as px
import time
import base64



from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.platypus import TableStyle

from ingestion.load_data import load_global_data
from analytics.carbon_metrics import calculate_emission
from analytics.country_analysis import average_country_intensity

ENERGY_PER_TASK = 0.5
CARBON_PRICE_PER_KG = 1.5


def splash_screen():
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    logo_path = os.path.join(BASE_DIR, "assets", "logo.png")

    if not os.path.exists(logo_path):
        st.error(f"❌ Logo not found at: {logo_path}")
        st.stop()

    import base64
    with open(logo_path, "rb") as f:
        encoded_logo = base64.b64encode(f.read()).decode()

    splash_html = f"""
    <style>
    .splash {{
        position: fixed;
        inset: 0;
        background-color: #013220;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        z-index: 9999;
        animation: fadeIn 1.2s ease-in;
    }}

    @keyframes fadeIn {{
        from {{ opacity: 0; }}
        to {{ opacity: 1; }}
    }}

    .logo {{
        animation: glow 2s ease-in-out infinite alternate;
    }}

    @keyframes glow {{
        from {{
            filter: drop-shadow(0 0 6px #00ff99);
        }}
        to {{
            filter: drop-shadow(0 0 25px #00ff99);
        }}
    }}

    .loader {{
        margin-top: 25px;
        border: 6px solid #f3f3f3;
        border-top: 6px solid #00ff99;
        border-radius: 50%;
        width: 48px;
        height: 48px;
        animation: spin 1s linear infinite;
    }}

    @keyframes spin {{
        0% {{ transform: rotate(0deg); }}
        100% {{ transform: rotate(360deg); }}
    }}

    .text {{
        margin-top: 15px;
        font-size: 20px;
        color: white;
        letter-spacing: 1px;
        animation: pulse 1.5s infinite;
    }}

    @keyframes pulse {{
        0% {{ opacity: 0.6; }}
        50% {{ opacity: 1; }}
        100% {{ opacity: 0.6; }}
    }}
    </style>

    <div class="splash">
        <img class="logo" src="data:image/png;base64,{encoded_logo}" width="220"/>
        <div class="text">GreenCode Initializing...</div>
        <div class="loader"></div>
    </div>
    """

    st.markdown(splash_html, unsafe_allow_html=True)
    time.sleep(3)

if "splash_done" not in st.session_state:
    splash_screen()
    st.session_state.splash_done = True
    st.rerun()


# ---------------- LOAD DATA ----------------
@st.cache_data
def load_data():
    df = load_global_data()
    df["country_lower"] = df["country"].str.lower()
    df["timestamp"] = pd.to_datetime(df["timestamp"])  # ✅ FIX
    return df

df = load_data()
df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
df = df.dropna(subset=["timestamp"])

countries = sorted(df["country"].unique())

# ---------------- PAGE SETUP ----------------
st.set_page_config(page_title="GreenCode Global Dashboard", layout="wide")

#----standard look----------
with st.spinner("🌱 GreenCode is initializing carbon data..."):
    time.sleep(2)

##proffesional look in website##--------------
progress = st.progress(0)

for i in range(100):
    time.sleep(0.02)
    progress.progress(i + 1)

progress.empty()

st.title("🌍 GreenCode – Global Carbon Pollution Analyzer")
st.write("AI-based system to analyze, compare, and reduce carbon pollution globally")
st.markdown("---")

# =========================================================
# 🌍 LIVE GLOBAL CARBON STATUS
# =========================================================
st.header("🌍 Live Global Carbon Pollution Status")

global_avg = df.groupby("country")["carbon_intensity_gCO2_per_kWh"].mean().reset_index()

q_low = global_avg["carbon_intensity_gCO2_per_kWh"].quantile(0.33)
q_high = global_avg["carbon_intensity_gCO2_per_kWh"].quantile(0.66)

def classify_level(value):
    if value >= q_high:
        return "High"
    elif value >= q_low:
        return "Moderate"
    return "Low"

global_avg["Level"] = global_avg["carbon_intensity_gCO2_per_kWh"].apply(classify_level)

col1, col2, col3 = st.columns(3)

high_df = (
    global_avg[global_avg["Level"] == "High"]
    .head(5)
    .reset_index(drop=True)
)
high_df = high_df.rename(
    columns={"carbon_intensity_gCO2_per_kWh": "Carbon Intensity (gCO₂/kWh)"}
)


high_df.index = high_df.index + 1
high_df.index.name = "Sl.No"

col1.dataframe(high_df)

moderate_df = (
    global_avg[global_avg["Level"] == "Moderate"]
    .head(5)
    .reset_index(drop=True)
)

moderate_df = moderate_df.rename(
    columns={"carbon_intensity_gCO2_per_kWh": "Carbon Intensity (gCO₂/kWh)"}
)


moderate_df.index = moderate_df.index + 1
moderate_df.index.name = "Sl.No"

col2.dataframe(moderate_df)

low_df = (
    global_avg[global_avg["Level"] == "Low"]
    .head(5)
    .reset_index(drop=True)
)
low_df = low_df.rename(
    columns={"carbon_intensity_gCO2_per_kWh": "Carbon Intensity (gCO₂/kWh)"}
)

low_df.index = low_df.index + 1
low_df.index.name = "Sl.No"

col3.dataframe(low_df)

# 🌍 World Map
fig = px.choropleth(
    global_avg,
    locations="country",
    locationmode="country names",
    color="Level",
    color_discrete_map={"High":"red","Moderate":"orange","Low":"green"}
)
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# =========================================================
# 🔎 COUNTRY ANALYSIS
# =========================================================
country = st.selectbox("Search & select country:", countries)

avg_intensity = average_country_intensity(df, country)
normal_emission = calculate_emission(avg_intensity, ENERGY_PER_TASK)
green_emission = normal_emission * 0.6
saved = normal_emission - green_emission

green_score = max(0, 100 - avg_intensity / 4)
carbon_cost = (saved / 1000) * CARBON_PRICE_PER_KG
reduction_percentage = (saved / normal_emission) * 100
country_level = classify_level(avg_intensity)




# ================= TREND CALCULATION =================
trend_data = df[df["country"] == country].sort_values("timestamp")

avg_7_day = trend_data.tail(7)["carbon_intensity_gCO2_per_kWh"].mean()
avg_30_day = trend_data.tail(30)["carbon_intensity_gCO2_per_kWh"].mean()

if avg_7_day > avg_30_day:
    trend_status = "Increasing"
else:
    trend_status = "Decreasing"

# 🚦 Indicator
if country_level == "High":
    st.error("🔴 HIGH Carbon Zone")
elif country_level == "Moderate":
    st.warning("🟠 MODERATE Carbon Zone")
else:
    st.success("🟢 LOW Carbon Zone")

# Results
st.success(f"🌱 Results for {country}")
st.write(f"Normal Emission: {normal_emission:.2f} gCO₂")
st.write(f"Green Emission: {green_emission:.2f} gCO₂")
st.write(f"Carbon Saved: {saved:.2f} gCO₂")
st.metric("🌱 Green Score", f"{green_score:.1f}/100")
st.metric("📉 Reduction (%)", f"{reduction_percentage:.2f}%")
st.write(f"💰 Cost Saved: ₹{carbon_cost:.2f}")

st.markdown("---")
st.header("📉 Carbon Pollution Trend")

trend_option = st.radio(
    "Select Trend Period:",
    ["📅 Week", "🗓️ Month"],
    horizontal=True
)

# # Convert UI choice to days
trend_days = 7 if "Week" in trend_option else 30



trend_data = (
    df[df["country"] == country]
    .sort_values("timestamp")
    .tail(trend_days * 24)
)

daily_trend = (
    trend_data
    .groupby(trend_data["timestamp"].dt.date)
    ["carbon_intensity_gCO2_per_kWh"]
    .mean()
)

st.line_chart(daily_trend)

st.subheader("🟢 Green Time Recommendation")

if avg_intensity <= q_low:
    st.success("✅ Best time to execute tasks (Low Carbon)")
elif avg_intensity <= q_high:
    st.warning("⚠️ Acceptable time – optimize execution")
else:
    st.error("⛔ Avoid execution – high carbon period")



# =========================================================
# 📈 HOUR-WISE CARBON ANALYSIS (FIX FOR best_hour)
# =========================================================
selected_day = (
    df[df["country"] == country]
    .sort_values("timestamp")
    .tail(24)
)
# 📊 TREND CALCULATION (UP / DOWN)
trend_start = selected_day["carbon_intensity_gCO2_per_kWh"].iloc[0]
trend_end = selected_day["carbon_intensity_gCO2_per_kWh"].iloc[-1]

trend_change = trend_end - trend_start


if not selected_day.empty:
    best_hour = selected_day.loc[
        selected_day["carbon_intensity_gCO2_per_kWh"].idxmin()
    ]["utc_hour"]

    st.markdown("---")
    st.header("📈 Hour-wise Carbon Pollution")
    st.line_chart(
        selected_day.set_index("utc_hour")["carbon_intensity_gCO2_per_kWh"]
    )
    
    st.success(f"✅ Best Hour to Run Task: {int(best_hour)}:00")
else:
    best_hour = "N/A"
    # 🚨 AUTO TREND ALERT
if trend_change > 0:
    st.error("🚨 ALERT: Carbon pollution trend is increasing")
else:
    st.success("✅ Carbon pollution trend is stable or decreasing")

st.markdown("---")
st.header("📊 Carbon Pollution Trend ")

trend_data = df[df["country"] == country].sort_values("timestamp")

last_7 = trend_data.tail(7)["carbon_intensity_gCO2_per_kWh"].mean()
last_30 = trend_data.tail(30)["carbon_intensity_gCO2_per_kWh"].mean()

st.metric("📅 Weekly Average", f"{last_7:.2f} gCO₂/kWh")
st.metric("🗓️ Monthly Average", f"{last_30:.2f} gCO₂/kWh")

if last_7 > last_30:
    st.error("🚨 Carbon trend is worsening in the last 7 days")
else:
    st.success("✅ Carbon trend is improving")

st.markdown("---")
st.header("🏭 National Carbon Savings (GreenCode Simulation)")

TOTAL_TASKS_PER_DAY = 1_000_000  # simulated national tasks

daily_saved = saved * TOTAL_TASKS_PER_DAY / 1000  # kg CO₂
annual_saved = daily_saved * 365 / 1000           # tonnes CO₂

st.metric("Daily CO₂ Saved", f"{daily_saved:,.2f} kg")
st.metric("Annual CO₂ Saved", f"{annual_saved:,.2f} tonnes")

st.info(
    f"If {country} adopts GreenCode nationwide, "
    f"it can save approximately {annual_saved:,.0f} tonnes of CO₂ annually."
)

# =========================================================
# 🌍 GLOBAL RANK
# =========================================================
rank_df = global_avg.sort_values("carbon_intensity_gCO2_per_kWh").reset_index(drop=True)
rank = rank_df[rank_df["country"] == country].index[0] + 1
st.write(f"🌍 Global Rank: {rank}/{len(rank_df)}")

#  =========================================================
# # ⚖️ COUNTRY COMPARISON
# # =========================================================

st.header("⚖️ Country Comparison (X vs Y)")

c1, c2 = st.columns(2)
with c1:
    country_x = st.selectbox("Country X", countries, index=0)
with c2:
    country_y = st.selectbox("Country Y", countries, index=1)

if st.button("Compare Countries"):
    avg_x = average_country_intensity(df, country_x)
    avg_y = average_country_intensity(df, country_y)

    emission_x = calculate_emission(avg_x, ENERGY_PER_TASK)
    emission_y = calculate_emission(avg_y, ENERGY_PER_TASK)

    if country_x == country_y:
        st.info("ℹ️ Same country selected. Self-comparison shown.")
        diff = 0.0
        percent_diff = 0.0
    else:
        diff = abs(emission_x - emission_y)
        percent_diff = (diff / max(emission_x, emission_y)) * 100

    st.metric("🔄 Carbon Difference (gCO₂)", f"{diff:.2f}")
    st.metric("📊 Percentage Difference (%)", f"{percent_diff:.2f}%")


        # ================= CLEANER COUNTRY ALERT SYSTEM =================

    # Determine cleaner country now
    if avg_x < avg_y:
        cleaner_now = country_x
        cleaner_value = avg_x
    else:
        cleaner_now = country_y
        cleaner_value = avg_y

    # Save previous cleaner country data
    if "prev_cleaner_value" not in st.session_state:
        st.session_state.prev_cleaner_value = cleaner_value
        st.session_state.prev_cleaner_country = cleaner_now

    # 🚨 Alert if cleaner country becomes worse
    if cleaner_value > st.session_state.prev_cleaner_value:
        st.warning(
            f"🔔 ALERT: {cleaner_now} carbon pollution has increased "
            f"from {st.session_state.prev_cleaner_value:.2f} → {cleaner_value:.2f} gCO₂/kWh"
        )

    # Update session memory
    st.session_state.prev_cleaner_value = cleaner_value
    st.session_state.prev_cleaner_country = cleaner_now

        # ================= COLORED SIDE-BY-SIDE BAR CHART =================
    st.markdown("### 📊 Carbon Intensity Comparison ")

    # Decide colors
    if avg_x < avg_y:
        colors_map = {country_x: "green", country_y: "red"}
        best_country = country_x
        reason = f"{country_x} has lower carbon intensity than {country_y}."
    else:
        colors_map = {country_x: "red", country_y: "green"}
        best_country = country_y
        reason = f"{country_y} has lower carbon intensity than {country_x}."

    compare_df = pd.DataFrame({
        "Country": [country_x, country_y],
        "Carbon Intensity (gCO₂/kWh)": [avg_x, avg_y]
    })

    fig = px.bar(
        compare_df,
        x="Country",
        y="Carbon Intensity (gCO₂/kWh)",
        color="Country",
        color_discrete_map=colors_map,
        text_auto=".2f"
    )

    fig.update_layout(
        yaxis_title="Carbon Intensity (gCO₂/kWh)",
        xaxis_title="Country",
        showlegend=False
    )

    st.plotly_chart(fig, use_container_width=True)

    # ✅ Explanation
    st.success(f"✅ Best Country: {best_country}")
    st.info(f"📌 Reason: {reason}")


    # ================= DETAILED COUNTRY COMPARISON =================
    st.markdown("### 🧾 Detailed Country Comparison")

    st.write(f"**{country_x} Carbon Intensity:** {avg_x:.2f} gCO₂/kWh")
    st.write(f"**{country_y} Carbon Intensity:** {avg_y:.2f} gCO₂/kWh")

    level_x = classify_level(avg_x)
    level_y = classify_level(avg_y)

    st.write(f"**{country_x} Carbon Level:** {level_x}")
    st.write(f"**{country_y} Carbon Level:** {level_y}")



    # ================= BEST COUNTRY DECISION =================
    if avg_x < avg_y:
        best_country = country_x
        worst_country = country_y
        reason = (
            f"{worst_country} has higher carbon pollution due to "
            f"greater dependence on fossil-fuel-based power generation."
        )
        
    elif avg_y < avg_x:
        best_country = country_y
        worst_country = country_x
        reason = (
            f"{worst_country} produces more carbon emissions because of "
            f"carbon-intensive energy sources."
        )
    else:
        best_country = "Both countries"
        reason = "Both countries have nearly equal carbon intensity."

    st.markdown("---")
    st.success(f"🏆 Best Country for Green Execution: **{best_country}**")

    if best_country != "Both countries":
        st.warning(f"🔴 Why **{worst_country}** has higher carbon pollution:\n\n{reason}")



# =========================================================
# 🔁 RECOMMENDATION
# =========================================================
def get_dynamic_recommendation(val):
    if val >= q_high:
        return "High carbon level. Postpone tasks."
    elif val >= q_low:
        return "Moderate level. Optimize scheduling."
    return "Low level. Safe to execute."

if "prev_level" not in st.session_state:
    st.session_state.prev_level = country_level

if st.session_state.prev_level != country_level:
    st.warning(
        f"🚨 ALERT: {country} moved from "
        f"{st.session_state.prev_level} → {country_level}"
    )

st.session_state.prev_level = country_level

st.markdown("---")
st.header("🧪 What-If Carbon Simulation")

delay_hours = st.slider("Delay task by hours:", 0, 6, 2)

simulated_emission = normal_emission * (1 - delay_hours * 0.05)

st.write(f"📉 Simulated Emission: {simulated_emission:.2f} gCO₂")
st.write(f"🌱 Extra Carbon Saved: {(normal_emission - simulated_emission):.2f} gCO₂")

st.markdown("---")
st.header("🏭 National-Scale Carbon Savings")

tasks_per_day = st.number_input(
    "Estimated tasks per day:", min_value=100, value=1000, step=100
)

daily_savings = saved * tasks_per_day
yearly_savings = daily_savings * 365 / 1000  # kg CO₂

st.metric("🌍 Daily CO₂ Saved (g)", f"{daily_savings:,.0f}")
st.metric("🌍 Yearly CO₂ Saved (kg)", f"{yearly_savings:,.2f}")

st.markdown("---")
st.header("📋 Country Carbon Health Scorecard")

if avg_intensity <= q_low:
    grade = "A"
    remark = "Excellent – Low carbon footprint"
elif avg_intensity <= q_high:
    grade = "B"
    remark = "Moderate – Needs optimization"
else:
    grade = "C"
    remark = "Poor – High carbon footprint"

st.metric("Carbon Grade", grade)
st.write(f"📌 Assessment: {remark}")


# =========================================================
# 📄 PDF REPORT (YOUR ORIGINAL STRATEGY – FIXED)
# =========================================================

def generate_pdf():
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()
    elements = []

    # ---------------- TITLE ----------------
    elements.append(
        Paragraph("<b>GreenCode – Global Carbon Pollution Analysis Report</b>", styles["Title"])
    )
    elements.append(Spacer(1, 20))

    # ---------------- EXECUTIVE SUMMARY ----------------
    elements.append(Paragraph("<b>1. Executive Summary</b>", styles["Heading2"]))
    elements.append(Spacer(1, 10))

    summary_table = Table([
        ["Metric", "Value"],
        ["Country", country],
        ["Global Rank", f"{rank} / {len(rank_df)}"],
        ["Green Score", f"{green_score:.1f} / 100"],
        ["Carbon Reduction (%)", f"{reduction_percentage:.2f}%"],
        ["Best Execution Hour", f"{best_hour}:00"]
    ], colWidths=[200, 250])

    summary_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.darkgreen),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ("FONT", (0, 0), (-1, 0), "Helvetica-Bold")
    ]))

    elements.append(summary_table)
    elements.append(Spacer(1, 20))

    # ---------------- EMISSION ANALYSIS ----------------
    elements.append(Paragraph("<b>2. Carbon Emission Analysis</b>", styles["Heading2"]))
    elements.append(Spacer(1, 10))

    emission_table = Table([
        ["Type", "Value (gCO2)"],
        ["Normal Execution", f"{normal_emission:.2f} "],
        ["GreenCode Execution", f"{green_emission:.2f} "],
        ["Carbon Saved", f"{saved:.2f} "],
        ["Estimated Cost Saved", f"{carbon_cost:.2f}"]
    ], colWidths=[200, 250])

    emission_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.darkgreen),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ("FONT", (0, 0), (-1, 0), "Helvetica-Bold")
    ]))

    elements.append(emission_table)
    elements.append(Spacer(1, 20))

    # ---------------- TREND ANALYSIS ----------------
    trend_status = "Increasing" if avg_7_day > avg_30_day else "Decreasing / Stable"

    elements.append(Paragraph("<b>3. Carbon Trend Analysis</b>", styles["Heading2"]))
    elements.append(Spacer(1, 10))

    trend_table = Table([
        ["Period", "Avg Carbon Intensity"],
        ["Last 7 Days", f"{avg_7_day:.2f} gCO2/kWh"],
        ["Last 30 Days", f"{avg_30_day:.2f} gCO2/kWh"],
        ["Trend Status", trend_status]
    ], colWidths=[200, 250])

    trend_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.darkgreen),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ("FONT", (0, 0), (-1, 0), "Helvetica-Bold")
    ]))

    elements.append(trend_table)
    elements.append(Spacer(1, 20))

    # ---------------- SUSTAINABILITY IMPACT ----------------
    impact_level = country_level
    elements.append(Paragraph("<b>4. Sustainability Impact</b>", styles["Heading2"]))

    impact_table = Table([
         ["Indicator", "Assessment"],
        ["Carbon Intensity", f"{avg_intensity:.2f} gCO2/kWh"],
        ["Impact Level", impact_level],
        ["Recommendation", get_dynamic_recommendation(avg_intensity)]
    ], colWidths=[200, 250])

    impact_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.darkgreen),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ("FONT", (0, 0), (-1, 0), "Helvetica-Bold")
    ]))

    elements.append(impact_table)

    # ---------------- BUILD PDF ----------------
    doc.build(elements)
    buffer.seek(0)
    return buffer

st.download_button(
    "⬇️ Download PDF Report",
    generate_pdf(),
    file_name=f"{country}_carbon_report.pdf",
    mime="application/pdf"
)
st.markdown("---")


scorecard_data = [
    (1, "Carbon Level", country_level),
    (2, "Global Rank", f"{rank} / {len(rank_df)}"),
    (3, "Trend Status", trend_status),
    (4, "Best Execution Time", f"{int(best_hour)}:00" if best_hour != "N/A" else "N/A"),
    (5, "Recommendation", get_dynamic_recommendation(avg_intensity)),
]
st.markdown("""
<style>
.scorecard-table {
    width: 100%;
    border-collapse: collapse;
}
.scorecard-table th, .scorecard-table td {
    border: 1px solid #555;
    padding: 10px;
}
.scorecard-table th {
    background-color: #1f4f3b;
    color: white;
    text-align: center;
}
.scorecard-table td:nth-child(1) {
    text-align: center;   /* Sl.No centered */
    font-weight: bold;
}
.scorecard-table td:nth-child(2) {
    font-weight: 600;
}
</style>

<h3>📊 Country Carbon Health Scorecard</h3>

<table class="scorecard-table">
<tr>
    <th>Sl.No</th>
    <th>Indicator</th>
    <th>Assessment</th>
</tr>
""" + "".join([
    f"<tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td></tr>"
    for row in scorecard_data
]) + "</table>", unsafe_allow_html=True)
