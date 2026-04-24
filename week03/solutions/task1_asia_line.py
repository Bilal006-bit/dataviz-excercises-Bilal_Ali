"""
Task 1 — Multi-series line chart with highlight

Shows CO2 emissions over time for all Asian countries.
China is highlighted in red; all others are grey for context.
"""

import os
import pandas as pd
import plotly.graph_objects as go

script_dir = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.normpath(os.path.join(script_dir, '..', '..', 'data-viz-class-material', 'data', 'co2_emissions.csv'))

df = pd.read_csv(data_path)

asia = df[df['Region'] == 'Asia'].copy()
highlight = 'China'
grey = '#DDDDDD'
highlight_color = '#E63946'

fig = go.Figure()

# All non-highlighted countries in grey
for country in asia['Country'].unique():
    if country == highlight:
        continue
    d = asia[asia['Country'] == country]
    fig.add_trace(go.Scatter(
        x=d['Year'], y=d['CO2_Mt'],
        mode='lines',
        line=dict(color=grey, width=1.5),
        showlegend=False,
        hovertemplate=f'{country}: %{{y:.0f}} Mt<extra></extra>'
    ))

# Highlighted country
d_highlight = asia[asia['Country'] == highlight]
fig.add_trace(go.Scatter(
    x=d_highlight['Year'], y=d_highlight['CO2_Mt'],
    mode='lines',
    line=dict(color=highlight_color, width=3),
    showlegend=False,
    hovertemplate=f'{highlight}: %{{y:.0f}} Mt<extra></extra>'
))

# Direct label at the end of the line
last = d_highlight[d_highlight['Year'] == d_highlight['Year'].max()].iloc[0]
fig.add_annotation(
    x=last['Year'], y=last['CO2_Mt'],
    text=f'<b>{highlight}</b>',
    showarrow=False, xanchor='left', xshift=8,
    font=dict(color=highlight_color, size=13)
)

fig.update_layout(
    template='simple_white',
    title_text="China's CO2 emissions tripled since 2000, dwarfing every other Asian nation",
    title_x=0.02,
    xaxis_title='',
    yaxis_title='CO2 emissions (Mt)',
    height=480,
    margin=dict(r=80)
)
fig.update_yaxes(rangemode='tozero')

fig.show()
