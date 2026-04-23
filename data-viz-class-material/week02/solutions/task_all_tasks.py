"""
Combined Week 02 tasks (Task 1, Task 2, Task 3 stretch)

Generates three Plotly charts and writes them as HTML files into an `output/` folder
next to this script. Also prints the output paths so you can open them locally.

Run from the workspace root or anywhere — the script resolves the data path
relative to its own location.
"""

import os
import pandas as pd
import plotly.express as px

script_dir = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.normpath(os.path.join(script_dir, '..', '..', 'data', 'world_happiness_2023.csv'))
output_dir = os.path.join(script_dir, 'output')
os.makedirs(output_dir, exist_ok=True)

# Load data
df = pd.read_csv(data_path)
df.columns = ['Country','Region','Happiness_Score','GDP','Social_Support',
              'Life_Expectancy','Freedom','Generosity','Corruption']

# Helper to write and report
def save_fig(fig, name):
    out = os.path.join(output_dir, f"{name}.html")
    fig.write_html(out)
    print(f"Saved: {out}")


if __name__ == '__main__':
    print("Running combined tasks — outputs will be saved to the 'output' folder.")

    # ------------------
    # Task 1 — Regional Comparison Bar Chart
    # ------------------
    print('\n=== Task 1: Regional comparison (horizontal bars) ===')
    region_avg = (df.groupby('Region')['Happiness_Score']
                  .mean()
                  .reset_index()
                  .sort_values('Happiness_Score', ascending=False))

    fig1 = px.bar(region_avg,
                 x='Happiness_Score', y='Region',
                 orientation='h',
                 color='Happiness_Score',
                 color_continuous_scale='Blues',
                 labels={'Happiness_Score':'Avg happiness score','Region':''},
                 )
    fig1.update_xaxes(range=[0, region_avg['Happiness_Score'].max()*1.05])
    top_region = region_avg.iloc[0]['Region']
    fig1.update_layout(template='simple_white',
                       title_text=f"{top_region} has the highest average happiness — regional differences matter for policy",
                       title_x=0.02, height=420)
    fig1.update_traces(texttemplate='%{x:.2f}', textposition='inside', marker_line_width=0)
    save_fig(fig1, 'task1_regional_comparison')

    # ------------------
    # Task 2 — Top 8 vs Bottom 8 Contrast
    # ------------------
    print('\n=== Task 2: Top 8 vs Bottom 8 contrast ===')
    top8 = df.nlargest(8, 'Happiness_Score').copy()
    top8['Group'] = 'Top 8'
    bottom8 = df.nsmallest(8, 'Happiness_Score').copy()
    bottom8['Group'] = 'Bottom 8'

    combined = pd.concat([bottom8, top8]).sort_values('Happiness_Score')
    global_avg = df['Happiness_Score'].mean()
    print(f"Global average: {global_avg:.2f}")

    country_order = combined['Country'].tolist()
    color_map = {'Top 8':'#1f77b4','Bottom 8':'#ff7f0e'}

    fig2 = px.bar(combined, x='Happiness_Score', y='Country', orientation='h',
                  color='Group', color_discrete_map=color_map,
                  category_orders={'Country': country_order},
                  labels={'Happiness_Score':'Happiness score','Country':''},
                  )
    fig2.update_xaxes(range=[0, combined['Happiness_Score'].max()*1.05])

    gap_start = bottom8['Happiness_Score'].max()
    gap_end = top8['Happiness_Score'].min()
    fig2.add_shape(type='rect', x0=gap_start, x1=gap_end, y0=-0.5, y1=len(combined)-0.5, yref='y', xref='x',
                   fillcolor='LightSalmon', opacity=0.08, layer='below', line_width=0)
    fig2.add_vline(x=global_avg, line_dash='dash', line_color='gray')
    fig2.add_annotation(x=global_avg, y=0, xref='x', yref='paper', showarrow=False,
                        text=f'Global avg: {global_avg:.2f}', xanchor='left', yanchor='bottom')

    fig2.update_layout(template='simple_white',
                       title_text='Top 8 vs Bottom 8: Large gap in happiness highlights global inequality',
                       title_x=0.02, height=700)
    fig2.update_traces(marker_line_width=0)
    save_fig(fig2, 'task2_top_bottom_contrast')

    # ------------------
    # Task 3 (Stretch) — Grouped bar chart comparing two sub-factors
    # Regions: 'Western Europe', 'Latin America', 'East Asia', 'Sub-Saharan Africa', 'South Asia'
    # Compare average 'GDP' and 'Freedom' across these regions.
    # ------------------
    print('\n=== Task 3 (stretch): Grouped bar chart for sub-factors ===')
    regions = ['Western Europe', 'Latin America', 'East Asia', 'Sub-Saharan Africa', 'South Asia']
    sub = df[df['Region'].isin(regions)].copy()
    if sub.empty:
        print('Warning: no data for the specified regions in Task 3. Skipping Task 3 output.')
    else:
        agg = sub.groupby('Region')[['GDP','Freedom']].mean().reset_index()
        # Keep only regions present in the data, preserve requested order
        available = set(agg['Region'].tolist())
        present = [r for r in regions if r in available]
        if not present:
            print('Warning: none of the requested regions found in the dataset. Skipping Task 3 output.')
        else:
            agg = agg[agg['Region'].isin(present)].set_index('Region').reindex(present).reset_index()

            fig3 = px.bar(agg, x='Region', y=['GDP','Freedom'], barmode='group',
                          labels={'value':'Average', 'Region':'Region'},)
            fig3.update_layout(template='simple_white', title_text='Average GDP and Freedom by region (stretch)',
                               title_x=0.02, height=480)
            save_fig(fig3, 'task3_grouped_subfactors')

    print('\nAll tasks complete. Open the saved HTML files in the solutions/output folder to view the charts.')
