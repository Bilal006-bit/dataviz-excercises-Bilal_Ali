"""
Task 2 — Slopegraph: Regional CO2 change 2000 vs 2022

Compares average regional CO2 emissions between 2000 and 2022.
Red = regions that increased, blue = regions that decreased.
"""

import os
import pandas as pd
import plotly.graph_objects as go

script_dir = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.normpath(os.path.join(script_dir, '..', '..', 'data-viz-class-material', 'data', 'co2_emissions.csv'))

df = pd.read_csv(data_path)

# Aggregate to regional averages for 2000 and 2022
slope_data = (
    df[df['Year'].isin([2000, 2022])]
    .groupby(['Region', 'Year'])['CO2_Mt']
    .mean()
    .reset_index()
)

pivot = slope_data.pivot(index='Region', columns='Year', values='CO2_Mt')
pivot['increased'] = pivot[2022] > pivot[2000]

color_up = '#E63946'    # increased
color_down = '#457B9D'  # decreased

fig = go.Figure()

for region, row in pivot.iterrows():
    color = color_up if row['increased'] else color_down
    v2000, v2022 = row[2000], row[2022]

    fig.add_trace(go.Scatter(
        x=[2000, 2022], y=[v2000, v2022],
        mode='lines+markers',
        line=dict(color=color, width=2.5),
        marker=dict(size=8, color=color),
        showlegend=False,
        hovertemplate=f'{region}<extra></extra>'
    ))

    # Left label (2000)
    fig.add_annotation(
        x=2000, y=v2000,
        text=f'{region}  {v2000:.0f} Mt',
        showarrow=False, xanchor='right', xshift=-6,
        font=dict(color=color, size=11)
    )
    # Right label (2022)
    fig.add_annotation(
        x=2022, y=v2022,
        text=f'{v2022:.0f} Mt  {region}',
        showarrow=False, xanchor='left', xshift=6,
        font=dict(color=color, size=11)
    )

fig.update_layout(
    template='simple_white',
    title_text='Asia surged while North America and Europe cut CO2 — a widening regional divide since 2000',
    title_x=0.02,
    height=520,
    xaxis=dict(tickvals=[2000, 2022], ticktext=['2000', '2022'], showgrid=False),
    yaxis=dict(showticklabels=False, showgrid=False, zeroline=False),
    margin=dict(l=160, r=160)
)

fig.show()
