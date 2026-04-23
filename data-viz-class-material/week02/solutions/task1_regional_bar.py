"""
Task 1 — Regional comparison bar chart (starter)

Creates a horizontal bar chart of average Happiness_Score by Region.
"""

import pandas as pd
import plotly.express as px

# Load data (path is relative to this script)
df = pd.read_csv('../../data/world_happiness_2023.csv')
df.columns = ['Country','Region','Happiness_Score','GDP','Social_Support',
              'Life_Expectancy','Freedom','Generosity','Corruption']

# Compute average happiness by region
region_avg = (df.groupby('Region')['Happiness_Score']
              .mean()
              .reset_index()
              .sort_values('Happiness_Score', ascending=False))

# Build horizontal bar chart
fig = px.bar(region_avg,
             x='Happiness_Score', y='Region',
             orientation='h',
             color='Happiness_Score',
             color_continuous_scale='Blues',
             labels={'Happiness_Score':'Avg happiness score','Region':''},
             )

# Enforce zero baseline
fig.update_xaxes(range=[0, region_avg['Happiness_Score'].max()*1.05])

# Design tweaks
top_region = region_avg.iloc[0]['Region']
fig.update_layout(template='simple_white',
                  title_text=f"{top_region} has the highest average happiness — regional differences matter for policy",
                  title_x=0.02,
                  height=420)
fig.update_traces(texttemplate='%{x:.2f}', textposition='inside', marker_line_width=0)

fig.show()
