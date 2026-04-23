"""
Task 2 — Top 8 vs Bottom 8 contrast (starter)

Creates a horizontal bar chart showing the top 8 and bottom 8 countries
with a visual separator and a global-average reference line.
"""

import pandas as pd
import plotly.express as px

# Load data (path is relative to this script)
df = pd.read_csv('../../data/world_happiness_2023.csv')
df.columns = ['Country','Region','Happiness_Score','GDP','Social_Support',
              'Life_Expectancy','Freedom','Generosity','Corruption']

# Get top and bottom 8
top8 = df.nlargest(8, 'Happiness_Score').copy()
top8['Group'] = 'Top 8'
bottom8 = df.nsmallest(8, 'Happiness_Score').copy()
bottom8['Group'] = 'Bottom 8'

combined = pd.concat([bottom8, top8]).sort_values('Happiness_Score')
global_avg = df['Happiness_Score'].mean()
print(f"Global average: {global_avg:.2f}")

# Preserve order so bars are plotted from bottom->top by score
country_order = combined['Country'].tolist()

color_map = {'Top 8':'#1f77b4','Bottom 8':'#ff7f0e'}
fig = px.bar(combined, x='Happiness_Score', y='Country', orientation='h',
             color='Group', color_discrete_map=color_map,
             category_orders={'Country': country_order},
             labels={'Happiness_Score':'Happiness score','Country':''},
             )

# Zero baseline
fig.update_xaxes(range=[0, combined['Happiness_Score'].max()*1.05])

# Visual gap shading between bottom and top groups
gap_start = bottom8['Happiness_Score'].max()
gap_end = top8['Happiness_Score'].min()
fig.add_shape(type='rect', x0=gap_start, x1=gap_end, y0=-0.5, y1=len(combined)-0.5, yref='y', xref='x',
              fillcolor='LightSalmon', opacity=0.08, layer='below', line_width=0)

# Global average reference line
fig.add_vline(x=global_avg, line_dash='dash', line_color='gray')
fig.add_annotation(x=global_avg, y=0, xref='x', yref='paper', showarrow=False,
                   text=f'Global avg: {global_avg:.2f}', xanchor='left', yanchor='bottom')

fig.update_layout(template='simple_white',
                  title_text='Top 8 vs Bottom 8: Large gap in happiness highlights global inequality',
                  title_x=0.02, height=700)
fig.update_traces(marker_line_width=0)

fig.show()
