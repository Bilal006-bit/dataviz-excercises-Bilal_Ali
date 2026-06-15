#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lecture 9 — Class Exercise
World Happiness Dashboard (Streamlit + Plotly)

Steps 1-4: full dashboard from class (KPIs, rankings, score vs GDP)
Step 6 (Class Exercise): third chart using a DIVERGING colour scale —
Generosity relative to the global average, with the midpoint (global
average) labelled in an annotation.
"""

import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="World Happiness", page_icon="🌍", layout="wide")

df = pd.read_csv('../data/world_happiness_2023.csv')
df.columns = ['Country', 'Region', 'Score', 'GDP', 'Social_Support',
               'Life_Expectancy', 'Freedom', 'Generosity', 'Corruption']

with st.sidebar:
    st.header("Filters")
    regions = ['All'] + sorted(df['Region'].unique().tolist())
    selected_region = st.selectbox("Region", regions)
    top_n = st.slider("Show top N", 5, 25, 15)

filtered = df if selected_region == 'All' else df[df['Region'] == selected_region]

st.title("🌍 World Happiness Dashboard")
st.caption("Source: World Happiness Report 2023 | Kaggle")

# KPI row — BBD: big numbers at the top, readable in 5 seconds
col1, col2, col3 = st.columns(3)
col1.metric("Countries", len(filtered))
col2.metric("Avg Score", f"{filtered['Score'].mean():.2f}",
             f"{filtered['Score'].mean() - df['Score'].mean():+.2f} vs global")
col3.metric("Happiest", filtered.nlargest(1, 'Score')['Country'].values[0])

st.divider()

# Two-column layout
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Rankings")
    top = filtered.nlargest(top_n, 'Score').sort_values('Score')

    fig1 = px.bar(top, x='Score', y='Country', orientation='h',
                   color_discrete_sequence=['#2E75B6'],
                   labels={'Score': 'Score (0–10)', 'Country': ''})

    fig1.update_layout(plot_bgcolor='white', paper_bgcolor='white',
                        xaxis=dict(range=[0, 8.5]), font=dict(family='Arial', size=12),
                        margin=dict(l=10, r=10, t=5, b=10))
    fig1.update_traces(marker_line_width=0)
    st.plotly_chart(fig1, width='stretch')

with col_right:
    st.subheader("Score vs GDP")
    fig2 = px.scatter(filtered, x='GDP', y='Score', hover_name='Country',
                       color_discrete_sequence=['#E63946'])
    fig2.update_layout(plot_bgcolor='white', paper_bgcolor='white',
                        font=dict(family='Arial', size=12),
                        margin=dict(l=10, r=10, t=5, b=10))
    st.plotly_chart(fig2, width='stretch')

st.divider()

# ── STEP 6: Third chart — diverging colour scale, midpoint labelled ──────
st.subheader("Generosity vs the Global Average")
st.caption("Diverging scale centred on the global mean — red = less generous "
            "than the world, blue = more generous than the world.")

global_generosity = df['Generosity'].mean()
gen = filtered.nlargest(top_n, 'Score').sort_values('Generosity').copy()
gen['Generosity_vs_avg'] = gen['Generosity'] - global_generosity

fig3 = px.bar(
    gen, x='Generosity_vs_avg', y='Country', orientation='h',
    color='Generosity_vs_avg',
    color_continuous_scale='RdBu',   # diverging: red = below avg, blue = above avg
    color_continuous_midpoint=0,     # white at zero = global average
    labels={'Generosity_vs_avg': 'Generosity vs global average', 'Country': ''},
)

fig3.add_vline(x=0, line_dash='dash', line_color='grey')
fig3.add_annotation(x=0, y=1.06, yref='paper', showarrow=False,
                     text=f'Global average ({global_generosity:.3f})',
                     font=dict(size=11, color='grey'))

fig3.update_layout(plot_bgcolor='white', paper_bgcolor='white',
                    font=dict(family='Arial', size=12),
                    coloraxis_showscale=False,
                    margin=dict(l=10, r=20, t=35, b=10))
fig3.update_traces(marker_line_width=0)

st.plotly_chart(fig3, width='stretch')

st.divider()
st.caption("Built with Streamlit + Plotly")
