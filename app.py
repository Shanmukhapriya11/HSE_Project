"""HSE Risk Intelligence — synthetic analytics and decision-support demo."""

from __future__ import annotations

from datetime import date

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler


st.set_page_config(page_title="HSE Risk Intelligence", page_icon=":material/health_and_safety:", layout="wide")

SEED = 42
LOCATIONS = ["Laboratory A", "Manufacturing Unit", "Storage Area B", "Warehouse", "Office"]
CATEGORIES = ["Chemical", "Electrical", "Ergonomic", "Fire", "Mechanical", "Environmental", "Slip/Fall"]
RISK_ORDER = ["Low", "Medium", "High", "Critical"]
COLORS = {"Low": "#5A8F76", "Medium": "#96CDB0", "High": "#C18D52", "Critical": "#081B1B"}


def risk_level(score: int) -> str:
    """Map the 1–25 likelihood × severity score to a risk band."""
    if not 1 <= score <= 25:
        raise ValueError("Risk score must be between 1 and 25.")
    if score <= 4:
        return "Low"
    if score <= 9:
        return "Medium"
    if score <= 16:
        return "High"
    return "Critical"


def action_priority(level: str) -> str:
    return {
        "Low": "Monitor and manage through routine controls",
        "Medium": "Plan timely controls and supervisor review",
        "High": "Prompt action and formal HSE review required",
        "Critical": "Stop/avoid exposure and escalate immediately for HSE review",
    }[level]


@st.cache_data
def make_hse_data(n: int = 104) -> pd.DataFrame:
    """Create stable, synthetic HSE reports for demonstration only."""
    rng = np.random.default_rng(SEED)
    dates = pd.to_datetime("2025-01-01") + pd.to_timedelta(rng.integers(0, 243, n), unit="D")
    likelihood = rng.choice([1, 2, 3, 4, 5], n, p=[0.12, 0.25, 0.31, 0.22, 0.10])
    severity = rng.choice([1, 2, 3, 4, 5], n, p=[0.10, 0.25, 0.30, 0.24, 0.11])
    scores = likelihood * severity
    report_types = rng.choice(["Hazard", "Near Miss", "Incident"], n, p=[0.45, 0.35, 0.20])
    df = pd.DataFrame(
        {
            "report_id": [f"HSE-{i:04d}" for i in range(1, n + 1)],
            "date": dates,
            "report_type": report_types,
            "location": rng.choice(LOCATIONS, n, p=[0.22, 0.30, 0.16, 0.19, 0.13]),
            "category": rng.choice(CATEGORIES, n, p=[0.22, 0.10, 0.13, 0.10, 0.19, 0.12, 0.14]),
            "likelihood": likelihood,
            "severity": severity,
            "risk_score": scores,
            "risk_level": [risk_level(int(score)) for score in scores],
            "capa_status": rng.choice(["Open", "In Progress", "Closed"], n, p=[0.25, 0.30, 0.45]),
            "people_exposed": rng.integers(1, 31, n),
            "downtime_hours": np.round(rng.gamma(1.4, 2.2, n), 1),
            "environmental_impact_score": rng.integers(1, 6, n),
            "repeat_count": rng.integers(0, 5, n),
        }
    )
    return df.sort_values("date").reset_index(drop=True)


@st.cache_data
def make_environmental_data() -> pd.DataFrame:
    """Create stable monthly synthetic sustainability indicators."""
    rng = np.random.default_rng(SEED + 1)
    months = pd.date_range("2025-01-01", periods=8, freq="MS")
    data = pd.DataFrame(
        {
            "month": months,
            "Electricity (MWh)": np.round(510 + np.linspace(0, -25, 8) + rng.normal(0, 14, 8), 1),
            "Water (m³)": np.round(1180 + np.linspace(0, -55, 8) + rng.normal(0, 35, 8), 1),
            "CO2e (t)": np.round(205 + np.linspace(0, -14, 8) + rng.normal(0, 7, 8), 1),
            "Waste (t)": np.round(54 + np.linspace(0, -3, 8) + rng.normal(0, 2.2, 8), 1),
            "Recycling (%)": np.round(58 + np.linspace(0, 8, 8) + rng.normal(0, 1.8, 8), 1),
        }
    )
    # Deliberate but plausible demo variation for the transparent anomaly calculation.
    data.loc[7, "Water (m³)"] = round(data.loc[4:6, "Water (m³)"].mean() * 1.19, 1)
    return data


KEYWORDS = {
    "Chemical": ["solvent", "acid", "chemical", "spill", "leak", "fumes"],
    "Electrical": ["wire", "wiring", "socket", "voltage", "electric"],
    "Ergonomic": ["lifting", "posture", "repetitive", "chair", "strain"],
    "Fire": ["smoke", "flame", "combustible", "fire"],
    "Mechanical": ["machine", "guard", "rotating", "equipment"],
    "Environmental": ["waste", "wastewater", "emission", "discharge"],
    "Slip/Fall": ["wet floor", "slippery", "trip", "fall"],
}


def suggest_category(description: str) -> tuple[str, list[str]]:
    """Transparent classifier: select the category with most keyword matches."""
    text = description.lower()
    matches = {category: [word for word in words if word in text] for category, words in KEYWORDS.items()}
    best = max(matches, key=lambda category: len(matches[category]))
    if not matches[best]:
        return "Mechanical", []
    return best, matches[best]


CONTROLS = {
    "Chemical": ["Remove the hazardous chemical/task where feasible", "Consider a less hazardous formulation", "Use closed transfer, containment or local exhaust", "Review SOP, labelling, storage and spill response", "Assess gloves, goggles and respiratory protection"],
    "Electrical": ["De-energize and remove defective equipment", "Use lower-voltage or safer equipment where feasible", "Install guarding, isolation and protective devices", "Apply lockout/tagout, inspection and permit controls", "Assess arc-rated and electrical PPE"],
    "Ergonomic": ["Remove unnecessary manual handling", "Use lighter loads or alternative packaging", "Provide lifting aids and adjustable workstations", "Use task rotation, training and work-rest planning", "Assess suitable gloves or supportive PPE"],
    "Fire": ["Remove ignition sources or combustible inventory", "Use less-flammable materials where feasible", "Provide detection, suppression and segregation", "Review hot-work permits, drills and inspections", "Assess fire-resistant PPE for trained responders"],
    "Mechanical": ["Eliminate access to the hazardous motion", "Use equipment with a safer operating principle", "Install fixed/interlocked guards and emergency stops", "Apply lockout/tagout, maintenance and competency controls", "Assess eye, hand and foot protection"],
    "Environmental": ["Eliminate the discharge or waste stream", "Substitute lower-impact materials or processes", "Install capture, treatment and secondary containment", "Monitor waste routes, permits and response procedures", "Assess task-specific protective clothing"],
    "Slip/Fall": ["Remove the spill, obstruction or level change", "Use less-slippery flooring/materials", "Improve drainage, barriers, lighting and handrails", "Use inspections, housekeeping and warning controls", "Assess slip-resistant footwear"],
}


def capa_suggestions(category: str) -> dict[str, str]:
    return {
        "Immediate corrective action": f"Secure the area and apply an interim {category.lower()} hazard control.",
        "Root-cause investigation area": "Review task conditions, equipment, procedure, training and recent changes.",
        "Preventive action": f"Define a durable control using the hierarchy of controls for the {category.lower()} hazard.",
        "Verification / follow-up": "Assign an owner and due date; verify effectiveness after implementation.",
    }


def anomaly_result(series: pd.Series) -> tuple[float, float, bool]:
    """Compare latest value with mean of preceding three months; flag >15%."""
    baseline = float(series.iloc[-4:-1].mean())
    latest = float(series.iloc[-1])
    deviation = ((latest - baseline) / baseline) * 100 if baseline else 0.0
    return baseline, deviation, abs(deviation) > 15


def style_app() -> None:
    st.markdown(
        """
        <style>
        html, body, [class*="st-"], [data-testid="stAppViewContainer"] {
            font-family: "Times New Roman", Times, serif;
        }
        h1, h2, h3 {color: #203B37; letter-spacing: .01em;}
        [data-testid="stMetric"] {
            background:#EEE8B2; border:1px solid #96CDB0; padding:14px;
            border-radius:10px; box-shadow:0 2px 8px #081B1B18;
        }
        .demo-tag {
            display:inline-block; background:#96CDB0; color:#081B1B;
            padding:5px 11px; border-radius:20px; font-weight:700; margin-bottom:8px;
        }
        .panel {
            background:#EEE8B2; color:#081B1B; border-left:5px solid #5A8F76;
            padding:16px 18px; border-radius:8px; box-shadow:0 2px 8px #081B1B18;
        }
        .disclaimer {
            background:#EEE8B2; border:1px solid #C18D52; padding:14px;
            border-radius:8px; font-weight:700; color:#203B37;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def header(title: str, subtitle: str) -> None:
    st.markdown('<span class="demo-tag">Synthetic Demo Data</span>', unsafe_allow_html=True)
    st.title(title)
    st.caption(subtitle)


def operational_overview(df: pd.DataFrame) -> None:
    header("Operational HSE Overview", "Stable synthetic reports for analytics demonstration")
    high = df[df["risk_level"].isin(["High", "Critical"])]
    incidents = df[df["report_type"].eq("Incident")]
    last_incident = incidents["date"].max()
    days_without = max(0, int((df["date"].max() - last_incident).days)) if pd.notna(last_incident) else int((df["date"].max() - df["date"].min()).days)
    cols = st.columns(5)
    values = [len(df), (df["report_type"] == "Near Miss").sum(), len(high), (df["capa_status"] != "Closed").sum(), days_without]
    labels = ["Total Reports", "Near Misses", "High/Critical Risk", "Open CAPAs", "Days Without LTI*"]
    for col, label, value in zip(cols, labels, values):
        col.metric(label, int(value))
    st.caption("*Prototype proxy: days since the latest synthetic incident; no separate lost-time field is modelled.")

    left, right = st.columns(2)
    category_counts = df["category"].value_counts().rename_axis("category").reset_index(name="reports")
    left.plotly_chart(px.bar(category_counts, x="category", y="reports", title="Reports by category", color_discrete_sequence=["#5A8F76"]), width="stretch")
    location_counts = high["location"].value_counts().rename_axis("location").reset_index(name="reports")
    right.plotly_chart(px.bar(location_counts, x="location", y="reports", title="High-risk reports by location", color_discrete_sequence=["#C18D52"]), width="stretch")
    df_month = df.assign(month=df["date"].dt.to_period("M").dt.to_timestamp()).groupby(["month", "report_type"]).size().reset_index(name="reports")
    left.plotly_chart(px.line(df_month, x="month", y="reports", color="report_type", markers=True, title="Monthly reports split by report type"), width="stretch")
    risk_counts = df["risk_level"].value_counts().reindex(RISK_ORDER, fill_value=0).rename_axis("risk_level").reset_index(name="reports")
    right.plotly_chart(px.bar(risk_counts, x="risk_level", y="reports", color="risk_level", color_discrete_map=COLORS, title="Risk-level distribution"), width="stretch")

    top_category = high["category"].value_counts().idxmax()
    top_location = high["location"].value_counts().idxmax()
    st.markdown(f'<div class="panel"><b>Pattern Detected</b><br>The greatest number of High/Critical reports occurs in the <b>{top_category}</b> category and at <b>{top_location}</b>. This is a descriptive signal for review, not proof of causation.</div>', unsafe_allow_html=True)


def risk_matrix(selected_likelihood: int, selected_severity: int) -> go.Figure:
    z = [[i * j for i in range(1, 6)] for j in range(1, 6)]
    text = [[f"{score}<br>{risk_level(score)}" for score in row] for row in z]
    fig = go.Figure(go.Heatmap(z=z, x=[1, 2, 3, 4, 5], y=[1, 2, 3, 4, 5], text=text, texttemplate="%{text}", colorscale=[[0, "#5A8F76"], [.16, "#5A8F76"], [.17, "#96CDB0"], [.36, "#96CDB0"], [.37, "#C18D52"], [.64, "#C18D52"], [.65, "#081B1B"], [1, "#081B1B"]], zmin=1, zmax=25, showscale=False))
    fig.add_shape(type="rect", x0=selected_likelihood - .48, x1=selected_likelihood + .48, y0=selected_severity - .48, y1=selected_severity + .48, line=dict(color="white", width=5))
    fig.update_layout(title="5×5 Risk Matrix", xaxis_title="Likelihood", yaxis_title="Severity", height=430, margin=dict(t=60, b=45))
    return fig


def assessment_page() -> None:
    header("Hazard and Near-Miss Assessment", "Transparent rules with user override and human review")
    st.markdown('<div class="disclaimer">Decision-support only. Final risk assessment and controls require review by qualified HSE personnel.</div>', unsafe_allow_html=True)
    st.write("")
    with st.form("assessment"):
        c1, c2 = st.columns(2)
        location = c1.selectbox("Location", LOCATIONS)
        report_type = c2.selectbox("Report Type", ["Hazard", "Near Miss", "Incident"])
        description = st.text_area("Description", placeholder="Example: Solvent leak and fumes near a transfer line")
        c3, c4 = st.columns(2)
        likelihood = c3.number_input("Likelihood (1–5)", min_value=1, max_value=5, value=3, step=1)
        severity = c4.number_input("Severity (1–5)", min_value=1, max_value=5, value=3, step=1)
        submitted = st.form_submit_button("Assess report", type="primary")
    if submitted:
        if not description.strip():
            st.error("Enter a description before assessing the report.")
            return
        suggested, matched = suggest_category(description)
        st.session_state["assessment_result"] = {"location": location, "report_type": report_type, "description": description, "likelihood": int(likelihood), "severity": int(severity), "suggested": suggested, "matched": matched}
    if "assessment_result" not in st.session_state:
        st.info("Complete the form to calculate and display an assessment.")
        return
    a = st.session_state["assessment_result"]
    st.subheader("Calculated results")
    match_text = ", ".join(a["matched"]) if a["matched"] else "no listed keyword; default requires review"
    st.caption(f"Keyword suggestion: {a['suggested']} (matched: {match_text}). You may override it below.")
    category = st.selectbox("Hazard category", CATEGORIES, index=CATEGORIES.index(a["suggested"]), key="category_override")
    score = a["likelihood"] * a["severity"]
    level = risk_level(score)
    cols = st.columns(4)
    for col, label, value in zip(cols, ["Likelihood", "Severity", "Risk Score", "Risk Level"], [a["likelihood"], a["severity"], f"{score}/25", level]):
        col.metric(label, value)
    st.info(f"Recommended action priority: {action_priority(level)}")
    st.plotly_chart(risk_matrix(a["likelihood"], a["severity"]), width="stretch")
    st.subheader("Potential controls requiring HSE review")
    for heading, recommendation in zip(["1. Elimination", "2. Substitution", "3. Engineering Controls", "4. Administrative Controls", "5. PPE"], CONTROLS[category]):
        st.markdown(f"**{heading}:** {recommendation}")
    st.subheader("Suggested CAPA items")
    st.caption("Recommendations—not calculated findings. Assign and validate through the site CAPA process.")
    for heading, item in capa_suggestions(category).items():
        st.markdown(f"**{heading}:** {item}")


def sustainability_page(df: pd.DataFrame) -> None:
    header("Environmental Sustainability and Data Exploration", "Monthly indicators and exploratory PCA")
    env = make_environmental_data()
    latest = env.iloc[-1]
    metrics = [col for col in env.columns if col != "month"]
    cols = st.columns(5)
    for col, metric in zip(cols, metrics):
        baseline, deviation, flagged = anomaly_result(env[metric])
        col.metric(metric, f"{latest[metric]:,.1f}", f"{deviation:+.1f}% vs 3-mo mean", delta_color="inverse" if metric != "Recycling (%)" else "normal")
    left, right = st.columns(2)
    consumption = env.melt(id_vars="month", value_vars=["Electricity (MWh)", "Water (m³)"], var_name="metric", value_name="value")
    emissions = env.melt(id_vars="month", value_vars=["CO2e (t)", "Waste (t)", "Recycling (%)"], var_name="metric", value_name="value")
    left.plotly_chart(px.line(consumption, x="month", y="value", color="metric", markers=True, title="Electricity and water trends"), width="stretch")
    right.plotly_chart(px.line(emissions, x="month", y="value", color="metric", markers=True, title="Emissions, waste and recycling trends"), width="stretch")

    st.subheader("Transparent anomaly check")
    st.code("percentage deviation = (latest month − mean of preceding 3 months) / mean of preceding 3 months × 100")
    rows = []
    for metric in metrics:
        baseline, deviation, flagged = anomaly_result(env[metric])
        rows.append({"Metric": metric, "Latest": latest[metric], "3-month baseline mean": round(baseline, 2), "Deviation": f"{deviation:+.1f}%", "Flag (>15%)": "Flagged" if flagged else "Not flagged"})
    st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")
    flagged_metrics = [row["Metric"] for row in rows if row["Flag (>15%)"] == "Flagged"]
    if flagged_metrics:
        st.warning(f"Investigate operational or measurement changes for: {', '.join(flagged_metrics)}. The comparison does not establish causation.")
    else:
        st.success("No metric exceeds the ±15% rule. Continue routine review; this does not establish that no issue exists.")

    st.subheader("PCA: Exploring HSE Report Patterns")
    features = ["likelihood", "severity", "people_exposed", "downtime_hours", "environmental_impact_score", "repeat_count"]
    # PCA pipeline: standardize all six inputs, then reduce to two components.
    scaled = StandardScaler().fit_transform(df[features])
    pca = PCA(n_components=2)
    components = pca.fit_transform(scaled)
    plot_df = pd.DataFrame({"PC1": components[:, 0], "PC2": components[:, 1], "risk_level": df["risk_level"], "report_id": df["report_id"]})
    pc_cols = st.columns(3)
    pc_cols[0].metric("PC1 explained variance", f"{pca.explained_variance_ratio_[0] * 100:.1f}%")
    pc_cols[1].metric("PC2 explained variance", f"{pca.explained_variance_ratio_[1] * 100:.1f}%")
    pc_cols[2].metric("Cumulative variance", f"{pca.explained_variance_ratio_.sum() * 100:.1f}%")
    fig = px.scatter(plot_df, x="PC1", y="PC2", color="risk_level", color_discrete_map=COLORS, category_orders={"risk_level": RISK_ORDER}, hover_data=["report_id"], title="PC1 versus PC2, coloured by risk level")
    st.plotly_chart(fig, width="stretch")
    st.info("Standardization prevents large-scale variables from dominating. PCA creates new variables called principal components: PC1 captures the greatest variance, while PC2 captures the next greatest variance and remains orthogonal (uncorrelated in direction) to PC1. This plot is exploratory and does not prove clusters or causes.")


style_app()
df_reports = make_hse_data()
st.sidebar.title("HSE Risk Intelligence")
st.sidebar.caption("Analytics & Decision-Support Prototype")
page = st.sidebar.radio("Navigate", ["Operational HSE Overview", "Hazard & Near-Miss Assessment", "Environmental Sustainability & Data Exploration"])
st.sidebar.markdown("---")
st.sidebar.caption("Synthetic Demo Data · Fixed seed 42")

if page == "Operational HSE Overview":
    operational_overview(df_reports)
elif page == "Hazard & Near-Miss Assessment":
    assessment_page()
else:
    sustainability_page(df_reports)
