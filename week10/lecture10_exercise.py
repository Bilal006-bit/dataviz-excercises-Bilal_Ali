
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
import datetime

st.set_page_config(page_title="CO2 Dashboard", page_icon="🌱", layout="wide")

# ── Data ──────────────────────────────────────────────────────────────────────
# @st.cache_data: Streamlit reruns the entire script on every widget interaction.
# Without caching, the CSV is read from disk on every interaction — slow and wasteful.
# cache_data stores the result after the first run and reuses it until the file changes.
@st.cache_data
def load_data():
    # .resolve() first: when run as `streamlit run lecture10_exercise.py` from
    # inside week10/, __file__ is a single segment ("lecture10_exercise.py"),
    # so parent.parent would collapse to cwd without resolving to absolute first.
    path = Path(__file__).resolve().parent.parent / 'data' / 'co2_emissions.csv'
    df = pd.read_csv(path)
    df['Date'] = pd.to_datetime(df['Year'].astype(str) + '-01-01')
    return df

df = load_data()

st.title("🌱 CO2 Emissions Explorer")
st.caption("Source: Our World in Data — ourworldindata.org/co2-emissions")

# ── TASK 1: Sidebar with 5 widgets ────────────────────────────────────────────
#   a) st.selectbox for Region (with 'All')
#   b) st.multiselect for Countries (updates based on region — chained)
#   c) st.date_input for date range (two-handle; convert years to Jan-1 dates)
#   d) st.radio for Metric: "Total CO2 (Mt)" vs "CO2 per capita"
#   e) st.checkbox labelled "Show only top emitter highlighted"
#
# Guards:
#   - empty countries → st.warning + st.stop()
#   - incomplete date_input → st.warning + st.stop()
# Convert date_input result to pd.Timestamp before filtering.
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Filters")

    # a) Region — chained filter, narrows the Countries options below
    regions = ['All'] + sorted(df['Region'].unique())
    selected_region = st.selectbox("Region", regions)

    country_options = (sorted(df['Country'].unique()) if selected_region == 'All'
                        else sorted(df[df['Region'] == selected_region]['Country'].unique()))

    # b) Countries
    selected_countries = st.multiselect("Countries", country_options, default=country_options[:3])

    if not selected_countries:
        st.warning("Select at least one country.")
        st.stop()

    # c) Date range — calendar picker for the underlying timestamps
    date_range = st.date_input(
        "Date range",
        value=(datetime.date(2010, 1, 1), datetime.date(2020, 1, 1)),
        min_value=datetime.date(int(df['Year'].min()), 1, 1),
        max_value=datetime.date(int(df['Year'].max()), 1, 1),
        format="YYYY-MM-DD",
    )
    if len(date_range) != 2:
        st.warning("Select a start AND end date.")
        st.stop()

    # d) Metric — 2 mutually exclusive options, clearer than a selectbox here
    metric = st.radio("Metric", ["Total CO2 (Mt)", "CO2 per capita"])

    # e) Highlight toggle — default unchecked
    highlight_top = st.checkbox("Show only top emitter highlighted")

# Always convert date_input → pd.Timestamp before pandas comparisons
start_ts, end_ts = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])
filtered = df[
    df['Country'].isin(selected_countries) &
    (df['Date'] >= start_ts) &
    (df['Date'] <= end_ts)
]

if filtered.empty:
    st.warning("No data in this date range for the selected countries.")
    st.stop()

y_col = 'CO2_Mt' if metric == "Total CO2 (Mt)" else 'CO2_per_capita'
y_label = 'CO2 Emissions (Mt)' if y_col == 'CO2_Mt' else 'CO2 per Capita'

# ── TASK 2: Filter summary caption ────────────────────────────────────────────
# BBD rule: always show users how many records match current filters
# ─────────────────────────────────────────────────────────────────────────────
st.caption(
    f"{len(selected_countries)} countries | {selected_region} | "
    f"{date_range[0].strftime('%d %b %Y')} – {date_range[1].strftime('%d %b %Y')} | {metric}"
)

# ── EXTENSION: KPI row above the charts ───────────────────────────────────────
#   - Total CO2 in last year of selected range (sum across selected countries)
#   - % change from first to last year
#   - Country with highest emissions in last year
# ─────────────────────────────────────────────────────────────────────────────
last_year = filtered['Year'].max()
first_year = filtered['Year'].min()
last_year_data = filtered[filtered['Year'] == last_year]
first_year_data = filtered[filtered['Year'] == first_year]

total_last_year = last_year_data['CO2_Mt'].sum()
total_first_year = first_year_data['CO2_Mt'].sum()
pct_change = ((total_last_year - total_first_year) / total_first_year * 100) if total_first_year else 0
top_emitter_last_year = last_year_data.sort_values(y_col, ascending=False)['Country'].iloc[0]

k1, k2, k3 = st.columns(3)
k1.metric(f"Total CO2 in {last_year}", f"{total_last_year:,.0f} Mt")
k2.metric(f"Change since {first_year}", f"{pct_change:+.1f}%")
k3.metric(f"Top emitter in {last_year}", top_emitter_last_year)

st.divider()

# ── TASK 3: Two charts reacting to ALL filters ────────────────────────────────
#   Left: line chart — selected metric over time, one line per country
#         If "Show only top emitter highlighted" checkbox is on:
#           - grey all lines except the highest emitter in the date range
#           - label that country at the end of its line (SWD grey-and-highlight)
#   Right: bar chart — ranking for the last year in selected date range
#
# BBD colour requirement: name the colour type in a comment next to each chart
# SWD requirements: white background, insight title, use_container_width=True
# ─────────────────────────────────────────────────────────────────────────────
col_left, col_right = st.columns([2, 1])

with col_left:
    if highlight_top:
        # BBD COLOUR TYPE: highlight — one country in colour, rest greyed (SWD grey-and-highlight)
        top_country = filtered.groupby('Country')[y_col].sum().idxmax()
        color_map = {c: ('#E63946' if c == top_country else '#CCCCCC') for c in selected_countries}

        fig1 = px.line(filtered, x='Date', y=y_col, color='Country',
                       color_discrete_map=color_map,
                       labels={y_col: y_label, 'Date': ''},
                       title=f'{top_country} is the Largest Emitter Among Selected Countries')

        for trace in fig1.data:
            trace.line.width = 4 if trace.name == top_country else 1.5
            trace.showlegend = (trace.name == top_country)

        top_line = filtered[filtered['Country'] == top_country].sort_values('Date')
        fig1.add_annotation(
            x=top_line['Date'].iloc[-1], y=top_line[y_col].iloc[-1],
            text=top_country, showarrow=False, xanchor='left', xshift=8,
            font=dict(color='#E63946', size=12),
        )
    else:
        # BBD COLOUR TYPE: categorical — each country is an unordered distinct group
        extended_palette = px.colors.qualitative.Alphabet
        fig1 = px.line(filtered, x='Date', y=y_col, color='Country',
                       color_discrete_sequence=extended_palette,
                       labels={y_col: y_label, 'Date': ''},
                       title=f'{metric} Over Time')

    fig1.update_layout(plot_bgcolor='white', paper_bgcolor='white',
                       font=dict(family='Arial'))
    st.plotly_chart(fig1, width='stretch')

with col_right:
    # BBD COLOUR TYPE: highlight — single bold colour, focus on the ranking itself
    latest = filtered[filtered['Year'] == last_year].sort_values(y_col)
    top_in_latest = latest['Country'].iloc[-1]

    fig2 = px.bar(latest, x=y_col, y='Country', orientation='h',
                  color_discrete_sequence=['#2E75B6'],
                  labels={y_col: y_label, 'Country': ''},
                  title=f'{top_in_latest} Leads in {last_year}')
    fig2.update_layout(plot_bgcolor='white', paper_bgcolor='white', font=dict(family='Arial'),
                       xaxis=dict(range=[0, latest[y_col].max() * 1.15]))
    fig2.update_traces(marker_line_width=0)
    st.plotly_chart(fig2, width='stretch')

st.divider()
st.caption("Built with Streamlit + Plotly")
