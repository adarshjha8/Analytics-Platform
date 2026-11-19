
import streamlit as st
import plotly.express as px
import textwrap
import pandas as pd
import os

from analytics.dashboard_engine import get_dashboard_data


# ==========================================================
# 1. PAGE CONFIGURATION
# ==========================================================

st.set_page_config(
    page_title="Analytics Platform",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ==========================================================
# 2. HTML RENDERING - IMPORTANT FIX
# ==========================================================

def html(content):
    """
    Render actual HTML directly.
    Do not use st.markdown for custom HTML.
    """

    st.html(textwrap.dedent(content).strip())


# ==========================================================
# 3. CUSTOM DARK THEME
# ==========================================================

html("""
<style>

.stApp {
    background: #0b1020;
    color: #f1f5f9;
}

header[data-testid="stHeader"] {
    background: #0b1020;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 1rem;
    max-width: 100%;
}

[data-testid="stMetric"] {
    background: linear-gradient(135deg, #172747, #19233d);
    border: 1px solid #30466b;
    border-radius: 13px;
    padding: 16px;
    min-height: 105px;
}

[data-testid="stMetricLabel"] {
    color: #b8c7e2 !important;
}

[data-testid="stMetricValue"] {
    color: white !important;
}

[data-testid="stMetricDelta"] {
    color: #34d399 !important;
}

div[data-testid="stVerticalBlockBorderWrapper"] {
    background: #141d33;
    border: 1px solid #293753;
    border-radius: 13px;
    padding: 12px;
}

[data-testid="stMain"] {
    background: #0b1020;
}

[data-testid="stSelectbox"] label,
[data-testid="stDateInput"] label {
    color: #cbd5e1 !important;
}

.stSelectbox div[data-baseweb="select"] > div,
.stDateInput input,
.stTextInput input {
    background: #18233c !important;
    color: white !important;
    border-color: #354767 !important;
}

.stButton button {
    background: #4f46e5;
    color: white;
    border: 1px solid #6366f1;
    border-radius: 9px;
    width: 100%;
    font-weight: 600;
}

.stButton button:hover {
    background: #6366f1;
    color: white;
}

h1, h2, h3, h4 {
    color: #f8fafc !important;
}

p, label {
    color: #cbd5e1;
}

[data-testid="stCaptionContainer"] {
    color: #94a3b8;
}

hr {
    border-color: #293753;
}

</style>
""")


# ==========================================================
# 4. LOAD DATA
# ==========================================================

@st.cache_data(ttl=60, show_spinner=False)
def load_dashboard(filters):
    return get_dashboard_data(filters)


with st.spinner("Loading installation intelligence..."):

    initial_data = load_dashboard({})

options = initial_data["filter_options"]

min_date = options["date_range"]["start"]
max_date = options["date_range"]["end"]


# ==========================================================
# 5. SESSION STATE
# ==========================================================

FILTER_KEYS = [
    "source_filter",
    "utility_filter",
    "type_filter",
    "division_filter",
    "vendor_type_filter",
    "vendor_manager_filter"
]


def reset_all_filters():

    for key in FILTER_KEYS:
        st.session_state[key] = "All"

    st.session_state["from_date_filter"] = min_date
    st.session_state["to_date_filter"] = max_date


for key in FILTER_KEYS:

    if key not in st.session_state:
        st.session_state[key] = "All"


if "from_date_filter" not in st.session_state:
    st.session_state["from_date_filter"] = min_date

if "to_date_filter" not in st.session_state:
    st.session_state["to_date_filter"] = max_date


# ==========================================================
# 6. TOP HEADER
# ==========================================================

header_left, header_right = st.columns([5, 2])

with header_left:

    html("""
    <div style="
        display:flex;
        align-items:center;
        gap:14px;
        min-height:76px;
        padding:12px 0;
        overflow:visible;
        line-height:1.35;
    ">

        <div style="
            background:linear-gradient(135deg,#4f46e5,#2563eb);
            padding:10px 15px;
            border-radius:12px;
            font-size:27px;
        ">
            ⚡
        </div>

        <div>

            <div style="
                font-size:25px;
                font-weight:750;
                line-height:1.35;
                white-space:nowrap;
                color:white;
            ">
                AI Analytics Platform
            </div>

        </div>

    </div>
    """)


with header_right:

    html("""
    <div style="
        text-align:right;
        padding-top:15px;
        color:#a5b4fc;
        font-size:14px;
    ">
        ⚡ Analytics Workspace
    </div>
    """)


st.divider()


# ==========================================================
# 7. PAGE NAVIGATION AND MAIN LAYOUT
# ==========================================================

if "active_page" not in st.session_state:
    st.session_state["active_page"] = "Dashboard"

left_panel, center_panel = st.columns(
    [1.25, 8.0],
    gap="medium"
)


# ==========================================================
# 8. LEFT NAVIGATION AND FILTERS
# ==========================================================

with left_panel:

    # Data Source filter removed; keep source unrestricted.
    source = None

    st.markdown("### Dashboard Filters")


    # FILTER FUNCTION

    def create_filter(label, key, values):

        clean_values = sorted({
            str(value).strip()
            for value in values
            if value is not None and str(value).strip()
        })

        selected = st.selectbox(
            label,
            options=["All"] + clean_values,
            key=key
        )

        return None if selected == "All" else selected


    # UTILITY

    utility = create_filter(
        "Utility",
        "utility_filter",
        options["utility"]
    )


    # INSTALLATION TYPE

    installation_type = create_filter(
        "Installation Type",
        "type_filter",
        options["installation_type"]
    )


    # DIVISION

    division = create_filter(
        "Division",
        "division_filter",
        options["division_name"]
    )


    # VENDOR TYPE

    vendor_type = create_filter(
        "Vendor Type",
        "vendor_type_filter",
        options["vendor_type"]
    )


    # VENDOR MANAGER

    vendor_manager = create_filter(
        "Vendor Manager",
        "vendor_manager_filter",
        options["vendor_manager"]
    )


    # DATE FILTER

    st.markdown("### Installation Date")

    start_date = st.date_input(
        "From",
        value=st.session_state["from_date_filter"],
        min_value=min_date,
        max_value=max_date,
        key="from_date_filter"
    )

    end_date = st.date_input(
        "To",
        value=st.session_state["to_date_filter"],
        min_value=min_date,
        max_value=max_date,
        key="to_date_filter"
    )

    if start_date > end_date:
        st.warning("From date is later than To date. The dates have been reversed for filtering.")
        start_date, end_date = end_date, start_date


    # RESET BUTTON

    st.button(
        "↻ Reset All Filters",
        on_click=reset_all_filters,
        use_container_width=True
    )

    st.divider()


    # NAVIGATION (MOVED BELOW FILTERS)

    st.divider()
    st.markdown("### Navigation")

    nav_items = [
        ("🏠", "Dashboard"),
        ("💬", "Ask AI")
    ]

    for icon, label in nav_items:
        active = st.session_state["active_page"] == label
        is_available = label in ("Dashboard", "Ask AI")

        if st.button(
            f"{icon}  {label}",
            key=f"nav_{label.lower().replace(' ', '_')}",
            use_container_width=True,
            type="primary" if active else "secondary",
            disabled=not is_available
        ):
            st.session_state["active_page"] = label
            st.rerun()

    st.divider()


    # DATA ENGINE INFORMATION

    html("""
    <div style="
        background:#103b37;
        border:1px solid #167b68;
        border-radius:10px;
        padding:13px;
        color:#6ee7b7;
        font-size:12px;
        line-height:1.9;
    ">



    </div>
    """)


# ==========================================================
# 9. APPLY FILTERS
# ==========================================================

filters = {

    "source": source,

    "utility": utility,

    "installation_type": installation_type,

    "division_name": division,

    "vendor_type": vendor_type,

    "vendor_manager": vendor_manager,

    "start_date": start_date,

    "end_date": end_date

}


# ==========================================================
# 10. LOAD FILTERED DASHBOARD
# ==========================================================

with st.spinner("Analysing installation data..."):

    results = load_dashboard(filters)


kpis = results["kpis"].iloc[0]

daily = results["daily_trend"]

monthly = results["monthly_trend"]

division_data = results["division"]



# ==========================================================
# 11. CENTER DASHBOARD
# ==========================================================

if st.session_state["active_page"] == "Dashboard":

    with center_panel:


        # WELCOME HEADER + ASK AI BUTTON

        welcome_col, welcome_ai_col = st.columns([5, 1.25], vertical_alignment="center")

        with welcome_col:
            html("""
            <div style="padding:8px 0 15px 0; min-height:76px; line-height:1.35;">
                <div style="
                    font-size:25px;
                    font-weight:750;
                    line-height:1.35;
                    color:white;
                ">
                
                </div>
                <div style="
                    font-size:14px;
                    line-height:1.5;
                    color:#94a3b8;
                ">
                    Here's the latest installation performance overview.
                </div>
            </div>
            """)

        with welcome_ai_col:
            if st.button(
                "✨ Ask AI",
                key="ask_ai_beside_welcome",
                use_container_width=True,
                type="primary"
            ):
                st.session_state["active_page"] = "Ask AI"
                st.rerun()


        # ------------------------------------------------------
        # KPI CARDS
        # ------------------------------------------------------

        total_divisions = (
            division_data["division_name"].nunique()
            if not division_data.empty else 0
        )

        c1, c2, c3, c4 = st.columns(4)

        with c1:

            st.metric(
                "⚡ Total Installations",
                f"{int(kpis['total_records']):,}"
            )

        with c2:

            st.metric(
                "📊 MI Records",
                f"{int(kpis['mi_records']):,}"
            )

        with c3:

            st.metric(
                "🔷 NMI Records",
                f"{int(kpis['nmi_records']):,}"
            )

        with c4:

            st.metric(
                "🏢 Divisions",
                f"{total_divisions:,}"
            )


        # ======================================================
        # LATEST INSTALLATION DATE - MI AND NMI KPIs
        # ======================================================

        latest_date_kpis = results["latest_date_kpis"]

        with st.container(border=True):

            if not latest_date_kpis.empty and latest_date_kpis.iloc[0]["latest_date"] is not None:

                latest_row = latest_date_kpis.iloc[0]
                latest_date = pd.to_datetime(latest_row["latest_date"]).strftime("%d %b %Y")

                st.markdown(f"### Latest Installation Date: **{latest_date}**")

                latest_mi_col, latest_nmi_col = st.columns(2)

                with latest_mi_col:
                    st.metric(
                        "📊 MI Installations",
                        f"{int(latest_row['mi_records']):,}"
                    )

                with latest_nmi_col:
                    st.metric(
                        "🟠 NMI Installations",
                        f"{int(latest_row['nmi_records']):,}"
                    )

            else:
                st.info("No installation records available for the selected filters.")


        # ======================================================
        # MONTHLY TREND
        # ======================================================

        with st.container(border=True):

            st.markdown("### Monthly Installation Trend")

            if not monthly.empty:

                monthly_chart = monthly.sort_values("month").copy()
                monthly_chart["month_label"] = (
                    pd.to_datetime(monthly_chart["month"]).dt.strftime("%b %Y")
                )

                fig_monthly = px.bar(
                    monthly_chart,
                    x="month_label",
                    y=["mi_records", "nmi_records"],
                    barmode="group",
                    text_auto=True,
                    color_discrete_map={
                        "mi_records": "#3b9cff",
                        "nmi_records": "#F97316"
                    },
                    labels={
                        "month_label": "Month",
                        "value": "Records",
                        "variable": "Type"
                    }
                )

                fig_monthly.update_traces(
                    texttemplate="%{y:,}",
                    textposition="inside",
                    insidetextanchor="middle",
                    textfont=dict(color="white", size=11),
                    cliponaxis=False
                )

                fig_monthly.update_layout(
                    template="plotly_dark",
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    height=280,
                    margin=dict(l=5, r=5, t=10, b=5),
                    xaxis_title="Month",
                    yaxis_title="Records",
                    legend_title_text=""
                )

                # Use readable month labels instead of numeric date values.
                fig_monthly.update_xaxes(
                    type="category",
                    categoryorder="array",
                    categoryarray=monthly_chart["month_label"].tolist(),
                    showgrid=False
                )

                st.plotly_chart(
                    fig_monthly,
                    use_container_width=True
                )

            else:

                st.info("No monthly data available.")


        # ======================================================
        # UTILITY-WISE DIVISION PERFORMANCE TABLE
        # ======================================================

        st.markdown("### Utility-wise Division Performance")

        ranked_divisions = None

        if not division_data.empty:

            # Retain ranking data for the existing Key Insights section.
            ranked_divisions = (
                division_data.groupby(
                    "division_name",
                    as_index=False
                )["total_records"]
                .sum()
                .sort_values(
                    "total_records",
                    ascending=False
                )
            )

            division_table = division_data[
                [
                    "utility",
                    "division_name",
                    "mi_records",
                    "nmi_records",
                    "total_records",
                    "manpower"
                ]
            ].copy()

            division_table.columns = [
                "Utility",
                "Division",
                "MI",
                "NMI",
                "Total",
                "Manpower"
            ]

            for count_column in ["MI", "NMI", "Total", "Manpower"]:
                division_table[count_column] = (
                    division_table[count_column].fillna(0).astype(int)
                )

            st.dataframe(
                division_table,
                hide_index=True,
                use_container_width=True,
                height=420
            )

        else:

            st.info("Division performance data is unavailable for the selected filters.")


        # ======================================================
        # FIELD WORKER PRODUCTIVITY
        # ======================================================

        st.markdown("### Field Worker Productivity")

        productivity_data = results["field_worker_productivity"]

        if not productivity_data.empty:

            productivity_table = productivity_data.rename(
                columns={
                    "field_worker_id": "Field Worker ID"
                }
            ).copy()

            for count_column in ["MI", "NMI", "MI + NMI"]:
                productivity_table[count_column] = (
                    productivity_table[count_column].fillna(0).astype(int)
                )

            st.dataframe(
                productivity_table,
                hide_index=True,
                use_container_width=True,
                height=450,
                column_config={
                    "Field Worker ID": st.column_config.TextColumn(
                        "Field Worker ID"
                    ),
                    "MI": st.column_config.NumberColumn(
                        "MI",
                        format="%d"
                    ),
                    "NMI": st.column_config.NumberColumn(
                        "NMI",
                        format="%d"
                    ),
                    "MI + NMI": st.column_config.NumberColumn(
                        "MI + NMI",
                        format="%d"
                    )
                }
            )

            st.caption(
                f"Showing {len(productivity_table):,} unique field worker IDs. "
                "Productivity is calculated from the currently selected dashboard filters."
            )

        else:
            st.info(
                "No field worker productivity data is available for the selected filters. "
                "Check that the MI and NMI field worker ID columns are present in dated_records."
            )



# ==========================================================
# 12. AI PAGE - GEMINI DATA ANALYST
# ==========================================================

if st.session_state["active_page"] == "Ask AI":

    with center_panel:

        st.markdown("## ✨ AI ChatBot")
        st.caption("Ask questions in natural language about your MI and NMI installation data.")

        try:
            from ai_assistant import ask_data_question

            gemini_ready = bool(os.getenv("GEMINI_API_KEY"))

            if not gemini_ready:
                try:
                    gemini_ready = bool(
                        st.secrets.get("GEMINI_API_KEY")
                    )
                except Exception:
                    gemini_ready = False

        except Exception as import_error:
            ask_data_question = None
            gemini_ready = False
            st.error(f"AI module could not be loaded: {import_error}")

        with st.container(border=True):

            html("""
            <div style="
                background:linear-gradient(120deg,#28245c,#172b4b);
                border:1px solid #48418b;
                border-radius:12px;
                padding:20px;
                margin-bottom:15px;
            ">
                <div style="font-size:22px;font-weight:750;color:white;">
                    ✨ AI Assistant
                </div>
                <div style="font-size:14px;color:#cbd5e1;margin-top:8px;">
                    Ask questions about installations, divisions, vendors, utilities,
                    dates, and field-worker productivity.
                </div>
            </div>
            """)

            st.markdown("### Suggested Questions")
            questions = [
                "Which division has the highest number of installations?",
                "Show the top 10 field workers by total MI and NMI installations.",
                "Compare MI and NMI installation counts by utility.",
                "Which vendors have completed the most installations?",
                "Show monthly installation trends for the last 3 months."
            ]

            for index, suggested_question in enumerate(questions):
                if st.button(
                    f"💬  {suggested_question}",
                    key=f"suggested_question_{index}",
                    use_container_width=True
                ):
                    st.session_state["ai_question_input"] = suggested_question

            st.divider()

            if gemini_ready:
                st.success("API connected")
            else:
                st.warning(
                    "Gemini API key not detected. Configure GEMINI_API_KEY "
                    "in your environment variables or Streamlit Secrets."
                )

            with st.form("ai_question_form", clear_on_submit=False):
                question = st.text_area(
                    "Ask a question",
                    key="ai_question_input",
                    placeholder="Example: Which division had the highest MI installations last month?",
                    height=100
                )
                ask_clicked = st.form_submit_button(
                    "➤ Ask AI",
                    use_container_width=True,
                    disabled=not gemini_ready
                )

            if ask_clicked and question.strip():
                current_ai_filters = {
                    "utility": utility,
                    "installation_type": installation_type,
                    "division_name": division,
                    "vendor_type": vendor_type,
                    "vendor_manager": vendor_manager,
                    "start_date": start_date,
                    "end_date": end_date
                }

                with st.spinner("Gemini is analysing your installation data..."):
                    try:
                        response = ask_data_question(
                            question,
                            filters=current_ai_filters
                        )
                        st.markdown("### Answer")
                        st.markdown(response["answer"])

                        if not response["data"].empty:
                            st.markdown("### Query Results")
                            st.dataframe(
                                response["data"],
                                hide_index=True,
                                use_container_width=True
                            )

                        with st.expander("View generated SQL"):
                            st.code(response["sql"], language="sql")

                    except Exception as exc:
                        st.error(f"Unable to answer this question: {exc}")
                        st.caption(
                            "Check your internet connection, Gemini API quota, "
                            "Parquet file paths, and the generated query."
                        )


# ==========================================================
# 13. FOOTER
# ==========================================================

st.divider()

html("""
<div style="
    text-align:center;
    color:#64748b;
    font-size:11px;
    padding:12px;
">
    Analytics Platform |
    Python • DuckDB • Parquet • Streamlit
</div>
""")
