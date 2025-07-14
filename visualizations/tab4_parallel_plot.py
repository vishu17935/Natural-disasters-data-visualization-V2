import plotly.graph_objects as go
# import pandas as pd.
def plot_parallel_coordinates(df, plot_type='risk_vs_outcome'):
    """
    Draws a parallel coordinates plot for different themes in a disaster dataset.

    Parameters:
    - df: pandas DataFrame with disaster data
    - plot_type: one of ['risk_vs_outcome', 'wealth_vs_impact', 'vulnerability_path']
    """

    plot_configs = {
        'risk_vs_outcome': {
            'cols': [
                'World Risk Index', 'Disaster Severity Index',
                "Total Damage ('000 US$)", 'Coping Capacity', 'Adaptive Capacity'
            ],
            'color': 'World Risk Index',
            'title': 'Risk & Capacity vs Disaster Outcomes',
            'colorscale': 'Viridis',
        },
        'wealth_vs_impact': {
            'cols': [
                'gdp_per_capita', 'hdi', 'hospital_beds',
                'urban_population_pct', 'Disaster Severity Index', "Total Damage ('000 US$)"
            ],
            'color': 'gdp_per_capita',
            'title': 'Wealth, Health & Urbanization vs Impact',
            'colorscale': 'Tealgrn',
        },
        'vulnerability_path': {
            'cols': [
                'Vulnerability', 'Exposure', 'Coping Capacity',
                'Adaptive Capacity', 'gov_effectiveness', 'Disaster Severity Index'
            ],
            'color': 'Vulnerability',
            'title': 'Governance, Vulnerability & Deaths',
            'colorscale': 'Plasma',
        },
    }

    if plot_type not in plot_configs:
        raise ValueError(f"Invalid plot_type. Choose from: {list(plot_configs.keys())}")

    config = plot_configs[plot_type]
    cols = config['cols']
    color_col = config['color']

    # Drop NaNs
    df_clean = df.dropna(subset=cols)
    # print(df_clean.columns)
    # Build dimensions
    dimensions = []
    for col in cols:
        label = col.replace('_', ' ').replace("('000 US$)", 'k USD').strip()
        if 'Damage' in col:
            label = label.replace('Total', 'Total<br>').replace('Damage', 'Damage<br>')
        dimensions.append(dict(label=label, values=df_clean[col]))

    # Build plot
    fig = go.Figure(
        data=go.Parcoords(
            line=dict(
                color=df_clean[color_col],
                colorscale=config['colorscale'],
                showscale=True,
                cmin=df_clean[color_col].min(),
                cmax=df_clean[color_col].max()
            ),
            dimensions=dimensions
        )
    )

    fig.update_layout(
        font=dict(size=14, color='white'),
        paper_bgcolor='black',
        plot_bgcolor='black',
        margin=dict(l=80, r=80, t=50, b=50)
    )

    return fig
