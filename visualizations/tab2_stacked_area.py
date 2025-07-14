import pandas as pd
import plotly.express as px
import numpy as np

import plotly.express as px
import pandas as pd

def plot_stacked_disasters_by_year(df):
    # Drop rows with missing year or type
    filtered = df.dropna(subset=['Start Year', 'Disaster Type'])

    # Group and count disasters per year and type
    count_df = (
        filtered.groupby(['Start Year', 'Disaster Type'])
        .size()
        .reset_index(name='Disaster Count')
    )

    # Create stacked bar chart
    fig = px.bar(
        count_df,
        x='Start Year',
        y='Disaster Count',
        color='Disaster Type',
        title='Disaster Events per Year by Type (Stacked)',
        labels={'Start Year': 'Year', 'Disaster Count': 'Number of Disasters'},
        height=500
    )

    fig.update_layout(
        barmode='stack',
        xaxis=dict(type='category', tickangle=45),
        legend=dict(title='Disaster Type')
    )

    return fig


def get_area_chart_viz(
    data: pd.DataFrame,
    country: str,
    metric: str,
    year_start: int,
    year_end: int
) -> px.area:
    """
    Create an interactive stacked area chart showing log-scaled metric values over years by disaster type.

    Parameters:
    - data: DataFrame with columns ['Country name', 'Year', 'Disaster Type', metric]
    - country: country to filter (use 'World' to skip filtering)
    - metric: metric column name to plot (e.g., 'Deaths')
    - year_start: start year
    - year_end: end year

    Returns:
    - Plotly area chart figure
    """
    try:
        # Filter year range
        df_filtered = data[(data['Year'] >= year_start) & (data['Year'] <= year_end)].copy()
        if country != 'World':
            df_filtered = df_filtered[df_filtered['Country name'] == country]

        # Group by year and disaster type
        df_area = df_filtered.groupby(['Year', 'Disaster Type'])[metric].sum().reset_index()

        # Log-scale value (avoid log(0))
        df_area['log_value'] = np.log10(df_area[metric] + 1)

        # Prepare customdata
        df_area['customdata'] = df_area.apply(lambda row: [row[metric], row['Disaster Type']], axis=1)

        # Plot
        fig = px.area(
            df_area,
            x='Year',
            y='log_value',
            color='Disaster Type',
            title=f"Stacked Area Chart: {metric} Over Years by Disaster Type ({country}, {year_start}-{year_end})"
        )

        # Update hover
        fig.update_traces(
            hovertemplate=(
                "Year: %{x}<br>"
                "Disaster Type: %{customdata[1]}<br>"
                "Original Value: %{customdata[0]:,.0f}<br>"
                "Shown Value (log): %{y:.2f}<extra></extra>"
            ),
            customdata=df_area['customdata']
        )

        fig.update_yaxes(title=f"{metric} (log-scaled)")

        return fig

    except Exception as e:
        print(f"Error creating area chart: {str(e)}")
        return px.area()  # Empty chart if error
