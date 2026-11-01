from __future__ import annotations

from io import BytesIO
from pathlib import Path
import re
import unicodedata
from datetime import date

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="SeguraSM | Observatorio vial",
    page_icon="🚦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ------------------------------------------------------------
# IDENTIDAD VISUAL
# ------------------------------------------------------------

COLORS = {
    "navy": "#102A43",
    "navy2": "#173F5F",
    "teal": "#00A896",
    "teal_light": "#DDF5F1",
    "gold": "#E6A23C",
    "ink": "#203449",
    "muted": "#718096",
    "line": "#E5ECF2",
    "paper": "#F4F7FA",
    "white": "#FFFFFF",
    "red": "#D95D5D",
}

st.markdown(
    f"""
    <style>
      @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=Manrope:wght@500;600;700;800&display=swap');

      html, body, [class*="css"] {{
        font-family: 'DM Sans', sans-serif;
      }}

      .stApp {{
        background: {COLORS['paper']};
        color: {COLORS['ink']};
      }}

      .block-container {{
        max-width: 1500px;
        padding-top: 1.35rem;
        padding-bottom: 2.6rem;
      }}

      [data-testid="stSidebar"] {{
        background: #102A43;
        border-right: 1px solid rgba(255,255,255,.08);
      }}

      [data-testid="stSidebar"] * {{
        color: #F2F7FA !important;
      }}

      [data-testid="stSidebar"] [data-testid="stCaptionContainer"] p {{
        color: #B8CBD8 !important;
      }}

      [data-testid="stSidebar"] hr {{
        border-color: rgba(255,255,255,.16);
      }}

      [data-testid="stSidebar"] [data-baseweb="select"] > div {{
        background: #173F5F;
        border-color: #42627B;
      }}

      [data-testid="stSidebar"] input {{
        color: #102A43 !important;
      }}

      .brand {{
        display:flex;
        align-items:center;
        gap:.7rem;
        padding:.3rem 0 1rem 0;
      }}

      .brand-mark {{
        width:42px;
        height:42px;
        display:flex;
        align-items:center;
        justify-content:center;
        border-radius:13px;
        background:linear-gradient(145deg,#00A896,#54C7B8);
        color:white;
        font-size:1.35rem;
      }}

      .brand-name {{
        font-family:'Manrope',sans-serif;
        font-weight:800;
        font-size:1.22rem;
        letter-spacing:-.04em;
        color:white;
      }}

      .brand-sub {{
        color:#AEC5D3;
        font-size:.68rem;
        letter-spacing:.13em;
        text-transform:uppercase;
        margin-top:-2px;
      }}

      .eyebrow {{
        color:{COLORS['teal']};
        font-size:.70rem;
        letter-spacing:.16em;
        font-weight:800;
        text-transform:uppercase;
      }}

      .hero {{
        position:relative;
        overflow:hidden;
        padding:1.8rem 2rem;
        border-radius:22px;
        background:linear-gradient(115deg,#102A43 0%,#173F5F 65%,#176B70 100%);
        box-shadow:0 14px 34px rgba(16,42,67,.14);
        margin-bottom:1.2rem;
      }}

      .hero:after {{
        content:'';
        position:absolute;
        width:260px;
        height:260px;
        right:-55px;
        top:-115px;
        border:1px solid rgba(255,255,255,.13);
        border-radius:50%;
        box-shadow:0 0 0 28px rgba(255,255,255,.035),
                   0 0 0 58px rgba(255,255,255,.025);
      }}

      .hero h1 {{
        font-family:'Manrope',sans-serif;
        font-size:2.65rem;
        line-height:1.1;
        color:white;
        margin:.35rem 0 .55rem 0;
        letter-spacing:-.055em;
      }}

      .hero p {{
        color:#D7E5EC;
        font-size:1rem;
        max-width:760px;
        margin:0;
        line-height:1.6;
      }}

      .hero-meta {{
        display:flex;
        gap:.55rem;
        flex-wrap:wrap;
        margin-top:1.05rem;
      }}

      .hero-pill {{
        display:inline-block;
        padding:.35rem .65rem;
        border-radius:100px;
        background:rgba(255,255,255,.10);
        border:1px solid rgba(255,255,255,.13);
        color:#E8F2F6;
        font-size:.72rem;
      }}

      .section-head {{
        display:flex;
        justify-content:space-between;
        align-items:flex-end;
        margin:1.15rem 0 .75rem 0;
      }}

      .section-title {{
        color:{COLORS['navy']};
        font-family:'Manrope',sans-serif;
        font-size:1.22rem;
        font-weight:800;
        letter-spacing:-.025em;
        margin:0;
      }}

      .section-sub {{
        color:{COLORS['muted']};
        font-size:.82rem;
        margin:.18rem 0 0 0;
      }}

      .metric-card {{
        background:white;
        border:1px solid {COLORS['line']};
        border-radius:17px;
        padding:1.05rem 1.15rem .95rem;
        min-height:128px;
        box-shadow:0 5px 18px rgba(16,42,67,.035);
        position:relative;
        overflow:hidden;
      }}

      .metric-card:before {{
        content:'';
        position:absolute;
        left:0;
        top:0;
        bottom:0;
        width:4px;
        background:var(--accent,{COLORS['teal']});
      }}

      .metric-label {{
        color:{COLORS['muted']};
        font-size:.76rem;
        font-weight:700;
        letter-spacing:.015em;
      }}

      .metric-value {{
        color:{COLORS['navy']};
        font-family:'Manrope',sans-serif;
        font-size:2rem;
        line-height:1.2;
        font-weight:800;
        margin:.35rem 0 .2rem;
      }}

      .metric-foot {{
        color:#91A0AE;
        font-size:.72rem;
      }}

      .panel-title {{
        color:{COLORS['navy']};
        font-family:'Manrope',sans-serif;
        font-size:.98rem;
        font-weight:800;
        margin:0 0 .1rem 0;
      }}

      .panel-caption {{
        color:{COLORS['muted']};
        font-size:.76rem;
        margin:0 0 .7rem 0;
      }}

      .insight {{
        background:#EAF6F4;
        border:1px solid #D1ECE7;
        border-radius:14px;
        padding:.9rem 1rem;
        color:#245C58;
        font-size:.86rem;
      }}

      .method {{
        background:#FFF8EA;
        border:1px solid #F4E4C2;
        border-left:4px solid {COLORS['gold']};
        border-radius:12px;
        padding:.85rem 1rem;
        color:#6D542A;
        font-size:.82rem;
        line-height:1.55;
      }}

      .footer {{
        color:#8A99A7;
        font-size:.72rem;
        text-align:center;
        padding:1.6rem 0 .2rem;
      }}

      div[data-testid="stMetric"] {{
        background:white;
        border:1px solid {COLORS['line']};
        border-radius:16px;
        padding:.8rem;
      }}

      div[data-testid="stTabs"] button {{
        font-weight:700;
        color:{COLORS['muted']};
      }}

      div[data-testid="stTabs"] button[aria-selected="true"] {{
        color:{COLORS['teal']} !important;
        border-bottom-color:{COLORS['teal']} !important;
      }}

      div[data-testid="stDataFrame"] {{
        border:1px solid {COLORS['line']};
        border-radius:12px;
        overflow:hidden;
      }}

      footer {{
        visibility:hidden;
      }}
    </style>
    """,
    unsafe_allow_html=True,
)


# ------------------------------------------------------------
# NORMALIZACIÓN Y LECTURA DE DATOS
# ------------------------------------------------------------

def clean_name(value: object) -> str:
    value = unicodedata.normalize(
        "NFKD",
        str(value).strip().lower()
    ).encode("ascii", "ignore").decode("ascii")

    return re.sub(r"[^a-z0-9]+", "_", value).strip("_")


def find_column(frame: pd.DataFrame, aliases: list[str]) -> str | None:
    normalized = {
        clean_name(column): column
        for column in frame.columns
    }

    for alias in aliases:
        if clean_name(alias) in normalized:
            return normalized[clean_name(alias)]

    return None


def parse_dates(series: pd.Series) -> pd.Series:
    if pd.api.types.is_numeric_dtype(series):
        values = pd.to_numeric(series, errors="coerce")

        median = (
            values.dropna().median()
            if values.notna().any()
            else 0
        )

        if median > 100_000_000_000:
            return pd.to_datetime(
                values,
                unit="ms",
                errors="coerce"
            )

        if median > 1_000_000_000:
            return pd.to_datetime(
                values,
                unit="s",
                errors="coerce"
            )

    return pd.to_datetime(
        series,
        errors="coerce",
        dayfirst=True
    )


def find_best_sheet(
    sheets: dict[str, pd.DataFrame]
) -> tuple[str | None, pd.DataFrame | None]:

    best_name = None
    best_frame = None
    best_score = -1

    for name, frame in sheets.items():

        if frame is None or frame.empty:
            continue

        score = 0

        if find_column(
            frame,
            ["FECHA", "FECHA_ACCIDENTE", "FECHA_ACCI"]
        ):
            score += 2

        if find_column(
            frame,
            ["LATITUD", "LATITUD_GEOMETRIA", "latitude"]
        ):
            score += 3

        if find_column(
            frame,
            ["LONGITUD", "LONGITUD_GEOMETRIA", "longitude"]
        ):
            score += 3

        if find_column(
            frame,
            ["SIEVI_CLAS", "TIPO_SINIESTRO", "CLASE_ACCI", "TIPO_CHOQ"]
        ):
            score += 1

        if score > best_score:
            best_name = name
            best_frame = frame
            best_score = score

    return (
        (best_name, best_frame)
        if best_score >= 5
        else (None, None)
    )


def prepare_data(raw: pd.DataFrame) -> pd.DataFrame:

    aliases = {
        "FECHA": [
            "FECHA",
            "FECHA_ACCIDENTE",
            "FECHA_ACCI",
            "fecha_siniestro"
        ],
        "LATITUD": [
            "LATITUD",
            "LATITUD_GEOMETRIA",
            "latitude",
            "lat"
        ],
        "LONGITUD": [
            "LONGITUD",
            "LONGITUD_GEOMETRIA",
            "longitude",
            "lon",
            "lng"
        ],
        "TIPO": [
            "SIEVI_CLAS",
            "TIPO_SINIESTRO",
            "CLASE_ACCI",
            "TIPO_CHOQ",
            "CLASE_ACCIDENTE",
            "TIPO"
        ],
        "LUGAR": [
            "LUGARO",
            "LUGAR",
            "SITIO",
            "UBICACION"
        ],
        "HIPOTESIS": [
            "HIPOTESIS_",
            "HIPOTESIS",
            "CAUSA"
        ],
        "MUERTOS": [
            "SMUERTOS",
            "MUERTOS",
            "FALLECIDOS"
        ],
        "LESIONADOS": [
            "SLESIONADO",
            "LESIONADOS",
            "HERIDOS"
        ],
    }

    data = pd.DataFrame(index=raw.index)

    for target, options in aliases.items():
        source = find_column(raw, options)

        if source is not None:
            data[target] = raw[source]

    data["FECHA"] = (
        parse_dates(data["FECHA"])
        if "FECHA" in data
        else pd.NaT
    )

    for col in ["LATITUD", "LONGITUD", "MUERTOS", "LESIONADOS"]:

        if col not in data:
            data[col] = (
                float("nan")
                if col in ["LATITUD", "LONGITUD"]
                else 0
            )

        data[col] = pd.to_numeric(
            data[col],
            errors="coerce"
        )

    for col in ["TIPO", "LUGAR", "HIPOTESIS"]:

        if col not in data:
            data[col] = "Sin dato"

        data[col] = (
            data[col]
            .fillna("Sin dato")
            .astype(str)
            .str.strip()
        )

        data.loc[
            data[col].str.lower().isin(
                ["", "nan", "none", "-", "na"]
            ),
            col
        ] = "Sin dato"

    data["MUERTOS"] = data["MUERTOS"].fillna(0)
    data["LESIONADOS"] = data["LESIONADOS"].fillna(0)

    data["DIA"] = data["FECHA"].dt.day_name().map({
        "Monday": "Lunes",
        "Tuesday": "Martes",
        "Wednesday": "Miércoles",
        "Thursday": "Jueves",
        "Friday": "Viernes",
        "Saturday": "Sábado",
        "Sunday": "Domingo",
    })

    data["MES"] = data["FECHA"].dt.strftime("%b %Y")
    data["MES_ORDEN"] = data["FECHA"].dt.to_period("M").astype(str)
    data["ORIGEN"] = "Archivo cargado"

    return data.reset_index(drop=True)


@st.cache_data(show_spinner=False)
def load_excel(file_bytes: bytes) -> tuple[pd.DataFrame, str]:

    sheets = pd.read_excel(
        BytesIO(file_bytes),
        sheet_name=None
    )

    sheet_name, raw = find_best_sheet(sheets)

    if raw is None:
        raise ValueError(
            "No se encontró una hoja con fecha, latitud y longitud. "
            "Revisa que hayas cargado SeguraSM_Resultados.xlsx."
        )

    return prepare_data(raw), sheet_name or "Datos"


@st.cache_data(show_spinner=False)
def load_csv(file_bytes: bytes) -> tuple[pd.DataFrame, str]:

    try:
        raw = pd.read_csv(
            BytesIO(file_bytes),
            encoding="utf-8-sig"
        )

    except UnicodeDecodeError:
        raw = pd.read_csv(
            BytesIO(file_bytes),
            encoding="latin-1"
        )

    if raw.empty:
        raise ValueError("El archivo CSV está vacío.")

    if find_column(
        raw,
        ["FECHA", "FECHA_ACCIDENTE", "FECHA_ACCI"]
    ) is None:
        raise ValueError(
            "No se encontró una columna de fecha en el CSV."
        )

    return prepare_data(raw), "CSV cargado"


def style_figure(fig: go.Figure, height: int = 330) -> go.Figure:

    fig.update_layout(
        height=height,
        margin=dict(l=12, r=12, t=28, b=12),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(
            family="DM Sans, sans-serif",
            color=COLORS["ink"],
            size=12
        ),
        title=dict(
            font=dict(
                family="Manrope, sans-serif",
                size=14,
                color=COLORS["navy"]
            ),
            x=0,
            xanchor="left"
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            x=0
        ),
        hoverlabel=dict(
            bgcolor=COLORS["navy"],
            font_color="white"
        ),
    )

    fig.update_xaxes(
        showgrid=False,
        linecolor=COLORS["line"],
        tickfont=dict(color=COLORS["muted"])
    )

    fig.update_yaxes(
        gridcolor="#EDF1F5",
        zeroline=False,
        tickfont=dict(color=COLORS["muted"])
    )

    return fig


def metric_card(
    label: str,
    value: str,
    foot: str,
    accent: str
) -> None:

    st.markdown(
        f"""
        <div class="metric-card" style="--accent:{accent}">
          <div class="metric-label">{label}</div>
          <div class="metric-value">{value}</div>
          <div class="metric-foot">{foot}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section(title: str, subtitle: str) -> None:

    st.markdown(
        f"""
        <div class="section-head">
          <div>
            <div class="section-title">{title}</div>
            <div class="section-sub">{subtitle}</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ------------------------------------------------------------
# BARRA LATERAL Y ARCHIVO
# ------------------------------------------------------------

with st.sidebar:

    st.markdown(
        """
        <div class="brand">
          <div class="brand-mark">🚦</div>
          <div>
            <div class="brand-name">SeguraSM</div>
            <div class="brand-sub">Observatorio vial</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("**SANTA MARTA · MAGDALENA**")
    st.caption("Panel académico de exploración de datos")
    st.divider()

    default_file = Path("SeguraSM_Resultados.xlsx")

    uploaded_file = st.file_uploader(
        "Cargar datos (Excel o CSV)",
        type=["xlsx", "xls", "csv"],
        help=(
            "Puedes cargar SeguraSM_Resultados.xlsx "
            "o un CSV con fecha, latitud y longitud."
        ),
    )

    if uploaded_file is not None:

        file_bytes = uploaded_file.getvalue()
        file_is_csv = uploaded_file.name.lower().endswith(".csv")

    elif default_file.exists():

        file_bytes = default_file.read_bytes()
        file_is_csv = False

        st.caption("✓ Archivo del proyecto cargado automáticamente")

    else:

        file_bytes = None
        file_is_csv = False

        st.info("Carga un archivo Excel o CSV para abrir el tablero.")


if file_bytes is None:

    st.markdown(
        """
        <div class="hero">
          <div class="eyebrow">
            ANÁLISIS DE SEGURIDAD VIAL · SANTA MARTA
          </div>
          <h1>SeguraSM</h1>
          <p>
            Un observatorio académico para explorar los registros
            históricos de siniestros viales y comprender sus patrones.
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.stop()


try:

    data, sheet_name = (
        load_csv(file_bytes)
        if file_is_csv
        else load_excel(file_bytes)
    )

except Exception as error:

    st.error(str(error))
    st.stop()


if data.empty:

    st.warning("El archivo no contiene registros para analizar.")
    st.stop()


# ------------------------------------------------------------
# REGISTROS MANUALES
# ------------------------------------------------------------

st.session_state.setdefault(
    "segurasm_manual_records",
    []
)

if st.session_state["segurasm_manual_records"]:

    manual_raw = pd.DataFrame(
        st.session_state["segurasm_manual_records"]
    )

    manual_data = prepare_data(manual_raw)

    manual_data["ORIGEN"] = "Entrada manual · no verificada"

    data = pd.concat(
        [data, manual_data],
        ignore_index=True
    )


# ------------------------------------------------------------
# FILTROS
# ------------------------------------------------------------

valid_dates = data["FECHA"].dropna()

min_date = (
    valid_dates.min().date()
    if not valid_dates.empty
    else None
)

max_date = (
    valid_dates.max().date()
    if not valid_dates.empty
    else None
)


with st.sidebar:

    st.divider()
    st.markdown("### FILTRAR RESULTADOS")

    if min_date and max_date:

        date_range = st.date_input(
            "Rango de fechas",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
            format="DD/MM/YYYY"
        )

    else:

        date_range = None

    type_values = sorted(
        data["TIPO"].unique().tolist()
    )

    selected_types = st.multiselect(
        "Tipo de siniestro",
        type_values,
        default=type_values
    )

    place_values = sorted([
        value
        for value in data["LUGAR"].unique().tolist()
        if value != "Sin dato"
    ])

    selected_places = st.multiselect(
        "Lugar (opcional)",
        place_values,
        default=[]
    )

    st.divider()

    st.caption(
        "Fuente: registros históricos preparados para el proyecto. "
        "También puedes cargar un archivo propio."
    )


filtered = data.copy()


if (
    date_range
    and isinstance(date_range, (tuple, list))
    and len(date_range) == 2
):

    start_date, end_date = date_range

    filtered = filtered[
        filtered["FECHA"].notna()
        & (filtered["FECHA"].dt.date >= start_date)
        & (filtered["FECHA"].dt.date <= end_date)
    ]


if selected_types:

    filtered = filtered[
        filtered["TIPO"].isin(selected_types)
    ]

else:

    filtered = filtered.iloc[0:0]


if selected_places:

    filtered = filtered[
        filtered["LUGAR"].isin(selected_places)
    ]


# ------------------------------------------------------------
# ENCABEZADO
# ------------------------------------------------------------

period_label = (
    f"{min_date.strftime('%d %b %Y')} — "
    f"{max_date.strftime('%d %b %Y')}"
    if min_date and max_date
    else "Periodo sin fecha"
)


st.markdown(
    f"""
    <div class="hero">
      <div class="eyebrow">
        ANÁLISIS DE SEGURIDAD VIAL · SANTA MARTA, COLOMBIA
      </div>

      <h1>
        SeguraSM<span style="color:#56D4C2">.</span>
      </h1>

      <p>
        Explora la distribución de los siniestros viales registrados,
        identifica patrones temporales y consulta su comportamiento
        geográfico.
      </p>

      <div class="hero-meta">
        <span class="hero-pill">
          PERIODO DEL ARCHIVO · {period_label}
        </span>

        <span class="hero-pill">FUENTE · ANSV</span>
        <span class="hero-pill">ANÁLISIS DESCRIPTIVO</span>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)


if filtered.empty:

    st.warning(
        "No hay registros para los filtros seleccionados. "
        "Amplía el periodo o selecciona otros tipos de siniestro."
    )

    st.stop()


# ------------------------------------------------------------
# INDICADORES
# ------------------------------------------------------------

section(
    "Panorama general",
    "Indicadores calculados sobre los registros que cumplen los filtros seleccionados."
)

coords = filtered.dropna(
    subset=["LATITUD", "LONGITUD"]
)

coords = coords[
    coords["LATITUD"].between(-90, 90)
    & coords["LONGITUD"].between(-180, 180)
]


k1, k2, k3, k4 = st.columns(4, gap="medium")

with k1:

    metric_card(
        "REGISTROS ANALIZADOS",
        f"{len(filtered):,}",
        "Registros incluidos en el filtro",
        COLORS["teal"]
    )

with k2:

    metric_card(
        "PERSONAS FALLECIDAS",
        f"{int(filtered['MUERTOS'].sum()):,}",
        "Fallecimientos registrados",
        COLORS["red"]
    )

with k3:

    metric_card(
        "PERSONAS LESIONADAS",
        f"{int(filtered['LESIONADOS'].sum()):,}",
        "Lesiones registradas",
        COLORS["gold"]
    )

with k4:

    metric_card(
        "PUNTOS EN EL MAPA",
        f"{len(coords):,}",
        "Registros con coordenadas válidas",
        COLORS["navy2"]
    )


manual_in_view = int(
    (
        filtered["ORIGEN"]
        == "Entrada manual · no verificada"
    ).sum()
)

source_caption = (
    f"Cobertura del archivo base: {period_label} "
    f"· Fuente: {sheet_name} "
    f"· {filtered['TIPO'].nunique()} categorías."
)

if manual_in_view:

    source_caption += (
        f" Incluye {manual_in_view} registro(s) "
        "manual(es) no verificado(s)."
    )

st.caption(source_caption)


# ------------------------------------------------------------
# VISTAS PRINCIPALES
# ------------------------------------------------------------

tab_overview, tab_map, tab_data, tab_add = st.tabs([
    "✦  Resumen",
    "⌖  Mapa de siniestros",
    "▤  Registros",
    "＋  Agregar dato"
])


# ------------------------------------------------------------
# PESTAÑA RESUMEN
# ------------------------------------------------------------

with tab_overview:

    section(
        "Comportamiento de los siniestros",
        "Compara los registros por mes, tipo y día de la semana."
    )

    c1, c2 = st.columns(
        [1.25, 1],
        gap="large"
    )

    with c1:

        with st.container(border=True):

            st.markdown(
                """
                <div class="panel-title">Evolución mensual</div>
                <div class="panel-caption">
                  Cantidad de registros por mes disponible.
                </div>
                """,
                unsafe_allow_html=True
            )

            monthly = (
                filtered
                .dropna(subset=["FECHA"])
                .groupby("MES_ORDEN")
                .size()
                .reset_index(name="Registros")
            )

            monthly["Mes"] = (
                pd.to_datetime(
                    monthly["MES_ORDEN"] + "-01"
                )
                .dt.strftime("%b %Y")
            )

            fig = px.bar(
                monthly,
                x="Mes",
                y="Registros",
                text="Registros",
                color_discrete_sequence=[COLORS["teal"]]
            )

            fig.update_traces(
                textposition="outside",
                marker_cornerradius=7,
                hovertemplate=(
                    "%{x}<br>"
                    "Registros: %{y}"
                    "<extra></extra>"
                )
            )

            fig.update_yaxes(
                title="Registros",
                rangemode="tozero"
            )

            fig.update_xaxes(title="")

            st.plotly_chart(
                style_figure(fig, 330),
                use_container_width=True,
                config={"displayModeBar": False}
            )

    with c2:

        with st.container(border=True):

            st.markdown(
                """
                <div class="panel-title">Tipos de siniestro</div>
                <div class="panel-caption">
                  Participación de cada categoría en el total filtrado.
                </div>
                """,
                unsafe_allow_html=True
            )

            by_type = (
                filtered
                .groupby("TIPO")
                .size()
                .reset_index(name="Registros")
                .sort_values("Registros", ascending=False)
            )

            fig = px.pie(
                by_type,
                names="TIPO",
                values="Registros",
                hole=.66,
                color_discrete_sequence=[
                    COLORS["teal"],
                    COLORS["navy2"],
                    COLORS["gold"],
                    "#79A9B8",
                    "#D77878",
                    "#A6B4C2"
                ]
            )

            fig.update_traces(
                textposition="outside",
                textinfo="percent",
                hole=0.66,
                marker=dict(
                    line=dict(color="white", width=3)
                ),
                hovertemplate=(
                    "%{label}<br>"
                    "%{value} registros "
                    "(%{percent})"
                    "<extra></extra>"
                )
            )

            st.plotly_chart(
                style_figure(fig, 330),
                use_container_width=True,
                config={"displayModeBar": False}
            )


    c3, c4 = st.columns(2, gap="large")


    with c3:

        with st.container(border=True):

            st.markdown(
                """
                <div class="panel-title">Registros por día</div>
                <div class="panel-caption">
                  Distribución según el día de la semana.
                </div>
                """,
                unsafe_allow_html=True
            )

            order = [
                "Lunes",
                "Martes",
                "Miércoles",
                "Jueves",
                "Viernes",
                "Sábado",
                "Domingo"
            ]

            by_day = (
                filtered
                .dropna(subset=["DIA"])
                .groupby("DIA")
                .size()
                .reindex(order)
                .fillna(0)
                .reset_index(name="Registros")
            )

            fig = px.bar(
                by_day,
                x="DIA",
                y="Registros",
                text="Registros",
                color_discrete_sequence=[COLORS["navy2"]]
            )

            fig.update_traces(
                textposition="outside",
                marker_cornerradius=6
            )

            fig.update_xaxes(
                title="",
                tickangle=-20
            )

            fig.update_yaxes(
                title="Registros",
                rangemode="tozero"
            )

            st.plotly_chart(
                style_figure(fig, 310),
                use_container_width=True,
                config={"displayModeBar": False}
            )


    with c4:

        with st.container(border=True):

            st.markdown(
                """
                <div class="panel-title">Personas afectadas</div>
                <div class="panel-caption">
                  Totales reportados en los registros seleccionados.
                </div>
                """,
                unsafe_allow_html=True
            )

            people = pd.DataFrame({
                "Categoría": [
                    "Fallecidas",
                    "Lesionadas"
                ],
                "Personas": [
                    filtered["MUERTOS"].sum(),
                    filtered["LESIONADOS"].sum()
                ]
            })

            fig = px.bar(
                people,
                x="Categoría",
                y="Personas",
                color="Categoría",
                text_auto=True,
                color_discrete_map={
                    "Fallecidas": COLORS["red"],
                    "Lesionadas": COLORS["teal"]
                }
            )

            fig.update_traces(
                textposition="outside",
                marker_cornerradius=7,
                showlegend=False
            )

            fig.update_yaxes(
                title="Personas",
                rangemode="tozero"
            )

            fig.update_xaxes(title="")

            st.plotly_chart(
                style_figure(fig, 310),
                use_container_width=True,
                config={"displayModeBar": False}
            )


    # Hallazgos calculados a partir de los conteos.

    top_type = filtered["TIPO"].value_counts()
    top_day = filtered["DIA"].value_counts()

    top_place = (
        filtered.loc[
            filtered["LUGAR"] != "Sin dato",
            "LUGAR"
        ].value_counts()
    )

    facts = []

    if not top_type.empty:

        facts.append(
            f"La categoría más frecuente es "
            f"**{top_type.index[0]}**, con "
            f"**{int(top_type.iloc[0])} registros**."
        )

    if not top_day.empty:

        facts.append(
            f"El día con más registros es "
            f"**{top_day.index[0]}**, con "
            f"**{int(top_day.iloc[0])} registros**."
        )

    if not top_place.empty:

        facts.append(
            f"El lugar más repetido entre los registros "
            f"con ubicación textual es "
            f"**{top_place.index[0]}** "
            f"(**{int(top_place.iloc[0])} registros**)."
        )


    section(
        "Lecturas rápidas",
        "Observaciones automáticas a partir de los conteos del archivo; no explican causas."
    )

    st.markdown(
        '<div class="insight">'
        + "<br><br>".join(facts)
        + "</div>",
        unsafe_allow_html=True
    )


# ------------------------------------------------------------
# PESTAÑA MAPA
# ------------------------------------------------------------

with tab_map:

    section(
        "Distribución geográfica",
        "Cada punto representa un registro con coordenadas válidas dentro de la selección."
    )

    if not coords.empty:

        map_data = coords.copy()

        map_data["FECHA_TEXTO"] = (
            map_data["FECHA"]
            .dt.strftime("%d/%m/%Y")
        )

        fig = px.scatter_map(
            map_data,
            lat="LATITUD",
            lon="LONGITUD",
            color="TIPO",
            size_max=10,
            hover_name="TIPO",
            hover_data={
                "FECHA_TEXTO": True,
                "LUGAR": True,
                "MUERTOS": True,
                "LESIONADOS": True,
                "LATITUD": False,
                "LONGITUD": False
            },
            zoom=11,
            height=590,
            map_style="carto-positron",
            color_discrete_sequence=[
                COLORS["teal"],
                COLORS["navy2"],
                COLORS["gold"],
                "#D77878",
                "#79A9B8",
                "#94A3B8"
            ]
        )

        fig.update_layout(
            margin=dict(l=0, r=0, t=5, b=0),
            paper_bgcolor="white",
            legend_title_text="Tipo"
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
            config={"displayModeBar": False}
        )

        st.caption(
            f"{len(coords):,} de {len(filtered):,} "
            "registros seleccionados tienen coordenadas válidas."
        )

    else:

        st.info(
            "No hay coordenadas válidas para los filtros seleccionados."
        )


    loc_col, hypothesis_col = st.columns(2, gap="large")


    with loc_col:

        with st.container(border=True):

            st.markdown(
                """
                <div class="panel-title">Lugares más frecuentes</div>
                <div class="panel-caption">
                  Primeros ocho lugares por número de registros.
                </div>
                """,
                unsafe_allow_html=True
            )

            places = (
                filtered[
                    filtered["LUGAR"] != "Sin dato"
                ]["LUGAR"]
                .value_counts()
                .head(8)
                .sort_values()
                .reset_index()
            )

            places.columns = [
                "Lugar",
                "Registros"
            ]

            if not places.empty:

                fig = px.bar(
                    places,
                    x="Registros",
                    y="Lugar",
                    orientation="h",
                    text="Registros",
                    color_discrete_sequence=[COLORS["teal"]]
                )

                fig.update_traces(
                    textposition="outside"
                )

                st.plotly_chart(
                    style_figure(fig, 340),
                    use_container_width=True,
                    config={"displayModeBar": False}
                )

            else:

                st.caption(
                    "El archivo no contiene lugares textuales para esta selección."
                )


    with hypothesis_col:

        with st.container(border=True):

            st.markdown(
                """
                <div class="panel-title">Hipótesis reportadas</div>
                <div class="panel-caption">
                  Hipótesis más frecuentes en los registros disponibles.
                </div>
                """,
                unsafe_allow_html=True
            )

            hypotheses = (
                filtered[
                    filtered["HIPOTESIS"] != "Sin dato"
                ]["HIPOTESIS"]
                .value_counts()
                .head(8)
                .sort_values()
                .reset_index()
            )

            hypotheses.columns = [
                "Hipótesis",
                "Registros"
            ]

            if not hypotheses.empty:

                fig = px.bar(
                    hypotheses,
                    x="Registros",
                    y="Hipótesis",
                    orientation="h",
                    text="Registros",
                    color_discrete_sequence=[COLORS["navy2"]]
                )

                fig.update_traces(
                    textposition="outside"
                )

                st.plotly_chart(
                    style_figure(fig, 340),
                    use_container_width=True,
                    config={"displayModeBar": False}
                )

            else:

                st.caption(
                    "El archivo no contiene hipótesis para esta selección."
                )


# ------------------------------------------------------------
# PESTAÑA REGISTROS
# ------------------------------------------------------------

with tab_data:

    section(
        "Explorar los registros",
        "Consulta los campos disponibles y descarga el conjunto filtrado."
    )

    table = filtered[
        [
            "FECHA",
            "TIPO",
            "LUGAR",
            "HIPOTESIS",
            "MUERTOS",
            "LESIONADOS",
            "LATITUD",
            "LONGITUD",
            "ORIGEN"
        ]
    ].copy()

    table["FECHA"] = (
        table["FECHA"]
        .dt.strftime("%d/%m/%Y")
    )

    search = st.text_input(
        "Buscar en tipo, lugar o hipótesis",
        placeholder="Escribe una palabra para filtrar la tabla..."
    )

    if search.strip():

        mask = (
            table[
                ["TIPO", "LUGAR", "HIPOTESIS"]
            ]
            .astype(str)
            .apply(
                lambda col: col.str.contains(
                    search.strip(),
                    case=False,
                    na=False
                )
            )
            .any(axis=1)
        )

        table = table[mask]

    st.dataframe(
        table,
        use_container_width=True,
        hide_index=True,
        height=430
    )

    csv = table.to_csv(
        index=False
    ).encode("utf-8-sig")

    st.download_button(
        "⬇ Descargar registros filtrados (CSV)",
        data=csv,
        file_name="SeguraSM_registros_filtrados.csv",
        mime="text/csv"
    )


# ------------------------------------------------------------
# PESTAÑA AGREGAR DATO
# ------------------------------------------------------------

with tab_add:

    section(
        "Agregar un registro",
        "Introduce un dato para explorar cómo cambiarían los indicadores. "
        "Los registros manuales no se verifican contra una fuente oficial."
    )

    st.markdown(
        """
        <div class="method">
          <strong>Importante.</strong>
          Los datos que agregues aquí son aportes manuales y solo se
          conservan durante tu sesión actual. Se identificarán como
          no verificados y no se mezclarán silenciosamente con la
          fuente oficial.
        </div>
        """,
        unsafe_allow_html=True
    )

    with st.form("segurasm_add_record"):

        c1, c2 = st.columns(2)

        with c1:

            manual_date = st.date_input(
                "Fecha del siniestro",
                value=date.today(),
                format="DD/MM/YYYY"
            )

            type_choice = st.selectbox(
                "Tipo de siniestro",
                [
                    "CHOQUE",
                    "ATROPELLO",
                    "VOLCAMIENTO",
                    "CAÍDA DE OCUPANTE",
                    "OTRO"
                ]
            )

            custom_type = st.text_input(
                "Especifica el tipo (si elegiste OTRO)",
                placeholder="Ej. Incendio de vehículo"
            )

            place = st.text_input(
                "Lugar o sector",
                placeholder="Ej. Avenida del Libertador"
            )

            hypothesis = st.text_input(
                "Hipótesis o causa reportada",
                placeholder="Ej. No mantener distancia"
            )

        with c2:

            deaths = st.number_input(
                "Personas fallecidas",
                min_value=0,
                max_value=1000,
                value=0,
                step=1
            )

            injuries = st.number_input(
                "Personas lesionadas",
                min_value=0,
                max_value=1000,
                value=0,
                step=1
            )

            lat_text = st.text_input(
                "Latitud (opcional)",
                placeholder="Ej. 11.2408"
            )

            lon_text = st.text_input(
                "Longitud (opcional)",
                placeholder="Ej. -74.1990"
            )

        submitted = st.form_submit_button(
            "＋ Agregar registro",
            use_container_width=True,
            type="primary"
        )


    if submitted:

        chosen_type = (
            custom_type.strip()
            if type_choice == "OTRO" and custom_type.strip()
            else type_choice
        )

        try:

            lat_value = (
                float(lat_text.replace(",", "."))
                if lat_text.strip()
                else float("nan")
            )

            lon_value = (
                float(lon_text.replace(",", "."))
                if lon_text.strip()
                else float("nan")
            )

            if (
                pd.notna(lat_value)
                and not -90 <= lat_value <= 90
            ):

                raise ValueError(
                    "La latitud debe estar entre -90 y 90."
                )

            if (
                pd.notna(lon_value)
                and not -180 <= lon_value <= 180
            ):

                raise ValueError(
                    "La longitud debe estar entre -180 y 180."
                )

            if pd.notna(lat_value) != pd.notna(lon_value):

                raise ValueError(
                    "Ingresa latitud y longitud juntas, "
                    "o deja ambas vacías."
                )

            st.session_state[
                "segurasm_manual_records"
            ].append({
                "FECHA": manual_date,
                "TIPO": chosen_type,
                "LUGAR": place.strip() or "Sin dato",
                "HIPOTESIS": hypothesis.strip() or "Sin dato",
                "MUERTOS": int(deaths),
                "LESIONADOS": int(injuries),
                "LATITUD": lat_value,
                "LONGITUD": lon_value,
            })

            st.success(
                "Registro agregado. Los indicadores, las gráficas "
                "y la tabla se actualizarán con este dato."
            )

            st.rerun()

        except ValueError as error:

            st.error(str(error))


    manual_count = len(
        st.session_state["segurasm_manual_records"]
    )

    st.caption(
        f"Registros manuales añadidos en esta sesión: {manual_count}"
    )

    if manual_count:

        manual_export = pd.DataFrame(
            st.session_state["segurasm_manual_records"]
        )

        st.download_button(
            "⬇ Descargar mis registros manuales (CSV)",
            data=manual_export.to_csv(
                index=False
            ).encode("utf-8-sig"),
            file_name="SeguraSM_registros_manual.csv",
            mime="text/csv"
        )

        if st.button(
            "Eliminar todos mis registros manuales",
            type="secondary"
        ):

            st.session_state[
                "segurasm_manual_records"
            ] = []

            st.rerun()


# ------------------------------------------------------------
# NOTA METODOLÓGICA Y PIE DE PÁGINA
# ------------------------------------------------------------

st.markdown(
    """
    <div class="method">
      <strong>Nota metodológica.</strong>
      Este tablero describe únicamente los registros históricos
      incluidos en el archivo utilizado. La cobertura identificada
      para este conjunto es del 01/01/2019 al 11/08/2019.
      No representa necesariamente todos los siniestros ocurridos
      en Santa Marta y no constituye una predicción de accidentes futuros.
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="footer">
      SEGURASM · PROYECTO ACADÉMICO DE ANÁLISIS DE SEGURIDAD VIAL
      · SANTA MARTA, COLOMBIA
    </div>
    """,
    unsafe_allow_html=True
)
