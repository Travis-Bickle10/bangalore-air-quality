from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


DATA_PATH = Path(__file__).parent / "data" / "bangalore_master.csv"

POLLUTANTS = {
    "pm25": {"label": "PM2.5", "unit": "ug/m3", "color": "#d85a30", "limit": 15},
    "pm10": {"label": "PM10", "unit": "ug/m3", "color": "#185fa5", "limit": 45},
    "no2": {"label": "NO2", "unit": "ug/m3", "color": "#1d9e75", "limit": 25},
    "so2": {"label": "SO2", "unit": "ug/m3", "color": "#ba7517", "limit": 40},
    "o3": {"label": "O3", "unit": "ug/m3", "color": "#7a5195", "limit": 100},
    "co": {"label": "CO", "unit": "ug/m3", "color": "#665191", "limit": None},
}

POLICY_EVENTS = {
    2003: "CNG mandate",
    2011: "BS-IV norms",
    2017: "BS-VI fuel",
    2020: "COVID lockdown",
}


st.set_page_config(
    page_title="Bangalore Air Quality Dashboard",
    page_icon="",
    layout="wide",
)


@st.cache_data
def load_default_data() -> pd.DataFrame:
    return pd.read_csv(DATA_PATH)


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [col.strip().lower() for col in df.columns]
    required = {"year"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError("CSV must contain a year column.")

    for col in ["year", *POLLUTANTS.keys(), "vehicles_millions"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    if "notes" not in df.columns:
        df["notes"] = ""

    df["year"] = df["year"].astype("Int64")
    return df.sort_values("year")


def available_pollutants(df: pd.DataFrame) -> list[str]:
    return [col for col in POLLUTANTS if col in df.columns and df[col].notna().any()]


def add_policy_lines(fig: go.Figure, year_min: int, year_max: int) -> None:
    for year, label in POLICY_EVENTS.items():
        if year_min <= year <= year_max:
            fig.add_vline(
                x=year,
                line_width=1,
                line_dash="dot",
                line_color="#8a8a8a",
                annotation_text=label,
                annotation_position="top",
            )


def trend_delta(df: pd.DataFrame, pollutant: str) -> tuple[float | None, float | None]:
    data = df[["year", pollutant]].dropna()
    if len(data) < 2:
        return None, None
    first = data.iloc[0][pollutant]
    last = data.iloc[-1][pollutant]
    return first, last - first


st.title("Bangalore Air Quality Dashboard")
st.caption("Interactive view of the 2000-2025 analysis dataset")

uploaded_file = st.sidebar.file_uploader(
    "Use another bangalore_master.csv",
    type=["csv"],
)

try:
    if uploaded_file is not None:
        df = clean_data(pd.read_csv(uploaded_file))
        source_label = "Uploaded CSV"
    else:
        df = clean_data(load_default_data())
        source_label = "Included dataset"
except Exception as exc:
    st.error(f"Could not load the dataset: {exc}")
    st.stop()

pollutant_cols = available_pollutants(df)
if not pollutant_cols:
    st.error("No pollutant columns were found in the data.")
    st.stop()

year_min = int(df["year"].min())
year_max = int(df["year"].max())
selected_years = st.sidebar.slider(
    "Year range",
    min_value=year_min,
    max_value=year_max,
    value=(year_min, year_max),
)
selected_pollutants = st.sidebar.multiselect(
    "Pollutants",
    options=pollutant_cols,
    default=[col for col in ["pm25", "pm10", "no2", "so2"] if col in pollutant_cols],
    format_func=lambda col: POLLUTANTS[col]["label"],
)

view = df[df["year"].between(*selected_years)].copy()

latest_year = int(view["year"].max())
latest = view[view["year"] == latest_year].iloc[0]

st.markdown(f"**Data source:** {source_label}")
metric_cols = st.columns(4)
for idx, pollutant in enumerate(selected_pollutants[:4]):
    first, delta = trend_delta(view, pollutant)
    value = latest.get(pollutant)
    label = POLLUTANTS[pollutant]["label"]
    unit = POLLUTANTS[pollutant]["unit"]
    if pd.isna(value):
        metric_cols[idx].metric(label, "No data", help=f"Latest selected year: {latest_year}")
    else:
        delta_text = None if delta is None else f"{delta:+.1f} {unit}"
        metric_cols[idx].metric(label, f"{value:.1f} {unit}", delta_text)

st.subheader("Pollution Trends")
long_df = view.melt(
    id_vars=["year"],
    value_vars=selected_pollutants,
    var_name="pollutant",
    value_name="value",
).dropna()
long_df["pollutant_label"] = long_df["pollutant"].map(
    lambda col: POLLUTANTS[col]["label"]
)

trend_fig = px.line(
    long_df,
    x="year",
    y="value",
    color="pollutant_label",
    markers=True,
    color_discrete_map={
        cfg["label"]: cfg["color"] for cfg in POLLUTANTS.values()
    },
    labels={"year": "Year", "value": "Concentration", "pollutant_label": ""},
)
trend_fig.update_layout(
    height=470,
    margin=dict(l=20, r=20, t=30, b=20),
    hovermode="x unified",
    legend_orientation="h",
)
add_policy_lines(trend_fig, selected_years[0], selected_years[1])
st.plotly_chart(trend_fig, use_container_width=True)

left, right = st.columns([1.1, 0.9])

with left:
    st.subheader("Vehicle Growth vs Pollution")
    scatter_pollutant = st.selectbox(
        "Pollutant for vehicle comparison",
        options=[col for col in selected_pollutants if col in view.columns],
        format_func=lambda col: POLLUTANTS[col]["label"],
    )
    scatter_data = view.dropna(subset=["vehicles_millions", scatter_pollutant])
    if scatter_data.empty:
        st.info("Vehicle comparison needs both vehicle and pollutant data.")
    else:
        scatter_fig = px.scatter(
            scatter_data,
            x="vehicles_millions",
            y=scatter_pollutant,
            color="year",
            text="year",
            color_continuous_scale="RdYlGn_r",
            labels={
                "vehicles_millions": "Registered vehicles (millions)",
                scatter_pollutant: f"{POLLUTANTS[scatter_pollutant]['label']} ({POLLUTANTS[scatter_pollutant]['unit']})",
                "year": "Year",
            },
        )
        scatter_fig.update_traces(textposition="top center")
        scatter_fig.update_layout(height=430, margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(scatter_fig, use_container_width=True)

with right:
    st.subheader("Data Coverage")
    coverage = []
    for pollutant in pollutant_cols:
        valid = view[pollutant].notna()
        coverage.append(
            {
                "Pollutant": POLLUTANTS[pollutant]["label"],
                "Years": int(valid.sum()),
                "First": int(view.loc[valid, "year"].min()) if valid.any() else None,
                "Last": int(view.loc[valid, "year"].max()) if valid.any() else None,
            }
        )
    st.dataframe(pd.DataFrame(coverage), hide_index=True, use_container_width=True)

    notes = view[view["notes"].fillna("").astype(str).str.strip() != ""][
        ["year", "notes"]
    ]
    if not notes.empty:
        st.markdown("**Flagged values**")
        st.dataframe(notes, hide_index=True, use_container_width=True)

st.subheader("Dataset")
st.dataframe(view, hide_index=True, use_container_width=True)
