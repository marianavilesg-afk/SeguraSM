from __future__ import annotations

from io import BytesIO
from pathlib import Path
import re
import unicodedata

import pandas as pd
import plotly.express as px
import streamlit as st


# ------------------------------------------------------------
# Configuración y estilo
# ------------------------------------------------------------
st.set_page_config(
    page_title="SeguraSM | Seguridad vial en Santa Marta",
    page_icon="🚦",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
      .stApp { background: linear-gradient(180deg, #f5f8fc 0%, #eef3f8 100%); }
      .block-container { padding-top: 1.7rem; padding-bottom: 2.5rem; max-width: 1450px; }
      [data-testid="stSidebar"] { background: #10243a; }
      [data-testid="stSidebar"] * { color: #f2f6fb !important; }
      .hero {
        padding: 1.7rem 1.9rem; border-radius: 22px;
        background: linear-gradient(115deg, #10243a 0%, #174c69 58%, #1b7180 100%);
        color: white; margin-bottom: 1.2rem;
        box-shadow: 0 12px 30px rgba(16,36,58,.15);
      }
      .hero-kicker { color: #bfe8e8; font-size: .78rem; font-weight: 700; letter-spacing: .14em; }
      .hero h1 { color: white; font-size: 2.55rem; margin: .25rem 0 .35rem 0; }
      .hero p { color: #e1edf4; margin: 0; font-size: 1.02rem; }
      .section-title { color: #18344c; font-size: 1.2rem; font-weight: 750; margin: .5rem 0 .8rem 0; }
      .note {
        border-left: 4px solid #e4a83b; background: #fff8e9; color: #59431e;
        padding: .9rem 1rem; border-radius: 9px; font-size: .9rem;
      }
      .small-muted { color: #64788b; font-size: .86rem; }
      div[data-testid="stMetric"] {
        background: white; border: 1px solid #e2eaf1; padding: 1rem 1.1rem;
        border-radius: 16px; box-shadow: 0 5px 18px rgba(25,55,80,.05);
      }
      div[data-testid="stMetricLabel"] p { color: #61768a; }
      div[data-testid="stMetricValue"] { color: #163a52; }
      div[data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 16px; border-color: #e2eaf1;
      }
      footer { visibility: hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)


# ------------------------------------------------------------
# Lectura flexible del archivo Excel o CSV
# ------------------------------------------------------------
def clean_name(value: object) -> str:
    text = str(value).strip().lower()
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", "_", text).strip("_")


def find_column(df: pd.DataFrame, aliases: list[str]) -> str | None:
    normalized = {clean_name(col): col for col in df.columns}
    for alias in aliases:
        if clean_name(alias) in normalized:
            return normalized[clean_name(alias)]
    return None


def parse_dates(series: pd.Series) -> pd.Series:
    if pd.api.types.is_numeric_dtype(series):
        numeric = pd.to_numeric(series, errors="coerce")
        median = numeric.dropna().median() if numeric.notna().any() else 0
        if median > 100_000_000_000:
            return pd.to_datetime(numeric, unit="ms", errors="coerce")
        if median > 1_000_000_000:
            return pd.to_datetime(numeric, unit="s", errors="coerce")
    return pd.to_datetime(series, errors="coerce", dayfirst=True)


def choose_data_sheet(sheets: dict[str, pd.DataFrame]) -> tuple[str | None, pd.DataFrame | None]:
    best_name, best_df, best_score = None, None, -1
    for name, frame in sheets.items():
        if frame is None or frame.empty:
            continue
        score = 0
        if find_column(frame, ["FECHA", "FECHA_ACCIDENTE", "FECHA_ACCI"]):
            score += 2
        if find_column(frame, ["LATITUD", "LATITUD_GEOMETRIA", "latitude"]):
            score += 3
        if find_column(frame, ["LONGITUD", "LONGITUD_GEOMETRIA", "longitude"]):
            score += 3
        if find_column(frame, ["SIEVI_CLAS", "TIPO_SINIESTRO", "CLASE_ACCI", "TIPO_CHOQ"]):
            score += 1
        if score > best_score:
            best_name, best_df, best_score = name, frame, score
    if best_score < 5:
        return None, None
    return best_name, best_df


def canonicalize(raw: pd.DataFrame) -> pd.DataFrame:
    aliases = {
        "FECHA": ["FECHA", "FECHA_ACCIDENTE", "FECHA_ACCI", "fecha_siniestro"],
        "LATITUD": ["LATITUD", "LATITUD_GEOMETRIA", "latitude", "lat"],
        "LONGITUD": ["LONGITUD", "LONGITUD_GEOMETRIA", "longitude", "lon", "lng"],
        "TIPO": ["SIEVI_CLAS", "TIPO_SINIESTRO", "CLASE_ACCI", "TIPO_CHOQ", "CLASE_ACCIDENTE", "TIPO"],
        "LUGAR": ["LUGARO", "LUGAR", "SITIO", "UBICACION"],
        "HIPOTESIS": ["HIPOTESIS_", "HIPOTESIS", "CAUSA"],
        "MUERTOS": ["SMUERTOS", "MUERTOS", "FALLECIDOS"],
        "LESIONADOS": ["SLESIONADO", "LESIONADOS", "HERIDOS"],
        "AGRUPACION": ["AGRUPACION", "CLUSTER", "GRUPO"],
    }

    data = pd.DataFrame(index=raw.index)
    for target, options in aliases.items():
        source = find_column(raw, options)
        if source is not None:
            data[target] = raw[source]

    if "FECHA" in data:
        data["FECHA"] = parse_dates(data["FECHA"])
    else:
        data["FECHA"] = pd.NaT

    for col in ["LATITUD", "LONGITUD", "MUERTOS", "LESIONADOS"]:
        if col in data:
            data[col] = pd.to_numeric(data[col], errors="coerce")
        else:
            data[col] = 0 if col in ["MUERTOS", "LESIONADOS"] else float("nan")

    for col in ["TIPO", "LUGAR", "HIPOTESIS"]:
        if col not in data:
            data[col] = "Sin dato"
        data[col] = data[col].fillna("Sin dato").astype(str).str.strip()
        data.loc[data[col].isin(["", "nan", "None", "-", "NaN"]), col] = "Sin dato"

    if "AGRUPACION" not in data:
        data["AGRUPACION"] = "No disponible"

    data["MUERTOS"] = data["MUERTOS"].fillna(0)
    data["LESIONADOS"] = data["LESIONADOS"].fillna(0)
    data["DIA"] = data["FECHA"].dt.day_name().map({
        "Monday": "Lunes", "Tuesday": "Martes", "Wednesday": "Miércoles",
        "Thursday": "Jueves", "Friday": "Viernes", "Saturday": "Sábado",
        "Sunday": "Domingo",
    })
    data["MES"] = data["FECHA"].dt.to_period("M").astype(str)
    return data.reset_index(drop=True)


@st.cache_data(show_spinner=False)
def load_file(file_bytes: bytes, filename: str) -> tuple[pd.DataFrame, str]:
    if filename.lower().endswith(".csv"):
        raw = pd.read_csv(BytesIO(file_bytes))
        source_sheet = "CSV"
    else:
        sheets = pd.read_excel(BytesIO(file_bytes), sheet_name=None)
        source_sheet, raw = choose_data_sheet(sheets)
        if raw is None:
            raise ValueError("No encontré una hoja con fecha, latitud y longitud.")
    return canonicalize(raw), source_sheet or "Datos"


def plot_layout(fig, height: int = 330):
    fig.update_layout(
        height=height,
        margin=dict(l=12, r=12, t=25, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#29465c"),
        legend_title_text="",
    )
    return fig


# ------------------------------------------------------------
# Encabezado
# ------------------------------------------------------------
st.markdown(
    """
    <div class="hero">
      <div class="hero-kicker">ANÁLISIS DE SEGURIDAD VIAL · SANTA MARTA, COLOMBIA</div>
      <h1>🚦 SeguraSM</h1>
      <p>Explora los registros históricos de siniestros viales, identifica patrones y consulta su distribución geográfica.</p>
    </div>
    """,
    unsafe_allow_html=True,
)


# ------------------------------------------------------------
# Archivo de datos y filtros
# ------------------------------------------------------------
with st.sidebar:
    st.markdown("## ⚙️ Panel de control")
    st.caption("Carga el archivo de resultados que generaste en Google Colab.")
    uploaded = st.file_uploader("Archivo de datos", type=["xlsx", "xls", "csv"])
    st.divider()
    st.markdown("**Fuente del análisis**")
    st.caption("Registros históricos consultados desde el servicio de datos de la ANSV y preparados para este proyecto.")

file_bytes = None
filename = None
if uploaded is not None:
    file_bytes = uploaded.getvalue()
    filename = uploaded.name
else:
    local_file = Path("SeguraSM_Resultados.xlsx")
    if local_file.exists():
        file_bytes = local_file.read_bytes()
        filename = local_file.name

if file_bytes is None:
    st.info("Para comenzar, carga **SeguraSM_Resultados.xlsx** en el panel izquierdo. También puedes dejar ese archivo junto a `app.py` en el repositorio de GitHub.")
    st.stop()

try:
    data, sheet_name = load_file(file_bytes, filename or "datos.xlsx")
except Exception as error:
    st.error(f"No pude leer el archivo: {error}")
    st.stop()

if data.empty:
    st.warning("El archivo no contiene registros para mostrar.")
    st.stop()

valid_dates = data["FECHA"].dropna()
min_date = valid_dates.min().date() if not valid_dates.empty else None
max_date = valid_dates.max().date() if not valid_dates.empty else None

with st.sidebar:
    st.divider()
    st.markdown("### 🔎 Filtros")
    if min_date and max_date:
        date_range = st.date_input(
            "Periodo",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
            format="DD/MM/YYYY",
        )
    else:
        date_range = None
    types = sorted(data["TIPO"].dropna().unique().tolist())
    selected_types = st.multiselect("Tipo de siniestro", types, default=types)

filtered = data.copy()
if date_range and isinstance(date_range, (tuple, list)) and len(date_range) == 2:
    start_date, end_date = date_range
    filtered = filtered[
        filtered["FECHA"].notna()
        & (filtered["FECHA"].dt.date >= start_date)
        & (filtered["FECHA"].dt.date <= end_date)
    ]
if selected_types:
    filtered = filtered[filtered["TIPO"].isin(selected_types)]
else:
    filtered = filtered.iloc[0:0]


# ------------------------------------------------------------
# Indicadores principales
# ------------------------------------------------------------
st.markdown('<div class="section-title">Resumen del periodo seleccionado</div>', unsafe_allow_html=True)
col1, col2, col3, col4 = st.columns(4)
col1.metric("Registros analizados", f"{len(filtered):,}")
col2.metric("Personas fallecidas registradas", f"{int(filtered['MUERTOS'].sum()):,}")
col3.metric("Personas lesionadas registradas", f"{int(filtered['LESIONADOS'].sum()):,}")
col4.metric("Tipos identificados", f"{filtered['TIPO'].nunique():,}")

if not valid_dates.empty:
    period_text = f"Cobertura del archivo: **{min_date.strftime('%d/%m/%Y')} – {max_date.strftime('%d/%m/%Y')}**. Hoja utilizada: **{sheet_name}**."
    st.markdown(f'<p class="small-muted">{period_text}</p>', unsafe_allow_html=True)

if filtered.empty:
    st.warning("No hay registros que coincidan con los filtros seleccionados.")
    st.stop()


# ------------------------------------------------------------
# Gráficas
# ------------------------------------------------------------
st.markdown('<div class="section-title">Comportamiento de los siniestros</div>', unsafe_allow_html=True)
left, right = st.columns(2)

with left:
    monthly = filtered.dropna(subset=["FECHA"]).groupby("MES").size().reset_index(name="REGISTROS")
    if not monthly.empty:
        fig_month = px.bar(monthly, x="MES", y="REGISTROS", text="REGISTROS", title="Registros por mes")
        fig_month.update_traces(textposition="outside")
        fig_month.update_xaxes(title="Mes", tickangle=-25)
        fig_month.update_yaxes(title="Cantidad de registros", rangemode="tozero")
        st.plotly_chart(plot_layout(fig_month), use_container_width=True)
    else:
        st.info("No hay fechas válidas para construir la gráfica mensual.")

with right:
    by_type = filtered.groupby("TIPO").size().reset_index(name="REGISTROS").sort_values("REGISTROS", ascending=False)
    fig_type = px.pie(by_type, names="TIPO", values="REGISTROS", hole=.58, title="Distribución por tipo")
    fig_type.update_traces(textposition="inside", textinfo="percent+label")
    st.plotly_chart(plot_layout(fig_type), use_container_width=True)

left, right = st.columns(2)
with left:
    weekday_order = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    by_day = filtered.dropna(subset=["DIA"]).groupby("DIA").size().reindex(weekday_order).fillna(0).reset_index(name="REGISTROS")
    fig_day = px.bar(by_day, x="DIA", y="REGISTROS", title="Registros por día de la semana", text="REGISTROS")
    fig_day.update_traces(textposition="outside")
    fig_day.update_xaxes(title="Día", tickangle=-20)
    fig_day.update_yaxes(title="Cantidad de registros", rangemode="tozero")
    st.plotly_chart(plot_layout(fig_day), use_container_width=True)

with right:
    casualties = pd.DataFrame({
        "Indicador": ["Fallecidos", "Lesionados"],
        "Personas": [filtered["MUERTOS"].sum(), filtered["LESIONADOS"].sum()],
    })
    fig_people = px.bar(casualties, x="Indicador", y="Personas", color="Indicador", text_auto=True, title="Personas afectadas registradas")
    fig_people.update_xaxes(title="")
    fig_people.update_yaxes(title="Cantidad", rangemode="tozero")
    st.plotly_chart(plot_layout(fig_people), use_container_width=True)


# ------------------------------------------------------------
# Mapa y hallazgos por lugar
# ------------------------------------------------------------
st.markdown('<div class="section-title">Distribución geográfica</div>', unsafe_allow_html=True)
map_data = filtered.dropna(subset=["LATITUD", "LONGITUD"]).copy()
map_data = map_data[
    map_data["LATITUD"].between(-90, 90)
    & map_data["LONGITUD"].between(-180, 180)
]
if not map_data.empty:
    map_data["REGISTRO"] = 1
    fig_map = px.scatter_map(
        map_data,
        lat="LATITUD",
        lon="LONGITUD",
        color="TIPO",
        hover_name="TIPO",
        hover_data={
            "FECHA": True,
            "LUGAR": True,
            "MUERTOS": True,
            "LESIONADOS": True,
            "LATITUD": False,
            "LONGITUD": False,
        },
        zoom=10,
        height=510,
        map_style="carto-positron",
        title="Ubicación de los registros disponibles",
    )
    fig_map.update_layout(margin=dict(l=0, r=0, t=45, b=0), legend_title_text="Tipo de siniestro")
    st.plotly_chart(fig_map, use_container_width=True)
    st.caption(f"Se muestran {len(map_data):,} registros con coordenadas válidas. Cada punto representa un registro del conjunto de datos.")
else:
    st.info("El archivo no contiene coordenadas válidas para mostrar el mapa.")

place_col, hypothesis_col = st.columns(2)
with place_col:
    st.markdown("**Lugares más frecuentes**")
    places = filtered[filtered["LUGAR"] != "Sin dato"].groupby("LUGAR").size().sort_values(ascending=False).head(8).reset_index(name="REGISTROS")
    if places.empty:
        st.caption("No hay información de lugar en los registros filtrados.")
    else:
        fig_places = px.bar(places.sort_values("REGISTROS"), x="REGISTROS", y="LUGAR", orientation="h", text="REGISTROS")
        fig_places.update_traces(textposition="outside")
        fig_places.update_layout(height=320, margin=dict(l=5, r=25, t=10, b=5), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_places, use_container_width=True)
with hypothesis_col:
    st.markdown("**Hipótesis reportadas con mayor frecuencia**")
    hypotheses = filtered[filtered["HIPOTESIS"] != "Sin dato"].groupby("HIPOTESIS").size().sort_values(ascending=False).head(8).reset_index(name="REGISTROS")
    if hypotheses.empty:
        st.caption("No hay hipótesis registradas en los datos filtrados.")
    else:
        fig_hyp = px.bar(hypotheses.sort_values("REGISTROS"), x="REGISTROS", y="HIPOTESIS", orientation="h", text="REGISTROS")
        fig_hyp.update_traces(textposition="outside")
        fig_hyp.update_layout(height=320, margin=dict(l=5, r=25, t=10, b=5), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_hyp, use_container_width=True)


# ------------------------------------------------------------
# Tabla y nota metodológica
# ------------------------------------------------------------
with st.expander("Consultar los registros incluidos en el análisis"):
    display_cols = ["FECHA", "TIPO", "LUGAR", "HIPOTESIS", "MUERTOS", "LESIONADOS", "LATITUD", "LONGITUD"]
    st.dataframe(
        filtered[display_cols].sort_values("FECHA", ascending=False),
        use_container_width=True,
        hide_index=True,
    )

st.markdown(
    """
    <div class="note">
      <strong>Nota metodológica:</strong> este tablero describe los registros históricos incluidos en el archivo cargado. No representa necesariamente todos los siniestros ocurridos en Santa Marta y no debe interpretarse como una predicción de accidentes futuros. La cobertura temporal y la calidad de los registros limitan las conclusiones posibles.
    </div>
    """,
    unsafe_allow_html=True,
)
st.markdown("<p class='small-muted' style='text-align:center; margin-top:1.5rem;'>SeguraSM · Proyecto académico de análisis de seguridad vial</p>", unsafe_allow_html=True)
