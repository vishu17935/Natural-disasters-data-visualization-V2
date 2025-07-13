import pandas as pd
import plotly.express as px

def get_country_metric_correlation_viz(
    data: pd.DataFrame,
    country: str = "India",
    year_start: int = 2000,
    year_end: int = 2020,
    metrics: list = ['Deaths', 'Injuries', 'Assistance', 'Damages', 'Affected', 'Rendered homeless']
) -> px.imshow:
    """
    Returns a Plotly heatmap of correlations between selected metrics
    for a given country and time range—so it can be inlined in Dash.
    """
    # Copy & filter
    df_filtered = data.copy()
    if country != "World":
        df_filtered = df_filtered[df_filtered['Country name'] == country]
    df_country = df_filtered[
        (df_filtered['Year'] >= year_start) &
        (df_filtered['Year'] <= year_end)
    ]
    if df_country.empty:
        # Return an empty Plotly figure rather than pop up or crash
        return px.imshow([[]], text_auto=True)

    # Aggregate
    df_yearly = df_country.groupby('Year').agg({
        m: ('mean' if m == 'Damages' else 'sum') for m in metrics
    }).reset_index()

    # Correlation
    corr_matrix = df_yearly[metrics].fillna(0).corr()

    # Plotly heatmap
    fig = px.imshow(
        corr_matrix,
        text_auto=True,
        aspect="auto",
        color_continuous_scale="RdBu",
        zmin=-1, zmax=1,
        labels=dict(x="Metric", y="Metric", color="Correlation")
    )
    fig.update_layout(
        title=f'Metric Correlation Over Time in {country} ({year_start}–{year_end})',
        width=800,
        height=600,
        template="plotly_dark"
    )
    return fig
