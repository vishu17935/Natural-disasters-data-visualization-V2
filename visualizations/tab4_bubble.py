import plotly.graph_objects as go
import pandas as pd
import numpy as np

def create_disaster_bubble_chart(df, countries=None, y_metric='gdp_per_capita', 
                                size_metric='Total Affected', top_n=5):
    """
    Create a bubble chart with bubbles sized by aggregated yearly totals per country.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        The disaster dataset
    countries : list, optional
        List of countries to filter. If None, includes all countries
    y_metric : str
        Y-axis metric 
    size_metric : str
        Bubble size metric: 'Total Affected', 'Total Deaths', or 'Total Damage ('000 US$)'
    top_n : int
        Not used anymore, kept for compatibility
    
    Returns:
    --------
    plotly.graph_objects.Figure
        Interactive bubble chart figure
    """
    
    # Create a copy and filter
    data = df.copy()
    
    if countries:
        data = data[data['Country_x'].isin(countries)]
    
    # Clean data
    required_cols = ['Start Year', y_metric, size_metric, 'Country_x']
    data = data.dropna(subset=required_cols)
    data = data[data[size_metric] > 0]  # Remove zero/negative values
    
    # Aggregate by country and year - sum the size_metric for each year
    yearly_totals = data.groupby(['Country_x', 'Start Year']).agg({
        size_metric: 'sum',
        y_metric: 'first',  # Take first value (should be same for country)
        'Total Affected': 'sum',
        'Total Deaths': 'sum',
        'Disaster Type': lambda x: list(x)  # Keep all disaster types as list
    }).reset_index()
    
    # Get unique countries
    unique_countries = yearly_totals['Country_x'].unique()
    
    # Colors for countries
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', 
              '#A8E6CF', '#FFD93D', '#6C5CE7', '#FD79A8', '#FDCB6E', '#E17055']
    
    fig = go.Figure()
    
    # Add one trace per country
    for i, country in enumerate(unique_countries):
        country_data = yearly_totals[yearly_totals['Country_x'] == country]
        
        # Create hover text with top 3 disasters
        hover_texts = []
        for _, row in country_data.iterrows():
            # Get disaster types and their counts
            disaster_types = row['Disaster Type']
            disaster_counts = pd.Series(disaster_types).value_counts()
            
            # Get top 3 disasters
            top_3_disasters = disaster_counts.head(3)
            disaster_text = "<br>".join([f"{disaster}: {count}" for disaster, count in top_3_disasters.items()])
            
            hover_text = (f"<b>{row['Country_x']} - {int(row['Start Year'])}</b><br>" +
                         f"Total Affected: {row['Total Affected']:,.0f}<br>" +
                         f"Total Deaths: {row['Total Deaths']:,.0f}<br>" +
                         f"{y_metric.replace('_', ' ').title()}: {row[y_metric]:,.2f}<br>" +
                         f"<b>Top 3 Disasters:</b><br>{disaster_text}")
            
            hover_texts.append(hover_text)
        
        fig.add_trace(go.Scatter(
            x=country_data['Start Year'],
            y=country_data[y_metric],
            mode='markers',
            marker=dict(
                size=country_data[size_metric],
                color=colors[i % len(colors)],
                opacity=0.7,
                line=dict(width=1, color='white'),
                sizemode='area',
                sizeref=2.*max(yearly_totals[size_metric])/(60.**2),  # Scale to reasonable size
                sizemin=4
            ),
            text=hover_texts,
            hovertemplate='%{text}<extra></extra>',
            name=country,
            showlegend=True
        ))
    
    # Update layout
    fig.update_layout(
        title=dict(
            text=f'<b>Global Disaster Impact Analysis (Yearly Totals)</b><br>' +
                 f'<sub>Bubble size: {size_metric} | Y-axis: {y_metric.replace("_", " ").title()}</sub>',
            font=dict(size=18, color='#2C3E50'),
            x=0.5
        ),
        xaxis=dict(
            title='<b>Year</b>',
            gridcolor='#ECF0F1',
            tickfont=dict(size=12)
        ),
        yaxis=dict(
            title=f'<b>{y_metric.replace("_", " ").title()}</b>',
            gridcolor='#ECF0F1',
            tickfont=dict(size=12)
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        hovermode='closest',
        legend=dict(
            bgcolor='rgba(255,255,255,0.9)',
            bordercolor='#BDC3C7',
            borderwidth=1
        ),
        height=600,
        width=1000
    )
    
    return fig


# Example usage:
# fig = create_disaster_bubble_chart(
#     df=merged_data, 
#     countries=['India', 'China', 'Japan'],
#     y_metric='urban_population_pct',
#     size_metric='Total Damage (\'000 US$)',
#     top_n=5
# )
# fig.show()
#  Y-axis metric from: 'gdp_per_capita', 'gdp_per_capita_ppp', 'hospital_beds', 
#         'hdi', 'urban_population_pct', 'gov_effectiveness', 'population_density', 
#         'Disaster_Score', 'Average_Risk_Index', 'World Risk Index', 'Exposure', 
#         'Vulnerability', 'Susceptibility', 'Coping Capacity', 'Adaptive Capacity'