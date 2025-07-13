import plotly.graph_objects as go
import pandas as pd
import numpy as np

def country_risk_radar_with_slider(df, country_name):
    """
    Create a radar chart with year slider for comparing a country's risk dimensions over time.
    
    Parameters:
    df (pd.DataFrame): DataFrame containing disaster data
    country_name (str): Name of the country to analyze
    
    Returns:
    plotly.graph_objects.Figure: Radar chart figure object with year slider
    """
    
    # Define the risk dimensions to include in the radar chart
    risk_dimensions = [
        'World Risk Index',
        'Exposure', 
        'Vulnerability',
        'Susceptibility',
        'Coping Capacity',
        'Adaptive Capacity',
        'Average_Risk_Index',
        'Disaster_Score'
    ]
    
    # Filter data for the specified country
    country_data = df[df['Country_x'] == country_name].copy()
    
    if country_data.empty:
        raise ValueError(f"Country '{country_name}' not found in the dataset")
    
    # Get available years for the country
    available_years = sorted(country_data['Start Year'].dropna().unique())
    
    if len(available_years) == 0:
        raise ValueError(f"No year data found for country '{country_name}'")
    
    # Create figure
    fig = go.Figure()
    
    # Create traces for each year
    for year in available_years:
        year_data = country_data[country_data['Start Year'] == year]
        
        # Get values for each dimension for this year
        year_values = []
        dimension_names = []
        
        for dim in risk_dimensions:
            if dim in df.columns:
                values = year_data[dim].dropna()
                if len(values) > 0:
                    year_values.append(values.mean())
                    dimension_names.append(dim)
        
        if not year_values:
            continue
        
        # Add trace for this year (initially visible only for the first year)
        fig.add_trace(go.Scatterpolar(
            r=year_values,
            theta=dimension_names,
            fill='toself',
            name=f'{country_name} ({year})',
            line=dict(color='rgba(0, 123, 255, 0.8)', width=3),
            fillcolor='rgba(0, 123, 255, 0.3)',
            visible=True if year == available_years[0] else False,
            hovertemplate='<b>%{theta}</b><br>' +
                         f'<b>{country_name} ({year})</b><br>' +
                         'Score: %{r:.1f}<br>' +
                         '<extra></extra>'
        ))
    
    # Create slider steps
    steps = []
    for i, year in enumerate(available_years):
        step = dict(
            method="update",
            args=[{"visible": [False] * len(available_years)},
                  {"title": f"Risk Dimensions Profile: {country_name} ({year})"}],
            label=str(year)
        )
        step["args"][0]["visible"][i] = True  # Toggle i'th trace to "visible"
        steps.append(step)
    
    # Add slider
    sliders = [dict(
        active=0,
        currentvalue={"prefix": "Year: "},
        pad={"t": 50},
        steps=steps
    )]
    
    # Update layout
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickmode='linear',
                tick0=0,
                dtick=20,
                showticklabels=True,
                tickfont=dict(size=10),
                gridcolor='rgba(128, 128, 128, 0.3)'
            ),
            angularaxis=dict(
                tickfont=dict(size=12),
                rotation=90,
                direction='clockwise'
            )
        ),
        showlegend=True,
        title=dict(
            text=f'Risk Dimensions Profile: {country_name} ({available_years[0]})',
            x=0.5,
            font=dict(size=16, family='Arial, sans-serif')
        ),
        font=dict(family='Arial, sans-serif'),
        width=700,
        height=700,
        margin=dict(l=80, r=80, t=100, b=80),
        sliders=sliders
    )
    
    # Add annotations to explain the chart
    fig.add_annotation(
        text="Scale: 0-100 (original scores)",
        xref="paper", yref="paper",
        x=0.5, y=-0.1,
        showarrow=False,
        font=dict(size=10, color="gray"),
        xanchor="center"
    )
    
    return fig

def multi_country_risk_radar_with_slider(df, countries_list, max_countries=3):
    """
    Create a radar chart with year slider comparing multiple countries' risk dimensions over time.
    
    Parameters:
    df (pd.DataFrame): DataFrame containing disaster data
    countries_list (list): List of country names to compare
    max_countries (int): Maximum number of countries to display
    
    Returns:
    plotly.graph_objects.Figure: Radar chart figure object with year slider
    """
    
    # Limit the number of countries to avoid overcrowding
    if len(countries_list) > max_countries:
        countries_list = countries_list[:max_countries]
        print(f"Limited to first {max_countries} countries for better visualization")
    
    risk_dimensions = [
        'World Risk Index',
        'Exposure', 
        'Vulnerability',
        'Susceptibility',
        'Coping Capacity',
        'Adaptive Capacity',
        'Average_Risk_Index'
    ]
    
    # Color palette for different countries
    colors = [
        'rgba(255, 99, 132, 0.8)',   # Red
        'rgba(54, 162, 235, 0.8)',   # Blue  
        'rgba(255, 205, 86, 0.8)',   # Yellow
        'rgba(75, 192, 192, 0.8)',   # Teal
        'rgba(153, 102, 255, 0.8)',  # Purple
    ]
    
    # Get available years across all countries
    all_years = set()
    for country in countries_list:
        country_data = df[df['Country_x'] == country]
        if not country_data.empty:
            years = country_data['Start Year'].dropna().unique()
            all_years.update(years)
    
    available_years = sorted(list(all_years))
    
    if len(available_years) == 0:
        raise ValueError("No year data found for any of the specified countries")
    
    fig = go.Figure()
    
    # Create traces for each country for each year
    trace_info = []  # Keep track of traces for slider
    
    for year in available_years:
        year_traces = []
        
        for idx, country_name in enumerate(countries_list):
            # Filter data for the country and year
            country_year_data = df[(df['Country_x'] == country_name) & 
                                 (df['Start Year'] == year)]
            
            if country_year_data.empty:
                # Add empty trace to maintain consistent indexing
                year_traces.append(None)
                continue
            
            # Get values for each dimension
            country_values = []
            dimension_names = []
            
            for dim in risk_dimensions:
                if dim in df.columns:
                    values = country_year_data[dim].dropna()
                    if len(values) > 0:
                        country_values.append(values.mean())
                        dimension_names.append(dim)
            
            if not country_values:
                year_traces.append(None)
                continue
            
            # Add trace for this country and year
            trace = go.Scatterpolar(
                r=country_values,
                theta=dimension_names,
                fill='toself',
                name=f'{country_name}',
                line=dict(color=colors[idx % len(colors)], width=2),
                fillcolor=colors[idx % len(colors)].replace('0.8', '0.2'),
                visible=True if year == available_years[0] else False,
                hovertemplate='<b>%{theta}</b><br>' +
                             f'<b>{country_name} ({year})</b><br>' +
                             'Score: %{r:.1f}<br>' +
                             '<extra></extra>'
            )
            
            fig.add_trace(trace)
            year_traces.append(len(fig.data) - 1)  # Store trace index
        
        trace_info.append(year_traces)
    
    # Create slider steps
    steps = []
    for i, year in enumerate(available_years):
        # Create visibility array
        visible = [False] * len(fig.data)
        
        # Make traces for this year visible
        for trace_idx in trace_info[i]:
            if trace_idx is not None:
                visible[trace_idx] = True
        
        step = dict(
            method="update",
            args=[{"visible": visible},
                  {"title": f"Risk Dimensions Comparison ({year})"}],
            label=str(year)
        )
        steps.append(step)
    
    # Add slider
    sliders = [dict(
        active=0,
        currentvalue={"prefix": "Year: "},
        pad={"t": 50},
        steps=steps
    )]
    
    # Update layout
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickmode='linear',
                tick0=0,
                dtick=20,
                showticklabels=True,
                tickfont=dict(size=10),
                gridcolor='rgba(128, 128, 128, 0.3)'
            ),
            angularaxis=dict(
                tickfont=dict(size=11),
                rotation=90,
                direction='clockwise'
            )
        ),
        showlegend=True,
        title=dict(
            text=f'Risk Dimensions Comparison ({available_years[0]})',
            x=0.5,
            font=dict(size=16, family='Arial, sans-serif')
        ),
        font=dict(family='Arial, sans-serif'),
        width=800,
        height=800,
        margin=dict(l=80, r=80, t=120, b=80),
        sliders=sliders
    )
    
    return fig

# Simple version that aggregates data by year for smoother experience
def country_risk_radar_yearly(df, country_name):
    """
    Create a radar chart with year slider using aggregated yearly data.
    This version aggregates all disaster data by year for smoother visualization.
    
    Parameters:
    df (pd.DataFrame): DataFrame containing disaster data
    country_name (str): Name of the country to analyze
    
    Returns:
    plotly.graph_objects.Figure: Radar chart figure object with year slider
    """
    
    risk_dimensions = [
        'World Risk Index',
        'Exposure', 
        'Vulnerability',
        'Susceptibility',
        'Coping Capacity',
        'Adaptive Capacity',
        'Average_Risk_Index'
    ]
    
    # Filter data for the specified country
    country_data = df[df['Country_x'] == country_name].copy()
    
    if country_data.empty:
        raise ValueError(f"Country '{country_name}' not found in the dataset")
    
    # Group by year and aggregate the risk dimensions
    yearly_data = country_data.groupby('Start Year')[risk_dimensions].mean().reset_index()
    yearly_data = yearly_data.dropna(subset=['Start Year'])
    
    if yearly_data.empty:
        raise ValueError(f"No valid yearly data found for country '{country_name}'")
    
    available_years = sorted(yearly_data['Start Year'].unique())
    
    fig = go.Figure()
    
    # Create traces for each year
    for year in available_years:
        year_row = yearly_data[yearly_data['Start Year'] == year].iloc[0]
        
        # Get values for each dimension for this year
        year_values = []
        dimension_names = []
        
        for dim in risk_dimensions:
            if not pd.isna(year_row[dim]):
                year_values.append(year_row[dim])
                dimension_names.append(dim)
        
        if not year_values:
            continue
        
        # Add trace for this year
        fig.add_trace(go.Scatterpolar(
            r=year_values,
            theta=dimension_names,
            fill='toself',
            name=f'{country_name} ({int(year)})',
            line=dict(color='rgba(0, 123, 255, 0.8)', width=3),
            fillcolor='rgba(0, 123, 255, 0.3)',
            visible=True if year == available_years[0] else False,
            hovertemplate='<b>%{theta}</b><br>' +
                         f'<b>{country_name} ({int(year)})</b><br>' +
                         'Score: %{r:.1f}<br>' +
                         '<extra></extra>'
        ))
    
    # Create slider steps
    steps = []
    for i, year in enumerate(available_years):
        step = dict(
            method="update",
            args=[{"visible": [False] * len(available_years)},
                  {"title": f"Risk Dimensions Profile: {country_name} ({int(year)})"}],
            label=str(int(year))
        )
        step["args"][0]["visible"][i] = True
        steps.append(step)
    
    # Add slider
    sliders = [dict(
        active=0,
        currentvalue={"prefix": "Year: "},
        pad={"t": 50},
        steps=steps
    )]
    
    # Update layout
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickmode='linear',
                tick0=0,
                dtick=20,
                showticklabels=True,
                tickfont=dict(size=10),
                gridcolor='rgba(128, 128, 128, 0.3)'
            ),
            angularaxis=dict(
                tickfont=dict(size=12),
                rotation=90,
                direction='clockwise'
            )
        ),
        showlegend=True,
        title=dict(
            text=f'Risk Dimensions Profile: {country_name} ({int(available_years[0])})',
            x=0.5,
            font=dict(size=16, family='Arial, sans-serif')
        ),
        font=dict(family='Arial, sans-serif'),
        width=700,
        height=700,
        margin=dict(l=80, r=80, t=120, b=80),
        sliders=sliders
    )
    
    # Add annotations to explain the chart
    fig.add_annotation(
        text="Scale: 0-100 (original scores) • Use slider to change year",
        xref="paper", yref="paper",
        x=0.5, y=-0.12,
        showarrow=False,
        font=dict(size=10, color="gray"),
        xanchor="center"
    )
    
    return fig

# Example usage:
"""
# Single country with year slider
fig1 = create_country_risk_radar_with_slider(df, 'India')
fig1.show()

# Multiple countries with year slider
fig2 = create_multi_country_risk_radar_with_slider(df, ['India', 'China', 'Japan'])
fig2.show()

# Yearly aggregated version (recommended for cleaner visualization)
fig3 = create_country_risk_radar_yearly(df, 'India')
fig3.show()
"""