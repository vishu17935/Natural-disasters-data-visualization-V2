import pandas as pd
import plotly.express as px

def get_scatter_matrix_viz(
    data: pd.DataFrame,
    country: str = "India",
    year_start: int = 2000,
    year_end: int = 2020,
    disaster_type: str = "All",
    metric_x: str = "Deaths",
    metric_y: str = "Damages"
) -> px.scatter_matrix:
    """
    Returns a Plotly scatter-matrix (pair plot) between two metrics
    for a given country, time range, and disaster type—so it can be
    rendered inline in Dash.
    """
    # 1) Filter data
    df_filtered = data.copy()
    if country != "World":
        df_filtered = df_filtered[df_filtered['Country name'] == country]
    df_filtered = df_filtered[
        (df_filtered['Year'] >= year_start) &
        (df_filtered['Year'] <= year_end)
    ]
    if disaster_type != "All":
        df_filtered = df_filtered[df_filtered['Disaster Type'] == disaster_type]

    # 2) Aggregate
    df_yearly = df_filtered.groupby('Year').agg({
        metric_x: 'sum',
        metric_y: 'sum'
    }).reset_index()

    # 3) Handle empty
    if df_yearly.empty:
        # returns an empty figure rather than crashing or popping up
        return px.scatter_matrix(pd.DataFrame(), dimensions=[])

    # 4) Build Plotly scatter-matrix
    fig = px.scatter_matrix(
        df_yearly,
        dimensions=[metric_x, metric_y],
        color='Year',
        title=(
            f"Scatter Matrix: {metric_x} vs {metric_y}\n"
            f"{country if country!='World' else 'World'}, "
            f"{disaster_type} ({year_start}–{year_end})"
        ),
        labels={metric_x: metric_x, metric_y: metric_y}
    )
    fig.update_layout(
        width=500,
        height=500,
        template="plotly_dark"
    )
    return fig
